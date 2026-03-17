#!/bin/bash

SELF_PATH=$(dirname $(realpath $0))
CONFIG_HOME=$XDG_CONFIG_HOME

if [ "$CONFIG_HOME" = "" ]; then
    CONFIG_HOME=$HOME/.config
fi

mkdir -p $CONFIG_HOME/opencode/tools
mkdir -p $CONFIG_HOME/opencode/agents
cp -a $SELF_PATH/amphimixis.md $CONFIG_HOME/opencode/agents

cp -a $SELF_PATH/tools/amphimixis.analyze.ts $SELF_PATH/tools/amphimixis.build.ts $CONFIG_HOME/opencode/tools

ln -sdf $SELF_PATH/../amphimixis $CONFIG_HOME/opencode/tools/amphimixis
