# 1 · Files, folders and privacy

## Layout

```
my_tax_files/                      ← private: ignored by git + blocked by the pre-commit hook
├── profile.yml                    ← who you are, tax-wise (step 1 of TaxAssistUS.html)
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
