# Rollback Guide

Autosave makes local edits recoverable by putting them into Git history. Use Git to inspect and roll back changes.

## Inspect Before Rolling Back

```bash
git status
git diff
git log --oneline -10
```

## Roll Back Uncommitted Changes

Restore one file:

```bash
git restore path/to/file
```

Restore one directory:

```bash
git restore path/to/directory
```

Restore all uncommitted changes:

```bash
git restore .
```

## Undo The Last Autosave Commit

Keep the committed changes in the working tree:

```bash
git reset --mixed HEAD~1
```

Drop the last commit and its changes only when you are certain:

```bash
git reset --hard HEAD~1
```

Use the hard reset form carefully. Prefer `--mixed` when reviewing or salvaging changes.

## Restore One Skill From An Older Commit

Find prior versions:

```bash
git log -- canonical/cursor/skills/revise-plans/SKILL.md
```

Restore a file from a commit:

```bash
git checkout <commit> -- canonical/cursor/skills/revise-plans/SKILL.md
```

Then save the restored state:

```bash
bin/vibe-save --source rollback
```

## Recover After A Bad Pull

Inspect recent branch movement:

```bash
git reflog
```

Return to a previous state:

```bash
git reset --mixed <reflog-entry>
```

Run validation:

```bash
bin/vibe-merge-check
bin/vibe-save --source rollback-after-pull
```

## Symlink Install Rollback

If a symlink points to the wrong place:

```bash
ls -l ~/.cursor/skills
```

Remove only the bad symlink, then reinstall:

```bash
rm ~/.cursor/skills/<skill-id>
./install.sh
```

Do not remove real, unmanaged files unless you intentionally backed them up first.
