---
name: brain-build
description: Builder role. Claim a ready spec from the vault, implement it in the project's code repository on a spec branch, and write the build log. Use when the owner says build, implement, pick up or work on a spec.
---
# brain-build

All vault paths are relative to the vault root (the folder containing `AGENTS.md`).

1. Read `AGENTS.md`, `Identity/soul.md` and `Identity/identity.md`.
2. **Pick a spec**: the one the owner named, otherwise the oldest `status: ready` spec in `Projects/*/specs/`. Never pick one that is `building` or `proposed`.
3. **Claim it before coding**: set `status: building`, `builder: <your agent name>`, `branch: spec/<slug>`, `updated: <today>`. If `base:` is empty, also set it to the branch you will build from (usually `main`; read it with `git -C <repo> branch --show-current`). Never change a `base:` that is already set.
4. Read the project note; it names the code repository. Read that repository's own agent instructions. In the repository, create branch `spec/<slug>` from `base` with `git switch -c spec/<slug> <base>`, or use `git worktree add ../<repo>-<slug> -b spec/<slug> <base>` if another agent works in the same checkout. On a fix round the branch already exists: do not create it again, see "Fix rounds".
5. Implement the **smallest change that satisfies the acceptance criteria**. Tick tasks in the spec as you go. If the spec is wrong or ambiguous, write the problem under `## Questions`, set `status: draft` and stop. Do not improvise the design.
6. Verify each acceptance criterion (lint, typecheck, tests or running the app). Commit in the code repository.
7. Append to `## Build log`: what changed (files, commits), how each criterion was verified, surprises, and a one-line "why" for each non-obvious choice. Do not edit the spec body, other agents' sections or `## Review`.
8. Set `status: review`. Tell the owner the branch is ready for review.

Never merge the branch, push to a shared branch, or enable services. The owner merges after a passing review. Lessons that apply beyond this project go through `brain-capture`.

## Fix rounds
If the architect sent the spec back (`status: ready` with new unticked tasks from `## Review`), claim it again (step 3, keeping `base:`), then reuse the existing branch: `git switch spec/<slug>`, or, if a worktree for it already exists (`git worktree list`), work in that worktree; if the branch exists but has no worktree, `git worktree add ../<repo>-<slug> spec/<slug>` (no `-b`). Add new commits on top; do not recreate or reset the branch. Do only the new unticked tasks, increment nothing yourself (`round` belongs to the reviewer), and start the build-log entry with "Round N fixes".
