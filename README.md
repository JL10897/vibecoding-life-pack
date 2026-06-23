# Vibecoding Life Pack

Personal life pack for maintaining Cursor, Claude Code, and Codex skills across devices.

The repository is the source of truth. Agent folders are installation targets.

## Goals

- Keep reusable skills and agent workflows in one GitHub repository.
- Make new-device setup fast with one install command.
- Keep multi-device changes mergeable through a canonical + device override model.
- Automatically commit life pack changes at the end of agent sessions so local edits are not forgotten.

## Repository Model

```text
canonical/        Shared source of truth.
devices/          Small per-device overrides.
bin/              Maintenance commands.
docs/             Merge, rollback, and manifest documentation.
manifest.yaml     Machine-readable inventory.
```

Use `canonical/` for anything that should travel across machines. Use `devices/<device-id>/` only when a setting or skill really belongs to one machine.

## Quick Start

```bash
git clone <your-github-url> ~/vibecoding-life-pack
cd ~/vibecoding-life-pack
./install.sh
```

Default install mode is symlink mode. In symlink mode, agent directories point back to this repository, so a `git pull` updates installed skills immediately.

## Daily Workflow

Check current state:

```bash
bin/vibe-status
```

Save local changes:

```bash
bin/vibe-save --source manual
```

Pull and validate:

```bash
./sync.sh
```

`sync.sh` runs:

```text
vibe-save -> git pull --rebase -> vibe-merge-check -> vibe-save
```

## Autosave

Autosave is handled by `bin/vibe-save`. It stages all life pack repository changes and creates a local commit when changes exist.

Autosave does not push in v1.

Commit message shape:

```text
chore(life-pack): autosave changes from <source> on <device-id>

Source: <source>
Device: <device-id>
Timestamp: <iso-timestamp>
```

Cursor can call this through a `sessionEnd` hook. Claude Code and Codex should use native hooks if available, or wrappers that call `bin/vibe-save` after the agent exits.

## Merge Rules

Read `docs/merge-policy.md` before resolving conflicts.

Short version:

- Shared behavior belongs in `canonical/`.
- Machine-only behavior belongs in `devices/<device-id>/`.
- If two devices edit the same skill, merge the intent, not only the text.
- After resolving conflicts, run `bin/vibe-merge-check`.

## Rollback

Read `docs/rollback.md` for recipes.

Common rollback:

```bash
git status
git diff
git restore path/to/file
```

To undo the last autosave commit but keep its changes unstaged:

```bash
git reset --mixed HEAD~1
```

## Manifest

`manifest.yaml` tracks agents, install targets, skills, external packs, devices, and autosave policy.

See `docs/manifest-schema.md` when adding new skills or agent sections.
