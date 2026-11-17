import React from "react";
import { AbsoluteFill, Audio, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { BgMesh, Grade, Grain, RoughDefs, Vignette } from "./layers";
import { Entrance, WordReveal } from "./motion";

export const C = theme.colors;
export const clampOpt = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
export const display = theme.fonts.display;

/** Every scene: five-layer stack, whoosh on entry, optional thumps, a fast exit. */
export const SceneFrame: React.FC<{ tag: string; index: number; thumps?: number[]; children: React.ReactNode }> = ({ tag, index, thumps = [], children }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const exitP = interpolate(frame, [durationInFrames - 12, durationInFrames - 2], [0, 1], { easing: theme.ease.in, ...clampOpt });
  const tagP = spring({ frame, fps: 30, config: theme.spring.smooth });
  return (
    <AbsoluteFill style={{ fontFamily: theme.fonts.body, color: C.text }}>
      <RoughDefs />
      <BgMesh />
      <Sequence from={0}><Audio src={staticFile("sfx/whoosh.wav")} volume={0.35} /></Sequence>
      {thumps.map((t) => (
        <Sequence key={t} from={Math.max(0, t - 3)}><Audio src={staticFile("sfx/thump.wav")} volume={0.7} /></Sequence>
      ))}
      <AbsoluteFill style={{ opacity: 1 - exitP, transform: `translateY(${-42 * exitP}px)` }}>
        <div style={{ position: "absolute", left: 120, top: 46, display: "flex", alignItems: "center", columnGap: 16, opacity: tagP, borderLeft: `5px solid ${C.ink}`, paddingLeft: 16, fontSize: 24, fontWeight: 700, letterSpacing: "0.16em", textTransform: "uppercase", color: C.ink }}>
          <span style={{ color: C.primary }}>{String(index).padStart(2, "0")}</span>
          <span>{tag}</span>
        </div>
        {children}
      </AbsoluteFill>
      <Grade />
      <Grain />
      <Vignette />
    </AbsoluteFill>
  );
};

export const Heading: React.FC<{ text: string; size?: number; delay?: number; hero?: string; style?: React.CSSProperties }> = ({ text, size = 120, delay = 0, hero, style }) => (
  <WordReveal text={text} delay={delay} per={3} hero={hero} style={{ fontFamily: display, fontSize: size, lineHeight: 1.04, letterSpacing: "-0.01em", color: C.ink, textTransform: "uppercase", ...style }} />
);

export const Para: React.FC<{ children: React.ReactNode; delay?: number; size?: number; dim?: boolean; style?: React.CSSProperties }> = ({ children, delay = 0, size = 34, dim, style }) => (
  <Entrance delay={delay} style={{ fontSize: size, lineHeight: 1.4, color: dim ? C.textDim : C.text, ...style }}>{children}</Entrance>
);

/** Staggered bullet list with square markers. Items are [bold lead, detail]. */
export const Bullets: React.FC<{ items: [string, string][]; delay?: number; per?: number; size?: number; style?: React.CSSProperties }> = ({ items, delay = 0, per = 14, size = 32, style }) => (
  <div style={{ display: "flex", flexDirection: "column", rowGap: 18, ...style }}>
    {items.map(([lead, detail], i) => (
      <Entrance key={i} delay={delay + i * per} style={{ display: "flex", columnGap: 18, alignItems: "baseline" }}>
        <div style={{ width: 14, height: 14, background: C.ink, flex: "none", transform: "translateY(-3px)" }} />
        <div style={{ fontSize: size, lineHeight: 1.35 }}>
          <b style={{ color: C.ink }}>{lead}</b>{detail ? <span style={{ color: C.text }}> {detail}</span> : null}
        </div>
      </Entrance>
    ))}
  </div>
);

/** Big number with a label under it, hairline on top. */
export const Stat: React.FC<{ value: React.ReactNode; label: string; delay?: number; width?: number; size?: number }> = ({ value, label, delay = 0, width = 260, size = 84 }) => (
  <Entrance delay={delay} style={{ width, borderTop: `5px solid ${C.ink}`, paddingTop: 10 }}>
    <div style={{ fontFamily: display, fontSize: size, lineHeight: 1, color: C.ink, fontVariantNumeric: "tabular-nums" }}>{value}</div>
    <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", color: C.textDim, marginTop: 8 }}>{label}</div>
  </Entrance>
);

/** One animated horizontal bar row. */
export const BarRow: React.FC<{ label: string; value: number; max: number; delay: number; right?: string; color?: string; hatch?: boolean; width: number; labelW?: number; height?: number; extra?: { value: number; color: string; progress: number } }> = ({ label, value, max, delay, right, color = C.ink, hatch, width, labelW = 330, height = 26, extra }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - delay, fps, config: theme.spring.smooth });
  const track = width - labelW - 110;
  const w = (value / max) * track * p;
  const ew = extra ? (extra.value / max) * track * extra.progress : 0;
  const bg = hatch ? `repeating-linear-gradient(135deg, ${color} 0 8px, #fff 8px 14px)` : color;
  return (
    <div style={{ display: "flex", alignItems: "center", columnGap: 16, width, opacity: Math.min(1, p * 1.5) }}>
      <div style={{ width: labelW, fontSize: 25, fontWeight: 600, color: C.ink, textAlign: "right", flex: "none" }}>{label}</div>
      <div style={{ width: track, height, background: "#EAEAE9", position: "relative", flex: "none" }}>
        <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: w, background: bg, outline: hatch ? `3px solid ${color}` : undefined, outlineOffset: -3 }} />
        {extra && <div style={{ position: "absolute", left: w, top: 0, bottom: 0, width: ew, background: `repeating-linear-gradient(135deg, ${extra.color} 0 8px, #fff 8px 14px)`, outline: `3px solid ${extra.color}`, outlineOffset: -3 }} />}
      </div>
      <div style={{ width: 90, fontFamily: display, fontSize: 32, color: C.ink, fontVariantNumeric: "tabular-nums" }}>{right}</div>
    </div>
  );
};

