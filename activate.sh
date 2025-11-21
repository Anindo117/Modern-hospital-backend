#!/bin/bash
# Activate the Python virtual environment
source venv/bin/activate
echo "✓ Virtual environment activated (Python $(python --version 2>&1 | awk '{print $2}'))"
