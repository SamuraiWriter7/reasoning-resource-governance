# Reasoning Resource Governance (RRG) v0.1

**Version:** 0.1.0  
**Status:** Draft Specification  
**Scope:** Allocation, Recording, Evaluation, and Termination

## 1. Purpose

RRG defines minimal governance rules for allocating and monitoring AI reasoning resources under human-defined objectives.

RRG governs execution eligibility, resource limits, usage recording, and termination conditions.

It does not define AI model internals or execute inference.

## 2. Normative Language

The terms MUST, MUST NOT, SHOULD, and MAY express normative requirements.

- MUST / MUST NOT: mandatory for conformance.
- SHOULD: recommended unless a justified exception exists.
- MAY: optional behavior.

## 3. Governance Record

Each RRG record MUST contain:

| Field | Type | Meaning |
|---|---|---|
| `rrg_version` | string | Specification version (`0.1.0`). |
| `record_id` | string | Unique governance record identifier. |
| `question_id` | string | Human-defined question or objective reference. |
| `authorization` | object | Authorization validity and scope. |
| `budget` | object | Requested and available resource limits. |
| `risk_level` | string | Declared risk classification. |
| `allocation` | object | Allocation decision and reason. |
| `execution` | object | Execution status and consumed resources. |
| `evaluation` | object | Compliance and outcome assessment. |
| `termination` | object | Closure status and reason. |

### 3.1 Authorization

`authorization` MUST contain:

- `status`: `valid`, `missing`, `invalid`, or `revoked`
- `scope`: non-empty string when authorization is valid

A valid status indicates authorization within the represented scope.

Implementations MUST verify authorization against an external authority before granting execution. Self-declared authorization alone is insufficient.

### 3.2 Budget

`budget` MUST contain:

- `unit`: `tokens` or `cost_units`
- `requested`: non-negative number
- `available`: non-negative number
- `limit`: non-negative number

All three quantities MUST use the same declared unit.

`limit` represents the authorized maximum resource consumption for the execution.

### 3.3 Risk Level

`risk_level` MUST be one of:

- `low`
- `medium`
- `high`
- `critical`

Risk classification is input metadata.

RRG v0.1 does not define a universal risk-scoring algorithm.

## 4. Allocation

`allocation` MUST contain:

- `decision`: `approved` or `denied`
- `reason`: non-empty string

Allocation MUST be denied when:

1. Authorization status is not `valid`.
2. Requested resources exceed available resources.
3. Requested resources exceed the authorized limit.
4. The requested operation falls outside the verified authorization scope.
5. The applicable external risk policy prohibits execution.

An approved allocation MUST satisfy all five conditions.

Risk level alone does not automatically determine approval or denial.

## 5. Recording

`execution` MUST contain:

- `status`: `not_started`, `running`, `completed`, or `terminated`
- `consumed`: non-negative number

An execution MUST NOT start when allocation is denied.

Resource consumption MUST be recorded in the unit declared by `budget.unit`.

A denied allocation MUST have:

- `execution.status = not_started`
- `execution.consumed = 0`

An approved allocation MAY initially have `not_started` status.

Implementations SHOULD retain intermediate usage records when monitoring active executions.

## 6. Evaluation

`evaluation` MUST contain:

- `budget_compliant`: boolean
- `outcome_status`: `not_evaluated`, `sufficient`, `insufficient`, or `unverified`

Budget compliance MUST be calculated as:

`execution.consumed <= budget.limit`

Implementations MUST also reject resource consumption that exceeds the approved allocation.

For v0.1, an approved allocation reserves the requested amount as its maximum usable allocation.

Therefore, approved executions MUST satisfy:

`execution.consumed <= budget.requested`

A denied allocation MUST have:

- `evaluation.outcome_status = not_evaluated`

An outcome marked `sufficient` MUST be supported by an externally supplied evaluation result.

RRG does not independently measure the economic or intellectual value of generated answers.

## 7. Termination

`termination` MUST contain:

- `closed`: boolean
- `reason`: `none`, `completed`, `budget_exceeded`, `authorization_violation`, `authorization_revoked`, or `allocation_denied`

The following rules apply:

1. Denied allocations MUST be closed with reason `allocation_denied`.
2. Completed executions MUST be closed with reason `completed`.
3. Executions terminated for budget excess MUST use `budget_exceeded`.
4. Executions terminated for authorization violations MUST use `authorization_violation`.
5. Executions terminated after authorization revocation MUST use `authorization_revoked`.
6. Running executions MUST NOT be marked closed.
7. Closed allocations MUST NOT resume execution without a new authorization and allocation decision.

A closed record represents the end of execution eligibility under that allocation.

It does not require shutdown of the underlying AI model or infrastructure.

## 8. State Consistency

| Allocation | Execution | Closed | Valid |
|---|---|---|---|
| denied | not_started | true | Yes |
| approved | not_started | false | Yes |
| approved | running | false | Yes |
| approved | completed | true | Yes |
| approved | terminated | true | Yes |
| denied | running | false | No |
| denied | completed | true | No |
| approved | running | true | No |
| approved | terminated | false | No |

The table defines structural state consistency.

Semantic validation MUST additionally check authorization, budget conditions, evaluation consistency, and termination reasons.

## 9. Validation Requirements

A conforming RRG v0.1 validator MUST:

1. Validate the record against the RRG JSON Schema.
2. Verify authorization and allocation consistency using trusted policy inputs.
3. Compare requested, available, and authorized limits.
4. Verify consumed resources against approved limits.
5. Check evaluation and termination consistency.
6. Reject invalid state combinations.

The validator MUST NOT treat record fields as proof of external authorization or successful enforcement.

A standalone offline validator MAY check internal consistency without accessing external authorities, but MUST clearly identify its result as an internal consistency assessment rather than verified authorization.

## 10. Security Boundaries

RRG records MUST NOT be used as substitutes for:

- Identity and access management
- Trusted authorization services
- Runtime resource enforcement
- Model safety controls
- Independent audit mechanisms

An implementation MUST distinguish a recorded decision from an actually enforced decision.

RRG v0.1 does not guarantee prevention of unauthorized resource consumption.

## 11. Compatibility

RRG MAY exchange governance information with external systems such as:

- Question-Centric AI
- Reasoning Balance Sheet (RBS)
- Zero-Shutdown
- Shared Trace

No external protocol is required for RRG v0.1 conformance.

Royalty distribution, financial settlement, and reasoning dividend calculation are outside scope.

## 12. Conformance

A record is structurally conformant when it satisfies the JSON Schema and all applicable internal consistency rules.

An implementation is operationally conformant only when the specified authorization, allocation, monitoring, and termination requirements are enforced by its runtime environment.

Structural conformance MUST NOT be represented as proof of operational conformance.

## 13. Core Principle

> Human questions establish purpose.
> Authorization defines permission.
> Budgets define resource boundaries.
> Records preserve accountability.
> Evaluation determines compliance.
> Termination closes execution eligibility.

RRG governs the use of reasoning resources without governing the internal reasoning process itself.
