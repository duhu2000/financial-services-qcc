---
name: ic-memo
description: >
  Drafts an Investment Committee (IC) memorandum for private-equity or
  venture-capital transactions.  Activate when the user asks for an "IC memo",
  "investment committee memo", "deal memo", or any request that implies a formal
  write-up for an investment decision.

  # Purpose & Usage
  The IC memo is the primary decision document for:
    • New equity or quasi-equity investments (buyouts, growth, venture)
    • Follow-on rounds (pro-rata, up-round, down-round)
    • Exits (full or partial), secondary sales, or write-offs

  # Input requirements
  The user should supply (or you must gather) the following:
    • Target company name, sector, stage (seed → pre-IPO)
    • Deal size, instrument (ordinary / pref / convertible), pre-money valuation
    • Sponsors / co-investors (if any)
    • Investment thesis (value creation levers)
    • Key risks and mitigants
    • Exit assumptions (timeframe, multiple, path)
  If any item is missing, explicitly flag it as "TBD" in the memo.

  # Output format (standard 7-section IC memo)
  1. Executive Summary – Recommendation, amount, valuation, key terms
  2. Company Overview – Business model, market, competitive position
  3. Transaction Overview – Structure, size, syndicate, use of proceeds
  4. Investment Thesis – Strategic rationale, value creation plan
  5. Financial Analysis – Historical, projections, returns analysis
  6. Risk Factors – Market, execution, regulatory, ESG; mitigants
  7. Appendices – Cap table, comps, organigram (if available)

  # Data sources
  • Target data room (VDR) – primary source for financials
  • Management presentations – for business model
  • Sector reports – for TAM / market growth
  • Comparable company / transaction analysis – for valuation
  • Legal / tax / ESG due-diligence reports – for risk section

  # Tone & style
  • Professional, concise (10-15 pages)
  • Use bullet points for arguments; prose for narrative
  • Quantify where possible (revenue CAGR, margin expansion, MOIC, IRR)

  # Anti-hallucination rules
  • Do not invent financial projections
  • Do not assume exit multiples without citing comparables
  • Flag "data pending" rather than filling gaps with assumptions

license: Apache-2.0
---

## IC-MEMO WORKFLOW

When the user triggers this skill, follow the steps below.

### 1.  Gather Inputs
Ask the user (or confirm) the following:
- "What is the target company name and sector?"
- "What is the deal size and instrument (ordinary, preferred, convertible)?"
- "What is the pre-money valuation?"
- "Who are the co-investors or lead investors?"
- "What is the investment thesis (2-3 bullet points)?"
- "What are the top 3 risks you want highlighted?"
- "Do you have a data room or management model I should reference?"

### 2.  Populate the 7-Section Template

---

**Investment Committee Memorandum**

**Target:** [Company Name] ([Sector], [Stage])
**Date:** [YYYY-MM-DD]
**Prepared by:** [Analyst / Associate Name]

---

**1. Executive Summary**

| Item | Detail |
|------|--------|
| Recommendation | [Proceed / Decline / Hold] |
| Investment Amount | [Currency] [X] million |
| Instrument | [Ordinary / Preferred / Convertible / SAFE] |
| Pre-Money Valuation | [Currency] [X] million |
| Post-Money Valuation | [Currency] [X] million |
| Ownership (%) | [X]% |
| Syndicate | [Lead: X, Co-investors: Y, Z] |
| Use of Proceeds | [e.g., growth capex, working capital, M&A] |
| Expected Exit | [Year] via [IPO / Trade sale / Secondary] |
| Target MOIC | [X]x |
| Target IRR | [X]% |

**2. Company Overview**

*2.1 Business Model*
[2-3 sentences describing what the company does, how it makes money, and its
core value proposition.]

*2.2 Market Opportunity*
- TAM: [Currency] [X] billion (CAGR [X]%)
- SAM: [Currency] [X] billion
- Key growth drivers: [bullet list]

*2.3 Competitive Position*
- Primary competitors: [list]
- Competitive moat: [e.g., proprietary tech, network effects, brand]
- Market share: [X]% (if known)

