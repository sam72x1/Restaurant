const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const SIZE = fs.statSync('/tmp/claude-0/-home-user-Restaurant/d31cf2df-6db6-599d-8498-c3368f191265/scratchpad/bigs/photo_1.jpg').size;
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const page = await (await b.newContext({viewport:{width:420,height:900}})).newPage();
  await page.addInitScript((size) => {
    // نزرع صفًا فاشلًا لنفس الملف الذي سنعيد رفعه
    const store = { 'old-failed': { name:'photo_1.jpg', category:'supplier', note:'',
      mime:'image/jpeg', originalSize:size, createdAt:'2026-09-11T10:00:00.000Z',
      status:'error', chunks:0, error:'timeout' } };
    window.__store = store; window.__deleted = [];
    const subs=[];
    function push(){ const d=Object.keys(store).map(k=>({id:k,exists:true,data:()=>store[k]}));
      d.sort((a,b)=>(store[b.id].createdAt||'').localeCompare(store[a.id].createdAt||''));
      subs.forEach(f=>f({docs:d,size:d.length,empty:!d.length,docChanges:()=>[]})); }
    function mkDoc(p){ const sg=p.split('/'), top=sg.length===2 && sg[0]==='uploads', id=sg[1];
      return { set:(d)=>{ if(top){store[id]={...d};push();} return Promise.resolve(); },
               update:(d)=>{ if(top){store[id]={...store[id],...d};push();} return Promise.resolve(); },
               delete:()=>{ if(top){ window.__deleted.push(id); delete store[id]; push(); } return Promise.resolve(); },
               collection:(x)=>mkCol(p+'/'+x) }; }
    function mkCol(p){ const q={orderBy:()=>q,limit:()=>q,
      onSnapshot:(n)=>{if(p==='uploads'){subs.push(n);setTimeout(push,10);}return()=>{};},doc:(i)=>mkDoc(p+'/'+i)};return q;}
    window.claude={use:(n)=>Promise.resolve(n==='db'?{collection:mkCol,doc:mkDoc}
      :n==='assets'?{list:()=>Promise.resolve({assets:[],usage:{files:0,bytes:0,maxFiles:9,maxBytes:9e8}}),
                     upload:()=>Promise.resolve({id:'e'.repeat(32),url:'',sizeBytes:1,contentType:'image/jpeg'}),
                     delete:()=>Promise.resolve({deleted:true})}:null)};
  }, SIZE);
  await page.goto('file:///home/user/Restaurant/web/upload-portal.html');
  await page.waitForSelector('#btn-pick:not([disabled])');
  await page.waitForTimeout(700);

  const shown = await page.evaluate(()=>{ const r=document.getElementById('retry');
    return { hidden:r.hidden, count:document.getElementById('retry-count').textContent,
             names:document.getElementById('retry-names').textContent }; });
  console.log('١) لوحة إعادة المحاولة ظاهرة؟', shown.hidden ? '❌ لا' : '✅ نعم');
  console.log('   النص :', shown.count);
  console.log('   الملفات:', shown.names);

  await page.setInputFiles('#picker', '/tmp/claude-0/-home-user-Restaurant/d31cf2df-6db6-599d-8498-c3368f191265/scratchpad/bigs/photo_1.jpg');
  await page.waitForFunction(()=>Object.values(window.__store).some(r=>r.status==='stored'), null, {timeout:60000});
  await page.waitForTimeout(3500);

  const after = await page.evaluate(()=>({ del:window.__deleted, keys:Object.keys(window.__store),
    statuses:Object.values(window.__store).map(r=>r.status),
    retryHidden:document.getElementById('retry').hidden }));
  console.log('٢) أُعيد الرفع بنجاح؟', after.statuses.includes('stored') ? '✅ نعم' : '❌ لا');
  console.log('٣) حُذف الصف الفاشل تلقائيًا؟', after.del.includes('old-failed') ? '✅ نعم' : '❌ لا');
  console.log('٤) اختفت اللوحة بعد الإصلاح؟', after.retryHidden ? '✅ نعم' : '❌ لا');
  console.log('   المتبقي في المخزن:', after.keys.length, 'صف ·', after.statuses.join(','));
  await b.close();
})();
