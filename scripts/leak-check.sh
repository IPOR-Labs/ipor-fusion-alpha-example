#!/usr/bin/env bash
# Fails when stdin names something internal. This repository is public, so the
# names themselves are not here: one extended regex per line comes from
# $LEAK_PATTERNS (CI, a repository secret) or from the file
# ${XDG_CONFIG_HOME:-~/.config}/ipor/leak-patterns (local). Issue-tracker keys
# are built in.
#
#   git log --format=%B origin/main.. | scripts/leak-check.sh
set -euo pipefail

BUILTIN_LEAKS='(^|[^A-Za-z0-9])IL-[0-9]+'

leak_patterns() {
  printf '%s\n' "${BUILTIN_LEAKS}"
  if [ -n "${LEAK_PATTERNS:-}" ]; then
    printf '%s\n' "${LEAK_PATTERNS}"
  else
    local file="${XDG_CONFIG_HOME:-${HOME}/.config}/ipor/leak-patterns"
    [ -f "${file}" ] && cat "${file}"
  fi
  return 0
}

patterns=$(leak_patterns | grep -vE '^[[:space:]]*(#|$)')
rc=0
hits=$(grep -inE -f <(printf '%s\n' "${patterns}")) || rc=$?
case "${rc}" in
  0) ;;
  1) exit 0 ;;
  # A broken pattern must not pass everything, the built-in one included.
  *) echo "Leak check failed (grep exit ${rc}): fix the leak patterns." >&2; exit 2 ;;
esac
echo "Internal references (issue keys, internal hosts, private names) do not belong in this public repository:" >&2
printf '%s\n' "${hits}" >&2
exit 1
