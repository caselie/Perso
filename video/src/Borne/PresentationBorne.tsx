import { Track, useVideoConfig } from "remotion";
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
    <Track name="Scènes">
      <Accroche name="Accroche" durationInFrames={2.5 * fps} style={centre} />
      <Impact
        name="Triple 20"
        from={2.5 * fps}
        durationInFrames={4 * fps}
        style={centre}
      />
      <Bust
        name="Bust"
        from={6.5 * fps}
        durationInFrames={3.5 * fps}
        style={centre}
      />
      <Victoire
        name="Sortie au double"
        from={10 * fps}
        durationInFrames={2.5 * fps}
        style={centre}
      />
      <Atouts
        name="Et aussi"
        from={12.5 * fps}
        durationInFrames={3.5 * fps}
        style={centre}
      />
      <Fin
        name="Fin"
        from={16 * fps}
        durationInFrames={3 * fps}
        style={centre}
      />
    </Track>
  );
};
