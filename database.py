# database.py
import sqlite3

DB_PATH = "engineering_costs.db"


def get_connection():
    """Open a connection to our database file."""
    return sqlite3.connect(DB_PATH)


def init_database():
    """
    Create the database tables and fill them with starting data.
    This only fills data once — if the data is already there, it skips.
    """
    conn = get_connection()
    cur  = conn.cursor()

    # ── Create materials table ──────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS material_costs (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            material_name    TEXT    NOT NULL,
            aliases          TEXT,
            cost_per_kg_usd  REAL    NOT NULL,
            density_g_cm3    REAL    NOT NULL,
            lead_time_days   INTEGER NOT NULL DEFAULT 14,
            notes            TEXT
        )
    """)

    # ── Seed data (only insert if table is empty) ───────────────────────────
    cur.execute("SELECT COUNT(*) FROM material_costs")
    if cur.fetchone()[0] == 0:
        materials = [
            # (name,                  aliases,                              $/kg,  density, lead, notes)
            ("Mild Steel",            "mild steel|ms|low carbon steel",     0.80,  7.85, 7,  "General purpose structural steel"),
            ("Stainless Steel 304",   "ss304|ss 304|304|304l|inox",         3.20,  7.93, 10, "Corrosion resistant, food-grade"),
            ("Stainless Steel 316",   "ss316|ss 316|316|316l|marine grade", 4.50,  7.98, 14, "Superior corrosion resistance"),
            ("Aluminum 6061",         "al6061|6061|6061-t6|aluminium 6061", 2.80,  2.70, 7,  "Lightweight, great machinability"),
            ("Aluminum 7075",         "al7075|7075|aerospace aluminum",     5.20,  2.81, 21, "High strength aerospace grade"),
            ("Brass C360",            "brass|c360|free-cutting brass",      6.50,  8.50, 10, "Excellent machinability"),
            ("Copper",                "cu|copper|pure copper",              8.90,  8.96, 14, "High electrical conductivity"),
            ("Titanium Grade 5",      "titanium|ti-6al-4v|ti grade 5",     35.00, 4.43, 30, "Premium aerospace material"),
            ("HDPE",                  "hdpe|high density polyethylene",     1.50,  0.95, 5,  "Chemical resistant plastic"),
            ("Delrin/Acetal",         "delrin|acetal|pom",                  3.80,  1.41, 7,  "Engineering plastic, low friction"),
            ("Carbon Steel 1045",     "1045|c45|carbon steel",             1.20,  7.85, 10, "Medium carbon, good strength"),
        ]
        cur.executemany("""
            INSERT INTO material_costs
            (material_name, aliases, cost_per_kg_usd, density_g_cm3, lead_time_days, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, materials)
        print(f"  Seeded {len(materials)} materials into database.")

    conn.commit()
    conn.close()
    print("Database ready!")


def lookup_material(search_name: str) -> dict | None:
    """
    Search for a material by name or alias.
    Returns a dict with all its info, or None if not found.
    """
    conn = get_connection()
    cur  = conn.cursor()
    search = search_name.lower().strip()

    cur.execute("""
        SELECT material_name, aliases, cost_per_kg_usd,
               density_g_cm3, lead_time_days, notes
        FROM material_costs
    """)
    rows = cur.fetchall()
    conn.close()

    for row in rows:
        name, aliases, cost, density, lead, notes = row
        # Check if search matches the main name
        if search in name.lower():
            return _row_to_dict(row)
        # Check if search matches any alias
        alias_list = [a.strip() for a in (aliases or "").lower().split("|")]
        for alias in alias_list:
            if alias and (alias in search or search in alias):
                return _row_to_dict(row)

    return None  # nothing found


def _row_to_dict(row: tuple) -> dict:
    """Helper: turn a database row tuple into a readable dictionary."""
    return {
        "material_name":   row[0],
        "cost_per_kg_usd": row[2],
        "density_g_cm3":   row[3],
        "lead_time_days":  row[4],
        "notes":           row[5],
    }


def get_all_materials() -> list[dict]:
    """Return every material in the database."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT material_name, cost_per_kg_usd, density_g_cm3,
               lead_time_days, notes
        FROM material_costs
        ORDER BY material_name
    """)
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "material":        r[0],
            "cost_per_kg_usd": r[1],
            "density_g_cm3":   r[2],
            "lead_time_days":  r[3],
            "notes":           r[4],
        }
        for r in rows
    ]


if __name__ == "__main__":
    init_database()
    result = lookup_material("ss304")
    print("Test lookup:", result)
