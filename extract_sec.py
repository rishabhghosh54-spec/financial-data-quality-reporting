from pathlib import Path
import csv,io,json,zipfile,hashlib
ROOT=Path(__file__).resolve().parent
P=ROOT
RAW=P/'data/raw'; RAW.mkdir(parents=True,exist_ok=True)
import argparse
a=argparse.ArgumentParser();a.add_argument('--archive',type=Path,required=True);args=a.parse_args()
source=args.archive
ciks={'895421','886982','19617','70858','316709','1390777','93751','1393818'}
z=zipfile.ZipFile(source)
def stream(name): return csv.DictReader(io.TextIOWrapper(z.open(name),encoding='utf-8-sig',newline=''),delimiter='\t')
subs=[r for r in stream('sub.txt') if r['cik'] in ciks and r['form'] in ('10-Q','10-K','10-Q/A','10-K/A')]
adsh={r['adsh'] for r in subs}
def selected(name):
    with io.TextIOWrapper(z.open(name),encoding='utf-8-sig',newline='') as f:
        header=next(f); lines=io.StringIO(header+''.join(line for line in f if line.split('\t',1)[0] in adsh))
    return list(csv.DictReader(lines,delimiter='\t'))
nums=selected('num.txt'); pres=selected('pre.txt')
keys={(r['tag'],r['version']) for r in nums+pres}
tags=[r for r in stream('tag.txt') if (r['tag'],r['version']) in keys]
def save(name,rows):
    with (RAW/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
for name,rows in [('sub.tsv',subs),('num.tsv',nums),('pre.tsv',pres),('tag.tsv',tags)]:save(name,rows)
manifest={'source_title':'SEC Financial Statement Data Sets','source_url':'https://www.sec.gov/files/dera/data/financial-statement-data-sets/2026q3.zip','landing_page':'https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets','documentation_url':'https://www.sec.gov/files/financial-statement-data-sets.pdf','download_batch':'2026Q3','downloaded_on':'2026-11-08','archive_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'selection':{'ciks':sorted(ciks),'forms':['10-Q','10-K','10-Q/A','10-K/A']},'files':{name:{'rows':len(rows),'sha256':hashlib.sha256((RAW/name).read_bytes()).hexdigest()} for name,rows in [('sub.tsv',subs),('num.tsv',nums),('pre.tsv',pres),('tag.tsv',tags)]},'classification':'Real public financial facts. Subset extraction only; no injected errors in data/raw.'}
(P/'data/source_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
print('TAGS:',sorted({r['tag'] for r in nums if not r['segments'] and not r['coreg'] and any(t in r['tag'].lower() for t in ['assets','liabilities','stockholdersequity','netincome','revenues','revenuefrom','noninterestincome'])}))
