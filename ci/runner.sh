#!/bin/bash

CONFIG_FILE="ci/.temp_config"
./ci/environment_configure.sh "$CONFIG_FILE"

if [ -f "$CONFIG_FILE" ]; then
    COMMAND=$(cat "$CONFIG_FILE")
    rm -f "$CONFIG_FILE"
else
    echo "Error: Config file not found"
    exit 1
fi

./ci/pylint.sh "$COMMAND"
./ci/mypy.sh "$COMMAND"
./ci/black.sh "$COMMAND"
