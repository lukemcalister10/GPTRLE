// PARITY GATE — A1 canonicalised: this loads the SHIPPED engine (_engine_block_v23.js) as the SINGLE
// source of truth and runs it, instead of duplicating the engine math. Any divergence between the
// shipped block and Python is now caught here (it wasn't before, when this file had its own copy).
const D=require('./rl_app_data.json');
const fs=require('fs');
const blk=fs.readFileSync(__dirname+'/_engine_block_v23.js','utf8');
// Run the block in a function scope with D in scope, then hand back the bindings the gate needs.
const eng=new Function('D', blk+'\nreturn {players, recompute, valuePlayer, projFromPeak, get SCALE(){return SCALE;}};')(D);
const {players, recompute}=eng;

recompute('bal');
let maxd=0,nd=0,worst=null;
players.forEach(p=>{const d=Math.abs(p.val-p.v);if(d>maxd){maxd=d;worst=p;}if(d>2)nd++;});
const top=players.slice().sort((a,b)=>b.val-a.val).slice(0,6);
console.log('players |JS-Py|>2:',nd,'/',players.length,'| max diff',maxd, worst?('('+worst.name+' js'+worst.val+' py'+worst.v+' g'+worst.g+' ep'+worst.ep+')'):'');
console.log('SCALE',eng.SCALE.toFixed(4),'| top6 JS:',top.map(p=>p.name.split(' ').slice(-1)[0]+' '+p.val).join(', '));
const wst=players.map(p=>({p,d:Math.abs(p.val-p.v)})).sort((a,b)=>b.d-a.d).slice(0,6);
wst.forEach(({p,d})=>{if(d>0)console.log('  diff',d,p.name,'js',p.val,'py',p.v,'| ep',p.ep,'lnNull',p.lnNull,'g',p.g);});
['Tom Green','Nicholas Martin','Jagga Smith','Errol Gulden','Harry Sheezel'].forEach(nm=>{const p=players.find(x=>x.name===nm);if(p)console.log('  '+nm.padEnd(16),'JS',p.val,'Py',p.v);});
