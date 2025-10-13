#!/bin/bash
BLUE='\e[34m'
NC='\e[0m'
COMMAND="${1}"

echo -e "${BLUE}Running MyPy type checker...${NC}"
mapfile -t files < <(git ls-files 'src/*.py')
"$COMMAND" run mypy "${files[@]}"

