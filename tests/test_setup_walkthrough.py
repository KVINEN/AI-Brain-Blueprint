"""Synthetic walkthrough of the brain-setup skill's file operations and of the clean-export procedure.

The setup skill is instructions for an agent, so these tests do NOT enforce it. They apply the skill's
documented allowlist, mapping and destination rules (a reference model written here) to synthetic answers
and check that the resulting vault is complete and consistent. Set BLUEPRINT_SCRATCH_DIR to keep the
generated vaults for inspection; otherwise they live in a temporary directory.
"""
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKER = os.path.join(ROOT, "scripts", "check_public.py")

VAULT_FILES = (
    ["AGENTS.md", "CLAUDE.md", "Home.md", "Board.base"]
    + [f"Identity/{n}.md" for n in ("user", "soul", "identity")]
    + [f"Templates/{n}.md" for n in ("project", "spec", "task", "decision", "knowledge", "source", "moc")]
    + [f"{d}/.gitkeep" for d in ("Projects", "Decisions", "Knowledge/Sources", "MOCs", "Inbox", "TODO")]
)
SKILL_FILES = [f".agents/skills/brain-{n}/SKILL.md" for n in ("capture", "spec", "build", "review")]

TWO_AGENTS = dict(alias="Sam", role="hobby developer", goals="ship a small app", projects=[("recipe-box", "keep recipes", "../recipe-box")],
                  language="English", depth="brief", avoid="long preambles", tone="direct",
                  architect="agent-a", builder="agent-b", approval="manual", outside="passwords and tokens", actions="ask first",
                  editor="Obsidian", git="local-only")
SINGLE_AGENT = dict(TWO_AGENTS, architect="agent-a", builder="agent-a", approval="auto")
SKIPPED = dict(alias=None, role=None, goals=None, projects=[], language=None, depth=None, avoid=None, tone=None,
               architect=None, builder=None, approval=None, outside=None, actions=None, editor=None, git=None)


def validate_destination(dest, checkout, worktrees):
    """Reference model of SKILL.md section 2. Returns None when acceptable, else the rule that rejects it."""
    real = os.path.realpath(dest)
    for tree in [checkout, *worktrees]:
        t = os.path.realpath(tree)
        if real == t or real.startswith(t + os.sep) or t.startswith(real + os.sep):
            return "overlaps-checkout"
    if os.path.exists(real) and (not os.path.isdir(real) or os.listdir(real)):
        return "not-empty"
    return None


def source_ok(rel):
    path = os.path.join(ROOT, rel)
    parts = rel.split("/")
    return os.path.isfile(path) and not any(os.path.islink(os.path.join(ROOT, *parts[:i])) for i in range(1, len(parts) + 1))


def fill(text, label, value):
    """Replace the placeholder after `label` with value, or keep _unconfigured_ when skipped."""
    if value is None:
        return text
    return re.sub(rf"(\*\*{re.escape(label)}:\*\* )_unconfigured_", lambda m: m.group(1) + value, text)


