# AI brain blueprint

A small, generic starting point for an **AI second brain**: a folder of plain markdown notes that you and your AI coding agents share, plus a few instruction files ("skills") that define how work moves from an idea to reviewed code.

You get a template vault and an interactive setup skill that creates **your own private vault** from it. This repository holds nothing personal and should stay that way (see [docs/privacy.md](docs/privacy.md)).

## What "AI OS" means here
"AI OS" or "command center" is a workflow metaphor, not software. The vault is shared memory; the skills are routines; the spec loop is the scheduler. Notes live in git-friendly markdown, so a vault under git can carry durable context between sessions and machines. Agents do **not** read it by themselves: every session must be told to (the vault's `AGENTS.md` says what to read first).

## Who it helps
People who work with one or two coding agents across several projects and want decisions, lessons and specs to outlast any single chat.

## The lifecycle: capture → spec → build → review
A fictional example, project "recipe-box":

1. **Capture.** You tell the agent: "capture a request: add a shopping-list export to recipe-box". `brain-capture` writes `Tasks/2026-01-05-shopping-export.md` (`status: requested`).
2. **Spec.** The architect agent runs `brain-spec`. It reads the project note, inspects the code repository the note points to, and writes `Projects/recipe-box/specs/2026-01-05-shopping-export.md` with goal, approach and checkable acceptance criteria. With **manual** approval it sets `status: proposed` and stops; you read the spec and change it to `ready`. (With `auto` approval it writes `ready` itself.)
3. **Build.** The builder runs `brain-build`: it claims the spec (`building`, its name, `branch: spec/shopping-export`) before coding, works on that branch in the code repository, ticks tasks, verifies the criteria, appends to `## Build log` and sets `review`.
4. **Review.** The architect runs `brain-review` against the spec and the branch diff. `pass` sets `done`; `changes requested` adds tasks and sets `ready` again (at most 3 rounds).
5. **Merge.** Only you merge `spec/shopping-export`. No agent merges, pushes to shared branches or enables services.

One agent can do both jobs. Keep the steps separate: write and approve the spec first, build second, review as a fresh step.

## Layout
```text
README.md                    # public repo tooling
docs/
└── privacy.md               # public repo tooling
scripts/
└── check_public.py          # public repo tooling
tests/                       # public repo tooling
.agents/skills/
├── brain-setup/             # onboarding interview (this repo only)
├── brain-capture/           # copied into your vault
├── brain-spec/              # copied into your vault
├── brain-build/             # copied into your vault
└── brain-review/            # copied into your vault
vault/                       # generic skeleton that setup copies
├── AGENTS.md
├── CLAUDE.md
├── Home.md
├── Board.base
├── Identity/
│   ├── user.md
│   ├── soul.md
│   └── identity.md
├── Templates/
│   ├── project.md
│   ├── spec.md
│   ├── task.md
│   ├── decision.md
│   ├── knowledge.md
│   ├── source.md
│   └── moc.md
├── Projects/
├── Decisions/
├── Knowledge/
│   └── Sources/
├── MOCs/
├── Inbox/
└── Tasks/
```

## Prerequisites
- A coding agent that can read local files and follow written instructions (one is enough; two give a separate architect and builder).
- `git` and `python3` (the checker and tests use only the standard library).
- Optional: [Obsidian](https://obsidian.md) to browse notes and `Board.base`; a **private** git remote if you want your vault on several machines.

## Quickstart
1. Clone or download this repository.
2. Open it in your agent and say: **"Read `.agents/skills/brain-setup/SKILL.md` and run it."** This works without any global skill installation.
3. Answer the interview in short batches; skip anything optional. Pick a vault location **outside** this checkout.
4. Review the summary the skill shows (which answer lands in which file). Confirm, and the skill creates the vault.
5. Open the new vault in your agent and say: "Read `AGENTS.md`, then capture my first request."

Setup refuses destinations inside this checkout (or its worktrees), through symlinks, or in a non-empty folder. Re-running it on an existing vault only previews changes; it never silently overwrites. Setup does not create remotes, install tools, write outside the vault, enable services or touch global agent configuration.

## Using the vault
- **Each session:** tell the agent to read `AGENTS.md` and the three `Identity/` notes. The vault's `CLAUDE.md` simply imports `AGENTS.md` for tools that look for that name.
- **Skills** are plain instruction files in `<vault>/.agents/skills/<name>/SKILL.md`. Some clients discover them automatically; this blueprint does not promise that. Otherwise say "read `.agents/skills/brain-spec/SKILL.md` and follow it".
- **Board:** `Board.base` (Obsidian Bases) lists specs by status and open tasks.
- **Spec statuses:** `draft` (open question), `proposed` (awaiting your approval), `ready`, `building`, `review`, `done`, `blocked` (needs you; `blocked_reason` says why).
- No sync tooling is included. If you version your vault with git, commit when you like.

## Optional tooling (you do these yourself)
- **Git:** `git init` in the vault; add a private remote only if you want one.
- **Obsidian:** open the vault folder; templates in `Templates/` can be used with its Templates or Templater plugin (`{{date:YYYY-MM-DD}}` placeholders).
- **Automation:** unattended dispatch, sync scripts and global skill installation are not part of this release.

## Before you publish a fork
Both the **contents and the history** need review: a clean working tree does not make inherited commits safe. Run `python3 scripts/check_public.py`, its `--staged` mode and the tests, then follow the clean-export procedure in [docs/privacy.md](docs/privacy.md).
