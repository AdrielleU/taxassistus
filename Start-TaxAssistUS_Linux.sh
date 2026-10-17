#!/bin/sh
# Tax Assist US launcher for a Linux DESKTOP (and macOS): ./Start-TaxAssistUS_Linux.sh
#   ./Start-TaxAssistUS_Linux.sh          open the page in your browser
#   ./Start-TaxAssistUS_Linux.sh serve    serve it at http://127.0.0.1:8765 instead (Ctrl+C stops)
# On a Mac, double-click Start-TaxAssistUS_Mac.command (it runs this).
# On a headless Linux SERVER, use Start-TaxAssistUS_LinuxServer.sh.
cd "$(dirname "$0")" || exit 1
[ $# -eq 0 ] && set -- start

for py in python3 python; do
  if command -v "$py" >/dev/null 2>&1 && "$py" -c 'import sys; sys.exit(sys.version_info < (3, 8))' >/dev/null 2>&1; then
    exec "$py" tools/taxassist.py "$@"
  fi
done

echo "Python 3.8 or newer wasn't found, so folder views and the inbox count won't show."
case "$(uname -s)" in
  Darwin) echo "Install it: accept the macOS prompt to install developer tools, or get it from https://www.python.org/downloads/" ;;
  *)      echo "Install it: sudo apt install python3   (Fedora: sudo dnf install python3, Arch: sudo pacman -S python)" ;;
esac
echo "Opening the page anyway: profile, estimate and CSV loading still work."
if command -v open >/dev/null 2>&1 && [ "$(uname -s)" = Darwin ]; then open TaxAssistUS.html
elif command -v xdg-open >/dev/null 2>&1; then xdg-open TaxAssistUS.html
else echo "Open this file in your browser: $(pwd)/TaxAssistUS.html"; fi
