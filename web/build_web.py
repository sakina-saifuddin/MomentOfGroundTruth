"""Build the website from the project deck (docs/Moment of GroundTruth.html).

Run from the repository root::

    python web/build_web.py

Writes:
  web/index.html                      the deck, plus the live demo slide, the audience game slides, favicon
  web/play/index.html                 the phone page the QR code opens
  netlify/functions/answers.mjs       true causes + model answers for the game (kept server side until reveal)

The live demo slide calls the prediction API (api/server.py). Saved results for the eight example reports are
embedded so the demo still works if the server is unreachable.
"""

from __future__ import annotations

import base64
import io
import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
sys.path.insert(0, str(ROOT / "app"))
from causes import CAUSES, LABELS  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from copy_edits import EDITS, EXPLAIN, ORDER, PLAN, exp_slides, explain_html, summary_slide  # noqa: E402

SITE = "https://momentofgroundtruth.netlify.app"
PLAY_URL = SITE + "/play/"
EXAMPLE_ROWS = [438, 83, 72, 365, 130, 12, 434, 118]
HOST_KEY_DEFAULT = "mog-7f3a9c2e41"  # default host key for reveal/reset; override with a HOST_KEY env var in Netlify
LIVE_API_ENABLED = False  # set True once the prediction API is running on the VM (see deploy/setup_vm.sh)
ROUND_PICKS = [2]  # which of the eight examples (1-based) the audience game uses, in order
SAVED = WEB / "saved_results.json"  # real model + SHAP output for the eight examples


def read(name: str) -> str:
    return (WEB / name).read_text(encoding="utf-8")


def offline() -> dict:
    saved = json.loads(SAVED.read_text(encoding="utf-8"))
    df = pd.read_csv(ROOT / "data" / "experiment1" / "test.csv")
    items = []
    for i, (row, s) in enumerate(zip(EXAMPLE_ROWS, saved["items"])):
        items.append({"name": f"Report {i + 1}", "text": df.loc[row, "narrative_clean"], "truth": df.loc[row, "CAUSE"], "probs": s["probs"], "words": s["words"]})
    return {
        "labels": LABELS,
        "titles": [CAUSES[l]["title"] for l in LABELS],
        "causes": [{"title": CAUSES[l]["title"], "caption": CAUSES[l]["caption"]} for l in LABELS],
        "items": items,
    }


