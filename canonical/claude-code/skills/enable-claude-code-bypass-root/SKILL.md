---
name: enable-claude-code-bypass-root
description: >-
  Enable Claude Code IDE-extension bypassPermissions mode (auto-accept all
  tool calls) under the root user on Linux. Use when the user runs Cursor /
  VS Code Remote as root on a remote dev machine and wants to skip the
  per-tool permission prompts, or reports the "cannot be used with root /
  sudo privileges" error after setting allowDangerouslySkipPermissions in
  settings.json. Trigger phrases: "enable bypass mode", "skip claude code
  permissions", "root 用 bypass", "Claude Code 自动放行", "root 用户 Claude Code
  权限".
---

# enable-claude-code-bypass-root

Configures the Claude Code Cursor / VS Code extension to start in
`bypassPermissions` mode under root on Linux, by injecting `IS_SANDBOX=1`
into the env the extension passes to its spawned Claude process. Also
appends `IS_SANDBOX=1` to `/etc/environment` so terminal `claude
--dangerously-skip-permissions` works too.

The driver is **[driver.py](driver.py)** — Python stdlib only, works on
3.6+. Idempotent: re-runs print "already configured" and change nothing.

## Why this is non-trivial

The Claude Code CLI hard-refuses bypassPermissions when `geteuid() == 0`
unless `IS_SANDBOX=1` or `CLAUDE_CODE_BUBBLEWRAP=1` is in its env. Naive
fixes that DON'T work in cursor-server / vscode-server SSH-remote mode:

- Adding `export IS_SANDBOX=1` to `~/.bashrc` — the remote server process
  is started by the SSH/PAM session before `.bashrc` runs for the
  interactive shell; the extension host inherits the server's env, not
  yours.
- Adding `IS_SANDBOX=1` to `/etc/environment` — only loaded for **new**
  PAM sessions. The cursor-server already running on this box doesn't get
  it. "Reload Window" doesn't restart the server.
- Just toggling `claudeCode.allowDangerouslySkipPermissions: true` +
  `claudeCode.initialPermissionMode: "bypassPermissions"` — the
  extension's spawned CLI still hits the root gate and exits.

The working approach: use the extension's own `claudeCode.environmentVariables`
setting. The extension **directly injects** that into the spawned Claude
subprocess env, bypassing the whole parent-process inheritance chain. No
shell restart, no server restart, just Reload Window.

## Run

```bash
python3 /root/.claude/skills/enable-claude-code-bypass-root/driver.py
```

Add `--dry-run` to preview changes without writing. Add
`--skip-etc-environment` if running as a non-root user testing the IDE
config piece in isolation.

Then in Cursor / VS Code: **Cmd/Ctrl+Shift+P → Reload Window** (or fully
reconnect the Remote session). The extension reads Machine settings on
window load.

## What the driver does

1. Scans `~/.cursor-server/extensions/anthropic.claude-code-*` and
   `~/.vscode-server/extensions/anthropic.claude-code-*` for installed
   extensions. Picks the lexically-newest version (so 2.1.145 wins
   over 2.1.144).
2. Reads each install's `package.json` and verifies the three setting
   keys still exist:
   `claudeCode.environmentVariables`,
   `claudeCode.allowDangerouslySkipPermissions`,
   `claudeCode.initialPermissionMode`.
   If any key is missing (schema drift in a future version), prints a
   warning but writes anyway — you'll see what's wrong in IDE output.
3. Reads `data/Machine/settings.json` for each server (creates it if
   missing), tolerates JSONC (line/block comments, trailing commas),
   merges these three keys, preserves everything else, writes atomically
   via temp file + rename.
4. Appends `IS_SANDBOX=1` to `/etc/environment` only if absent (for
   terminal-CLI fallback).

It skips a server entirely if the Claude Code extension isn't installed
there — only configures where it'll actually be used.

## Verify

```bash
# the three keys should be present and correct
python3 -c "import json; s=json.load(open('/root/.cursor-server/data/Machine/settings.json')); print(json.dumps({k:v for k,v in s.items() if k.startswith('claudeCode.')}, indent=2))"

# /etc/environment fallback
grep -F IS_SANDBOX=1 /etc/environment

# inside Cursor's Claude Code panel, mode indicator should read
# "bypass permissions" after Reload Window
```

## Gotchas

- **Reload Window vs. full reconnect.** Reload Window is enough because
  Machine settings are read on workspace load. You only need a full
  Remote reconnect if you wanted the parent-server env to inherit
  `IS_SANDBOX=1` — which we don't, because the extension setting
  bypasses that.