def run_setup(dest, a):
    """Reference model of SKILL.md sections 4 (write) for synthetic answers `a`."""
    for rel in VAULT_FILES:
        assert source_ok("vault/" + rel), rel
        os.makedirs(os.path.dirname(os.path.join(dest, rel)) or dest, exist_ok=True)
        shutil.copyfile(os.path.join(ROOT, "vault", rel), os.path.join(dest, rel))
    for rel in SKILL_FILES:
        assert source_ok(rel), rel
        os.makedirs(os.path.dirname(os.path.join(dest, rel)), exist_ok=True)
        shutil.copyfile(os.path.join(ROOT, rel), os.path.join(dest, rel))

    def edit(rel, fn):
        p = os.path.join(dest, rel)
        with open(p, encoding="utf-8") as fh:
            text = fh.read()
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(fn(text))

    def user(t):
        t = fill(t, "Name or alias", a["alias"])
        t = fill(t, "Role / background", a["role"])
        return fill(t, "Goals (next 3–6 months)", a["goals"])

    def soul(t):
        t = fill(t, "Explanation depth", a["depth"])
        t = fill(t, "Tone and format preferences", a["tone"])
        return fill(t, "Avoid", a["avoid"])

    def identity(t):
        agents = ", ".join(dict.fromkeys(x for x in (a["architect"], a["builder"]) if x)) or None
        t = fill(t, "Agents in use", agents)
        t = fill(t, "Architect", a["architect"])
        t = fill(t, "Builder", a["builder"])
        t = fill(t, "Spec approval", a["approval"])
        return fill(t, "Actions needing approval beyond local note edits", a["actions"])

    def agents(t):
        if a["architect"] or a["builder"]:
            roles = f"architect = {a['architect'] or '_unconfigured_'}, builder = {a['builder'] or '_unconfigured_'}"
            if a["architect"] and a["architect"] == a["builder"]:
                roles += " (one agent holds both roles; review stays a separate step)"
            t = re.sub(r"architect = _unconfigured_, builder = _unconfigured_[^\n]*", lambda m: roles, t)
        if a["approval"]:
            t = re.sub(r"(- Spec approval: )_unconfigured_[^\n]*", lambda m: m.group(1) + a["approval"], t)
        if a["language"]:
            t = t.replace("Language for notes: English", "Language for notes: " + a["language"])
        return t

    def home(t):
        if a["projects"]:
            bullets = "".join(f"- [[{slug}]]\n" for slug, _, _ in a["projects"])
            t = re.sub(r"- _None yet\._ Add one note per project[^\n]*\n", lambda m: bullets, t)
        if a["editor"] or a["git"]:
            t += f"\n## Setup choices\n- Editor: {a['editor'] or '_unconfigured_'}\n- Versioning: {a['git'] or '_unconfigured_'}\n"
        return t

    edit("Identity/user.md", user)
    edit("Identity/soul.md", soul)
    edit("Identity/identity.md", identity)
    edit("AGENTS.md", agents)
    edit("Home.md", home)
    for rel in ("AGENTS.md", "Home.md", "Identity/user.md", "Identity/soul.md", "Identity/identity.md"):
        edit(rel, lambda t: re.sub(r"^> Status: \*\*unconfigured\*\*.*$", "Status: configured by brain-setup", t, flags=re.M))
    with open(os.path.join(ROOT, "vault/Templates/project.md"), encoding="utf-8") as fh:
        template = fh.read()
    for slug, purpose, repo in a["projects"]:
        note = template.replace("repo:\n", f"repo: {repo}\n").replace("# <project>", f"# {slug}")
        note = note.replace("one line.", purpose).replace("local path of the code repository, or \"none yet\".", repo)
        os.makedirs(os.path.join(dest, "Projects", slug, "specs"), exist_ok=True)
        with open(os.path.join(dest, "Projects", slug, f"{slug}.md"), "w", encoding="utf-8") as fh:
            fh.write(note)
        open(os.path.join(dest, "Projects", slug, "specs", ".gitkeep"), "w").close()


def tree(dest):
    return sorted(os.path.relpath(os.path.join(d, f), dest) for d, _, fs in os.walk(dest) for f in fs)


def read(dest, rel):
    with open(os.path.join(dest, rel), encoding="utf-8") as fh:
        return fh.read()


class ScratchBase(unittest.TestCase):
    def scratch(self, name):
        keep = os.environ.get("BLUEPRINT_SCRATCH_DIR")
        if keep:
            path = os.path.join(keep, name)
            shutil.rmtree(path, ignore_errors=True)
            os.makedirs(path)
            return path
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return os.path.join(tmp.name, name)