*2.4 Management Team*
- CEO: [Name, background]
- CFO: [Name, background]
- Key gaps / additions needed: [list]

**3. Transaction Overview**

*3.1 Structure*
[Diagram or description of deal structure: equity vs. convertible, tranches,
conditions precedent]

*3.2 Syndicate & Governance*
- Board seats: [Investor X: N seats]
- Protective provisions: [list]
- Information rights: [monthly / quarterly]

*3.3 Use of Proceeds*
| Category | Amount | % of Total |
|----------|--------|------------|
| [e.g., R&D] | [ ] | [ ]% |
| [e.g., Sales & Marketing] | [ ] | [ ]% |
| [e.g., Capex] | [ ] | [ ]% |
| Working Capital | [ ] | [ ]% |

**4. Investment Thesis**

*4.1 Strategic Rationale*
[2-3 bullets on why this fits the fund strategy.]

*4.2 Value Creation Plan*
| Initiative | Revenue Impact | Margin Impact | Timeline |
|------------|---------------|---------------|----------|
| [e.g., new product launch] | +[X]% | +[X]bps | Y1-Y2 |
| [e.g., geographic expansion] | +[X]% | neutral | Y2-Y3 |

*4.3 Downside Protection*
[liquidation preference, anti-dilution, milestones, etc.]

**5. Financial Analysis**

*5.1 Historical Performance*
| Metric | Y-2 | Y-1 | LTM |
|--------|-----|-----|-----|
| Revenue | [ ] | [ ] | [ ] |
| Gross Profit | [ ] | [ ] | [ ] |
| EBITDA | [ ] | [ ] | [ ] |
| Net Income | [ ] | [ ] | [ ] |

*5.2 Projections (Management Case)*
| Metric | Y+1 | Y+2 | Y+3 | Exit |
|--------|------|------|------|------|
| Revenue | [ ] | [ ] | [ ] | [ ] |
| EBITDA | [ ] | [ ] | [ ] | [ ] |
| EBITDA Margin | [ ]% | [ ]% | [ ]% | [ ]% |

*5.3 Returns Analysis*
- Entry EBITDA multiple: [X]x
- Exit EBITDA multiple: [X]x (justified by: [comparable analysis])
- Gross MOIC: [X]x
- Net MOIC (after fees, carry): [X]x
- Gross IRR: [X]%
- Net IRR: [X]%

**6. Risk Factors & Mitigants**

| Risk | Likelihood | Impact | Mitigant |
|------|------------|--------|----------|
| [e.g., Market saturation] | Med | High | [Diversification, pricing power] |
| [e.g., Key person dependency] | Med | High | [Key-man insurance, succession plan] |
| [e.g., Regulatory change] | Low | Med | [Legal review, government relations] |
| [e.g., Technology obsolescence] | Med | Med | [R&D spend, IP protection] |

**7. Appendices**

*7.1 Cap Table (Pre- and Post-Money)*
[table]

*7.2 Comparable Companies / Transactions*
[table]

*7.3 Organigram*
[if available]

*7.4 Term Sheet Summary*
[if available]

---

### 3.  Quality Check
Before submitting the memo:
- [ ] All "TBD" items are flagged for follow-up.
- [ ] Financial figures reconcile with the data room.
- [ ] Valuation multiples are justified with comparables.
- [ ] Risk factors are specific (not generic).
- [ ] Exit assumptions are consistent with market practice.

### 4.  Delivery
Output the memo in Markdown or Word format as required by the firm's template.
If the user has a specific IC memo template (e.g., "Use our Firm X template"),
map the sections above to that template.

## NEVER DO THESE

- Do not write the memo without flagging missing data points.
- Do not assume financial projections are conservative; label the case (base /
  upside / downside).
- Do not omit the risk section; every deal has risks that must be disclosed.
- Do not fabricate comparable transactions; cite source and date.

ALL OUTPUTS MUST BE REVIEWED BY INVESTMENT COMMITTEE MEMBERS AND LEGAL COUNSEL
BEFORE APPROVAL.
