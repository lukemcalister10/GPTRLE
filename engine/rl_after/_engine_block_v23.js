/* ===== v2.3 ENGINE (DOM-free, asymmetric tilt + 8-band, verified to Python) ===== */
const {PEAK,PEAK_AGE,GAMMA,PMAX,S_SH,BUST_BAND,LENS,BAND_ANCHOR,bands,MIX,BASEPK_REG,POOL,DELTAS,
  CAPT_GAIN,CAPT_EXP,CAPT_CAP,pm_pos:PM_POS,pm_band:PM_BAND,
  TILT_REF,SUS_MIN}=D;
// Output-tilt params are LIVE-editable in-app (tilt sliders). Defaults come straight from D and
// reproduce the shipped Balanced board exactly. Tilt feeds outTilt() -> the per-player `relative`
// term only; it does NOT enter SCALE or the pick curve (those come from projFromPeak), so changing
// tilt re-runs valuePlayer but never triggers a curve rebuild.
let GAIN_UP=D.GAIN_UP,W_UP=D.W_UP,UP_MAX=D.UP_MAX,TILT_HI=D.TILT_HI,
    GAIN_DN=D.GAIN_DN,W_DN=D.W_DN,DN_MAX=D.DN_MAX,TILT_LO=D.TILT_LO,NBAD_REF=D.NBAD_REF;
const NB=bands.length;
const PVC0=D.PVC, SCALE0=D.SCALE, REPL0=D.REPL, CAPT0=D.CAPT_THRESH, ALPHA0=D.ALPHA, CURVE_H0=D.CURVE_H;
let REPL=Object.assign({},D.REPL), CAPT_THRESH=D.CAPT_THRESH, ALPHA=D.ALPHA, CURVE_H=D.CURVE_H,
    SEASON_PROG=D.SEASON_PROG,
    SCALE=1, PVC={};
