web: bin/start-nginx bin/start-pgbouncer newrelic-admin run-program uwsgi uwsgi.ini
worker: bin/start-pgbouncer newrelic-admin run-program celery -A main worker -E -B -l $BOOTCAMP_LOG_LEVEL
extra_worker: bin/start-pgbouncer newrelic-admin run-program celery -A main worker -E -l $BOOTCAMP_LOG_LEVEL
