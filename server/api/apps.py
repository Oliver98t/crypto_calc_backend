from django.apps import AppConfig
import time
import threading

def periodic_DB_update(delay: int):
    #while True:
    print("here")
    time.sleep(delay)


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    # TODO perdiodic update mechanism
    def ready(self):
        # start thread that periodcially updates DB
        # DONT FORGET "python manage.py runserver --noreload"
        print("<------------------------------Crypto Calc Backend Boot--------------------------->")
        
        t = threading.Thread(target=periodic_DB_update, args=(1,))
        t.start()
        
        return