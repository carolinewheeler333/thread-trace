import streamlit as st
import os
import time
from src import matcher

st.set_page_config(layout="wide", page_title="Thread-Trace")

# Load persisted analysis cache from disk into session_state on first run
if "ai_analysis" not in st.session_state:
    st.session_state.ai_analysis = matcher.load_cache()

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=Jost:wght@300;400&display=swap');

    /* ── Base — warm organic blob background ── */
    .stApp {
        background-color: #e8dfd4;
        background-image:
            radial-gradient(ellipse 100% 60% at 8%  12%, rgba(216,195,172,0.75) 0%, transparent 55%),
            radial-gradient(ellipse 70%  80% at 90% 85%, rgba(196,172,148,0.60) 0%, transparent 52%),
            radial-gradient(ellipse 55%  55% at 78% 10%, rgba(225,208,190,0.50) 0%, transparent 50%),
            radial-gradient(ellipse 65%  45% at 25% 90%, rgba(200,182,162,0.55) 0%, transparent 50%),
            radial-gradient(ellipse 40%  70% at 55% 50%, rgba(230,218,204,0.30) 0%, transparent 55%);
        color: #2c2c2c;
        font-family: 'Jost', sans-serif;
        font-weight: 300;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stToolbar"] { display: none; }

    /* ── Soft content box over the striped background ── */
    .main .block-container {
        background: rgba(245, 242, 238, 0.93);
        border-radius: 20px;
        box-shadow: 0 4px 32px rgba(44, 36, 28, 0.09);
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1.5rem !important;
    }

    /* ── Hero ── */
    .hero {
        text-align: center;
        padding: 3.5rem 0 2rem 0;
        border-bottom: 1px solid #ddd9d3;
        margin-bottom: 2rem;
        position: relative;
    }
    .hero-ornament {
        font-family: 'Cormorant Garamond', serif;
        font-size: 0.85rem;
        color: #ccc7c0;
        letter-spacing: 0.6em;
        text-transform: uppercase;
        margin-bottom: 1rem;
        display: block;
    }
    .hero h1 {
        font-family: 'Cormorant Garamond', serif;
        font-size: 5rem;
        font-weight: 300;
        letter-spacing: 0.15em;
        color: #2c2418;
        text-transform: uppercase;
        margin: 0;
        line-height: 1;
    }
    .hero .tagline {
        font-family: 'Jost', sans-serif;
        font-size: 0.72rem;
        font-weight: 300;
        letter-spacing: 0.3em;
        text-transform: uppercase;
        color: #9e9890;
        margin-top: 0.9rem;
    }
    .hero-rule {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.8rem;
        margin-top: 1.2rem;
        color: #ccc7c0;
        font-size: 0.6rem;
        letter-spacing: 0.3em;
    }
    .hero-rule::before, .hero-rule::after {
        content: '';
        display: block;
        width: 60px;
        height: 1px;
        background: #ccc7c0;
    }

    /* ── Section labels ── */
    h4 {
        font-family: 'Jost', sans-serif;
        font-size: 0.7rem;
        font-weight: 400;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: #9e9890;
        margin-bottom: 1.2rem;
    }

    /* ── Tabs ── */
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

    /* ── File uploader ── */
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

    /* ── Images ── */
    img { border-radius: 2px; }

    /* ── Custom attribute bar ── */
    .attr-row { margin-bottom: 1rem; }
    .attr-label {
        font-family: 'Jost', sans-serif;
        font-size: 0.78rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #6b6259;
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
    }
    .attr-label span.pct { color: #b0a89e; font-size: 0.7rem; }
    .attr-track {
        height: 3px;
        background: #e5e1db;
        border-radius: 0;
    }
    .attr-fill {
        height: 3px;
        background: #2c2c2c;
        border-radius: 0;
        transition: width 0.6s ease;
    }

    /* ── Expander ── */
    [data-testid="stExpander"] summary {
        font-family: 'Jost', sans-serif;
        font-size: 0.68rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #b0a89e;
    }

    /* ── Links ── */
    a {
        color: #6b6259 !important;
        text-decoration: none !important;
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        border-bottom: 1px solid #c4bfb8;
    }
    a:hover { color: #2c2c2c !important; border-bottom-color: #2c2c2c; }

    /* ── Divider ── */
    hr { border-color: #ddd9d3; margin: 2rem 0; }

    /* ── Captions ── */
    [data-testid="stCaptionContainer"] p {
        color: #9e9890;
        font-size: 0.72rem;
        letter-spacing: 0.06em;
        font-family: 'Jost', sans-serif;
    }

    /* ── Info / alert ── */
    .stAlert {
        background-color: #edeae5;
        border: none;
        color: #9e9890;
        font-size: 0.78rem;
        font-family: 'Jost', sans-serif;
    }

    /* ── Bold ── */
    strong { font-weight: 400; letter-spacing: 0.04em; }

    /* ── Column spacing ── */
    [data-testid="column"] { padding: 0 0.5rem; }

    /* ── Search query pill ── */
    .search-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: #edeae5;
        border: 1px solid #ccc7c0;
        border-radius: 20px;
        padding: 0.35rem 1rem;
        font-family: 'Jost', sans-serif;
        font-size: 0.78rem;
        letter-spacing: 0.08em;
        color: #6b6259;
        margin: 0.6rem 0 1.2rem 0;
    }
    .search-pill .label {
        color: #b0a89e;
        text-transform: uppercase;
        font-size: 0.65rem;
        letter-spacing: 0.14em;
        white-space: nowrap;
    }

    /* ── Pipeline visualization ── */
    .pipeline {
        display: flex;
        align-items: flex-start;
        gap: 0;
        margin: 1.4rem 0 0.5rem 0;
        flex-wrap: wrap;
    }
    .pipe-step {
        flex: 1;
        min-width: 140px;
        background: #edeae5;
        border-radius: 4px;
        padding: 1rem 1.1rem;
        position: relative;
    }
    .pipe-num {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.6rem;
        font-weight: 300;
        color: #ddd9d3;
        line-height: 1;
        margin-bottom: 0.3rem;
    }
    .pipe-title {
        font-family: 'Jost', sans-serif;
        font-size: 0.72rem;
        font-weight: 400;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #2c2c2c;
        margin-bottom: 0.3rem;
    }
    .pipe-desc {
        font-family: 'Jost', sans-serif;
        font-size: 0.72rem;
        color: #9e9890;
        line-height: 1.5;
    }
    .pipe-model {
        display: inline-block;
        margin-top: 0.5rem;
        font-family: 'Jost', sans-serif;
        font-size: 0.62rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #b0a89e;
        background: #f5f2ee;
        border-radius: 10px;
        padding: 0.1rem 0.5rem;
    }
    .pipe-arrow {
        display: flex;
        align-items: center;
        padding: 0 0.4rem;
        color: #ccc7c0;
        font-size: 1.1rem;
        padding-top: 1rem;
        flex-shrink: 0;
    }

    /* ── Relevance badge ── */
    .rel-badge {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 10px;
        font-family: 'Jost', sans-serif;
        font-size: 0.68rem;
        letter-spacing: 0.06em;
        font-weight: 400;
        margin-bottom: 0.3rem;
    }
    .rel-high { background: #d6edd6; color: #3a6b3a; }
    .rel-mid  { background: #f0ecd6; color: #7a6b2a; }
    .rel-low  { background: #ede5e5; color: #7a3a3a; }

    /* ── Source badge ── */
    .src-badge {
        display: inline-block;
        padding: 0.1rem 0.5rem;
        border-radius: 8px;
        font-family: 'Jost', sans-serif;
        font-size: 0.62rem;
        letter-spacing: 0.08em;
        font-weight: 400;
        text-transform: uppercase;
        margin-left: 0.3rem;
    }
    .src-etsy { background: #faeee4; color: #c36b27; }
    .src-ebay { background: #e4eef7; color: #1a4e8c; }
    .src-other { background: #edeae5; color: #9e9890; }

    /* ── Match card hover ── */
    .match-card {
        background: #fff;
        border-radius: 4px;
        overflow: hidden;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
        margin-bottom: 0.8rem;
    }
    .match-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.07);
    }
    .match-card-body {
        padding: 0.7rem 0.7rem 0.4rem 0.7rem;
    }

    /* ── Upload summary card ── */
    .upload-card {
        background: #edeae5;
        border-radius: 4px;
        padding: 1.4rem;
        height: 100%;
    }

    /* ── Feedback stats bar ── */
    .feedback-bar {
        background: #edeae5;
        border-radius: 4px;
        padding: 1rem 1.5rem;
        font-family: 'Jost', sans-serif;
        font-size: 0.8rem;
        color: #9e9890;
        letter-spacing: 0.06em;
        margin-top: 2rem;
    }

    /* ── All small buttons (feedback + remove) ── */
    .stButton > button {
        background: transparent !important;
        border: 1px solid #ddd9d3 !important;
        border-radius: 20px !important;
        color: #9e9890 !important;
        font-size: 0.75rem !important;
        padding: 0.15rem 0.6rem !important;
        font-family: 'Jost', sans-serif !important;
        letter-spacing: 0.05em !important;
        transition: border-color 0.15s, color 0.15s, background 0.15s !important;
        min-height: 0 !important;
        height: auto !important;
    }
    .stButton > button:hover {
        border-color: #2c2c2c !important;
        color: #2c2c2c !important;
        background: transparent !important;
    }
    /* Remove button — red tint on hover */
    .stButton > button[kind="secondary"]:has-text("Remove"):hover,
    .remove-btn .stButton > button:hover {
        border-color: #c0574a !important;
        color: #c0574a !important;
    }

    /* ── Archive grid (Inspiration tab) ── */
    .archive-grid {
        display: flex;
        gap: 3px;
        align-items: stretch;
        height: 520px;
        overflow: hidden;
        border-radius: 4px;
    }
    .archive-card {
        position: relative;
        flex: 1;
        overflow: hidden;
        cursor: pointer;
        display: block;
        text-decoration: none !important;
        border: none !important;
        background: #1a1814;
        min-width: 0;
        transition: flex 0.4s cubic-bezier(0.4,0,0.2,1);
    }
    .archive-card:hover {
        flex: 2.2;
    }
    .archive-card img {
        display: block;
        width: 100%;
        height: 100%;
        object-fit: cover;
        opacity: 0.82;
        transition: opacity 0.35s ease, transform 0.45s ease;
        border-radius: 0 !important;
    }
    .archive-card:hover img {
        opacity: 0.55;
        transform: scale(1.06);
    }
    /* Top label — always visible */
    .archive-label {
        position: absolute;
        top: 0; left: 0; right: 0;
        background: linear-gradient(180deg, rgba(14,12,10,0.96) 0%, transparent 100%);
        padding: 0.8rem 0.75rem 2rem 0.75rem;
        z-index: 2;
        pointer-events: none;
    }
    .archive-code {
        display: block;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.52rem;
        letter-spacing: 0.2em;
        color: #7a7268;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
        white-space: nowrap;
    }
    .archive-title {
        display: block;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.6rem;
        letter-spacing: 0.1em;
        color: #d8d2c8;
        text-transform: uppercase;
        line-height: 1.4;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    /* Bottom panel — hidden, slides up on hover */
    .archive-footer {
        position: absolute;
        bottom: 0; left: 0; right: 0;
        background: linear-gradient(0deg, rgba(14,12,10,0.97) 0%, rgba(14,12,10,0.6) 60%, transparent 100%);
        padding: 3rem 0.75rem 0.9rem 0.75rem;
        z-index: 2;
        transform: translateY(100%);
        transition: transform 0.35s cubic-bezier(0.4,0,0.2,1);
        pointer-events: none;
    }
    .archive-card:hover .archive-footer {
        transform: translateY(0);
    }
    .archive-desc {
        font-family: 'Cormorant Garamond', serif;
        font-size: 0.78rem;
        font-style: italic;
        color: #c8c2b8;
        line-height: 1.55;
        margin-bottom: 0.5rem;
    }
    .archive-attrs {
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.5rem;
        letter-spacing: 0.16em;
        color: #7a7268;
        text-transform: uppercase;
        line-height: 1.8;
    }
    .archive-open-hint {
        font-family: 'Jost', sans-serif;
        font-size: 0.55rem;
        letter-spacing: 0.22em;
        color: #e8e2d8;
        text-transform: uppercase;
        margin-top: 0.6rem;
        display: block;
        opacity: 0.8;
    }

    /* ── Quick-view modal (CSS :target) ── */
    .modal-overlay {
        display: none;
        position: fixed;
        inset: 0;
        z-index: 9999;
        align-items: center;
        justify-content: center;
        padding: 1.5rem;
    }
    .modal-overlay:target { display: flex; }

    .modal-backdrop {
        position: absolute;
        inset: 0;
        background: rgba(28, 22, 16, 0.72);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
    }
    .modal-panel {
        position: relative;
        z-index: 10;
        background: #f8f4ef;
        border-radius: 10px;
        max-width: 860px;
        width: 100%;
        max-height: 86vh;
        overflow: hidden;
        display: flex;
        box-shadow: 0 32px 80px rgba(0,0,0,0.28);
    }
    .modal-img-side {
        width: 42%;
        flex-shrink: 0;
        position: relative;
    }
    .modal-img-side img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
        border-radius: 0 !important;
    }
    .modal-info-side {
        flex: 1;
        padding: 2.2rem 2rem 1.6rem 2rem;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 0;
    }
    .modal-close {
        position: absolute;
        top: 0.9rem;
        right: 0.9rem;
        z-index: 20;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(248,244,239,0.88);
        border-radius: 50%;
        font-family: 'Jost', sans-serif;
        font-size: 1rem;
        color: #6b6259 !important;
        text-decoration: none !important;
        border: none !important;
        line-height: 1;
        transition: background 0.15s;
    }
    .modal-close:hover { background: #edeae5; color: #2c2c2c !important; }

    .modal-code-label {
        font-family: 'Courier New', monospace;
        font-size: 0.52rem;
        letter-spacing: 0.22em;
        color: #b0a89e;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }
    .modal-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 2.4rem;
        font-weight: 400;
        color: #2c2418;
        line-height: 1.1;
        margin: 0 0 0.3rem 0;
    }
    .modal-desc {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1rem;
        font-style: italic;
        color: #6b6259;
        line-height: 1.7;
        margin: 0.5rem 0 1.2rem 0;
    }
    .modal-attr-row { margin-bottom: 0.7rem; }
    .modal-attr-label {
        font-family: 'Jost', sans-serif;
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #6b6259;
        display: flex;
        justify-content: space-between;
        margin-bottom: 3px;
    }
    .modal-attr-label span.pct { color: #b0a89e; font-size: 0.68rem; }
    .modal-attr-track {
        height: 2px;
        background: #e5e1db;
        border-radius: 0;
    }
    .modal-attr-fill {
        height: 2px;
        background: #8c7b6b;
        border-radius: 0;
    }
    .modal-actions {
        display: flex;
        gap: 0.6rem;
        margin-top: auto;
        padding-top: 1.3rem;
        border-top: 1px solid #ddd9d3;
        flex-wrap: wrap;
    }
    .modal-btn {
        display: inline-block;
        padding: 0.48rem 1.1rem;
        border: 1px solid #2c2c2c;
        border-radius: 20px;
        font-family: 'Jost', sans-serif;
        font-size: 0.7rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #2c2c2c !important;
        text-decoration: none !important;
        transition: background 0.18s, color 0.18s;
    }
    .modal-btn:hover {
        background: #2c2c2c !important;
        color: #f8f4ef !important;
        border-color: #2c2c2c !important;
    }
    .modal-btn-ghost {
        border-color: #ccc7c0;
        color: #9e9890 !important;
    }
    .modal-btn-ghost:hover {
        background: #edeae5 !important;
        color: #2c2c2c !important;
        border-color: #9e9890 !important;
    }

    /* ── Sketchbook Outfit Board ──────────────────────────────────────── */
    .sketchbook-header {
        font-family: 'Jost', sans-serif;
        font-size: 0.58rem;
        letter-spacing: 0.45em;
        text-transform: uppercase;
        color: #b0a89e;
        display: flex;
        align-items: center;
        gap: 1.2rem;
        margin-bottom: 1.8rem;
    }
    .sketchbook-header-rule { flex: 1; height: 1px; background: #ccc7c0; }

    /* Polaroid photo cards */
    .polaroid {
        background: #fff;
        padding: 4px 4px 18px 4px;
        box-shadow: 2px 3px 8px rgba(44,32,12,0.16);
        display: inline-block;
        position: relative;
    }
    .polaroid img {
        width: 100%;
        display: block;
        aspect-ratio: 3/4;
        object-fit: cover;
    }
    .polaroid-hero { display: block; }
    .polaroid-hero img { aspect-ratio: 2/3; }
    .polaroid-caption {
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 0.72rem;
        color: #8a7a6a;
        text-align: center;
        padding-top: 3px;
    }
    .tilt-l1 { transform: rotate(-1.8deg); }
    .tilt-r1 { transform: rotate(1.3deg); }
    .tilt-l2 { transform: rotate(-0.6deg); }
    .tilt-r2 { transform: rotate(1.9deg); }
    .tilt-l3 { transform: rotate(-1.2deg); }

    /* Sticky notes */
    .sticky {
        padding: 0.6rem 0.85rem 0.8rem;
        box-shadow: 1px 2px 6px rgba(44,32,12,0.11);
        border: 1px solid rgba(44,32,12,0.06);
        position: relative;
        margin-bottom: 0.7rem;
    }
    .sticky-rose     { background: #e8e0d4; transform: rotate(-1deg); }
    .sticky-sage     { background: #e3ddd5; transform: rotate(0.6deg); }
    .sticky-lavender { background: #e6e0d8; transform: rotate(-0.3deg); }
    .sticky-num {
        font-family: 'Jost', sans-serif;
        font-size: 0.55rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #a89e90;
        margin: 0 0 0.15rem 0;
    }
    .sticky-title {
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 1.2rem;
        font-weight: 400;
        color: #2c2420;
        margin: 0 0 0.2rem 0;
        line-height: 1.2;
    }
    .sticky-body {
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 0.82rem;
        color: #6b5e54;
        line-height: 1.55;
        margin: 0;
    }
    .sticky-hero-title {
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 1.45rem;
        font-weight: 400;
        color: #2c2420;
        margin: 0 0 0.3rem 0;
        line-height: 1.15;
    }
    .sticky-hero-sub {
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 0.85rem;
        color: #6b5e54;
        line-height: 1.6;
        margin: 0 0 0.35rem 0;
    }
    .sticky-footer {
        font-family: 'Jost', sans-serif;
        font-size: 0.55rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #a89e90;
        margin: 0.45rem 0 0 0;
    }

    /* Saved badge */
    .saved-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-family: 'Jost', sans-serif;
        font-size: 0.58rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #7a6a30;
        background: #f5edd0;
        border: 1px solid #d4c07a;
        padding: 4px 12px;
        border-radius: 2px;
        margin-bottom: 1.8rem;
    }

    /* Outfit board editorial layout */
    .outfit-board { display:flex; gap:1.4rem; align-items:flex-start; }
    .ob-left { flex: 0 0 180px; }
    .ob-right { flex:1; display:flex; flex-direction:column; gap:0.8rem; }
    .ob-piece-row { display:flex; gap:0.9rem; align-items:flex-start; }
    .ob-piece-sticky { flex: 0 0 155px; margin:0 !important; }
    .ob-products { flex:1; display:flex; flex-wrap:wrap; gap:8px; align-items:flex-start; }

    /* Saved looks thumbnails */
    .saved-polaroid {
        background: #fff;
        padding: 5px 5px 20px 5px;
        box-shadow: 2px 3px 8px rgba(44,32,12,0.15);
        display: block;
        text-decoration: none;
    }
    .saved-polaroid img {
        width: 100%;
        aspect-ratio: 3/4;
        object-fit: cover;
        display: block;
    }
    .saved-polaroid-label {
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 0.78rem;
        color: #6b5e54;
        text-align: center;
        padding-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <span class="hero-ornament">— est. 2025 —</span>
    <h1>Thread&thinsp;Trace</h1>
    <div class="tagline">Mood &nbsp;·&nbsp; Match &nbsp;·&nbsp; Marketplace</div>
    <div class="hero-rule">✦</div>
</div>
""", unsafe_allow_html=True)

col_left, col_mid, col_right = st.columns([1, 2, 1])
with col_mid:
    uploaded = st.file_uploader("Upload a mood or Pinterest image", type=["jpg", "jpeg", "png"])

# API keys
api_key     = st.secrets.get("OPENAI_API_KEY", "")
etsy_key    = st.secrets.get("ETSY_API_KEY", "")
ebay_app_id = st.secrets.get("EBAY_APP_ID", "")

_api_key_valid = bool(api_key and not api_key.startswith("sk-...") and len(api_key) > 20)


# Helper: source badge HTML
def source_badge(source: str) -> str:
    cls = {"Etsy": "src-etsy", "eBay": "src-ebay"}.get(source, "src-other")
    return f"<span class='src-badge {cls}'>{source}</span>" if source else ""


# Helper: custom attribute bar HTML
def attr_bar(label: str, value: float) -> str:
    pct = int(value * 100)
    return (
        f"<div class='attr-row'>"
        f"<div class='attr-label'><span>{label}</span><span class='pct'>{pct}%</span></div>"
        f"<div class='attr-track'><div class='attr-fill' style='width:{pct}%'></div></div>"
        f"</div>"
    )


# Helper: archive card HTML (Inspiration tab)
import base64 as _b64

def _safe_modal_id(fname: str) -> str:
    """Turn a filename into a safe HTML id for the :target modal."""
    return "modal-" + fname.replace(".", "-").replace(" ", "-").replace("_", "-")


def _load_b64(fname: str):
    """Return (data_uri, mime) for an inspiration image, or (None, None)."""
    img_path = os.path.join("data/inspiration", fname)
    try:
        with open(img_path, "rb") as f:
            b64 = _b64.b64encode(f.read()).decode()
        ext  = fname.rsplit(".", 1)[-1].lower()
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
        return f"data:{mime};base64,{b64}", mime
    except Exception:
        return None, None


def archive_card_html(fname: str, index: int, analysis: dict) -> str:
    """Archive strip card — clicking opens the quick-view modal."""
    data_uri, _ = _load_b64(fname)
    if not data_uri:
        return ""

    modal_id  = _safe_modal_id(fname)
    code_num  = f"CODE_{index+1:03d} //"
    title     = (analysis.get("title") or fname).upper()
    attrs     = analysis.get("attributes", {})
    top_attrs = sorted(attrs.items(), key=lambda x: x[1], reverse=True)[:2]
    attr_str  = " · ".join(k.upper() for k, _ in top_attrs) if top_attrs else ""
    desc      = analysis.get("description", "")

    return (
        f"<a class='archive-card' href='#{modal_id}'>"
        f"  <div class='archive-label'>"
        f"    <span class='archive-code'>{code_num}</span>"
        f"    <span class='archive-title'>{title}</span>"
        f"  </div>"
        f"  <img src='{data_uri}' alt='{fname}' />"
        f"  <div class='archive-footer'>"
        + (f"    <div class='archive-desc'>{desc}</div>" if desc else "")
        + f"    <div class='archive-attrs'>{attr_str}</div>"
        f"    <span class='archive-open-hint'>✦ quick view</span>"
        f"  </div>"
        f"</a>"
    )


def archive_modal_html(fname: str, index: int, analysis: dict) -> str:
    """Full-screen quick-view modal for one inspiration image.

    Uses the CSS :target trick — the modal is hidden until its id matches
    the URL hash. Clicking the backdrop or × clears the hash (href='#').
    """
    data_uri, _ = _load_b64(fname)
    if not data_uri:
        return ""

    modal_id   = _safe_modal_id(fname)
    code_num   = f"CODE_{index+1:03d} //"
    title      = analysis.get("title") or fname
    desc       = analysis.get("description", "")
    attrs      = analysis.get("attributes", {})
    sq         = analysis.get("search_query", "")

    # Attribute bars HTML
    attr_bars = ""
    for k, v in attrs.items():
        pct = int(v * 100)
        attr_bars += (
            f"<div class='modal-attr-row'>"
            f"<div class='modal-attr-label'><span>{k}</span>"
            f"<span class='pct'>{pct}%</span></div>"
            f"<div class='modal-attr-track'>"
            f"<div class='modal-attr-fill' style='width:{pct}%'></div>"
            f"</div></div>"
        )

    sq_pill = (
        f"<div class='search-pill' style='margin:1rem 0 0 0;font-size:0.7rem'>"
        f"<span class='label'>Searching for</span>{sq}</div>"
    ) if sq else ""

    return (
        f"<div id='{modal_id}' class='modal-overlay'>"
        f"  <a href='#' class='modal-backdrop'></a>"
        f"  <div class='modal-panel'>"
        f"    <a href='#' class='modal-close'>×</a>"
        f"    <div class='modal-img-side'>"
        f"      <img src='{data_uri}' alt='{title}' />"
        f"    </div>"
        f"    <div class='modal-info-side'>"
        f"      <div class='modal-code-label'>{code_num}</div>"
        f"      <div class='modal-title'>{title}</div>"
        + (f"<p class='modal-desc'>{desc}</p>" if desc else "")
        + attr_bars
        + sq_pill
        + f"    <div class='modal-actions'>"
        f"        <a href='#goto-matches' class='modal-btn'>View Matches →</a>"
        f"        <a href='#goto-outfit' class='modal-btn modal-btn-ghost'>Outfit Builder →</a>"
        f"    </div>"
        f"    </div>"
        f"  </div>"
        f"</div>"
    )


# Pipeline
def run_ai_analysis(fname, img_bytes):
    """Run the full pipeline for one image and persist to cache.

    Steps:
      1. GPT-4o vision → style JSON               (LLM #1)
      2. GPT-4o-mini   → retail search query       (LLM #2)
      3. Etsy / eBay   → live second-hand listings
      4. GPT-4o-mini   → relevance score per item  (LLM #3)
    """
    cached     = st.session_state.ai_analysis.get(fname, {})
    needs_ai   = not cached or cached.get("error")
    # Don't retry marketplace search if we already attempted it (avoids burning API quota
    # on every reload). Re-run only if we have no query yet or no previous attempt recorded.
    needs_live = (
        not cached.get("search_attempted")
        and not cached.get("live_matches")
        and (etsy_key or ebay_app_id)
    )

    if not _api_key_valid:
        return

    if needs_ai:
        with st.spinner("Analysing your aesthetic…"):
            result = matcher.get_ai_analysis(img_bytes, api_key)
        st.session_state.ai_analysis[fname] = result
        cached = result
        needs_live = bool(etsy_key or ebay_app_id)

    if needs_live and not cached.get("error"):
        with st.spinner("Generating search query…"):
            q = matcher.generate_search_query(cached, api_key)
            cached["search_query"]    = q.get("query", "")
            cached["search_category"] = q.get("category", "")

        # Mark as attempted BEFORE the call so a rate-limit error doesn't cause
        # infinite retries on every page reload.
        cached["search_attempted"] = True
        st.session_state.ai_analysis[fname] = cached
        matcher.save_cache(st.session_state.ai_analysis)

        with st.spinner(f"Searching marketplaces for \"{cached['search_query']}\"…"):
            live = matcher.search_live(
                cached["search_query"],
                etsy_key=etsy_key,
                ebay_app_id=ebay_app_id,
            )

        if live:
            # Filter out error sentinel before scoring
            errors = [m for m in live if m.get("error")]
            real   = [m for m in live if not m.get("error")]
            if errors:
                cached["_search_error"] = errors[0]["error"]
            if real:
                with st.spinner("Scoring relevance…"):
                    cached["live_matches"] = matcher.score_match_relevance(real, cached, api_key)
            else:
                cached["live_matches"] = []
        else:
            cached["live_matches"] = []

        st.session_state.ai_analysis[fname] = cached

    matcher.save_cache(st.session_state.ai_analysis)


# Handle file upload
if uploaded:
    save_path = os.path.join("data/inspiration", uploaded.name)
    uploaded.seek(0)
    img_bytes = uploaded.read()
    uploaded.seek(0)
    with open(save_path, "wb") as f:
        f.write(img_bytes)
    run_ai_analysis(uploaded.name, img_bytes)

# Run AI analysis for demo images
for demo_fname in matcher.list_demo_inspirations():
    demo_cached = st.session_state.ai_analysis.get(demo_fname, {})
    if not demo_cached or demo_cached.get("error"):
        demo_path = os.path.join("data/inspiration", demo_fname)
        if os.path.exists(demo_path):
            with open(demo_path, "rb") as f:
                demo_bytes = f.read()
            run_ai_analysis(demo_fname, demo_bytes)
            time.sleep(2)

# Tabs
tab1, tab2, tab3 = st.tabs(["Inspiration", "Matches", "Outfit Builder"])

# Tab navigation helper (modal buttons → JS clicks the right Streamlit tab)
import streamlit.components.v1 as _components
_components.html("""
<script>
(function() {
  function clickTab(label) {
    var tabs = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
    for (var i = 0; i < tabs.length; i++) {
      if (tabs[i].innerText.trim().toUpperCase() === label.toUpperCase()) {
        tabs[i].click();
        break;
      }
    }
  }

  function handleHash() {
    var h = window.parent.location.hash;
    if (h === '#goto-matches') {
      setTimeout(function() {
        clickTab('Matches');
        window.parent.history.replaceState(null, '', window.parent.location.pathname);
      }, 80);
    } else if (h === '#goto-outfit') {
      setTimeout(function() {
        clickTab('Outfit Builder');
        window.parent.history.replaceState(null, '', window.parent.location.pathname);
      }, 80);
    }
  }

  window.parent.addEventListener('hashchange', handleHash);
  handleHash(); // handle on initial load too
})();
</script>
""", height=0)

# Tab 1: Inspiration
with tab1:
    st.markdown("#### Your Closet")
    st.markdown(
        "<p style='font-family:Cormorant Garamond,serif;font-style:italic;font-size:0.9rem;"
        "color:#9e9890;margin:-0.8rem 0 1.4rem 0'>Click any image to view AI style analysis "
        "and navigate to matches or outfit suggestions.</p>",
        unsafe_allow_html=True,
    )
    demo_list = matcher.list_demo_inspirations()
    if demo_list:
        # Archive grid + modals (all in one HTML block so :target works)
        html_block = "<div class='archive-grid'>"
        for i, fname in enumerate(demo_list):
            analysis = st.session_state.ai_analysis.get(fname, {})
            html_block += archive_card_html(fname, i, analysis)
        html_block += "</div>"
        # Modals rendered outside the grid but inside the same markdown block
        for i, fname in enumerate(demo_list):
            analysis = st.session_state.ai_analysis.get(fname, {})
            html_block += archive_modal_html(fname, i, analysis)
        st.markdown(html_block, unsafe_allow_html=True)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

        # Delete buttons row
        st.markdown(
            "<p style='font-family:Jost,sans-serif;font-size:0.62rem;letter-spacing:0.18em;"
            "text-transform:uppercase;color:#b0a89e;margin-bottom:0.5rem'>Remove from closet</p>",
            unsafe_allow_html=True,
        )
        del_cols = st.columns(len(demo_list))
        for i, fname in enumerate(demo_list):
            label = (st.session_state.ai_analysis.get(fname, {}).get("title") or fname)
            short = label[:18] + "…" if len(label) > 18 else label
            if del_cols[i].button(f"× {short}", key=f"del_{fname}"):
                matcher.delete_image(fname)
                if fname in st.session_state.ai_analysis:
                    del st.session_state.ai_analysis[fname]
                st.rerun()
    else:
        st.info("No images in your closet yet — upload one above!")

# Tab 2: Matches
with tab2:
    st.markdown("#### Found for You")

    # Uploaded image: live pipeline results
    if uploaded:
        cached       = st.session_state.ai_analysis.get(uploaded.name, {})
        live_matches = cached.get("live_matches", [])
        search_query = cached.get("search_query", "")
        style_title  = cached.get("title", "")
        style_desc   = cached.get("description", "")

        if live_matches:
            # Side-by-side: upload summary card | match cards
            c_img, c_matches = st.columns([1, 2])

            with c_img:
                uploaded.seek(0)
                st.image(uploaded, use_column_width=True)
                st.markdown(
                    f"<div class='upload-card' style='margin-top:0.8rem'>"
                    + (f"<p style='font-family:Cormorant Garamond,serif;font-size:1.3rem;"
                       f"font-weight:400;color:#1e1e1e;margin:0 0 0.4rem 0'>{style_title}</p>"
                       if style_title else "")
                    + (f"<p style='font-family:Cormorant Garamond,serif;font-size:0.95rem;"
                       f"font-style:italic;color:#6b6259;line-height:1.6;margin:0 0 0.8rem 0'>"
                       f"{style_desc}</p>"
                       if style_desc else "")
                    + (f"<div class='search-pill' style='margin:0'>"
                       f"<span class='label'>Searched for</span>{search_query}</div>"
                       if search_query else "")
                    + "</div>",
                    unsafe_allow_html=True,
                )

            with c_matches:
                n_cols = min(3, len(live_matches))
                match_cols = st.columns(n_cols)
                for i, item in enumerate(live_matches):
                    col     = match_cols[i % n_cols]
                    img_url = item.get("img", "")
                    title   = item.get("title", "")
                    price   = item.get("price", "")
                    url     = item.get("url", "")
                    source  = item.get("source", "")
                    score   = item.get("relevance_score", 0)
                    reason  = item.get("relevance_reason", "")

                    badge_cls = "rel-high" if score >= 70 else ("rel-mid" if score >= 50 else "rel-low")

                    # Card wrapper
                    col.markdown("<div class='match-card'>", unsafe_allow_html=True)
                    try:
                        col.image(img_url, use_column_width=True)
                    except Exception:
                        col.write("(image unavailable)")

                    col.markdown(
                        f"<div class='match-card-body'>"
                        f"<div style='display:flex;align-items:center;gap:0.4rem;flex-wrap:wrap;"
                        f"margin-bottom:0.3rem'>"
                        f"<span class='rel-badge {badge_cls}'>{score}% match</span>"
                        f"{source_badge(source)}"
                        f"</div>"
                        + (f"<p style='font-family:Jost,sans-serif;font-size:0.78rem;"
                           f"color:#2c2c2c;margin:0 0 0.2rem 0;line-height:1.4'>{title}</p>"
                           if title else "")
                        + (f"<p style='font-family:Jost,sans-serif;font-size:0.7rem;"
                           f"color:#9e9890;margin:0 0 0.2rem 0;font-style:italic'>{reason}</p>"
                           if reason else "")
                        + (f"<p style='font-family:Jost,sans-serif;font-size:0.72rem;"
                           f"color:#6b6259;margin:0 0 0.4rem 0;font-weight:400'>{price}</p>"
                           if price else "")
                        + (f"<a href='{url}' target='_blank'>View listing →</a>"
                           if url else "")
                        + "</div></div>",
                        unsafe_allow_html=True,
                    )

                    # Feedback buttons
                    fb1, fb2 = col.columns(2)
                    if fb1.button("👍", key=f"up_{uploaded.name}_{i}"):
                        matcher.log_feedback(uploaded.name, title, url, "up")
                        st.toast("Thanks for your feedback!")
                    if fb2.button("👎", key=f"dn_{uploaded.name}_{i}"):
                        matcher.log_feedback(uploaded.name, title, url, "down")
                        st.toast("Thanks for your feedback!")

            st.divider()

        elif not etsy_key and not ebay_app_id:
            st.markdown(
                "<div style='background:#edeae5;border-radius:4px;padding:2.5rem 2rem;"
                "text-align:center;margin:1rem 0 2rem 0'>"
                "<p style='font-family:Cormorant Garamond,serif;font-size:1.6rem;"
                "font-weight:400;color:#1e1e1e;margin-bottom:0.6rem'>Live matching is almost ready.</p>"
                "<p style='font-family:Jost,sans-serif;font-size:0.82rem;letter-spacing:0.1em;"
                "color:#9e9890;line-height:1.7'>Add your Etsy or eBay API key to "
                "<code>.streamlit/secrets.toml</code> to fetch real second-hand listings.</p>"
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            search_error = cached.get("_search_error", "")
            if search_error:
                # Show a friendly message for rate limit errors
                if "exceeded" in search_error.lower() or "rate" in search_error.lower():
                    st.markdown(
                        "<div style='background:#edeae5;border-radius:4px;padding:2rem;"
                        "text-align:center;margin:1rem 0'>"
                        "<p style='font-family:Cormorant Garamond,serif;font-size:1.4rem;"
                        "font-weight:400;color:#1e1e1e;margin-bottom:0.5rem'>"
                        "eBay daily limit reached.</p>"
                        "<p style='font-family:Jost,sans-serif;font-size:0.8rem;"
                        "letter-spacing:0.08em;color:#9e9890;line-height:1.7'>"
                        "New eBay developer accounts have a small daily call quota. "
                        "The limit resets every 24 hours — try again tomorrow, "
                        "or add an Etsy API key for unlimited searches in the meantime.</p>"
                        "</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.warning(f"Marketplace search error: {search_error}")
            else:
                st.info("No results found for your image. Try a clearer photo of a single garment.")

    # Demo inspirations: curated matches
    groups = [(fname, matcher.load_matches_for(fname)) for fname in matcher.WIZARD_MAP if matcher.load_matches_for(fname)]

    if groups:
        st.markdown(
            "<p style='font-size:0.65rem;letter-spacing:0.2em;text-transform:uppercase;"
            "color:#b0a89e;margin-bottom:1.2rem'>Demo inspirations</p>",
            unsafe_allow_html=True,
        )
        for group_name, matches in groups:
            analysis    = st.session_state.ai_analysis.get(group_name, {})
            group_title = analysis.get("title", "") or group_name
            st.markdown(
                f"<p style='font-size:0.65rem;letter-spacing:0.2em;text-transform:uppercase;"
                f"color:#b0a89e;margin-bottom:0.8rem'>Inspired by &nbsp;{group_title}</p>",
                unsafe_allow_html=True,
            )
            cols = st.columns(min(4, len(matches)))
            for i, item in enumerate(matches):
                if isinstance(item, dict):
                    img    = item.get("img")
                    title  = item.get("title", "")
                    price  = item.get("price", "")
                    url    = item.get("url", "")
                    source = item.get("source", "")
                else:
                    img    = item
                    title  = os.path.basename(str(item))
                    price  = ""
                    url    = ""
                    source = ""

                col = cols[i % 4]
                col.markdown("<div class='match-card'>", unsafe_allow_html=True)
                try:
                    col.image(img, use_column_width=True)
                except Exception:
                    col.write("(image missing)")

                col.markdown(
                    f"<div class='match-card-body'>"
                    + (f"<p style='font-family:Jost,sans-serif;font-size:0.78rem;"
                       f"color:#2c2c2c;margin:0 0 0.2rem 0;line-height:1.4'>{title}</p>"
                       if title else "")
                    + (f"<p style='font-family:Jost,sans-serif;font-size:0.72rem;"
                       f"color:#6b6259;margin:0 0 0.2rem 0;font-weight:400'>{price}</p>"
                       if price else "")
                    + (f"<span style='font-family:Jost,sans-serif;font-size:0.65rem;"
                       f"color:#9e9890;letter-spacing:0.06em'>"
                       + source_badge(source) + f"</span>"
                       if source else "")
                    + (f"<br><a href='{url}' target='_blank' style='margin-top:0.3rem;"
                       f"display:inline-block'>View listing →</a>"
                       if url else "")
                    + "</div></div>",
                    unsafe_allow_html=True,
                )
            st.divider()

    # Feedback stats
    stats = matcher.load_feedback_stats()
    if stats["total"] > 0:
        st.markdown(
            f"<div class='feedback-bar'>"
            f"User feedback &nbsp;·&nbsp; {stats['total']} ratings &nbsp;·&nbsp; "
            f"<strong>{stats['pct']}% found relevant</strong>"
            f"</div>",
            unsafe_allow_html=True,
        )

# Tab 3: Outfit Builder
with tab3:
    st.markdown("#### Outfit Builder")

    if not uploaded:
        st.markdown(
            "<div style='text-align:center;padding:3rem 1rem'>"
            "<p style='font-family:Cormorant Garamond,serif;font-size:1.5rem;"
            "font-weight:400;color:#b0a89e'>Upload an image to build your outfit.</p>"
            "<p style='font-family:Jost,sans-serif;font-size:0.78rem;color:#ccc7c0;"
            "letter-spacing:0.1em'>Thread-Trace will suggest complementary second-hand pieces.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
    elif not _api_key_valid:
        st.info("Add an OpenAI API key to use the Outfit Builder.")
    else:
        cached       = st.session_state.ai_analysis.get(uploaded.name, {})
        style_title  = cached.get("title", "")
        suggestions  = cached.get("outfit_suggestions", [])
        outfit_matches = cached.get("outfit_matches", {})

        # Generate suggestions if not yet cached
        if cached and not cached.get("error") and not suggestions and not cached.get("outfit_attempted"):
            with st.spinner("Styling your outfit…"):
                suggestions = matcher.generate_outfit_suggestions(cached, api_key)
            cached["outfit_suggestions"] = suggestions
            cached["outfit_attempted"]   = True
            st.session_state.ai_analysis[uploaded.name] = cached
            matcher.save_cache(st.session_state.ai_analysis)

        # Fetch Etsy results for each suggestion (Etsy only — no eBay quota used)
        if suggestions and etsy_key:
            for idx, s in enumerate(suggestions):
                key = str(idx)
                if key not in outfit_matches and not cached.get(f"outfit_fetched_{key}"):
                    with st.spinner(f"Finding {s['piece']}…"):
                        raw  = matcher.search_etsy_used(s["query"], etsy_key, n=4)
                        scored = matcher.score_match_relevance(raw, cached, api_key) if raw else []
                        outfit_matches[key] = scored
                    cached["outfit_matches"]           = outfit_matches
                    cached[f"outfit_fetched_{key}"]    = True
                    st.session_state.ai_analysis[uploaded.name] = cached
                    matcher.save_cache(st.session_state.ai_analysis)

        # Display
        if suggestions:
            import base64 as _b64_outfit
            _tilts       = ["tilt-l1", "tilt-r1", "tilt-l2", "tilt-r2", "tilt-l3"]
            _sticky_cls  = ["sticky-rose", "sticky-sage", "sticky-lavender"]
            _ordinals    = ["01", "02", "03", "04"]

            # Saved badge
            st.markdown(
                "<div class='saved-badge'>✓ &nbsp; Saved to your closet</div>",
                unsafe_allow_html=True,
            )

            # Header rule
            st.markdown(
                "<div class='sketchbook-header'>"
                "<span class='sketchbook-header-rule'></span>"
                "<span>Outfit Board</span>"
                "<span class='sketchbook-header-rule'></span>"
                "</div>",
                unsafe_allow_html=True,
            )

            # Build base64 for hero image
            uploaded.seek(0)
            _img_b64 = _b64_outfit.b64encode(uploaded.read()).decode()
            _ext  = uploaded.name.rsplit(".", 1)[-1].lower()
            _mime = "image/jpeg" if _ext in ("jpg", "jpeg") else f"image/{_ext}"
            _desc = cached.get("description", "")

            # Build right-column piece rows as a string first
            _right_html = ""
            for idx, s in enumerate(suggestions):
                key     = str(idx)
                piece   = s.get("piece", "")
                why     = s.get("why", "")
                results = outfit_matches.get(key, [])
                _sc     = _sticky_cls[idx % len(_sticky_cls)]
                _num    = _ordinals[idx] if idx < len(_ordinals) else str(idx+1).zfill(2)

                _right_html += (
                    f"<div class='ob-piece-row'>"
                    f"  <div class='ob-piece-sticky sticky {_sc}'>"
                    f"    <p class='sticky-num'>{_num}</p>"
                    f"    <p class='sticky-title'>{piece}</p>"
                    f"    <p class='sticky-body'>{why}</p>"
                    f"  </div>"
                    f"  <div class='ob-products'>"
                )
                if results:
                    for i, item in enumerate(results):
                        img_url = item.get("img", "")
                        title   = item.get("title", "")
                        price   = item.get("price", "")
                        url     = item.get("url", "")
                        score   = item.get("relevance_score", 0)
                        _tilt   = _tilts[i % len(_tilts)]
                        _short  = title[:28] + "..." if len(title) > 28 else title
                        _right_html += (
                            f"<a href='{url}' target='_blank' style='text-decoration:none;"
                            f"display:inline-block;width:100px;vertical-align:top'>"
                            f"  <div class='polaroid {_tilt}' style='width:100px'>"
                            + (f"  <img src='{img_url}' style='width:100px;height:130px;object-fit:cover;display:block' />"
                               if img_url else
                               "  <div style='width:100px;height:130px;background:#edeae5'></div>")
                            + f"  <p class='polaroid-caption' style='font-size:0.6rem'>{price}</p>"
                            f"  </div>"
                            f"  <p style='font-family:Cormorant Garamond,serif;font-style:italic;"
                            f"  font-size:0.68rem;color:#6b5e54;margin:3px 0 1px 0;line-height:1.3'>{_short}</p>"
                            f"  <p style='font-family:Jost,sans-serif;font-size:0.48rem;"
                            f"  letter-spacing:0.1em;text-transform:uppercase;color:#b0a89e;margin:0'>{score}% match</p>"
                            f"</a>"
                        )
                elif not etsy_key:
                    _right_html += (
                        "<p style='font-family:Jost,sans-serif;font-size:0.75rem;color:#b0a89e;"
                        "letter-spacing:0.06em;align-self:center'>Add an Etsy API key to see live results.</p>"
                    )
                _right_html += "  </div></div>"

            # Full editorial board: hero on left, all piece rows on right
            _board_html = (
                f"<div class='outfit-board'>"
                f"  <div class='ob-left'>"
                f"    <div class='polaroid polaroid-hero tilt-l1' style='width:180px'>"
                f"      <img src='data:{_mime};base64,{_img_b64}' style='width:180px;height:240px;object-fit:cover;display:block' />"
                f"      <p class='polaroid-caption'>your inspiration</p>"
                f"    </div>"
                f"    <div class='sticky sticky-rose' style='margin-top:0.9rem'>"
                f"      <p class='sticky-hero-title'>{style_title if style_title else 'The Look'}</p>"
                + (f"      <p class='sticky-hero-sub'>{_desc}</p>" if _desc else "")
                + f"      <p class='sticky-footer'>{len(suggestions)} pieces to complete this look</p>"
                f"    </div>"
                f"  </div>"
                f"  <div class='ob-right'>{_right_html}</div>"
                f"</div>"
            )
            st.markdown(_board_html, unsafe_allow_html=True)

            # Saved Looks: previously generated boards
            _saved = {
                fname: data for fname, data in st.session_state.ai_analysis.items()
                if data.get("outfit_suggestions") and fname != uploaded.name
            }
            if _saved:
                st.divider()
                st.markdown(
                    "<p style='font-family:Jost,sans-serif;font-size:0.6rem;letter-spacing:0.3em;"
                    "text-transform:uppercase;color:#b0a89e;margin-bottom:1rem'>Previously saved looks</p>",
                    unsafe_allow_html=True,
                )
                _saved_html = "<div style='display:flex;flex-wrap:wrap;gap:14px;margin-top:0.5rem'>"
                for _si, (_sfname, _sdata) in enumerate(_saved.items()):
                    _stitle = _sdata.get("title", _sfname)
                    _spath  = os.path.join("data", "inspiration", _sfname)
                    if os.path.exists(_spath):
                        with open(_spath, "rb") as _sf:
                            _sb64 = _b64_outfit.b64encode(_sf.read()).decode()
                        _sext  = _sfname.rsplit(".", 1)[-1].lower()
                        _smime = "image/jpeg" if _sext in ("jpg", "jpeg") else f"image/{_sext}"
                        _saved_html += (
                            f"<div class='saved-polaroid {_tilts[_si % len(_tilts)]}' style='width:150px'>"
                            f"<img src='data:{_smime};base64,{_sb64}' style='width:150px;height:195px;object-fit:cover;display:block' />"
                            f"<p class='saved-polaroid-label'>{_stitle[:22]}{'…' if len(_stitle)>22 else ''}</p>"
                            f"</div>"
                        )
                _saved_html += "</div>"
                st.markdown(_saved_html, unsafe_allow_html=True)

        elif cached.get("outfit_attempted"):
            st.info("Could not generate outfit suggestions for this image. Try a clearer photo of a single garment.")
        elif not cached:
            st.info("Upload an image and wait for AI analysis to complete first.")
