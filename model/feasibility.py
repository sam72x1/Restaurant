#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
محرك دراسة الجدوى — استحواذ على مطعم قائم.

المبدأ: لا يُحتسب رقم بلا مصدر. كل مدخل يحمل تصنيف مصدر:
  verified  = مثبت بمستند مستقل
  claimed   = ادعاء البائع (يُعزل في سيناريو منفصل)
  estimated = تقدير قطاعي (للحساسية فقط)

التشغيل:
  python3 model/feasibility.py --inputs model/inputs.json --out reports/
"""
import argparse, json, sys, os
from datetime import date

SRC_RANK = {"verified": 3, "claimed": 1, "estimated": 2, "missing": 0}
SRC_AR = {"verified": "مثبت", "claimed": "ادعاء بائع",
          "estimated": "تقدير", "missing": "ناقص"}


class Field:
    """قيمة رقمية مع مصدرها."""
    def __init__(self, raw, path):
        self.path = path
        self.ref = ""
        if raw is None:
            self.value, self.src = None, "missing"
        elif isinstance(raw, dict):
            self.value = raw.get("v")
            self.src = raw.get("src", "estimated")
            self.ref = raw.get("ref", "")
            if self.value is None:
                self.src = "missing"
        else:
            self.value, self.src = raw, "estimated"

    @property
    def ok(self):
        return self.value is not None

    def n(self, default=0.0):
        return float(self.value) if self.ok else float(default)

    def __float__(self):
        return self.n()


class Inputs:
    def __init__(self, data):
        self.data = data
        self.fields = []

    def f(self, path, default=None, required=False):
        """قراءة حقل بمسار منقّط، مع تسجيله في سجل المصادر."""
        node = self.data
        for key in path.split("."):
            if isinstance(node, dict) and key in node:
                node = node[key]
            else:
                node = None
                break
        fld = Field(node if node is not None else default, path)
        fld.required = required
        self.fields.append(fld)
        return fld

    def unique_fields(self):
        """حقل واحد لكل مسار، بأقوى مصدر مسجّل له."""
        best = {}
        for f in self.fields:
            cur = best.get(f.path)
            if cur is None or SRC_RANK[f.src] > SRC_RANK[cur.src]:
                best[f.path] = f
        return list(best.values())

    def missing_required(self):
        return [f.path for f in self.unique_fields() if f.required and not f.ok]

    def evidence_summary(self):
        counts = {"verified": 0, "claimed": 0, "estimated": 0, "missing": 0}
        for f in self.unique_fields():
            counts[f.src] = counts.get(f.src, 0) + 1
        return counts


# ---------------------------------------------------------------- الإيرادات
def build_revenue(inp):
    """
    إيراد شهري إجمالي + صافي بعد عمولات قنوات التوصيل.
    كل قناة: orders_per_day, avg_ticket, commission_pct
    """
    channels = inp.data.get("revenue", {}).get("channels", []) or []
    days = inp.f("revenue.operating_days_per_month", 30).n(30)
    rows, gross, net, orders = [], 0.0, 0.0, 0.0
    for i, ch in enumerate(channels):
        name = ch.get("name", f"قناة {i+1}")
        opd = Field(ch.get("orders_per_day"), f"revenue.channels[{i}].orders_per_day")
        tkt = Field(ch.get("avg_ticket_sar"), f"revenue.channels[{i}].avg_ticket_sar")
        com = Field(ch.get("commission_pct", 0), f"revenue.channels[{i}].commission_pct")
        opd.required = tkt.required = True
        com.required = False
        inp.fields += [opd, tkt, com]
        if not (opd.ok and tkt.ok):
            rows.append({"name": name, "missing": True})
            continue
        g = opd.n() * tkt.n() * days
        c = g * com.n(0) / 100.0
        rows.append({"name": name, "orders_day": opd.n(), "ticket": tkt.n(),
                     "gross": g, "commission_pct": com.n(0), "commission": c,
                     "net": g - c,
                     "src": min((opd.src, tkt.src), key=lambda s: SRC_RANK[s])})
        gross += g
        net += g - c
        orders += opd.n() * days
    return {"rows": rows, "gross": gross, "net": net,
            "orders_month": orders, "days": days}


# ---------------------------------------------------------------- العمالة
def build_staff(inp):
    """كلفة العمالة المحمّلة بالكامل: راتب + تأمينات + سكن + تذاكر + نهاية خدمة."""
    staff = inp.data.get("staff", []) or []
    gosi = inp.f("assumptions.gosi_pct_saudi", 21.5).n(21.5)
    gosi_x = inp.f("assumptions.gosi_pct_expat", 2.0).n(2.0)
    eos = inp.f("assumptions.end_of_service_monthly_pct", 5.8).n(5.8)
    rows, total = [], 0.0
    for i, s in enumerate(staff):
        role = s.get("role", f"وظيفة {i+1}")
        cnt = float(s.get("count") or 0)
        sal = s.get("salary_sar")
        if sal is None:
            rows.append({"role": role, "missing": True})
            continue
        sal = float(sal)
        saudi = bool(s.get("is_saudi", False))
        housing = float(s.get("housing_sar") or 0)
        other = float(s.get("other_monthly_sar") or 0)
        gov = float(s.get("gov_fees_monthly_sar") or 0)
        soc = sal * (gosi if saudi else gosi_x) / 100.0
        end = sal * eos / 100.0
        per = sal + soc + end + housing + other + gov
        rows.append({"role": role, "count": cnt, "salary": sal, "saudi": saudi,
                     "loaded_each": per, "total": per * cnt})
        total += per * cnt
    return {"rows": rows, "total": total}


# ---------------------------------------------------------------- التكاليف
def build_costs(inp, rev, staff):
    food_pct = inp.f("cogs.food_cost_pct", required=True)
    pack_pct = inp.f("cogs.packaging_cost_pct", 0)
    base = rev["gross"]
    food = base * food_pct.n(0) / 100.0
    pack = base * pack_pct.n(0) / 100.0

    fixed_keys = [
        ("opex_monthly.rent_sar", "الإيجار", True),
        ("opex_monthly.utilities_sar", "الكهرباء والمياه", True),
        ("opex_monthly.gov_fees_sar", "رسوم حكومية (موزّعة شهريًا)", False),
        ("opex_monthly.marketing_sar", "التسويق", False),
        ("opex_monthly.maintenance_sar", "الصيانة", False),
        ("opex_monthly.pos_software_sar", "نقاط البيع والاشتراكات", False),
        ("opex_monthly.cleaning_pest_sar", "النظافة ومكافحة الحشرات", False),
        ("opex_monthly.insurance_sar", "التأمين", False),
        ("opex_monthly.accounting_sar", "المحاسبة", False),
        ("opex_monthly.equipment_reserve_sar", "مخصص إحلال المعدات", False),
        ("opex_monthly.other_sar", "أخرى", False),
    ]
    fixed, fixed_total = [], 0.0
    for path, label, req in fixed_keys:
        fld = inp.f(path, None if req else 0, required=req)
        v = fld.n(0)
        fixed.append({"label": label, "value": v, "src": fld.src, "path": path})
        fixed_total += v

    owner = inp.f("opex_monthly.owner_or_manager_salary_sar", 0).n(0)
    fixed.append({"label": "راتب المدير / المالك", "value": owner,
                  "src": "estimated", "path": "opex_monthly.owner_or_manager_salary_sar"})
    fixed_total += owner

    return {"food": food, "food_pct": food_pct, "pack": pack, "pack_pct": pack_pct,
            "variable_total": food + pack,
            "staff_total": staff["total"],
            "fixed_rows": fixed, "fixed_total": fixed_total,
            "opex_total": fixed_total + staff["total"]}


# ---------------------------------------------------------------- التحليل
def pnl(rev, cost):
    net_rev = rev["net"]                    # بعد عمولات التوصيل
    gross_profit = net_rev - cost["variable_total"]
    ebitda = gross_profit - cost["opex_total"]
    return {"net_rev": net_rev, "gross_rev": rev["gross"],
            "gross_profit": gross_profit,
            "gross_margin_pct": (gross_profit / net_rev * 100) if net_rev else 0,
            "ebitda": ebitda,
            "ebitda_margin_pct": (ebitda / net_rev * 100) if net_rev else 0,
            "annual_ebitda": ebitda * 12}


def breakeven(rev, cost):
    """
    نقطة التعادل: الإيراد الذي يساوي فيه EBITDA صفرًا.
    التكاليف المتغيرة = نسبة من الإيراد الإجمالي (مواد + تغليف + عمولة القنوات).
    """
    g = rev["gross"]
    if g <= 0:
        return None
    var_pct = cost["variable_total"] / g
    comm_pct = (g - rev["net"]) / g
    contrib = 1.0 - var_pct - comm_pct
    if contrib <= 0:
        return {"impossible": True, "contribution_pct": contrib * 100}
    be_rev = cost["opex_total"] / contrib
    avg_ticket = g / rev["orders_month"] if rev["orders_month"] else 0
    return {"contribution_pct": contrib * 100,
            "monthly_revenue": be_rev,
            "daily_revenue": be_rev / rev["days"] if rev["days"] else 0,
            "orders_per_day": (be_rev / avg_ticket / rev["days"])
                              if avg_ticket and rev["days"] else 0,
            "utilization_pct": (be_rev / g * 100) if g else 0,
            "avg_ticket": avg_ticket}


def investment(inp):
    parts = [
        ("acquisition.purchase_price_sar", "سعر الشراء / التنازل", True),
        ("acquisition.inventory_sar", "المخزون عند التسليم", False),
        ("acquisition.renovation_capex_sar", "ترميم وتجديد", False),
        ("acquisition.equipment_replacement_sar", "إحلال معدات فورية", False),
        ("acquisition.license_transfer_fees_sar", "رسوم نقل الرخص والتوثيق", False),
        ("acquisition.working_capital_sar", "رأس مال عامل (3 أشهر تشغيل)", True),
        ("acquisition.rent_deposit_sar", "دفعة الإيجار المقدمة", False),
        ("acquisition.contingency_sar", "احتياطي طوارئ", False),
    ]
    rows, total = [], 0.0
    for path, label, req in parts:
        fld = inp.f(path, None if req else 0, required=req)
        rows.append({"label": label, "value": fld.n(0), "src": fld.src, "path": path})
        total += fld.n(0)
    return {"rows": rows, "total": total}


def npv(rate, flows):
    return sum(cf / ((1 + rate) ** t) for t, cf in enumerate(flows))


def irr(flows, lo=-0.95, hi=10.0, tol=1e-7):
    if npv(lo, flows) * npv(hi, flows) > 0:
        return None
    for _ in range(300):
        mid = (lo + hi) / 2
        v = npv(mid, flows)
        if abs(v) < tol:
            return mid
        if npv(lo, flows) * v < 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def returns(inp, p, inv, cost):
    years = int(inp.f("assumptions.horizon_years", 5).n(5))
    growth = inp.f("assumptions.annual_revenue_growth_pct", 0).n(0) / 100.0
    rent_esc = inp.f("assumptions.annual_rent_escalation_pct", 0).n(0) / 100.0
    disc = inp.f("assumptions.discount_rate_pct", 12).n(12) / 100.0
    zakat = inp.f("assumptions.zakat_pct", 2.5).n(2.5) / 100.0

    rent_annual = next((r["value"] for r in cost["fixed_rows"]
                        if r["path"].endswith("rent_sar")), 0.0) * 12

    flows = [-inv["total"]]
    detail = []
    ann = p["annual_ebitda"]
    for y in range(1, years + 1):
        # نمو الإيراد يرفع الربح، والزيادة الإيجارية التراكمية تخصمه
        e = ann * ((1 + growth) ** (y - 1))
        e -= rent_annual * (((1 + rent_esc) ** (y - 1)) - 1)
        z = max(e, 0) * zakat
        cf = e - z
        flows.append(cf)
        detail.append({"year": y, "ebitda": e, "zakat": z, "cash": cf})

    tv_mult = inp.f("assumptions.terminal_value_multiple", 0).n(0)
    terminal = detail[-1]["ebitda"] * tv_mult if detail and tv_mult > 0 else 0.0
    if terminal:
        flows[-1] += terminal

    cum, payback = 0.0, None
    for d in detail:
        prev = cum
        cum += d["cash"]
        if payback is None and cum >= inv["total"]:
            need = inv["total"] - prev
            payback = (d["year"] - 1) + (need / d["cash"] if d["cash"] else 0)
    r = irr(flows)
    return {"years": years, "detail": detail, "flows": flows,
            "terminal_value": terminal, "terminal_multiple": tv_mult,
            "npv": npv(disc, flows), "irr": r,
            "payback_years": payback,
            "roi_annual_pct": (p["annual_ebitda"] / inv["total"] * 100)
                              if inv["total"] else None,
            "discount_rate_pct": disc * 100}


def valuation(inp, p):
    """تقييم السعر العادل بثلاث طرق مستقلة."""
    ann = p["annual_ebitda"]
    assets = inp.f("acquisition.equipment_fair_value_sar", 0).n(0)
    stock = inp.f("acquisition.inventory_sar", 0).n(0)
    lo = inp.f("assumptions.valuation_multiple_low", 1.0).n(1.0)
    hi = inp.f("assumptions.valuation_multiple_high", 2.0).n(2.0)
    asked = inp.f("acquisition.purchase_price_sar").n(0)
    return {"annual_ebitda": ann,
            "multiple_low": lo, "multiple_high": hi,
            "earnings_low": ann * lo, "earnings_high": ann * hi,
            "asset_floor": assets + stock,
            "asking_price": asked,
            "implied_multiple": (asked / ann) if ann > 0 else None}


def sensitivity(inp, rev, cost, base_inv):
    """أثر تغير الإيراد ونسبة تكلفة المواد والإيجار على الربح السنوي."""
    out = {}
    g, n = rev["gross"], rev["net"]
    comm_pct = (g - n) / g if g else 0
    food_pct = cost["food_pct"].n(0) / 100.0
    pack_pct = cost["pack_pct"].n(0) / 100.0
    opex = cost["opex_total"]

    def ebitda_at(rev_mult=1.0, food_delta_pp=0.0, rent_delta=0.0):
        gg = g * rev_mult
        nn = gg * (1 - comm_pct)
        var = gg * (food_pct + food_delta_pp / 100.0 + pack_pct)
        return (nn - var - (opex + rent_delta)) * 12

    out["revenue"] = [{"label": f"{int((m-1)*100):+d}%", "annual_ebitda": ebitda_at(rev_mult=m)}
                      for m in (0.70, 0.85, 1.00, 1.15, 1.30)]
    out["food_cost"] = [{"label": f"{d:+.0f} نقطة", "annual_ebitda": ebitda_at(food_delta_pp=d)}
                        for d in (-5, -2, 0, 2, 5)]
    out["rent"] = [{"label": f"{d:+,.0f} ريال/شهر", "annual_ebitda": ebitda_at(rent_delta=d)}
                   for d in (-2000, 0, 2000, 5000)]
    for k in out:
        for row in out[k]:
            row["payback_years"] = (base_inv / row["annual_ebitda"]
                                    if row["annual_ebitda"] > 0 else None)
    return out


# ---------------------------------------------------------------- الإخراج
def money(x):
    return f"{x:,.0f}" if isinstance(x, (int, float)) else "—"


def pct(x, d=1):
    return f"{x:.{d}f}%" if isinstance(x, (int, float)) else "—"


def render(inp, rev, staff, cost, p, be, inv, ret, val, sens):
    L = []
    a = L.append
    meta = inp.data.get("meta", {})
    a(f"# دراسة الجدوى — {meta.get('project_name') or 'مطعم (لم يُسمَّ بعد)'}")
    a("")
    a(f"- **التاريخ:** {date.today().isoformat()}")
    if meta.get("location"):
        a(f"- **الموقع:** {meta['location']}")
    if meta.get("concept"):
        a(f"- **النشاط:** {meta['concept']}")
    a("")

    # جودة الأدلة أولًا — قبل أي رقم
    ev = inp.evidence_summary()
    a("## 0. جودة الأدلة")
    a("")
    a("| التصنيف | عدد المدخلات |")
    a("|---|---:|")
    for k in ("verified", "claimed", "estimated", "missing"):
        a(f"| {SRC_AR[k]} | {ev.get(k, 0)} |")
    a("")
    uniq = inp.unique_fields()
    claimed = [f.path for f in uniq if f.src == "claimed"]
    if claimed:
        a("> **تنبيه:** المدخلات التالية مبنية على ادّعاء البائع بلا مستند مستقل، "
          "ولا يصح بناء قرار شراء عليها:")
        a(">")
        for c in claimed[:20]:
            a(f"> - `{c}`")
        a("")
    if ev.get("missing"):
        a("> **مدخلات ناقصة** — النتائج أدناه جزئية حتى تُستكمل:")
        a(">")
        for f in uniq:
            if f.src == "missing":
                a(f"> - `{f.path}`")
        a("")

    # الإيرادات
    a("## 1. الإيرادات")
    a("")
    a("| القناة | طلبات/يوم | متوسط الفاتورة | إجمالي شهري | العمولة | صافي شهري | المصدر |")
    a("|---|---:|---:|---:|---:|---:|---|")
    for r in rev["rows"]:
        if r.get("missing"):
            a(f"| {r['name']} | — | — | — | — | — | ناقص |")
            continue
        a(f"| {r['name']} | {r['orders_day']:,.0f} | {money(r['ticket'])} | "
          f"{money(r['gross'])} | {pct(r['commission_pct'],0)} ({money(r['commission'])}) | "
          f"{money(r['net'])} | {SRC_AR[r['src']]} |")
    a(f"| **الإجمالي** | | | **{money(rev['gross'])}** | "
      f"**{money(rev['gross']-rev['net'])}** | **{money(rev['net'])}** | |")
    a("")
    a(f"- أيام التشغيل شهريًا: **{rev['days']:,.0f}**")
    a(f"- إجمالي الطلبات شهريًا: **{rev['orders_month']:,.0f}**")
    a("")

    # التكاليف
    a("## 2. التكاليف")
    a("")
    a("### 2.1 التكاليف المتغيرة")
    a("")
    a("| البند | النسبة من الإيراد | شهريًا |")
    a("|---|---:|---:|")
    a(f"| تكلفة المواد الغذائية | {pct(cost['food_pct'].n(0))} | {money(cost['food'])} |")
    a(f"| التغليف والمستهلكات | {pct(cost['pack_pct'].n(0))} | {money(cost['pack'])} |")
    a(f"| **الإجمالي** | | **{money(cost['variable_total'])}** |")
    a("")
    a("### 2.2 العمالة (محمّلة بالكامل)")
    a("")
    a("| الوظيفة | العدد | الراتب | التكلفة الفعلية للفرد | الإجمالي |")
    a("|---|---:|---:|---:|---:|")
    for r in staff["rows"]:
        if r.get("missing"):
            a(f"| {r['role']} | — | — | — | ناقص |")
            continue
        a(f"| {r['role']} | {r['count']:,.0f} | {money(r['salary'])} | "
          f"{money(r['loaded_each'])} | {money(r['total'])} |")
    a(f"| **الإجمالي** | | | | **{money(staff['total'])}** |")
    a("")
    a("> التكلفة الفعلية للفرد = الراتب + التأمينات + مخصص نهاية الخدمة + السكن "
      "+ الرسوم الحكومية. الاكتفاء بالراتب الأساسي خطأ تقديري شائع.")
    a("")
    a("### 2.3 التكاليف الثابتة")
    a("")
    a("| البند | شهريًا | المصدر |")
    a("|---|---:|---|")
    for r in cost["fixed_rows"]:
        a(f"| {r['label']} | {money(r['value'])} | {SRC_AR.get(r['src'], r['src'])} |")
    a(f"| **الإجمالي** | **{money(cost['fixed_total'])}** | |")
    a("")
    a(f"**إجمالي المصروفات التشغيلية شهريًا: {money(cost['opex_total'])} ريال**")
    a("")

    # قائمة الدخل
    a("## 3. قائمة الدخل")
    a("")
    a("| البند | شهريًا | سنويًا |")
    a("|---|---:|---:|")
    a(f"| الإيراد الإجمالي | {money(rev['gross'])} | {money(rev['gross']*12)} |")
    a(f"| (−) عمولات قنوات التوصيل | ({money(rev['gross']-rev['net'])}) | "
      f"({money((rev['gross']-rev['net'])*12)}) |")
    a(f"| **صافي الإيراد** | **{money(p['net_rev'])}** | **{money(p['net_rev']*12)}** |")
    a(f"| (−) تكلفة المواد والتغليف | ({money(cost['variable_total'])}) | "
      f"({money(cost['variable_total']*12)}) |")
    a(f"| **مجمل الربح** | **{money(p['gross_profit'])}** | **{money(p['gross_profit']*12)}** |")
    a(f"| (−) العمالة | ({money(cost['staff_total'])}) | ({money(cost['staff_total']*12)}) |")
    a(f"| (−) المصروفات الثابتة | ({money(cost['fixed_total'])}) | ({money(cost['fixed_total']*12)}) |")
    a(f"| **صافي ربح التشغيل** | **{money(p['ebitda'])}** | **{money(p['annual_ebitda'])}** |")
    a("")
    a(f"- هامش مجمل الربح: **{pct(p['gross_margin_pct'])}**")
    a(f"- هامش صافي الربح: **{pct(p['ebitda_margin_pct'])}**")
    a("")
    a("> ضريبة القيمة المضافة (15%) تُحصَّل من العميل وتُورَّد، فهي ليست مصروفًا — "
      "لكنها تؤثر على التدفق النقدي بين التحصيل والتوريد، وتُحتسب في رأس المال العامل.")
    a("")

    # التعادل
    a("## 4. نقطة التعادل")
    a("")
    if not be:
        a("- غير محسوبة: الإيراد صفر أو ناقص.")
    elif be.get("impossible"):
        a(f"- **هامش المساهمة سالب ({pct(be['contribution_pct'])}) — لا توجد نقطة تعادل.**")
        a("- المعنى: كل ريال مبيعات يزيد الخسارة. المشكلة في التسعير أو نسبة التكلفة، "
          "لا في حجم المبيعات.")
    else:
        a(f"- هامش المساهمة: **{pct(be['contribution_pct'])}**")
        a(f"- إيراد التعادل الشهري: **{money(be['monthly_revenue'])} ريال**")
        a(f"- إيراد التعادل اليومي: **{money(be['daily_revenue'])} ريال**")
        a(f"- طلبات التعادل يوميًا: **{be['orders_per_day']:,.0f} طلب**")
        a(f"- نسبة التعادل من المبيعات الحالية: **{pct(be['utilization_pct'])}**")
        a("")
        margin = 100 - be["utilization_pct"]
        if margin < 15:
            a(f"> **خطر:** هامش الأمان {pct(margin)} فقط. انخفاض بسيط في المبيعات "
              "يحوّل المشروع إلى خسارة.")
        elif margin < 30:
            a(f"> هامش الأمان {pct(margin)} — مقبول لكنه غير مريح.")
        else:
            a(f"> هامش الأمان {pct(margin)} — جيد.")
    a("")

    # الاستثمار
    a("## 5. الاستثمار المطلوب")
    a("")
    a("| البند | المبلغ | المصدر |")
    a("|---|---:|---|")
    for r in inv["rows"]:
        a(f"| {r['label']} | {money(r['value'])} | {SRC_AR.get(r['src'], r['src'])} |")
    a(f"| **الإجمالي** | **{money(inv['total'])}** | |")
    a("")

    # العائد
    a("## 6. العائد والاسترداد")
    a("")
    a(f"- العائد السنوي على الاستثمار: **{pct(ret['roi_annual_pct'])}**")
    a(f"- فترة الاسترداد: **{ret['payback_years']:.1f} سنة**"
      if ret["payback_years"] else "- فترة الاسترداد: **لا تُسترد خلال أفق الدراسة**")
    a(f"- صافي القيمة الحالية (خصم {pct(ret['discount_rate_pct'],0)}): "
      f"**{money(ret['npv'])} ريال**")
    a(f"- معدل العائد الداخلي: **{pct(ret['irr']*100) if ret['irr'] is not None else '—'}**")
    if ret["terminal_value"]:
        a(f"- قيمة البيع المفترضة نهاية السنة {ret['years']} "
          f"(×{ret['terminal_multiple']:g} من ربح السنة الأخيرة): "
          f"**{money(ret['terminal_value'])} ريال** — مُدرجة في الحسابات أعلاه")
    else:
        a(f"- **لم تُدرج قيمة بيع نهائية.** صافي القيمة الحالية ومعدل العائد أعلاه "
          f"يفترضان أن قيمة المشروع بعد {ret['years']} سنوات = صفر، وهو افتراض "
          "متشدد. لإدراجها: `assumptions.terminal_value_multiple`.")
    a("")
    a("| السنة | صافي ربح التشغيل | الزكاة | التدفق النقدي |")
    a("|---:|---:|---:|---:|")
    for d in ret["detail"]:
        a(f"| {d['year']} | {money(d['ebitda'])} | ({money(d['zakat'])}) | {money(d['cash'])} |")
    a("")

    # التقييم
    a("## 7. تقييم السعر — هل السعر المطلوب عادل؟")
    a("")
    a(f"- صافي الربح السنوي المتحقق: **{money(val['annual_ebitda'])} ريال**")
    a(f"- القيمة بطريقة مضاعف الأرباح (×{val['multiple_low']:g} إلى ×{val['multiple_high']:g}): "
      f"**{money(val['earnings_low'])} – {money(val['earnings_high'])} ريال**")
    a(f"- الحد الأدنى بطريقة الأصول (معدات + مخزون): **{money(val['asset_floor'])} ريال**")
    a(f"- **السعر المطلوب من البائع: {money(val['asking_price'])} ريال**")
    if val["implied_multiple"]:
        a(f"- المضاعف الضمني للسعر المطلوب: **×{val['implied_multiple']:.2f}** "
          "من صافي الربح السنوي")
    a("")
    ask = val["asking_price"]
    if ask and val["annual_ebitda"] > 0:
        if ask > val["earnings_high"]:
            gap = ask - val["earnings_high"]
            a(f"> **الحكم: السعر مرتفع.** يتجاوز أعلى تقييم معقول بـ "
              f"**{money(gap)} ريال**. نقطة التفاوض المقترحة: "
              f"{money(val['earnings_low'])} – {money(val['earnings_high'])} ريال.")
        elif ask < val["earnings_low"]:
            a("> **الحكم: السعر أقل من نطاق التقييم.** تحقق من السبب — "
              "سعر منخفض بلا مبرر غالبًا يخفي مشكلة (عقد قصير، مخالفات، هبوط مبيعات).")
        else:
            a("> **الحكم: السعر داخل النطاق المعقول** — بشرط أن تكون الأرقام `مثبتة` "
              "لا `ادعاءً`.")
    a("")

    # الحساسية
    a("## 8. تحليل الحساسية")
    a("")
    for key, title in (("revenue", "8.1 تغير الإيراد"),
                       ("food_cost", "8.2 تغير نسبة تكلفة المواد"),
                       ("rent", "8.3 تغير الإيجار")):
        a(f"### {title}")
        a("")
        a("| التغير | صافي الربح السنوي | فترة الاسترداد |")
        a("|---|---:|---:|")
        for row in sens[key]:
            pb = (f"{row['payback_years']:.1f} سنة"
                  if row["payback_years"] else "لا يُسترد")
            a(f"| {row['label']} | {money(row['annual_ebitda'])} | {pb} |")
        a("")

    a("---")
    a("")
    a("## ملاحظة منهجية")
    a("")
    a("هذه الدراسة تحسب ما تُدخله فقط. دقتها = دقة المستندات التي بُنيت عليها. "
      "أي بند مصنّف «ادعاء بائع» أو «تقدير» يجب أن يتحول إلى «مثبت» قبل توقيع العقد.")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", default="model/inputs.json")
    ap.add_argument("--out", default="reports/")
    ap.add_argument("--name", default="feasibility-study.md")
    args = ap.parse_args()

    if not os.path.exists(args.inputs):
        sys.exit(f"لم يُعثر على ملف المدخلات: {args.inputs}")
    with open(args.inputs, encoding="utf-8") as fh:
        data = json.load(fh)

    inp = Inputs(data)
    rev = build_revenue(inp)
    staff = build_staff(inp)
    cost = build_costs(inp, rev, staff)
    p = pnl(rev, cost)
    be = breakeven(rev, cost)
    inv = investment(inp)
    ret = returns(inp, p, inv, cost)
    val = valuation(inp, p)
    sens = sensitivity(inp, rev, cost, inv["total"])

    missing = inp.missing_required()
    report = render(inp, rev, staff, cost, p, be, inv, ret, val, sens)

    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, args.name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(report + "\n")

    print(f"✔ التقرير: {path}")
    print(f"  الإيراد الشهري الإجمالي : {money(rev['gross'])} ريال")
    print(f"  صافي ربح التشغيل الشهري : {money(p['ebitda'])} ريال")
    print(f"  الاستثمار المطلوب        : {money(inv['total'])} ريال")
    if ret["payback_years"]:
        print(f"  فترة الاسترداد           : {ret['payback_years']:.1f} سنة")
    if missing:
        print(f"\n⚠ مدخلات حرجة ناقصة ({len(missing)}):")
        for m in missing:
            print(f"   - {m}")
        print("  النتائج أعلاه جزئية حتى تُستكمل.")


if __name__ == "__main__":
    main()
