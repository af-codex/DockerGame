#!/bin/bash
set -euo pipefail
source ../checker_lib.sh

USER_CONTAINER_NAME="c11-server"
HOST_PORT="8011"
CONTAINER_PORT="8080"
CHECKER_IMAGE_NAME="dockerlings-c11-test"
EXPECTED_TEXT="Hello from a container"

IMAGES_TO_CLEAN+=("$CHECKER_IMAGE_NAME")

require_file "Dockerfile"
build_image "$CHECKER_IMAGE_NAME"

log_info "Checking for 'EXPOSE $CONTAINER_PORT' in the image metadata..."
if ! docker inspect --format='{{json .Config.ExposedPorts}}' "$CHECKER_IMAGE_NAME" | grep -q "\"$CONTAINER_PORT/tcp\""; then
  log_fail "The image metadata does not show port '$CONTAINER_PORT' as exposed." "Did you add 'EXPOSE $CONTAINER_PORT' to your Dockerfile?"
fi
log_success "EXPOSE instruction found in the image."

assert_container_running "$USER_CONTAINER_NAME"

log_info "Verifying port mapping on the running container..."
PORT_MAPPING=$(docker port "$USER_CONTAINER_NAME" "$CONTAINER_PORT")
EXPECTED_MAPPING="0.0.0.0:$HOST_PORT"

if ! echo "$PORT_MAPPING" | grep -q "$EXPECTED_MAPPING"; then
  log_fail "Container port $CONTAINER_PORT is not correctly published to host port $HOST_PORT." "Did you use the '-p $HOST_PORT:$CONTAINER_PORT' flag in your 'docker run' command?"
fi
log_success "Port mapping is correct."

check_web_endpoint "$HOST_PORT" "$EXPECTED_TEXT" "$USER_CONTAINER_NAME"
