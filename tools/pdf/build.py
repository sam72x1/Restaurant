# -*- coding: utf-8 -*-
import json, os, sys, datetime
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import charts; from css import CSS
D=json.load(open(f"{HERE}/facts.json",encoding="utf-8"))
N=json.load(open(f"{HERE}/finance.json",encoding="utf-8"))
FONTS=open("/tmp/claude-0/-home-user-Restaurant/d31cf2df-6db6-599d-8498-c3368f191265/scratchpad/fonts/embedded.css",encoding="utf-8").read()
AR="٠١٢٣٤٥٦٧٨٩"
def a(x):  return "".join(AR[int(c)] if c.isdigit() else c for c in str(x))
from decimal import Decimal, ROUND_HALF_UP
def m(x,d=0):
    q=Decimal(str(x)).quantize(Decimal(1) if d==0 else Decimal("1."+"0"*d), rounding=ROUND_HALF_UP)
    return f"{q:,}"
P=[]; add=P.append
SEC=[0]
def sec(title, lede=None, brk=True):
    SEC[0]+=1
    add(f'<section class="{"brk" if brk else ""}"><h2 class="sec"><span class="num">{a(f"{SEC[0]:02d}")}</span>{title}</h2>')
    if lede: add(f'<p class="lede">{lede}</p>')
def end(): add('</section>')
def chart(svg, cap): add(f'<div class="chart">{svg}<div class="cap">{cap}</div></div>')

MO=D["months"]; APR=MO[0]; AUG=MO[4]; SEP=MO[5]; E=D["entry"]; O=D["ops"]
FX=N["fixed"]; BE=N["breakeven"]; PATH=N["path"]; PLAN=N["plan"]

# ══════════ الغلاف ══════════
add(f'''<div class="cover">
  <div class="kicker">دراسة جدوى استحواذ · سرّية</div>
  <h1>مشوي كور<br>الحمراء — تبوك</h1>
  <div class="tag">تقييم شراء مطعم شاورما قائم بثلاثين ألف ريال.<br>
  مبنية على {a(D["period"]["days"])} يومًا متصلة من فواتير نظام رواء — لا على تقديرات.</div>
  <div class="spacer"></div>
  <dl class="facts">
    <div><dt>فترة القياس</dt><dd><span class="ltr">{D["period"]["from"]} – {D["period"]["to"]}</span></dd></div>
    <div><dt>الفواتير المحلَّلة</dt><dd>{m(D["totals"]["invoices"])}</dd></div>
    <div><dt>إجمالي المبيعات المقيسة</dt><dd>{m(D["totals"]["revenue"])} ريال</dd></div>
    <div><dt>أيام ناقصة في السجل</dt><dd>{D["period"]["missing_days"]}</dd></div>
    <div><dt>متوسط المبيعات اليومية</dt><dd>{m(D["avg"]["rev_day"],0)} ريال</dd></div>
    <div><dt>نقطة الدخول (آخر ١٤ يومًا)</dt><dd>{m(E["rev_day"],0)} ريال/يوم</dd></div>
  </dl>
  <div class="foot">أُعدّت لـ: المشتري &nbsp;·&nbsp; التاريخ: ١٢ سبتمبر ٢٠٢٦ &nbsp;·&nbsp; النسخة السابعة<br>
  مصادر الأرقام: تصديرا فواتير رواء التفصيليان · {D["purchases"]["invoices"]} فاتورة مورّد موثقة · إفادات المشتري المباشرة</div>
</div>''')

# ══════════ الملخص التنفيذي ══════════
add('<section><h2 class="sec">الملخص التنفيذي</h2>')
add(f'''<div class="note o"><span class="t">الحكم: اشترِ — لأنك تشتري محلًا مُهمَلًا لا محلًا منتهيًا.</span>
المبيعات هبطت من <strong>{m(APR["rev_day"],0)}</strong> ريالًا يوميًا في أبريل إلى <strong>{m(AUG["rev_day"],0)}</strong> في أغسطس — ناقص <strong>{round(100-100*AUG["rev_day"]/APR["rev_day"])}٪</strong>.
لكن السبب ليس انصراف الزبائن: المحل كان يفتح <strong>{a(O["april"]["open"])}</strong> صباحًا في أبريل و<strong>{a(O["august"]["open"])}</strong> ظهرًا في أغسطس،
والمنيو انكمش من {a(D["menu_size"]["مايو"])} صنفًا إلى {a(D["menu_size"]["أغسطس"])}، وسيخ اللحم أُوقف في يونيو.
الانحدار يطابق انسحاب المالك — وهو نفسه سبب البيع الذي ذكره: عدم تفرّغه واعتماده على ولده.</div>''')
add(f'''<dl class="kpis">
 <div class="kpi"><dt>نقطة الدخول اليوم</dt><dd>{m(E["rev_day"],0)}<span>ريال/يوم</span></dd></div>
 <div class="kpi g"><dt>بعد الاستعادة وخطة الرفع</dt><dd>{m(PATH[3]["rev_day"])}<span>ريال/يوم</span></dd></div>
 <div class="kpi"><dt>ذروة التشغيل المثبتة</dt><dd>{m(APR["rev_day"],0)}<span>ريال/يوم</span></dd></div>
 <div class="kpi r"><dt>القاع المسجَّل</dt><dd>{m(AUG["rev_day"],0)}<span>ريال/يوم</span></dd></div>
 <div class="kpi"><dt>متوسط الزبائن يوميًا</dt><dd>{E["inv_day"]}<span>طلبًا</span></dd></div>
 <div class="kpi"><dt>متوسط الفاتورة</dt><dd>{E["ticket"]}<span>ريال</span></dd></div>
 <div class="kpi y"><dt>النقد المطلوب</dt><dd>{m(N["cash"]["total"])}<span>ريال</span></dd></div>
 <div class="kpi g"><dt>الاسترداد المتوقع</dt><dd><span class="ltr">{N["payback"]["best_months"]}–{N["payback"]["mid_months"]}</span><span>شهرًا</span></dd></div>
</dl>''')
add(f'''<h3 class="sub">الخلاصة في ست نقاط</h3>
<ol class="steps">
 <li><b>الهبوط تشغيلي لا سوقي.</b><span>ناقص {round(100-100*E["rev_day"]/APR["rev_day"])}٪ عن أبريل، وتفكيكه: ساعات العمل نزلت من {a(O["april"]["active_hours"])} إلى {a(O["now"]["active_hours"])} ساعة (ناقص {round(100-100*O["now"]["active_hours"]/O["april"]["active_hours"])}٪)، بينما الإنتاجية في الساعة تعافت إلى {round(100*O["now"]["rev_per_hour"]/O["april"]["rev_per_hour"])}٪ من مستوى أبريل. الفجوة اليوم <strong>ساعات فتح، لا طلبًا مفقودًا</strong>.</span></li>
 <li><b>الزبائن غادروا، ولم يقلّ إنفاقهم.</b><span>الطلبات من {a(APR["inv_day"])} إلى {a(AUG["inv_day"])} يوميًا، ومتوسط الفاتورة ثابت بين {a(MO[2]["ticket"])} و{a(APR["ticket"])} ريالًا طوال الأشهر الستة.</span></li>
 <li><b>التعافي بدأ فعلًا.</b><span>آخر أربعة أسابيع ({D["weeks"][-4]["start"]} حتى {D["weeks"][-1]["end"]}): {" · ".join(m(w["rev"],0) for w in D["weeks"][-4:])} ريالًا، والطلبات من {D["weeks"][-4]["inv"]} إلى {D["weeks"][-1]["inv"]} يوميًا — مع استعادة جزء من الساعات وإعادة سيخ اللحم.</span></li>
 <li><b>أنظف فرصة: الظهيرة.</b><span>الفترة ١١–١٧ تُنتج {a(D["bands"][1]["now"])} ريالات يوميًا، وكانت تُنتج {a(D["bands"][1]["april"])}. ست ساعات مُلغاة فعليًا، واستعادتها <strong>+{m(D["bands"][1]["gap_month"])} ريالًا شهريًا</strong> برواتب مدفوعة أصلًا.</span></li>
 <li><b>السجل نظيف ويستحق الثقة.</b><span>{m(D["integrity"]["expected"])} رقم فاتورة متسلسل بلا فجوة واحدة، {a(D["integrity"]["discounts"])} ريالًا خصومات يدوية في {a(D["period"]["days"])} يومًا، و{a(D["integrity"]["returns"])} مرتجعات مسجّلة. الأرقام التي تشتري عليها حقيقية.</span></li>
 <li><b>والتحذير: أنت ستغيب أيضًا.</b><span>عندك سجل مقيس لما يحدث لهذا المحل حين يغيب مالكه — ناقص {round(100-100*AUG["rev_day"]/APR["rev_day"])}٪ في أربعة أشهر. ترتيب المشرف والرقابة اليومية ليس تفصيلًا في هذه الصفقة، بل هو الصفقة.</span></li>
</ol>''')
add(f'''<div class="note b"><span class="t">الشرط الذي يحكم الربحية كلها</span>
ربحك يقع داخل فرضية أن <strong>المقابل المالي للعمالة لا يُدفع</strong> (إفادتك). في عمود التكلفة الكاملة يبقى الصافي سالبًا ({m(PATH[3]["full"])} ريالًا) حتى بعد الاستعادة وخطة الرفع، ولا يصبح موجبًا إلا بعودة كاملة لمستوى أبريل. اكتب هذه الفرضية صراحة وراجعها كلما تغيّر النظام.</div>''')
end()

# ══════════ المحتويات ══════════
TOC=[("نطاق الدراسة ومصادر أرقامها",""),("المبيعات — الصورة الكاملة",""),
 ("الزبائن والطلبات ومتوسط الفاتورة",""),("التشخيص — لماذا هبطت المبيعات",""),
 ("الفترات اليومية وأيام الأسبوع",""),("المنيو — ما يبيعه المحل فعلًا",""),
 ("اللحوم — المطابقة الفيزيائية",""),("سلامة السجل — أربعة اختبارات",""),
 ("تكلفة المواد — بناء من أسعار الموردين",""),("الرواتب والتكاليف الثابتة",""),
 ("نقطة التعادل",""),("مسار الاستعادة والربحية",""),("خطة الرفع — خمسة إجراءات",""),
 ("النقد المطلوب وهيكل الدفع",""),("بنية الصفقة القانونية",""),
 ("حافز المشرف والرقابة اليومية",""),("المخاطر مرتبة بالأثر",""),("معيار الإيقاف",""),
 ("ما تسأل البائع عنه",""),("حدود هذه الدراسة","")]
add('<section class="brk"><h2 class="sec">المحتويات</h2><div class="toc">')
for i,(t,_) in enumerate(TOC,1): add(f'<div><span class="tn">{a(f"{i:02d}")}</span><span>{t}</span></div>')
add('<div><span class="tn">أ</span><span>ملحق: البيانات اليومية الكاملة — ١٦٥ يومًا</span></div>')
add('<div><span class="tn">ب</span><span>ملحق: المنيو الكامل بالكميات والأسعار</span></div>')
add('</div>')
add(f'''<div class="note"><span class="t">كيف تقرأ درجات الإثبات في هذه الوثيقة</span>
<span class="grade g-v">مقيس</span> رقم مأخوذ مباشرة من مستند (فاتورة رواء أو فاتورة مورّد) — لا اجتهاد فيه.<br>
<span class="grade g-c">منقول</span> إفادة شفهية من البائع أو المشتري بلا مستند يسندها.<br>
<span class="grade g-e">استنتاج</span> اشتقاق مني من أرقام مقيسة — منطقه معروض ليُراجَع.</div>''')
end()

# ══════════ 01 النطاق ══════════
sec("نطاق الدراسة ومصادر أرقامها",
    "كل رقم في هذه الوثيقة يعود إلى أحد ثلاثة مصادر، ودرجة إثباته مذكورة عند وروده.")
