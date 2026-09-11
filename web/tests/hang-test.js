const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const page = await (await b.newContext({viewport:{width:420,height:900}})).newPage();
  await page.addInitScript(() => {
    // محاكاة العطل الحقيقي: تحويل الصورة يعلّق للأبد
    window.createImageBitmap = () => new Promise(() => {});
    const rec=(p,d)=>Promise.resolve();
    const mkDoc=(p)=>({set:rec,update:rec,delete:rec,collection:(s)=>mkCol(p+'/'+s)});
    const mkCol=(p)=>{const q={orderBy:()=>q,limit:()=>q,onSnapshot:(n)=>{setTimeout(()=>n({docs:[],size:0,empty:true,docChanges:()=>[]}),20);return()=>{};},doc:(i)=>mkDoc(p+'/'+i)};return q;};
    window.claude={use:(n)=>Promise.resolve(n==='db'?{collection:mkCol,doc:mkDoc}
      :n==='assets'?{list:()=>Promise.resolve({assets:[],usage:{files:0,bytes:0,maxFiles:9,maxBytes:9}}),upload:()=>Promise.resolve({id:'y'.repeat(32),url:'',sizeBytes:1,contentType:'image/jpeg'}),delete:()=>Promise.resolve({deleted:true})}:null)};
  });
  await page.goto('file:///home/user/Restaurant/web/upload-portal.html');
  await page.waitForSelector('#btn-pick:not([disabled])');
  await page.setInputFiles('#picker','/tmp/claude-0/-home-user-Restaurant/d31cf2df-6db6-599d-8498-c3368f191265/scratchpad/probe.png');
  await page.evaluate(()=>{document.getElementById('diag').open=true;});
  await page.waitForFunction(() => /تجاوز المهلة|رجوع للملف الخام|✓ تم/.test(document.getElementById('diag-log').textContent), null, {timeout:60000});
  console.log(await page.evaluate(()=>document.getElementById('diag-log').textContent));
  console.log('حالة الصف:', await page.evaluate(()=>{const e=document.querySelector('.state');return e?e.textContent:null;}));
  await page.evaluate(()=>window.scrollTo(0,document.body.scrollHeight));await page.screenshot({path:'diag.png'});await b.close();
})();
