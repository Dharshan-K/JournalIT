#!/bin/bash

# Set variables
VENV_NAME="JournalIT"
REQUIREMENTS_FILE="requirements.txt"

# Function to print colored output
print_step() {
    echo -e "\033[1;34m[SETUP]\033[0m $1"
}

# Check if virtual environment already exists
if [ -d "$VENV_NAME" ]; then
    print_step "Virtual environment already exists. Removing existing environment."
    rm -rf "$VENV_NAME"
fi

# Create virtual environment
wget https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf
print_step "Creating virtual environment..."
python3 -m venv "$VENV_NAME"

# Activate virtual environment
print_step "Activating virtual environment..."
source "$VENV_NAME/bin/activate"

# Check if requirements.txt exists
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo -e "\033[1;31m[ERROR] requirements.txt not found!\033[0m"
    exit 1
fi

# Install requirements
print_step "Installing requirements..."
pip install --upgrade pip
pip install -r "$REQUIREMENTS_FILE"

# Print completion message
print_step "Setup complete! Virtual environment is active."

# Optional: Provide instructions for deactivation
echo -e "\n\033[1;33mTo deactivate the virtual environment, run: deactivate\033[0m"