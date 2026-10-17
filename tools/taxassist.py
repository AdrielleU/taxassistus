#!/usr/bin/env python3
"""Tax Assist US helper. Standard library only; reads and writes local files only.

Usage (from the project root):
  python3 tools/taxassist.py start          # set up on first run, refresh the snapshot, open TaxAssistUS.html
  python3 tools/taxassist.py serve          # same, but served at http://127.0.0.1:8765 (this computer only); Ctrl+C stops
  python3 tools/taxassist.py serve --headless   # on a Linux server: no browser, prints the SSH tunnel command
  python3 tools/taxassist.py init 2026       # create my_tax_files/organized/2026_TaxDocs from templates
  python3 tools/taxassist.py inbox           # list files waiting in my_tax_files/inbox with a best guess for each
  python3 tools/taxassist.py organize FILE YEAR SUBFOLDER [--name NEW] [--as WHAT] [--ledger CSV] [--notes TEXT]
                                             # move one inbox file into a year folder and log it
  python3 tools/taxassist.py check 2025      # validate ledgers against receipts
  python3 tools/taxassist.py summary 2025    # print totals as Markdown (safe to share: no card numbers)
  python3 tools/taxassist.py status          # refresh my_tax_files/status.js for TaxAssistUS.html (includes profile.yml)
"""
import argparse
import csv
import json
import re
import shutil
import sys
import urllib.parse
import webbrowser
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "YEAR_TaxDocs"
PRIVATE = ROOT / "my_tax_files"
INBOX = PRIVATE / "inbox"
ORGANIZED = PRIVATE / "organized"
LOG = ORGANIZED / "organize_log.csv"
STATUS = PRIVATE / "status.js"
PROFILE = PRIVATE / "profile.yml"
FILING_STATUSES = {"single", "married_joint", "married_separate", "head_of_household", "qualifying_surviving_spouse"}
LOG_HEAD = ["Date Organized", "Original Name", "Detected As", "Tax Year", "New Location", "Ledger Updated", "Organized By", "Notes"]
EXPENSE_LEDGERS = {"software_expenses": "software_expenses", "hardware_expenses": "hardware_expenses"}
SUBFOLDERS = ["income_docs", "investment_services", "loans", "software_expenses", "hardware_expenses", "filed_returns"]

# Best-guess rules for inbox files, checked in order against the lowercased file name.
# Keep in sync with RULES in TaxAssistUS.html. A guess is a starting point; the
# assistant opens the file to confirm before organizing it.
GUESS_RULES = [
    (r"w-?2", "W-2 (wages)", "income_docs", "w2"),
    (r"1099-?nec|1099-?k|1099-?misc", "1099 for business income", "income_docs", "business_income"),
    (r"1099-?r|1099-?g|ssa-?1099", "1099 (retirement / government)", "income_docs", "payments_and_deductions"),
    (r"1099|consolidated|brokerage|invest|acorns|stash|wealthfront|robinhood|fidelity|schwab|vanguard|etrade|coinbase", "Investment 1099", "investment_services", "investments"),
    (r"1098-?e|student.?loan|aidvantage|nelnet|mohela|navient", "1098-E (student loan interest)", "loans", "payments_and_deductions"),
    (r"1098-?t|tuition", "1098-T (tuition)", "income_docs", "payments_and_deductions"),
    (r"1098|mortgage|property.?tax", "Mortgage / property tax", "income_docs", "payments_and_deductions"),
    (r"5498|hsa|1095", "HSA / health coverage form", "income_docs", "payments_and_deductions"),
    (r"1040|return|directpay|confirmation|e-?file|4868|extension", "Filed return or confirmation", "filed_returns", None),
    (r"amazon|best.?buy|newegg|laptop|monitor|keyboard|mouse|hardware|computer|printer|desk|chair", "Equipment receipt", "hardware_expenses", "hardware_expenses"),
    (r"invoice|receipt|order|subscription|billing|statement", "Expense receipt", "software_expenses", "software_expenses"),
]


