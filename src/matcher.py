"""Matcher module for the Thread-Trace Wizard-of-Oz prototype.

AI analysis (style read + attributes) is handled by a single GPT-4o vision
call per image. Match results fall back to curated demo items for any upload.
Prediction logic lives here so app.py stays UI-only.
"""
import os
import json
import base64


def get_ai_analysis(image_bytes: bytes, api_key: str) -> dict:
    """Send image to GPT-4o and return title, style description + attribute scores.

    Returns a dict:
        {
            "title": "Caramel Suede Moment",
            "description": "2-3 sentence style read ...",
            "attributes": {"Earth Tones": 0.85, "Relaxed Fit": 0.7, ...}
        }
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        prompt = (
            "You are a fashion stylist analysing an outfit or mood board image. "
            "Respond with ONLY a JSON object — no markdown, no extra text — in this exact format:\n"
            '{"title": "<2-4 word plain descriptive name for the key clothing item shown, e.g. Brown Corduroy Pants, Cream Knit Dress, Tan Suede Loafers — no poetic language, just what it is>", '
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


# Curated demo match images — shown for any uploaded image
WIZARD_MAP = {
	"inspo1.jpeg": ["data/matches/inspo1_1.jpg", "data/matches/inspo1_2.jpg"],
	"inspo2.jpeg": ["data/matches/inspo2_1.jpg", "data/matches/inspo2_2.jpg"],
	"inspo3.jpeg": ["data/matches/inspo3_1.jpg", "data/matches/inspo3_2.jpg"],
}

# All demo match keys, used as fallback for any non-demo upload
DEMO_KEYS = list(WIZARD_MAP.keys())


def list_demo_inspirations(folder="data/inspiration"):
	if not os.path.isdir(folder):
		return []
	return sorted([f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))])


def load_matches_for(filename):
	"""Load structured match metadata for filename.

	Falls back to all curated demo matches for any image not in the map,
	so the prototype always shows results regardless of what was uploaded.
	"""
	if not filename:
		return []

	# Try JSON file first
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

	# Try WIZARD_MAP for exact demo match
	if filename in WIZARD_MAP:
		imgs = WIZARD_MAP[filename]
		return [{"img": p, "url": "", "title": os.path.basename(p), "price": "", "source": ""} for p in imgs]

	# Fallback: return all demo matches for any other uploaded image
	all_matches = []
	for key in DEMO_KEYS:
		json_path = os.path.join("data", "matches", f"{os.path.splitext(key)[0]}.json")
		if os.path.exists(json_path):
			try:
				with open(json_path, "r", encoding="utf8") as fh:
					data = json.load(fh)
					if isinstance(data, list):
						all_matches.extend(data)
						continue
			except Exception:
				pass
		for p in WIZARD_MAP.get(key, []):
			all_matches.append({"img": p, "url": "", "title": os.path.basename(p), "price": "", "source": ""})
	return all_matches

