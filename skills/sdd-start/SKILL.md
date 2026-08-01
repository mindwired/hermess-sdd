---
name: sdd-start
description: Start or onboard a substantial project with adaptive, low-ceremony spec-driven development. Use for greenfield systems, large features, multi-session implementations, or work requiring durable decisions and requirements.
license: MIT
compatibility: Hermes Agent with the sdd plugin enabled.
metadata:
  author: hermes-sdd
  version: "0.1.0"
---

# Start an SDD project

Use this workflow only when durable coordination is likely to improve the result. A trivial edit should remain a normal Hermes task.

## Principles

- The implementation outcome matters more than the workflow.
- Record only information that another agent or future session must know.
- Prefer a few precise requirements over a long speculative document.
- Plan the whole direction, but detail only the first executable milestone.
- Ask for clarification only when a wrong assumption would materially change the system. Otherwise choose a reasonable default and record it.

## Choose rigor

Score each signal from 0–3: novelty, ambiguity, surface area, operational risk, expected duration, and coordination. Pass the signals to `sdd(operation="init")`; `mode="auto"` resolves to:

- `quick`: small, bounded work; minimal artifacts.
- `standard`: several files or sessions; requirements plus one milestone.
- `deep`: cross-cutting architecture or high risk; decisions and stronger evidence.
- `program`: a large greenfield product or many milestones; roadmap and context-isolated execution.

Never choose a heavier mode merely because it sounds safer.

## Workflow

1. Inspect the repository enough to distinguish greenfield from brownfield. Do not inventory every file before it is useful.
2. Initialize:

```json
{"operation":"init","root":"<repo>","payload":{"name":"<project>","goal":"<one outcome>","summary":"<brief scope>","mode":"auto","signals":{"novelty":2,"ambiguity":2,"surface_area":3,"risk":2,"duration":3,"coordination":2},"success_criteria":["observable result"],"constraints":["hard constraint"],"non_goals":["explicit exclusion"],"principles":["project-specific engineering rule"]}}
```

3. Capture requirements with `upsert_spec`. Requirements must describe observable behavior or a hard quality attribute. Give each requirement concise acceptance criteria. Do not turn implementation choices into requirements.
4. Record architecture only to the level justified now. For a new large system, establish boundaries, data ownership, major interfaces, deployment shape, and security assumptions. Leave reversible details open.
5. Record an ADR only for a cross-cutting or costly-to-reverse decision:

```json
{"operation":"record_decision","root":"<repo>","payload":{"title":"Decision title","context":"Why this decision exists","decision":"What is selected","alternatives":["Rejected option and reason"],"consequences":["Trade-off"]}}
```

6. Create milestones as vertical outcomes, not component buckets. Each milestone must produce something demonstrably useful and have explicit exit criteria.
7. Immediately load `sdd-plan` and detail only the active milestone.

## Greenfield guidance

For extremely large projects, the first milestone should normally reduce uncertainty while creating an executable skeleton: repository/toolchain, one end-to-end path, core contracts, automated checks, and deployment or local-run proof. Avoid generating every service, table, endpoint, and screen before an end-to-end slice works.

## Completion

Return a compact summary of the project mode, requirements, decisions, milestones, unresolved risks, and the exact next planning action. Do not paste all generated artifacts into chat.
