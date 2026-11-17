import React from "react";
import { Composition, Series } from "remotion";
import { SixResults } from "./scenes/SixResults";
import { AppScene, LimitsScene, ResultsScene, WhyScene, ClosingScene } from "./scenes/part3";
import { BertScene, ExperimentsScene, GruScene, LstmScene } from "./scenes/part2";
import { DataScene, IdeaScene, SplitScene, StoryScene, TitleScene } from "./scenes/part1";

// Scene lengths in frames at 30 fps. Total 8400 frames = 4:40.
export const SCENES: { id: string; frames: number; C: React.FC }[] = [
  { id: "title", frames: 240, C: TitleScene },
  { id: "story", frames: 660, C: StoryScene },
  { id: "idea", frames: 540, C: IdeaScene },
  { id: "data", frames: 660, C: DataScene },
  { id: "split", frames: 480, C: SplitScene },
  { id: "gru", frames: 600, C: GruScene },
  { id: "lstm", frames: 600, C: LstmScene },
  { id: "bert", frames: 600, C: BertScene },
  { id: "experiments", frames: 900, C: ExperimentsScene },
  { id: "results", frames: 900, C: ResultsScene },
  { id: "why", frames: 900, C: WhyScene },
  { id: "limits", frames: 660, C: LimitsScene },
  { id: "app", frames: 420, C: AppScene },
  { id: "closing", frames: 240, C: ClosingScene },
];
const TOTAL = SCENES.reduce((a, s) => a + s.frames, 0);

const Full: React.FC = () => (
  <Series>
    {SCENES.map(({ id, frames, C }) => (
      <Series.Sequence key={id} durationInFrames={frames}><C /></Series.Sequence>
    ))}
  </Series>
);

export const Root: React.FC = () => (
  <>
    <Composition id="FullStory" component={Full} durationInFrames={TOTAL} fps={30} width={1920} height={1080} />
    {SCENES.map(({ id, frames, C }) => (
      <Composition key={id} id={"S-" + id} component={C} durationInFrames={frames} fps={30} width={1920} height={1080} />
    ))}
    <Composition id="SixResults" component={SixResults} durationInFrames={300} fps={30} width={1920} height={1080} />
  </>
);
