#!/bin/bash

# Install a virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip3 install -r requirements.txt

# Run the API
uvicorn main:app --reload

# Print success message
echo "Virtual environment activated and dependencies installed!"
echo "You can now access the API documentation at: http://localhost:8000/docs"
