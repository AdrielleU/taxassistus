# 1 · Files, folders and privacy

## Layout

```
my_tax_files/                      ← private: ignored by git + blocked by the pre-commit hook
├── profile.yml                    ← who you are, tax-wise (step 1 of TaxAssistUS.html)
├── state_tax_rates.csv            ← optional: only rows you add or correct (the full table is the project's)
├── inbox/                         ← drop anything here, any name. Only you add files.
├── organized/
│   ├── organize_log.csv           ← one row per file moved out of the inbox
│   └── <YEAR>_TaxDocs/            ← one per TAX year (a 2025 W-2 that arrives in Jan 2026 goes in 2025)
│       ├── w2_<YEAR>.csv                    business_income_<YEAR>.csv
│       ├── software_expenses_<YEAR>.csv     hardware_expenses_<YEAR>.csv
│       ├── investments_<YEAR>.csv           payments_and_deductions_<YEAR>.csv
│       ├── income_docs/  investment_services/  loans/
│       ├── software_expenses/  hardware_expenses/      ← receipts for the two expense ledgers
│       ├── filed_returns/                              ← final returns + confirmations
│       ├── <YEAR>_research_notes.md                    ← figures the AI looked up: value, source URL, date checked
│       └── <YEAR>_<topic>.html                         ← generated reports
└── status.js                      ← snapshot for TaxAssistUS.html (`taxassist.py status`)
```

## Names

`<vendor>_<doctype>_<YYYY>_<MM>[-pN].<ext>`, lowercase, no spaces: `googleworkspace_invoice_2025_03.pdf`, `w2_allaboard_2025.pdf`, `1099_wealthfront_2025.pdf`, `federal_return_2025.pdf`.

## Ledgers (CSV)

Keep the template headers exactly. One row per document or transaction, dates `YYYY-MM-DD`, plain numbers (`1234.56`, negative for losses). An optional last `TOTAL` row is ignored, but `check` verifies it adds up.

| Ledger | One row per | Key columns |
|---|---|---|
| `w2_` | W-2 | Boxes 1–6, 12 (D = 401(k), W = HSA, DD = health info), 16–17 |
| `business_income_` | payment received | Date, Payer, Form (`1099-NEC`/`1099-K`/`none`), Amount |
| `software_expenses_` / `hardware_expenses_` | receipt | Date paid, Vendor, Amount, Service Period, Category, Business Use %, Deductible Amount, Business Purpose, Receipt File |
| `investments_` | broker | 1099-INT/DIV boxes, short/long-term proceeds, basis, wash sale, gain/loss |
| `payments_and_deductions_` | payment or deduction | Type: `student_loan_interest`, `estimated_payment`, `extension_payment`, `state_estimated_payment`, `hsa_contribution`, `ira_deduction`, `other_adjustment`, `itemized_deduction`, `other_deduction`, `other_credit`, `other_income` |

**Expense categories → Schedule C line:** Advertising & Marketing 8 · Car & Truck 9 · Contract Labor 11 · Equipment (de minimis safe harbor) 22/27a · Equipment (depreciated / Section 179) 13 · Insurance 15 · Legal & Professional / Startup-Organizational 17 · Office Expense 18 · Rent 20b · Supplies 22 · Taxes & Licenses 23 · Travel 24a · Meals (50%) 24b · Utilities / Telephone 25 · Software & Subscriptions, Cloud Infrastructure, Domains & Hosting 27a · Home Office 30.

**State tax rates** (`state_tax_rates.csv` in the project folder, kept current by the daily re-check). `check` reads it directly; `my_tax_files/state_tax_rates.csv` is optional and holds only rows you add or correct (same header). A row there replaces the project row with the same State, Tax Year, Filing Status, Item and From, so updates to the project table reach you without copying. The project table covers all 50 states and Washington, DC for tax years 2024–2027, researched on 2026-10-17 from each state's official site (about 2,150 rows). 2024 and 2025 are complete. 2026 and 2027 are partly published: what's officially set is there, rows marked `no` (estimates, drafts, withholding tables) still need checking, and anything not published yet has a `placeholder` row with its Next Check date. Rates are state-level only (local income taxes are in Notes), and US territories aren't included. One rule per row (the layout tax-modeling projects use), so deductions that are a percentage, have a floor or cap, or phase out still fit:

