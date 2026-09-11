const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const page = await (await b.newContext({viewport:{width:420,height:900}})).newPage();
  await page.addInitScript(() => {
    window.__hidden = true;                       // نحاكي: الصفحة في الخلفية
    Object.defineProperty(document, 'hidden', { get: () => window.__hidden });
    window.createImageBitmap = () => new Promise(() => {});   // عملية لا تنتهي
    const ok=()=>Promise.resolve();
    const mkDoc=(p)=>({set:ok,update:ok,delete:ok,collection:(s)=>mkCol(p+'/'+s)});
    const mkCol=(p)=>{const q={orderBy:()=>q,limit:()=>q,onSnapshot:(n)=>{setTimeout(()=>n({docs:[],size:0,empty:true,docChanges:()=>[]}),20);return()=>{};},doc:(i)=>mkDoc(p+'/'+i)};return q;};
    window.claude={use:(n)=>Promise.resolve(n==='db'?{collection:mkCol,doc:mkDoc}
      :n==='assets'?{list:()=>Promise.resolve({assets:[],usage:{files:0,bytes:0,maxFiles:9,maxBytes:9}}),upload:()=>Promise.resolve({id:'z'.repeat(32),url:'',sizeBytes:1,contentType:'image/jpeg'}),delete:()=>Promise.resolve({deleted:true})}:null)};
  });
  await page.goto('file:///home/user/Restaurant/web/upload-portal.html');
  await page.waitForSelector('#btn-pick:not([disabled])');
  await page.evaluate(()=>{document.getElementById('diag').open=true;});
  await page.setInputFiles('#picker','/tmp/claude-0/-home-user-Restaurant/d31cf2df-6db6-599d-8498-c3368f191265/scratchpad/probe.png');

  await page.waitForTimeout(25000);   // 25 ثانية والصفحة "في الخلفية"
  const during = await page.evaluate(()=>document.getElementById('diag-log').textContent);
  console.log('بعد 25 ثانية في الخلفية — هل انتهت المهلة؟',
              /timeout|فشل التحويل/.test(during) ? '❌ نعم (خطأ)' : '✅ لا — العملية ما زالت معلّقة بانتظار العودة');

  await page.evaluate(()=>{ window.__hidden=false; document.dispatchEvent(new Event('visibilitychange')); });
  console.log('… أعدنا الصفحة للمقدمة، ننتظر 17 ثانية مرئية');
  await page.waitForTimeout(17000);
  const after = await page.evaluate(()=>document.getElementById('diag-log').textContent);
  console.log('بعد العودة — هل استأنفت وأكملت؟', /✓ تم/.test(after) ? '✅ نعم' : '❌ لا');
  console.log('\n--- السجل ---\n' + after.split('\n').filter(l=>l.trim()).join('\n'));
  await b.close();
})();
