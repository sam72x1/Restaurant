# -*- coding: utf-8 -*-
"""رسوم SVG للطباعة — كل قيمة من facts.json."""
import datetime
INK="#14232A"; MUT="#52707A"; LINE="#C9D9DC"
TEAL="#0A6068"; TEAL_L="#8FC0C4"; GRN="#14653E"; GRN_L="#9CCBB4"
RED="#96271F"; RED_L="#DFA59F"; AMB="#9A6206"; AMB_L="#DCBC85"
from decimal import Decimal, ROUND_HALF_UP
def ar(x):
    """أرقام لاتينية موحَّدة مع الجداول، وتقريب نصف-لأعلى مثل متن الوثيقة."""
    if isinstance(x,(int,float)):
        q=Decimal(str(x)).quantize(Decimal(1), rounding=ROUND_HALF_UP)
        return f"{q:,}"
    return str(x)

def _txt(x,y,t,size=8,anchor="middle",fill=MUT,weight="400",mono=True):
    fam="IBM Plex Mono, IBM Plex Sans Arabic, monospace" if mono else "IBM Plex Sans Arabic,sans-serif"
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
            f'fill="{fill}" font-family="{fam}" font-weight="{weight}">{t}</text>')

def monthly(D):
    W,H,B,T,L=760,230,34,12,40
    ms=D["months"]; mx=1100.0
    y=lambda v: T+(H-T-B)*(1-v/mx)
    bw=(W-L)/len(ms)
    o=[f'<line x1="{L}" x2="{W}" y1="{H-B}" y2="{H-B}" stroke="{LINE}" stroke-width="1"/>']
    for g in (0,250,500,750,1000):
        o.append(f'<line x1="{L}" x2="{W}" y1="{y(g):.1f}" y2="{y(g):.1f}" stroke="{LINE}" stroke-width=".6" stroke-dasharray="2 3"/>')
        o.append(_txt(L-5,y(g)+3,ar(g),7.5,"end"))
    for i,m in enumerate(ms):
        v=m["rev_day"]; x=L+i*bw+bw*.18; w=bw*.64
        col=GRN_L if v>=800 else (TEAL_L if v>=600 else RED_L)
        o.append(f'<rect x="{x:.1f}" y="{y(v):.1f}" width="{w:.1f}" height="{H-B-y(v):.1f}" fill="{col}" rx="2"/>')
        o.append(_txt(x+w/2,y(v)-4,ar(round(v)),9,"middle",INK,"600"))
        o.append(_txt(x+w/2,H-B+13,m["name"],8.5,"middle",MUT,"500",False))
        o.append(_txt(x+w/2,H-B+24,ar(m["inv_day"])+" طلب",7.5,"middle",MUT,"400",False))
    for v,c,lab in [(832,RED,"تعادل 832"),(687,AMB,"687"),(578,GRN,"578")]:
        o.append(f'<line x1="{L}" x2="{W-52}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="{c}" stroke-width="1.1" stroke-dasharray="4 3"/>')
        o.append(_txt(W-48,y(v)+3,ar(lab),7.5,"start",c,"600",False))
    return f'<svg viewBox="0 0 {W} {H}" width="100%">'+"".join(o)+'</svg>'

def daily(D):
    W,H,B,T,L=760,210,26,10,36
    s=D["series"]; n=len(s); mx=1350.0; bw=(W-L)/n
    y=lambda v: T+(H-T-B)*(1-v/mx)
    COL={4:GRN_L,5:GRN_L,6:TEAL_L,7:AMB_L,8:RED_L,9:GRN_L}
    o=[f'<line x1="{L}" x2="{W}" y1="{H-B}" y2="{H-B}" stroke="{LINE}" stroke-width="1"/>']
    for g in (0,400,800,1200):
        o.append(f'<line x1="{L}" x2="{W}" y1="{y(g):.1f}" y2="{y(g):.1f}" stroke="{LINE}" stroke-width=".5" stroke-dasharray="2 3"/>')
        o.append(_txt(L-5,y(g)+3,ar(g),7,"end"))
    for i,(d,v) in enumerate(s):
        m=int(d[5:7])
        o.append(f'<rect x="{L+i*bw+.25:.2f}" y="{y(v):.1f}" width="{bw-.5:.2f}" height="{H-B-y(v):.1f}" fill="{COL[m]}"/>')
    pts=[]
    for i in range(6,n):
        v=sum(s[j][1] for j in range(i-6,i+1))/7
        pts.append(f"{L+(i-3)*bw+bw/2:.1f},{y(v):.1f}")
    o.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>')
    for i,(d,v) in enumerate(s):
        if d[8:10]=="01" and i>0:
            o.append(f'<line x1="{L+i*bw:.1f}" x2="{L+i*bw:.1f}" y1="{T}" y2="{H-B}" stroke="{LINE}" stroke-width=".8"/>')
    MN=["أبريل","مايو","يونيو","يوليو","أغسطس","سبتمبر"]; idx=[0,30,61,91,122,153,165]
    for k in range(6):
        o.append(_txt(L+(idx[k]+idx[k+1])/2*bw,H-B+13,MN[k],8,"middle",MUT,"500",False))
    for v,c in [(832,RED),(578,GRN)]:
        o.append(f'<line x1="{L}" x2="{W}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="{c}" stroke-width="1" stroke-dasharray="4 3" opacity=".75"/>')
    return f'<svg viewBox="0 0 {W} {H}" width="100%">'+"".join(o)+'</svg>'

