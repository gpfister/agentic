# Agentic Workspace

Workspace coordinator for developing and maintaining **Google Antigravity** plugins, alongside a centralized **Obsidian Vault** for documentation, architecture decision records (ADRs), and detailed agent session tracking.

## Repositories & Sub-projects

| Project | Type | Description |
| :--- | :--- | :--- |
| **`agentic-coding-plugin/`** | Antigravity Plugin | Starter coding assistant plugin featuring custom skills, rules, and MCP configurations. |
| **`agentic-obsidian/`** | Obsidian Vault | Documentation hub containing session transcripts, architecture guidelines, and plugin docs. |

## Quick Start

### 1. Synchronize Antigravity Sessions into Obsidian

Extract sessions from `~/.gemini/antigravity-cli/brain/<session_id>` with full reasoning, tools invoked, tasks, and artifacts into Obsidian markdown notes:

```bash
# Sync specific session
python3 scripts/sync_sessions.py <session_id>

# Sync the most recent session
python3 scripts/sync_sessions.py --latest

# Sync all sessions
python3 scripts/sync_sessions.py --all
```

### 2. Parallel Sessions via Git Worktrees

Run multiple concurrent Antigravity sessions or agent tasks in isolated worktrees:

```bash
# List active worktrees across repos
python3 scripts/worktree.py list

# Spin up a parallel worktree workspace
python3 scripts/worktree.py create feature-x

# Remove worktrees and delete branches once merged
python3 scripts/worktree.py remove feature-x -D
```

### 3. Development Guidelines

See [AGENTS.md](file:///Users/gpfister/Development/Projects/gpfister/agentic/AGENTS.md) for full workspace conventions, plugin authoring standards, and session tracking protocols.