def parse_yaml(text):
    """Read the simple YAML used by profile.yml: nested maps (2-space indent), `- item` lists,
    lists of maps (`- name: x` then indented keys), inline [a, b] lists, and plain scalars.
    Standard library only, so no PyYAML needed."""
    def scalar(v):
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
            return v[1:-1]
        if v.startswith("[") and v.endswith("]"):
            return [scalar(x) for x in v[1:-1].split(",") if x.strip()]
        low = v.lower()
        if low in ("yes", "true", "on"):
            return True
        if low in ("no", "false", "off"):
            return False
        if low in ("", "null", "~"):
            return None
        if re.fullmatch(r"-?\d+", v):
            return int(v)
        if re.fullmatch(r"-?\d*\.\d+", v):
            return float(v)
        return v

    lines = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        line, quote = "", None
        for i, ch in enumerate(raw):  # strip trailing comments outside quotes
            if ch in "'\"" and quote in (None, ch):
                quote = None if quote else ch
            if ch == "#" and quote is None and (i == 0 or raw[i - 1] == " "):
                break
            line += ch
        if line.strip():
            lines.append((len(line) - len(line.lstrip(" ")), line.strip()))

    root = {}
    stack = [(-1, root)]
    for n, (indent, content) in enumerate(lines):
        is_item = content == "-" or content.startswith("- ")
        while indent < stack[-1][0] or (indent == stack[-1][0] and not (is_item and isinstance(stack[-1][1], list))):
            stack.pop()
        parent = stack[-1][1]
        if is_item:
            if not isinstance(parent, list):
                continue
            item = content[1:].strip()
            if re.match(r"^[A-Za-z_][\w-]*:(\s|$)", item):  # "- key: value" starts a map
                entry = {}
                parent.append(entry)
                stack.append((indent, entry))
                key, _, val = item.partition(":")
                entry[key.strip()] = scalar(val) if val.strip() else None
            else:
                parent.append(scalar(item))
            continue
        key, _, val = content.partition(":")
        if not isinstance(parent, dict):
            continue
        if val.strip():
            parent[key.strip()] = scalar(val)
        else:
            nxt = lines[n + 1] if n + 1 < len(lines) else None
            if nxt and (nxt[1] == "-" or nxt[1].startswith("- ")) and nxt[0] >= indent:
                child = []
            elif nxt and nxt[0] > indent:
                child = {}
            else:
                parent[key.strip()] = None
                continue
            parent[key.strip()] = child
            stack.append((indent, child))
    return root


def load_profile():
    if not PROFILE.exists():
        return None, []
    profile = parse_yaml(PROFILE.read_text(encoding="utf-8"))
    old = profile.get("business")
    if "businesses" not in profile and isinstance(old, dict):  # profiles from before multi-business support
        has = old.get("entity") not in (None, "none")
        profile["businesses"] = [{"name": old.get("name"), "type": old.get("entity"), "started": old.get("started"),
                                  "home_office": bool(old.get("home_office"))}] if has else []
    profile.pop("business", None)
    issues = []
    if profile.get("filing_status") not in FILING_STATUSES:
        issues.append(f"filing_status should be one of: {', '.join(sorted(FILING_STATUSES))}")
    if not re.fullmatch(r"[A-Z]{2}", str(profile.get("state") or "")):
        issues.append("state should be a two-letter code, e.g. AZ")
    return profile, issues


def year_dir(year):
    return ORGANIZED / f"{year}_TaxDocs"


def rel(path):
    return str(Path(path).relative_to(ROOT))


def num(value):
    s = (value or "").replace("$", "").replace(",", "").strip()
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    try:
        return float(s)
    except ValueError:
        return 0.0


def money(n):
    return f"-${abs(n):,.2f}" if n < 0 else f"${n:,.2f}"


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader if (list(r.values()) or [""])[0].strip().upper() != "TOTAL"]
        total = None
        f.seek(0)
        for r in csv.reader(f):
            if r and r[0].strip().lstrip("﻿").upper() == "TOTAL":
                total = r
        return reader.fieldnames or [], rows, total


