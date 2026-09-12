"""Evaluate a ShadowLeak benchmark report against governance decision profiles."""

import argparse
import json
from pathlib import Path

from research.governance import evaluate_profiles, load_profiles


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True)
    parser.add_argument("--profiles", required=True)
    parser.add_argument("--condition", default="guardshield-v1")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    result = evaluate_profiles(
        report, load_profiles(args.profiles), condition=args.condition
    )
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Wrote governance decision report to {destination}")


if __name__ == "__main__":
    main()
