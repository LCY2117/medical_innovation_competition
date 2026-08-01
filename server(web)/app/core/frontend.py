from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import Settings


def frontend_ready(settings: Settings) -> bool:
    return _index_file(settings).is_file()


def frontend_health(settings: Settings) -> dict:
    index_file = _index_file(settings)
    assets_dir = settings.web_dist_dir / "assets"
    asset_files = sorted(path for path in assets_dir.glob("*") if path.is_file()) if assets_dir.is_dir() else []
    return {
        "ok": index_file.is_file(),
        "webDistDir": str(settings.web_dist_dir),
        "indexHtml": str(index_file),
        "indexReady": index_file.is_file(),
        "indexMtime": int(index_file.stat().st_mtime) if index_file.is_file() else None,
        "assetsDir": str(assets_dir),
        "assetsReady": assets_dir.is_dir(),
        "assetCount": len(asset_files),
        "latestAssetMtime": int(max((path.stat().st_mtime for path in asset_files), default=0)) or None,
        "mobileChunkReady": any(path.name.startswith("MobileApp-") for path in asset_files),
        "desktopChunkReady": any(path.name.startswith("App-") for path in asset_files),
    }


def mount_frontend(app: FastAPI, settings: Settings) -> None:
    assets_dir = settings.web_dist_dir / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="web-assets")

    app.include_router(build_frontend_router(settings))


def build_frontend_router(settings: Settings) -> APIRouter:
    router = APIRouter()

    @router.get("/")
    async def frontend_root() -> FileResponse:
        return _serve_frontend(settings)

    @router.get("/{full_path:path}")
    async def frontend_fallback(full_path: str) -> FileResponse:
        if not full_path or full_path.startswith(("api", "ws", "docs", "openapi", "redoc")):
            raise HTTPException(status_code=404, detail="Not found")

        requested_file = settings.web_dist_dir / Path(full_path)
        if requested_file.is_file():
            return FileResponse(requested_file, headers=_frontend_file_headers(requested_file))

        return _serve_frontend(settings)

    return router


def _index_file(settings: Settings) -> Path:
    return settings.web_dist_dir / "index.html"


def _serve_frontend(settings: Settings) -> FileResponse:
    index_file = _index_file(settings)
    if not index_file.is_file():
        raise HTTPException(
            status_code=503,
            detail="Frontend build not found. Run `npm install` and `npm run build` inside `web/` first.",
        )
    return FileResponse(
        index_file,
        headers=_no_store_headers(),
    )


def _frontend_file_headers(path: Path) -> dict[str, str]:
    if path.name in {"index.html", "mobile-sw.js"}:
        return _no_store_headers()
    return {}


def _no_store_headers() -> dict[str, str]:
    return {
        "Cache-Control": "no-store, max-age=0",
        "Pragma": "no-cache",
    }
