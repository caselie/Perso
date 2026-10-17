import { Audio } from "@remotion/media";
import { staticFile, Track, useVideoConfig } from "remotion";
import { BorneReelle } from "./BorneReelle";
import { Accroche, Atouts, Bust, Fin, Impact, Victoire } from "./Scenes";
import { couleurs } from "./theme";

const centre = {
  backgroundColor: couleurs.fond,
  justifyContent: "center",
  alignItems: "center",
  flexDirection: "column",
} as const;

// Vidéo verticale (Reels / TikTok / Shorts) de présentation de la borne.
export const PresentationBorne = () => {
  const { fps } = useVideoConfig();

  return (
    <>
      <Track name="Scènes">
        <Accroche name="Accroche" durationInFrames={2.5 * fps} style={centre} />
        <BorneReelle
          name="Vraie borne"
          from={2.5 * fps}
          durationInFrames={5 * fps}
          style={centre}
        />
        <Impact
          name="Triple 20"
          from={7.5 * fps}
          durationInFrames={4 * fps}
          style={centre}
        />
        <Bust
          name="Bust"
          from={11.5 * fps}
          durationInFrames={3.5 * fps}
          style={centre}
        />
        <Victoire
          name="Sortie au double"
          from={15 * fps}
          durationInFrames={2.5 * fps}
          style={centre}
        />
        <Atouts
          name="Et aussi"
          from={17.5 * fps}
          durationInFrames={3.5 * fps}
          style={centre}
        />
        <Fin
          name="Fin"
          from={21 * fps}
          durationInFrames={3 * fps}
          style={centre}
        />
      </Track>
      <Audio name="Musique" src={staticFile("sfx/musique.wav")} volume={0.35} />
    </>
  );
};
