#!/usr/bin/env python3
"""A small, cached Open Library lookup for 24 human-curated books.
No accounts, book texts, publisher descriptions, covers or customer data are fetched.
"""
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
import csv,json,re,time,unicodedata,hashlib,datetime
ROOT=Path(__file__).resolve().parent
CACHE=ROOT/'data/openlibrary';CACHE.mkdir(exist_ok=True)
# These are lookup targets and editorial shelf labels, not claimed API responses.
SELECTIONS=[
('The Hobbit','Tolkien','Fantasy','fantasy adventure dragons'),
("Howl's Moving Castle",'Diana Wynne Jones','Fantasy','fantasy magic adventure'),
('A Wizard of Earthsea','Ursula Le Guin','Fantasy','fantasy magic coming-of-age'),
('Legends & Lattes','Travis Baldree','Fantasy','cozy fantasy coffee'),
('The House in the Cerulean Sea','Klune','Fantasy','fantasy found-family'),
("The Hitchhiker's Guide to the Galaxy",'Douglas Adams','Science fiction','science fiction space humor comedy'),
('The Long Way to a Small, Angry Planet','Becky Chambers','Science fiction','science fiction space found-family'),
('The Martian','Andy Weir','Science fiction','science fiction space survival'),
('A Psalm for the Wild-Built','Becky Chambers','Science fiction','science fiction robots nature'),
('Pride and Prejudice','Jane Austen','Classics','classic romance society'),
('Jane Eyre','Charlotte Bronte','Classics','classic gothic romance'),
('Little Women','Louisa May Alcott','Classics','classic family coming-of-age'),
('The Murder of Roger Ackroyd','Agatha Christie','Mystery','mystery detective crime'),
('The Hound of the Baskervilles','Arthur Conan Doyle','Mystery','mystery detective Sherlock Holmes'),
('The Adventures of Sherlock Holmes','Arthur Conan Doyle','Mystery','mystery detective Sherlock Holmes short-stories'),
('Frankenstein','Mary Shelley','Gothic','gothic science fiction horror'),
('Dracula','Bram Stoker','Gothic','gothic vampires horror'),
('The Time Machine','Wells','Science fiction','science fiction time-travel'),
('The Secret Garden','Frances Hodgson Burnett',"Children's fiction",'children garden friendship'),
('Anne of Green Gables','Montgomery','Classics','classic childhood family'),
("Alice's Adventures in Wonderland",'Lewis Carroll','Fantasy','fantasy children nonsense'),
('The Wind in the Willows','Kenneth Grahame',"Children's fiction",'children animals friendship'),
('Walden','Henry David Thoreau','Nature','nature essays reflective'),
("A Room of One's Own",'Virginia Woolf','Essays','essays literature women')]
PRICES=['17.50','18.00','22.00','16.00','19.00','15.00','21.00','14.00','28.00','26.00','20.00','18.50','18.00','16.50','23.00','19.50','18.00','17.00','24.00','25.00','13.50','15.50','21.00','24.50']
STOCK=[8,5,7,12,4,9,6,11,3,6,0,8,4,10,5,7,0,9,5,4,15,8,3,5]
def norm(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]','',s)
def matching(doc,title,author):
    t=norm(doc.get('title',''));target=norm(title)
    # Ampersand vs 'and' is a catalog punctuation difference.
    aliases={norm('Frankenstein'):{norm('Frankenstein; or, The Modern Prometheus')},norm('The Adventures of Sherlock Holmes'):{norm('The Adventures of Sherlock Holmes [12 stories]')}}
    title_ok=t==target or t.replace('and','')==target.replace('and','') or t in aliases.get(target,set())
    # Match at least the surname; selected work title must also match exactly.
    surname=norm(author.split()[-1])
    return title_ok and any(surname in norm(a) for a in doc.get('author_name',[]))
