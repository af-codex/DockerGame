#!/bin/bash
set -euo pipefail

GREEN=$(tput setaf 2 2>/dev/null || true)
YELLOW=$(tput setaf 3 2>/dev/null || true)
RED=$(tput setaf 1 2>/dev/null || true)
CYAN=$(tput setaf 6 2>/dev/null || true)
RESET=$(tput sgr0 2>/dev/null || true)

CHECKER_LIB="../checker_lib.sh"

checked=0
failed=0

while IFS= read -r check_script; do
  dir=$(dirname "$check_script")

  cd "$dir"

  # Resolve the real path of the checker library relative to the current exercise
  if [[ -f "$CHECKER_LIB" ]]; then
    lib_path="$CHECKER_LIB"
  elif [[ -f "../../checker_lib.sh" ]]; then
    lib_path="../../checker_lib.sh"
  elif [[ -f "../checklib_sh" ]]; then
    lib_path="../checklib_sh"
  else
    echo -e "${RED}Library not found for $dir${RESET}"
    cd - >/dev/null
    ((failed++))
    continue
  fi

  if shellcheck -x "$lib_path" "check.sh"; then
    echo -e "${GREEN}$dir is clean!${RESET}"
  else
    echo -e "${RED}Issues found in $dir/check.sh${RESET}"
    ((failed++))
  fi

  ((checked++))

  cd - >/dev/null
done < <(find . -type f -name "check.sh" | sort)

echo -e "${CYAN}Done! Checked: $checked exercise(s)${RESET}"
if ((failed > 0)); then
  echo -e "${RED}Failed: $failed with issues${RESET}"
  exit 1
else
  echo -e "${GREEN}All clean!${RESET}"
  exit 0
fi
