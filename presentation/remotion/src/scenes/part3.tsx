import React from "react";
import { Img, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { MODELS, POOLER } from "../data";
import { BarRow, Bullets, C, Flow, Heading, Para, SceneFrame, Stamp, Stat, clampOpt, display } from "../components/kit";
import { Counter, Entrance } from "../components/motion";

const MODEL_COLORS = [theme.colors.gru, theme.colors.lstm, theme.colors.bert];

/* ---------------- 10 · THE SIX RESULTS ---------------- */
const BASE_Y = 880;
const SCALE = 400;
const BAR_W = 150;
const BAR_GAP = 28;
const CENTERS = [400, 960, 1520];

export const ResultsScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const hit = 420;
  const pick = interpolate(frame, [hit, hit + 14], [0, 1], { easing: theme.ease.out, ...clampOpt });
  return (
    <SceneFrame tag="The six results" index={10} thumps={[hit + 8]}>
      <div style={{ position: "absolute", left: 120, top: 100, width: 1680 }}>
        <Heading text="THE SIX RESULTS" size={120} />
        <Para delay={20} size={32} dim style={{ marginTop: 8 }}>3 models × 2 experiments, all scored on the same 458 unseen test reports. Bars: macro-F1.</Para>
      </div>

      <div style={{ position: "absolute", left: 1000, top: 304, width: 800 }}>
        <Stamp text="Best macro-F1" at={hit + 8} size={60} />
        <Entrance delay={hit + 30} style={{ marginTop: 14, fontSize: 28, lineHeight: 1.35, color: C.text }}>
          Frozen BERT, class weights: <b style={{ color: C.ink }}>0.553</b> macro-F1 and <b style={{ color: C.ink }}>60.3%</b> accuracy. BiGRU Exp 2 ties on accuracy, not on macro-F1.
        </Entrance>
        <Entrance delay={640} style={{ marginTop: 12, fontSize: 26, lineHeight: 1.35, color: C.textDim }}>
          Same BERT with the first-token shortcut: <b style={{ color: C.ink }}>{POOLER.e1.f1.toFixed(3)}</b> and <b style={{ color: C.ink }}>{POOLER.e2.f1.toFixed(3)}</b>. Always guessing the top cause: <b style={{ color: C.ink }}>26%</b> accuracy.
        </Entrance>
      </div>

      {MODELS.map((m, gi) => {
        const left = CENTERS[gi] - BAR_W - BAR_GAP / 2;
        return (
          <React.Fragment key={m.id}>
            {[m.e1, m.e2].map((r, ei) => {
              const i = gi * 2 + ei;
              const p = spring({ frame: frame - 50 - i * 8, fps, config: theme.spring.smooth });
              const h = r.f1 * SCALE * p;
              const winner = gi === 2 && ei === 0;
              const dim = winner ? 1 : 1 - 0.55 * pick;
              const x = left + ei * (BAR_W + BAR_GAP);
              const col = MODEL_COLORS[gi];
              return (
                <React.Fragment key={ei}>
                  <div style={{ position: "absolute", left: x, bottom: 1080 - BASE_Y, width: BAR_W, height: h, opacity: dim, background: ei === 0 ? col : `repeating-linear-gradient(135deg, ${col} 0 10px, #fff 10px 18px)`, outline: ei === 1 ? `4px solid ${col}` : undefined, outlineOffset: -4 }}>
                    {winner && <div style={{ position: "absolute", inset: 0, background: C.primary, opacity: pick, boxShadow: `0 0 60px ${C.primary}66, 0 0 120px ${C.primary}33` }} />}
                  </div>
                  <div style={{ position: "absolute", left: x, width: BAR_W, textAlign: "center", bottom: 1080 - BASE_Y + h + 12, opacity: Math.min(1, p * 1.4) * dim, fontFamily: display, fontSize: 48, color: winner && pick > 0.5 ? C.primary : C.ink }}>
                    <Counter to={r.f1} delay={50 + i * 8} />
                  </div>
                  <div style={{ position: "absolute", left: x, width: BAR_W, top: BASE_Y + 12, textAlign: "center", fontSize: 22, fontWeight: 600, letterSpacing: "0.1em", color: C.textDim, opacity: p }}>EXP {ei + 1}</div>
                </React.Fragment>
              );
            })}
            <Entrance delay={70 + gi * 10} style={{ position: "absolute", left: CENTERS[gi] - 290, width: 580, top: BASE_Y + 44, textAlign: "center" }}>
              <div style={{ fontFamily: display, fontSize: 42, letterSpacing: "0.03em", color: C.ink, textTransform: "uppercase" }}>{m.name}</div>
              <div style={{ fontSize: 24, color: C.textDim, marginTop: 4 }}>{m.who} · accuracy {(m.e1.acc * 100).toFixed(1)}% / {(m.e2.acc * 100).toFixed(1)}%</div>
            </Entrance>
          </React.Fragment>
        );
      })}
      <div style={{ position: "absolute", left: 120, width: interpolate(spring({ frame: frame - 40, fps, config: theme.spring.smooth }), [0, 1], [0, 1680]), top: BASE_Y, height: 4, background: C.ink }} />
    </SceneFrame>
  );
};

