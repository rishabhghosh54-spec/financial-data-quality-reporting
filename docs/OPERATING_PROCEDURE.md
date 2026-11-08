# Operating procedure

## Preconditions

Python 3.10+ and the selected public source files in `data/raw`. Power BI Desktop is needed only for the interactive report. Preserve a copy of the extraction manifest. No credentials or customer data are required.

## Run

1. Confirm the source batch/selection in `data/source_manifest.json`.
2. Run `python pipeline.py` from the project folder.
3. Run `python test_controls.py`.
4. Inspect `reports/run_summary.json` and `reports/test_summary.json`.
5. Open the PBIP, update CSV paths if the folder moved, and refresh.
6. Check baseline totals, then sample a company and a rule; clear the slicers afterward.

## Outputs and ownership

| Output | Interpretation | Project owner persona |
| --- | --- | --- |
| exceptions.csv | Traceable row-level INFO/REVIEW/ERROR events | Reporting analyst / data engineer |
| control_results.csv | Evaluated/flagged counts by company and rule | Data engineer |
| company_metrics.csv | Context-safe selected financial facts and checks | Reporting analyst |
| query_01..08.csv | Reproducible SQL answers | Analyst/reviewer |
| test_results.csv | Isolated-case and source-regression outcomes | QA reviewer |
| run_summary.json | Coverage, counts, hashes and run timestamp | Reporting manager |

## Triage

- **ERROR:** inspect the complete fact key and raw record. Quarantine from downstream use until the cause is understood. This project reports the event but does not automatically delete or repair source rows.
- **REVIEW:** inspect the unit/context expectation and source filing. A type-policy mismatch is not proof the source financial statement is wrong.
- **INFO:** preserve disclosure context. Nil values must not be converted to zero to remove the event.
- **Balance REVIEW/NOT_EVALUATED:** check tag availability, candidate ambiguity, date, unit, context and scope before drawing an accounting conclusion. Do not substitute parent-only equity for a total including noncontrolling interests.

Ownership is illustrative. Escalation timings must be agreed in a real deployment; no bank SLA is invented here.

## Recovery and reruns

Outputs are derived and can be regenerated from the raw subset. The pipeline rebuilds its named local SQLite tables. Keep separate output directories for experiments via `--output-dir`; tests intentionally target the supplied baseline reports. If a test fails, resolve it before presenting its result as passed. A run is not current merely because the Power BI window was reopened: refresh after regenerating CSVs.

## Publication

Share only public source subsets, code, documentation and screenshots after reviewing the final package. Do not add `.pbi` cache files, personal paths or credentials to GitHub. Update path instructions for a cloned copy. No external publishing or sharing is performed by the pipeline itself.
