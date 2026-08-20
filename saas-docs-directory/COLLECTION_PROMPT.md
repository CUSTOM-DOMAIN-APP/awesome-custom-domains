# PROMPT — Build an Exhaustive Directory of Every SaaS "Custom Domain / Connect Domain / DNS Setup" Help & Docs Page

> **How to use this prompt.** Paste everything below the line into a capable
> agent (Claude Code with web tools + a code sandbox, or a data engineer).
> It is written so the executor FIRST investigates the collection method,
> THEN chooses the most efficient stack, THEN executes and produces a single
> deduplicated, structured directory. Brute-force "search one keyword at a
> time" is explicitly treated as the fallback, not the plan.

---

## ROLE

You are a data-collection and web-mining engineer. Your job is to assemble the
most **exhaustive** possible directory of public web pages that document, for a
software/SaaS product, **how an end user connects, adds, sets up, verifies, or
points a custom domain** at that product — including the DNS steps (CNAME / A /
TXT records, nameservers, apex handling), domain verification, and SSL/TLS
setup. These are the "help desk / docs / support / knowledge-base" pages that
flood the results when someone searches *connect domain*, *add a custom
domain*, *set up DNS*, etc.

Optimize for **coverage first** (find essentially all of them), correctness
second, and cost third. Naive one-page-at-a-time browsing does NOT scale to
"all of them" — you must use index-level and platform-level methods.

## TARGET DEFINITION — what counts as a hit

**IN scope** — a public URL that is primarily an instructional/help page for
*a specific product* explaining any of:
- Connecting / adding / setting up / configuring / pointing / mapping / linking
  a **custom domain** (or "your own domain", subdomain, apex/root domain,
  vanity/branded/white-label domain) to that product.
- The **DNS records** to create for that (CNAME, A/AAAA, ALIAS/ANAME, TXT
  verification, MX/SPF/DKIM when part of the domain-connect flow), nameserver
  changes, or provider-specific DNS instructions.
- **Domain verification** and **SSL/TLS / HTTPS** provisioning for a custom
  domain.

