#!/usr/bin/env bash
# build_files.sh

echo "Installing dependencies from requirements.txt..."
# Menggunakan 'python' saja, bukan 'python3.10'
python -m pip install -r requirements.txt

echo "Collecting static files..."
# Menggunakan 'python' saja
python manage.py collectstatic --noinput --clear

echo "Running database migrations..."
# Menggunakan 'python' saja
python manage.py migrate

echo "Loading initial data from databackup_final.json..."
# Menggunakan 'python' saja
python manage.py loaddata databackup_final.json

echo "Build process complete."