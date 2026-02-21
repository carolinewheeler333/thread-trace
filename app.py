import streamlit as st
from PIL import Image
import os
from src import matcher

st.set_page_config(layout="wide", page_title="Thread-Trace")

st.markdown("""
<style>
    /* Background and base font */
    .stApp {
        background-color: #f7f5f2;
        color: #2c2c2c;
        font-family: 'Georgia', serif;
    }

    /* Hide default Streamlit header/footer */
    #MainMenu, footer, header { visibility: hidden; }

    /* Main title */
    h1 {
        font-family: 'Georgia', serif;
        font-size: 2.2rem;
        font-weight: 400;
        letter-spacing: 0.12em;
        color: #2c2c2c;
        text-transform: uppercase;
        padding-bottom: 0.2rem;
    }

    /* Subheaders */
    h2, h3 {
        font-family: 'Georgia', serif;
        font-weight: 400;
        letter-spacing: 0.08em;
        color: #4a4a4a;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 1px solid #d4cfc9;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Georgia', serif;
        font-size: 0.85rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #8a8178;
        background-color: transparent;
        border: none;
        padding-bottom: 0.6rem;
    }
    .stTabs [aria-selected="true"] {
        color: #2c2c2c !important;
        border-bottom: 2px solid #2c2c2c !important;
        background-color: transparent !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #eeeae5;
        border: 1px dashed #c4bfb8;
        border-radius: 4px;
        padding: 1rem;
    }

    /* Progress bars (used for analysis) */
    .stProgress > div > div {
        background-color: #8a8178;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-family: 'Georgia', serif;
        font-size: 0.8rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #8a8178;
    }

    /* Links */
    a {
        color: #6b6259 !important;
        text-decoration: underline;
        font-size: 0.82rem;
        letter-spacing: 0.04em;
    }

    /* Divider */
    hr {
        border-color: #d4cfc9;
    }

    /* Caption / small text */
    .stCaption, small {
        color: #8a8178;
        font-size: 0.78rem;
        letter-spacing: 0.04em;
    }

    /* Info boxes */
    .stAlert {
        background-color: #eeeae5;
        border: none;
        color: #6b6259;
    }
</style>
""", unsafe_allow_html=True)

st.title("Thread-Trace")
st.caption("Mood → Marketplace — find second-hand pieces that match your aesthetic")

st.divider()

uploaded = st.file_uploader("Upload a Pinterest or mood image to begin", type=["jpg","jpeg","png"])

tab1, tab2, tab3 = st.tabs(["Inspiration", "AI Analysis", "Matches"])

with tab1:
	if uploaded:
		st.image(Image.open(uploaded), width=600)
	else:
		st.markdown("#### Demo Inspirations")
		demo_list = matcher.list_demo_inspirations()
		if demo_list:
			cols = st.columns(min(3, len(demo_list)))
			for i, fname in enumerate(demo_list[:3]):
				cols[i].image(os.path.join("data/inspiration", fname), caption=fname, use_container_width=True)
		else:
			st.info("No demo images found in data/inspiration.")

with tab2:
	st.markdown("#### Style Attributes Detected")
	demo_list = matcher.list_demo_inspirations()
	if not uploaded and demo_list:
		for fname in demo_list[:3]:
			st.markdown(f"**{fname}**")
			analysis = matcher.simulate_analysis(fname)
			for k, v in analysis.items():
				st.caption(f"{k} — {int(v*100)}%")
				st.progress(v)
			st.divider()
	elif uploaded:
		analysis = matcher.simulate_analysis(uploaded.name)
		for k, v in analysis.items():
			st.caption(f"{k} — {int(v*100)}%")
			st.progress(v)
	with st.expander("How this works"):
		st.write("Attributes are extracted via simulated feature vector analysis and nearest-neighbor search (Wizard-of-Oz prototype).")

with tab3:
	st.markdown("#### Curated Matches")
	if uploaded:
		matches = matcher.load_matches_for(uploaded.name)
		groups = [(uploaded.name, matches)] if matches else []
	else:
		groups = []
		for fname in matcher.WIZARD_MAP.keys():
			m = matcher.load_matches_for(fname)
			if m:
				groups.append((fname, m))

	if not groups:
		st.info("No matches found. Add demo matches JSON files to data/matches or map filenames in src/matcher.py")
	else:
		for group_name, matches in groups:
			st.markdown(f"**Inspired by:** {group_name}")
			cols = st.columns(min(4, len(matches)))
			for i, item in enumerate(matches):
				if isinstance(item, dict):
					img = item.get("img")
					title = item.get("title", "")
					price = item.get("price", "")
					url = item.get("url", "")
					source = item.get("source", "")
				else:
					img = item
					title = os.path.basename(str(item))
					price = ""
					url = ""
					source = ""

				col = cols[i % 4]
				try:
					col.image(img, use_container_width=True)
				except Exception:
					col.write("(image missing)")

				if title:
					col.markdown(f"**{title}**")
				if price:
					col.caption(price)
				if source:
					col.caption(source)
				if url:
					col.markdown(f"[View listing →]({url})")
			st.divider()

