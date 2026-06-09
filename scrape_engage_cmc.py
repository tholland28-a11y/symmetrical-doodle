"""
CMC Engage Alumni Directory Scraper — Direct API version
---------------------------------------------------------
No browser needed. Uses your live session token.

Install: pip3 install requests openpyxl pandas
Run:     python3 scrape_engage_cmc.py

TOKEN EXPIRES — if you get 401 errors, grab a fresh bearer token from
DevTools > Network > any Search request > Headers > authorization
and paste it into the TOKEN variable below.
"""

import requests
import pandas as pd
import time

# ── PASTE YOUR TOKEN HERE (everything after "bearer ") ──────────────────────
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1lIjoidGhvbGxhbmQyOEBzdHVkZW50cy5jbGFyZW1vbnRtY2tlbm5hLmVkdSIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL2VtYWlsYWRkcmVzcyI6InRob2xsYW5kMjhAc3R1ZGVudHMuY2xhcmVtb250bWNrZW5uYS5lZHUiLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9zaWQiOiI3ODY4MTIiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJVc2VyIiwiZXhwIjoxNzgzNjE1NDQ0LCJpc3MiOiJhcGlVc2VyIiwiYXVkIjoiYXBpQXVkaWVuY2UifQ.INtQybY-gbRiqBnbjMYbqRjvUsNHKSx1MSBDUFZ4rsk"
# ────────────────────────────────────────────────────────────────────────────

API_URL  = "https://api.ng.prod.us-east1.manual.graduway.com/Directory/Search"
PER_PAGE = 20

HEADERS = {
    "accept":           "application/json, text/plain, */*",
    "authorization":    f"bearer {TOKEN}",
    "content-type":     "application/json",
    "horizontalid":     "31436",
    "horizontalname":   "engagecmc",
    "sharedlanguageid": "4",
    "origin":           "https://engage.cmc.edu",
    "referer":          "https://engage.cmc.edu/",
    "user-agent":       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/149.0.0.0 Safari/537.36",
}

TARGET_KEYWORDS = [
    "artificial intelligence", "machine learning", " ai ", "startup",
    "venture", "founder", "software engineer", "product manager",
    "data scientist", "data analyst", "quantitative", "quant",
    "engineer", "developer", "saas", "fintech",
    "investment banking", "goldman", "morgan stanley", "jp morgan",
    "lazard", "evercore", "jefferies", "moelis", "houlihan",
    "private equity", "private credit", "hedge fund", "asset management",
    "equity research", "capital markets", "corporate finance",
    "wealth management", "m&a",
    "consulting", "consultant", "mckinsey", "bain", "bcg", "deloitte",
    "accenture", "pwc", "kpmg", "oliver wyman",
    "venture capital", "growth equity",
]


def tag_industry(title: str, company: str) -> str:
    text = f"{title} {company}".lower()
    tags = []
    if any(k in text for k in ["consulting", "consultant", "mckinsey", "bain", "bcg",
                                "deloitte", "accenture", "pwc", "kpmg", "oliver wyman"]):
        tags.append("Consulting")
    if any(k in text for k in ["investment banking", "goldman", "morgan stanley", "jp morgan",
                                "lazard", "evercore", "jefferies", "moelis", "m&a",
                                "capital markets", "corporate finance"]):
        tags.append("IB / Corp Finance")
    if any(k in text for k in ["private equity", "private credit", "hedge fund",
                                "asset management", "venture capital", "growth equity",
                                "wealth management"]):
        tags.append("Finance / Investing")
    if any(k in text for k in ["artificial intelligence", "machine learning", "saas",
                                "fintech", "software engineer", "developer", "data scientist"]):
        tags.append("AI / Tech")
    if any(k in text for k in ["startup", "founder", "co-founder"]):
        tags.append("Startup")
    return ", ".join(tags) if tags else "Other"


def is_relevant(title: str, company: str) -> bool:
    text = f" {title} {company} ".lower()
    return any(k in text for k in TARGET_KEYWORDS)


