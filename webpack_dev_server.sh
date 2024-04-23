#!/bin/bash
set -ef -o pipefail

WEBPACK_HOST='0.0.0.0'
WEBPACK_PORT='8098'

# The webpack server should only be run in one of two cases:
#    1) We are running Linux and inside the Docker container
#    2) We're on an OSX host machine. Our current workflow for developing on a Docker container involves running
#       the webpack server on the host machine rather than the container.
# If neither of those are true, running this script is basically a no-op.

if [[ $1 == "--install" ]]; then
	yarn install --frozen-lockfile && echo "Finished yarn install"
fi
# Start the webpack dev server on the appropriate host and port
node ./hot-reload-dev-server.js --host "$WEBPACK_HOST" --port "$WEBPACK_PORT"
