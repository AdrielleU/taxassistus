#!/bin/sh
# Start Caddy with the Tax Assist US login (docker-compose.yml).
#
#   login.sh LOGIN_FILE CADDYFILE
#
# The login is TAXASSIST_LOGIN_USER and TAXASSIST_LOGIN_HASH (a bcrypt hash
# from `caddy hash-password`) in LOGIN_FILE, data/caddy/data/login.env on the
# server. It's kept there, not in .env, so Caddy never needs the project
# folder (your tax files) mounted. If there's no hash yet (first start), this
# makes a random password, saves its hash and the username (admin unless
# set), and prints the password once. Lost it? Delete login.env and restart:
# a new one is made.
set -eu

login_file=$1
caddyfile=$2

# The value of NAME in LOGIN_FILE, without quotes around it.
value() {
  [ -f "$login_file" ] || return 0
  sed -n "s/^$1=//p" "$login_file" | tail -n 1 |
    sed -e "s/^'\(.*\)'\$/\1/" -e 's/^"\(.*\)"$/\1/'
}

user=$(value TAXASSIST_LOGIN_USER)
hash=$(value TAXASSIST_LOGIN_HASH)
user=${user:-admin}

if [ -z "$hash" ]; then
  password=$(LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c 20)
  hash=$(caddy hash-password --plaintext "$password")
  tmp="$login_file.tmp"
  (
    umask 077 # only its owner can read the hash
    {
      echo "TAXASSIST_LOGIN_USER=$user"
      echo "TAXASSIST_LOGIN_HASH='$hash'"
    } >"$tmp"
  )
  # Owned like the folder it's in, not by the container's root.
  chown "$(stat -c %u:%g "$(dirname "$login_file")")" "$tmp" 2>/dev/null || true
  mv "$tmp" "$login_file"
  cat <<EOF
==================================================================
 Tax Assist US login, made on first start. Save the password now:
 only its hash is kept (in data/caddy/data/login.env), so it isn't
 shown again.

   Username: $user
   Password: $password

 To change it: delete data/caddy/data/login.env and restart
 (podman-compose up -d) for a new random one, or put your own
 hash there (caddy hash-password).
==================================================================
EOF
fi

export TAXASSIST_LOGIN_USER="$user" TAXASSIST_LOGIN_HASH="$hash"
exec caddy run --config "$caddyfile" --adapter caddyfile
