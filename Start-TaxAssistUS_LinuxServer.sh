#!/bin/sh
# Tax Assist US launcher for a headless Linux SERVER (no desktop, reached over SSH).
#   ./Start-TaxAssistUS_LinuxServer.sh               serve on this server's 127.0.0.1:8765
#   ./Start-TaxAssistUS_LinuxServer.sh --port 9000   use another port
# It never listens on the network. View it from your own computer through an SSH tunnel;
# the exact command is printed when it starts. Ctrl+C stops it.
cd "$(dirname "$0")" || exit 1

for py in python3 python; do
  if command -v "$py" >/dev/null 2>&1 && "$py" -c 'import sys; sys.exit(sys.version_info < (3, 8))' >/dev/null 2>&1; then
    exec "$py" tools/taxassist.py serve --headless "$@"
  fi
done

echo "Python 3.8 or newer is required on the server."
echo "Install it: sudo apt install python3   (Fedora/RHEL: sudo dnf install python3, Arch: sudo pacman -S python)"
exit 1
