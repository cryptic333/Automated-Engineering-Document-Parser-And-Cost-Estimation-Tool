import re
from models import ExtractedItem

MATERIAL_MAP = {
    "ss304": "Stainless Steel 304",
    "stainless steel 304": "Stainless Steel 304",
    "ss316": "Stainless Steel 316",
    "mild steel": "Mild Steel",
    "aluminum 6061": "Aluminum 6061",
    "6061": "Aluminum 6061",
    "hdpe": "HDPE",
}

def extract_block_items(text: str):
    """Split RFQ into logical item blocks instead of lines"""
    blocks = re.split(r'\n\s*\n', text)  # split by empty lines
    return [b.strip() for b in blocks if len(b.strip()) > 10]


def find_material(text: str):
    t = text.lower()
    for k, v in MATERIAL_MAP.items():
        if k in t:
            return v
    return None


def find_dimension(text: str):
    m = re.search(r'\d+.*x.*\d+.*x?.*\d*', text.lower())
    return m.group() if m else None


def find_quantity(text: str):
    m = re.search(r'(qty|quantity|nos|pcs)[^\d]*(\d+)', text.lower())
    return int(m.group(2)) if m else None


def find_tolerance(text: str):
    m = re.search(r'±\s*\d+(\.\d+)?\s*mm', text)
    return m.group() if m else None


def parse_document(text: str):
    items = []

    blocks = extract_block_items(text)

    for block in blocks:
        item = ExtractedItem(
            material=find_material(block),
            dimension=find_dimension(block),
            tolerance=find_tolerance(block),
            quantity=find_quantity(block),
            raw_text=block
        )

        if item.material or item.dimension:
            items.append(item)

    return items
