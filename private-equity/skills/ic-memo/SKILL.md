# Investment Committee Memo

description: Draft a structured investment committee memo for PE deal approval. Synthesizes due diligence findings, financial analysis, and deal terms into a professional IC-ready document. Use when preparing for investment committee, writing up a deal, or creating a formal recommendation. Triggers on "write IC memo", "investment committee memo", "deal write-up", "prepare IC materials", or "recommendation memo".

## Workflow

### Step 1: Gather Inputs & Qichacha MCP Full Due Diligence

Collect from the user (or from prior analysis in the session), and **for Chinese target companies, automatically enrich data via Qichacha MCP**:

- Company overview and business description
- Industry/market context
- Historical financials (3-5 years)
- Management assessment
- Deal terms (price, structure, financing)
        - **Due diligence findings (commercial, financial, legal, operational)**: For Chinese companies, trigger `/qcc-full-dd-profile` to obtain comprehensive data including:
            - **工商注册信息** (get_company_registration_info)
            - **股东信息** (get_shareholder_info) 及股权穿透
            - **全面的风险信息** (get_company_risk_info)，涵盖司法、经营、行政等
            - **知识产权资产** (get_patent_info, get_trademark_info, get_software_copyright_info, get_copyright_work_info)
            - **经营动态** (get_bidding_info，招投标信息)
- Value creation plan / 100-day plan
- Returns analysis (base, upside, downside)


### Step 2: Draft Memo Structure

Standard IC memo format:

**I. Executive Summary** (1 page)
- Company description, deal rationale, key terms
- Recommendation and headline returns
        - Top 3 risks and mitigants (For Chinese companies, prioritize Qichacha MCP 识别的风险，例如：失信被执行人、行政处罚、司法文书等)

**II. Company Overview** (1-2 pages)
- Business description, products/services
- Customer base and go-to-market
- Competitive positioning
- Management team

**III. Industry & Market** (1 page)
- Market size and growth
- Competitive landscape
- Secular trends / tailwinds
- Regulatory environment

**IV. Financial Analysis** (2-3 pages)
- Historical performance (revenue, EBITDA, margins, cash flow)
- Quality of earnings adjustments
- Working capital analysis
- Capex requirements

**V. Investment Thesis** (1 page)
- Why this is an attractive investment (3-5 pillars)
- Value creation levers (organic growth, margin expansion, M&A, multiple expansion)
- 100-day priorities

**VI. Deal Terms & Structure** (1 page)
- Enterprise value and implied multiples
- Sources & uses
        - Capital structure / leverage (For Chinese companies, leverage Qichacha MCP 的 `get_shareholder_info` 获取详细股权结构)
- Key legal terms

**VII. Returns Analysis** (1 page)
- Base, upside, and downside scenarios
- IRR and MOIC across scenarios
- Key assumptions driving returns
- Sensitivity analysis

**VIII. Risk Factors** (1 page)
        - Key risks ranked by severity and likelihood (For Chinese companies, 整合 Qichacha MCP 的 `get_company_risk_info` 风险发现)
- Mitigants for each risk
- Deal-breaker risks (if any)

**IX. Recommendation**
- Clear recommendation: Proceed / Pass / Conditional proceed
- Key conditions or next steps

### Step 3: Output Format

- Default: Word document (.docx) with professional formatting
- Alternative: Markdown for quick review
- Include tables for financials and returns, not just prose

## Important Notes

- IC memos should be factual and balanced — present both bull and bear cases honestly
- Don't minimize risks. IC members will find them anyway; credibility matters
- Use the firm's standard memo template if the user provides one
- Financial tables should tie — check that EBITDA bridges, S&U balances, and returns math is consistent
- Ask for missing inputs rather than making assumptions on deal terms or returns
