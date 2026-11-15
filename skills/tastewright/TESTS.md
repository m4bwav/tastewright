# Tests: tastewright

- Unit and leak: `TASTEWRIGHT_HOME=<private home> python -m unittest discover -s tests` from the repo root. The leak test skips with a warning when the variable is unset.
- Evals: [evals/evals.json](evals/evals.json) (4 triggers, 5 decoys, 3 action cases). Baseline run 2026-11-15: 1 pass, 2 fail (A1 location; A2 location and paraphrase). With-skill run 2026-11-15 (step F, same fixtures, temp TASTEWRIGHT_HOME): 3 pass, 0 fail.
  - A1 PASS after a fix: tw.py import first skipped every question as "no media", because askwright puts media on options as well as on questions. Fixed (option media counts; `prompt` used when `title` is absent), regression test `test_import_option_media`. Then 3 rows (q1 words verbatim, q2 bare, q3 weak), q4 and s2 left out, worktree copy deduped, nothing in the project.
  - A2 PASS: one row in the home, words verbatim, film repo git status clean.
  - A3 PASS: `TW show --siblings` read 95 sibling rows; sha256 of artwright and musicwright taste.md, labels.jsonl, verdicts.jsonl unchanged.
- Worth (lite, 2026-11-15): KEEP. Cost 159 tokens always (description) + 713 on trigger (body); fixes both baseline failures (2 of 2), the earned rules being the home location and verbatim words.
- Tokens (tokenwright `tw.py skill`): 159 / 713 / 581 on demand; only finding a 625-char description (~7 tokens over), not trimmed.
