"""Build web/index.html: the project deck (docs/Moment of GroundTruth.html) with a live demo slide.

Run from the repository root::

    python web/build_web.py

The live slide calls the prediction API (api/server.py). Saved results for the eight example reports are
embedded so the demo still works if the server is unreachable.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
sys.path.insert(0, str(ROOT / "app"))
from causes import CAUSES, LABELS  # noqa: E402

EXAMPLE_ROWS = [438, 83, 72, 365, 130, 12, 434, 118]
SAVED = WEB / "saved_results.json"  # real model + SHAP output for the eight examples


def offline() -> dict:
    saved = json.loads(SAVED.read_text(encoding="utf-8"))
    df = pd.read_csv(ROOT / "data" / "experiment1" / "test.csv")
    items = []
    for i, (row, s) in enumerate(zip(EXAMPLE_ROWS, saved["items"])):
        items.append({"name": f"Example {i + 1}", "text": df.loc[row, "narrative_clean"], "truth": df.loc[row, "CAUSE"], "probs": s["probs"], "words": s["words"]})
    return {
        "labels": LABELS,
        "titles": [CAUSES[l]["title"] for l in LABELS],
        "causes": [{"title": CAUSES[l]["title"], "caption": CAUSES[l]["caption"]} for l in LABELS],
        "items": items,
    }


def favicon() -> str:
    """The project stamp as the browser-tab icon, embedded so it works on any host."""
    import base64
    import io

    from PIL import Image

    im = Image.open(ROOT / "docs" / "images" / "logo-stamp.png").convert("RGBA")
    side = max(im.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(im, ((side - im.width) // 2, (side - im.height) // 2), im)
    buf = io.BytesIO()
    canvas.resize((128, 128), Image.LANCZOS).save(buf, "PNG")
    uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    return f'<link rel="icon" type="image/png" href="{uri}">' + chr(10) + f'<link rel="apple-touch-icon" href="{uri}">'


def main() -> None:
    html = (ROOT / "docs" / "Moment of GroundTruth.html").read_text(encoding="utf-8")

    html, n = re.subn(r'<section class="slide s-app" id="s14">.*?</section>', lambda m: (WEB / "live_slide.html").read_text(encoding="utf-8").strip(), html, count=1, flags=re.S)
    assert n == 1, "slide 14 not found"

    marker = "@media (prefers-reduced-motion:reduce)"
    assert marker in html
    html = html.replace(marker, (WEB / "live_slide.css").read_text(encoding="utf-8") + (WEB / "stamp_anim.css").read_text(encoding="utf-8") + marker, 1)

    start = html.index("/* ---------- slide 14 app ---------- */")
    end = html.index("/* ---------- enter hooks ---------- */")
    js = (WEB / "stamp_anim.js").read_text(encoding="utf-8") + (WEB / "fit.js").read_text(encoding="utf-8") + "const OFFLINE=" + json.dumps(offline(), ensure_ascii=False) + ";\n" + (WEB / "live_slide.js").read_text(encoding="utf-8") + "\n"
    html = html[:start] + js + html[end:]

    assert "e.target.matches('input')" in html
    html = html.replace("e.target.matches('input')", "e.target.matches('input,textarea')", 1)

    html = html.replace("function onEnter(n){", "function onEnter(n){" + chr(10) + "  if(n===0)playStamp();", 1)
    hook = "if(n===9&&window._barsReset)window._barsReset();"
    assert hook in html
    html = html.replace(hook, hook + "\n  if(n===12&&window._lvEnter)window._lvEnter();", 1)

    old = "Switch to the live app. Paste or pick a real test narrative."
    assert old in html
    html = html.replace(old, "The live demo is on this slide, no window switch. Pick an example or paste any narrative; the page calls our model on Oracle Cloud. The badge top right says LIVE or OFFLINE.", 1)

    html = html.replace("</head>", favicon() + chr(10) + "</head>", 1)
    (WEB / "index.html").write_text(html, encoding="utf-8")
    print("wrote", WEB / "index.html", f"{len(html) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
