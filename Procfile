web: bin/start-nginx bin/start-pgbouncer newrelic-admin run-program uwsgi uwsgi.ini
worker: bin/start-pgbouncer celery -A bootcamp worker -B -l $BOOTCAMP_LOG_LEVEL
extra_worker: bin/start-pgbouncer celery -A bootcamp worker -l $BOOTCAMP_LOG_LEVEL
