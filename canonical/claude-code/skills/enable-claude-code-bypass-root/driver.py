#!/usr/bin/env python3
"""
Enable Claude Code IDE-extension bypassPermissions mode under root on Linux.

Idempotent. Re-running prints "already configured" and changes nothing.

What it does:
  1. Scan ~/.cursor-server/extensions and ~/.vscode-server/extensions for
     anthropic.claude-code-* installs.
  2. Read each install's package.json to confirm the setting keys are still
     `claudeCode.environmentVariables`, `claudeCode.allowDangerouslySkipPermissions`,
     `claudeCode.initialPermissionMode` (warn loudly if the schema drifted).
  3. Merge three keys into the corresponding Machine settings.json:
       claudeCode.environmentVariables   += {name: IS_SANDBOX, value: 1}
       claudeCode.allowDangerouslySkipPermissions = true
       claudeCode.initialPermissionMode  = "bypassPermissions"
     Preserves any pre-existing keys. Tolerates JSONC (// comments,
     trailing commas) — VS Code/Cursor accept them.
  4. Append `IS_SANDBOX=1` to /etc/environment if absent (terminal fallback
     for `claude --dangerously-skip-permissions`).

Usage:
    python3 driver.py              # apply
    python3 driver.py --dry-run    # show what would change, write nothing
    python3 driver.py --home DIR   # override $HOME (testing)
"""

import argparse
import json
import os
import re
import sys
from glob import glob
from pathlib import Path
from typing import List, Optional, Tuple

EXT_GLOB_REL = "extensions/anthropic.claude-code-*"
SERVERS = ("cursor-server", "vscode-server")

REQUIRED_KEYS = (
    "claudeCode.environmentVariables",
    "claudeCode.allowDangerouslySkipPermissions",
    "claudeCode.initialPermissionMode",
)

DESIRED_ENV_ENTRY = {"name": "IS_SANDBOX", "value": "1"}
ETC_ENV = "/etc/environment"
ETC_ENV_LINE = "IS_SANDBOX=1"


def log(tag: str, msg: str) -> None:
    print(f"[{tag}] {msg}")


