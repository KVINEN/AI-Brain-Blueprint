---
name: brain-spec
description: Architect role. Turn an idea or task note into a spec the builder can implement, stopping at proposed or ready depending on the approval setting. Use when the owner wants to plan, design or spec a feature, refactor or experiment for one of their projects.
---
# brain-spec

All paths are relative to the vault root (the folder containing `AGENTS.md`). The architect role is configurable (see `Identity/identity.md`); a single agent may play architect and builder, but must do them as separate steps.

1. Read `AGENTS.md`, `Identity/soul.md`, `Identity/identity.md` and `Projects/<project>/<project>.md`. The project note names the code repository; resolve it from there.
2. Investigate before designing: read the relevant code in that repository and any linked `Decisions/`. Do not spec against code you have not looked at.
3. **Challenge the idea first.** If it is over-scoped, premature or conflicts with an earlier decision, say so and propose the smaller version. Ask the owner only questions the code cannot answer (at most 3).
4. Write `Projects/<project>/specs/YYYY-MM-DD-<slug>.md` from `Templates/spec.md`:
   - Goal, Context (links), Approach (including what is out of scope).
   - Acceptance criteria the builder can verify (commands, behaviours), not vibes.
   - Tasks small enough for one build session. With more than about 8 tasks, split the spec.
   - `architect:` set to your agent name.
5. If the design makes a real architectural choice, also write a `Decisions/` note and link it.
6. Set the status from the approval setting in `Identity/identity.md`:
   - `manual`: `status: proposed`. **Stop.** Show the owner the spec; only the owner moves it to `ready`.
   - `auto`: `status: ready`.
   - Open questions remain: `status: draft`, with the questions under `## Questions`.
7. If the spec came from a `TODO/` note, set that task to `status: specced` and add `spec: <path>`.
   - Keep the task's `stage: in-progress` from specification start; set reciprocal `task: <path>`, `importance` (default normal), `task_stage: in-progress`, and `round: 0` on the spec. Quote the task's full latest body and custom context under `## Original task`; record initial observed importance with a UTC date under `## Dispatch history`. Keep this request snapshot exact, including headings/comments/links.
   - Leave proposed/draft/blocked work unfinished and visible. A specced task is represented by its spec in Lifecycle; do not remove it.
8. When selecting unspecified work, use review → ready build → requested intake, then importance (`critical`, `high`, `normal`, `low`), filename date and relative path. A future-dated intake waits until its UTC date; never interrupt a claim to change priority.
9. Reply with the spec path and a three-line summary. For `proposed`, say what the owner must do to approve it (set `status: ready`).
