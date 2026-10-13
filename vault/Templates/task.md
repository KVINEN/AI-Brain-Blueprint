---
type: task
project: "[[<project>]]"
status: requested
importance: normal
stage: backlog
created: {{date:YYYY-MM-DD}}
---
What you want done, in plain words. The architect turns it into a spec; the builder implements it; the architect reviews it.

Save in `TODO/YYYY-MM-DD-<slug>.md`. These are manual requests: nothing picks them up automatically. Importance is `critical`, `high`, `normal` (default) or `low`. Missing/blank importance means normal. Stage is `backlog` until a real next reservation (`next`) or specification starts (`in-progress`).

Ask the architect to run `brain-spec` on this note. Once the spec exists, set `status: specced` and `spec: <path>`; the spec represents the unfinished request on the board. Keep unresolved work, including blocked/waiting work. Only a completed passing review permits retention and removal or archive; follow `brain-review`.
