# -*- coding: utf-8 -*-
"""النموذج المالي — مبني على facts.json وأسعار الموردين الفعلية."""
import csv, collections, datetime, json, os
HERE=os.path.dirname(os.path.abspath(__file__))
D=json.load(open(os.path.join(HERE,"facts.json"),encoding="utf-8"))
SALES=["/root/.claude/uploads/d31cf2df-6db6-599d-8498-c3368f191265/9909a8a7-order_invoices_export_01M2BD2BKV6VZRSA70YTVNC6AB.csv",
       "/root/.claude/uploads/d31cf2df-6db6-599d-8498-c3368f191265/417fbcdd-order_invoices_export_01M2B9EA2N0TSB93NC7VJQF99J.csv"]
dt=lambda s: datetime.datetime.strptime(s.strip(),"%B %d, %Y %I:%M %p")
F=lambda x: float(x) if (x or "").strip() else 0.0
LN=[]
for f in SALES:
    for r in csv.DictReader(open(f,encoding="utf-8-sig")):
        if r["Line type"]=="Sale Line":
            r["_d"]=dt(r["Date"]).date(); LN.append(r)
ds=sorted({datetime.date.fromisoformat(x[0]) for x in D["series"]}); TAIL=set(ds[-14:])
q=collections.defaultdict(float)
for r in LN:
    if r["_d"] in TAIL: q[r["Details"].strip()]+=F(r["Quantity"])
qd={k:v/14 for k,v in q.items()}
SH=lambda n:("شاورما" in n) or n.startswith("عربي")
U=D["unit_costs"]
M={}
# لحوم — كرتون 10 كجم خام، صافي على السيخ 8 كجم (إفادة المشتري)
M["دجاج"]      = D["meat"]["chicken_kg_entry"] * (U["كرتون دجاج ١٠ كجم"]/8)
M["لحم"]       = D["meat"]["beef_kg_entry"]    * (U["كرتون لحم ١٠ كجم"]/8)
sand = sum(v for k,v in qd.items() if SH(k))
M["خبز"]       = sand * 0.70      # تقدير
M["خضار وصلصة"]= sand * 0.50      # تقدير
M["ورق وتغليف"]= sand * 0.25      # تقدير
drinks=sum(v for k,v in qd.items() if any(x in k for x in ["ميرندا","ديو","بيبسي","عصير","مياه","شاهي"]))
M["مشروبات"]   = sum(qd.get(k,0)*c for k,c in
                  [("ميرندا حمضيات",U["كرتون مشروب ٢٤ علبة"]/24),("ماونتن ديو",U["كرتون مشروب ٢٤ علبة"]/24),
                   ("بيبسي",U["كرتون مشروب ٢٤ علبة"]/24),("عصير ربيع",U["كرتون عصير"]/24),
                   ("مياه",0.30),("شاهي",0.25)])
fries=sum(v for k,v in qd.items() if "بطاطس" in k)
M["بطاطس وزيت"]= fries*(U["كرتون بطاطس ١٠ كجم"]/10*0.25) + fries*(U["تنكة زيت ١٧ لتر"]/17*0.05)
fal=sum(v for k,v in qd.items() if any(x in k for x in ["فلافل","بيض","كبدة","شكشوكة","حمص","مقلقل","جبن سايل"]))
M["الفطور والمقبلات"]= fal*1.10   # تقدير
cheese=sum(v for k,v in qd.items() if "جبن" in k)
M["جبن"]       = cheese*0.45
M["غاز ومستهلكات"]=8.0            # تقدير
mat=sum(M.values()); REV=D["entry"]["rev_day"]
FIN={"materials":{k:round(v,1) for k,v in sorted(M.items(),key=lambda x:-x[1])},
     "materials_day":round(mat,1),"food_cost_pct":round(100*mat/REV,1),
     "cm_pct_derived":round(100-100*mat/REV,1),"cm_pct_used":55.0,
     "drinks_day":round(drinks,1),"fries_day":round(fries,1),"sandwiches_day":round(sand,1)}
# ── الثوابت ────────────────────────────────────────────────────────
STAFF=[{"role":"شيف تركي — شاورما","salary":2500},{"role":"عامل هندي","salary":1500},{"role":"مشرف","salary":1500}]
BASE=sum(s["salary"] for s in STAFF)
LINES=[("إيجار شامل الكهرباء والمياه",2000,2000,2000),
       ("رواتب أساسية (٣ عمّال)",BASE,BASE,BASE),
       ("سكن العمالة (٦٠٠ × ٣)",1800,1800,0),
       ("المقابل المالي (٨٠٠ × ٣)",2400,0,0),
       ("التأمينات الاجتماعية ٢٪",round(BASE*0.02),round(BASE*0.02),round(BASE*0.02)),
       ("مخصص نهاية الخدمة ٥٫٨٪",round(BASE*0.058),round(BASE*0.058),round(BASE*0.058)),
       ("رسوم حكومية دورية",300,300,300),("صيانة",300,300,300),("اشتراك نظام رواء",200,200,200),
       ("نظافة ومكافحة حشرات",200,200,200),("محاسبة",300,300,300),("احتياطي إحلال معدات",300,300,300)]
