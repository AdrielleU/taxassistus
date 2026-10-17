# TaxAssistUS

**Use AI to get your US taxes right, and see your estimate before you pay.** For single filers, married couples, and anyone with an LLC, several LLCs, or 1099 side work.

TaxAssistUS keeps your tax documents in one private folder on your computer. An AI desktop app (Claude, ChatGPT or Gemini) sorts them, and a step-by-step page shows what you'll owe or get back, federal and state, before you file.

> **Planning tool, not tax advice.** It doesn't file anything or talk to the IRS. Your tax software (or your CPA) has the final word. For anything complicated, or with a lot at stake, see a CPA or enrolled agent.

## What to expect

**It does:**
- Keep every W-2, 1099, 1098 and receipt in one standard folder layout, year by year
- Estimate federal + state tax with charts: where every dollar goes, your tax brackets, and what saving more pre-tax would save you
- Give you setup steps and copy-paste prompts for ChatGPT, Claude, Gemini, Grok or Gemma
- Check that every expense has a receipt and the ledgers add up
- Give you a filing checklist, key dates, and ways to pay less next year. Recommended filing software: **FreeTaxUSA** (federal $0, state $15.99)

**It doesn't:**
- File returns, make payments, or log into any account
- Send your data anywhere on its own. There's no server and no account. The page makes no network calls, and "upload" means copying into your own `inbox/` folder. Data only leaves your computer if *you* give files to an online AI.
- Run in the background. The launcher opens the page and exits. The optional `serve` mode runs until you press Ctrl+C.
- Cover every situation. The estimate covers wages, investments, a Schedule C business, common deductions and credits, and Arizona or a flat state rate. It doesn't cover married filing separately, AMT, refundable credits, multi-state or part-year returns, rentals, K-1s, or other states' detailed rules ([full list](guides/2_taxes.md#the-estimate-step-4-of-taxassistushtml)).

**On the 2025 test year, the estimate matched a hand-built worksheet within $0.07.**

## Get started

1. **Get the code** and put it somewhere in your home folder: on GitHub, click **Code → Download ZIP** and unzip it, or
   ```bash
   git clone https://github.com/AdrielleU/taxassistus.git TaxAssistUS
   ```
2. **Double-click the launcher** for your computer:

   | | Launcher | The first time |
   |---|---|---|
   | **Windows** | `Start-TaxAssistUS_Windows.bat` | "Windows protected your PC": **More info** → **Run anyway** |
   | **Mac** | `Start-TaxAssistUS_Mac.command` | "Unidentified developer": right-click → **Open** → **Open**. It runs the `_Linux.sh` file, so keep both. |
   | **Linux desktop** | `./Start-TaxAssistUS_Linux.sh` in a terminal | Or right-click it in your file manager → **Run as a Program** |
   | **Linux server** (headless, over SSH) | `./Start-TaxAssistUS_LinuxServer.sh` on the server | Prints the SSH tunnel command to run on your own computer ([below](#on-a-linux-server)) |

3. **Your browser opens Tax Assist US.** Follow the five steps:

   | Step | You do | Takes | Saved in |
   |---|---|---|---|
   | 1 Profile | Filing status, state, household, jobs, business type (e.g. single-member LLC) | 2 min | `my_tax_files/profile.yml` |
   | 2 Upload | Drop in documents, or copy them into the inbox folder | as you get them | `my_tax_files/inbox/` |
   | 3 AI Organize | Pick your AI, run it in this project's folder, paste the numbered prompts | 5 min once | `my_tax_files/organized/<YEAR>_TaxDocs/` |
   | 4 Estimate | Click **Load my <YEAR> files** | instant | your browser |
   | 5 File & plan | Tick off the checklist; see dates and savings ideas | | your browser |

**On the first run** the launcher creates `my_tax_files/` with an inbox, a folder for the current year, and a blank profile. **Each later run** refreshes the page's snapshot of your folders. The page doesn't update by itself after your AI organizes files: run the launcher again (or reload the page, if the AI ran `taxassist.py status`).

### Prefer a web address? (`serve`)

By default the page opens straight from disk (`file://…/TaxAssistUS.html`), so there's no port. To get one instead, add `serve`:

```bash
./Start-TaxAssistUS_Linux.sh serve          # Mac: same command; Windows: Start-TaxAssistUS_Windows.bat serve
```

It serves at **http://127.0.0.1:8765** (the next free port if that's taken; `--port 9000` to choose), opens your browser, and keeps the snapshot fresh: just reload the page. Step 5's **Records check** also runs live: automatically when you open the step, or with **Run check**. Press **Ctrl+C** to stop.

It's **this computer only**. It listens on 127.0.0.1, never your network address, so phones and other computers can't reach it. It also refuses requests from other websites open in your browser, and never serves hidden files like `.git`.

### On a Linux server

On a headless server, run `./Start-TaxAssistUS_LinuxServer.sh`. It serves on the **server's** 127.0.0.1 (still not on the network) and prints the two lines you need on your own computer:

```bash
ssh -N -L 8765:127.0.0.1:8765 you@your-server       # 1. tunnel (leave it running)
# 2. open http://127.0.0.1:8765/TaxAssistUS.html in your browser
```

Add documents by copying them to the server's inbox: `scp *.pdf you@your-server:~/TaxAssistUS/my_tax_files/inbox/` (the exact path is printed). Don't use the page's **Connect folder** in this mode: it would pick a folder on *your* computer, not the server. Press **Ctrl+C** on the server to stop it, and close the `ssh` command to disconnect.

### What you need

- **A browser.** Chrome, Edge or Chromium can also save uploads and your profile straight into the folder (click **Connect folder** once). In Safari or Firefox you copy files into `my_tax_files/inbox/` yourself.
- **Python 3.8 or newer** (recommended, free). It powers the folder and inbox views and the helper commands. Nothing to `pip install`. Tested on 3.8, 3.10 and 3.12. Without it, open `TaxAssistUS.html` directly: profile, estimate and CSV loading still work.

  | | Have it already? | Get it |
  |---|---|---|
  | **Windows** | No (typing `python` only opens the Microsoft Store) | [python.org/downloads](https://www.python.org/downloads/), tick **"Add python.exe to PATH"**, or `winget install Python.Python.3.13` |
  | **Mac** | Not on a new Mac | The first launch offers Apple's developer tools (includes Python): click **Install**. Or [python.org/downloads](https://www.python.org/downloads/) |
  | **Linux** | Almost always | `sudo apt install python3` · `sudo dnf install python3` · `sudo pacman -S python` |

  Check with `python3 --version` (Windows: `py --version`).
- **An AI assistant** (optional): ChatGPT, Claude, Gemini, Grok, or Gemma running offline. Turn on web search where it exists, so it can check each year's figures on irs.gov and your state's site.

## Using an AI assistant

Step 3 shows setup and prompts for the assistant you pick. Every assistant follows the same rules in **`AGENTS.md`** (`CLAUDE.md`, `GEMINI.md` and `GROK.md` just point to it):

- It reads your profile first, opens each document instead of trusting its name, and files it with a standard name, adding the matching ledger rows.
- It **never deletes** your documents and logs every move in `organized/organize_log.csv`. Anything it's unsure about stays in the inbox with a question for you.
- It looks up each year's figures on official sites (irs.gov, your state's `.gov`), not calculator sites, and cites and logs them.

| Your assistant | How it touches your files |
|---|---|
| **Desktop apps (recommended):** Claude Desktop (Cowork), ChatGPT desktop, Gemini app. Mac and Windows | Works directly in **this project's folder** once you grant it (grant only this folder) |
| Websites, **only if you can't install apps** (e.g. a work computer): claude.ai, chatgpt.com, gemini.google.com, grok.com | Only files you upload. It gives you the names, rows and commands to apply. |
| Terminal tools for Linux: Claude Code, Codex CLI, Gemini CLI | Works in the folder after you `cd` into it |
| Gemma (Ollama / LM Studio) | Offline. Only text you paste. **Nothing leaves your computer.** |

Before uploading anything to an online AI, black out SSNs and account numbers ([privacy guide](guides/1_files.md#privacy)).

## How to stop or undo things

| You want to | Do this |
|---|---|
| **Stop Tax Assist US** | Close the browser tab. Nothing else is running: the launcher exits after opening the page. |
| **Stop `serve` mode** | Press **Ctrl+C** in its window (or close the window). On a Linux server: Ctrl+C on the server, then close the `ssh -L` command on your computer. Lost the window? `pkill -f "taxassist.py serve"` (Windows: end the `python` task in Task Manager). |
| **Stop an AI mid-task** | CLI agents (Codex, Claude Code, Gemini CLI): press **Ctrl+C**, or close the terminal. Web assistants: press stop in the chat. Gemma: quit Ollama or LM Studio. |
| **Undo what the AI filed** | Open `my_tax_files/organized/organize_log.csv`: each row shows the original name and where the file went. Move it back to `inbox/`, and delete the ledger row it added. |
| **Remove a web AI's copy of your files** | Delete the Project / Gem and its uploaded files in ChatGPT, Claude, Gemini or Grok. Also check their data-training settings (step 3 says where). |
| **Revoke the page's folder access** (Chrome/Edge) | Click the icon left of the address bar → reset permissions, or clear site data for the page. The next upload will ask again. |
| **Clear what the page remembers** | The page keeps your estimate inputs, checklist ticks and unsaved profile edits in this browser only. **Clear all** in step 4 resets the estimate; clearing the browser's site data removes the rest. Your files aren't affected. |
| **Start a year over** | Delete `my_tax_files/organized/<YEAR>_TaxDocs/`, then run the launcher (or `python3 tools/taxassist.py init <YEAR>`) |
| **Uninstall** | **Back up `my_tax_files/` first.** It holds your tax records; keep them at least 3 years. Then delete the `TaxAssistUS` folder. Python, Ollama and the like uninstall separately. |
| **Stop the git safety hook** | `git config --unset core.hooksPath` (not recommended) |

## Privacy and git

Everything personal lives in **`my_tax_files/`**, which git ignores. If you use git, run `git config core.hooksPath .githooks` once per clone: it blocks private files and SSN-shaped numbers from ever being committed, even with `git add -f`. Keep the folder on an encrypted disk with an encrypted backup. More in [guides/1_files.md](guides/1_files.md#privacy).

## What's in the folder

| Path | What it is | In git |
|---|---|---|
| `Start-TaxAssistUS_Windows.bat` / `_Mac.command` / `_Linux.sh` / `_LinuxServer.sh` | Launchers (desktop ones take `serve`) | yes |
| `TaxAssistUS.html` | The app (the five steps) | yes |
| `AGENTS.md` + `CLAUDE.md`, `GEMINI.md`, `GROK.md` | Rules for AI assistants, and pointers to them | yes |
| `guides/1_files.md` | Folder layout, file names, ledger columns, forms to collect, privacy | yes |
| `guides/2_taxes.md` | Expense rules, the estimate, filing, year-round planning | yes |
| `guides/3_ai.md` | AI setups, prompts, how to check its work | yes |
| `templates/` | Blank `profile.yml` and year ledgers | yes |
| `tools/tax_engine.js` | Tax math and the 2025/2026 federal tables | yes |
| `tools/taxassist.py` | Helper: `start`, `serve`, `init`, `inbox`, `organize`, `check`, `summary`, `status` | yes |
| `my_tax_files/` | Your profile, inbox, organized years, and `status.js` (the page's snapshot) | **never** |
| `LICENSE` | MIT License | yes |

## Troubleshooting

| Problem | Fix |
|---|---|
| The page shows "No folder snapshot" | Run the launcher (needs Python), or `python3 tools/taxassist.py start` |
| Organized files don't show up | Run the launcher again, then reload the page |
| Windows: the launcher window flashes and closes | Install Python with **"Add python.exe to PATH"** ticked, then try again |
| Mac: "cannot be opened" | Right-click → **Open**. If it says it isn't executable: `chmod +x Start-TaxAssistUS_*.sh Start-TaxAssistUS_*.command` |
| Uploads don't save into the folder | That needs Chrome or Edge (**Connect folder**). In other browsers, copy files into `my_tax_files/inbox/` |
| `serve`: "Ports … are busy" | Another program is using them: `serve --port 9000` |
| Linux server: the page won't load on your computer | Keep the `ssh -N -L …` command running, and use the same port it prints |
| The estimate differs from your tax software | Find out why before filing: compare line by line (step 4, **Copy as text**), and ask your AI to review the differences |

## Contributing

Issues and pull requests are welcome. **Never post real tax documents, screenshots of returns, SSNs, account numbers or dollar amounts from your own taxes** in an issue or pull request. Describe the problem with made-up numbers instead. If you change tax figures in `tools/tax_engine.js`, cite the official IRS or state source.

## License

[MIT](LICENSE) © 2026 AdrielleU. Free to use, change and share; keep the copyright notice. Provided as is, with no warranty. It's a planning tool, not tax advice.
