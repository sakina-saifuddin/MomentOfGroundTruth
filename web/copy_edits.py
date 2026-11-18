"""The story version of the project deck (docs/Moment of GroundTruth.html), applied when building the website.

What lives here:

* EDITS: wording and small markup changes. Each entry is (old, new) and each old string must occur exactly once,
  so a change to the source deck that moves the text fails the build instead of being skipped silently.
* ORDER: the order of the slides, as the story is told. Slides left out of ORDER are not in the website.
* PLAN: the speaker plan (who talks, for how long, what to say). The reasons for every choice live here, in the
  speaker notes, and not on the slides.
* summary_slide(): the closing slide, drawn from the real results.

Rules for the slides: the figures and numbers carry the message, so a slide has one headline sentence of about
eight words or fewer and no paragraphs. The numbers we talk about pulse, the best model gets its own outline,
and the weaker run fades back (see story.css and spot.js).

The reasons for the choices come from the project PRD (Group1_Project_PRD.pdf): attention because the reports
are long, frozen BERT because only the small head needs training, one shared split and macro-F1 so the
comparison is fair, the same settings for both recurrent models.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


EDITS: list[tuple[str, str]] = [
    # ---------- 1 · title
    ("Classifying gas transmission and gathering pipeline incident causes using BiGRU, BiLSTM with attention, and BERT-base.",
     "We trained three models to read pipeline incident reports and name the cause of each incident."),

    # ---------- 2 · the problem
    ('<p class="eyebrow"><b>Why it matters</b><i></i>NTSB investigations</p>',
     '<p class="eyebrow"><b>1 · The problem</b><i></i>Why it matters</p>'),
    ("<h2>Pipelines fail where <em>nobody can see</em></h2>",
     "<h2>Every pipeline failure ends in <em>a written report</em></h2>"),
    ("<p>Defective seam weld and a pressure increase before the rupture.</p>", '<p class="tagline">Cause: a defective seam weld</p>'),
    ("<p>Severe internal corrosion.</p>", '<p class="tagline">Cause: severe internal corrosion</p>'),
    ("Operators file a written report within <b>30 days</b>. The cause is somewhere in the text.",
     'A written report is due within <b class="pulse">30 days</b>.'),

    # ---------- 3 · the data
    ('<p class="eyebrow"><b>The data</b><i></i>PHMSA gas transmission and gathering incidents</p>',
     '<p class="eyebrow"><b>2 · The data and the test</b><i></i>The reports</p>'),
    ("<h2>3,044 reports, <em>eight</em> possible causes</h2>",
     "<h2>We have <em>3,044</em> reports, and some causes are rare</h2>"),
    ('<span class="lab" style="display:block;margin-top:.3rem">narratives, all usable</span>',
     '<span class="lab" style="display:block;margin-top:.3rem">real reports</span>'),
    ('<div><span class="big" data-count="136">136</span><span class="lab" style="display:block">median words</span></div>',
     '<div><span class="big pulse">4.8×</span><span class="lab" style="display:block">equipment failure vs incorrect operation</span></div>'),
    ('<div><span class="big">2001–2026</span><span class="lab" style="display:block">report years</span></div>', ""),
    ("Source: U.S. DOT, PHMSA, Form F 7100.2. The 2010–present file has 623 fields; we kept six. The 2002–2009 historical file is merged in and older cause labels are mapped to today's eight. The model reads the narrative only.",
     "Source: U.S. DOT PHMSA public incident reports."),
    ('<span class="pill" style="color:var(--text)">Proposal draft: 3,027 · Final file: 3,044</span>', ""),

    # ---------- 4 · the test
    ('<p class="eyebrow"><b>Experiment design</b><i></i>Same split for every model</p>',
     '<p class="eyebrow"><b>2 · The data and the test</b><i></i>How we test</p>'),
    ("<h2>One split. <em>Two ways</em> to handle imbalance.</h2>",
     "<h2>Every model is tested on <em>reports it never saw</em></h2>"),
    ('<p class="credit">Stratified, seed 42. Validation and test sets are identical in both experiments.</p>',
     '<p class="credit">The same split for all three models.</p>'),
    ('<p class="xnote" style="min-height:0">Cleaning comes first: extra whitespace and HTML artifacts removed, all text lowercased.</p>', ""),
    ("'<b>Exp 1</b> trains on the 2,130 original rows. The loss is weighted so rare causes count more.'",
     "'Rare causes count more in the loss.'"),
    ("'<b>Exp 2</b> adds <b>681 validated synthetic narratives</b> (hatched), written by an AI assistant from training reports only, for six smaller causes. Every cause reaches 300 rows. 2,811 in total, plain loss.'",
     "'<b>+681</b> synthetic reports (hatched) for the six smaller causes.'"),

    # ---------- 5 · BiGRU (model 1)
    ('<p class="eyebrow"><b>Model 1</b><i></i>BiGRU + FastText</p>',
     '<p class="eyebrow"><b>3 · The models</b><i></i>Model 1 of 3</p><span class="rank" style="--c:var(--gru)">#3</span>'),
    ("<h2>Reads the narrative <em>both directions</em></h2>", "<h2>The BiGRU is our <em>simple baseline</em></h2>"),
    ('<div class="arch" id="arch-gru"></div>',
     '<div class="arch" id="arch-gru"></div><div class="chips"><span>Adam · lr 0.001</span><span>dropout 0.3</span><span>early stopping</span></div>'),
    ('<p class="callout" style="--c:var(--gru)">Oversampling lifted accuracy <b>7.6 points</b> but macro-F1 by only <b>0.007</b>. Incorrect-operation recall fell from <b>0.32 to 0.12</b>.</p>',
     '<div class="chips res"><span class="up">With synthetic data: accuracy ▲ <b class="pulse">+7.6 pts</b></span><span>macro-F1 only <b>+0.007</b></span></div>'),

    # ---------- 6 · BiLSTM (model 2)
    ('<p class="eyebrow"><b>Model 2</b><i></i>BiLSTM + attention + FastText</p>',
     '<p class="eyebrow"><b>3 · The models</b><i></i>Model 2 of 3</p><span class="rank" style="--c:var(--lstm)">#2</span>'),
    ("<h2>Learns <em>which words</em> carry the cause</h2>", "<h2>The BiLSTM adds attention to <em>key words</em></h2>"),
    ('<div class="arch" id="arch-lstm"></div>',
     '<div class="arch" id="arch-lstm"></div><div class="chips"><span>Adam · lr 0.001</span><span>dropout 0.3</span><span>same settings as BiGRU</span></div>'),
    ('<p class="callout" style="--c:var(--lstm)">Best RNN. Highest corrosion F1 of any run: <b>0.729</b>, with <b>0.805</b> precision. Oversampling cost it <b>0.067</b> macro-F1.</p>',
     '<div class="chips res"><span class="up">Best corrosion F1 of any run: <b class="pulse">0.729</b></span><span class="down">With synthetic data: macro-F1 ▼ <b>0.067</b></span></div>'),

    # ---------- 7 · frozen BERT (model 3)
    ('<p class="eyebrow"><b>Model 3</b><i></i>bert-base-uncased, frozen</p>',
     '<p class="eyebrow"><b>3 · The models</b><i></i>Model 3 of 3</p><span class="rank best">#1 BEST</span>'),
    ("<h2>Keep BERT frozen. <em>Train one small head.</em></h2>", "<h2>Frozen BERT <em>trains only a small layer</em></h2>"),
    ('<div class="row"><i class="sw" style="background:var(--paper)"></i><div>Narrative, up to <b>512</b> tokens</div></div>',
     '<div class="row"><i class="sw" style="background:var(--paper)"></i><div>Report in, up to <b>512</b> tokens</div></div>'),
    ('<div class="row"><i class="sw" style="background:rgba(160,190,200,.55)"></i><div><b>12 layers</b>, 12 heads, 768-d. All weights frozen.</div></div>',
     '<div class="row"><i class="sw" style="background:rgba(160,190,200,.55)"></i><div><b>12 layers</b>, all frozen</div></div>'),
    ('<div class="row"><i class="sw" style="background:var(--gru)"></i><div>One 768-number vector per narrative</div></div>',
     '<div class="row"><i class="sw" style="background:var(--gru)"></i><div>768 numbers per report</div></div>'),
    ('<div class="row"><i class="sw" style="background:var(--bert)"></i><div>Linear head 768 → 8. <b>6,152</b> trainable weights, against 903,688 in the BiLSTM.</div></div>',
     '<div class="row"><i class="sw" style="background:var(--bert)"></i><div>Trained: <b class="pulse">6,152</b> weights (BiLSTM: 903,688)</div></div>'),
    ('<p class="hint">DRAG TO ROTATE · HOVER A LAYER</p>',
     '<div class="chips"><span>AdamW · lr 0.002</span><span>early stopping</span></div>'
     '<div class="chips res"><span class="up">Macro-F1 <b class="pulse">0.553</b></span><span class="up">Accuracy <b>60.3%</b></span></div>'
     '<p class="hint">DRAG TO ROTATE · HOVER A LAYER</p>'),

    # ---------- 8 · the pooling choice
    ('<p class="eyebrow"><b>Model 3</b><i></i>Class-weighted loss, test set</p>',
     '<p class="eyebrow"><b>3 · The models</b><i></i>The choice that mattered most</p>'),
    ("<h2>One design choice moved macro-F1 by <em>0.25</em></h2>", "<h2>One choice changed the score by <em>0.25</em></h2>"),
    ("Same frozen BERT, same head, same data. Only the step that builds the narrative vector differs: one [CLS] token, or the average of every token.", ""),
    ("`<b>+${f3(d)}</b> macro-F1 and <b>+${((MM.bert.runs['1'].acc-MM.pool.runs['1'].acc)*100).toFixed(1)}</b> accuracy points over pooler_output`",
     "`<b>+${f3(d)}</b> macro-F1`"),
    ("`This is the original design. Switch to mean pooling.`", "`This was our first design.`"),

    # ---------- 9 · head to head
    ('<p class="eyebrow"><b>Results</b><i></i>458 held-out test narratives</p>',
     '<p class="eyebrow"><b>4 · The results</b><i></i>All six runs on the test reports</p>'),
    ("<h2>A close race: top three within <em>0.022</em></h2>", "<h2>Frozen BERT scored <em>highest</em></h2>"),
    ("rk.hidden=r<0;rk.textContent=r+1});", "rk.hidden=r<0;rk.textContent=r+1;rk.classList.toggle('first',r===0);b.classList.toggle('winbar',r===0)});"),

    # ---------- backup slides
    ('<p class="eyebrow"><b>The labels</b><i></i>Drag, click a card, or use the arrows</p>',
     '<p class="eyebrow"><b>2 · The data and the test</b><i></i>Drag the cards to read real examples</p>'),
    ("<h2>Each cause, in the <em>operators' own words</em></h2>", "<h2>The eight causes the model chooses from</h2>"),
    ('<p class="eyebrow"><b>Per-cause results</b><i></i>Test F1 · click a row for precision and recall</p>',
     '<p class="eyebrow"><b>Backup</b><i></i>Click a row to see precision and recall</p>'),
    ("<h2>Easy causes are <em>easy</em>. Vague ones are not.</h2>", "<h2>Clear causes are <em>easy</em>, and vague ones are not</h2>"),
    ('<p class="eyebrow"><b>Errors</b><i></i>Each row sums to 100% of that true cause</p>',
     '<p class="eyebrow"><b>Backup</b><i></i>Where the models confuse causes</p>'),
    ("<h2>Where the models <em>confuse</em> causes</h2>", "<h2>This is where the models <em>confuse</em> one cause for another</h2>"),

    # ---------- the deck's script: slide positions become slide ids, room for more stakes, timer text
    ("if(n===3)startAuto(); else stopAuto();", "if(s.id==='s4')startAuto(); else stopAuto();"),
    ("if(n===2){$$('.fill',s)", "if(s.id==='s3'){$$('.fill',s)"),
    ("if(n===9&&window._barsReset)window._barsReset();", "if(s.id==='s10'&&window._barsReset)window._barsReset();"),
    ("for(let i=0;i<16;i++){const g=new THREE.Group();", "for(let i=0;i<24;i++){const g=new THREE.Group();"),
    ("TARGET 12:00 · LIMIT 13:00", "TARGET 10:00 · LIMIT 15:00"),
]

# slide order, as the story is told (ids are the section ids in the deck). The demo slide (s14) is not in the
# website; the backup slides come after the summary.
ORDER = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "sv", "sr", "s16", "s11", "s12"]

# the speaker plan, in the same order: (who, seconds, title, notes). The main talk is about 10 minutes, which
# leaves five for the audience game and questions inside the 15-minute slot. Backup slides have no time.
PLAN = [
    ("sakina", 20, "Title",
     ["Introduce the team: Parva built the BiGRU, Muhammad the BiLSTM with attention, and Sakina the frozen BERT.",
      "Give the plan in one breath: the problem, the data, the three models, the results, and then a short game."]),
    ("sakina", 45, "The problem",
     ["Point at the pulsing numbers: San Bruno in 2010 killed 8 people and Carlsbad in 2000 killed 12.",
      "After every incident the operator files a written report within 30 days, and the cause is described somewhere in that text.",
      "Our question is whether a model can read the report and name the cause automatically."]),
    ("parva", 50, "The data",
     ["We have 3,044 real reports from the public PHMSA incident file, and the model reads only the narrative.",
      "Point at the two glowing bars: equipment failure has 787 reports and incorrect operation has 165, about 4.8 times fewer.",
      "That is the imbalance. A model could look accurate just by guessing the common causes, so we have to handle it."]),
    ("parva", 40, "The eight causes",
     ["These are the eight causes the model has to choose from. Drag the cards to read a real example of each one.",
      "Say that every report has exactly one of these causes, and the model must pick it from the written story alone."]),
    ("parva", 50, "The test",
     ["We split the reports once, 70 / 15 / 15, and all three models use the same split. Point at the test block: the model never sees those reports until the end.",
      "The validation reports are for tuning and for stopping training early, and the test reports are used only once.",
      "To handle the imbalance we ran two experiments. Press the Exp 2 button and point at the blinking hatched bars: 681 synthetic reports that an AI assistant wrote from training reports only."]),
    ("parva", 55, "BiGRU",
     ["Why we chose it: it reads a report word by word in both directions, and it is simple and fast, so it is our baseline. It finished third.",
      "Settings and why: the FastText vectors are frozen because they already know English, including technical words. Dropout of 0.3 and early stopping on validation macro-F1 stop it from memorizing the training reports. Adam with a learning rate of 0.001 is the usual starting point for recurrent models.",
      "Point at the pulsing number: synthetic data raised accuracy by 7.6 points, but macro-F1 only by 0.007, so it did not really help the rare causes."]),
    ("muhammad", 55, "BiLSTM with attention",
     ["Why we chose it: reports are long, about a thousand characters, and attention lets the model give more weight to the few words that point to the cause, such as corrosion or backhoe. It finished second.",
      "Settings and why: exactly the same settings as the BiGRU, so any difference comes from attention and not from tuning.",
      "The brighter run is Experiment 1, and the fainter one is Experiment 2. Synthetic data lowered its macro-F1 by 0.067. Point at 0.729: the best corrosion score of any run."]),
    ("sakina", 55, "Frozen BERT",
     ["Why we chose it: BERT has already read a huge amount of English, so we only train a small layer on top. It finished first.",
      "Point at the pulsing 6,152: that is all that is trained, against 903,688 in the BiLSTM. With only 3,044 reports, training a small layer is safer than retraining 110 million weights, and it is fast.",
      "Why the learning rate is higher: only the small layer is learning, so 0.002 is fine. Training stopped early on validation macro-F1, like the other models."]),
    ("sakina", 50, "The pooling choice",
     ["This was the choice that mattered most. Our first plan used the [CLS] token as the summary of the report, and it scored 0.305 macro-F1.",
      "Click Mean pooling: averaging every token gives 0.553. Point at the pulsing plus 0.248, with the same model, head and data.",
      "The lesson is that how you summarize the report mattered more than which model we picked."]),
    ("muhammad", 60, "Head to head",
     ["Six runs on the test reports, ranked by macro-F1 because it gives all eight causes equal weight, so rare causes count as much as common ones.",
      "The glowing bar is the winner: frozen BERT with mean pooling at 0.553 macro-F1 and 60.3 percent accuracy. Be honest that the top three are within 0.022 and each is a single run.",
      "The hatched bars use synthetic data. They did not clearly help: they lowered the macro-F1 of the BiLSTM and of BERT."]),
    ("muhammad", 40, "Beat the model",
     ["Ask everyone to take out their phones and scan the code.",
      "Say why we play: we want to see how hard this task is for a person, because that tells us whether our model's score is good.",
      "The report comes from the test set, so the model has never seen it. Watch the pulsing counter, and move on when it stops growing."]),
    ("muhammad", 80, "Crowd vs model",
     ["Press V or click Reveal. The glowing row is the correct answer, and the blinking M is the model's answer.",
      "Whatever the result, tie it back to the findings: if people disagree, the labels are ambiguous, and that limits every model, not just ours.",
      "One report is only an illustration, not evidence. Press Shift+X afterwards to wipe the votes."]),
    ("all", 40, "Summary",
     ["Frozen BERT with mean pooling worked best. Walk through the three charts, each with the best bar glowing.",
      "It generalized best: its score dropped the least from validation to test. It was strongest on the rare causes. And the way we summarized each report mattered most.",
      "The caveat: each model ran once on 458 test reports, so small gaps are not reliable. Then thank the audience and take questions."]),
    ("muhammad", 0, "Backup: per-cause results",
     ["Backup slide. Excavation damage is easiest because its reports name the equipment. Other incident cause is hardest because its reports are vague. BERT is strongest on the rare causes."]),
    ("muhammad", 0, "Backup: errors",
     ["Backup slide. Each row shows how reports of one true cause were classified. For BERT with class weights, 69 percent of corrosion reports are right but 20 percent are called material failure."]),
]


def summary_slide() -> str:
    """The closing slide: three small charts from the real results, with the best bar highlighted."""
    rows = json.loads((ROOT / "evaluation" / "master_results.json").read_text(encoding="utf-8"))

    def run(prefix: str, exp: int = 1) -> dict:
        return next(r for r in rows if r["model"].startswith(prefix) and r["experiment"] == exp)

    gru, lstm, bert = run("BiGRU"), run("BiLSTM"), run("Frozen BERT, mean")
    cls = run("Frozen BERT, pooler")

    def drop(r: dict) -> float:
        return r["best_val_macro_f1"] - r["macro_f1"]

    def rare(r: dict) -> float:
        return (r["per_class_f1"]["OTHER INCIDENT CAUSE"] + r["per_class_f1"]["INCORRECT OPERATION"]) / 2

    def bars(items: list[tuple[str, str, float]], best_low: bool) -> str:
        values = [v for _, _, v in items]
        best = min(values) if best_low else max(values)
        top = max(values)
        out = []
        for name, color, v in items:
            klass = "mb best" if v == best else "mb"
            out.append(
                f'<div class="{klass}" style="--c:var({color});--w:{v / top * 100:.0f}%"><span class="n">{name}</span>'
                f'<span class="t"><i class="f"></i></span><b class="v">{v:.3f}</b></div>'
            )
        return '<div class="mini">' + "".join(out) + "</div>"

    models = [("BiGRU", "--gru"), ("BiLSTM", "--lstm"), ("BERT", "--bert")]
    c1 = bars([(n, c, drop(r)) for (n, c), r in zip(models, (gru, lstm, bert))], best_low=True)
    c2 = bars([(n, c, rare(r)) for (n, c), r in zip(models, (gru, lstm, bert))], best_low=False)
    c3 = bars([("[CLS]", "--pool", cls["macro_f1"]), ("Mean", "--bert", bert["macro_f1"])], best_low=False)

    return f"""<section class="slide s-end" id="s16">
  <p class="eyebrow"><b>6 · The takeaway</b><i></i>Team 1</p>
  <h2>Frozen BERT worked best, and <em>here is why</em></h2>
  <div class="body why3">
    <div class="wcard"><h3>It generalizes best</h3>{c1}<span class="cap">Score drop from validation to test (lower is better)</span></div>
    <div class="wcard"><h3>It wins on rare causes</h3>{c2}<span class="cap">F1 on the two rarest causes</span></div>
    <div class="wcard"><h3>How we pool matters most</h3>{c3}<span class="cap">BERT macro-F1: [CLS] token vs mean pooling</span></div>
  </div>
  <p class="endnote">One run per model on 458 test reports. Data: U.S. DOT PHMSA. Photos: Wikimedia Commons and NTSB; credits in the repository.</p>
</section>"""
