# Business requirements

## Problem and objective

A reporting analyst needs repeatable metrics from public financial filings and a clear way to distinguish actionable ingestion defects from valid disclosure conventions. Manual copying can confuse filing dates with financial periods, multiply facts through presentation joins, convert nils into zero, or mix currencies and durations.

Deliver a reproducible local ingestion/control workflow, traceable exception outputs, documented SQL and an understandable monitoring report. Success is measured against acceptance checks, not an invented time-saving percentage.

## Stakeholders (project personas, not actual bank contacts)

| Persona | Decision supported |
| --- | --- |
| Reporting analyst | Can this dataset support the selected metrics, and what needs investigation? |
| Data engineer | Which source/context contract failed, and can the run be reproduced? |
| Reporting manager | What is the source coverage and control outcome for this run? |
| Reviewer | Are assertions supported by source records, SQL and tests? |

## Functional requirements

| ID | Requirement | Acceptance evidence |
| --- | --- | --- |
| FR-01 | Preserve original selected source values and full context | Manifest hashes and provenance test |
| FR-02 | Validate 11 fact-level structural/type controls | Named rule outcomes and mutation tests |
| FR-03 | Separate INFO, REVIEW and ERROR outcomes | Nil handling test and explicit actionable-event measure |
| FR-04 | Resolve company, filing and tag/version relationships | Foreign-key tests and SQL exports |
| FR-05 | Reconcile selected balance totals in identical contexts | Eight balance checks and SQL/Python reconciliation |
| FR-06 | Support reruns and configurable input/output folders | CLI arguments and idempotent output checks |
| FR-07 | Export an attributable investigation queue | CSV includes rule, owner, accession and fact context |
| FR-08 | Expose understandable reporting and QA views | PBIP pages and recorded Desktop checks |
| FR-09 | Retain independent, reproducible test evidence | 23 named test results |

## Data contracts and interpretation

- SUB grain: one filing accession (`adsh`).
- TAG grain: tag plus taxonomy/custom version.
- NUM grain: all eight fields in the official natural key, not company/tag alone.
- PRE can map a fact to multiple presentation lines; use an existence check for coverage.
- Empty segment/coregistrant fields represent a legitimate context.
- Empty numeric values are unknown/nil, not numeric zero.
- Negative numeric values are not automatically invalid.
- Monetary units must resemble currency identifiers; the current type check does not validate membership in an ISO currency registry. Currency conversion is out of scope.
- USD and EUR facts remain separate. Shares are never added to currency amounts.
- Instant balance facts use `qtrs=0`; quarter net income uses `qtrs=1`. Year-to-date duration is not substituted for quarterly results.
- Scalar metric selection requires exactly one finite, consolidated, USD candidate in the selected filing period. Missing/ambiguous candidates are not arbitrarily chosen.

## Non-functional requirements

Use standard-library Python and local SQLite; perform no automatic source edits or external sends. Record input hashes and run time. Keep test mutations isolated from real source data. Preserve source links and meaningful column names. Surface limitations alongside headline results.

## Scope exclusions

No claims of real customer portfolio access, trade settlement, fraud detection, regulatory certification, live market analytics or actual employer collaboration. No production incident SLA is claimed.
