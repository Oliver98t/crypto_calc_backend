from django.apps import AppConfig, apps
import time
import threading
import logging
import atexit

from tests import API_test

logger = logging.getLogger(__name__)

SECONDS_IN_HOUR = 3600
START_UP_TIME_S = 5

periodic_DB_update_thread = None

def start_periodic_DB_update():
    t = threading.Thread(target=periodic_DB_update, daemon=True)
    t.start()

def periodic_DB_update():
    logger.info("App loading")
    # allow django to be fully loaded before making http request
    time.sleep(START_UP_TIME_S)
    logger.info("App loaded")

    while True:
        API_test.update_all_pairs()
        logger.info("DB updated")
        time.sleep(SECONDS_IN_HOUR)

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    # TODO perdiodic update mechanism
    def ready(self):
        # start thread that periodcially updates DB
        # DONT FORGET "python manage.py runserver --noreload"
        print("<------------------------------Crypto Calc Backend Boot--------------------------->")
        start_periodic_DB_update()
        return