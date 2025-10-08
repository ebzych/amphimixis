#!/bin/bash

uv run black --check $(git ls-files '*.py')
