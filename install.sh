#!/bin/bash

echo "================================================================"
echo "  SHCAP Installation Script"
echo "  SmallHolder Carbon Assessment Platform"
echo "================================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 is installed"
PYTHON_VERSION=$(python3 --version)
echo "  $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠ Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check environment variables
echo "Checking environment variables..."
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create a .env file with the required variables."
    exit 1
fi

source .env

if [ -z "$DATABASE_URL" ]; then
    echo "⚠ DATABASE_URL not set in .env"
else
    echo "✓ DATABASE_URL is configured"
fi

if [ -z "$SECRET_KEY" ]; then
    echo "⚠ SECRET_KEY not set in .env"
else
    echo "✓ SECRET_KEY is configured"
fi

if [ -z "$MAIL_USERNAME" ]; then
    echo "⚠ Email not configured (2FA and password reset will not work)"
else
    echo "✓ Email is configured"
fi
echo ""

# Run tests
echo "Running system verification tests..."
python test_auth.py
echo ""

echo "================================================================"
echo "  Installation Complete!"
echo "================================================================"
echo ""
echo "Next steps:"
echo "1. Configure email settings in .env (if not done)"
echo "2. Run the application:"
echo "   • Development: python app.py"
echo "   • Quick start: ./run.sh"
echo "   • Production: gunicorn wsgi:app"
echo ""
echo "3. Open your browser to: http://localhost:5000"
echo ""
echo "For more information, see:"
echo "  • README.md - Complete documentation"
echo "  • QUICKSTART.md - Getting started guide"
echo "  • DEPLOYMENT.md - Production deployment"
echo ""
echo "================================================================"
