import React from "react";
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { CAUSES, COMPANY } from "../data";
import { BarRow, Bullets, C, Flow, Heading, Para, SceneFrame, Stamp, Stat, clampOpt, display } from "../components/kit";
import { Counter, Entrance } from "../components/motion";

/* ---------------- 1 · TITLE ---------------- */
export const TitleScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const p = spring({ frame: frame - 18, fps, config: theme.spring.bouncy });
  const kb = interpolate(frame, [0, durationInFrames], [1, 1.08], { easing: theme.ease.inOut });
  const breathe = 1 + Math.sin(frame / 22) * 0.012;
  return (
    <SceneFrame tag="Group 1 · EDS 6352 · NLP · University of Houston" index={1} thumps={[22]}>
      <div style={{ position: "absolute", left: 120, top: 170, width: 1050 }}>
        <Heading text="MOMENT OF GROUNDTRUTH" size={164} />
        <Para delay={40} size={40} style={{ marginTop: 26, maxWidth: 900 }}>Reading gas pipeline incident reports and stamping the root cause.</Para>
        <div style={{ marginTop: 40, display: "flex", flexDirection: "column", rowGap: 14 }}>
          {[["Sakina Saifuddin", "Frozen BERT", theme.colors.bert], ["Muhammad Murtaza", "BiLSTM with attention", theme.colors.lstm], ["Parva Shah", "BiGRU", theme.colors.gru]].map(([n, r, c], i) => (
            <Entrance key={n} delay={62 + i * 8} style={{ display: "flex", alignItems: "center", columnGap: 18, fontSize: 32 }}>
              <div style={{ width: 22, height: 22, background: c }} />
              <b style={{ color: C.ink }}>{n}</b><span style={{ color: C.textDim }}>{r}</span>
            </Entrance>
          ))}
        </div>
      </div>
      <div style={{ position: "absolute", left: 1170, top: 190, width: 620, height: 566, opacity: Math.min(1, p * 1.5), transform: `scale(${interpolate(p, [0, 1], [1.7, 1]) * breathe}) rotate(${interpolate(p, [0, 1], [-14, -3])}deg)` }}>
        <Img src={staticFile("logo-stamp.png")} style={{ width: "100%", height: "100%", objectFit: "contain", transform: `scale(${kb})` }} />
      </div>
    </SceneFrame>
  );
};

/* ---------------- 2 · STORY (career fair) ---------------- */
const BEATS = [
  { at: 20, t: "It started at a career fair." },
  { at: 140, t: `I stopped at the booth of ${COMPANY} and talked to one of their recruiters.` },
  { at: 290, t: "He mentioned how much of the work is reading incident reports and deciding what caused each one." },
  { at: 470, t: "That is a language problem, so it was a good fit for my NLP project. I chose it." },
];

const Person: React.FC<{ x: number; color: string; delay: number; flip?: boolean }> = ({ x, color, delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - delay, fps, config: theme.spring.smooth });
  const bob = Math.sin((frame + x) / 26) * 3;
  return (
    <div style={{ position: "absolute", left: x, top: 470, width: 110, opacity: p, transform: `translateY(${interpolate(p, [0, 1], [50, 0]) + bob}px)` }}>
      <div style={{ width: 70, height: 70, borderRadius: "50%", background: color, margin: "0 auto" }} />
      <div style={{ width: 110, height: 190, borderRadius: "50px 50px 0 0", background: color, marginTop: 10 }} />
    </div>
  );
};

