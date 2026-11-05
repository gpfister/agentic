# Agentic Workspace

Workspace coordinator for developing and maintaining **Google Antigravity** plugins, alongside a centralized **Obsidian Vault** for documentation, architecture decision records (ADRs), and detailed agent session tracking.

## Repositories & Sub-projects

| Project | Type | Description |
| :--- | :--- | :--- |
| **`agentic-coding-plugin/`** | Antigravity Plugin | Structured 7-stage software development companion (`@coding`) with clean code reviews, local deployment verification, Question Relay Protocol inquiry routing, and documentation maintenance. |
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
   - **Pure Subagents** (`@coding-clarify`, `@coding-deploy`, `@coding-review`): Exclusively run under `@coding`, omit `ask_question` from tools, and always relay inquiries via `send_message`.
   - **Dual-Mode Subagents** (`@coding-investigate`, `/project-grooming`, `@coding-monitor`, `@coding-research`): Dynamically detect caller ID; relay through the parent orchestrator when delegated, or call `ask_question` directly when invoked standalone in root session turns.
