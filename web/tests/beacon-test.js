const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const page = await (await b.newContext({viewport:{width:420,height:900}})).newPage();
  await page.addInitScript(() => {
    window.__diag = {}; const store={}, subs=[];
    function push(){ const d=Object.keys(store).map(k=>({id:k,exists:true,data:()=>store[k]}));
      subs.forEach(f=>f({docs:d,size:d.length,empty:!d.length,docChanges:()=>[]})); }
    function mkDoc(p){ const sg=p.split('/'), top=sg.length===2, id=sg[1], col=sg[0];
      return { set:(d)=>{ if(col==='diag'){window.__diag[id]={...d};}
                          else if(top){store[id]={...d};push();} return Promise.resolve(); },
               update:(d)=>{if(top&&col==='uploads'){store[id]={...store[id],...d};push();}return Promise.resolve();},
               delete:()=>Promise.resolve(), collection:(x)=>mkCol(p+'/'+x) }; }
    function mkCol(p){ const q={orderBy:()=>q,limit:()=>q,
      onSnapshot:(n)=>{if(p==='uploads'){subs.push(n);setTimeout(push,10);}return()=>{};},doc:(i)=>mkDoc(p+'/'+i)};return q;}
    window.claude={use:(n)=>Promise.resolve(n==='db'?{collection:mkCol,doc:mkDoc}
      :n==='assets'?{list:()=>Promise.resolve({assets:[],usage:{files:0,bytes:0,maxFiles:9,maxBytes:9e8}}),
                     upload:()=>Promise.resolve({id:'d'.repeat(32),url:'',sizeBytes:1,contentType:'image/jpeg'}),
                     delete:()=>Promise.resolve({deleted:true})}:null)};
  });
  await page.goto('file:///home/user/Restaurant/web/upload-portal.html');
  await page.waitForSelector('#btn-pick:not([disabled])');
  await page.setInputFiles('#picker', ['/tmp/claude-0/-home-user-Restaurant/d31cf2df-6db6-599d-8498-c3368f191265/scratchpad/bigs/photo_1.jpg',
                                       '/tmp/claude-0/-home-user-Restaurant/d31cf2df-6db6-599d-8498-c3368f191265/scratchpad/bigs/photo_2.jpg']);
  await page.waitForTimeout(9000);
  const d = await page.evaluate(()=>window.__diag);
  const k = Object.keys(d)[0];
  if(!k){ console.log('❌ لم تُكتب أي تيليمتري'); } else {
    console.log('✅ وثيقة التشخيص:', k, '| المتصفح:', (d[k].ua||'').slice(0,48));
    console.log('--- الأحداث المسجّلة ---');
    console.log(d[k].events);
  }
  await b.close();
})();
