#!/usr/bin/env bash
# build_files.sh

echo "Installing dependencies from requirements.txt..."
# Menggunakan python3.10 sesuai dengan runtime di vercel.json
python3.10 -m pip install -r requirements.txt

echo "Collecting static files..."
# --noinput: tidak meminta konfirmasi
# --clear: menghapus file statis lama sebelum mengumpulkan yang baru
python3.10 manage.py collectstatic --noinput --clear

echo "Running database migrations..."
python3.10 manage.py migrate

echo "Build process complete."