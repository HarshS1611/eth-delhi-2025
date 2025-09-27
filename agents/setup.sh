#!/bin/bash

echo "🚀 Setting up Dataset Validation Agent"
echo "====================================="

# Check if Python 3 is installed
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 is installed: $(python3 --version)"
else
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip3 is available
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 is available"
else
    echo "❌ pip3 is not available. Please install pip3."
    exit 1
fi

echo ""
echo "📦 Installing required packages..."

# Install packages
pip3 install uagents pandas numpy jsonschema

if [ $? -eq 0 ]; then
    echo "✅ Packages installed successfully!"
else
    echo "❌ Package installation failed. Please check your pip3 installation."
    exit 1
fi

echo ""
echo "🧪 Running test validation..."

# Run the test script
python3 test_validation.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run the main agent: python3 dataset_validation_agent.py"
echo "2. In another terminal, run: python3 validation_client.py"
echo "3. Check the README.md for detailed usage instructions"