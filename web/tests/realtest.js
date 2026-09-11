const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const N = Number(process.argv[3] || 30);
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const page = await (await b.newContext({viewport:{width:420,height:900}})).newPage();
  await page.addInitScript(() => {
    window.__created = 0;
    const real = document.createElement.bind(document);
    document.createElement = function(t){ window.__created++; return real(t); };
    window.__store = {}; const subs = [];
    function push(){ const d=Object.keys(window.__store).map(k=>({id:k,exists:true,data:()=>window.__store[k]}));
      subs.forEach(f=>f({docs:d,size:d.length,empty:!d.length,docChanges:()=>[]})); }
    function mkDoc(p){ const sg=p.split('/'), top=sg.length===2, id=sg[1];
      return { set:(d)=>{if(top){window.__store[id]={...d};push();}return Promise.resolve();},
               update:(d)=>{if(top){window.__store[id]={...window.__store[id],...d};push();}return Promise.resolve();},
               delete:()=>Promise.resolve(), collection:(s)=>mkCol(p+'/'+s) }; }
    function mkCol(p){ const q={orderBy:()=>q,limit:()=>q,
      onSnapshot:(n)=>{if(p==='uploads'){subs.push(n);setTimeout(push,10);}return()=>{};},doc:(i)=>mkDoc(p+'/'+i)};return q;}
    window.claude={use:(n)=>Promise.resolve(n==='db'?{collection:mkCol,doc:mkDoc}
      :n==='assets'?{list:()=>Promise.resolve({assets:[],usage:{files:0,bytes:0,maxFiles:999,maxBytes:1e9}}),
                     upload:()=>Promise.resolve({id:'c'.repeat(32),url:'',sizeBytes:1,contentType:'image/jpeg'}),
                     delete:()=>Promise.resolve({deleted:true})}:null)};
  });
  await page.goto('file://' + process.argv[2]);
  await page.waitForSelector('#btn-pick:not([disabled])');
  const files = Array.from({length:N},(_,i)=>`/tmp/claude-0/-home-user-Restaurant/d31cf2df-6db6-599d-8498-c3368f191265/scratchpad/bigs/photo_${i+1}.jpg`);
  const t = Date.now();
  await page.setInputFiles('#picker', files);
  let done = 0;
  try {
    await page.waitForFunction((n)=>Object.values(window.__store).filter(r=>r.status==='stored').length>=n,
                               N, {timeout:420000, polling:500});
    done = N;
  } catch(e){
    done = await page.evaluate(()=>Object.values(window.__store).filter(r=>r.status==='stored').length);
  }
  const secs=(Date.now()-t)/1000;
  const st = await page.evaluate(()=>{
    const v=Object.values(window.__store);
    return { stored:v.filter(r=>r.status==='stored').length, err:v.filter(r=>r.status==='error').length,
             chunks:v.reduce((a,r)=>a+(r.chunks||0),0),
             heap: performance.memory?Math.round(performance.memory.usedJSHeapSize/1048576):null,
             created: window.__created, li: document.querySelectorAll('#docs li').length };
  });
  console.log(`  مكتمل      : ${st.stored}/${N}   (فشل ${st.err})`);
  console.log(`  الزمن      : ${secs.toFixed(1)} ث  =  ${(secs/Math.max(st.stored,1)).toFixed(2)} ث/صورة`);
  console.log(`  أجزاء      : ${st.chunks}  (${(st.chunks/Math.max(st.stored,1)).toFixed(1)} لكل صورة)`);
  console.log(`  عناصر DOM  : ${st.created.toLocaleString()}   صفوف: ${st.li}`);
  console.log(`  كومة JS    : ${st.heap} م.ب`);
  console.log(`  توقّع 139  : ${((secs/Math.max(st.stored,1))*139/60).toFixed(1)} دقيقة`);
  await b.close();
})();
