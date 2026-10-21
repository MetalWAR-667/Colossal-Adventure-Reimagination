# MetalLabs Harness

**Foundation I — Deterministic role router (experimental)**

A small, read-only Rust CLI that routes named tasks to existing agent contracts. It **does not** invoke language models, delegate tasks, write project files, grant tool permissions, or commit to Git. `STATUS: READY` means the contract path resolved, **not** that an agent has run.

## Prerequisites

- Rust toolchain (`rustup`, `cargo`), with access to crates.io for first dependency download.
- Existing `RPG_Archaeology_IF/.agents/agents/` contracts (not bundled here).

## Start

From the folder containing `Cargo.toml`:

```sh
cargo test
cargo run -- route research --agents-root "G:/Mi unidad/RPG_Archaeology_IF/.agents"
cargo run -- route documentation --agents-root "G:/Mi unidad/RPG_Archaeology_IF/.agents"
cargo run -- route orbital_laser --agents-root "G:/Mi unidad/RPG_Archaeology_IF/.agents"
```

The Windows path is **illustrative**: substitute the real synced Drive location. Without `--agents-root`, the config resolves `contracts_root` relative to the `config/` directory, which assumes sibling directories in a particular layout; override it if your folders differ.

Custom config: `cargo run -- route audit --config config/roles.toml --agents-root PATH`

## Files

- `Cargo.toml`: Rust package and dependencies (`serde`, `toml`).
- `src/main.rs`: CLI, TOML parsing, route resolution, contract path checks, unit tests.
- `config/roles.toml`: explicit role/route mapping for seven roles.

## Safety contract

- Unknown tasks and missing role configurations fail closed.
- Contract paths must stay under the selected root; symlink escapes are rejected via canonicalization.
- The router only prints the selected role and its existing contract path. No automatic writes or agent execution.
- A valid route is **not** a sandbox or authorization system; tool-level permissions come later.

## Foundation I acceptance

1. `research` resolves to `doc_brown` and an existing `AGENT.md`.
2. `documentation` resolves to `gandulf_chronicler` and an existing `AGENT.md`.
3. Unknown tasks return non-zero exit status and do not invent a role.
4. `cargo test` passes locally.

## Next steps — not implemented

Task Envelope, context composition, LLM adapters, handoff validation, approval gates. Changes to agent contracts or automatic commits are out of scope.

**Status:** scaffold authored; local Cargo compilation and integration validation must be performed by the project owner on their computer.
