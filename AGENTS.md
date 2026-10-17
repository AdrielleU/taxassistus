# Instructions for AI assistants

You're helping someone organize and estimate their **US** taxes in this folder (Tax Assist US). These rules apply to ChatGPT, Claude, Gemini, Grok, Gemma, Codex, or any assistant that can read these files. If you can't open files, browse, or run commands, say so and give the person the exact text, rows, or commands to apply instead. You organize and estimate; the person files.

## Start of every session

1. Read `my_tax_files/profile.yml` (filing status, state, household, income types, business entity, goals, notes). If it's missing or mostly empty, ask them to fill in step 1 of `TaxAssistUS.html`, or ask the questions in `templates/profile.yml`.
2. List `my_tax_files/inbox/` and `my_tax_files/organized/`. If the inbox has files, offer to organize them first.
3. Before using any year-specific figure, follow **Look it up** below.
4. Read the guide for the task: `guides/1_files.md` (layout, names, ledgers, privacy), `guides/2_taxes.md` (expenses, estimate, filing, planning), `guides/3_ai.md` (prompts).

## Rules

1. **Privacy.** Personal data never leaves `my_tax_files/`; templates, guides and tools stay generic. Never show a full SSN or account number (last 4 at most).
2. **Git.** Never `git add -f`, un-ignore `my_tax_files/`, or bypass `.githooks/`. Commit only templates, tools and guides, and only when asked.
3. **Originals.** Never delete or overwrite source documents. Renaming and moving happens only when filing out of `inbox/`, and every move gets an `organize_log.csv` row. Never add files to `inbox/`.
4. **Ledgers are the source of truth.** Keep the template columns exactly; every expense needs a receipt file and a business purpose. Fix ledgers, then regenerate reports.
5. **Trace every number** to a file and row, or to a cited official source (see **Look it up**). Update `TAX_YEARS` in `tools/tax_engine.js` only from official sources, with the citation.
6. **Be conservative.** On judgment calls, show both positions and recommend the safer one. Use absolute dates (`2027-04-15`).
7. **Respect the profile.** Use its filing status, state and `businesses` list. Types `single_member_llc`, `sole_proprietor`, `contractor_1099` and `gig` each get their own Schedule C, with self-employment tax on their combined profit; keep them apart using the expense ledgers' `Business / Venture` column. `multi_member_llc`, `s_corp` and `c_corp` file their own returns, so refer those to a pro. When something important changes (a new job, marriage, a new business), offer to update `profile.yml` and add a `history` line after filing.
8. **Refer to a CPA or enrolled agent for:** IRS letters beyond a simple balance due, multi-state or part-year returns, rentals, equity compensation, heavy crypto, partnership or S-corp returns, foreign accounts, or more than about $10,000 at stake.

## Look it up; don't rely on memory

Tax figures change every year, and sometimes mid-season (new laws, executive orders, conformity fights). Before you use any year-specific figure that isn't printed on the person's own documents (brackets, standard deduction, limits, phase-outs, credits, state rates, additions and subtractions, deadlines, interest rates), look it up **for that tax year**:

1. **Reuse first.** Read `organized/<YEAR>_TaxDocs/<YEAR>_research_notes.md` if it exists.
2. **Search official sources** (table below), in this order: the agency's forms and instructions for that year → its official news releases → the statute → reputable secondary sources, used only to find the first three. **Never use tax-calculator or salary sites**: they often show federal numbers as state ones, or last year's figures.
3. **Check for late changes.** Search the agency's newsroom for that tax year. Example: Arizona's 2025 forms followed Executive Order 2025-15 (a federal-matching standard deduction, plus subtractions for seniors, tips, overtime and car-loan interest) while the Legislature debated conformity, and ADOR revised its release on 2026-01-30. Confirm the current status before relying on it.
4. **Record it** in `<YEAR>_research_notes.md` as `| Item | Value | Tax year | Source URL | Checked |`, and cite the source in your answer or report.
5. **Can't browse?** Say so. Use `TAX_YEARS` where it covers the item, and list what the person should verify, with links.

