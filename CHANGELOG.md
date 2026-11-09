# Changelog

All notable changes to Reasoning Resource Governance (RRG) are documented in this file.

RRG is a minimal, model-agnostic specification for question-centered AI reasoning resource governance.

This project follows Semantic Versioning for release identification.

## [0.1.0] - 2026-11-09

### Initial Release

Established the first public specification of Reasoning Resource Governance (RRG).

RRG v0.1.0 defines a minimal governance framework for allocating, recording, evaluating, and terminating AI reasoning resource usage under human-defined purposes, authorization, and budget constraints.

### Added

#### Core Specification

- Added `README.md` describing the project's purpose, scope, and design principles.
- Added `specs/rrg-v0.1.md` defining the four core governance functions:
  - Allocation
  - Recording
  - Evaluation
  - Termination

#### Governance Data Model

- Added `schemas/rrg-v0.1.schema.json`.
- Defined JSON Schema Draft 2020-12 validation.
- Introduced governance records containing:
  - Question identifier
  - Authorization status and scope
  - Resource budget
  - Risk classification
  - Allocation decision
  - Resource consumption
  - Evaluation result
  - Termination state

#### Validation Examples

- Added `examples/valid-allocation.json`.
  - Demonstrates authorized allocation and completed execution within budget.

- Added `examples/denied-allocation.json`.
  - Demonstrates allocation denial when requested resources exceed available and authorized limits.

Both examples are expected to satisfy structural and semantic validation.

#### Automated Validation

- Added `scripts/validate_examples.py`.
- Implemented:
  - JSON Schema validation
  - Budget consistency checks
  - Authorization-state consistency checks
  - Execution-state consistency checks
  - Evaluation consistency checks
  - Termination-state consistency checks
  - Expected allocation-decision verification

- Added `.github/workflows/validate.yml`.
- Enabled automated validation on:
  - Push to `main`
  - Pull requests
  - Manual workflow dispatch

### Validation Status

GitHub Actions validation passed for the initial v0.1 examples.

Validated example records:

| Example | Expected Decision | Result |
|---|---|---|
| `valid-allocation.json` | approved | PASS |
| `denied-allocation.json` | denied | PASS |

Validation confirms internal structural and semantic consistency for the supplied examples.

It does not establish runtime enforcement, external authorization authenticity, or comprehensive security assurance.

### Design Boundaries

RRG v0.1.0 intentionally excludes:

- AI model internals
- Reasoning optimization algorithms
- Economic valuation of AI output
- Reasoning dividend calculation
- Royalty distribution
- Financial settlement
- Enterprise identity management
- Infrastructure-level shutdown mechanisms

RRG may interoperate with Question-Centric AI, Reasoning Balance Sheet (RBS), Zero-Shutdown, and Shared Trace.

No external protocol is required for v0.1 conformance.

### Known Limitations

- Runtime resource enforcement is not implemented.
- External authorization is not independently verified.
- Outcome quality is not independently assessed.
- Validation uses a limited set of example records.
- Comprehensive negative test coverage is not yet provided.
- Production deployment suitability has not been established.

### Release Principle

> Allocate only what is needed.
> Record what is consumed.
> Evaluate what is achieved.
> Terminate what is no longer authorized or necessary.

RRG v0.1.0 establishes a minimal, independently understandable governance specification.

Further expansion is not required for the initial specification release.
