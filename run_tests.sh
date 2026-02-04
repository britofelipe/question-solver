#!/bin/bash
echo "Running Backend Tests..."
cd backend
# Need to set PYTHONPATH or just run as module?
# Simplest: install dependencies if not present (in docker usually)
# Here we assume user runs locally or we exec in container
# For local run:
pip install pytest httpx
pytest -v test_main.py
