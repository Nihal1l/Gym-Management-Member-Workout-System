#!/bin/bash
# Render Deployment Setup Script
# This script prepares your Django app for Render deployment

echo "🚀 Gym Management API - Render Deployment Setup"
echo "=================================================="

# Check if required files exist
echo "✓ Checking required files..."
if [ ! -f "requirements.txt" ]; then
    echo "✗ requirements.txt not found!"
    exit 1
fi

if [ ! -f "manage.py" ]; then
    echo "✗ manage.py not found!"
    exit 1
fi

if [ ! -f "Procfile" ]; then
    echo "✗ Procfile not found!"
    exit 1
fi

echo "✓ All required files present"

# Create .env for local testing
echo ""
echo "📝 Creating .env file for testing..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env created from .env.example"
else
    echo "✓ .env already exists"
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo ""
echo "🗄️  Running migrations..."
python manage.py migrate

# Create test data
echo ""
echo "👥 Creating test data..."
python manage.py create_test_data

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Push to GitHub: git push -u origin main"
echo "2. Go to https://render.com"
echo "3. Follow RENDER_DEPLOYMENT.md instructions"
echo ""
echo "Test locally first:"
echo "  python manage.py runserver"
echo ""
