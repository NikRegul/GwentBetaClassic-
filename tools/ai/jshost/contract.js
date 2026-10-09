'use strict';
const SPACE = { 0: [0, 14, 2], 1: [0, 12, 4], 2: [0, 1, 1], 3: [0, 1, 1], 4: [0, 1, 1], 6: [1, 6, 1], 7: [3, 9, 1], 8: [0, 10, 1], 9: [2, 6, 1], 10: [0, 8, 1], 11: [0, 20, 2], 12: [0, 20, 2], 13: [0, 10, 1], 14: [0, 6, 1], 15: [0, 20, 2], 16: [0, 16, 2], 17: [0, 100, 10], 18: [10, 30, 2], 19: [0, 8, 1], 20: [14, 34, 2], 21: [14, 34, 2], 22: [4, 20, 2], 23: [1, 4, 1], 24: [2, 6, 1], 25: [60, 95, 5], 26: [0, 100, 10], 27: [0, 100, 10], 28: [0, 24, 2], 29: [0, 12, 2], 30: [0, 6, 1], 31: [0, 4, 1], 32: [0, 200, 25] };
const fs=require('fs');
function atomic(file,value){const tmp=file+'.tmp';fs.writeFileSync(tmp,JSON.stringify(value,null,2));fs.renameSync(tmp,file);}
function validate(tunes){for(const [key,value] of Object.entries(tunes)){const range=SPACE[key];if(!range||!Number.isInteger(value)||value<range[0]||value>range[1])throw Error('Invalid tune '+key);}return tunes;}
module.exports={SPACE,atomic,validate};