/** Rubber stamp that slams in at `at`. */
export const Stamp: React.FC<{ text: string; at: number; size?: number; color?: string; rotate?: number; style?: React.CSSProperties }> = ({ text, at, size = 70, color = C.primary, rotate = -4, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - at, fps, config: theme.spring.bouncy });
  const float = frame > at + 20 ? Math.sin(frame / 30) * 2.5 : 0;
  if (frame < at) return null;
  return (
    <div style={{ display: "inline-block", transform: `translateY(${float}px) rotate(${rotate}deg) scale(${interpolate(p, [0, 1], [2.4, 1])})`, opacity: Math.min(1, p * 1.6), border: `${Math.round(size / 9)}px solid ${color}`, color, fontFamily: display, fontSize: size, lineHeight: 1, padding: `${size * 0.16}px ${size * 0.34}px ${size * 0.08}px`, letterSpacing: "0.04em", textTransform: "uppercase", filter: "url(#rough)", ...style }}>
      {text}
    </div>
  );
};

/** A row of boxes joined by arrows; boxes enter in sequence. */
export const Flow: React.FC<{ nodes: string[]; delay?: number; per?: number; width: number; fontSize?: number; heroIndex?: number }> = ({ nodes, delay = 0, per = 12, width, fontSize = 24, heroIndex }) => {
  const gap = 34;
  const w = (width - gap * (nodes.length - 1)) / nodes.length;
  return (
    <div style={{ display: "flex", alignItems: "stretch", columnGap: 0, width }}>
      {nodes.map((n, i) => (
        <React.Fragment key={i}>
          <Entrance delay={delay + i * per} style={{ width: w, minHeight: 92, border: `3px solid ${i === heroIndex ? C.primary : C.ink}`, background: "#fff", display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", fontSize, fontWeight: 700, lineHeight: 1.2, padding: "10px 12px", color: i === heroIndex ? C.primary : C.ink }}>{n}</Entrance>
          {i < nodes.length - 1 && (
            <Entrance delay={delay + i * per + 6} style={{ width: gap, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 30, color: C.ink, fontWeight: 700 }}>→</Entrance>
          )}
        </React.Fragment>
      ))}
    </div>
  );
};
