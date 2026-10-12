# Privacy and the public/private boundary

This repository is a **public blueprint**: generic templates, skills and docs. Your own brain is a **private vault** created elsewhere by the `brain-setup` skill. The two must never mix.

## Rules
- The setup skill refuses any destination inside this checkout or its linked worktrees, and never writes answers here.
- Do not put your notes, names, project names, paths or credentials in this repository, even temporarily.
- Keep your private vault out of public remotes. If you version it with git, use a private remote.
- Agents in your vault follow `AGENTS.md`: no secrets in notes, and actions beyond local note edits need your approval.

## What is tracked
Only the files listed in `scripts/check_public.py` (`ALLOWED_EXACT` and the test pattern): the README, this document, the checker, tests, `.gitignore`, the generic `vault/` skeleton, and the five skills under `.agents/skills/`. Anything else fails the check. `.gitignore` is only secondary protection (caches, `.env*`, editor state).

## The checker
```
python3 scripts/check_public.py                  # tracked files as on disk
python3 scripts/check_public.py --staged         # versions in the git index
python3 scripts/check_public.py --denylist FILE  # plus your own terms
python3 -m unittest discover -s tests            # offline tests
```
It uses only the standard library and local git. It enumerates tracked (or staged) files, requires each to be on the allowed path list, and refuses symlinks and binary files. It reports `path:line: rule` and never prints the matched value. Rules: home-directory paths, email addresses, private-key headers, credential assignments and common token formats, and denylist terms.

The **denylist** is a plain text file, one term per line (`#` comments allowed), matched case-insensitively against file names and lines. Put your own name, handles, employer, project names and device names in it. **Keep it outside the repository and never commit it.** Pass it with `--denylist` or the `BLUEPRINT_DENYLIST` environment variable.

The checker is an aid. It cannot prove that free text contains no personal facts; read the diff before publishing.

## Before publishing: contents and history
A clean working tree does not make a repository safe to publish. Every reachable commit carries its tree **and** its author and committer name/email. Before making any copy public:

1. Run the checker on disk and with `--staged`, with your denylist.
2. Audit history: for every commit (`git rev-list --all`), check its tree against the allowlist and the checker rules, and check author/committer metadata (`git log --all --format='%an %ae %cn %ce'`) for anything that identifies you or your machine.
3. Do not rewrite shared history or change your global git identity to fix this.

### Clean-export procedure (when history or metadata is identifying)
Publish a fresh repository built from the reviewed tree instead of the inherited history:

```
git clone --no-hardlinks <this-checkout> export-src       # or use the reviewed branch checkout
mkdir blueprint-public && git -C export-src archive HEAD | tar -x -C blueprint-public
cd blueprint-public
git init -q -b main
git config user.name  "<public commit name you choose>"    # repository-local only
git config user.email "<public commit email you choose>"
python3 scripts/check_public.py --denylist <your-denylist>
python3 -m unittest discover -s tests
git add -A && git commit -m "Initial public release"
python3 scripts/check_public.py --staged --denylist <your-denylist>
git log --all --format='%an %ae %cn %ce'                   # confirm only the public identity appears
```
Only then add a remote and push, deliberately and by hand. `git archive` exports tracked files only and no history, hooks or local configuration. Review the exported tree once more before pushing; also check the hosting account's default commit-email privacy setting.
