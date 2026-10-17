import type React from "react";
import {
  Interactive,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {
  ANNEAUX,
  ORDRE,
  VIEWBOX,
  bornesSecteur,
  pointImpact,
  polaire,
  quartier,
  rayon,
} from "./geometrie";
import { couleurs, police } from "./theme";

type CibleProps = {
  // Zone éclairée, comme sur la borne : « T20 », « D16 »… vide pour aucune.
  readonly surbrillance: string;
  // Image à laquelle la fléchette se plante ; négatif pour ne pas en lancer.
  readonly impact: number;
  readonly style?: React.CSSProperties;
};

const Flechette: React.FC<{
  readonly arrivee: number;
  readonly cible: string;
}> = ({ arrivee, cible }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const [x, y] = pointImpact(cible);
  const vol = 0.4 * fps;

  return (
    <g transform={`translate(${x} ${y})`}>
      <g
        style={{
          opacity: frame < arrivee - vol ? 0 : 1,
          translate: `${interpolate(frame, [arrivee - vol, arrivee], [520, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          })}px ${interpolate(frame, [arrivee - vol, arrivee], [760, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          })}px`,
          scale: interpolate(frame, [arrivee - vol, arrivee], [2.6, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          // Petit tremblement du fût au moment de l'impact.
          rotate: `${
            frame < arrivee
              ? 0
              : Math.sin((frame - arrivee) * 1.6) *
                interpolate(frame, [arrivee, arrivee + 0.5 * fps], [6, 0], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                })
          }deg`,
        }}
      >
        <line
          x1={0}
          y1={0}
          x2={34}
          y2={44}
          stroke="#c9d1d9"
          strokeWidth={5}
          strokeLinecap="round"
        />
        <line
          x1={34}
          y1={44}
          x2={92}
          y2={120}
          stroke="#6e7681"
          strokeWidth={22}
          strokeLinecap="round"
        />
        <line
          x1={92}
          y1={120}
          x2={150}
          y2={196}
          stroke={couleurs.texte}
          strokeWidth={8}
        />
        <polygon points="132,172 206,206 178,252 150,196" fill={couleurs.or} />
        <polygon points="132,172 178,140 206,206 150,196" fill="#e3b341" />
      </g>
    </g>
  );
};

const CibleInner: React.FC<CibleProps> = ({ surbrillance, impact, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const zone = surbrillance[0];
  const secteur = Number(surbrillance.slice(1));
  const pulsation = 0.55 + 0.45 * Math.sin((frame / fps) * Math.PI * 3);

  return (
    <svg viewBox={VIEWBOX} style={{ overflow: "visible", ...style }}>
      <circle r={540} fill="#0a0a0a" stroke={couleurs.bord} strokeWidth={6} />
      {ORDRE.map((s, i) => {
        const [a1, a2] = bornesSecteur(s);
        const sombre = i % 2 === 0;
        return ANNEAUX.map(({ zone: z, r1, r2 }) => {
          const eclaire = s === secteur && z === zone;
          const fond =
            z === "S"
              ? sombre
                ? "#1a1a1a"
                : "#efe3c4"
              : sombre
                ? "#c8242b"
                : "#13874a";
          return (
            <path
              key={`${s}-${z}-${r1}`}
              d={quartier(r1, r2, a1, a2)}
              fill={eclaire ? couleurs.or : fond}
              fillOpacity={eclaire ? pulsation : 1}
              stroke="#8a8f98"
              strokeWidth={1.5}
            />
          );
        });
      })}
      <circle
        r={rayon(15.9)}
        fill="#13874a"
        stroke="#8a8f98"
        strokeWidth={1.5}
      />
      <circle
        r={rayon(6.35)}
        fill="#c8242b"
        stroke="#8a8f98"
        strokeWidth={1.5}
      />
      {ORDRE.map((s) => {
        const [x, y] = polaire(196, -90 + ORDRE.indexOf(s) * 18);
        return (
          <text
            key={`n${s}`}
            x={x}
            y={y}
            fill={s === secteur ? couleurs.or : couleurs.texte}
            fontFamily={police}
            fontWeight={700}
            fontSize={50}
            textAnchor="middle"
            dominantBaseline="central"
          >
            {s}
          </text>
        );
      })}
      {impact >= 0 && surbrillance ? (
        <Flechette arrivee={impact} cible={surbrillance} />
      ) : null}
    </svg>
  );
};

export const Cible = Interactive.create({
  Component: CibleInner,
  layout: "none",
  schema: {
    surbrillance: {
      type: "string",
      default: "T20",
      description: "Zone éclairée (T20, D16…)",
    },
    impact: {
      type: "number",
      default: 30,
      integer: true,
      hiddenFromList: false,
      description: "Image de l'impact de la fléchette",
    },
  },
});