- **The `/etc/environment` route alone needs the server KILLED, not just
  reconnected** (seen 2026-05-31, cursor-server). The remote server
  process is persistent: even *Close Remote Connection → reopen* often
  reattaches to the **same** running server (started before your
  `/etc/environment` edit), so it never re-reads PAM env and the root
  gate keeps firing — the extension log still shows
  `--dangerously-skip-permissions cannot be used with root`. To force the
  env-inheritance route you must kill the server PID (`pgrep -f
  cursor-server` → `kill`, or Command Palette → "Kill VS Code Server on
  Host"); the client then re-bootstraps a fresh PAM session that carries
  `IS_SANDBOX=1`. The Machine-settings route this driver writes avoids the
  whole problem — Reload Window is enough.
- **Comments in settings.json get stripped on rewrite.** VS Code/Cursor
  accept JSONC, but Python's `json.dump` doesn't preserve comments. The
  resulting file is pure JSON and still valid; if you had `// note...`
  lines they're gone after the driver runs. Trailing commas are also
  normalized away. Tradeoff for not needing `jq` / a JSONC library.
- **The driver does NOT remove pre-existing `IS_SANDBOX` entries with
  other values** — it strips any old `IS_SANDBOX` entry and inserts
  `value: "1"`. Other env vars in the array (e.g. `ANTHROPIC_API_KEY`)
  are left alone.
- **`vscode-server` only gets touched if the extension is installed
  there.** If you have orphan `claudeCode.*` settings in
  `~/.vscode-server/data/Machine/settings.json` from earlier hand-edits,
  they sit harmlessly until you install the extension. Delete them
  manually if you care.
- **bypassPermissions is dangerous under root.** Every Bash, Edit, Write
  goes through with zero confirmation. Don't enable this on a box you
  also use as a shared production target. Use a `cwd` allowlist (via
  `permissions.deny` in `~/.claude/settings.json`) or skip this skill
  and approve per-call.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Driver says "no anthropic.claude-code-* extension under …" | Extension isn't installed in that server. Either install it via the Extensions panel, or you're using a different IDE flavor (e.g. Code-Server). Adapt the glob in `driver.py`. |
| Driver bails with "exists but is not valid JSON/JSONC" | Your `settings.json` has a real syntax error (not just comments). Open it in the IDE; the editor will mark the broken line. Fix and re-run. The driver refuses to clobber. |
| After Reload Window, panel still shows "default" mode | Check `data/Machine/settings.json` actually has the three keys (see Verify). If it does, also check **User** settings (sync'd from local) aren't overriding to `"default"` — Workspace > User > Machine precedence in VS Code. |
| Root gate still triggers in terminal `claude --dangerously-skip-permissions` | `/etc/environment` only loads for new login sessions. Open a **new** SSH session, or `exec env -i bash -l` (be careful — wipes current env). Or just `IS_SANDBOX=1 claude --dangerously-skip-permissions`. |
| Cursor auto-updates the extension and the setting keys change | Schema-drift warning will print at run time. Inspect `~/.cursor-server/extensions/anthropic.claude-code-*/package.json` `contributes.configuration.properties`, update the constants at the top of `driver.py`. |

## File map

```
/root/.claude/skills/enable-claude-code-bypass-root/
  SKILL.md     ← this file
  driver.py    ← the actual configurator
```

Both writes the driver makes are reversible by editing the JSON file (for
settings.json) or `sed -i '/^IS_SANDBOX=1$/d' /etc/environment` (for the
env file).

## Terminal CLI (bare `claude` in a shell / tmux)

The IDE route above does **not** cover the terminal CLI. To make bare `claude`
(the interactive REPL, e.g. launched in tmux) start in `bypassPermissions`
under root, you need **two** things — verified 2026-05-31 on any1+any3, CLI v2.1.157:

1. **Lift the root gate** — `IS_SANDBOX=1` in the shell env. `/etc/environment`
   (pam_env) covers fresh SSH/tmux logins; `export IS_SANDBOX=1` in `~/.bashrc`
   is belt-and-suspenders for non-login interactive shells. Without it:
   `--dangerously-skip-permissions cannot be used with root/sudo privileges`.
2. **Default the REPL to bypass** — in `~/.claude/settings.json`:
   ```json
   { "permissions": { "defaultMode": "bypassPermissions" },
     "skipDangerousModePermissionPrompt": true }
   ```
   `defaultMode` makes the interactive session start in bypass **without** the
   `--dangerously-skip-permissions` flag; `skipDangerousModePermissionPrompt`
   skips the one-time "are you sure" confirm. There is **no env var** for the
   default mode — it must be the settings key.

Subcommand-safe: `defaultMode` only affects the interactive REPL; `claude mcp`,
`claude config`, `claude --version` are unaffected (don't alias `claude` to add
the flag — that would break those subcommands).

Verify the gate logic without an LLM call:
```bash
env -u IS_SANDBOX claude --permission-mode bypassPermissions -p x </dev/null 2>&1 | head -1
# → prints the root-gate refusal, proving IS_SANDBOX is what lifts it.
```
