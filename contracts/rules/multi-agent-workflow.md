# Multi-Agent Workflow — MetalLabs Harness

**Version:** 0.1 — Shared rule  
**Applies to:** All MetalLabs agent roles and tasks  
**Status:** Proposed operational contract. Orchestration and enforcement are **not yet implemented or validated**.

## 1. Purpose

Coordinate specialist agents without turning collaboration into an obligation. **Use the fewest roles, handoffs and model calls required to complete an authorized task with verifiable evidence.** An agent persona is not a process, an authorization, or an independent execution environment.

This rule works alongside [`../AGENTS.md`](../AGENTS.md), `scope-and-authority.md`, applicable project/source contracts, and each role's `AGENT.md`. In a conflict, do not silently choose a convenient interpretation: stop the affected action and seek a human decision.

## 2. Participants and boundaries

- **Human owner:** supplies goals and scope, authorizes consequential changes, accepts/rejects results, performs Git commits by default.
- **Harness:** proposed future software that loads context, selects roles, tracks tasks and approvals, controls tools, captures evidence and enforces limits where implemented. Markdown alone cannot provide enforcement.
- **Specialist agents:** Butch (architecture), Ripley (implementation), Mr. Wolf (diagnosis), Deckard (audit), Doc Brown (research), Gandulf (documentation), Jack Burton (creative direction). They work within their individual contracts; no role may grant itself or another more authority than the initiating task.

**No mandatory manager agent.** The harness is the control plane; agents supply specialized reasoning and authorized work. A human may also explicitly select a role, for example through a future `RFD ripley` command. `RFD` would select or prepare a session, **not** authorize implementation. Commands described here are concepts, not existing software.

## 3. Task envelope (minimal contract)

Before side-effecting work, the harness or operator must establish a task envelope. It may be conversational for read-only questions, but must be explicit and recorded for file changes or tool execution:

| Field | Meaning |
| --- | --- |
| `task_id` | Stable identifier for reports and handoffs |
| `objective` | Required outcome, not an unlimited mission |
| `requester` / `assignee` | Origin and current accountable role |
| `authorized_actions` | Analysis, read, edit, execute tests, etc. |
| `allowed_paths` / `protected_paths` | Positive scope and exclusions |
| `inputs` / `contracts` | Relevant sources, approved decisions and versions |
| `acceptance_criteria` | Observable completion conditions |
| `verification` | Checks to run, or limits preventing execution |
| `budget` | Optional turns/time/tool calls/delegation ceiling |
| `stop_conditions` | Conditions requiring suspension and escalation |

A missing field is not an automatic grant of permission. A task handoff must preserve the envelope or narrow it, never silently enlarge it.

## 4. Task lifecycle

Use the following conceptual states; the harness must eventually make them durable and enforce permitted transitions.

| State | Meaning | Allowed next step |
| --- | --- | --- |
| `PROPOSED` | Request received, scope not yet settled | `READY`, `BLOCKED`, `CANCELLED` |
| `READY` | Scope and authority established | `ACTIVE`, `CANCELLED` |
| `ACTIVE` | Assigned agent working within bounds | `VERIFYING`, `WAITING`, `BLOCKED`, `CANCELLED` |
| `WAITING` | Awaiting bounded dependency/agent response or human decision | `ACTIVE`, `BLOCKED`, `CANCELLED` |
| `VERIFYING` | Actual results and evidence being checked | `REVIEW`, `ACTIVE`, `BLOCKED` |
| `REVIEW` | Work/evidence available for human assessment | `CLOSED`, `ACTIVE`, `BLOCKED`, `CANCELLED` |
| `CLOSED` | Human accepted outcome (or explicitly authorized an automated closure policy) | Terminal; further work requires a new task |
| `BLOCKED` | Safe continuation is impossible inside current envelope | `READY`/`ACTIVE` only after an authorized resolution; or `CANCELLED` |
| `CANCELLED` | Work withdrawn, with partial artifacts identified | Terminal |

A role's report of `PASS` means specified checks passed; it does **not** automatically move a task to `CLOSED`. Likewise, a tool returning success does not prove end-to-end correctness. Preserve earlier artifacts and reasons for reopening.

## 5. Routing: choose the minimum sufficient specialist

Default to one agent. Add another only when the task presents a real boundary of competency or needs separate verification.

- **Butch:** design decisions, contracts, dependency boundaries and small implementation cuts.
- **Ripley:** explicitly approved implementation and focused tests.
- **Mr. Wolf:** reproduce/isolate an unfamiliar or stubborn failure; diagnosis before repair.
- **Deckard:** independent evidence-based review; reports findings without modifying the audited artifact.
- **Doc Brown:** unfamiliar technology or source research, comparison and isolated probes.
- **Gandulf:** record approved decisions and verified state, reconcile documentary drift.
- **Jack Burton:** artistic direction, original concepts, visual briefs and bounded creative exploration.

Example paths (not mandatory pipelines):

- Tiny, approved code fix → Ripley → targeted checks → human review.
- Architectural change → Butch → human approval → Ripley → Deckard if warranted → Gandulf for material decisions → human acceptance.
- Difficult regression → Mr. Wolf → Ripley for separately authorized fix → Deckard if risk warrants.
- Unknown 3D technology → Doc Brown disposable probe → Butch feasibility assessment → human decision; Jack Burton may provide artistic requirements.

Never involve all roles merely because they exist.

## 6. Delegation and request/response contract

