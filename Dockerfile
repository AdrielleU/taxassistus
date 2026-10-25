# Tax Assist US server image: the app (taxassist.py serve) and Caddy (the login popup) in one image.
# docker-compose.yml runs it twice: "taxassist" (the app, with my_tax_files/ mounted) and
# "taxassist-caddy" (only Caddy, which never gets the tax files). Built and published to
# ghcr.io/adrielleu/taxassistus by .github/workflows/image.yml on each version tag.
# Build it yourself: docker build -t ghcr.io/adrielleu/taxassistus:dev .
FROM docker.io/library/caddy:2.11.7-alpine AS caddy

FROM docker.io/library/python:3.12.15-alpine3.24

# Caddy's binary only (the same pinned release as the official image), without the file capability
# it ships with (bind port 80): it listens on 8080, and a container with all capabilities dropped
# can't run a file that asks for one.
COPY --from=caddy /usr/bin/caddy /usr/bin/caddy
RUN apk add --no-cache --virtual .setcap libcap-setcap && setcap -r /usr/bin/caddy && apk del .setcap

# A plain user for both containers: no root, no shell login, no home folder
RUN addgroup -g 1000 taxassist && adduser -u 1000 -G taxassist -D -H -s /sbin/nologin taxassist

ENV TZ=America/Phoenix \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    XDG_CONFIG_HOME=/config \
    XDG_DATA_HOME=/data

WORKDIR /app
# The code, owned by root and read-only to the app (.dockerignore keeps out tax files and secrets)
COPY AGENTS.md CLAUDE.md GEMINI.md GROK.md README.md LICENSE TaxAssistUS.html state_tax_rates.csv ./
COPY assets/ assets/
COPY guides/ guides/
COPY templates/ templates/
COPY tools/ tools/
COPY docker/Caddyfile /etc/caddy/Caddyfile
# The only folders anything writes: the tax files (mounted over this) and Caddy's state
RUN mkdir -p /app/my_tax_files /data /config \
 && chown taxassist:taxassist /app/my_tax_files /data /config \
 && python3 -m py_compile tools/taxassist.py && rm -rf tools/__pycache__

USER taxassist
# Stop with Ctrl-C's signal: as the container's first process, Python ignores the default SIGTERM
# (Caddy stops cleanly on either).
STOPSIGNAL SIGINT
EXPOSE 8765 8080
CMD ["python3", "tools/taxassist.py", "serve", "--bind", "0.0.0.0", "--port", "8765"]
