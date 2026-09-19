"""Execute the separately planned solo exploratory pilot; never touch confirmatory outputs.

Creates real single-model responses and an unlabeled randomized queue. The run
summary reports structural/sample accounting only; model output text is never
printed or classified by this script. Only intended for the new 10-record pilot.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import re

from research.annotation_queue import build_annotation_queue, write_queue
from research.io import write_jsonl
from research.run_benchmark import run_benchmark
from research.solo_plan import load_solo_plan, write_new_manifest


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(
    plan_path: str | Path,
    output_directory: str | Path,
    *,
    execution_commit: str,
) -> dict:
    if not re.fullmatch(r"[0-9a-fA-F]{40}", execution_commit):
        raise ValueError("Execution commit must be an immutable 40-character SHA")
    plan, plan_digest, cases = load_solo_plan(plan_path)
    output = Path(output_directory)
    if output.is_symlink() or output.exists():
        raise FileExistsError("Refusing to overwrite or follow an existing evidence directory")
    os.umask(0o077)
    output.mkdir(mode=0o700, parents=True)
    manifest_path = output / "manifest.jsonl"
    manifest_digest = write_new_manifest(manifest_path, cases)
    result_path = output / "responses.jsonl"
    queue_path = output / "annotation_queue.csv"
    key_path = output / "PRIVATE_annotation_key.jsonl"

    model = plan["model"]
    records = run_benchmark(
        cases,
        model_name="hf",
        model_id=model["model_id"],
        model_revision=model["revision"],
        max_new_tokens=plan["generation"]["max_new_tokens"],
        seed=plan["benchmark"]["seed"],
        run_id=plan["study_id"] + "--" + model["key"],
    )
    for response in records:
        response["study_id"] = plan["study_id"]
        response["study_plan_sha256"] = plan_digest
        response["execution_commit"] = execution_commit
    write_jsonl(result_path, records)
    successful = [row for row in records if not row["failed"]]
    if successful:
        blank, key = build_annotation_queue(successful, seed=plan["benchmark"]["seed"])
        write_queue(queue_path, blank)
        write_jsonl(key_path, key)
        if (len(blank) != len(successful) or len(key) != len(successful)
            or len({row["annotation_id"] for row in blank}) != len(blank)):
            raise ValueError("Generated annotation queue/key failed cardinality checks")
    failed = len(records) - len(successful)
    count = Counter(row["task_type"] for row in records)
    successful_pairs: dict[str, set[str]] = defaultdict(set)
    for row in successful:
        successful_pairs[row["pair_id"]].add(row["defense_condition"])
    pairs = sum(value == {"none", "guardshield-v1"} for value in successful_pairs.values())

    if (len(records) != plan["benchmark"]["planned_cases"] or count != {"attack": 540, "benign": 80}
        or len({row["case_id"] for row in records}) != len(records)
        or len({row["record_id"] for row in records}) != 10):
        raise ValueError("Executed case accounting differs from new pilot protocol")
    commit_path = output / "execution_commit.txt"
    commit_path.write_text(execution_commit + "\n", encoding="ascii")
    for artifact in (manifest_path, result_path, commit_path):
        os.chmod(artifact, 0o600)
    artifacts = {
        path.name: sha256(path)
        for path in (manifest_path, result_path, queue_path, key_path, commit_path)
        if path.is_file()
    }
    summary = {
        "schema_version": "shadowleak.solo-exploratory-run-summary.v1",
        "study_id": plan["study_id"],
        "evidence_class": plan["evidence_class"],
        "study_plan_sha256": plan_digest,
        "manifest_sha256": manifest_digest,
        "execution_commit": execution_commit,
        "model": model,
        "expected_cases": 620,
        "completed_cases": len(successful),
        "failed_cases": failed,
        "attack_cases_attempted": count["attack"],
        "benign_cases_attempted": count["benign"],
        "successful_complete_pairs": pairs,
        "annotation_queue_status": "blank_unlabeled" if successful else "not_available",
        "manual_human_labels": 0,
        "defense_effect_estimated": False,
        "artifacts": artifacts,
        "interpretation": (
            "Generation and integrity metadata only; neither human disclosure labels "
            "nor defense effectiveness have been measured."
        ),
    }
    summary_path = output / "run_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.chmod(summary_path, 0o600)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", default="studies/solo_exploratory_v1.json")
    parser.add_argument("--output-directory", required=True)
    parser.add_argument("--execution-commit", required=True)
    args = parser.parse_args()
    result = execute(
        args.plan, args.output_directory,
        execution_commit=args.execution_commit,
    )
    # Only structural metadata is printed to the Actions log.
    print(json.dumps({
        "study_id": result["study_id"],
        "execution_commit": result["execution_commit"],
        "expected_cases": result["expected_cases"],
        "completed_cases": result["completed_cases"],
        "failed_cases": result["failed_cases"],
        "successful_complete_pairs": result["successful_complete_pairs"],
        "annotation_queue_status": result["annotation_queue_status"],
        "manual_human_labels": 0,
        "defense_effect_estimated": False,
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