def guess_year(low, folder):
    """A bare year ("w2_2025") is the tax year. A full date ("scan 2026-01-30") is when the file
    was made; tax forms arrive the year after the tax year they cover."""
    dated = re.search(r"(20\d\d)[-_.]?(0[1-9]|1[0-2])[-_.]?([0-2]\d|3[01])", low)
    bare = re.findall(r"(?<!\d)(20\d\d)(?![-_.]?(?:0[1-9]|1[0-2])[-_.]?\d\d)", low)
    if bare:
        return int(bare[0])
    if dated:
        year = int(dated.group(1))
        return year - 1 if folder in ("income_docs", "investment_services", "loans") else year
    return None


def guess(name):
    low = name.lower()
    if low.endswith(".csv"):
        return {"kind": "Ledger or export (CSV)", "folder": None, "ledger": None, "year": guess_year(low, None)}
    for pattern, kind, folder, ledger in GUESS_RULES:
        if re.search(pattern, low):
            return {"kind": kind, "folder": folder, "ledger": ledger, "year": guess_year(low, folder)}
    return {"kind": "Unknown: AI will open it", "folder": None, "ledger": None, "year": guess_year(low, None)}


def inbox_files():
    if not INBOX.is_dir():
        return []
    return sorted((f for f in INBOX.iterdir() if f.is_file() and not f.name.startswith(".") and f.name != "README.md"), key=lambda f: f.name.lower())


# ---------------------------------------------------------------- commands

def cmd_init(args):
    year = args.year
    INBOX.mkdir(parents=True, exist_ok=True)
    ORGANIZED.mkdir(parents=True, exist_ok=True)
    if not LOG.exists():
        with open(LOG, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(LOG_HEAD)
    dest = year_dir(year)
    created = 0
    for src in TEMPLATE.rglob("*"):
        target = dest / str(src.relative_to(TEMPLATE)).replace("YEAR", str(year))
        if src.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif src.name == ".gitkeep":
            continue
        elif target.exists():
            print(f"  keep     {rel(target)} (already exists)")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, target)
            created += 1
            print(f"  created  {rel(target)}")
    if not PROFILE.exists():
        shutil.copyfile(ROOT / "templates" / "profile.yml", PROFILE)
        print(f"  created  {rel(PROFILE)} (fill it in, or use step 1 of TaxAssistUS.html)")
    print(f"Ready: {rel(dest)} ({created} new files). Drop documents into {rel(INBOX)}/")
    write_status(quiet=True)


def cmd_inbox(args):
    files = inbox_files()
    if not files:
        print(f"{rel(INBOX)}/ is empty.")
        return
    print(f"{len(files)} file(s) waiting in {rel(INBOX)}/\n")
    for f in files:
        g = guess(f.name)
        dest = f"organized/{g['year'] or '<YEAR>'}_TaxDocs/{g['folder']}/" if g["folder"] else "(open the file to decide)"
        print(f"  {f.name}\n      looks like: {g['kind']}  →  {dest}")


def cmd_organize(args):
    src = Path(args.file)
    if not src.is_absolute():
        src = INBOX / src if (INBOX / src).exists() else Path.cwd() / src
    if not src.is_file():
        sys.exit(f"Not found: {args.file}")
    if args.subfolder not in SUBFOLDERS + ["."]:
        sys.exit(f"Subfolder must be one of: {', '.join(SUBFOLDERS)} or '.' for the year folder itself")
    dest_dir = year_dir(args.year) if args.subfolder == "." else year_dir(args.year) / args.subfolder
    if not year_dir(args.year).is_dir():
        sys.exit(f"{rel(year_dir(args.year))} doesn't exist. Run: python3 tools/taxassist.py init {args.year}")
    dest_dir.mkdir(parents=True, exist_ok=True)
    new_name = args.name or src.name
    if new_name != new_name.strip() or "/" in new_name:
        sys.exit("The new name can't contain slashes or leading/trailing spaces.")
    dest = dest_dir / new_name
    if dest.exists():
        sys.exit(f"{rel(dest)} already exists. Pick another --name; nothing was moved.")
    shutil.move(str(src), str(dest))
    new_file = not LOG.exists()
    with open(LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(LOG_HEAD)
        w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), src.name, args.what or guess(src.name)["kind"], args.year,
                    rel(dest).replace("my_tax_files/", ""), args.ledger or "", args.by, args.notes or ""])
    print(f"Moved {src.name} → {rel(dest)} and logged it in {rel(LOG)}")
    write_status(quiet=True)


