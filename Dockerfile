# Tax Assist US server image: the app (taxassist.py serve). docker-compose.yml runs it as "taxassist"
# with my_tax_files/ mounted, behind the official Caddy image (the login popup). Built and published
# to ghcr.io/adrielleu/taxassistus by .github/workflows/image.yml on each version tag.
# Build it yourself: docker build -t ghcr.io/adrielleu/taxassistus:dev .
FROM docker.io/library/python:3.12.15-alpine3.24

# A plain user: no root, no shell login, no home folder
RUN addgroup -g 1000 taxassist && adduser -u 1000 -G taxassist -D -H -s /sbin/nologin taxassist

ENV TZ=America/Phoenix \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
# The code, owned by root and read-only to the app (.dockerignore keeps out tax files and secrets)
COPY AGENTS.md CLAUDE.md GEMINI.md GROK.md README.md LICENSE TaxAssistUS.html state_tax_rates.csv ./
COPY assets/ assets/
COPY guides/ guides/
COPY templates/ templates/
COPY tools/ tools/
# The only folder it writes: the tax files (mounted over this)
RUN mkdir -p /app/my_tax_files && chown taxassist:taxassist /app/my_tax_files \
 && python3 -m py_compile tools/taxassist.py && rm -rf tools/__pycache__

USER taxassist
# Stop with Ctrl-C's signal: as the container's first process, Python ignores the default SIGTERM
STOPSIGNAL SIGINT
EXPOSE 8765
CMD ["python3", "tools/taxassist.py", "serve", "--bind", "0.0.0.0", "--port", "8765"]
