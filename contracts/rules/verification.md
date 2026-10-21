# Verification — MetalLabs Multi-Agent Harness

**Version:** 0.1 — Shared rule  
**Applies to:** Every agent, authorized task, handoff and acceptance report  
**Status:** Operational guidance; machine-enforced verification gates are not implemented yet

## 1. Principle

**Evidence must match the claim.** A model-generated `PASS` is not evidence that a feature works. An executed test demonstrates only the behavior and conditions that test actually covers. Keep observed results, inferences, unverified assumptions and proposed checks separate.

This rule complements [`../AGENTS.md`](../AGENTS.md), `scope-and-authority.md`, `multi-agent-workflow.md`, project-specific source/architecture contracts and the active role's `AGENT.md`. On conflicts, surface the issue; do not silently relax a governing contract.

## 2. Who does what

- **Butch / Architect:** defines testable acceptance criteria, integration boundaries and a verification plan proportional to risk; does not claim implementation passed.
- **Ripley / Engineer:** implements and runs relevant tests within an approved cut; reports commands, results and uncovered behavior.
- **Mr. Wolf / Troubleshooter:** provides reproducible failure cases, minimal reproductions and diagnostic evidence; does not silently repair production.
- **Deckard / Auditor:** evaluates whether evidence supports the claims and whether important counterexamples or regressions remain; works in a separate review pass and does not modify audited work by default.
- **Doc Brown / Researcher:** tests technical hypotheses in authorized, isolated probes; distinguishes feasibility from production readiness.
- **Gandulf / Chronicler:** records verified outcomes, approved decisions and outstanding gaps without promoting a proposal to fact.
- **Jack Burton / Creative Director:** states artistic acceptance criteria and coordinates human visual assessment where relevant; a generated asset alone does not establish artistic or technical fitness.

`verification.md` does **not** create or execute tests. It specifies the common standard for whoever performs them.

## 3. Select the smallest sufficient verification

Decide checks from the authorized change's impact and failure modes, not from a universal checklist. Possible methods:

| Method | What it can establish | What it cannot establish alone |
| --- | --- | --- |
| Static inspection / lint / type checking | A defined set of structural or syntactic properties | Correct runtime behavior |
| Unit test | Behavior of a specific unit under specified inputs | Correct whole-system integration |
| Integration / contract test | Compatibility across identified boundaries | All user-visible workflows |
| Regression test | Previously identified behavior remains intact for tested cases | Absence of new unknown failures |
| Deterministic data/schema check | Counts, IDs, references, formats and prescribed invariants | Fidelity beyond the checked source and rules |
| Runtime or end-to-end test | An observed workflow in an actual execution environment | Other environments or untested paths |
| Human visual/audio/UX assessment | Qualitative acceptance by an identified reviewer | Automatic technical correctness |
| Documentary audit | Consistency and traceability of recorded decisions and evidence | Runtime correctness unless supported by actual runtime checks |

Avoid expensive full-suite runs for trivial, low-risk documentation edits unless a relevant dependency requires them. Increase coverage for shared interfaces, migrations, state changes, content compilers and destructive risks.

## 4. Evidence record

For any substantive changed artifact, report enough information to reproduce or independently inspect the result:

1. **Task and baseline:** `task_id`, authorized objective, affected revision/files and relevant contracts.
2. **Check:** precise command, tool or manual procedure; inputs, fixtures and environment when material.
3. **Observed outcome:** actual exit status, assertions, measurements or human inspection notes; include relevant logs/errors or stable references.
4. **Coverage:** which acceptance criterion or risk the check addresses.
5. **Limitations:** checks not run, unavailable environments, untested branches or assumptions.
6. **Artifact identity:** changed paths/diff and, when needed, commit or file hash/version to associate evidence with the evaluated bytes.

Never fabricate logs, test execution, browser views, screenshots or human approvals. Clearly label illustrative examples as hypothetical.

## 5. Status and acceptance semantics

Separate **verification outcome** from **task lifecycle**:

- **`PASS`:** the stated checks actually ran or inspections actually occurred, and their relevant acceptance criteria passed. Scope the claim to those criteria and note outstanding untested areas. For a read-only review, a supported no-finding result can be `PASS`.
- **`PARTIAL`:** useful work or some checks succeeded, but the required verification or coverage is incomplete. List exact gaps.
- **`BLOCKED`:** safe verification or task progress is prevented by missing inputs, access, tools, unresolved contradictions or material risk. Identify the smallest resolution.
- **`FAIL` (check result):** an executed check did not meet its criterion. Record it as a failed check, even when the overall task status is `PARTIAL` or `BLOCKED`; do not conceal it with an overall `PASS`.
- **`NOT_RUN`:** the check was not executed. A planned test is not a passed test.