def run_checks(year):
    d = year_dir(year)
    problems, warnings = [], []
    if not d.is_dir():
        return [f"{rel(d)} not found"], []
    referenced = set()
    for template in sorted(TEMPLATE.glob("*_YEAR.csv")):
        path = d / template.name.replace("YEAR", str(year))
        if not path.exists():
            warnings.append(f"missing {path.name} (copy it from templates/ if you need it)")
            continue
        expected = read_csv(template)[0]
        head, rows, total = read_csv(path)
        if head != expected:
            missing = [h for h in expected if h not in head]
            problems.append(f"{path.name}: columns differ from the template" + (f" (missing: {', '.join(missing)})" if missing else ""))

        stem = template.name.replace("_YEAR.csv", "")
        if stem not in EXPENSE_LEDGERS:
            continue
        folder = d / EXPENSE_LEDGERS[stem]
        seen = set()
        for n, r in enumerate(rows, start=2):
            where = f"{path.name} line {n}"
            date = r.get("Date", "")
            if not date.startswith(str(year)):
                warnings.append(f"{where}: date {date!r} is outside {year} (cash method: record when paid)")
            amount, deductible = num(r.get("Amount")), num(r.get("Deductible Amount"))
            use = num(r.get("Business Use %")) if r.get("Business Use %") else 100
            if not 0 <= use <= 100:
                problems.append(f"{where}: Business Use % is {use}")
            if deductible - amount > 0.005:
                problems.append(f"{where}: deductible {money(deductible)} is more than paid {money(amount)}")
            if not r.get("Business Purpose"):
                warnings.append(f"{where}: no Business Purpose")
            receipt = (r.get("Receipt File") or "").strip()
            if not receipt:
                problems.append(f"{where}: no Receipt File")
            elif (folder / receipt).exists():
                referenced.add((folder / receipt).resolve())
            elif (d / receipt).exists():
                referenced.add((d / receipt).resolve())
            else:
                problems.append(f"{where}: receipt {receipt!r} not found in {folder.name}/")
            key = (r.get("Vendor"), r.get("Invoice #"), r.get("Amount"))
            if key[1] and key in seen:
                warnings.append(f"{where}: possible duplicate of invoice {key[1]}")
            seen.add(key)
        if total and "Deductible Amount" in expected:
            col = expected.index("Deductible Amount")
            if col < len(total) and total[col].strip():
                s = sum(num(r.get("Deductible Amount")) for r in rows)
                if abs(num(total[col]) - s) > 0.005:
                    problems.append(f"{path.name}: TOTAL row says {money(num(total[col]))} but rows add up to {money(s)}")
        if folder.is_dir():
            for f in sorted(folder.iterdir()):
                if f.name != f.name.strip():
                    problems.append(f"{folder.name}/{f.name!r} has leading/trailing spaces in its name")
                elif f.is_file() and f.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg"} and f.resolve() not in referenced:
                    warnings.append(f"{folder.name}/{f.name} is not referenced by any ledger row")
    return problems, warnings


def cmd_check(args):
    problems, warnings = run_checks(args.year)
    for p in problems:
        print(f"PROBLEM  {p}")
    for w in warnings:
        print(f"check    {w}")
    print(f"\n{len(problems)} problem(s), {len(warnings)} item(s) to review in {rel(year_dir(args.year))}")
    write_status(quiet=True)
    sys.exit(1 if problems else 0)


