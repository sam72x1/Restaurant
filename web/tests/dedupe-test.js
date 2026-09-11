const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const page = await (await b.newContext({viewport:{width:420,height:900}})).newPage();
  await page.addInitScript(() => {
    // مخزن حيّ يعكس الكتابات في اللقطات — لاختبار التخطّي فعليًا
    const store = {}, subs = [];
    window.__uploads = 0;
    function push(){ const docs = Object.keys(store).map(k=>({id:k,exists:true,data:()=>store[k]}));
                     subs.forEach(fn=>fn({docs,size:docs.length,empty:!docs.length,docChanges:()=>[]})); }
    function mkDoc(path){
      const id = path.split('/')[1];
      const isTop = path.split('/').length === 2;
      return {
        set:(d)=>{ if(isTop){ store[id]={...d}; window.__uploads++; push(); } return Promise.resolve(); },
        update:(d)=>{ if(isTop){ store[id]={...store[id],...d}; push(); } return Promise.resolve(); },
        delete:()=>{ if(isTop){ delete store[id]; push(); } return Promise.resolve(); },
        collection:(s)=>mkCol(path+'/'+s)
      };
    }
    function mkCol(path){
      const q={ orderBy:()=>q, limit:()=>q,
        onSnapshot:(next)=>{ if(path==='uploads'){ subs.push(next); setTimeout(push,20);} return ()=>{}; },
        doc:(i)=>mkDoc(path+'/'+i) };
      return q;
    }
    window.claude={use:(n)=>Promise.resolve(n==='db'?{collection:mkCol,doc:mkDoc}
      :n==='assets'?{list:()=>Promise.resolve({assets:[],usage:{files:0,bytes:0,maxFiles:500,maxBytes:104857600}}),
                     upload:()=>Promise.resolve({id:'q'.repeat(32),url:'',sizeBytes:1,contentType:'image/jpeg'}),
                     delete:()=>Promise.resolve({deleted:true})}:null)};
  });
  await page.goto('file:///home/user/Restaurant/web/upload-portal.html');
  await page.waitForSelector('#btn-pick:not([disabled])');
  await page.evaluate(()=>{document.getElementById('diag').open=true;});
  const probe = '/tmp/claude-0/-home-user-Restaurant/d31cf2df-6db6-599d-8498-c3368f191265/scratchpad/probe.png';

  await page.setInputFiles('#picker', probe);
  await page.waitForFunction(() => /✓ تم/.test(document.getElementById('diag-log').textContent), null, {timeout:30000});
  const first = await page.evaluate(()=>window.__uploads);
  console.log('الرفعة الأولى — مستندات أُنشئت:', first);

  await page.setInputFiles('#picker', probe);          // نفس الملف مرة ثانية
  await page.waitForTimeout(2500);
  const second = await page.evaluate(()=>window.__uploads);
  const banner = await page.evaluate(()=>{const b=document.getElementById('banner');return b.hidden?null:b.textContent;});
  console.log('بعد إعادة اختيار نفس الملف — مستندات أُنشئت:', second);
  console.log('هل تُخطّي التكرار؟', second === first ? '✅ نعم' : '❌ لا، رفعه مرة ثانية');
  console.log('الرسالة:', banner);
  await b.close();
})();
