#!/usr/bin/env python3
"""tastewright: one record of a person's taste verdicts across media.

Commands (each prints JSON):
  where                      home, record file, sibling sources found
  add    --medium --work --item --verdict [--words] [--over] [--file] [--source] [--date] [--weak]
  import <ask-dir>... --medium M [--work W] [--dry-run]
  show   [--medium M] [--work W] [--siblings] [--limit N]

The record is <TASTEWRIGHT_HOME>/verdicts.jsonl (default ~/.tastewright). Sibling
records (musicwright, artwright) are read, never written. Stdlib only.
"""
import argparse
import datetime
import hashlib
import json
import os
import sys

VERDICTS = ("keep", "reject", "maybe", "pick")


def home():
    return os.path.expanduser(os.environ.get("TASTEWRIGHT_HOME") or "~/.tastewright")


def owner():
    p = os.path.join(home(), "config.json")
    if os.path.isfile(p):
        try:
            return load_json(p).get("by") or "owner"
        except ValueError:
            pass
    return "owner"


def record_path():
    return os.path.join(home(), "verdicts.jsonl")


def read_jsonl(path):
    rows = []
    if not os.path.isfile(path):
        return rows
    with open(path, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                try:
                    rows.append(json.loads(ln))
                except ValueError:
                    pass
    return rows


def append_rows(rows):
    os.makedirs(home(), exist_ok=True)
    with open(record_path(), "a", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def row_key(r):
    raw = "|".join(str(r.get(k, "")) for k in ("medium", "work", "item", "verdict", "over", "words", "date"))
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def make_row(medium, work, item, verdict, words="", over=None, file=None, source="", date=None, weak=False):
    if verdict not in VERDICTS:
        raise SystemExit("verdict must be one of " + ", ".join(VERDICTS))
    r = {"type": "verdict", "date": date or datetime.date.today().isoformat(), "medium": medium,
         "work": work, "item": item, "verdict": verdict, "words": words or "", "by": owner(),
         "source": source}
    if over:
        r["over"] = over
    if file:
        r["file"] = file
    if weak:
        r["weak"] = True
    r["key"] = row_key(r)
    return r


def existing_keys():
    return {r.get("key") for r in read_jsonl(record_path())}


def cmd_add(a):
    r = make_row(a.medium, a.work, a.item, a.verdict, a.words, a.over, a.file, a.source or "said", a.date, a.weak)
    if r["key"] in existing_keys():
        return {"added": 0, "duplicate": r["key"], "record": record_path()}
    append_rows([r])
    return {"added": 1, "row": r, "record": record_path()}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def picks_from_set(d, medium, work=None):
    """Rows from one askwright set folder; answered choice questions with media only."""
    q = load_json(os.path.join(d, "questions.json"))
    ans = load_json(os.path.join(d, "answers.json")).get("answers", {})
    w = work or (q.get("project") or {}).get("name") or q.get("title") or os.path.basename(d)
    out, skipped = [], []
    for qq in q.get("questions", []):
        qid = qq.get("id")
        a = ans.get(qid)
        if not a or a.get("state") != "answered" or not a.get("choice"):
            skipped.append([qid, "unanswered"])
            continue
        if not (qq.get("media") or any(o.get("media") for o in qq.get("options", []))):
            skipped.append([qid, "no media (process decision)"])
            continue
        labels = {o.get("id"): o.get("label", o.get("id")) for o in qq.get("options", [])}
        choice = a["choice"]
        rest = [labels[k] for k in labels if k != choice and k not in ("none", "skip")]
        r = make_row(medium, w, "%s: %s" % (qid, qq.get("title") or qq.get("prompt", "")), "pick",
                     words=a.get("note", ""), over="; ".join(rest) or None,
                     source=os.path.join(d, "answers.json").replace(os.sep, "/"),
                     date=(a.get("updated") or "")[:10] or None,
                     weak=bool(a.get("guess_revealed_before_pick")))
        r["choice"] = labels.get(choice, choice)
        r["key"] = hashlib.sha1(("%s|%s|%s|%s" % (q.get("id") or q.get("title"), qid, choice,
                                                   a.get("updated"))).encode("utf-8")).hexdigest()[:16]
        out.append(r)
    return out, skipped


def cmd_import(a):
    keys = existing_keys()
    new, skipped = [], []
    for d in a.dirs:
        rows, sk = picks_from_set(d, a.medium, a.work)
        skipped += [[d] + s for s in sk]
        for r in rows:
            if r["key"] in keys:
                continue
            keys.add(r["key"])
            new.append(r)
    if not a.dry_run:
        append_rows(new)
    return {"added": 0 if a.dry_run else len(new), "would_add": len(new), "skipped": skipped,
            "record": record_path(), "rows": new}


def sibling_sources():
    cfg = {}
    p = os.path.join(home(), "config.json")
    if os.path.isfile(p):
        cfg = load_json(p).get("siblings", {})
    src = {}
    for name, env, rel in (("musicwright", "MUSICWRIGHT_HOME", "verdicts.jsonl"),
                           ("artwright", "ARTWRIGHT_HOME", "calibration/labels.jsonl")):
        h = os.environ.get(env) or cfg.get(name)
        if h:
            f = os.path.join(os.path.expanduser(h), rel)
            if os.path.isfile(f):
                src[name] = f
    return src


def sibling_rows():
    out = []
    for name, f in sibling_sources().items():
        for r in read_jsonl(f):
            if name == "musicwright" and r.get("type") == "verdict":
                out.append({"medium": "music", "work": r.get("take", ""), "item": r.get("take", ""),
                            "verdict": r.get("verdict"), "words": r.get("note", ""), "date": str(r.get("date", ""))[:10],
                            "source": f.replace(os.sep, "/"), "from": name})
            elif name == "artwright" and r.get("by") == "human":
                pick = r.get("pick")
                win = (r.get(pick) or {}).get("file", "") if pick in ("a", "b") else ""
                out.append({"medium": "art", "work": "calibration", "item": os.path.basename(win) or "tie",
                            "verdict": "pick" if pick in ("a", "b") else "maybe", "words": r.get("note", ""),
                            "date": str(r.get("at", ""))[:10], "source": f.replace(os.sep, "/"), "from": name})
    return out


def cmd_show(a):
    rows = read_jsonl(record_path())
    if a.siblings:
        rows += sibling_rows()
    if a.medium:
        rows = [r for r in rows if r.get("medium") == a.medium]
    if a.work:
        rows = [r for r in rows if a.work.lower() in str(r.get("work", "")).lower()]
    rows.sort(key=lambda r: str(r.get("date", "")))
    counts = {}
    for r in rows:
        k = "%s/%s" % (r.get("medium"), r.get("verdict"))
        counts[k] = counts.get(k, 0) + 1
    return {"count": len(rows), "by_medium_verdict": counts, "rows": rows[-a.limit:] if a.limit else rows}


def cmd_where(_a):
    return {"home": home(), "record": record_path(), "exists": os.path.isfile(record_path()),
            "rows": len(read_jsonl(record_path())), "siblings": sibling_sources()}


def main(argv=None):
    p = argparse.ArgumentParser(prog="tw.py")
    sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("where")
    ad = sp.add_parser("add")
    for k in ("medium", "work", "item", "verdict"):
        ad.add_argument("--" + k, required=True)
    for k in ("words", "over", "file", "source", "date"):
        ad.add_argument("--" + k)
    ad.add_argument("--weak", action="store_true")
    im = sp.add_parser("import")
    im.add_argument("dirs", nargs="+")
    im.add_argument("--medium", required=True)
    im.add_argument("--work")
    im.add_argument("--dry-run", action="store_true")
    sh = sp.add_parser("show")
    sh.add_argument("--medium")
    sh.add_argument("--work")
    sh.add_argument("--siblings", action="store_true")
    sh.add_argument("--limit", type=int, default=50)
    a = p.parse_args(argv)
    res = {"where": cmd_where, "add": cmd_add, "import": cmd_import, "show": cmd_show}[a.cmd](a)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
