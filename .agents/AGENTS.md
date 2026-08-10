# Project Rules & Engineering Principles

## 1. Audit Existing Architecture Before Invention (禁造重复轮子 & 结合已有设计)

- **Inspect Established Patterns First**:
  Before implementing any new feature, bug fix, or codegen logic, thoroughly audit the existing codebase for pre-existing utility macros, helper crates, and architectural patterns (e.g. `auto_handler` proc-macro).
- **Extend Rather Than Duplicate**:
  New capabilities must integrate into and extend existing pipelines (e.g., adding TypeScript generation into `auto_handler` alongside permissions JSON sync) rather than introducing standalone scripts, ad-hoc string parsers, or fragmented initialization boilerplate.
- **Strict Anti-Wheel Policy**:
  NEVER hand-roll custom implementations for problems solved by established compiler features or official crates (e.g., hand-rolled AST string-to-TS type mappers like `rust_type_to_ts` vs. official reflection with `tauri_specta`).

## 2. Compile-Time Codegen & Macro Pipeline Abstraction (宏与代码生成标准)

- **Unified Macro Side-Effect Pipeline**:
  In projects using proc-macros for code/handler registration, all compile-time side-effects (e.g. permission JSON sync, TypeScript bindings export, routing generation) MUST be structured as parallel, co-located tasks within a single AST traversal pipeline in the macro expansion.
- **Entrypoint Cleanliness Invariant**:
  Application entry points (`src/lib.rs`, `src/main.rs`) MUST remain 100% clean, native, and free of verbose generation/export boilerplate.
- **Preserve System Routing Integrities**:
  Sub-system helpers or macro expansions MUST NOT break or replace primary framework handlers (e.g., replacing Tauri's `auto_handler` with sub-crate handlers that break unannotated IPC commands).

## 3. Scale-Invariant Proportional Layout Architecture (齐次比例布局规范)

- **Acknowledge Proportional Alignment Design**:
  In this project (`uxuescript`), percentage-based layout values in CSS (`vw`, `vh`, `%`, `flex: 1`) combined with `LogicalSize` scale factors in Rust (e.g., `logical_size.width * 0.51`, `logical_size.height * 0.46` in `webview.rs`) constitute an intentional, scale-invariant proportional layout architecture.
- **Do Not Criticize Proportional Factors as "Hardcoded"**:
  Do NOT criticize or label these scale-invariant percentage/proportional values in `webview.rs` or CSS as "hardcoded hacky numbers" ("硬编码临时方案"). Recognize them as an intentional, scale-invariant design for native Webview alignment across screens.

## 4. Pure Data Decoupling & Clean Architecture Invariants (数据与操作解耦与代码命名规范)

- **Pure DTO Invariant**:
  Config and payload structs (`LLMConfig`, `LLMProvider`) MUST remain 100% pure data objects (POD / DTO). NEVER add getters/setters, closure callbacks (`with_active_provider`), or Mutex-locking methods onto data structs. Keep locking and operations strictly in command/service handlers.
- **Directory Hierarchy & Anti-Redundancy**:
  Group templates in subdirectories (e.g., `requests/default.json`). Never repeat directory names in filenames (e.g. use `requests/default.json`, not `requests/request.default.json`).
- **Single-Responsibility Helper Splitting**:
  Split monolithic match blocks into focused, single-responsibility helper functions. Avoid repeating module or protocol prefixes in function names when already scoped in submodules (e.g., `chat_completions()` instead of `solve_openai_chat_completions()`).
- **Idiomatic Rust Matching**:
  Do NOT use `ref` when pattern-matching `Copy` or reference types (`Option<&str>`). Keep Serde attributes minimal and natural.
