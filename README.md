# omzmini

Minimal, bootstrapper for `oh-my-zsh` that fetchs only core files and pulls plugins/themes based on `.zshrc`.

## 🚀 Features

- Core-only setup (no full repo clone)
- Parses `.zshrc` for plugins and theme
- Fetches only what's needed
- Self-upgrade (`--upgrade`) with SHA256 comparison
- Dry-run (`--dry-run`), diff (`--diff`), and audit logging (`--log`)
- `doctor` mode for diagnostics
- `restore` mode to rehydrate missing files
- Zsh tab-completion support
- Modular sourcing via `zshrc.d`


## 🧪 Usage

```bash
# Preview actions without executing
~/.config/omzmini/omzmini.py --dry-run

# Upgrade omzmini script itself
~/.config/omzmini/omzmini.py --upgrade
# Old version backed up as ~/.config/omzmini/omzmini.py.bak.<timestamp>
# To rollback: cp ~/.config/omzmini/omzmini.py.bak.<timestamp> ~/.config/omzmini/omzmini.py

# Show unified diff of outdated core/plugins/themes
~/.config/omzmini/omzmini.py --diff

# Restore missing or corrupted files
~/.config/omzmini/omzmini.py --restore

# List current plugin and theme status
~/.config/omzmini/omzmini.py --list

# Sync files to match .zshrc declarations
~/.config/omzmini/omzmini.py --sync

# Run diagnostics
~/.config/omzmini/omzmini.py --doctor

# Disable audit logging (enabled by default)
~/.config/omzmini/omzmini.py --log=false

# Show help
~/.config/omzmini/omzmini.py --help

# Pin a file to exclude it from future upgrades
~/.config/omzmini/omzmini.py --pin=<path>

```


## 🛠️ Install

You can install `omzmini` using either the automatic one-liner or manual setup.

---

### ⚡ Automatic Install (Recommended)

Run this one-liner to install `omzmini`:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/hdandekar/omzmini/refs/heads/main/install.sh)

```
* Creates `~/.config/omzmini` and `~/.oh-my-zsh/log`
* Copies `omzmini.py` into `~/.config/omzmini` and makes it executable
* Creates `.zshrc` from Oh My Zsh template if missing
* Adds modular sourcing snippet to `.zshrc` (`~/.config/zsh/zshrc.d/*.zsh`)
* Runs initial `--sync` to fetch core, plugins, and theme files declared in `.zshrc`


### Manual Install

```bash
# Create config directory
# Create config directory
mkdir -p ~/.config/omzmini

# Copy omzmini.py script
cp omzmini.py ~/.config/omzmini/
chmod +x ~/.config/omzmini/omzmini.py

# Create modular sourcing directory
mkdir -p ~/.config/zsh/zshrc.d

# Copy optional modular sourcing snippet if available
cp ~/.config/omzmini/zshrc.d/omzmini.zsh ~/.config/zsh/zshrc.d/

# Ensure .zshrc sources all modular snippets
if ! grep -q 'zshrc.d' ~/.zshrc; then
    echo 'for rcfile in ~/.config/zsh/zshrc.d/*.zsh; do source "$rcfile"; done' >> ~/.zshrc
fi

# Reload shell
source ~/.zshrc

# Run initial sync
~/.config/omzmini/omzmini.py --sync

```

## Recommended Workflow

1. Upgrading omzmini script
    * `~/.config/omzmini/omzmini.py --upgrade`
    * Backups of previous versions stored as: `~/.config/omzmini/omzmini.py.bak.<timestamp>`
    * Rollback command: `cp ~/.config/omzmini/omzmini.py.bak.<timestamp> ~/.config/omzmini/omzmini.py`

2. Updating Plugins & Themes
    * `~/.config/omzmini/omzmini.py --sync`
    * Fetches any missing or outdated plugins/themes based on `.zshrc`
    * Works for core files, Oh My Zsh lib/*, tools/*, and themes/plugins
    * Optional flags:
      * `--dry-run` → preview actions
      * `--diff` → see differences between local and remote
      * `--restore` → re-fetch missing files
3. Diagnostics & Status
    ```
    ~/.config/omzmini/omzmini.py --doctor   # Full diagnostics
    ~/.config/omzmini/omzmini.py --list     # Show status of plugins & theme
    ```
    * Verifies .zshrc existence, core files, plugins, and themes
    * Reports any missing or outdated items
4. Logging
    * Verifies .zshrc existence, core files, plugins, and themes
    * Reports any missing or outdated items
