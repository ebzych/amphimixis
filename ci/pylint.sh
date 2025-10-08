#!/bin/bash

uv run pylint $(git ls-files 'src/*.py')
