export const W=6,H=12,CRAB=7,PUFFER=8,JELLY=9;
export const LEVELS=[
 {name:'Harbor',colors:5,target:850,moves:30,leak:2,puffer:false,crabs:false,jelly:false},
 {name:'Open water',colors:6,target:1000,moves:30,leak:2.3,puffer:false,crabs:false,jelly:false},
 {name:'Crosscurrent',colors:6,target:1200,moves:32,leak:2.6,puffer:true,crabs:false,jelly:false},
 {name:'Rough seas',colors:7,target:1400,moves:34,leak:2.8,puffer:true,crabs:false,jelly:false},
 {name:'Crab country',colors:7,target:1700,moves:36,leak:3,puffer:true,crabs:true,jelly:false},
 {name:'Deep water',colors:7,target:2000,moves:36,leak:3.2,puffer:true,crabs:true,jelly:true}
];
export function groups(b){const out=[];for(let y=0;y<H;y++)for(let x=0;x<W;x++){let i=y*W+x,t=b[i];if(t<0||t>=7)continue;if(x===0||b[i-1]!==t){let run=[];for(let k=x;k<W&&b[y*W+k]===t;k++)run.push(y*W+k);if(run.length>=3)out.push(run);}if(y===0||b[i-W]!==t){let run=[];for(let k=y;k<H&&b[k*W+x]===t;k++)run.push(k*W+x);if(run.length>=3)out.push(run);}}return out;}
export const matches=b=>[...new Set(groups(b).flat())];
export function matchScore(g,cascade=false){if(!g.length)return 0;const base=g.reduce((s,r)=>s+30+(r.length-3)*20,0);return Math.round(base*[0,1,3,5,7][Math.min(4,g.length)]*(cascade?.25:1));}
export function comboName(g){if(g.length>=4)return g.some(r=>r.length>=5)?'Vegas!':'Sea Donkey!';if(g.length===3)return 'Bingo!';if(g.length===2)return g.some(r=>r.length>=5)?'Yarrr!':g.every(r=>r.length>=4)?'Har!':'Arrr!';if(g[0]?.length>=5)return 'Great!';if(g[0]?.length===4)return 'Good!';return '';}
export function randomTile(level){let c=LEVELS[level],r=Math.random();if(c.crabs&&r<.026)return CRAB;if(c.puffer&&r>=.026&&r<.039)return PUFFER;if(c.jelly&&r>=.039&&r<.047)return JELLY;return Math.floor(Math.random()*c.colors);}
export function fresh(level=0){let b=[],c=LEVELS[level];for(let i=0;i<W*H;i++){let choices=Array.from({length:c.colors},(_,t)=>t).filter(t=>!(i%W>1&&b[i-1]===t&&b[i-2]===t)&&!(i>=2*W&&b[i-W]===t&&b[i-2*W]===t));b.push(choices[Math.floor(Math.random()*choices.length)]);}if(c.puffer)b[49]=PUFFER;if(c.crabs){b[62]=CRAB;b[69]=CRAB;}if(c.jelly)b[58]=JELLY;return b;}
export function refill(b,cleared,level=0){let s=new Set(cleared),n=[...b];for(let x=0;x<W;x++){let col=[];for(let y=0;y<H;y++)if(!s.has(y*W+x))col.push(b[y*W+x]);while(col.length<H)col.push(randomTile(level));for(let y=0;y<H;y++)n[y*W+x]=col[y];}return n;}
export const waterHeight=water=>25+Math.max(0,Math.min(100,water))*.5;
export function releasedCrabs(b,water){let line=H*(1-waterHeight(water)/100);return b.flatMap((v,i)=>v===CRAB&&Math.floor(i/W)+.5<=line?[i]:[]);}
export function specialClear(b,i,j){let a=b[i],c=b[j];if(a===CRAB||c===CRAB)return {blocked:true,cells:[]};if((a===PUFFER||c===PUFFER)&&a!==c){let p=a===PUFFER?i:j,x=p%W,y=Math.floor(p/W),cells=[];for(let yy=Math.max(0,y-1);yy<=Math.min(H-1,y+1);yy++)for(let xx=Math.max(0,x-1);xx<=Math.min(W-1,x+1);xx++)cells.push(yy*W+xx);return {kind:'puffer',cells};}if((a===JELLY&&c<7)||(c===JELLY&&a<7)){let color=a===JELLY?c:a;return {kind:'jelly',cells:b.flatMap((v,k)=>v===color||k===(a===JELLY?i:j)?[k]:[])};}return {cells:[]};}
