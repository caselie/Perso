import { Audio } from "@remotion/media";
import {
  Easing,
  Interactive,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Atout } from "./Atout";
import { Cible } from "./Cible";
import { couleurs, police, policeMono } from "./theme";

const borne = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const sortie = Easing.bezier(0.16, 1, 0.3, 1);

const titre: React.CSSProperties = {
  fontFamily: police,
  fontWeight: 900,
  color: couleurs.texte,
  textAlign: "center",
  letterSpacing: -2,
  lineHeight: 1.05,
};

// ─── 1. Accroche ───────────────────────────────────────────────────────────

const AccrocheInner = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <>
      <Interactive.Div
        name="Ton vieux PC portable"
        style={{
          ...titre,
          fontSize: 104,
          color: couleurs.texteDoux,
          opacity: interpolate(frame, [0, 0.4 * fps], [0, 1], {
            ...borne,
            easing: sortie,
          }),
          translate: `0px ${interpolate(frame, [0, 0.4 * fps], [60, 0], { ...borne, easing: sortie })}px`,
        }}
      >
        Ton vieux PC portable
      </Interactive.Div>
      <Interactive.Div
        name="devient une"
        style={{
          ...titre,
          fontSize: 104,
          marginTop: 24,
          opacity: interpolate(frame, [0.4 * fps, 0.8 * fps], [0, 1], {
            ...borne,
            easing: sortie,
          }),
          translate: `0px ${interpolate(frame, [0.4 * fps, 0.8 * fps], [60, 0], { ...borne, easing: sortie })}px`,
        }}
      >
        devient une
      </Interactive.Div>
      <Interactive.Div
        name="borne de fléchettes"
        style={{
          ...titre,
          fontSize: 150,
          marginTop: 24,
          color: couleurs.or,
          scale: interpolate(frame, [0.8 * fps, 1.4 * fps], [0, 1], {
            ...borne,
            easing: Easing.spring({ damping: 11 }),
            output: "perceptual-scale",
          }),
          rotate: `${interpolate(frame, [0.8 * fps, 1.4 * fps], [-8, -3], { ...borne, easing: sortie })}deg`,
        }}
      >
        borne de
        <br />
        fléchettes.
      </Interactive.Div>
      <Audio name="Whoosh" src={staticFile("sfx/whoosh.wav")} volume={0.5} />
      <Audio
        name="Fouet"
        src={staticFile("sfx/whip.wav")}
        from={0.8 * fps}
        volume={0.7}
      />
    </>
  );
};

export const Accroche = Interactive.create({
  Component: AccrocheInner,
  layout: "absolute-fill",
  schema: { ...Interactive.backgroundSchema },
});

// ─── 2. Une fléchette, un clic, le score suit ──────────────────────────────

const ImpactInner = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const impact = 1.2 * fps;

  return (
    <>
      <Interactive.Div
        name="Légende"
        style={{
          ...titre,
          position: "absolute",
          top: 170,
          width: "100%",
          fontSize: 76,
          opacity: interpolate(frame, [0, 0.4 * fps], [0, 1], borne),
        }}
      >
        Tu touches la zone.
        <br />
        <span style={{ color: couleurs.vertClair }}>La borne compte.</span>
      </Interactive.Div>
      <Cible
        name="Cible"
        surbrillance="T20"
        impact={impact}
        style={{
          width: 900,
          height: 900,
          scale: interpolate(frame, [0, 0.8 * fps], [0.3, 1], {
            ...borne,
            easing: Easing.spring({ damping: 14 }),
            output: "perceptual-scale",
          }),
          rotate: `${interpolate(frame, [0, 0.8 * fps], [-40, 0], { ...borne, easing: sortie })}deg`,
        }}
      />
      <Interactive.Div
        name="T20 · 60"
        style={{
          position: "absolute",
          top: 400,
          padding: "18px 40px",
          borderRadius: 999,
          backgroundColor: couleurs.or,
          color: couleurs.fond,
          fontFamily: police,
          fontSize: 64,
          fontWeight: 900,
          opacity: frame < impact ? 0 : 1,
          scale: interpolate(frame, [impact, impact + 0.4 * fps], [0.2, 1], {
            ...borne,
            easing: Easing.spring({ damping: 9 }),
            output: "perceptual-scale",
          }),
        }}
      >
        TRIPLE 20 · 60
      </Interactive.Div>
      <Interactive.Div
        name="Score"
        style={{
          position: "absolute",
          bottom: 190,
          display: "flex",
          alignItems: "baseline",
          gap: 36,
          fontFamily: police,
          color: couleurs.texte,
          opacity: interpolate(frame, [0.3 * fps, 0.7 * fps], [0, 1], borne),
        }}
      >
        <span
          style={{ fontSize: 56, fontWeight: 700, color: couleurs.texteDoux }}
        >
          Joueur 1
        </span>
        <span
          style={{
            fontSize: 200,
            fontWeight: 900,
            fontVariantNumeric: "tabular-nums",
          }}
        >
          {Math.round(
            interpolate(
              frame,
              [impact + 0.3 * fps, impact + 1.1 * fps],
              [501, 441],
              {
                ...borne,
                easing: Easing.bezier(0.33, 1, 0.68, 1),
              },
            ),
          )}
        </span>
      </Interactive.Div>
      <Audio
        name="Vol"
        src={staticFile("sfx/whoosh.wav")}
        from={impact - 0.4 * fps}
        volume={0.6}
      />
      <Audio name="Impact" src={staticFile("sfx/impact.wav")} from={impact} />
      <Audio
        name="Pastille"
        src={staticFile("sfx/switch.wav")}
        from={impact + 2}
        volume={0.5}
      />
    </>
  );
};

