"""
CMC Engage Alumni Directory Scraper
------------------------------------
Run this script LOCALLY on your machine (not in the cloud).

Requirements:
    pip install playwright openpyxl pandas
    playwright install chromium

Usage:
    python scrape_engage_cmc.py
"""

import asyncio
import re
import json
import pandas as pd
from playwright.async_api import async_playwright

DIRECTORY_URL = "https://engage.cmc.edu/directory"

TARGET_KEYWORDS = [
    "artificial intelligence", "machine learning", " ai ", "ml ", "startup",
    "venture", "founder", "software engineer", "product manager", "product",
    "data scientist", "data analyst", "quantitative", "quant", "tech",
    "engineer", "developer", "saas", "fintech", "deeptech",
    "investment banking", "investment bank", "goldman", "morgan stanley",
    "jp morgan", "jpmorgan", "bank of america", "citi", "citigroup",
    "lazard", "evercore", "jefferies", "moelis", "houlihan",
    "private equity", "private credit", "hedge fund", "asset management",
    "equity research", "capital markets", "corporate finance", "financial analyst",
    "wealth management", "portfolio", "m&a",
    "consulting", "consultant", "mckinsey", "bain", "bcg", "deloitte",
    "accenture", "pwc", "kpmg", "ey ", "ernst", "strategy&", "oliver wyman",
    "venture capital", "vc ", "growth equity",
]


def tag_industry(title: str, company: str) -> str:
    text = f"{title} {company}".lower()
    tags = []
    if any(k in text for k in ["consulting", "consultant", "mckinsey", "bain", "bcg",
                                 "deloitte", "accenture", "pwc", "kpmg", "oliver wyman"]):
        tags.append("Consulting")
    if any(k in text for k in ["investment banking", "investment bank", "goldman", "morgan stanley",
                                 "jp morgan", "lazard", "evercore", "jefferies", "moelis", "m&a",
                                 "capital markets", "corporate finance"]):
        tags.append("IB / Corp Finance")
    if any(k in text for k in ["private equity", "private credit", "hedge fund", "asset management",
                                 "venture capital", "vc ", "growth equity", "wealth management"]):
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


# Intercept API responses to grab JSON directly
api_records = []

