#!/bin/bash

COMMAND="${1:-uv}"
"$COMMAND" run black --check $(git ls-files 'src/*.py')
