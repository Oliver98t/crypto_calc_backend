cd server
python manage.py makemigrations
python manage.py migrate
gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile - --error-logfile - server.wsgi:application