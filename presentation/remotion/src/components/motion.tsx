import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";

/** Premium entrance: opacity + rise + scale, on a spring. */
export const Entrance: React.FC<{ delay?: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ delay = 0, children, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - delay, fps, config: theme.spring.smooth });
  return (
    <div style={{ opacity: p, transform: `translateY(${interpolate(p, [0, 1], [40, 0])}px) scale(${interpolate(p, [0, 1], [0.94, 1])})`, ...style }}>
      {children}
    </div>
  );
};

/** Word-by-word reveal, staggered. Pixel gap, never em. */
export const WordReveal: React.FC<{ text: string; delay?: number; per?: number; style?: React.CSSProperties; hero?: string }> = ({ text, delay = 0, per = 3, style, hero }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={{ display: "flex", flexWrap: "wrap", columnGap: 30, rowGap: 0, ...style }}>
      {text.split(" ").map((word, i) => {
        const p = spring({ frame: frame - delay - i * per, fps, config: theme.spring.snappy });
        return (
          <span key={i} style={{ display: "inline-block", opacity: p, transform: `translateY(${interpolate(p, [0, 1], [34, 0])}px)`, color: hero === word ? theme.colors.primary : undefined }}>
            {word}
          </span>
        );
      })}
    </div>
  );
};

/** Animated counter with tabular numbers. */
export const Counter: React.FC<{ to: number; delay?: number; decimals?: number; suffix?: string; style?: React.CSSProperties }> = ({ to, delay = 0, decimals = 3, suffix = "", style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const v = interpolate(spring({ frame: frame - delay, fps, config: { damping: 30, stiffness: 60 } }), [0, 1], [0, to]);
  const txt = decimals === 0 ? Math.round(v).toLocaleString("en-US") : v.toFixed(decimals);
  return <span style={{ fontVariantNumeric: "tabular-nums", ...style }}>{txt}{suffix}</span>;
};
