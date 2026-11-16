"""Moment of GroundTruth: predict the cause of a gas pipeline incident from its narrative, and explain the project.

Run from the repository root::

    streamlit run app/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).parent
ROOT = APP_DIR.parent
sys.path.insert(0, str(APP_DIR))

st.set_page_config(page_title="Moment-of-GroundTruth", page_icon=str(ROOT / "docs" / "images" / "logo-stamp.png"), layout="centered")

RED = "#C8201C"
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"], .stApp {{ font-family: 'Inter', system-ui, sans-serif; }}
h1, h2, h3, .anton {{ font-family: 'Anton', 'Impact', sans-serif !important; letter-spacing: .03em; text-transform: uppercase; font-weight: 400 !important; }}
h2 {{ color: {RED}; margin-top: 1.4rem; }}
h3 {{ margin-top: 1.1rem; }}
h5 {{ font-family: 'Anton', sans-serif !important; letter-spacing:.04em; text-transform: uppercase; font-weight:400 !important; margin-top:1.1rem; }}
.block-container {{ max-width: 900px; padding-top: 1.6rem; }}
.title {{ font-family: 'Anton', sans-serif; color: {RED}; font-size: 3.1rem; line-height: 1; letter-spacing: .02em; margin: 0; }}
.tag {{ color: #444; margin: .35rem 0 0 0; font-size: 1.02rem; }}
.small {{ color: #6b6b6b; font-size: .86rem; }}
.take {{ font-size: .93rem; border-left: 4px solid {RED}; padding-left: .7rem; margin-bottom: 1.6rem; }}
.stamp {{ display:inline-block; border: 5px solid {RED}; border-radius: 10px; padding: .35rem 1.1rem; transform: rotate(-3deg);
         color: {RED}; font-family:'Anton',sans-serif; font-size: 2.3rem; text-transform: uppercase; letter-spacing:.03em; line-height:1.15; }}
.stamp-wrap {{ padding: .3rem 0 .8rem .3rem; }}
.bar-row {{ display:flex; align-items:center; gap:.6rem; margin:.28rem 0; font-size:.92rem; }}
.bar-name {{ width: 15rem; flex: none; }}
.bar-track {{ flex:1; background:#EFE9E5; height: 14px; border-radius: 7px; overflow:hidden; }}
.bar-fill {{ height: 100%; border-radius: 7px; }}
.bar-pct {{ width: 3.2rem; text-align:right; font-variant-numeric: tabular-nums; }}
.narr {{ line-height: 2.05; font-size: 1.02rem; background:#FBF8F6; padding: 1rem 1.1rem; border-radius: 10px; border: 1px solid #EFE6E0; }}
.narr span {{ padding: 2px 3px; border-radius: 3px; margin-right: 1px; }}
.legend span {{ display:inline-block; padding: 2px 8px; border-radius: 4px; margin-right: .5rem; font-size:.82rem; }}
.card {{ border:1px solid #EFE6E0; border-radius: 12px; overflow:hidden; background:#fff; }}
.card .txt {{ padding: .9rem 1.1rem 1rem 1.1rem; }}
.noimg {{ height: 190px; display:flex; align-items:center; justify-content:center; background:#F6F1EE; color:{RED}; }}
.noimg-small {{ height: 120px; display:flex; align-items:center; justify-content:center; background:#F6F1EE; color:{RED}; border-radius:8px; font-size:.85rem; }}
.callout {{ background:#FBF4F2; border-left: 5px solid {RED}; border-radius: 6px; padding: .8rem 1rem; margin: .7rem 0 1rem 0; }}
.stats {{ display:flex; gap:.7rem; flex-wrap:wrap; margin: .6rem 0 1rem 0; }}
.stat {{ flex:1; min-width: 8.5rem; background:#FBF4F2; border-radius: 10px; padding: .8rem .9rem; text-align:center; }}
.stat .num {{ font-family:'Anton',sans-serif; color:{RED}; font-size:1.9rem; line-height:1.1; }}
.stat .lab {{ font-size:.8rem; color:#555; margin-top:.15rem; }}
.steps {{ display:flex; gap:.7rem; margin: .2rem 0 1rem 0; }}
.step {{ flex:1; background:#FBF4F2; border-radius:10px; padding:.7rem .9rem; }}
.step .n {{ display:inline-block; width:1.7rem; height:1.7rem; border-radius:50%; background:{RED}; color:#fff; text-align:center; line-height:1.7rem; font-weight:600; margin-bottom:.25rem; }}
button[data-baseweb="tab"] {{ font-family:'Anton',sans-serif; letter-spacing:.05em; text-transform: uppercase; font-size: 1rem; }}
div.stButton > button[kind="primary"] {{ font-family:'Anton',sans-serif; letter-spacing:.06em; font-size:1.15rem; padding:.5rem 1.5rem; border-radius: 8px; }}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def load_model():
    from explain import Classifier

    return Classifier()


# header
c1, c2 = st.columns([1, 4], vertical_alignment="center")
c1.image(str(ROOT / "docs" / "images" / "logo-stamp.png"), width=130)
c2.markdown(
    '<p class="title">MOMENT OF GROUNDTRUTH</p>'
    '<p class="tag">Every pipeline incident has a moment of truth. Paste a report and we dig down to the root cause.</p>',
    unsafe_allow_html=True,
)
st.write("")

# load the model once, before the user clicks anything, so the first answer is instant
if not (APP_DIR / "artifacts" / "head.pt").exists():
    st.error("The model file is missing. Run `python app/build_head.py` once to build it.")
    st.stop()
with st.spinner("Warming up the model (first visit only, about 10 seconds)..."):
    model = load_model()

import learn_tabs  # noqa: E402
import predict_tab  # noqa: E402

t_find, t_story, t_data, t_models, t_results, t_limits = st.tabs(
    ["Find the cause", "The story", "Data & split", "The models", "Results", "Limits & credits"]
)
with t_find:
    predict_tab.render(model)
with t_story:
    learn_tabs.story()
with t_data:
    learn_tabs.data_and_split()
with t_models:
    learn_tabs.models()
with t_results:
    learn_tabs.results()
with t_limits:
    learn_tabs.limits_and_credits()
