#!/bin/bash
# Setup script for Macro Tracker using Conda

echo "=================================="
echo "Macro Tracker - Conda Setup"
echo "=================================="
echo ""

# Check if conda is installed
if ! command -v conda &> /dev/null
then
    echo "❌ Conda is not installed!"
    echo ""
    echo "Please install Miniconda or Anaconda first:"
    echo "  Miniconda: https://docs.conda.io/en/latest/miniconda.html"
    echo "  Anaconda: https://www.anaconda.com/download"
    exit 1
fi

echo "✓ Conda found: $(conda --version)"
echo ""

# Create conda environment
echo "Creating conda environment from environment.yml..."
conda env create -f environment.yml

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Conda environment created successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Activate the environment:"
    echo "   conda activate macro_tracker"
    echo ""
    echo "2. Configure your .env file:"
    echo "   cp .env.example .env"
    echo "   # Then edit .env with your API keys"
    echo ""
    echo "3. Test the setup:"
    echo "   python test_setup.py"
    echo ""
    echo "4. Run the app:"
    echo "   python app.py"
    echo ""
else
    echo ""
    echo "❌ Failed to create conda environment"
    echo ""
    echo "Try running manually:"
    echo "  conda env create -f environment.yml"
    exit 1
fi
