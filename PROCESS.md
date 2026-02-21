# Thread-Trace — Process & Decisions

## Overview

Thread-Trace is a Wizard-of-Oz prototype that demonstrates how a user could go from a mood board or Pinterest image to marketplace listings that match the "vibe." The prototype focuses on UI design, AI pipeline conceptual design, and accuracy/value tradeoffs.

## Idea & Vision

The idea came from a personal frustration: seeing aspirational outfits on Pinterest but having no easy way to find affordable, second-hand alternatives. Thread-Trace addresses this by treating the mood image as a query and returning ranked marketplace matches.

- **Input:** a mood board or Pinterest screenshot
- **Output:** a short ranked list of second-hand marketplace items (Vinted, Depop, eBay) that match the look
- **Value:** saves users time and bridges the gap between inspiration and accessible fashion

## Prototype Approach — Wizard-of-Oz

Rather than building a full computer vision pipeline for the prototype, I used a Wizard-of-Oz approach:
- Pre-downloaded demo inspiration images are stored in `data/inspiration/`
- A `WIZARD_MAP` in `src/matcher.py` maps each inspiration image to a set of curated match images and metadata stored in `data/matches/`
- `simulate_analysis()` returns per-image style attribute confidence scores (e.g. "Suede: 80%")

This approach proves the UX and pipeline design without requiring a trained embedding model, which is appropriate for a prototype at this stage.

## Three Prototype Pillars

**1. Appearance / UX**
The app uses a neutral, boutique-style layout with serif typography and a warm off-white palette. Widgets used include `st.file_uploader`, `st.tabs`, `st.columns`, `st.expander`, `st.progress`, and custom CSS injected via `st.markdown`. The layout prioritises images and keeps text minimal.

**2. Data / AI Pipeline**
The conceptual pipeline is: image upload → feature extraction (CLIP embeddings) → nearest-neighbour search (FAISS) → ranked marketplace results. In the prototype, this is simulated via `WIZARD_MAP` and `simulate_analysis()`. Prediction logic is fully separated from the UI in `src/matcher.py`.

**3. Accuracy vs Value**
The prototype demonstrates value even without a perfect model — a small curated set of high-confidence matches is more useful to a user than a large noisy result set. This tradeoff is intentional and reflects real product thinking.

## How I Used AI

I used GitHub Copilot CLI throughout the development of this prototype. Specifically:
- Debugging launch errors (missing dependencies, empty JSON files)
- Refactoring the matches tab to group results by inspiration image
- Applying custom CSS styling for the neutral/modern visual design
- Reviewing the project against the assignment brief to identify gaps
- Restructuring documentation (README vs PROCESS split)

Copilot CLI was used as a collaborative tool — I directed the decisions and reviewed every change before accepting it.

## Next Steps (Real Implementation)

- Replace `WIZARD_MAP` with CLIP embeddings + FAISS for genuine nearest-neighbour search
- Ingest real marketplace listings from `ppdai_a1.json` via `src/data_loader.py`
- Add automated tests in `src/` and a CI pipeline
- Deploy to Streamlit Cloud for a persistent shareable link

