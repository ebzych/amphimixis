#!/bin/bash

SELF_PATH=$(dirname $(realpath $0))
CONFIG_HOME=$XDG_CONFIG_HOME

if [ "$CONFIG_HOME" = "" ]; then
    CONFIG_HOME=$HOME/.config
fi

mkdir -p $CONFIG_HOME/opencode/tools
mkdir -p $CONFIG_HOME/opencode/agents
cp -a $SELF_PATH/amphimixis.md $CONFIG_HOME/opencode/agents

cp -a $SELF_PATH/tools/amphimixis.analyze.ts $SELF_PATH/tools/amphimixis.build.ts $SELF_PATH/tools/amphimixis.profile.ts $SELF_PATH/tools/amphimixis.configure.ts $CONFIG_HOME/opencode/tools

bun install --cwd $CONFIG_HOME/opencode yaml

cd $CONFIG_HOME/opencode/tools
python3 -m venv .venv
source .venv/bin/activate
pip install ./amphimixis
