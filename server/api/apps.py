from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    # TODO perdiodic update mechanism
    def ready(self):
        # start thread that periodcially updates DB
        # DONT FORGET "python manage.py runserver --noreload"
        print("<------------------------------Crypto Calc Backend Boot--------------------------->")
        
        return