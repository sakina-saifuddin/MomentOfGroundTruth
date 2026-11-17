import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { theme } from "../theme";

/** Layer 1: never a flat background. Two slow-drifting soft blobs on paper. */
export const BgMesh: React.FC = () => {
  const frame = useCurrentFrame();
  const d1 = Math.sin(frame / 55) * 50;
  const d2 = Math.cos(frame / 70) * 40;
  return (
    <AbsoluteFill style={{ background: theme.colors.bg }}>
      <div style={{ position: "absolute", width: 1300, height: 1300, borderRadius: "50%", top: -600, left: -400 + d1, filter: "blur(60px)", background: `radial-gradient(circle, ${theme.colors.primary}14, transparent 62%)` }} />
      <div style={{ position: "absolute", width: 1100, height: 1100, borderRadius: "50%", bottom: -560, right: -300 - d2, filter: "blur(70px)", background: `radial-gradient(circle, ${theme.colors.ink}12, transparent 65%)` }} />
    </AbsoluteFill>
  );
};

/** Layer 4: colour grade above all content. */
export const Grade: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <AbsoluteFill style={{ backgroundColor: theme.colors.primary, mixBlendMode: "soft-light", opacity: 0.1 }} />
    <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0.05), transparent 28%, transparent 72%, rgba(0,0,0,0.08))" }} />
  </AbsoluteFill>
);

/** Layer 5a: procedural film grain, no asset file. */
export const Grain: React.FC = () => {
  const frame = useCurrentFrame();
  const noise = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='220' height='220' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E")`;
  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        backgroundImage: noise,
        backgroundSize: "220px",
        backgroundPosition: `${(frame * 7) % 220}px ${(frame * 13) % 220}px`,
        opacity: 0.06,
        mixBlendMode: "multiply",
      }}
    />
  );
};

/** Layer 5b: vignette, the topmost layer. */
export const Vignette: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none", background: "radial-gradient(ellipse at center, transparent 58%, rgba(0,0,0,0.12) 100%)" }} />
);

/** Rubber-stamp roughness filter, defined once and referenced by url(#rough). */
export const RoughDefs: React.FC = () => (
  <svg width={0} height={0} style={{ position: "absolute" }}>
    <filter id="rough" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves={2} seed={4} result="n" />
      <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.7 1.72" result="m" />
      <feComposite in="SourceGraphic" in2="m" operator="in" result="eaten" />
      <feTurbulence type="turbulence" baseFrequency=".05" numOctaves={2} seed={9} result="w" />
      <feDisplacementMap in="eaten" in2="w" scale={4} />
    </filter>
  </svg>
);
