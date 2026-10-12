"""Offline tests for scripts/check_public.py. All fixtures are synthetic and built at runtime."""
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "check_public.py")
spec = importlib.util.spec_from_file_location("check_public", SCRIPT)
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)

CLEAN = "# Notes\n\nNothing personal here. See [[Home]].\n"


def run_git(repo, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t")
    subprocess.run(["git", "-C", repo, *args], check=True, capture_output=True, env=env)


class Fixture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = self._tmp.name
        run_git(self.repo, "init", "-q")

    def write(self, rel, content, binary=False):
        path = os.path.join(self.repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb" if binary else "w") as fh:
            fh.write(content)
        return path

    def add(self, *rels):
        run_git(self.repo, "add", *rels)

    def rules(self, **kw):
        return {(p, r) for p, _, r in cp.check(self.repo, **kw)}


class AllowedContent(Fixture):
    def test_clean_allowed_tree_passes(self):
        self.write("README.md", CLEAN)
        self.write("vault/Home.md", CLEAN)
        self.write(".agents/skills/brain-spec/SKILL.md", CLEAN)
        self.write("vault/Tasks/.gitkeep", "")
        self.add(".")
        self.assertEqual(cp.check(self.repo), [])

    def test_cli_exit_codes(self):
        self.write("README.md", CLEAN)
        self.add(".")
        ok = subprocess.run([sys.executable, SCRIPT, "--repo", self.repo], capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0)
        self.write("notes.md", CLEAN)
        self.add(".")
        bad = subprocess.run([sys.executable, SCRIPT, "--repo", self.repo], capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1)
        self.assertIn("notes.md:0: path-not-allowed", bad.stdout)


class ForbiddenFiles(Fixture):
    def test_unlisted_paths_rejected(self):
        for rel in ("notes.md", "vault/.obsidian/workspace.json", "vault/Projects/mine.md", "Identity/user.md"):
            self.write(rel, CLEAN)
        self.add("-f", ".")
        rules = self.rules()
        for rel in ("notes.md", "vault/.obsidian/workspace.json", "vault/Projects/mine.md", "Identity/user.md"):
            self.assertIn((rel, "path-not-allowed"), rules)

    def test_tracked_symlink_rejected(self):
        self.write("README.md", CLEAN)
        os.symlink("README.md", os.path.join(self.repo, "vault_link.md"))
        self.add(".")
        self.assertIn(("vault_link.md", "symlink"), self.rules())

    def test_indexed_file_replaced_by_symlink_rejected_on_disk(self):
        self.write("README.md", CLEAN)
        self.add(".")
        outside = self.write("../" + os.path.basename(self.repo) + "-target.md", CLEAN)
        self.addCleanup(os.remove, outside)
        os.remove(os.path.join(self.repo, "README.md"))
        os.symlink(outside, os.path.join(self.repo, "README.md"))
        self.assertIn(("README.md", "symlink"), self.rules())
        self.assertEqual(self.rules(staged=True), set())

    def test_symlinked_tracked_directory_rejected_on_disk(self):
        self.write("docs/privacy.md", CLEAN)
        self.add(".")
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        with open(os.path.join(outside.name, "privacy.md"), "w") as fh:
            fh.write(CLEAN)
        os.rename(os.path.join(self.repo, "docs"), os.path.join(self.repo, "docs-moved"))
        os.symlink(outside.name, os.path.join(self.repo, "docs"))
        self.assertIn(("docs/privacy.md", "symlink"), self.rules())

    def test_binary_rejected(self):
        self.write("README.md", b"abc\x00def", binary=True)
        self.add(".")
        self.assertIn(("README.md", "binary"), self.rules())

    def test_non_utf8_rejected_as_binary(self):
        self.write("README.md", b"\xff\xfe\xfa", binary=True)
        self.add(".")
        self.assertIn(("README.md", "binary"), self.rules())


class SecretPatterns(Fixture):
    def assert_flagged(self, line, rule):
        self.write("README.md", CLEAN + line + "\n")
        self.add(".")
        found = [(ln, r) for _, ln, r in cp.check(self.repo)]
        self.assertIn((4, rule), found)

    def test_home_path(self):
        self.assert_flagged("see " + "/" + "home" + "/" + "alice" + "/notes", "home-path")
        self.assert_flagged("see " + "/" + "Users" + "/" + "bob", "home-path")

    def test_email(self):
        self.assert_flagged("mail " + "someone" + "@" + "example.org", "email")

    def test_private_key_header(self):
        self.assert_flagged("-----BEGIN " + "RSA PRIVATE" + " KEY-----", "private-key")

    def test_credential_assignment(self):
        self.assert_flagged("api_" + "key = " + "abcd1234efgh5678", "credential-assignment")
        self.assert_flagged("PASS" + "WORD: " + "hunter2hunter2", "credential-assignment")

    def test_credential_token(self):
        self.assert_flagged("x " + "gh" + "p_" + "A" * 24, "credential-token")

    def test_output_never_prints_values(self):
        value = "someone" + "@" + "example.org"
        self.write("README.md", CLEAN + value + "\n")
        self.add(".")
        proc = subprocess.run([sys.executable, SCRIPT, "--repo", self.repo], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        self.assertNotIn(value, proc.stdout + proc.stderr)

    def test_prose_mentioning_tokens_is_fine(self):
        self.write("README.md", CLEAN + "Never store a token or password in a note.\n")
        self.add(".")
        self.assertEqual(cp.check(self.repo), [])


class Denylist(Fixture):
    def make_denylist(self, *terms):
        path = os.path.join(self._tmp.name + "-deny.txt")
        with open(path, "w") as fh:
            fh.write("# comment\n" + "\n".join(terms) + "\n")
        self.addCleanup(os.remove, path)
        return path

    def test_content_and_path_matches(self):
        term = "zq" + "xjwv"
        deny = self.make_denylist(term)
        self.write("README.md", CLEAN + "About " + term.upper() + " project\n")
        self.write("docs/privacy.md", CLEAN)
        self.add(".")
        found = cp.check(self.repo, denylist=cp.load_denylist(deny))
        self.assertEqual([(p, ln, r) for p, ln, r in found], [("README.md", 4, "denylist")])

    def test_cli_denylist_flag_and_no_value_printed(self):
        term = "zq" + "xjwv"
        deny = self.make_denylist(term)
        self.write("README.md", CLEAN + term + "\n")
        self.add(".")
        proc = subprocess.run([sys.executable, SCRIPT, "--repo", self.repo, "--denylist", deny], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("README.md:4: denylist", proc.stdout)
        self.assertNotIn(term, proc.stdout)


class StagedMode(Fixture):
    def test_staged_offending_version_differs_from_clean_disk(self):
        self.write("README.md", CLEAN + "mail " + "someone" + "@" + "example.org\n")
        self.add("README.md")
        self.write("README.md", CLEAN)  # disk is clean again, index is not
        self.assertEqual(cp.check(self.repo, staged=False), [])
        self.assertIn(("README.md", "email"), self.rules(staged=True))

    def test_clean_staged_version_with_offending_disk(self):
        self.write("README.md", CLEAN)
        self.add("README.md")
        self.write("README.md", CLEAN + "mail " + "someone" + "@" + "example.org\n")
        self.assertEqual(cp.check(self.repo, staged=True), [])
        self.assertIn(("README.md", "email"), self.rules(staged=False))


if __name__ == "__main__":
    unittest.main()
