#!/usr/bin/env python3
"""Validate agent definitions against both runtimes' loader contracts.

Checks, for every agent in `agents/` (Stella) and `agents/cc-agents/`
(Claude Code):

  - frontmatter is present and parses under a strict YAML parser, which is
    what Claude Code uses (Stella's own parser is more forgiving, so passing
    only Stella is not enough for a shared body);
  - `name` is present, kebab-case, and equals the filename;
  - `description` is present and, for Stella, within its 80-character budget;
  - no unquoted ": " in a description — legal for Stella, a syntax error for
    strict YAML;
  - every named tool exists in the target runtime;
  - the body is non-empty and does not end mid-sentence.

Run from the repository root:

    python3 scripts/validate-agents.py

Exits non-zero if anything fails.
"""
from __future__ import annotations

import os
import re
import sys

# `stella tools` — the built-in toolbelt.
STELLA_TOOLS = {
    "bash", "delegate", "delete_file", "delete_state", "edit_file",
    "get_environment", "get_state", "list_state", "read_file", "save_state",
    "search", "task_assign", "task_cancel", "task_complete", "task_create",
    "task_list", "task_start", "write_file",
}
CC_TOOLS = {
    "Read", "Write", "Edit", "Bash", "Grep", "Glob", "Task", "WebSearch",
    "WebFetch", "TodoWrite", "NotebookEdit", "BashOutput", "KillShell",
}

try:
    import yaml
except ImportError:  # pragma: no cover - optional dependency
    yaml = None


def parse(raw: str):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not m:
        return None, None, "no YAML frontmatter"
    data = {}
    for line in m.group(1).split("\n"):
        km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if km:
            data[km.group(1)] = km.group(2).strip()
    return data, m.group(2), None


def check(directory: str, valid_tools: set[str], label: str, desc_limit: int):
    errors: list[str] = []
    rows = []
    files = sorted(f for f in os.listdir(directory) if f.endswith(".md"))

    for filename in files:
        path = os.path.join(directory, filename)
        raw = open(path, encoding="utf-8").read()
        data, body, err = parse(raw)
        if err:
            errors.append(f"{filename}: {err}")
            continue

        slug = filename[:-3]
        name = data.get("name", "")
        desc = data.get("description", "")

        # Any .md file in an agents directory is loaded as an agent, including
        # one with no frontmatter — so a stray README becomes a junk agent.
        if slug.lower() in {"readme", "index", "agents"}:
            errors.append(f"{filename}: docs must not live in an agents directory")

        if not name:
            errors.append(f"{filename}: missing name")
        elif name != slug:
            errors.append(f"{filename}: name '{name}' != filename '{slug}'")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
            errors.append(f"{filename}: filename is not kebab-case")
        if not desc:
            errors.append(f"{filename}: missing description")
        if len(desc) > desc_limit:
            errors.append(f"{filename}: description {len(desc)} chars > {desc_limit}")
        if ": " in desc and not desc[:1] in "\"'":
            errors.append(f"{filename}: unquoted ': ' in description breaks strict YAML")
        if not (body or "").strip():
            errors.append(f"{filename}: empty body")
        elif body.rstrip()[-1] not in ".!?`)]:":
            errors.append(f"{filename}: body may be truncated -> ...{body.rstrip()[-40:]!r}")

        if yaml is not None:
            fm = re.match(r"^---\n(.*?)\n---\n", raw, re.S)
            try:
                doc = yaml.safe_load(fm.group(1))
                if not isinstance(doc, dict):
                    errors.append(f"{filename}: frontmatter is not a mapping")
            except yaml.YAMLError as exc:
                errors.append(f"{filename}: strict YAML: {str(exc).splitlines()[0]}")

        granted: list[str] = []
        if data.get("tools"):
            granted = [t.strip().strip("[]\"'") for t in data["tools"].split(",")]
            granted = [t for t in granted if t]
            unknown = [t for t in granted if t not in valid_tools]
            if unknown:
                errors.append(f"{filename}: invalid {label} tools: {unknown}")

        rows.append((slug, len(desc), ", ".join(granted) or "ALL", len((body or "").split())))

    return files, rows, errors


def main() -> int:
    if not os.path.isdir("agents"):
        print("error: agents/ not found — run from the repository root", file=sys.stderr)
        return 1
    if yaml is None:
        print("note: PyYAML not installed — skipping strict-YAML checks\n")

    total = 0
    for directory, tools, label, limit in [
        ("agents", STELLA_TOOLS, "stella", 80),
        (os.path.join("agents", "cc-agents"), CC_TOOLS, "claude-code", 400),
    ]:
        if not os.path.isdir(directory):
            continue
        files, rows, errors = check(directory, tools, label, limit)
        print(f"=== {directory} — {len(files)} agents ===")
        for slug, desc_len, granted, words in rows:
            print(f"  {slug:<24} desc={desc_len:>3}  words={words:>4}  tools={granted}")
        if errors:
            total += len(errors)
            print(f"  !! {len(errors)} problem(s):")
            for e in errors:
                print(f"     - {e}")
        else:
            print("  OK — all valid")
        print()

    print(f"TOTAL PROBLEMS: {total}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
