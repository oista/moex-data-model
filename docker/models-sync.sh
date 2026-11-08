#!/bin/sh
# Fetch the models repository (fast-forward only) and publish the static viewer.
# No-op fetch when MOEX_MODELS_GIT_URL is empty: a bind-mounted checkout is enough.
# The next cycle starts only after this one returns, so a build longer than
# MOEX_MODELS_SYNC_INTERVAL does not overlap the next build. Do not shrink the
# interval to compensate.
set -eu

ROOT="${MOEX_MODELS_ROOT:-/models}"
REF="${MOEX_MODELS_GIT_REF:-main}"
URL="${MOEX_MODELS_GIT_URL:-}"
DIST="${MOEX_VIEWER_DIST:-/viewer-dist}"
INTERVAL="${MOEX_MODELS_SYNC_INTERVAL:-60}"
MARKER="model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml"
# moexmodel.git_sha is an image label and is not visible inside the process.
# Pass it as MOEX_IMAGE_GIT_SHA. Without it, hash the contracts manifest baked
# into this image.
MANIFEST="${MOEX_IMAGE_CONTRACTS_MANIFEST:-/app/generated/manifests/moex-dams-contracts.json}"

case "$INTERVAL" in
  ''|*[!0-9]*) INTERVAL=60 ;;
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
  if [ ! -d "$ROOT/.git" ] && [ ! -f "$ROOT/.git" ]; then
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

models_commit() {
  if [ -d "$ROOT/.git" ] || [ -f "$ROOT/.git" ]; then
    git -C "$ROOT" rev-parse HEAD
    return 0
  fi
  printf '%s\n' "nogit"
}

image_identity() {
  if [ -n "${MOEX_IMAGE_GIT_SHA:-}" ]; then
    printf '%s\n' "$MOEX_IMAGE_GIT_SHA"
    return 0
  fi
  if [ -f "$MANIFEST" ]; then
    if command -v sha256sum >/dev/null 2>&1; then
      sha256sum "$MANIFEST" | awk '{print $1}'
      return 0
    fi
    if command -v shasum >/dev/null 2>&1; then
      shasum -a 256 "$MANIFEST" | awk '{print $1}'
      return 0
    fi
  fi
  printf '%s\n' "unknown"
}

prune_releases() {
  [ -d "$DIST/releases" ] || return 0
  list=$(ls -1dt "$DIST/releases"/*/ 2>/dev/null || true)
  [ -n "$list" ] || return 0
  printf '%s\n' "$list" | awk 'NR>2' | while IFS= read -r dir; do
    [ -n "$dir" ] || continue
    rm -rf "$dir"
  done
}

publish_viewer() {
  commit="$1"
  image="$2"
  token="$3"
  ts=$(date -u +%Y%m%d%H%M%S)
  short=$(printf '%s' "$commit" | cut -c1-12)
  release="$DIST/releases/${short}-${ts}"
  mkdir -p "$release"
  snap=""
  build_root="$ROOT"
  if [ -n "$URL" ]; then
    snap=$(mktemp -d)
    mkdir -p "$snap/src"
    if ! git -C "$ROOT" archive --format=tar -o "$snap/src.tar" HEAD; then
      echo "WARNING: git archive failed" >&2
      rm -rf "$snap" "$release"
      return 0
    fi
    if ! tar -xf "$snap/src.tar" -C "$snap/src"; then
      echo "WARNING: snapshot extract failed" >&2
      rm -rf "$snap" "$release"
      return 0
    fi
    build_root="$snap/src"
  fi
  MOEX_BUILD_ROOT="$build_root"
  MOEX_BUILD_DIST="$release"
  export MOEX_BUILD_ROOT MOEX_BUILD_DIST
  start=$(date +%s)
  built=0
  if [ -n "${MOEX_VIEWER_BUILD:-}" ]; then
    if sh -c "$MOEX_VIEWER_BUILD"; then
      built=1
    fi
  else
    if python -m moex_publication_viewer.cli build --root "$build_root" --dist "$release"; then
      built=1
    fi
  fi
  end=$(date +%s)
  duration_ms=$(( (end - start) * 1000 ))
  if [ "$built" -ne 1 ]; then
    echo "WARNING: viewer build failed" >&2
    rm -rf "$release"
    if [ -n "$snap" ]; then
      rm -rf "$snap"
    fi
    return 0
  fi
  built_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  printf '%s\n' \
    '{' \
    "  \"commit\": \"${commit}\"," \
    "  \"built_at\": \"${built_at}\"," \
    "  \"image_sha\": \"${image}\"," \
    "  \"duration_ms\": ${duration_ms}," \
    '  "ok": true' \
    '}' > "$release/build-info.json"
  next="$DIST/.current-next"
  rm -rf "$next"
  ln -sfn "$release" "$next"
  # In the image, ln creates a symlink and mv -T replaces it in one rename.
  # A real directory only shows up when ln had to copy (no symlink privilege).
  if [ -d "$DIST/current" ] && [ ! -L "$DIST/current" ]; then
    rm -rf "$DIST/current"
  fi
  mv -T "$next" "$DIST/current"
  printf '%s\n' "$token" > "$DIST/.built-for"
  prune_releases
  if [ -n "$snap" ]; then
    rm -rf "$snap"
  fi
  echo "viewer built at $DIST/current"
}

run_once() {
  if ! sync_git; then
    echo "WARNING: git sync failed" >&2
    return 0
  fi
  if [ ! -f "$ROOT/$MARKER" ]; then
    echo "models marker not present yet: $ROOT/$MARKER"
    return 0
  fi
  commit=$(models_commit)
  image=$(image_identity)
  token="$commit $image"
  if [ -f "$DIST/.built-for" ]; then
    prev=$(cat "$DIST/.built-for")
    if [ "$prev" = "$token" ]; then
      echo "viewer already built for $token"
      return 0
    fi
  fi
  publish_viewer "$commit" "$image" "$token"
}

echo "models-sync root=$ROOT ref=$REF interval=${INTERVAL}s"
while true; do
  run_once
  if [ "${MOEX_SYNC_ONCE:-}" = "1" ]; then
    break
  fi
  sleep "$INTERVAL"
done
