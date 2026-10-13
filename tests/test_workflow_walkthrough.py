"""Synthetic manual-workflow reference model, not an included dispatcher or skill enforcement.

Check the published contract against actual templates, setup outputs, skill inventory and README.
These fixtures use fictional requests only and exercise retention before removal and archive fallback.
"""
from datetime import datetime, timezone
from pathlib import Path
import re
import unittest
from test_setup_walkthrough import ScratchBase, run_setup, SINGLE_AGENT, TWO_AGENTS, VAULT_FILES, SKILL_FILES

ROOT = Path(__file__).resolve().parents[1]
RANK = {v: i for i, v in enumerate(("critical", "high", "normal", "low"))}


def fields(text):
    front, body = text.split("---", 2)[1:]
    return dict(line.split(":", 1) for line in front.splitlines() if ":" in line), body


def select(items, today="2026-01-06"):
    phase = {"review": 0, "ready": 1, "requested": 2}
    eligible = [i for i in items if i["status"] in phase and
                (i["status"] != "requested" or Path(i["path"]).name[:10] <= today)]
    return sorted(eligible, key=lambda i: (phase[i["status"]], RANK[i.get("importance") or "normal"],
                                           Path(i["path"]).name[:10], i["path"]))


def finish(vault, task, spec, body, importance, references=(), verdict="pass", verified=True, context=()):
    """Human reference steps in brain-review: preserve before retire; archive if original needed."""
    if verdict != "pass" or not verified:
        return False
    quoted = "\n".join("> " + line if line else ">" for line in body.split("\n"))
    stamp = "2026-01-06T12:00:00Z"
    datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(timezone.utc)
    text = ("---\ntype: spec\nstatus: done\nimportance: " + importance +
            "\ntask_stage: done\ntask_completed_at: " + stamp + "\ntask: " + task +
            "\n---\n## Original task\n" + quoted +
            ("\n\nOther task fields, verbatim:\n" + "\n".join("> " + item for item in context) if context else "") +
            "\n\n## Dispatch history\n- " + stamp + " importance " + importance +
            " (observed)\n- " + stamp + " task done: review passed\n")
    original = vault / task
    archive = any("#Detail" in ref.read_text() or "![[" in ref.read_text() for ref in references)
    target = "Completed tasks/" + original.name if archive else spec
    if archive and (vault / target).exists():
        return False
    (vault / spec).parent.mkdir(parents=True, exist_ok=True)
    (vault / spec).write_text(text)
    assert quoted in (vault / spec).read_text()
    original.write_text("---\ntype: task\nstatus: done\nstage: done\n---\n" + body)
    for ref in references:
        ref.write_text(ref.read_text().replace(task, target))
    if archive:
        (vault / target).parent.mkdir(parents=True, exist_ok=True)
        original.rename(vault / target)
        (vault / spec).write_text(text.replace("task: " + task, "task: " + target) + "- archive: original section/embed needed\n")
    else:
        original.unlink()
    return True


