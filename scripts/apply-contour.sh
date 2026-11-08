#!/usr/bin/env bash
# Apply a contour drop on a closed host (ADR-058).
# Usage:
#   bash apply-contour.sh /path/to/moex-model-*-contour.zip
#   bash apply-contour.sh
# Env:
#   DEPLOY_DIR=/opt/moex-data-model
#   APPLY_ALLOW_DOWNGRADE=1
#   SKIP_COMPOSE=1
set -euo pipefail

DEPLOY_DIR="${DEPLOY_DIR:-/opt/moex-data-model}"
SKIP_COMPOSE="${SKIP_COMPOSE:-0}"
WORK="${CONTOUR_WORK:-/tmp/moex-contour-apply}"

die() { echo "ERROR: $*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "missing command: $1"; }

need docker
need unzip
need bash

json_field() {
  awk -v key="$1" '
    $0 ~ "\"" key "\"" {
      line = $0
      sub(/^[^:]*:[[:space:]]*/, "", line)
      gsub(/[",[:space:]]/, "", line)
      print line
      exit
    }
  ' "$2"
}

verify_sha256() {
  local sumfile="$1"
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum -c "$sumfile"
    return
  fi
  if command -v shasum >/dev/null 2>&1; then
    local expected actual fname
    expected="$(awk '{print $1}' "$sumfile")"
    fname="$(awk '{print $2}' "$sumfile")"
    fname="${fname#\*}"
    [[ -f "$fname" ]] || die "sha file references missing: $fname"
    actual="$(shasum -a 256 "$fname" | awk '{print $1}')"
    [[ "$expected" == "$actual" ]] || die "sha256 mismatch for $fname"
    echo "$fname: OK"
    return
  fi
  die "need sha256sum or shasum"
}

# Info-ZIP: 0=ok, 1=warnings, >=2=hard error.
unzip_ok() {
  local rc=0
  unzip "$@" || rc=$?
  if [[ "$rc" -gt 1 ]]; then
    die "unzip failed (exit $rc)"
  fi
  if [[ "$rc" -eq 1 ]]; then
    echo "WARNING: unzip reported warnings (exit 1); continuing"
  fi
}

ZIP="${1:-}"
if [[ -z "$ZIP" ]]; then
  shopt -s nullglob
  zips=(moex-model-*-contour.zip)
  shopt -u nullglob
  if [[ ${#zips[@]} -eq 1 ]]; then
    ZIP="${zips[0]}"
  elif [[ ${#zips[@]} -gt 1 ]]; then
    die "several contour zips here; pass one: bash apply-contour.sh <file>"
  else
    die "usage: bash apply-contour.sh /path/to/moex-model-*-contour.zip"
  fi
fi
[[ -f "$ZIP" ]] || die "not a file: $ZIP"
case "$ZIP" in
  *.zip) ;;
  *.tar.gz|*.tgz|*.gz)
    die "this is gzip/tar, not a contour zip. Use: unzip moex-model-*-contour.zip (never gunzip the contour zip)"
    ;;
  *) die "expected .zip (contour drop), got: $ZIP" ;;
esac

echo "Contour zip: $ZIP"
echo "Deploy dir:  $DEPLOY_DIR"
rm -rf "$WORK"
mkdir -p "$WORK"
unzip_ok -qo "$ZIP" -d "$WORK"
cd "$WORK"

if [[ -f APPLY.md ]]; then
  echo "---- APPLY.md (head) ----"
  head -n 24 APPLY.md || true
  echo "-------------------------"
fi

TAG=""
MODE=""

shopt -s nullglob
overlays=(moex-model-*-overlay.zip)
tars=(moex-model-*.tar.gz)
shopt -u nullglob

if [[ ${#overlays[@]} -gt 0 ]]; then
  MODE="overlay"
  OV="${overlays[0]}"
  if [[ -f "${OV}.sha256" ]]; then
    echo "Verify ${OV}.sha256 ..."
    verify_sha256 "${OV}.sha256"
  fi
  echo "Apply Overlay: $OV"
  rm -rf overlay-stage
  mkdir overlay-stage
  unzip_ok -qo "$OV" -d overlay-stage
  (
    cd overlay-stage
    chmod +x apply-overlay.sh 2>/dev/null || true
    if [[ -n "${APPLY_ALLOW_DOWNGRADE:-}" ]]; then
      export APPLY_ALLOW_DOWNGRADE
    fi
    bash apply-overlay.sh
  )
  if [[ -f overlay-stage/overlay.manifest.json ]]; then
    TAG="$(json_field new_tag overlay-stage/overlay.manifest.json)"
  fi
  if [[ -z "$TAG" ]]; then
    TAG="$(basename "$OV" .zip)"
    TAG="${TAG#moex-model-}"
    TAG="${TAG%-overlay}"
  fi
elif [[ ${#tars[@]} -gt 0 ]]; then
  MODE="full"
  TAR="${tars[0]}"
  case "$TAR" in
    *overlay*) die "unexpected overlay named as tar.gz: $TAR" ;;
  esac
  if [[ -f "${TAR}.sha256" ]]; then
    echo "Verify ${TAR}.sha256 ..."
    verify_sha256 "${TAR}.sha256"
  fi
  echo "docker load: $TAR"
  gunzip -c "$TAR" | docker load
  MAN="$(basename "$TAR" .tar.gz).manifest.json"
  if [[ ! -f "$MAN" ]]; then
    shopt -s nullglob
    mans=(moex-model-*.manifest.json)
    shopt -u nullglob
    if [[ ${#mans[@]} -gt 0 ]]; then
      MAN="${mans[0]}"
    else
      MAN=""
    fi
  fi
  if [[ -n "$MAN" && -f "$MAN" ]]; then
    TAG="$(json_field version "$MAN")"
  fi
  if [[ -z "$TAG" ]]; then
    TAG="$(basename "$TAR" .tar.gz)"
    TAG="${TAG#moex-model-}"
  fi
else
  die "contour drop has neither moex-model-*-overlay.zip nor moex-model-*.tar.gz"
fi

[[ -n "$TAG" ]] || die "could not determine MODEL_TAG"

echo "Mode=$MODE  MODEL_TAG=$TAG"

shopt -s nullglob
bundles=(release-bundle-*.zip)
shopt -u nullglob
[[ ${#bundles[@]} -gt 0 ]] || die "release-bundle-*.zip missing in contour drop"
BUNDLE="${bundles[0]}"

mkdir -p "$DEPLOY_DIR"
echo "Unpack config: $BUNDLE -> $DEPLOY_DIR"
unzip_ok -qo "$BUNDLE" -d "$DEPLOY_DIR"

if [[ ! -f "$DEPLOY_DIR/.env" ]]; then
  if [[ -f "$DEPLOY_DIR/.env.example" ]]; then
    cp "$DEPLOY_DIR/.env.example" "$DEPLOY_DIR/.env"
    echo "Created $DEPLOY_DIR/.env from .env.example — edit secrets before production use"
  else
    echo "WARNING: no .env and no .env.example in $DEPLOY_DIR"
  fi
fi

if [[ -f "$DEPLOY_DIR/.env" ]]; then
  if grep -q '^MODEL_TAG=' "$DEPLOY_DIR/.env" 2>/dev/null; then
    sed -i.bak "s/^MODEL_TAG=.*/MODEL_TAG=${TAG}/" "$DEPLOY_DIR/.env"
  else
    echo "MODEL_TAG=${TAG}" >> "$DEPLOY_DIR/.env"
  fi
fi

export MODEL_TAG="$TAG"
cd "$DEPLOY_DIR"

if [[ "$SKIP_COMPOSE" == "1" ]]; then
  echo "SKIP_COMPOSE=1 — images and config are ready. export MODEL_TAG=$TAG"
  exit 0
fi

echo "Compose up ..."
docker compose -f docker-compose.yml -f docker/docker-compose.prod.yml up -d

echo ""
echo "Done."
echo "  MODEL_TAG=$TAG"
echo "  curl -s http://127.0.0.1:8080/api/health"
