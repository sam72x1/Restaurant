#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعادة تجميع الملفات المرفوعة من بوابة الرفع.

الصفحة تقسّم كل ملف إلى أجزاء base64 داخل قاعدة بيانات الأداة، لأن حد
المستند الواحد 256 كيلوبايت. هذا السكربت يعيد تجميع الأجزاء إلى الملف الأصلي.

الاستخدام:
  1) اسحب الأجزاء إلى مجلد محلي (من جلسة كلود):
       Artifact read_db · db_op=list · collection="uploads/<id>/parts" · out_dir=<pull>
  2) أعد التجميع:
       python3 model/pull_uploads.py --pull <pull> --out data/

كل ملف يخرج باسم: <التصنيف>/<المعرّف>_<الاسم الأصلي>
"""
import argparse, base64, glob, json, os, sys

FOLDER = {
    "pos": "pos-reports", "bank": "bank", "vat": "bank",
    "contract": "contracts", "license": "licenses",
    "supplier": "invoices", "utility": "invoices",
    "stock": "stock", "menu": "menu",
    "payroll": "invoices", "other": "invoices",
}


def load_meta(pull_dir, doc_id):
    """بيانات المستند، إن كانت مسحوبة بجانب الأجزاء."""
    path = os.path.join(pull_dir, "uploads", doc_id + ".json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def reassemble(parts_dir):
    """يدمج أجزاء base64 بترتيب أسمائها ويعيد البايتات."""
    files = sorted(glob.glob(os.path.join(parts_dir, "*.json")))
    if not files:
        return None, 0
    chunks = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            body = json.load(fh)
        chunks.append((int(body.get("i", len(chunks))), body.get("b64", "")))
    chunks.sort(key=lambda c: c[0])
    return base64.b64decode("".join(c[1] for c in chunks)), len(files)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pull", required=True, help="المجلد الذي سُحبت إليه المستندات")
    ap.add_argument("--out", default="data", help="مجلد الإخراج")
    args = ap.parse_args()

    roots = glob.glob(os.path.join(args.pull, "uploads", "*", "parts"))
    if not roots:
        sys.exit("لم يُعثر على أي أجزاء تحت: " + args.pull)

    done = 0
    for parts_dir in sorted(roots):
        doc_id = os.path.basename(os.path.dirname(parts_dir))
        data, n = reassemble(parts_dir)
        if not data:
            print(f"  ⚠ {doc_id}: لا توجد أجزاء")
            continue
        meta = load_meta(args.pull, doc_id)
        name = meta.get("name") or (doc_id + ".bin")
        folder = FOLDER.get(meta.get("category", "other"), "invoices")
        dest_dir = os.path.join(args.out, folder)
        os.makedirs(dest_dir, exist_ok=True)
        safe = "".join(c for c in name if c not in '/\\:*?"<>|').strip() or "file.bin"
        dest = os.path.join(dest_dir, f"{doc_id}_{safe}")
        with open(dest, "wb") as fh:
            fh.write(data)
        note = meta.get("note", "")
        print(f"  ✔ {dest}  ({len(data):,} بايت، {n} جزء)" + (f" — {note}" if note else ""))
        done += 1

    print(f"\nأُعيد تجميع {done} ملفًا في: {args.out}")


if __name__ == "__main__":
    main()
