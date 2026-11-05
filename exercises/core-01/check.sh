#!/bin/bash
set -euo pipefail
source ../checker_lib.sh

IMAGE_NAME="dockerlings-core-01"
EXPECTED_OUTPUT="Hello Docker"

IMAGES_TO_CLEAN+=("$IMAGE_NAME")

build_image "$IMAGE_NAME"

log_info "Running container and capturing output..."
OUTPUT=$(docker run --rm "$IMAGE_NAME")

log_info "Checking the container's output..."
if [ "$OUTPUT" == "$EXPECTED_OUTPUT" ]; then
  log_success "The container produced the correct output."
else
  log_fail "The container output was incorrect." "Expected: '$EXPECTED_OUTPUT', Got: '$OUTPUT'"
fi
