#!/usr/bin/env bash
# build_files.sh

echo "Installing dependencies from requirements.txt..."
# Menggunakan 'python3' saja
python3 -m pip install -r requirements.txt

echo "Collecting static files..."
# Menggunakan 'python3' saja
python3 manage.py collectstatic --noinput --clear

echo "Running database migrations..."
# Menggunakan 'python3' saja
python3 manage.py migrate

echo "Loading initial data from databackup_final.json..."
# Menggunakan 'python3' saja
python3 manage.py loaddata databackup_final.json

echo "Build process complete."