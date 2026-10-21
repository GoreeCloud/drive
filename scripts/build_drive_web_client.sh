#!/usr/bin/env bash
# Build the pinned, source-included OpenCloud-derived web client and stage its
# real Files UI modules into the existing Go web service's embedded asset tree.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
frontend="$root/web-client"
dist="$frontend/dist"
assets="$root/services/web/assets/core"

if [[ ! -s "$frontend/LICENSE" || ! -s "$frontend/pnpm-lock.yaml" ]]; then
  echo "Missing AGPL-3.0 frontend source, license or pinned lockfile" >&2
  exit 2
fi
if ! command -v pnpm >/dev/null 2>&1; then
  echo "pnpm is required; use the packageManager version declared by web-client/package.json" >&2
  exit 2
fi

(
  cd "$frontend"
  pnpm install --frozen-lockfile
  TITLE="GoreeCloud Drive" pnpm build
)
for file in index.html oidc-callback.html manifest.json; do
  if [[ ! -s "$dist/$file" ]]; then
    echo "Missing required built frontend file: $file" >&2
    exit 3
  fi
done
if ! grep -q 'web-app-files' "$dist/index.html"; then
  echo "Built app entrypoint does not register Files" >&2
  exit 3
fi
# Prevent a bad path or missing build from deleting another directory.
if [[ "$assets" != "$root/services/web/assets/core" || ! -d "$assets" ]]; then
  echo "Unexpected embedded asset target" >&2
  exit 3
fi

# This directory is exclusively the generated web core distribution.
# Retain the tracked .keep marker and prune stale versioned bundles so old
# dependencies do not remain embedded in the Go executable.
find "$assets" -mindepth 1 -maxdepth 1 ! -name .keep -exec rm -rf -- {} +
cp -a "$dist"/. "$assets"/
printf '%s\n' "Staged GoreeCloud Drive frontend from pinned AGPL source into Go embedded core"
