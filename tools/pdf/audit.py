# -*- coding: utf-8 -*-
"""تدقيق مستقل: يُعيد اشتقاق الأرقام الرئيسية من الملفات الخام بمسار مختلف، ويقارنها بما في الوثيقة."""
import csv, json, datetime, collections, re
F=["/root/.claude/uploads/d31cf2df-6db6-599d-8498-c3368f191265/9909a8a7-order_invoices_export_01M2BD2BKV6VZRSA70YTVNC6AB.csv",
   "/root/.claude/uploads/d31cf2df-6db6-599d-8498-c3368f191265/417fbcdd-order_invoices_export_01M2B9EA2N0TSB93NC7VJQF99J.csv"]
D=json.load(open("facts.json",encoding="utf-8")); N=json.load(open("finance.json",encoding="utf-8"))
HTML=open("study.html",encoding="utf-8").read()
# --- إعادة القراءة بمسار مستقل: مجاميع خام بلا أي دوال مشتركة ---
tot=0.0; inv=0; byd={}; byh={}; items=0.0; first={}
for f in F:
    for r in csv.DictReader(open(f,encoding="utf-8-sig")):
        d=datetime.datetime.strptime(r["Date"].strip(),"%B %d, %Y %I:%M %p")
        v=float(r["Total (Tax inclusive)"] or 0)
        if r["Line type"]=="Sale":
            tot+=v; inv+=1
            byd[d.date()]=byd.get(d.date(),0)+v
            byh[d.hour]=byh.get(d.hour,0)+v
            if d.hour>=4: first[d.date()]=min(first.get(d.date(),99), d.hour+d.minute/60)
        elif r["Line type"]=="Sale Line": items+=float(r["Quantity"] or 0)
ds=sorted(byd)
OK=[]; BAD=[]
def chk(name, mine, doc, tol=0.51):
    ok = abs(mine-doc)<=tol
    (OK if ok else BAD).append((name, mine, doc))
chk("إجمالي المبيعات", round(tot,2), D["totals"]["revenue"], 0.01)
chk("عدد الفواتير", inv, D["totals"]["invoices"], 0)
chk("عدد الأيام", len(ds), D["period"]["days"], 0)
chk("أيام ناقصة", (ds[-1]-ds[0]).days+1-len(ds), D["period"]["missing_days"], 0)
chk("المتوسط اليومي", round(tot/len(ds),1), D["avg"]["rev_day"], 0.05)
chk("متوسط الفاتورة", round(tot/inv,2), D["avg"]["ticket"], 0.01)
chk("الطلبات اليومية", round(inv/len(ds),1), D["avg"]["inv_day"], 0.05)
chk("إجمالي الأصناف", round(items), D["totals"]["items"], 0)
for i,mn in enumerate([4,5,6,7,8,9]):
    dd=[d for d in ds if d.month==mn]
    chk(f"مبيعات شهر {mn}/يوم", round(sum(byd[d] for d in dd)/len(dd),1), D["months"][i]["rev_day"], 0.05)
    chk(f"أيام شهر {mn}", len(dd), D["months"][i]["days"], 0)
tail=ds[-14:]
chk("نقطة الدخول (آخر 14)", round(sum(byd[d] for d in tail)/14,1), D["entry"]["rev_day"], 0.05)
for k,(lo,hi) in {"الصباح":(5,11),"الظهيرة":(11,17),"المساء":(17,20),"الذروة":(20,24)}.items():
    apr=sum(v for d in ds if d.month==4 for h,v in [(0,0)])  # placeholder
# إعادة حساب الفترات بمسار مستقل
def band(sel,lo,hi):
    s=0.0
    for f in F:
        for r in csv.DictReader(open(f,encoding="utf-8-sig")):
            if r["Line type"]!="Sale": continue
            d=datetime.datetime.strptime(r["Date"].strip(),"%B %d, %Y %I:%M %p")
            if d.date() in sel and lo<=d.hour<hi: s+=float(r["Total (Tax inclusive)"] or 0)
    return s/len(sel)
APR=[d for d in ds if d.month==4]; TAIL=set(tail)
for i,(lo,hi) in enumerate([(5,11),(11,17),(17,20),(20,24)]):
    chk(f"فترة {lo}-{hi} أبريل", round(band(APR,lo,hi),1), D["bands"][i]["april"], 0.05)
    chk(f"فترة {lo}-{hi} الآن",  round(band(TAIL,lo,hi),1), D["bands"][i]["now"], 0.05)
# وقت الفتح
for lab,sel,key in [("أبريل",APR,"april"),("آخر 14",tail,"now")]:
    f_=[first[d] for d in sel if d in first and first[d]<99]; av=sum(f_)/len(f_)
    doc=D["ops"][key]["open"]; mine=f"{int(av):02d}:{int(av%1*60):02d}"
    (OK if mine==doc else BAD).append((f"وقت الفتح {lab}", mine, doc))
# المالية
CM=0.55
for k in ("full","nolevy","nolevy_nohouse"):
    chk(f"تعادل {k}", round(N["fixed"][k]/CM/30), N["breakeven"][k], 0.51)
    s=sum(l[k] for l in N["fixed_lines"])
    chk(f"مجموع الثوابت {k}", s, N["fixed"][k], 0)
for p in N["path"]:
    for k in ("full","nolevy","nolevy_nohouse"):
        pass
chk("مجموع خطة الرفع", sum(x["gain_month"] for x in N["plan"]), N["plan_total"], 0.51)
chk("مجموع النقد", sum(x["v"] for x in N["cash"]["lines"]), N["cash"]["total"], 0)
chk("المتبقي نقدًا", N["cash"]["available"]-N["cash"]["total"], N["cash"]["left"], 0)
chk("استرداد أفضل", round(30000/N["path"][3]["nolevy_nohouse"],1), N["payback"]["best_months"], 0.05)
chk("استرداد أوسط", round(30000/N["path"][3]["nolevy"],1), N["payback"]["mid_months"], 0.05)
# تسلسل الفواتير
nums=[]
for f in F:
    for r in csv.DictReader(open(f,encoding="utf-8-sig")):
        if r["Line type"]=="Sale" and (mm:=re.match(r"S\d{8}-(\d+)$",r["Invoice Number"])): nums.append(int(mm.group(1)))
nums=sorted(nums)
chk("فجوات الترقيم", len(set(range(nums[0],nums[-1]+1))-set(nums)), D["integrity"]["missing"], 0)
chk("مدى الترقيم", nums[-1]-nums[0]+1, D["integrity"]["expected"], 0)
# هل كل رقم رئيسي موجود فعلًا في نص الوثيقة؟
MUST=[f'{tot:,.0f}', f'{inv:,}', "995","468","620","723","832","687","578","39,325","13,729","11,329","9,529"]
missing=[x for x in MUST if x not in HTML]
print(f"✓ اجتاز: {len(OK)} فحصًا")
if BAD:
    print(f"\n✗ انحرافات: {len(BAD)}")
    for n_,a_,b_ in BAD: print(f"   {n_:<28} حسابي={a_}  الوثيقة={b_}")
else: print("✗ انحرافات: لا شيء")
print(f"\nأرقام رئيسية غائبة عن نص الوثيقة: {missing if missing else 'لا شيء'}")
