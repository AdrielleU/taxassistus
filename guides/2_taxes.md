# 2 · Doing the taxes: expenses, estimate, filing, planning

## Business expenses (Schedule C)

Deductible if **ordinary and necessary** for the business, with proof of amount, date and vendor (the receipt) and of **business purpose** (write it when you pay).

| Situation | Rule |
|---|---|
| Mixed personal/business use | Deduct the business share only (Business Use %, reason in Notes) |
| Equipment ≤ $2,500 per item/invoice | De minimis safe harbor: expense it in full. Elect it every year (software checkbox or attached statement) |
| Equipment > $2,500 | Depreciate, or Section 179 / bonus depreciation |
| Prepaying more than 12 months | 12-month rule: deduct only this year's share when the benefit runs past the end of next year (conservative) |
| Startup / formation costs | Up to $5,000 each of startup and organizational costs in year one (reduced above $50,000); the rest over 180 months |
| Meals with clients | 50%; entertainment 0% |
| Card rewards at checkout | Reduce the cost; gift cards count as payment |
| Prepaid balances (API, ad credits) | Deduct usage, not deposits |
| Home office | Exclusive, regular business use; simplified $5/sq ft up to 300 sq ft; can't create a loss |
| $0 statements | Cash method: deduct when actually paid |

**A loss** offsets wages only if the business is really trying to profit. Keep a plan, outreach records, a separate account, and time records (profit in 3 of 5 years creates a presumption). **A profit** owes 15.3% self-employment tax on 92.35% of it, with nothing withheld: make quarterly estimates or raise W-4 withholding.

## The estimate (step 4 of TaxAssistUS.html)

**Load my <YEAR> files** reads the organized ledgers; basics come from `profile.yml`. For the current year, project W-2s to a full year (`year-to-date ÷ paychecks so far × paychecks per year`).

**Covers:** wages, interest, dividends (0/15/20%), capital gains and the $3,000 loss limit, Schedule C, SE tax, QBI (below the threshold), student loan phase-out, standard vs itemized, 65+ additions and the 2025–2028 senior deduction, child tax credit (non-refundable part), foreign tax credit, Additional Medicare, NIIT, withholding and estimates. State: none, Arizona (2.5% with the 25% long-term gain subtraction), or a flat/effective rate.

**Doesn't cover:** married filing separately, AMT, refundable credits (EITC, ACTC, premium tax credit), education credit math, depreciation, multi-state or part-year returns, progressive state brackets, Social Security taxation, K-1 detail. Use tax software or a pro for these. On the 2025 sample year it matched the hand-built worksheet within $0.07.

**Estimate report** (`<YEAR>_tax_estimate_report.html`), for before filing:
1. W-2 wages
2. Investment income
3. Schedule C
4. Federal in three columns: *before expenses*, *with all expenses*, *conservative* (judgment calls taken the safe way)
5. State
6. Bottom line, and which scenario you'll file
7. Payment plan: interest at the IRS quarterly rate compounded daily, the penalty safe harbors, Direct Pay
8. How to file
9. Assumptions and open items

**New tax year in the engine:** copy the latest `TAX_YEARS` entry in `tools/tax_engine.js` and replace every value from the IRS inflation revenue procedure (published Oct/Nov), the SSA wage base, and the 401(k)/HSA limits. Cite them in `source`, then test against an IRS example or tax software.

## Filing (step 5 checklist)

- **Software: FreeTaxUSA is recommended.** Federal is **$0** (including W-2s, 1099s, a Schedule C business and investments), each state return is **$15.99**, and there's no income limit. Check freetaxusa.com for current prices; add-ons cost extra. Alternatives: IRS Free File for W-2-only returns under its AGI limit (about $84–89k); TurboTax or H&R Block for more hand-holding (they cost more); a CPA or enrolled agent for K-1s, rentals, multi-state, equity comp or IRS notices.
- **Enter in order:** personal info (last year's AGI, IP PIN) → W-2s (all boxes) → investments (per-broker summary; wash sales may need the PDF attached or mailed with Form 8453) → business (category totals, de minimis election) → adjustments → deductions → credits → payments. **Stop if the federal total differs from the estimate by more than a few dollars.**
- **Pay** at irs.gov/directpay ("Balance Due", 1040, the year). Late or on extension: interest runs from April 15. Can't pay? File anyway and set up a plan: the failure-to-file penalty is 10× the failure-to-pay one.
- **Extension** (Form 4868) extends the time to *file* to Oct 15, **not the time to pay**. Many states accept it automatically.
- **After:** save PDFs and confirmations in `filed_returns/`, confirm payments and refunds posted, and add a `history` line to `profile.yml`.

## Planning

**Calendar:** Jan 15 Q4 estimate · Jan 31 W-2s/1099s · Feb 15 broker 1099s · Apr 15 file/extend/pay, Q1 estimate, last day for prior-year IRA/HSA · Jun 15 Q2 · Sep 15 Q3 · Oct 15 extended deadline · Nov–Dec open enrollment, 401(k) top-up, loss harvesting.

**Withholding:** two jobs (or a working spouse) means each employer under-withholds. Use irs.gov/w4app, check Step 2(c) at both jobs, or add the per-paycheck amount from the estimate to Step 4(c).

**No underpayment penalty if** you owe under $1,000, or you paid 90% of this year's tax, or 100% of last year's (110% if AGI was over $150k). Easiest route: last year's total tax − this year's withholding, paid in 4 parts.

**Pay less:** pre-tax 401(k) (the what-if chart shows the savings) · HSA with a high-deductible plan (through payroll it also skips FICA) · deductible IRA · tax-loss harvesting (30-day wash-sale rule) · business expenses with receipts · bunching itemized deductions. A lower AGI also unlocks phased-out benefits (student loan interest, IDR payments, credits).

**Mid-year (Jun–Aug):** update `w2_<YEAR>.csv` year-to-date, run the estimate, and fix the W-4 if you'll owe more than about $500.
