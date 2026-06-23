#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

bin/vibe-save --source sync-before-pull

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  GIT_TOPLEVEL="$(git rev-parse --show-toplevel)"
  if [[ "$GIT_TOPLEVEL" == "$SCRIPT_DIR" ]] && git remote get-url origin >/dev/null 2>&1; then
    git pull --rebase
  else
    echo "sync.sh: life pack repo has no origin remote; skipping pull."
  fi
else
  echo "sync.sh: life pack is not initialized as a git repository; skipping pull."
fi

bin/vibe-merge-check
bin/vibe-save --source sync-after-pull

echo "sync.sh: done"
