"""The 'Find the cause' tab: paste a narrative, get a cause, a picture and a SHAP explanation."""

from __future__ import annotations

import html
from pathlib import Path

import pandas as pd
import streamlit as st

from causes import ASSETS, CAUSES, LABELS

ROOT = Path(__file__).resolve().parents[1]
RED = "#D8291F"
EXAMPLE_ROWS = [438, 83, 72, 365, 130, 12, 434, 118]  # one test-split narrative per cause


@st.cache_data(show_spinner=False)
def examples() -> list[dict]:
    df = pd.read_csv(ROOT / "data" / "experiment1" / "test.csv")
    return [
        {"name": f"Example {i + 1}", "text": df.loc[r, "narrative_clean"], "truth": df.loc[r, "CAUSE"]}
        for i, r in enumerate(EXAMPLE_ROWS)
    ]


def steps() -> None:
    st.markdown(
        '<div class="steps">'
        '<div class="step"><div class="n">1</div><b>Paste</b><br><span class="small">an incident narrative</span></div>'
        '<div class="step"><div class="n">2</div><b>Read</b><br><span class="small">the model scores all 8 causes</span></div>'
        '<div class="step"><div class="n">3</div><b>Stamp</b><br><span class="small">the cause, a picture, and why</span></div>'
        "</div>",
        unsafe_allow_html=True,
    )


