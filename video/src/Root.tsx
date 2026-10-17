import { Composition, Folder } from "remotion";
import { HelloWorld } from "./HelloWorld";
import { Logo } from "./HelloWorld/Logo";
import { Title } from "./HelloWorld/Title";
import { Atout } from "./Borne/Atout";
import { Cible } from "./Borne/Cible";
import { PresentationBorne } from "./Borne/PresentationBorne";
import { Accroche, Atouts, Bust, Fin, Impact, Victoire } from "./Borne/Scenes";
import { couleurs } from "./Borne/theme";

const vertical = { fps: 30, width: 1080, height: 1920 } as const;
const centre = {
  backgroundColor: couleurs.fond,
  justifyContent: "center",
  alignItems: "center",
  flexDirection: "column",
} as const;

// Each <Composition> is an entry in the sidebar!

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="PresentationBorne"
        component={PresentationBorne}
        durationInFrames={570}
        {...vertical}
      />
      <Folder name="Borne-scenes">
        <Composition
          id="Accroche"
          component={Accroche}
          durationInFrames={75}
          {...vertical}
          defaultProps={{ style: centre }}
        />
        <Composition
          id="Impact"
          component={Impact}
          durationInFrames={120}
          {...vertical}
          defaultProps={{ style: centre }}
        />
        <Composition
          id="Bust"
          component={Bust}
          durationInFrames={105}
          {...vertical}
          defaultProps={{ style: centre }}
        />
        <Composition
          id="Victoire"
          component={Victoire}
          durationInFrames={75}
          {...vertical}
          defaultProps={{ style: centre }}
        />
        <Composition
          id="Atouts"
          component={Atouts}
          durationInFrames={105}
          {...vertical}
          defaultProps={{ style: centre }}
        />
        <Composition
          id="Fin"
          component={Fin}
          durationInFrames={90}
          {...vertical}
          defaultProps={{ style: centre }}
        />
      </Folder>
      <Folder name="Borne-elements">
        <Composition
          id="Cible"
          component={Cible}
          durationInFrames={90}
          fps={30}
          width={1080}
          height={1080}
          defaultProps={{
            surbrillance: "T20",
            impact: 30,
            style: { width: 1000, height: 1000 },
          }}
        />
        <Composition
          id="Atout"
          component={Atout}
          durationInFrames={60}
          fps={30}
          width={1080}
          height={400}
          defaultProps={{
            children: "Ton téléphone sert de télécommande",
            accent: couleurs.vertClair,
          }}
        />
      </Folder>
      <Folder name="Elements">
        <Composition
          id="Logo"
          component={Logo}
          durationInFrames={150}
          fps={30}
          width={1920}
          height={1080}
          defaultProps={{
            logoColor1: "#91EAE4",
            logoColor2: "#86A8E7",
          }}
        />
        <Composition
          id="Title"
          component={Title}
          durationInFrames={115}
          fps={30}
          width={1920}
          height={1080}
          defaultProps={{
            titleText: "Welcome to Remotion",
            titleColor: "#000000",
          }}
        />
      </Folder>
      <Composition
        // You can take the "id" to render a video:
        // bunx remotion render HelloWorld
        id="HelloWorld"
        component={HelloWorld}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        // You can override these props for each render:
        // https://www.remotion.dev/docs/parametrized-rendering
        defaultProps={{
          titleText: "Welcome to Remotion",
          titleColor: "#000000",
        }}
      />
    </>
  );
};
