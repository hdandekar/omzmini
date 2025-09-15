#!/usr/bin/env python3
"""
omzmini.py - Minimal oh-my-zsh bootstrapper in Python
Supports: --sync, --upgrade, --restore, --doctor, --list, --dry-run, --diff, --pin
"""

import os
import sys
import argparse
import hashlib
import shutil
import datetime
import urllib.request
import difflib
from pathlib import Path

# ---------------- Paths ---------------- #
HOME = os.path.expanduser("~")
OHMYZSH_DIR = os.path.join(HOME, ".oh-my-zsh")
OMZMINI_DIR = os.path.join(HOME, ".config", "omzmini")
LOG_DIR = os.path.join(OHMYZSH_DIR, "log")
LOGFILE = os.path.join(LOG_DIR, "omzmini_audit.log")
HASHFILE = os.path.join(LOG_DIR, "omzmini_hashes.txt")
PIN_FILE = os.path.join(OMZMINI_DIR, "pinned.txt")
REPO_RAW = "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OMZMINI_DIR, exist_ok=True)

# ---------------- Utilities ---------------- #
def log(msg, log_enabled=True):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    if log_enabled:
        with open(LOGFILE, "a") as f:
            f.write(line + "\n")

def sha256(file_path):
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def fetch_file(path, dest, dry_run=False, diff=False, pinned=set(), log_enabled=True):
    dest_path = Path(dest).resolve()
    if dest_path in pinned:
        log(f"🔒 Skipped pinned file: {dest_path}", log_enabled)
        return

    url = f"{REPO_RAW}/{path}"
    os.makedirs(os.path.dirname(dest), exist_ok=True)

    if dry_run:
        log(f"DRY-RUN: Would fetch {url} -> {dest}", log_enabled)
        return

    try:
        data = urllib.request.urlopen(url).read()
    except Exception as e:
        log(f"❌ Failed to fetch {url}: {e}", log_enabled)
        return

    if os.path.exists(dest):
        old_hash = sha256(dest)
        new_hash = hashlib.sha256(data).hexdigest()
        if old_hash != new_hash:
            if diff:
                with open(dest, "r") as f:
                    local_lines = f.read().splitlines()
                remote_lines = data.decode(errors="ignore").splitlines()
                diff_lines = list(difflib.unified_diff(local_lines, remote_lines,
                                                       fromfile=dest, tofile="remote"))
                if diff_lines:
                    print("\n".join(diff_lines))
            ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            backup = f"{dest}.{ts}"
            shutil.move(dest, backup)
            log(f"📝 Local changes detected → backed up as {backup}", log_enabled)

    with open(dest, "wb") as f:
        f.write(data)
    log(f"✅ Fetched: {path} -> {dest}", log_enabled)

    with open(HASHFILE, "a") as f:
        f.write(f"{path} {sha256(dest)}\n")

# ---------------- Hardcoded core/lib/tools ---------------- #
CORE_FILES = [
    "oh-my-zsh.sh"
]

LIB_FILES = [
    "lib/completion.zsh",
    "lib/history.zsh",
    "lib/key-bindings.zsh",
    "lib/termcap.zsh",
]

TOOLS_FILES = [
    "tools/upgrade.sh",
    "tools/install.sh",
    "tools/uninstall.sh",
]

