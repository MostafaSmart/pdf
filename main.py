from fastapi import FastAPI, File, UploadFile
import pdfplumber
import re
import io
import arabic_reshaper
from bidi.algorithm import get_display
from fastapi.middleware.cors import CORSMiddleware



def fix_reversed_arabic(text):
    if not text:
        return text

    # عكس الجملة كاملة أولاً
    text = text[::-1]

    # عكس الكلمات داخل الجملة
    parts = text.split(" - ")
    parts = [p.strip() for p in parts]

    return " - ".join(parts)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
                name = fix_reversed_arabic(m.group(3).strip()) 
                items.append({
                    "name": name,
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