#!/bin/bash
# FamSync WhatsApp Agent — start script
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check .env exists
if [ ! -f ".env" ]; then
  echo "ERROR: .env file not found. Copy .env.example to .env and fill in your keys."
  exit 1
fi

# Check ANTHROPIC_API_KEY is set
source .env
if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "sk-ant-..." ]; then
  echo "ERROR: ANTHROPIC_API_KEY not set in .env"
  exit 1
fi

echo "Installing/updating dependencies..."
pip3 install -r requirements.txt -q

echo ""
echo "Starting FamSync WhatsApp Agent on port 5051..."
python3 server.py
