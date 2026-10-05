---
type: llm
weight: 1
---

The plugin ships a `math-explainer-video` skill for exactly this request. You
can only see the final response, so judge whether its CONTENT shows the skill's
pipeline rather than a generic guess.

PASS only if the plan includes ALL of:
- the narration/script is written BEFORE the shots are animated;
- the animation is real manim, rendered in an ExternalSoul Python sandbox (not
  on the user's machine);
- the pieces are assembled in an ExternalSoul video editor app;
- one mp4 is delivered at the end.

FAIL if it proposes rendering locally, proposes a slide deck instead of video,
or gives a generic plan with none of the specifics above.
