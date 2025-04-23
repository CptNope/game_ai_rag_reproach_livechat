
#!/bin/bash

echo "Setting up MegaMan AI environment..."

# Install system dependencies
sudo apt update
sudo apt install -y git python3 python3-pip wget unzip

# Optional: Install RetroArch
if ! command -v retroarch &> /dev/null; then
  echo "Installing RetroArch..."
  sudo apt install -y retroarch
else
  echo "RetroArch is already installed."
fi

# Install Python dependencies
pip install -U pip
pip install axolotl accelerate bitsandbytes peft transformers sentence-transformers mss pillow pytesseract

# Check for Ollama
if ! command -v ollama &> /dev/null; then
  echo "Warning: Ollama is not installed."
  echo "Download it from https://ollama.com/download"
else
  echo "Ollama is installed. You can optionally run:"
  echo "    ollama run deepseek-coder"
fi

# Suggest downloading DeepSeek model manually if not using Ollama
echo "If using HuggingFace: Download deepseek-ai/deepseek-coder-1.3b-base from HuggingFace manually."

echo "Setup complete."
