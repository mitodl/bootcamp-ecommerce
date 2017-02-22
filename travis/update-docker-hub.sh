#!/bin/bash
set -eo pipefail

docker build -t mitodl/mm_web_travis -f Dockerfile .
docker build -t mitodl/mm_watch_travis -f travis/Dockerfile-travis-watch-build .

docker push mitodl/mm_web_travis
docker push mitodl/mm_watch_travis
