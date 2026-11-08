#!/bin/sh
# Fetch the models repository (fast-forward only) and rebuild the static viewer.
# No-op fetch when MOEX_MODELS_GIT_URL is empty: a bind-mounted checkout is enough.
set -eu

ROOT="${MOEX_MODELS_ROOT:-/models}"
REF="${MOEX_MODELS_GIT_REF:-main}"
URL="${MOEX_MODELS_GIT_URL:-}"
DIST="${MOEX_VIEWER_DIST:-/viewer-dist}"
INTERVAL="${MOEX_MODELS_SYNC_INTERVAL:-300}"
MARKER="model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml"

case "$INTERVAL" in
  ''|*[!0-9]*) INTERVAL=300 ;;
esac
if [ "$INTERVAL" -lt 5 ]; then
  INTERVAL=5
fi

git config --global --add safe.directory "$ROOT" || true

run_git() {
  if [ -n "${MOEX_MODELS_DEPLOY_TOKEN:-}" ] && [ -z "${MOEX_MODELS_DEPLOY_USER:-}" ]; then
    echo "MOEX_MODELS_DEPLOY_USER is required when MOEX_MODELS_DEPLOY_TOKEN is set" >&2
    return 1
  fi
  if [ -n "${MOEX_MODELS_DEPLOY_TOKEN:-}" ]; then
    basic=$(printf '%s:%s' "$MOEX_MODELS_DEPLOY_USER" "$MOEX_MODELS_DEPLOY_TOKEN" | base64 -w 0)
    header="http.extraHeader=Authorization: Basic ${basic}"
    if [ -n "${MOEX_GITLAB_CA_BUNDLE:-}" ]; then
      git -c "$header" -c "http.sslCAInfo=${MOEX_GITLAB_CA_BUNDLE}" "$@"
    else
      git -c "$header" "$@"
    fi
    return
  fi
  if [ -n "${MOEX_GITLAB_CA_BUNDLE:-}" ]; then
    git -c "http.sslCAInfo=${MOEX_GITLAB_CA_BUNDLE}" "$@"
    return
  fi
  git "$@"
}

sync_git() {
  if [ -z "$URL" ]; then
    echo "MOEX_MODELS_GIT_URL is empty; skip fetch"
    return 0
  fi
  if [ ! -d "$ROOT/.git" ]; then
    if [ -n "$(ls -A "$ROOT" 2>/dev/null || true)" ]; then
      echo "ERROR: $ROOT is not a git checkout and is not empty" >&2
      return 1
    fi
    run_git clone --branch "$REF" --single-branch "$URL" "$ROOT"
    return 0
  fi
  git -C "$ROOT" remote set-url origin "$URL"
  run_git -C "$ROOT" fetch origin "$REF"
  git -C "$ROOT" checkout "$REF"
  git -C "$ROOT" merge --ff-only FETCH_HEAD
}

restore_fetched_tree() {
  # The viewer writes publication_conformance.json into the models tree.
  # Drop those files so the next fast-forward is not blocked. Only after a
  # fetch this script owns: an empty GIT_URL means the tree is a bind mount.
  if [ -z "$URL" ] || [ ! -d "$ROOT/.git" ]; then
    return 0
  fi
  git -C "$ROOT" reset --hard HEAD
  git -C "$ROOT" clean -fd
  echo "restored $ROOT to HEAD"
}

build_viewer() {
  if [ ! -f "$ROOT/$MARKER" ]; then
    echo "models marker not present yet: $ROOT/$MARKER"
    return 0
  fi
  if python -m moex_publication_viewer.cli build --root "$ROOT" --dist "$DIST"; then
    echo "viewer built at $DIST"
  else
    echo "WARNING: viewer build failed" >&2
  fi
  restore_fetched_tree
}

echo "models-sync root=$ROOT ref=$REF interval=${INTERVAL}s"
while true; do
  if sync_git; then
    build_viewer
  else
    echo "WARNING: git sync failed" >&2
  fi
  sleep "$INTERVAL"
done
