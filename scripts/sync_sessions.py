#!/usr/bin/env python3
"""Antigravity Session Synchronizer for Obsidian Vault.

Extracts session transcripts, reasoning traces, tool invocations, and artifacts
from ~/.gemini/antigravity-cli/brain/<session_id> and writes rich Obsidian markdown notes.
"""

import argparse
import datetime
import json
import os
from pathlib import Path
import re
import shutil
import sys
from typing import Any, Dict, List, Optional


def find_default_brain_dir() -> Path:
    env_brain = os.environ.get("ANTIGRAVITY_BRAIN_DIR")
    if env_brain:
        return Path(env_brain).expanduser().resolve()
    app_brain = (Path.home() / ".gemini" / "antigravity" / "brain").resolve()
    cli_brain = (Path.home() / ".gemini" / "antigravity-cli" / "brain").resolve()
    if app_brain.exists():
        return app_brain
    return cli_brain


def clean_user_input(text: str) -> str:
    """Extract core prompt from user request tags if present."""
    match = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def parse_session_transcript(session_dir: Path) -> Dict[str, Any]:
    logs_dir = session_dir / ".system_generated" / "logs"
    transcript_file = logs_dir / "transcript_full.jsonl"
    if not transcript_file.exists():
        transcript_file = logs_dir / "transcript.jsonl"

    if not transcript_file.exists():
        raise FileNotFoundError(f"No transcript found in {logs_dir}")

    steps: List[Dict[str, Any]] = []
    with open(transcript_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                steps.append(data)
            except json.JSONDecodeError as e:
                print(f"Warning: line {line_num} in {transcript_file.name} is invalid JSON: {e}", file=sys.stderr)

    return {
        "session_id": session_dir.name,
        "session_dir": session_dir,
        "transcript_path": transcript_file,
        "steps": steps,
    }


def analyze_session(data: Dict[str, Any]) -> Dict[str, Any]:
    steps = data["steps"]
    session_id = data["session_id"]
    session_dir = data["session_dir"]

    tool_counts: Dict[str, int] = {}
    distinct_tools = set()
    initial_user_prompt = ""
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    total_input_tokens = 0
    total_output_tokens = 0

    artifacts_found = []
    for item in session_dir.iterdir():
        if item.name.startswith("."):
            continue
        if item.name == "scratch":
            scratch_files = [f.name for f in item.glob("*") if f.is_file()]
            if scratch_files:
                artifacts_found.extend([f"scratch/{f}" for f in scratch_files])
            continue
        if item.is_file():
            artifacts_found.append(item.name)
        elif item.is_dir():
            artifacts_found.append(f"{item.name}/")

    for step in steps:
        created_at = step.get("created_at")
        if created_at:
            if not start_time:
                start_time = created_at
            end_time = created_at

        step_type = step.get("type")
        if step_type == "USER_INPUT" and not initial_user_prompt:
            content = step.get("content", "")
            initial_user_prompt = clean_user_input(content)

        if step_type == "PLANNER_RESPONSE":
            total_input_tokens += step.get("input_tokens", 0) or 0
            total_output_tokens += step.get("output_tokens", 0) or 0

            tool_calls = step.get("tool_calls") or []
            for tc in tool_calls:
                call_info = tc.get("call", {}) if "call" in tc else tc
                tool_name = call_info.get("tool", "") or call_info.get("name", "")
                if not tool_name and "tool_name" in call_info:
                    tool_name = call_info["tool_name"]
                if not tool_name:
                    tool_name = "unknown_tool"
                tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
                distinct_tools.add(tool_name)

    return {
        "session_id": session_id,
        "initial_prompt": initial_user_prompt or "Antigravity Session",
        "start_time": start_time or "Unknown",
        "end_time": end_time or "Unknown",
        "total_steps": len(steps),
        "tool_counts": tool_counts,
        "distinct_tools": sorted(list(distinct_tools)),
        "artifacts": artifacts_found,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "steps": steps,
        "session_dir": session_dir,
    }


def format_markdown_note(analysis: Dict[str, Any], vault_sessions_dir: Path) -> str:
    session_id = analysis["session_id"]
    initial_prompt = analysis["initial_prompt"].replace("\n", " ")
    if len(initial_prompt) > 80:
        title_summary = initial_prompt[:77] + "..."
    else:
        title_summary = initial_prompt

    start_date = analysis["start_time"]
    distinct_tools = analysis["distinct_tools"]
    tool_counts = analysis["tool_counts"]
    artifacts = analysis["artifacts"]
    steps = analysis["steps"]

    attachments_dir = vault_sessions_dir / "attachments" / session_id
    if artifacts:
        attachments_dir.mkdir(parents=True, exist_ok=True)
        for art in artifacts:
            src = analysis["session_dir"] / art
            if src.is_file():
                dest = attachments_dir / Path(art).name
                shutil.copy2(src, dest)

    md = []
    escaped_title = title_summary.replace('"', '\\"')
    # YAML Frontmatter
    md.append("---")
    md.append(f'session_id: "{session_id}"')
    md.append(f'title: "{escaped_title}"')
    md.append(f'date: "{start_date}"')
    md.append("tags:")
    md.append("  - antigravity-session")
    md.append("  - plugin-dev")
    md.append("tools_used:")
    for t in distinct_tools:
        md.append(f"  - {t}")
    md.append(f"total_steps: {analysis['total_steps']}")
    if artifacts:
        md.append("artifacts:")
        for a in artifacts:
            md.append(f"  - {a}")
    md.append("---\n")

    # Title & Overview
    md.append(f"# Session: {title_summary}\n")
    md.append(f"**Session ID:** `{session_id}`  ")
    md.append(f"**Started:** `{start_date}` | **Ended:** `{analysis['end_time']}`  ")
    md.append(f"**Total Steps:** `{analysis['total_steps']}` | **Tokens:** In `{analysis['input_tokens']}` / Out `{analysis['output_tokens']}`\n")

    # Tool Invocations Summary
    md.append("## Tools Executed\n")
    if tool_counts:
        md.append("| Tool Name | Invocations |")
        md.append("| :--- | :--- |")
        for tool_name, count in sorted(tool_counts.items(), key=lambda x: -x[1]):
            md.append(f"| `{tool_name}` | {count} |")
        md.append("")
    else:
        md.append("_No tools were invoked in this session._\n")

    # Artifacts Section
    md.append("## Artifacts & Outputs\n")
    if artifacts:
        for a in artifacts:
            rel_link = f"attachments/{session_id}/{Path(a).name}"
            md.append(f"- 📄 [{a}]({rel_link})")
        md.append("")
    else:
        md.append("_No artifacts generated during this session._\n")

    # Detailed Timeline
    md.append("## Session Trajectory\n")

    for i, step in enumerate(steps):
        step_idx = step.get("step_index", i)
        step_type = step.get("type", "UNKNOWN")
        source = step.get("source", "")
        created = step.get("created_at", "")

        if step_type == "USER_INPUT":
            raw_content = step.get("content", "")
            user_clean = clean_user_input(raw_content)
            md.append(f"### 👤 User (Step {step_idx} - {created})\n")
            md.append(f"{user_clean}\n")

        elif step_type == "PLANNER_RESPONSE":
            thinking = step.get("thinking", "").strip()
            tool_calls = step.get("tool_calls") or []

            md.append(f"### 🤖 Agent (Step {step_idx} - {created})\n")
            if thinking:
                md.append("> [!quote]- 💭 Reasoning Trace")
                for line in thinking.splitlines():
                    md.append(f"> {line}")
                md.append("")

            if tool_calls:
                for tc in tool_calls:
                    call = tc.get("call", {}) if "call" in tc else tc
                    name = call.get("tool") or call.get("name") or "tool"
                    args = call.get("args") or call.get("arguments") or {}
                    args_str = json.dumps(args, indent=2, ensure_ascii=False)
                    md.append(f"> [!example]- 🛠️ Tool Call: `{name}`")
                    md.append(f"> ```json\n{args_str}\n> ```\n")

            content = step.get("content", "").strip()
            if content:
                md.append(f"{content}\n")

        elif step_type == "GENERIC":
            content = step.get("content", "")
            if content:
                # Often tool output
                preview = content.strip()
                if len(preview) > 500:
                    preview_text = preview[:500] + "\n\n... (truncated for display) ..."
                else:
                    preview_text = preview
                md.append(f"> [!note]- ⚙️ Execution Result (Step {step_idx})")
                for line in preview_text.splitlines():
                    md.append(f"> {line}")
                md.append("")

    return "\n".join(md)


def sync_session_by_dir(session_dir: Path, vault_dir: Path) -> Path:
    sessions_dir = vault_dir / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    data = parse_session_transcript(session_dir)
    analysis = analyze_session(data)
    note_content = format_markdown_note(analysis, sessions_dir)

    target_file = sessions_dir / f"{session_dir.name}.md"
    target_file.write_text(note_content, encoding="utf-8")
    return target_file


def get_latest_session_dir(brain_dir: Path) -> Optional[Path]:
    candidates = [p for p in brain_dir.iterdir() if p.is_dir() and not p.name.startswith(".")]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def main():
    parser = argparse.ArgumentParser(description="Sync Antigravity session transcripts into Obsidian Vault.")
    parser.add_argument("session_id", nargs="?", help="Specific session UUID to sync")
    parser.add_argument("--latest", action="store_true", help="Sync the most recently active session")
    parser.add_argument("--all", action="store_true", help="Sync all sessions in the brain folder")
    parser.add_argument("--brain-dir", help="Path to Antigravity brain directory")
    parser.add_argument("--vault-dir", default="./agentic-obsidian", help="Path to Obsidian vault")

    args = parser.parse_args()

    brain_dir = Path(args.brain_dir).expanduser().resolve() if args.brain_dir else find_default_brain_dir()
    vault_dir = Path(args.vault_dir).resolve()

    if not brain_dir.exists():
        print(f"Error: Brain directory not found at {brain_dir}", file=sys.stderr)
        sys.exit(1)

    if not vault_dir.exists():
        print(f"Error: Vault directory not found at {vault_dir}", file=sys.stderr)
        sys.exit(1)

    if args.all:
        session_dirs = [p for p in brain_dir.iterdir() if p.is_dir() and not p.name.startswith(".")]
        print(f"Found {len(session_dirs)} session(s) in {brain_dir}")
        for s_dir in session_dirs:
            try:
                target = sync_session_by_dir(s_dir, vault_dir)
                print(f"Synced: {s_dir.name} -> {target.relative_to(vault_dir.parent)}")
            except Exception as e:
                print(f"Failed to sync {s_dir.name}: {e}", file=sys.stderr)
        return

    target_session_dir: Optional[Path] = None
    if args.latest:
        target_session_dir = get_latest_session_dir(brain_dir)
        if not target_session_dir:
            print("Error: No sessions found in brain directory.", file=sys.stderr)
            sys.exit(1)
    elif args.session_id:
        target_session_dir = brain_dir / args.session_id
        if not target_session_dir.exists():
            print(f"Error: Session {args.session_id} not found in {brain_dir}", file=sys.stderr)
            sys.exit(1)
    else:
        # Default to current conversation id or latest
        target_session_dir = get_latest_session_dir(brain_dir)
        if not target_session_dir:
            print("Error: No session ID provided and no sessions found.", file=sys.stderr)
            sys.exit(1)

    try:
        target_file = sync_session_by_dir(target_session_dir, vault_dir)
        print(f"Successfully synced session: {target_session_dir.name}")
        print(f"Saved to: {target_file}")
    except Exception as e:
        print(f"Error syncing session {target_session_dir.name}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
