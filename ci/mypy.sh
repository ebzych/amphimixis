#!/bin/bash

uv run mypy $(git ls-files '*.py')