add(f'''<table>
<thead><tr><th>المصدر</th><th class="f">الحجم</th><th>الفترة</th><th>ما يُثبته</th></tr></thead><tbody>
<tr><td>تصديرا فواتير رواء التفصيليان</td><td class="f">{m(D["totals"]["invoices"])} فاتورة · {m(D["totals"]["lines"])} سطر بيع</td><td class="f">{D["period"]["from"]} – {D["period"]["to"]}</td><td>المبيعات والطلبات والأصناف والساعات</td></tr>
<tr><td>فواتير موردين مصوَّرة</td><td class="f">{D["purchases"]["invoices"]} فاتورة · {D["purchases"]["lines"]} سطر</td><td class="f">{D["purchases"]["from"]} – {D["purchases"]["to"]}</td><td>أسعار الوحدات وتركّز الموردين</td></tr>
<tr><td>إفادات المشتري المباشرة</td><td class="f">—</td><td class="f">—</td><td>السعر · الإيجار · الرواتب · المقابل المالي</td></tr>
</tbody></table>''')
add(f'''<div class="note o"><span class="t">تغطية السجل كاملة بلا ثغرة</span>
{a(D["period"]["days"])} يومًا تقويميًا في الفترة، و{a(D["period"]["days"])} يومًا فيها بيع مسجَّل. <strong>صفر يوم ناقص.</strong>
هذا ليس عيّنة ولا تقديرًا — هو سجل المحل كاملًا لخمسة أشهر ونصف.</div>''')
add(f'''<h3 class="sub">ما لا تغطيه هذه المصادر</h3>
<ul class="plain">
<li>لا توجد بيانات لما قبل أول أبريل ٢٠٢٦ — نظام رواء لا يحمل سنة سابقة للمقارنة الموسمية.</li>
<li>فواتير المشتريات غير كاملة: تغطي أبريل–يونيو جيدًا، وشهر يوليو غائب كليًا، وأغسطس وسبتمبر خفيفان. لذلك تُستخدم لاستخراج <em>أسعار الوحدات</em> لا لحساب نسبة تكلفة المواد.</li>
<li>لم يصل كشف بنكي ولا إقرار ضريبي ولا عقد إيجار ولا جرد معدات موقَّع.</li>
</ul>''')
end()

# ══════════ 02 المبيعات ══════════
sec("المبيعات — الصورة الكاملة",
    f"إجمالي {m(D['totals']['revenue'])} ريال على {a(D['period']['days'])} يومًا. كل عمود في الرسم أدناه يوم واحد، والخط الأسود متوسط سبعة أيام.")
chart(charts.daily(D), f"المبيعات اليومية {D['period']['from']} – {D['period']['to']}. الخطان المتقطعان: تعادل ٨٣٢ (تكلفة كاملة) وتعادل ٥٧٨ (بلا مقابل مالي وسكن).")
add('<table><thead><tr><th>الشهر</th><th class="f">أيام</th><th class="f">المبيعات</th><th class="f">ريال/يوم</th><th class="f">طلبات/يوم</th><th class="f">متوسط الفاتورة</th><th class="f">أصناف/فاتورة</th><th class="f">التغيّر</th></tr></thead><tbody>')
prev=None
for x in MO:
    ch=f'{100*(x["rev_day"]/prev-1):+.0f}%' if prev else "—"
    cls=' class="lo"' if x["m"]==8 else (' class="hi"' if x["m"]==4 else "")
    add(f'<tr{cls}><td>{x["name"]}</td><td class="f">{x["days"]}</td><td class="f">{m(x["rev"])}</td>'
        f'<td class="f">{m(x["rev_day"],0)}</td><td class="f">{x["inv_day"]}</td>'
        f'<td class="f">{x["ticket"]}</td><td class="f">{x["items_inv"]}</td><td class="f">{ch}</td></tr>')
    prev=x["rev_day"]
add(f'<tr class="tot"><td>الإجمالي / المتوسط</td><td class="f">{D["period"]["days"]}</td><td class="f">{m(D["totals"]["revenue"])}</td>'
    f'<td class="f">{m(D["avg"]["rev_day"],0)}</td><td class="f">{D["avg"]["inv_day"]}</td>'
    f'<td class="f">{D["avg"]["ticket"]}</td><td class="f">{D["avg"]["items_inv"]}</td><td class="f">—</td></tr></tbody></table>')
chart(charts.monthly(D), "المبيعات اليومية بالمتوسط الشهري، وتحتها عدد الطلبات اليومي.")
add(f'''<h3 class="sub">توزيع الأيام</h3>
<dl class="kpis">
 <div class="kpi"><dt>الوسيط</dt><dd>{m(D["dist"]["median"],0)}<span>ريال</span></dd></div>
 <div class="kpi"><dt>الربع الأدنى</dt><dd>{m(D["dist"]["p25"],0)}<span>ريال</span></dd></div>
 <div class="kpi"><dt>الربع الأعلى</dt><dd>{m(D["dist"]["p75"],0)}<span>ريال</span></dd></div>
 <div class="kpi"><dt>المدى</dt><dd><span class="ltr">{m(D["dist"]["min"],0)}–{m(D["dist"]["max"],0)}</span><span>ريال</span></dd></div>
</dl>''')
add(f'''<h3 class="sub">آخر ثمانية أسابيع — التعافي</h3>
<table class="sm"><thead><tr><th>الأسبوع</th><th class="f">ريال/يوم</th><th class="f">طلبات/يوم</th></tr></thead><tbody>''')
for w in D["weeks"][-8:]:
    add(f'<tr><td class="f">{w["start"]} – {w["end"]}</td><td class="f">{m(w["rev"],0)}</td><td class="f">{w["inv"]}</td></tr>')
add('</tbody></table>')
add(f'''<div class="note o"><span class="t">أربعة أسابيع صاعدة متتالية</span>
{" · ".join(m(w["rev"],0) for w in D["weeks"][-4:])} ريالًا يوميًا، بارتفاع <strong>{round(100*(D["weeks"][-1]["rev"]/D["weeks"][-4]["rev"]-1))}٪</strong> عن قاع أغسطس.
والطلبات ارتفعت معها من {a(D["weeks"][-4]["inv"])} إلى {a(D["weeks"][-1]["inv"])} يوميًا — أي أن الارتفاع زبائن حقيقيون لا فواتير أكبر. <span class="grade g-v">مقيس</span></div>''')
end()

# ══════════ 03 الزبائن ══════════
sec("الزبائن والطلبات ومتوسط الفاتورة",
    "السؤال الحاسم في أي انحدار: هل قلّ عدد الزبائن أم قلّ إنفاق كل زبون؟ الجواب هنا قاطع.")
add(f'''<dl class="kpis">
 <div class="kpi"><dt>متوسط الطلبات يوميًا — الفترة كلها</dt><dd>{D["avg"]["inv_day"]}</dd></div>
 <div class="kpi"><dt>أبريل</dt><dd>{APR["inv_day"]}</dd></div>
 <div class="kpi r"><dt>أغسطس</dt><dd>{AUG["inv_day"]}</dd></div>
 <div class="kpi g"><dt>آخر ١٤ يومًا</dt><dd>{E["inv_day"]}</dd></div>
</dl>''')
add(f'''<table><thead><tr><th>&nbsp;</th><th class="f">أبريل</th><th class="f">أغسطس</th><th class="f">التغيّر</th></tr></thead><tbody>
<tr><td>الطلبات يوميًا</td><td class="f">{APR["inv_day"]}</td><td class="f">{AUG["inv_day"]}</td><td class="f neg">{100*(AUG["inv_day"]/APR["inv_day"]-1):+.0f}%</td></tr>
<tr><td>متوسط الفاتورة</td><td class="f">{APR["ticket"]}</td><td class="f">{AUG["ticket"]}</td><td class="f pos">{100*(AUG["ticket"]/APR["ticket"]-1):+.1f}%</td></tr>
<tr><td>أصناف لكل فاتورة</td><td class="f">{APR["items_inv"]}</td><td class="f">{AUG["items_inv"]}</td><td class="f">{100*(AUG["items_inv"]/APR["items_inv"]-1):+.1f}%</td></tr>
<tr class="tot"><td>المبيعات يوميًا</td><td class="f">{m(APR["rev_day"],0)}</td><td class="f">{m(AUG["rev_day"],0)}</td><td class="f neg">{100*(AUG["rev_day"]/APR["rev_day"]-1):+.0f}%</td></tr>
</tbody></table>''')
add(f'''<div class="note b"><span class="t">الهبوط كله في عدد الزبائن</span>
متوسط الفاتورة <strong>لم ينخفض</strong> — بل ارتفع قليلًا. وأصناف الفاتورة ثابتة عند {a(D["avg"]["items_inv"])} تقريبًا.
أي أن من بقي من الزبائن يشتري كما كان يشتري تمامًا، لكن <strong>نصفهم لم يعد يأتي</strong>. هذه بصمة مشكلة وصول (ساعات فتح، ظهور)، لا مشكلة منتج ولا تسعير. <span class="grade g-v">مقيس</span></div>''')
add(f'''<h3 class="sub">حجم السلة</h3>
<table class="sm"><thead><tr><th>عدد الأصناف في الفاتورة</th><th class="f">عدد الفواتير</th><th class="f">النسبة</th></tr></thead><tbody>''')
tot_b=sum(D["basket"].values())
for k,v in D["basket"].items():
    lab=f'{a(k)} أصناف فأكثر' if k=="6" else (f'صنف واحد' if k=="1" else f'{a(k)} أصناف')
    add(f'<tr><td>{lab}</td><td class="f">{m(v)}</td><td class="f">{100*v/tot_b:.1f}%</td></tr>')
add('</tbody></table>')
add(f'''<div class="note w"><span class="t">{a(D["attach"]["single"])}٪ من فواتيرك صنف واحد فقط</span>
<strong>{m(D["attach"]["single_n"])} فاتورة</strong> في {a(D["period"]["days"])} يومًا خرج صاحبها بسندويتش بلا مشروب ولا بطاطس.
هذه ليست مشكلة منيو — هي جملة لا تُقال عند الصندوق. معالجتها في القسم ١٣.</div>''')
add(f'''<h3 class="sub">معدلات الإرفاق</h3>
<table><thead><tr><th>الإضافة</th><th class="f">نسبة الفواتير التي تتضمّنها</th><th>الدلالة</th></tr></thead><tbody>
<tr><td>مشروب</td><td class="f">{D["attach"]["drink"]}%</td><td>ثلثا الزبائن يخرجون بلا مشروب</td></tr>
<tr><td>جبن</td><td class="f">{D["attach"]["cheese"]}%</td><td>إضافة بريال واحد، هامشها شبه كامل</td></tr>
<tr><td>بطاطس</td><td class="f">{D["attach"]["fries"]}%</td><td>أضعف رقم — وأعلى هامش بالريال</td></tr>
</tbody></table>''')
add(f'''<h3 class="sub">طرق الدفع</h3>
<table><thead><tr><th>الطريقة</th><th class="f">القيمة</th><th class="f">النسبة</th><th class="f">ريال/يوم</th></tr></thead><tbody>''')
for p in D["payments"]:
    add(f'<tr><td>{p["method"]}</td><td class="f">{m(p["value"])}</td><td class="f">{p["pct"]}%</td><td class="f">{m(p["day"],0)}</td></tr>')
add('</tbody></table>')
add(f'''<div class="note"><span class="t">النقد {D["payments"][1]["pct"]}٪ فقط</span>
نحو سبعين بالمئة من مبيعاتك تمرّ عبر الشبكة وتُسوَّى بنكيًا. هذا يقلّل مساحة التسرّب النقدي كثيرًا،
ويجعل مطابقة المبيعات بالإيداعات البنكية أداة رقابة عملية وأنت غائب.</div>''')
end()

# ══════════ 04 التشخيص ══════════
sec("التشخيص — لماذا هبطت المبيعات",
    "ثلاثة تغيّرات تشغيلية وقعت بين أبريل وأغسطس، وكلها مسجَّلة في البيانات لا مستنتَجة.")
