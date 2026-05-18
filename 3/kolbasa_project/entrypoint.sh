#!/bin/bash
mkdir -p /app/db
python manage.py migrate --noinput
echo "Running tests..."
python manage.py test catalog.tests.test_routes catalog.tests.test_content catalog.tests.test_models catalog.tests.test_roles --noinput --verbosity=2
TEST_EXIT=$?
if [ $TEST_EXIT -ne 0 ]; then
  echo "Tests failed, exiting."
  exit 1
fi
echo "Tests passed. Starting gunicorn..."
gunicorn kolbasa_project.wsgi:application --bind 0.0.0.0:8000 --workers 3