# Brain: rules for every agent

This vault is a personal second brain: plain markdown that you and your AI agents read and write. It is a workflow, not a program. Agents only know what they are told to read, so start every session with the steps below.

> Status: **unconfigured**. Run the `brain-setup` skill to replace the placeholders in `Identity/` and in this file's Configuration section.

## Configuration

- Language for notes: English
- Roles: architect = _unconfigured_, builder = _unconfigured_ (one agent may hold both)
- Spec approval: _unconfigured_ (`manual`: a human moves `proposed` to `ready`; `auto`: the architect writes `ready`)
- Merge policy: a human merges. No agent merges, pushes to a shared branch or publishes.
- Actions beyond local note edits (network, installs, services): ask first.
- Keep out of notes: secrets, credentials, anything the owner listed in `Identity/user.md` under "Stays outside the vault".

## Before you do anything

1. Read `Identity/user.md` (who the owner is), `Identity/soul.md` (how to talk to them) and `Identity/identity.md` (your role).
2. For project work, read `Projects/<project>/<project>.md` first. It names the code repository and its location.
3. If the vault is under git, check `git status` first. Syncing is optional and manual in this blueprint.

## Roles

| Role | Does | Writes |
|---|---|---|
| **Architect** | Plans, writes specs, reviews builds, records decisions | spec bodies, `## Review` sections, `Decisions/` |
| **Builder** | Implements specs in the code repository | `## Build log` sections, spec `status`/`builder`/`branch` fields |
| Either | Learner/curator | `Knowledge/`, `Inbox/`, project notes, `MOCs/` |

Roles are configurable. With one agent, that agent does both jobs but still follows the loop below: write the spec, claim it, build, then review it as a separate step.

## The spec loop

```
request ─► proposed ─► ready ─► building ─► review ─┬─► done
(task or   (human      (architect  (builder)  (architect) │
 inbox)     approves)   or human)                  ▲      │
                                                   └ changes requested (back to ready)
```

- Specs live in `Projects/<project>/specs/YYYY-MM-DD-<slug>.md` (template: `Templates/spec.md`).
- **Approval:** with `manual` approval the architect stops at `proposed`; only the human sets `ready`. With `auto` the architect may write `ready` directly.
- **Claiming:** the builder sets `status: building`, `builder: <agent>`, `branch: spec/<slug>` *before* writing code. Never take a spec that is already `building`.
- Build on a branch `spec/<slug>` in the code repository (use a git worktree if another agent works there too).
- **Never merge.** When a review passes, the spec becomes `done` and the human merges the branch.
- `draft` means an agent has a question under `## Questions`; `blocked` means it cannot continue (give `blocked_reason`).
- `Board.base` lists specs and tasks by status.

## Writing rules

- **Stay in your sections.** Do not rewrite another agent's spec body, build log or review. Append below it or add a note under `## Questions`.
- **Frontmatter is the API.** Every note has a `type` (`project | spec | task | decision | knowledge | source | moc`). Keep the fields from `Templates/`.
- **Link generously** with `[[wikilinks]]`. A concept mentioned twice deserves a `Knowledge/` note.
- **Don't delete.** Superseded decisions get `status: superseded` and a link to the replacement.
- **Concise, no filler.** Notes are for the future owner and future agents: what, why, and where it lives.
- **No secrets.** No API keys, tokens, passwords or `.env` contents. Ever.
- **Sources stay where they are.** Keep large files outside the vault; a `Knowledge/Sources/` note holds the distilled summary and points to the file.

## Skills (in `.agents/skills/`)

| Skill | Role | Does |
|---|---|---|
| `brain-capture` | either | File a decision, lesson or idea in the right place |
| `brain-spec` | architect | Turn a request into a spec |
| `brain-build` | builder | Claim a ready spec, implement it, write the build log |
| `brain-review` | architect | Check a build against its acceptance criteria |

Skills are plain instruction files. If your agent does not discover them automatically, tell it to read `.agents/skills/<name>/SKILL.md` and follow it.

## Layout

```
Identity/      who the owner is, how to talk, agent roles
Home.md        start page
Board.base     board of specs and tasks (Obsidian Bases view)
Projects/<p>/  <p>.md project note + specs/
Decisions/     YYYY-MM-DD-<slug>.md
Knowledge/     reusable concepts; Sources/ holds distilled source notes
MOCs/          maps of content, once a topic exceeds ~8 notes
Inbox/         quick captures
Tasks/         manual requests (status: requested)
Templates/     note templates
```
