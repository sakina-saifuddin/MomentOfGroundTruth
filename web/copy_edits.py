"""The story version of the project deck (docs/Moment of GroundTruth.html), applied when building the website.

Three things live here:

* EDITS: wording and small markup changes. Each entry is (old, new) and each old string must occur exactly once,
  so a change to the source deck that moves the text fails the build instead of being skipped silently.
* ORDER: the order of the slides, as the story is told.
* PLAN: the speaker plan (who talks, for how long, what to say), which has to follow ORDER.

Writing rules for the text: complete sentences, one idea per slide, the headline says the point of the slide,
and the models are introduced in the order we tried them, each with the reason we chose it. The reasons come from
the project PRD (Group1_Project_PRD.pdf): attention because the reports are long, frozen BERT because only the
small head needs training, one shared split and macro-F1 so the comparison is fair, the same settings for both
recurrent models.
"""


def why(color: str, key: str, text: str) -> str:
    return f'<div class="story" style="--c:var({color})"><span class="k">{key}</span><p>{text}</p></div>'


EDITS: list[tuple[str, str]] = [
    # ---------- 1 · title
    ("Classifying gas transmission and gathering pipeline incident causes using BiGRU, BiLSTM with attention, and BERT-base.",
     "We trained three models to read pipeline incident reports and name the cause of each incident."),

    # ---------- 2 · the problem
    ('<p class="eyebrow"><b>Why it matters</b><i></i>NTSB investigations</p>',
     '<p class="eyebrow"><b>1 · The problem</b><i></i>Why it matters</p>'),
    ("<h2>Pipelines fail where <em>nobody can see</em></h2>",
     "<h2>The cause of a pipeline failure is hidden in <em>a written report</em></h2>"),
    ("<p>Defective seam weld and a pressure increase before the rupture.</p>",
     "<p>Investigators blamed a defective seam weld and a pressure increase before the rupture.</p>"),
    ("<p>Severe internal corrosion.</p>", "<p>Investigators blamed severe internal corrosion.</p>"),
    ("Operators file a written report within <b>30 days</b>. The cause is somewhere in the text.",
     "After every incident, the operator writes a report within <b>30 days</b>. Reading thousands of them by hand is slow, so we asked whether a model could read each report and name the cause."),

    # ---------- 3 · what the model must choose (the eight cause cards)
    ('<p class="eyebrow"><b>The labels</b><i></i>Drag, click a card, or use the arrows</p>',
     '<p class="eyebrow"><b>1 · The problem</b><i></i>Drag the cards to read real examples</p>'),
    ("<h2>Each cause, in the <em>operators' own words</em></h2>",
     "<h2>For every report, the model must pick <em>one of eight causes</em></h2>"),

    # ---------- 4 · the data
    ('<p class="eyebrow"><b>The data</b><i></i>PHMSA gas transmission and gathering incidents</p>',
     '<p class="eyebrow"><b>2 · The data and the test</b><i></i>The reports</p>'),
    ("<h2>3,044 reports, <em>eight</em> possible causes</h2>",
     "<h2>We have <em>3,044</em> real reports, and some causes are much rarer than others</h2>"),
    ('<span class="lab" style="display:block;margin-top:.3rem">narratives, all usable</span>',
     '<span class="lab" style="display:block;margin-top:.3rem">reports, each with a written narrative</span>'),
    ('<span class="lab" style="display:block">median words</span>', '<span class="lab" style="display:block">words in a typical report</span>'),
    ('<div><span class="big">2001–2026</span><span class="lab" style="display:block">report years</span></div>', ""),
    ("Source: U.S. DOT, PHMSA, Form F 7100.2. The 2010–present file has 623 fields; we kept six. The 2002–2009 historical file is merged in and older cause labels are mapped to today's eight. The model reads the narrative only.",
     "The reports come from the public incident file of the U.S. Department of Transportation (PHMSA). The model reads only the written narrative."),
    ('<span class="pill" style="color:var(--text)">Proposal draft: 3,027 · Final file: 3,044</span>',
     why("--stamp", "Why this matters",
         "Equipment failure is about five times more common than incorrect operation. A model could look accurate just by guessing the common causes, so we have to deal with this imbalance.")),

    # ---------- 5 · the test
    ('<p class="eyebrow"><b>Experiment design</b><i></i>Same split for every model</p>',
     '<p class="eyebrow"><b>2 · The data and the test</b><i></i>How we test fairly</p>'),
    ("<h2>One split. <em>Two ways</em> to handle imbalance.</h2>",
     "<h2>Every model is tested on <em>reports it has never seen</em></h2>"),
    ('<p class="credit">Stratified, seed 42. Validation and test sets are identical in both experiments.</p>',
     '<p class="credit">We split the reports once, and all three models use the same split. We tune on the validation reports and use the test reports only once, at the end.</p>'),
    ('<p class="xnote" style="min-height:0">Cleaning comes first: extra whitespace and HTML artifacts removed, all text lowercased.</p>',
     why("--stamp", "Why two experiments",
         "Rare causes are easy for a model to ignore. We tried two different fixes, class weights and synthetic reports, and compared them.")),
    ("'<b>Exp 1</b> trains on the 2,130 original rows. The loss is weighted so rare causes count more.'",
     "'<b>Experiment 1</b> uses the 2,130 original training reports. The loss counts mistakes on rare causes more heavily, so the model cannot ignore them.'"),
    ("'<b>Exp 2</b> adds <b>681 validated synthetic narratives</b> (hatched), written by an AI assistant from training reports only, for six smaller causes. Every cause reaches 300 rows. 2,811 in total, plain loss.'",
     "'<b>Experiment 2</b> adds <b>681 synthetic reports</b> (hatched), which an AI assistant wrote from training reports only. Each of the six smaller causes reaches 300 reports, and the loss is not weighted.'"),

    # ---------- 7 · BiGRU (model 1)
    ('<p class="eyebrow"><b>Model 1</b><i></i>BiGRU + FastText</p>',
     '<p class="eyebrow"><b>3 · The models</b><i></i>Model 1 of 3: BiGRU</p>'),
    ("<h2>Reads the narrative <em>both directions</em></h2>",
     "<h2>The BiGRU is our <em>simple baseline</em></h2>"),
    ('<div class="arch" id="arch-gru"></div>',
     '<div class="arch" id="arch-gru"></div>'
     + why("--gru", "Why we chose it",
           "A GRU reads a report one word at a time, in both directions, so every word can use the words on either side of it. It is simple and fast, which makes it a good baseline.")
     + why("--gru", "How we set it up",
           "We froze the FastText word vectors because they already know English, including rare technical words. We used dropout and early stopping so that the model does not memorize the training reports.")),
    ('<p class="callout" style="--c:var(--gru)">Oversampling lifted accuracy <b>7.6 points</b> but macro-F1 by only <b>0.007</b>. Incorrect-operation recall fell from <b>0.32 to 0.12</b>.</p>',
     '<p class="callout" style="--c:var(--gru)">Synthetic reports raised accuracy by <b>7.6 points</b>, but macro-F1 rose by only <b>0.007</b>, and recall for incorrect operation fell from <b>0.32 to 0.12</b>.</p>'),

    # ---------- 8 · BiLSTM (model 2)
    ('<p class="eyebrow"><b>Model 2</b><i></i>BiLSTM + attention + FastText</p>',
     '<p class="eyebrow"><b>3 · The models</b><i></i>Model 2 of 3: BiLSTM with attention</p>'),
    ("<h2>Learns <em>which words</em> carry the cause</h2>",
     "<h2>The BiLSTM adds attention to <em>focus on key words</em></h2>"),
    ('<div class="arch" id="arch-lstm"></div>',
     '<div class="arch" id="arch-lstm"></div>'
     + why("--lstm", "Why we chose it",
           "Reports are long, about a thousand characters on average. Attention lets the model give more weight to the few words that point to the cause, such as “corrosion” or “backhoe”, wherever they appear.")
     + why("--lstm", "How we set it up",
           "We gave it the same settings as the BiGRU, so any difference between the two comes from attention and not from tuning.")),
    ('<p class="callout" style="--c:var(--lstm)">Best RNN. Highest corrosion F1 of any run: <b>0.729</b>, with <b>0.805</b> precision. Oversampling cost it <b>0.067</b> macro-F1.</p>',
     '<p class="callout" style="--c:var(--lstm)">This is the better of the two recurrent models, and it has the best corrosion score of any run (F1 <b>0.729</b>). Synthetic reports lowered its macro-F1 by <b>0.067</b>.</p>'),

    # ---------- 9 · frozen BERT (model 3)
    ('<p class="eyebrow"><b>Model 3</b><i></i>bert-base-uncased, frozen</p>',
     '<p class="eyebrow"><b>3 · The models</b><i></i>Model 3 of 3: frozen BERT</p>'),
    ("<h2>Keep BERT frozen. <em>Train one small head.</em></h2>",
     "<h2>BERT already understands English, so we <em>train only a small layer</em></h2>"),
    ('<div class="row"><i class="sw" style="background:var(--paper)"></i><div>Narrative, up to <b>512</b> tokens</div></div>',
     '<div class="row"><i class="sw" style="background:var(--paper)"></i><div>The report goes in. BERT can read up to <b>512</b> tokens at once.</div></div>'),
    ('<div class="row"><i class="sw" style="background:rgba(160,190,200,.55)"></i><div><b>12 layers</b>, 12 heads, 768-d. All weights frozen.</div></div>',
     '<div class="row"><i class="sw" style="background:rgba(160,190,200,.55)"></i><div>BERT\'s <b>12 layers</b> read it. We never change them, because they were already trained on a huge amount of text.</div></div>'),
    ('<div class="row"><i class="sw" style="background:var(--gru)"></i><div>One 768-number vector per narrative</div></div>',
     '<div class="row"><i class="sw" style="background:var(--gru)"></i><div>The layers turn the report into one list of 768 numbers.</div></div>'),
    ('<div class="row"><i class="sw" style="background:var(--bert)"></i><div>Linear head 768 → 8. <b>6,152</b> trainable weights, against 903,688 in the BiLSTM.</div></div>',
     '<div class="row"><i class="sw" style="background:var(--bert)"></i><div>Only this small layer is trained. It has <b>6,152</b> weights, against 903,688 in the BiLSTM.</div></div>'),
    ('<p class="hint">DRAG TO ROTATE · HOVER A LAYER</p>',
     why("--bert", "Why we kept BERT frozen",
         "With only 3,044 reports, training a small layer is safer than retraining all 110 million weights, and it is fast. We used a higher learning rate than for the other models because only that small layer is learning.")
     + '<p class="hint">DRAG TO ROTATE · HOVER A LAYER</p>'),

    # ---------- 10 · the pooling choice
    ('<p class="eyebrow"><b>Model 3</b><i></i>Class-weighted loss, test set</p>',
     '<p class="eyebrow"><b>3 · The models</b><i></i>The choice that mattered most</p>'),
    ("<h2>One design choice moved macro-F1 by <em>0.25</em></h2>",
     "<h2>How BERT summarizes a report <em>changed the score by 0.25</em></h2>"),
    ("Same frozen BERT, same head, same data. Only the step that builds the narrative vector differs: one [CLS] token, or the average of every token.",
     "Our first plan used BERT's [CLS] token as the summary of the report, and it scored poorly. Averaging every token instead uses every word in the report and scored far better. Everything else stayed the same."),
    ("`<b>+${f3(d)}</b> macro-F1 and <b>+${((MM.bert.runs['1'].acc-MM.pool.runs['1'].acc)*100).toFixed(1)}</b> accuracy points over pooler_output`",
     "`Mean pooling gains <b>${f3(d)}</b> macro-F1 and <b>${((MM.bert.runs['1'].acc-MM.pool.runs['1'].acc)*100).toFixed(1)}</b> accuracy points over pooler_output.`"),

    # ---------- 11 · head to head
    ('<p class="eyebrow"><b>Results</b><i></i>458 held-out test narratives</p>',
     '<p class="eyebrow"><b>4 · The results</b><i></i>All six runs on the test reports</p>'),
    ("<h2>A close race: top three within <em>0.022</em></h2>",
     "<h2>Frozen BERT scored highest, but <em>the top three are close</em></h2>"),
    ('<div class="row mute" style="font-size:.84rem">Macro-F1 gives each of the 8 causes equal weight. Micro-F1 equals accuracy in single-label classification, so we report accuracy.</div>',
     '<div class="row mute" style="font-size:.92rem">We rank the models by macro-F1, which gives all eight causes equal weight, so rare causes count as much as common ones.</div>'),
    ('<div class="row mute" style="font-size:.84rem">Highest validation macro-F1 was BiGRU Exp 2 (0.586). The test ranking differs, so treat the top runs as close.</div>',
     '<div class="row mute" style="font-size:.92rem">The hatched bars use synthetic reports. They did not clearly help: they lowered the macro-F1 of the BiLSTM and of BERT.</div>'),

    # ---------- 12 · per cause
    ('<p class="eyebrow"><b>Per-cause results</b><i></i>Test F1 · click a row for precision and recall</p>',
     '<p class="eyebrow"><b>4 · The results</b><i></i>Click a row to see precision and recall</p>'),
    ("<h2>Easy causes are <em>easy</em>. Vague ones are not.</h2>",
     "<h2>Clear causes are easy to recognize, and <em>vague ones are not</em></h2>"),
    ('<div class="det" id="det"></div>',
     '<div class="det" id="det"></div>'
     + '<div class="story wide" style="--c:var(--bert)"><span class="k">What this tells us</span><p>Excavation damage is the easiest cause because its reports name the equipment, such as a backhoe or a trencher. “Other incident cause” is the hardest because its reports are vague. BERT does best on the rare causes, which is where the other two models struggle most.</p></div>'),

    # ---------- summary
    ('<p class="eyebrow"><b>Summary</b><i></i>Team 1</p>',
     '<p class="eyebrow"><b>6 · The takeaway</b><i></i>Team 1</p>'),
    ("<h2>Every incident has a moment of <em>truth</em></h2>",
     "<h2>Frozen BERT worked best, and <em>here is why</em></h2>"),
    ('<p class="lede" style="font-size:1.6rem;margin-top:1.6rem">Thank you. Questions?</p>',
     '<ol class="steps">'
     "<li><div>It already understands English, so only a small layer had to learn from our 3,044 reports.</div></li>"
     "<li><div>It generalized best: its score dropped the least from validation to test, and it was strongest on the rare causes.</div></li>"
     "<li><div>How we summarize each report mattered most: averaging every token beat the [CLS] token by 0.25 macro-F1.</div></li>"
     "</ol>"
     '<p class="note">We ran each model once on 458 test reports, so small gaps between the top runs are not reliable.</p>'
     '<p class="lede" style="font-size:1.15rem;margin-top:1rem">Thank you for listening, and we are happy to take your questions.</p>'),
    ("macro-F1 from mean pooling over [CLS]", "gain in macro-F1 from mean pooling instead of [CLS]"),

    # ---------- appendix · confusion matrix
    ('<p class="eyebrow"><b>Errors</b><i></i>Each row sums to 100% of that true cause</p>',
     '<p class="eyebrow"><b>Appendix</b><i></i>Where the models confuse causes</p>'),
    ("<h2>Where the models <em>confuse</em> causes</h2>",
     "<h2>This is where the models <em>confuse</em> one cause for another</h2>"),

    # ---------- the deck's script: slide positions become slide ids, room for more stakes, timer text
    ("if(n===3)startAuto(); else stopAuto();", "if(s.id==='s4')startAuto(); else stopAuto();"),
    ("if(n===2){$$('.fill',s)", "if(s.id==='s3'){$$('.fill',s)"),
    ("if(n===9&&window._barsReset)window._barsReset();", "if(s.id==='s10'&&window._barsReset)window._barsReset();"),
    ("for(let i=0;i<16;i++){const g=new THREE.Group();", "for(let i=0;i<24;i++){const g=new THREE.Group();"),
    ("TARGET 12:00 · LIMIT 13:00", "TARGET 12:30 · LIMIT 15:00"),
]

