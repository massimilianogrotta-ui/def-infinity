"""Tests for stage_check.py and attempts.py. Run: python3 -m unittest discover -s tests"""
import pathlib, sys, tempfile, unittest
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import attempts, stage_check  # noqa: E402

PLAN = """Product stage: {stage}
### 1. a
- Archetype: Builder (bench) · Prototyper already used
### 2. b
- Archetype: builder
### 3. c
- **Archetype:** maintainer, cadence weekly
"""

class StageTests(unittest.TestCase):
    def test_parse(self):
        t = PLAN.format(stage="in crescita")
        self.assertEqual(stage_check.read_stage(t), "growing")
        self.assertEqual(stage_check.read_archetypes(t), ["builder", "builder", "maintainer"])
    def test_growing_warns_missing_sweeper_grower(self):
        lines, warn = stage_check.report("growing", ["builder", "builder", "maintainer"])
        self.assertEqual(len(warn), 2)
        self.assertTrue(any("sweeper" in w for w in warn) and any("grower" in w for w in warn))
    def test_new_product_flags_maintainer(self):
        _, warn = stage_check.report("new", ["prototyper", "builder", "sweeper", "maintainer"])
        self.assertEqual(warn, ["maintainer is not in the mix for a new product (1 piece(s)): is that work for now?"])
    def test_fit(self):
        _, warn = stage_check.report("mature", ["sweeper", "grower", "maintainer", "builder"])
        self.assertEqual(warn, [])
    def test_no_stage_exit1(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("- Archetype: builder\n")
        self.assertEqual(stage_check.main([f.name]), 1)
        self.assertEqual(stage_check.main([f.name, "--stage", "new"]), 0)

class AttemptTests(unittest.TestCase):
    def test_three_strikes(self):
        d = tempfile.mkdtemp()
        for i in range(2):
            attempts.main(["log", "--piece", "4", "--outcome", "fail", "--note", f"try {i}", "--dir", d])
        self.assertEqual(attempts.main(["check", "--piece", "4", "--dir", d]), 0)
        attempts.main(["log", "--piece", "4", "--outcome", "fail", "--dir", d])
        self.assertEqual(attempts.main(["check", "--piece", "4", "--dir", d]), 2)
        self.assertEqual(attempts.main(["check", "--piece", "5", "--dir", d]), 0)   # other pieces unaffected
        attempts.main(["log", "--piece", "4", "--outcome", "ok", "--dir", d])
        self.assertEqual(attempts.main(["check", "--piece", "4", "--dir", d]), 0)   # success resets

if __name__ == "__main__":
    unittest.main()
