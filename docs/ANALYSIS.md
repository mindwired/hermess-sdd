# Deep analysis: SDD for Hermes at very large scale

Research snapshot: **August 1, 2026**.

## Executive conclusion

The best Hermes integration is not a port of any single existing framework. It combines:

- OpenSpec's fluid, behavior-first artifacts and visual discoverability;
- GSD's durable state, fresh-context workers, bounded orchestration, and quick-path escape hatch;
- Spec Kit's attention to project principles and explicit acceptance criteria;
- BMAD's scale adaptation and role specialization;
- Hermes's native plugin, skill, subagent, Kanban, Dashboard, and Desktop primitives.

It deliberately rejects their most expensive tendencies: dozens of permanent tools, large mandatory templates, every-phase-for-every-task rules, workflow transcripts as context, and multiple copies of the same state.

The resulting design treats SDD as a **context and coordination compiler**. It converts durable intent into the smallest reliable execution context for the next task, then requires evidence that the output satisfies the intent.

## Evaluation criteria

Each project was assessed against the intended Hermes use case:

1. Greenfield and repository-scale suitability.
2. Quality of requirements, architecture, planning, execution, and verification.
3. Context-window and token efficiency.
4. Recovery across sessions and workers.
5. Safe parallelism and specialization.
6. Brownfield and change-evolution support.
7. Human reviewability and visual interfaces.
8. Hermes API compatibility and maintenance burden.
9. Risk of process becoming the agent's primary task.
10. Extensibility without locking the state to one UI or model.

## Comparative decision matrix

| Approach | Hermes-native correctness | Large greenfield programs | Brownfield/change work | Context efficiency | Parallel execution | Visual support | Ceremony risk |
|---|---|---|---|---|---|---|---|
| Hermes OpenSpec | High | Medium | High | Medium | Low–medium | Dashboard | Medium |
| Hermes Spec-Kit | Skills-only | High | Medium | Medium | Medium | None | High |
| GSD Hermes | High through adapter | High | High | High when disciplined | High | Workflow/status surfaces | Medium–high |
| PlanForge | Low on current APIs | Medium in concept | Medium | Unknown | Medium in concept | Claimed Dashboard | High implementation risk |
| `paalstack/hermes-spec` | Low | Low–medium | Low–medium | Low | Low | None | Medium |
| GitHub Spec Kit | External methodology | High | Medium | Medium–low | Medium | External ecosystem | High |
| OpenSpec upstream | External methodology | Medium | High | High | Low | External ecosystem | Low–medium |
| BMAD | External methodology | High | Medium | Medium | High | External ecosystem | High |
| **This plugin** | **High** | **High** | **High** | **High by default** | **Conservative, enforceable** | **Dashboard + Desktop + all chat/TUI surfaces** | **Adaptive** |

The ratings are architectural judgments for the stated Hermes use case, not universal quality rankings. A methodology optimized for team governance may intentionally accept more ceremony than a single-agent implementation workflow should.

## Hermes extension constraints

Hermes currently exposes three distinct plugin systems:

- The Python Agent plugin supports tools, hooks, slash commands, CLI commands, and bundled skills. It is the functional layer common to CLI, TUI, gateways, Dashboard chat, Desktop chat, and worker processes.
- The web Dashboard loads an IIFE bundle through `window.__HERMES_PLUGIN_SDK__` and can mount a FastAPI backend under `/api/plugins/<id>/`.
- The native Desktop app loads one uncompiled ESM file through `@hermes/plugin-sdk`. It can use the same FastAPI namespace but not the Dashboard frontend code.

No independent TUI UI-contribution SDK is documented. The TUI shares the Agent tool and slash-command layer. This makes a single Python core with thin visual adapters the only architecture that provides consistent behavior on every surface without duplication.

## Project analysis

### `FelineStateMachine/hermes-openspec`

**What it gets right**

