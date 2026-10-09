'use strict';
// Host runtime for transpiled WitcherScript (see tools/ai/ws2js.py).
const AP = Array.prototype;
AP.Size = function () { return this.length; };
AP.PushBack = function (v) { this.push(v); };
AP.Clear = function () { this.length = 0; };
AP.Erase = function (i) { this.splice(i, 1); };
AP.EraseFast = AP.Erase;
AP.Insert = function (i, v) { this.splice(i, 0, v); };
AP.Contains = function (v) { return this.indexOf(v) >= 0; };
AP.FindFirst = function (v) { return this.indexOf(v); };
AP.PopBack = function () { return this.pop(); };
AP.Last = function () { return this[this.length - 1]; };
AP.Remove = function (v) { const i = this.indexOf(v); if (i >= 0) { this.splice(i, 1); return true; } return false; };
AP.Grow = function (n) { const s = this.length; for (let i = 0; i < n; i++) this.push(0); return s; };
AP.Resize = function (n, fill) { while (this.length < n) this.push(fill ? fill() : 0); this.length = n; };
class IScriptable {}
function __cp(v) {
  if (v === null || v === undefined) return v;
  if (Array.isArray(v)) { const r = new Array(v.length); for (let i = 0; i < v.length; i++) r[i] = __cp(v[i]); return r; }
  if (typeof v === 'object' && v.__copy) return v.__copy();
  return v;
}
const __cpu = __cp;
function __idiv(a, b) { if (b === 0) throw new Error('integer division by zero'); return Math.trunc(a / b); }
function __cast(v, cls) { return v instanceof cls ? v : null; }
const Host = { random: null, log: null, policy: null, strength: [1, 1], seat: 2 };
function Max(a, b) { return a > b ? a : b; }
function Min(a, b) { return a < b ? a : b; }
function Abs(a) { return a < 0 ? -a : a; }
function FloorF(a) { return Math.floor(a); }
function Clamp(a, lo, hi) { return a < lo ? lo : a > hi ? hi : a; }
function RandRange(n) { return n > 0 ? Math.floor(Host.random() * n) : 0; }
function LogChannel(channel, message) { if (Host.log) Host.log(message); }
function BetaGwentAITrainingWeight(preset, index) { return Host.policy ? Host.policy(preset, index) : typeof __snapshotTrainingWeight === 'function' ? __snapshotTrainingWeight(preset,index) : 0; }
function BetaGwentAIChooseOrdinaryPreset() { throw new Error('self play must supply an explicit preset'); }
function BetaGwentAIRandomPreset() { return BetaGwentAIChooseOrdinaryPreset(); }
function BetaGwentAIStrength() { return Host.strength; }
const __tuneDefaults = { 0: 6, 1: 0, 2: 0, 3: 0, 4: 1, 5: 10, 6: 3, 7: 6, 8: 5, 9: 4, 10: 3, 11: 10, 12: 10, 13: 5, 14: 2, 15: 12, 16: 8, 17: 50, 18: 18, 19: 0, 20: 26, 21: 25, 22: 10, 23: 2, 24: 3, 25: 85, 26: 50, 27: 50, 28: 12, 29: 6, 30: 2, 31: 2, 32: 100 };
function BetaGwentAITune(i) { if (Host.reads) Host.reads[i] = 1; const t = Host.tunes && Host.tunes[Host.seatIndex]; if (t && t[i] !== undefined) return t[i]; return __tuneDefaults[i] !== undefined ? __tuneDefaults[i] : 0; }
let __simDepthHost = 0;
function BetaGwentLog(message) { if (__simDepthHost === 0 && Host.log) Host.log(message); }
function BetaGwentAISimEnter() { __simDepthHost++; }
function BetaGwentAISimLeave() { __simDepthHost = Math.max(0, __simDepthHost - 1); }