def fetch_group(group,refresh=False):
    query=' OR '.join('(title:"'+t.replace('"','')+'" AND author:('+a+'))' for t,a,*_ in group)
    params={'q':query,'fields':'key,title,author_name,first_publish_year,subject,edition_count','limit':100}
    url='https://openlibrary.org/search.json?'+urlencode(params)
    key=hashlib.sha256(url.encode()).hexdigest()[:16];path=CACHE/(key+'.json')
    if path.exists() and not refresh:
        payload=json.loads(path.read_text());return payload,url
    req=Request(url,headers={'User-Agent':'MoonlitBooksPortfolio/1.0 (educational local demo)','Accept':'application/json'})
    print('Looking up a group of real books in Open Library…',flush=True)
    with urlopen(req,timeout=45) as r:
        raw=r.read(3_000_001)
    if len(raw)>3_000_000:raise ValueError('Open Library response exceeded the bounded demo limit.')
    data=json.loads(raw)
    if not isinstance(data.get('docs'),list):raise ValueError('Open Library did not return book records.')
    payload={'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'request_url':url,'response':data}
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2))
    time.sleep(1.1) # Below the documented unauthenticated limit of one request/second.
    return payload,url
def import_catalog(refresh=False):
    docs=[];requests=[];timestamps=[]
    for start in range(0,len(SELECTIONS),8):
        payload,url=fetch_group(SELECTIONS[start:start+8],refresh)
        docs.extend(payload['response']['docs']);requests.append(url);timestamps.append(payload['retrieved_at'])
    rows=[];missing=[]
    for index,(title,author,genre,tags) in enumerate(SELECTIONS):
        matches=[d for d in docs if matching(d,title,author) and re.fullmatch(r'(?:/works/)?OL\d+W',d.get('key',''))]
        if not matches:missing.append(title);continue
        doc=max(matches,key=lambda d:d.get('edition_count',0));work=doc['key'].split('/')[-1]
        subjects=[s for s in doc.get('subject',[]) if isinstance(s,str)][:18]
        year=doc.get('first_publish_year')
        rows.append(dict(book_id=f'BK{index+1:03}',title=doc['title'],author='; '.join(doc['author_name']),genre=genre,tags=tags,price_usd=PRICES[index],stock=STOCK[index],blurb='Open Library subjects: '+('; '.join(subjects) if subjects else 'Not supplied in this record.'),openlibrary_work_id=work,source_url='https://openlibrary.org/works/'+work,first_publish_year=str(year) if isinstance(year,int) else '',metadata_source='Open Library Search API',subjects=json.dumps(subjects,ensure_ascii=False),editorial_note='Shelf and reading tags are portfolio curation; price and stock are simulated.'))
    critical={'BK001','BK002','BK004','BK006','BK008','BK010','BK013','BK014'}
    if len(rows)<18 or not critical.issubset({r['book_id'] for r in rows}):
        raise ValueError('Incomplete Open Library matches; existing catalog was preserved. Missing: '+', '.join(missing))
    temp=ROOT/'data/catalog.csv.tmp'
    with temp.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    temp.replace(ROOT/'data/catalog.csv')
    info={'catalog_kind':'openlibrary','count':len(rows),'imported_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_retrieved_at':timestamps,'source':'Open Library Search API','requests':requests,'missing_lookup_targets':missing,'cached':True,'scope':'Real bibliographic records; editorial shelf/tags; simulated USD prices and inventory. No book texts or original covers downloaded.','licensing_url':'https://openlibrary.org/developers/licensing','catalog_sha256':hashlib.sha256((ROOT/'data/catalog.csv').read_bytes()).hexdigest()}
    (ROOT/'data/catalog-info.json').write_text(json.dumps(info,ensure_ascii=False,indent=2))
    print(f'Open Library catalog ready: {len(rows)} real books.',flush=True)
    if missing:print('Unmatched targets omitted: '+', '.join(missing),flush=True)
    return info
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--refresh',action='store_true');args=parser.parse_args()
    import_catalog(args.refresh)
