#!/bin/bash

python3.12 -m venv .venv
source ./.venv/bin/activate
python3.12 -m pip install -r ./sca/requirements.txt