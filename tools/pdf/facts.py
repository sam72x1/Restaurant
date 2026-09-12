# -*- coding: utf-8 -*-
"""الحساب المرجعي الوحيد لدراسة جدوى مشوي كور. كل رقم في الـPDF يخرج من هنا."""
import csv, collections, datetime, json, re, os

SALES=["/root/.claude/uploads/d31cf2df-6db6-599d-8498-c3368f191265/9909a8a7-order_invoices_export_01M2BD2BKV6VZRSA70YTVNC6AB.csv",
       "/root/.claude/uploads/d31cf2df-6db6-599d-8498-c3368f191265/417fbcdd-order_invoices_export_01M2B9EA2N0TSB93NC7VJQF99J.csv"]
PURCH="/home/user/Restaurant/data/extracted/purchases.csv"
dt=lambda s: datetime.datetime.strptime(s.strip(),"%B %d, %Y %I:%M %p")
F=lambda x: float(x) if (x or "").strip() not in ("","-") else 0.0

rows=[]
for f in SALES:
    for r in csv.DictReader(open(f,encoding="utf-8-sig")):
        r["_dt"]=dt(r["Date"]); r["_d"]=r["_dt"].date(); rows.append(r)
SL=[r for r in rows if r["Line type"]=="Sale"]
LN=[r for r in rows if r["Line type"]=="Sale Line"]
PY_=[r for r in rows if r["Line type"]=="Payment"]
assert len({r["Invoice Number"] for r in SL})==len(SL), "فواتير مكررة بين الملفين"

D={}
day=collections.defaultdict(float); dinv=collections.defaultdict(int); ditems=collections.defaultdict(float)
for r in SL: day[r["_d"]]+=F(r["Total (Tax inclusive)"]); dinv[r["_d"]]+=1
for r in LN: ditems[r["_d"]]+=F(r["Quantity"])
ds=sorted(day); N=len(ds)
D["period"]={"from":str(ds[0]),"to":str(ds[-1]),"days":N,
             "calendar_days":(ds[-1]-ds[0]).days+1,"missing_days":(ds[-1]-ds[0]).days+1-N}
D["totals"]={"revenue":round(sum(day.values()),2),"invoices":len(SL),"lines":len(LN),
             "items":round(sum(ditems.values()))}

# ── شهريًا ──────────────────────────────────────────────────────────
MN={4:"أبريل",5:"مايو",6:"يونيو",7:"يوليو",8:"أغسطس",9:"سبتمبر"}
SH=lambda n:("شاورما" in n) or n.startswith("عربي")
isbeef=lambda n: SH(n) and "لحم" in n
beef=collections.defaultdict(float); beefq=collections.defaultdict(float); chickq=collections.defaultdict(float)
for r in LN:
    n=r["Details"].strip()
    if isbeef(n): beef[r["_d"]]+=F(r["Total (Tax inclusive)"]); beefq[r["_d"]]+=F(r["Quantity"])
    elif SH(n):   chickq[r["_d"]]+=F(r["Quantity"])
months=[]
for m in sorted(MN):
    dd=[d for d in ds if d.month==m]; nd=len(dd)
    rev=sum(day[d] for d in dd); inv=sum(dinv[d] for d in dd); it=sum(ditems[d] for d in dd)
    months.append({"m":m,"name":MN[m],"days":nd,"rev_day":round(rev/nd,1),"rev":round(rev),
        "inv_day":round(inv/nd,1),"inv":inv,"ticket":round(rev/inv,2),
        "items_inv":round(it/inv,2),"beef_day":round(sum(beef[d] for d in dd)/nd,1),
        "exbeef_day":round((rev-sum(beef[d] for d in dd))/nd,1)})
D["months"]=months
D["avg"]={"rev_day":round(sum(day.values())/N,1),"inv_day":round(len(SL)/N,1),
          "ticket":round(sum(day.values())/len(SL),2),
          "items_inv":round(sum(ditems.values())/len(SL),2)}
