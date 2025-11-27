#!/bin/bash
set -e

ORIG_DIR=$(pwd)
CI_PATH=$(dirname "$0")

cd "${CI_PATH}"/..

pytest -m integration -s -v

cd "${ORIG_DIR}"
