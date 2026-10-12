---
name: brain-capture
description: Save something worth remembering into the vault, filed as a decision, knowledge note, project update or inbox item. Use when the owner says remember, note, capture, save this or log this, or when you learn a lesson, gotcha or decision that future sessions should know.
---
# brain-capture

All paths are relative to the vault root (the folder containing `AGENTS.md`).

1. Read `AGENTS.md` and `Identity/soul.md` if you have not this session. Decide where the item belongs:

   | It is… | Goes to |
   |---|---|
   | A choice between options, with reasons | `Decisions/YYYY-MM-DD-<slug>.md` (template `Templates/decision.md`) |
   | A concept, pattern or gotcha reusable across projects | `Knowledge/<Concept Name>.md` (template `Templates/knowledge.md`) |
   | A status change or fact about one project | that project note, under the right heading |
   | A request for work | `Tasks/YYYY-MM-DD-<slug>.md` (template `Templates/task.md`) |
   | Unclear or half-formed | `Inbox/YYYY-MM-DD-<slug>.md`, a few lines |

2. **Search first** (for example `grep -ril "<term>" . --include=*.md`). Extend an existing note instead of creating a near-duplicate.
3. Knowledge notes teach: explain the idea so the owner understands it a year from now without context. Lead with a one-line summary, add gotchas and "Seen in" links.
4. Add `[[links]]` to the project, related concepts and sources, and a backlink from the project note's Decisions or Lessons list.
5. Never capture secrets (keys, tokens, passwords) or anything the owner listed under "Stays outside the vault" in `Identity/user.md`. If the item contains such content, store a pointer to where it lives instead.
6. If the vault is under git, leave committing to the owner unless they asked you to commit. Confirm in one line with the file path.