def strip_jsonc(text):
    """Strip // line comments, /* */ block comments, and trailing commas."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == '"':
                    j += 1
                    break
                j += 1
            out.append(text[i:j])
            i = j
        elif c == "/" and i + 1 < n and text[i + 1] == "/":
            j = text.find("\n", i)
            i = n if j == -1 else j
        elif c == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            i = n if j == -1 else j + 2
        else:
            out.append(c)
            i += 1
    cleaned = "".join(out)
    cleaned = re.sub(r",(\s*[}\]])", r"\1", cleaned)
    return cleaned


def load_settings(path: Path) -> dict:
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    try:
        return json.loads(strip_jsonc(raw))
    except json.JSONDecodeError as e:
        raise SystemExit(
            f"[error] {path} exists but is not valid JSON/JSONC: {e}.\n"
            f"        Refusing to clobber. Fix it by hand or move it aside."
        )


def find_extension(server_root: Path) -> Optional[Path]:
    matches = sorted(glob(str(server_root / EXT_GLOB_REL)))
    return Path(matches[-1]) if matches else None  # newest by lexical sort


def verify_schema(ext_dir: Path) -> Tuple[bool, List[str]]:
    pkg = ext_dir / "package.json"
    if not pkg.exists():
        return False, [f"package.json missing under {ext_dir}"]
    try:
        data = json.loads(pkg.read_text(encoding="utf-8"))
    except Exception as e:
        return False, [f"package.json unreadable ({e})"]
    props = data.get("contributes", {}).get("configuration", {}).get("properties", {})
    missing = [k for k in REQUIRED_KEYS if k not in props]
    return (not missing), missing


def merge_settings(current: dict) -> Tuple[dict, List[str]]:
    """Return (new_settings, list_of_change_descriptions)."""
    new = dict(current)
    changes = []  # type: List[str]

    env_list = list(new.get("claudeCode.environmentVariables", []))
    if not any(
        isinstance(e, dict) and e.get("name") == "IS_SANDBOX" and str(e.get("value")) == "1"
        for e in env_list
    ):
        env_list = [e for e in env_list if not (isinstance(e, dict) and e.get("name") == "IS_SANDBOX")]
        env_list.append(dict(DESIRED_ENV_ENTRY))
        new["claudeCode.environmentVariables"] = env_list
        changes.append("set claudeCode.environmentVariables += {IS_SANDBOX=1}")

    if new.get("claudeCode.allowDangerouslySkipPermissions") is not True:
        new["claudeCode.allowDangerouslySkipPermissions"] = True
        changes.append("set claudeCode.allowDangerouslySkipPermissions = true")

    if new.get("claudeCode.initialPermissionMode") != "bypassPermissions":
        new["claudeCode.initialPermissionMode"] = "bypassPermissions"
        changes.append('set claudeCode.initialPermissionMode = "bypassPermissions"')

    return new, changes


def write_settings(path: Path, data: dict, dry_run: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(data, indent=4, ensure_ascii=False) + "\n"
    if dry_run:
        log("dry-run", f"would write {path}:\n{rendered}")
        return
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(rendered, encoding="utf-8")
    tmp.replace(path)


def handle_server(home: Path, server: str, dry_run: bool) -> bool:
    server_root = home / f".{server}"
    if not server_root.exists():
        log(server, "not installed, skipping")
        return False

    ext = find_extension(server_root)
    if ext is None:
        log(server, f"no anthropic.claude-code-* extension under {server_root}/extensions, skipping")
        return False
    log(server, f"found extension at {ext}")

    ok, missing = verify_schema(ext)
    if not ok:
        log(server, f"WARNING schema drift: missing keys {missing} in {ext}/package.json")
        log(server, "         writing settings anyway — verify the keys still work for your version")

    settings_path = server_root / "data" / "Machine" / "settings.json"
    current = load_settings(settings_path)
    new, changes = merge_settings(current)

    if not changes:
        log(server, f"settings.json already configured at {settings_path}")
        return True

    log(server, f"updating {settings_path}:")
    for c in changes:
        log(server, f"  - {c}")
    write_settings(settings_path, new, dry_run)
    return True


def handle_etc_environment(dry_run: bool) -> None:
    p = Path(ETC_ENV)
    if not p.exists():
        log("env", f"{ETC_ENV} missing, skipping (uncommon — system PAM env file)")
        return
    try:
        existing = p.read_text(encoding="utf-8")
    except PermissionError:
        log("env", f"cannot read {ETC_ENV} (need root)")
        return

    for line in existing.splitlines():
        s = line.strip()
        if s.startswith("#"):
            continue
        if s.replace(" ", "") == ETC_ENV_LINE:
            log("env", f"{ETC_ENV} already contains {ETC_ENV_LINE}")
            return

    new_text = existing
    if new_text and not new_text.endswith("\n"):
        new_text += "\n"
    new_text += ETC_ENV_LINE + "\n"

    if dry_run:
        log("dry-run", f"would append '{ETC_ENV_LINE}' to {ETC_ENV}")
        return
    try:
        p.write_text(new_text, encoding="utf-8")
        log("env", f"appended {ETC_ENV_LINE} to {ETC_ENV}")
    except PermissionError:
        log("env", f"cannot write {ETC_ENV} (need root) — skipping")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--home", default=os.environ.get("HOME", "/root"),
                        help="override home directory (for testing)")
    parser.add_argument("--skip-etc-environment", action="store_true",
                        help="don't touch /etc/environment (e.g. when running as non-root)")
    args = parser.parse_args()

    if os.geteuid() != 0:
        log("warn", f"running as uid {os.geteuid()}, not root — the whole point of this is root.")
        log("warn", "continuing anyway, but the bypass gate only triggers for uid 0.")

    home = Path(args.home)
    log("info", f"home={home}, dry_run={args.dry_run}")

    touched_any = False
    for server in SERVERS:
        if handle_server(home, server, args.dry_run):
            touched_any = True

    if not touched_any:
        log("warn", "no Claude Code extension found under cursor-server or vscode-server.")
        log("warn", "settings will still be written if you install the extension later; for now skipping.")

    if not args.skip_etc_environment:
        handle_etc_environment(args.dry_run)

    print()
    log("done", "next: fully reconnect Cursor / VS Code Remote (or Reload Window) for changes to take effect.")
    log("done", "WARNING bypassPermissions disables all Bash/Edit confirmations under root. Use with care.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
