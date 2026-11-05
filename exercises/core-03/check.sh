#!/bin/bash
set -euo pipefail
source ../checker_lib.sh

LOG_FILE="logs.txt"
EXPECTED_LINES=(
  "Starting process..."
  "Process is running."
  "Process finished."
)

require_file "$LOG_FILE"

log_info "Checking contents of '$LOG_FILE'..."
for line in "${EXPECTED_LINES[@]}"; do
  if ! grep -Fq "$line" "$LOG_FILE"; then
    log_fail "Could not find the expected log line in '$LOG_FILE'." "Missing line: \"$line\""
  fi
done

log_success "All expected log lines were found in '$LOG_FILE'."