class Onboarding(ScratchBase):
    def test_shipped_sources_are_regular_files(self):
        for rel in ["vault/" + r for r in VAULT_FILES] + SKILL_FILES:
            self.assertTrue(source_ok(rel), rel)

    def test_two_agent_manual_vault_is_complete_and_consistent(self):
        dest = self.scratch("two-agent")
        run_setup(dest, TWO_AGENTS)
        expected = set(VAULT_FILES) | set(SKILL_FILES) | {"Projects/recipe-box/recipe-box.md", "Projects/recipe-box/specs/.gitkeep"}
        self.assertEqual(set(tree(dest)), expected)
        self.assertNotIn("brain-setup", " ".join(tree(dest)))
        self.assertIn("**Name or alias:** Sam", read(dest, "Identity/user.md"))
        self.assertIn("- [[recipe-box]]\n", read(dest, "Home.md"))
        self.assertNotIn("_None yet._", read(dest, "Home.md"))
        self.assertIn("architect = agent-a, builder = agent-b", read(dest, "AGENTS.md"))
        self.assertIn("**Architect:** agent-a", read(dest, "Identity/identity.md"))
        self.assertIn("**Builder:** agent-b", read(dest, "Identity/identity.md"))
        self.assertIn("Spec approval: manual", read(dest, "AGENTS.md"))
        self.assertIn("**Spec approval:** manual", read(dest, "Identity/identity.md"))
        self.assertIn("repo: ../recipe-box", read(dest, "Projects/recipe-box/recipe-box.md"))
        for rel in ("AGENTS.md", "Home.md", "Identity/user.md", "Identity/soul.md", "Identity/identity.md"):
            self.assertNotIn("**unconfigured**", read(dest, rel))
            self.assertIn("configured by brain-setup", read(dest, rel))
        self.assertNotIn("_unconfigured_", read(dest, "Identity/identity.md").split("Actions")[0])

    def test_single_agent_auto_vault(self):
        dest = self.scratch("single-agent")
        run_setup(dest, SINGLE_AGENT)
        agents = read(dest, "AGENTS.md")
        self.assertIn("architect = agent-a, builder = agent-a (one agent holds both roles", agents)
        self.assertIn("Spec approval: auto", agents)
        self.assertIn("**Agents in use:** agent-a\n", read(dest, "Identity/identity.md"))
        self.assertIn("a human merges", agents)

    def test_skipped_answers_stay_unconfigured_and_no_project_notes(self):
        dest = self.scratch("skipped")
        run_setup(dest, SKIPPED)
        self.assertEqual(set(tree(dest)), set(VAULT_FILES) | set(SKILL_FILES))
        self.assertIn("**Name or alias:** _unconfigured_", read(dest, "Identity/user.md"))
        self.assertIn("architect = _unconfigured_, builder = _unconfigured_", read(dest, "AGENTS.md"))
        self.assertIn("_None yet._ Add one note per project", read(dest, "Home.md"))

    def test_extra_and_symlinked_files_are_never_copied(self):
        extra = os.path.join(ROOT, "vault", "Inbox", "zz-extra.md")
        self.assertFalse(os.path.exists(extra))  # the model copies exact names only, so extras cannot leak
        dest = self.scratch("exact")
        run_setup(dest, SKIPPED)
        self.assertNotIn("Inbox/zz-extra.md", tree(dest))

    def test_vault_contains_no_checkout_path_or_answers_leak_back(self):
        dest = self.scratch("noleak")
        run_setup(dest, TWO_AGENTS)
        for rel in tree(dest):
            self.assertNotIn(ROOT, read(dest, rel), rel)
        with open(os.path.join(ROOT, "vault", "Identity", "user.md"), encoding="utf-8") as fh:
            self.assertNotIn("Sam", fh.read())


