web: bin/start-nginx bin/start-pgbouncer-stunnel newrelic-admin run-program uwsgi uwsgi.ini
worker: celery -A bootcamp worker -B -l $BOOTCAMP_LOG_LEVEL
extra_worker: celery -A bootcamp worker -l $BOOTCAMP_LOG_LEVEL
