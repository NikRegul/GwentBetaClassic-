'use strict';
const {spawn} = require('child_process');
const path = require('path');
const root = path.resolve(__dirname, '../..');

class OriginalBetaClient {
  constructor({onEvent = () => {}, onDiagnostic = () => {}} = {}) {
    this.nextId = 1; this.pending = new Map(); this.buffer = ''; this.exited = false;
    this.ready = new Promise((resolve, reject) => { this.resolveReady=resolve; this.rejectReady=reject; });
    this.child = spawn('dotnet', [path.join(root,
      'BetaGwent/drafts/day-iteration-20261023/beta-original-js/native-host/bin/Release/net6.0/OriginalBetaHost.dll'),
      path.join(root,'Gwent 0.9.24.3.432/Gwent_Data/Managed'),
      path.join(root,'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/data_definitions'), '--rpc'],
      {cwd:root,windowsHide:true,stdio:['pipe','pipe','pipe']});
    this.child.stdout.setEncoding('utf8');
    this.child.stderr.setEncoding('utf8'); this.child.stderr.on('data',onDiagnostic);
    this.child.stdout.on('data',chunk => {
      this.buffer += chunk;
      for (;;) {
        const end=this.buffer.indexOf('\n'); if(end<0) break;
        const line=this.buffer.slice(0,end).trim(); this.buffer=this.buffer.slice(end+1); if(!line) continue;
        let message;
        try { message=JSON.parse(line); } catch(e) { this.fail(new Error('Invalid native protocol JSON')); this.child.kill(); return; }
        if(message.stage) { onEvent(message); if(message.stage==='original-rpc-ready')this.resolveReady(message); continue; }
        const pending=this.pending.get(message.id);
        if(!pending) { this.fail(new Error('Unexpected response id '+message.id)); this.child.kill(); return; }
        this.pending.delete(message.id); clearTimeout(pending.timer);
        if(message.ok) pending.resolve(message.result);
        else pending.reject(Object.assign(new Error(message.error),{sequence:message.sequence,poisoned:message.poisoned}));
      }
    });
    this.child.on('error',error=>this.fail(error));
    this.child.on('exit',(code,signal)=>{
      this.exited=true;
      this.fail(new Error('Original backend exited: '+code+'/'+signal));
    });
  }
  fail(error) {
    this.rejectReady(error);
    for(const p of this.pending.values()) { clearTimeout(p.timer); p.reject(error); }
    this.pending.clear();
  }
  async request(op,fields={}) {
    await this.ready;
    if(this.exited) throw new Error('Original backend already exited');
    if(this.pending.size) throw new Error('Concurrent commands are forbidden');
    const id=this.nextId++;
    return new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>{ this.pending.delete(id); reject(new Error('Native RPC timeout')); this.child.kill(); },40000);
      this.pending.set(id,{resolve,reject,timer});
      this.child.stdin.write(JSON.stringify({...fields,id,op})+'\n');
    });
  }
  async close() {
    if(this.exited)return;
    try { await this.request('close'); } finally { this.child.stdin.end(); }
  }
  kill() { this.child.kill(); }
}
module.exports={OriginalBetaClient};