FIX=[sum(l[i] for l in LINES) for i in (1,2,3)]
FIN["staff"]=STAFF; FIN["fixed_lines"]=[{"name":l[0],"full":l[1],"nolevy":l[2],"nolevy_nohouse":l[3]} for l in LINES]
FIN["fixed"]={"full":FIX[0],"nolevy":FIX[1],"nolevy_nohouse":FIX[2]}
CM=0.55
FIN["breakeven"]={k:round(v/CM/30) for k,v in FIN["fixed"].items()}
# ── خطة الرفع ──────────────────────────────────────────────────────
inv_day=D["entry"]["inv_day"]
def price_lift(item,delta):
    return {"name":f"رفع سعر {item} بريال","now":round(qd.get(item,0),2),
            "gain_day":round(qd.get(item,0)*delta,1),"gain_month":round(qd.get(item,0)*delta*30)}
PLAN=[price_lift("شاورما صاروخ خبز تركي",1), price_lift("شاورما عربي",1)]
def attach(name,cur,tgt,price,cost):
    add=inv_day*(tgt-cur)/100
    return {"name":name,"now":cur,"target":tgt,"extra_day":round(add,1),
            "gain_day":round(add*(price-cost),1),"gain_month":round(add*(price-cost)*30)}
PLAN+=[attach("إرفاق المشروب",D["attach"]["drink"],55,3.0,U["كرتون مشروب ٢٤ علبة"]/24),
       attach("إرفاق البطاطس",D["attach"]["fries"],18,5.0,2.26),
       attach("إرفاق الجبن",D["attach"]["cheese"],32,1.0,0.45)]
FIN["plan"]=PLAN; FIN["plan_total"]=round(sum(p["gain_month"] for p in PLAN))
FIN["plan_rev_day"]=round(sum(p["gain_day"] for p in PLAN[:2])+
    sum(p["extra_day"]*pr for p,pr in zip(PLAN[2:],[3.0,5.0,1.0])),1)
# ── مسار الاستعادة ─────────────────────────────────────────────────
gap={b["name"]:b["gap"] for b in D["bands"]}
STEPS=[("نقطة الدخول — آخر ١٤ يومًا",REV),
       ("+ استعادة الظهيرة ١١–١٧",REV+gap["الظهيرة"]),
       ("+ استعادة الصباح ٥–١١",REV+gap["الظهيرة"]+gap["الصباح"]),
       ("+ خطة الرفع",REV+gap["الظهيرة"]+gap["الصباح"]+FIN["plan_rev_day"]),
       ("عودة كاملة لمستوى أبريل",D["months"][0]["rev_day"])]
def pnl(rev, extra_cm=0):
    c=rev*30*CM+extra_cm
    return {k: round(c-v) for k,v in FIN["fixed"].items()}
FIN["path"]=[]
for i,(lab,rev) in enumerate(STEPS):
    extra = FIN["plan_total"] if i>=3 else 0
    base_rev = rev - (FIN["plan_rev_day"] if i>=3 and i<4 else 0)
    p=pnl(base_rev if i==3 else rev, extra if i==3 else 0)
    FIN["path"].append({"label":lab,"rev_day":round(rev),**p})
PRICE=30000; CASH=[("ثمن المحل شامل المعدات",PRICE),("نقل الرخص والسجل التجاري",2000),
  ("تأمين الإيجار (شهر)",2000),("رأس مال تشغيلي",5325)]
FIN["cash"]={"lines":[{"name":a,"v":b} for a,b in CASH],"total":sum(b for _,b in CASH),
  "available":40000,"left":40000-sum(b for _,b in CASH)}
best=FIN["path"][3]["nolevy_nohouse"]; mid=FIN["path"][3]["nolevy"]
FIN["payback"]={"best_monthly":best,"best_months":round(PRICE/best,1) if best>0 else None,
  "mid_monthly":mid,"mid_months":round(PRICE/mid,1) if mid>0 else None}
FIN["annual_at_plan"]=round(FIN["path"][3]["rev_day"]*365)
FIN["vat_threshold"]=375000
json.dump(FIN, open(os.path.join(HERE,"finance.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(FIN,ensure_ascii=False,indent=1))
