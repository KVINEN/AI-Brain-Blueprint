---
name: brain-review
description: Architect role. Review a built spec against its acceptance criteria and the branch diff, then pass it or send it back. Use when the owner asks to review a build or a spec branch.
---
# brain-review

All vault paths are relative to the vault root (the folder containing `AGENTS.md`). If one agent built the spec, review it in a fresh session or as an explicit separate step, judging the result as if someone else wrote it.

1. Pick the spec the owner named, otherwise the oldest `status: review` spec in `Projects/*/specs/`.
2. Read the spec (criteria, build log). The project note names the code repository; read the diff with `git -C <repo> diff <base>...spec/<slug>`.
3. Judge against the **spec**, not taste. Check every acceptance criterion, then look for correctness bugs, security issues and over-engineering (code beyond the spec counts as a defect).
4. Run the verification yourself where it is cheap (lint, typecheck, tests).
5. Append `## Review` with today's date, a verdict (`pass` or `changes requested`) and specific findings (`file:line`, what is wrong, why). Increment `round` by one.
   - **pass**: set `status: done`. Tell the owner the branch is ready to merge. Do not merge it.
   - **changes requested**: add the fixes as new unticked tasks and set `status: ready`, so the builder can pick it up again. After 3 rounds without a pass, set `status: blocked` with a one-line `blocked_reason` and let the owner decide.
6. Patterns worth remembering go through `brain-capture`.