const cohort=D.cohort;
const players=D.active.map((p,i)=>Object.assign({},p,{id:i,del:false,ovr:null,val:0}));
const BACK=(D.back||[]).map((p,i)=>Object.assign({},p,{id:100000+i,del:false,ovr:null,val:0})); // recalled retirees, backward views only
const DEFC=[56,62,67,71,74,77,79,80,80,79];
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
// round-half-to-even to match Python round()
const r2e=x=>{if(!isFinite(x))return x;const s=x<0?-1:1;x=Math.abs(x);const f=Math.floor(x),d=x-f;let r;if(d<0.5)r=f;else if(d>0.5)r=f+1;else r=(f%2===0)?f:f+1;return s*r;};
const grpOf=p=>p.ovr||p.grp;
const frac=(a,pa)=>DELTAS[String(clamp(Math.round(a-pa),-8,14))];
const captPrem=l=>{const o=Math.max(0,l-CAPT_THRESH);if(o<=0)return 0;const cb=CAPT_GAIN*Math.pow(o,CAPT_EXP);return cb*CAPT_CAP/(CAPT_CAP+cb);};
const posval=x=>S_SH*Math.log(1+Math.exp(Math.min(x/S_SH,40)));
const bandof=k=>{for(let i=0;i<bands.length;i++)if(k>=bands[i][0]&&k<=bands[i][1])return i;return bands.length-1;};
const bandcoord=pk=>{if(pk<=BAND_ANCHOR[0])return 0;if(pk>=BAND_ANCHOR[NB-1])return NB-1;for(let i=0;i<NB-1;i++)if(BAND_ANCHOR[i]<=pk&&pk<=BAND_ANCHOR[i+1])return i+(pk-BAND_ANCHOR[i])/(BAND_ANCHOR[i+1]-BAND_ANCHOR[i]);return NB-1;};
const basepk=(g,b)=>{const a=BASEPK_REG[g+'|'+b];if(a!=null)return a;const c=POOL[String(b)];return c!=null?c:75;};
const basepkC=(g,pk)=>{const fb=bandcoord(pk),lo=Math.floor(fb),hi=Math.min(NB-1,lo+1),f=fb-lo;return (1-f)*basepk(g,lo)+f*basepk(g,hi);};
function expected(g,band,s){s=Math.max(1,Math.min(10,Math.round(s)));let c=PM_POS[band+'|'+g]||PM_BAND[String(band)]||DEFC;let v=c[s-1];if(v==null){const vv=c.filter(x=>x!=null);v=vv.length?vv[Math.min(s-1,vv.length-1)]:DEFC[s-1];}return v;}
function expectedC(g,pk,s){const fb=bandcoord(pk),lo=Math.floor(fb),hi=Math.min(NB-1,lo+1),f=fb-lo;return (1-f)*expected(g,lo,s)+f*expected(g,hi,s);}
function outTilt(p,g,ep){const ln=p.ln;if(ln==null)return 1.0;const tr=p.track||[];const cs=tr.length?Math.max.apply(null,tr.map(t=>t.s)):Math.max(1,2026-p.yr);const sig=ln-expectedC(g,ep,cs);if(sig>=0){const conf=clamp(p.g/W_UP,0,UP_MAX);return clamp(1+GAIN_UP*sig/TILT_REF*conf,TILT_LO,TILT_HI);}let nb=0;for(const t of tr){if(t.a<expectedC(g,ep,t.s)-1)nb++;}const sus=clamp(nb/NBAD_REF,SUS_MIN,1.0),conf=clamp(p.g/W_DN,0,DN_MAX)*sus;return clamp(1+GAIN_DN*sig/TILT_REF*conf,TILT_LO,TILT_HI);}
function projFromPeak(g,lp,a,cur,L,g0,fut,preHc){const pa=PEAK_AGE[g],d=LENS[L];let cl=cur||lp*frac(a,pa),prod=0;preHc=preHc||0;
  if(g0==null)g0=g; if(fut==null)fut=[[g,1]];
  for(let k=0;k<18;k++){const ag=a+k;if(ag>38||frac(ag,pa)<0.42)break;let lev=lp*frac(ag,pa);if(ag<=pa)lev=Math.max(lev,cl);if(k==0)lev=Math.max(lev,cl);if(k==0&&preHc>0)lev*=(1-preHc);const base=lev+captPrem(lev);
    if(k==0)prod+=posval(base-REPL[g0])*21/Math.pow(1+d,k);
    else{let s=0;for(const fp of fut)s+=fp[1]*posval(base-REPL[fp[0]]);prod+=s*21/Math.pow(1+d,k);}}
  if(g=='KEY_FWD'||g=='KEY_DEF')prod*=1.05;const runway=clamp((25-a)/6,0,1),elite=clamp((lp/PEAK[g]-0.97)/0.30,0,1);return prod*(1+runway*elite*PMAX);}
const val=r=>r>0?r2e(SCALE*Math.pow(r,GAMMA)):0;
function pickRaw(k){const b=bandof(k);let s=0;const m=MIX[String(b)];for(const gg in m){if(m[gg]>0)s+=m[gg]*projFromPeak(gg,basepkC(gg,k),19,null,'bal');}return s*(1-(BUST_BAND[String(b)]!=null?BUST_BAND[String(b)]:0.15));}
function peakvalC(c){return c.pkbest!=null?val(projFromPeak(c.grp,c.pkbest,PEAK_AGE[c.grp],c.pkbest,'bal'))*c.relc:val(pickRaw(c.ep))*0.25;}
function edge(h0,h1,d0,d1){let m=((2*h0+h1)*d0-h0*d1)/(h0+h1);if(Math.sign(m)!=Math.sign(d0))m=0;else if(Math.sign(d0)!=Math.sign(d1)&&Math.abs(m)>3*Math.abs(d0))m=3*d0;return m;}
function pchip(xs,ys,xq){const n=xs.length,h=[],dl=[];for(let i=0;i<n-1;i++){h.push(xs[i+1]-xs[i]);dl.push((ys[i+1]-ys[i])/(xs[i+1]-xs[i]));}
  const m=new Array(n);m[0]=n>2?edge(h[0],h[1],dl[0],dl[1]):dl[0];m[n-1]=n>2?edge(h[n-2],h[n-3],dl[n-2],dl[n-3]):dl[n-2];
  for(let i=1;i<n-1;i++){if(dl[i-1]*dl[i]<=0)m[i]=0;else{const w1=2*h[i]+h[i-1],w2=h[i]+2*h[i-1];m[i]=(w1+w2)/(w1/dl[i-1]+w2/dl[i]);}}
  return xq.map(x=>{let i=0;while(i<n-2&&x>xs[i+1])i++;const t=(x-xs[i])/h[i],t2=t*t,t3=t2*t;return (2*t3-3*t2+1)*ys[i]+(t3-2*t2+t)*h[i]*m[i]+(-2*t3+3*t2)*ys[i+1]+(t3-t2)*h[i]*m[i+1];});}
