'use strict';
// node tools/ai/check_bearer097.cjs <rules-snapshot> [report.json]
const F=require('./fixture_batch100096.cjs')(process.argv[2]);
const {add,snap,id,check,flush,run,begin,finish}=F;
for(const side of [1,2])run(200294,side,'bearer reacts on own soldier play',g=>{
 const bearer=add(g,200294,side,1,0,8),ally=add(g,132209,side,1,1,10);
 const knight=add(g,122308,side,8,0,4);g.mulliganReactions=true;
 check(g.Play(side,id(knight),2),"knight play");flush(g);
 const pend=!!g.IsPending(),owner=pend?g.RequestDecisionSide():0;
 check(pend&&owner===side||snap(ally).power.currentPower===12||snap(bearer).power.currentPower===10,'boost resolved or offered to owner during own play');
});
finish(process.argv[3],'Standard Bearer reacts on the owner own soldier play');
