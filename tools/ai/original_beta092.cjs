/* Launch the UNMODIFIED original C# Beta backend from the JS test environment.
 * This is not a JS translation or a mixed-policy comparison yet.
 */
'use strict';
const fs = require('fs');
const path = require('path');
const {spawn} = require('child_process');
const root = path.resolve(__dirname, '../..');
const draft = path.join(root, 'BetaGwent/drafts/day-iteration-20261023/beta-original-js');
const host = path.join(draft, 'native-host/bin/Release/net6.0/OriginalBetaHost.dll');
const args = process.argv.slice(2);
if (args.some(a => a !== '--smoke')) throw new Error('Only --smoke is supported; no cross-policy comparison implemented');
for (const file of [host, path.join(draft, 'Settings.xml')])
  if (!fs.existsSync(file)) throw new Error('Missing original host input: ' + file);
const child = spawn('dotnet', [host,
  path.join(root, 'Gwent 0.9.24.3.432/Gwent_Data/Managed'),
  path.join(root, 'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/data_definitions'), ...args],
  {cwd: root, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe']});
let pending = '', final = null;
child.stdout.setEncoding('utf8');
child.stdout.on('data', chunk => {
  pending += chunk;
  for (;;) {
    const end = pending.indexOf('\n');
    if (end < 0) break;
    const line = pending.slice(0, end).trim(); pending = pending.slice(end + 1);
    if (!line) continue;
    try {
      const record = JSON.parse(line);
      if (record.stage === 'original-game-progress' && record.state === 512) final = record;
      process.stdout.write(JSON.stringify(record) + '\n');
    } catch (error) {
      process.stderr.write('Invalid native JSON: ' + line + '\n');
      child.kill(); process.exitCode = 1;
    }
  }
});
child.stderr.pipe(process.stderr);
const timer = setTimeout(() => {
  process.stderr.write('Original backend exceeded195s wall limit\n'); child.kill(); process.exitCode = 1;
}, 195000);
child.on('error', error => { clearTimeout(timer); console.error(error); process.exitCode = 1; });
child.on('close', code => {
  clearTimeout(timer);
  if (pending.trim()) { console.error('Incomplete native JSON'); process.exitCode = 1; }
  if (code !== 0 || (args.includes('--smoke') && (!final || final.loggerErrors !== 0))) {
    console.error('Original backend incomplete or failed; exit=' + code); process.exitCode = 1;
  }
});
