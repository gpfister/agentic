#!/usr/bin/env python3
"""Worktree Management Utility for Agentic Multi-Repo Workspace.

Allows running multiple Antigravity agent sessions and development workflows
in parallel using isolated Git worktrees across the root workspace and sub-repositories.
"""

import argparse
import os
from pathlib import Path
import subprocess
import sys
from typing import Dict, List, Optional, Tuple


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORKTREES_DIR = WORKSPACE_ROOT / ".worktrees"


def run_git(cmd: List[str], cwd: Path) -> Tuple[int, str, str]:
    res = subprocess.run(["git"] + cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()


def discover_repos(root: Path) -> Dict[str, Path]:
    """Find root repository and all sub-repositories (containing .git)."""
    repos: Dict[str, Path] = {"root": root}
    for item in root.iterdir():
        if item.name.startswith(".") or item.name == "scripts":
            continue
        if item.is_dir() and (item / ".git").exists():
            repos[item.name] = item
    return repos


def sanitize_branch_name(name: str) -> str:
    cleaned = name.replace(" ", "-").replace("/", "-")
    return cleaned


def cmd_list(repos: Dict[str, Path]):
    print("=== Active Git Worktrees ===")
    for name, repo_path in sorted(repos.items()):
        code, out, err = run_git(["worktree", "list"], cwd=repo_path)
        print(f"\n📂 Repository: {name} ({repo_path.relative_to(WORKSPACE_ROOT) if repo_path != WORKSPACE_ROOT else '.'})")
        if code == 0 and out:
            for line in out.splitlines():
                print(f"   {line}")
        else:
            print(f"   (Failed or empty: {err})")


def cmd_create(
    name: str,
    repos: Dict[str, Path],
    target_repo: Optional[str] = None,
    branch_name: Optional[str] = None,
    base_ref: Optional[str] = None,
):
    clean_name = sanitize_branch_name(name)
    session_dir = DEFAULT_WORKTREES_DIR / clean_name
    session_dir.mkdir(parents=True, exist_ok=True)

    selected_repos: Dict[str, Path] = {}
    if target_repo:
        if target_repo not in repos:
            print(f"Error: Repository '{target_repo}' not found. Available: {list(repos.keys())}", file=sys.stderr)
            sys.exit(1)
        selected_repos = {target_repo: repos[target_repo]}
    else:
        # Default: create worktrees for all sub-repos (plugins, vault) and root
        selected_repos = repos

    print(f"Creating parallel worktree session '{clean_name}' in: {session_dir}")

    for r_name, r_path in selected_repos.items():
        wt_path = session_dir / (r_name if r_name != "root" else "agentic-root")
        if wt_path.exists():
            print(f"⚠️  Worktree path already exists: {wt_path.relative_to(WORKSPACE_ROOT)}")
            continue

        actual_branch = branch_name or f"session/{clean_name}"
        if r_name != "root":
            actual_branch = f"session/{clean_name}-{r_name}"

        # Check if branch already exists
        check_code, _, _ = run_git(["rev-parse", "--verify", actual_branch], cwd=r_path)
        
        args = ["worktree", "add"]
        if check_code == 0:
            # Branch exists, attach worktree to it
            args.extend([str(wt_path), actual_branch])
        else:
            # Create new branch
            args.extend(["-b", actual_branch, str(wt_path)])
            if base_ref:
                args.append(base_ref)

        code, out, err = run_git(args, cwd=r_path)
        if code == 0:
            print(f"✅ [{r_name}] Worktree created at: {wt_path.relative_to(WORKSPACE_ROOT)} (branch: {actual_branch})")
        else:
            print(f"❌ [{r_name}] Failed to create worktree: {err}", file=sys.stderr)


def cmd_remove(name: str, repos: Dict[str, Path], delete_branch: bool = False):
    clean_name = sanitize_branch_name(name)
    session_dir = DEFAULT_WORKTREES_DIR / clean_name

    print(f"Removing worktrees for session '{clean_name}'...")
    for r_name, r_path in repos.items():
        wt_path = session_dir / (r_name if r_name != "root" else "agentic-root")
        if wt_path.exists():
            code, out, err = run_git(["worktree", "remove", "--force", str(wt_path)], cwd=r_path)
            if code == 0:
                print(f"✅ [{r_name}] Removed worktree: {wt_path.name}")
            else:
                print(f"⚠️ [{r_name}] Could not remove via git worktree ({err}). Removing directory manually...")
                if wt_path.is_dir():
                    import shutil
                    shutil.rmtree(wt_path, ignore_errors=True)

            if delete_branch:
                actual_branch = f"session/{clean_name}" if r_name == "root" else f"session/{clean_name}-{r_name}"
                b_code, _, b_err = run_git(["branch", "-D", actual_branch], cwd=r_path)
                if b_code == 0:
                    print(f"   Deleted branch: {actual_branch}")

        # Prune worktree refs
        run_git(["worktree", "prune"], cwd=r_path)

    if session_dir.exists() and not any(session_dir.iterdir()):
        session_dir.rmdir()
        print(f"Cleaned up empty directory: {session_dir.relative_to(WORKSPACE_ROOT)}")


def cmd_prune(repos: Dict[str, Path]):
    print("Pruning stale worktrees across all repositories...")
    for name, path in repos.items():
        code, out, err = run_git(["worktree", "prune", "-v"], cwd=path)
        if out or err:
            print(f"[{name}] {out or err}")
        else:
            print(f"[{name}] Clean.")


def main():
    parser = argparse.ArgumentParser(description="Git Worktree Coordinator for Parallel Agent Sessions.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    subparsers.add_parser("list", help="List active worktrees across all repositories")

    # create
    create_parser = subparsers.add_parser("create", help="Create a parallel worktree session")
    create_parser.add_argument("name", help="Session ID, feature name, or ticket identifier")
    create_parser.add_argument("--repo", help="Target specific repository (default: all)")
    create_parser.add_argument("--branch", help="Custom branch name")
    create_parser.add_argument("--base", help="Base branch/commit to branch from (default: HEAD)")

    # remove
    remove_parser = subparsers.add_parser("remove", help="Remove worktree session")
    remove_parser.add_argument("name", help="Session ID or name to remove")
    remove_parser.add_argument("--delete-branch", "-D", action="store_true", help="Delete associated branches")

    # prune
    subparsers.add_parser("prune", help="Prune dead worktree metadata across repositories")

    args = parser.parse_args()
    repos = discover_repos(WORKSPACE_ROOT)

    if args.command == "list":
        cmd_list(repos)
    elif args.command == "create":
        cmd_create(args.name, repos, target_repo=args.repo, branch_name=args.branch, base_ref=args.base)
    elif args.command == "remove":
        cmd_remove(args.name, repos, delete_branch=args.delete_branch)
    elif args.command == "prune":
        cmd_prune(repos)


if __name__ == "__main__":
    main()
