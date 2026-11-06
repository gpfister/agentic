# Agentic Workspace

Workspace coordinator for developing and maintaining **Google Antigravity** plugins, alongside a centralized **Obsidian Vault** for documentation, architecture decision records (ADRs), and detailed agent session tracking.

## Repositories & Sub-projects

| Project | Type | Description |
| :--- | :--- | :--- |
| **`agentic-coding-plugin/`** | Antigravity Plugin | Structured 7-stage software development companion (`@coding`), operating as a Dual-Mode Orchestrator with Multi-Hop Relay, Anti-Direct-Coding Guardrails, clean code reviews, local deployment verification, and after-each-phase documentation maintenance. |
| **`agentic-issue-investigation-plugin/`** | Antigravity Plugin | Autonomous multi-repository issue investigation and root cause diagnosis plugin (`@coding-investigate`). |
| **`agentic-obsidian/`** | Obsidian Vault | Centralized documentation hub containing session transcripts, architecture guidelines, and plugin docs. |
| **`agentic-project-documenting-plugin/`** | Antigravity Plugin | Autonomous documentation and knowledge curation companion (`@coding-document`) for Obsidian vaults. |
| **`agentic-project-grooming-plugin/`** | Antigravity Plugin | Interactive project initialization and requirements grooming companion (`/project-grooming`) with 7-category interrogation. |
| **`agentic-prompt-triage-plugin/`** | Antigravity Plugin | Dynamic prompt triage and intent classification plugin using Laya Router System 1 model. |
| **`agentic-task-monitoring-plugin/`** | Antigravity Plugin | Telemetry and stream surveillance plugin (`@coding-monitor`) with anomaly detection and interactive pause gates. |
| **`agentic-topic-researching-plugin/`** | Antigravity Plugin | Autonomous multi-query deep web and literature research plugin (`@coding-research`) with evidence verification. |

## Quick Start

### 1. Synchronize Multi-Repository Workspace

The workspace uses independent Git repositories for each plugin and the Obsidian vault, ignored by the root repository and synchronized via `Makefile`:

```bash
# Check repository status across all projects
make status

# Pull all sub-repositories and clone any missing ones
make sync

# Push commits across all repositories
make push

# Clone sub-repositories only
make clone
```

### 2. Synchronize Antigravity Sessions into Obsidian

Extract sessions from `~/.gemini/antigravity-cli/brain/<session_id>` with full reasoning, tools invoked, tasks, and artifacts into Obsidian markdown notes:

```bash
# Sync specific session
python3 scripts/sync_sessions.py <session_id>

# Sync the most recent session
python3 scripts/sync_sessions.py --latest

# Sync all sessions
python3 scripts/sync_sessions.py --all
```

### 3. Parallel Sessions via Git Worktrees

Run multiple concurrent Antigravity sessions or agent tasks in isolated worktrees:

```bash
# List active worktrees across repos
make worktrees
# or: python3 scripts/worktree.py list

# Spin up a parallel worktree workspace
python3 scripts/worktree.py create feature-x

# Remove worktrees and delete branches once merged
python3 scripts/worktree.py remove feature-x -D
```

### 4. Development Guidelines