add(f'''<table><thead><tr><th>المؤشر</th><th class="f">أبريل</th><th class="f">أغسطس</th><th class="f">آخر ١٤ يومًا</th></tr></thead><tbody>
<tr><td>وقت أول بيعة في اليوم</td><td class="f">{O["april"]["open"]}</td><td class="f neg">{O["august"]["open"]}</td><td class="f">{O["now"]["open"]}</td></tr>
<tr><td>عدد الساعات النشطة</td><td class="f">{O["april"]["active_hours"]}</td><td class="f">{O["august"]["active_hours"]}</td><td class="f">{O["now"]["active_hours"]}</td></tr>
<tr><td>أيام فيها بيع قبل ١١ ص</td><td class="f">{O["april"]["morning_days_pct"]}%</td><td class="f neg">{O["august"]["morning_days_pct"]}%</td><td class="f">{O["now"]["morning_days_pct"]}%</td></tr>
<tr><td>إيراد الصباح ٥–١١</td><td class="f">{O["april"]["morning_rev"]}</td><td class="f neg">{O["august"]["morning_rev"]}</td><td class="f">{O["now"]["morning_rev"]}</td></tr>
<tr><td>أصناف نشطة على المنيو</td><td class="f">{D["menu_size"]["أبريل"]}</td><td class="f neg">{D["menu_size"]["أغسطس"]}</td><td class="f">{D["menu_size"]["سبتمبر"]}</td></tr>
<tr><td>سيخ اللحم (ريال/يوم)</td><td class="f pos">{D["meat"]["beef_timeline"]["أبريل"]}</td><td class="f neg">{D["meat"]["beef_timeline"]["أغسطس"]}</td><td class="f pos">{D["meat"]["beef_timeline"]["سبتمبر"]}</td></tr>
<tr class="tot"><td>المبيعات يوميًا</td><td class="f">{m(O["april"]["rev_day"],0)}</td><td class="f">{m(O["august"]["rev_day"],0)}</td><td class="f">{m(O["now"]["rev_day"],0)}</td></tr>
<tr class="tot"><td>الإيراد لكل ساعة نشطة</td><td class="f">{O["april"]["rev_per_hour"]}</td><td class="f neg">{O["august"]["rev_per_hour"]}</td><td class="f">{O["now"]["rev_per_hour"]}</td></tr>
</tbody></table>''')
hr_now=O["now"]["active_hours"]/O["april"]["active_hours"]; pr_now=O["now"]["rev_per_hour"]/O["april"]["rev_per_hour"]
hr_aug=O["august"]["active_hours"]/O["april"]["active_hours"]; pr_aug=O["august"]["rev_per_hour"]/O["april"]["rev_per_hour"]
add(f'''<h3 class="sub">تفكيك الفجوة — عاملان فقط، ولا ثالث</h3>
<table><thead><tr><th>مقارنةً بأبريل</th><th class="f">الساعات</th><th class="f">× الإنتاجية/ساعة</th><th class="f">= الناتج</th><th class="f">المبيعات الفعلية</th></tr></thead><tbody>
<tr><td>أغسطس</td><td class="f">{100*hr_aug:.0f}%</td><td class="f">{100*pr_aug:.0f}%</td><td class="f">{100*hr_aug*pr_aug:.0f}%</td><td class="f">{100*O["august"]["rev_day"]/O["april"]["rev_day"]:.0f}%</td></tr>
<tr class="hi"><td>آخر ١٤ يومًا</td><td class="f">{100*hr_now:.0f}%</td><td class="f">{100*pr_now:.0f}%</td><td class="f">{100*hr_now*pr_now:.0f}%</td><td class="f">{100*O["now"]["rev_day"]/O["april"]["rev_day"]:.0f}%</td></tr>
</tbody></table>''')
add(f'''<div class="note o"><span class="t">وهذا أهم سطر في الدراسة كلها</span>
في أغسطس انهار العاملان معًا: الساعات إلى {100*hr_aug:.0f}٪ والإنتاجية إلى {100*pr_aug:.0f}٪.
أما اليوم فقد <strong>تعافت الإنتاجية في الساعة إلى {100*pr_now:.0f}٪ من مستوى أبريل</strong> — أي أن المحل حين يفتح، يبيع كما كان يبيع تقريبًا.
الفجوة المتبقية <strong>ساعات فتح وحدها</strong>: {a(O["now"]["active_hours"])} ساعة مقابل {a(O["april"]["active_hours"])}.
وهذا أسهل ما يُصلَح في مطعم: قرار فتحٍ لا استثمار. <span class="grade g-e">استنتاج</span></div>''')
add(f'''<h3 class="sub">سيخ اللحم — استعادة لا ابتكار</h3>
<table class="sm"><thead><tr><th>الشهر</th>''' + "".join(f'<th class="f">{k}</th>' for k in D["meat"]["beef_timeline"]) + '</tr></thead><tbody><tr><td>إيراد اللحم ريال/يوم</td>' +
    "".join(f'<td class="f">{v}</td>' for v in D["meat"]["beef_timeline"].values()) + '</tr></tbody></table>')
add(f'''<div class="note"><span class="t">تصحيح مهم</span>
سيخ اللحم كان يعمل في أبريل ({a(D["meat"]["beef_timeline"]["أبريل"])} ريالًا يوميًا) ومايو ({a(D["meat"]["beef_timeline"]["مايو"])})، ثم توقّف من يونيو إلى أغسطس، وأُعيد في سبتمبر ({a(D["meat"]["beef_timeline"]["سبتمبر"])}).
فهو <strong>استعادة لمنتج مُثبت على هذا المحل تحديدًا</strong>، لا فكرة جديدة تُجرَّب. وهذا أقوى، لا أضعف: أثره مقيس لا متوقَّع.</div>''')
add(f'''<div class="note b"><span class="t">وما لا تستطيع هذه الدراسة حسمه</span>
كم من الهبوط سببه صيف تبوك وكم سببه تقصير الساعات؟ لا أستطيع الفصل: نظام رواء بدأ في ٢٠٢٦ ولا يحمل سنة سابقة للمقارنة.
وقراءتي — أن المالك انسحب فتقلّصت الساعات — <strong>قد تكون معكوسة</strong>: ربما ضعف الطلب هو ما دفعه للتقصير.
السؤال الذي يحسم الاتجاه مذكور في القسم ١٩، وأكتوبر ونوفمبر يحسمانه نهائيًا.</div>''')
end()

# ══════════ 05 الفترات ══════════
sec("الفترات اليومية وأيام الأسبوع",
    "أين يقع المال داخل اليوم، وأين اختفى. المقارنة بين أبريل (ذروة التشغيل) وآخر أربعة عشر يومًا.")
chart(charts.hourly(D), "الإيراد بالريال لكل ساعة من اليوم — أبريل مقابل آخر ١٤ يومًا. المحور يبدأ من الرابعة فجرًا.")
add('<table><thead><tr><th>الفترة</th><th class="f">الساعات</th><th class="f">أبريل</th><th class="f">الآن</th><th class="f">الفجوة/يوم</th><th class="f">الفجوة/شهر</th></tr></thead><tbody>')
for b in D["bands"]:
    cls=' class="lo"' if b["name"]=="الظهيرة" else ""
    sign="pos" if b["gap"]>0 else "neg"
    add(f'<tr{cls}><td>{b["name"]}</td><td class="f">{b["range"]}</td><td class="f">{b["april"]}</td>'
        f'<td class="f">{b["now"]}</td><td class="f {sign}">{b["gap"]:+.1f}</td><td class="f {sign}">{b["gap_month"]:+,}</td></tr>')
add(f'<tr class="tot"><td>الإجمالي</td><td class="f">—</td><td class="f">{m(APR["rev_day"],0)}</td><td class="f">{m(E["rev_day"],0)}</td>'
    f'<td class="f">{APR["rev_day"]-E["rev_day"]:+.1f}</td><td class="f pos">+{m(D["bands_gap_total"])}</td></tr></tbody></table>')
add(f'''<div class="note o"><span class="t">أنظف رقم في الوثيقة: الظهيرة</span>
الفترة ١١–١٧ تُنتج اليوم <strong>{a(D["bands"][1]["now"])} ريالات</strong>، وكانت تُنتج <strong>{a(D["bands"][1]["april"])} ريالًا</strong>.
ست ساعات مُلغاة فعليًا. واستعادتها لا تحتاج زبونًا جديدًا ولا ريالًا مستثمرًا — رواتب الثلاثة مدفوعة أصلًا عن تلك الساعات.
<strong>+{m(D["bands"][1]["gap_month"])} ريالًا شهريًا من قرار فتحٍ لا أكثر.</strong> <span class="grade g-v">مقيس</span></div>''')
add(f'''<div class="note w"><span class="t">والفترة الوحيدة التي نمت</span>
بعد منتصف الليل ارتفعت من {a(D["bands"][4]["april"])} إلى {a(D["bands"][4]["now"])} ريالًا.
هذا متسق مع محل انكمش نهارًا وتركّز ليلًا — وهو عرَض للمشكلة لا حلٌّ لها.</div>''')
add('<h3 class="sub">أيام الأسبوع</h3>')
chart(charts.dow(D), f"متوسط المبيعات وعدد الطلبات لكل يوم من أيام الأسبوع على {a(D['period']['days'])} يومًا.")
add('<table class="sm"><thead><tr><th>اليوم</th><th class="f">ريال/يوم</th><th class="f">طلبات/يوم</th><th class="f">مقابل المتوسط</th><th class="f">عدد الأيام</th></tr></thead><tbody>')
avg_dow=sum(x["rev"] for x in D["dow"])/7
for x in sorted(D["dow"],key=lambda z:-z["rev"]):
    d=100*(x["rev"]/avg_dow-1)
    add(f'<tr><td>{x["name"]}</td><td class="f">{m(x["rev"])}</td><td class="f">{x["inv"]}</td>'
        f'<td class="f {"pos" if d>0 else "neg"}">{d:+.0f}%</td><td class="f">{x["days"]}</td></tr>')
add('</tbody></table>')
add(f'''<div class="note"><span class="t">الفارق بين أقوى يوم وأضعفه {round(100*(max(x["rev"] for x in D["dow"])/min(x["rev"] for x in D["dow"])-1))}٪</span>
وهو فارق معتدل لا يستدعي جدولة مختلفة للعمالة. خطّط على أسبوع متجانس، وركّز الجهد على الساعات لا على الأيام.</div>''')
end()

# ══════════ 06 المنيو ══════════
sec("المنيو — ما يبيعه المحل فعلًا",
    f"{a(len(D['items']))} صنفًا سُجّل بيعه في الفترة. الجدول يعرض العشرين الأعلى إيرادًا، والملحق (ب) يعرضها كاملة.")
add('<table><thead><tr><th>#</th><th>الصنف</th><th class="f">السعر</th><th class="f">حبة/يوم</th><th class="f">الإجمالي</th><th class="f">الإيراد</th><th class="f">حصته</th></tr></thead><tbody>')
for i,it in enumerate(D["items"][:20],1):
    add(f'<tr><td class="f">{i}</td><td>{it["name"]}</td><td class="f">{it["price"]}</td><td class="f">{it["qty_day"]}</td>'
        f'<td class="f">{m(it["qty"])}</td><td class="f">{m(it["rev"])}</td><td class="f">{it["share"]}%</td></tr>')
top20=sum(x["share"] for x in D["items"][:20])
add(f'<tr class="tot"><td colspan="6">حصة العشرين الأعلى من إجمالي الإيراد</td><td class="f">{top20:.1f}%</td></tr></tbody></table>')
top5=sum(x["share"] for x in D["items"][:5])
add(f'''<div class="note"><span class="t">تركّز عالٍ في المنيو</span>
خمسة أصناف فقط تصنع <strong>{top5:.0f}٪</strong> من إيرادك، وعشرون صنفًا تصنع {top20:.0f}٪.
هذا يعني أن رفع سعر صنفين أو ثلاثة يمرّ إلى أسفل القائمة مباشرة — وهو أساس خطة القسم ١٣.</div>''')
add('<h3 class="sub">التقسيم حسب النوع</h3>')
kinds={}
for it in D["items"]: kinds.setdefault(it["kind"],[0,0.0]); kinds[it["kind"]][0]+=it["qty"]; kinds[it["kind"]][1]+=it["rev"]
tr=sum(v for _,v in kinds.values())
add('<table><thead><tr><th>النوع</th><th class="f">الكمية</th><th class="f">حبة/يوم</th><th class="f">الإيراد</th><th class="f">الحصة</th></tr></thead><tbody>')
for k in ["دجاج","لحم","غيره"]:
    if k not in kinds: continue
    q,v=kinds[k]
    add(f'<tr><td>شاورما {k}</td><td class="f">{m(q)}</td><td class="f">{q/D["period"]["days"]:.1f}</td><td class="f">{m(v)}</td><td class="f">{100*v/tr:.1f}%</td></tr>'
        if k!="غيره" else
        f'<tr><td>مشروبات وفطور ومقبلات</td><td class="f">{m(q)}</td><td class="f">{q/D["period"]["days"]:.1f}</td><td class="f">{m(v)}</td><td class="f">{100*v/tr:.1f}%</td></tr>')
add('</tbody></table>')
end()

# ══════════ 07 اللحوم ══════════
MEAT=D["meat"]; U=D["unit_costs"]
sec("اللحوم — المطابقة الفيزيائية",
    "أقوى اختبار لصدق سجل المبيعات: هل يطابق ما يُباع ما يُشترى؟ يُجرى بربط كميات السندويتش بوزن اللحم المشترى.")
