#!/bin/bash

sudo apt install -y python3-pip
python3 -m pip install pylint
pylint .
