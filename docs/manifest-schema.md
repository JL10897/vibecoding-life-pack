# Manifest Schema

`manifest.yaml` is the inventory for this life pack. It should answer three questions:

1. What is included?
2. Where should it be installed?
3. How should it be maintained across devices?

## Top-Level Fields

```yaml
version: 1
pack: {}
agents: {}
shared: {}
skills: []
external_packs: []
devices: {}
autosave: {}
```

## `pack`

```yaml
pack:
  name: vibecoding-life-pack
  owner: yiranqu
  description: Personal vibecoding life pack for Cursor, Claude Code, and Codex skills.
```

`name` should match the repository name. `owner` is informational and used in generated docs or commit messages.

## `agents`

Each agent entry defines its canonical source path and install targets.

```yaml
agents:
  cursor:
    canonical_path: canonical/cursor
    install_targets:
      skills: ~/.cursor/skills
      rules: ~/.cursor/rules
      hooks_dir: ~/.cursor/hooks
      hooks_json: ~/.cursor/hooks.json
```

Use `canonical_path` for content that should be shared across devices. Keep install target keys stable so install scripts can rely on them.

## `skills`

Each skill entry should be explicit:

```yaml
skills:
  - id: revise-plans
    agent: cursor
    path: canonical/cursor/skills/revise-plans
    status: active
    source: personal
    description: Revise existing plan documents while preserving logical consistency.
```

Allowed `status` values:

- `active`: installed or intended for installation.
- `draft`: not ready for default installation.
- `archived`: kept for history, not installed by default.
- `referenced`: tracked as an external dependency or note.

Allowed `source` values:

- `personal`: authored in this pack.
- `external`: maintained elsewhere.
- `imported`: copied from another local environment.

## `external_packs`

Use this for externally maintained packs where the preferred behavior is to record the source and install method rather than vendor all files.

```yaml
external_packs:
  - id: external-skill-pack
    status: referenced
    source: external
    description: Skills maintained in a separate upstream repository.
    install_note: Record source and install method instead of vendoring by default.
```

## `devices`

Device overrides are intentionally small.

```yaml
devices:
  strategy: canonical-plus-device-overrides
  override_root: devices
  rule: Keep overrides small. Promote reusable changes back into canonical.
```

If an override becomes useful on multiple machines, move it into `canonical/` and remove the override.

## `autosave`

Autosave commits local life pack changes so edits are not left behind on one machine.

```yaml
autosave:
  enabled: true
  commit_scope: all
  push: false
  entrypoint: bin/vibe-save
```

`push` should stay `false` until the autosave workflow has proven reliable.
