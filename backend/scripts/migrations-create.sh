#!/bin/bash

# Exit on any error
set -e

# Install the local package in editable mode if not already installed
pip install -e .

# Check if a migration message was provided
if [ -z "$1" ]; then
    echo "Error: Please provide a migration message"
    echo "Usage: ./scripts/migrations-create.sh \"your migration message\""
    exit 1
fi

# Run alembic revision with the provided message
alembic revision --autogenerate -m "$1"