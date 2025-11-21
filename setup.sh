#!/bin/bash

# Setup script for the hospital management system backend

echo "================================"
echo "Hospital Management System Setup"
echo "================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run database migration
echo ""
echo "Running database migration..."
python scripts/migrate_db.py

echo ""
echo "================================"
echo "Setup completed successfully!"
echo "================================"
echo ""
echo "To start the server, run:"
echo "  source venv/bin/activate"
echo "  python run.py"
echo ""
