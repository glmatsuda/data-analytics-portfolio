from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import sqlite3,statistics,collections
W=Path(__file__).resolve().parents[1]
db=sqlite3.connect(W/'results/seattle-energy.sqlite');db.row_factory=sqlite3.Row
rows=db.execute('SELECT * FROM analytics_energy').fetchall();db.close()
def font(n):
    for path in ['/System/Library/Fonts/Helvetica.ttc','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if Path(path).exists():return ImageFont.truetype(path,n)
    return ImageFont.load_default(size=n)
im=Image.new('RGB',(1600,1080),'#edf3f5');d=ImageDraw.Draw(im)
def text(x,y,t,size=22,color='#183142'):d.text((x,y),t,font=font(size),fill=color)
def box(x,y,w,h,fill='white'):d.rounded_rectangle((x,y,x+w,y+h),radius=16,fill=fill)
box(45,35,1510,225,'#133346');text(78,64,'SEATTLE PUBLIC DATA  /  INDEPENDENT PORTFOLIO STUDY',17,'#83d6db')
text(78,102,'Building energy & reporting',49,'white');text(78,172,'Coverage, compliance and weather-normalized energy intensity',25,'#c3d9e2')
text(78,218,'2024 reporting year  ·  All property uses  ·  All neighborhoods',20,'#c3d9e2')
sel=[r for r in rows if r['reporting_year']==2024];eligible=[r for r in sel if r['eligible_eui']]
cards=[('Reported records',f'{len(sel):,}','One property × reporting year'),('Compliance rate',f'{100*sum(r["compliance_status"]=="Compliant" for r in sel)/len(sel):.1f}%','All selected records'),('Median eligible EUI',f'{statistics.median(r["site_eui_wn_kbtu_sqft"] for r in eligible):.1f}','kBtu/ft² · weather normalized'),('Eligible EUI records',f'{len(eligible):,}','Compliant, active, positive EUI')]
for i,(label,value,note) in enumerate(cards):
 x=45+i*383;box(x,285,361,155);text(x+21,305,label,20,'#526e7e');text(x+21,339,value,46);text(x+21,402,note,16,'#526e7e')
box(45,465,735,420);box(800,465,755,420);text(70,486,'Median EUI by reporting year',26);text(70,525,'Changing eligible cohorts; not a same-building trend.',17,'#526e7e')
annual=[]
for y in range(2015,2025):
 v=[r['site_eui_wn_kbtu_sqft'] for r in rows if r['reporting_year']==y and r['eligible_eui']]
 annual.append((y,statistics.median(v),len(v)))
for i,(y,v,n) in enumerate(annual):
 yy=561+i*29;text(70,yy,str(y),17);d.rounded_rectangle((135,yy+2,135+v/50*460,yy+18),radius=3,fill='#167f89');text(610,yy,f'{v:.1f}  n={n:,}',16,'#526e7e')
text(825,486,'Property use comparison',26);text(825,525,'Five largest eligible groups · median EUI (kBtu/ft²)',17,'#526e7e')
groups=collections.defaultdict(list)
for r in eligible:groups[r['property_use']].append(r['site_eui_wn_kbtu_sqft'])
top=sorted(groups,key=lambda k:(-len(groups[k]),k))[:5]
for i,k in enumerate(top):
 yy=570+i*58;v=statistics.median(groups[k]);label=k if len(k)<43 else k[:40]+'…';text(825,yy,label,18);text(1350,yy,f'{v:.1f}  n={len(groups[k]):,}',17,'#526e7e');d.rounded_rectangle((825,yy+29,825+min(v/80,1)*660,yy+40),radius=3,fill='#167f89')
box(45,908,1510,106);text(70,927,'Coverage before conclusions',23);text(70,963,'2024: 239 missing EUI values. The median excludes 287 records failing one or more eligibility rules.',20,'#526e7e')
text(48,1030,'Generated static preview of actual metrics · Interactive HTML included · Source: City of Seattle / teqw-tu6e',18,'#526e7e')
text(48,1055,'Snapshot 20 October 2026 · Source contains 2025 records; dashboard stops at 2024 pending metadata review.',16,'#526e7e')
im.save(W/'results/dashboard-preview.png')
print('Created actual-data static preview.')
