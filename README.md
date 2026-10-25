<p align="center"><img src="assets/logo.svg" alt="TaxAssistUS" width="420"></p>

# TaxAssistUS

**Use AI to get your United States of America (US) taxes right, and see your estimate before you pay.** For single filers, married couples, and anyone with an LLC, several LLCs, or 1099 side work.

**Tax years:** 2024, 2025 and 2026, tested on real 2024 and 2025 returns. Each year's figures live in one table, so the rest works the same any year. Upcoming: **2027** (filing by April 15, 2028, a Saturday, so the IRS will set the exact date), available May 1, 2027.

TaxAssistUS keeps your tax documents in one private folder on your computer. An AI desktop app (Claude, ChatGPT or Gemini) sorts them, and a step-by-step page shows what you'll owe or get back, federal and state, before you file.

**[→ Get started](#get-started):** [fastest, in any AI chatbot](#fastest-any-ai-chatbot-nothing-to-install) (nothing to install) · [full setup](#full-setup-a-private-folder-on-your-computer) (a private folder on your computer)

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
- Send your data anywhere on its own. There's no server and no account (unless you set up the optional [Docker server](#docker-server-shared-with-a-login)). The page makes no network calls, and "upload" means copying into your own `inbox/` folder. Data only leaves your computer if *you* give files to an online AI.
- Run in the background. The launcher opens the page and exits. The optional `serve` mode runs until you press Ctrl+C.
- Cover every situation. The estimate covers wages, investments, a Schedule C business, common deductions and credits, and Arizona or a flat state rate. It doesn't cover married filing separately, AMT, refundable credits, multi-state or part-year returns, rentals, K-1s, or other states' detailed rules ([full list](guides/2_taxes.md#the-estimate-step-4-of-taxassistushtml)).

**Tested on real 2024 and 2025 returns: federal and state estimates matched hand-built worksheets with a relative difference (Δ) under 0.01%, i.e. more than 99.99% accurate. Other testers report mostly similar results.**

## Get started

### Fastest: any AI chatbot, nothing to install

1. Open ChatGPT, Claude, Gemini or Grok, and **turn on web search**.
2. **Upload your documents** (W-2s, 1099s, 1098s, receipts). Black out Social Security numbers (keep the last 4 at most), account numbers and birth dates first, with a real Redact tool:
   - [Adobe Acrobat Pro](https://helpx.adobe.com/acrobat/desktop/protect-documents/redact-pdfs/redact.html): paid; desktop or web app
   - [Stirling-PDF](https://www.stirling.com/): free and private; runs on your own computer
   - Paper forms: cover the numbers before you scan or photograph them

   A black box or highlight drawn in an ordinary PDF viewer leaves the text underneath, so it isn't enough.
3. Copy this prompt, fill in the two blanks, and send it:

   ```text
   Help me with my US taxes. Tax year: ____   State: ____

   If you can, look at this GitHub repo and follow its AGENTS.md ("Chat-only mode"):
   https://github.com/AdrielleU/taxassistus

   Using the documents I uploaded, do what the repo's Python scripts would do, yourself:
   list and sort my documents, fill the ledgers, and check for problems. Then estimate my
   federal and state tax the way tools/tax_engine.js does, using state_tax_rates.csv for
   my state. Look up anything missing on official .gov sites and cite it. Give me one
   HTML file I can open, plus the ledgers as CSV. Ask me if anything is unclear, and tell
   me what to double-check.
   ```
4. **Open the HTML file it gives you** (download it, then double-click it). If something's wrong, just say so ("I'm married filing jointly", "box 1 is $52,300", "that receipt is personal") and ask for a new version. To check its math, open `TaxAssistUS.html` from the ZIP in your browser (no install needed) and type the same numbers into step 4.

If the chatbot can't open the link, download the ZIP from GitHub and upload `AGENTS.md`, `state_tax_rates.csv` and `tools/tax_engine.js` along with your documents. Uploading puts your documents on that company's servers. For more privacy, use the setup below, where your files stay in a folder on your computer.

### Full setup: a private folder on your computer

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
| **Docker server** (shared, with a login) | `docker compose up -d` on the server | Fill in `.env` first ([below](#docker-server-shared-with-a-login)) |

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

### Docker server (shared, with a login)

`docker-compose.yml` runs the same `serve` mode behind [Caddy](https://caddyserver.com), which asks for a **username and password** (the browser's login popup), so people on your network can open it from their own browsers without SSH. It works with Podman (`podman-compose`) or Docker. Both come from one ready-made image, `ghcr.io/adrielleu/taxassistus` (built from `Dockerfile` for each release), so the server needs only `docker-compose.yml`, `.env` and your `my_tax_files/`.

**Everyone who logs in sees and edits the same `my_tax_files/`**: full documents, SSNs included. Use it for one household or one person's own devices, not for unrelated people. Give each household its own copy of the project and its own port.

1. `cp .env.example .env`, then set `TAXASSIST_HOSTS` to every name or IP people will type (the server's LAN IP, its host name), comma-separated, without the port. Rootless Podman: also set `TAXASSIST_UID=0` and `TAXASSIST_GID=0` (container root is your own user there, so files stay yours).
2. Once per host, create the shared network: `podman network create network_container` (Docker: `docker network create network_container`).
3. Set the login in `.env`: `TAXASSIST_LOGIN_USER` and `TAXASSIST_LOGIN_HASH`, a bcrypt hash of your password (the password itself is never stored). `.env.example` has the one command that makes it: paste it as is, type the password at the prompts, and copy the `TAXASSIST_LOGIN_HASH='$2a$14$...'` line it prints into `.env`, single quotes included. Without the login, compose refuses to start.
4. Start it with `podman-compose up -d` (or `docker compose up -d`). To change the password later, make a new hash the same way and run `podman-compose up -d` again. To update, set `TAXASSIST_TAG` in `.env` to a [release](https://github.com/AdrielleU/taxassistus/releases), then `podman-compose pull && podman-compose up -d`.
5. Open `http://<server IP>:17202/` and log in. To use another port, change the first number of `"17202:8080"` under `ports:` in `docker-compose.yml`. `"127.0.0.1:17202:8080"` limits it to the server itself.

It runs two containers, `taxassist` and `taxassist-caddy`. Both join the shared `network_container` used by the other stacks on the host. How it's locked down: both run as a plain user, read-only, with every Linux capability dropped. `taxassist` has no published port, so people reach it only through Caddy's login. Caddy never gets `my_tax_files/`. Other containers on `network_container` can reach `taxassist` directly, so keep only trusted stacks on that network. The code is inside the image, `my_tax_files/` is the only writable folder, and it refuses host names not in `TAXASSIST_HOSTS`. Add documents with `scp` into `my_tax_files/inbox/`. Your AI can run the tools inside the container: `podman exec taxassist python3 tools/taxassist.py status`. Stop it with `podman-compose down` (or `docker compose down`).

It's plain HTTP, so the password crosses your network unencrypted: fine on a home network you trust. From outside, use a VPN (WireGuard, Tailscale, NetBird) rather than opening the port to the internet. A password is only one lock, and Caddy doesn't rate-limit login attempts.

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

## Keeping the state table current (GitHub Actions)

`.github/workflows/state-rates-check.yml` runs every day on GitHub. It validates `state_tax_rates.csv` and finds every row whose **Next Check** date is today or past due. Then:

- **With an `ANTHROPIC_API_KEY` secret**, Claude researches those states on their official sites (up to 8 states a run) and opens a **pull request** with the updated rows and a summary. It never pushes to `main`. The research step can't run commands or write to the repo, and the pull request is only opened if the CSV is the sole change and it passes validation. **Review each changed row against its Source URL before merging.**
- **Without the key**, it keeps one issue, "State tax rates due for re-check", listing what's due, so a person (or your own AI) can do it.
- When nothing is due, it closes that issue.

**People approve every change.** The workflow only opens pull requests; it never approves or merges. You're notified of each new one, and `.github/CODEOWNERS` requests a review from the maintainer.

One-time setup on GitHub:
1. **Settings → Actions → General → Workflow permissions:** tick **Allow GitHub Actions to create and approve pull requests** (GitHub's single setting for letting the workflow open a PR).
2. **Settings → Rules → Rulesets → New branch ruleset** for `main`: require a pull request with 1 approval and **review from Code Owners**. A bot isn't a code owner, so only a person can approve. Add yourself as a bypass actor if you still push to `main` directly.
3. Optional: **Settings → Secrets and variables → Actions → New repository secret**, `ANTHROPIC_API_KEY` (from console.anthropic.com; usage is billed to that key).
4. Optional variables on the same page: `RATES_STATES_PER_RUN` (default `8`) and `CLAUDE_MODEL` (default: the action's model).

Run it by hand from **Actions → State tax rates re-check → Run workflow**, optionally "as of" a future date to preview. GitHub pauses scheduled workflows in public repos after 60 days without activity; re-enable it on the same page. Locally, `python3 tools/taxassist.py rates` runs the same check (`--as-of 2027-01-15` to preview).

## What's in the folder

| Path | What it is | In git |
|---|---|---|
| `Start-TaxAssistUS_Windows.bat` / `_Mac.command` / `_Linux.sh` / `_LinuxServer.sh` | Launchers (desktop ones take `serve`) | yes |
| `Dockerfile`, `docker-compose.yml`, `docker/Caddyfile`, `.env.example` | Optional shared server: a login in front of `serve` | yes (your `.env` never) |
| `TaxAssistUS.html` | The app (the five steps) | yes |
| `AGENTS.md` + `CLAUDE.md`, `GEMINI.md`, `GROK.md` | Rules for AI assistants, and pointers to them | yes |
| `guides/1_files.md` | Folder layout, file names, ledger columns, forms to collect, privacy | yes |
| `guides/2_taxes.md` | Expense rules, the estimate, filing, year-round planning | yes |
| `guides/3_ai.md` | AI setups, prompts, how to check its work | yes |
| `state_tax_rates.csv` | State income tax rules for all 50 states + DC, 2024–2027: brackets, deductions, exemptions, each with source, date checked, verified, next check ([columns](guides/1_files.md#ledgers-csv)) | yes |
| `templates/` | Blank `profile.yml` and year ledgers | yes |
| `.github/workflows/state-rates-check.yml` | Daily re-check of `state_tax_rates.csv` ([above](#keeping-the-state-table-current-github-actions)) | yes |
| `tools/tax_engine.js` | Tax math and the 2024, 2025 and 2026 federal tables | yes |
| `tools/taxassist.py` | Helper: `start`, `serve`, `init`, `inbox`, `organize`, `import`, `check`, `summary`, `status`, `rates` | yes |
| `my_tax_files/` | Your profile, state rates, inbox, organized years, and `status.js` (the page's snapshot) | **never** |
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
| Docker: connection refused, or 403 | Use the port from `ports:` in `docker-compose.yml` (default 17202), and a name or IP listed in `TAXASSIST_HOSTS` in `.env`; others are refused |
| The estimate differs from your tax software | Find out why before filing: compare line by line (step 4, **Copy as text**), and ask your AI to review the differences |

## Contributing

Issues and pull requests are welcome. **Never post real tax documents, screenshots of returns, SSNs, account numbers or dollar amounts from your own taxes** in an issue or pull request. Describe the problem with made-up numbers instead. If you change tax figures in `tools/tax_engine.js`, cite the official IRS or state source.

## License

[MIT](LICENSE) © 2026 AdrielleU. Free to use, change and share; keep the copyright notice. Provided as is, with no warranty. It's a planning tool, not tax advice.
