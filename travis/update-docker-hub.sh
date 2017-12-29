#!/bin/bash
set -eo pipefail

docker build -t mitodl/bootcamp_web_travis_next -f Dockerfile .
docker build -t mitodl/bootcamp_watch_travis_next -f travis/Dockerfile-travis-watch-build .

docker push mitodl/bootcamp_web_travis_next
docker push mitodl/bootcamp_watch_travis_next