| Column | What goes in it |
|---|---|
| State, Tax Year | `AZ`, `2026` |
| Filing Status | `single`, `married_joint`, `married_separate`, `head_of_household`, `qualifying_surviving_spouse`, or `all` |
| Item | `bracket`, `standard_deduction`, `personal_exemption`, `dependent_exemption`, `exemption_credit` (a dollar credit, not a deduction), or `placeholder` (nothing published yet) |
| From, To | Bracket bounds in taxable income; To blank for the top bracket |
| Rate % | Bracket rate, or a percentage-of-income deduction (`2.5` means 2.5%) |
| Amount | Dollar amount of a deduction, exemption or credit; on a bracket, the fixed tax the schedule prints at its start ("$342 plus 2.75% of the excess") |
| Min, Max | Floor and cap of a percentage deduction (Maryland 2024: 15% of AGI, $1,800 to $2,700) |
| Phase-out Start, Phase-out End | Income range over which the item shrinks to zero |
| Notes, Source URL, Last Checked, Verified, Next Check | Explanation; the official page read; `YYYY-MM-DD`; `yes`/`no`; when to look again |

A flat-rate state needs one `bracket` row per filing status (or one `all` row), and a state with no income tax needs one `bracket` row at `0`. `check` validates every row for the year and reminds you when your state's Next Check date has passed. Mark `yes` only after reading the number on the state's own official site (`.gov`, or an older `.state.XX.us` address) or form; `check` enforces that. State sites are often hard for an AI to read, so you can fill this in yourself (in any spreadsheet app, saved as CSV) and drop it in the inbox, or paste the rows to your AI.

**Importing from Favabooks (Beancount).** In Fava's Query page run this (with your tax year in place of 2025), download the result as CSV and drop it in the inbox:

```
SELECT date, payee, narration, entry_meta('invoice') AS invoice, entry_meta('service_period') AS service_period, entry_meta('sales_tax') AS sales_tax, number AS amount, entry_meta('card') AS card, entry_meta('billing') AS billing, account, entry_meta('business_use') AS business_use, entry_meta('business') AS business, entry_meta('purpose') AS purpose, entry_meta('document') AS document, entry_meta('note') AS note, id FROM year = 2025 WHERE account ~ '^Expenses:' ORDER BY date
```

Then `python3 tools/taxassist.py import <file> 2025 --dry-run` to preview and the same without `--dry-run` to apply. `Expenses:Equipment` rows go to `hardware_expenses_`, every other expense to `software_expenses_`, and accounts map back to the categories above. A CSV already in the expense ledger columns works too. Duplicates are skipped, so re-importing the same or an overlapping export is safe. A row is skipped if a ledger row has the same vendor, Invoice # and amount, or the same date, vendor and amount. Matching is one for one, so two real identical charges both stay. A row with the same date and amount as another vendor's row is held as a possible duplicate (often the same charge under two names); add it by hand, or rerun with `--keep-possible`. Rows dated outside the year are skipped. The export is filed in the year folder and logged.

**Organize log columns:** Date Organized, Original Name, Detected As, Tax Year, New Location, Ledger Updated, Organized By, Notes. `taxassist.py organize` writes it for you and never overwrites.

## What to collect

| Form | From | Arrives | Folder → ledger |
|---|---|---|---|
| W-2 | each employer | Jan 31 | `income_docs/` → `w2_` |
| 1099-NEC, 1099-K | clients, payment apps | Jan 31 | `income_docs/` → `business_income_` (report all income, form or not) |
| Consolidated 1099 (INT/DIV/B) | brokers, banks | Feb 15 | `investment_services/` → `investments_` |
| 1099-R, 1099-G, SSA-1099 | retirement plan, state, SSA | Jan 31 | `income_docs/` → `other_income` row |
| 1098-E | loan servicer | Jan 31 | `loans/` → `student_loan_interest` |
| 1098, 1098-T, 5498-SA, 1095-A | lender, school, HSA, marketplace | Jan–May | `income_docs/` → matching type |
| Estimated / extension payment confirmations | irs.gov | when paid | `filed_returns/` → `estimated_payment` |
| Business receipts, formation papers, mileage, home office size | you | all year | expense folders → expense ledgers |

## Privacy

- **Git:** `.gitignore` ignores `my_tax_files/` plus any `*_TaxDocs/`, PDF, image or CSV outside `templates/`. The hook (`git config core.hooksPath .githooks`, once per clone) blocks them even with `git add -f`, and blocks SSN-shaped numbers. Check: `git ls-files my_tax_files ':!my_tax_files/README.md'` prints nothing. If something leaks, rewriting history isn't enough: treat it as exposed.
- **AI tools:** ChatGPT uploads and Projects copy files to OpenAI; local agents (Codex, Claude Code) send what they read to their provider. Share CSVs or `taxassist.py summary` output (no card numbers) instead of PDFs when you can, redact SSNs and account numbers, turn off model training in ChatGPT settings, and never share e-file or IP PINs.
- **Storage:** keep the folder on an encrypted disk with an encrypted backup.
- **Keep records** 3 years after filing (6 if income was under-reported by 25%+, 7 for bad debt or worthless securities); property and cost-basis records until 3 years after you sell; filed returns forever.
- **If it leaks:** get an IRS IP PIN (irs.gov/ippin), freeze your credit at all three bureaus, and file Form 14039 if someone files in your name.
