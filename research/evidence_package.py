"""Build a deterministic manifest for ShadowLeak evidence artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from research.study_plan import load_study_plan

EVIDENCE_PACKAGE_SCHEMA = "shadowleak.evidence-package.v1"
REPORTING_PLAN_SCHEMA = "shadowleak.reporting-plan.v1"


def file_sha256(path: str | Path) -> str:
    source = Path(path)
    digest = hashlib.sha256()
    with source.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_entry(role: str, path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise ValueError(f"Evidence artifact does not exist or is not a file: {source}")
    return {
        "role": role,
        "path": source.as_posix(),
        "size_bytes": source.stat().st_size,
        "sha256": file_sha256(source),
    }


def build_evidence_package(
    study_plan_path: str | Path,
    reporting_plan_path: str | Path,
    artifacts: dict[str, str | Path] | None = None,
) -> dict[str, Any]:
    """Return a deterministic evidence-package manifest without reading outcomes."""
    study_plan, study_plan_sha256 = load_study_plan(study_plan_path)

    reporting_path = Path(reporting_plan_path)
    reporting_raw = reporting_path.read_bytes()
    reporting_plan = json.loads(reporting_raw)
    if reporting_plan.get("schema_version") != REPORTING_PLAN_SCHEMA:
        raise ValueError(f"Expected reporting schema {REPORTING_PLAN_SCHEMA}")
    if reporting_plan.get("study_id") != study_plan["study_id"]:
        raise ValueError("Study plan and reporting plan refer to different studies")
    if reporting_plan.get("status") != "frozen_before_confirmatory_outcome_inspection":
        raise ValueError("Reporting plan must be frozen before outcome inspection")

    reporting_sha256 = hashlib.sha256(reporting_raw).hexdigest()
    entries: list[dict[str, Any]] = [
        _artifact_entry("study_plan", study_plan_path),
        _artifact_entry("reporting_plan", reporting_plan_path),
    ]

    supplied = artifacts or {}
    if len(supplied) != len(set(supplied)):
        raise ValueError("Evidence artifact roles must be unique")
    for role in sorted(supplied):
        if role in {"study_plan", "reporting_plan"}:
            raise ValueError(f"Reserved evidence role: {role}")
        entries.append(_artifact_entry(role, supplied[role]))

    return {
        "schema_version": EVIDENCE_PACKAGE_SCHEMA,
        "study_id": study_plan["study_id"],
        "study_plan_sha256": study_plan_sha256,
        "reporting_plan_sha256": reporting_sha256,
        "artifact_count": len(entries),
        "artifacts": entries,
        "evidence_boundary": study_plan["evidence_boundary"],
        "interpretation_rule": (
            "This manifest records provenance and integrity only. "
            "Artifact presence or hash verification does not establish a substantive result."
        ),
    }


def _parse_artifacts(values: list[str]) -> dict[str, str]:
    artifacts: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError("--artifact must use ROLE=PATH syntax")
        role, path = value.split("=", 1)
        role = role.strip()
        path = path.strip()
        if not role or not path:
            raise ValueError("--artifact must use non-empty ROLE=PATH values")
        if role in artifacts:
            raise ValueError(f"Duplicate evidence artifact role: {role}")
        artifacts[role] = path
    return artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study-plan", required=True)
    parser.add_argument("--reporting-plan", required=True)
    parser.add_argument(
        "--artifact",
        action="append",
        default=[],
        help="Additional evidence artifact as ROLE=PATH; may be repeated.",
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    package = build_evidence_package(
        args.study_plan,
        args.reporting_plan,
        _parse_artifacts(args.artifact),
    )
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(package, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(
        f"Wrote evidence package manifest for {package['study_id']} "
        f"with {package['artifact_count']} artifacts to {destination}"
    )


if __name__ == "__main__":
    main()
