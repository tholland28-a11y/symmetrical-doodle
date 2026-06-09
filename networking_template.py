"""
Run this to generate a blank networking spreadsheet template (no scraping needed).
    python networking_template.py
"""

import pandas as pd

COLUMNS = ["Name", "Title", "Company/Org", "Email", "Grad Year", "Industry Tag", "Connection", "Notes"]

EXAMPLE_ROWS = [
    {
        "Name": "Jane Smith '18",
        "Title": "Associate",
        "Company/Org": "Goldman Sachs",
        "Email": "jsmith18@alumni.cmc.edu",
        "Grad Year": "2018",
        "Industry Tag": "IB / Corp Finance",
        "Connection": "CMC Alumni",
        "Notes": "Reached out 6/10 — follow up in 2 weeks",
    },
    {
        "Name": "Alex Chen '20",
        "Title": "Product Manager",
        "Company/Org": "OpenAI",
        "Email": "",
        "Grad Year": "2020",
        "Industry Tag": "AI / Tech",
        "Connection": "CMC Alumni",
        "Notes": "",
    },
]

df = pd.DataFrame(EXAMPLE_ROWS, columns=COLUMNS)

with pd.ExcelWriter("networking_template.xlsx", engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Networking List", index=False)
    ws = writer.sheets["Networking List"]
    for col in ws.columns:
        max_len = max((len(str(cell.value or "")) for cell in col), default=12)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 50)

print("Created networking_template.xlsx")
