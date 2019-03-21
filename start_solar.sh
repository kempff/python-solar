#!/bin/bash
export PYTHONPATH=/usr/lib/python3/dist-packages
export PRINT_LOGS=True
export DEBUG_MODE=True
export PROCESS_TIME=10
export LOG_LEVEL=DEBUG
pipenv run python -m python-solar
