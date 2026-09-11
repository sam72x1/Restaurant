const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await b.newContext({ viewport:{width:420,height:900} });
  const page = await ctx.newPage();
  page.on('console', m => { if(m.type()==='error') console.log('PAGE ERROR:', m.text()); });

  await page.addInitScript(() => {
    window.__writes = [];
    const rec = (op, path, data) => { window.__writes.push({op, path, keys:data?Object.keys(data):null, size:data&&data.b64?data.b64.length:null}); return Promise.resolve(); };
    function makeDoc(path){
      return { set:(d)=>rec('set',path,d), update:(d)=>rec('update',path,d), delete:()=>rec('del',path),
               collection:(sub)=>makeCol(path+'/'+sub) };
    }
    function makeCol(path){
      const q = { orderBy(){return q;}, limit(){return q;},
        onSnapshot(next){ setTimeout(()=>next({docs:[],size:0,empty:true,docChanges:()=>[]}),30); return ()=>{}; },
        doc:(id)=>makeDoc(path+'/'+(id||'auto')) };
      return q;
    }
    window.claude = { use:(n)=> Promise.resolve(
      n==='db' ? { collection:makeCol, doc:makeDoc }
    : n==='assets' ? { list:()=>Promise.resolve({assets:[],usage:{files:0,bytes:0,maxFiles:200,maxBytes:104857600}}),
                       upload:(blob,opts)=>{ window.__writes.push({op:'asset', type:(opts&&opts.type)||blob.type, bytes:blob.size});
                                             return Promise.resolve({id:'x'.repeat(32), url:'/_blob/'+'x'.repeat(32), sizeBytes:blob.size, contentType:'image/jpeg'}); },
                       delete:()=>Promise.resolve({deleted:true}) }
    : null) };
  });

  await page.goto('file:///home/user/Restaurant/web/upload-portal.html');
  await page.waitForSelector('#btn-pick:not([disabled])', { timeout: 8000 });
  await page.evaluate(()=>{document.getElementById('diag').open=true;});
  console.log('✓ الأزرار فُعّلت بعد اتصال التخزين');

  await page.setInputFiles('#picker', '/tmp/claude-0/-home-user-Restaurant/d31cf2df-6db6-599d-8498-c3368f191265/scratchpad/probe.png');
  await page.waitForFunction(() => window.__writes.some(w => w.op==='update' && w.keys && w.keys.indexOf('chunks')!==-1), { timeout: 20000 });

  const w = await page.evaluate(() => window.__writes);
  console.log('\n--- عمليات الكتابة المسجَّلة ---');
  w.forEach(x => console.log(' ', x.op.padEnd(6), (x.path||('type='+x.type)).padEnd(46), x.size?('b64='+x.size):(x.bytes?('bytes='+x.bytes):'')));

  const banner = await page.evaluate(() => { const b=document.getElementById('banner'); return b.hidden ? null : b.textContent; });
  const rowState = await page.evaluate(() => { const e=document.querySelector('.state'); return e?e.textContent:null; });
  const inputCleared = await page.evaluate(() => document.getElementById('picker').value === '');
  console.log('\nحالة الصف :', rowState);
  console.log('شريط التنبيه:', banner || '(لا شيء — جيد)');
  console.log('حقل الملف صُفِّر بعد الانتهاء:', inputCleared);

  await b.close();
})();
