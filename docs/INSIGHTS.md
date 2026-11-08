# Verified observations

1. The selected real sample contains **8 filings, 8,951 numeric facts, 531 tag definitions and 1,223 presentation rows**. These are source-coverage counts, not portfolio holdings or assets under management.
2. Eleven controls generated **98,461 rule evaluations**. A rule-evaluation count is not a distinct-fact count. One fact could generate multiple events in a defective input.
3. The real source produced **zero ERROR and zero REVIEW events** under the implemented contracts. There were **12 INFO events**, all nil `CommitmentsAndContingencies` disclosures. There is no evidence here of twelve incorrect company filings.
4. All eight same-context `Assets` versus `LiabilitiesAndStockholdersEquity` checks passed. This compares reported totals and does not independently audit all underlying accounting components.
5. Source units include USD, EUR and shares. A single aggregate sum of all numeric facts would be meaningless. The financial chart uses only selected consolidated USD asset facts.
6. Comparative dates, quarterly/YTD durations, segments and coregistrants are legitimate context distinctions. Ignoring them could produce false duplicates or misleading totals.
7. All **23 executed tests passed**: 17 isolated cases (including valid-context/negative/nil protections) and 6 read-only source regressions. The isolated cases are not source-data findings.
8. SQL and Decimal-based Python metric selection reconciled within USD 0.01; the selected metric ambiguity query returned no rows. Presentation coverage used an existence check and retained the 8,951-fact denominator.

## What remains limited

The eight-filing selection is not a representative sample of all issuers. It contains no real operational incident-resolution history. No measured time-saving, commercial benefit, prediction accuracy or financial recommendation is claimed. CSV refresh is local, and a source-clean result cannot establish the completeness or economic truth of the original filings.
