#!/usr/bin/env python3
"""Local-only Moonlit Books demo. Run with Python 3.10 or later."""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse,parse_qs
import json,threading,mimetypes,datetime,traceback
# Import once from the user-started local process; later launches reuse the snapshot.
if __name__=='__main__' and not (Path(__file__).resolve().parent/'data/catalog-info.json').exists():
    print('Preparing the real Open Library catalog (three cached API lookups)…',flush=True)
    from import_openlibrary import import_catalog
    try:import_catalog()
    except Exception as e:raise SystemExit('Open Library import failed; no real-book catalog was claimed. '+str(e))
import core

ROOT=Path(__file__).resolve().parent
RESULTS=ROOT/'results';RESULTS.mkdir(exist_ok=True)
STATE={'running':False,'completed':0,'total':18,'results':[],'report':None}
if (RESULTS/'evaluation.json').is_file():
    try:
        saved=json.loads((RESULTS/'evaluation.json').read_text())
        if saved.get('catalog_sha256')==core.CATALOG_HASH and saved.get('pipeline_version')==core.PIPELINE_VERSION:STATE['report']=saved
    except ValueError:pass
LOCK=threading.Lock();EXTRACTIONS={}
def evaluate_job():
    try:
        def update(p):
            with LOCK:STATE.update(p)
        report=core.run_evaluation(update)
        (RESULTS/'evaluation.json').write_text(json.dumps(report,indent=2))
        with LOCK:STATE.update(report=report,running=False)
    except Exception as e:
        with LOCK:STATE.update(running=False,error=str(e))

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def send_json(self,data,status=200):
        b=json.dumps(data,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(b)
    def send_file(self,path):
        if not path.is_file():return self.send_json({'error':'File not found'},404)
        b=path.read_bytes();self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(str(path))[0] or 'application/octet-stream');self.send_header('Content-Length',str(len(b)));self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(b)
    def do_GET(self):
        u=urlparse(self.path)
        if u.path=='/api/status':return self.send_json(core.model_status())
        if u.path=='/api/catalog':return self.send_json(core.BOOKS)
        if u.path=='/api/catalog-info':return self.send_json(core.CATALOG_INFO)
        if u.path=='/api/fixtures':return self.send_json([{k:f[k] for k in ['id','label','description']} for f in core.FIXTURES])
        if u.path=='/api/invoice-source':
            i=parse_qs(u.query).get('id',[''])[0]
            try:
                text,method=core.invoice_text(i);return self.send_json(dict(text=text,method=method,pdf_url='/invoices/'+i+'.pdf'))
            except ValueError as e:return self.send_json(dict(error=str(e)),400)
        if u.path=='/api/evaluation':
            with LOCK:data=json.loads(json.dumps(STATE))
            return self.send_json(data)
        if u.path=='/api/reviews':
            p=RESULTS/'review-log.jsonl'
            return self.send_json([json.loads(l) for l in p.read_text().splitlines()] if p.exists() else [])
        if u.path=='/invoices/'+Path(u.path).name and Path(u.path).stem in core.FIXTURE_MAP and u.path.endswith('.pdf'):
            return self.send_file(ROOT/'data/invoices'/Path(u.path).name)
        path=ROOT/'web'/('index.html' if u.path=='/' else u.path.lstrip('/'))
        resolved=path.resolve()
        if not resolved.is_relative_to((ROOT/'web').resolve()):return self.send_json(dict(error='Not found'),404)
        return self.send_file(resolved)
    def do_POST(self):
        # Same-origin localhost UI only; no arbitrary remote provider endpoints.
        origin=self.headers.get('Origin')
        if origin and origin not in {'http://127.0.0.1:8867','http://localhost:8867'}:return self.send_json(dict(error='Use the local Moonlit Books page.'),403)
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<12000:raise ValueError('Invalid request size')
            data=json.loads(self.rfile.read(size))
            if not isinstance(data,dict):raise ValueError('Expected an object')
            if self.path=='/api/evaluate':
                with LOCK:
                    if STATE['running']:return self.send_json(dict(error='An evaluation is already running.'),409)
                    if not core.model_status()['ready']:return self.send_json(dict(error='The local qwen3:8b model is not ready.'),503)
                    STATE.update(running=True,completed=0,results=[],error=None)
                threading.Thread(target=evaluate_job,daemon=True).start();return self.send_json(dict(started=True))
            if STATE['running'] and self.path in {'/api/concierge','/api/invoice'}:return self.send_json(dict(error='The quality benchmark is using the model. Try again when it completes.'),409)
            if self.path=='/api/concierge':return self.send_json(core.concierge(data.get('question')))
            if self.path=='/api/invoice':
                result=core.extract_invoice(data.get('fixture_id'));EXTRACTIONS[result['fixture_id']]=result;return self.send_json(result)
            if self.path=='/api/review':
                i=data.get('fixture_id');decision=data.get('decision')
                if i not in EXTRACTIONS:raise ValueError('Extract this invoice before recording a review.')
                if decision not in {'reviewed','follow-up'}:raise ValueError('Unknown review outcome.')
                if decision=='reviewed' and EXTRACTIONS[i]['flags']:raise ValueError('An invoice with open flags requires follow-up.')
                event=dict(timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),fixture_id=i,decision=decision,flags=EXTRACTIONS[i]['flags'],scope='Local synthetic demo only; no payment or external accounting action')
                with (RESULTS/'review-log.jsonl').open('a') as f:f.write(json.dumps(event)+'\n')
                return self.send_json(event)
            return self.send_json(dict(error='Not found'),404)
        except core.ModelError as e:return self.send_json(dict(error=str(e)),503)
        except (ValueError,TypeError,KeyError) as e:return self.send_json(dict(error=str(e)),400)
        except Exception:return self.send_json(dict(error='The operation failed. No generated result was accepted.'),500)

if __name__=='__main__':
    print('Moonlit Books: http://127.0.0.1:8867',flush=True)
    print('Real Open Library metadata + simulated shop records. Press Ctrl+C to stop.',flush=True)
    try:ThreadingHTTPServer(('127.0.0.1',8867),Handler).serve_forever()
    except KeyboardInterrupt:pass
