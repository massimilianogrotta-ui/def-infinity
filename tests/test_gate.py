"""Unit tests for gate.py and guard_hook.py (stdlib only). Run: python3 -m unittest discover -s tests"""
import json, os, pathlib, subprocess, sys, tempfile, unittest
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import gate, guard_hook  # noqa: E402

def ev(agent, tool, cwd, **inp):
    return {"agent_type": agent, "tool_name": tool, "cwd": str(cwd), "tool_input": inp}

class Repo:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory(); self.p = pathlib.Path(self.tmp.name)
        for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
            subprocess.run(["git", "-C", str(self.p), *a], check=True)
        (self.p / "package.json").write_text("{}\n"); (self.p / "test").mkdir(); (self.p / "test/a.test.js").write_text("x\n")
        subprocess.run(["git", "-C", str(self.p), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.p), "commit", "-qm", "init"], check=True)
    def run(self, *args):
        return gate.main(["--repo", str(self.p), *args])

class GateTests(unittest.TestCase):
    def test_glob(self):
        self.assertTrue(gate.matches(".spike/x/y.py", [".spike/**"]))
        self.assertTrue(gate.matches("a/b/spike_q.md", ["**/spike_*.md"]))
        self.assertTrue(gate.matches("spike_q.md", ["**/spike_*.md"]))
        self.assertFalse(gate.matches("package.json", [".spike/**", "**/spike_*.md"]))
        self.assertTrue(gate.matches("config/.env.local", gate.ALWAYS_DENY))

    def test_prototyper_touching_package_json_escalates(self):
        r = Repo(); (r.p / "package.json").write_text('{"scripts":{}}\n')
        self.assertEqual(r.run("--archetype", "prototyper"), 2)
    def test_prototyper_spike_ok(self):
        r = Repo(); (r.p / ".spike").mkdir(); (r.p / ".spike/a.py").write_text("1"); (r.p / "spike_cov.md").write_text("x")
        self.assertEqual(r.run("--archetype", "prototyper"), 0)
    def test_grower_needs_approval(self):
        r = Repo(); (r.p / "ONBOARDING.txt").write_text("new"); (r.p / "EXPERIMENT_x.md").write_text("e")
        self.assertEqual(r.run("--archetype", "grower"), 2)
        self.assertEqual(r.run("--archetype", "grower", "--approved"), 0)
    def test_maintainer_levels(self):
        r = Repo(); (r.p / "package.json").write_text('{"a":1}\n')
        self.assertEqual(r.run("--archetype", "maintainer"), 2)          # no state file = L1
        (r.p / "MAINTAINER_STATE.md").write_text("**Level:** L2\n")
        self.assertEqual(r.run("--archetype", "maintainer"), 0)          # L2 may edit an existing file
        (r.p / "sync.sh").write_text("#!/bin/sh\n")
        self.assertEqual(r.run("--archetype", "maintainer"), 2)          # but not add a script
    def test_sweeper(self):
        r = Repo(); (r.p / "test/a.test.js").unlink()
        self.assertEqual(r.run("--archetype", "sweeper"), 2)             # deleting a test
        subprocess.run(["git", "-C", str(r.p), "checkout", "-q", "--", "."], check=True)
        (r.p / "UNSHIP_LIST.md").write_text("x")
        self.assertEqual(r.run("--archetype", "sweeper"), 0)
        (r.p / "helper.js").write_text("x")
        self.assertEqual(r.run("--archetype", "sweeper"), 2)             # adding a file
    def test_secrets_blocked_even_for_builder(self):
        r = Repo(); (r.p / ".env").write_text("K=1")
        self.assertEqual(r.run("--archetype", "builder"), 2)
    def test_base_ref_sees_commits(self):
        r = Repo(); base = subprocess.run(["git", "-C", str(r.p), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        (r.p / "package.json").write_text('{"b":1}\n')
        subprocess.run(["git", "-C", str(r.p), "commit", "-qam", "c"], check=True)
        self.assertEqual(r.run("--archetype", "prototyper"), 0)          # clean tree, commit invisible
        self.assertEqual(r.run("--archetype", "prototyper", "--base", base), 2)

class HookTests(unittest.TestCase):
    def setUp(self):
        self.r = Repo()
    def d(self, *a, **k):
        return guard_hook.decide(ev(*a, cwd=self.r.p, **k))
    def test_other_agents_untouched(self):
        self.assertIsNone(self.d("", "Write", file_path="package.json"))
        self.assertIsNone(self.d("Explore", "Write", file_path="package.json"))
    def test_prototyper(self):
        self.assertIsNotNone(self.d("def-infinity:prototyper", "Edit", file_path=str(self.r.p / "package.json")))
        self.assertIsNone(self.d("def-infinity:prototyper", "Write", file_path=".spike/q/a.py"))
        self.assertIsNotNone(self.d("prototyper", "Write", file_path="/tmp/x.py"))
    def test_push_blocked(self):
        self.assertIsNotNone(self.d("def-infinity:builder", "Bash", command="npm test && git push origin main"))
        self.assertIsNotNone(self.d("def-infinity:builder", "Bash", command="git -C ../repo push"))
        self.assertIsNotNone(self.d("def-infinity:sweeper", "Bash", command="gh pr merge 3"))
        self.assertIsNone(self.d("def-infinity:builder", "Bash", command="git status && npm test"))
        self.assertIsNone(self.d("def-infinity:builder", "Bash", command="git log --grep pushed"))
    def test_maintainer_new_file(self):
        (self.r.p / "MAINTAINER_STATE.md").write_text("Level: L2\n")
        self.assertIsNone(self.d("def-infinity:maintainer", "Edit", file_path="package.json"))
        self.assertIsNotNone(self.d("def-infinity:maintainer", "Write", file_path="sync.sh"))
    def test_grower_and_sweeper(self):
        self.assertIsNotNone(self.d("def-infinity:grower", "Write", file_path="ONBOARDING.txt"))
        self.assertIsNone(self.d("def-infinity:grower", "Write", file_path="EXPERIMENT_onb.md"))
        self.assertIsNotNone(self.d("def-infinity:sweeper", "Write", file_path="new_helper.js"))
        self.assertIsNone(self.d("def-infinity:sweeper", "Edit", file_path="package.json"))
    def test_shell_writes(self):
        heredoc = "mkdir -p scripts && cat > scripts/sync-json.mjs <<'EOF'\nconst a = b > c;\necho x > y\nEOF\nchmod +x scripts/sync-json.mjs"
        self.assertIsNotNone(self.d("def-infinity:maintainer", "Bash", command=heredoc))   # the real escape seen on the bench
        self.assertEqual(guard_hook.bash_targets(heredoc), [("scripts/sync-json.mjs", "write")])
        self.assertIsNone(self.d("def-infinity:maintainer", "Bash", command="cat fonte.json copia.json; diff fonte.json copia.json > /dev/null"))
        self.assertIsNone(self.d("def-infinity:maintainer", "Bash", command="echo ok > HEALTHCHECK_2026-10-19.md"))
        self.assertIsNotNone(self.d("def-infinity:prototyper", "Bash", command="npm pkg set scripts.coverage='node --test'"))
        self.assertIsNone(self.d("def-infinity:prototyper", "Bash", command="node --test --experimental-test-coverage 2>&1 | tee .spike/cov/out.txt"))
        self.assertIsNotNone(self.d("def-infinity:grower", "Bash", command="cp .spike/new.txt ONBOARDING.txt"))
        self.assertIsNotNone(self.d("def-infinity:grower", "Bash", command="sed -i 's/a/b/' ONBOARDING.txt"))
        self.assertIsNotNone(self.d("def-infinity:sweeper", "Bash", command="rm -f test/a.test.js"))
        self.assertIsNone(self.d("def-infinity:sweeper", "Bash", command="rm src/dead.js"))
        self.assertIsNone(self.d("def-infinity:builder", "Bash", command="cat > src/x.js <<'EOF'\nx\nEOF"))
        self.assertIsNone(self.d("def-infinity:prototyper", "Bash", command="ls -la 2>&1 && git log --oneline | head"))

    def test_secret_blocked_for_builder(self):
        self.assertIsNotNone(self.d("def-infinity:builder", "Write", file_path=".env.local"))
    def test_hook_output_is_deny_json(self):
        p = subprocess.run([sys.executable, str(ROOT / "scripts/guard_hook.py")], capture_output=True, text=True,
                           input=json.dumps(ev("def-infinity:grower", "Write", self.r.p, file_path="README.md")))
        out = json.loads(p.stdout)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")
        p = subprocess.run([sys.executable, str(ROOT / "scripts/guard_hook.py")], capture_output=True, text=True, input="not json")
        self.assertEqual((p.returncode, p.stdout), (0, ""))

if __name__ == "__main__":
    unittest.main()
