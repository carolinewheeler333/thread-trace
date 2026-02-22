import streamlit as st
from PIL import Image
import os
import io
import urllib.request
from src import matcher

st.set_page_config(layout="wide", page_title="Thread-Trace")

# Cache AI style reads so we don't re-call the API on every rerender
if "style_reads" not in st.session_state:
    st.session_state.style_reads = {}

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
        font-size: 0.7rem;
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
    url_input = st.text_input("Or paste an image URL", placeholder="https://...")

api_key = st.secrets.get("OPENAI_API_KEY", "")

# Handle URL: download and save to data/inspiration/
if url_input:
    try:
        fname = url_input.split("/")[-1].split("?")[0]
        if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
            fname = "url_image.jpg"
        save_path = os.path.join("data/inspiration", fname)
        if not os.path.exists(save_path):
            with urllib.request.urlopen(url_input) as r:
                img_bytes = r.read()
            with open(save_path, "wb") as f:
                f.write(img_bytes)
        # Get AI style read for URL image if not cached
        if fname not in st.session_state.style_reads and api_key and not api_key.startswith("sk-..."):
            with open(save_path, "rb") as f:
                img_bytes = f.read()
            with st.spinner("Reading your style..."):
                st.session_state.style_reads[fname] = matcher.get_ai_style_read(img_bytes, api_key)
    except Exception as e:
        st.error(f"Could not load image from URL: {e}")

# Handle file upload: save to data/inspiration/ and get AI style read
if uploaded:
    save_path = os.path.join("data/inspiration", uploaded.name)
    uploaded.seek(0)
    img_bytes = uploaded.read()
    uploaded.seek(0)
    with open(save_path, "wb") as f:
        f.write(img_bytes)
    if uploaded.name not in st.session_state.style_reads and api_key and not api_key.startswith("sk-..."):
        with st.spinner("Reading your style..."):
            st.session_state.style_reads[uploaded.name] = matcher.get_ai_style_read(img_bytes, api_key)

tab1, tab2, tab3 = st.tabs(["Inspiration", "AI Analysis", "Matches"])

with tab1:
	st.markdown("#### Inspirations")
	demo_list = matcher.list_demo_inspirations()
	if demo_list:
		cols = st.columns(min(3, len(demo_list)))
		for i, fname in enumerate(demo_list):
			col = cols[i % 3]
			col.image(os.path.join("data/inspiration", fname), use_column_width=True)
			style_read = st.session_state.style_reads.get(fname, "")
			if style_read:
				col.markdown(
					f"<p style='font-family:Cormorant Garamond,serif;font-size:0.85rem;"
					f"font-style:italic;color:#9e9890;line-height:1.6;margin-top:0.4rem'>"
					f"{style_read}</p>",
					unsafe_allow_html=True,
				)
			else:
				col.caption(fname)
	else:
		st.info("No images found in data/inspiration.")

with tab2:
	st.markdown("#### Style Attributes")
	demo_list = matcher.list_demo_inspirations()
	if not uploaded and demo_list:
		cols = st.columns(min(3, len(demo_list[:3])))
		for i, fname in enumerate(demo_list[:3]):
			with cols[i]:
				st.caption(fname)
				style_read = st.session_state.style_reads.get(fname, "")
				if style_read:
					st.markdown(
						f"<p style='font-family:Cormorant Garamond,serif;font-size:0.85rem;"
						f"font-style:italic;color:#6b6259;line-height:1.6;margin-bottom:0.8rem'>"
						f"{style_read}</p>",
						unsafe_allow_html=True,
					)
				analysis = matcher.simulate_analysis(fname)
				for k, v in analysis.items():
					st.markdown(f"<span style='font-size:0.7rem;letter-spacing:0.12em;text-transform:uppercase;color:#9e9890'>{k}</span>", unsafe_allow_html=True)
					st.progress(v)
	elif uploaded:
		c1, c2, c3 = st.columns([1, 2, 1])
		with c2:
			style_read = st.session_state.style_reads.get(uploaded.name, "")
			if style_read:
				st.markdown(
					f"<p style='font-family:Cormorant Garamond,serif;font-size:1.1rem;"
					f"font-style:italic;color:#6b6259;line-height:1.7;margin-bottom:1.5rem'>"
					f"{style_read}</p>",
					unsafe_allow_html=True,
				)
			analysis = matcher.simulate_analysis(uploaded.name)
			for k, v in analysis.items():
				st.markdown(f"<span style='font-size:0.7rem;letter-spacing:0.12em;text-transform:uppercase;color:#9e9890'>{k}</span>", unsafe_allow_html=True)
				st.progress(v)
	st.divider()
	with st.expander("How this works"):
		st.write("Uploaded images are described by GPT-4o vision to generate a real-time style read. Confidence attributes are extracted via simulated feature vector analysis — a Wizard-of-Oz approximation of a CLIP + FAISS pipeline.")

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
		st.info("No matches found.")
	else:
		for group_name, matches in groups:
			st.markdown(f"<p style='font-size:0.68rem;letter-spacing:0.2em;text-transform:uppercase;color:#b0a89e;margin-bottom:1rem'>Inspired by &nbsp;{group_name}</p>", unsafe_allow_html=True)
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

