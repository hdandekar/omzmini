#!/bin/bash
set -euo pipefail

# ---------------- Paths ---------------- #
HOME_DIR="$HOME"
OMZMINI_DIR="$HOME_DIR/.config/omzmini"
OMZMINI_PY="$OMZMINI_DIR/omzmini.py"
ZSHRC="$HOME_DIR/.zshrc"

# ---------------- Checks ---------------- #
echo "🔍 Checking for python3..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ python3 is required but not found. Please install Python 3."
    exit 1
fi

echo "🔍 Checking for curl..."
if ! command -v curl >/dev/null 2>&1; then
    echo "❌ curl is required but not found. Please install curl."
    exit 1
fi

# ---------------- Setup ---------------- #
mkdir -p "$OMZMINI_DIR"

# Download omzmini.py
echo "📥 Downloading omzmini.py..."
curl -fsSL "https://raw.githubusercontent.com/hdandekar/omzmini/main/omzmini.py" -o "$OMZMINI_PY"
chmod +x "$OMZMINI_PY"

# ---------------- Zshrc Alias ---------------- #
ALIAS_LINE='alias omzmini="python3 ~/.config/omzmini/omzmini.py"'
if ! grep -Fxq "$ALIAS_LINE" "$ZSHRC"; then
    echo "$ALIAS_LINE" >> "$ZSHRC"
    echo "✅ Added alias to $ZSHRC"
else
    echo "ℹ️ Alias already exists in $ZSHRC"
fi

# ---------------- Scaffold .zshrc ---------------- #
if [[ ! -f "$ZSHRC" ]]; then
    echo "🧪 Creating minimal .zshrc from template..."
    curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/templates/zshrc.zsh-template -o "$ZSHRC"
fi

# ---------------- Initial Update ---------------- #
echo "🚀 Running initial update (fetch core, plugins, theme)..."
python3 "$OMZMINI_PY" --update || true

# ---------------- Completion Suggestion ---------------- #
echo "ℹ️ You can now use 'omzmini --help' after restarting your shell or running 'source ~/.zshrc'."
echo "✅ Installation complete."
