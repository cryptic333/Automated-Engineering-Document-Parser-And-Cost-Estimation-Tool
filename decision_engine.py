import re
from models import ExtractedItem, BomLineItem
from database import lookup_material

DEFAULT_THICK_MM = 10.0
MINIMUM_PRICE = 8.0


def parse_dimensions_mm(dim_str):
    if not dim_str:
        return None

    nums = re.findall(r'\d+\.?\d*', dim_str)
    nums = [float(n) for n in nums]

    if len(nums) >= 3:
        return nums[0], nums[1], nums[2]
    elif len(nums) == 2:
        return nums[0], nums[1], DEFAULT_THICK_MM
    elif len(nums) == 1:
        return nums[0], DEFAULT_THICK_MM, DEFAULT_THICK_MM

    return None


def calc_weight(dims, density):
    l, w, h = dims
    volume_cm3 = (l * w * h) / 1000
    return volume_cm3 * density / 1000


def calc_price(mat, dims):
    if dims:
        weight = calc_weight(dims, mat["density_g_cm3"])
        base = weight * mat["cost_per_kg_usd"]
    else:
        base = mat["cost_per_kg_usd"]

    return max(round(base * 1.5, 2), MINIMUM_PRICE)


def build_bom(items):
    bom = []
    warnings = []
    i = 1

    for item in items:
        if not item.material:
            warnings.append(f"Skipped: {item.raw_text[:50]}")
            continue

        mat = lookup_material(item.material)
        if not mat:
            warnings.append(f"Material not found: {item.material}")
            continue

        dims = parse_dimensions_mm(item.dimension)
        qty = item.quantity or 1

        unit = calc_price(mat, dims)
        total = unit * qty

        bom.append(BomLineItem(
            item_number=i,
            material=mat["material_name"],
            dimension=item.dimension or "N/A",
            quantity=qty,
            unit_price_usd=unit,
            total_price_usd=total,
            notes="auto-generated"
        ))

        i += 1

    return bom, warnings
