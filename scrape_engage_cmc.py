"""
CMC Engage Alumni Directory Scraper
Run: python3 scrape_engage_cmc.py
"""

import asyncio
import re
import json
import pandas as pd
from playwright.async_api import async_playwright

DIRECTORY_URL = "https://engage.cmc.edu/directory"

TARGET_KEYWORDS = [
    "artificial intelligence", "machine learning", " ai ", "startup",
    "venture", "founder", "software engineer", "product manager",
    "data scientist", "data analyst", "quantitative", "quant",
    "engineer", "developer", "saas", "fintech",
    "investment banking", "goldman", "morgan stanley", "jp morgan",
    "lazard", "evercore", "jefferies", "moelis",
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
    if any(k in text for k in ["investment banking", "goldman", "morgan stanley",
                                "jp morgan", "lazard", "evercore", "jefferies", "moelis",
                                "m&a", "capital markets", "corporate finance"]):
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


async def scrape_directory():
    records = []
    intercepted_json = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Intercept API calls
        async def handle_response(response):
            url = response.url
            if any(x in url for x in ["/api/", "/users", "/directory", "/members", "/search", "/people"]):
                try:
                    ct = response.headers.get("content-type", "")
                    if "json" in ct:
                        body = await response.json()
                        intercepted_json.append({"url": url, "data": body})
                        print(f"  [API hit] {url}")
                except Exception:
                    pass

        page.on("response", handle_response)

        await page.goto(DIRECTORY_URL)

        print("\n" + "="*60)
        print("STEP 1: A browser window just opened.")
        print("STEP 2: Log into Engage CMC with your CMC email.")
        print("STEP 3: Wait until you can SEE alumni names/profiles.")
        print("STEP 4: Come back here and press ENTER.")
        print("="*60 + "\n")

        # Block here until user presses ENTER
        input("Press ENTER when you can see alumni profiles in the browser: ")

        print("\nGot it! Waiting 5 seconds for page to fully settle...")
        await asyncio.sleep(5)

        # Save snapshot
        html = await page.content()
        with open("engage_snapshot.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Saved engage_snapshot.html")

        if intercepted_json:
            with open("engage_api_calls.json", "w") as f:
                json.dump(intercepted_json, f, indent=2, default=str)
            print(f"Saved {len(intercepted_json)} API response(s) to engage_api_calls.json")

        # --- Parse API JSON if available ---
        for call in intercepted_json:
            data = call["data"]
            items = []
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                for key in ["data", "results", "users", "members", "directory", "items", "profiles"]:
                    if key in data and isinstance(data[key], list):
                        items = data[key]
                        break

            for item in items:
                if not isinstance(item, dict):
                    continue
                name = (item.get("name") or item.get("full_name") or
                        f"{item.get('first_name', '')} {item.get('last_name', '')}".strip())
                email = item.get("email") or item.get("email_address") or ""
                title = item.get("title") or item.get("position") or item.get("job_title") or ""
                company = (item.get("company") or item.get("organization") or
                           item.get("employer") or "")
                grad_year = str(item.get("graduation_year") or item.get("grad_year") or
                                item.get("class_year") or "")
                if name and name.strip():
                    records.append({
                        "Name": name.strip(),
                        "Title": title,
                        "Company/Org": company,
                        "Email": email,
                        "Grad Year": grad_year,
                        "Industry Tag": tag_industry(title, company),
                        "_relevant": is_relevant(title, company),
                        "Connection": "CMC Alumni",
                        "Notes": "",
                    })

        # --- DOM fallback ---
        if not records:
            print("No API JSON matched — trying DOM scrape...")
            # Dump all text blocks that look like person cards
            all_text_blocks = await page.evaluate("""() => {
                const results = [];
                document.querySelectorAll('*').forEach(el => {
                    const text = el.innerText;
                    if (!text) return;
                    const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                    // Look for elements with 2-8 lines, first line looks like a name
                    if (lines.length >= 2 && lines.length <= 8) {
                        const firstLine = lines[0];
                        // Name pattern: two capitalized words
                        if (/^[A-Z][a-z]+ [A-Z]/.test(firstLine) && firstLine.length < 50) {
                            results.push(lines);
                        }
                    }
                });
                // Deduplicate
                const seen = new Set();
                return results.filter(block => {
                    const key = block[0];
                    if (seen.has(key)) return false;
                    seen.add(key);
                    return true;
                });
            }""")

            print(f"DOM: found {len(all_text_blocks)} candidate profile blocks")
            for lines in all_text_blocks:
                name = lines[0]
                email = next((l for l in lines if "@" in l and "." in l), "")
                title = lines[1] if len(lines) > 1 else ""
                company = lines[2] if len(lines) > 2 else ""
                grad_year = ""
                for l in lines:
                    m = re.search(r"\b(19[89]\d|20[0-3]\d)\b", l)
                    if m:
                        grad_year = m.group()
                        break
                records.append({
                    "Name": name,
                    "Title": title,
                    "Company/Org": company,
                    "Email": email,
                    "Grad Year": grad_year,
                    "Industry Tag": tag_industry(title, company),
                    "_relevant": is_relevant(title, company),
                    "Connection": "CMC Alumni",
                    "Notes": "",
                })

        print(f"\nTotal records extracted: {len(records)}")

        input("\nPress ENTER to close the browser: ")
        await browser.close()

    return records


def save_to_excel(records, filename="networking_list.xlsx"):
    if not records:
        print("\nNo records found.")
        print("Share engage_snapshot.html and engage_api_calls.json so I can fix the selectors.")
        return

    df_all = pd.DataFrame(records)
    df_relevant = df_all[df_all["_relevant"]].drop(columns=["_relevant"]).sort_values(
        ["Industry Tag", "Grad Year"])
    df_full = df_all.drop(columns=["_relevant"])

    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df_relevant.to_excel(writer, sheet_name="Relevant Targets", index=False)
        df_full.to_excel(writer, sheet_name="All Alumni", index=False)
        for ws in writer.sheets.values():
            for col in ws.columns:
                w = max((len(str(c.value or "")) for c in col), default=10)
                ws.column_dimensions[col[0].column_letter].width = min(w + 4, 50)

    df_relevant.to_csv(filename.replace(".xlsx", ".csv"), index=False)
    print(f"\nSaved {len(df_relevant)} relevant contacts → {filename}")
    print(f"Total alumni: {len(df_full)}")
    print("\nIndustry breakdown:")
    print(df_relevant["Industry Tag"].value_counts().to_string())


async def main():
    records = await scrape_directory()
    save_to_excel(records)


if __name__ == "__main__":
    asyncio.run(main())
