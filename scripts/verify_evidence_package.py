from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import zipfile
from io import StringIO
from pathlib import PurePosixPath


def _is_safe_zip_name(name: str) -> bool:
    path = PurePosixPath(name)
    return (
        bool(name)
        and not path.is_absolute()
        and "\\" not in name
        and all(part not in {"", ".", ".."} for part in path.parts)
    )


def _load_manifest(archive: zipfile.ZipFile) -> dict:
    try:
        raw = archive.read("manifest.json")
    except KeyError as exc:
        raise ValueError("manifest.json is missing") from exc
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("manifest.json is not valid UTF-8 JSON") from exc


def _read_text_file(archive: zipfile.ZipFile, name: str) -> str | None:
    try:
        raw = archive.read(name)
    except KeyError:
        return None
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None


def _collect_json_participant_ids(value: object, ids: set[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"userId", "patientUserId"} and isinstance(item, str):
                ids.add(item)
            elif key == "assignments" and isinstance(item, dict):
                ids.update(str(user_id) for user_id in item.values() if user_id)
            elif key == "dispatchRationale" and isinstance(item, dict):
                for decision in item.values():
                    if isinstance(decision, dict) and isinstance(decision.get("userId"), str):
                        ids.add(decision["userId"])
            _collect_json_participant_ids(item, ids)
    elif isinstance(value, list):
        for item in value:
            _collect_json_participant_ids(item, ids)


def _raw_participant_ids(archive: zipfile.ZipFile, name_set: set[str]) -> set[str]:
    ids: set[str] = set()
    if "experiment.json" in name_set:
        text = _read_text_file(archive, "experiment.json")
        if text:
            try:
                _collect_json_participant_ids(json.loads(text), ids)
            except json.JSONDecodeError:
                pass

    if "clients.csv" in name_set:
        text = _read_text_file(archive, "clients.csv")
        if text:
            for row in csv.DictReader(StringIO(text)):
                user_id = row.get("userId")
                if user_id:
                    ids.add(user_id)

    return {item for item in ids if len(item.strip()) >= 4}


def verify_package(zip_path: str, *, require_public_guidance: bool = True) -> list[str]:
    problems: list[str] = []
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        name_set = set(names)
        if len(name_set) != len(names):
            problems.append("ZIP contains duplicate file names")

        for name in names:
            if not _is_safe_zip_name(name):
                problems.append(f"Unsafe ZIP path: {name}")

        manifest = _load_manifest(archive)
        if manifest.get("schemaVersion") != 1:
            problems.append("Unsupported manifest schemaVersion")
        verification = manifest.get("verification") or {}
        if verification.get("algorithm") != "SHA-256":
            problems.append("manifest verification algorithm is not SHA-256")

        entries = manifest.get("files")
        if not isinstance(entries, list):
            problems.append("manifest.files must be a list")
            entries = []

        manifest_names: set[str] = set()
        for entry in entries:
            if not isinstance(entry, dict):
                problems.append("manifest.files contains a non-object entry")
                continue
            file_name = entry.get("fileName")
            expected_hash = entry.get("sha256")
            expected_bytes = entry.get("bytes")
            if not isinstance(file_name, str) or not file_name:
                problems.append("manifest.files entry has an invalid fileName")
                continue
            if file_name == "manifest.json":
                problems.append("manifest.files must not include manifest.json")
                continue
            if file_name in manifest_names:
                problems.append(f"manifest.files duplicates {file_name}")
            manifest_names.add(file_name)
            if file_name not in name_set:
                problems.append(f"manifest lists missing file: {file_name}")
                continue
            raw = archive.read(file_name)
            actual_hash = hashlib.sha256(raw).hexdigest()
            if actual_hash != expected_hash:
                problems.append(f"SHA-256 mismatch: {file_name}")
            if isinstance(expected_bytes, int) and len(raw) != expected_bytes:
                problems.append(f"byte count mismatch: {file_name}")

        actual_payload_names = name_set - {"manifest.json"}
        for name in sorted(actual_payload_names - manifest_names):
            problems.append(f"ZIP contains file not listed in manifest: {name}")
        for name in sorted(manifest_names - actual_payload_names):
            problems.append(f"manifest lists file not present in ZIP: {name}")

        declared_count = manifest.get("fileCountExcludingManifest")
        if isinstance(declared_count, int) and declared_count != len(actual_payload_names):
            problems.append("fileCountExcludingManifest does not match ZIP contents")

        if require_public_guidance:
            privacy = manifest.get("privacyGuidance") or {}
            public_files = privacy.get("publicOrExpertReview") or []
            internal_files = privacy.get("internalReviewOnly") or []
            if not isinstance(public_files, list) or not public_files:
                problems.append("privacyGuidance.publicOrExpertReview is missing or empty")
                public_files = []
            if not isinstance(internal_files, list):
                problems.append("privacyGuidance.internalReviewOnly must be a list")
                internal_files = []
            for name in public_files + internal_files:
                if name not in name_set:
                    problems.append(f"privacy guidance references missing file: {name}")
            overlap = set(public_files) & set(internal_files)
            if overlap:
                problems.append(f"privacy guidance marks files as both public and internal: {', '.join(sorted(overlap))}")

            raw_ids = _raw_participant_ids(archive, name_set)
            for name in public_files:
                if name not in name_set:
                    continue
                text = _read_text_file(archive, name)
                if text is None:
                    continue
                for raw_id in sorted(raw_ids):
                    if raw_id in text:
                        problems.append(f"public file leaks raw participant id: {name}")
                        break

    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify a LifeReflexArc evidence-package ZIP against manifest.json SHA-256 hashes.",
    )
    parser.add_argument("zip_path", help="Path to the downloaded evidence-package ZIP")
    parser.add_argument(
        "--no-public-guidance",
        action="store_true",
        help="Skip privacyGuidance public/internal file-boundary checks.",
    )
    args = parser.parse_args(argv)

    try:
        problems = verify_package(args.zip_path, require_public_guidance=not args.no_public_guidance)
    except (OSError, zipfile.BadZipFile, ValueError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1

    if problems:
        print("FAILED: evidence package verification found problems:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1

    print("OK: evidence package manifest, SHA-256 hashes, file list, privacy guidance, and public-file anonymization are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
