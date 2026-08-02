# Vibecoding Life Pack

Personal life pack for maintaining **Cursor**, **Claude Code**, and **Codex** skills across devices.

The repository is the single source of truth. Per-agent `~/.<agent>/skills/` directories are installation targets (symlinks back to the repo). One skill, authored once, is consumable by all three agents on every device.

## Goals

- Keep reusable skills and agent workflows in one GitHub repository.
- Author a skill once and have it work on Cursor, Claude Code, and Codex without duplication.
- Make new-device setup fast with one install command.
- Keep multi-device changes mergeable through a canonical + device override model.
- Automatically commit life pack changes at the end of agent sessions so local edits are not forgotten.

## Repository Model

```text
canonical/                      Shared source of truth.
  shared/                       Cross-platform content.
    skills/                     Skills fanned out to ALL three agents.
    principles/  planning/  debugging/  review/
  cursor/                       Cursor-only content.
    skills/  rules/  hooks/
  claude-code/                  Claude Code-only content.
    skills/  commands/  settings/
  codex/                        Codex-only content.
    skills/  prompts/  settings/
devices/                        Small per-device overrides.
bin/                            Maintenance commands.
docs/                           Merge, rollback, and manifest documentation.
manifest.yaml                   Machine-readable inventory.
```

Use `canonical/` for anything that should travel across machines. Use `devices/<device-id>/` only when a setting or skill really belongs to one machine.

## Shared agent principles

`canonical/shared/principles/AgentPrinciples.md` is the single source of truth for personal rules that should load in every coding-agent session.

Running `./install.sh` links it into:

```text
~/.codex/AGENTS.md
~/.claude/rules/agent-principles.md
```

Codex and Claude Code load those files for every project. Project instructions can still add more specific rules.

Cursor global User Rules are managed in the application rather than by a supported repository file. Print the same source text with:

```bash
bin/vibe-print-cursor-user-rules
```

Paste the output into **Cursor Settings > Rules > User Rules**. Repeat this manual step after changing `AgentPrinciples.md`. Project-specific Cursor rules remain under `.cursor/rules/` with `alwaysApply: true` when they should apply to every task in that project.

## Skills: shared vs platform-only

A skill is a directory containing a `SKILL.md` with YAML frontmatter (`name`, `description`) followed by markdown. The format is the same for all three agents, so one file works everywhere unless a skill truly needs platform-specific fields.

- **Shared skill** → author at `canonical/shared/skills/<id>/SKILL.md`. `install.sh` symlinks it into `~/.cursor/skills/<id>`, `~/.claude/skills/<id>`, and `~/.codex/skills/<id>`. This is the default for anything that should run on all agents.
- **Platform-only skill** → author at `canonical/<platform>/skills/<id>/SKILL.md` (e.g. `canonical/claude-code/skills/<id>/`). It only lands on that one agent. A platform-only skill with the same id as a shared one overrides the shared copy on that platform.

After creating or changing a skill in the repo, run `./install.sh` so the consumer-dir symlinks are (re)created.

## Cross-platform authoring: auto-absorb

If an agent (or you) creates a skill directly inside a consumer dir as real files — `~/.cursor/skills/<id>/`, `~/.claude/skills/<id>/`, or `~/.codex/skills/<id>/` — the life pack pulls it back into the canonical shared location automatically:

```text
~/.<agent>/skills/<id>/  (real files)
        │  bin/vibe-absorb-skills  (runs inside bin/vibe-save)
        ▼
canonical/shared/skills/<id>/   (moved here)
        │  symlink back
        ▼
~/.<agent>/skills/<id>  -> canonical/shared/skills/<id>
```

So "created from any platform → lands in one common place" happens on the next save, with no manual steps. `vibe-absorb-skills` is idempotent (symlinks are left alone) and never touches Cursor's self-managed `~/.cursor/skills-cursor/` directory.

Run it manually if you want to absorb immediately:

```bash
bin/vibe-absorb-skills
```

## Quick Start

```bash
git clone <your-github-url> ~/vibecoding-life-pack
cd ~/vibecoding-life-pack
./install.sh
```

Default install mode is symlink mode. In symlink mode, agent directories point back to this repository, so a `git pull` updates installed skills immediately. Use `--mode copy` for a self-contained, non-symlinked install.

## Daily Workflow

Check current state:

```bash
bin/vibe-status
```

Save local changes (also runs auto-absorb):

```bash
bin/vibe-save --source manual
```

Pull, re-link, and validate:

```bash
./sync.sh
```

`sync.sh` runs:

```text
vibe-save (absorb + commit) -> git pull --rebase -> install.sh -> vibe-merge-check -> vibe-save
```

The `install.sh` step after pull means shared skills contributed by another device are linked into all three consumer dirs automatically — no manual install needed after sync.

## Adding a new skill

Preferred — author directly in the repo:

```bash
mkdir -p canonical/shared/skills/<id>
$EDITOR canonical/shared/skills/<id>/SKILL.md
./install.sh
bin/vibe-save --source manual
```

Or just create it under any consumer dir; the next `vibe-save` absorbs it into `canonical/shared/skills/<id>/`.

Register the skill in `manifest.yaml` (see `docs/manifest-schema.md`) and use `agent: shared` for cross-platform skills.

## Autosave

Autosave is handled by `bin/vibe-save`. It:

1. Runs `bin/vibe-absorb-skills` to pull consumer-dir skills into canonical.
2. Stages all life pack repository changes.
3. Creates a local commit when changes exist.

Autosave does not push in v1.

Commit message shape:

```text
chore(life-pack): autosave changes from <source> on <device-id>

Source: <source>
Device: <device-id>
Timestamp: <iso-timestamp>
```

Cursor calls this through a `sessionEnd` hook (`canonical/cursor/hooks/`). Claude Code and Codex should use native hooks if available, or wrappers that call `bin/vibe-save` after the agent exits.

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

`manifest.yaml` tracks agents, install targets, shared skills, platform skills, external packs, devices, and autosave policy. Skills can be marked `agent: shared` (fanned out to all three) or `agent: cursor|claude-code|codex` (platform-only).

See `docs/manifest-schema.md` when adding new skills or agent sections.
