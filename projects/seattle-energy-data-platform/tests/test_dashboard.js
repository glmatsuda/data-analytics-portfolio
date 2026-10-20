// Logic-level checks; no browser renderer is required or simulated.
const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
const root=path.join(__dirname,'..');const text=fs.readFileSync(path.join(root,'results/dashboard.html'),'utf8');
const script=text.match(/<script>([\s\S]*?)<\/script>/)[1];const els={};
for(const id of ['year','use','hood','reset','scope','cards','trend','types','coverage'])els[id]={value:id==='year'?'2024':'',innerHTML:'',textContent:'',addEventListener(){}};
const context={document:{getElementById:id=>els[id]},window:{}};vm.createContext(context);vm.runInContext(script,context);
const expected=JSON.parse(fs.readFileSync(path.join(__dirname,'dashboard-expectations.json')));
for(const c of expected){els.year.value=String(c.year);els.use.value=c.use;els.hood.value=c.hood;vm.runInContext('update()',context);const s=context.window.dashboardState;for(const field of ['year','records','eligible','compliant','median'])assert.strictEqual(s[field],c[field],JSON.stringify(c)+' '+field);}
els.reset.onclick();assert.strictEqual(context.window.dashboardState.records,3712);assert(!els.year.innerHTML.includes('2025'));assert(!text.includes('__DATA__'));
console.log('Dashboard logic passed 5 independently derived SQLite/Python cohort checks and reset/year-policy checks. Browser rendering is not covered.');
