from fastapi import FastAPI, File, UploadFile
import pdfplumber
import re
import io
import arabic_reshaper
from bidi.algorithm import get_display

def fix_arabic(text):
    if not text:
        return text

    # إصلاح تشكيل الحروف
    reshaped = arabic_reshaper.reshape(text)

    # إصلاح اتجاه العربية
    return get_display(reshaped)

app = FastAPI()

def fix_reversed_arabic(text):
    if not text:
        return text
    return " - ".join([p.strip()[::-1] for p in text[::-1].split(" - ")])

pattern = re.compile(
    r'^([\d,]+\.\d{2})\s+([\d,]+\.\d{2})\s+1\s+\S+\s+(.*?)\s*\*?\s*([0-9\-]+)$'
)

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        content = await file.read()

        pdf_file = io.BytesIO(content)

        with pdfplumber.open(pdf_file) as pdf:
            text = "\n".join([p.extract_text() or "" for p in pdf.pages])

        lines = text.split("\n")

        items = []

        for line in lines:
            m = pattern.match(line)
            if m:
                items.append({
                    "name": fix_arabic(m.group(3)),
                    "price": float(m.group(2).replace(",", "")),
                    "totalPrice": float(m.group(1).replace(",", "")),
                    "code": m.group(4),
                    "quantity": 1
                })

        return {
            "success": True,
            "count": len(items),
            "data": items
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }