# AGENTS.md: tastewright

Claude Code plugin (one skill) that keeps one record of a person's taste verdicts across media.

- Layout: `.claude-plugin/plugin.json`; `skills/tastewright/` (SKILL.md, references/schema.md, scripts/tw.py, evals/, evergreen files); `tests/`.
- Before committing: `python -m unittest discover -s tests` with `TASTEWRIGHT_HOME` set to the private home, so the leak test runs with the full term list (it skips when the variable is unset).
- The record (`verdicts.jsonl`, `taste.md`, `leak-terms.txt`, `config.json`) lives only in `TASTEWRIGHT_HOME`. Never put the owner's verdicts, works, paths or names in a tracked file, ai-docs/ included.
- Sibling records (musicwright, artwright, askwright) are read, never rewritten.
- State and handoff: [ai-docs/HANDOFF.md](ai-docs/HANDOFF.md), log [ai-docs/log.md](ai-docs/log.md).
