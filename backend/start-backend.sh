#!/bin/bash

# Install system dependencies
apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

# Install pipenv
pip install --user pipenv

# Add local bin to PATH
export PATH="$PATH:$HOME/.local/bin"

# Install project dependencies
pipenv install --dev
pipenv install --system --deploy

# Run the application with Flask development server and debug mode
FLASK_APP=app.py FLASK_ENV=development FLASK_DEBUG=1 pipenv run python -m flask run --host=0.0.0.0 --port=4001