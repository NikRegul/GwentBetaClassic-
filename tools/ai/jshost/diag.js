// Diagnostics of AI decisions: weather placements, round economy.
const vm = require('vm'), fs = require('fs'), path = require('path');
const rules = process.argv[2], games = +process.argv[3] || 40;
const src = fs.readFileSync(path.join(__dirname, 'runtime.js'), 'utf8') + '\n' + fs.readFileSync(rules, 'utf8') + '\n' + fs.readFileSync(path.join(__dirname, 'harness.js'), 'utf8') + `
var __stats={plays:0,intoHazard:0,hazardAvoidable:0,examples:[]};
const __origPlay=CBetaGwentDuelSession.prototype.Play;
CBetaGwentDuelSession.prototype.Play=function(side,id,row){
  if(side===2&&!this.__inner){const c=this.FindCard(id);const d=c?c.Definition():null;
    if(d&&d.header.typeMask===4&&!BetaGwentDuelSpying(d.header.templateId)){__stats.plays++;
      const dmg=this.weather.Hazard?this.weather.Hazard(2,row):this.weather.Damage(2,row);
      if(dmg>0){__stats.intoHazard++;let alt=false;for(let r=1;r<=4;r*=2){if(r!==row&&this.CountLocation(2,r)<9&&this.weather.Hazard(2,r)===0)alt=true;}
        if(alt){__stats.hazardAvoidable++;if(__stats.examples.length<15)__stats.examples.push(d.title+' '+d.header.templateId+' row='+row+' dmg='+dmg+' weatherProfile='+this.weatherProfile+' preset='+this.presetTwo);}}}}
  return __origPlay.call(this,side,id,row);};
globalThis.__stats=__stats;`;
const ctx = { console }; vm.createContext(ctx); vm.runInContext(src, ctx);
const h = ctx.__harness; let n = 0;
for (let i = 0; i < games; i++) { const a = 54 + (i % 40), b = 54 + ((i * 7 + 3) % 40); h.play(a, b, 1000 + i, +(process.argv[4]||1), +(process.argv[4]||1)); }
console.log(JSON.stringify(ctx.__stats, null, 1));
