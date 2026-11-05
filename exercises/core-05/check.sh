#!/bin/bash
set -euo pipefail
source ../checker_lib.sh

IMAGE_NAME="dockerlings-core-05-test"
CONTAINER_NAME="core-05-checker"
HOST_PORT=5005
EXPECTED_TEXT="Hello, Docker!"

CONTAINERS_TO_CLEAN+=("$CONTAINER_NAME")
IMAGES_TO_CLEAN+=("$IMAGE_NAME")

require_file "Dockerfile"
build_image "$IMAGE_NAME"

log_info "Running the container..."
docker run -d --name "$CONTAINER_NAME" -p "$HOST_PORT":5000 "$IMAGE_NAME" >/dev/null

check_web_endpoint "$HOST_PORT" "$EXPECTED_TEXT" "$CONTAINER_NAME"