class Workflow(ScratchBase):
    def vault(self, answers=SINGLE_AGENT):
        v = Path(self.scratch("workflow"))
        run_setup(str(v), answers)
        return v

    def test_setup_allowlist_and_fresh_manual_and_auto_vaults_agree(self):
        setup = (ROOT / ".agents/skills/brain-setup/SKILL.md").read_text()
        for rel in VAULT_FILES:
            self.assertIn("`" + rel + "`", setup)
        self.assertEqual(len(VAULT_FILES), 20)
        self.assertEqual(len(SKILL_FILES), 4)
        for answers in (TWO_AGENTS, SINGLE_AGENT):
            with self.subTest(approval=answers["approval"]):
                v = self.vault(answers)
                self.assertTrue((v / "TODO/.gitkeep").is_file())
                self.assertFalse((v / "Tasks").exists())
                self.assertFalse((v / "Completed tasks").exists())
                self.assertFalse((v / "scripts").exists())
                self.assertFalse((v / ".agents/skills/brain-setup").exists())
                task, _ = fields((v / "Templates/task.md").read_text())
                self.assertEqual(task["importance"].strip(), "normal")
                self.assertEqual(task["stage"].strip(), "backlog")

    def test_phase_then_importance_date_and_path_selection(self):
        items = [
            dict(path="TODO/2026-01-01-first.md",status="requested",importance="critical"),
            dict(path="Projects/a/specs/2026-01-02-build.md",status="ready",importance="critical"),
            dict(path="Projects/a/specs/2026-01-05-review.md",status="review",importance="low"),
            dict(path="TODO/2026-01-01-normal.md",status="requested",importance=""),
            dict(path="TODO/2026-01-02-high.md",status="requested",importance="high"),
            dict(path="TODO/2026-01-07-future.md",status="requested",importance="critical"),
            dict(path="TODO/2026-01-01-blocked.md",status="blocked",importance="critical"),
        ]
        self.assertEqual([i["status"] for i in select(items)][:3], ["review", "ready", "requested"])
        self.assertEqual([Path(i["path"]).stem for i in select(items)][-2:], ["2026-01-02-high", "2026-01-01-normal"])
        tie = [dict(path="TODO/2026-01-02-z.md",status="requested"),
               dict(path="TODO/2026-01-01-z.md",status="requested"),
               dict(path="TODO/2026-01-02-a.md",status="requested")]
        self.assertEqual([Path(i["path"]).stem for i in select(tie)], ["2026-01-01-z", "2026-01-02-a", "2026-01-02-z"])
        agents = (ROOT / "vault/AGENTS.md").read_text()
        self.assertIn("review, then ready build, then requested intake", agents)
        self.assertIn("filename date, then relative path", agents)

    def test_capture_to_acceptance_retains_latest_request_and_repairs_link(self):
        v = self.vault()
        task = "TODO/2026-01-05-export.md"
        spec = "Projects/recipe-box/specs/2026-01-05-export.md"
        body = "Export recipes.\n## Detail\nLatest context.\n<!-- keep this -->\nSee [[recipe-box]]."
        (v / task).write_text("---\ntype: task\nstatus: requested\nimportance: high\nstage: backlog\n---\n" + body)
        template = (v / "Templates/spec.md").read_text()
        self.assertIn("task_stage: in-progress", template)
        self.assertEqual(select([dict(path=task, status="requested", importance="high"),
                                 dict(path="TODO/2026-01-05-low.md", status="requested", importance="low")])[0]["path"], task)
        for status in ("proposed", "ready", "building", "review"):
            spec_text = template.replace("status: draft", "status: " + status).replace("task:\n", "task: " + task + "\n")
            (v / spec).parent.mkdir(parents=True, exist_ok=True)
            (v / spec).write_text(spec_text)
            (v / task).write_text("---\ntype: task\nstatus: specced\nstage: in-progress\nimportance: high\nspec: " + spec + "\nscope: synthetic export\n---\n" + body)
            self.assertTrue((v / task).exists(), status)
            self.assertIn("task_stage: in-progress", (v / spec).read_text())
        ref = v / "Inbox/link.md"
        ref.write_text("[request](" + task + ")")
        self.assertTrue(finish(v, task, spec, body, "high", [ref], context=("scope: synthetic export",)))
        self.assertFalse((v / task).exists())
        retained = (v / spec).read_text()
        self.assertIn("> ## Detail\n> Latest context.\n> <!-- keep this -->", retained)
        self.assertIn("> scope: synthetic export", retained)
        self.assertIn("importance: high", retained)
        self.assertIn("task_completed_at: 2026-01-06T12:00:00Z", retained)
        self.assertEqual(ref.read_text(), "[request](" + spec + ")")

    def test_approval_fixes_blocked_and_waiting_never_authorize_retirement(self):
        v = self.vault(TWO_AGENTS)
        task = "TODO/2026-01-05-pending.md"
        spec = "Projects/recipe-box/specs/2026-01-05-pending.md"
        for status in ("proposed", "draft", "ready", "blocked", "waiting"):
            with self.subTest(status=status):
                original = "---\ntype: task\nstatus: specced\nstage: in-progress\n---\nPending."
                (v / task).write_text(original)
                self.assertFalse(finish(v, task, spec, "Pending.", "normal", verdict=status))
                self.assertEqual((v / task).read_text(), original)
        self.assertFalse(finish(v, task, spec, "Pending.", "normal", verified=False))
        self.assertTrue((v / task).exists())
        for rel in ("vault/AGENTS.md", ".agents/skills/brain-review/SKILL.md"):
            text = (ROOT / rel).read_text()
            self.assertIn("retry_after" if rel.startswith("vault") else "never authorize deletion", text)
        board = (ROOT / "vault/Board.base").read_text()
        self.assertIn('!file.inFolder("Completed tasks")', board)
        self.assertNotIn("dispatch == true", board)
        self.assertIn('name: Lifecycle', board)
        done = board.split("name: Done", 1)[1].split("  - type:", 1)[0]
        self.assertIn('type == "spec"', done)

    def test_anchored_reference_archives_original_and_refuses_collision(self):
        v = self.vault()
        task = "TODO/2026-01-05-export.md"
        spec = "Projects/recipe-box/specs/2026-01-05-export.md"
        body = "Request\n## Detail\nKeep original meaning."
        (v / task).write_text(body)
        ref = v / "Inbox/link.md"
        ref.write_text("[details](" + task + "#Detail)")
        self.assertTrue(finish(v, task, spec, body, "normal", [ref]))
        archived = v / "Completed tasks/2026-01-05-export.md"
        self.assertTrue(archived.read_text().endswith(body))
        self.assertIn("Completed tasks/2026-01-05-export.md#Detail", ref.read_text())
        self.assertIn("archive: original section/embed needed", (v / spec).read_text())
        (v / task).write_text("Another request")
        ref.write_text("[details](" + task + "#Detail)")
        before = archived.read_text()
        self.assertFalse(finish(v, task, spec, "Another request", "normal", [ref]))
        self.assertEqual(archived.read_text(), before)
        self.assertTrue((v / task).exists())

    def test_readme_inventory_links_and_layout_fence(self):
        readme = (ROOT / "README.md").read_text()
        table = readme.split("## Skills\n", 1)[1].split("## Layout", 1)[0]
        links = re.findall(r"\[(brain-[a-z]+)\]\(([^)]+)\)", table)
        inventory = sorted(p.parent.name for p in (ROOT / ".agents/skills").glob("*/SKILL.md"))
        self.assertEqual(sorted(name for name, _ in links), inventory)
        self.assertEqual(len(links), len(inventory))
        for name, rel in links:
            self.assertTrue((ROOT / rel).is_file(), name)
        layout = readme.split("## Layout\n```text\n", 1)[1].split("```", 1)[0]
        self.assertIn("└── TODO/\n", layout)
        self.assertNotIn("Tasks/", layout)
        self.assertIn("## Prerequisites", readme.split("## Layout", 1)[1].split("```", 2)[2])
        self.assertIn("20 files", (ROOT / ".agents/skills/brain-setup/SKILL.md").read_text())
        rerun = (ROOT / ".agents/skills/brain-setup/SKILL.md").read_text().split("## 5. Rerun", 1)[1]
        self.assertIn("approved preview", rerun)
        self.assertIn("leave existing `Tasks/` notes untouched", rerun)
        self.assertIn("no Kanban plugin", (ROOT / "vault/AGENTS.md").read_text())


if __name__ == "__main__":
    unittest.main()