class DestinationRules(ScratchBase):
    """Reference-model checks of the checklist in SKILL.md section 2; the skill itself is not machine-enforced."""

    def test_checkout_and_worktree_overlap_rejected(self):
        self.assertEqual(validate_destination(os.path.join(ROOT, "my-vault"), ROOT, []), "overlaps-checkout")
        self.assertEqual(validate_destination(ROOT, ROOT, []), "overlaps-checkout")
        self.assertEqual(validate_destination(os.path.dirname(ROOT), ROOT, []), "overlaps-checkout")
        with tempfile.TemporaryDirectory() as other:
            self.assertEqual(validate_destination(os.path.join(other, "wt", "v"), ROOT, [os.path.join(other, "wt")]), "overlaps-checkout")

    def test_symlink_into_checkout_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            link = os.path.join(tmp, "link")
            os.symlink(ROOT, link)
            self.assertEqual(validate_destination(os.path.join(link, "v"), ROOT, []), "overlaps-checkout")
            self.assertEqual(validate_destination(link, ROOT, []), "overlaps-checkout")

    def test_nonempty_and_file_destinations_rejected_empty_or_absent_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            checkout = os.path.join(tmp, "checkout")
            os.mkdir(checkout)
            full = os.path.join(tmp, "full")
            os.mkdir(full)
            open(os.path.join(full, "a.md"), "w").close()
            afile = os.path.join(tmp, "afile")
            open(afile, "w").close()
            empty = os.path.join(tmp, "empty")
            os.mkdir(empty)
            self.assertEqual(validate_destination(full, checkout, []), "not-empty")
            self.assertEqual(validate_destination(afile, checkout, []), "not-empty")
            self.assertIsNone(validate_destination(empty, checkout, []))
            self.assertIsNone(validate_destination(os.path.join(tmp, "absent"), checkout, []))


class CleanExport(unittest.TestCase):
    """Runs the docs/privacy.md clean-export commands on a synthetic source repository."""

    def git(self, cwd, *args):
        env = dict(os.environ, GIT_AUTHOR_NAME="pub", GIT_AUTHOR_EMAIL="pub", GIT_COMMITTER_NAME="pub", GIT_COMMITTER_EMAIL="pub")
        return subprocess.run(["git", "-C", cwd, *args], check=True, capture_output=True, env=env).stdout

    def checker(self, cwd, *extra):
        return subprocess.run([sys.executable, os.path.join(cwd, "scripts", "check_public.py"), "--repo", cwd, *extra],
                              capture_output=True, text=True)

    def make_source(self, tmp, dirty):
        src = os.path.join(tmp, "src")
        os.makedirs(os.path.join(src, "scripts"))
        shutil.copyfile(CHECKER, os.path.join(src, "scripts", "check_public.py"))
        with open(os.path.join(src, "README.md"), "w") as fh:
            fh.write("# Blueprint\n" + ("mail " + "someone" + "@" + "example.org\n" if dirty else ""))
        self.git(src, "init", "-q")
        self.git(src, "add", ".")
        self.git(src, "commit", "-qm", "source")
        return src

    def export(self, src, out):
        os.makedirs(out)
        archive = os.path.join(os.path.dirname(out), "a.tar")
        with open(archive, "wb") as fh:
            fh.write(self.git(src, "archive", "HEAD"))
        with tarfile.open(archive) as tf:
            tf.extractall(out, filter="data")
        self.git(out, "init", "-q", "-b", "main")

    def test_staged_before_checks_clean_export_passes_then_commits(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "public")
            self.export(self.make_source(tmp, dirty=False), out)
            empty_index = self.checker(out, "--staged")  # why the old order was unsafe: nothing is staged yet
            self.assertEqual(empty_index.returncode, 0)
            self.assertEqual(self.git(out, "ls-files").strip(), b"")
            self.git(out, "add", "-A")
            self.assertEqual(self.checker(out).returncode, 0)
            staged = self.checker(out, "--staged")
            self.assertEqual(staged.returncode, 0)
            self.assertIn("README.md", self.git(out, "ls-files").decode())
            self.git(out, "commit", "-qm", "Initial public release")
            self.assertEqual(self.git(out, "log", "--format=%an %ae %cn %ce").decode().split(), ["pub"] * 4)

    def test_dirty_export_is_caught_before_the_first_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "public")
            self.export(self.make_source(tmp, dirty=True), out)
            self.git(out, "add", "-A")
            self.assertEqual(self.checker(out).returncode, 1)
            self.assertEqual(self.checker(out, "--staged").returncode, 1)
            self.assertNotEqual(subprocess.run(["git", "-C", out, "rev-parse", "--verify", "-q", "HEAD"], capture_output=True).returncode, 0)


if __name__ == "__main__":
    unittest.main()
