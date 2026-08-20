# SaaS custom-domain docs directory

A machine-readable directory of **real help/docs pages where SaaS products explain how a
customer connects a custom domain** — the "add a custom domain / set your CNAME / verify
your domain / enable SSL" articles that flood search results for *connect domain* and its
variations. Plus the reproducible pipeline used to build it.

## What's here

| File | What it is |
|---|---|
| `directory.csv` / `directory.json` | The directory itself — one row per doc URL |
| `scripts/1_serp_seed.py` | Stage 1 — SERP API seed (discovers hosts) |
| `scripts/2_sitemap_expand.py` | Stage 2 — free per-host sitemap harvest (the multiplier) |
| `scripts/3_cc_harvest.py` | Stage 3 — Common Crawl harvest + clean + write directory |
| `common-crawl-scale-recipe.md` | The web-scale path (columnar index via DuckDB/Athena) |
| `COLLECTION_PROMPT.md` | The full collection spec / prompt this was built from |

### Schema (`directory.csv`)

`product, vendor_host, doc_url, doc_title, doc_platform, discovery_source`

`discovery_source` records which method surfaced each row, so coverage is auditable.

## Current snapshot

Built from **8 SERP searches** (of a 250/month free tier) plus free expansion:

- **172** canonical custom-domain / DNS setup doc URLs
- **51** distinct SaaS products
- Source mix: `sitemap(free)` 112 · `serp` 37 · `commoncrawl-domain(free)` 23
- **18 products surfaced *only* via Common Crawl** — custom-domained help centers
  (e.g. on `intercom.help`) that keyword search never ranks: Aasaan, Appointmatic,
  Art Storefronts, CloudCone, Dynalinks, Mini-Course-Generator, Xperiencify, and more.

This is a **seed snapshot**, not the ceiling — see scaling below.

## Method (why it reaches "basically all")

SERP is the *seed*, not the harvester. The exhaustive bulk comes from free, uncapped
index/platform methods that the seed unlocks:

1. **SERP → discover help-center HOSTS** (not just pages). ~10 results per exact-phrase
   query, so spend the budget on breadth of phrasing, not depth.
2. **Sitemap / `llms.txt` per host** — one request returns every article on a host; filter
   slugs for domain/DNS keywords. ~48× more URLs than the seed here, at zero SERP cost.
3. **Common Crawl** — `cc_harvest.py` runs two CDX modes: *host-mode* recovers docs from
   hosts with no sitemap; *domain-mode* enumerates custom-domain articles across **all
   tenants** of a help platform (`intercom.help`, `readme.io`, …).
4. **Columnar index (the real scale answer)** — DuckDB/Athena over Common Crawl's Parquet
   index scans **every host at once** (`url_path LIKE '%custom-domain%'`), catching the
   custom-domained help centers that CDX domain-mode misses. See
   `common-crawl-scale-recipe.md`. This removes SERP from the critical path entirely.

**Precision** is an iterative filter: drop community/forum hosts and Discourse `/t/` paths,
require phrase-level keywords (not bare `dns`/`domain`), then classify each page with a
cheap LLM to fill `apex_supported`, `verification_method`, `ssl_notes`, etc.

## Reproduce

```bash
cd saas-docs-directory
export SERP_KEY=...            # SerpAPI key (free tier is fine for the seed)
# optional: export CA_BUNDLE=/path/to/proxy-ca.crt   (only behind a TLS-intercepting proxy)
python3 scripts/1_serp_seed.py       # -> data/seed.json
python3 scripts/2_sitemap_expand.py  # -> data/expanded.json
python3 scripts/3_cc_harvest.py      # -> data/full.json + directory.csv
```

To go web-scale, run the DuckDB query in `common-crawl-scale-recipe.md` across each 2026
crawl and merge — expected to take the product count from ~50 into the thousands.

## Scope & ethics

Public documentation URLs only. Infrastructure vendors (Cloudflare, Approximated, Entri,
customdomain.ai, …) are the *suppliers* cataloged in the main list, not the SaaS help pages
here. Scripts obey standard rate limits and prefer official APIs, sitemaps, and the Common
Crawl index (which avoids hitting sites live) over ad-hoc scraping.
