#!/bin/bash
BLUE='\e[34m'
NC='\e[0m'

echo -e "${BLUE}Running linter Pylint...${NC}"
mapfile -t files < <(git ls-files '*.py')
uv run pylint "${files[@]}"
