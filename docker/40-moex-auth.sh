#!/bin/sh
# Nginx entrypoint snippet: turn auth/htpasswd into auth_basic, or refuse
# to start when the server mode trusts the proxy and the file is missing.
set -eu

HTPASSWD="${MOEX_AUTH_HTPASSWD:-/etc/nginx/auth/htpasswd}"
AUTH_INC="${MOEX_AUTH_INC:-/etc/nginx/conf.d/auth.inc}"
MODE="${MOEX_AUTH_MODE:-dev}"

mkdir -p "$(dirname "$AUTH_INC")"

if [ -f "$HTPASSWD" ]; then
  printf 'auth_basic "MOEX";\nauth_basic_user_file %s;\n' "$HTPASSWD" > "$AUTH_INC"
  exit 0
fi

if [ "$MODE" = "trusted-header" ]; then
  echo "MOEX_AUTH_MODE=trusted-header requires $HTPASSWD (see .env.example)" >&2
  exit 1
fi

echo "WARNING: $HTPASSWD is missing; nginx will not ask for a password" >&2
: > "$AUTH_INC"