add(f'''<table><thead><tr><th>الخطوة</th><th class="f">القيمة</th><th>المصدر</th></tr></thead><tbody>
<tr><td>سندويتشات الدجاج يوميًا</td><td class="f">{MEAT["chicken_day_entry"]}</td><td>عدّ من فواتير آخر ١٤ يومًا <span class="grade g-v">مقيس</span></td></tr>
<tr><td>وزن الحشوة للسندويتش الواحد</td><td class="f">{MEAT["gram"]} غرامًا</td><td>إفادة المشتري <span class="grade g-c">منقول</span></td></tr>
<tr><td>استهلاك الدجاج يوميًا</td><td class="f">{MEAT["chicken_kg_entry"]} كجم</td><td>حاصل الضرب</td></tr>
<tr><td>صافي الكرتون على السيخ</td><td class="f">8 كجم</td><td>إفادة المشتري بعد تصفية الماء والجلد <span class="grade g-c">منقول</span></td></tr>
<tr class="tot"><td>الكراتين المطلوبة شهريًا</td><td class="f">{MEAT["cartons_month"]}</td><td>المشتق من النظام</td></tr>
<tr class="hi"><td>الكراتين المشتراة فعلًا — فواتير المورّد</td><td class="f">13.0</td><td>أبريل–يونيو، ٣٩ كرتونًا على ٣ أشهر <span class="grade g-v">مقيس</span></td></tr>
</tbody></table>''')
add(f'''<div class="note o"><span class="t">المطابقة {round(100*13.0/MEAT["cartons_month"])}٪ — والسجل يجتاز الاختبار</span>
مصدران مستقلان لا يعرف أحدهما الآخر — نظام نقاط البيع وفواتير المورّد — يتفقان في حدود سبعة بالمئة.
لو كان نصف المبيعات يُباع خارج النظام لاحتاج المحل ضعف الكراتين، والفواتير تقول إنه لم يشترها.
<strong>لا دليل على مبيعات لا تمرّ بالنظام.</strong> <span class="grade g-e">استنتاج</span></div>''')
add(f'''<div class="note b"><span class="t">تصحيح مسجَّل لصالح الأمانة</span>
في نسخة سابقة من هذه الدراسة استنتجتُ أن نحو نصف المبيعات لا تمرّ بالنظام، وسمّيتُه مثبتًا.
كان مبنيًا على تقدير شفهي بأن المحل يستهلك كرتونًا يوميًا (٣٠ شهريًا). القياس أعلاه نفاه: الاستهلاك الفعلي {a(MEAT["cartons_month"])} كرتونًا.
<strong>الاستنتاج سُحب بالكامل</strong>، والقاعدة المستفادة مطبَّقة في هذه النسخة: لا يُرفع رقم إلى درجة «مقيس» ما لم يسنده مصدران مستقلان.</div>''')
add(f'''<h3 class="sub">سيخ اللحم — السؤال التشغيلي المفتوح</h3>
<p>تركّب <strong>٣ كجم</strong> لحم يوميًا. النظام يسجّل بيع <strong>{a(MEAT["beef_day_entry"])}</strong> سندويتشات = <strong>{a(MEAT["beef_kg_entry"])} كجم</strong>. الباقي — نحو ٢٫٤ كجم — يعود إلى الثلاجة ويُركَّب في اليوم التالي.</p>
<table><thead><tr><th>الفرض</th><th class="f">تكلفة اللحم يوميًا</th><th class="f">إيراده يوميًا</th><th class="f">صافيه شهريًا</th></tr></thead><tbody>
<tr class="hi"><td>المرتجع يُعاد استخدامه فعلًا</td><td class="f">{MEAT["beef_kg_entry"]*U["كرتون لحم ١٠ كجم"]/8+7:.0f}</td><td class="f">{MEAT["beef_timeline"]["سبتمبر"]}</td><td class="f pos">+{(MEAT["beef_timeline"]["سبتمبر"]-(MEAT["beef_kg_entry"]*U["كرتون لحم ١٠ كجم"]/8+7))*30:,.0f}</td></tr>
<tr class="lo"><td>الثلاثة كيلو تُستهلك أو تُتلف</td><td class="f">{3*U["كرتون لحم ١٠ كجم"]/8+7:.0f}</td><td class="f">{MEAT["beef_timeline"]["سبتمبر"]}</td><td class="f neg">{(MEAT["beef_timeline"]["سبتمبر"]-(3*U["كرتون لحم ١٠ كجم"]/8+7))*30:+,.0f}</td></tr>
</tbody></table>
<p style="font-size:8.6pt;color:#52707A">سعر كرتون اللحم {U["كرتون لحم ١٠ كجم"]} ريالًا، صافيه ٨ كجم = {U["كرتون لحم ١٠ كجم"]/8:.2f} ريالًا للكيلو. أُضيف ٧ ريالات يوميًا للخبز والخضار والورق.</p>''')
add(f'''<div class="note w"><span class="t">الفارق بين الحالتين نحو {(((MEAT["beef_timeline"]["سبتمبر"]-(MEAT["beef_kg_entry"]*U["كرتون لحم ١٠ كجم"]/8+7))-(MEAT["beef_timeline"]["سبتمبر"]-(3*U["كرتون لحم ١٠ كجم"]/8+7)))*30):,.0f} ريال شهريًا</span>
ولا يحسمه إلا قياسك أنت: زِن ما يعود إلى الثلاجة سبعة أيام متتالية وسجّل متى يُتلف. لا تعتمد على انطباع الشيف.
<br><br>وبصرف النظر عن الجواب: تركيب ٣ كجم لبيع {a(MEAT["beef_kg_entry"])} كجم يعني تدويرًا حراريًا يوميًا للحم نفسه — يُفسد الطعم، وإفساد الطعم يُضعف البيع، وضعف البيع يزيد المرتجع.
<strong>ابدأ بكيلو ونصف وارفعها حين ينفد السيخ فعلًا.</strong></div>''')
end()

# ══════════ 08 السلامة ══════════
I=D["integrity"]
sec("سلامة السجل — أربعة اختبارات",
    "قبل أن تُبنى قرارات على سجلٍّ، يُختبر السجل نفسه. اجتاز الأربعة.")
add(f'''<table><thead><tr><th>الاختبار</th><th>ما يكشفه</th><th class="f">النتيجة</th></tr></thead><tbody>
<tr><td>تسلسل أرقام الفواتير</td><td>فواتير أُنشئت ثم حُذفت</td><td class="f pos">{I["seq_from"]}–{I["seq_to"]} · صفر فجوة من {m(I["expected"])}</td></tr>
<tr><td>مطابقة الدجاج</td><td>مبيعات لا تمرّ بالنظام</td><td class="f pos">{MEAT["cartons_month"]} مقابل 13.0 كرتونًا</td></tr>
<tr><td>الخصومات اليدوية</td><td>تلاعب عند الصندوق</td><td class="f pos">{I["discounts"]:.0f} ريالًا على {I["discount_invoices"]} فواتير</td></tr>
<tr><td>المرتجعات</td><td>إخفاء إلغاءات</td><td class="f pos">{I["returns"]} مرتجعات مسجّلة بـ{I["returns_value"]:.0f} ريالًا</td></tr>
</tbody></table>''')
add(f'''<div class="note o"><span class="t">السجل نظيف</span>
{m(I["expected"])} رقم فاتورة متسلسل من {I["seq_from"]} إلى {I["seq_to"]}، وكلها موجودة. لا فاتورة واحدة حُذفت في {a(D["period"]["days"])} يومًا.
<strong>هذا خبر جيد بمعنى واحد: الرقم الذي تشتري عليه حقيقي.</strong> وليس خبرًا عن حجم الرقم نفسه.</div>''')
add(f'''<div class="note w"><span class="t">حدّ هذا الدليل — يجب أن يُقال</span>
صفر فجوة يُثبت أن فاتورة أُنشئت لم تُحذف. ولا يُثبت أن كل بيعة سُجّلت: البيعة التي لا تُدخل أصلًا لا تترك فجوة.
لكن مطابقة الدجاج تغطي هذه الثغرة من الجهة الأخرى — فاجتماع الاختبارين أقوى من كلٍّ منهما وحده.</div>''')
add(f'''<div class="note b"><span class="t">وثغرة رقابية حقيقية يجب إقفالها يوم الاستلام</span>
النظام يعمل بمستخدم واحد <span class="n">({I["users"][0]})</span> وصندوق واحد ({I["registers"][0]}).
أي أن كل عملية في {a(D["period"]["days"])} يومًا تُنسب إلى الحساب نفسه، ولا يمكن معرفة من نفّذها.
هذا مقبول لمالكٍ حاضر، وغير مقبول لمالكٍ غائب. <strong>أنشئ مستخدمًا باسم كل موظف من اليوم الأول.</strong></div>''')
add(f'''<h3 class="sub">وضع ضريبة القيمة المضافة — مفترق طريق</h3>
<p>كل فواتير المبيعات الـ{m(D["totals"]["invoices"])} بضريبة <strong>صفر</strong>. وفي المقابل، <strong>{D["purchases"]["with_vat"]} من {D["purchases"]["lines"]}</strong> سطر مشتريات يحمل ضريبة مدخلات مدفوعة. الجواب على سؤال واحد يحدد أيّ الحالتين أنت فيها:</p>
<table><thead><tr><th>الحالة</th><th>الأثر عليك</th><th class="f">المبلغ</th></tr></thead><tbody>
<tr><td>المؤسسة <strong>غير مسجّلة</strong></td><td>سليم نظاميًا — مبيعاتك السنوية المتوقعة {m(N["annual_at_plan"])} تحت حد الإلزام {m(N["vat_threshold"])}. لكنك تدفع ضريبة مدخلات ولا تستردّها، وهي محسوبة أصلًا داخل تكلفة المواد.</td><td class="f">صفر التزام</td></tr>
<tr class="lo"><td>المؤسسة <strong>مسجّلة</strong></td><td>ضريبة مخرجات غير محصَّلة على مبيعات الفترة، زائد غرامات تأخر. والمدة الكاملة أطول من فترة القياس.</td><td class="f neg">{m(D["vat_if_registered"]["on_period"])} ريال<br>({m(D["vat_if_registered"]["monthly"])} شهريًا)</td></tr>
</tbody></table>
<p>لا تفترض الجواب. اطلب <strong>شهادة التسجيل الضريبي أو ما يُثبت عدمه</strong> قبل التوقيع — وراجع القسم ١٥ لأن بنية الصفقة تحدد إن كان هذا الالتزام ينتقل إليك أصلًا.</p>''')
end()

# ══════════ 09 تكلفة المواد ══════════
sec("تكلفة المواد — بناء من أسعار الموردين",
    "لا تُقدَّر نسبة مئوية اعتباطية. تُبنى التكلفة من الكميات المقيسة مضروبةً في أسعار الوحدات من فواتير مورّديك.")
add('<h3 class="sub">أسعار الوحدات — من الفواتير</h3>')
add('<table class="sm"><thead><tr><th>الوحدة</th><th class="f">متوسط السعر</th><th>الاشتقاق</th></tr></thead><tbody>')
DERIV={"كرتون دجاج ١٠ كجم":"صافي ٨ كجم على السيخ – "+f'{U["كرتون دجاج ١٠ كجم"]/8:.2f} ريال/كجم',
 "كرتون لحم ١٠ كجم":"صافي ٨ كجم – "+f'{U["كرتون لحم ١٠ كجم"]/8:.2f} ريال/كجم',
 "كرتون بطاطس ١٠ كجم":f'{U["كرتون بطاطس ١٠ كجم"]/10:.2f} ريال/كجم',
 "تنكة زيت ١٧ لتر":f'{U["تنكة زيت ١٧ لتر"]/17:.2f} ريال/لتر',
 "كرتون مشروب ٢٤ علبة":f'{U["كرتون مشروب ٢٤ علبة"]/24:.2f} ريال/علبة — تُباع بـ٣',
 "كرتون عصير":f'{U["كرتون عصير"]/24:.2f} ريال/علبة — يُباع بـ٢'}
for k,v in U.items():
    add(f'<tr><td>{k}</td><td class="f">{v}</td><td>{DERIV.get(k,"")}</td></tr>')
add('</tbody></table>')
add(f'<h3 class="sub">التكلفة اليومية عند مستوى {m(E["rev_day"],0)} ريال</h3>')
add('<table><thead><tr><th>البند</th><th class="f">ريال/يوم</th><th class="f">من المبيعات</th><th>الأساس</th></tr></thead><tbody>')
BASIS={"دجاج":f'{MEAT["chicken_kg_entry"]} كجم × {U["كرتون دجاج ١٠ كجم"]/8:.2f} <span class="grade g-v">مقيس</span>',
 "لحم":f'{MEAT["beef_kg_entry"]} كجم × {U["كرتون لحم ١٠ كجم"]/8:.2f} <span class="grade g-v">مقيس</span>',
 "مشروبات":f'{N["drinks_day"]} علبة × سعر الفاتورة <span class="grade g-v">مقيس</span>',
 "خبز":f'{N["sandwiches_day"]} سندويتش × ٠٫٧٠ <span class="grade g-e">تقدير</span>',
 "خضار وصلصة":f'{N["sandwiches_day"]} × ٠٫٥٠ <span class="grade g-e">تقدير</span>',
 "ورق وتغليف":f'{N["sandwiches_day"]} × ٠٫٢٥ <span class="grade g-e">تقدير</span>',
 "بطاطس وزيت":f'{N["fries_day"]} صحن × التكلفة المشتقة <span class="grade g-v">مقيس</span>',
 "الفطور والمقبلات":'فلافل وبيض وكبدة <span class="grade g-e">تقدير</span>',
 "جبن":'حسب عدد الإضافات المسجّلة <span class="grade g-e">تقدير</span>',
 "غاز ومستهلكات":'من فواتير الغاز <span class="grade g-e">تقدير</span>'}