export const Impact = Interactive.create({
  Component: ImpactInner,
  layout: "absolute-fill",
  schema: { ...Interactive.backgroundSchema },
});

// ─── 3. Le bust ────────────────────────────────────────────────────────────

const BustInner = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const premiere = 0.6 * fps;
  const bust = 1.5 * fps;
  const secousse =
    frame < bust
      ? 0
      : Math.sin((frame - bust) * 2.2) *
        interpolate(frame, [bust, bust + 0.7 * fps], [40, 0], borne);

  return (
    <>
      <Interactive.Div
        name="Flash rouge"
        style={{
          position: "absolute",
          inset: 0,
          backgroundColor: couleurs.rouge,
          opacity: interpolate(
            frame,
            [bust, bust + 0.15 * fps, bust + 0.8 * fps],
            [0, 0.45, 0],
            borne,
          ),
        }}
      />
      <Interactive.Div
        name="Reste 32"
        style={{
          ...titre,
          position: "absolute",
          top: 230,
          width: "100%",
          fontSize: 72,
          color: couleurs.texteDoux,
          opacity: interpolate(frame, [0, 0.3 * fps], [0, 1], borne),
        }}
      >
        Il reste 32.
        <br />
        Tu forces sur le 20…
      </Interactive.Div>
      <Interactive.Div
        name="Score restant"
        style={{
          fontFamily: police,
          fontWeight: 900,
          fontSize: 380,
          fontVariantNumeric: "tabular-nums",
          color:
            frame >= bust && frame < bust + 0.9 * fps
              ? "#ff7b72"
              : couleurs.texte,
          translate: `${secousse}px 0px`,
        }}
      >
        {frame < premiere
          ? 32
          : frame < bust
            ? Math.round(
                interpolate(
                  frame,
                  [premiere, premiere + 0.4 * fps],
                  [32, 12],
                  borne,
                ),
              )
            : frame < bust + 0.9 * fps
              ? -8
              : 32}
      </Interactive.Div>
      <Interactive.Div
        name="Fléchettes jouées"
        style={{
          display: "flex",
          gap: 24,
          marginTop: 10,
          fontFamily: policeMono,
          fontSize: 52,
          fontWeight: 700,
          color: couleurs.texte,
        }}
      >
        <span style={{ opacity: frame < premiere ? 0.2 : 1 }}>S20</span>
        <span style={{ opacity: frame < bust ? 0.2 : 1 }}>S20</span>
        <span style={{ opacity: 0.2 }}>—</span>
      </Interactive.Div>
      <Interactive.Div
        name="BUST"
        style={{
          ...titre,
          position: "absolute",
          top: 1290,
          fontSize: 230,
          color: couleurs.rouge,
          textShadow: `0 0 60px ${couleurs.rouge}`,
          opacity: frame < bust ? 0 : 1,
          scale: interpolate(frame, [bust, bust + 0.35 * fps], [3, 1], {
            ...borne,
            easing: Easing.bezier(0.5, 0, 0.75, 0),
            output: "perceptual-scale",
          }),
          rotate: "-8deg",
        }}
      >
        BUST !
      </Interactive.Div>
      <Interactive.Div
        name="Explication"
        style={{
          ...titre,
          position: "absolute",
          bottom: 260,
          width: "100%",
          fontSize: 52,
          fontWeight: 700,
          color: couleurs.texteDoux,
          opacity: interpolate(
            frame,
            [bust + 0.9 * fps, bust + 1.2 * fps],
            [0, 1],
            borne,
          ),
        }}
      >
        La borne remet le score à 32.
        <br />
        Et passe la main.
      </Interactive.Div>
      <Audio
        name="Premier S20"
        src={staticFile("sfx/impact.wav")}
        from={premiere}
        volume={0.8}
      />
      <Audio
        name="Second S20"
        src={staticFile("sfx/impact.wav")}
        from={bust}
        volume={0.8}
      />
      <Audio
        name="Buzzer"
        src={staticFile("sfx/buzzer.wav")}
        from={bust + 2}
        volume={0.6}
      />
    </>
  );
};