async def scrape_directory():
    global api_records
    records = []
    intercepted_json = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        context = await browser.new_context()
        page = await context.new_page()

        # Intercept network responses to catch API calls
        async def handle_response(response):
            url = response.url
            if any(x in url for x in ["/api/", "/users", "/directory", "/members", "/search"]):
                try:
                    ct = response.headers.get("content-type", "")
                    if "json" in ct:
                        body = await response.json()
                        intercepted_json.append({"url": url, "data": body})
                        print(f"  [API] Intercepted: {url}")
                except Exception:
                    pass

        page.on("response", handle_response)

        print("Opening Engage CMC directory...")
        print(">>> Log in with your CMC SSO when the browser opens. <<<")
        print(">>> Press ENTER in this terminal once you can see alumni profiles. <<<\n")

        await page.goto(DIRECTORY_URL)

        # Wait for user to confirm they're logged in and see results
        await asyncio.get_event_loop().run_in_executor(None, input, "")

        print("Scraping... please wait.\n")
        await asyncio.sleep(3)

        # Save HTML snapshot for debugging
        html = await page.content()
        with open("engage_snapshot.html", "w") as f:
            f.write(html)
        print("Saved HTML snapshot to engage_snapshot.html")

        # Save intercepted API calls
        if intercepted_json:
            with open("engage_api_calls.json", "w") as f:
                json.dump(intercepted_json, f, indent=2)
            print(f"Saved {len(intercepted_json)} API call(s) to engage_api_calls.json")

        # --- Try to extract records from intercepted API JSON ---
        for call in intercepted_json:
            data = call["data"]
            # Common patterns: list at root, or nested under "data", "results", "users", "members"
            items = []
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                for key in ["data", "results", "users", "members", "directory", "items"]:
                    if key in data and isinstance(data[key], list):
                        items = data[key]
                        break

            for item in items:
                if not isinstance(item, dict):
                    continue
                # Try common field names
                name = (item.get("name") or item.get("full_name") or
                        f"{item.get('first_name','')} {item.get('last_name','')}".strip() or "")
                email = item.get("email") or item.get("email_address") or ""
                title = item.get("title") or item.get("position") or item.get("job_title") or ""
                company = (item.get("company") or item.get("organization") or
                           item.get("employer") or item.get("org") or "")
                grad_year = str(item.get("graduation_year") or item.get("grad_year") or
                                item.get("class_year") or "")

                if name:
                    records.append({
                        "Name": name,
                        "Title": title,
                        "Company/Org": company,
                        "Email": email,
                        "Grad Year": grad_year,
                        "Industry Tag": tag_industry(title, company),
                        "_relevant": is_relevant(title, company),
                        "Connection": "",
                        "Notes": "",
                    })

        # --- Fallback: scrape visible DOM ---
        if not records:
            print("No API JSON found — trying DOM scrape...")

            # Broad selector sweep
            all_selectors = [
                "li", "tr", "div[class]", "article", "section > div",
            ]
            best_cards = []
            for sel in all_selectors:
                cards = await page.query_selector_all(sel)
                # A "profile card" likely has 3-6 lines of text and contains an @ or a name pattern
                candidates = []
                for card in cards:
                    try:
                        text = await card.inner_text()
                        lines = [l.strip() for l in text.splitlines() if l.strip()]
                        if 2 <= len(lines) <= 10 and any(
                            re.search(r"[A-Z][a-z]+ [A-Z][a-z]+", l) for l in lines[:2]
                        ):
                            candidates.append((card, lines))
                    except Exception:
                        pass
                if len(candidates) > len(best_cards):
                    best_cards = candidates

            print(f"DOM: found {len(best_cards)} candidate cards")
            for card, lines in best_cards:
                name = lines[0] if lines else ""
                email = next((l for l in lines if "@" in l and "." in l), "")
                title = lines[1] if len(lines) > 1 else ""
                company = lines[2] if len(lines) > 2 else ""
                grad_year = ""
                for l in lines:
                    m = re.search(r"\b(19[89]\d|20[0-3]\d)\b", l)
                    if m:
                        grad_year = m.group()
                        break
                if name:
                    records.append({
                        "Name": name,
                        "Title": title,
                        "Company/Org": company,
                        "Email": email,
                        "Grad Year": grad_year,
                        "Industry Tag": tag_industry(title, company),
                        "_relevant": is_relevant(title, company),
                        "Connection": "",
                        "Notes": "",
                    })

        await browser.close()

    return records


def save_to_excel(records: list, filename="networking_list.xlsx"):
    if not records:
        print("\nNo records found.")
        print("Check engage_snapshot.html and engage_api_calls.json for clues.")
        print("Share those files and I can fix the selectors.")
        return

    df_all = pd.DataFrame(records)
    df_relevant = df_all[df_all["_relevant"] == True].drop(columns=["_relevant"])
    df_relevant = df_relevant.sort_values(["Industry Tag", "Grad Year"])
    df_full = df_all.drop(columns=["_relevant"])

    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df_relevant.to_excel(writer, sheet_name="Relevant Targets", index=False)
        df_full.to_excel(writer, sheet_name="All Alumni", index=False)
        for sheet_name in writer.sheets:
            ws = writer.sheets[sheet_name]
            for col in ws.columns:
                max_len = max((len(str(cell.value or "")) for cell in col), default=10)
                ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 50)

    df_relevant.to_csv(filename.replace(".xlsx", ".csv"), index=False)
    print(f"\nSaved {len(df_relevant)} relevant contacts to '{filename}'")
    print(f"Total alumni scraped: {len(df_full)}")
    print(f"\nIndustry breakdown:")
    print(df_relevant["Industry Tag"].value_counts().to_string())


async def main():
    records = await scrape_directory()
    save_to_excel(records)


if __name__ == "__main__":
    asyncio.run(main())
