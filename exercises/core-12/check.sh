#!/bin/bash
set -euo pipefail
source ../checker_lib.sh

COMPOSE_FILE="docker-compose.yml"
CONTAINER_NAME="c12-redis"
SERVICE_NAME="redis-server"
HOST_PORT="6379"
PROJECT_NAME=$(basename "$PWD")
NETWORK_NAME="${PROJECT_NAME}_default"

project_cleanup() {
  log_info "Shutting down Docker Compose project..."
  if [ -f "$COMPOSE_FILE" ]; then
    docker compose down -v --remove-orphans >/dev/null 2>&1 || true
  fi
}
trap 'project_cleanup; cleanup' EXIT

require_file "$COMPOSE_FILE"

log_info "Running 'docker compose up -d'..."
if ! docker compose up -d; then
  log_fail "'docker compose up -d' command failed." "Check the syntax of your '$COMPOSE_FILE'. Is the YAML valid?"
fi

assert_container_running "$CONTAINER_NAME"

log_info "Verifying port mapping..."
if ! docker port "$CONTAINER_NAME" "$HOST_PORT" >/dev/null 2>&1; then
  log_fail "Port $HOST_PORT is not published." "Did you include the 'ports' section in your '$COMPOSE_FILE' correctly?"
fi
log_success "Port mapping is correct."

log_info "Checking Redis responsiveness..."
if docker run --rm --network "$NETWORK_NAME" redis:alpine redis-cli -h "$SERVICE_NAME" PING | grep -q "PONG"; then
  log_success "The Redis service is running and responsive. Docker Compose setup is correct."
else
  log_fail "Could not get a 'PONG' response from the Redis container." "Is the Redis container running correctly? Check its logs with 'docker compose logs'."
fi
