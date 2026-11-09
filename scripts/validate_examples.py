#!/usr/bin/env python3
"""
Reasoning Resource Governance (RRG) v0.1 Validator.

Validation layers:
1. JSON Schema structural validation
2. Semantic consistency validation
3. Expected example outcome validation

This validator checks internal record consistency.
It does not verify external authorization, actual
runtime enforcement, or independent outcome evidence.
"""

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, SchemaError


ROOT = Path(__file__).resolve().parents[1]

SCHEMA_PATH = ROOT / "schemas" / "rrg-v0.1.schema.json"
EXAMPLES_DIR = ROOT / "examples"

EXPECTED_RESULTS = {
    "valid-allocation.json": "approved",
    "denied-allocation.json": "denied",
}

VALID_TERMINATION_REASONS = {
    "budget_exceeded",
    "authorization_violation",
    "authorization_revoked",
}


def load_json(path):
    """Load a JSON file."""
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_semantics(record):
    """
    Check RRG v0.1 semantic consistency.

    Assumes JSON Schema validation has already passed.
    Returns a list of error messages.
    """
    errors = []

    authorization = record["authorization"]
    budget = record["budget"]
    allocation = record["allocation"]
    execution = record["execution"]
    evaluation = record["evaluation"]
    termination = record["termination"]

    auth_status = authorization["status"]
    auth_scope = authorization["scope"]

    requested = budget["requested"]
    available = budget["available"]
    limit = budget["limit"]

    decision = allocation["decision"]
    status = execution["status"]
    consumed = execution["consumed"]

    closed = termination["closed"]
    reason = termination["reason"]

    # -----------------------------------------
    # 1. Allocation validation
    # -----------------------------------------

    within_budget = (
        requested <= available
        and requested <= limit
    )

    if decision == "approved":
        if auth_status != "valid":
            errors.append(
                "Approved allocation requires valid authorization."
            )

        if not auth_scope.strip():
            errors.append(
                "Approved allocation requires a non-empty scope."
            )

        if not within_budget:
            errors.append(
                "Approved allocation exceeds available "
                "resources or authorized limit."
            )

    elif decision == "denied":
        # A denial is valid even if the numerical request
        # is within budget. External policy or scope
        # restrictions may independently require denial.
        if status != "not_started":
            errors.append(
                "Denied allocation must not start execution."
            )

        if consumed != 0:
            errors.append(
                "Denied allocation must consume zero resources."
            )

        if evaluation["outcome_status"] != "not_evaluated":
            errors.append(
                "Denied allocation must have "
                "outcome_status=not_evaluated."
            )

        if not closed or reason != "allocation_denied":
            errors.append(
                "Denied allocation must be closed "
                "with reason=allocation_denied."
            )

    # -----------------------------------------
    # 2. Resource consumption validation
    # -----------------------------------------

    expected_compliance = consumed <= limit

    if evaluation["budget_compliant"] != expected_compliance:
        errors.append(
            "budget_compliant does not match "
            "actual consumption against budget.limit."
        )

    if decision == "approved" and consumed > requested:
        errors.append(
            "Resource consumption exceeds "
            "the approved requested allocation."
        )

    # -----------------------------------------
    # 3. Execution and termination validation
    # -----------------------------------------

    if decision == "approved":
        if status == "not_started":
            if closed or reason != "none":
                errors.append(
                    "Not-started approved execution "
                    "must remain open with reason=none."
                )

            if consumed != 0:
                errors.append(
                    "Not-started execution must "
                    "consume zero resources."
                )

        elif status == "running":
            if closed or reason != "none":
                errors.append(
                    "Running execution must remain "
                    "open with reason=none."
                )

        elif status == "completed":
            if not closed or reason != "completed":
                errors.append(
                    "Completed execution must be closed "
                    "with reason=completed."
                )

        elif status == "terminated":
            if not closed:
                errors.append(
                    "Terminated execution must be closed."
                )

            if reason not in VALID_TERMINATION_REASONS:
                errors.append(
                    "Terminated execution has "
                    "an invalid termination reason."
                )

    # -----------------------------------------
    # 4. Evaluation consistency validation
    # -----------------------------------------

    outcome = evaluation["outcome_status"]

    if status == "not_started" and outcome != "not_evaluated":
        errors.append(
            "Not-started execution must have "
            "outcome_status=not_evaluated."
        )

    if status == "running" and outcome == "sufficient":
        errors.append(
            "Running execution cannot declare "
            "a final sufficient outcome."
        )

    # -----------------------------------------
    # 5. Authorization consistency
    # -----------------------------------------

    if (
        decision == "approved"
        and reason == "authorization_revoked"
        and status != "terminated"
    ):
        errors.append(
            "Authorization revocation must terminate "
            "the approved execution."
        )

    return errors


def validate_example(path, schema_validator):
    """Validate one example file."""
    print(f"\n[CHECK] {path.relative_to(ROOT)}")

    try:
        record = load_json(path)
    except (OSError, json.JSONDecodeError) as error:
        print(f"[FAIL] JSON loading error: {error}")
        return False

    # JSON Schema validation
    schema_errors = sorted(
        schema_validator.iter_errors(record),
        key=lambda error: str(error.path),
    )

    if schema_errors:
        for error in schema_errors:
            location = ".".join(
                str(part) for part in error.absolute_path
            )
            print(
                f"[SCHEMA FAIL] {location or '<root>'}: "
                f"{error.message}"
            )

        return False

    print("[SCHEMA PASS]")

    # Semantic validation
    semantic_errors = validate_semantics(record)

    if semantic_errors:
        for error in semantic_errors:
            print(f"[SEMANTIC FAIL] {error}")

        return False

    print("[SEMANTIC PASS]")

    # Verify expected example allocation decision
    expected_decision = EXPECTED_RESULTS.get(path.name)

    if expected_decision is not None:
        actual_decision = record["allocation"]["decision"]

        if actual_decision != expected_decision:
            print(
                "[EXPECTATION FAIL] "
                f"expected={expected_decision}, "
                f"actual={actual_decision}"
            )
            return False

    print(
        "[PASS] "
        f"decision={record['allocation']['decision']} "
        f"status={record['execution']['status']} "
        f"closed={record['termination']['closed']}"
    )

    return True


def main():
    """Run validation for the RRG v0.1 examples."""
    print("=== RRG v0.1 Validation ===")

    try:
        schema = load_json(SCHEMA_PATH)
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)

    except (
        OSError,
        json.JSONDecodeError,
        SchemaError,
    ) as error:
        print(f"[FATAL] Schema loading error: {error}")
        return 1

    print("[SCHEMA OK] RRG v0.1")

    all_passed = True

    # Required examples must exist.
    for filename in EXPECTED_RESULTS:
        path = EXAMPLES_DIR / filename

        if not path.is_file():
            print(f"[MISSING] {path.relative_to(ROOT)}")
            all_passed = False

    # Validate all JSON examples.
    example_paths = sorted(EXAMPLES_DIR.rglob("*.json"))

    if not example_paths:
        print("[FATAL] No JSON examples found.")
        return 1

    passed = 0
    failed = 0

    for path in example_paths:
        result = validate_example(path, validator)

        if result:
            passed += 1
        else:
            failed += 1
            all_passed = False

    print("\n=== Validation Summary ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if all_passed:
        print("[SUCCESS] All RRG v0.1 examples passed.")
        return 0

    print("[FAILURE] RRG v0.1 validation failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
