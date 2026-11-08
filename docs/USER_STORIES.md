# User journeys and acceptance criteria

## Journey 1 — Reporting analyst

Run the pipeline, inspect the real-data page, select a company, read the rule outcomes, and investigate any relevant CSV event using its accession and complete fact context. A nil disclosure stays visible as INFO; it does not enter the action backlog.

**US-01:** As a reporting analyst, I need company-level source coverage so I know what the report includes.

- Eight selected accessions reconcile to the SUB subset.
- Company filtering changes filing/fact totals without multiplying fact counts by rules.
- Filing batch and financial period are separately labelled.

**US-02:** As a reporting analyst, I need nil disclosures separated from ingestion failures.

- Empty values remain empty in the raw files.
- The real run reports twelve INFO events and zero ERROR/REVIEW events.
- The nil test expects no NUMERIC_VALUE failure.

## Journey 2 — Data engineer

Inspect an ERROR/REVIEW context, reproduce its control result in a separate test copy, correct the processing assumption or obtain a corrected source, rerun, and compare source hashes. Never overwrite public source values just to make a check pass.

**US-03:** As a data engineer, I need complete-context duplicate detection to avoid discarding valid comparative/segment facts.

- Exact duplicates and conflicting values are detected.
- Different dates, segment contexts and coregistrants are not duplicate-key failures.
- Original rows are retained; this project flags rather than silently deletes them.

**US-04:** As a data engineer, I need input provenance and deterministic counts.

- A rerun on the supplied raw files has the same event/control/metric results, excluding run timestamp.
- Input hashes match the extraction manifest.
- All query outputs can be regenerated locally.

## Journey 3 — Reporting manager / reviewer

Read the run summary, source coverage, balance-check result and test evidence. Review exclusions before signing off on use for this demonstration report. No actual bank stakeholder approval is represented.

**US-05:** As a reviewer, I need independently reconciled metrics.

- Python Decimal-selected values agree with SQL-selected values within USD 0.01.
- The SQL candidate-ambiguity query returns zero rows for the selected metrics.
- Balance checks compare the same filing, date, unit, duration and consolidated context.

**US-06:** As a reporting manager, I need clear evidence of what was tested.

- The QA page distinguishes isolated cases from read-only real-source regressions.
- Every listed case has PASS/FAIL evidence from an executed test.
- Passing cases are not presented as a count of real source errors caught.

## Local delivery backlog

| Item | Priority | Status / evidence |
| --- | --- | --- |
| Source acquisition and eight-company extraction | P1 | Complete; manifest |
| Fact-level validation controls | P1 | Complete; pipeline/tests |
| SQL metric reconciliation | P1 | Complete; Query 3 and regression test |
| Controlled test suite | P1 | Complete; 23 cases |
| Reporting and QA report definitions | P1 | Complete; both pages rendered and saved |
| Desktop refresh and filter review | P1 | Complete for representative contexts; see DELIVERY_STATUS.md |
| Source-specific limitations/runbook | P1 | Complete; docs |
| Optional future scheduled refresh | P3 | Not implemented |
| Optional future issue-tracker integration | P3 | Not implemented |

These are project-management artifacts created for this portfolio; they are not records of a real Morgan Stanley sprint or stakeholder engagement.