# the new slide that introduces the three models and why each one is there
PLAN_SLIDE = """<section class="slide s-plan" id="splan">
  <p class="eyebrow"><b>3 · The models</b><i></i>Our plan</p>
  <h2>We tried three models, and each one adds <em>a new idea</em></h2>
  <div class="body">
    <div class="mc" style="--c:var(--gru)"><span class="n">1</span><h3>BiGRU</h3><span class="who">Parva</span>
      <p>It reads a report word by word, in both directions. It is simple and fast, so it is our baseline.</p><span class="adds">Adds: reading order</span></div>
    <div class="mc" style="--c:var(--lstm)"><span class="n">2</span><h3>BiLSTM with attention</h3><span class="who">Muhammad</span>
      <p>It adds attention, so the model can focus on key words like “corrosion” or “backhoe” in a long report.</p><span class="adds">Adds: focus on key words</span></div>
    <div class="mc" style="--c:var(--bert)"><span class="n">3</span><h3>Frozen BERT</h3><span class="who">Sakina</span>
      <p>It already understands English from pretraining, so we train only a small layer on top of it.</p><span class="adds">Adds: prior knowledge of language</span></div>
    <div class="story wide" style="--c:var(--stamp)"><span class="k">Why this order</span><p>All three read the same reports, so any difference in the results comes from the model and not from the data. We start with the simplest model and add one idea at a time.</p></div>
  </div>
</section>"""

