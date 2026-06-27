#!/usr/bin/env bash
set -euo pipefail

MODE="symlink"
DEVICE_ID="${VIBE_DEVICE_ID:-$(hostname | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9._-' '-')}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="${2:-symlink}"
      shift 2
      ;;
    --device)
      DEVICE_ID="${2:?missing device id}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ "$MODE" != "symlink" && "$MODE" != "copy" ]]; then
  echo "install.sh: --mode must be symlink or copy" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"
BACKUP_ROOT="$REPO_ROOT/.life-pack/backups/$(date -u +"%Y%m%dT%H%M%SZ")"

expand_target() {
  local path="$1"
  echo "${path/#\~/$HOME}"
}

backup_existing() {
  local target="$1"
  mkdir -p "$BACKUP_ROOT"
  local backup="$BACKUP_ROOT${target}"
  mkdir -p "$(dirname "$backup")"
  mv "$target" "$backup"
  echo "install.sh: backed up $target -> $backup"
}

install_one() {
  local source_path="$1"
  local target_path="$2"

  mkdir -p "$(dirname "$target_path")"

  if [[ -L "$target_path" ]]; then
    local current_target
    current_target="$(readlink "$target_path")"
    if [[ "$current_target" == "$source_path" ]]; then
      echo "install.sh: already linked $target_path"
      return 0
    fi
    backup_existing "$target_path"
  elif [[ -e "$target_path" ]]; then
    backup_existing "$target_path"
  fi

  if [[ "$MODE" == "symlink" ]]; then
    ln -s "$source_path" "$target_path"
  else
    cp -R "$source_path" "$target_path"
  fi

  echo "install.sh: installed $target_path"
}

install_collection() {
  local source_dir="$1"
  local target_dir="$2"

  [[ -d "$source_dir" ]] || return 0
  mkdir -p "$target_dir"

  local source_path
  for source_path in "$source_dir"/* "$source_dir"/.[!.]* "$source_dir"/..?*; do
    [[ -e "$source_path" ]] || continue
    install_one "$source_path" "$target_dir/$(basename "$source_path")"
  done
}

install_cursor_hooks() {
  local source_dir="$1"
  [[ -d "$source_dir" ]] || return 0

  local hooks_dir
  hooks_dir="$(expand_target "~/.cursor/hooks")"
  mkdir -p "$hooks_dir"

  local source_path
  for source_path in "$source_dir"/* "$source_dir"/.[!.]* "$source_dir"/..?*; do
    [[ -e "$source_path" ]] || continue
    if [[ "$(basename "$source_path")" == "hooks.json" ]]; then
      install_one "$source_path" "$(expand_target "~/.cursor/hooks.json")"
    else
      install_one "$source_path" "$hooks_dir/$(basename "$source_path")"
    fi
  done
}

install_shared_skills() {
  # Shared skills are authored once under canonical/shared/skills and fanned
  # out to all three consumer dirs so Cursor, Claude Code, and Codex all see
  # them. Run before platform-specific installs so a platform copy can override.
  local shared_skills_dir="$REPO_ROOT/canonical/shared/skills"
  [[ -d "$shared_skills_dir" ]] || return 0

  local cursor_skills claude_skills codex_skills
  cursor_skills="$(expand_target "~/.cursor/skills")"
  claude_skills="$(expand_target "~/.claude/skills")"
  codex_skills="$(expand_target "~/.codex/skills")"

  local source_path name
  for source_path in "$shared_skills_dir"/* "$shared_skills_dir"/.[!.]* "$shared_skills_dir"/..?*; do
    [[ -e "$source_path" ]] || continue
    name="$(basename "$source_path")"
    [[ "$name" == .* ]] && continue
    install_one "$source_path" "$cursor_skills/$name"
    install_one "$source_path" "$claude_skills/$name"
    install_one "$source_path" "$codex_skills/$name"
  done
}

install_agent_tree() {
  local root="$1"

  install_collection "$root/cursor/skills" "$(expand_target "~/.cursor/skills")"
  install_collection "$root/cursor/rules" "$(expand_target "~/.cursor/rules")"
  install_cursor_hooks "$root/cursor/hooks"

  install_collection "$root/claude-code/skills" "$(expand_target "~/.claude/skills")"
  install_collection "$root/claude-code/commands" "$(expand_target "~/.claude/commands")"
  install_collection "$root/claude-code/settings" "$(expand_target "~/.claude/settings")"

  install_collection "$root/codex/skills" "$(expand_target "~/.codex/skills")"
  install_collection "$root/codex/prompts" "$(expand_target "~/.codex/prompts")"
  install_collection "$root/codex/settings" "$(expand_target "~/.codex/settings")"
}

echo "install.sh: installing canonical content in $MODE mode"
install_shared_skills
install_agent_tree "$REPO_ROOT/canonical"

if [[ -d "$REPO_ROOT/devices/$DEVICE_ID" ]]; then
  echo "install.sh: applying device overrides for $DEVICE_ID"
  install_agent_tree "$REPO_ROOT/devices/$DEVICE_ID"
else
  echo "install.sh: no device overrides for $DEVICE_ID"
fi

echo "install.sh: done"
