#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
WEB_DIR="$ROOT_DIR/web"
LOG_DIR="$ROOT_DIR/logs"
RUN_DIR="$ROOT_DIR/run"
PID_FILE="$RUN_DIR/server.pid"

ensure_command() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 1
  fi
}

stop_existing() {
  if [[ -f "$PID_FILE" ]]; then
    local old_pid
    old_pid="$(cat "$PID_FILE")"
    if [[ -n "$old_pid" ]] && kill -0 "$old_pid" >/dev/null 2>&1; then
      echo "Stopping existing backend process: $old_pid"
      kill "$old_pid"
      sleep 1
    fi
    rm -f "$PID_FILE"
  fi
}

main() {
  ensure_command python3
  ensure_command npm

  mkdir -p "$LOG_DIR" "$RUN_DIR"

  if [[ ! -d "$VENV_DIR" ]]; then
    python3 -m venv "$VENV_DIR"
  fi

  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate"

  python -m pip install --upgrade pip
  python -m pip install "fastapi>=0.115,<1.0" "uvicorn[standard]>=0.30,<1.0"

  if [[ ! -f "$ROOT_DIR/.env" ]]; then
    cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
    echo "Created .env from .env.example. Please edit it if needed."
  fi

  pushd "$WEB_DIR" >/dev/null
  npm install
  npm run build
  popd >/dev/null

  stop_existing

  local host port
  host="${LRA_HOST:-0.0.0.0}"
  port="${LRA_PORT:-8080}"

  nohup "$VENV_DIR/bin/python" -m app.cli --host "$host" --port "$port" >"$LOG_DIR/server.log" 2>&1 &
  echo $! >"$PID_FILE"

  echo "Deployment finished."
  echo "Backend PID: $(cat "$PID_FILE")"
  echo "Health URL: http://127.0.0.1:${port}/api/health/detail"
  echo "Log file: $LOG_DIR/server.log"
}

main "$@"