for k,v in N["materials"].items():
    add(f'<tr><td>{k}</td><td class="f">{v}</td><td class="f">{100*v/E["rev_day"]:.1f}%</td><td>{BASIS.get(k,"")}</td></tr>')
add(f'<tr class="tot"><td>إجمالي المواد</td><td class="f">{N["materials_day"]}</td><td class="f">{N["food_cost_pct"]}%</td><td>—</td></tr>')
add(f'<tr class="hi"><td>هامش المساهمة الناتج</td><td class="f">{E["rev_day"]-N["materials_day"]:.1f}</td><td class="f">{N["cm_pct_derived"]}%</td><td>كل ريال إضافي يترك {N["cm_pct_derived"]:.0f} هللة</td></tr></tbody></table>')
add(f'''<div class="note w"><span class="t">أستخدم {N["cm_pct_used"]:.0f}٪ في كل جداول هذه الدراسة، لا {N["cm_pct_derived"]}٪</span>
البناء أعلاه يعطي هامشًا أفضل، لكن أربعة من بنوده تقديرات (الخبز والخضار والفطور والجبن) لا فواتير.
<strong>اخترت الرقم الأسوأ عمدًا</strong> حتى لا تُبنى قرارات على فارق لم يُقس. الفارق في صالحك، فلا تنفقه قبل أن تثبته.
<br><br><strong>ما يثبته:</strong> صوّر كل فاتورة مشتريات لشهر كامل بعد الاستلام. حينها فقط تصبح نسبة تكلفة المواد رقمًا مقيسًا.</div>''')
add(f'''<h3 class="sub">تركّز الموردين — مخاطرة قائمة</h3>
<table class="sm"><thead><tr><th>المورّد</th><th class="f">قيمة المشتريات</th><th class="f">الحصة</th></tr></thead><tbody>''')
for s in D["suppliers"]:
    add(f'<tr><td>{s["name"] or "غير محدد"}</td><td class="f">{m(s["value"])}</td><td class="f">{s["pct"]}%</td></tr>')
add(f'<tr class="tot"><td>إجمالي المشتريات الموثقة</td><td class="f">{m(D["purchases"]["total"])}</td><td class="f">100%</td></tr></tbody></table>')
add(f'''<div class="note b"><span class="t">مورّد واحد يحمل {D["suppliers"][0]["pct"]}٪ من مشترياتك</span>
توقّفه أو تشديد شروطه أو رفع أسعاره ينتقل إليك كاملًا وفورًا، ولا بديل مجرَّب عندك.
<strong>الإجراء:</strong> اطلب عرضين من موردين منافسين في الشهر الأول — لا لتغيّر، بل لتملك بديلًا وسعرًا مرجعيًا.
كل نقطة مئوية توفّرها على هذا الحجم تساوي نحو ٩٠٠ ريال سنويًا، والقدرة على المفاوضة تبدأ من وجود بديل.</div>''')
end()

# ══════════ 10 الرواتب والثوابت ══════════
sec("الرواتب والتكاليف الثابتة",
    "الفريق ثلاثة كما يعمل المحل اليوم. وبندان فقط — المقابل المالي والسكن — يقرران إن كان المحل رابحًا أو خاسرًا.")
add('<h3 class="sub">الرواتب الأساسية</h3>')
add('<table><thead><tr><th>الوظيفة</th><th class="f">الراتب الشهري</th><th>ملاحظة</th></tr></thead><tbody>')
NOTE={"شيف تركي — شاورما":"المنتج كله بيده — أعلى راتب وأعلى خطر عند التبديل",
      "عامل هندي":"تحضير وخدمة","مشرف":"نفس راتب من يشرف عليه — راجع القسم ١٦"}
for s in N["staff"]:
    add(f'<tr><td>{s["role"]}</td><td class="f">{m(s["salary"])}</td><td>{NOTE[s["role"]]}</td></tr>')
base=sum(s["salary"] for s in N["staff"])
add(f'<tr class="tot"><td>إجمالي الرواتب الأساسية</td><td class="f">{m(base)}</td><td>ثلاثة عمّال</td></tr></tbody></table>')
add(f'''<div class="note"><span class="t">الراتب ليس التكلفة</span>
كل عامل وافد يحمل فوق راتبه سكنًا ومقابلًا ماليًا وتأمينات ومخصص نهاية خدمة.
التكلفة المحمّلة للفريق في الحالة الكاملة <strong>{m(base+1800+2400+110+319)}</strong> ريالًا — أي {100*(base+1800+2400+110+319)/base-100:.0f}٪ فوق الرواتب.
وفي حالتك المُعلَنة (بلا مقابل مالي ولا سكن) تنزل إلى <strong>{m(base+110+319)}</strong>.</div>''')
add('<h3 class="sub">التكاليف الثابتة الشهرية — ثلاث حالات</h3>')
add('<table><thead><tr><th>البند</th><th class="f">تكلفة كاملة</th><th class="f">بلا مقابل مالي</th><th class="f">بلا مقابل وسكن</th></tr></thead><tbody>')
for l in N["fixed_lines"]:
    z=lambda v: m(v) if v else "—"
    add(f'<tr><td>{l["name"]}</td><td class="f">{z(l["full"])}</td><td class="f">{z(l["nolevy"])}</td><td class="f">{z(l["nolevy_nohouse"])}</td></tr>')
add(f'<tr class="tot"><td>إجمالي الثوابت شهريًا</td><td class="f">{m(FX["full"])}</td><td class="f">{m(FX["nolevy"])}</td><td class="f">{m(FX["nolevy_nohouse"])}</td></tr>')
add(f'<tr class="tot"><td>أي يوميًا (٣٠ يومًا)</td><td class="f">{FX["full"]/30:.0f}</td><td class="f">{FX["nolevy"]/30:.0f}</td><td class="f">{FX["nolevy_nohouse"]/30:.0f}</td></tr></tbody></table>')
add(f'''<div class="note w"><span class="t">البند الذي يقلب النتيجة: السكن</span>
ثلاثة عمّال يسكنون في مكان ما. إن كان المحل يوفّره فهو تكلفتك ولو لم تدفعها نقدًا كل شهر.
وإن كانوا يسكنون على ترتيب يخصّ الكفيل الحالي، فالسؤال: <strong>هل ينتقل هذا الترتيب إليك؟</strong>
اكتب الجواب في العقد، لا في المجلس. الفارق بين العمودين الأخيرين {m(FX["nolevy"]-FX["nolevy_nohouse"])} ريالًا شهريًا.</div>''')
add(f'''<div class="note b"><span class="t">والمقابل المالي — فرضية تحمل الربح كله</span>
أفدتَ بأن التأشيرات وما يتصل بها بلا تكلفة عليك، وطلبتَ ألّا يُسأل عن التفصيل. التُزم بذلك، وعُرضت الحالات الثلاث بدل افتراض واحدة.
لكن الأثر يجب أن يُذكر صريحًا: <strong>{m(FX["full"]-FX["nolevy"])} ريالًا شهريًا</strong> هي الفارق، وهي أكبر من الربح المتوقع في معظم السيناريوهات.
احسب على {m(FX["nolevy"])} كحدٍّ أدنى، واعتبر الإعفاء مكسبًا قابلًا للزوال بتغيّر النظام. <span class="grade g-c">منقول</span></div>''')
end()

# ══════════ 11 التعادل ══════════
sec("نقطة التعادل",
    f"المبيعات اليومية التي تغطي كل التكاليف بلا ربح ولا خسارة، بهامش مساهمة {N['cm_pct_used']:.0f}٪.")
add(f'''<table><thead><tr><th>الحالة</th><th class="f">الثوابت شهريًا</th><th class="f">÷ هامش {N["cm_pct_used"]:.0f}٪</th><th class="f">÷ ٣٠ يومًا</th><th class="f">نقطة التعادل</th></tr></thead><tbody>
<tr><td>تكلفة كاملة</td><td class="f">{m(FX["full"])}</td><td class="f">{m(FX["full"]/0.55)}</td><td class="f">÷ 30</td><td class="f neg">{BE["full"]} ريال/يوم</td></tr>
<tr><td>بلا مقابل مالي</td><td class="f">{m(FX["nolevy"])}</td><td class="f">{m(FX["nolevy"]/0.55)}</td><td class="f">÷ 30</td><td class="f">{BE["nolevy"]} ريال/يوم</td></tr>
<tr class="hi"><td>بلا مقابل مالي ولا سكن</td><td class="f">{m(FX["nolevy_nohouse"])}</td><td class="f">{m(FX["nolevy_nohouse"]/0.55)}</td><td class="f">÷ 30</td><td class="f pos">{BE["nolevy_nohouse"]} ريال/يوم</td></tr>
</tbody></table>''')
add(f'''<dl class="kpis">
 <div class="kpi r"><dt>نقطة الدخول اليوم</dt><dd>{m(E["rev_day"],0)}<span>ريال/يوم</span></dd></div>
 <div class="kpi"><dt>مقابل التعادل الأدنى</dt><dd>{BE["nolevy_nohouse"]}<span>ريال/يوم</span></dd></div>
 <div class="kpi"><dt>الفجوة للتعادل الأوسط</dt><dd>{BE["nolevy"]-round(E["rev_day"])}<span>ريال/يوم</span></dd></div>
 <div class="kpi"><dt>الفجوة للتعادل الأعلى</dt><dd>{BE["full"]-round(E["rev_day"])}<span>ريال/يوم</span></dd></div>
</dl>''')
add(f'''<div class="note"><span class="t">كيف تقرأ هذه الأرقام</span>
عند مستواك الحالي ({m(E["rev_day"],0)} ريالًا) أنت <strong>فوق</strong> التعادل الأدنى بـ{round(E["rev_day"])-BE["nolevy_nohouse"]} ريالًا، و<strong>تحت</strong> التعادل الأوسط بـ{BE["nolevy"]-round(E["rev_day"])}.
أي أن ربحيتك اليوم تتوقف حرفيًا على صحة فرضيتَي المقابل المالي والسكن. القسم التالي يبيّن كيف تخرج من هذا الحدّ.</div>''')
end()

# ══════════ 12 المسار ══════════
sec("مسار الاستعادة والربحية",
    "كل خطوة أدناه استعادةٌ لشيء فعله هذا المحل بالفعل هذه السنة — لا رهان على نمو جديد.")
chart(charts.waterfall(N), "مسار المبيعات اليومية، وتحت كل عمود الصافي الشهري في حالة «بلا مقابل مالي ولا سكن».")
add('<table><thead><tr><th>الخطوة</th><th class="f">ريال/يوم</th><th class="f">تكلفة كاملة</th><th class="f">بلا مقابل</th><th class="f">بلا مقابل وسكن</th></tr></thead><tbody>')
for i,p in enumerate(PATH):
    cls=' class="hi"' if i==3 else (' class="lo"' if i==0 else "")
    f=lambda v: f'<td class="f {"pos" if v>0 else "neg"}">{v:+,}</td>'
    add(f'<tr{cls}><td>{p["label"]}</td><td class="f">{m(p["rev_day"])}</td>{f(p["full"])}{f(p["nolevy"])}{f(p["nolevy_nohouse"])}</tr>')
