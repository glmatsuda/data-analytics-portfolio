"""Validate and consolidate metadata CSV exports. Python 3.10+, no packages."""
from pathlib import Path
import argparse, csv, hashlib, html, json, re, os, tempfile
FIELDS=['system','table','column','data_type','owner','classification']
TYPES={'string','integer','decimal','date','boolean'}
CLASSES={'Public','Internal','Confidential','Restricted'}
IDENT=re.compile(r'^[A-Za-z][A-Za-z0-9_]*$')
EMAIL=re.compile(r'^[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
def run(source, destination):
    source=Path(source).resolve(); destination=Path(destination).resolve()
    if not source.is_dir(): raise ValueError('Input must be an existing directory')
    if source==destination or source in destination.parents or destination in source.parents:
        raise ValueError('Input and output directories must be separate, non-nested folders')
    paths=sorted(source.glob('*.csv'))
    if not paths: raise ValueError('No CSV inputs found')
    records=[]; manifest=[]
    # Read and check every schema before making any output changes.
    for path in paths:
        manifest.append({'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        with path.open(newline='',encoding='utf-8-sig') as f:
            reader=csv.DictReader(f)
            if reader.fieldnames!=FIELDS: raise ValueError(f'{path.name}: expected exact headers {FIELDS}')
            for line,row in enumerate(reader,2):
                if None in row or any(v is None for v in row.values()): raise ValueError(f'{path.name}:{line}: invalid field count')
                records.append(({k:v.strip() for k,v in row.items()},path.name,line))
    groups={}; rejected=[]; valid=0
    for row,file,line in records:
        reasons=[]
        if any(not IDENT.fullmatch(row[k]) for k in ['system','table','column']): reasons.append('invalid identifier')
        if row['data_type'] not in TYPES: reasons.append('unknown data_type')
        if not EMAIL.fullmatch(row['owner']): reasons.append('missing or invalid owner')
        if row['classification'] not in CLASSES: reasons.append('unknown classification')
        if reasons: rejected.append([file,line,row['system'],row['table'],row['column'],'; '.join(reasons)])
        else:
            valid+=1; key=tuple(row[k].lower() for k in ['system','table','column'])
            groups.setdefault(key,[]).append((row,file,line))
    accepted=[]; duplicate_rows=0; conflict_rows=0
    for key,group in sorted(groups.items()):
        variants={tuple(row[k] for k in ['data_type','owner','classification']) for row,_,_ in group}
        if len(variants)>1:
            conflict_rows+=len(group)
            for row,file,line in group: rejected.append([file,line,*key,'conflicting metadata for same key'])
        else:
            row=dict(group[0][0]); row.update(zip(['system','table','column'],key))
            accepted.append([row[k] for k in FIELDS]); duplicate_rows+=len(group)-1
    summary={'input_rows':len(records),'accepted_unique_columns':len(accepted),'duplicate_rows_collapsed':duplicate_rows,
             'rejected_rows':len(rejected),'conflicting_rows':conflict_rows,'input_files':manifest}
    assert len(records)==len(accepted)+duplicate_rows+len(rejected)
    destination.mkdir(parents=True,exist_ok=True)
    # Stage files before replacing destinations. Atomic per file, not a batch transaction.
    with tempfile.TemporaryDirectory(dir=destination) as tmp:
        tmp=Path(tmp)
        for name,head,rows in [('catalog.csv',FIELDS,accepted),('exceptions.csv',['file','line','system','table','column','reason'],rejected)]:
            with (tmp/name).open('w',newline='',encoding='utf-8') as f:
                w=csv.writer(f); w.writerow(head)
                # Prevent untrusted exception fields from becoming spreadsheet formulas.
                w.writerows([["'"+v if isinstance(v,str) and v.startswith(('=','+','-','@')) else v for v in r] for r in rows])
        (tmp/'run-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
        body=''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in r)+'</tr>' for r in accepted)
        (tmp/'catalog.html').write_text('<!doctype html><meta charset="utf-8"><title>Metadata catalog demo</title><style>body{font:16px system-ui;margin:40px;color:#172c3c}table{border-collapse:collapse}td,th{padding:12px;border-bottom:1px solid #ddd;text-align:left}th{background:#edf5f6}</style><h1>Metadata catalog</h1><p>Synthetic portfolio demonstration. '+str(len(accepted))+' accepted columns. Exceptions require review.</p><table><tr>'+''.join('<th>'+k+'</th>' for k in FIELDS)+'</tr>'+body+'</table>')
        for path in tmp.iterdir(): os.replace(path,destination/path.name)
    return summary
def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--input',type=Path,required=True); parser.add_argument('--output',type=Path,required=True); args=parser.parse_args()
    try: result=run(args.input,args.output)
    except (ValueError,OSError,csv.Error) as exc: parser.exit(2,f'Error: {exc}\n')
    print(json.dumps(result,indent=2)); return 0
if __name__=='__main__': main()
