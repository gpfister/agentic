# Agentic Workspace

Workspace coordinator for developing and maintaining **Google Antigravity** plugins, alongside a centralized **Obsidian Vault** for documentation, architecture decision records (ADRs), and detailed agent session tracking.

## Repositories & Sub-projects

| Project | Type | Description |
| :--- | :--- | :--- |
| **`agentic-coding-plugin/`** | Antigravity Plugin | Structured 6-stage software development companion (`@coding`) with clean code reviews and after-each-phase documentation maintenance. |
| **`agentic-coding-tui/`** | TUI Application | Standalone Textual terminal user interface assistant integrating Google ADK workflows and 100% transparent pass-through background rendering. |
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
