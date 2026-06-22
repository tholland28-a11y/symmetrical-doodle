# Industry → Typical Function Map

A starting template for Stage 2 (Functional Decomposition). Look up the
company's industry (from `company_profile.industry.primary`), take the function
list as a **starting point**, then tailor it to the specific company — add what
is missing, drop what does not apply, and weight each function `core` /
`standard` / `peripheral` for that company.

These lists are deliberately not exhaustive. The judgment about what is material
to a given company is the human's, exercised at Checkpoint 1.

## Cross-industry functions (apply to most companies)

These recur almost everywhere; include the ones that matter for the company:

- Cybersecurity & Information Security
- Finance & Controllership
- Human Capital / Talent
- Legal, Risk & Compliance
- Procurement & Supplier Management
- IT & Data
- Sales & Revenue
- Marketing & Brand
- Customer Success / Support

## By industry

### Banking / Financial Services
- Credit & Underwriting
- Risk Management (credit, market, operational)
- Regulatory Compliance & Financial Crime (AML/KYC)
- Treasury & Liquidity
- Payments & Settlement
- Wealth / Asset Management
- Cybersecurity
- Fraud Management

### Retail / Consumer
- Merchandising & Assortment
- Supply Chain & Logistics
- Store / Field Operations
- E-commerce & Omnichannel
- Pricing & Promotion
- Payments & Loss Prevention
- Customer Loyalty
- Cybersecurity (POS / payment data)

### Cybersecurity / Software Vendor
- Product Security & Secure Development (SDLC)
- Threat Intelligence & Detection Engineering
- Incident Response
- Cloud & Infrastructure Security
- Identity & Access Management
- Compliance & Certifications (SOC 2, ISO 27001, FedRAMP)
- Customer Trust & Vulnerability Disclosure
- Sales Engineering

### Manufacturing / Industrial
- Production & Operations (lean / OEE)
- Quality Management
- Supply Chain & Procurement
- Maintenance & Reliability
- Health, Safety & Environment (HSE)
- Engineering & Product Development
- OT / ICS Security
- Logistics & Distribution

### Healthcare / Life Sciences
- Clinical Operations / Care Delivery
- Regulatory Affairs (FDA / EMA)
- Quality & Patient Safety
- Revenue Cycle Management
- Pharmacovigilance / Safety
- Data Privacy & HIPAA Security
- Supply Chain (cold chain, devices)
- Research & Development

### SaaS / Technology
- Product Management
- Engineering & Reliability (SRE)
- Cloud & Platform Security
- Go-to-Market / Sales
- Customer Success & Retention
- Data & Analytics
- Finance (SaaS metrics: ARR, NRR, CAC)
- Trust, Privacy & Compliance

### Energy / Utilities
- Generation / Production Operations
- Grid / Network Operations & Reliability
- HSE & Environmental Compliance
- Regulatory Affairs
- Asset Maintenance & Reliability
- OT / Critical-Infrastructure Security
- Trading & Risk
- Capital Projects

### Professional Services / Consulting
- Client Delivery & Engagement Management
- Practice / Capability Development
- Business Development & Sales
- Talent & People
- Knowledge Management
- Risk & Independence / Compliance
- Finance & Utilization

## How to use this

1. Match the company to the closest industry (or blend two if it spans them).
2. Start from that list plus the relevant cross-industry functions.
3. Tailor: a payments-heavy retailer needs a strong Payments/Loss-Prevention
   function; a single-product SaaS may fold several functions into one.
4. Weight each for this company and write a 1-2 sentence scope and research
   themes per `schemas/function.schema.json`.
5. Present the result at Checkpoint 1 for approval.
