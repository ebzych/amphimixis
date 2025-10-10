#!/bin/bash

COMMAND="${1:-uv}"
"$COMMAND" run mypy $(git ls-files '*src/*.py')