**OUT of scope** (record-and-skip, don't let them pollute the directory):
- Domain **registrars/resale** pages about buying a domain in general.
- Generic "what is DNS" educational blog posts not tied to a product's setup.
- The custom-domain *infrastructure vendors themselves* (Cloudflare for SaaS,
  Approximated, Entri, SaaS Custom Domains, domainee.dev, customdomain.ai) —
  keep these in a **separate "infra/API vendors" table**, they are suppliers,
  not the SaaS help pages we're cataloging.
- Marketing/pricing pages with no setup instructions.

One product may have several qualifying pages (e.g. a Zendesk-DNS article, a
GitBook-DNS article, an apex vs subdomain article) — capture each, but tag them
to the same product so the directory can roll up to one product per row.

## DELIVERABLE

A single machine-readable dataset (CSV **and** JSON, plus a rendered Markdown
index grouped by category), one row per documentation URL, with this schema:

| field | meaning |
|---|---|
| `product` | SaaS product / platform name (e.g. "Webflow", "Substack") |
| `vendor_url` | product's main site |
| `doc_url` | the specific help/docs page (canonical, de-duplicated) |
| `doc_title` | page title |
| `doc_platform` | help-desk platform hosting it (Zendesk, Intercom, GitBook, ReadMe, Mintlify, Freshdesk, HelpScout, Document360, Notion, Docusaurus, custom, …) |
| `category` | product category (website builder, e-commerce, newsletter, no-code, LMS, link-in-bio, docs/KB, community, video, forms, etc.) |
| `record_types` | DNS records the page instructs (CNAME / A / AAAA / TXT / ALIAS / NS / MX) |
| `apex_supported` | does it document apex/root domains? (yes/no/unknown) |
| `verification_method` | TXT / CNAME / meta-tag / file / none / unknown |
| `ssl_notes` | how SSL is handled (auto / Let's Encrypt / manual / unknown) |
| `cname_target` | the CNAME/edge target it tells users to point at, if shown (e.g. `cname.vercel-dns.com`) |
| `discovery_source` | which method found it (sitemap / zendesk-api / serp / commoncrawl / seed-list / autosuggest) |
| `lang` | page language |
| `last_seen` | date fetched |
| `confidence` | classifier confidence it's really a custom-domain setup page |

Also emit: a `coverage_report.md` (how many products/pages per category, per
platform, per discovery source; estimated coverage and known gaps) and a
`sources_and_methods.md` documenting exactly which methods you ran and their
yield.

---

## PHASE 0 — INVESTIGATE THE METHOD (do this before collecting anything)

Do not start keyword-searching yet. First produce a short **method plan** by
answering these, using quick web research where needed:

1. **Where do these pages physically live?** Confirm that the overwhelming
   majority of SaaS help centers run on a *small number of platforms* (Zendesk
   Guide, Intercom Help, Freshdesk, Help Scout, Document360, GitBook, ReadMe,
   Mintlify, HubSpot KB, Zoho Desk, Notion, Docusaurus). This is the key
   insight: **enumerate the platforms, not the internet.**
2. **Which of those platforms expose a search/list API or a predictable
   sitemap?** (e.g. Zendesk's Help Center Search API; nearly every docs site
   ships `/sitemap.xml`; many modern docs now ship `/llms.txt` /
   `/llms-full.txt`.) Prefer structured endpoints over HTML scraping.
3. **What index-level corpora can substitute for live crawling?** (Common
   Crawl URL index; HTTP Archive on BigQuery with detected-technology columns;
   PublicWWW/BuiltWith technology enumeration.)
4. **What SERP API gives the deepest, cheapest pagination** for the residual
   long tail, and what are its result caps?
5. **What is the dedup key** (canonical host + normalized path) and how will
   you roll multiple pages up to one product?

Output the method plan as a ranked list (most efficient → fallback), then
execute Phases 1–5 in that order, stopping to add methods only if coverage
checks (Phase 5) show gaps.

---

## PHASE 1 — BUILD THE QUERY / KEYWORD UNIVERSE (permutation engine)

Generate the query set programmatically from a matrix, don't hand-type a few.

**Action verbs:** connect · add · set up · setup · configure · use · point ·
map · link · verify · bring · attach · assign · enable · change · switch to ·
migrate

**Objects:** domain · custom domain · your own domain · your domain ·
subdomain · apex domain · root domain · naked domain · vanity domain · branded
domain · white-label domain

**DNS/technical tokens:** DNS · DNS records · DNS settings · CNAME · CNAME
record · A record · AAAA · TXT record · nameservers · name servers · domain
verification · verify domain · SSL · SSL certificate · HTTPS

**Help-context tokens (for URL/path dorks):** help · support · docs ·
documentation · knowledge base · kb · hc · guide · guides · article · faq ·
getting started · learn

Cross-product these into (a) plain SERP queries ("how to connect a custom
domain", "add CNAME record custom domain", "point your domain DNS settings")
and (b) **search dorks** (see appendix) that pin results to help-desk hosts and
paths. Then **expand** the set with Google/Bing **autosuggest** and **"related
searches"** scraping so you capture phrasings you didn't predict.

---

## PHASE 2 — MULTI-CHANNEL HARVESTING (run in this efficiency order)

### A. Sitemap + `llms.txt` harvesting (highest yield per request)
For every help/docs host you know or discover, fetch `/sitemap.xml` (and nested
sitemaps), `/sitemap_index.xml`, `/llms.txt`, `/llms-full.txt`. One request
returns *all* article URLs for that host; grep the URL slugs and titles for the
domain/DNS keyword set. This is the single most efficient per-site method — use
it the instant you learn a new host.

### B. Help-desk platform enumeration + native search APIs (highest coverage)
This is the core of "get all of them." For each platform:
1. **Enumerate tenants** using it (see technographic sources in E): the set of
   `*.zendesk.com`, `intercom.help/*`, `*.freshdesk.com`,
   `*.helpscoutdocs.com`, `*.gitbook.io`, `*.readme.io`, `*.mintlify.app`,
   `*.document360.io`, `*.zohodesk.com`, `*.helpjuice.com`, `*.notion.site`,
   plus custom-domained help centers (`help.*`, `support.*`, `docs.*`, `kb.*`).
2. **Hit each tenant's native search** for "custom domain", "DNS", "CNAME":
   - **Zendesk Guide:** `GET https://{sub}.zendesk.com/api/v2/help_center/articles/search.json?query=custom%20domain`
     — returns up to **1000** results, 100/page, offset pagination, JSON with
     title/url/section. Also `.../articles.json` lists *all* articles for tiny
     tenants.
   - **Intercom Help / GitBook / ReadMe / Mintlify / Docusaurus:** use their
     sitemap (method A) or on-page search JSON; many are Algolia-backed
     (`/1/indexes/*/queries`) — query the index directly where public.
3. Classify each returned article with the Phase-4 classifier.

### C. SERP API with deep pagination + dorks (the residual web)
Run the Phase-1 queries and dorks through a **SERP API** (Serper.dev is cheapest
at scale — ~$0.30–$1 / 1k queries, 2,500 free; alternatives: SerpAPI, DataForSEO,
Bing Web Search, Brave — note Google Custom Search JSON API is closed to new
customers, sunset Jan 1 2027). Paginate to the API's max depth per query, not
just page 1. Dedup URLs as you go. Use `site:` and `inurl:` dorks to force
help-desk hosts (appendix).

### D. Common Crawl / HTTP Archive index filtering (long tail, offline)
For the tail that live search won't surface:
- **Common Crawl URL index (columnar/Parquet via Amazon Athena)**: filter by
  `url_host_registered_domain`, `url_path` LIKE the help/DNS patterns, and
  language — flexible field filtering without a URL-prefix constraint. The
  legacy **CDX API** (`index.commoncrawl.org/CC-MAIN-*-index?url=…&matchType=domain`)
  works when you already have host prefixes.
- **HTTP Archive on BigQuery**: join detected-**technology** (Zendesk/Intercom/
  GitBook/…) against pages whose URL matches help/DNS patterns — this gives you
  "every help center running platform X" plus the page, in one query.

### E. Seed lists & technographic enumeration (bootstraps A–D)
- Product universes: **G2 / Capterra / Product Hunt** category pages, "awesome-*"
  lists, SaaS directories → for each product, resolve its help center → sitemap.
- **Technographics:** **BuiltWith** "websites using Zendesk/Intercom/…" lists,
  **Wappalyzer**, **PublicWWW** (search page *source code* for a platform's
  embed signature, e.g. the Intercom or Zendesk widget snippet, to enumerate
  users). These produce the tenant lists that feed Method B.
- Your own **`awesome-custom-domains`** repo and the customdomain.ai
  "63 DNS providers" list as high-quality seeds.

### F. Autosuggest / related-search expansion (widen recall)
Feed discovered phrasings back into Phase 1 and re-run B/C until new methods
stop producing new products (see Phase 5 stop rule).

---

## PHASE 3 — NORMALIZE & DEDUP
- Canonicalize URLs (strip tracking params, fragments, trailing slashes;
  resolve redirects; prefer the canonical `<link rel=canonical>`).
- Dedup on normalized `doc_url`; then group rows to a **product** via
  registered domain + help-center brand.
- Detect language; keep non-English pages (tag `lang`) — "exhaustive" is
  multilingual.

## PHASE 4 — CLASSIFY & EXTRACT (cheap model, batched)
For each candidate page, run a **cheap LLM classifier/extractor** that:
1. Confirms it's really a custom-domain setup page (drop registrar/marketing/
   generic-DNS-explainer false positives) → `confidence`.
2. Extracts the structured fields (`record_types`, `apex_supported`,
   `verification_method`, `ssl_notes`, `cname_target`, `category`,
   `doc_platform`). Feed it the page text (from sitemap-fetched HTML or the
   Common Crawl WARC record — don't re-crawl what you already have).

## PHASE 5 — ASSEMBLE + COVERAGE / QA
- Emit CSV + JSON + grouped Markdown index.
- **Coverage report:** counts per category / platform / discovery source;
  products found per method; overlap between methods.
- **Stop rule (how you know you got "basically all"):** iterate methods until
  **two consecutive full passes add < 1% new unique products**, and every major
  category (website builders, e-commerce, newsletter/creator, no-code, LMS,
  link-in-bio, docs/KB, community, forms, video) has double-digit coverage.
  Log every known gap explicitly rather than hiding it.
- **QA sample:** re-verify a random 3–5% of rows by hand; report precision.

---

## EFFICIENCY LADDER — cheapest/most-exhaustive first, brute force last

1. **Sitemap / `llms.txt` per known host** — ~1 request → all article URLs. Do
   this for every host you touch.
2. **Platform native search API / article-list API** (Zendesk et al.) — up to
   1000 hits per tenant, structured, no HTML parsing.
3. **Technographic tenant enumeration** (BuiltWith / PublicWWW / HTTP Archive
   tech column) → feeds (1) and (2); turns "search the web" into "enumerate a
   few hundred thousand known help centers."
4. **Common Crawl / HTTP Archive index queries** — the whole indexed web,
   filtered offline by URL/host/language, no live crawl, no rate limits.
5. **SERP API deep pagination + dorks** — for anything the above miss; pay per
   query, so run it *after* the index methods to minimize spend.
6. **Per-keyword agent browsing (last turn's 50-agent approach)** — good for
   *method discovery, seed-finding, and classification*, but the **worst** tool
   for exhaustive URL enumeration (≈10 results/query, heavy overlap). Use agents
   as the brains around the pipeline, not as the crawler.

> Bottom line: the exhaustive list is a **pipeline** problem (indexes +
> platform APIs + sitemaps), with LLM agents doing method-selection,
> classification, and extraction — not a "spawn N searchers" problem.

## GUARDRAILS (respect these)
- Obey `robots.txt` and each platform's API Terms; prefer official APIs and
  sitemaps over scraping. Rate-limit and cache (Common Crawl/HTTP Archive avoid
  hitting sites at all). Set a real User-Agent. Don't collect anything behind
  auth or any personal data. SERP/technographic providers have their own ToS —
  stay within plan limits. This catalogs *public documentation URLs* only.

## SUCCESS CRITERIA
- Thousands of products across every category, multilingual, deduped to one
  product per row with N doc URLs each.
- Each discovery method's yield logged; index methods (1–4) should supply the
  bulk, SERP/agents only the tail.
- Coverage report shows the stop rule was met and lists residual gaps.

---

## APPENDIX A — starter search-dork set (feed to the SERP API)
```
"connect a custom domain" (site:zendesk.com OR site:intercom.help OR site:gitbook.io OR site:readme.io OR site:document360.io OR site:helpscoutdocs.com OR site:freshdesk.com)
inurl:help "custom domain" (CNAME OR "A record" OR "TXT record")
inurl:(support OR docs OR hc OR kb) "add a custom domain"
intitle:"custom domain" (setup OR connect OR configure) (DNS OR CNAME)
"point your domain" "CNAME" (inurl:help OR inurl:support)
"set up your custom domain" "SSL"
"bring your own domain" (docs OR help) CNAME
site:*.zendesk.com/hc "custom domain"
"verify your domain" "TXT record" (inurl:help OR inurl:docs)
```
Cross-multiply with the Phase-1 verb×object×DNS matrix and with each
help-platform host to generate hundreds of dorks; paginate each deeply.

## APPENDIX B — help-desk platform host fingerprints (for enumeration)
```
Zendesk Guide      *.zendesk.com/hc/ , custom help.* on Zendesk
Intercom           intercom.help/* , *.intercom.help
Freshdesk          *.freshdesk.com , *.freshworks.com
Help Scout         *.helpscoutdocs.com , docs.* on Help Scout
Document360        *.document360.io
GitBook            *.gitbook.io , docs.* on GitBook
ReadMe             *.readme.io , *.readme.com
Mintlify           *.mintlify.app , custom docs.*
Docusaurus/self    docs.* , support.* (static-site fingerprint)
HubSpot KB         knowledge.* , help.* on HubSpot
Zoho Desk          *.zohodesk.com , help.* on Zoho
Helpjuice/Guru/…   *.helpjuice.com , getguru, archbee, slab, tettra
Notion-as-docs     *.notion.site
Generic subdomains help.* support.* docs.* kb.* learn.* guides.*
```

## APPENDIX C — ready-to-run enumeration snippets
```bash
# Zendesk Help Center search (per tenant) — up to 1000 hits, structured JSON
curl -s "https://SUBDOMAIN.zendesk.com/api/v2/help_center/articles/search.json?query=custom%20domain&per_page=100"

# Any docs host: pull every article URL in one shot, then grep DNS terms
curl -s https://HOST/sitemap.xml | grep -Eo 'https?://[^<]+' \
  | grep -Ei 'custom-?domain|dns|cname|connect-?domain|nameserver'

# Modern docs increasingly ship this — instant, complete map for an LLM
curl -s https://HOST/llms.txt ; curl -s https://HOST/llms-full.txt

# Common Crawl CDX (when you have a host prefix)
curl -s "https://index.commoncrawl.org/CC-MAIN-2025-XX-index?url=HOST/*&output=json&filter=url:.*(custom.?domain|cname|dns).*"
```
For web-scale filtering, run the Common Crawl **columnar index** or **HTTP
Archive** in Athena/BigQuery: `WHERE url_path LIKE` the DNS/help patterns
(optionally joined to a detected-technology column) — no live crawling.

---

### Sources this method is grounded in
- Zendesk Help Center Search API (query/pagination/1000-cap): https://developer.zendesk.com/api-reference/help_center/help-center-api/articles/
- Common Crawl columnar/URL index vs CDX API: https://commoncrawl.org/blog/index-to-warc-files-and-urls-in-columnar-format · https://commoncrawl.org/cdxj-index
- SERP API options & caps (Serper cheapest; Google CSE closing 2027): https://scrapfly.io/blog/posts/google-serp-api-and-alternatives
- PublicWWW source-code search for technographic enumeration: https://publicwww.com/
