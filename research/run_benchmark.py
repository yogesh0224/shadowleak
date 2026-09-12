"""Execute a ShadowLeak benchmark manifest and record model provenance."""

from __future__ import annotations

import argparse
import hashlib
import re
import time
from typing import Any

from guardshield.output_sanitizer import sanitize_output
from guardshield.prompt_filter import is_prompt_risky, sanitize_prompt
from model_interface.mock_model import MockModelInterface
from research.io import read_jsonl, write_jsonl

REQUIRED_CASE_FIELDS = {
    "case_id",
    "pair_id",
    "record_id",
    "prompt",
    "context",
    "defense_condition",
    "task_type",
}


def _digest_rows(rows: list[dict[str, Any]]) -> str:
    import json

    payload = "\n".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _case_seed(seed: int, pair_id: str) -> int:
    digest = hashlib.sha256(f"{seed}:{pair_id}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def validate_manifest(cases: list[dict[str, Any]]) -> None:
    case_ids: set[str] = set()
    pairs: dict[str, list[str]] = {}
    for row_number, case in enumerate(cases, start=1):
        missing = REQUIRED_CASE_FIELDS - case.keys()
        if missing:
            raise ValueError(f"Manifest row {row_number} is missing: {sorted(missing)}")
        case_id = str(case["case_id"])
        if case_id in case_ids:
            raise ValueError(f"Duplicate case_id: {case_id}")
        case_ids.add(case_id)
        pairs.setdefault(str(case["pair_id"]), []).append(
            str(case["defense_condition"])
        )
    invalid = [
        pair
        for pair, conditions in pairs.items()
        if sorted(conditions) != ["guardshield-v1", "none"]
    ]
    if invalid:
        raise ValueError(f"Pairs must contain both defense conditions: {invalid[:3]}")


def execute_case(
    case: dict[str, Any], model_name: str, seed: int, shared_model: Any = None
) -> dict[str, Any]:
    model = (
        MockModelInterface(seed=_case_seed(seed, str(case["pair_id"])))
        if model_name == "mock"
        else shared_model
    )
    if model is None:
        raise ValueError(f"No model adapter configured for {model_name}")
    prompt = str(case["prompt"])
    context = str(case["context"])
    defense = str(case["defense_condition"])
    input_blocked = False
    output_sanitized = False
    failed = False
    error_type = None
    started = time.perf_counter()
    try:
        if defense == "guardshield-v1" and is_prompt_risky(prompt):
            response = sanitize_prompt(prompt)
            input_blocked = True
        else:
            raw_response = model.generate(prompt, context)
            if defense == "guardshield-v1":
                response = sanitize_output(raw_response)
                output_sanitized = response != raw_response
            else:
                response = raw_response
    except Exception as exc:  # pragma: no cover - defensive boundary for real adapters
        response = ""
        failed = True
        error_type = type(exc).__name__
    latency_ms = round((time.perf_counter() - started) * 1000, 3)

    metadata_keys = (
        "schema_version",
        "benchmark_version",
        "case_id",
        "pair_id",
        "record_id",
        "split_group",
        "task_type",
        "template_schema_version",
        "template_id",
        "attack_family",
        "target_field",
        "protected_value",
        "prompt",
        "context",
        "defense_condition",
        "synthetic_data",
    )
    return {
        **{key: case[key] for key in metadata_keys},
        "response_schema_version": "shadowleak.benchmark-response.v1",
        "response": response,
        "input_blocked": input_blocked,
        "output_sanitized": output_sanitized,
        "failed": failed,
        "error_type": error_type,
        "latency_ms": latency_ms,
    }


def run_benchmark(
    cases: list[dict[str, Any]],
    model_name: str = "mock",
    model_revision: str = "shadowleak-mock-v1",
    model_id: str | None = None,
    seed: int = 42,
    run_id: str | None = None,
) -> list[dict[str, Any]]:
    validate_manifest(cases)
    if model_name not in {"mock", "hf"}:
        raise ValueError(f"Unsupported model: {model_name}")
    shared_model = None
    resolved_model_id = "shadowleak/mock" if model_name == "mock" else model_id
    if model_name == "hf":
        if not model_id:
            raise ValueError("model_id is required for Hugging Face runs")
        if not re.fullmatch(r"[0-9a-fA-F]{40}", model_revision):
            raise ValueError(
                "Hugging Face model_revision must be an exact 40-character commit SHA"
            )
        from model_interface.hf_model import HuggingFaceModelInterface

        shared_model = HuggingFaceModelInterface(model_id, model_revision)
    manifest_sha256 = _digest_rows(cases)
    model_token = str(resolved_model_id).replace("/", "-")
    resolved_run_id = run_id or f"run_{manifest_sha256[:12]}_{model_token}_{seed}"
    evidence_class = "plumbing_only" if model_name == "mock" else "empirical"
    return [
        {
            **execute_case(
                case,
                model_name=model_name,
                seed=seed,
                shared_model=shared_model,
            ),
            "run_id": resolved_run_id,
            "manifest_sha256": manifest_sha256,
            "model_adapter": model_name,
            "model_name": resolved_model_id,
            "model_revision": model_revision,
            "run_seed": seed,
            "evidence_class": evidence_class,
        }
        for case in cases
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", choices=("mock", "hf"), default="mock")
    parser.add_argument("--model-id", help="Hugging Face repository ID")
    parser.add_argument("--model-revision", default="shadowleak-mock-v1")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--run-id")
    args = parser.parse_args()
    cases = read_jsonl(args.manifest)
    responses = run_benchmark(
        cases,
        model_name=args.model,
        model_id=args.model_id,
        model_revision=args.model_revision,
        seed=args.seed,
        run_id=args.run_id,
    )
    write_jsonl(args.output, responses)
    print(f"Wrote {len(responses)} responses to {args.output}")
    if args.model == "mock":
        print("NOTICE: mock outputs test plumbing only and are not empirical findings.")


if __name__ == "__main__":
    main()
