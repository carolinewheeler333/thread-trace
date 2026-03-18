# Thread-Trace

A Streamlit app that turns a mood board or Pinterest image into curated second-hand marketplace matches using a four-stage AI pipeline.

Built for *Prototyping Products with Data and Artificial Intelligence* (Assignment 2).

---

## What it does

1. Upload a mood board or Pinterest screenshot
2. GPT-4o vision analyses the image and returns a structured style profile (title, description, attribute confidence scores)
3. GPT-4o-mini translates that profile into a concrete retail search query
4. The app searches eBay and Etsy for real second-hand listings
5. GPT-4o-mini scores each result 0–100 for relevance and filters out weak matches
6. A fourth LLM call suggests three complementary pieces to complete the outfit, each with its own search results

---

## How to run locally

```bash
git clone https://github.com/carolinewheeler333/thread-trace.git
cd thread-trace
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Add API keys to `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY = "sk-..."
ETSY_API_KEY   = ""
EBAY_APP_ID    = ""
```

The app runs without marketplace keys — the Outfit Builder and demo images work from cache.

---

## Project structure

```
thread-trace/
├── app.py              # Streamlit UI (UI only, no prediction logic)
├── src/
│   └── matcher.py      # Full pipeline: vision analysis, search, relevance scoring, outfit suggestions
├── data/
│   ├── inspiration/    # Uploaded and demo inspiration images
│   ├── matches/        # Curated match metadata for demo images
│   └── analysis_cache.json  # Persistent cache of all AI results
└── requirements.txt
```

---

## AI pipeline

```
Upload → GPT-4o vision (LLM 1)  → style JSON
       → GPT-4o-mini (LLM 2)    → retail search query
       → eBay / Etsy API         → live second-hand listings
       → GPT-4o-mini (LLM 3)    → relevance score 0–100 per listing
       → GPT-4o-mini (LLM 4)    → 3 complementary outfit pieces
```
