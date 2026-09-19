"""Validate the separate solo-exploratory plan and create its NEW metadata-only manifest.

Never opens confirmatory response archives or executes a model. The original
registered study-plan validator intentionally remains unchanged.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path

from research.benchmark_manifest import build_manifest
from research.run_benchmark import validate_manifest

SCHEMA = "shadowleak.solo-exploratory-plan.v1"
STUDY_ID = "shadowleak-solo-exploratory-v1"
FROZEN_ID = "shadowleak-confirmatory-v1"
PRIMARY_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
PRIMARY_REVISION = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"


def _identities(cases: list[dict]) -> set[tuple[str, str]]:
    found: set[tuple[str, str]] = set()
    for row in cases:
        lines = dict(line.split(": ", 1) for line in row["context"].splitlines() if ": " in line)
        found.add((lines.get("Name", ""), lines.get("Email", "")))
    return found


def validate_solo_plan(plan: dict) -> list[dict]:
    if (plan.get("schema_version") != SCHEMA or plan.get("study_id") != STUDY_ID
        or plan.get("original_study_id") != FROZEN_ID
        or plan.get("original_study_outputs_allowed") is not False
        or plan.get("evidence_class") != "exploratory_single_investigator_not_original_confirmatory"
        or plan.get("status") != "prospectively_documented_before_new_model_execution"):
        raise ValueError("Solo plan must be prospectively documented and distinct from the original study")
    b = plan.get("benchmark", {})
    if (b.get("benchmark_version") != "2.0.0" or b.get("attack_template_version") != "v2"
        or b.get("benign_template_version") != "v1" or b.get("seed") != 20260919
        or b.get("record_count") != 10
        or b.get("attack_templates_per_record") != 27
        or b.get("benign_templates_per_record") != 4
        or b.get("defense_conditions") != ["none", "guardshield-v1"]
        or b.get("planned_cases") != 620 or b.get("planned_attack_cases") != 540
        or b.get("planned_benign_cases") != 80 or b.get("planned_pairs") != 310):
        raise ValueError("Solo pilot's sample, seeds, versions and planned outcomes are fixed")
    model = plan.get("model", {})
    if (model.get("model_id") != PRIMARY_MODEL or model.get("revision") != PRIMARY_REVISION
        or model.get("key") != "qwen2_5_1_5b_instruct"
        or model.get("role") != "single_pilot_model"):
        raise ValueError("Solo pilot must use the one specified pinned model")
    gen = plan.get("generation", {})
    if (gen.get("do_sample") is not False or gen.get("max_new_tokens") != 64
        or gen.get("selective_reruns") is not False):
        raise ValueError("Solo pilot generation must use frozen deterministic settings")
    labels = plan.get("annotation", {})
    if (labels.get("human_annotators") != 1 or labels.get("independent_double_annotation") is not False
        or labels.get("adjudicated_human_gold") is not False
        or labels.get("detector_predictions_hidden_until_label_freeze") is not True
        or labels.get("condition_mapping_hidden_until_label_freeze") is not True):
        raise ValueError("Solo study must not claim independently adjudicated labels")
    if (plan.get("analysis", {}).get("evidence_class") != "exploratory_descriptive"
        or plan["analysis"].get("registered_primary_significance_test") is not False):
        raise ValueError("Solo study must not claim a confirmatory primary test")
    cases = build_manifest(record_count=10, seed=20260919, attack_template_version="v2")
    validate_manifest(cases)
    kinds = Counter(row["task_type"] for row in cases)
    pairs: dict[str, set[str]] = defaultdict(set)
    for case in cases:
        pairs[case["pair_id"]].add(case["defense_condition"])
    if (len(cases) != 620 or kinds != {"attack": 540, "benign": 80}
        or len(pairs) != 310 or any(conditions != {"none", "guardshield-v1"}
                                   for conditions in pairs.values())
        or len({row["record_id"] for row in cases}) != 10):
        raise ValueError("Generated manifest is inconsistent with solo protocol")
    original = build_manifest(record_count=30, seed=42, attack_template_version="v2")
    if set(row["record_id"] for row in cases) & set(row["record_id"] for row in original):
        raise ValueError("New record IDs unexpectedly overlap with the original study")
    if _identities(cases) & _identities(original):
        raise ValueError("New synthetic name/email identities unexpectedly overlap with original study")
    return cases


def load_solo_plan(path: str | Path) -> tuple[dict, str, list[dict]]:
    raw = Path(path).read_bytes()
    plan = json.loads(raw)
    cases = validate_solo_plan(plan)
    return plan, hashlib.sha256(raw).hexdigest(), cases


def write_new_manifest(output: str | Path, cases: list[dict]) -> str:
    target = Path(output)
    if target.is_symlink():
        raise ValueError("Refusing to write into a symlink")
    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    content = "".join(json.dumps(row, sort_keys=True) + "\n" for row in cases).encode("utf-8")
    fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(content)
    return hashlib.sha256(content).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", default="studies/solo_exploratory_v1.json")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--manifest-output", type=Path)
    args = parser.parse_args()
    if args.validate_only == bool(args.manifest_output):
        parser.error("Specify exactly one of --validate-only or --manifest-output PATH")
    plan, digest, cases = load_solo_plan(args.plan)
    report = {"study_id": plan["study_id"], "evidence_class": plan["evidence_class"],
              "plan_sha256": digest, "cases": len(cases), "records": 10,
              "attack_cases": 540, "benign_cases": 80,
              "planned_complete_pairs": 310,
              "model_execution": "not_performed_by_this_command",
              "human_labels": "not_performed_by_this_command"}
    if args.manifest_output:
        os.umask(0o077)
        report["manifest_sha256"] = write_new_manifest(args.manifest_output, cases)
        report["manifest_output"] = str(args.manifest_output)
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