/* ---------------- 11 · WHY BERT WON ---------------- */
const SIX = [
  { l: "BiGRU · Exp 1", r: MODELS[0].e1 }, { l: "BiGRU · Exp 2", r: MODELS[0].e2 },
  { l: "BiLSTM · Exp 1", r: MODELS[1].e1 }, { l: "BiLSTM · Exp 2", r: MODELS[1].e2 },
  { l: "BERT · Exp 1", r: MODELS[2].e1 }, { l: "BERT · Exp 2", r: MODELS[2].e2 },
];
const REASONS = [
  { h: "It drops the least from validation to test", d: "We pick settings on the validation set. A big drop on the test set means a model fitted the validation set too closely. BERT drops least, the BiGRU drops most.", note: "macro-F1 drop, validation to test · lower is better" },
  { h: "Only 6,152 weights are free to memorize", d: "We have just 2,130 training reports. The BiLSTM has 903,688 trainable weights and can memorize them. BERT keeps its roughly 110 million pretrained weights frozen and trains one small layer.", note: "trainable weights · fewer is less to overfit" },
  { h: "It does best on the two hardest causes", d: "Other incident cause and Incorrect operation are the rarest. Macro-F1 counts them as much as the common causes, so the ranking is decided here. BERT does not win every cause: BiLSTM is better on Corrosion and Material failure.", note: "average F1 on the 2 hardest causes · higher is better" },
  { h: "It averages every token", d: "With BERT frozen, its first-token summary was never trained for this task. Averaging all tokens keeps the whole report and lifted macro-F1 by about 0.25.", note: "frozen BERT test macro-F1 · higher is better" },
];
const rare = (pc: readonly number[]) => (pc[6] + pc[7]) / 2;

const EvSet: React.FC<{ idx: number; dur: number }> = ({ idx, dur }) => {
  const frame = useCurrentFrame();
  const out = interpolate(frame, [dur - 8, dur], [1, 0], { easing: theme.ease.in, ...clampOpt });
  const reason = REASONS[idx];
  let rows: { label: string; value: number; max: number; right: string; color: string; hatch?: boolean }[] = [];
  if (idx === 0) rows = SIX.map((s, i) => ({ label: s.l, value: s.r.val - s.r.f1, max: 0.12, right: "−" + (s.r.val - s.r.f1).toFixed(3), color: i === 4 ? C.primary : C.ink, hatch: i % 2 === 1 }));
  if (idx === 1) rows = [
    { label: "BiGRU", value: 0, max: 1, right: "not recorded", color: C.ink },
    { label: "BiLSTM + attention", value: 903688, max: 903688, right: "903,688", color: C.ink },
    { label: "Frozen BERT", value: 6152, max: 903688, right: "6,152", color: C.primary },
  ];
  if (idx === 2) rows = SIX.map((s, i) => ({ label: s.l, value: rare(s.r.pc), max: 0.4, right: rare(s.r.pc).toFixed(3), color: i === 4 ? C.primary : C.ink, hatch: i % 2 === 1 }));
  if (idx === 3) rows = [
    { label: "First token · Exp 1", value: POOLER.e1.f1, max: 0.6, right: POOLER.e1.f1.toFixed(3), color: C.textDim },
    { label: "First token · Exp 2", value: POOLER.e2.f1, max: 0.6, right: POOLER.e2.f1.toFixed(3), color: C.textDim, hatch: true },
    { label: "Average · Exp 1", value: MODELS[2].e1.f1, max: 0.6, right: MODELS[2].e1.f1.toFixed(3), color: C.primary },
    { label: "Average · Exp 2", value: MODELS[2].e2.f1, max: 0.6, right: MODELS[2].e2.f1.toFixed(3), color: C.ink, hatch: true },
  ];
  return (
    <div style={{ opacity: out }}>
      <Entrance delay={0} style={{ fontSize: 28, lineHeight: 1.4, color: C.text, marginBottom: 22 }}>{reason.d}</Entrance>
      <div style={{ display: "flex", flexDirection: "column", rowGap: 18 }}>
        {rows.map((r, i) => (
          <BarRow key={i} label={r.label} value={r.value} max={r.max} delay={10 + i * 6} right={r.right} color={r.color} hatch={r.hatch} width={820} labelW={250} height={28} />
        ))}
      </div>
      <Entrance delay={40} style={{ marginTop: 18, fontSize: 22, fontWeight: 700, letterSpacing: "0.08em", textTransform: "uppercase", color: C.textDim }}>{reason.note}</Entrance>
    </div>
  );
};

