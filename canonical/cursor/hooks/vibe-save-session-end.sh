#!/usr/bin/env bash
set -euo pipefail

# Cursor command hooks receive event JSON on stdin. Autosave does not need it,
# but consuming stdin prevents broken pipe surprises in some hook runners.
if [[ ! -t 0 ]]; then
  cat >/dev/null || true
fi

if [[ -n "${VIBE_LIFE_PACK_HOME:-}" ]]; then
  REPO_ROOT="$VIBE_LIFE_PACK_HOME"
else
  SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
  REPO_ROOT="$(cd "$(dirname "$SCRIPT_PATH")/../../.." && pwd)"
fi

"$REPO_ROOT/bin/vibe-save" --source cursor-sessionEnd