export const StoryScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const activeIdx = BEATS.reduce((a, b, i) => (frame >= b.at ? i : a), 0);
  const boothP = spring({ frame: frame - 130, fps, config: theme.spring.smooth });
  const paperP = spring({ frame: frame - 290, fps, config: theme.spring.smooth });
  const stampAt = 480;
  return (
    <SceneFrame tag="How it started" index={2} thumps={[stampAt]}>
      <div style={{ position: "absolute", left: 120, top: 130, width: 880 }}>
        <Heading text="HOW IT STARTED" size={112} />
        <div style={{ marginTop: 40, display: "flex", flexDirection: "column", rowGap: 22 }}>
          {BEATS.map((b, i) => {
            const p = spring({ frame: frame - b.at, fps, config: theme.spring.smooth });
            const dim = i < activeIdx ? 0.42 : 1;
            return (
              <div key={i} style={{ display: "flex", columnGap: 22, alignItems: "flex-start", opacity: p * dim, transform: `translateX(${interpolate(p, [0, 1], [-50, 0])}px)` }}>
                <div style={{ fontFamily: display, fontSize: 52, lineHeight: 1, color: i === activeIdx ? C.primary : C.ink, width: 50, flex: "none" }}>{i + 1}</div>
                <div style={{ fontSize: 34, lineHeight: 1.35, color: C.text, paddingTop: 4 }}>{b.t}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* booth */}
      <div style={{ position: "absolute", left: 1090, top: 150, width: 700, height: 130, background: C.ink, display: "flex", alignItems: "center", justifyContent: "center", color: "#fff", fontFamily: display, fontSize: 50, letterSpacing: "0.05em", textTransform: "uppercase", opacity: boothP, transform: `translateY(${interpolate(boothP, [0, 1], [-40, 0])}px)`, textAlign: "center", padding: "0 20px" }}>{COMPANY}</div>
      <div style={{ position: "absolute", left: 1090, top: 280, width: 700, height: 440, background: "#EDEDEC", border: `3px solid ${C.rule}`, opacity: boothP }} />
      <Person x={1200} color={theme.colors.gru} delay={30} />
      <Person x={1560} color={theme.colors.lstm} delay={44} />
      <div style={{ position: "absolute", left: 1070, top: 690, width: 740, height: 36, background: C.rule, opacity: boothP }} />
      {/* report stack */}
      <div style={{ position: "absolute", left: 1370, top: 560, width: 170, height: 130, opacity: paperP, transform: `translateY(${interpolate(paperP, [0, 1], [-60, 0])}px)` }}>
        {[0, 1, 2, 3].map((k) => (
          <div key={k} style={{ position: "absolute", left: k * 4, top: -k * 8 + 30, width: 150, height: 100, background: "#fff", border: `2px solid ${C.ink}`, transform: `rotate(${(k - 1.5) * 2}deg)` }}>
            <div style={{ margin: "14px 12px", height: 6, background: C.rule }} /><div style={{ margin: "8px 12px", height: 6, background: C.rule }} /><div style={{ margin: "8px 12px", height: 6, width: 70, background: C.rule }} />
          </div>
        ))}
      </div>
      {frame >= 300 && frame < stampAt && (
        <div style={{ position: "absolute", left: 1420, top: 440, fontFamily: display, fontSize: 90, color: C.ink, opacity: Math.min(1, paperP) }}>?</div>
      )}
      <div style={{ position: "absolute", left: 1290, top: 330 }}><Stamp text="Root cause" at={stampAt} size={56} /></div>
    </SceneFrame>
  );
};

/* ---------------- 3 · IDEA ---------------- */
const NARR = "on october 26, 2025, a sensor line for a pilot-operated psv on a compressor unit failed due to excessive vibration. the failure of the sensor line led to an unintended release of gas. the sensor line was immediately repaired, replaced with flex tubing, and additional supports have been installed to prevent future occurrences.";

export const IdeaScene: React.FC = () => {
  const frame = useCurrentFrame();
  const typed = Math.floor(interpolate(frame, [30, 250], [0, NARR.length], { easing: theme.ease.inOut, ...clampOpt }));
  const sheetP = spring({ frame: frame - 10, fps: 30, config: theme.spring.smooth });
  const markP = interpolate(frame, [262, 290], [0, 1], { easing: theme.ease.out, ...clampOpt });
  const key = "failed due to excessive vibration";
  const kStart = NARR.indexOf(key);
  const shown = NARR.slice(0, typed);
  const before = shown.slice(0, kStart);
  const inKey = shown.slice(kStart, kStart + key.length);
  const after = shown.slice(kStart + key.length);
  return (
    <SceneFrame tag="The idea" index={3} thumps={[320]}>
      <div style={{ position: "absolute", left: 120, top: 130, width: 860 }}>
        <Heading text="THE IDEA" size={130} />
        <Bullets delay={20} per={16} size={36} style={{ marginTop: 34 }} items={[["In:", "the written account of a pipeline incident."], ["Out:", "one of 8 causes, stamped on it."], ["Why:", "nobody should have to read thousands of reports by hand to find the pattern."]]} />
        <div style={{ marginTop: 44, display: "flex", flexDirection: "column", rowGap: 14 }}>
          {[["Moment", "the instant a cause gets decided"], ["Ground truth", "machine learning's word for the correct label"], ["Ground", "pipelines are buried, the root cause is something we dig for"]].map(([w, d], i) => (
            <Entrance key={w} delay={150 + i * 16} style={{ display: "flex", columnGap: 20, alignItems: "baseline", borderTop: `1px solid ${C.rule}`, paddingTop: 10 }}>
              <div style={{ fontFamily: display, fontSize: 32, color: C.primary, width: 210, flex: "none", textTransform: "uppercase" }}>{w}</div>
              <div style={{ fontSize: 28, color: C.text }}>{d}</div>
            </Entrance>
          ))}
        </div>
      </div>
      <div style={{ position: "absolute", left: 1080, top: 130, width: 720 }}>
        <Entrance delay={6} style={{ fontSize: 22, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", color: C.textDim, marginBottom: 12 }}>A real test-set report</Entrance>
        <div style={{ background: "#fff", border: `3px solid ${C.ink}`, boxShadow: `14px 14px 0 ${C.rule}`, padding: "30px 34px", height: 520, opacity: sheetP, transform: `translateY(${interpolate(sheetP, [0, 1], [40, 0])}px)`, fontSize: 31, lineHeight: 1.55, color: C.text }}>
          {before}
          <span style={{ background: `linear-gradient(${C.ink}, ${C.ink}) no-repeat left bottom / ${markP * 100}% 5px` }}>{inKey}</span>
          {after}
          {typed < NARR.length && <span style={{ opacity: Math.floor(frame / 8) % 2 }}>|</span>}
        </div>
        <div style={{ marginTop: 34 }}><Stamp text="Equipment failure" at={320} size={62} /></div>
      </div>
    </SceneFrame>
  );
};

/* ---------------- 4 · DATA ---------------- */
export const DataScene: React.FC = () => {
  const frame = useCurrentFrame();
  const hot = interpolate(frame, [400, 430], [0, 1], { easing: theme.ease.out, ...clampOpt });
  return (
    <SceneFrame tag="The data" index={4}>
      <div style={{ position: "absolute", left: 120, top: 130, width: 860 }}>
        <Heading text="THE DATA" size={130} />
        <div style={{ display: "flex", columnGap: 24, marginTop: 30 }}>
          <Stat value={<Counter to={3044} decimals={0} delay={20} />} label="narratives" delay={16} width={250} />
          <Stat value="2002–2026" label="years covered" delay={24} width={340} size={64} />
          <Stat value={<Counter to={136} decimals={0} delay={30} />} label="median words" delay={32} width={230} />
        </div>
        <Para delay={60} size={30} style={{ marginTop: 34 }}>
          Public PHMSA gas transmission and gathering incident reports (U.S. Department of Transportation, Form PHMSA F 7100.2). We merged the 2002–2009 history with 2010 to today and mapped older cause labels into today's eight.
        </Para>
        <Entrance delay={110} style={{ marginTop: 30, fontSize: 22, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", color: C.textDim }}>How we cleaned every narrative</Entrance>
        <div style={{ marginTop: 12 }}><Flow nodes={["Unescape HTML", "Remove tags", "Fix spaces", "Lowercase"]} delay={120} per={10} width={860} fontSize={23} /></div>
      </div>
      <div style={{ position: "absolute", left: 1010, top: 150, width: 800, display: "flex", flexDirection: "column", rowGap: 24 }}>
        <Entrance delay={8} style={{ fontSize: 22, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", color: C.textDim }}>Reports per cause</Entrance>
        {CAUSES.map((c, i) => (
          <BarRow key={c.title} label={c.title.replace(" of pipe or weld", "")} value={c.n} max={800} delay={30 + i * 6} right={String(c.n)} width={800} labelW={310} color={i === 0 && hot > 0.5 ? C.primary : C.ink} />
        ))}
        <Entrance delay={400} style={{ fontSize: 30, lineHeight: 1.4, color: C.text, marginTop: 6 }}>
          Equipment failure is <b style={{ color: C.ink }}>25.9%</b> of reports, incorrect operation only <b style={{ color: C.ink }}>5.4%</b>. A model that always guesses the top cause is right about 26% of the time. That is the bar to beat.
        </Entrance>
      </div>
    </SceneFrame>
  );
};

/* ---------------- 5 · SPLIT ---------------- */
export const SplitScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const piles = [
    { n: 2130, pct: "70%", name: "Train", note: "the model learns from these", color: C.ink },
    { n: 456, pct: "15%", name: "Validation", note: "we pick settings with these", color: theme.colors.gru },
    { n: 458, pct: "15%", name: "Test", note: "sealed until the end", color: C.primary },
  ];
  const total = 1680, gap = 12;
  const widths = [0.7, 0.15, 0.15].map((f) => f * (total - gap * 2));
  return (
    <SceneFrame tag="How we split it" index={5} thumps={[60]}>
      <div style={{ position: "absolute", left: 120, top: 120, width: 1680 }}>
        <Heading text="STUDY. PRACTICE. FINAL EXAM." size={108} />
      </div>
      <div style={{ position: "absolute", left: 120, top: 300, width: total, display: "flex", columnGap: gap }}>
        {piles.map((p, i) => {
          const sp = spring({ frame: frame - 30 - i * 10, fps, config: theme.spring.smooth });
          return (
            <div key={p.name} style={{ width: widths[i] * sp, overflow: "hidden", opacity: Math.min(1, sp * 1.4) }}>
              <div style={{ width: widths[i], height: 200, background: p.color, color: "#fff", padding: "20px 24px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                <div style={{ fontFamily: display, fontSize: i === 0 ? 96 : 60, lineHeight: 1 }}><Counter to={p.n} decimals={0} delay={36 + i * 10} /></div>
                <div style={{ fontSize: 26, fontWeight: 700, letterSpacing: "0.08em", textTransform: "uppercase" }}>{p.name} · {p.pct}</div>
              </div>
              <div style={{ fontSize: 24, color: C.textDim, marginTop: 10, width: widths[i], whiteSpace: i === 0 ? "normal" : "normal" }}>{p.note}</div>
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", left: 120, top: 600, width: 1680 }}>
        <Bullets delay={110} per={22} size={33} items={[
          ["Stratified.", "Every pile holds the eight causes in the same proportions, so rare causes show up in train, validation and test."],
          ["Leakage-safe.", "Near-identical narratives stay in the same pile, so the test set cannot contain a copy of something the model studied."],
          ["Reproducible.", "A fixed seed of 42 rebuilds the exact same split for all three models."],
          ["Same exam for everyone.", "All three models and both experiments are scored on the same 458 test reports."],
        ]} />
      </div>
    </SceneFrame>
  );
};
