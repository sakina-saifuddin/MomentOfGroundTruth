import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { CAUSES, MODELS } from "../data";
import { BarRow, Bullets, C, Flow, Heading, Para, SceneFrame, Stamp, clampOpt, display } from "../components/kit";
import { Counter, Entrance } from "../components/motion";

type Model = (typeof MODELS)[number];

const MODEL_COLOR: Record<string, string> = { gru: theme.colors.gru, lstm: theme.colors.lstm, bert: theme.colors.bert };

/* ---------------- 6-8 · ONE SCENE PER MODEL ---------------- */
const ModelScene: React.FC<{
  index: number;
  m: Model;
  plain: string;
  flow: string[];
  facts: [string, string][];
  takeaway: React.ReactNode;
  stamp?: { text: string; at: number };
}> = ({ index, m, plain, flow, facts, takeaway, stamp }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const col = MODEL_COLOR[m.id];
  return (
    <SceneFrame tag={`Model ${index - 5} of 3 · built by ${m.who}`} index={index} thumps={stamp ? [stamp.at] : []}>
      <div style={{ position: "absolute", left: 120, top: 120, width: 880 }}>
        <Entrance delay={4} style={{ display: "flex", alignItems: "center", columnGap: 16, marginBottom: 14 }}>
          <div style={{ width: 26, height: 26, background: col }} />
          <div style={{ fontSize: 28, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", color: C.ink }}>{m.who}</div>
        </Entrance>
        <Heading text={m.name.toUpperCase()} size={96} delay={6} />
        <Para delay={30} size={30} style={{ marginTop: 22 }}>{plain}</Para>
        <div style={{ marginTop: 28 }}><Flow nodes={flow} delay={60} per={12} width={880} fontSize={22} heroIndex={flow.length - 1} /></div>
        <div style={{ marginTop: 30, borderTop: `1px solid ${C.rule}` }}>
          {facts.map(([k, v], i) => (
            <Entrance key={k} delay={130 + i * 8} style={{ display: "flex", justifyContent: "space-between", padding: "9px 0", borderBottom: `1px solid ${C.rule}`, fontSize: 26 }}>
              <span style={{ color: C.textDim }}>{k}</span><b style={{ color: C.ink }}>{v}</b>
            </Entrance>
          ))}
        </div>
      </div>

      <div style={{ position: "absolute", left: 1060, top: 110, width: 740 }}>
        <div style={{ display: "flex", columnGap: 0, borderTop: `5px solid ${C.ink}` }}>
          {[m.e1, m.e2].map((r, i) => (
            <Entrance key={i} delay={20 + i * 10} style={{ flex: 1, padding: "12px 12px 12px " + (i ? 24 : 0) + "px", borderLeft: i ? `1px solid ${C.rule}` : undefined }}>
              <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", color: C.ink }}>{i === 0 ? "Exp 1 · class weights" : "Exp 2 · oversampling"}</div>
              <div style={{ fontFamily: display, fontSize: 96, lineHeight: 1.05, color: col === theme.colors.gru ? C.textDim : col, fontVariantNumeric: "tabular-nums" }}>
                <Counter to={r.acc * 100} decimals={1} delay={30 + i * 10} suffix="%" />
              </div>
              <div style={{ fontSize: 24, color: C.textDim }}>test accuracy · macro-F1 <b style={{ color: C.ink }}>{r.f1.toFixed(3)}</b></div>
            </Entrance>
          ))}
        </div>
        <div style={{ marginTop: 22, background: "#fff", border: `3px solid ${C.ink}`, boxShadow: `10px 10px 0 ${C.rule}`, padding: "16px 22px" }}>
          <div style={{ display: "flex", columnGap: 26, fontSize: 21, fontWeight: 700, marginBottom: 6, color: C.ink }}>
            <span><i style={{ display: "inline-block", width: 26, height: 12, background: col, marginRight: 8 }} />Exp 1</span>
            <span><i style={{ display: "inline-block", width: 26, height: 12, marginRight: 8, background: `repeating-linear-gradient(135deg, ${col} 0 5px, #fff 5px 9px)`, outline: `2px solid ${col}`, outlineOffset: -2 }} />Exp 2</span>
            <span style={{ marginLeft: "auto", fontWeight: 500, color: C.textDim }}>F1 score for each cause</span>
          </div>
          {CAUSES.map((c, i) => {
            const p = spring({ frame: frame - 90 - i * 5, fps, config: theme.spring.smooth });
            return (
              <div key={c.title} style={{ display: "flex", alignItems: "center", columnGap: 14, padding: "4px 0", opacity: Math.min(1, p * 1.5) }}>
                <div style={{ width: 268, fontSize: 22, fontWeight: 600, color: C.ink }}>{c.title.replace(" of pipe or weld", "").replace(" damage", " dmg")}</div>
                <div style={{ flex: 1, display: "flex", flexDirection: "column", rowGap: 3 }}>
                  <div style={{ height: 10, width: `${m.e1.pc[i] * 100 * p}%`, background: col }} />
                  <div style={{ height: 10, width: `${m.e2.pc[i] * 100 * p}%`, background: `repeating-linear-gradient(135deg, ${col} 0 5px, #fff 5px 9px)`, outline: `2px solid ${col}`, outlineOffset: -2 }} />
                </div>
                <div style={{ width: 96, textAlign: "right", fontSize: 21, fontWeight: 700, fontVariantNumeric: "tabular-nums", lineHeight: 1.15, color: C.ink }}>
                  {m.e1.pc[i].toFixed(2)}<div style={{ fontWeight: 500, color: C.textDim }}>{m.e2.pc[i].toFixed(2)}</div>
                </div>
              </div>
            );
          })}
        </div>
        <Entrance delay={300} style={{ marginTop: 22, borderLeft: `8px solid ${col === theme.colors.gru ? C.ink : col}`, paddingLeft: 20, fontSize: 27, lineHeight: 1.4, color: C.text }}>{takeaway}</Entrance>
      </div>
      {stamp && <div style={{ position: "absolute", left: 130, top: 880 }}><Stamp text={stamp.text} at={stamp.at} size={54} /></div>}
    </SceneFrame>
  );
};

export const GruScene: React.FC = () => (
  <ModelScene
    index={6}
    m={MODELS[0]}
    plain="Parva's model reads each report forwards and backwards at the same time, word by word, and keeps a short memory of what it has read. It starts from pretrained FastText word vectors and learns the rest from our reports."
    flow={["Report words", "FastText vectors", "GRU → and ←", "8 cause scores"]}
    facts={[["Reads", "both directions"], ["Word vectors", "FastText, pretrained"], ["Trainable weights", "not recorded"], ["Best epoch", "14 of 19 run · 12 of 17"]]}
    takeaway={<>Oversampling lifted accuracy by 7.6 points, from 52.4% to 60.0%, but macro-F1 barely moved (0.468 to 0.475). It got better at common causes, not rare ones: recall on <b style={{ color: C.ink }}>Incorrect operation fell from 32% to 12%</b>.</>}
  />
);

export const LstmScene: React.FC = () => (
  <ModelScene
    index={7}
    m={MODELS[1]}
    plain="Muhammad's model has a longer memory than the GRU, plus attention: it learns which words to underline before it decides. It also starts from pretrained FastText word vectors."
    flow={["Report words", "FastText vectors", "LSTM → and ←", "Attention", "8 cause scores"]}
    facts={[["Trainable weights", "903,688"], ["Settings", "2 layers · 128 hidden · dropout .3"], ["Training", "batch 32 · lr 1e-3 · 300 words max"], ["Best epoch", "22 of 27 run · 17 of 22"]]}
    takeaway={<>Class weights worked better than synthetic data here. With Exp 2, macro-F1 fell from 0.535 to 0.468, and <b style={{ color: C.ink }}>Other incident cause dropped from 0.245 to 0.042 F1</b>.</>}
  />
);

export const BertScene: React.FC = () => (
  <ModelScene
    index={8}
    m={MODELS[2]}
    plain="My model: BERT already understands English from reading huge amounts of text. We keep all 12 layers frozen and train only one small layer on top that turns BERT's summary of a report into 8 scores."
    flow={["Report tokens", "BERT, frozen", "Average of tokens", "Layer 768 → 8"]}
    facts={[["Trainable weights", "6,152"], ["Summary vector", "average of every token"], ["Reads at most", "512 tokens per report"], ["Best epoch", "11 of 16 run · 18 of 20"]]}
    takeaway={<>Same <b style={{ color: C.ink }}>60.3% accuracy</b> in both experiments, and the highest macro-F1 of all six runs: 0.553 with class weights. Synthetic data did not help the frozen model (0.531).</>}
    stamp={{ text: "Best macro-F1", at: 420 }}
  />
);

/* ---------------- 9 · TWO EXPERIMENTS + SYNTHETIC DATA ---------------- */
const STEPS: [string, string][] = [
  ["Pick", "three real narratives of one cause, from the training set only."],
  ["Ask", "a language model (Gemini, GPT-OSS or Qwen) for a new 100 to 300 word report in the same style, lowercase, not copying a sentence."],
  ["Check", "reject malformed text, any text that names the cause label, and exact duplicates."],
  ["Add", "the survivors to the training pile. Validation and test are never touched."],
];

export const ExperimentsScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const phase1Out = interpolate(frame, [318, 330], [1, 0], { easing: theme.ease.in, ...clampOpt });
  const synBase = 470;
  const rowsNow = Math.round(2130 + 681 * interpolate(frame, [synBase, synBase + 150], [0, 1], { easing: theme.ease.inOut, ...clampOpt }));
  return (
    <SceneFrame tag="The two experiments" index={9} thumps={[synBase]}>
      {/* phase 1 */}
      <div style={{ position: "absolute", left: 120, top: 120, width: 860, opacity: phase1Out }}>
        <Heading text="EXPERIMENT 1" size={120} />
        <Para delay={14} size={36} style={{ marginTop: 6, color: C.primary }}><b style={{ color: C.primary }}>Class-weighted loss</b></Para>
        <Bullets delay={30} per={18} size={34} style={{ marginTop: 26 }} items={[["Train on the original 2,130 reports.", ""], ["Rare causes get a bigger weight", "in the loss, so a mistake on Incorrect operation costs more than one on Equipment failure."], ["No new data.", "Only the importance of each mistake changes."]]} />
      </div>
      {/* phase 2 */}
      <div style={{ position: "absolute", left: 120, top: 120, width: 900 }}>
        <Heading text="EXPERIMENT 2" size={120} delay={332} />
        <Para delay={344} size={36} style={{ marginTop: 6 }}><b style={{ color: C.primary }}>Smart oversampling with synthetic data</b></Para>
        <Para delay={360} size={30} style={{ marginTop: 14 }}>Goal: lift every smaller cause up to <b style={{ color: C.ink }}>300</b> training reports. <b style={{ color: C.ink }}>681</b> synthetic narratives bring training to <b style={{ color: C.ink }}>2,811</b> rows. No class weights.</Para>
        <Entrance delay={400} style={{ marginTop: 22, fontSize: 22, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", color: C.textDim }}>How we made them</Entrance>
        <div style={{ marginTop: 10, display: "flex", flexDirection: "column", rowGap: 12 }}>
          {STEPS.map(([a, b], i) => (
            <Entrance key={a} delay={415 + i * 40} style={{ display: "flex", columnGap: 18, alignItems: "baseline" }}>
              <div style={{ fontFamily: display, fontSize: 34, color: C.primary, width: 170, flex: "none", textTransform: "uppercase", whiteSpace: "nowrap" }}>{i + 1} {a}</div>
              <div style={{ fontSize: 27, lineHeight: 1.35, color: C.text }}>{b}</div>
            </Entrance>
          ))}
        </div>
      </div>

      {/* bars */}
      <div style={{ position: "absolute", left: 1040, top: 140, width: 760, display: "flex", flexDirection: "column", rowGap: 22 }}>
        <Entrance delay={10} style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
          <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", color: C.textDim }}>Training reports per cause</div>
          <div style={{ fontFamily: display, fontSize: 52, color: C.ink, fontVariantNumeric: "tabular-nums" }}>{rowsNow.toLocaleString("en-US")}</div>
        </Entrance>
        {CAUSES.map((c, i) => {
          const sp = interpolate(frame, [synBase + 10 + i * 8, synBase + 90 + i * 8], [0, 1], { easing: theme.ease.out, ...clampOpt });
          return (
            <BarRow key={c.title} label={c.title.replace(" of pipe or weld", "")} value={c.train} max={600} delay={24 + i * 5} width={760} labelW={290} right={String(c.train + Math.round(c.syn * sp))} extra={{ value: c.syn, color: C.primary, progress: sp }} />
          );
        })}
        <Entrance delay={760} style={{ fontSize: 27, lineHeight: 1.4, color: C.text }}>
          Red hatching is synthetic. Validation <b style={{ color: C.ink }}>456</b> and test <b style={{ color: C.ink }}>458</b> are identical in both experiments. Synthetic text never reaches them.
        </Entrance>
      </div>
    </SceneFrame>
  );
};
