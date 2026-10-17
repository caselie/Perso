import { Audio } from "@remotion/media";
import { lightLeak } from "@remotion/effects/light-leak";
import { TransitionSeries } from "@remotion/transitions";
import type React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  random,
  Solid,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// Anime une photo fixe en plan de cinéma : deux calques (sujet détouré +
// décor rebouché) déplacés à des vitesses différentes pour la parallaxe,
// profondeur de champ, lumière, reflets sur l'eau, grain et bandes 2.39:1.
// Les calques sont produits par scripts/calques-photo.py dans public/perso/.

const LARGEUR = 1920;
const HAUTEUR = 1080;
const RATIO_PHOTO = 1500 / 2000;
const BANDE = Math.round((HAUTEUR - LARGEUR / 2.39) / 2);

type Camera = {
  // Échelle de la photo (1 = largeur de l'image).
  readonly echelle: number;
  // Point de la photo (0–1) placé au centre de l'image.
  readonly x: number;
  readonly y: number;
  // Glissement latéral qui révèle la parallaxe, en px.
  readonly glisse: number;
  readonly roulis: number;
  // Flou du décor (profondeur de champ), en px.
  readonly flou: number;
  // Intensité de la lumière dorée et du flare (0–1).
  readonly lumiere: number;
};

type PlanProps = {
  readonly duree: number;
  readonly debut: Camera;
  readonly fin: Camera;
};

const placement = (echelle: number, x: number, y: number, glisse: number) => {
  const w = LARGEUR * echelle;
  const h = w * RATIO_PHOTO;
  const gauche = Math.min(
    0,
    Math.max(LARGEUR - w, LARGEUR / 2 - x * w + glisse),
  );
  const haut = Math.min(0, Math.max(HAUTEUR - h, HAUTEUR / 2 - y * h));
  return { width: w, height: h, left: gauche, top: haut };
};

const Plan: React.FC<PlanProps> = ({ duree, debut, fin }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [0, duree - 1], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.45, 0.05, 0.35, 1),
  });
  const cam = Object.fromEntries(
    Object.keys(debut).map((k) => {
      const cle = k as keyof Camera;
      return [cle, debut[cle] + (fin[cle] - debut[cle]) * p];
    }),
  ) as Record<keyof Camera, number>;

  // Le décor bouge et grossit moins vite que le sujet : c'est la parallaxe.
  const echelleDecor = cam.echelle * (1 - 0.025 * p);
  const sujet = placement(cam.echelle, cam.x, cam.y, cam.glisse);
  const decor = placement(echelleDecor, cam.x, cam.y, cam.glisse * 0.4);
  const frequence = 0.011 + 0.002 * Math.sin(frame / 9);

  return (
    <AbsoluteFill
      style={{ overflow: "hidden", rotate: `${cam.roulis}deg`, scale: 1.02 }}
    >
      <svg width={0} height={0} style={{ position: "absolute" }}>
        <filter id="eau">
          <feTurbulence
            type="fractalNoise"
            baseFrequency={`${frequence} ${frequence * 3.2}`}
            numOctaves={2}
            seed={4}
          />
          <feDisplacementMap in="SourceGraphic" scale={9} />
        </filter>
      </svg>
      <div
        style={{
          position: "absolute",
          ...decor,
          filter: `blur(${cam.flou}px)`,
        }}
      >
        <Img
          src={staticFile("perso/fond.jpg")}
          style={{ width: "100%", height: "100%" }}
        />
        {/* Ondulation de l'eau, limitée au bassin. */}
        <Img
          src={staticFile("perso/fond.jpg")}
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            clipPath: "inset(63% 0 0 0)",
            filter: "url(#eau)",
          }}
        />
        {/* Brume : le lointain s'éclaircit et se réchauffe. */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "linear-gradient(180deg, rgba(255,226,190,0.22) 0%, rgba(255,226,190,0.10) 45%, rgba(255,226,190,0) 62%)",
          }}
        />
      </div>
      <Img
        src={staticFile("perso/premier-plan.png")}
        style={{
          position: "absolute",
          ...sujet,
          filter: `brightness(${1 + 0.04 * cam.lumiere * Math.sin(frame / 22)})`,
        }}
      />
      {/* Lumière de fin d'après-midi qui glisse depuis le haut à droite. */}
      <AbsoluteFill
        style={{
          mixBlendMode: "screen",
          opacity: 0.25 + 0.45 * cam.lumiere,
          background: `radial-gradient(ellipse 70% 60% at ${88 - 20 * p}% ${4 + 8 * p}%, rgba(255,196,120,0.75), rgba(255,160,80,0.18) 45%, rgba(0,0,0,0) 70%)`,
        }}
      />
      <Flare intensite={cam.lumiere} progression={p} />
    </AbsoluteFill>
  );
};