def hourly(D):
    W,H,B,T,L=760,230,34,12,38
    ha=D["hourly"]["april"]; hn=D["hourly"]["now"]
    ks=sorted(set(ha)|set(hn), key=lambda x:(int(x)-4)%24)
    mx=max(max(ha.values()),max(hn.values()))*1.12
    y=lambda v: T+(H-T-B)*(1-v/mx); bw=(W-L)/len(ks)
    o=[f'<line x1="{L}" x2="{W}" y1="{H-B}" y2="{H-B}" stroke="{LINE}" stroke-width="1"/>']
    for g in (0,50,100,150,200):
        if g>mx: break
        o.append(f'<line x1="{L}" x2="{W}" y1="{y(g):.1f}" y2="{y(g):.1f}" stroke="{LINE}" stroke-width=".6" stroke-dasharray="2 3"/>')
        o.append(_txt(L-5,y(g)+3,ar(g),7,"end"))
    for i,k in enumerate(ks):
        a=ha.get(k,0); b=hn.get(k,0); x=L+i*bw
        o.append(f'<rect x="{x+bw*.12:.1f}" y="{y(a):.1f}" width="{bw*.38:.1f}" height="{H-B-y(a):.1f}" fill="{TEAL_L}"/>')
        o.append(f'<rect x="{x+bw*.50:.1f}" y="{y(b):.1f}" width="{bw*.38:.1f}" height="{H-B-y(b):.1f}" fill="{TEAL}"/>')
        o.append(_txt(x+bw/2,H-B+11,ar(k),7,"middle"))
    o.append(f'<rect x="{L+6}" y="{T}" width="9" height="9" fill="{TEAL_L}"/>')
    o.append(_txt(L+19,T+8,"أبريل",8,"start",MUT,"500",False))
    o.append(f'<rect x="{L+66}" y="{T}" width="9" height="9" fill="{TEAL}"/>')
    o.append(_txt(L+79,T+8,"آخر ١٤ يومًا",8,"start",MUT,"500",False))
    return f'<svg viewBox="0 0 {W} {H}" width="100%">'+"".join(o)+'</svg>'

def dow(D):
    W,H,B,T,L=760,150,32,10,38
    d=D["dow"]; mx=max(x["rev"] for x in d)*1.18
    y=lambda v: T+(H-T-B)*(1-v/mx); bw=(W-L)/7
    o=[f'<line x1="{L}" x2="{W}" y1="{H-B}" y2="{H-B}" stroke="{LINE}" stroke-width="1"/>']
    avg=sum(x["rev"] for x in d)/7
    for i,x in enumerate(d):
        v=x["rev"]; px=L+i*bw+bw*.2; w=bw*.6
        col=GRN_L if v>avg*1.02 else (RED_L if v<avg*.95 else TEAL_L)
        o.append(f'<rect x="{px:.1f}" y="{y(v):.1f}" width="{w:.1f}" height="{H-B-y(v):.1f}" fill="{col}" rx="1.5"/>')
        o.append(_txt(px+w/2,y(v)-4,ar(v),8.5,"middle",INK,"600"))
        o.append(_txt(px+w/2,H-B+13,x["name"],8,"middle",MUT,"500",False))
        o.append(_txt(px+w/2,H-B+23,ar(x["inv"])+" طلب",7,"middle",MUT,"400",False))
    o.append(f'<line x1="{L}" x2="{W}" y1="{y(avg):.1f}" y2="{y(avg):.1f}" stroke="{INK}" stroke-width=".9" stroke-dasharray="4 3"/>')
    o.append(_txt(W-2,y(avg)-4,"المتوسط "+ar(round(avg)),7.5,"end",INK,"600",False))
    return f'<svg viewBox="0 0 {W} {H}" width="100%">'+"".join(o)+'</svg>'

def waterfall(FIN):
    W,H,B,T,L=760,200,44,14,40
    p=FIN["path"]; mx=1100.0
    y=lambda v: T+(H-T-B)*(1-v/mx); bw=(W-L)/len(p)
    o=[f'<line x1="{L}" x2="{W}" y1="{H-B}" y2="{H-B}" stroke="{LINE}" stroke-width="1"/>']
    for g in (0,250,500,750,1000):
        o.append(f'<line x1="{L}" x2="{W}" y1="{y(g):.1f}" y2="{y(g):.1f}" stroke="{LINE}" stroke-width=".6" stroke-dasharray="2 3"/>')
        o.append(_txt(L-5,y(g)+3,ar(g),7,"end"))
    LBL=["الدخول","+ الظهيرة","+ الصباح","+ خطة الرفع","مستوى أبريل"]
    for i,st in enumerate(p):
        v=st["rev_day"]; x=L+i*bw+bw*.2; w=bw*.6
        col=GRN_L if i==3 else (TEAL_L if i<3 else "#DDE7E8")
        o.append(f'<rect x="{x:.1f}" y="{y(v):.1f}" width="{w:.1f}" height="{H-B-y(v):.1f}" fill="{col}" rx="2"/>')
        o.append(_txt(x+w/2,y(v)-4,ar(v),9,"middle",INK,"600"))
        o.append(_txt(x+w/2,H-B+13,LBL[i],7.8,"middle",MUT,"500",False))
        n=st["nolevy_nohouse"]
        o.append(_txt(x+w/2,H-B+25,("+" if n>0 else "")+ar(f"{n:,}"),7.6,"middle",GRN if n>0 else RED,"600"))
        o.append(_txt(x+w/2,H-B+34,"ريال/شهر",6.8,"middle",MUT,"400",False))
    for v,c,t in [(832,RED,"832"),(687,AMB,"687"),(578,GRN,"578")]:
        o.append(f'<line x1="{L}" x2="{W-26}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="{c}" stroke-width="1.1" stroke-dasharray="4 3"/>')
        o.append(_txt(W-22,y(v)+3,t,7.5,"start",c,"600"))
    return f'<svg viewBox="0 0 {W} {H}" width="100%">'+"".join(o)+'</svg>'
