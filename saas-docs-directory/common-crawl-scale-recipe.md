# Common Crawl — the web-scale path to "basically all" custom-domain docs

The CDX harvester (`cc_harvest.py`) is great for **known hosts** and **canonical help
platforms** (`intercom.help`, `readme.io`, …). But it has a ceiling: `matchType=domain`
only sees pages captured *under that domain*, and most mature help centers are
**custom-domained** (`help.acme.com`, not `acme.zendesk.com`). To catch those, you must
scan the crawl by **URL/path across every host at once** — that is the **columnar index**.

This removes SERP from the critical path completely: one query over one monthly crawl
returns every page on the web whose path looks like a custom-domain/DNS setup doc.

---

## Option A (recommended, no AWS account) — DuckDB over the public Parquet index

Common Crawl publishes the index as Hive-partitioned Parquet in a public S3 bucket
(`s3://commoncrawl/cc-index/table/cc-main/warc/`, region `us-east-1`, anonymous reads).
DuckDB can query it directly — you only need DuckDB + outbound S3.

```sql
INSTALL httpfs; LOAD httpfs;
SET s3_region='us-east-1';
SET s3_access_key_id=''; SET s3_secret_access_key='';   -- anonymous

COPY (
  SELECT url, url_host_name, url_path, content_languages
  FROM read_parquet(
    's3://commoncrawl/cc-index/table/cc-main/warc/crawl=CC-MAIN-2026-30/subset=warc/*.parquet',
    hive_partitioning = 1)
  WHERE fetch_status = 200
    AND url_host_tld <> 'onion'
    AND (
         lower(url_path) LIKE '%custom-domain%'  OR lower(url_path) LIKE '%custom_domain%'
      OR lower(url_path) LIKE '%connect-domain%' OR lower(url_path) LIKE '%connect-a-custom-domain%'
      OR lower(url_path) LIKE '%cname%'          OR lower(url_path) LIKE '%your-own-domain%'
      OR lower(url_path) LIKE '%bring-your-own-domain%' OR lower(url_path) LIKE '%vanity-domain%'
      OR lower(url_path) LIKE '%apex-domain%'    OR lower(url_path) LIKE '%domain-verification%'
      OR lower(url_path) LIKE '%verify-your-domain%' OR lower(url_path) LIKE '%nameserver%'
    )
    -- drop obvious community/forum hosts up front
    AND url_host_name NOT LIKE 'answers.%'
    AND url_host_name NOT LIKE 'forum.%'
    AND url_host_name NOT LIKE 'community.%'
) TO 'cc_customdomain_urls.csv' (HEADER, DELIMITER ',');
```

- **Partition pruning** on `crawl=`/`subset=` is essential — it limits the scan to one
  crawl. Columnar read touches only the few columns referenced, so scan volume is small.
- Loop the query over every 2026 crawl id (`CC-MAIN-2026-30`, `-25`, `-21`, …) and
  `UNION`/dedup to cover the year. New products appear crawl-to-crawl.
- Refine `url_path LIKE` patterns after eyeballing a sample; add `url_host_name LIKE`
  filters (`help.%`, `docs.%`, `support.%`, `%zendesk.com`, `%intercom.help`, …) if you
  want to bias toward help centers specifically.

## Option B (enterprise scale) — Amazon Athena

Same data, SQL engine managed by AWS. One-time table setup, then query. Athena bills
~$5/TB scanned; with partition pruning + columnar reads a single-crawl query is typically
**well under $1**.

```sql
-- one-time
CREATE DATABASE ccindex;
CREATE EXTERNAL TABLE ccindex.ccindex (
  url_surtkey string, url string, url_host_name string, url_host_tld string,
  url_path string, fetch_status smallint, content_mime_type string,
  content_languages string, warc_filename string, warc_record_offset int, warc_record_length int
)
PARTITIONED BY (crawl string, subset string)
STORED AS parquet
LOCATION 's3://commoncrawl/cc-index/table/cc-main/warc/';
MSCK REPAIR TABLE ccindex.ccindex;   -- discover partitions (or ALTER TABLE ADD PARTITION for one crawl)

-- query (same WHERE clause as Option A)
SELECT url, url_host_name, url_path, content_languages
FROM ccindex.ccindex
WHERE crawl = 'CC-MAIN-2026-30' AND subset = 'warc' AND fetch_status = 200
  AND ( lower(url_path) LIKE '%custom-domain%' OR lower(url_path) LIKE '%cname%'
        OR lower(url_path) LIKE '%connect-a-custom-domain%' OR lower(url_path) LIKE '%domain-verification%'
        /* ...same patterns... */ );
```

## Option C (this session's fallback) — CDX API, client-side filtered

What `cc_harvest.py` already does, and all that's possible without S3/Athena egress:
- `matchType=host` for every host you know → recovers its custom-domain docs even when the
  site has **no sitemap** (fixed the render.com / okta / github gaps).
- `matchType=domain` for the canonical help platforms (`intercom.help`, `readme.io`,
  `gitbook.io`, `document360.io`, `freshdesk.com`, …) → discovers custom-domain articles
  across **all tenants** of that platform.
- Proxy-safe pattern that matters: request only `fl=url,status,mime`, paginate with
  `showNumPages` → `&page=N`, retry with backoff. Server-side `filter=` is unreliable
  through a relay; filter client-side.

---

## How the methods stack (coverage vs. cost)

| Method | Finds custom-domained help centers? | SERP quota | Infra needed | Ceiling |
|---|---|---|---|---|
| SERP seed (SerpAPI) | via organic ranking only | yes (250/mo) | none | discovery of *hosts* |
| Sitemap / llms.txt per host | n/a (needs host first) | 0 | none | all docs on a known host |
| CDX host-mode | n/a (needs host first) | 0 | none | known host, even w/o sitemap |
| CDX domain-mode | only `*.platform.com` tenants | 0 | none | platform-hosted tenants |
| **Columnar (DuckDB/Athena)** | **yes — scans every host** | **0** | S3 egress (+AWS for Athena) | **the whole indexed web** |

**Pipeline:** columnar index = the spine (find the URLs across all hosts) → dedup/roll-up
to product → cheap LLM classifier for the structured fields. SERP + sitemaps + CDX become
supplements that catch what the latest crawl missed.
