// Synthesizes a tiny deterministic SFX kit as 16-bit mono WAVs. No downloads.
import { writeFileSync, mkdirSync } from "node:fs";

const SR = 44100;
mkdirSync(new URL("../public/sfx/", import.meta.url), { recursive: true });

function wav(samples) {
  const buf = Buffer.alloc(44 + samples.length * 2);
  buf.write("RIFF", 0); buf.writeUInt32LE(36 + samples.length * 2, 4); buf.write("WAVE", 8);
  buf.write("fmt ", 12); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(1, 22);
  buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 2, 28); buf.writeUInt16LE(2, 32); buf.writeUInt16LE(16, 34);
  buf.write("data", 36); buf.writeUInt32LE(samples.length * 2, 40);
  samples.forEach((v, i) => buf.writeInt16LE(Math.max(-1, Math.min(1, v)) * 32767 | 0, 44 + i * 2));
  return buf;
}
let seed = 12345;
const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296) * 2 - 1;

// whoosh: noise burst through a sweeping low-pass, swell then fade
{
  const n = Math.floor(SR * 0.55), out = new Float32Array(n); let lp = 0;
  for (let i = 0; i < n; i++) {
    const t = i / n, a = Math.sin(Math.PI * Math.pow(t, 0.7)) * 0.5, k = 0.04 + 0.5 * Math.sin(Math.PI * t);
    lp += (rnd() - lp) * k; out[i] = lp * a * 1.6;
  }
  writeFileSync(new URL("../public/sfx/whoosh.wav", import.meta.url), wav(out));
}
// thump: sine pitch-drop 140 -> 45 Hz with a short click, for the stamp landing
{
  const n = Math.floor(SR * 0.5), out = new Float32Array(n); let ph = 0;
  for (let i = 0; i < n; i++) {
    const t = i / SR, f = 45 + 95 * Math.exp(-t * 18); ph += (2 * Math.PI * f) / SR;
    out[i] = Math.sin(ph) * Math.exp(-t * 7) * 0.9 + (i < 400 ? rnd() * 0.3 * (1 - i / 400) : 0);
  }
  writeFileSync(new URL("../public/sfx/thump.wav", import.meta.url), wav(out));
}
console.log("wrote public/sfx/whoosh.wav and thump.wav");