export const WhyScene: React.FC = () => {
  const frame = useCurrentFrame();
  const active = frame < 600 ? Math.floor(frame / 150) : -1;
  return (
    <SceneFrame tag="Why one model won" index={11}>
      <div style={{ position: "absolute", left: 120, top: 100, width: 840 }}>
        <Heading text="WHY BERT COMES FIRST" size={104} />
        <div style={{ marginTop: 34, borderTop: `5px solid ${C.ink}` }}>
          {REASONS.map((r, i) => {
            const on = active === i;
            return (
              <Entrance key={i} delay={16 + i * 8} style={{ display: "flex", alignItems: "center", columnGap: 18, padding: "20px 14px", background: on ? C.ink : "transparent", color: on ? "#fff" : C.ink, borderBottom: `1px solid ${C.rule}`, transition: "none" }}>
                <div style={{ fontFamily: display, fontSize: 48, lineHeight: 1, color: on ? C.primary : C.rule, width: 46, flex: "none" }}>{i + 1}</div>
                <div style={{ fontSize: 31, fontWeight: 700, lineHeight: 1.25 }}>{r.h}</div>
              </Entrance>
            );
          })}
        </div>
      </div>
      <div style={{ position: "absolute", left: 1000, top: 130, width: 820 }}>
        {[0, 1, 2, 3].map((i) => (
          <Sequence key={i} from={i * 150} durationInFrames={150} layout="none"><EvSet idx={i} dur={150} /></Sequence>
        ))}
        <Sequence from={600} durationInFrames={300} layout="none">
          <div style={{ border: `4px solid ${C.primary}`, padding: "30px 34px", background: "#fff" }}>
            <Entrance delay={0} style={{ fontFamily: display, fontSize: 64, color: C.primary, textTransform: "uppercase" }}>Be careful</Entrance>
            <Bullets delay={14} per={22} size={30} style={{ marginTop: 18 }} items={[
              ["One seed, 458 test reports.", "Accuracy is uncertain by about ±4.5 points, so BERT's 60.3% vs BiLSTM's 56.8% is not a proven gap."],
              ["Measured patterns, not proven causes.", "Confirming a reason would need repeated runs with different seeds."],
              ["Separate code.", "The three models were trained with their own code and settings, so some of the gap may come from training choices."],
            ]} />
          </div>
        </Sequence>
      </div>
    </SceneFrame>
  );
};

/* ---------------- 12 · LIMITATIONS ---------------- */
const LIMITS: [string, string][] = [
  ["One seed, 458 test reports.", "Small gaps between models are not proof. Repeating runs would show which hold."],
  ["Separate training code.", "Each of us trained our own model, so some differences come from settings, not architecture."],
  ["Imbalanced causes.", "Equipment failure is 25.9% of reports, Incorrect operation 5.4%. No model scored above 0.28 F1 on Other incident cause."],
  ["Synthetic text can hurt.", "Exp 2 lowered macro-F1 for the BiLSTM (0.535 to 0.468) and for BERT (0.553 to 0.531)."],
  ["BERT reads 512 tokens.", "About 6% of reports are longer and get cut off. Only the beginning is used."],
  ["Labels are reporting choices.", "Operators file the reports, and older cause categories were mapped to today's eight."],
  ["It labels the past.", "The model reads a finished report. It does not predict whether or when an incident will happen."],
  ["App head is a retrain.", "The head inside the demo app scores 57.9% and 0.522, close to but below the 0.553 Colab run. BiGRU's weight count was not recorded."],
];