An agent may **request assistance**, but only the harness/operator actually dispatches the request if the target role, available tools, permissions and budget permit it. Delegation is not the transfer of ownership or of approval power.

Each request should identify:

1. Parent `task_id` and a unique `request_id`.
2. Sender, recipient, question, and why expertise is needed.
3. Evidence/context sufficient for the recipient (prefer exact files and bounded excerpts over whole-project dumps).
4. Permitted actions, file boundaries, dependencies, budget and stop conditions; all a subset of the parent authorization.
5. Expected answer format and how findings will be verified.

Recipient returns `request_id`, observed results, sources/files, tests actually run, uncertainty, risks, and a recommendation if appropriate. **A recommendation is not approval.** The requester evaluates the result; the harness records the handoff and merges only relevant evidence back into the parent context.

**Default policy for v0.1:** one delegation level from a task's active role; no child-to-grandchild delegation, no self-delegation, no cycles, and no parallel writes to the same artifact. If deeper delegation is genuinely needed, return to the harness/human to create a separately scoped request. A future implementation may allow configurable depth and concurrency after tests.

## 7. Context isolation and communication

Each agent session receives the project entrypoint, applicable shared rules, its own role contract, the task envelope and only the relevant source evidence. **Do not load every role's full instructions or entire repository by default.**

Use explicit handoff artifacts, not assumptions about another agent's private conversational memory. Preserve provenance: who stated a fact, where it came from, what was verified and when. Do not treat roleplay or model-generated summaries as authoritative source files.

A future `RFD <role>` may activate/select a persona and optionally display a greeting, but `TASK` must still check scope and required approval. `DISMISS` may close a session, not erase task records or evidence.

## 8. Verification and independent review

The acting agent checks its own work where tools permit. Report exactly what was executed, which environments were used, results observed, and what remains unverified. For source changes, include a bounded diff or changed-file list and actual test outputs.

Deckard's review must be a distinct examination of the artifact, applicable contract and evidence, preferably with read-only permissions and a separate context/pass. Different role instructions using the same model may reduce confirmation bias but do **not** guarantee independence. An auditor's findings need reproducible references; severity does not confer permission to repair.

A serious finding returns the task to `ACTIVE` (with approved correction scope) or `BLOCKED`; it cannot silently rewrite the requirements. Do not confuse a green test with a completed feature or graphical validation with a command-line check.

## 9. Approvals, writes, Git and human ownership

No automatic commits, pushes, publishing, deployment, migrations, broad refactors, dependency changes or destructive operations without separate explicit authorization. A human authorization must identify the affected task and action; approval of a proposal is not automatically approval to execute every follow-up.

For Google Drive Markdown edits follow **read → prepare minimal change → reread to detect interference → preserve a backup if material → replace → reread → compare → report**. This is not atomic concurrency control; stop on mismatches. Confirm Google Drive Desktop has synchronized the expected local bytes before the human commits in Git.

Agents operating locally should inspect `git status`, preserve human changes, avoid out-of-scope paths, and report the final diff and uncommitted state. The owner decides adoption and performs commits by default.

## 10. Failure, timeout and disagreement

- On missing source, contradictory contracts, unsafe writes or insufficient verification, stop the affected operation and mark `BLOCKED` with the smallest actionable resolution.
- On failed tests, preserve outputs; ask Mr. Wolf for bounded diagnosis only if useful.
- On disagreement between agents, compare cited evidence and governing contracts. Do not conduct endless agent-to-agent debate. Escalate unresolved decisions to the human.
- On model/tool timeout or budget exhaustion, return `PARTIAL` with durable artifacts, checks completed, gaps and a safe resume point.
- Retry only when the operation is safe/idempotent or its side effects have been inspected; avoid duplicate writes or commands.

## 11. Minimal handoff/report

Use a concise record, scaled to task complexity:

```yaml
# Illustrative schema, not yet parser-enforced
task_id: HARNESS-CUT-001
agent: ripley_engineer
status: REVIEW
scope: "Implement an approved, bounded parser change"
changed_files: ["src/parser.py"]
checks:
  - command: "pytest tests/test_parser.py"
    outcome: "PASS — hypothetical example, not executed"
observed: ["Example-only result"]
unverified: ["Human interactive acceptance"]
risks: []
approval_needed: "Human review and Git commit"
```

In real reports, never populate `PASS` or observed results unless the relevant check actually ran. Keep the task history and handoff linked to the exact artifacts used.

## 12. First implementation tests (future, not yet executed)

1. **Single-role smoke test:** route a read-only task to Butch; verify no other role is invoked.
2. **Bounded handoff:** Butch asks Doc Brown one research question; verify identical or narrower authority and a captured reply.
3. **Authorization gate:** Ripley requests an out-of-scope file write; execution is blocked even if the model proposes it.
4. **Audit separation:** Deckard reviews Ripley's output without write access; evidence and findings are recorded.
5. **Cycle protection:** reject Doc Brown → Butch → Doc Brown infinite delegation.
6. **Failure recovery:** test failure and timeout yield `BLOCKED`/`PARTIAL` without fake success or lost outputs.
7. **Human closure:** task remains in `REVIEW` until human acceptance; commits remain human-controlled.

Passing a document review is not passing these operational tests. Record implementation-specific mechanisms and outcomes only when an actual harness exists.

**Goal:** A small, auditable collaboration system in which specialization improves results without multiplying coordination overhead.
