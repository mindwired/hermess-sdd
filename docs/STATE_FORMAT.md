# `.sdd/` state format

## Authority and portability

Project-local `.sdd/` files are the source of truth. They are deliberately plain JSON, Markdown, and JSONL so
humans, Git, agents, scripts, and alternate UIs can inspect them without a service. The registry database under
`$HERMES_HOME` only remembers which repository paths visual clients should list.

## Top-level files

### `project.json`

Project identity, goal, mode, constraints, success criteria, complexity score/signals, timestamps, and format
version.

### `state.json`

Current project status, active milestone, verified milestone list, blockers, and update timestamp. It is a compact
resume pointer, not a substitute for reading the active milestone plan.

### `requirements.json`

A versioned requirement collection. Each requirement has an id, title, normative statement, acceptance criteria,
priority, status, source, and timestamps. Markdown rendering is derived in `REQUIREMENTS.md`.

### `architecture.md`

Only durable architecture context needed across tasks. Avoid dumping exploratory transcripts here.

### `events.jsonl`

Append-only lifecycle facts: initialization, specification updates, planning, transitions, evidence, validation,
and finalization. Events support recovery and audit but do not override current JSON state.

## Milestones

Each `.sdd/milestones/<id>/` contains:

- `milestone.json`: objective, requirement links, exit criteria, dependencies, risk, status, interface stability.
- `plan.json`: revisioned task DAG.
- `PLAN.md`: human rendering of the current plan.
- `summary.md`: verification/finalization record.

A task includes id, title, objective, status, risk, dependencies, acceptance criteria, conservative file scopes,
requirement links, evidence ids, notes, summary, and timestamps.

`plan.json.revision` increments on every task/plan mutation. Callers may pass `expected_revision` to prevent stale
whole-plan or targeted updates from overwriting concurrent work.

## Evidence

Evidence records are immutable JSON files under `.sdd/evidence/`. Typical fields include type, task/milestone,
command, result, `passed`, details, artifact paths, and timestamp. Manual completion evidence may be recorded as
failed/insufficient; it does not automatically satisfy program/high-risk verification gates.

## Checkpoints

A checkpoint stores hashes of authoritative `.sdd/` files plus task-scoped source files. Glob patterns are
expanded to concrete files at checkpoint time. A delta reports added, changed, and removed paths without reading
unrelated source content into the agent context.

## Locking and atomicity

Read-modify-write mutations acquire a project metadata lock before reading the relevant plan/state. Writes use a
temporary file and atomic replacement. This prevents independent workers from silently losing each other's task
status updates. Lock files are implementation details and are not authoritative state.
