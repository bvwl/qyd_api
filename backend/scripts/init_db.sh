#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${BACKEND_DIR}"

if [ -f ".env" ]; then
  set -a
  . ".env"
  set +a
fi

if [ ! -d "migrations" ]; then
  aerich init -t app.core.settings.TORTOISE_ORM
fi

aerich init-db

