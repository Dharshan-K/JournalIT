#!/bin/bash
mkdir models
wget -O models/phi-2.Q4_K_M.gguf https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf 
# Install requirements
pip install -r requirements.txt
