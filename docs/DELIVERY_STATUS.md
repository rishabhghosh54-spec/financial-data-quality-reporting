# Delivery verification

Completed: official-source download; eight-company extraction; source hashes; Python pipeline; eight SQL queries; Decimal/SQL reconciliation; 23 automated tests; requirements, stories, runbook and insights; two-page PBIP definitions with 16 DAX measures.

Power BI Desktop verification completed:

- Both CSV sources refreshed successfully in the new local PBIP.
- Reporting Controls rendered 8 filings, 8,951 facts, 98,461 evaluations, zero actionable events, 12 informational nil disclosures, and 100% balance-check pass coverage.
- Company selection responded: Bank of America showed 1,532 source facts, two informational nils, and reported assets of USD 3,499.2 billion at displayed precision.
- QA Test Evidence rendered 23 cases, 23 passed, zero failed and 100% pass rate.
- Selecting REAL_SOURCE_REGRESSION changed the QA cards to 6 cases, 6 passed, zero failed and 100%; clearing the filter restored 23 cases.
- Both pages were saved with their filters reset to All and Reporting Controls as the opening page.
- Actual Desktop screenshots are included in screenshots/.

The first Desktop session encountered a WebView2 preview error during filter review. Restarting Desktop and reopening/refreshing the same saved sources recovered the preview; both pages were then checked and saved. This is not a claim that the desktop runtime cannot fail again.

Source checks, SQL/Python reconciliation, repeat-run CSV equality, source hashes, report JSON/bounds, and 23 automated cases all passed. Filter checks are representative, not exhaustive; individual control-rule and QA-status selections were not separately exercised.

This GitHub source copy excludes the Desktop cache and replaces machine-specific CSV paths with documented defaults. The original local report was checked before preparing this copy. No Power BI service publication or application submission has been performed.
