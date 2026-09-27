#!/bin/bash
echo "Setting up the project..."
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
echo "Setup done!"
