-- 1: Context-safe source totals. These are fact counts, not summed dollars across incompatible tags.
SELECT s.name AS company, s.form, s.period AS report_period, s.filed,
       COUNT(*) AS numeric_facts,
       SUM(CASE WHEN TRIM(f.value)='' THEN 1 ELSE 0 END) AS nil_disclosures
FROM facts f JOIN submissions s ON s.adsh=f.adsh
GROUP BY s.adsh,s.name,s.form,s.period,s.filed ORDER BY numeric_facts DESC;

-- 2: Duplicate detection uses the complete SEC natural key, including segment and coregistrant.
SELECT adsh,tag,version,ddate,qtrs,uom,segments,coreg,COUNT(*) AS occurrences
FROM facts GROUP BY adsh,tag,version,ddate,qtrs,uom,segments,coreg
HAVING COUNT(*)>1 ORDER BY occurrences DESC;

-- 3: Independent SQL metric selection. Never join PRE directly and multiply facts.
SELECT s.name AS company,s.period,
 MAX(CASE WHEN f.tag='Assets' AND f.qtrs='0' THEN CAST(NULLIF(f.value,'') AS REAL) END) AS assets_usd,
 MAX(CASE WHEN f.tag='LiabilitiesAndStockholdersEquity' AND f.qtrs='0' THEN CAST(NULLIF(f.value,'') AS REAL) END) AS reported_liabilities_equity_usd,
 MAX(CASE WHEN f.tag='NetIncomeLoss' AND f.qtrs='1' THEN CAST(NULLIF(f.value,'') AS REAL) END) AS quarter_net_income_usd
FROM submissions s JOIN facts f ON f.adsh=s.adsh AND f.ddate=s.period
WHERE f.uom='USD' AND f.segments='' AND f.coreg=''
GROUP BY s.adsh,s.name,s.period ORDER BY s.name;

-- 4: Candidate ambiguity check supports the scalar-selection assumptions in Query 3.
SELECT adsh,tag,ddate,qtrs,COUNT(*) AS candidates
FROM facts WHERE uom='USD' AND segments='' AND coreg=''
AND ((tag IN ('Assets','LiabilitiesAndStockholdersEquity') AND qtrs='0') OR (tag='NetIncomeLoss' AND qtrs='1'))
GROUP BY adsh,tag,ddate,qtrs HAVING COUNT(*)>1;

-- 5: Operational exception queue; informational nils do not inflate the action backlog.
SELECT company,rule_id,severity,owner,COUNT(*) AS events
FROM exceptions GROUP BY company,rule_id,severity,owner ORDER BY severity,company;

-- 6: Business-friendly control health by rule; denominators are rule evaluations.
SELECT rule_id,severity,SUM(CAST(checked_count AS INTEGER)) AS checks,
 SUM(CAST(flagged_count AS INTEGER)) AS flagged,
 ROUND(100.0*SUM(CAST(flagged_count AS INTEGER))/NULLIF(SUM(CAST(checked_count AS INTEGER)),0),4) AS flag_rate_pct
FROM control_results GROUP BY rule_id,severity ORDER BY flagged DESC,rule_id;

-- 7: Taxonomy/units inspection preserves USD versus EUR and share facts separately.
SELECT t.datatype,f.uom,COUNT(*) AS facts
FROM facts f JOIN tags t ON t.tag=f.tag AND t.version=f.version
GROUP BY t.datatype,f.uom ORDER BY facts DESC;

-- 8: Presentation coverage is an existence check, so one fact is counted once.
SELECT COUNT(*) AS numeric_facts,
 SUM(CASE WHEN EXISTS(SELECT 1 FROM presentation p WHERE p.adsh=f.adsh AND p.tag=f.tag AND p.version=f.version) THEN 1 ELSE 0 END) AS facts_with_presentation
FROM facts f;
