#!/usr/bin/env bash
# shellcheck disable=SC2145,SC2068
status=0

echohighlight() {
	echo -e "\x1b[32;1m$@\x1b[0m"
}

function run_test {
	echohighlight "[TEST SUITE] $@"
	poetry run $@
	local test_status=$?
	if [ $test_status -ne 0 ]; then
		status=$test_status
	fi
	return $status
}

run_test pytest --no-pylint

exit $status
