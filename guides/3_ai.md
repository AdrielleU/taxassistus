# 3 · Working with an AI assistant

## Setups

Step 3 of `TaxAssistUS.html` has the setup steps and copy-paste prompts for each assistant; this is the summary.

| Assistant | Use this: desktop app with folder access | Website: only if you can't install apps | Linux / terminal |
|---|---|---|---|
| Claude | **Claude Desktop** (claude.ai/download) → Cowork → grant this folder | claude.ai Project: instructions + knowledge | Claude Code (`CLAUDE.md` → `AGENTS.md`) |
| ChatGPT | **ChatGPT desktop** (chatgpt.com/download, includes Codex) → open this folder | chatgpt.com Project: instructions + files | Codex CLI (`AGENTS.md`) |
| Gemini | **Gemini app** (Mac: gemini.google/mac; Windows) → grant this folder | gemini.google.com Gem: instructions + knowledge | Gemini CLI (`GEMINI.md` → `AGENTS.md`) |
| Grok | No official desktop app that opens folders yet; skip unofficial downloads | grok.com Project: instructions + sources | `GROK.md` → `AGENTS.md` for any future agent |
| Gemma | Runs **offline** in Ollama or LM Studio. Paste `AGENTS.md` as the system prompt; raise the context (`num_ctx` 32768+) | | |

With a desktop app, grant **only this project's folder**, then paste prompt 1 ("Read AGENTS.md first…"). The desktop apps run on Mac and Windows; on Linux, use the terminal tools. App features change often (checked October 2026); step 3 of `TaxAssistUS.html` has the current steps.

Chat apps and Gemma can't move files on your computer. They give you the new names, ledger rows and `taxassist.py organize` commands to run. Gemma is the most private option (nothing leaves your machine), but smaller models slip on arithmetic: let step 4 do the math and have Gemma explain, sort and draft.

**Turn on web search** where it exists. Tax figures change every year, and `AGENTS.md` (**Look it up**) has the assistant check them on official sites and log them in `<YEAR>_research_notes.md`. Without search, it tells you what to verify.

Read the privacy part of guide 1 first.

## Prompts

**Start:** Read AGENTS.md, then my_tax_files/profile.yml, then list my_tax_files/inbox and my_tax_files/organized. Tell me in five bullets what you see, what's missing, and what you'd do next. Don't change files yet.

**Organize the inbox** (also on the AI Organize step of TaxAssistUS.html): Read AGENTS.md and do the "Organize the inbox" task for every file in my_tax_files/inbox/. Leave anything you're unsure about there and ask me. Finish with `taxassist.py check <YEAR>` and `taxassist.py status`.

**What will I owe?** Using the <YEAR> ledgers, profile.yml and tools/tax_engine.js, estimate federal and state. Look up anything the engine doesn't cover (my state's rules especially) on official sources and cite them. Show the math in a table, name the three biggest drivers, and say what would change the answer most.

**Mid-year:** My pay stubs show [YTD wages, federal withheld, state withheld] after [N] of [M] paychecks. Project the full year and tell me exactly what to put in W-4 Step 4(c) to owe about $0.

**Is this deductible?** [item, amount, how I use it]: yes/no/partly, the rule, the Schedule C line, the Business Use %, the record I need. If yes, add the ledger row.

**Reports:** Build `<YEAR>_tax_estimate_report.html` (guide 2, sections 1–9, three scenarios) / `<YEAR>_business_expense_report.html` (by category, by vendor, purpose by vendor, equipment, items to explain, full ledger) / `<YEAR>_<software>_walkthrough.html` (exact screens and values, in guide 2 filing order). Match last year's style; every number cites its file.

**Check my state:** Look up <STATE> <YEAR> individual income tax rules on the state revenue site (AGENTS.md, Look it up): rate, standard deduction, exemptions, credits, differences from federal, estimate and extension rules, deadlines. Save them to <YEAR>_research_notes.md and tell me what the estimator misses for me.

**Next year:** From the <YEAR> result and profile.yml, write `organized/<YEAR+1>_TaxDocs/README.md` as a checklist: wrap-up items, changes to make now, the monthly routine, estimate dates, documents to collect.

**Review:** Compare my software's summary [numbers] with the estimate report. List every difference over $5, the likely cause, and which side is right.

## Check its work

- Ask "which file and row?" for any surprising number.
- Year-specific figures must come from `TAX_YEARS` or a cited IRS page; AI tools mix up years.
- Load the same files in the Estimate step; results should match within a few dollars.
- Your tax software is the final word; reconcile before filing.
- When it says "may" or "it depends", ask for the conservative answer.
- **Stop and get a human** if it suggests deducting personal costs, moving dates between years, or skipping income without a form; if you get an IRS notice other than a simple balance due; or if you have income in more than one state.
