# Documentation — MetalLabs Multi-Agent Harness

**Version:** 0.1 — Shared rule  
**Applies to:** All agents, tasks, decisions and project documents  
**Status:** Documentation contract; automated enforcement is not yet implemented

## 1. Purpose

**Documentation must preserve what was decided, what was done, why it matters, and what remains uncertain — without becoming a second project.** Write for the next developer or agent who must resume work, verify a claim, or understand a boundary. Prefer a short, accurate record to an impressive but stale report.

This rule complements [`../AGENTS.md`](../AGENTS.md), `scope-and-authority.md`, `multi-agent-workflow.md`, `verification.md`, approved project contracts, and the active role's `AGENT.md`. Documentation never grants permission to implement, migrate, publish, or revise a protected decision.

## 2. Ownership and responsibilities

- **Human owner:** approves substantive decisions, accepts results, and controls Git commits by default.
- **Gandulf / Chronicler:** reconciles documentary state, records accepted decisions and verified outcomes, identifies contradictions, and proposes minimal updates. Gandulf does not approve decisions or invent evidence.
- **Butch / Architect:** supplies rationale, interfaces, alternatives and decisions proposed for approval; marks proposals as proposals.
- **Ripley / Engineer:** supplies actual changes, affected paths, tests executed and limitations; does not silently close a task.
- **Deckard / Auditor:** records evidence-based findings, including documentary drift and missing proof; does not rewrite history to make a report green.
- **Mr. Wolf / Troubleshooter:** supplies reproduction steps, diagnosis, uncertainty and the observed resolution when verified.
- **Doc Brown / Researcher:** separates sources, experiments and findings from hypotheses and adoption recommendations.
- **Jack Burton / Creative Director:** documents artistic intent, references, asset provenance, options and human-approved direction separately from speculative concepts.

Every agent is responsible for an accurate task handoff; Gandulf is the specialist for substantial documentary reconciliation, not a mandatory hop after trivial work.

## 3. Document authority and provenance

Use the project's explicit source-of-truth hierarchy. Selected source files and their specific revisions govern source facts; editorial diagrams, transformations and notes are derived interpretations, not replacements. Approved technical/art contracts govern their own domains. [`../AGENTS.md`](../AGENTS.md) routes work but does not supersede source integrity or human decisions.

For consequential claims, retain enough provenance to find the supporting artifact: relevant file/path or URL, source revision or date, and the exact observation or approval. Distinguish:

- **OBSERVED / VERIFIED:** supported by inspection, tool result or executed check, with a reference.
- **APPROVED / DECIDED:** an explicit human decision, with its scope and date where available.
- **PROPOSED:** a recommendation not yet authorized.
- **PENDING:** an identified decision, check or activity that has not occurred.
- **DEFERRED:** deliberately set aside, with its reason or condition for reopening.
- **UNKNOWN / DISPUTED:** insufficient or conflicting evidence, clearly identified.

Never turn a proposed implementation into `ACTIVE`, an agent's `PASS` into human `CLOSED`, or a draft diagram into canonical historical evidence.

## 4. What to document, and when

Document proportionally to impact:

- **Small, local change:** a concise change summary, affected files and test outcomes may suffice; do not force a new ADR or ceremony.
- **Approved architectural/artistic decision:** record the problem, chosen option, rationale, alternatives worth remembering, affected contracts, trade-offs and who approved it.
- **Completed implementation cut:** record baseline, boundaries, changes, verification actually performed, unresolved risks and review/acceptance status.
- **Research or isolated probe:** record hypothesis, inputs, environment, observations and applicability limits; do not label the result production-ready.
- **Historical transformation:** record pinned source, transformation method, counts/IDs, exceptions, rights and traceability to the source.
- **Blocked or deferred work:** record blocker, preserved artifacts, owner of the decision, and a concrete resumption condition.

Update an operational state document **only when the operational state really changed**. Where the project uses a `CURRENT_STATE.md` convention, an unchanged state should be reported as `CURRENT_STATE_UPDATE: NOT_REQUIRED`; do not churn the file for cosmetic edits. Projects without that convention need not adopt it blindly.

## 5. Decision records and historical integrity

An accepted decision should be reconstructable without rereading a long chat. Use a small ADR or decision entry when the choice affects multiple modules, the team, or future compatibility. Include:

