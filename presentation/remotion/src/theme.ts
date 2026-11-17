// theme.ts — single source of truth. Palette sampled from the Moment of GroundTruth logo:
// white paper, stamp red (the one hero colour), charcoal and greys.
import { Easing } from "remotion";
import { loadFont as loadAnton } from "@remotion/google-fonts/Anton";
import { loadFont as loadArchivo } from "@remotion/google-fonts/Archivo";

const anton = loadAnton();
const archivo = loadArchivo();

export const theme = {
  colors: {
    bg: "#FBFBFA",
    bgAlt: "#EFEFEE",
    primary: "#C71F1B", // THE hero colour: max one element (or one group) per frame
    ink: "#1C1C1C",
    text: "#333333",
    textDim: "#767676",
    rule: "#D0D0D0",
    gru: "#9B9B9B",
    lstm: "#555555",
    bert: "#1C1C1C",
    glow: "rgba(199, 31, 27, 0.35)",
  },
  fonts: {
    display: `Impact, ${anton.fontFamily}, sans-serif`,
    body: `${archivo.fontFamily}, Helvetica, Arial, sans-serif`,
  },
  ease: {
    out: Easing.bezier(0.16, 1, 0.3, 1), // entrances
    inOut: Easing.bezier(0.83, 0, 0.17, 1), // moves
    in: Easing.bezier(0.7, 0, 0.84, 0), // exits only
  },
  spring: {
    snappy: { damping: 14, stiffness: 160, mass: 0.6 },
    smooth: { damping: 20, stiffness: 90, mass: 1 },
    bouncy: { damping: 11, stiffness: 170, mass: 0.7 },
  },
} as const;
