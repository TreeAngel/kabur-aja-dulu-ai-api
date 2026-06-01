#!/bin/bash

echo "====================================="
echo "Activating virtual environment..."
echo "====================================="

source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

echo
echo "====================================="
echo "Checking dependencies..."
echo "====================================="

pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo
    echo "Failed to install required packages."
    exit 1
fi

echo
echo "====================================="
echo "Starting KaburAjaDulu.AI API Server"
echo "====================================="
echo "Docs   : http://localhost:8000/docs"
echo "Health : http://localhost:8000/health"
echo

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000