# Learnings: tastewright

General lessons only. Lessons about one owner's taste live in the private home (`TASTEWRIGHT_HOME/taste.md`), never here.

- L-001 `record-outside-repo` (2026-11-15): with no known home, a bare model writes taste notes into the working folder or the film repository. The record needs a fixed home outside any repository. Source: baseline evals A1, A2 (plugin-backlog learning-gap/tastewright-evals.md).
- L-002 `words-verbatim` (2026-11-15): a bare model paraphrases a spoken verdict ("Characters talk to the camera again" for "they're talking to the camera again"). Store the words exactly. Source: baseline eval A2.
- L-003 `bare-model-hygiene-ok` (2026-11-15): a bare model already dedupes worktree copies, skips unanswered and process questions, flags a pick made after the guess was shown and keeps a bare pick bare; tw.py does it only to save tokens over many sets. Source: baseline eval A1.
- L-004 `siblings-own-their-medium` (2026-11-15): music and art verdicts already have structured homes (musicwright verdicts.jsonl, artwright labels.jsonl); read them, never copy or rewrite. Film, sfx and voice had none. Source: harvest, section 1.
- L-005 `process-vs-taste` (2026-11-15): about 41 of 140 answered askwright sets were process or plugin decisions, not taste. A question with no media is treated as process. Source: harvest, section 3.
- L-006 `close-pairs-have-a-pick` (2026-11-15): when an automatic judge ties two close takes, the person often still has a clear pick; show them. Source: artwright taste record (calibration picks).
- L-007 `simple-questions` (2026-11-15): verdicts come in best from many simple questions with side-by-sides and a guess. Source: review-method preference in the harvest.