def stamp_uri() -> str:
    """The project stamp as a small PNG data URI (browser-tab icon and phone-page logo)."""
    from PIL import Image

    im = Image.open(ROOT / "docs" / "images" / "logo-stamp.png").convert("RGBA")
    side = max(im.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(im, ((side - im.width) // 2, (side - im.height) // 2), im)
    buf = io.BytesIO()
    canvas.resize((128, 128), Image.LANCZOS).save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def favicon() -> str:
    uri = stamp_uri()
    return f'<link rel="icon" type="image/png" href="{uri}">' + chr(10) + f'<link rel="apple-touch-icon" href="{uri}">'


def qr_svg(url: str) -> str:
    import qrcode
    import qrcode.image.svg

    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, border=0, box_size=10, error_correction=qrcode.constants.ERROR_CORRECT_M)
    svg = img.to_string().decode("utf-8")
    svg = re.sub(r"<\?xml[^>]*\?>", "", svg).strip()
    svg = re.sub(r'\swidth="[^"]*"', "", svg, count=1)
    svg = re.sub(r'\sheight="[^"]*"', "", svg, count=1)
    svg = svg.replace("<svg", '<svg role="img" aria-label="QR code to play the game" shape-rendering="crispEdges"', 1)
    return re.sub(r'(<path[^>]*?)\sfill="[^"]*"', r"\1", svg).replace("<path", '<path fill="#1b1612"', 1)


def game_data(off: dict) -> tuple[list[dict], list[dict]]:
    """Rounds shown to the audience (no answers) and the answers (server side only)."""
    rounds, answers = [], []
    for n in ROUND_PICKS:
        it = off["items"][n - 1]
        probs = it["probs"]
        model = max(range(8), key=lambda i: probs[i])
        words = it["text"].split()
        rounds.append({"text": it["text"], "excerpt": " ".join(words[:20]) + (" ..." if len(words) > 20 else "")})
        answers.append({"truth": LABELS.index(it["truth"]), "model": model, "conf": round(probs[model], 3)})
    return rounds, answers


def build_play(rounds: list[dict]) -> None:
    causes = [{"title": CAUSES[l]["title"], "blurb": CAUSES[l]["blurb"]} for l in LABELS]
    html = read("play_template.html").replace("/*STAMP*/", stamp_uri())
    html = html.replace("const ROUNDS=/*ROUNDS*/[];", "const ROUNDS=" + json.dumps(rounds, ensure_ascii=False) + ";")
    html = html.replace("const CAUSES=/*CAUSES*/[];", "const CAUSES=" + json.dumps(causes, ensure_ascii=False) + ";")
    out = WEB / "play"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    html = (ROOT / "docs" / "Moment of GroundTruth.html").read_text(encoding="utf-8")
    for old, new in EDITS:
        assert html.count(old) == 1, f"copy edit does not match exactly once: {old[:60]!r}"
        html = html.replace(old, new)
    off = offline()
    rounds, answers = game_data(off)

    fn_dir = ROOT / "netlify" / "functions"
    fn_dir.mkdir(parents=True, exist_ok=True)
    (fn_dir / "answers.mjs").write_text("// Generated by web/build_web.py. Sent to clients only after the host reveals.\nexport default " + json.dumps(answers, indent=2) + ";\nexport const HOST_DEFAULT = " + json.dumps(HOST_KEY_DEFAULT) + ";\n", encoding="utf-8")
    build_play(rounds)

    # slides: the app slide becomes the live demo; the two game slides go in front of it
    nr = len(rounds)
    what = "a real incident report" if nr == 1 else f"{nr} real incident reports"
    model_gets = "The model has never seen this report." if nr == 1 else f"The model has never seen these {nr} reports."
    game_slides = read("game_slides.html").replace("/*QR*/", qr_svg(PLAY_URL)).replace("/*PLAYURL*/", PLAY_URL.replace("https://", "")).replace("/*WHAT*/", what).replace("/*MODELGETS*/", model_gets)
    # the live demo slide (s14) is only in the website if ORDER lists it
    with_demo = "s14" in ORDER
    live = (read("live_slide.html").strip() + chr(10) + chr(10) if with_demo else "") + game_slides.strip()
    html, n = re.subn(r'<section class="slide s-app" id="s14">.*?</section>', lambda m: live, html, count=1, flags=re.S)
    assert n == 1, "slide 14 not found"

    marker = "@media (prefers-reduced-motion:reduce)"
    assert marker in html
    html = html.replace(marker, read("live_slide.css") + read("stamp_anim.css") + read("game.css") + read("deck_fixes.css") + read("story.css") + read("theme_light.css") + marker, 1)

    start = html.index("/* ---------- slide 14 app ---------- */")
    end = html.index("/* ---------- enter hooks ---------- */")
    js = (
        read("stamp_anim.js")
        + read("fit.js")
        + "const OFFLINE=" + json.dumps(off, ensure_ascii=False) + ";"
        + chr(10)
        + "const LIVE_API_ENABLED=" + ("true" if LIVE_API_ENABLED else "false") + ";"
        + chr(10)
        + "const HOST_DEFAULT=" + json.dumps(HOST_KEY_DEFAULT) + ";"
        + chr(10)
        + "const GAME_ROUNDS=" + json.dumps(rounds, ensure_ascii=False) + ";"
        + chr(10)
        + read("game.js")
        + read("spot.js")
        + (read("live_slide.js") if with_demo else "")
        + chr(10)
    )
    html = html[:start] + js + html[end:]

    assert "e.target.matches('input')" in html
    html = html.replace("e.target.matches('input')", "e.target.matches('input,textarea')", 1)

    # the speaker plan, in the order of the story
    start = html.index("const PLAN=[")
    end = html.index("const total=PLAN.reduce")
    assert len(PLAN) == len(ORDER), "PLAN and ORDER must have the same length"
    items = [
        "{w:%s,t:%d,title:%s,say:%s}" % (json.dumps(w), t, json.dumps(title, ensure_ascii=False), json.dumps(say, ensure_ascii=False))
        for w, t, title, say in PLAN
    ]
    nl = chr(10)
    html = html[:start] + "const PLAN=[" + nl + " " + ("," + nl + " ").join(items) + nl + "];" + nl + html[end:]

    # the slides, in the order of the story (the plan slide is new, the rest come from the deck)
    sec_re = re.compile(r'<section class="slide [^"]*" id="([^"]+)"[^>]*>.*?</section>', re.S)
    found = list(sec_re.finditer(html))
    blocks = {m.group(1): m.group(0) for m in found}
    blocks["s16"] = summary_slide()
    blocks.update(exp_slides())
    for sid in EXPLAIN:
        assert sid in blocks, f"EXPLAIN names a slide that does not exist: {sid}"
        blocks[sid] = blocks[sid].rstrip()[: -len("</section>")] + explain_html(sid) + "</section>"
    assert set(ORDER) <= set(blocks), f"ORDER lists slides that do not exist: {set(ORDER) - set(blocks)}"
    html = html[: found[0].start()] + (chr(10) * 2).join(blocks[i] for i in ORDER) + html[found[-1].end() :]

    html = html.replace("function onEnter(n){", "function onEnter(n){" + chr(10) + "  if(n===0)playStamp();", 1)
    hook = "if(s.id==='s10'&&window._barsReset)window._barsReset();"
    assert hook in html
    html = html.replace(hook, hook + chr(10) + "  spotlight(s.id);" + chr(10) + ("  if(s.id==='s14'&&window._lvEnter)window._lvEnter();" + chr(10) if with_demo else "") + "  if(s.id==='sv'||s.id==='sr')gameEnter();else gameLeave();", 1)

    html = html.replace("</head>", favicon() + chr(10) + "</head>", 1)
    (WEB / "index.html").write_text(html, encoding="utf-8")
    print("wrote", WEB / "index.html", f"{len(html) / 1e6:.2f} MB;", len(rounds), "game rounds; QR ->", PLAY_URL)


if __name__ == "__main__":
    main()