def fetch_page(page_number: int) -> dict:
    payload = {
        "sortType": 1,
        "freeText": None,
        "displayLostAlumni": False,
        "companyIds": [],
        "bounds": None,
        "coordinates": None,
        "paginationFilter": {
            "perPage": PER_PAGE,
            "pageNumber": page_number,
        },
        "totalCount": 0,
    }
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def parse_person(item: dict) -> dict:
    # Try multiple common field name patterns from Graduway API
    first = item.get("firstName") or item.get("first_name") or ""
    last  = item.get("lastName")  or item.get("last_name")  or ""
    name  = item.get("name") or item.get("fullName") or f"{first} {last}".strip()

    title   = (item.get("jobTitle") or item.get("job_title") or
               item.get("title") or item.get("position") or "")
    company = (item.get("company") or item.get("companyName") or
               item.get("organization") or item.get("employer") or "")
    email   = (item.get("email") or item.get("emailAddress") or
               item.get("email_address") or "")
    grad    = str(item.get("graduationYear") or item.get("graduation_year") or
                  item.get("classYear") or item.get("class_year") or "")
    major   = item.get("major") or item.get("fieldOfStudy") or ""

    return {
        "Name":        name,
        "Title":       title,
        "Company/Org": company,
        "Email":       email,
        "Grad Year":   grad,
        "Major":       major,
        "Industry Tag": tag_industry(title, company),
        "_relevant":   is_relevant(title, company),
        "Connection":  "CMC Alumni",
        "Notes":       "",
    }


def scrape_all() -> list:
    print("Fetching page 1 to detect total count...")
    first = fetch_page(1)

    # Detect total and list of items — Graduway wraps results differently
    total    = 0
    items    = []
    raw_keys = list(first.keys()) if isinstance(first, dict) else []

    if isinstance(first, list):
        items = first
    elif isinstance(first, dict):
        for key in ["data", "results", "items", "users", "members", "profiles", "people"]:
            if key in first and isinstance(first[key], list):
                items = first[key]
                break
        if not items:
            # fallback: first list value in the dict
            for v in first.values():
                if isinstance(v, list) and len(v) > 0:
                    items = v
                    break
        total = (first.get("totalCount") or first.get("total") or
                 first.get("count") or first.get("totalRecords") or 0)

    if not items:
        print(f"\nUnexpected response structure. Keys: {raw_keys}")
        print("First 500 chars of response:", str(first)[:500])
        print("\nShare this output so I can adjust the parser.")
        return []

    # If API didn't return totalCount, estimate from first batch
    if not total:
        total = len(items) * 50  # rough estimate, will stop when empty

    total_pages = max(1, -(-total // PER_PAGE))  # ceiling division
    print(f"Total users: {total} → {total_pages} pages\n")

    all_records = [parse_person(p) for p in items]
    print(f"  Page 1: {len(items)} records")

    for page in range(2, total_pages + 1):
        try:
            data  = fetch_page(page)
            batch = []
            if isinstance(data, list):
                batch = data
            elif isinstance(data, dict):
                for key in ["data", "results", "items", "users", "members", "profiles", "people"]:
                    if key in data and isinstance(data[key], list):
                        batch = data[key]
                        break
                if not batch:
                    for v in data.values():
                        if isinstance(v, list):
                            batch = v
                            break
            if not batch:
                print(f"  Page {page}: empty — stopping.")
                break
            all_records.extend(parse_person(p) for p in batch)
            print(f"  Page {page}/{total_pages}: {len(batch)} records  (total so far: {len(all_records)})")
            time.sleep(0.15)  # be polite to the server
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                print("\n401 Unauthorized — your token expired.")
                print("Grab a fresh token from DevTools and update TOKEN in the script.")
            else:
                print(f"  Page {page} error: {e}")
            break

    return all_records


def save_to_excel(records: list, filename="networking_list.xlsx"):
    if not records:
        print("No records to save.")
        return

    df_all = pd.DataFrame(records)
    df_rel = (df_all[df_all["_relevant"]]
              .drop(columns=["_relevant"])
              .sort_values(["Industry Tag", "Grad Year"]))
    df_full = df_all.drop(columns=["_relevant"])

    col_order = ["Name", "Title", "Company/Org", "Email", "Grad Year", "Major",
                 "Industry Tag", "Connection", "Notes"]

    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df_rel[col_order].to_excel(writer, sheet_name="Relevant Targets", index=False)
        df_full[col_order].to_excel(writer, sheet_name="All Alumni", index=False)
        for ws in writer.sheets.values():
            for col in ws.columns:
                w = max((len(str(c.value or "")) for c in col), default=10)
                ws.column_dimensions[col[0].column_letter].width = min(w + 4, 55)

    df_rel[col_order].to_csv(filename.replace(".xlsx", ".csv"), index=False)

    print(f"\n✓ Saved {len(df_rel)} relevant contacts → {filename}")
    print(f"  Total alumni scraped: {len(df_full)}")
    print(f"\nIndustry breakdown:")
    print(df_rel["Industry Tag"].value_counts().to_string())
    print(f"\nFile saved to your current folder.")


if __name__ == "__main__":
    records = scrape_all()
    save_to_excel(records)
