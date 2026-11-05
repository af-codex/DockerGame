#!/bin/bash
set -euo pipefail
source ../checker_lib.sh

CONTAINER_NAME="my-nginx"
HOST_PORT=8080
EXPECTED_TEXT="<title>Welcome to nginx!</title>"

assert_container_running "$CONTAINER_NAME"

check_web_endpoint "$HOST_PORT" "$EXPECTED_TEXT" "$CONTAINER_NAME"