def render(model) -> None:
    steps()
    ex = examples()
    names = [e["name"] for e in ex]

    st.markdown("**Try a real report** from the held-out test set, or write your own:")
    pick = st.pills("Examples", names, selection_mode="single", label_visibility="collapsed")
    if st.session_state.get("_pick") != pick:
        st.session_state["_pick"] = pick
        if pick:
            st.session_state["narrative"] = ex[names.index(pick)]["text"]
        st.session_state.pop("result", None)
        st.session_state.pop("explain_for", None)

    narrative = st.text_area(
        "Incident narrative",
        key="narrative",
        height=170,
        placeholder="e.g. A contractor using a backhoe struck the 12-inch transmission line while digging a trench...",
    )
    words = len(narrative.split())
    c1, c2 = st.columns([1, 3], vertical_alignment="center")
    go = c1.button("Find the root cause", type="primary", disabled=not narrative.strip())
    c2.caption(f"{words} words" + ("  ·  reports over about 350 words may be cut off at BERT's 512-piece limit" if words > 350 else ""))

    if go:
        cleaned, probs = model.predict(narrative)
        st.session_state["result"] = {"cleaned": cleaned, "probs": probs.tolist(), "pick": pick}
        st.session_state.pop("explain_for", None)

    result = st.session_state.get("result")
    if not result:
        st.caption("The model reads the narrative only. It never sees the operator name or any other field. Curious how it was built? See the other tabs.")
        return

    cleaned, probs = result["cleaned"], result["probs"]
    top = max(range(8), key=lambda i: probs[i])
    cause = CAUSES[LABELS[top]]

    st.markdown("---")
    left, right = st.columns([3, 2], vertical_alignment="center")
    with left:
        st.markdown("##### Predicted cause")
        st.markdown(f'<div class="stamp-wrap"><div class="stamp">{html.escape(str(cause["title"]))}</div></div>', unsafe_allow_html=True)
    with right:
        st.metric("Model confidence", f"{probs[top]:.0%}")
    st.markdown(str(cause["blurb"]))
    if probs[top] < 0.5:
        st.info("The model is not sure: no cause is above 50%. Look at the runner-up causes below.")
    if result.get("pick"):
        truth = ex[names.index(result["pick"])]["truth"]
        ok = truth == LABELS[top]
        verdict = "the model got it right." if ok else "the model got it wrong, which happens roughly 4 times in 10."
        st.markdown(
            f'<p class="small">This example is from the test set. Its recorded cause is <b>{html.escape(str(CAUSES[truth]["title"]))}</b>: {verdict}</p>',
            unsafe_allow_html=True,
        )

    rows = sorted(range(8), key=lambda i: -probs[i])
    bars = ""
    for rank, i in enumerate(rows):
        color = RED if rank == 0 else "#7d7365"
        bars += (
            f'<div class="bar-row"><div class="bar-name">{html.escape(str(CAUSES[LABELS[i]]["title"]))}</div>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{probs[i] * 100:.1f}%;background:{color}"></div></div>'
            f'<div class="bar-pct">{probs[i]:.0%}</div></div>'
        )
    st.markdown("##### How sure is it about each cause?")
    st.markdown(bars, unsafe_allow_html=True)

    st.markdown("##### What this cause can look like")
    img = cause["image"]
    if img:
        st.image(str(ASSETS / str(img)), width="stretch")
        st.markdown(f'<p class="small">{html.escape(str(cause["caption"]))} Photo: {html.escape(str(cause["credit"]))}.</p>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="card"><div class="noimg"><svg width="260" height="150" viewBox="0 0 260 150" fill="none" stroke="{RED}" stroke-width="5" stroke-linecap="round">'
            '<line x1="10" y1="120" x2="250" y2="120"/><rect x="10" y="126" width="240" height="14" rx="7"/>'
            '<rect x="60" y="62" width="110" height="40" rx="6"/><circle cx="85" cy="108" r="12"/><circle cx="150" cy="108" r="12"/>'
            '<line x1="190" y1="70" x2="215" y2="55"/><line x1="195" y1="88" x2="228" y2="88"/><line x1="190" y1="106" x2="215" y2="121"/></svg></div>'
            f'<div class="txt small">{html.escape(str(cause["caption"]))} The sketch shows the idea: something outside the operator hits the line.</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("##### Why did the model say this?")
    st.markdown(
        f"Each word is shaded by how much it pushed the model **toward** (red) or **away from** (teal) <b>{html.escape(str(cause['title']))}</b>. "
        "This is **SHAP**: it re-scores the narrative many times with some words hidden, and measures how much each word changed the answer.",
        unsafe_allow_html=True,
    )
    mode = st.radio("Explanation detail", ["Quick (about 15 s)", "Detailed (about 40 s)"], horizontal=True)
    evals = 150 if mode.startswith("Quick") else 400
    key = (cleaned, top, evals)
    cache = st.session_state.setdefault("shap_cache", {})
    if st.button("Explain this prediction"):
        if key not in cache:
            bar = st.progress(0.0, text="Hiding words and re-scoring the narrative...")
            cache[key] = model.explain(
                cleaned, top, evals, progress=lambda f: bar.progress(f, text=f"Hiding words and re-scoring... {f:.0%}")
            )
            bar.empty()
        st.session_state["explain_for"] = key
    if st.session_state.get("explain_for") == key and key in cache:
        pairs = cache[key]
        mx = max((abs(v) for _, v in pairs), default=1e-9) or 1e-9
        spans = []
        for word, v in pairs:
            if not word.strip():
                continue
            a = min(abs(v) / mx, 1.0) * 0.85
            col = f"rgba(216,41,31,{a:.2f})" if v > 0 else f"rgba(95,168,173,{a:.2f})"
            spans.append(f'<span style="background:{col}" title="{v:+.3f}">{html.escape(word.strip())}</span>')
        st.markdown(
            '<p class="legend"><span style="background:rgba(216,41,31,.6)">pushes toward this cause</span>'
            '<span style="background:rgba(95,168,173,.6)">pushes away</span></p>',
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="narr">{" ".join(spans)}</div>', unsafe_allow_html=True)

        df = pd.DataFrame(pairs, columns=["word", "shap"])
        df = df[df.word.str.strip().astype(bool)].assign(word=lambda d: d.word.str.strip()).groupby("word", as_index=False)["shap"].sum()
        top_words = pd.concat([df.nlargest(8, "shap"), df.nsmallest(5, "shap")]).drop_duplicates("word").sort_values("shap")
        st.markdown("**Words with the biggest effect**")
        st.bar_chart(top_words.set_index("word")["shap"], horizontal=True, color=RED)
        st.caption("Numbers are the change in the model's probability for the predicted cause. Hover a highlighted word to see its value.")

    with st.expander("What the model actually saw"):
        st.write(cleaned)
        st.caption("Your text after cleaning: tags removed, spaces tidied, everything lowercase. This is the same cleaning used for the training data.")

    m = model.metrics
    st.markdown(
        f'<p class="small">On {m["test_rows"]} held-out test narratives this model scored {m["test_accuracy"]:.0%} accuracy and {m["test_macro_f1"]:.2f} macro-F1, '
        "so treat a prediction as a second opinion, not a finding. Rare causes are the least reliable. Pictures illustrate the cause; they are not photos of your incident.</p>",
        unsafe_allow_html=True,
    )
