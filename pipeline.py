"""Real SEC filing ingestion, contextual controls and reproducible reporting.

No network calls or third-party packages are required for the supplied subset.
Run: python pipeline.py --input-dir data/raw --output-dir reports
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re,sqlite3
from pathlib import Path
from datetime import datetime,timezone
from decimal import Decimal,InvalidOperation
from collections import Counter,defaultdict
from contextlib import closing

ROOT=Path(__file__).resolve().parent
FIRMS={'895421':'Morgan Stanley','886982':'Goldman Sachs','19617':'JPMorgan Chase','70858':'Bank of America','316709':'Charles Schwab','1390777':'BNY Mellon','93751':'State Street','1393818':'Blackstone'}
KEY=('adsh','tag','version','ddate','qtrs','uom','segments','coreg')
EVENT_FIELDS=['origin','row_number','cik','company','rule_id','severity','owner','adsh','tag','version','ddate','qtrs','uom','segments','coreg','observed_value','detail']
RULES={
 'REQUIRED_FIELDS':('ERROR','Data Engineering','Required numeric-fact keys are populated.'),
 'FILING_LINK':('ERROR','Data Engineering','Fact accession resolves to a selected filing.'),
 'TAG_LINK':('ERROR','Data Engineering','Tag and taxonomy version resolve together.'),
 'VALID_DATE':('ERROR','Data Engineering','Fact period-end is a valid YYYYMMDD date.'),
 'VALID_DURATION':('ERROR','Data Engineering','Quarter duration is a non-negative integer.'),
 'NUMERIC_VALUE':('ERROR','Data Engineering','Non-nil values parse as finite decimals.'),
 'NIL_DISCLOSURE':('INFO','Reporting Analyst','Nil facts are preserved as unknown, never converted to zero.'),
 'DUPLICATE_KEY':('ERROR','Data Engineering','Full SEC NUM context key is unique; other dates/segments are not duplicates.'),
 'CONFLICTING_VALUE':('ERROR','Data Engineering','Repeated full context keys cannot disagree on value.'),
 'INSTANT_DURATION':('ERROR','Reporting Analyst','Instant-type taxonomy facts have zero quarter duration.'),
 'UNIT_CONTRACT':('REVIEW','Reporting Analyst','Monetary and share facts use compatible unit types.'),
}
def read_tsv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def load(path):return {key:read_tsv(path/(key+'.tsv')) for key in ('sub','num','tag','pre')}
def finite(value):
    try:
        n=Decimal(value)
        return n if n.is_finite() else None
    except (InvalidOperation,ValueError,TypeError):return None
def valid_date(value):
    try:return bool(re.fullmatch(r'\d{8}',value)) and datetime.strptime(value,'%Y%m%d') is not None
    except (ValueError,TypeError):return False
def scan(data,origin='REAL_PUBLIC'):
    subs={r['adsh']:r for r in data['sub']};tags={(r['tag'],r['version']):r for r in data['tag']}
    seen={};events=[];counts=Counter();flags=Counter()
    for idx,row in enumerate(data['num'],start=1):
        sub=subs.get(row.get('adsh',''),{});cik=sub.get('cik','UNKNOWN')
        tag=tags.get((row.get('tag',''),row.get('version','')),{});key=tuple(row.get(k,'') for k in KEY)
        def check(rule,bad,detail):
            counts[(cik,rule)]+=1
            if bad:
                flags[(cik,rule)]+=1;severity,owner,_=RULES[rule]
                events.append(dict(origin=origin,row_number=idx,cik=cik,company=sub.get('name','UNRESOLVED'),rule_id=rule,severity=severity,owner=owner,adsh=row.get('adsh',''),tag=row.get('tag',''),version=row.get('version',''),ddate=row.get('ddate',''),qtrs=row.get('qtrs',''),uom=row.get('uom',''),segments=row.get('segments',''),coreg=row.get('coreg',''),observed_value=row.get('value',''),detail=detail))
        check('REQUIRED_FIELDS',any(not row.get(k,'') for k in KEY[:6]),'Missing required context field; empty segments/coreg are valid.')
        check('FILING_LINK',not sub,'Accession not present in selected SUB table.')
        check('TAG_LINK',not tag,'Tag/version pair not present in selected TAG table.')
        check('VALID_DATE',not valid_date(row.get('ddate','')),'Invalid fact date.')
        q=row.get('qtrs','');qvalid=bool(re.fullmatch(r'\d+',q))
        check('VALID_DURATION',not qvalid,'Quarter duration must be an integer >= 0.')
        value=row.get('value','');nil=value.strip()==''
        check('NUMERIC_VALUE',not nil and finite(value) is None,'Non-nil value is not a finite decimal.')
        check('NIL_DISCLOSURE',nil,'Source nil disclosure. Informational, not evidence of a filing error.')
        check('DUPLICATE_KEY',key in seen,'Repeated full context key, including reporting date, duration, units, segments and coregistrant.')
        check('CONFLICTING_VALUE',key in seen and seen[key]!=value,'Same context key has conflicting raw values.')
        check('INSTANT_DURATION',tag.get('iord')=='I' and qvalid and int(q)!=0,'Instant fact has nonzero duration.')
        u=row.get('uom','');dtype=tag.get('datatype')
        incompatible=(dtype=='monetary' and not re.fullmatch(r'[A-Z]{3}',u)) or (dtype=='shares' and u!='shares')
        check('UNIT_CONTRACT',bool(incompatible),'Datatype/unit combination requires review; currency codes are not converted.')
        seen.setdefault(key,value)
    summary=[]
    for (cik,rule),checked in sorted(counts.items()):
        severity,owner,definition=RULES[rule];flagged=flags[(cik,rule)]
        summary.append(dict(origin=origin,cik=cik,company=next((s['name'] for s in data['sub'] if s['cik']==cik),'UNRESOLVED'),rule_id=rule,severity=severity,owner=owner,definition=definition,checked_count=checked,flagged_count=flagged,passed_count=checked-flagged,status=('INFORMATION' if severity=='INFO' else 'ACTION') if flagged else 'PASS'))
    return events,summary

def metric_rows(data):
    """Context-safe metrics; ambiguous candidates produce no arbitrary selected value."""
    result=[]
    for sub in data['sub']:
        rs=[r for r in data['num'] if r['adsh']==sub['adsh'] and r['ddate']==sub['period'] and r['uom']=='USD' and not r['segments'] and not r['coreg']]
        def get(tag,q):
            candidates=[r for r in rs if r['tag']==tag and r['qtrs']==str(q) and finite(r['value']) is not None]
            return finite(candidates[0]['value']) if len(candidates)==1 else None
        assets=get('Assets',0);rhs=get('LiabilitiesAndStockholdersEquity',0);income=get('NetIncomeLoss',1)
        delta=assets-rhs if assets is not None and rhs is not None else None
        # Direct reported balance-sheet totals avoid parent-equity/NCI scope mismatches.
        tolerance=max(Decimal('1'),abs(assets or 0)*Decimal('0.000000001'))
        status='PASS' if delta is not None and abs(delta)<=tolerance else 'NOT_EVALUATED' if delta is None else 'REVIEW'
        result.append(dict(cik=sub['cik'],company=sub['name'],display_name=FIRMS.get(sub['cik'],sub['name']),adsh=sub['adsh'],form=sub['form'],report_period=sub['period'],filed_date=sub['filed'],download_batch='2026Q3',assets_usd=str(assets) if assets is not None else '',reported_liabilities_equity_usd=str(rhs) if rhs is not None else '',quarter_net_income_usd=str(income) if income is not None else '',balance_difference_usd=str(delta) if delta is not None else '',balance_status=status,tolerance_usd=str(tolerance),numeric_facts=sum(r['adsh']==sub['adsh'] for r in data['num']),filing_url=f"https://www.sec.gov/Archives/edgar/data/{sub['cik']}/{sub['adsh'].replace('-','')}/",origin='REAL_PUBLIC'))
    return result

def csv_out(path,rows,fields=None):
    if fields is None:fields=list(rows[0]) if rows else []
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def database(path,data,events,controls,metrics):
    with closing(sqlite3.connect(path)) as con:
        for name,rows in [('submissions',data['sub']),('facts',data['num']),('tags',data['tag']),('presentation',data['pre']),('exceptions',events),('control_results',controls),('company_metrics',metrics)]:
            con.execute('DROP TABLE IF EXISTS "'+name+'"')
            if not rows and name!='exceptions':continue
            fields=list(rows[0]) if rows else EVENT_FIELDS;con.execute('CREATE TABLE "'+name+'" ('+','.join('"'+f+'" TEXT' for f in fields)+')')
            con.executemany('INSERT INTO "'+name+'" VALUES ('+','.join('?' for _ in fields)+')',[[str(r[k]) for k in fields] for r in rows])
        con.execute('CREATE INDEX idx_facts_context ON facts(adsh,tag,version,ddate,qtrs,uom,segments,coreg)')
        con.execute('CREATE INDEX idx_exception_rule ON exceptions(rule_id,cik)')
        sql=(ROOT/'queries.sql').read_text(encoding='utf-8')
        statements=[];buffer=''
        for line in sql.splitlines(keepends=True):
            buffer+=line
            if sqlite3.complete_statement(buffer):statements.append(buffer);buffer=''
        if buffer.strip():raise ValueError('Incomplete SQL statement at end of queries.sql')
        for i,query in enumerate(statements):
            cur=con.execute(query);csv_out(path.parent/f'query_{i+1:02}.csv',[dict(zip([c[0] for c in cur.description],r)) for r in cur.fetchall()],[c[0] for c in cur.description])
        con.commit()

def main():
    a=argparse.ArgumentParser();a.add_argument('--input-dir',type=Path,default=ROOT/'data/raw');a.add_argument('--output-dir',type=Path,default=ROOT/'reports');args=a.parse_args()
    data=load(args.input_dir);args.output_dir.mkdir(parents=True,exist_ok=True)
    events,controls=scan(data);metrics=metric_rows(data)
    csv_out(args.output_dir/'exceptions.csv',events,EVENT_FIELDS)
    csv_out(args.output_dir/'control_results.csv',controls)
    csv_out(args.output_dir/'company_metrics.csv',metrics)
    csv_out(args.output_dir/'companies.csv',[{'cik':s['cik'],'company':s['name']} for s in data['sub']])
    by_cik={m['cik']:m for m in metrics}
    dashboard=[]
    for control in controls:
        m=by_cik[control['cik']]
        dashboard.append(dict(m,**{k:v for k,v in control.items() if k not in m},balance_passed=1 if m['balance_status']=='PASS' else 0))
    csv_out(args.output_dir/'dashboard_controls.csv',dashboard)
    database(args.output_dir/'financial_quality.sqlite',data,events,controls,metrics)
    summary=dict(run_utc=datetime.now(timezone.utc).isoformat(),source_mode='REAL_PUBLIC',filings=len(data['sub']),companies=len({s['cik'] for s in data['sub']}),numeric_facts=len(data['num']),tag_definitions=len(data['tag']),presentation_rows=len(data['pre']),rule_evaluations=sum(c['checked_count'] for c in controls),exception_events=len(events),error_events=sum(e['severity']=='ERROR' for e in events),review_events=sum(e['severity']=='REVIEW' for e in events),informational_events=sum(e['severity']=='INFO' for e in events),distinct_facts_with_error_or_review=len({e['row_number'] for e in events if e['severity']!='INFO'}),balance_checks_passed=sum(m['balance_status']=='PASS' for m in metrics),balance_checks_evaluated=sum(m['balance_status']!='NOT_EVALUATED' for m in metrics),input_sha256={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(args.input_dir.glob('*.tsv'))})
    assert summary['rule_evaluations']==len(data['num'])*len(RULES)
    assert summary['companies']==len(metrics)
    (args.output_dir/'run_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
