#!/bin/bash

COMMAND="${1:-uv}"
"$COMMAND" run pylint $(git ls-files 'src/*.py')
