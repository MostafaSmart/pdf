from fastapi import FastAPI, File, UploadFile
import pdfplumber
import re

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
    content = await file.read()

    with pdfplumber.open(io.BytesIO(content)) as pdf:
        text = "\n".join([p.extract_text() or "" for p in pdf.pages])

    lines = text.split("\n")

    items = []

    for line in lines:
        m = pattern.match(line)
        if m:
            items.append({
                "name": fix_reversed_arabic(m.group(3)),
                "price": float(m.group(2).replace(",", "")),
                "totalPrice": float(m.group(1).replace(",", "")),
                "code": m.group(4),
                "quantity": 1
            })

    return {"count": len(items), "data": items}