const Flare: React.FC<{
  readonly intensite: number;
  readonly progression: number;
}> = ({ intensite, progression }) => {
  const sx = LARGEUR * (0.86 - 0.12 * progression);
  const sy = HAUTEUR * 0.12;
  const reflets = [
    { t: 0.35, r: 46, c: "rgba(255,210,150,0.35)" },
    { t: 0.62, r: 22, c: "rgba(170,220,255,0.30)" },
    { t: 0.85, r: 90, c: "rgba(255,180,120,0.14)" },
    { t: 1.15, r: 34, c: "rgba(200,255,220,0.22)" },
  ];
  return (
    <AbsoluteFill style={{ mixBlendMode: "screen", opacity: intensite }}>
      <div
        style={{
          position: "absolute",
          left: sx - 260,
          top: sy - 260,
          width: 520,
          height: 520,
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(255,240,215,0.9), rgba(255,200,130,0.25) 35%, rgba(0,0,0,0) 70%)",
        }}
      />
      {reflets.map(({ t, r, c }) => {
        const x = sx + (LARGEUR / 2 - sx) * 2 * t;
        const y = sy + (HAUTEUR / 2 - sy) * 2 * t;
        return (
          <div
            key={t}
            style={{
              position: "absolute",
              left: x - r,
              top: y - r,
              width: 2 * r,
              height: 2 * r,
              borderRadius: "50%",
              background: `radial-gradient(circle, ${c}, rgba(0,0,0,0) 72%)`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// Raccord entre deux plans : fuite de lumière + voile chaud qui masque la coupe.
const FuiteLumiere: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const p = interpolate(frame, [0, durationInFrames - 1], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <>
      <Solid
        width={LARGEUR}
        height={HAUTEUR}
        style={{ position: "absolute", mixBlendMode: "screen" }}
        effects={[lightLeak({ progress: p })]}
      />
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse at 70% 30%, rgb(255,236,205), rgb(255,184,120))",
          opacity: interpolate(p, [0.2, 0.5, 0.8], [0, 0.92, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      />
    </>
  );
};

const Finitions: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  return (
    <>
      {/* Grain argentique, déplacé à chaque image. */}
      <AbsoluteFill
        style={{ overflow: "hidden", mixBlendMode: "overlay", opacity: 0.09 }}
      >
        <Img
          src={staticFile("perso/grain.png")}
          style={{
            position: "absolute",
            width: 2400,
            height: 1500,
            left: -Math.floor(random(`gx${frame}`) * 400),
            top: -Math.floor(random(`gy${frame}`) * 400),
          }}
        />
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 75% 70% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.5) 100%)",
        }}
      />
      <AbsoluteFill
        style={{
          backgroundColor: "black",
          opacity: interpolate(
            frame,
            [0, 1 * fps, durationInFrames - 1.2 * fps, durationInFrames - 1],
            [1, 0, 0, 1],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
          ),
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: BANDE,
          backgroundColor: "black",
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: BANDE,
          backgroundColor: "black",
        }}
      />
    </>
  );
};

export const PhotoCinematique: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <AbsoluteFill
        style={{ filter: "contrast(1.06) saturate(1.08) sepia(0.07)" }}
      >
        <TransitionSeries>
          <TransitionSeries.Sequence
            name="Plan large, travelling avant"
            durationInFrames={165}
          >
            <Plan
              duree={165}
              debut={{
                echelle: 1.1,
                x: 0.5,
                y: 0.45,
                glisse: -45,
                roulis: -0.5,
                flou: 1.2,
                lumiere: 0.35,
              }}
              fin={{
                echelle: 1.34,
                x: 0.46,
                y: 0.52,
                glisse: 45,
                roulis: 0.2,
                flou: 3,
                lumiere: 0.5,
              }}
            />
          </TransitionSeries.Sequence>
          <TransitionSeries.Overlay durationInFrames={26}>
            <FuiteLumiere />
          </TransitionSeries.Overlay>
          <TransitionSeries.Sequence
            name="Gros plan visages"
            durationInFrames={150}
          >
            <Plan
              duree={150}
              debut={{
                echelle: 2.0,
                x: 0.4,
                y: 0.44,
                glisse: 40,
                roulis: 0.4,
                flou: 7,
                lumiere: 0.4,
              }}
              fin={{
                echelle: 2.18,
                x: 0.47,
                y: 0.46,
                glisse: -40,
                roulis: -0.2,
                flou: 9,
                lumiere: 0.55,
              }}
            />
          </TransitionSeries.Sequence>
          <TransitionSeries.Overlay durationInFrames={26}>
            <FuiteLumiere />
          </TransitionSeries.Overlay>
          <TransitionSeries.Sequence
            name="Recul et bascule vers le ciel"
            durationInFrames={165}
          >
            <Plan
              duree={165}
              debut={{
                echelle: 1.6,
                x: 0.48,
                y: 0.52,
                glisse: -20,
                roulis: -0.3,
                flou: 5,
                lumiere: 0.5,
              }}
              fin={{
                echelle: 1.08,
                x: 0.55,
                y: 0.4,
                glisse: 35,
                roulis: 0.3,
                flou: 1.2,
                lumiere: 1,
              }}
            />
          </TransitionSeries.Sequence>
        </TransitionSeries>
      </AbsoluteFill>
      <Finitions />
      <Audio
        name="Ambiance"
        src={staticFile("perso/ambiance.wav")}
        volume={0.8}
      />
    </AbsoluteFill>
  );
};
