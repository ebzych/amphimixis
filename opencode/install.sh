#!/bin/bash

SELF_PATH=$(dirname $(realpath $0))
CONFIG_HOME=$XDG_CONFIG_HOME

if [ "$CONFIG_HOME" = "" ]; then
    CONFIG_HOME=$HOME/.config
fi

mkdir -p $CONFIG_HOME/opencode/tools
mkdir -p $CONFIG_HOME/opencode/agents
cp -a $SELF_PATH/agents/*.md $CONFIG_HOME/opencode/agents

cp -a $SELF_PATH/tools/*.ts $CONFIG_HOME/opencode/tools

bun install --cwd $CONFIG_HOME/opencode yaml

cd $CONFIG_HOME/opencode/tools
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install $SELF_PATH/..
