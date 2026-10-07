// Human-readable replay: node replay.js rules.js left right seed sl sr
const vm = require('vm'), fs = require('fs'), path = require('path');
const [rules, L, R, seed, sl, sr] = process.argv.slice(2);
const src = fs.readFileSync(path.join(__dirname, 'runtime.js'), 'utf8') + '\n' + fs.readFileSync(rules, 'utf8') + '\n' + fs.readFileSync(path.join(__dirname, 'harness.js'), 'utf8') + `
var __out=[];var __game=null;
function __side(g,s){return __reversed(g)?(s===1?'B':'A'):(s===1?'A':'B');}
function __board(g){const rows=[];for(const side of [1,2]){let parts=[];for(let r=1;r<=4;r*=2){const cs=[];g.GetZoneCards(side,r,{v:cs}) ;}}}
const __oPlay=CBetaGwentDuelSession.prototype.Play;
CBetaGwentDuelSession.prototype.Play=function(side,id,row){if(this.aiSimulating)return __oPlay.call(this,side,id,row);const c=this.FindCard(id);const d=c.Definition();
 if(side===2)__out.push('  '+__side(this,2)+' plays '+d.title+' ['+d.header.power+'] -> row '+row+(this.weather.Token(BetaGwentDuelSpying(d.header.templateId)?1:2,row)?' (row token '+this.weather.Token(2,row)+')':'')+'  hand '+this.CountLocation(2,8));
 const r=__oPlay.call(this,side,id,row);if(side===2)__out.push('     score A:B = '+(__reversed(this)?this.Score(2)+':'+this.Score(1):this.Score(1)+':'+this.Score(2)));return r;};
const __oPass=CBetaGwentDuelSession.prototype.Pass;
CBetaGwentDuelSession.prototype.Pass=function(side){if(side===2&&!this.aiSimulating)__out.push('  '+__side(this,2)+' PASSES at '+(__reversed(this)?this.Score(2)+':'+this.Score(1):this.Score(1)+':'+this.Score(2))+' hands A:B '+(__reversed(this)?this.CountLocation(2,8)+':'+this.CountLocation(1,8):this.CountLocation(1,8)+':'+this.CountLocation(2,8)));return __oPass.call(this,side);};
const __oLead=CBetaGwentDuelSession.prototype.UseLeader;
CBetaGwentDuelSession.prototype.UseLeader=function(side){if(side===2&&!this.aiSimulating)__out.push('  '+__side(this,2)+' uses LEADER '+this.Leader(2).Definition().title);return __oLead.call(this,side);};
const __oNext=CBetaGwentDuelSession.prototype.BeginNextRound;
CBetaGwentDuelSession.prototype.BeginNextRound=function(){if(!this.aiSimulating)__out.push('=== next round');return __oNext.call(this);};
globalThis.__out=__out;`;
const ctx = { console }; vm.createContext(ctx); vm.runInContext(src, ctx);
const h = ctx.__harness;
h.Host.log = null;
const r = h.play(+L, +R, +seed, +(sl || 1), +(sr || 1));
console.log(ctx.__out.join('\n')); console.log(JSON.stringify(r).slice(0, 400));