# slide order, as the story is told (ids are the section ids in the deck)
ORDER = ["s1", "s2", "s4", "s3", "s5", "splan", "s6", "s7", "s8", "s9", "s10", "s11", "s14", "sv", "sr", "s16", "s12"]

# the speaker plan, in the same order: (who, seconds, title, notes). Seconds add up to about 12.5 minutes,
# which leaves room for the game and for questions inside the 15-minute slot.
PLAN = [
    ("sakina", 20, "Title",
     ["Introduce the team and the three models: Parva built the BiGRU, Muhammad the BiLSTM with attention, and Sakina the frozen BERT.",
      "Tell the audience the plan: the problem, the data, the three models, the results, and then a short game."]),
    ("sakina", 50, "The problem",
     ["Pipeline failures can be deadly. San Bruno in 2010 killed 8 people, and Carlsbad in 2000 killed 12.",
      "After every incident the operator writes a report, and the cause is described somewhere in that text.",
      "Our question is whether a model can read the report and name the cause automatically."]),
    ("parva", 30, "The eight causes",
     ["The model must choose one of eight causes for each report. Drag the cards to read two or three real examples.",
      "Point out that excavation reports name a backhoe, while some other reports are vague. This matters later."]),
    ("parva", 45, "The data",
     ["We have 3,044 real reports from the public PHMSA incident file, and the model reads only the narrative.",
      "The causes are very uneven. Equipment failure has 787 reports and incorrect operation has 165.",
      "That is why a model could look accurate by guessing common causes, and why we need to handle the imbalance."]),
    ("parva", 50, "The test",
     ["We split the reports once, 70 / 15 / 15, and all three models use that split, so the comparison is fair.",
      "The validation reports are for tuning and for stopping training early. The test reports are used only once, at the end.",
      "To handle the imbalance we ran two experiments: class weights, and synthetic reports written by an AI assistant from training reports only."]),
    ("sakina", 45, "Our three models",
     ["We introduce the models in the order we tried them, and each one adds one idea.",
      "The BiGRU is the simple baseline, the BiLSTM adds attention for long reports, and BERT brings prior knowledge of English.",
      "All three read the same reports, so differences come from the model."]),
    ("parva", 55, "BiGRU",
     ["Why we chose it: it is simple and fast, so it shows what a basic model can do.",
      "Settings and why: FastText vectors are frozen because they already know English, including technical words. Dropout of 0.3 and early stopping on validation macro-F1 stop it from memorizing the training reports. Adam with a learning rate of 0.001 is the usual starting point for recurrent models.",
      "Result: 52.4 percent accuracy and 0.468 macro-F1 with class weights. Synthetic reports raised accuracy but not macro-F1, and recall for incorrect operation fell."]),
    ("muhammad", 55, "BiLSTM with attention",
     ["Why we chose it: reports are long, about a thousand characters, and attention lets the model focus on the words that point to the cause.",
      "Settings and why: exactly the same settings as the BiGRU, so any difference comes from attention and not from tuning.",
      "Result: 56.8 percent accuracy and 0.535 macro-F1. It is the better recurrent model and has the best corrosion score of any run."]),
    ("sakina", 55, "Frozen BERT",
     ["Why we chose it: BERT has already read a huge amount of English, so we only train a small layer on top. That layer has 6,152 weights, against 903,688 in the BiLSTM.",
      "Why frozen: with only 3,044 reports, training a small layer is safer than retraining 110 million weights, and training is fast.",
      "Why the learning rate is higher: only the small layer is learning, so 0.002 is fine. Training stopped early on validation macro-F1, like the other models."]),
    ("sakina", 50, "The pooling choice",
     ["This was the choice that mattered most. Our first plan used the [CLS] token as the summary, and it scored 0.305 macro-F1.",
      "Averaging every token gave 0.553, a gain of 0.25, with the same model, head and data.",
      "The lesson is that how you summarize the report mattered more than which model we picked."]),
    ("muhammad", 60, "Head to head",
     ["We rank by macro-F1 because it gives all eight causes equal weight, so rare causes count as much as common ones.",
      "Frozen BERT with mean pooling is first at 0.553, with 60.3 percent accuracy. The top three runs are within 0.022, and each is a single run, so be honest that the gap is small.",
      "Synthetic reports did not clearly help. They lowered the macro-F1 of the BiLSTM and of BERT, and only raised BiGRU accuracy."]),
    ("muhammad", 50, "Per-cause results",
     ["Excavation damage is easiest because its reports name the equipment. Other incident cause is hardest because its reports are vague.",
      "BERT is strongest on the rare causes, and that is where the other two struggle most. This is the main reason it won.",
      "BERT also dropped the least from validation to test, which suggests it generalizes better."]),
    ("sakina", 30, "The model in action",
     ["This is the real model on a real test report. Pick one, and the model stamps a cause and shows its confidence.",
      "The shaded words show which words pushed the model toward its answer. If you are running late, skip this slide."]),
    ("muhammad", 40, "Beat the model",
     ["Ask everyone to take out their phones and scan the code.",
      "Say why we play: we want to see how hard this task is for a person, because that tells us whether our model's score is good.",
      "The report comes from the test set, so the model has never seen it. Watch the counter, and move on when it stops growing."]),
    ("muhammad", 80, "Crowd vs model",
     ["Press V or click Reveal to show the correct answer and the model's answer.",
      "Whatever the result, tie it back to the findings: if people disagree, the labels are ambiguous, and that limits every model, not just ours.",
      "One report is only an illustration, not evidence. Press Shift+X afterwards to wipe the votes."]),
    ("all", 30, "Summary",
     ["Frozen BERT with mean pooling worked best: 0.553 macro-F1 and 60.3 percent accuracy.",
      "Three reasons: it already understands English, it generalized best, and the way we summarized each report mattered most.",
      "The caveat is that each model ran once on 458 test reports, so small gaps are not reliable. Then thank the audience and take questions."]),
    ("muhammad", 0, "Appendix: errors",
     ["Backup slide for questions. Each row shows how reports of one true cause were classified.",
      "For BERT with class weights, 69 percent of corrosion reports are right but 20 percent are called material failure. Incorrect operation is called equipment failure 28 percent of the time."]),
]
