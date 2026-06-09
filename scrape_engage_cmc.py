"""
CMC Engage Alumni Directory Scraper
------------------------------------
Run this script LOCALLY on your machine (not in the cloud).

Requirements:
    pip install playwright openpyxl pandas
    playwright install chromium

Usage:
    python scrape_engage_cmc.py

It will open a Chromium browser, let you log in with your CMC SSO,
then automatically scrape the alumni directory and save:
  - networking_list.xlsx   (Excel, ready to use)
  - networking_list.csv    (backup CSV)
"""

import asyncio
import re
import pandas as pd
from playwright.async_api import async_playwright

DIRECTORY_URL = "https://engage.cmc.edu/directory"

# Keywords to flag as high-relevance (case-insensitive)
TARGET_KEYWORDS = [
    # AI / Tech / Startups
    "artificial intelligence", "machine learning", "ai", "ml", "startup",
    "venture", "founder", "software engineer", "product manager", "product",
    "data scientist", "data analyst", "quantitative", "quant", "tech",
    "engineer", "developer", "saas", "fintech", "deeptech",
    # Finance / Banking
    "investment banking", "investment bank", "ib", "goldman", "morgan stanley",
    "jp morgan", "jpmorgan", "bank of america", "citi", "citigroup",
    "lazard", "evercore", "jefferies", "moelis", "houlihan",
    "private equity", "pe", "private credit", "hedge fund", "asset management",
    "equity research", "capital markets", "corporate finance", "financial analyst",
    "wealth management", "portfolio", "m&a",
    # Consulting
    "consulting", "consultant", "mckinsey", "bain", "bcg", "deloitte",
    "accenture", "pwc", "kpmg", "ey", "ernst", "strategy&", "oliver wyman",
    "l.e.k", "monitor", "roland berger",
    # Venture / Growth
    "venture capital", "vc", "growth equity", "principal", "associate",
    "analyst", "associate", "vice president", "vp", "director", "managing director",
]

COLUMNS = ["Name", "Title", "Company/Org", "Email", "Grad Year", "Industry Tag", "Connection", "Notes"]


def tag_industry(title: str, company: str) -> str:
    text = f"{title} {company}".lower()
    tags = []
    if any(k in text for k in ["consulting", "consultant", "mckinsey", "bain", "bcg",
                                 "deloitte", "accenture", "pwc", "kpmg", "ey", "oliver wyman"]):
        tags.append("Consulting")
    if any(k in text for k in ["investment banking", "investment bank", "goldman", "morgan stanley",
                                 "jp morgan", "lazard", "evercore", "jefferies", "moelis", "m&a",
                                 "capital markets", "corporate finance"]):
        tags.append("IB / Corp Finance")
    if any(k in text for k in ["private equity", "private credit", "hedge fund", "asset management",
                                 "venture capital", "vc", "growth equity", "wealth management", "portfolio"]):
        tags.append("Finance / Investing")
    if any(k in text for k in ["ai", "artificial intelligence", "machine learning", "saas",
                                 "fintech", "deeptech", "software", "engineer", "developer",
                                 "data scientist", "product manager"]):
        tags.append("AI / Tech")
    if any(k in text for k in ["startup", "founder", "co-founder", "venture"]):
        tags.append("Startup")
    return ", ".join(tags) if tags else "Other"


def is_relevant(title: str, company: str) -> bool:
    text = f"{title} {company}".lower()
    return any(k in text for k in TARGET_KEYWORDS)


async def scrape_directory():
    records = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()

        print("Opening Engage CMC directory...")
        print(">>> Log in with your CMC SSO when the browser opens. <<<")
        print(">>> The script will wait until you're on the directory page. <<<\n")

        await page.goto(DIRECTORY_URL)

        # Wait for manual login — poll until we see directory content
        print("Waiting for login and directory to load (up to 3 minutes)...")
        try:
            await page.wait_for_selector("[class*='profile'], [class*='directory'], [class*='user-card'], .directory-result",
                                         timeout=180_000)
        except Exception:
            print("Could not auto-detect directory content. Waiting 30 more seconds...")
            await asyncio.sleep(30)

        print("Directory loaded. Starting scrape...\n")

        page_num = 1
        while True:
            print(f"Scraping page {page_num}...")

            # Grab all profile cards — Engage uses varying class names; we cast a wide net
            cards = await page.query_selector_all("[class*='profile'], [class*='user-card'], [class*='directory-item'], li[class*='user']")

            if not cards:
                # Try alternate structure: table rows
                cards = await page.query_selector_all("tr[class*='user'], div[class*='result']")

            for card in cards:
                text = await card.inner_text()
                lines = [l.strip() for l in text.splitlines() if l.strip()]

                name = lines[0] if lines else ""
                # Email: look for @
                email = next((l for l in lines if "@" in l and "." in l), "")
                # Title / Company: usually lines 1-3
                title = lines[1] if len(lines) > 1 else ""
                company = lines[2] if len(lines) > 2 else ""
                # Grad year: 4-digit number in 1990-2035
                grad_year = ""
                for l in lines:
                    m = re.search(r"\b(19[89]\d|20[0-3]\d)\b", l)
                    if m:
                        grad_year = m.group()
                        break

                if not name:
                    continue

                industry_tag = tag_industry(title, company)
                relevant = is_relevant(title, company)

                records.append({
                    "Name": name,
                    "Title": title,
                    "Company/Org": company,
                    "Email": email,
                    "Grad Year": grad_year,
                    "Industry Tag": industry_tag,
                    "_relevant": relevant,
                    "Connection": "",
                    "Notes": "",
                })

            # Try to go to next page
            next_btn = await page.query_selector("a[aria-label='Next'], button[aria-label='Next'], .pagination-next, a:has-text('Next')")
            if next_btn:
                await next_btn.click()
                await page.wait_for_load_state("networkidle")
                page_num += 1
            else:
                print("No more pages found.")
                break

        await browser.close()

    return records


def save_to_excel(records: list, filename="networking_list.xlsx"):
    if not records:
        print("No records scraped.")
        return

    df_all = pd.DataFrame(records)

    # Sheet 1: Relevant only (sorted by industry tag)
    df_relevant = df_all[df_all["_relevant"] == True].drop(columns=["_relevant"])
    df_relevant = df_relevant.sort_values(["Industry Tag", "Grad Year"])

    # Sheet 2: All alumni
    df_full = df_all.drop(columns=["_relevant"])

    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df_relevant.to_excel(writer, sheet_name="Relevant Targets", index=False)
        df_full.to_excel(writer, sheet_name="All Alumni", index=False)

        # Auto-width columns
        for sheet_name in writer.sheets:
            ws = writer.sheets[sheet_name]
            for col in ws.columns:
                max_len = max((len(str(cell.value or "")) for cell in col), default=10)
                ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 50)

    df_relevant.to_csv(filename.replace(".xlsx", ".csv"), index=False)
    print(f"\nDone! Saved {len(df_relevant)} relevant contacts to '{filename}'")
    print(f"Total alumni scraped: {len(df_full)}")
    print(f"\nIndustry breakdown:")
    print(df_relevant["Industry Tag"].value_counts().to_string())


async def main():
    records = await scrape_directory()
    save_to_excel(records)


if __name__ == "__main__":
    asyncio.run(main())
