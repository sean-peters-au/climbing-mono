#!/bin/bash

# Exit on any error
set -e

# Install the local package in editable mode if not already installed
pip install -e .

# Run alembic upgrade
alembic upgrade head