# models.py

# models.py
from pydantic import BaseModel
from typing import Optional

class ExtractedItem(BaseModel):
    """One thing we found in the document."""
    material:  Optional[str] = None   # e.g. "Stainless Steel 304"
    dimension: Optional[str] = None   # e.g. "100mm x 50mm x 10mm"
    tolerance: Optional[str] = None   # e.g. "±0.05mm"
    quantity:  Optional[int] = None   # e.g. 5
    raw_text:  Optional[str] = None   # the original line it came from

class BomLineItem(BaseModel):
    """One row on the Bill of Materials."""
    item_number:     int
    material:        str
    dimension:       str
    quantity:        int
    unit_price_usd:  float
    total_price_usd: float
    notes:           str

class QuotationResponse(BaseModel):
    """The full response we send back."""
    document_name:    str
    extracted_items:  list[ExtractedItem]
    bom:              list[BomLineItem]
    grand_total_usd:  float
    warnings:         list[str]
