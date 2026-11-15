# Tests: tastewright

- Unit and leak: `TASTEWRIGHT_HOME=<private home> python -m unittest discover -s tests` from the repo root. The leak test skips with a warning when the variable is unset.
- Evals: [evals/evals.json](evals/evals.json) (4 triggers, 5 decoys, 3 action cases). Baseline run 2026-11-15: 1 pass, 2 fail (A1 location; A2 location and paraphrase). With-skill run: not yet (step F).
