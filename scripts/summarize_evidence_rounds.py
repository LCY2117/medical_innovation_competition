from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
import sys
import zipfile
from io import StringIO
from pathlib import Path

from verify_evidence_package import verify_package


BASE_FIELDS = [
    "packagePath",
    "packageSha256",
    "verificationStatus",
    "verificationProblems",
    "manifestIncidentId",
    "manifestGeneratedAtIso",
    "manifestPhase",
]


def _candidate_zip_paths(inputs: list[str], *, recursive: bool) -> list[Path]:
    paths: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if path.is_dir():
            pattern = "**/*.zip" if recursive else "*.zip"
            paths.extend(sorted(path.glob(pattern)))
        else:
            matched = [Path(match) for match in sorted(glob.glob(raw, recursive=recursive))] if any(char in raw for char in "*?[") else [path]
            paths.extend(matched)
    unique: dict[Path, None] = {}
    for path in paths:
        unique[path.resolve()] = None
    return list(unique.keys())


def _read_manifest(archive: zipfile.ZipFile) -> dict:
    return json.loads(archive.read("manifest.json").decode("utf-8"))


def _read_round_summary(archive: zipfile.ZipFile) -> list[dict[str, str]]:
    raw = archive.read("pre_experiment_round_summary.csv").decode("utf-8-sig")
    return [dict(row) for row in csv.DictReader(StringIO(raw))]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def summarize_packages(paths: list[Path], *, include_invalid: bool = False) -> tuple[list[str], list[dict[str, str]]]:
    rows: list[dict[str, str]] = []
    round_fields: list[str] = []
    for path in paths:
        package_hash = _sha256(path) if path.is_file() else ""
        problems: list[str]
        try:
            problems = verify_package(str(path))
        except (OSError, zipfile.BadZipFile, ValueError) as exc:
            problems = [str(exc)]

        status = "OK" if not problems else "FAILED"
        if problems and not include_invalid:
            raise ValueError(f"{path}: " + "; ".join(problems))

        manifest: dict = {}
        summary_rows: list[dict[str, str]] = [{}]
        if not problems:
            with zipfile.ZipFile(path) as archive:
                manifest = _read_manifest(archive)
                summary_rows = _read_round_summary(archive)

        for summary in summary_rows:
            for field in summary:
                if field not in round_fields:
                    round_fields.append(field)
            row = {
                "packagePath": str(path),
                "packageSha256": package_hash,
                "verificationStatus": status,
                "verificationProblems": " | ".join(problems),
                "manifestIncidentId": str(manifest.get("incidentId", "")),
                "manifestGeneratedAtIso": str(manifest.get("generatedAtIso", "")),
                "manifestPhase": str(manifest.get("phase", "")),
            }
            row.update({key: str(value) for key, value in summary.items()})
            rows.append(row)

    return BASE_FIELDS + [field for field in round_fields if field not in BASE_FIELDS], rows


def write_csv(fieldnames: list[str], rows: list[dict[str, str]], output: Path | None) -> None:
    target = output.open("w", encoding="utf-8-sig", newline="") if output else sys.stdout
    close_target = output is not None
    try:
        writer = csv.DictWriter(target, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if close_target:
            target.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify LifeReflexArc evidence-package ZIPs and merge their "
            "pre_experiment_round_summary.csv rows into one CSV."
        ),
    )
    parser.add_argument("paths", nargs="+", help="Evidence ZIP file, directory, or glob pattern")
    parser.add_argument("-o", "--output", help="Output CSV path. Defaults to stdout.")
    parser.add_argument("--recursive", action="store_true", help="When a directory is passed, scan ZIPs recursively.")
    parser.add_argument(
        "--include-invalid",
        action="store_true",
        help="Include invalid packages as FAILED rows instead of aborting.",
    )
    args = parser.parse_args(argv)

    paths = _candidate_zip_paths(args.paths, recursive=args.recursive)
    if not paths:
        print("FAILED: no ZIP packages matched the given input paths.", file=sys.stderr)
        return 1

    try:
        fieldnames, rows = summarize_packages(paths, include_invalid=args.include_invalid)
    except ValueError as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1

    output = Path(args.output) if args.output else None
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
    write_csv(fieldnames, rows, output)
    if output:
        print(f"OK: summarized {len(rows)} evidence round(s) from {len(paths)} package(s) -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
