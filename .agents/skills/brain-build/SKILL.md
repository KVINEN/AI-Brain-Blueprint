---
name: brain-build
description: Builder role. Claim a ready spec from the vault, implement it in the project's code repository on a spec branch, and write the build log. Use when the owner says build, implement, pick up or work on a spec.
---
# brain-build

All vault paths are relative to the vault root (the folder containing `AGENTS.md`).

1. Read `AGENTS.md`, `Identity/soul.md` and `Identity/identity.md`.
2. **Pick a spec**: the one the owner named, otherwise the oldest `status: ready` spec in `Projects/*/specs/`. Never pick one that is `building` or `proposed`.
3. **Claim it before coding**: set `status: building`, `builder: <your agent name>`, `branch: spec/<slug>`, `updated: <today>`.
4. Read the project note; it names the code repository. Read that repository's own agent instructions. In the repository, create branch `spec/<slug>` (use `git worktree add ../<repo>-<slug> -b spec/<slug>` if another agent works in the same checkout).
5. Implement the **smallest change that satisfies the acceptance criteria**. Tick tasks in the spec as you go. If the spec is wrong or ambiguous, write the problem under `## Questions`, set `status: draft` and stop. Do not improvise the design.
6. Verify each acceptance criterion (lint, typecheck, tests or running the app). Commit in the code repository.
7. Append to `## Build log`: what changed (files, commits), how each criterion was verified, surprises, and a one-line "why" for each non-obvious choice. Do not edit the spec body, other agents' sections or `## Review`.
8. Set `status: review`. Tell the owner the branch is ready for review.

Never merge the branch, push to a shared branch, or enable services. The owner merges after a passing review. Lessons that apply beyond this project go through `brain-capture`.

## Fix rounds
If the architect sent the spec back (`status: ready` with new unticked tasks from `## Review`), claim it again, do only those tasks, increment nothing yourself (`round` belongs to the reviewer), and start the build-log entry with "Round N fixes".
