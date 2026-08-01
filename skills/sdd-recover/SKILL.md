---
name: sdd-recover
description: Recover a long-running SDD project after context loss, interruption, conflicting workers, stale plans, or partial implementation.
license: MIT
compatibility: Hermes Agent with the sdd plugin enabled.
metadata:
  author: hermes-sdd
  version: "0.1.0"
---

# Recover an SDD project

Use durable state as a hypothesis and the repository as evidence. Never assume a task status is correct merely because it is recorded.

## Recovery sequence

1. Call `sdd(operation="status")` and `sdd(operation="validate", payload={"record":false}, options={"detail":"normal"})`.
2. Inspect `git status`, recent commits, changed files, running processes, test results, and the active milestone plan.
3. If a checkpoint exists, call `context_delta` to identify which authoritative and scoped files changed since it was created.
4. Reconcile each `in_progress` task:
   - implementation and evidence complete → verify, record evidence, mark done;
   - partial but coherent → keep in progress and update notes/remaining acceptance;
   - no meaningful work → return to pending;
   - impossible pending dependency or conflict → mark blocked with reason.
5. Detect overlapping worker edits before resuming parallel work. Merge or serialize conflicting scopes.
6. Refresh only stale artifacts. Preserve valid decisions and requirements; do not regenerate the project specification from scratch.
7. Request `next` and resume with a fresh context pack.

## Stale-plan rule

Change a plan when reality invalidates it: a dependency changed, an interface proved wrong, acceptance is untestable, or task scope became unsafe. Do not rewrite a plan simply to match incidental implementation details.

## Recovering from context overload

Before starting a new session, leave:

- accurate task statuses;
- a short task or milestone summary;
- reproducible evidence;
- a checkpoint;
- explicit blockers and decisions.

The new session should need only `status`, `context_delta`, and a selected task context pack—not the entire old conversation.

## Output

State what was reconciled, what remains uncertain, which tasks changed state, and the next safe action.
