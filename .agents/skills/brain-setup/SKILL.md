---
name: brain-setup
description: First-run onboarding for the AI brain blueprint. Interviews the user in short batches and, after confirmation, creates their private vault outside this public checkout. Use when the user asks to set up their brain, run brain-setup, or onboard.
---
# brain-setup

You turn this public blueprint into the user's **private** vault. The blueprint is shared; the user's answers are not.

## Hard rules
- **Never write answers, transcripts, names, paths or examples derived from them into this checkout** (or any linked worktree). The only writes are to the confirmed private destination.
- **Never ask for or store secrets**: passwords, tokens, API keys, SSH keys, hostnames, account identifiers, legal identity, addresses, phone numbers or emails. If the user volunteers one, do not repeat it; tell them it will not be stored.
- **Never inspect the user's project repositories** during onboarding. Record only the path they give you.
- Do not create git remotes, install tools, write outside the destination, enable timers/services, or touch global agent configuration. Explain optional steps instead (see "After setup").
- Write nothing until the user has confirmed the summary (step 3).

## 1. Interview
Ask in short batches (2–3 questions at a time). Every question except the destination may be skipped; a skipped answer becomes the explicit text `_unconfigured_` in the vault. Offer the stated default when there is one. Ask only what is needed to configure the vault.

1. **About you:** preferred name or alias; broad role or background; goals for the next 3–6 months. Do not ask for legal identity or contact details.
2. **Projects:** active projects, one line on the purpose of each, and optionally the local path of each code repository.
3. **Communication:** preferred tone, explanation depth, things agents should avoid, and note language (default English).
4. **Agents and roles:** which agents they use, who is architect and who is builder, or "single agent does both". Approval before a spec becomes ready: `manual` (default, a human moves `proposed` to `ready`) or `auto`. The merge policy is fixed: a human merges.
5. **Vault and tooling:** private vault destination (required), editor or Obsidian preference, one or several machines, and local-only versus optional private git. Ask for OS only if they want help with tooling steps; skip it otherwise. No hostnames, credentials, keys or account identifiers.
6. **Boundaries:** what belongs in notes, what must stay elsewhere (this becomes "Stays outside the vault"), and whether agent actions beyond local note edits (network, installs, services) need approval (default: yes, always ask).

## 2. Validate the destination
Resolve with symlinks followed (for example `realpath -m`). Apply every check to the resolved path; stop and ask for a different destination on any failure.

1. Get the checkout root with `git rev-parse --show-toplevel`, and every linked worktree with `git worktree list --porcelain`; resolve each too.
2. **Reject** the destination if it equals, contains or is inside the checkout or any linked worktree (compare resolved paths; also reject when any existing parent component is a symlink resolving into one of them).
3. **Reject** a destination that exists and is a file, or exists and is not empty. The one exception is a rerun (section 5): the destination holds an earlier vault of this blueprint (`AGENTS.md` plus `.agents/skills/brain-spec/SKILL.md`).
4. **Reject** a destination that overlaps another git repository's working tree unless the user explicitly confirms it is their intended private vault repository and it is empty.
5. An absent destination is created only after confirmation. Create parent directories only if the user agreed.

## 3. Confirm before writing
Show a summary table: each answer on the left, the file and section it lands in on the right (mapping below), the resolved destination, and the list of files to be created. State that nothing is written to this checkout. Ask for explicit confirmation ("yes, create it"). Anything else means revise or stop.

## 4. Write the vault
Copy **only these exact files** from the checkout into the destination (create parent directories as needed), then fill them in. Do not copy directories recursively and do not glob: anything not listed here is never copied, even if it sits in the same folder.

From `vault/` to the destination root (20 files):
- `AGENTS.md`, `CLAUDE.md`, `Home.md`, `Board.base`
- `Identity/user.md`, `Identity/soul.md`, `Identity/identity.md`
- `Templates/project.md`, `Templates/spec.md`, `Templates/task.md`, `Templates/decision.md`, `Templates/knowledge.md`, `Templates/source.md`, `Templates/moc.md`
- `Projects/.gitkeep`, `Decisions/.gitkeep`, `Knowledge/Sources/.gitkeep`, `MOCs/.gitkeep`, `Inbox/.gitkeep`, `TODO/.gitkeep`

From `.agents/skills/` to `<destination>/.agents/skills/` (4 files): `brain-capture/SKILL.md`, `brain-spec/SKILL.md`, `brain-build/SKILL.md`, `brain-review/SKILL.md`.

