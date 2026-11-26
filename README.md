# tastewright

![tastewright banner](.github/images/banner.jpg)

An agent plugin that keeps one record of your taste verdicts across media: films, images, music, sound effects, voices, pixel art and sites. Each verdict is your own call (keep, reject, maybe or pick) with the date, the work and your words exactly as you said them.

- `tw.py add` records a verdict you just gave.
- `tw.py import` pulls answered picks from askwright decision pages, skipping unanswered and process questions and duplicate copies.
- `tw.py show --siblings` reads what musicwright and artwright already record, without changing their files.

The record lives in `TASTEWRIGHT_HOME` (default `~/.tastewright`), outside any repository. Row format: [skills/tastewright/references/schema.md](skills/tastewright/references/schema.md).

## Install

```
claude plugin marketplace add m4bwav/tastewright
claude plugin install tastewright
```

## Tests

```
TASTEWRIGHT_HOME=~/.tastewright python -m unittest discover -s tests
```

MIT licence. Python 3.9+, standard library only.