add(f'<tr class="tot"><td>نقطة التعادل المطلوبة</td><td class="f">—</td><td class="f">{BE["full"]}</td><td class="f">{BE["nolevy"]}</td><td class="f">{BE["nolevy_nohouse"]}</td></tr></tbody></table>')
add(f'''<div class="note o"><span class="t">الصف المظلَّل هو خطتك الواقعية</span>
عند <strong>{m(PATH[3]["rev_day"])}</strong> ريالًا يوميًا — وهو <strong>أقل</strong> من مستوى أبريل المثبت بـ{m(APR["rev_day"]-PATH[3]["rev_day"],0)} ريالًا —
تربح <strong>{m(PATH[3]["nolevy"])}</strong> إلى <strong>{m(PATH[3]["nolevy_nohouse"])}</strong> ريالًا شهريًا.
استرداد الثلاثين ألفًا في <strong>{a(N["payback"]["best_months"])} إلى {a(N["payback"]["mid_months"])} شهرًا</strong>.</div>''')
add(f'''<div class="note b"><span class="t">وعمود التكلفة الكاملة يبقى سالبًا ({m(PATH[3]["full"])})</span>
لا يصبح موجبًا إلا بعودة كاملة لمستوى أبريل. أي أن ربحك يقع كله داخل فرضية أن المقابل المالي لا يُدفع.
<strong>اكتب هذه الجملة على ورقة اليوم:</strong> «أربح فقط ما دام المقابل المالي لا يُدفع» — وراجعها كلما تغيّر النظام.</div>''')
add(f'''<h3 class="sub">سيولة الصيف — خطّط لها من الآن</h3>
<p>يوليو وأغسطس القادمان قد يعودان إلى نحو <span class="ltr">{m(MO[4]["rev_day"],0)}–{m(MO[3]["rev_day"],0)}</span> ريالًا يوميًا إن كان جزء من الهبوط موسميًا فعلًا.
عند ذلك المستوى تستهلك الشهرين نقدًا حتى في أفضل حالة تكلفة:</p>
<table class="sm"><thead><tr><th>المستوى</th><th class="f">تكلفة كاملة</th><th class="f">بلا مقابل</th><th class="f">بلا مقابل وسكن</th></tr></thead><tbody>''')
for lab,rev in [("يوليو المسجَّل",MO[3]["rev_day"]),("أغسطس المسجَّل",MO[4]["rev_day"])]:
    c=rev*30*0.55
    add(f'<tr><td>{lab} — {m(rev,0)} ريال/يوم</td>'
        + "".join(f'<td class="f {"pos" if c-v>0 else "neg"}">{c-v:+,.0f}</td>' for v in FX.values()) + '</tr>')
add('</tbody></table>')
add(f'''<div class="note w"><span class="t">ادّخر من موسم الشتاء والربيع</span>
أشيع سبب لإغلاق مطاعم <em>رابحة سنويًا</em> هو نفاد النقد في موسمها الضعيف. خصّص من كل شهر قوي احتياطًا للصيف، ولا تسحب كامل الربح.</div>''')
end()

# ══════════ 13 خطة الرفع ══════════
sec("خطة الرفع — خمسة إجراءات",
    f"تكلفتها مجتمعة دون مئتي ريال، وأثرها المحسوب +{m(N['plan_total'])} ريالًا شهريًا. كل رقم مشتق من كمياتك المقيسة وهوامشك الفعلية.")
add('<table><thead><tr><th>الإجراء</th><th class="f">الوضع اليوم</th><th class="f">الهدف</th><th class="f">الأثر/يوم</th><th class="f">الأثر/شهر</th></tr></thead><tbody>')
for p in PLAN:
    now=f'{p["now"]} حبة/يوم' if "رفع سعر" in p["name"] else f'{p["now"]}%'
    tgt="+1 ريال" if "رفع سعر" in p["name"] else f'{p["target"]}%'
    add(f'<tr><td>{p["name"]}</td><td class="f">{now}</td><td class="f">{tgt}</td>'
        f'<td class="f">+{p["gain_day"]}</td><td class="f pos">+{m(p["gain_month"])}</td></tr>')
add(f'<tr class="tot"><td>المجموع</td><td class="f">—</td><td class="f">—</td><td class="f">+{N["plan_rev_day"]} إيرادًا</td><td class="f pos">+{m(N["plan_total"])}</td></tr></tbody></table>')
add(f'''<div class="note o"><span class="t">لماذا هذان الصنفان بالذات لرفع السعر</span>
«شاورما صاروخ خبز تركي» و«شاورما عربي» هما الأكثر مبيعًا بعد الشامي الصغير، وسعراهما {a(9)} و{a(12)} ريالًا.
رفع ريال واحد يعني زيادة {100/9:.0f}٪ و{100/12:.0f}٪ — وهي نسب يتحمّلها السوق عادةً بلا انصراف ملحوظ.
والأثر يصل إلى الصافي كاملًا لأن تكلفة المواد لا تتغيّر بريال البيع.</div>''')
add(f'''<div class="note w"><span class="t">ولا تمسّ «شاورما خبز شامي صغير» عند خمسة ريالات</span>
هو أكثر أصنافك بالعدد ({a(D["items"][2]["qty_day"])} حبة يوميًا) وأرخصها — أي أنه <strong>جالب الزبون لا مصدر الربح</strong>.
رفعه ريالًا زيادة {100/5:.0f}٪ على أحسّ صنف بالسعر عندك. اتركه طُعمًا، واربح على ما يُضاف إليه.</div>''')
add(f'''<h3 class="sub">الإرفاق — أين المال الحقيقي</h3>
<p>{a(D["attach"]["single"])}٪ من فواتيرك صنف واحد. هذه ليست مشكلة منيو بل جملة لا تُقال. النص المطلوب من الكاشير، بهذا الترتيب:</p>
<ol class="steps">
<li><b>«معه بيبسي؟»</b><span>لا تسأل «تبي شي ثاني؟» — سؤال مفتوح جوابه «لا». سؤال مغلق باسم منتج محدد يرفع معدل القبول أضعافًا. الهدف: من {D["attach"]["drink"]}٪ إلى ٥٥٪.</span></li>
<li><b>«صحن بطاطس معه؟»</b><span>أضعف رقم عندك ({D["attach"]["fries"]}٪) وأعلى هامش بالريال ({5-2.26:.2f} ريالًا للصحن). الهدف ١٨٪.</span></li>
<li><b>«جبن فيه؟ بريال»</b><span>تكلفة الجبن أقل من نصف ريال. الهدف من {D["attach"]["cheese"]}٪ إلى ٣٢٪.</span></li>
<li><b>اربط الحافز بالتنفيذ</b><span>عمولة المشرف في القسم ١٦ مبنية على المبيعات المسجَّلة — وهي ما يجعل هذه الجمل تُقال فعلًا وأنت غائب.</span></li>
</ol>''')
add(f'''<div class="note"><span class="t">ترتيب التنفيذ</span>
ابدأ بـ<strong>استعادة الساعات</strong> (القسم ٠٥) لأنها أكبر أثرًا وأقل خطرًا — {m(D["bands"][0]["gap_month"]+D["bands"][1]["gap_month"])} ريالًا شهريًا بلا أي تغيير في المنتج أو السعر.
ثم الإرفاق. وأجّل <strong>رفع الأسعار</strong> إلى الشهر الثالث: لا ترفع السعر وأنت تستعيد زبائن غادروا.</div>''')
end()

# ══════════ 14 النقد ══════════
C=N["cash"]
sec("النقد المطلوب وهيكل الدفع",
    "ما تحتاجه فعلًا لإتمام الصفقة وتشغيل المحل، وكيف تدفعه بحيث تشتري حق التراجع.")
add('<table><thead><tr><th>البند</th><th class="f">المبلغ</th><th>الأساس</th></tr></thead><tbody>')
BAS={"ثمن المحل شامل المعدات":"السعر المطروح — لم يصل جرد يُثبت قيمة المعدات <span class=\"grade g-c\">منقول</span>",
 "نقل الرخص والسجل التجاري":"تقدير <span class=\"grade g-e\">تقدير</span>",
 "تأمين الإيجار (شهر)":"شهر واحد بقيمة الإيجار",
 "رأس مال تشغيلي":"يغطي شهرين محتملَي خسارة + تداخل الطاهي شهرًا"}
for l in C["lines"]:
    add(f'<tr><td>{l["name"]}</td><td class="f">{m(l["v"])}</td><td>{BAS[l["name"]]}</td></tr>')
add(f'<tr class="tot"><td>إجمالي المطلوب</td><td class="f">{m(C["total"])}</td><td>—</td></tr>')
add(f'<tr><td>المتاح لديك</td><td class="f">{m(C["available"])}</td><td>إفادتك</td></tr>')
add(f'<tr class="lo"><td>المتبقي احتياطًا</td><td class="f neg">{m(C["left"])}</td><td>لا شيء عمليًا</td></tr></tbody></table>')
add(f'''<div class="note b"><span class="t">أخطر سطر في الجدول: الاحتياطي {m(C["left"])} ريال</span>
مصفوفة القسم ١٢ تقول إنك قد تخسر {m(abs(PATH[0]["full"]))} ريالًا شهريًا في الحالة غير المواتية.
شهر واحد أسوأ من المتوقع، أو عطل في شواية، أو تأخّر الشيف التركي أسبوعين — يُخرجك عن الخطة كليًا.
<strong>لا تدفع الثلاثين دفعة واحدة.</strong></div>''')
add(f'''<h3 class="sub">هيكل الدفع المقترح</h3>
<ol class="steps">
<li><b>{m(15000)} ريال عند التوقيع</b><span>نصف الثمن مقابل التسليم الفعلي: المفاتيح والمعدات بجرد موقَّع والسجل.</span></li>
<li><b>{m(7500)} ريال بعد ٦٠ يومًا — بشرط متوسط ٧٠٠ ريال/يوم</b><span>العتبة مرفوعة عمدًا: شهراك الأولان يقعان خارج الصيف، فعتبة منخفضة كانت ستمرّ بلا أن تختبر شيئًا. سبعمئة تختبر فعلًا أن الاستعادة تعمل.</span></li>
<li><b>{m(7500)} ريال بعد ١٢٠ يومًا</b><span>مشروطة بانتقال العمالة فعليًا وسريان عقد «إيجار» باسمك.</span></li>
<li><b>اكتب في العقد صراحة</b><span>«الأجرة {m(2000)} ريال شاملة استهلاك الكهرباء والمياه بلا سقف طوال مدة العقد» — مع اسم صاحب العدّاد. وكذلك ترتيب سكن العمالة.</span></li>
</ol>''')
add(f'''<div class="note o"><span class="t">أثر الهيكل</span>
يبقى بيدك <strong>{m(15000)} ريالًا نقدًا</strong> في الشهرين الأولين — وهما بالضبط الشهران اللذان قد تخسر فيهما.
تشتري بذلك <strong>حق التراجع</strong>، وهو أرخص تأمين متاح لك. والبائع صديقك وميسور وعدم تفرّغه هو سبب البيع — فحجّة «أبي فلوسي الآن» لا تنطبق، ورفضه التجزئة هو نفسه معلومة.</div>''')
add(f'''<h3 class="sub">اعتمادك على تنازل شخص واحد</h3>
<table><thead><tr><th>السيناريو</th><th class="f">إيجار + مرافق</th><th class="f">الصافي شهريًا عند خطة الرفع</th></tr></thead><tbody>
<tr class="hi"><td>الترتيب الحالي (المؤجّر صديقك)</td><td class="f">{m(2000)}</td><td class="f pos">+{m(PATH[3]["nolevy_nohouse"])}</td></tr>
<tr class="lo"><td>إيجار سوق ومرافق مدفوعة</td><td class="f">{m(6300)}</td><td class="f neg">{PATH[3]["nolevy_nohouse"]-4300:+,}</td></tr>
</tbody></table>
<p>الفارق {m(4300)} ريال شهريًا — <strong>أكبر من ربحك كله</strong>. بلا هذا الترتيب لا يوجد مشروع أصلًا.
وهذا ليس سببًا للتراجع، بل سبب لتحويل الجميل إلى حق مكتوب.</p>''')
add(f'''<div class="note w"><span class="t">واحمِ الصداقة بالانضباط</span>
ادفع الأجرة في موعدها تحويلًا بنكيًا موثّقًا، لا نقدًا ولا تأجيلًا. أسرع طريق لفقد التنازل أن يصبح صديقك دائنًا متعثرًا.
واستردادك المتوقع {a(N["payback"]["best_months"])}–{a(N["payback"]["mid_months"])} شهرًا، فالسؤال ليس «هل تدوم العلاقة عشر سنوات؟» بل «هل تدوم سنة ونصفًا؟» — وهو سؤال أسهل بكثير.</div>''')
end()

# ══════════ 15 بنية الصفقة ══════════
sec("بنية الصفقة القانونية",
    "«شراء المحل» عبارة تخفي ثلاثة مسارات مختلفة جذريًا في المسؤولية. الفرق بينها قد يساوي أكثر من سعر الصفقة.")