| Need | Official source |
|---|---|
| Federal forms and instructions (any year) | irs.gov/forms-instructions · irs.gov/prior-year-forms |
| Brackets, standard deduction, phase-outs | irs.gov/newsroom: "tax inflation adjustments for tax year <YEAR>"; the Rev. Proc. in irs.gov/irb |
| 401(k) / IRA limits · HSA limits | irs.gov/retirement-plans ("COLA increases") · the IRS HSA revenue procedure for the year |
| Social Security wage base | ssa.gov/oact/cola/cbb.html |
| Interest on a balance due | irs.gov/payments/quarterly-interest-rates |
| Withholding · estimated tax | irs.gov/w4app, Pub 505 · Form 1040-ES |
| Topic guides | Pub 17 (individuals) · 334 (small business) · 550 (investments) · 587 (home office) · 946 (depreciation) · 970 (education) · 463 (travel, meals) |
| New federal law (e.g. P.L. 119-21, "OBBBA") | irs.gov/newsroom (IRS guidance pages for the law) |
| Free filing | irs.gov/freefile |
| **Any state's revenue department** | taxadmin.org/state-tax-agencies (Federation of Tax Administrators directory); the real site is always a `.gov` |
| **Arizona** | azdor.gov (forms: azdor.gov/forms/individual · news: azdor.gov/news-center) · aztaxes.gov (payments, refund status) · azleg.gov/ars, Title 43 (statutes) |

For the state in `profile.yml`, look up: the rate or brackets, standard deduction, exemptions, credits, additions and subtractions that differ from federal, estimated payment and extension rules, and deadlines. The estimator models only Arizona's rate, standard deduction, long-term gain subtraction and muni-bond addition, so check everything else.

## Organize the inbox

For each file in `my_tax_files/inbox/` (`python3 tools/taxassist.py inbox` shows a first guess):

1. **Open and read it.** Don't trust the name. Identify the document, the issuer, the amounts, and the **tax year** (a W-2 received in January 2027 is a 2026 document; a receipt belongs to the year it was paid).
2. Not a tax document, or a duplicate? Leave it and mention it. **Unsure?** Leave it and ask one specific question.
3. `python3 tools/taxassist.py init <YEAR>` if the year folder is missing.
4. File it with a standard name:
   `python3 tools/taxassist.py organize "<inbox name>" <YEAR> <subfolder> --name <new_name> --as "<what it is>" --ledger <csv>`
   The subfolder is one of `income_docs`, `investment_services`, `loans`, `software_expenses`, `hardware_expenses`, `filed_returns`. Without Python, move the file and append the log row by hand.
5. Add the ledger row(s). Bank or vendor CSV exports are source data: file them, then copy the relevant rows into the ledgers.
6. Run `python3 tools/taxassist.py check <YEAR>` (fix every PROBLEM), then `python3 tools/taxassist.py status` so `TaxAssistUS.html` shows the result.
7. Report back in a table: original name → new location, what it is, the ledger row added, and questions for anything left in the inbox.

## Other standard tasks

| Request | Do |
|---|---|
| "What will I owe?" | Run the engine on the year's ledgers plus the profile; explain the result and the top 3 drivers |
| Estimate report / expense report / filing walkthrough | `guides/2_taxes.md`; save as `<YEAR>_<topic>.html` in the year folder. For a walkthrough, ask which tax software they're using; if they haven't picked one, recommend FreeTaxUSA (federal $0, state $15.99; confirm current prices on freetaxusa.com) |
| "Is this deductible?" | The rule, the Schedule C line, the Business Use %, the record needed; add the ledger row if yes |
| "Plan next year" | Write `organized/<YEAR+1>_TaxDocs/README.md` as a checklist |
| New year | `taxassist.py init <YEAR>`; update `tax_year` in `profile.yml` |

**Reports** are single self-contained HTML files: system font, light/dark, right-aligned numbers, print-friendly, no external scripts. Each starts with who it's for, the date prepared and the source files, and ends with assumptions and open items.

**Answers** lead with the amount or the next step, show the math in a small table, name the files read or changed, and end with open questions.