- It is a genuine current Hermes Agent plugin rather than a prompt bundle pretending to be one.
- Its project artifacts live beside code and remain readable without the UI.
- It provides a useful Dashboard board, source registry, structured spec browser, branch comparison, and lifecycle operations.
- It separates filesystem-backed operations from those requiring the OpenSpec CLI.
- OpenSpec's current upstream philosophy is explicitly fluid, iterative, lightweight, brownfield-friendly, and behavior-first. Its convention specification correctly discourages implementation detail inside behavioral requirements.

**Weaknesses for this use case**

- Twenty Agent tools impose a larger permanent tool-description footprint and increase tool-selection ambiguity.
- The documented four-layer architecture intentionally duplicates skills, CLI behavior, plugin wrappers, and Dashboard filesystem logic with different return shapes. That is understandable for compatibility, but it raises sync and debugging costs.
- Upstream skills shell out to an external CLI rather than use the plugin's own operations.
- The strongest workflow centers on individual changes. It is less opinionated about multi-milestone greenfield program decomposition, context-sized workers, and safe execution waves.
- It adds another runtime dependency for the complete experience.
- It has no native Desktop UI.

**What we adopt**

Behavior-first requirements, fluid artifact revision, project-local state, visual browsing, and explicit separation between proposed change and current specification.

**What we avoid**

Tool proliferation, external CLI dependence, and four semantically overlapping execution layers.

### `kmarecki/hermes-spec-kit`

**What it gets right**

- It addresses greenfield work directly.
- It covers constitution, specification, planning, tasks, implementation, verification, closure, bugfix, and reopen paths.
- It has project-purpose and architecture guidance rather than assuming one web-app shape.
- It makes acceptance criteria, TDD, regression protection, branch safety, and closure explicit.
- Its separate modes acknowledge that a bugfix should not run the same flow as a new system.

**Weaknesses for this use case**

- Thirteen skills, many templates, a three-level decision tree, twelve principle categories, mandatory phase commits, and mandatory close can become a second project layered over the real project.
- Fixed phase gates can encourage agents to optimize artifact completion rather than discover the simplest correct implementation.
- A large generic constitution often repeats engineering defaults the repository already encodes in tests, linters, package managers, and CI.
- Prompt-only state has weaker machine validation and visual projection.
- Its broad trigger vocabulary can make the methodology activate when ordinary coding would be better.

**What we adopt**

Explicit success criteria, project-specific principles, mode differentiation, reopen/recovery semantics, and meaningful closure.

**What we avoid**

The universal constitution wizard, mandatory commits per phase, and fixed ceremony independent of task risk.

### `dexteon/gsd-hermes`

**What it gets right**

- It articulates the most important scaling problem: quality degradation as a long orchestration context accumulates noise.
- Durable `.planning/` artifacts allow workers and sessions to share state without sharing conversation history.
- Discuss → Plan → Execute → Verify → Ship is easy to understand.
- Fresh-context researchers, planners, executors, and verifiers are strong for large work.
- Dependency waves and context-sized plans are appropriate for repository-scale generation.
- Quick/fast routes explicitly acknowledge that the full loop is wasteful for small tasks.
- It treats orchestration context headroom as an operational concern.

**Weaknesses for this use case**

- It is a large cross-runtime framework with a substantial installer, prompt inventory, agent roster, hooks, adapters, and generated files.
- Supporting many runtimes forces abstractions and maintenance unrelated to Hermes's richer native APIs.
- Fresh subagents for every phase add latency and token cost even where the main session has adequate context.
- A strict orchestrator that “never touches source files” can introduce unnecessary delegation for small, tightly coupled work.
- Context windows named in framework prompts can become stale as runtimes and models change.
- The framework can produce many intermediate summaries and handoffs, each of which costs tokens and creates opportunities for semantic drift.

**What we adopt**

Durable state, context isolation, task-sized plans, safe waves, checkpoints, explicit recovery, and a light path.

**What we change**

Delegation is conditional. The main session may implement a small task directly. Context packs are deterministic and budgeted rather than repeatedly LLM-summarized. Hermes-native tool and subagent APIs replace cross-runtime shims.

### PlanForge

**Strengths**

- Clear phase, wave, verification, and roadmap concepts.
- A visual roadmap is the correct type of UI for long work.
- The `.planning/` compatibility goal is pragmatic.

**Weaknesses**