add('''<table><thead><tr><th>&nbsp;</th><th>نقل مؤسسة البائع إليك</th><th>سجل جديد باسمك</th></tr></thead><tbody>
<tr><td>ضريبة قيمة مضافة غير مسدّدة</td><td class="neg">تلاحق السجل</td><td class="pos">تبقى مع البائع</td></tr>
<tr><td>مستحقات التأمينات والعمال</td><td class="neg">تنتقل إليك</td><td class="pos">تبقى مع البائع</td></tr>
<tr><td>مخالفات بلدية متراكمة</td><td class="neg">تنتقل إليك</td><td class="pos">تبقى مع البائع</td></tr>
<tr><td>حساب التوصيل وتقييماته</td><td class="pos">يُحتفظ به</td><td class="neg">يبدأ من الصفر</td></tr>
<tr><td>الرخص والتصاريح</td><td class="pos">قائمة وسارية</td><td class="neg">إصدار جديد — أسابيع بلا إيراد</td></tr>
<tr><td>نقل كفالة العمالة</td><td class="pos">أسهل</td><td class="neg">يتبع نطاقات منشأتك</td></tr>
</tbody></table>''')
add(f'''<div class="note o"><span class="t">والمسار الثالث الأنظف: شراء أصول</span>
لأن المعدات ضمن السعر، تستطيع ألّا تنقل المؤسسة ولا تشتري «المحل» — بل تشتري <strong>المعدات</strong> بعقد بيع يسرد كل قطعة،
وتوقّع إيجارك مباشرة مع صديقك المؤجّر، وتفتح سجلك التجاري.
حينها <strong>لا ينتقل إليك شيء من ماضيه النظامي</strong>: لا ضريبة ولا تأمينات ولا مخالفات.</div>''')
add(f'''<div class="note w"><span class="t">وثمن هذا المسار بندان — سعّرهما قبل أن تختار</span>
حساب التوصيل وتقييماته يبدأ من الصفر (اطلب كشف حساب المتجر لتعرف حجمه)، والرخص الجديدة تستغرق أسابيع برواتب تجري وبلا إيراد.
قابِل هذين البندين بحجم الالتزام الضريبي المحتمل في القسم ٠٨ ({m(D["vat_if_registered"]["on_period"])} ريالًا على فترة القياس وحدها) ثم قرّر.</div>''')
add('''<div class="note"><span class="t">التوصية</span>
<strong>شراء أصول بسجل جديد باسمك</strong> — إلا أن يُثبت البائع الخلوّ بمخالصة من الهيئة وشهادة تأمينات سارية.
وأنت في أفضل موضع للطلب، ومن يملك ملاءة لا يتعثّر في احتجاز عشرة آلاف ريال ستين يومًا.
<strong>راجع هذا القسم مع محاسب قانوني قبل التوقيع</strong> — فهو الوحيد في هذه الوثيقة الذي يحتاج رأيًا مهنيًا مرخَّصًا لا تحليل بيانات.</div>''')
end()

# ══════════ 16 المشرف ══════════
sec("حافز المشرف والرقابة اليومية",
    "أنت لن تكون حاضرًا. هذا القسم هو ما يحلّ محلّ حضورك — وقد أثبتت البيانات أنه ليس تفصيلًا.")
add(f'''<div class="note b"><span class="t">خطر لا يُرى إلا في الأرقام</span>
مشرفك يتقاضى <strong>نفس راتب من يشرف عليه</strong> — {m(1500)} ريال مثل العامل الهندي.
فإن لم تكن العمولة حقيقية فهو عامل ثالث باسم آخر، وأنت تسلّمه محلًا وأنت غائب.</div>''')
add(f'''<h3 class="sub">الصيغة: ٥٪ على كل ريال يُسجَّل في رواء فوق ٦٠٠ ريال يوميًا</h3>
<table><thead><tr><th>المبيعات/يوم</th><th class="f">عمولته شهريًا</th><th class="f">دخله الكلي</th><th class="f">فوق العامل</th><th>تكلفتها عليك</th></tr></thead><tbody>''')
for rev in [620, PATH[1]["rev_day"], PATH[3]["rev_day"], 900]:
    com=max(0,(rev-600))*0.05*30
    cls = ' class="hi"' if rev==PATH[3]["rev_day"] else ""
    pay = 100*com/(rev*30*0.55)
    add(f'<tr{cls}><td>{m(rev)}</td><td class="f">{m(com,0)}</td>'
        f'<td class="f">{m(1500+com,0)}</td><td class="f">{100*com/1500:.0f}%</td>'
        f'<td>تُسدَّد برفع {pay:.1f}٪ فقط من المبيعات</td></tr>')
add('</tbody></table>')
add(f'''<div class="note o"><span class="t">لماذا ٦٠٠ بالذات</span>
عتبة واحدة طوال السنة عمدًا: تكاد لا تُصرف في شهر ضعيف، وتُصرف بسخاء في شهر قوي — فتدفع الحافز من الموسم الذي يموّله.
والأهم أنها تجعل المشرف <strong>مستفيدًا من تسجيل كل بيع</strong> لا من إخفائه — وهو ما يحمي سلامة السجل التي اعتمدت عليها هذه الدراسة كلها.</div>''')
add(f'''<div class="note w"><span class="t">ولا ترفع العتبة أعلى من ذلك</span>
حافز لا يُصرف أبدًا ليس حافزًا — هو وعد يفقد مصداقيته في الشهر الثاني، ومعه تفقد أنت أداة الرقابة الوحيدة المتاحة لك وأنت غائب.</div>''')
add(f'''<h3 class="sub">لوحة الرقابة اليومية — خمس دقائق مساءً</h3>
<ol class="steps">
<li><b>مستخدم باسم كل موظف في رواء</b><span>اليوم يعمل النظام بحساب واحد ({D["integrity"]["users"][0]})، فلا يمكن معرفة من نفّذ أي عملية. هذا أول ما يُقفل يوم الاستلام.</span></li>
<li><b>إقفال وردية يومي إلزامي</b><span>يُقارن النقد المعدود بالمسجَّل. الفروقات تظهر يومًا بيوم لا شهرًا بشهر.</span></li>
<li><b>تقرير المبيعات يصلك على جوالك كل ليلة</b><span>رقم واحد: المبيعات المسجَّلة. وثانٍ: وقت أول بيعة — وهو مؤشر فتح المحل في موعده، وقد رأيت في القسم ٠٤ ماذا يحدث حين ينزلق.</span></li>
<li><b>مطابقة شهرية بالإيداعات البنكية</b><span>نحو {100-D["payments"][1]["pct"]:.0f}٪ من مبيعاتك عبر الشبكة وتُسوَّى بنكيًا. قارن مجموع التسويات بمبيعات النظام — انحراف متكرر إشارة تستحق السؤال.</span></li>
<li><b>أدخل أسعار التكلفة لكل صنف في رواء</b><span>النظام اليوم يعرض «إجمالي الربح» مساويًا للمبيعات لأن أسعار التكلفة غير مُدخلة — أي أن أحدًا لا يعرف ربح أي صنف. إدخالها يحوّل النظام من صندوق نقد إلى أداة إدارة.</span></li>
</ol>''')
end()

# ══════════ 17 المخاطر ══════════
sec("المخاطر مرتبة بالأثر",
    "كل مخاطرة أدناه نشأت من رقم أو ثغرة في البيانات، لا من تحوّط عام.")
RISKS=[
 ("r1","حرج","الموسمية غير مفصولة عن الإهمال",
  f"المبيعات هبطت من {m(APR['rev_day'],0)} إلى {m(AUG['rev_day'],0)} ريالًا. قرأتُ السبب انسحابًا للمالك — وهو متسق مع تقصير الساعات وسبب البيع المعلن. لكن رواء لا يحمل سنة سابقة، فلا أستطيع الفصل قطعيًا بين صيف تبوك والإهمال. ولو كانت القراءة معكوسة — أن ضعف الطلب هو ما دفعه للتقصير — فالمسار كله يحتاج مراجعة.",
  "اسأل البائع سؤال القسم ١٩ الأول. وأكتوبر ونوفمبر يحسمانهما نهائيًا — وشرط الستين يومًا في القسم ١٤ هو ما يحوّل هذا الغموض إلى اختبار مدفوع الثمن سلفًا."),
 ("r1","حرج","المقابل المالي ليس صفرًا",
  f"كل ربحية هذه الدراسة تقع داخل فرضية أن المقابل المالي لا يُدفع. إن كان {m(800)} ريال لكل عامل واقعًا، فالثوابت {m(FX['full'])} والتعادل {BE['full']} ريالًا — وهو مستوى لم يبلغه المحل إلا في أبريل.",
  f"احسب على {m(FX['nolevy'])} كحدٍّ أدنى، واعتبر الإعفاء مكسبًا مؤقتًا قابلًا للزوال. ولا تبنِ التزامات طويلة على فارق الـ{m(FX['full']-FX['nolevy'])} ريال."),
 ("r1","حرج","تبديل الفريق كاملًا في وقت هشّ",
  "الشيف هو المنتج في محل شاورما، والمبيعات تتبع يده لا لافتتك. والتعافي الجاري في آخر أربعة أسابيع صنعه الفريق الحالي — فتبديله الآن يخاطر بإطفاء الشيء الوحيد الذي يعمل.",
  f"تداخُل أسبوعين على الأقل بين الشيف المغادر والقادم. ادفع للاثنين معًا — نحو {m(2000)} ريال تأمينًا على إيراد شهري يتجاوز {m(PATH[3]['rev_day']*30)} ريالًا."),
 ("r2","مرتفع","عقد الإيجار — مدته وانتقاله",
  f"الإيجار {m(2000)} ريال شاملًا المرافق هو ما يجعل الخطة ممكنة، ومصدره صداقة شخصية لا سعر سوق. لم تصل نسخة عقد ولا مدة متبقية. وسقف التحمّل مبيّن في القسم ١٤: إيجار سوق يقلب الربح إلى خسارة.",
  "عقد تجاري موثّق في «إيجار» باسمك، خمس سنوات لا ثلاث، وسقف زيادة عند التجديد لا يتجاوز ١٠٪، وسطر صريح بشمول المرافق. اطلبها الآن وحسن النية في ذروته — لا بعد سنة."),
 ("r2","مرتفع","المعدات غير مقيَّمة ولا موثّقة الملكية",
  "تدفع ثلاثين ألفًا «شاملة المعدات» بلا ورقة تُثبت ما تملكه. وشائع في هذا القطاع أن مبردات المشروبات والمثلجات ملك الموردين تُسترد عند انتهاء التعامل، وأن بعض التجهيزات مقسّطة أو ملك المؤجّر ضمن العين.",
  f"جرد موقَّع قبل الدفع، بعمودَي «المالك» و«الحالة»، وفحص فني للشوايات والتبريد والتكييف تدفع أنت ثمنه. ثم سعّره لدى تاجر معدات مستعملة — رقمه هو أرضية خسارتك."),
 ("r2","مرتفع","هامش المساهمة أقل من المفترض",
  f"أربعة من بنود تكلفة المواد تقديرات لا فواتير. كل انخفاض نقطة مئوية في الهامش يرفع التعادل نحو {FX['nolevy']/0.55/30 - FX['nolevy']/0.56/30:.0f}–{FX['full']/0.54/30-FX['full']/0.55/30:.0f} ريالات يوميًا.",
  "صوّر كل فاتورة مشتريات لشهر كامل بعد الاستلام. شهر واحد يحوّل هذا البند من تقدير إلى قياس."),
 ("r2","مرتفع","مورّد واحد يحمل ٨٤٪ من المشتريات",
  f"شركة دار السالمين = {m(D['suppliers'][0]['value'])} ريالًا من {m(D['purchases']['total'])}. توقّفها أو رفع أسعارها ينتقل إليك كاملًا وفورًا بلا بديل مجرَّب.",
  "اطلب عرضين من موردين منافسين في الشهر الأول — لتملك بديلًا وسعرًا مرجعيًا، لا لتغيّر بالضرورة."),
 ("r2","مرتفع","الوضع الضريبي غير محسوم",
  f"كل فواتير البيع بضريبة صفر، بينما {D['purchases']['with_vat']} من {D['purchases']['lines']} سطر مشتريات يحمل ضريبة مدخلات. إن كانت المؤسسة مسجّلة فالالتزام نحو {m(D['vat_if_registered']['on_period'])} ريال على فترة القياس وحدها زائد غرامات.",
  "شهادة التسجيل الضريبي أو ما يُثبت عدمه، قبل التوقيع. وبنية «شراء أصول» في القسم ١٥ تعزل هذا الالتزام عنك أصلًا."),
 ("r3","متوسط","مستخدم واحد في النظام بلا تتبع",
  f"كل عمليات {a(D['period']['days'])} يومًا تُنسب إلى حساب واحد ({D['integrity']['users'][0]}). مقبول لمالكٍ حاضر، غير مقبول لمالكٍ غائب.",
  "مستخدم باسم كل موظف وإقفال وردية يومي من اليوم الأول — القسم ١٦."),
 ("r3","متوسط","الصفقة مع صديق",
  "البائع والمؤجّر كلاهما صديقك. هذا يخفض التكلفة ويرفع خطرًا آخر: الترتيبات الشفهية لا تُنفَّذ عند الخلاف، والخلاف مع صديق أصعب لا أسهل.",
  "كل تنازل يُكتب. الصداقة سبب للكتابة لا مبرر لتركها."),
]
for c,lab,t,body,fix in RISKS:
    add(f'<div class="risk {c}"><div class="rh">{t}<span class="rl">{lab}</span></div>'
        f'<p>{body}</p><div class="fx"><b>الإجراء:</b> {fix}</div></div>')
