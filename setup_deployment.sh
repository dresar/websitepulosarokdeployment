#!/bin/bash

# Setup Deployment Script untuk Hosting
# Mode Tidak Ketat - Fokus pada Fungsionalitas

echo "🚀 Setting up deployment untuk hosting..."

# Set environment variables
export DATABASE_ENGINE=django.db.backends.sqlite3
export DATABASE_NAME=db.sqlite3
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OMP_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMBA_NUM_THREADS=1

# Set permissions
echo "📁 Setting permissions..."
chmod 755 passenger_wsgi.py
chmod 644 .htaccess
chmod 644 deployment_config.env
chmod 755 logs/
chmod 755 staticfiles/
chmod 755 media/
chmod 644 db.sqlite3

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3.10 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements_hosting_simple.txt

# Run migrations
echo "🗄️ Running migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser (optional)
echo "👤 Creating superuser (optional)..."
echo "You can create superuser manually with: python manage.py createsuperuser"

# Test deployment
echo "🧪 Testing deployment..."
python manage.py check --deploy

echo "✅ Deployment setup completed!"
echo "🌐 Your website should be accessible at your domain"
echo "📝 Check logs/django.log for any issues"