function buildPVC(alpha){const pv=cohort.map(c=>({ep:c.ep,v:peakvalC(c)}));const raw=new Array(99).fill(NaN);
  for(let k=1;k<=99;k++){const vs=pv.filter(x=>Math.abs(x.ep-k)<=4).map(x=>x.v);if(vs.length){const mm=vs.map(v=>Math.pow(Math.max(v,1),alpha)).reduce((a,b)=>a+b,0)/vs.length;raw[k-1]=Math.pow(mm,1/alpha);}}
  for(let i=0;i<99;i++)if(isNaN(raw[i]))raw[i]=i?raw[i-1]:5000;
  for(let i=0;i<99;i++)raw[i]=r2e(raw[i]);
  let vv=raw.map(v=>-v),idx=raw.map((_,i)=>[i]),i=0;
  while(i<vv.length-1){if(vv[i]>vv[i+1]+1e-9){const nv=(vv[i]*idx[i].length+vv[i+1]*idx[i+1].length)/(idx[i].length+idx[i+1].length);vv[i]=nv;idx[i]=idx[i].concat(idx[i+1]);vv.splice(i+1,1);idx.splice(i+1,1);i=Math.max(0,i-1);}else i++;}
  const iso=new Array(99);vv.forEach((v,j)=>{for(const t of idx[j])iso[t]=-v;});
  let kx=[],ky=[];i=0;while(i<99){let j=i;while(j+1<99&&Math.abs(iso[j+1]-iso[i])<1e-6)j++;kx.push((i+j)/2);ky.push(iso[i]);i=j+1;}
  if(kx[0]>0){kx.unshift(0);ky.unshift(iso[0]);}if(kx[kx.length-1]<98){kx.push(98);ky.push(iso[98]);}
  const sm=pchip(kx,ky,Array.from({length:99},(_,i)=>i));for(let i=1;i<99;i++)sm[i]=Math.min(sm[i],sm[i-1]-1);
  const o={};for(let k=1;k<=99;k++)o[k]=Math.max(210,r2e(sm[k-1]*CURVE_H));return o;}
function prodFloor(p){if(p.ln==null)return 0;const g=grpOf(p),a=p.age,pa=PEAK_AGE[g],cur=p.ln,d=LENS['bal'];let H=clamp((40-a)/3,1,3),prod=0,k=0;
  while(k<H){const ag=a+k,wt=Math.min(1,H-k);let lev=cur*Math.min(1,frac(ag,pa)/Math.max(frac(a,pa),1e-6));if(k==0&&(p.b2hc||0)>0)lev*=(1-p.b2hc);prod+=wt*posval(lev+captPrem(lev)-REPL[g])*21/Math.pow(1+d,k);k++;}return val(prod);}
function relC(g,ep,pn){return clamp(Math.pow(pn/Math.max(basepkC(g,ep),40),2.2),0.40,3.0);}
const playsig=cg=>1-Math.exp(-cg/6.0);
function debutFactor(p){const ep=p.ep,s=2026-p.yr,cg=p.cg;
  const elapsed=clamp((s-1)+SEASON_PROG,0,1.6),ref=0.58*Math.min(1,elapsed),sig=playsig(cg)-ref;
  const Apos=(0.05+0.30*Math.exp(-Math.pow((ep-34)/24.0,2)))*clamp(ep/14.0,0.30,1.0)*clamp((22-cg)/22.0,0.0,1.0);
  const Aneg=0.16+0.12*Math.exp(-Math.pow((ep-34)/30.0,2));
  return clamp(1+(sig>=0?Apos:Aneg)*sig,0.78,1.28);}
