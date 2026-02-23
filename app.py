import streamlit as st
from PIL import Image
import os
import io
from src import matcher

st.set_page_config(layout="wide", page_title="Thread-Trace")

# Load persisted analysis cache from disk into session_state on first run
if "ai_analysis" not in st.session_state:
    st.session_state.ai_analysis = matcher.load_cache()

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=Jost:wght@300;400&display=swap');

    /* Background and base */
    .stApp {
        background-color: #f5f2ee;
        color: #2c2c2c;
        font-family: 'Jost', sans-serif;
        font-weight: 300;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stToolbar"] { display: none; }

    /* Hero title */
    .hero {
        text-align: center;
        padding: 3rem 0 1.5rem 0;
        border-bottom: 1px solid #ddd9d3;
        margin-bottom: 2rem;
    }
    .hero h1 {
        font-family: 'Cormorant Garamond', serif;
        font-size: 4rem;
        font-weight: 300;
        letter-spacing: 0.35em;
        color: #1e1e1e;
        text-transform: uppercase;
        margin: 0;
        line-height: 1;
    }
    .hero .tagline {
        font-family: 'Jost', sans-serif;
        font-size: 0.72rem;
        font-weight: 300;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: #9e9890;
        margin-top: 0.75rem;
    }

    /* Section labels */
    h4 {
        font-family: 'Jost', sans-serif;
        font-size: 0.7rem;
        font-weight: 400;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: #9e9890;
        margin-bottom: 1.2rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 3rem;
        border-bottom: 1px solid #ddd9d3;
        background-color: transparent;
        justify-content: center;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Jost', sans-serif;
        font-size: 0.85rem;
        font-weight: 300;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #b0a89e;
        background-color: transparent;
        border: none;
        padding-bottom: 0.75rem;
    }
    .stTabs [aria-selected="true"] {
        color: #1e1e1e !important;
        border-bottom: 1px solid #1e1e1e !important;
        background-color: transparent !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #edeae5;
        border: 1px dashed #ccc7c0;
        border-radius: 2px;
        padding: 1.5rem;
    }
    [data-testid="stFileUploader"] label {
        font-family: 'Jost', sans-serif;
        font-size: 0.72rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #9e9890;
    }

    /* Images — rounded corners */
    img {
        border-radius: 2px;
    }

    /* Progress bar track */
    [data-testid="stProgressBar"] > div {
        background-color: #e5e1db;
        border-radius: 0;
        height: 3px !important;
    }
    [data-testid="stProgressBar"] > div > div {
        background-color: #2c2c2c !important;
        border-radius: 0;
    }

    /* Expander */
    [data-testid="stExpander"] summary {
        font-family: 'Jost', sans-serif;
        font-size: 0.68rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #b0a89e;
    }

    /* Links */
    a {
        color: #6b6259 !important;
        text-decoration: none !important;
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        border-bottom: 1px solid #c4bfb8;
    }
    a:hover { color: #2c2c2c !important; border-bottom-color: #2c2c2c; }

    /* Divider */
    hr { border-color: #ddd9d3; margin: 2rem 0; }

    /* Caption */
    [data-testid="stCaptionContainer"] p {
        color: #9e9890;
        font-size: 0.72rem;
        letter-spacing: 0.06em;
        font-family: 'Jost', sans-serif;
    }

    /* Info box */
    .stAlert {
        background-color: #edeae5;
        border: none;
        color: #9e9890;
        font-size: 0.78rem;
        font-family: 'Jost', sans-serif;
    }

    /* Bold text in markdown */
    strong {
        font-weight: 400;
        letter-spacing: 0.04em;
    }

    /* Match card spacing */
    [data-testid="column"] {
        padding: 0 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>Thread&thinsp;Trace</h1>
    <div class="tagline">Mood &nbsp;·&nbsp; Match &nbsp;·&nbsp; Marketplace</div>
</div>
""", unsafe_allow_html=True)

col_left, col_mid, col_right = st.columns([1, 2, 1])
with col_mid:
    uploaded = st.file_uploader("Upload a mood or Pinterest image", type=["jpg","jpeg","png"])

api_key = st.secrets.get("OPENAI_API_KEY", "")

def run_ai_analysis(fname, img_bytes):
    """Run OpenAI analysis, cache in session_state and persist to disk."""
    if (fname not in st.session_state.ai_analysis or st.session_state.ai_analysis[fname].get("error")) \
            and api_key and not api_key.startswith("sk-...") and len(api_key) > 20:
        with st.spinner("Analysing your aesthetic — this takes a few seconds..."):
            result = matcher.get_ai_analysis(img_bytes, api_key)
            st.session_state.ai_analysis[fname] = result
            matcher.save_cache(st.session_state.ai_analysis)

# Handle file upload: save to data/inspiration/ and run AI analysis
if uploaded:
    save_path = os.path.join("data/inspiration", uploaded.name)
    uploaded.seek(0)
    img_bytes = uploaded.read()
    uploaded.seek(0)
    with open(save_path, "wb") as f:
        f.write(img_bytes)
    run_ai_analysis(uploaded.name, img_bytes)

# Run AI analysis for demo images — process sequentially with delay to avoid rate limits
import time
for demo_fname in matcher.list_demo_inspirations():
    if demo_fname not in st.session_state.ai_analysis or st.session_state.ai_analysis[demo_fname].get("error"):
        demo_path = os.path.join("data/inspiration", demo_fname)
        if os.path.exists(demo_path):
            with open(demo_path, "rb") as f:
                demo_bytes = f.read()
            run_ai_analysis(demo_fname, demo_bytes)
            time.sleep(2)

tab1, tab2, tab3 = st.tabs(["Inspiration", "AI Analysis", "Matches"])

with tab1:
	st.markdown("#### Inspirations")
	demo_list = matcher.list_demo_inspirations()
	if demo_list:
		cols = st.columns(min(3, len(demo_list)))
		for i, fname in enumerate(demo_list):
			col = cols[i % 3]
			col.image(os.path.join("data/inspiration", fname), use_column_width=True)
			analysis = st.session_state.ai_analysis.get(fname, {})
			title = analysis.get("title", "")
			desc = analysis.get("description", "")
			display_label = f"{title} — {fname}" if title else fname
			col.markdown(
				f"<p style='font-family:Jost,sans-serif;font-size:0.9rem;letter-spacing:0.1em;"
				f"text-transform:uppercase;color:#9e9890;margin-top:0.4rem'>{display_label}</p>",
				unsafe_allow_html=True,
			)
			if desc:
				col.markdown(
					f"<p style='font-family:Cormorant Garamond,serif;font-size:1.15rem;"
					f"font-style:italic;color:#9e9890;line-height:1.6;margin-top:0.2rem'>"
					f"{desc}</p>",
					unsafe_allow_html=True,
				)
	else:
		st.info("No images found in data/inspiration.")

with tab2:
	st.markdown("#### Style Attributes")
	demo_list = matcher.list_demo_inspirations()
	if demo_list:
		for fname in demo_list:
			analysis = st.session_state.ai_analysis.get(fname, {})
			title = analysis.get("title", "")
			desc = analysis.get("description", "")
			attrs = analysis.get("attributes", {})
			display_label = f"{title} — {fname}" if title else fname
			st.markdown(
				f"<div style='background:#edeae5;border-radius:4px;padding:1.4rem 1.6rem;margin-bottom:0.8rem'>"
				f"<p style='font-family:Cormorant Garamond,serif;font-size:1.5rem;font-weight:400;"
				f"color:#1e1e1e;margin:0 0 0.25rem 0;line-height:1.2'>{display_label}</p>"
				+ (f"<p style='font-family:Cormorant Garamond,serif;font-size:1.05rem;font-style:italic;"
				   f"color:#6b6259;line-height:1.65;margin:0'>{desc}</p>" if desc else
				   f"<p style='font-family:Jost,sans-serif;font-size:0.82rem;color:#b0a89e;margin:0'>Analysing your aesthetic — this takes a few seconds...</p>")
				+ "</div>",
				unsafe_allow_html=True,
			)
			for k, v in attrs.items():
				st.markdown(
					f"<span style='font-family:Jost,sans-serif;font-size:0.82rem;letter-spacing:0.12em;"
					f"text-transform:uppercase;color:#6b6259'>{k}</span>",
					unsafe_allow_html=True,
				)
				st.progress(float(v))
			if analysis.get("error"):
				st.caption(f"Error: {analysis['error']}")
			st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
	else:
		st.info("No images found in data/inspiration.")
	st.divider()
	with st.expander("How this works"):
		st.write("Uploaded images are analysed by GPT-4o vision, which generates both a style description and attribute confidence scores in real time. Match results are curated to demonstrate the end-to-end pipeline.")

with tab3:
	st.markdown("#### Curated Matches")
	if uploaded:
		st.markdown(
			"<div style='background:#edeae5;border-radius:4px;padding:2.5rem 2rem;text-align:center;margin-top:1rem'>"
			"<p style='font-family:Cormorant Garamond,serif;font-size:1.6rem;font-weight:400;color:#1e1e1e;margin-bottom:0.6rem'>"
			"Your threads are on their way.</p>"
			"<p style='font-family:Jost,sans-serif;font-size:0.82rem;letter-spacing:0.1em;color:#9e9890;line-height:1.7'>"
			"This app is a prototype — real-time product matching is coming in the next update.<br>"
			"Check back soon to locate your threads.</p>"
			"</div>",
			unsafe_allow_html=True,
		)
	else:
		groups = []
		for fname in matcher.WIZARD_MAP.keys():
			m = matcher.load_matches_for(fname)
			if m:
				groups.append((fname, m))

		if not groups:
			st.info("No matches found.")
		else:
			for group_name, matches in groups:
				analysis = st.session_state.ai_analysis.get(group_name, {})
				group_title = analysis.get("title", "")
				display_group = f"{group_title} — {group_name}" if group_title else group_name
				st.markdown(f"<p style='font-size:0.68rem;letter-spacing:0.2em;text-transform:uppercase;color:#b0a89e;margin-bottom:1rem'>Inspired by &nbsp;{display_group}</p>", unsafe_allow_html=True)
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
						col.image(img, use_column_width=True)
					except Exception:
						col.write("(image missing)")

					if title:
						col.markdown(f"<span style='font-size:0.8rem;font-weight:400'>{title}</span>", unsafe_allow_html=True)
					if price or source:
						col.caption(f"{price}  {f'· {source}' if source else ''}")
					if url:
						col.markdown(f"[View listing →]({url})")
				st.divider()