def cmd_summary(args):
    year = args.year
    d = year_dir(year)
    out = [f"# {year} tax file summary", ""]

    p = d / f"w2_{year}.csv"
    if p.exists():
        _, rows, _ = read_csv(p)
        out += ["## W-2s", "", "| Employer | Box 1 wages | Box 2 federal w/h | Box 17 state w/h |", "|---|--:|--:|--:|"]
        for r in rows:
            out.append(f"| {r['Employer']} | {money(num(r.get('Box 1 Wages Tips Other Comp')))} | {money(num(r.get('Box 2 Federal Income Tax Withheld')))} | {money(num(r.get('Box 17 State Income Tax')))} |")
        out.append("")

    by_cat, by_vendor, count, total = defaultdict(float), defaultdict(float), 0, 0.0
    for stem in EXPENSE_LEDGERS:
        p = d / f"{stem}_{year}.csv"
        if not p.exists():
            continue
        _, rows, _ = read_csv(p)
        for r in rows:
            amt = num(r.get("Deductible Amount"))
            by_cat[r.get("Category") or "Uncategorized"] += amt
            by_vendor[r.get("Vendor") or "Unknown"] += amt
            count += 1
            total += amt
    if count:
        out += [f"## Business expenses ({count} receipts, {money(total)} deductible)", "", "| Category | Deductible |", "|---|--:|"]
        out += [f"| {k} | {money(v)} |" for k, v in sorted(by_cat.items(), key=lambda kv: -kv[1])]
        out += ["", "| Vendor | Deductible |", "|---|--:|"]
        out += [f"| {k} | {money(v)} |" for k, v in sorted(by_vendor.items(), key=lambda kv: -kv[1])]
        out.append("")

    p = d / f"business_income_{year}.csv"
    if p.exists():
        _, rows, _ = read_csv(p)
        out += [f"## Business income: {money(sum(num(r.get('Amount')) for r in rows))} from {len(rows)} payment(s)", ""]

    p = d / f"investments_{year}.csv"
    if p.exists():
        head, rows, _ = read_csv(p)
        cols = [h for h in head if h not in ("Broker", "Source File")]
        out += ["## Investments (1099 totals)", "", "| Item | Total |", "|---|--:|"]
        out += [f"| {c} | {money(sum(num(r.get(c)) for r in rows))} |" for c in cols]
        out.append("")

    p = d / f"payments_and_deductions_{year}.csv"
    if p.exists():
        _, rows, _ = read_csv(p)
        if rows:
            out += ["## Payments and deductions", "", "| Type | Description | Amount |", "|---|---|--:|"]
            out += [f"| {r.get('Type')} | {r.get('Description')} | {money(num(r.get('Amount')))} |" for r in rows]
            out.append("")

    print("\n".join(out))


def write_status(quiet=False):
    """Write my_tax_files/status.js: a snapshot the HTML pages load with a <script> tag (works from file://)."""
    if not PRIVATE.is_dir():
        return
    inbox = []
    for f in inbox_files():
        st = f.stat()
        inbox.append({"name": f.name, "size": st.st_size,
                      "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"), "guess": guess(f.name)})
    years = []
    for d in sorted(ORGANIZED.glob("[0-9][0-9][0-9][0-9]_TaxDocs"), reverse=True):
        year = int(d.name[:4])
        folders = {s: sum(1 for f in (d / s).iterdir() if f.is_file() and not f.name.startswith(".")) for s in SUBFOLDERS if (d / s).is_dir()}
        ledgers, csv_text = {}, {}
        for p in sorted(d.glob(f"*_{year}.csv")):
            _, rows, _ = read_csv(p)
            ledgers[p.name] = len(rows)
            csv_text[p.name] = p.read_text(encoding="utf-8-sig")
        reports = sorted(p.name for p in d.glob("*.html"))
        problems, warnings = run_checks(year)
        years.append({"year": year, "folder": f"organized/{d.name}", "folders": folders, "ledgers": ledgers,
                      "reports": reports, "problems": problems[:20], "problemCount": len(problems),
                      "warningCount": len(warnings), "csv": csv_text})
    log = []
    if LOG.exists():
        _, rows, _ = read_csv(LOG)
        log = rows[-30:][::-1]
    profile, issues = load_profile()
    untouched = PROFILE.exists() and PROFILE.read_text(encoding="utf-8") == (ROOT / "templates" / "profile.yml").read_text(encoding="utf-8")
    data = {"generated": datetime.now().strftime("%Y-%m-%d %H:%M"), "inboxPath": str(INBOX), "privatePath": str(PRIVATE),
            "profile": profile, "profileIssues": issues, "profileIsTemplate": untouched,
            "agentsText": (ROOT / "AGENTS.md").read_text(encoding="utf-8") if (ROOT / "AGENTS.md").exists() else None, "inbox": inbox, "years": years, "log": log}
    STATUS.write_text("// Generated by tools/taxassist.py status. Private: never commit.\nwindow.TAX_ASSIST_STATUS = "
                      + json.dumps(data, indent=1) + ";\n", encoding="utf-8")
    for issue in [] if untouched else issues:
        print(f"profile  {issue}")
    if not quiet:
        print(f"Wrote {rel(STATUS)}: {len(inbox)} in inbox, {len(years)} year folder(s), {len(log)} log entries")