- The inspected code targets an older or proposed Hermes API: command and hook signatures and the veto return shape do not match current documented APIs.
- The manifest shape does not match the current Python Agent plugin manifest.
- The repository is small and lacks convincing compatibility and end-to-end test evidence.
- Several advertised features are declarations rather than mature integrations.

**Insight**

A plugin must be built against current Hermes source and official examples, not inferred from a conceptual plugin interface.

### `paalstack/hermes-spec`

**Strengths**

- A compact set of explicit operations from research through documentation.
- Project-local `.spec/` artifacts.
- Attempts to reuse Hermes profiles and delegation.

**Weaknesses**

- It imports `hermes_tools` as a normal plugin API, although that module is designed for Hermes code-execution subprocesses.
- Static inspection found inconsistent state keys and fragile directory initialization.
- Most stages delegate with generic prompts and then store the whole output, creating large, weakly structured artifacts.
- It lacks a robust dependency graph, scoped context, evidence model, UI, and recovery protocol.

**Insight**

A list of lifecycle verbs is not enough. The hard problems are durable semantics, bounded context, conflict-safe execution, and proof.

### GitHub Spec Kit

Spec Kit advances a strong “specification as executable source” model, with constitution, specify, clarify, plan, tasks, and implementation flows. It is strongest when a team wants thorough up-front alignment and repeatable generated artifacts.

Its risks are visible in its strengths: rigid phase ordering, sizable Markdown output, and a tendency to make specification the dominant artifact even where code and tests provide more precise truth. For Hermes, the right interpretation is **spec-anchored**, not universally spec-as-source: stable behavior and constraints remain authoritative, while source code, schemas, tests, and migrations remain authoritative for implementation reality.

### OpenSpec upstream

OpenSpec's current positioning directly addresses the heavyweight problem: fluid rather than rigid, iterative rather than waterfall, behavior-first, and applicable to brownfield systems. Its explore/propose/apply/verify separation is useful. The plugin adopts this fluidity but adds program-level milestones and context engineering.

### BMAD Method

BMAD contributes scale-adaptive planning, role-specific agents, and an end-to-end product-development perspective. This is valuable for a huge greenfield product where product, UX, architecture, security, and QA reasoning differ.

The downside is a large catalog of agents and workflows. Role specialization should be selected per task, not loaded as a permanent virtual organization. Hermes profiles or `delegate_task` roles can supply specialization only when needed.

## What SDD should mean in Hermes

SDD is valuable when it solves at least one of these problems:

- the task cannot be fully and correctly described in one short prompt;
- decisions must survive multiple sessions;
- several independent workers need a shared contract;
- implementation must trace to safety, compliance, or product requirements;
- the system is large enough that context selection matters;
- verification requires more than “the code looks plausible.”

It is not automatically valuable for a typo, mechanical rename, narrow bug, or obvious one-file change.

### Three levels of authority

1. **Spec-first:** the spec is agreed before implementation, but can evolve as learning occurs. Default for normal features.
2. **Spec-anchored:** stable goals, constraints, and interfaces are authoritative; detailed design evolves with code. Best default for large Hermes projects.
3. **Spec-as-source:** formal schemas/models generate or mechanically constrain implementation. Reserve for APIs, protocols, configuration schemas, compliance rules, or generated systems where determinism justifies the cost.

The plugin supports all three without forcing a label into every task.

## Failure modes and defenses

### Process capture

**Failure:** the agent focuses on completing phases and documents rather than the product.

**Defense:** adaptive modes, one active milestone, concise artifacts, and skills that explicitly prioritize implementation outcomes.

### Artifact inflation

**Failure:** every stage writes a long Markdown document that later agents must reread.

**Defense:** structured JSON, byte-size warnings, bounded context packs, compact generated views, and external references for logs/research.

### Premature architecture

**Failure:** a greenfield agent designs every service and abstraction before an end-to-end path works.

**Defense:** vertical first milestone, irreversible-decision ADR threshold, and plan detail only for the active milestone.

### False parallelism

**Failure:** several agents edit shared contracts or adjacent files, causing merge conflicts and incompatible assumptions.

