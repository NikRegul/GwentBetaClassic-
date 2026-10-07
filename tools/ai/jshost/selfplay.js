'use strict';
// Headless self-play of the transpiled WS battle engine (port of tools/ai/host/SelfPlay.cs).
const fs = require('fs'), path = require('path'), vm = require('vm');
function load(rulesPath) {
  const src = fs.readFileSync(path.join(__dirname, 'runtime.js'), 'utf8') + '\n' + fs.readFileSync(rulesPath, 'utf8') + '\n' +
    fs.readFileSync(path.join(__dirname, 'harness.js'), 'utf8');
  const ctx = { console };
  vm.createContext(ctx);
  vm.runInContext(src, ctx, { filename: 'bundle.js' });
  return ctx.__harness;
}
module.exports = { load };
