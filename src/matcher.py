"""Matcher module for Thread-Trace A2.

Pipeline per uploaded image:
  1. get_ai_analysis()            — GPT-4o vision → style JSON          (LLM #1)
  2. generate_search_query()      — GPT-4o-mini text → retail keywords  (LLM #2)
  3. search_live()                — Etsy / eBay API → real listings
  4. score_match_relevance()      — GPT-4o-mini → 0-100 per listing     (LLM #3 / evaluation)
  5. generate_outfit_suggestions() — GPT-4o-mini → complementary pieces (LLM #4 / outfit tab)

Demo inspiration images still use curated JSON matches so the UI always
shows something even without API keys.
"""
import os
import json
import base64
import csv
import requests


# ---------------------------------------------------------------------------
# LLM #1 — GPT-4o vision: image → style JSON
# ---------------------------------------------------------------------------

def get_ai_analysis(image_bytes: bytes, api_key: str) -> dict:
    """Send image to GPT-4o and return title, style description + attribute scores.

    Returns:
        {
            "title": "Brown Wide-Leg Pants",
            "description": "2-3 sentence style read ...",
            "attributes": {"Earth Tones": 0.9, "Oversized Fit": 1.0, ...}
        }
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        prompt = (
            "You are a fashion stylist analysing an outfit or mood board image. "
            "Respond with ONLY a JSON object — no markdown, no extra text — in this exact format:\n"
            '{"title": "<2-4 word plain descriptive name for the key clothing item shown, '
            'e.g. Brown Corduroy Pants, Cream Knit Dress, Tan Suede Loafers — no poetic language, just what it is>", '
            '"description": "<2-3 sentence style read: aesthetic, silhouette, colour palette, vibe>", '
            '"attributes": {"<label>": <0.0-1.0>, "<label>": <0.0-1.0>, "<label>": <0.0-1.0>, "<label>": <0.0-1.0>}}\n'
            "Labels should be short fashion terms (e.g. Earth Tones, Oversized Fit, Suede, Monochrome). "
            "Scores should reflect how strongly the attribute appears in the image."
        )
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                ],
            }],
            max_tokens=250,
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        parsed = json.loads(raw)
        return {
            "title": parsed.get("title", ""),
            "description": parsed.get("description", ""),
            "attributes": parsed.get("attributes", {}),
        }
    except Exception as e:
        return {"title": "", "description": "", "attributes": {}, "error": str(e)}


# ---------------------------------------------------------------------------
# LLM #2 — GPT-4o-mini text: style JSON → retail search query
# ---------------------------------------------------------------------------

def generate_search_query(analysis: dict, api_key: str) -> dict:
    """Convert abstract style analysis into a concrete retail search query.

    A single GPT-4o vision call returns terms like "Avant-Garde", "Earth Tones",
    and "Oversized Fit" — these are NOT directly searchable on eBay or Etsy.
    This second LLM call translates them into short, concrete keywords a buyer
    would actually type.

    Args:
        analysis: dict with keys title, description, attributes
        api_key:  OpenAI API key

    Returns:
        {"query": "brown wide leg pants women vintage", "category": "Pants"}
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        attributes_text = ", ".join(
            f"{k} ({v:.0%})" for k, v in analysis.get("attributes", {}).items()
        )
        prompt = (
            "You are a second-hand fashion search assistant. "
            "Given the style analysis below, generate the best short search query "
            "to find matching second-hand clothing on eBay or Etsy. "
            "The query must use plain, concrete keywords a buyer would type — "
            "no poetic or abstract fashion terms. Include garment type, colour, "
            "fit/silhouette, and 'women' if appropriate. Keep it under 8 words.\n\n"
            f"Title: {analysis.get('title', '')}\n"
            f"Description: {analysis.get('description', '')}\n"
            f"Style attributes: {attributes_text}\n\n"
            "Respond with ONLY a JSON object:\n"
            '{"query": "<short concrete search string>", "category": "<garment type>"}'
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        parsed = json.loads(raw)
        return {
            "query": parsed.get("query", analysis.get("title", "")),
            "category": parsed.get("category", ""),
        }
    except Exception as e:
        return {"query": analysis.get("title", ""), "category": "", "error": str(e)}


# ---------------------------------------------------------------------------
# Marketplace search — Etsy (live now) and eBay (when key is available)
# ---------------------------------------------------------------------------

def search_etsy_used(query: str, api_key: str, n: int = 6) -> list:
    """Search Etsy for second-hand / vintage clothing listings.

    Uses the Etsy Open API v3.  taxonomy_id=1811 targets Women's Clothing.

    Args:
        query:   search string from generate_search_query()
        api_key: Etsy API key (x-api-key header)
        n:       max results to return

    Returns:
        List of dicts: {title, img, price, url, source}
    """
    if not api_key or not query:
        return []
    try:
        url = "https://openapi.etsy.com/v3/application/listings/active"
        params = {
            "keywords": query,
            "limit": n,
            "taxonomy_id": 1811,  # Women's Clothing
            "sort_on": "score",
        }
        headers = {"x-api-key": api_key}
        resp = requests.get(url, params=params, headers=headers, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("results", []):
            images = item.get("images", [])
            img_url = images[0].get("url_570xN", "") if images else ""
            price_info = item.get("price", {})
            price_str = ""
            if price_info:
                amount = price_info.get("amount", 0) / max(price_info.get("divisor", 100), 1)
                currency = price_info.get("currency_code", "USD")
                price_str = f"${amount:.2f}" if currency == "USD" else f"{amount:.2f} {currency}"
            listing_id = item.get("listing_id", "")
            item_url = f"https://www.etsy.com/listing/{listing_id}" if listing_id else ""
            if img_url:
                results.append({
                    "title": item.get("title", ""),
                    "img": img_url,
                    "price": price_str,
                    "url": item_url,
                    "source": "Etsy",
                })
        return results
    except Exception:
        return []


def search_ebay_used(query: str, app_id: str, n: int = 6) -> list:
    """Search eBay for clothing listings via the Finding API.

    Keeps filters minimal — no condition filter, no listing type filter —
    so eBay's server doesn't choke on multi-value param encoding.
    The relevance scorer (LLM #3) handles quality filtering downstream.

    Args:
        query:  search string from generate_search_query()
        app_id: eBay Production AppID (Client ID)
        n:      max results to return

    Returns:
        List of dicts: {title, img, price, url, source}
        OR a single-item list [{"error": "..."}] if the call fails.
    """
    if not app_id or not query:
        return []
    try:
        url = "https://svcs.ebay.com/services/search/FindingService/v1"
        params = {
            "OPERATION-NAME":                "findItemsByKeywords",
            "SERVICE-VERSION":               "1.0.0",
            "SECURITY-APPNAME":              app_id,
            "RESPONSE-DATA-FORMAT":          "JSON",
            "keywords":                      query,
            "paginationInput.entriesPerPage": str(n),
            "outputSelector":                "PictureURLLarge",
        }
        resp = requests.get(url, params=params, timeout=10)

        # Parse JSON regardless of status so we can surface eBay's error message
        try:
            data = resp.json()
        except Exception:
            return [{"error": f"HTTP {resp.status_code} — could not parse response",
                     "title": "", "img": "", "price": "", "url": "", "source": "eBay"}]

        # eBay can put errors at the TOP level OR inside findItemsByKeywordsResponse
        def _extract_ebay_error(d):
            # Top-level errorMessage (e.g. auth errors)
            top = d.get("errorMessage", [])
            if top:
                return top[0].get("error", [{}])[0].get("message", ["Unknown eBay error"])[0]
            # Nested inside the response wrapper
            nested = (
                d.get("findItemsByKeywordsResponse", [{}])[0]
                 .get("errorMessage", [])
            )
            if nested:
                return nested[0].get("error", [{}])[0].get("message", ["Unknown eBay error"])[0]
            return None

        ebay_error_msg = _extract_ebay_error(data)
        if ebay_error_msg or resp.status_code >= 400:
            msg = ebay_error_msg or f"HTTP {resp.status_code}"
            return [{"error": msg, "title": "", "img": "", "price": "", "url": "", "source": "eBay"}]

        items = (
            data.get("findItemsByKeywordsResponse", [{}])[0]
            .get("searchResult", [{}])[0]
            .get("item", [])
        )
        results = []
        for item in items:
            img = (
                item.get("pictureURLLarge", [""])[0]
                or item.get("galleryURL", [""])[0]
            )
            price_val = (
                item.get("sellingStatus", [{}])[0]
                .get("currentPrice", [{}])[0]
                .get("__value__", "")
            )
            price_str = f"${float(price_val):.2f}" if price_val else ""
            item_url  = item.get("viewItemURL", [""])[0]
            results.append({
                "title":  item.get("title", [""])[0],
                "img":    img,
                "price":  price_str,
                "url":    item_url,
                "source": "eBay",
            })
        return results
    except Exception as e:
        return [{"error": str(e), "title": "", "img": "", "price": "", "url": "", "source": "eBay"}]


def search_live(query: str, etsy_key: str = "", ebay_app_id: str = "", n: int = 6) -> list:
    """Combine eBay and Etsy results, falling back gracefully.

    Tries eBay first (larger second-hand fashion inventory).
    Adds Etsy results if slots remain, deduplicating by title prefix.
    """
    results = []
    if ebay_app_id:
        results.extend(search_ebay_used(query, ebay_app_id, n))
    if etsy_key and len(results) < n:
        etsy = search_etsy_used(query, etsy_key, n - len(results))
        existing = {r["title"][:30].lower() for r in results}
        for item in etsy:
            if item["title"][:30].lower() not in existing:
                results.append(item)
    return results[:n]


# ---------------------------------------------------------------------------
# LLM #3 — GPT-4o-mini: relevance scoring (evaluation layer)
# ---------------------------------------------------------------------------

def score_match_relevance(matches: list, analysis: dict, api_key: str) -> list:
    """Score each marketplace listing for relevance to the style profile.

    All listing titles are sent in a single batched call to minimise cost.
    Scores are 0-100; results are sorted highest-first; items below 40 are dropped.

    Args:
        matches:  list of {title, img, price, url, source} dicts
        analysis: style dict with title, description, attributes
        api_key:  OpenAI API key

    Returns:
        Filtered, sorted list of match dicts each with added:
            relevance_score (int 0-100)
            relevance_reason (str, one sentence)
    """
    if not matches or not api_key:
        for m in matches:
            m.setdefault("relevance_score", 75)
            m.setdefault("relevance_reason", "")
        return matches

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        attributes_text = ", ".join(
            f"{k} ({v:.0%})" for k, v in analysis.get("attributes", {}).items()
        )
        listings_text = "\n".join(
            f"{i+1}. {m['title']} — {m.get('price', '')}"
            for i, m in enumerate(matches)
        )
        prompt = (
            "You are a fashion matching evaluator. "
            "Given the style profile and a numbered list of second-hand listings, "
            "score each listing 0-100 for how well it matches the style. "
            "100 = perfect match in garment type, colour, and aesthetic. "
            "0 = completely wrong.\n\n"
            f"Style profile:\n"
            f"  Title: {analysis.get('title', '')}\n"
            f"  Description: {analysis.get('description', '')}\n"
            f"  Attributes: {attributes_text}\n\n"
            f"Listings:\n{listings_text}\n\n"
            "Respond with ONLY a JSON array, one object per listing in the same order:\n"
            '[{"score": <int>, "reason": "<one sentence>"}, ...]'
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        scores = json.loads(raw)

        scored = []
        for i, m in enumerate(matches):
            entry = scores[i] if i < len(scores) else {"score": 50, "reason": ""}
            m["relevance_score"] = int(entry.get("score", 50))
            m["relevance_reason"] = entry.get("reason", "")
            if m["relevance_score"] >= 40:
                scored.append(m)

        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored

    except Exception:
        for m in matches:
            m.setdefault("relevance_score", 75)
            m.setdefault("relevance_reason", "")
        return matches


# ---------------------------------------------------------------------------
# LLM #4 — GPT-4o-mini: outfit suggestions (Outfit Inspiration tab)
# ---------------------------------------------------------------------------

def generate_outfit_suggestions(analysis: dict, api_key: str) -> list:
    """Suggest 3 complementary second-hand pieces to complete the outfit.

    Uses the style profile from LLM #1 to identify what other garments and
    accessories would pair well, then generates a concrete Etsy search query
    for each one.  Intentionally uses Etsy-only search (no eBay) to avoid
    burning the eBay daily quota on secondary searches.

    Args:
        analysis: style dict with title, description, attributes
        api_key:  OpenAI API key

    Returns:
        [
            {
                "piece":  "Wide-leg linen trousers",
                "query":  "wide leg linen trousers women boho",
                "why":    "The relaxed silhouette echoes the flowy fringe detail"
            },
            ...  (3 items total)
        ]
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        attributes_text = ", ".join(
            f"{k} ({v:.0%})" for k, v in analysis.get("attributes", {}).items()
        )
        prompt = (
            "You are a personal stylist helping someone build a second-hand outfit. "
            "Given the clothing item analysis below, suggest exactly 3 complementary "
            "pieces (mix of clothing and accessories) that would complete the look. "
            "For each piece, write a concrete Etsy search query someone would type to "
            "find it second-hand — short, specific, no abstract style words.\n\n"
            f"Item: {analysis.get('title', '')}\n"
            f"Description: {analysis.get('description', '')}\n"
            f"Style attributes: {attributes_text}\n\n"
            "Respond with ONLY a JSON array of exactly 3 objects:\n"
            '[{"piece": "<short name>", "query": "<etsy search string>", '
            '"why": "<one sentence why it pairs well>"}]'
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        suggestions = json.loads(raw)
        return suggestions[:3] if isinstance(suggestions, list) else []
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Image deletion
# ---------------------------------------------------------------------------

def delete_image(filename: str, inspiration_folder: str = "data/inspiration"):
    """Delete an image file and remove its cache entry.

    Args:
        filename: basename of the image (e.g. 'inspo1.jpeg')
        inspiration_folder: folder where inspiration images are stored
    """
    # Delete image file
    img_path = os.path.join(inspiration_folder, filename)
    if os.path.exists(img_path):
        os.remove(img_path)

    # Remove from cache and re-save
    cache = load_cache()
    if filename in cache:
        del cache[filename]
        save_cache(cache)


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

CACHE_PATH = "data/analysis_cache.json"


def load_cache() -> dict:
    """Load persisted analysis results from disk."""
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cache(cache: dict):
    """Persist analysis results to disk."""
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


# ---------------------------------------------------------------------------
# Feedback logging
# ---------------------------------------------------------------------------

FEEDBACK_PATH = "data/feedback.csv"


def log_feedback(image_name: str, match_title: str, match_url: str, rating: str):
    """Append a user thumbs-up / thumbs-down rating to feedback.csv."""
    os.makedirs(os.path.dirname(FEEDBACK_PATH), exist_ok=True)
    write_header = not os.path.exists(FEEDBACK_PATH)
    with open(FEEDBACK_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["image", "match_title", "match_url", "rating"])
        writer.writerow([image_name, match_title, match_url, rating])


def load_feedback_stats() -> dict:
    """Return aggregate feedback stats: total ratings and % positive."""
    if not os.path.exists(FEEDBACK_PATH):
        return {"total": 0, "positive": 0, "pct": 0}
    try:
        total = positive = 0
        with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                total += 1
                if row.get("rating") == "up":
                    positive += 1
        pct = round(positive / total * 100) if total else 0
        return {"total": total, "positive": positive, "pct": pct}
    except Exception:
        return {"total": 0, "positive": 0, "pct": 0}


# ---------------------------------------------------------------------------
# Demo / Wizard-of-Oz helpers (kept for curated inspo images)
# ---------------------------------------------------------------------------

WIZARD_MAP = {
    "inspo1.jpeg": ["data/matches/inspo1_1.jpg", "data/matches/inspo1_2.jpg"],
    "inspo2.jpeg": ["data/matches/inspo2_1.jpg", "data/matches/inspo2_2.jpg"],
    "inspo3.jpeg": ["data/matches/inspo3_1.jpg", "data/matches/inspo3_2.jpg"],
}

DEMO_KEYS = list(WIZARD_MAP.keys())


def list_demo_inspirations(folder="data/inspiration"):
    if not os.path.isdir(folder):
        return []
    return sorted([f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))])


def load_matches_for(filename):
    """Load structured match metadata for demo inspiration images.

    For uploaded images the pipeline uses live_matches from the cache instead.
    """
    if not filename:
        return []

    base = os.path.splitext(filename)[0]
    json_path = os.path.join("data", "matches", f"{base}.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf8") as fh:
                data = json.load(fh)
                if isinstance(data, list):
                    return data
        except Exception:
            pass

    if filename in WIZARD_MAP:
        imgs = WIZARD_MAP[filename]
        return [{"img": p, "url": "", "title": os.path.basename(p), "price": "", "source": ""} for p in imgs]

    all_matches = []
    for key in DEMO_KEYS:
        jp = os.path.join("data", "matches", f"{os.path.splitext(key)[0]}.json")
        if os.path.exists(jp):
            try:
                with open(jp, "r", encoding="utf8") as fh:
                    data = json.load(fh)
                    if isinstance(data, list):
                        all_matches.extend(data)
                        continue
            except Exception:
                pass
        for p in WIZARD_MAP.get(key, []):
            all_matches.append({"img": p, "url": "", "title": os.path.basename(p), "price": "", "source": ""})
    return all_matches
