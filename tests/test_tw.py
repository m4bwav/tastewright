import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "tastewright", "scripts"))
import tw  # noqa: E402


def run(*argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        tw.main(list(argv))
    return json.loads(buf.getvalue())


def make_set(d, sid="s1"):
    os.makedirs(d)
    opts = [{"id": "t1", "label": "Take 1"}, {"id": "t2", "label": "Take 2"}]
    media = [{"src": "a.mp4", "type": "video"}]
    qs = [{"id": "q1", "kind": "choice", "title": "Opening", "media": media, "options": opts},
          {"id": "q2", "kind": "choice", "title": "Bridge", "media": media, "options": opts},
          {"id": "q3", "kind": "choice", "title": "Ending", "media": media, "options": opts},
          {"id": "q4", "kind": "choice", "title": "Skipped", "media": media, "options": opts},
          {"id": "q5", "kind": "choice", "title": "Which branch?", "options": opts}]
    ans = {"q1": {"choice": "t1", "note": "they're talking to the camera again", "state": "answered",
                  "updated": "2026-11-01T10:00:00"},
           "q2": {"choice": "t2", "note": "", "state": "answered", "updated": "2026-11-01T10:01:00"},
           "q3": {"choice": "t1", "note": "", "state": "answered", "updated": "2026-11-01T10:02:00",
                  "guess_revealed_before_pick": True},
           "q4": {"state": "skipped"},
           "q5": {"choice": "t1", "note": "", "state": "answered", "updated": "2026-11-01T10:03:00"}}
    json.dump({"id": sid, "title": "Test set", "project": {"name": "test film"}, "questions": qs},
              open(os.path.join(d, "questions.json"), "w"))
    json.dump({"answers": ans}, open(os.path.join(d, "answers.json"), "w"))


class TwTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.old = {k: os.environ.get(k) for k in ("TASTEWRIGHT_HOME", "MUSICWRIGHT_HOME", "ARTWRIGHT_HOME")}
        os.environ["TASTEWRIGHT_HOME"] = os.path.join(self.tmp, "home")
        os.environ.pop("MUSICWRIGHT_HOME", None)
        os.environ.pop("ARTWRIGHT_HOME", None)

    def tearDown(self):
        for k, v in self.old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_add_keeps_words_verbatim_and_dedupes(self):
        words = "take 3 of test film, they're talking to the camera again, reject it"
        r = run("add", "--medium", "film", "--work", "test film", "--item", "take 3",
                "--verdict", "reject", "--words", words, "--date", "2026-11-15")
        self.assertEqual(r["added"], 1)
        self.assertEqual(r["row"]["words"], words)
        self.assertTrue(r["record"].startswith(os.environ["TASTEWRIGHT_HOME"]))
        again = run("add", "--medium", "film", "--work", "test film", "--item", "take 3",
                    "--verdict", "reject", "--words", words, "--date", "2026-11-15")
        self.assertEqual(again["added"], 0)

    def test_bad_verdict_refused(self):
        with self.assertRaises(SystemExit):
            run("add", "--medium", "film", "--work", "w", "--item", "i", "--verdict", "love")

    def test_import_hygiene(self):
        a, b = os.path.join(self.tmp, "proj", "s1"), os.path.join(self.tmp, "proj-wt", "s1")
        make_set(a)
        make_set(b)
        r = run("import", a, b, "--medium", "film")
        self.assertEqual(r["added"], 3)  # q1-q3; q4 skipped, q5 no media, worktree copy deduped
        rows = {x["item"].split(":")[0]: x for x in r["rows"]}
        self.assertEqual(rows["q1"]["words"], "they're talking to the camera again")
        self.assertEqual(rows["q2"]["words"], "")
        self.assertTrue(rows["q3"].get("weak"))
        self.assertNotIn("weak", rows["q1"])
        self.assertEqual(rows["q1"]["date"], "2026-11-01")
        self.assertEqual(rows["q1"]["work"], "test film")
        self.assertEqual(rows["q1"]["choice"], "Take 1")
        self.assertEqual(rows["q1"]["over"], "Take 2")
        self.assertEqual(run("import", a, "--medium", "film")["added"], 0)

    def test_import_option_media(self):
        d = os.path.join(self.tmp, "opt", "s1")
        os.makedirs(d)
        q = {"askwright": 1, "title": "Ships", "questions": [
            {"id": "q1", "kind": "pick", "prompt": "Which ship?", "options": [
                {"id": "t1", "label": "Flat", "media": "t1.png"}, {"id": "t2", "label": "Glossy", "media": "t2.png"}]},
            {"id": "c1", "kind": "pick", "prompt": "Retry?", "options": [{"id": "y", "label": "Yes"}, {"id": "n", "label": "No"}]}]}
        a = {"answers": {"q1": {"choice": "t1", "note": "", "state": "answered", "updated": "2026-11-02T20:11:00"},
                         "c1": {"choice": "y", "note": "", "state": "answered", "updated": "2026-11-02T20:11:00"}}}
        for n, o in (("questions.json", q), ("answers.json", a)):
            with open(os.path.join(d, n), "w", encoding="utf-8") as fh:
                json.dump(o, fh)
        r = run("import", d, "--medium", "pixel", "--dry-run")
        self.assertEqual(r["would_add"], 1)  # option-level media counts; c1 is a process question
        self.assertIn("Which ship?", r["rows"][0]["item"])

    def test_siblings_read_not_written(self):
        mh = os.path.join(self.tmp, "music")
        os.makedirs(mh)
        f = os.path.join(mh, "verdicts.jsonl")
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"type": "verdict", "date": "2026-10-17T12:00:00", "take": "flute_1",
                                 "verdict": "keep", "note": "solo means solo", "by": "x"}) + "\n")
        before = hashlib.sha256(open(f, "rb").read()).hexdigest()
        os.environ["MUSICWRIGHT_HOME"] = mh
        r = run("show", "--siblings", "--medium", "music")
        self.assertEqual(r["count"], 1)
        self.assertEqual(r["rows"][0]["words"], "solo means solo")
        self.assertEqual(before, hashlib.sha256(open(f, "rb").read()).hexdigest())

    def test_where(self):
        r = run("where")
        self.assertFalse(r["exists"])
        self.assertEqual(r["siblings"], {})


if __name__ == "__main__":
    unittest.main()
