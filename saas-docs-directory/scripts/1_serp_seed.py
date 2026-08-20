#!/usr/bin/env python3
"""Stage 1 - SERP seed.
Discover custom-domain / DNS setup help pages (and, more importantly, the HOSTS
that hold them) via a SERP API. Uses SerpAPI by default.

Env:
  SERP_KEY   (required)  your SerpAPI key
  DATA_DIR   (optional)  output dir, default ./data
Output: DATA_DIR/seed.json  (list of {product, vendor_host, doc_url, doc_title,
                                       doc_platform, discovery_source})

Note: exact-phrase dorks return ~10 results each, so spend searches on breadth of
PHRASING and let stages 2-3 (sitemap + Common Crawl) do the exhaustive expansion.
"""
import os, json, re, time, urllib.request, urllib.parse

KEY = os.environ.get("SERP_KEY")
if not KEY: raise SystemExit("set SERP_KEY (SerpAPI key)")
DATA = os.environ.get("DATA_DIR", "data"); os.makedirs(DATA, exist_ok=True)

QUERIES = [
    '"connect a custom domain"',
    '"add a custom domain" CNAME',
    '"point your domain" "CNAME record"',
    '"set up your custom domain" (SSL OR HTTPS)',
    'intitle:"custom domain" (connect OR setup OR configure) (DNS OR CNAME)',
    '"custom domain" "TXT record" (verify OR verification) inurl:help',
    '"use your own domain" (CNAME OR "A record") inurl:docs',
    '"bring your own domain" CNAME (inurl:help OR inurl:docs)',
]
PLATFORM_TLD = {"zendesk.com","freshdesk.com","gitbook.io","readme.io","readme.com",
    "document360.io","helpscoutdocs.com","notion.site","helpjuice.com","zohodesk.com","mintlify.app"}
INFRA = ("customdomain.ai","approximated.app","entri.com","saascustomdomains.com","domainee.dev")

def host_of(u): return urllib.parse.urlparse(u).netloc.lower()
def reg_domain(h):
    p=h.split("."); two={"co.uk","com.au","co.jp","com.br","co.in","co.nz","com.mx","co.za"}
    if len(p)>=3 and ".".join(p[-2:]) in two: return ".".join(p[-3:])
    return ".".join(p[-2:]) if len(p)>=2 else h
def product_of(u):
    h=host_of(u); rd=reg_domain(h); p=h.split(".")
    if "intercom.help" in h:
        seg=[x for x in urllib.parse.urlparse(u).path.split("/") if x]; return seg[0] if seg else "intercom"
    if rd in PLATFORM_TLD and len(p)>=3: return p[0]
    return rd.split(".")[0]
def platform(u):
    s=u.lower()
    for sig,name in [("zendesk.com","Zendesk"),("/hc/","Zendesk"),("intercom.help","Intercom"),
        ("gitbook.io","GitBook"),("readme.io","ReadMe"),("mintlify","Mintlify"),("freshdesk.com","Freshdesk"),
        ("helpscout","HelpScout"),("document360","Document360"),("notion.site","Notion"),("helpjuice","Helpjuice")]:
        if sig in s: return name
    return ""
def relevant(u,t):
    s=(u+" "+(t or "")).lower()
    return any(k in s for k in ["custom domain","custom-domain","cname","nameserver","point your domain",
        "connect your domain","bring your own domain","verify your domain","dns record","apex domain","your own domain"])

rows, seen = [], set()
for q in QUERIES:
    url="https://serpapi.com/search.json?"+urllib.parse.urlencode(
        {"engine":"google","q":q,"num":"100","hl":"en","gl":"us","api_key":KEY})
    try:
        with urllib.request.urlopen(url, timeout=60) as r: d=json.load(r)
    except Exception as e:
        print(f"[serp FAIL] {q[:40]!r}: {e}"); continue
    for it in d.get("organic_results",[]) or []:
        link=it.get("link") or ""; title=it.get("title") or ""
        if not link or any(x in host_of(link) for x in INFRA) or not relevant(link,title): continue
        key=re.sub(r"[#?].*$","",link).rstrip("/")
        if key in seen: continue
        seen.add(key)
        rows.append({"product":product_of(link),"vendor_host":reg_domain(host_of(link)),
            "doc_url":link,"doc_title":title,"doc_platform":platform(link),"discovery_source":"serp"})
    print(f"[serp ok] {q[:46]!r}")
    time.sleep(0.5)

json.dump(rows, open(os.path.join(DATA,"seed.json"),"w"), indent=2)
print(f"seed rows: {len(rows)} -> {DATA}/seed.json")
