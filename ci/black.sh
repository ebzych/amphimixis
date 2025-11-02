#!/bin/bash
BLUE='\e[34m'
NC='\e[0m'
COMMAND="${1}"

echo -e "${BLUE}Running Black code formatter...${NC}"
mapfile -t files < <(git ls-files '*.py')
"$COMMAND" run black --check "${files[@]}"


