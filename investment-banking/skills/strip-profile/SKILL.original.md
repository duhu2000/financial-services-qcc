---
name: strip-profile
description: >
  Generates a concise 1-page "strip profile" for an investment-banking client or
  counterparty.  Activate when the user asks for a "strip profile", "company
  strip", "counterparty summary", or any request that implies a short (≈1 page)
  written profile of a corporate entity.

  # Purpose & Usage
  The strip profile is intended for:
    • New-client onboarding (KYC / AML checks)
    • Deal-team kick-off (M&A, ECM, DCM)
    • Counterparty credit or risk approval
    • Internal memoranda that do not require a full IC memo

  # Input requirements
  The user must supply **at least one** of the following:
    • Legal name of the company (and ticker if public)
    • LEI, CUSIP, ISIN or any other standard identifier
  If the user supplies only a ticker, resolve the legal name before writing the
  profile.

  # Output format (≈1 page)
  1. Header  – Legal name, domicile, identifiers, listing status
  2. Business description – 3-5 sentences: sector, products, revenue drivers,
     geography
  3. Ownership / structure – Ultimate parent, material subs, group chart if
     complex
  4. Financial snapshot – Latest FY revenue, EBITDA, Net debt (or caption if
     unavailable)
  5. Recent corporate activity – M&A, capital markets, restructuring (last 24m)
  6. Risk flags – Litigation, regulatory, ESG red-flags (brief)
  7. Source line – "Sources: [list primary data vendors used]"

  # Data sources (preferred hierarchy)
  1. Bloomberg / Refinitiv / FactSet (for public companies)
  2. Orbis / S&P Capital IQ (for private corporates)
  3. Company regulatory filings (10-K, 20-F, Annual Report)
  4. Exchange announcements (RNS, HKEX, etc.)
  5. Rating-agency reports (Moody’s, S&P, Fitch)

  # Tone & style
  • Neutral, factual, third-person
  • No investment opinion or valuation
  • Cite data gaps explicitly (e.g., "EBITDA: not disclosed")

  # Anti-hallucination rules
  • If a datapoint is not found, write "Not disclosed" rather than fabricating
  • Never infer revenue from employee count or sector averages
  • Verify ticker-to-name mapping before outputting financials

license: Apache-2.0
---

## STRIP-PROFILE WORKFLOW

When the user triggers this skill, follow the steps below in order.

### 1.  Gather Inputs
Ask the user (if not provided):
- "What is the legal name of the company?"
- "Is the company publicly listed? If so, ticker and exchange?"
- "Do you have an LEI, CUSIP or ISIN?"
- "Is there a specific deal or relationship context I should highlight?"

### 2.  Entity Resolution
- If the user gave a ticker, resolve → legal name using the primary market-data
  source.
- If the name is ambiguous (e.g., "Apple" vs "Apple Inc."), request
  clarification.
- Store the resolved legal name; it becomes the document header.

### 3.  Data Retrieval (parallel where possible)
Execute the following data calls:

| Data element | Primary source | Fallback source |
|--------------|----------------|-----------------|
| Legal name, domicile, identifiers | Bloomberg / Refinitiv | Company registry search |
| Business description | Latest Annual Report (10-K, 20-F) | Company website "About" |
| Revenue, EBITDA, Net debt | Bloomberg / Capital IQ | Rating-agency report |
| Ownership structure | S&P Capital IQ / Orbis | Shareholder disclosure filings |
| Recent corporate activity | Exchange announcements | News archive (FACTIVA) |
| Litigation / regulatory | Court dockets / Regulator registers | Company disclosure |

### 4.  Draft the Profile
Populate the 7-section template below.

---

**Strip Profile – [Legal Name]**
*Date: [YYYY-MM-DD]*

**1. Identification**
- Legal name: [ ]
- Domicile: [ ]
- LEI: [ ] (if available)
- Ticker / Exchange: [ ] (if public)
- auditors: [ ]
- Fiscal year end: [ ]

**2. Business Description**
[3-5 sentences describing: industry classification, primary products/services,
revenue drivers, geographic footprint]

**3. Ownership & Group Structure**
- Ultimate parent: [ ]
- Key operating subsidiaries: [list]
- % owned by parent: [ ]
- Listed / unlisted status of parent: [ ]
- Group chart: [attach if structure is complex]

**4. Financial Snapshot (Latest FY)**
| Metric | Value | Currency | Source |
|--------|-------|----------|--------|
| Revenue | [ ] | [ ] | [ ] |
| EBITDA | [ ] | [ ] | [ ] |
| Net Debt | [ ] | [ ] | [ ] |
| Market Cap (if public) | [ ] | [ ] | [ ] |

*Note: If a metric is unavailable, write "Not disclosed".*

**5. Recent Corporate Activity (Last 24 Months)**
- [Date] – [Event description, e.g., acquisition of X, issuance of Y bonds]
- [Date] – [Event description]
- …

**6. Risk Flags**
| Category | Description | Severity | Source |
|----------|-------------|----------|--------|
| Litigation | [ ] | [Low/Med/High] | [ ] |
| Regulatory | [ ] | [Low/Med/High] | [ ] |
| ESG | [ ] | [Low/Med/High] | [ ] |
| Other | [ ] | [Low/Med/High] | [ ] |

*If no material flags, write "None identified."*

**7. Sources**
- [Primary data vendor, e.g., Bloomberg Terminal, Refinitiv Eikon]
- [Secondary source, e.g., Moody's Investor Service, Company 10-K filed 2024-03-15]

---

### 5.  Quality Check
Before delivering the profile:
- [ ] All mandatory fields (legal name, domicile, identifiers) are populated.
- [ ] Financial figures include currency and source.
- [ ] No fabricated data; gaps are labeled "Not disclosed".
- [ ] Ticker-to-name mapping verified.
- [ ] Consistent date format (YYYY-MM-DD).

### 6.  Delivery
Output the profile in plain text or Markdown as appropriate for the user's
workflow. If the user asks for a specific template (e.g., bank KYC form), map
the sections above to that template.

## NEVER DO THESE

- Do not provide investment recommendations or valuation opinions.
- Do not guess financials based on sector averages or employee counts.
- Do not omit the source line; transparency on data provenance is required.
- Do not confuse ticker symbols (e.g., "T" for AT&T vs. "T" for Tesla in some
  jurisdictions).

ALL OUTPUTS MUST BE REVIEWED BY A QUALIFIED PROFESSIONAL BEFORE USE IN
REGULATED ACTIVITIES.
