# ==============================================================================
# Agentic Workspace Makefile
# Multi-repository synchronization and management automation
# ==============================================================================

SHELL := /bin/bash

# Configuration
GITHUB_ORG ?= gpfister
GIT_PROTOCOL ?= ssh

ifeq ($(GIT_PROTOCOL),ssh)
GIT_BASE_URL := git@github.com:$(GITHUB_ORG)
else
GIT_BASE_URL := https://github.com/$(GITHUB_ORG)
endif

# Sub-repositories
REPOS := agentic-coding-tui agentic-coding-plugin agentic-issue-investigation-plugin agentic-obsidian agentic-project-documenting-plugin agentic-project-grooming-plugin agentic-prompt-triage-plugin agentic-task-monitoring-plugin agentic-topic-researching-plugin

.PHONY: all help sync clone pull fetch push status st diff worktrees sessions sessions-all clean

all: help

help:
	@echo "=================================================================="
	@echo "                   Agentic Workspace Automation                   "
	@echo "=================================================================="
	@echo "Usage: make <target> [VARIABLE=value]"
	@echo ""
	@echo "Targets:"
	@echo "  sync          Clone missing repos, pull all updates, and show status"
	@echo "  clone         Clone all sub-repositories if not present locally"
	@echo "  pull          Pull latest changes (fast-forward) across all repos"
	@echo "  fetch         Fetch remotes and prune deleted branches across all repos"
	@echo "  push          Push current branch commits across all repos"
	@echo "  status, st    Display branch and clean/dirty status across all repos"
	@echo "  diff          Show uncommitted changes across all repos"
	@echo "  worktrees     List active Git worktrees across the workspace"
	@echo "  sessions      Sync latest Antigravity session into Obsidian vault"
	@echo "  sessions-all  Sync all Antigravity sessions into Obsidian vault"
	@echo "  clean         Remove cache and temporary build files"
	@echo ""
	@echo "Variables:"
	@echo "  GITHUB_ORG    GitHub organization or user (default: $(GITHUB_ORG))"
	@echo "  GIT_PROTOCOL  Protocol for cloning: 'ssh' or 'https' (default: $(GIT_PROTOCOL))"
	@echo "=================================================================="

sync: clone pull status

clone:
	@echo -e "\033[1;34m==> Checking and cloning missing repositories...\033[0m"
	@for r in $(REPOS); do \
		if [ ! -d "$$r/.git" ]; then \
			echo -e "  \033[1;33mCloning $$r from $(GIT_BASE_URL)/$$r.git...\033[0m"; \
			git clone "$(GIT_BASE_URL)/$$r.git" "$$r" || { echo "❌ Failed to clone $$r"; exit 1; }; \
		else \
			echo -e "  \033[0;32m✓\033[0m $$r already cloned."; \
		fi; \
	done
	@echo -e "\033[1;32m✓ Repository check complete.\033[0m\n"

pull:
	@echo -e "\033[1;34m==> Pulling latest changes across all repositories...\033[0m"
	@echo -e "  \033[1;36mPulling root (agentic)...\033[0m"
	@git pull --ff-only 2>/dev/null || echo -e "  \033[1;33m⚠️ Could not fast-forward root (or uncommitted local changes exist)\033[0m"
	@for r in $(REPOS); do \
		if [ -d "$$r/.git" ]; then \
			echo -e "  \033[1;36mPulling $$r...\033[0m"; \
			git -C "$$r" pull --ff-only 2>/dev/null || echo -e "  \033[1;33m⚠️ Could not fast-forward $$r (or uncommitted local changes exist)\033[0m"; \
		else \
			echo -e "  \033[1;31m✗ $$r not found. Run 'make clone' first.\033[0m"; \
		fi; \
	done
	@echo -e "\033[1;32m✓ Pull complete.\033[0m\n"

fetch:
	@echo -e "\033[1;34m==> Fetching updates across all repositories...\033[0m"
	@echo -e "  \033[1;36mFetching root (agentic)...\033[0m"
	@git fetch --all --prune
	@for r in $(REPOS); do \
		if [ -d "$$r/.git" ]; then \
			echo -e "  \033[1;36mFetching $$r...\033[0m"; \
			git -C "$$r" fetch --all --prune; \
		fi; \
	done
	@echo -e "\033[1;32m✓ Fetch complete.\033[0m\n"

