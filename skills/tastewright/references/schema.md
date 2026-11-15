# Verdict row (shared convention)

One JSON object per line in `<HOME>/verdicts.jsonl`; the latest row for an item wins. Widened from musicwright's verdict row so every media plugin can write the same shape.

| Field | Required | Meaning |
|---|---|---|
| `type` | yes | always `"verdict"` |
| `date` | yes | ISO date of the call (askwright: the answer's `updated`) |
| `medium` | yes | film, art, music, sfx, voice, pixel, site |
| `work` | yes | the film, game, track or project |
| `item` | yes | take, shot, image or question |
| `verdict` | yes | `keep`, `reject`, `maybe` or `pick` |
| `words` | yes | the person's words verbatim, or `""`; never paraphrased |
| `by` | yes | who made the call (from `config.json` `by`, default `owner`) |
| `source` | yes | where the call was made: an `answers.json` path, `said`, a file |
| `over` | no | the options passed over, for a pick |
| `choice` | no | the chosen option's label (askwright imports) |
| `file` | no | the media file judged |
| `weak` | no | `true` when the guess was shown before the pick |
| `key` | yes | dedupe hash, written by tw.py |

Rules: nothing inferred from silence; a bare pick stays bare; records never go in a repository.

Sibling records read as-is (never rewritten): musicwright `verdicts.jsonl` (`take`, `note`, `verdict`), artwright `calibration/labels.jsonl` (`pick`, `note`, `at`, `by: human`). askwright sets: `questions.json` (`questions[].options[]`, `media`) and `answers.json` (`answers.<id>.choice, note, state, updated, guess_revealed_before_pick`).
