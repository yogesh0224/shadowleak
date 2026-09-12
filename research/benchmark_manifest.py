"""Generate a deterministic, versioned ShadowLeak benchmark manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from research.canaries import generate_canaries
from research.io import write_jsonl

MANIFEST_SCHEMA_VERSION = "shadowleak.benchmark-case.v1"
DEFENSE_CONDITIONS = ("none", "guardshield-v1")
DATA_DIRECTORY = Path(__file__).with_name("data")


def _stable_id(prefix: str, *parts: object) -> str:
    payload = "\x1f".join(str(part) for part in parts).encode("utf-8")
    return f"{prefix}_{hashlib.sha256(payload).hexdigest()[:16]}"


def _load_templates(filename: str) -> dict[str, Any]:
    with (DATA_DIRECTORY / filename).open(encoding="utf-8") as handle:
        document = json.load(handle)
    if not isinstance(document.get("templates"), list) or not document["templates"]:
        raise ValueError(f"{filename} contains no templates")
    identifiers: set[str] = set()
    for template in document["templates"]:
        required = {"template_id", "prompt"}
        if filename.startswith("attack_"):
            required |= {"attack_family", "target_field"}
        missing = required - template.keys()
        if missing:
            raise ValueError(f"Template in {filename} is missing: {sorted(missing)}")
        if template["template_id"] in identifiers:
            raise ValueError(f"Duplicate template_id in {filename}: {template['template_id']}")
        identifiers.add(template["template_id"])
    return document


def _context(record: dict[str, Any]) -> str:
    return "
".join(
        [
            f"Name: {record['name']}",
            f"Email: {record['email']}",
            f"Phone: {record['phone']}",
            f"City: {record['city']}",
            f"Organization: {record['organization']}",
            f"Date of birth: {record['dob']}",
        ]
    )


def build_manifest(
    record_count: int = 100,
    seed: int = 42,
    attack_template_version: str = "v1",
) -> list[dict[str, Any]]:
    """Return paired attack and benign cases for deterministic synthetic records."""
    if attack_template_version not in {"v1", "v2"}:
        raise ValueError("attack_template_version must be v1 or v2")
    attacks = _load_templates(f"attack_templates_{attack_template_version}.json")
    benign = _load_templates("benign_templates_v1.json")
    cases: list[dict[str, Any]] = []

    for index, canary in enumerate(generate_canaries(record_count, seed), start=1):
        raw_record = asdict(canary)
        raw_record["dob"] = canary.dob.isoformat()
        record_id = _stable_id(
            "record", seed, index, json.dumps(raw_record, sort_keys=True)
        )
        base = {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "benchmark_version": "2.0.0" if attack_template_version == "v2" else "1.0.0",
            "record_id": record_id,
            "split_group": record_id,
            "synthetic_data": True,
            "seed": seed,
            "context": _context(raw_record),
        }

        for template in attacks["templates"]:
            prompt = template["prompt"].format(subject_name=canary.name)
            pair_id = _stable_id(
                "pair",
                record_id,
                attacks["schema_version"],
                template["template_id"],
                prompt,
            )
            protected_value = str(raw_record[template["target_field"]])
            for defense in DEFENSE_CONDITIONS:
                cases.append(
                    {
                        **base,
                        "case_id": _stable_id("case", pair_id, defense),
                        "pair_id": pair_id,
                        "task_type": "attack",
                        "template_schema_version": attacks["schema_version"],
                        "template_id": template["template_id"],
                        "attack_family": template["attack_family"],
                        "target_field": template["target_field"],
                        "generalization_split": template.get("generalization_split", "not_applicable"),
                        "protected_value": protected_value,
                        "prompt": prompt,
                        "defense_condition": defense,
                    }
                )

        for template in benign["templates"]:
            pair_id = _stable_id(
                "pair",
                record_id,
                benign["schema_version"],
                template["template_id"],
                template["prompt"],
            )
            for defense in DEFENSE_CONDITIONS:
                cases.append(
                    {
                        **base,
                        "case_id": _stable_id("case", pair_id, defense),
                        "pair_id": pair_id,
                        "task_type": "benign",
                        "template_schema_version": benign["schema_version"],
                        "template_id": template["template_id"],
                        "attack_family": "not_applicable",
                        "target_field": "not_applicable",
                        "protected_value": "not_applicable",
                        "prompt": template["prompt"],
                        "defense_condition": defense,
                    }
                )
    return cases


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--attack-template-version", choices=("v1", "v2"), default="v1")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    cases = build_manifest(
        record_count=args.records,
        seed=args.seed,
        attack_template_version=args.attack_template_version,
    )
    write_jsonl(args.output, cases)
    print(f"Wrote {len(cases)} cases to {args.output}")


if __name__ == "__main__":
    main()
