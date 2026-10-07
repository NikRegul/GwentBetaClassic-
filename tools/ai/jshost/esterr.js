const vm = require('vm'), fs = require('fs'), path = require('path');
const rules = process.argv[2], games = +process.argv[3] || 30;
const src = fs.readFileSync(path.join(__dirname, 'runtime.js'), 'utf8') + '\n' + fs.readFileSync(rules, 'utf8') + '\n' + fs.readFileSync(path.join(__dirname, 'harness.js'), 'utf8') + `
var __E=[];const __oPlay=CBetaGwentDuelSession.prototype.Play;
CBetaGwentDuelSession.prototype.Play=function(side,id,row){
 if(side!==2)return __oPlay.call(this,side,id,row);
 const c=this.FindCard(id);const d=c.Definition();const est=this.AiCardTempo(c,true,this.BestVranAnchor(2),this.AiPublicClearRisk());
 const before=this.Score(2)-this.Score(1);const r=__oPlay.call(this,side,id,row);
 // resolve AI-side pending choices like the harness does
 let guard=0;while(this.IsPending()&&!this.mulligan&&guard++<10){if(!__pending(this))break;}
 const after=this.Score(2)-this.Score(1);__E.push({t:d.title,id:d.header.templateId,est,act:after-before});return r;};
globalThis.__E=__E;`;
const ctx = { console }; vm.createContext(ctx); vm.runInContext(src, ctx);
const h = ctx.__harness;
for (let i = 0; i < games; i++) h.play(54 + (i % 40), 54 + ((i * 7 + 3) % 40), 9000 + i, 1, 1);
const E = ctx.__E; let abs = 0, big = 0; const by = {};
for (const e of E) { const d = e.est - e.act; abs += Math.abs(d); if (Math.abs(d) >= 5) big++; const k = e.t + ' ' + e.id; by[k] = by[k] || [0, 0, 0]; by[k][0]++; by[k][1] += e.est; by[k][2] += e.act; }
console.log('plays', E.length, 'mean abs err', (abs / E.length).toFixed(2), 'err>=5', big);
const worst = Object.entries(by).map(([k, v]) => [k, v[0], (v[1] / v[0]).toFixed(1), (v[2] / v[0]).toFixed(1), Math.abs(v[1] - v[2]) / v[0]]).sort((a, b) => b[4] * Math.sqrt(b[1]) - a[4] * Math.sqrt(a[1])).slice(0, 30);
for (const w of worst) console.log(w.slice(0, 4).join('  est/act '));