export const LimitsScene: React.FC = () => (
  <SceneFrame tag="What holds it back" index={12}>
    <div style={{ position: "absolute", left: 120, top: 100, width: 1680 }}>
      <Heading text="LIMITATIONS, SAID OUT LOUD" size={112} />
    </div>
    <div style={{ position: "absolute", left: 120, top: 300, width: 1680, display: "grid", gridTemplateColumns: "1fr 1fr", columnGap: 70, rowGap: 24 }}>
      {LIMITS.map(([a, b], i) => (
        <Entrance key={a} delay={30 + i * 34} style={{ display: "flex", columnGap: 20, alignItems: "flex-start", borderTop: `3px solid ${C.ink}`, paddingTop: 12 }}>
          <div style={{ fontFamily: display, fontSize: 44, lineHeight: 1, color: C.primary, width: 40, flex: "none" }}>{i + 1}</div>
          <div style={{ fontSize: 28, lineHeight: 1.35, color: C.text }}><b style={{ color: C.ink }}>{a}</b> {b}</div>
        </Entrance>
      ))}
    </div>
  </SceneFrame>
);

/* ---------------- 13 · THE APP ---------------- */
export const AppScene: React.FC = () => (
  <SceneFrame tag="From notebook to app" index={13} thumps={[250]}>
    <div style={{ position: "absolute", left: 120, top: 110, width: 1680 }}>
      <Heading text="FROM NOTEBOOK TO APP" size={116} />
      <Para delay={20} size={34} style={{ marginTop: 10 }}>A Streamlit app: paste a report, get the cause, a photo of what it looks like, and a SHAP explanation of which words decided it.</Para>
    </div>
    <div style={{ position: "absolute", left: 120, top: 400 }}>
      <Flow nodes={["Paste a narrative", "Same cleaning as training", "Frozen BERT + 6,152-weight layer", "Cause stamped + SHAP words"]} delay={40} per={18} width={1680} fontSize={30} heroIndex={3} />
    </div>
    <div style={{ position: "absolute", left: 120, top: 620, display: "flex", columnGap: 50 }}>
      <Stat value="0.1 s" label="to predict" delay={130} width={300} />
      <Stat value="15–40 s" label="for SHAP words" delay={146} width={380} />
      <Stat value="57.9%" label="app test accuracy" delay={162} width={360} />
      <Stat value="OCI VM" label="where it runs" delay={178} width={340} />
    </div>
    <Para delay={210} size={32} style={{ position: "absolute", left: 120, top: 860, width: 1560 }}>Treat a prediction as a second opinion, not a finding. The model reads the narrative only and never sees the operator name.</Para>
    <div style={{ position: "absolute", left: 1500, top: 90 }}><Stamp text="Second opinion" at={250} size={44} /></div>
  </SceneFrame>
);

/* ---------------- 14 · CLOSING ---------------- */
export const ClosingScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - 16, fps, config: theme.spring.bouncy });
  return (
    <SceneFrame tag="Questions" index={14} thumps={[20]}>
      <div style={{ position: "absolute", left: 120, top: 170, width: 1000 }}>
        <Heading text="DIG IN." size={230} />
        <Para delay={30} size={38} style={{ marginTop: 18 }}>Thank you. Pick any report in the app, or ask us why a model got one wrong.</Para>
        <div style={{ marginTop: 36, display: "flex", flexDirection: "column", rowGap: 12 }}>
          {[["Sakina Saifuddin", "Frozen BERT", MODEL_COLORS[2]], ["Muhammad Murtaza", "BiLSTM with attention", MODEL_COLORS[1]], ["Parva Shah", "BiGRU", MODEL_COLORS[0]]].map(([n, r, c], i) => (
            <Entrance key={n} delay={60 + i * 8} style={{ display: "flex", alignItems: "center", columnGap: 18, fontSize: 32 }}>
              <div style={{ width: 22, height: 22, background: c }} /><b style={{ color: C.ink }}>{n}</b><span style={{ color: C.textDim }}>{r}</span>
            </Entrance>
          ))}
        </div>
        <Entrance delay={100} style={{ marginTop: 30, fontSize: 28, fontWeight: 700, color: C.primary }}>github.com/sakina-saifuddin/MomentOfGroundTruth</Entrance>
        <Entrance delay={112} style={{ marginTop: 10, fontSize: 22, color: C.textDim, maxWidth: 900 }}>Data: PHMSA public incident reports, U.S. Department of Transportation. Cause photos from Wikimedia Commons, credited in the repository.</Entrance>
      </div>
      <div style={{ position: "absolute", left: 1210, top: 220, width: 560, height: 510, opacity: Math.min(1, p * 1.5), transform: `scale(${interpolate(p, [0, 1], [1.6, 1])}) rotate(${interpolate(p, [0, 1], [-12, -3])}deg)` }}>
        <Img src={staticFile("logo-stamp.png")} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
      </div>
    </SceneFrame>
  );
};