vals=sorted(day.values())
D["dist"]={"median":round(vals[N//2],1),"min":round(min(vals),1),"max":round(max(vals),1),
           "p25":round(vals[N//4],1),"p75":round(vals[3*N//4],1)}
TAIL=ds[-14:]; TSET=set(TAIL)
D["entry"]={"days":14,"from":str(TAIL[0]),"to":str(TAIL[-1]),
   "rev_day":round(sum(day[d] for d in TAIL)/14,1),"inv_day":round(sum(dinv[d] for d in TAIL)/14,1),
   "ticket":round(sum(day[d] for d in TAIL)/sum(dinv[d] for d in TAIL),2)}

# ── أسبوعيًا ─────────────────────────────────────────────────────────
_wi=sorted(range(N-7,-1,-7))   # نوافذ أسبوعية مثبَّتة على آخر يوم في السلسلة
D["weeks"]=[{"start":str(ds[i]),"end":str(ds[i+6]),
             "rev":round(sum(day[d] for d in ds[i:i+7])/7,1),
             "inv":round(sum(dinv[d] for d in ds[i:i+7])/7,1)} for i in _wi]
D["series"]=[[str(d),round(day[d])] for d in ds]

# ── التشغيل: الفتح والساعات ─────────────────────────────────────────
first={}; hrs=collections.defaultdict(lambda: collections.defaultdict(float))
morn=collections.defaultdict(float)
for r in SL:
    h=r["_dt"].hour+r["_dt"].minute/60
    if h>=4: first[r["_d"]]=min(first.get(r["_d"],99), h)
    hrs[r["_dt"].hour][r["_d"]]+=F(r["Total (Tax inclusive)"])
    if 5<=r["_dt"].hour<11: morn[r["_d"]]+=F(r["Total (Tax inclusive)"])
def ops(sel):
    nd=len(sel)
    f=[first[d] for d in sel if d in first and first[d]<99]
    act=[h for h in hrs if sum(1 for d in sel if hrs[h].get(d,0)>0)/nd>=0.15]
    rev=sum(day[d] for d in sel)/nd
    mdays=sum(1 for d in sel if morn.get(d,0)>0)
    return {"open":f"{int(sum(f)/len(f)):02d}:{int(sum(f)/len(f)%1*60):02d}",
            "active_hours":len(act),"rev_day":round(rev,1),"rev_per_hour":round(rev/len(act),1),
            "morning_days_pct":round(100*mdays/nd),"morning_rev":round(sum(morn.get(d,0) for d in sel)/nd,1)}
D["ops"]={"april":ops([d for d in ds if d.month==4]),"august":ops([d for d in ds if d.month==8]),
          "now":ops(TAIL)}
# أصناف نشطة شهريًا
act_items={}
for m in MN:
    s={r["Details"].strip() for r in LN if r["_d"].month==m and F(r["Quantity"])>0}
    act_items[MN[m]]=len(s)
D["menu_size"]=act_items

# ── الفترات اليومية ─────────────────────────────────────────────────
BANDS=[("الصباح","٥–١١",range(5,11)),("الظهيرة","١١–١٧",range(11,17)),
       ("المساء","١٧–٢٠",range(17,20)),("الذروة","٢٠–٢٤",range(20,24)),
       ("بعد منتصف الليل","٠٠–٠٢",range(0,2))]
def bandrev(sel,hh): return sum(hrs[h].get(d,0) for h in hh for d in sel)/len(sel)
APR=[d for d in ds if d.month==4]
D["bands"]=[{"name":a,"range":b,"april":round(bandrev(APR,h),1),"now":round(bandrev(TAIL,h),1),
             "gap":round(bandrev(APR,h)-bandrev(TAIL,h),1),
             "gap_month":round((bandrev(APR,h)-bandrev(TAIL,h))*30)} for a,b,h in BANDS]
D["bands_gap_total"]=round(sum(x["gap"] for x in D["bands"] if x["gap"]>0)*30)
D["hourly"]={"april":{f"{h:02d}":round(sum(hrs[h].get(d,0) for d in APR)/30,1) for h in sorted(hrs)},
             "now":{f"{h:02d}":round(sum(hrs[h].get(d,0) for d in TAIL)/14,1) for h in sorted(hrs)}}
AR_DOW=["الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت","الأحد"]
dw=collections.defaultdict(lambda:[0.0,0,0])
for d in ds: dw[d.weekday()][0]+=day[d]; dw[d.weekday()][1]+=1; dw[d.weekday()][2]+=dinv[d]
D["dow"]=[{"name":AR_DOW[w],"rev":round(dw[w][0]/dw[w][1]),"inv":round(dw[w][2]/dw[w][1],1),
           "days":dw[w][1]} for w in range(7)]

# ── المنيو ──────────────────────────────────────────────────────────
agg=collections.defaultdict(lambda:[0.0,0.0])
for r in LN:
    k=r["Details"].strip(); agg[k][0]+=F(r["Quantity"]); agg[k][1]+=F(r["Total (Tax inclusive)"])
tot=sum(v for _,v in agg.values())
D["items"]=[{"name":k,"qty":round(q),"qty_day":round(q/N,2),"rev":round(v),
             "share":round(100*v/tot,2),"price":round(v/q,2),
             "kind":("لحم" if isbeef(k) else ("دجاج" if SH(k) else "غيره"))}
            for k,(q,v) in sorted(agg.items(),key=lambda x:-x[1][1])]
inv_items=collections.defaultdict(list)
for r in LN: inv_items[r["Invoice Number"]].append((r["Details"].strip(),F(r["Quantity"])))
DRK=["ميرندا","ديو","بيبسي","عصير","مياه","شاهي"]
ni=len(inv_items)
pct=lambda p: round(100*sum(1 for v in inv_items.values() if any(p(x) for x,_ in v))/ni,1)
D["attach"]={"cheese":pct(lambda x:"جبن" in x),"drink":pct(lambda x:any(d in x for d in DRK)),
  "fries":pct(lambda x:"بطاطس" in x),
  "single":round(100*sum(1 for v in inv_items.values() if sum(int(q) for _,q in v)==1)/ni,1),
  "single_n":sum(1 for v in inv_items.values() if sum(int(q) for _,q in v)==1),"invoices":ni}
D["basket"]=collections.Counter(min(int(sum(q for _,q in v)),6) for v in inv_items.values())
D["basket"]={str(k):v for k,v in sorted(D["basket"].items())}

# ── السلامة ─────────────────────────────────────────────────────────
nums=sorted(int(m.group(1)) for r in SL if (m:=re.match(r"S\d{8}-(\d+)$",r["Invoice Number"])))
D["integrity"]={"seq_from":nums[0],"seq_to":nums[-1],"expected":nums[-1]-nums[0]+1,
  "present":len(nums),"missing":len(set(range(nums[0],nums[-1]+1))-set(nums)),
  "returns":sum(1 for r in SL if r["Sell type"]=="Return"),
  "returns_value":round(sum(F(r["Total (Tax inclusive)"]) for r in SL if F(r["Total (Tax inclusive)"])<0),2),
  "discounts":round(sum(F(r["Discount"]) for r in SL),2),
  "discount_invoices":sum(1 for r in SL if F(r["Discount"])>0),
  "users":sorted({r["User"] for r in SL if r["User"]}),
  "registers":sorted({r["Register"] for r in SL if r["Register"]})}
pm=collections.defaultdict(float)
for r in PY_: pm[r["Payment method"]]+=F(r["Paid amount"])
tp=sum(pm.values())
D["payments"]=[{"method":k,"value":round(v),"pct":round(100*v/tp,1),"day":round(v/N,1)}
               for k,v in sorted(pm.items(),key=lambda x:-x[1])]
D["vat_if_registered"]={"on_period":round(D["totals"]["revenue"]*15/115),
  "monthly":round(D["totals"]["revenue"]*15/115/N*30)}

# ── اللحوم ──────────────────────────────────────────────────────────
GR=0.085
D["meat"]={"chicken_day_entry":round(sum(chickq[d] for d in TAIL)/14,1),
  "beef_day_entry":round(sum(beefq[d] for d in TAIL)/14,1),
  "chicken_kg_entry":round(sum(chickq[d] for d in TAIL)/14*GR,2),
  "beef_kg_entry":round(sum(beefq[d] for d in TAIL)/14*GR,2),
  "gram":int(GR*1000),
  "cartons_month":round(sum(chickq[d] for d in TAIL)/14*GR/8*30,1),
  "beef_timeline":{MN[m]:round(sum(beef[d] for d in ds if d.month==m)/len([d for d in ds if d.month==m]),1) for m in MN}}

# ── المشتريات ───────────────────────────────────────────────────────
pr=list(csv.DictReader(open(PURCH,encoding="utf-8")))
sup=collections.defaultdict(float)
for r in pr: sup[(r["المورد"] or "غير محدد").strip()[:42]]+=F(r["الإجمالي"])
tsup=sum(sup.values())
D["suppliers"]=[{"name":k or "غير محدد","value":round(v),"pct":round(100*v/tsup,1)}
                for k,v in sorted(sup.items(),key=lambda x:-x[1])[:6]]
D["purchases"]={"total":round(tsup),"invoices":len({(r["المورد"],r["رقم_الفاتورة"]) for r in pr}),
  "lines":len(pr),"with_vat":sum(1 for r in pr if F(r["الضريبة"])>0),
  "from":min(r["التاريخ"] for r in pr if r["التاريخ"]),
  "to":max(r["التاريخ"] for r in pr if r["التاريخ"])}
def unit(key):
    h=[(F(r["الكمية"]),F(r["الإجمالي"])) for r in pr if key in r["الصنف"]]
    q=sum(a for a,_ in h); v=sum(b for _,b in h)
    return round(v/q,2) if q else None
D["unit_costs"]={"كرتون دجاج ١٠ كجم":unit("جي سي"),"كرتون لحم ١٠ كجم":unit("شاورما لحم 10"),
  "كرتون بطاطس ١٠ كجم":unit("بطاطس مايدا"),"تنكة زيت ١٧ لتر":unit("زيت دلال تنك"),
  "كرتون مشروب ٢٤ علبة":unit("شد 24"),"كرتون عصير":unit("عصير ربيع")}
json.dump(D, open(os.path.join(os.path.dirname(__file__),"facts.json"),"w",encoding="utf-8"),
          ensure_ascii=False, indent=1, default=str)
print("✓ facts.json")
for k in ("period","totals","avg","dist","entry","ops","menu_size","attach","integrity","meat","purchases","unit_costs","vat_if_registered"):
    print(f"\n── {k} ──"); print(json.dumps(D[k],ensure_ascii=False,indent=1))
print("\n── months ──")
for m in D["months"]: print(" ",m)
print("\n── bands ──")
for b in D["bands"]: print(" ",b)
print(" مجموع الفجوة/شهر:",D["bands_gap_total"])
