web: bin/start-nginx bin/start-pgbouncer-stunnel newrelic-admin run-program uwsgi uwsgi.ini
worker: celery -A bootcamp worker -B
extra_worker: celery -A bootcamp worker