push:
	@echo -e "\033[1;34m==> Pushing changes across all repositories...\033[0m"
	@for r in $(REPOS); do \
		if [ -d "$$r/.git" ]; then \
			branch=$$(git -C "$$r" rev-parse --abbrev-ref HEAD 2>/dev/null); \
			if [ -n "$$branch" ] && [ "$$branch" != "HEAD" ]; then \
				echo -e "  \033[1;36mPushing $$r ($$branch)...\033[0m"; \
				git -C "$$r" push origin "$$branch" || echo -e "  \033[1;33m⚠️ Push failed for $$r\033[0m"; \
			fi; \
		fi; \
	done
	@echo -e "  \033[1;36mPushing root (agentic)...\033[0m"
	@git push origin HEAD || echo -e "  \033[1;33m⚠️ Push failed for root repository\033[0m"
	@echo -e "\033[1;32m✓ Push complete.\033[0m\n"

status st:
	@echo -e "\033[1;34m=== Repository Status Overview ===\033[0m"
	@repos="root $(REPOS)"; \
	for r in $$repos; do \
		if [ "$$r" = "root" ]; then \
			dir="."; \
			name="agentic (root)"; \
		else \
			dir="$$r"; \
			name="$$r"; \
		fi; \
		if [ -d "$$dir/.git" ]; then \
			branch=$$(git -C "$$dir" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached"); \
			dirty=$$(git -C "$$dir" status --porcelain 2>/dev/null); \
			ahead_behind=$$(git -C "$$dir" rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1 && git -C "$$dir" rev-list --left-right --count HEAD...@{u} 2>/dev/null || echo ""); \
			if [ -z "$$dirty" ]; then \
				status_str="\033[0;32mclean\033[0m"; \
			else \
				status_str="\033[0;31mmodified\033[0m"; \
			fi; \
			printf "  \033[1;37m%-28s\033[0m branch: \033[1;33m%-14s\033[0m [%b]" "$$name" "$$branch" "$$status_str"; \
			if [ -n "$$ahead_behind" ]; then \
				ahead=$$(echo "$$ahead_behind" | awk '{print $$1}'); \
				behind=$$(echo "$$ahead_behind" | awk '{print $$2}'); \
				if [ "$$ahead" -gt 0 ] || [ "$$behind" -gt 0 ]; then \
					printf " (ahead: %s, behind: %s)" "$$ahead" "$$behind"; \
				fi; \
			fi; \
			echo ""; \
			if [ -n "$$dirty" ]; then \
				git -C "$$dir" status -s | sed 's/^/      /'; \
			fi; \
		else \
			printf "  \033[1;31m%-28s NOT CLONED\033[0m (run 'make clone')\n" "$$name"; \
		fi; \
	done
	@echo ""

diff:
	@echo -e "\033[1;34m=== Uncommitted Diffs Across Repositories ===\033[0m"
	@repos="root $(REPOS)"; \
	for r in $$repos; do \
		if [ "$$r" = "root" ]; then \
			dir="."; \
			name="agentic (root)"; \
		else \
			dir="$$r"; \
			name="$$r"; \
		fi; \
		if [ -d "$$dir/.git" ]; then \
			d=$$(git -C "$$dir" diff 2>/dev/null); \
			if [ -n "$$d" ]; then \
				echo -e "\n\033[1;33m--- $$name ---\033[0m"; \
				git -C "$$dir" diff --stat; \
			fi; \
		fi; \
	done

worktrees:
	@python3 scripts/worktree.py list

sessions:
	@python3 scripts/sync_sessions.py --latest

sessions-all:
	@python3 scripts/sync_sessions.py --all

clean:
	@echo "Cleaning Python and OS cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.py[cod]" -delete 2>/dev/null || true
	@find . -name ".DS_Store" -delete 2>/dev/null || true
	@echo "Clean complete."
