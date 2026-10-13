---
name: brain-review
description: Architect role. Review a built spec against its acceptance criteria and the branch diff, then pass it or send it back. Use when the owner asks to review a build or a spec branch.
---
# brain-review

All vault paths are relative to the vault root (the folder containing `AGENTS.md`). If one agent built the spec, review it in a fresh session or as an explicit separate step, judging the result as if someone else wrote it.

1. Pick the spec the owner named, otherwise select `status: review` specs by importance (`critical`, `high`, `normal`, `low`, missing/blank means normal), filename date and path in `Projects/*/specs/`.
2. Read the spec (criteria, build log). The project note names the code repository; read the diff with `git -C <repo> diff <base>...spec/<slug>`, where `<base>` is the spec's `base:` field recorded by the builder. If `base:` is empty (older spec), ask the owner which branch the work started from rather than guessing.
3. Judge against the **spec**, not taste. Check every acceptance criterion, then look for correctness bugs, security issues and over-engineering (code beyond the spec counts as a defect).
4. Finish every required verification check and review the exact committed HEAD, requiring it to remain unchanged with a clean worktree. Before recording a pass, validate any live request association and ensure its latest body/custom context can be retained; an invalid association is a blocker. Missing verification is a blocker, not a passing verdict. Record the command/error and concrete next action; do not weaken checks.
5. Append `## Review` with today's date, a verdict (`pass` or `changes requested`) and specific findings (`file:line`, what is wrong, why). Increment `round` by one.
   - **pass**: set `status: done`, `task_stage: done` and `task_completed_at` to the actual UTC review completion time. Follow completion bookkeeping below. Tell the owner the branch is ready to merge. Do not merge it.
   - **changes requested**: add the fixes as new unticked tasks and set `status: ready`, so the builder can pick it up again. After 3 rounds without a pass, set `status: blocked` with a one-line `blocked_reason` and let the owner decide.
6. For a task-backed pass, read the live task through its reciprocal `task:`/`spec:` pointers and verify the project/date/slug identity. Before marking or removing it, quote its latest exact body and custom context fields under `## Original task`; preserve headings/comments/links as literal provenance. Copy importance (missing/blank means normal); append dated observations and real completion under `## Dispatch history`. Keep this snapshot exact. Mark the task `status: done`, `stage: done` only after checking that retention is complete.
7. Prefer removing the completed task once working ordinary links are repaired to the spec with their labels intact, keeping the historical source pointer in `task:`. If an anchor/embed needs the original or context cannot transfer safely, archive its unchanged body with done metadata in `Completed tasks/` (create on demand), retarget the working links and `task:`, and record why. Never overwrite a collision. Leave code examples and retained provenance unchanged. If a link cannot be repaired safely, keep the task and report it. Proposed/draft, blocked/waiting, interrupted/failed verification and fixes never authorize deletion, even when a spec exists.
8. For changes requested, keep `task_stage: in-progress`, preserve the request and live task, and clear any obsolete completion timestamp; the manual user chooses the next fix build. Waiting/blocked work keeps its previous lifecycle stage. Record a concrete next action.
9. Patterns worth remembering go through `brain-capture`.
