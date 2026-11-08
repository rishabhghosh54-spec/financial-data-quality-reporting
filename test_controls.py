"""Controlled mutations are isolated in memory. Public raw files are never changed."""
import unittest,copy,csv,json,sqlite3,io
from decimal import Decimal
from pathlib import Path
import pipeline
from contextlib import closing

P=Path(__file__).resolve().parent
REAL=pipeline.load(P/'data/raw')
SOURCE=next(r for r in REAL['num'] if r['tag']=='Assets' and r['ddate']=='20260630' and not r['segments'] and not r['coreg'] and r['uom']=='USD')
SUB=next(r for r in REAL['sub'] if r['adsh']==SOURCE['adsh'])
TAG=next(r for r in REAL['tag'] if (r['tag'],r['version'])==(SOURCE['tag'],SOURCE['version']))

class Controls(unittest.TestCase):
    def setUp(self):self.data={'sub':[copy.deepcopy(SUB)],'num':[copy.deepcopy(SOURCE)],'tag':[copy.deepcopy(TAG)],'pre':[]}
    def codes(self):return {e['rule_id'] for e in pipeline.scan(self.data,'SIMULATED_QA')[0]}
    def test_01_valid_baseline(self):
        """Valid real fact produces no events."""
        self.assertEqual(self.codes(),set())
    def test_02_exact_duplicate(self):
        """Injected duplicate full context is detected."""
        self.data['num'].append(copy.deepcopy(SOURCE));self.assertIn('DUPLICATE_KEY',self.codes());self.assertNotIn('CONFLICTING_VALUE',self.codes())
    def test_03_conflicting_value(self):
        """Injected conflicting duplicate is detected."""
        other=copy.deepcopy(SOURCE);other['value']=str(Decimal(other['value'])+1);self.data['num'].append(other)
        self.assertTrue({'DUPLICATE_KEY','CONFLICTING_VALUE'}<=self.codes())
    def test_04_missing_context(self):
        """Injected missing accession is detected."""
        self.data['num'][0]['adsh']='';self.assertIn('REQUIRED_FIELDS',self.codes())
    def test_05_orphan_filing(self):
        """Injected orphan filing is detected."""
        self.data['num'][0]['adsh']='0000000000-26-999999';self.assertIn('FILING_LINK',self.codes())
    def test_06_unknown_tag(self):
        """Injected missing tag/version relationship is detected."""
        self.data['num'][0]['version']='unregistered/2099';self.assertIn('TAG_LINK',self.codes())
    def test_07_invalid_date(self):
        """Injected impossible date is detected."""
        self.data['num'][0]['ddate']='20260230';self.assertIn('VALID_DATE',self.codes())
    def test_08_invalid_duration(self):
        """Injected negative quarter duration is detected."""
        self.data['num'][0]['qtrs']='-1';self.assertIn('VALID_DURATION',self.codes())
    def test_09_instant_duration(self):
        """Injected duration on an instant fact is detected."""
        self.data['num'][0]['qtrs']='1';self.assertIn('INSTANT_DURATION',self.codes())
    def test_10_invalid_numeric(self):
        """Injected text in numeric value is detected."""
        self.data['num'][0]['value']='NOT_A_NUMBER';self.assertIn('NUMERIC_VALUE',self.codes())
    def test_11_nonfinite(self):
        """Injected nonfinite value is detected."""
        self.data['num'][0]['value']='NaN';self.assertIn('NUMERIC_VALUE',self.codes())
    def test_12_wrong_unit(self):
        """Injected shares unit for monetary fact is detected."""
        self.data['num'][0]['uom']='shares';self.assertIn('UNIT_CONTRACT',self.codes())
    def test_13_nil_is_not_zero(self):
        """Nil is informational and never treated as invalid numeric zero."""
        self.data['num'][0]['value']='';self.assertEqual(self.codes(),{'NIL_DISCLOSURE'});self.assertIsNone(pipeline.finite(''))
    def test_14_negative_is_valid(self):
        """A finite negative number is not automatically a data defect."""
        self.data['num'][0]['value']='-123.50';self.assertNotIn('NUMERIC_VALUE',self.codes())
    def test_15_other_period_is_not_duplicate(self):
        """Different reporting dates remain distinct facts."""
        other=copy.deepcopy(SOURCE);other['ddate']='20251231';self.data['num'].append(other);self.assertNotIn('DUPLICATE_KEY',self.codes())
    def test_16_other_segment_is_not_duplicate(self):
        """Different segment context remains distinct."""
        other=copy.deepcopy(SOURCE);other['segments']='QA_AXIS=QA_MEMBER';self.data['num'].append(other);self.assertNotIn('DUPLICATE_KEY',self.codes())
    def test_17_other_coreg_is_not_duplicate(self):
        """Different coregistrant context remains distinct."""
        other=copy.deepcopy(SOURCE);other['coreg']='QA_COREGISTRANT';self.data['num'].append(other);self.assertNotIn('DUPLICATE_KEY',self.codes())
    def test_18_real_source_baseline(self):
        """Real subset has 8,951 facts, 12 informational nils and zero actionable events."""
        events,controls=pipeline.scan(REAL);self.assertEqual(len(REAL['num']),8951)
        self.assertEqual(len(events),12);self.assertTrue(all(e['severity']=='INFO' for e in events));self.assertEqual(sum(r['checked_count'] for r in controls),98461)
    def test_19_balance_context(self):
        """All eight same-context balance-sheet total checks pass."""
        metrics=pipeline.metric_rows(REAL);self.assertEqual(len(metrics),8);self.assertTrue(all(m['balance_status']=='PASS' for m in metrics))
    def test_20_sql_python_reconciliation(self):
        """Independent SQL selection matches Decimal-based Python metrics."""
        metrics={m['company']:m for m in pipeline.metric_rows(REAL)}
        rows=list(csv.DictReader((P/'reports/query_03.csv').open(encoding='utf-8-sig')))
        self.assertEqual(len(rows),8)
        for r in rows:
            for key in ['assets_usd','reported_liabilities_equity_usd','quarter_net_income_usd']:
                self.assertLess(abs(Decimal(r[key])-Decimal(metrics[r['company']][key])),Decimal('0.01'))
        self.assertEqual(list(csv.DictReader((P/'reports/query_04.csv').open(encoding='utf-8-sig'))),[])
    def test_21_input_provenance(self):
        """Selected public source files match the extraction manifest hashes."""
        import hashlib
        manifest=json.loads((P/'data/source_manifest.json').read_text())
        for name,d in manifest['files'].items():self.assertEqual(hashlib.sha256((P/'data/raw'/name).read_bytes()).hexdigest(),d['sha256'])
    def test_22_no_presentation_fanout(self):
        """Presentation coverage query retains the original fact denominator."""
        r=next(csv.DictReader((P/'reports/query_08.csv').open(encoding='utf-8-sig')));self.assertEqual(int(r['numeric_facts']),8951);self.assertEqual(int(r['facts_with_presentation']),8951)
    def test_23_empty_exception_queue(self):
        """A fully clean subset still exports an empty exception table and query headers."""
        import tempfile
        clean=copy.deepcopy(REAL);clean['num']=[r for r in clean['num'] if r['value'].strip()]
        events,controls=pipeline.scan(clean);self.assertEqual(events,[])
        work=P/'work';work.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as tmp:
            out=Path(tmp)/'clean.sqlite';pipeline.database(out,clean,events,controls,pipeline.metric_rows(clean))
            with closing(sqlite3.connect(out)) as con:self.assertEqual(con.execute('SELECT COUNT(*) FROM exceptions').fetchone()[0],0)
            self.assertEqual(list(csv.DictReader((Path(tmp)/'query_05.csv').open(encoding='utf-8-sig'))),[])

class Recorder(unittest.TextTestResult):
    rows=[]
    def record(self,test,status,detail=''):
        real=int(test._testMethodName.split('_')[1])>=18
        self.rows.append(dict(test_id=test._testMethodName,description=test.shortDescription(),origin='REAL_SOURCE_REGRESSION' if real else 'ISOLATED_QA_CASE',status=status,passed=1 if status=='PASS' else 0,failed=0 if status=='PASS' else 1,detail=detail))
    def addSuccess(self,test):super().addSuccess(test);self.record(test,'PASS')
    def addFailure(self,test,err):super().addFailure(test,err);self.record(test,'FAIL',str(err[1]))
    def addError(self,test,err):super().addError(test,err);self.record(test,'ERROR',str(err[1]))

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Controls)
    result=unittest.TextTestRunner(verbosity=2,resultclass=Recorder).run(suite)
    pipeline.csv_out(P/'reports/test_results.csv',result.rows)
    (P/'reports/test_summary.json').write_text(json.dumps(dict(tests=result.testsRun,passed=sum(r['passed'] for r in result.rows),failed=sum(r['failed'] for r in result.rows),source='Controlled in-memory cases and read-only source regressions; no injected rows in data/raw.'),indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)
