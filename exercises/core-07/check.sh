#!/bin/bash
set -euo pipefail
source ../checker_lib.sh

IMAGE_NAME="dockerlings-core-07-test"
CONTAINER_NAME="core-07-checker"
HOST_PORT=8007
EXPECTED_TEXT="My Custom Nginx Site"

IMAGES_TO_CLEAN+=("$IMAGE_NAME")
CONTAINERS_TO_CLEAN+=("$CONTAINER_NAME")

require_file "Dockerfile"

build_image "$IMAGE_NAME"

log_info "Running the container..."
docker run -d --name "$CONTAINER_NAME" -p "$HOST_PORT":80 "$IMAGE_NAME" >/dev/null

check_web_endpoint "$HOST_PORT" "$EXPECTED_TEXT" "$CONTAINER_NAME"