See [AGENTS.md](file:///Users/gpfister/Development/Projects/gpfister/agentic/AGENTS.md) for full workspace conventions, plugin authoring standards, and session tracking protocols.

---

## Cross-Cutting Architecture Principles & Ecosystem Standards

### Question Relay Protocol (Subagent User Inquiries)

In Google Antigravity, background worker subagents spawned via `invoke_subagent` face a rigid **60-second execution timeout** when executing `ask_question`. If human users take longer than 60 seconds to deliberate or respond, the turn aborts catastrophically.

To preserve interactive human-in-the-loop oversight without timing out, the workspace mandates the **Question Relay Protocol (Option 3)** formalized in [ADR-005](file:///Users/gpfister/Development/Projects/gpfister/agentic/agentic-obsidian/architecture/adr-005-question-relay-protocol.md) and [`AGENTS.md`](file:///Users/gpfister/Development/Projects/gpfister/agentic/AGENTS.md#32-question-relay-protocol-subagent-user-inquiries):

1. **Subagent Inquiries via `[QUESTION_RELAY_REQUEST]`**: Subagents never invoke `ask_question` while under orchestrator control; they dispatch a structured `[QUESTION_RELAY_REQUEST]` envelope via `send_message` to the parent caller and enter an idle state.
2. **Top-Level Orchestrator Prompting**: The parent orchestrator (`@coding` or root agent) intercepts the relay request and executes `ask_question` in the root turn (free of background timeouts), giving human users unlimited deliberation time.
3. **Reactive Wakeup via `[QUESTION_RELAY_RESPONSE]`**: The parent orchestrator packages the user's choice into `[QUESTION_RELAY_RESPONSE]` and sends it back to the subagent via `send_message`, reactively resuming worker execution.
4. **Agent Tiering & Tool Permissions**:
   - **Pure Subagents** (`@coding-clarify`, `@coding-deploy`, `@coding-review`, `@coding-merge`): Exclusively run under `@coding`, omit `ask_question` from tools, and always relay inquiries via `send_message`.
   - **Dual-Mode Orchestrators & Agents** (`@coding`, `@coding-investigate`, `/project-grooming`, `@coding-monitor`, `@coding-research`): Dynamically detect caller ID; relay through the parent orchestrator via multi-hop when delegated, or call `ask_question` directly when invoked standalone in root session turns.

### Artifact Approval Relay Protocol (Subagent Artifact Gates)

Similar to user inquiries, background worker subagents authoring interactive milestone artifacts (`specification.md`, `plan.md`, `issue-assessment.md`, `Project_Request_Grooming.md`, `research-report.md`) face the rigid **60-second execution timeout** if they invoke `write_file(RequestFeedback=True)`.

The workspace mandates the **Artifact Approval Relay Protocol** formalized in [ADR-006](file:///Users/gpfister/Development/Projects/gpfister/agentic/agentic-obsidian/architecture/adr-006-artifact-approval-relay-protocol.md):
1. **Authoring to Disk**: Background subagents write artifacts directly to disk without feedback metadata (`RequestFeedback=False` or omitted).
2. **Relay via `[ARTIFACT_APPROVAL_REQUEST]`**: Subagents dispatch `[ARTIFACT_APPROVAL_REQUEST]` to `caller_id` via `send_message` and enter an idle state.
3. **Root Presentation**: The root orchestrator presents the interactive gate via `write_file(RequestFeedback=True)` as the sole and final tool call of that turn (free of background execution timeouts).
4. **Reactive Wakeup via `[ARTIFACT_APPROVAL_RESPONSE]`**: User approval or feedback is returned downward to the waiting subagent.

### Dual-Mode Coding Orchestrator & Anti-Direct-Coding Guardrails

To resolve duplicate UI approval gates and protect against workflow bypass during automated handoffs (formalized in [ADR-008](file:///Users/gpfister/Development/Projects/gpfister/agentic/agentic-obsidian/architecture/adr-008-dual-mode-coding-orchestrator.md)):
1. **Dual-Mode Orchestration**: When `@coding` detects an upstream caller (`caller_id` present), it operates in **Subagent Mode**, multi-hop relaying all approval requests (`[ARTIFACT_APPROVAL_REQUEST]`) and user inquiries (`[QUESTION_RELAY_REQUEST]`) upward without rendering local gates or asking questions directly. In **Standalone Mode** (no `caller_id`), `@coding` directly handles gates and questions.
2. **Hard Anti-Direct-Coding Guardrails**: `@coding` is strictly a meta-orchestrator and **MUST NEVER** edit application source code, configs, or test suites directly. `write_file` is restricted to approval gate rendering in standalone mode; `run_command` is restricted to workspace inspection (`git status`). All implementation is delegated to `@coding-develop`.
3. **Pre-Clarified Fast-Path**: Skips Phase 1 (`coding-clarify`) for pre-clarified requirements while strictly enforcing Phase 2 and Phase 3 approval gates before code development begins.
