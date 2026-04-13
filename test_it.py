from database import init_database
from nlp_pipeline import parse_document
from decision_engine import build_bom

print("Init DB...")
init_database()

sample = """
Item 1:
Material: Stainless Steel 304
Dimension: 100mm x 50mm x 10mm
Quantity: 5

Item 2:
Material: Aluminum 6061
Dimension: 200 x 100 x 6
Qty: 10
"""

items = parse_document(sample)

print("\nParsed Items:")
for i in items:
    print(i)

bom, warnings = build_bom(items)

print("\nBoM:")
for b in bom:
    print(b)

print("\nWarnings:", warnings)