def ensure_setup():
    INBOX.mkdir(parents=True, exist_ok=True)
    ORGANIZED.mkdir(parents=True, exist_ok=True)
    if not any(ORGANIZED.glob("[0-9][0-9][0-9][0-9]_TaxDocs")):
        print("First run: setting up your private folder.")
        cmd_init(argparse.Namespace(year=datetime.now().year))
    elif not PROFILE.exists():
        shutil.copyfile(ROOT / "templates" / "profile.yml", PROFILE)
    write_status()


def cmd_start(args):
    """What the Start launchers run: first-run setup, fresh snapshot, open the app."""
    ensure_setup()
    page = ROOT / "TaxAssistUS.html"
    print(f"\nYour files:  {PRIVATE}\nDrop documents into:  {INBOX}")
    if args.no_browser or not webbrowser.open(page.as_uri()):
        print(f"Open this in your browser:  {page.as_uri()}")


def cmd_serve(args):
    """Serve the project at http://127.0.0.1:<port>, reachable from this computer only.

    Binding to 127.0.0.1 keeps other devices out. Because any website open in your browser
    could still try to load http://127.0.0.1/... (e.g. <script src=".../status.js">), every
    response also refuses cross-site use, and requests from other sites or with a foreign
    Host header (DNS rebinding) are rejected. On a headless server, reach it through an SSH
    tunnel; any local port works, because only the host name is checked."""
    import getpass
    import http.server
    import socket

    ensure_setup()
    local_names = {"127.0.0.1", "localhost", "[::1]"}

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(ROOT), **kw)

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            self.send_header("Cross-Origin-Resource-Policy", "same-origin")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            super().end_headers()

        def allowed(self):
            host = (self.headers.get("Host") or "").lower()
            name = host.rsplit(":", 1)[0] if not host.endswith("]") else host
            if name not in local_names:
                return False
            site = self.headers.get("Sec-Fetch-Site")
            if site and site not in ("same-origin", "none"):
                return False
            path = urllib.parse.unquote(urllib.parse.urlsplit(self.path).path)
            return not any(part.startswith(".") for part in path.split("/") if part)

        def do_GET(self):
            if not self.allowed():
                self.send_error(403, "Tax Assist US only answers this computer's own pages")
                return
            path = urllib.parse.urlsplit(self.path).path
            if path in ("", "/"):
                self.send_response(302)
                self.send_header("Location", "/TaxAssistUS.html")
                self.end_headers()
                return
            if path == "/my_tax_files/status.js":
                write_status(quiet=True)  # always fresh: just reload the page
            if path == "/api/check":
                self.api_check()
                return
            super().do_GET()

        def api_check(self):
            """Read-only: run the ledger/receipt checks for ?year=YYYY and return JSON."""
            year = (urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query).get("year") or [""])[0]
            if not re.fullmatch(r"20\d\d", year):
                self.send_error(400, "year must look like 2025")
                return
            problems, warnings = run_checks(int(year))
            write_status(quiet=True)
            body = json.dumps({"year": int(year), "problems": problems, "warnings": warnings,
                               "ranAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            """The only write: replace my_tax_files/profile.yml with valid profile YAML (step 1's Save)."""
            origin = self.headers.get("Origin")
            if not self.allowed() or (origin and urllib.parse.urlsplit(origin).hostname not in ("127.0.0.1", "localhost", "::1")):
                self.send_error(403)
                return
            if urllib.parse.urlsplit(self.path).path != "/api/profile":
                self.send_error(404)
                return
            length = int(self.headers.get("Content-Length") or 0)
            if not 0 < length <= 65536:
                self.send_error(413)
                return
            try:
                text = self.rfile.read(length).decode("utf-8")
                parsed = parse_yaml(text)
            except Exception:
                self.send_error(400, "not valid profile YAML")
                return
            if not isinstance(parsed, dict) or parsed.get("filing_status") not in FILING_STATUSES:
                self.send_error(400, "not a Tax Assist US profile")
                return
            tmp = PROFILE.with_name("profile.yml.tmp")
            tmp.write_text(text, encoding="utf-8")
            tmp.replace(PROFILE)
            write_status(quiet=True)
            body = json.dumps({"saved": True, "issues": load_profile()[1]}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_HEAD(self):
            if not self.allowed():
                self.send_error(403)
                return
            super().do_HEAD()

        def log_message(self, fmt, *a):
            pass

    server = None
    for port in range(args.port, args.port + 10):
        try:
            server = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    if server is None:
        sys.exit(f"Ports {args.port}-{args.port + 9} are busy. Try: python3 tools/taxassist.py serve --port 9000")
    url = f"http://127.0.0.1:{port}/TaxAssistUS.html"
    if args.headless:
        who = f"{getpass.getuser()}@{socket.getfqdn()}"
        print(f"\nTax Assist US is serving on this server's 127.0.0.1:{port} only (not on the network).")
        print("On your own computer, open a terminal and run:\n")
        print(f"    ssh -N -L {port}:127.0.0.1:{port} {who}\n")
        print(f"then open  {url}  in your browser. Close that ssh command to disconnect.")
        print(f"Add documents with:  scp <files> {who}:{INBOX}/")
        print("Press Ctrl+C here to stop the server.")
    else:
        print(f"\nTax Assist US is running at  {url}\nOnly this computer can open it. Press Ctrl+C (or close this window) to stop.")
        if not args.no_browser:
            webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


def main():
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to a code page without arrows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)  # also flush logs under nohup/systemd
    ap = argparse.ArgumentParser(prog="taxassist.py", description="Tax Assist US helper (local files only).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("init", cmd_init), ("check", cmd_check), ("summary", cmd_summary)):
        sp = sub.add_parser(name)
        sp.add_argument("year", type=int)
        sp.set_defaults(fn=fn)
    sub.add_parser("inbox", help="list files waiting in the inbox").set_defaults(fn=cmd_inbox)
    sub.add_parser("status", help="refresh my_tax_files/status.js").set_defaults(fn=lambda a: write_status())
    sp = sub.add_parser("start", help="first-run setup, refresh the snapshot, open TaxAssistUS.html")
    sp.add_argument("--no-browser", action="store_true", help="print the page address instead of opening it")
    sp.set_defaults(fn=cmd_start)
    sp = sub.add_parser("serve", help="serve TaxAssistUS.html at http://127.0.0.1:8765 (this computer only)")
    sp.add_argument("--port", type=int, default=8765, help="first port to try (default 8765)")
    sp.add_argument("--no-browser", action="store_true", help="don't open a browser")
    sp.add_argument("--headless", action="store_true", help="Linux server: no browser; print SSH tunnel instructions")
    sp.set_defaults(fn=cmd_serve)
    sp = sub.add_parser("organize", help="move one inbox file into a year folder and log it")
    sp.add_argument("file", help="file name in my_tax_files/inbox/ (or a path)")
    sp.add_argument("year", type=int)
    sp.add_argument("subfolder", help=f"one of {', '.join(SUBFOLDERS)}, or '.'")
    sp.add_argument("--name", help="new file name, following guides/1_files.md")
    sp.add_argument("--as", dest="what", help="what the document is, e.g. 'W-2 from Acme Corp'")
    sp.add_argument("--ledger", help="ledger CSV you added a row to, if any")
    sp.add_argument("--notes", help="anything worth remembering")
    sp.add_argument("--by", default="assistant", help="who organized it (default: assistant)")
    sp.set_defaults(fn=cmd_organize)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
