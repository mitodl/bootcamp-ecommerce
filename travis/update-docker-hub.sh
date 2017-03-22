#!/bin/bash
set -eo pipefail

docker build -t mitodl/bootcamp_web_travis -f Dockerfile .
docker build -t mitodl/bootcamp_watch_travis -f travis/Dockerfile-travis-watch-build .

docker push mitodl/bootcamp_web_travis
docker push mitodl/bootcamp_watch_travis
