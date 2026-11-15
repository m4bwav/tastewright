---
name: tastewright
description: "One record of the user's taste verdicts across media (film, art, music, sfx, voice, pixel art, sites): add a verdict in their own words, import answered askwright picks, read what artwright and musicwright already hold, and answer 'what do I like' across media. tw.py add, import, show, where. Use on 'pull my askwright picks into my taste record', 'remember I hated the lens-talking in take 3', 'what do I like across art, music and film', 'give the film plugin my taste'. Not for one music take (musicwright-curate), ranking images (artwright-judge), making a decision page (askwright) or site fonts (sitewright-direction)."
---

# Tastewright

A verdict is the user's own call on a piece of work: a keep, reject, maybe or pick, with the date, the work and their words. This skill keeps those calls in one record so every media plugin can read them.

## Step 0

1. `TW` below means `python "<this folder>/scripts/tw.py"` (Python 3.9+, stdlib, prints JSON).
2. Run `TW where`. The record lives in `TASTEWRIGHT_HOME` (default `~/.tastewright`), never in a project or repository. Read `taste.md` there if it exists: the owner's distilled taste, each line citing a record row.

## Rules

1. **Write only to the home.** `TW add` or `TW import`; never a notes file in the project, the film folder or this repository.
2. **Store their words verbatim.** `--words` is exactly what they said or typed, or empty. Never paraphrase, never add a reason they did not give, never infer a verdict from silence or from a pick they did not make.
3. **Siblings are read-only.** `TW show --siblings` reads musicwright `verdicts.jsonl` and artwright `calibration/labels.jsonl` from their homes (`MUSICWRIGHT_HOME`, `ARTWRIGHT_HOME`, or `config.json` in the home); a new music or art verdict goes to that plugin's own curate skill.

## Commands

- `TW add --medium film --work "<work>" --item "<take>" --verdict reject --words "<verbatim>"` (`--over`, `--file`, `--source`, `--date`, `--weak`).
- `TW import <ask-set-dir>... --medium film [--work W] [--dry-run]`: answered choice questions with media only; skipped and process questions left out; worktree copies deduped; a pick made after the guess was shown is marked `weak`.
- `TW show [--medium M] [--work W] [--siblings]`: rows plus counts per medium and verdict. Cite the `source` of each line you quote.

Row format: [references/schema.md](references/schema.md). Distilling a profile: write `taste.md` in the home by hand when two or more rows agree, each line citing its rows.

## Maintenance

Evergreen unit: [evergreen.json](evergreen.json), [RESEARCH.md](RESEARCH.md), [LEARNINGS.md](LEARNINGS.md), [CHANGELOG.md](CHANGELOG.md), [TESTS.md](TESTS.md). Refresh with evergreen-refresh when due; record lessons with evergreen-learn (owner-specific ones go to the home, not here).
