import type React from "react";
import { Interactive } from "remotion";
import { couleurs, police } from "./theme";

type AtoutProps = {
  readonly children: React.ReactNode;
  readonly accent: string;
  readonly style?: React.CSSProperties;
};

// Une ligne de la scène « Et aussi » : pastille de couleur + texte.
const AtoutInner: React.FC<AtoutProps> = ({ children, accent, style }) => (
  <div
    style={{
      display: "flex",
      alignItems: "center",
      gap: 32,
      width: 920,
      padding: "36px 44px",
      borderRadius: 28,
      backgroundColor: couleurs.fond2,
      border: `2px solid ${couleurs.bord}`,
      color: couleurs.texte,
      fontFamily: police,
      fontSize: 50,
      fontWeight: 700,
      lineHeight: 1.2,
      ...style,
    }}
  >
    <div
      style={{
        flexShrink: 0,
        width: 22,
        height: 22,
        borderRadius: 11,
        backgroundColor: accent,
        boxShadow: `0 0 24px ${accent}`,
      }}
    />
    {children}
  </div>
);

export const Atout = Interactive.create({
  Component: AtoutInner,
  layout: "none",
  schema: {
    ...Interactive.childrenSchema,
    accent: {
      type: "color",
      default: couleurs.vert,
      description: "Couleur de la pastille",
    },
  },
});
