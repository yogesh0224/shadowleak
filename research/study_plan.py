"""Validate and execute a frozen ShadowLeak study plan."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from research.annotation_queue import build_annotation_queue, write_queue
from research.benchmark_manifest import build_manifest
from research.io import write_jsonl
from research.run_benchmark import run_benchmark

STUDY_PLAN_SCHEMA = "shadowleak.study-plan.v1"


def load_study_plan(path: str | Path) -> tuple[dict[str, Any], str]:
    source = Path(path)
    raw = source.read_bytes()
    plan = json.loads(raw)
    validate_study_plan(plan)
    return plan, hashlib.sha256(raw).hexdigest()


def validate_study_plan(plan: dict[str, Any]) -> None:
    if plan.get("schema_version") != STUDY_PLAN_SCHEMA:
        raise ValueError(f"Expected schema_version {STUDY_PLAN_SCHEMA}")
    if plan.get("status") != "frozen_before_model_execution":
        raise ValueError("Study plan must be frozen before model execution")
    benchmark = plan.get("benchmark", {})
    if not isinstance(benchmark.get("record_count"), int) or benchmark["record_count"] < 1:
        raise ValueError("benchmark.record_count must be a positive integer")
    expected = benchmark["record_count"] * 32
    if benchmark.get("expected_cases_per_model") != expected:
        raise ValueError(f"expected_cases_per_model must equal {expected}")
    generation = plan.get("generation", {})
    if generation.get("do_sample") is not False:
        raise ValueError("Study plan v1 requires deterministic decoding")
    if not isinstance(generation.get("max_new_tokens"), int) or generation["max_new_tokens"] < 1:
        raise ValueError("generation.max_new_tokens must be positive")
    failure_policy = plan.get("failure_policy", {})
    maximum_failure_rate = failure_policy.get("maximum_failure_rate")
    if not isinstance(maximum_failure_rate, (int, float)) or not 0 <= maximum_failure_rate <= 1:
        raise ValueError("maximum_failure_rate must be between zero and one")

    models = plan.get("models")
    if not isinstance(models, list) or len(models) < 2:
        raise ValueError("At least two models are required")
    keys: set[str] = set()
    model_ids: set[str] = set()
    for model in models:
        required = {"key", "model_id", "revision", "license", "model_card"}
        missing = required - model.keys()
        if missing:
            raise ValueError(f"Study model is missing: {sorted(missing)}")
        if model["key"] in keys or model["model_id"] in model_ids:
            raise ValueError("Model keys and IDs must be unique")
        keys.add(model["key"])
        model_ids.add(model["model_id"])
        if not re.fullmatch(r"[0-9a-fA-F]{40}", model["revision"]):
            raise ValueError(f"Model {model['key']} is not pinned to a commit SHA")
        if not str(model["model_card"]).startswith("https://huggingface.co/"):
            raise ValueError(f"Model {model['key']} has an invalid model-card URL")


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def execute_study_model(
    plan: dict[str, Any], plan_sha256: str, model_key: str, output_directory: str | Path
) -> dict[str, Any]:
    try:
        model = next(item for item in plan["models"] if item["key"] == model_key)
    except StopIteration as exc:
        raise ValueError(f"Unknown model key: {model_key}") from exc

    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = output / "manifest.jsonl"
    responses_path = output / "responses.jsonl"
    queue_path = output / "annotation_queue.csv"
    key_path = output / "annotation_key.jsonl"
    summary_path = output / "run_summary.json"
    benchmark = plan["benchmark"]
    cases = build_manifest(
        record_count=benchmark["record_count"],
        seed=benchmark["seed"],
    )
    write_jsonl(manifest_path, cases)
    run_id = f"{plan['study_id']}--{model_key}"
    responses = run_benchmark(
        cases,
        model_name="hf",
        model_id=model["model_id"],
        model_revision=model["revision"],
        max_new_tokens=plan["generation"]["max_new_tokens"],
        seed=benchmark["seed"],
        run_id=run_id,
    )
    for response in responses:
        response["study_id"] = plan["study_id"]
        response["study_plan_sha256"] = plan_sha256
    write_jsonl(responses_path, responses)

    successful = [response for response in responses if not response["failed"]]
    if successful:
        queue, key = build_annotation_queue(successful, seed=benchmark["seed"])
        write_queue(queue_path, queue)
        write_jsonl(key_path, key)
    failures = len(responses) - len(successful)
    failure_rate = failures / len(responses)
    summary = {
        "summary_schema_version": "shadowleak.study-run-summary.v1",
        "study_id": plan["study_id"],
        "study_plan_sha256": plan_sha256,
        "run_id": run_id,
        "model": model,
        "planned_cases": benchmark["expected_cases_per_model"],
        "completed_cases": len(successful),
        "failed_cases": failures,
        "failure_rate": failure_rate,
        "artifacts": {
            "manifest.jsonl": _file_sha256(manifest_path),
            "responses.jsonl": _file_sha256(responses_path),
        },
        "evidence_boundary": plan["evidence_boundary"],
    }
    if successful:
        summary["artifacts"]["annotation_queue.csv"] = _file_sha256(queue_path)
        summary["artifacts"]["annotation_key.jsonl"] = _file_sha256(key_path)
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    maximum = plan["failure_policy"]["maximum_failure_rate"]
    if failure_rate > maximum:
        raise RuntimeError(
            f"Failure rate {failure_rate:.3f} exceeds preregistered maximum {maximum:.3f}"
        )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--model-key")
    parser.add_argument("--output-directory")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    plan, plan_sha256 = load_study_plan(args.plan)
    if args.validate_only:
        print(f"Valid study plan: {plan['study_id']} ({plan_sha256})")
        return
    if not args.model_key or not args.output_directory:
        parser.error("--model-key and --output-directory are required for execution")
    summary = execute_study_model(
        plan, plan_sha256, args.model_key, args.output_directory
    )
    print(
        f"Completed {summary['completed_cases']}/{summary['planned_cases']} cases "
        f"for {summary['model']['model_id']}"
    )


if __name__ == "__main__":
    main()
