import { Audio } from "@remotion/media";
import {
  Easing,
  Img,
  Interactive,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { couleurs, police } from "./theme";

// Captures de la vraie borne (Playwright, 1280×800) pendant un 180 de Léa :
// chaque appui sur l'écran fait passer à la capture suivante.
const LARGEUR_CAPTURE = 1280;
const ECRAN = 880;
const ECHELLE = ECRAN / LARGEUR_CAPTURE;
const TRIPLE = { x: 1124, y: 140 };
const VINGT = { x: 613, y: 656 };

const APPUIS = [
  { image: 18, ...TRIPLE },
  { image: 30, ...VINGT },
  { image: 42, ...TRIPLE },
  { image: 54, ...VINGT },
  { image: 66, ...TRIPLE },
  { image: 78, ...VINGT },
];
const FIN_DE_VOLEE = 93;

const Appui: React.FC<{
  readonly debut: number;
  readonly x: number;
  readonly y: number;
}> = ({ debut, x, y }) => {
  const frame = useCurrentFrame();
  if (frame < debut || frame > debut + 14) {
    return null;
  }
  return (
    <div
      style={{
        position: "absolute",
        left: x * ECHELLE - 40,
        top: y * ECHELLE - 40,
        width: 80,
        height: 80,
        borderRadius: 40,
        border: `5px solid ${couleurs.texte}`,
        backgroundColor: "rgba(230, 237, 243, 0.25)",
        opacity: interpolate(frame, [debut, debut + 14], [1, 0], {
          extrapolateRight: "clamp",
        }),
        scale: interpolate(frame, [debut, debut + 14], [0.4, 1.4], {
          extrapolateRight: "clamp",
          easing: Easing.out(Easing.quad),
        }),
      }}
    />
  );
};

const BorneReelleInner = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const captureActive =
    frame >= FIN_DE_VOLEE
      ? 7
      : APPUIS.filter((a) => frame >= a.image + 3).length;
  const secousse =
    frame < FIN_DE_VOLEE
      ? 0
      : Math.sin((frame - FIN_DE_VOLEE) * 2.5) *
        interpolate(frame, [FIN_DE_VOLEE, FIN_DE_VOLEE + 0.6 * fps], [22, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

  return (
    <>
      <Interactive.Div
        name="Légende"
        style={{
          position: "absolute",
          top: 210,
          width: "100%",
          textAlign: "center",
          fontFamily: police,
          fontWeight: 900,
          fontSize: 80,
          lineHeight: 1.05,
          letterSpacing: -2,
          color: couleurs.texte,
          opacity: interpolate(frame, [0, 0.3 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Pas une maquette.
        <br />
        <span style={{ color: couleurs.vertClair }}>La vraie borne.</span>
      </Interactive.Div>
      <Interactive.Div
        name="Portable"
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          translate: `${secousse}px 0px`,
          scale: interpolate(frame, [0, 0.6 * fps, 5 * fps], [0.85, 1, 1.05], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
        }}
      >
        <div
          style={{
            position: "relative",
            width: ECRAN,
            height: ECRAN * (800 / 1280),
            border: "22px solid #2b3036",
            borderBottomWidth: 34,
            borderRadius: 26,
            boxSizing: "content-box",
            overflow: "hidden",
            backgroundColor: couleurs.fond,
            boxShadow: `0 40px 120px rgba(0,0,0,0.6), 0 0 0 2px ${couleurs.bord}`,
          }}
        >
          {[0, 1, 2, 3, 4, 5, 6, 7].map((n) => (
            <Img
              key={n}
              src={staticFile(`borne/e${n}.png`)}
              style={{
                position: "absolute",
                inset: 0,
                width: "100%",
                height: "100%",
                opacity: n === captureActive ? 1 : 0,
              }}
            />
          ))}
          {APPUIS.map((a) => (
            <Appui key={a.image} debut={a.image} x={a.x} y={a.y} />
          ))}
        </div>
        <div
          style={{
            width: ECRAN + 100,
            height: 30,
            borderRadius: "0 0 30px 30px",
            background: "linear-gradient(#3a4048, #1f2328)",
          }}
        />
      </Interactive.Div>
      <Interactive.Div
        name="180"
        style={{
          position: "absolute",
          bottom: 250,
          fontFamily: police,
          fontWeight: 900,
          fontSize: 260,
          letterSpacing: -6,
          color: couleurs.or,
          textShadow: `0 0 80px ${couleurs.or}`,
          opacity: frame < FIN_DE_VOLEE ? 0 : 1,
          rotate: "-6deg",
          scale: interpolate(
            frame,
            [FIN_DE_VOLEE, FIN_DE_VOLEE + 0.5 * fps],
            [0, 1],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.spring({ damping: 8 }),
              output: "perceptual-scale",
            },
          ),
        }}
      >
        180 !
      </Interactive.Div>
      <Audio
        name="Appui Triple"
        src={staticFile("sfx/mouse-click.wav")}
        from={APPUIS[0].image}
        volume={0.6}
      />
      <Audio
        name="Appui 20"
        src={staticFile("sfx/impact.wav")}
        from={APPUIS[1].image}
        volume={0.7}
      />
      <Audio
        name="Appui Triple"
        src={staticFile("sfx/mouse-click.wav")}
        from={APPUIS[2].image}
        volume={0.6}
      />
      <Audio
        name="Appui 20"
        src={staticFile("sfx/impact.wav")}
        from={APPUIS[3].image}
        volume={0.7}
      />
      <Audio
        name="Appui Triple"
        src={staticFile("sfx/mouse-click.wav")}
        from={APPUIS[4].image}
        volume={0.6}
      />
      <Audio
        name="Appui 20"
        src={staticFile("sfx/impact.wav")}
        from={APPUIS[5].image}
        volume={0.7}
      />
      <Audio
        name="Boom 180"
        src={staticFile("sfx/boom.wav")}
        from={FIN_DE_VOLEE}
      />
    </>
  );
};

export const BorneReelle = Interactive.create({
  Component: BorneReelleInner,
  layout: "absolute-fill",
  schema: { ...Interactive.backgroundSchema },
});
