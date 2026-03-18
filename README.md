# Thread-Trace

A Streamlit prototype that maps Pinterest mood board images onto curated second-hand marketplace listings, helping users find affordable alternatives that match their aesthetic.

Built for *Prototyping Products with Data and Artificial Intelligence* (Assignment 1).

---

## What it does

1. Upload a mood board or Pinterest screenshot
2. The app simulates AI-based style analysis (feature extraction + nearest-neighbor search)
3. Returns a ranked list of second-hand marketplace matches from eBay and etsy

---

## How to run locally

```bash
# 1. Clone the repo
git clone https://github.com/cswheeler42/thread-trace.git
cd thread-trace

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

---

## Project structure

```
thread-trace/
├── app.py              # Streamlit UI (UI-only, no prediction logic)
├── src/
│   ├── matcher.py      # Wizard-of-Oz matching logic and analysis simulation
│   ├── model.py        # Placeholder for real CV model integration
│   └── data_loader.py  # Placeholder for dataset ingestion
├── data/
│   ├── inspiration/    # Demo mood board images (inspo1–3.jpeg)
│   └── matches/        # Match images + metadata JSON files
├── PROCESS.md          # Process document (decisions, pipeline, AI usage)
└── requirements.txt
```

