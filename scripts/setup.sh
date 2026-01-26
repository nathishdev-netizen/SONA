#!/bin/bash

# SONA AI - Development Environment Setup Script
echo "🧠 Setting up SONA AI Development Environment..."

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your API keys!"
fi

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd ../frontend
pip install -r requirements.txt

cd ..

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update backend/.env with your API keys"
echo "2. Start PostgreSQL: brew services start postgresql"
echo "3. Run backend: cd backend && uvicorn src.main:app --reload"
echo "4. Run frontend: cd frontend && streamlit run app.py"
echo ""
echo "Or use Docker:"
echo "docker-compose -f infrastructure/docker/docker-compose.yml up"
