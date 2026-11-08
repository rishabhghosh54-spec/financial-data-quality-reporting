# Interview walkthrough

## Explain the project in about a minute

I built a financial reporting data-quality workflow using public SEC filings from eight financial-services companies. Python preserves source context and runs eleven controls; SQLite provides reproducible reporting queries; Power BI summarizes control health and test evidence. I kept genuine source findings separate from deliberately altered test cases. The real sample has 8,951 facts, twelve informational nil disclosures and no actionable events under my implemented contracts. Twenty-three automated tests cover defects, valid edge cases and reconciliation against the source.

## Questions to be ready for

**Why use public financial statements?** They provide traceable, real records with reporting dates, units, taxonomy versions and meaningful data-quality challenges. I do not claim access to bank customer or internal trade data.

**Why not simply remove duplicate tags?** A tag can legitimately recur across dates, durations, units, segments, filings and coregistrants. I use the complete SEC context key and retain all raw records.

**Why aren't the twelve blank values errors?** They are nil disclosure facts on CommitmentsAndContingencies. I retain them as unknown and classify them as INFO rather than inventing zero values or issuer defects.

**What would make the controls useful when this sample has no actionable defects?** Isolated cases demonstrate that specific defects are caught, and valid edge cases demonstrate some false-positive protections. The project also shows repeatable ingestion, metric reconciliation, source lineage and investigation outputs. It does not claim real operational incidents were resolved.

**How did you prevent double-counting?** The SQL coverage query uses an existence check for presentation mappings. DAX fact/financial metrics deduplicate the repeated company/rule rows at filing accession grain. I keep quarterly net income separate from YTD duration.

**What is a limitation of the balance check?** It compares reported Assets with reported LiabilitiesAndStockholdersEquity in the same context. That is a consistency check, not an independent audit of every component. Parent-only equity can differ because of noncontrolling interests and other scope items.

**What is the meaning of 98,461?** It is eleven rule evaluations for each of 8,951 facts, not a count of distinct transactions or distinct defects.

**What would you improve next?** Agree reporting requirements and ownership with a real stakeholder, extend source coverage with explicit versioning, add a proper currency registry and richer taxonomy policies, and define refresh/escalation expectations. These are future improvements, not completed features.

Be able to open and explain the actual SQL, Python controls and test assertions before adding skills or ownership claims to a resume. No real employer collaboration or business benefit measurement is represented by this portfolio.
