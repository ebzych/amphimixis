#!/bin/bash

RED='\e[31m'
BLUE='\e[34m'
NC='\e[0m'

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

if ! command_exists "uv"; then
    if command_exists "curl"; then
        echo -e "${BLUE}Installing uv with curl...${NC}"
        curl -LsSf https://astral.sh/uv/install.sh | sh
    elif  command_exists "wget"; then
        echo -e "${BLUE}Installing uv with wget...${NC}"
        wget -qO- https://astral.sh/uv/install.sh | sh
    else
         echo "Please install curl for check CI:"
         echo "sudo apt install curl"
         exit 1
    fi

fi

if ! command_exists "uv"; then
    echo -e "${RED}Error: UV installation failed - command 'uv' not found${NC}"
    exit 1
fi

uv sync
