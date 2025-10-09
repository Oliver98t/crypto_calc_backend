cd server
python manage.py makemigrations
python manage.py migrate
#python manage.py runserver 0.0.0.0:8000 # uncomment if you want to debug
gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile - --error-logfile - server.wsgi:application
