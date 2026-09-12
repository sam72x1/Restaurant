# -*- coding: utf-8 -*-
CSS = """
@page { size: A4; margin: 17mm 15mm 16mm 15mm; }
@page :first { margin: 0; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body{ margin:0; direction:rtl; font-family:"IBM Plex Sans Arabic",sans-serif;
      font-size:9.6pt; line-height:1.72; color:#14232A; background:#fff; }
.n{ font-family:"IBM Plex Mono","IBM Plex Sans Arabic",monospace; font-variant-numeric:tabular-nums; }
h1,h2,h3{ font-family:"Noto Kufi Arabic",sans-serif; margin:0; text-wrap:balance; }
p{ margin:0 0 7pt; max-width:none; }
strong{ font-weight:600; color:#0C1A20; }
em{ font-style:normal; font-weight:600; color:#0A6068; }

/* ── الغلاف ── */
.cover{ height:297mm; padding:26mm 22mm; display:flex; flex-direction:column;
        background:#0A3940; color:#E8F2F2; page-break-after:always; }
.cover .kicker{ font-size:10pt; letter-spacing:.16em; color:#7FC4C8; font-weight:600; }
.cover h1{ font-size:34pt; line-height:1.22; margin:12mm 0 0; color:#fff; }
.cover .tag{ font-size:13pt; color:#A9D3D5; margin-top:6mm; line-height:1.7; font-weight:400;
             font-family:"IBM Plex Sans Arabic",sans-serif; }
.cover .spacer{ flex:1; }
.cover .facts{ display:grid; grid-template-columns:1fr 1fr; gap:0; border-top:1px solid #2A6068; }
.cover .facts div{ padding:5mm 0; border-bottom:1px solid #17494F; }
.cover .facts dt{ font-size:8.6pt; color:#7FC4C8; margin-bottom:1.5mm; }
.cover .facts dd{ margin:0; font-size:15pt; font-weight:600; font-family:"IBM Plex Mono","IBM Plex Sans Arabic",monospace; color:#fff; }
.cover .foot{ margin-top:8mm; font-size:8.4pt; color:#6FA9AD; line-height:1.8; }

/* ── الأقسام ── */
section{ page-break-inside:auto; }
h2.sec{ font-size:15pt; color:#0A3940; margin:0 0 2mm; padding-bottom:2.5mm;
        border-bottom:2.2pt solid #0A6068; page-break-after:avoid; }
h2.sec .num{ font-family:"IBM Plex Mono","IBM Plex Sans Arabic",monospace; font-size:10pt; color:#0A6068; margin-left:4mm; }
h3.sub{ font-size:10.6pt; color:#0A3940; margin:6mm 0 2.5mm; page-break-after:avoid; }
.lede{ color:#4A6670; font-size:10pt; margin-bottom:4mm; }
.brk{ page-break-before:always; }

/* ── الجداول ── */
table{ border-collapse:collapse; width:100%; font-size:9pt; margin:3mm 0 4mm;
       page-break-inside:auto; }
thead{ display:table-header-group; }
tr{ page-break-inside:avoid; }
th,td{ padding:2.1mm 2.6mm; text-align:right; border-bottom:.4pt solid #D9E4E6; }
thead th{ background:#EDF3F3; font-size:8.2pt; font-weight:600; color:#3C5A63;
          border-bottom:.9pt solid #B6CBCE; letter-spacing:.02em; }
td.f,th.f{ font-family:"IBM Plex Mono","IBM Plex Sans Arabic",monospace; font-variant-numeric:tabular-nums; white-space:nowrap; direction:ltr; text-align:right; }
thead th.f{ direction:rtl; }
tr.tot td{ background:#EDF3F3; font-weight:600; border-top:.9pt solid #B6CBCE; }
tr.hi td{ background:#E4F1E9; font-weight:600; }
tr.lo td{ background:#FBEAE8; }
.pos{ color:#14653E; } .neg{ color:#96271F; }
table.sm{ font-size:8.4pt; } table.sm th,table.sm td{ padding:1.5mm 2mm; }

/* ── الملاحظات ── */
.note{ border-right:3pt solid #0A6068; background:#EDF5F5; padding:3mm 4mm;
       margin:3.5mm 0; font-size:9.2pt; page-break-inside:avoid; }
.note.w{ border-color:#9A6206; background:#FBF1DF; }
.note.b{ border-color:#96271F; background:#FBEAE8; }
.note.o{ border-color:#14653E; background:#E4F1E9; }
.note .t{ font-weight:600; display:block; margin-bottom:1mm; }

/* ── البطاقات ── */
.kpis{ display:grid; grid-template-columns:repeat(4,1fr); gap:2.5mm; margin:4mm 0; }
.kpi{ border:.5pt solid #C9D9DC; border-radius:2mm; padding:3mm; page-break-inside:avoid; }
.kpi dt{ font-size:7.8pt; color:#52707A; margin-bottom:1mm; line-height:1.4; }
.kpi dd{ margin:0; font-size:15pt; font-weight:600; font-family:"IBM Plex Mono","IBM Plex Sans Arabic",monospace; line-height:1.1; }
.kpi dd span{ font-size:7.8pt; font-weight:400; color:#52707A;
              font-family:"IBM Plex Sans Arabic",sans-serif; margin-right:1.5mm; }
.kpi.g{ background:#E4F1E9; border-color:#9CCBB4; } .kpi.g dd{ color:#14653E; }
.kpi.r{ background:#FBEAE8; border-color:#DFA59F; } .kpi.r dd{ color:#96271F; }
.kpi.y{ background:#FBF1DF; border-color:#DCBC85; } .kpi.y dd{ color:#9A6206; }

.grade{ display:inline-block; font-size:7.4pt; font-weight:600; padding:.3mm 1.8mm;
        border-radius:1mm; border:.4pt solid; white-space:nowrap; }
.g-v{ color:#14653E; background:#E4F1E9; border-color:#9CCBB4; }
.g-c{ color:#9A6206; background:#FBF1DF; border-color:#DCBC85; }
.g-e{ color:#52707A; background:#EDF3F3; border-color:#C2D2D5; }

ol.steps{ list-style:none; counter-reset:s; margin:0; padding:0; }
ol.steps li{ counter-increment:s; border:.5pt solid #D2E0E2; border-radius:2mm;
             padding:2.8mm 3.5mm 2.8mm 3.5mm; margin-bottom:2.2mm; font-size:9.2pt;
             page-break-inside:avoid; position:relative; padding-right:11mm; }
ol.steps li::before{ content:counter(s); position:absolute; right:3.5mm; top:2.8mm;
             font-family:"IBM Plex Mono","IBM Plex Sans Arabic",monospace; font-weight:600; color:#fff;
             background:#0A6068; width:5.2mm; height:5.2mm; border-radius:50%;
             display:flex; align-items:center; justify-content:center; font-size:7.6pt; }
ol.steps b{ font-weight:600; }
ol.steps span{ display:block; color:#4A6670; font-size:8.8pt; margin-top:.8mm; }

.risk{ border:.5pt solid #D2E0E2; border-right-width:3pt; border-radius:2mm;
       padding:3mm 4mm; margin-bottom:2.5mm; page-break-inside:avoid; }
.risk.r1{ border-right-color:#96271F; } .risk.r2{ border-right-color:#9A6206; }
.risk.r3{ border-right-color:#7A939B; }
.risk .rh{ font-weight:600; font-size:9.8pt; margin-bottom:1mm; }
.risk .rl{ font-size:7.4pt; font-weight:600; padding:.3mm 1.8mm; border-radius:1mm;
           margin-right:2mm; vertical-align:1pt; }
.risk.r1 .rl{ color:#96271F; background:#FBEAE8; } .risk.r2 .rl{ color:#9A6206; background:#FBF1DF; }
.risk.r3 .rl{ color:#52707A; background:#EDF3F3; }
.risk p{ font-size:8.9pt; color:#43606A; margin:0 0 1.5mm; }
.risk .fx{ font-size:8.9pt; color:#14232A; } .risk .fx b{ color:#0A6068; }

.chart{ border:.5pt solid #D2E0E2; border-radius:2mm; padding:3mm 3mm 1.5mm;
        margin:3mm 0; page-break-inside:avoid; }
.chart .cap{ font-size:8pt; color:#52707A; margin-top:1.5mm; }
.kill{ border:1.2pt dashed #96271F; background:#FBEAE8; border-radius:2mm;
       padding:4mm 5mm; page-break-inside:avoid; }
.kill .rule{ font-family:"IBM Plex Mono","IBM Plex Sans Arabic",monospace; font-size:11pt; font-weight:600;
       background:#fff; border:.5pt solid #DFA59F; border-radius:1.5mm;
       padding:3mm 4mm; margin:3mm 0; line-height:1.75; }
.ltr{ direction:ltr; unicode-bidi:isolate; display:inline-block; }
.toc{ font-size:9.6pt; }
.toc div{ display:flex; gap:3mm; padding:1.5mm 0; border-bottom:.4pt dotted #C9D9DC; }
.toc .tn{ font-family:"IBM Plex Mono","IBM Plex Sans Arabic",monospace; color:#0A6068; font-weight:600; width:8mm; }
ul.plain{ margin:2mm 0; padding-right:5mm; font-size:9.2pt; color:#43606A; }
ul.plain li{ margin-bottom:1.6mm; }
"""
