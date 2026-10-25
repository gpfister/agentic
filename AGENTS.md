# AGENTS.md — Agentic Workspace Coordinator

Welcome to the **agentic** workspace. This repository serves as the central coordination hub for authoring, maintaining, and integrating **Google Antigravity** plugins, alongside an **Obsidian Vault** for cross-cutting documentation and session intelligence.

---

## 1. Workspace Architecture & Layout

This workspace uses a multi-repo model. The root `agentic` repository orchestrates individual sub-repositories and provides workspace-wide automation and guidelines.

```text
agentic/
├── AGENTS.md                 # This coordination guide & agent instructions
├── README.md                 # Human-facing workspace overview
├── .gitignore                # Global workspace gitignore
├── scripts/                  # Workspace management and sync automation
│   └── sync_sessions.py      # Session transcript -> Obsidian vault exporter
├── gp-coding-plugin/         # Git Sub-repo: First Antigravity plugin
│   ├── plugin.json           # Plugin manifest
│   ├── rules/AGENTS.md       # Plugin-scoped agent rules & guidelines
│   ├── skills/               # Reusable progressive-disclosure skills
│   ├── hooks/                # Lifecycle hooks
│   ├── mcp_config.json       # Plugin-provided MCP servers
│   └── README.md
└── obsidian-vault/           # Git Sub-repo: Centralized Obsidian documentation vault
    ├── .obsidian/            # Obsidian workspace configuration
    ├── sessions/             # Formatted records of Antigravity agent sessions
    │   └── attachments/      # Artifacts and attachments linked to sessions
    ├── plugins/              # Documentation and specifications for each plugin
    ├── architecture/         # System designs, architecture decisions (ADRs)
    ├── templates/            # Obsidian note templates (sessions, plugins, ADRs)
    └── references/           # Antigravity APIs, SDK references, best practices
```

---

## 2. Antigravity Plugin Standards

All plugins within this ecosystem must adhere to the Antigravity Customization System standards:

### 2.1 File & Directory Conventions
- **Manifest (`plugin.json`)**: Every plugin must include a valid `plugin.json` at its root with `"name"` matching its directory name.
- **Rules (`rules/AGENTS.md`)**: Recommended location for plugin-specific instructions and rules. Merged into active rules when the plugin is active.
- **Skills (`skills/<skill_name>/SKILL.md`)**: Progressive-disclosure instructions with YAML frontmatter (`name`, `description`).
- **Hooks (`hooks.json` or `hooks/`)**: Lifecycle event handlers (pre-tool, post-tool, etc.). Native plugins must register `hooks.json` at root.
- **MCP Servers (`mcp_config.json`)**: Outlines MCP servers launched with the plugin, specifying command, args, and environment variables.

### 2.2 Isolation & Independence
- Each plugin lives in its own Git repository so it can be versioned, tagged, and distributed independently or installed via `agy plugin install`.
- Avoid hardcoded machine-local paths; use relative paths within plugin bundles.

---

## 3. Obsidian Vault & Session Tracking Protocol

The `obsidian-vault/` repository serves as the knowledge base for documentation, architectural decisions, and agent interaction telemetry.

### 3.1 Session Tracking
Antigravity stores session data in `~/.gemini/antigravity-cli/brain/<conversation-id>/`. Every significant session should be recorded into `obsidian-vault/sessions/<conversation-id>.md`.

Each session note must include:
1. **YAML Frontmatter**:
   ```yaml
   ---
   session_id: "<UUID>"
   title: "Descriptive Session Title"
   date: "YYYY-MM-DD HH:MM:SS"
   model: "Gemini 3.8 Flash (or active model)"
   status: "Completed | In-Progress"
   tags:
     - antigravity-session
     - plugin-dev
   tools_used:
     - run_command
     - write_file
     - ask_question
   step_count: 35
   artifacts:
     - "brain_artifact_1.md"
   ---
   ```
2. **Executive Summary**: Goals, actions taken, and outcomes.
3. **Tasks & Decisions**: High-level milestones and key design choices.
4. **Tool Invocations & Reasoning**: Collapsible callouts (`> [!example]- Reasoning Step X` or markdown `<details>`) detailing tool calls and internal chain of thought.
5. **Artifacts & File Changes**: Copies or links to artifacts created during the session.

### 3.2 Syncing Sessions
Use the bundled Python script to parse and export transcripts into the vault:

```bash
# Sync current / specific session by ID:
python3 scripts/sync_sessions.py <session-id>

# Sync the most recent session automatically:
python3 scripts/sync_sessions.py --latest

# Sync all sessions in the brain directory:
python3 scripts/sync_sessions.py --all
```

---

## 4. Agent Operational Instructions

When an Antigravity agent operates in this workspace:
1. **Identify the Scope**:
   - If working on a specific plugin (e.g. `gp-coding-plugin/`), follow that plugin's internal `rules/AGENTS.md` and keep commits isolated to that plugin's git repository.
   - If working across plugins or global setup, follow this root `AGENTS.md`.
2. **Update Documentation**:
   - When introducing or altering a plugin, update `obsidian-vault/plugins/<plugin-name>.md`.
   - When recording architectural decisions or standards, write to `obsidian-vault/architecture/`.
3. **Session Record Keeping**:
   - At the conclusion of major tasks or upon user request, trigger `scripts/sync_sessions.py` to archive the current conversation state into `obsidian-vault/sessions/`.
4. **Code Quality & Links**:
   - Always create clickable markdown links using `file://` scheme when referencing files and code symbols.