export const Bust = Interactive.create({
  Component: BustInner,
  layout: "absolute-fill",
  schema: { ...Interactive.backgroundSchema },
});

// ─── 4. La sortie au double ────────────────────────────────────────────────

const VictoireInner = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const impact = 1 * fps;

  return (
    <>
      <Interactive.Div
        name="Sortie suggérée"
        style={{
          position: "absolute",
          top: 190,
          display: "flex",
          alignItems: "center",
          gap: 24,
          padding: "22px 44px",
          borderRadius: 24,
          border: `3px solid ${couleurs.or}`,
          fontFamily: police,
          fontSize: 58,
          fontWeight: 700,
          color: couleurs.texte,
          opacity: interpolate(frame, [0, 0.3 * fps], [0, 1], borne),
          translate: `0px ${interpolate(frame, [0, 0.3 * fps], [-40, 0], { ...borne, easing: sortie })}px`,
        }}
      >
        Sortie suggérée
        <span style={{ fontFamily: policeMono, color: couleurs.or }}>D16</span>
      </Interactive.Div>
      <Cible
        name="Cible D16"
        surbrillance="D16"
        impact={impact}
        style={{
          width: 820,
          height: 820,
          opacity: interpolate(
            frame,
            [impact + 0.2 * fps, impact + 0.5 * fps],
            [1, 0.35],
            borne,
          ),
        }}
      />
      <Interactive.Div
        name="Halo vert"
        style={{
          position: "absolute",
          width: 700,
          height: 700,
          borderRadius: 999,
          border: `16px solid ${couleurs.vertClair}`,
          opacity: interpolate(
            frame,
            [impact + 0.2 * fps, impact + 1 * fps],
            [1, 0],
            borne,
          ),
          scale: interpolate(
            frame,
            [impact + 0.2 * fps, impact + 1 * fps],
            [0.2, 2.2],
            borne,
          ),
        }}
      />
      <Interactive.Div
        name="GAGNÉ"
        style={{
          ...titre,
          position: "absolute",
          fontSize: 210,
          color: couleurs.vertClair,
          textShadow: `0 0 70px ${couleurs.vert}`,
          opacity: frame < impact + 0.2 * fps ? 0 : 1,
          scale: interpolate(
            frame,
            [impact + 0.2 * fps, impact + 0.7 * fps],
            [0, 1],
            {
              ...borne,
              easing: Easing.spring({ damping: 8 }),
              output: "perceptual-scale",
            },
          ),
        }}
      >
        GAGNÉ !
      </Interactive.Div>
      <Audio
        name="Impact D16"
        src={staticFile("sfx/impact.wav")}
        from={impact}
      />
      <Audio
        name="Jingle"
        src={staticFile("sfx/victoire.wav")}
        from={impact + 0.2 * fps}
        volume={0.7}
      />
    </>
  );
};

export const Victoire = Interactive.create({
  Component: VictoireInner,
  layout: "absolute-fill",
  schema: { ...Interactive.backgroundSchema },
});

// ─── 5. Le reste ───────────────────────────────────────────────────────────

const apparition = (frame: number, debut: number, fps: number) => ({
  opacity: interpolate(frame, [debut, debut + 0.35 * fps], [0, 1], borne),
  translate: `${interpolate(frame, [debut, debut + 0.35 * fps], [-140, 0], { ...borne, easing: sortie })}px 0px`,
});

