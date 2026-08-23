import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "results" / "manifest.json"


def main() -> int:
    manifest = json.loads(
        MANIFEST.read_text(encoding="utf-8")
    )

    failures = 0

    print("LAB-003 SHOWCASE — CANONICAL RESULT VALIDATION")
    print()

    for item in manifest["canonical_results"]:
        path = ROOT / "results" / item["file"]

        if not path.exists():
            print(f"FAIL  {item['file']} — file missing")
            failures += 1
            continue

        data = json.loads(
            path.read_text(encoding="utf-8")
        )

        outcome = data["security_outcome"]

        expected_model = item["model_exploited"]
        expected_app = item["application_exploited"]

        actual_model = outcome["model_exploited"]
        actual_app = outcome["application_exploited"]

        passed = (
            expected_model == actual_model
            and expected_app == actual_app
        )

        status = "PASS" if passed else "FAIL"

        print(
            f"{status}  {item['file']}"
        )
        print(
            f"      Model exploited       : {actual_model}"
        )
        print(
            f"      Application exploited : {actual_app}"
        )
        print(
            f"      Outcome               : "
            f"{outcome['final_result']}"
        )
        print()

        if not passed:
            failures += 1

    if failures:
        print(
            f"FINAL: FAIL — {failures} canonical "
            f"result(s) did not match the manifest."
        )
        return 1

    print(
        "FINAL: PASS — all canonical results "
        "match the published manifest."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