# ---------------- Actions ---------------- #
def parse_zshrc(zshrc_path):
    plugins, theme = [], None
    if not os.path.exists(zshrc_path):
        return plugins, theme
    with open(zshrc_path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("plugins="):
                plugins = line.split("(", 1)[1].split(")")[0].split()
            elif line.startswith("ZSH_THEME="):
                theme = line.split('"')[1]
    return plugins, theme

def sync_plugins_and_theme(zshrc, dry_run=False, diff=False, pinned=set(), log_enabled=True):
    plugins, theme = parse_zshrc(zshrc)

    # Core files
    for f in CORE_FILES:
        fetch_file(f, os.path.join(OHMYZSH_DIR, f), dry_run=dry_run, diff=diff, pinned=pinned, log_enabled=log_enabled)
    # Lib files
    for f in LIB_FILES:
        fetch_file(f, os.path.join(OHMYZSH_DIR, f), dry_run=dry_run, diff=diff, pinned=pinned, log_enabled=log_enabled)
    # Tools files
    for f in TOOLS_FILES:
        fetch_file(f, os.path.join(OHMYZSH_DIR, f), dry_run=dry_run, diff=diff, pinned=pinned, log_enabled=log_enabled)
    # Plugins
    for plugin in plugins:
        plugin_file = f"plugins/{plugin}/{plugin}.plugin.zsh"
        fetch_file(plugin_file, os.path.join(OHMYZSH_DIR, plugin_file), dry_run=dry_run, diff=diff, pinned=pinned, log_enabled=log_enabled)
    # Theme
    if theme:
        theme_file = f"themes/{theme}.zsh-theme"
        fetch_file(theme_file, os.path.join(OHMYZSH_DIR, theme_file), dry_run=dry_run, diff=diff, pinned=pinned, log_enabled=log_enabled)

    log("✅ Sync complete", log_enabled)

def run_doctor(zshrc):
    print("🩺 Running omzmini diagnostics...")
    if os.path.exists(zshrc):
        print("✅ .zshrc found")
    else:
        print("❌ .zshrc missing")

    core_file = os.path.join(OHMYZSH_DIR, "oh-my-zsh.sh")
    if os.path.exists(core_file):
        print("✅ oh-my-zsh.sh present")
    else:
        print("❌ oh-my-zsh.sh missing")

    plugins, theme = parse_zshrc(zshrc)
    if not plugins:
        print("⚠️ No plugins declared")
    if not theme:
        print("⚠️ No theme declared")

def run_list(zshrc):
    print("📋 Plugins and theme:")
    plugins, theme = parse_zshrc(zshrc)
    if plugins:
        print("Plugins:", ", ".join(plugins))
    else:
        print("⚠️ No plugins declared")
    if theme:
        print("Theme:", theme)
    else:
        print("⚠️ No theme declared")

def upgrade_self(dry_run=False, pinned=set()):
    omzmini_path = os.path.join(OMZMINI_DIR, "omzmini.py")
    backup = f"{omzmini_path}.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    if dry_run:
        log(f"DRY-RUN: Would upgrade omzmini and backup to {backup}")
        return
    shutil.copy2(omzmini_path, backup)
    fetch_file("omzmini.py", omzmini_path, dry_run=False, pinned=pinned)
    os.chmod(omzmini_path, 0o755)
    log(f"✅ omzmini upgraded. Backup: {backup}")

# ---------------- Main ---------------- #
def main():
    parser = argparse.ArgumentParser(description="omzmini - minimal oh-my-zsh bootstrapper")
    parser.add_argument("--sync", action="store_true", help="Fetch any missing files to match .zshrc declarations")
    parser.add_argument("--upgrade", action="store_true", help="Upgrade omzmini script itself")
    parser.add_argument("--restore", action="store_true", help="Re-fetch missing or corrupted files")
    parser.add_argument("--doctor", action="store_true", help="Run diagnostics on omzmini setup")
    parser.add_argument("--list", action="store_true", help="Show status of plugins and theme")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without executing")
    parser.add_argument("--diff", action="store_true", help="Show diff for outdated files")
    parser.add_argument("--pin", nargs="*", help="Pin files to exclude from upgrades")
    args = parser.parse_args()

    pinned = set()
    if args.pin:
        pinned.update(Path(p).resolve() for p in args.pin)
    elif Path(PIN_FILE).exists():
        pinned.update(Path(p.strip()).resolve() for p in Path(PIN_FILE).read_text().splitlines())

    zshrc = os.path.join(HOME, ".zshrc")
    if args.upgrade:
        upgrade_self(dry_run=args.dry_run, pinned=pinned)
    if args.sync:
        sync_plugins_and_theme(zshrc, dry_run=args.dry_run, diff=args.diff, pinned=pinned)
    if args.restore:
        sync_plugins_and_theme(zshrc, dry_run=False, diff=False, pinned=pinned)
    if args.doctor:
        run_doctor(zshrc)
    if args.list:
        run_list(zshrc)

if __name__ == "__main__":
    main()