const AtoutsInner = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <>
      <Interactive.Div
        name="Et aussi"
        style={{
          ...titre,
          fontSize: 110,
          marginBottom: 60,
          opacity: interpolate(frame, [0, 0.3 * fps], [0, 1], borne),
        }}
      >
        Et aussi
      </Interactive.Div>
      <Atout
        name="Jeux"
        accent={couleurs.or}
        style={{ ...apparition(frame, 0.3 * fps, fps), marginBottom: 32 }}
      >
        501, Cricket, Killer, Shanghai, Around the Clock
      </Atout>
      <Atout
        name="Cible"
        accent={couleurs.rouge}
        style={{ ...apparition(frame, 0.6 * fps, fps), marginBottom: 32 }}
      >
        N'importe quelle cible, pointes acier comprises
      </Atout>
      <Atout
        name="Télécommande"
        accent={couleurs.vertClair}
        style={{ ...apparition(frame, 0.9 * fps, fps), marginBottom: 32 }}
      >
        Ton téléphone sert de télécommande
      </Atout>
      <Atout
        name="Stats"
        accent="#58a6ff"
        style={apparition(frame, 1.2 * fps, fps)}
      >
        Stats, 180, et reprise après une coupure
      </Atout>
      <Audio
        name="Jeux"
        src={staticFile("sfx/switch.wav")}
        from={0.3 * fps}
        volume={0.4}
      />
      <Audio
        name="Cible"
        src={staticFile("sfx/switch.wav")}
        from={0.6 * fps}
        volume={0.4}
      />
      <Audio
        name="Télécommande"
        src={staticFile("sfx/switch.wav")}
        from={0.9 * fps}
        volume={0.4}
      />
      <Audio
        name="Stats"
        src={staticFile("sfx/switch.wav")}
        from={1.2 * fps}
        volume={0.4}
      />
    </>
  );
};

export const Atouts = Interactive.create({
  Component: AtoutsInner,
  layout: "absolute-fill",
  schema: { ...Interactive.backgroundSchema },
});

// ─── 6. Fin ────────────────────────────────────────────────────────────────

const COMMANDE = "./scripts/run.sh";

const FinInner = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const tapes = Math.floor(
    interpolate(frame, [0.2 * fps, 1 * fps], [0, COMMANDE.length], borne),
  );

  return (
    <>
      <Interactive.Div
        name="Terminal"
        style={{
          width: 920,
          padding: "48px 52px",
          borderRadius: 28,
          backgroundColor: "#010409",
          border: `2px solid ${couleurs.bord}`,
          fontFamily: policeMono,
          fontSize: 60,
          fontWeight: 700,
          color: couleurs.texte,
          opacity: interpolate(frame, [0, 0.2 * fps], [0, 1], borne),
        }}
      >
        <span style={{ color: couleurs.vertClair }}>$ </span>
        {COMMANDE.slice(0, tapes)}
        <span
          style={{
            opacity: Math.floor(frame / (0.25 * fps)) % 2 === 0 ? 1 : 0,
          }}
        >
          ▌
        </span>
      </Interactive.Div>
      <Interactive.Div
        name="Slogan"
        style={{
          ...titre,
          fontSize: 112,
          marginTop: 110,
          opacity: interpolate(frame, [1.2 * fps, 1.6 * fps], [0, 1], borne),
          translate: `0px ${interpolate(frame, [1.2 * fps, 1.6 * fps], [50, 0], { ...borne, easing: sortie })}px`,
        }}
      >
        Ton portable.
        <br />
        Ta cible.
        <br />
        <span style={{ color: couleurs.or }}>Ta borne.</span>
      </Interactive.Div>
      <Interactive.Div
        name="Mentions"
        style={{
          ...titre,
          fontSize: 46,
          fontWeight: 500,
          marginTop: 80,
          color: couleurs.texteDoux,
          opacity: interpolate(frame, [1.8 * fps, 2.2 * fps], [0, 1], borne),
        }}
      >
        Open source · Flask + SQLite · zéro abonnement
      </Interactive.Div>
      {COMMANDE.split("").map((_, k) => (
        <Audio
          key={k}
          name="Frappe"
          src={staticFile("sfx/touche.wav")}
          from={Math.round(0.2 * fps + (k * 0.8 * fps) / COMMANDE.length)}
          volume={0.5}
        />
      ))}
      <Audio
        name="Slogan"
        src={staticFile("sfx/whoosh.wav")}
        from={1.2 * fps}
        volume={0.5}
      />
    </>
  );
};

export const Fin = Interactive.create({
  Component: FinInner,
  layout: "absolute-fill",
  schema: { ...Interactive.backgroundSchema },
});
