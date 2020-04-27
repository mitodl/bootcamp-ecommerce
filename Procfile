web: bin/start-nginx bin/start-pgbouncer newrelic-admin run-program uwsgi uwsgi.ini
worker: bin/start-pgbouncer celery -A main worker -B -l $BOOTCAMP_LOG_LEVEL
extra_worker: bin/start-pgbouncer celery -A main worker -l $BOOTCAMP_LOG_LEVEL
