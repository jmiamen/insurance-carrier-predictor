#!/bin/bash
# Setup script for carrier-predictor

set -e

echo "🚀 Setting up Carrier Predictor..."

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv .venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ Created .env file. Edit if needed."
else
    echo "✓ .env file already exists"
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/carriers data/index

# Make scripts executable
echo "🔐 Making scripts executable..."
chmod +x scripts/update_kb.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   source .venv/Scripts/activate"
else
    echo "   source .venv/bin/activate"
fi
echo ""
echo "2. Place carrier documents in data/carriers/"
echo ""
echo "3. Build the knowledge base:"
echo "   python scripts/update_kb.py --path data/carriers"
echo ""
echo "4. Start the server:"
echo "   uvicorn src.app:app --reload"
echo ""
echo "5. Open docs at http://localhost:8000/docs"
