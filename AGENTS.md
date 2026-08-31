# Repository Agent Instructions

## Load the Existing Engineering Rules

- Read and follow [`.agents/AGENTS.md`](.agents/AGENTS.md) before reviewing or modifying this repository. Its architecture, code-generation, layout, DTO, and communication rules remain authoritative.
- Treat this file as an additional repository-context and review-discipline layer. User and system instructions take precedence if a conflict exists.

## Maintain a Stable Project Context

- Convert user-provided scope, verified runtime facts, project stage, and delivery constraints into persistent assumptions for the entire task. Do not silently fall back to generic framework assumptions in later replies.
- When the user supplies design intent, verify it against code, logs, or history when possible. Do not replace a supported project-specific explanation with a generic best-practice narrative.
- After correcting a premise, re-audit every conclusion that depended on it. Do not resurrect removed code, disproven races, or stale findings in later summaries.
- Distinguish the current worktree from committed history. Existing and untracked changes belong to the user unless explicitly identified otherwise.

## Evidence Order for Reviews and Diagnoses

Use evidence in this order:

1. Current code and current worktree state.
2. Actual normal-user call paths and runtime logs.
3. Git history and prior implementations.
4. Generic framework conventions and best practices.

- Prefer logs and observed event order over assumptions about typical Vue, Tauri, or WebView lifecycle behavior.
- A static possibility is only a candidate issue. Assess its reachability, frequency, and impact before assigning severity.
- Do not describe an issue as affecting normal reliability unless it is reachable through normal use or supported by runtime evidence.
- When evaluating evolution or author capability, inspect Git history and, when available, the sibling legacy repository `../uXuexitongJS` before inferring that a missing current feature reflects missing knowledge.

## Classify Findings Before Judging Them

Every review finding must be classified as one of the following:

- **Current normal-path defect:** present now and reachable during ordinary use.
- **Exceptional-path risk:** present now but requires failure, unusual concurrency, invalid state, or rare environment conditions.
- **Completion or migration gap:** planned or previously implemented behavior not yet restored or finalized in the current rewrite.
- **Intentional tradeoff or product constraint:** behavior chosen to preserve a required delivery or compatibility property.
- **Removed experiment or historical regression:** useful historical evidence, but not a current defect.
- **Cross-version capability gap:** a principle repeatedly absent across versions with no contrary design evidence.

Do not use completion gaps, deliberate constraints, or removed experiments as evidence of poor current runtime quality. Do not infer an author's inability from a feature's absence in one in-progress snapshot.

Keep these concepts separate in reports:

- Feature completeness versus code quality.
- Current code quality versus author capability.
- Normal-use reliability versus defensive hardening.
- AI-assisted output volume versus demonstrated technical ownership.
- Physical file splitting versus logical modularity and delivery requirements.

## Preserve Known Product and Architecture Constraints

- `src-tauri/src/scripts/core.js` is intentionally a single self-contained delivery artifact. The same source must remain usable both through direct browser-console copy/injection and through Tauri's `include_str!` plus WebView `eval` injection.
- Do not criticize `core.js` merely for being a single file or propose ES-module imports without preserving direct-copy execution. Judge its internal logical boundaries, state model, and behavior instead.
- Preserve progressive enhancement: without a Tauri backend, the standalone script uses defaults and can process supported non-Quiz tasks; with the backend, it gains configuration, Quiz solving, and status IPC.
- This dual standalone/backend model predates the Tauri rewrite and is a product contract inherited from `uXuexitongJS`, not an accidental fallback introduced by the current implementation.
- Dependency on Chaoxing DOM structure is inherent to third-party page automation. Review how selectors, waits, iframe transitions, and failure boundaries are isolated; do not label DOM dependency itself as a code defect.
- The project may defer README, release notes, and public documentation until the release phase. Evaluate documentation completeness relative to the stated project stage and historical release workflow.
- Remote WebView security findings must be based on the effective WebView label, remote-origin scope, capability merging, and exact allowed commands. Do not infer broad access from the presence of Tauri IPC alone.
- WebView startup and navigation conclusions must be verified against the actual Tauri creation order and logs. Small timing changes can affect WebView2 initial navigation; avoid adding startup `reload` calls without explicit state evidence.

## Reporting Discipline

- Lead with verified behavior and evidence, not a numerical score or a generic checklist.
- State uncertainty explicitly when intent, runtime reachability, or historical cost cannot be proven.
- Large diffs, deleted code, or replaced architecture do not by themselves prove expensive failed experimentation. Determine whether the old path delivered interim value and whether the replacement was staged.
- Claims about age, potential, seniority, rarity, or growth rate are inferences rather than repository facts. Keep them conditional and avoid false numerical precision.
- Do not manufacture weaknesses to make a review appear balanced. A review may conclude that a suspected issue is a reasonable tradeoff or not a defect.
