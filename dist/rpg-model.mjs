export const CREW={
lily:{name:'Lily',role:'Pump specialist',perk:'Clears remove 15% more water.',specialty:'pump',num:1,w:177,h:300},
steven:{name:'Steven',role:'Shipwright',perk:'Water enters 15% more slowly.',specialty:'seal',num:2,w:226,h:300},
hana:{name:'Hana',role:'Tide keeper',perk:'Emergency pump recharges in 9 clearing swaps, instead of 12.',specialty:'tide',num:3,w:231,h:300},
pip:{name:'Pip',role:'Pump specialist',perk:'Clears remove 15% more water.',specialty:'pump',num:4,w:211,h:300},
alex:{name:'Alex',role:'Pattern reader',perk:'Simultaneous combos do 25% more work.',specialty:'combo',num:5,w:126,h:300},
wool:{name:'Woolly',role:'Pattern reader',perk:'Simultaneous combos do 25% more work.',specialty:'combo',num:6,w:196,h:300},
moss:{name:'Moss',role:'Shipwright',perk:'Water enters 15% more slowly.',specialty:'seal',num:7,w:168,h:300},
cappy:{name:'Cappy',role:'Tide keeper',perk:'Emergency pump recharges in 9 clearing swaps, instead of 12.',specialty:'tide',num:8,w:201,h:300},
otto:{name:'Otto',role:'Shipwright',perk:'Water enters 15% more slowly.',specialty:'seal',num:9,w:232,h:300},
patch:{name:'Patch',role:'Pump specialist',perk:'Clears remove 15% more water.',specialty:'pump',num:10,w:176,h:300}
};
export const JOBS=[{id:'harbor',name:'Harbor skiff',desc:'Clear a flooded fishing boat before the hold fills.',rank:1,target:130,leak:.30,coins:40,xp:120,tier:0},{id:'ferry',name:'Coastal ferry',desc:'Keep the pumps working through a longer crossing.',rank:2,target:230,leak:.40,coins:75,xp:200,tier:1},{id:'salvage',name:'Offshore salvage',desc:'A badly flooded wreck. More symbols and special pieces.',rank:4,target:340,leak:.50,coins:120,xp:300,tier:2}];
export const rank=p=>1+Math.floor(p.xp/300);
export const difficulty=(p,j)=>Math.min(5,j.tier+Math.floor((rank(p)-1)/2));
export const specialtyOf=p=>CREW[p.character]?.specialty||'';
export const pumpFactor=p=>(1+p.upgrades.pump*.1)*(specialtyOf(p)==='pump'?1.15:1);
export const leakFactor=p=>(1-p.upgrades.seal*.1)*(specialtyOf(p)==='seal'?.85:1);
export const abilityCost=p=>specialtyOf(p)==='tide'?9:12;
export const upgradeCost=(p,k)=>60+60*p.upgrades[k];
export function cleanName(name){if(typeof name!=='string')return '';return name.replace(/[\u0000-\u001F\u007F]/g,'').replace(/\s+/g,' ').trim().slice(0,18);}
export const newProfile=()=>({version:1,character:'lily',name:'',xp:0,coins:0,completed:0,upgrades:{pump:0,seal:0},active:null,lastResult:null});
export function reward(p,success){const a=p.active;if(!a||a.status!=='running')return null;const j=JOBS.find(j=>j.id===a.job);const result={success,job:j.name,coins:success?j.coins:0,xp:success?j.xp:0,work:a.work,swaps:a.swaps,time:a.time};if(success){p.coins+=j.coins;p.xp+=j.xp;p.completed++;}p.active=null;p.lastResult=result;return result;}
export function buy(p,k){if(!['pump','seal'].includes(k)||p.active||p.upgrades[k]>=3)return false;const cost=upgradeCost(p,k);if(p.coins<cost)return false;p.coins-=cost;p.upgrades[k]++;return true;}
export function validProfile(p){return p&&p.version===1&&CREW[p.character]&&(p.name==null||typeof p.name==='string'&&p.name.length<=40)&&['xp','coins','completed'].every(k=>Number.isFinite(p[k])&&p[k]>=0)&&p.upgrades&&['pump','seal'].every(k=>Number.isInteger(p.upgrades[k])&&p.upgrades[k]>=0&&p.upgrades[k]<=3)&&(!p.active||(JOBS.some(j=>j.id===p.active.job)&&p.active.status==='running'&&Array.isArray(p.active.board)&&p.active.board.length===72&&p.active.board.every(x=>Number.isInteger(x)&&x>=0&&x<=9)&&['water','work','swaps','time','charge','level'].every(k=>Number.isFinite(p.active[k])&&p.active[k]>=0)&&p.active.level<=5&&Number.isInteger(p.active.level)));}
