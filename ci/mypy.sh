#!/bin/bash
BLUE='\e[34m'
NC='\e[0m'

echo -e "${BLUE}Running MyPy type checker...${NC}"
mapfile -t files < <(git ls-files '*.py')
uv run mypy "${files[@]}"

