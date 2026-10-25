/* Explicit snapshot/report selection for isolated adapter checks. Defaults keep
 * the historical P16 oracle; a different frozen snapshot must be named by the
 * caller and is validated by the runtime's complete manifest hashes. */
'use strict';
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'../..');
const draft=path.join(root,'BetaGwent/drafts/day-iteration-20261023/beta-original-js');
const rules=path.resolve(process.env.BETA_WS_RULES||path.join(root,'BetaGwent/build/release092-beta-final-20261023/rules'));
const reports=path.resolve(process.env.BETA_NATIVE_REPORT_DIR||draft);
fs.mkdirSync(reports,{recursive:true});
module.exports={root,draft,rules,reports};
