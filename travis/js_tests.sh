#!/bin/bash

status=0

function run_test {
    "$@"
    local test_status=$?
    if [ $test_status -ne 0 ]; then
        status=$test_status
    fi
    return $status
}

run_test yarn run codecov
run_test yarn run lint
run_test yarn run fmt:check
run_test yarn run scss_lint
run_test yarn run flow
NODE_ENV=production
run_test ./webpack_if_prod.sh

exit $status
