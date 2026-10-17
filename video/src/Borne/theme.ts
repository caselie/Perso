import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Mêmes couleurs que l'interface de la borne (web/static/css/app.css).
export const couleurs = {
  fond: "#0d1117",
  fond2: "#161b22",
  fond3: "#21262d",
  bord: "#30363d",
  texte: "#e6edf3",
  texteDoux: "#8b949e",
  vert: "#2ea043",
  vertClair: "#3fb950",
  rouge: "#da3633",
  or: "#d29922",
};

// Polices variables embarquées dans public/fonts : le rendu ne dépend pas du
// réseau (et passe derrière un proxy que Chromium ne reconnaît pas).
export const police = "Inter";
export const policeMono = "JetBrains Mono";

loadFont({
  family: police,
  url: staticFile("fonts/Inter.woff2"),
  weight: "100 900",
});
loadFont({
  family: policeMono,
  url: staticFile("fonts/JetBrainsMono.woff2"),
  weight: "100 800",
});
