#!/usr/bin/env python3
"""Check that a repository's tracked files are safe to publish.

Uses only the standard library and local git. Reports "path:line: rule" and
never prints the offending value. This is an aid, not proof that arbitrary
text contains no personal facts.

    python3 scripts/check_public.py                 # tracked files on disk
    python3 scripts/check_public.py --staged        # versions in the git index
    python3 scripts/check_public.py --denylist FILE # extra owner-specific terms
"""
import argparse
import os
import re
import subprocess
import sys

SKILLS = ("brain-setup", "brain-capture", "brain-spec", "brain-build", "brain-review")
TEMPLATES = ("project", "spec", "task", "decision", "knowledge", "source", "moc")
EMPTY_DIRS = ("Projects", "Decisions", "Knowledge/Sources", "MOCs", "Inbox", "Tasks")

ALLOWED_EXACT = {
    "README.md",
    ".gitignore",
    "docs/privacy.md",
    "scripts/check_public.py",
    "vault/AGENTS.md",
    "vault/CLAUDE.md",
    "vault/Home.md",
    "vault/Board.base",
}
ALLOWED_EXACT |= {f"vault/Identity/{n}.md" for n in ("user", "soul", "identity")}
ALLOWED_EXACT |= {f"vault/Templates/{n}.md" for n in TEMPLATES}
ALLOWED_EXACT |= {f"vault/{d}/.gitkeep" for d in EMPTY_DIRS}
ALLOWED_EXACT |= {f".agents/skills/{s}/SKILL.md" for s in SKILLS}
ALLOWED_PATTERNS = [re.compile(r"tests/test_[a-z0-9_]+\.py\Z")]

CONTENT_RULES = [
    ("home-path", re.compile(r"(?:/(?:home|Users)/[A-Za-z0-9._-]+|[A-Za-z]:\\Users\\[^\\\s]+)")),
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9.-]+")),
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    (
        "credential-assignment",
        re.compile(
            r"(?i)\b(?:api[_-]?key|secret|token|passw(?:or)?d|auth)\b[\"']?\s*[:=]\s*[\"']?"
            r"[A-Za-z0-9_\-/+=.]{8,}"
        ),
    ),
    (
        "credential-token",
        re.compile(r"\b(?:sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,})"),
    ),
]


def git(repo, *args):
    out = subprocess.run(
        ["git", "-C", repo, *args], check=True, capture_output=True
    )
    return out.stdout


def list_entries(repo, staged):
    """Return (mode, path) for every tracked (or staged) file."""
    raw = git(repo, "ls-files", "-s", "-z")
    entries = []
    for item in raw.split(b"\0"):
        if not item:
            continue
        meta, _, path = item.partition(b"\t")
        mode = meta.split()[0].decode()
        entries.append((mode, path.decode("utf-8", "surrogateescape")))
    return entries


def read_content(repo, path, staged):
    if staged:
        return git(repo, "show", ":" + path)
    with open(os.path.join(repo, path), "rb") as fh:
        return fh.read()


def path_allowed(path):
    return path in ALLOWED_EXACT or any(p.match(path) for p in ALLOWED_PATTERNS)


def load_denylist(path):
    if not path:
        return []
    with open(path, encoding="utf-8") as fh:
        terms = [ln.strip().lower() for ln in fh]
    return [t for t in terms if t and not t.startswith("#")]


def check(repo, staged=False, denylist=()):
    """Return a sorted list of (path, line, rule) violations."""
    violations = []
    for mode, path in list_entries(repo, staged):
        if mode == "120000":
            violations.append((path, 0, "symlink"))
            continue
        if not path_allowed(path):
            violations.append((path, 0, "path-not-allowed"))
            continue
        lowered_path = path.lower()
        if any(t in lowered_path for t in denylist):
            violations.append((path, 0, "denylist-path"))
        try:
            data = read_content(repo, path, staged)
        except (OSError, subprocess.CalledProcessError):
            violations.append((path, 0, "unreadable"))
            continue
        if b"\0" in data:
            violations.append((path, 0, "binary"))
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            violations.append((path, 0, "binary"))
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for rule, rx in CONTENT_RULES:
                if rx.search(line):
                    violations.append((path, lineno, rule))
            low = line.lower()
            if any(t in low for t in denylist):
                violations.append((path, lineno, "denylist"))
    return sorted(set(violations))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--staged", action="store_true", help="check index versions, not disk")
    ap.add_argument("--denylist", default=os.environ.get("BLUEPRINT_DENYLIST"),
                    help="file with one owner-specific term per line (keep it outside the repo)")
    ap.add_argument("--repo", default=None, help="repository root (default: this script's repo)")
    args = ap.parse_args(argv)
    repo = args.repo or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    violations = check(repo, args.staged, load_denylist(args.denylist))
    for path, line, rule in violations:
        print(f"{path}:{line}: {rule}")
    if violations:
        print(f"FAIL: {len(violations)} violation(s)")
        return 1
    print("OK: no violations (this is an aid, not proof of no personal facts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
