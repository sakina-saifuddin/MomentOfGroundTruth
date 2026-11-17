import React from "react";
import { AbsoluteFill, Audio, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { MODELS } from "../data";
import { BgMesh, Grade, Grain, RoughDefs, Vignette } from "../components/layers";
import { Counter, Entrance, WordReveal } from "../components/motion";

const BASE_Y = 900; // chart baseline from the top, px
const SCALE = 540; // px per 1.0 of macro-F1
const BAR_W = 150;
const BAR_GAP = 28;
const GROUP_CENTERS = [400, 960, 1520];
const MODEL_COLORS = [theme.colors.gru, theme.colors.lstm, theme.colors.bert];
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export const SixResults: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const s = (sec: number) => Math.round(sec * fps);

  const barStart = s(0.9);
  const hit = s(5); // the moment the winner is picked out
  const exitStart = durationInFrames - s(0.4);

  const exitP = interpolate(frame, [exitStart, durationInFrames - 2], [0, 1], { easing: theme.ease.in, ...clamp });
  const pick = interpolate(frame, [hit, hit + s(0.4)], [0, 1], { easing: theme.ease.out, ...clamp });
  const stampP = spring({ frame: frame - (hit + s(0.2)), fps, config: theme.spring.bouncy });
  const float = Math.sin(frame / 30) * 3;

  return (
    <AbsoluteFill style={{ fontFamily: theme.fonts.body, color: theme.colors.text }}>
      <RoughDefs />
      <BgMesh />

      <Sequence from={0}><Audio src={staticFile("sfx/whoosh.wav")} volume={0.5} /></Sequence>
      <Sequence from={barStart - 3}><Audio src={staticFile("sfx/whoosh.wav")} volume={0.35} /></Sequence>
      <Sequence from={hit + s(0.2) - 3}><Audio src={staticFile("sfx/thump.wav")} volume={0.8} /></Sequence>

      <AbsoluteFill style={{ opacity: 1 - exitP, transform: `translateY(${-42 * exitP}px)` }}>
        {/* title block */}
        <div style={{ position: "absolute", left: 120, top: 78, width: 1680 }}>
          <WordReveal text="SIX RESULTS, ONE WINNER" per={3} style={{ fontFamily: theme.fonts.display, fontSize: 150, lineHeight: 1.05, letterSpacing: "-0.01em", color: theme.colors.ink }} />
          <Entrance delay={s(0.6)} style={{ marginTop: 10, fontSize: 34, color: theme.colors.textDim }}>
            Macro-F1 on 458 unseen test reports. Every cause counts equally.
          </Entrance>
        </div>

        {/* callout: stamp + sentence, appears when the winner is picked */}
        <div style={{ position: "absolute", left: 980, top: 312, width: 820, opacity: stampP > 0.01 ? 1 : 0 }}>
          <div
            style={{
              display: "inline-block",
              transform: `translateY(${float}px) rotate(-4deg) scale(${interpolate(stampP, [0, 1], [2.4, 1])})`,
              opacity: Math.min(1, stampP * 1.6),
              border: `8px solid ${theme.colors.primary}`,
              color: theme.colors.primary,
              fontFamily: theme.fonts.display,
              fontSize: 68,
              lineHeight: 1,
              padding: "12px 24px 6px",
              letterSpacing: "0.04em",
              filter: "url(#rough)",
            }}
          >
            BEST MACRO-F1
          </div>
          <Entrance delay={hit + s(0.6)} style={{ marginTop: 18, fontSize: 30, lineHeight: 1.35, color: theme.colors.text, maxWidth: 740 }}>
            Frozen BERT with class weights scores <b style={{ color: theme.colors.ink }}>0.553</b>, ahead of both recurrent models.
          </Entrance>
        </div>

        {/* chart */}
        {MODELS.map((m, gi) => {
          const cx = GROUP_CENTERS[gi];
          const left = cx - BAR_W - BAR_GAP / 2;
          return (
            <React.Fragment key={m.name}>
              {[m.e1, m.e2].map((r, ei) => {
                const i = gi * 2 + ei;
                const p = spring({ frame: frame - barStart - i * 5, fps, config: theme.spring.smooth });
                const h = r.f1 * SCALE * p;
                const winner = gi === 2 && ei === 0;
                const dim = winner ? 1 : 1 - 0.55 * pick;
                const x = left + ei * (BAR_W + BAR_GAP);
                const col = MODEL_COLORS[gi];
                const hatch = `repeating-linear-gradient(135deg, ${col} 0 10px, #ffffff 10px 18px)`;
                return (
                  <React.Fragment key={ei}>
                    <div style={{ position: "absolute", left: x, bottom: 1080 - BASE_Y, width: BAR_W, height: h, opacity: dim, background: ei === 0 ? col : hatch, outline: ei === 1 ? `4px solid ${col}` : undefined, outlineOffset: -4 }}>
                      {winner && (
                        <div style={{ position: "absolute", inset: 0, background: theme.colors.primary, opacity: pick, boxShadow: `0 0 60px ${theme.colors.primary}66, 0 0 120px ${theme.colors.primary}33` }} />
                      )}
                    </div>
                    <div style={{ position: "absolute", left: x, width: BAR_W, textAlign: "center", bottom: 1080 - BASE_Y + h + 14, opacity: Math.min(1, p * 1.4) * dim, fontFamily: theme.fonts.display, fontSize: 50, color: winner && pick > 0.5 ? theme.colors.primary : theme.colors.ink }}>
                      <Counter to={r.f1} delay={barStart + i * 5} />
                    </div>
                    <div style={{ position: "absolute", left: x, width: BAR_W, top: BASE_Y + 12, textAlign: "center", fontSize: 22, fontWeight: 600, letterSpacing: "0.1em", color: theme.colors.textDim, opacity: p }}>
                      EXP {ei + 1}
                    </div>
                  </React.Fragment>
                );
              })}
              <Entrance delay={barStart + gi * 8 + 6} style={{ position: "absolute", left: cx - 280, width: 560, top: BASE_Y + 46, textAlign: "center" }}>
                <div style={{ fontFamily: theme.fonts.display, fontSize: 46, letterSpacing: "0.03em", color: theme.colors.ink }}>{m.name.toUpperCase()}</div>
                <div style={{ fontSize: 24, color: theme.colors.textDim, marginTop: 6 }}>
                  {m.who} · accuracy {(m.e1.acc * 100).toFixed(1)}% / {(m.e2.acc * 100).toFixed(1)}%
                </div>
              </Entrance>
            </React.Fragment>
          );
        })}

        {/* baseline rule */}
        <div style={{ position: "absolute", left: 120, width: interpolate(spring({ frame: frame - barStart, fps, config: theme.spring.smooth }), [0, 1], [0, 1680]), top: BASE_Y, height: 4, background: theme.colors.ink }} />
      </AbsoluteFill>

      <Grade />
      <Grain />
      <Vignette />
    </AbsoluteFill>
  );
};
