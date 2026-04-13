# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from database       import init_database, get_all_materials, lookup_material
from pdf_parser     import extract_text_from_pdf
from nlp_pipeline   import parse_document
from decision_engine import build_bom
from models         import QuotationResponse

app = FastAPI(
    title       = "Engineering Document Parser & Quotation Assistant",
    description = "Upload a PDF or paste text to get an auto-generated BoM and price estimate.",
    version     = "1.0.0",
)


# ── On startup: make sure the database exists ─────────────────────────────────
@app.on_event("startup")
async def on_startup():
    init_database()
    print("Server is ready.")


# ── GET /health ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["General"])
async def health():
    """Quick check that the server is alive."""
    return {"status": "ok"}


# ── GET /materials ────────────────────────────────────────────────────────────
@app.get("/materials", tags=["Materials"])
async def list_materials():
    """List every material in the cost database."""
    data = get_all_materials()
    return {"count": len(data), "materials": data}


# ── GET /materials/{name} ─────────────────────────────────────────────────────
@app.get("/materials/{name}", tags=["Materials"])
async def get_material(name: str):
    """Look up one material by name or code (e.g. ss304, brass, hdpe)."""
    result = lookup_material(name)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"'{name}' not found. Call /materials to see the full list."
        )
    return result


# ── POST /parse/text ──────────────────────────────────────────────────────────
@app.post("/parse/text", response_model=QuotationResponse, tags=["Parse"])
async def parse_text(payload: dict):
    """
    Paste raw RFQ text and get a BoM back.

    Send JSON:  { "text": "Material: SS304, 100x50x10mm, Qty: 5" }
    """
    raw_text = payload.get("text", "").strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="The 'text' field is empty.")

    extracted = parse_document(raw_text)
    bom, warnings = build_bom(extracted)
    total = round(sum(l.total_price_usd for l in bom), 2)

    return QuotationResponse(
        document_name   = "text_input",
        extracted_items = extracted,
        bom             = bom,
        grand_total_usd = total,
        warnings        = warnings,
    )


# ── POST /parse/pdf ───────────────────────────────────────────────────────────
@app.post("/parse/pdf", response_model=QuotationResponse, tags=["Parse"])
async def parse_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF engineering drawing or RFQ.
    Returns extracted parameters and a full priced BoM.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a .pdf file.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    try:
        raw_text = extract_text_from_pdf(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not read PDF: {e}")

    if not raw_text.strip():
        raise HTTPException(
            status_code=422,
            detail=(
                "No text extracted. The PDF may be a scanned image. "
                "Try /parse/text instead and paste the text manually."
            ),
        )

    extracted = parse_document(raw_text)
    bom, warnings = build_bom(extracted)
    total = round(sum(l.total_price_usd for l in bom), 2)

    if not extracted:
        warnings.append("No engineering parameters were detected in this document.")

    return QuotationResponse(
        document_name   = file.filename,
        extracted_items = extracted,
        bom             = bom,
        grand_total_usd = total,
        warnings        = warnings,
    )


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
