from __future__ import annotations

import argparse
import signal
import shutil
import subprocess
import sys
import time
from pathlib import Path

import uvicorn

from app.core.config import ROOT_DIR, get_settings


def _build_uvicorn_command(host: str, port: int, reload_enabled: bool) -> list[str]:
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    if reload_enabled:
        command.append("--reload")
    return command


def _build_vite_command(web_host: str, web_port: int) -> list[str]:
    npm_command = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm_command:
        raise FileNotFoundError(
            "Could not find npm in PATH. Install Node.js, or run the web dev server manually."
        )
    return [
        npm_command,
        "run",
        "dev",
        "--",
        "--host",
        web_host,
        "--port",
        str(web_port),
    ]


def _terminate_process(process: subprocess.Popen[bytes] | None) -> None:
    if process is None or process.poll() is not None:
        return

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def _run_dev_stack(host: str, port: int, reload_enabled: bool, web_host: str, web_port: int) -> int:
    server_process: subprocess.Popen[bytes] | None = None
    web_process: subprocess.Popen[bytes] | None = None
    web_dir = ROOT_DIR / "web"

    if not (web_dir / "package.json").is_file():
        print(f"Missing web package.json under {web_dir}", file=sys.stderr)
        return 1

    if not (web_dir / "node_modules").is_dir():
        print("Web dependencies are missing. Run `npm install` in the web directory first.", file=sys.stderr)
        return 1

    def shutdown(_signum: int, _frame: object) -> None:
        _terminate_process(web_process)
        _terminate_process(server_process)
        raise SystemExit(0)

    previous_sigint = signal.getsignal(signal.SIGINT)
    previous_sigterm = signal.getsignal(signal.SIGTERM)
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        server_process = subprocess.Popen(_build_uvicorn_command(host, port, reload_enabled), cwd=ROOT_DIR)
        web_process = subprocess.Popen(_build_vite_command(web_host, web_port), cwd=web_dir)

        print(f"Backend: http://{host}:{port}")
        print(f"Web dev server: http://{web_host}:{web_port}")
        print("Press Ctrl+C to stop both processes.")

        while True:
            server_code = server_process.poll()
            web_code = web_process.poll()

            if server_code is not None:
                print(f"Backend exited with code {server_code}. Stopping web dev server.", file=sys.stderr)
                _terminate_process(web_process)
                return server_code

            if web_code is not None:
                print(f"Web dev server exited with code {web_code}. Stopping backend.", file=sys.stderr)
                _terminate_process(server_process)
                return web_code

            time.sleep(0.5)
    except KeyboardInterrupt:
        _terminate_process(web_process)
        _terminate_process(server_process)
        return 0
    except Exception:
        _terminate_process(web_process)
        _terminate_process(server_process)
        raise
    finally:
        signal.signal(signal.SIGINT, previous_sigint)
        signal.signal(signal.SIGTERM, previous_sigterm)


def main() -> None:
    settings = get_settings()

    parser = argparse.ArgumentParser(description="Run the Life Reflex Arc backend server.")
    parser.add_argument("--host", default=settings.host)
    parser.add_argument("--port", type=int, default=settings.port)
    parser.add_argument("--reload", action="store_true", default=settings.reload)
    parser.add_argument(
        "--with-web",
        action="store_true",
        help="Start the FastAPI backend and the Vite web dev server together.",
    )
    parser.add_argument("--web-host", default=settings.web_dev_host)
    parser.add_argument("--web-port", type=int, default=settings.web_dev_port)
    args = parser.parse_args()

    if args.with_web and args.reload and sys.platform == "win32":
        print(
            "Warning: --with-web --reload is disabled on this Windows environment. "
            "Uvicorn reload uses multiprocessing pipes here and can raise PermissionError. "
            "Starting backend without reload instead.",
            file=sys.stderr,
        )
        args.reload = False

    if args.with_web:
        raise SystemExit(
            _run_dev_stack(
                host=args.host,
                port=args.port,
                reload_enabled=args.reload,
                web_host=args.web_host,
                web_port=args.web_port,
            )
        )

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
