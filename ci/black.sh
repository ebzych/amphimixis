#!/bin/bash
BLUE='\e[34m'
NC='\e[0m'

echo -e "${BLUE}Running Black code formatter...${NC}"
mapfile -t files < <(git ls-files '*.py')
uv run black --check "${files[@]}"


