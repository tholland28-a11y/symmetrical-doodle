# CMC Alumni Networking Scraper

## Setup (one-time, on your local machine)

```bash
pip install playwright openpyxl pandas
playwright install chromium
```

## Run the scraper

```bash
python scrape_engage_cmc.py
```

1. A Chromium window opens and navigates to `engage.cmc.edu/directory`
2. **Log in with your CMC SSO** — the script waits for you
3. Once the directory loads, it auto-scrapes all pages
4. Outputs `networking_list.xlsx` with two sheets:
   - **Relevant Targets** — filtered to AI/Tech, IB, Consulting, Finance/Investing, Startups
   - **All Alumni** — everyone scraped

## Spreadsheet columns

| Column | Description |
|---|---|
| Name | Alumni full name |
| Title | Job title |
| Company/Org | Employer |
| Email | Email if listed in directory |
| Grad Year | CMC graduation year |
| Industry Tag | Auto-tagged: AI/Tech, IB/Corp Finance, Finance/Investing, Consulting, Startup |
| Connection | Fill in: CMC Alumni, Mutual Contact, Cold, etc. |
| Notes | Your outreach notes / follow-up dates |

## If the scraper misses profiles

Engage CMC uses a JavaScript-heavy frontend. If the auto-scraper finds 0 cards:
1. Open the browser dev tools (F12) while on the directory page
2. Go to Network tab, filter by `XHR/Fetch`
3. Look for an API call like `/api/directory` or `/users` — it may return JSON directly
4. Share the endpoint URL and I can write a direct API scraper instead (much faster)

## Relevant keywords used for filtering

**AI/Tech:** ai, machine learning, software engineer, product manager, data scientist, saas, fintech  
**IB/Corp Finance:** investment banking, goldman, morgan stanley, jp morgan, lazard, evercore, m&a, capital markets  
**Finance/Investing:** private equity, private credit, hedge fund, asset management, venture capital, wealth management  
**Consulting:** consulting, mckinsey, bain, bcg, deloitte, accenture, pwc, oliver wyman  
**Startup:** startup, founder, co-founder, venture  
