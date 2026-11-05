#!/bin/bash
set -euo pipefail
source ../checker_lib.sh

NETWORK_NAME="c10-network"
DB_CONTAINER_NAME="c10-db"
APP_CONTAINER_NAME="c10-app"

CONTAINERS_TO_CLEAN+=("$APP_CONTAINER_NAME" "$DB_CONTAINER_NAME")
NETWORKS_TO_CLEAN+=("$NETWORK_NAME")

log_info "Checking if network '$NETWORK_NAME' exists..."
if ! docker network ls --filter "name=^$NETWORK_NAME$" | grep -q "$NETWORK_NAME"; then
  log_fail "Network '$NETWORK_NAME' not found." "Did you create the network first with 'docker network create $NETWORK_NAME'?"
fi
log_success "Network found."

require_file "run-containers.sh"

log_info "Executing your 'run-containers.sh' script..."
chmod +x run-containers.sh
./run-containers.sh
sleep 5

for name in $APP_CONTAINER_NAME $DB_CONTAINER_NAME; do
  assert_container_running "$name"
  log_info "Verifying container '$name' is on the correct network..."
  NETWORK=$(docker inspect --format='{{.HostConfig.NetworkMode}}' "$name")
  if [ "$NETWORK" != "$NETWORK_NAME" ]; then
    log_fail "Container '$name' is not on the '$NETWORK_NAME' network." "Did you include the '--network $NETWORK_NAME' flag in your 'docker run' command?"
  fi
done
log_success "Both containers are running on the correct network."

log_info "Testing name resolution from '$APP_CONTAINER_NAME' to '$DB_CONTAINER_NAME'..."
if docker exec "$APP_CONTAINER_NAME" ping -c 1 "$DB_CONTAINER_NAME"; then
  log_success "Container '$APP_CONTAINER_NAME' successfully resolved and pinged '$DB_CONTAINER_NAME'."
else
  log_fail "Container '$APP_CONTAINER_NAME' could not ping '$DB_CONTAINER_NAME' by its name." "Ensure both containers were launched with the '--network $NETWORK_NAME' flag."
fi