function trackSlip(dlt,games){if(dlt==null||dlt>=0)return 1.0;
  const raw=clamp(1+dlt/SLIP_REF,SLIP_CAP,1.0),conf=clamp(games/SLIP_CONF,0,1);return 1-conf*(1-raw);}
const LTILT=0.30,LTSPREAD=6.0;
function lensTilt(p,lens){if(lens==='bal')return 1.0;const g=grpOf(p);const phase=clamp((p.age-PEAK_AGE[g])/LTSPREAD,-1,1);return lens==='now'?clamp(1+LTILT*phase,0.7,1.3):clamp(1-LTILT*phase,0.7,1.3);}
function valuePlayer(p,lens){const ep=p.ep,decu=p.losd,df=debutFactor(p),ped=PVC[Math.min(ep,70)];
  const unpl_eq=ped*decu*df;
  const P=(p.P==null?1:p.P);                                    // establishment prob (frozen draft-cohort property); 1.0 = established/inert
  if(p.pedOnly)return r2e(unpl_eq*lensTilt(p,lens));            // genuine pre-debut prospect (or _pedonly): pure pedigree, P inert by design
  if(p.lnNull)return r2e(unpl_eq*P*lensTilt(p,lens));           // 0-game in-window: gated by P (matches Python unpl_eq*Pz)
  const gf=p.ovr||p.gf||p.grp, g0=p.ovr||p.grp, fut=p.ovr?[[p.ovr,1]]:(p.fut||[[gf,1]]);
  const prod_v=val(projFromPeak(gf,p.pn,p.age,p.ln,'bal',g0,fut,p.b2hc||0))*p.surv;
  let relative=clamp(relC(gf,ep,p.pn)*outTilt(p,gf,ep),0.40,3.0);
  if((gf==='RUC'||gf==='KEY_FWD'||gf==='KEY_DEF')&&p.age<=22&&relative<1.0){   // v3.4 relative-floor (young key-pos), now mirrored in JS
    const sc=({1:1.0,2:0.8,3:0.5,4:0.2})[2026-p.yr]||0; relative=relative+sc*(1.0-relative);}
  const pedestal=ped*relative*p.surv*Math.min(p.pedDecay,P);    // GATE 1: pedigree pedestal decay floored by P
  const pf=prodFloor(p); let prod_full=Math.max(prod_v,pf);
  if(P<1){                                                      // GATE 2: production-gating (PROD_GATE='blenddemo')
    const cred=Math.min(1,p.g/50), gfloor=Math.max(pedestal,cred*pf+(1-cred)*pedestal);
    const fully=P*prod_full+(1-P)*gfloor; prod_full=prod_full/3+2*fully/3;
  }
  let res=Math.max(prod_full,pedestal);
  if(p.brodieBase&&grpOf(p)!=='RUC')res*=0.5;                   // Brodie role-reliability cut (RUC exemption applied live on toggle)
  return r2e(res*lensTilt(p,lens)*(p.cvx||1));}
const atDefault=()=>CAPT_THRESH===CAPT0&&ALPHA===ALPHA0&&CURVE_H===CURVE_H0&&Object.keys(REPL0).every(k=>REPL[k]===REPL0[k]);
function recompute(lens){
  if(atDefault()){SCALE=SCALE0;PVC={};for(let k=1;k<=99;k++)PVC[k]=PVC0[String(k)];}
  else{const raws=players.filter(p=>!p.unpl&&!p.del).map(p=>projFromPeak(p.gf||p.grp,p.ps,p.age,p.lns,'bal',p.grp,p.fut||[[p.gf||p.grp,1]])).sort((a,b)=>a-b);
    const rkp=0.99*(raws.length-1),lo=Math.floor(rkp);SCALE=7000/Math.pow(raws[lo]+(rkp-lo)*((raws[lo+1]||raws[lo])-raws[lo]),GAMMA);
    PVC=buildPVC(ALPHA);}
  players.forEach(p=>{p.val=p.del?0:(p.v!=null?p.v:valuePlayer(p,lens));});}   // RELEASE: show baked redesign p.v; legacy valuePlayer is fallback only (per-position/lens/dial revaluation = v2)
/* ===== END ENGINE ===== */