Before copying, check each source with a no-follow test (for example `test -f F && ! test -L F`, and that no parent directory below the checkout root is a symlink). If a source is missing, is not a regular file or is a symlink, stop and report it; do not substitute. Copy file contents only, never links. Afterwards the destination must contain exactly the files above plus the notes you generate (project notes and their `specs/.gitkeep`); list any other file found there and ask before leaving it.

Never copy `.git`, logs, caches, `.env*`, editor workspace state, `tests/`, `scripts/`, `docs/`, `brain-setup` itself, or any untracked or extra file that happens to sit under `vault/` or the skill directories.

### Answer-to-file mapping
| Answer | File | Where |
|---|---|---|
| Name/alias, role, goals | `Identity/user.md` | the three fields at the top |
| Things to stay outside the vault | `Identity/user.md` | "Stays outside the vault" (plus the "no secrets" rule) |
| Tone, depth, avoid, language | `Identity/soul.md` | matching bullets |
| Agents, architect, builder | `Identity/identity.md` and `AGENTS.md` | "Agents in use", "Architect", "Builder"; `AGENTS.md` Configuration → Roles |
| Single-agent choice | both files above | architect = builder = that agent; keep the separate-steps note |
| Approval preference | `Identity/identity.md` and `AGENTS.md` | "Spec approval" / Configuration → Spec approval |
| Merge policy | `AGENTS.md` | Configuration → Merge policy: a human merges (not configurable) |
| Action approval | `Identity/identity.md` and `AGENTS.md` | "Actions needing approval" / Configuration |
| Note language | `AGENTS.md` and `Identity/soul.md` | Configuration → Language; add "Write notes in <language>" |
| Projects | `Projects/<slug>/<slug>.md` + `Projects/<slug>/specs/.gitkeep` | from `Templates/project.md`: What/Why from the purpose, `repo:` and **Repo:** from the path (else leave `repo:` empty and write "none yet") |
| Project list | `Home.md` | one `[[<slug>]]` bullet per project under Projects, replacing the `_None yet._` bullet (keep it when no project was given) |
| Editor, machines, git preference | `Home.md` | a short "Setup choices" section (editor, local-only or private git) with no machine names |

Then in the destination: replace every line starting `> Status: **unconfigured**` (in `AGENTS.md`, `Home.md` and the `Identity/` notes) with `Status: configured by brain-setup`; skipped fields keep `_unconfigured_`. If the single agent plays both roles, say so in `AGENTS.md` Roles. Do not add a transcript of the interview anywhere, and do not store the destination path inside the vault.

Finish by listing the files created and the next step: open the new vault in an agent and say "read AGENTS.md, then capture my first request".

## 5. Rerun
If the destination already holds an earlier vault: do **not** overwrite anything silently. Re-ask only what the user wants to change, then show a preview of exactly which lines or files would change (old → new) plus new files to add. Apply only the approved changes; never touch notes under `Projects/*/specs/`, `Decisions/`, `Knowledge/`, `Inbox/` or `TODO/`, legacy `Tasks/` or `Completed tasks/` beyond adding a requested new project note. If a project note already exists, show a diff and ask per file.

### Legacy queue migration (separate approved preview)
Fresh vaults have `TODO/`, not `Tasks/`. On a rerun, leave existing `Tasks/` notes untouched. Offer a separate preview only if the user requests migration: list each source/destination, reciprocal `task:`/`spec:` pointers and working links that need updating. Preserve every unfinished body, status, importance, retry field and review history. Reject duplicate destinations or ambiguous identities without overwriting. Never classify a task as completed merely because it has a spec, and never retire tasks during setup. Apply a migration only after explicit approval of that concrete preview; otherwise keep the legacy requests visible on the board. Do not create a fresh `Completed tasks/` placeholder; the reviewer creates it only for an actual archive fallback.

## After setup (the user does these, you only explain)
- **Git (optional):** `git init` inside the vault, commit, and add a *private* remote only if wanted. Keep it private; never push a vault to a public remote.
- **Obsidian (optional):** open the vault folder as a vault; `Board.base` offers lifecycle and importance tables plus spec status/project views; no Kanban plugin is required.
- **Skills:** the skills are plain files in `<vault>/.agents/skills/`. If an agent does not pick them up on its own, tell it to read `.agents/skills/<name>/SKILL.md` and follow it. How a given client discovers skills varies and is not guaranteed.
