#!/bin/bash

SELF_PATH=$(dirname "$(realpath "$0")")
PROJECT_ROOT=$(realpath "$SELF_PATH/../../")
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"

USE_UV=""
if [ "$1" = "--uv" ]; then
    USE_UV="uv"
fi

echo "Installing methodology agents and tools to $CONFIG_HOME/opencode"

# Create directories
mkdir -p "$CONFIG_HOME/opencode/tools"
mkdir -p "$CONFIG_HOME/opencode/agents"

# Copy methodology agents (from integrations/opencode/agents)
echo "  Copying methodology agents..."
cp -a "$SELF_PATH/agents/"*.md "$CONFIG_HOME/opencode/agents/"

# Copy methodology tools (from integrations/opencode/tools)
echo "  Copying methodology tools..."
cp -a "$SELF_PATH/tools/"*.ts "$CONFIG_HOME/opencode/tools/" 2>/dev/null

# Also copy existing amphimixis agents (from opencode/agents)
if [ -d "$PROJECT_ROOT/opencode/agents" ]; then
    echo "  Copying amphimixis agents..."
    cp -a "$PROJECT_ROOT/opencode/agents/"*.md "$CONFIG_HOME/opencode/agents/"
fi

# Also copy existing amphimixis tools (from opencode/tools, excluding .opencode dir)
if [ -d "$PROJECT_ROOT/opencode/tools" ]; then
    echo "  Copying amphimixis tools..."
    for f in "$PROJECT_ROOT/opencode/tools/"*.ts; do
        if [ -f "$f" ]; then
            cp "$f" "$CONFIG_HOME/opencode/tools/"
        fi
    done
fi

# Install bun dependencies
echo "  Installing bun dependencies..."
cd "$CONFIG_HOME/opencode" || exit 1
if command -v bun &> /dev/null; then
    bun install yaml 2>/dev/null || echo "    (bun install completed)"
else
    echo "    bun not found — install it from https://bun.sh"
fi

# Remove amphimixis core agent/tool stubs (they are provided by the Python package)
rm -f "$CONFIG_HOME/opencode/agents/amphimixis."*.md
rm -f "$CONFIG_HOME/opencode/tools/amphimixis."*.ts

# Set up Python venv and install amphimixis package
cd "$CONFIG_HOME/opencode/tools" || exit 1
rm -rf .venv
if [ "$USE_UV" != "" ]; then
    echo "  Setting up Python venv with uv..."
    "$USE_UV" venv
    "$USE_UV" pip install "$PROJECT_ROOT"
else
    echo "  Setting up Python venv..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install "$PROJECT_ROOT"
fi

echo ""
echo "Installation complete!"
echo "  Agents installed: $(ls "$CONFIG_HOME/opencode/agents/"*.md 2>/dev/null | wc -l)"
echo "  Tools installed: $(ls "$CONFIG_HOME/opencode/tools/"*.ts 2>/dev/null | wc -l)"
echo ""
echo "Methodology agents and tools are now available in opencode."