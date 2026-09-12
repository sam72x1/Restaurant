# مولّد دراسة الجدوى (PDF)

يُنتج `reports/جدوى-مشوي-كور.pdf` من البيانات الخام مباشرة. لا رقم مكتوب يدويًا في الوثيقة.

## التسلسل

```
facts.py    → facts.json     كل قياس من ملفَّي فواتير رواء ومن فواتير الموردين
finance.py  → finance.json   التكاليف والتعادل والمسار وخطة الرفع، مبنية على facts.json
charts.py                    رسوم SVG للطباعة، كل قيمة من facts.json
css.py                       أنماط الطباعة A4
build.py    → study.html     تركيب الوثيقة
audit.py                     تدقيق مستقل: يعيد اشتقاق الأرقام بمسار مختلف ويقارنها
```

## التشغيل

```bash
cd tools/pdf
python3 facts.py && python3 finance.py && python3 build.py
chromium --headless --no-pdf-header-footer \
  --print-to-pdf="../../reports/جدوى-مشوي-كور.pdf" \
  --virtual-time-budget=20000 "file://$PWD/study.html"
python3 audit.py     # يجب أن يخرج: صفر انحرافات
```

## الخطوط

تُضمَّن IBM Plex Sans Arabic وIBM Plex Mono وNoto Kufi Arabic كـ base64 داخل الملف،
فلا يعتمد الإخراج على خطوط النظام. تُجلب من Google Fonts وتُحوَّل مرة واحدة إلى
`fonts/embedded.css`.

## قواعد ثابتة

- التقريب نصف-لأعلى في المتن والجداول والرسوم معًا (994.5 ← 995).
- خلايا الأرقام معزولة اتجاهيًا (`direction:ltr`) حتى لا تنقلب السوالب والمديات.
- كل رقم يحمل درجة إثبات: مقيس / منقول / استنتاج.
- `audit.py` يجب أن يمرّ قبل أي تسليم.
