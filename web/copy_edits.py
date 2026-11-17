"""Wording changes applied to the project deck (docs/Moment of GroundTruth.html) when building the website.

Every entry is (old, new). Each old string must occur exactly once, so a change to the source deck that moves
the text fails the build instead of being skipped silently. The rule for new text: complete sentences that
read the way a person would say them aloud, not clipped fragments.
"""

EDITS: list[tuple[str, str]] = [
    # 1 · title
    ("Classifying gas transmission and gathering pipeline incident causes using BiGRU, BiLSTM with attention, and BERT-base.",
     "We trained three models to read pipeline incident reports and name the cause of each incident."),

    # 2 · why it matters
    ("<p>Defective seam weld and a pressure increase before the rupture.</p>",
     "<p>Investigators blamed a defective seam weld and a pressure increase before the rupture.</p>"),
    ("<p>Severe internal corrosion.</p>",
     "<p>Investigators blamed severe internal corrosion.</p>"),
    ("Operators file a written report within <b>30 days</b>. The cause is somewhere in the text.",
     "After every incident, the operator files a written report within <b>30 days</b>, and the cause is described somewhere in that text."),

    # 3 · the data
    ("<h2>3,044 reports, <em>eight</em> possible causes</h2>",
     "<h2>The data holds 3,044 reports, and each has one of <em>eight</em> causes</h2>"),
    ("Source: U.S. DOT, PHMSA, Form F 7100.2. The 2010–present file has 623 fields; we kept six. The 2002–2009 historical file is merged in and older cause labels are mapped to today's eight. The model reads the narrative only.",
     "The reports come from the U.S. DOT PHMSA incident file (Form F 7100.2). The file for 2010 to the present has 623 fields, and we kept six of them. We merged in the 2002 to 2009 file and mapped its older cause labels to today's eight causes. The model reads only the narrative."),
    ("Proposal draft: 3,027 · Final file: 3,044",
     "The proposal counted 3,027 reports, and the final file has 3,044."),

    # 4 · the eight causes
    ("Drag, click a card, or use the arrows", "Drag the cards, click one, or use the arrows."),
    ("<h2>Each cause, in the <em>operators' own words</em></h2>",
     "<h2>Operators describe each cause in <em>their own words</em></h2>"),

    # 5 · experiment design
    ("Same split for every model", "Every model sees the same data."),
    ("<h2>One split. <em>Two ways</em> to handle imbalance.</h2>",
     "<h2>All three models share one split and <em>two ways</em> of handling imbalance</h2>"),
    ("Stratified, seed 42. Validation and test sets are identical in both experiments.",
     "The split is stratified with seed 42, and the validation and test sets are identical in both experiments."),
    ("Cleaning comes first: extra whitespace and HTML artifacts removed, all text lowercased.",
     "Before splitting, we remove extra whitespace and HTML artifacts and lowercase all text."),

    # 6 · BiGRU
    ("<h2>Reads the narrative <em>both directions</em></h2>",
     "<h2>The BiGRU reads each narrative in <em>both directions</em></h2>"),

    # 7 · BiLSTM
    ("<h2>Learns <em>which words</em> carry the cause</h2>",
     "<h2>The BiLSTM learns <em>which words</em> carry the cause</h2>"),
    ("Best RNN. Highest corrosion F1 of any run: <b>0.729</b>, with <b>0.805</b> precision. Oversampling cost it <b>0.067</b> macro-F1.",
     "This is the better of the two recurrent models, and it has the highest corrosion F1 of any run (<b>0.729</b>, with <b>0.805</b> precision). Oversampling cost it <b>0.067</b> macro-F1."),

    # 8 · frozen BERT
    ("<h2>Keep BERT frozen. <em>Train one small head.</em></h2>",
     "<h2>We keep BERT frozen and <em>train only one small head</em></h2>"),

    # 9 · pooling
    ("<h2>One design choice moved macro-F1 by <em>0.25</em></h2>",
     "<h2>How we summarize the narrative changed macro-F1 by <em>0.25</em></h2>"),
    ("Same frozen BERT, same head, same data. Only the step that builds the narrative vector differs: one [CLS] token, or the average of every token.",
     "Both versions use the same frozen BERT, the same head and the same data. They differ only in how the narrative vector is built, either from the single [CLS] token or from the average of every token."),
    ("`<b>+${f3(d)}</b> macro-F1 and <b>+${((MM.bert.runs['1'].acc-MM.pool.runs['1'].acc)*100).toFixed(1)}</b> accuracy points over pooler_output`",
     "`Mean pooling gains <b>${f3(d)}</b> macro-F1 and <b>${((MM.bert.runs['1'].acc-MM.pool.runs['1'].acc)*100).toFixed(1)}</b> accuracy points over pooler_output.`"),

    # 10 · results
    ("<h2>A close race: top three within <em>0.022</em></h2>",
     "<h2>The three best runs finish within <em>0.022</em> of each other</h2>"),

    # 11 · per-cause
    ("Test F1 · click a row for precision and recall", "Click a row to see precision and recall."),
    ("<h2>Easy causes are <em>easy</em>. Vague ones are not.</h2>",
     "<h2>Clear causes are <em>easy</em> to recognize, and vague ones are not</h2>"),

    # 12 · errors
    ("Each row sums to 100% of that true cause", "Each row shows how reports of one true cause were classified."),
    ("<h2>Where the models <em>confuse</em> causes</h2>",
     "<h2>This is where the models <em>confuse</em> one cause for another</h2>"),

    # summary
    ("<p class=\"lede\" style=\"font-size:1.6rem;margin-top:1.6rem\">Thank you. Questions?</p>",
     "<p class=\"lede\" style=\"font-size:1.45rem;margin-top:1.6rem;max-width:34rem\">Frozen BERT with mean pooling performed best, and how we pooled the vectors mattered more than which architecture we chose.</p>"
     "<p class=\"lede\" style=\"font-size:1.2rem;margin-top:1rem\">Thank you for listening, and we are happy to take your questions.</p>"),
    ("macro-F1 from mean pooling over [CLS]", "gain in macro-F1 from mean pooling instead of [CLS]"),
]