**Defense:** dependency DAG, conservative file scopes, unstable-interface serialization, and critical-risk isolation.

### Status without proof

**Failure:** tasks become `done` because a worker says so.

**Defense:** risk-based evidence, structural validation, independent verification for high-risk milestones, and explicit finalization.

### Context laundering

**Failure:** repeated summaries omit constraints and become treated as truth.

**Defense:** source artifacts remain available; deterministic packs quote structured state; packs instruct agents to read exact source files.

### Stale specifications

**Failure:** the code changes while specs remain frozen, making the spec actively misleading.

**Defense:** fluid `upsert_spec`, event history, milestone finalization, recovery reconciliation, and no claim that every implementation detail belongs in the spec.

### Tool-schema tax

**Failure:** dozens of lifecycle tools consume prompt space and confuse model selection.

**Defense:** one operation-dispatched tool and on-demand skills.

## Token and quality economics

The important metric is not minimum tokens; it is **quality-adjusted token cost**.

Useful token expenditure:

- one bounded research task that prevents a wrong architecture;
- a context pack that prevents a worker from reading the entire repo;
- an independent verifier on a critical migration;
- durable acceptance criteria that prevent repeated rework.

Wasteful expenditure:

- reprinting the whole roadmap every turn;
- one subagent per trivial phase;
- regenerating unchanged documents;
- maintaining separate state shapes for every UI;
- verbose completion narratives with no evidence;
- universal constitutions made of generic best practices.

The plugin minimizes fixed cost and permits variable cost only where complexity or risk warrants it.

## Recommended large-project operating model

### Main session

Owns intent, decisions, active milestone, worker selection, conflict resolution, and user communication. It does not need to be forbidden from editing code; it simply avoids accumulating unrelated implementation detail.

### Research workers

Used for unfamiliar technology, standards, external APIs, security, or architecture choices. They return decisions, evidence, open questions, and source links—not browsing transcripts.

### Planning worker

Used when decomposition itself is complex. It receives requirements, architecture boundaries, and relevant repository facts. A checker should challenge high-risk plans, but not every ordinary plan.

### Execution workers

Receive one task context pack and exact repository access. Their result is code, tests, evidence, and a concise summary.

### Verification worker

Independent for high-risk or broad milestones. It starts from requirements, diff, and evidence rather than the implementation worker's reasoning.

### User checkpoints

Reserved for product ambiguity, destructive operations, irreversible decisions, security/privacy trade-offs, and scope changes. Avoid asking the user to approve routine mechanics.

## Why this implementation fits Hermes

- It uses the official current Python plugin API and bundled-skill registration.
- It uses Hermes's slash and CLI command APIs rather than invented command hooks.
- It shares a FastAPI namespace exactly as Dashboard and Desktop document.
- Its Desktop file is an uncompiled ESM module using only permitted imports.
- It does not require a TUI-specific extension that Hermes does not expose.
- It leaves subagent invocation to Hermes and the loaded execution skill rather than building a competing agent runtime.
- It can coexist with Hermes Kanban: SDD defines intent/dependencies/context; Kanban can dispatch actual workers if desired.

## Sources reviewed

- Hermes Agent plugin source and developer documentation: https://github.com/NousResearch/hermes-agent
- Hermes example plugins: https://github.com/NousResearch/hermes-example-plugins
- Hermes OpenSpec plugin: https://github.com/FelineStateMachine/hermes-openspec
- Hermes Spec-Kit: https://github.com/kmarecki/hermes-spec-kit
- GSD Hermes: https://github.com/dexteon/gsd-hermes
- PlanForge: https://github.com/AxDSan/planforge-hermes
- Hermes Spec: https://github.com/paalstack/hermes-spec
- GitHub Spec Kit: https://github.com/github/spec-kit
- OpenSpec: https://github.com/Fission-AI/OpenSpec
- BMAD Method: https://github.com/bmad-code-org/BMAD-METHOD
- Recent practitioner/research framing reviewed cautiously: arXiv 2602.00180, 2605.02455, and 2607.16680. These are recent and should not be treated as mature consensus or as proof of broad production outcomes.
