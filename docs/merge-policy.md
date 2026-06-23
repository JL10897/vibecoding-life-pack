# Merge Policy

This repository uses a canonical + device overrides model.

## Source Of Truth

`canonical/` is the default source of truth.

Use it for:

- Skills that should be available on all devices.
- Shared planning, debugging, testing, and review workflows.
- Agent hooks and scripts that are safe to reuse.

Use `devices/<device-id>/` for:

- Machine-specific paths.
- Local environment assumptions.
- Temporary experiments that should not affect other devices yet.

## Normal Sync Flow

Always autosave before pulling:

```bash
bin/vibe-save --source sync-before-pull
git pull --rebase
bin/vibe-merge-check
bin/vibe-save --source sync-after-pull
```

`sync.sh` runs this flow.

## Conflict Resolution Rules

When Git reports a conflict:

1. Identify whether the conflicted file is canonical or device-specific.
2. For `canonical/` conflicts, merge the intended behavior. Do not blindly choose one side.
3. For `devices/<device-id>/` conflicts, prefer the owner device's local intent.
4. If a device override is now useful everywhere, move it into `canonical/`.
5. Remove stale references from `manifest.yaml`.
6. Run `bin/vibe-merge-check`.
7. Commit the resolved state with `bin/vibe-save --source merge-resolution`.

## Skill-Level Merge Guidance

When two devices edit the same skill:

- Preserve the trigger description if it affects automatic skill loading.
- Keep exact user-authored workflow rules when they were written as source text.
- Merge checklist additions only when they do not contradict the required sequence.
- Remove duplicated or superseded sections.
- Re-read the final skill as one document before committing.

## Device Override Promotion

Promote an override when:

- It has been useful on more than one device.
- It no longer depends on local paths or local tools.
- It fixes a general workflow issue.

Promotion steps:

```text
copy intent into canonical -> delete override -> update manifest -> run merge check -> autosave
```

## What Not To Do

- Do not keep two divergent canonical versions of the same skill.
- Do not use device overrides for convenience when the behavior is generally useful.
- Do not resolve manifest conflicts without checking that referenced paths exist.
- Do not auto-push from autosave until this workflow has been proven reliable.
