#!/bin/sh
set -e

echo "▶️ Applying database migrations..."
# python manage.py makemigrations
python manage.py migrate
echo "✅ Migrations completed."
echo "========================================="

echo "▶️ Generating test data (5,000,000 products)..."
python manage.py create_test_products 5000000
echo "✅ Test data created."
echo "========================================="

echo "▶️ Rebuilding search index..."
python manage.py search_index --rebuild -f --parallel
echo "✅ Search index rebuilt."
echo "========================================="
echo ""
echo ""
echo ""

echo "▶️ Starting Django development server..."
exec python manage.py runserver 0.0.0.0:8000
