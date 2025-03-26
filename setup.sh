#!/bin/bash

wget https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf

# Install requirements
print_step "Installing requirements..."
pip install --upgrade pip
pip install -r "$REQUIREMENTS_FILE"