1. Decision identifier, title and date (when known).
2. Context/problem and evidence available at the time.
3. Decision and **human approval status**.
4. Meaningful rejected alternatives and trade-offs.
5. Affected contracts, risks and migration implications.
6. Conditions for reconsideration, if any.

Do not retroactively edit an old decision to imply it was always different. Supersede it with a linked new decision and explain the reason. Historical documents may contain obsolete facts; label them as historical instead of silently rewriting their past state.

## 6. Task, cut and handoff traceability

For material work, link documentation to the `task_id` defined in `multi-agent-workflow.md` and, where relevant, the parent delegation `request_id`. Distinguish the task's workflow state (`PROPOSED`, `READY`, `ACTIVE`, `WAITING`, `VERIFYING`, `REVIEW`, `CLOSED`, `BLOCKED`, `CANCELLED`) from a check result (`PASS`, `FAIL`, `NOT_RUN`) and an overall evidence-qualified status (`PASS`, `PARTIAL`, `BLOCKED`).

A report should usually identify: objective; scope and exclusions; source/baseline; actual files changed; commands and checks **actually** run; findings and residual unknowns; human approvals needed; and next bounded step. Do not fabricate test logs, commit hashes, permissions, visual inspections or dates.

If multiple documents disagree, identify exactly which claim differs and which evidence controls it. Reconcile only within authorized documentary scope; an unresolved technical decision remains unresolved.

## 7. Safe editing and Google Drive collaboration

For Markdown edits through Google Drive:

1. **Read** the current document and identify its stable file ID.
2. **Prepare** the smallest justified change while preserving unrelated content and human edits.
3. **Recheck** for intervening changes before writing; stop on unexpected differences.
4. **Back up** material or high-risk edits when appropriate.
5. **Replace** content preserving the same file ID/name/location.
6. **Reread** from Drive, compare to the intended content and report `PASS`, `PARTIAL`, or `BLOCKED` with the observed result.

This procedure reduces risk; it does **not** provide atomic compare-and-swap. Never claim that Drive Desktop synchronized locally without checking. Git operates on the local working tree; a Drive write is not a Git commit. Preserve local uncommitted changes and leave commits to the human unless explicitly authorized otherwise.

## 8. Terminology, style and scope

- Prefer plain Markdown, stable headings, concise tables and relative links where useful.
- Use consistent names, paths and role IDs (for example `mrwolf_tech_troubleshooter`, `gandulf_chronicler`, `jack_burton_the_artist`). Check real paths rather than assuming a folder has not been renamed.
- Quote exact technical identifiers, commands, errors and file names. Avoid embellishment and speculative explanations presented as facts.
- Make summaries useful without requiring readers to open every supporting file; link detailed evidence instead of duplicating entire logs.
- Do not add new document hierarchies, duplicated registries or templates unless an actual need is demonstrated and the scope authorizes it.
- Protect secrets, personal information, licensed assets and source attribution. Do not publish or redistribute historical game content merely because it is available online.
- The agent's personality can color its conversational commentary, **not** the factual precision or authority of the stored record.

## 9. Review, drift and closure

Before marking a documentation task ready for human review, check: current source and approved decisions consulted; claims supported; links and identifiers consistent; proposed versus accepted work separated; tests accurately described; current state not contradicted; and no unrelated edits introduced.

Gandulf may propose a correction to stale documentation. Deckard may independently audit the evidence. Neither may declare human acceptance on the owner's behalf. A documentary `PASS` demonstrates that the documented checks were performed; it does not prove runtime behavior or automatically move a task from `REVIEW` to `CLOSED`.

Stop and report a precise contradiction if canonical sources disagree, approval cannot be established, the correct revision is unknown, human edits may be lost, or the update would silently expand the project scope.

## 10. Future harness checks (not yet implemented)

An executable harness may later verify required task IDs, allowed file paths, reference validity, role names, consistent state transitions, evidence links, and recorded human approvals. It may prevent unsupported `CLOSED` transitions or unsafe writes. **Until those checks are implemented and exercised, these are behavioral instructions, not enforced guarantees.**

Initial behavioral tests should include: refusing to turn a proposal into an approved decision; reporting contradictory state documents; preserving a historical record when superseded; avoiding a pointless `CURRENT_STATE.md` update; and reporting an unsynchronized Drive edit as unverified locally.

**Gandulf's working principle:** Remember accurately, write only what helps, and never confuse a good story with an approved fact.