end()

# ══════════ 18 معيار الإيقاف ══════════
sec("معيار الإيقاف",
    "يُكتب قبل الدخول لأنه لا يُكتب بعده. المشاريع لا تُقتل بقرار خاطئ، بل بغياب لحظة يقول فيها صاحبها «كفى».")
add(f'''<div class="kill">
<p>ضع هذا أمامك واحسبه في نهاية كل شهر:</p>
<div class="rule">إذا مرّ <strong>الشهر الرابع</strong> — وكلها أشهر خارج الصيف —<br>
والمتوسط اليومي دون <strong>٧٠٠ ريال</strong>، بعد تنفيذ استعادة الساعات وخطة الرفع كاملة،<br>
فالتشخيص لم يكن صحيحًا، وعليك البيع أو الإغلاق.</div>
<p><strong>لماذا ٧٠٠:</strong> هي أقل من مستوى أبريل المثبت ({m(APR["rev_day"],0)})، وأقل من هدف خطة الرفع ({m(PATH[3]["rev_day"])})، وفوق تعادلك الأوسط ({BE["nolevy"]}) بقليل.
وأشهرك الأربعة الأولى — لو استلمت في أكتوبر — كلها خارج الموسم الضعيف. إن لم تبلغها في موسم جيد فأنت لا تدير محلًا ضعيفًا، بل تموّل خسارة.</p>
<p><strong>ولا تطبّق هذا المعيار على شهر صيفي.</strong> لو استلمت في الربيع وجاء يوليو دون ٧٠٠، فذلك موسم لا فشل — والمعيار حينها يُقاس على اثني عشر شهرًا كاملة.</p>
<p><strong>ولا تحرّك الرقم لأسفل حين تقترب منه.</strong> هذه أشيع طريقة يخسر بها الناس رؤوس أموالهم.</p>
</div>''')
add(f'''<h3 class="sub">وخسارتك عند الإيقاف ليست ثلاثين ألفًا</h3>
<p>لو أوقفت عند الشهر الرابع، تكون قد دفعت {m(15000)} أو {m(22500)} ريالًا بحسب الهيكل المرحلي (لا {m(30000)})،
وخسائر تشغيل تراكمية، مقابل معدات وسجل أربعة أشهر موثّق تستطيع البيع بهما.
<strong>هذا بالضبط ما يشتريه لك تقسيط الثمن.</strong></p>''')
end()

# ══════════ 19 أسئلة البائع ══════════
sec("ما تسأل البائع عنه",
    "ستة أسئلة. كلها نشأت من رقم أو تناقض في بياناتك، لا من سوء ظنّ. والصيغة مقترحة كما تُقال.")
Q=[("«ليش قصّرت ساعات الفتح من يونيو؟ ووش سبب إيقاف سيخ اللحم؟»",
  f"أهم سؤال في القائمة. البيانات تُظهر أن المحل كان يفتح {O['april']['open']} في أبريل و{O['august']['open']} في أغسطس، وأن اللحم توقّف في يونيو وعاد في سبتمبر. <strong>جواب «عمالة غادرت» يعني مشكلة تشغيلية قابلة للحل بتوظيف، وتشخيص هذه الدراسة صحيح. وجواب «ما كان فيه زباين» يعني أن السبب والنتيجة معكوسان وأن المسار كله يحتاج مراجعة.</strong>"),
 ("«هل المؤسسة مسجّلة في ضريبة القيمة المضافة؟ أبي شهادة التسجيل أو ما يُثبت عدمه»",
  f"مفترق طريق يغيّر رقمًا كبيرًا: إن كانت مسجّلة فهناك ضريبة مخرجات غير محصَّلة تقارب {m(D['vat_if_registered']['on_period'])} ريال على فترة القياس وحدها. لا تفترض الجواب."),
 ("«جرد المعدات موقَّعًا، وفيه عمود: مملوك للمحل / مملوك للمؤجّر / مستأجر من المورّد»",
  "تدفع ثلاثين ألفًا «شاملة المعدات» بلا ورقة واحدة تُثبت ما ستملكه. وإن كانت الثلاجة أو المشواة للمؤجّر أو للمورّد، اشتريت هواءً."),
 ("«عقد الإيجار الحالي ومدته المتبقية»",
  "القيمة كلها في هذا العقد. إن كانت مدته المتبقية ستة أشهر فأنت لا تشتري محلًا — تشتري ستة أشهر."),
 ("«براءة ذمة من الزكاة والدخل ومن التأمينات الاجتماعية، ومخالصات العمال»",
  "بتاريخ لا يتجاوز سبعة أيام. ومعها استعلام مخالفات بلدية وكشف مديونية عدّاد الكهرباء — فمتأخرات الكهرباء تلاحق العدّاد لا المستأجر السابق."),
 ("«ورق سكن العمالة — وين يسكنون وعلى حساب مين؟»",
  f"الفارق بين وجود هذا الترتيب وغيابه {m(1800)} ريال شهريًا، وهو أكبر من الربح في عدة سيناريوهات. اكتب الجواب في العقد.")]
add('<ol class="steps">')
for q,w in Q: add(f'<li><b>{q}</b><span>{w}</span></li>')
add('</ol>')
end()

# ══════════ 20 الحدود ══════════
sec("حدود هذه الدراسة",
    "ما لا تغطيه الأرقام أعلاه، مذكورًا صراحة حتى لا يُبنى عليه قرار.")
LIM=["<strong>الموسمية غير قابلة للفصل عن الإهمال.</strong> نظام رواء لا يحمل سنة سابقة، فلا يمكن القول كم من هبوط أبريل إلى أغسطس سببه الصيف وكم سببه تقصير الساعات. أكتوبر ونوفمبر يحسمانها ولا شيء قبلهما.",
 "<strong>«أبريل = التشغيل الكامل» افتراض مني.</strong> أبريل هو الشهر التالي لعيد الفطر وقد يحمل ارتفاعًا موسميًا لا يتكرر. استعادة مستواه ليست مضمونة حتى بتشغيل كامل.",
 "<strong>سبب تقصير الساعات غير معلوم.</strong> قرأتُه انسحابًا للمالك، والعكس ممكن. سؤال القسم ١٩ الأول يحسم الاتجاه، وقراءتي كلها تتغيّر بجوابه.",
 f"<strong>تكلفة المواد نصفها مقيس ونصفها مقدَّر.</strong> اللحوم والمشروبات والبطاطس من فواتير حقيقية؛ الخبز والخضار والفطور والجبن تقديرات. استُخدم الهامش الأسوأ ({N['cm_pct_used']:.0f}٪) عمدًا.",
 "<strong>المقابل المالي والسكن إفادتان غير موثقتين.</strong> عُرضت ثلاث حالات بدل افتراض واحدة، لأن الفارق بينها يقرر ربحية المشروع.",
 "<strong>قيمة المعدات صفر في هذا التقييم</strong> لعدم وجود جرد موقَّع — وليست صفرًا فعلًا، لكن ما لا يُوثَّق لا يُحتسب.",
 "<strong>لم يصل كشف بنكي ولا إقرار ضريبي.</strong> الإيراد لم يُختبر بمصدر ثالث مستقل عن النظام والموردين.",
 "<strong>صفر فجوة في الترقيم يُثبت عدم الحذف، لا اكتمال الإدخال.</strong> مطابقة الدجاج تغطي الثغرة من الجهة الأخرى لكنها لا تلغيها منطقيًا.",
 "<strong>لم يُختبر شيء من خطة الرفع ميدانيًا.</strong> أرقامها حسابية على كميات مقيسة، وتفترض ثبات الكمية عند رفع السعر — وهو افتراض لم يُقس في هذا المحل.",
 "<strong>بث المباريات والجلسات الخارجية خارج الحساب</strong> بقرارك، فلا تظهر في أي جدول."]
add('<ul class="plain">'+"".join(f'<li>{x}</li>' for x in LIM)+'</ul>')
add(f'''<div class="note"><span class="t">ما يجعل هذه الدراسة قابلة للتحديث</span>
كل رقم فيها يخرج من ملفين محفوظين: سجل المبيعات المستخرج ({a(D["period"]["days"])} يومًا) وسجل المشتريات ({D["purchases"]["lines"]} سطرًا).
عند وصول شهر كامل من فواتير المشتريات، أو بيانات أكتوبر ونوفمبر، تُعاد الحسابات كلها آليًا ويصدر إصدار جديد بالأرقام المصحَّحة.</div>''')
end()

# ══════════ ملحق أ: البيانات اليومية ══════════
import csv as _csv
add('<section class="brk"><h2 class="sec"><span class="num">أ</span>ملحق: البيانات اليومية الكاملة</h2>')
add(f'<p class="lede">{a(D["period"]["days"])} يومًا متصلة كما سجّلها نظام رواء. «أول بيعة» هي أول عملية مسجّلة في اليوم — وهي مؤشر فتح المحل في موعده.</p>')
daily_rows=list(_csv.DictReader(open("/home/user/Restaurant/data/extracted/sales-daily.csv",encoding="utf-8")))
half=(len(daily_rows)+1)//2
add('<div style="display:grid;grid-template-columns:1fr 1fr;gap:5mm">')
for chunk in (daily_rows[:half], daily_rows[half:]):
    add('<table class="sm"><thead><tr><th>التاريخ</th><th class="f">مبيعات</th><th class="f">طلبات</th><th class="f">فاتورة</th><th class="f">أول بيعة</th></tr></thead><tbody>')
    for r in chunk:
        mth=int(r["التاريخ"][5:7])
        cls=' class="lo"' if mth==8 else (' class="hi"' if mth==4 else "")
        add(f'<tr{cls}><td class="f">{r["التاريخ"][5:]}</td><td class="f">{float(r["المبيعات"]):,.0f}</td>'
            f'<td class="f">{r["عدد_الفواتير"]}</td><td class="f">{r["متوسط_الفاتورة"]}</td>'
            f'<td class="f">{r["أول_بيعة"] or "—"}</td></tr>')
    add('</tbody></table>')
add('</div>')
add(f'''<div class="note"><span class="t">كيف تقرأ عمود «أول بيعة»</span>
تتبّعه شهرًا بشهر ترَ القصة كلها: من نحو السابعة والنصف صباحًا في أبريل، إلى ما بعد الظهر في أغسطس، ثم عودته إلى نحو التاسعة في آخر أسبوعين.
<strong>هذا العمود وحده يفسّر معظم فارق المبيعات.</strong> واجعله مؤشرك اليومي بعد الاستلام.</div>''')
end()

# ══════════ ملحق ب: المنيو ══════════
add('<section class="brk"><h2 class="sec"><span class="num">ب</span>ملحق: المنيو الكامل</h2>')
add(f'<p class="lede">كل صنف سُجّل بيعه في الفترة، مرتّبًا بالإيراد. الكميات على {a(D["period"]["days"])} يومًا.</p>')
add('<table class="sm"><thead><tr><th>#</th><th>الصنف</th><th class="f">النوع</th><th class="f">السعر</th><th class="f">الكمية</th><th class="f">حبة/يوم</th><th class="f">الإيراد</th><th class="f">الحصة</th></tr></thead><tbody>')
for i,it in enumerate(D["items"],1):
    add(f'<tr><td class="f">{i}</td><td>{it["name"]}</td><td class="f">{it["kind"]}</td><td class="f">{it["price"]}</td>'
        f'<td class="f">{m(it["qty"])}</td><td class="f">{it["qty_day"]}</td><td class="f">{m(it["rev"])}</td><td class="f">{it["share"]}%</td></tr>')
add(f'<tr class="tot"><td colspan="4">الإجمالي — {a(len(D["items"]))} صنفًا</td><td class="f">{m(D["totals"]["items"])}</td>'
    f'<td class="f">{D["totals"]["items"]/D["period"]["days"]:.1f}</td><td class="f">{m(D["totals"]["revenue"])}</td><td class="f">100%</td></tr></tbody></table>')
end()

# ══════════ الإخراج ══════════
HTML=f"""<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<title>دراسة جدوى — مشوي كور، الحمراء بتبوك</title>
<style>{FONTS}</style><style>{CSS}</style></head><body>
{''.join(P)}
</body></html>"""
out=f"{HERE}/study.html"
open(out,"w",encoding="utf-8").write(HTML)
print(f"✓ {out}  —  {len(HTML)/1024:.0f} KB  —  {SEC[0]} قسمًا")
