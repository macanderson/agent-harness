# Agents

Agent definitions for [Stella](https://github.com/macanderson/stella), generated
into a Claude Code–compatible set alongside them.

- `agents/*.md` — **canonical.** Stella format. Edit these.
- `agents/cc-agents/*.md` — **generated.** Claude Code format. Do not edit.

Regenerate after any change:

```sh
python3 scripts/build-cc-agents.py
```

`cc-agents/` intentionally contains no `AGENT.md`. Stella's loader treats a
subdirectory as a single agent defined by that file and skips the directory
when it is absent, so the generated set never loads as a second, mis-tooled
copy of every agent.

This document lives in `docs/` rather than `agents/README.md` for the same
reason. The loader claims *every* `.md` file in an agents directory, and a file
without frontmatter still parses — it takes its name from the filename and its
description from the first line of the body. A `README.md` there loads as a
junk agent called "README".

## Format

```markdown
---
name: kebab-case-name
description: one line, under 80 characters
tools: comma, separated, tool, names
---
The complete system prompt the agent runs under.
```

Stella reads exactly four things — `name`, `description`, `tools`, and the body.
Every other frontmatter key is parsed and discarded, so `model:` and `color:`
are inert there; they are added only to the generated Claude Code set.

## Conventions

**Naming.** Files are `<name>.md`, and `name` matches the filename exactly.
Kebab-case, lowercase. Prefer a role noun (`debugger`, `architect`) or
`<domain>-<role>` (`security-reviewer`, `perf-auditor`). No `-agent` suffix —
everything here is an agent. A prefix family is used only where a real pipeline
exists: `spec-*` is an ordered workflow, not a topic grouping.

**Descriptions.** One line, under 80 characters, saying what the agent does.
The generator appends a "Use when…" trigger clause for Claude Code, which
selects agents automatically from the description; Stella does not need one.

Never put an unquoted `": "` in a description. Stella splits frontmatter on the
first colon and tolerates it, but Claude Code uses a strict YAML parser where
that is a syntax error. Use an em dash instead.

**Bodies.** The body *is* the system prompt — complete and self-contained, not
a description of a persona. Write dense, imperative prose. State what the agent
does, how it decides, and what "done" means with evidence.

**Portability.** No file here may reference another repository. No hardcoded
package names, internal module paths, ticket identifiers, environment URLs, or
one-project workflow rules. This harness installs user-globally and applies to
every project; project-specific law belongs in that project's own config.

## Tool grants

Stella enforces the toolbelt at the **prompt** level — it tells the model
"this agent's toolbelt is restricted to: …". A name that is not a real tool is
therefore worse than granting everything, because the model will silently work
around a capability it was told it lacks rather than report the gap. Omit
`tools:` entirely to grant all tools.

Valid Stella tools (`stella tools`):

`bash` · `delegate` · `delete_file` · `delete_state` · `edit_file` ·
`get_environment` · `get_state` · `list_state` · `read_file` · `save_state` ·
`search` · `task_assign` · `task_cancel` · `task_complete` · `task_create` ·
`task_list` · `task_start` · `write_file`

The generator maps them to Claude Code names:

| Stella | Claude Code |
|---|---|
| `read_file` | `Read` |
| `write_file` | `Write` |
| `edit_file` | `Edit` |
| `bash` | `Bash` |
| `search` | `Grep`, `Glob` |
| `delegate` | `Task` |
| `task_*` | `TodoWrite` |

Standard grants: read-only reviewers get `read_file, search` plus `bash` when
they run project checks; writing agents add `write_file, edit_file`.

## Roster

**Review and audit** — `code-reviewer`, `typescript-reviewer`,
`security-reviewer`, `database-reviewer`, `perf-auditor`,
`silent-failure-hunter`, `comment-auditor`

**Build and fix** — `architect`, `feature-shipper`, `debugger`, `simplifier`,
`test-engineer`, `e2e-tester`

**Spec workflow** — `spec-requirements` → `spec-design` → `spec-tasks`, with
`spec-judge` scoring competing drafts and `spec-builder` mining specs from
existing code

**Product and UX** — `ux-architect`, `usability-reviewer`, `parity-auditor`

**Docs and comms** — `docs-writer`, `launch-marketer`, `seo-specialist`,
`demo-director`

**Meta** — `output-evaluator`, `harness-optimizer`, `connector-author`

## Migration map

The previous set of 37 definitions consolidated to 28. Every one is accounted
for below.

| Was | Now | Why |
|---|---|---|
| `eval-code` | `code-reviewer` | Both were the generalist diff reviewer |
| `eval-typescript` | `typescript-reviewer` | Renamed to the role |
| `eval-types` | `typescript-reviewer` | Type-design scoring folded in as a section |
| `eval-security` | `security-reviewer` | Renamed to the role |
| `eval-database` | `database-reviewer` | Renamed to the role |
| `eval-performance` | `perf-auditor` | Merged with `hotpath-perf-auditor` |
| `hotpath-perf-auditor` | `perf-auditor` | Same job; this copy was truncated mid-sentence |
| `eval-silent-failure` | `silent-failure-hunter` | Renamed to the role |
| `eval-comments` | `comment-auditor` | Renamed to the role |
| `eval-agent` | `output-evaluator` | `eval-agent` read as "an agent for evals" |
| `break-fix` | `debugger` | Identical once the live-ops integrations were stripped |
| `doc-updater` | `docs-writer` | Codemap generation became a doc type |
| `marketing-agent` | `launch-marketer` | Campaign workflow merged into the claims-disciplined one |
| `e2e-runner` | `e2e-tester` | Renamed for consistency |
| `knowledge-source-author` | `connector-author` | Generalized off one platform's plugin model |
| `spec-impl` | `feature-shipper` | Task-list execution folded in |
| `spec-test` | `test-engineer` | Test-document authoring folded in |
| `spec-system-prompt-loader` | *removed* | Hardcoded a `.claude/` path; told itself to use no tools while granting all |

Unchanged in name: `architect`, `code-reviewer`, `debugger`, `demo-director`,
`docs-writer`, `feature-shipper`, `harness-optimizer`, `launch-marketer`,
`parity-auditor`, `seo-specialist`, `simplifier`, `spec-builder`,
`spec-design`, `spec-judge`, `spec-requirements`, `spec-tasks`,
`test-engineer`, `usability-reviewer`, `ux-architect`.