A `PASS` report **does not automatically close a task**. In `multi-agent-workflow.md`, a task enters `REVIEW` with its evidence; `CLOSED` requires human acceptance or a separately authorized closure policy. The human controls Git commits by default.

## 6. Independent audit

Deckard should examine the actual artifact and applicable contract rather than rely solely on Ripley's narrative. Where feasible, grant read-only access and use a separate execution/context pass. The same underlying model with a different persona is **not** a guarantee of independence.

An audit should check:

- Whether the implementation stayed within approved paths and behavioral scope.
- Whether acceptance criteria are measurable and sufficiently exercised.
- Whether claims match actual test commands, logs and affected revisions.
- Whether edge cases, negative cases, failure recovery or integration boundaries are materially under-tested.
- Whether historical/provenance constraints, safety or licensing boundaries were breached.

Findings should cite a reproducible artifact/location, the observed discrepancy, consequence, severity and suggested bounded remedy. Allowed severities: `BLOCKER`, `MAJOR`, `MINOR`, `NOTE`. An auditor may also report **no material findings**; manufacturing criticism is not the job.

## 7. Failed checks and corrections

Preserve failing evidence and classify whether the failure stems from the change, a pre-existing baseline, test drift, environment, or an unresolved cause; do not guess classification without evidence.

- **Inside authorized cut:** Ripley may make a bounded correction and rerun the relevant check if the change remains within authority.
- **Unknown cause:** request a focused Mr. Wolf investigation only when useful.
- **Out of scope, architectural, rights-related or destructive:** stop the affected action and seek a new human decision.
- **Stale tests:** compare test expectations against the approved current contract; do not blindly edit assertions to green a suite.

Record retries and preserve their relationship to the original failure. Do not mark an incomplete rerun as full regression success.

## 8. Source transformations and semantic boundaries (when applicable)

For reconstruction or transformation from a selected source, prioritize referential integrity, stable IDs, source meaning and text, provenance, conditional relationships and deterministic results. Verify totals and exceptions against the **specific selected source revision**, not guesses from derived editorial representations.

For editable diagrams, validate syntax and structural references, and distinguish machine validation from actual opening/rendering or human visual inspection. Never claim interactive or graphical inspection that did not occur.

Where a task actually includes a parser or model-assisted intent adapter, test semantic equivalence and deliberately invalid/ambiguous inputs against the deterministic domain rules. Distinguish direct, conditional and special transitions and preserve unresolved cases. A model's plausible prose is not evidence of a valid state transition. These are conditional verification principles, not authorization to implement such a system.

## 9. Minimal report format

```yaml
# Illustrative structure only; NOT a record of an executed test.
task_id: HARNESS-CUT-001
agent: ripley_engineer
artifact: "path/to/changed_file"
checks:
  - name: "Focused parser regression"
    command: "<actual command when executed>"
    result: NOT_RUN
    evidence: "No execution evidence yet"
acceptance_criteria:
  - criterion: "Specified command produces intended state transition"
    evaluation: UNVERIFIED
outstanding: ["Execute focused test and compare to pinned reference"]
status: PARTIAL
next_action: "Run checks within authorized environment, then request review"
```

Use simple prose for tiny tasks; structured reports are justified when multiple checks, agents or artifacts must be reconciled.

## 10. Future harness enforcement and smoke tests

Markdown rules instruct a model; they **do not enforce** verification. A future harness should capture real tool executions and exit statuses, bind results to exact artifacts, prevent `NOT_RUN` being represented as a successful check, preserve immutable task/handoff evidence where feasible, require necessary approvals and deny forbidden operations through tool permissions.

Initial executable tests should include: false `PASS` rejection with no recorded command; a failing check preserved across a retry; mismatch between report and changed revision; Deckard read-only audit; an unverified GUI check explicitly disclosed; and human `REVIEW` → `CLOSED` authorization. Do not mark these tests as passed until an actual harness runs them.

**Good verification is not maximal testing. It is the smallest convincing body of evidence for the claim being made.**
