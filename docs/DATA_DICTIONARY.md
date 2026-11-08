# Data dictionary and reporting grain

## Source subset

| File | Grain / purpose |
| --- | --- |
| sub.tsv | Filing accession (`adsh`), CIK, legal name, form, financial period, filing date |
| num.tsv | One reported numeric context: accession, tag, version, date, quarter duration, unit, segment, coregistrant |
| tag.tsv | Tag and taxonomy/custom version definition; includes datatype and instant/duration indicator |
| pre.tsv | Statement presentation line; multiple lines can refer to one fact |

Dates are YYYYMMDD source strings. `qtrs=0` represents instant facts; positive values describe duration. Empty `segments` and `coreg` are valid. An empty `value` is nil/unknown. Taxonomy versions are not interchangeable.

## Derived outputs

`company_metrics.csv` has one selected filing per company in this sample. Asset totals use the filing's `period`, USD, instant duration and empty segment/coreg context. Quarter net income uses the same selection except `qtrs=1`. Candidate ambiguity produces an unavailable result rather than an arbitrary pick. `balance_status` is PASS, REVIEW or NOT_EVALUATED.

`control_results.csv` has one row per company/rule: checked_count, flagged_count, passed_count, severity, owner and status. INFO flags are informational and excluded from actionable totals. The type-level UNIT_CONTRACT recognizes a three-capital-letter monetary unit shape, not a validated currency registry.

`dashboard_controls.csv` joins the one-filing metric row to its eleven rule rows. Its numeric_facts and financial metrics are repeated by design. DAX uses accession-level SUMX/MAX selection for those repeated fields, while checked/flagged counts are additive over company/rule rows. The report must not directly SUM repeated asset/fact columns.

`exceptions.csv` preserves source row number, accession, tag/version, date, duration, unit, segments/coreg, raw value, severity, rule and owner. Row numbers refer to the extracted subset's data rows, excluding its header; they are not original archive line numbers.

`test_results.csv` has one row per executed test. ISOLATED_QA_CASE means an in-memory case; REAL_SOURCE_REGRESSION means a read-only source assertion. `passed` and `failed` are one/zero flags. Tests never overwrite real raw rows.
