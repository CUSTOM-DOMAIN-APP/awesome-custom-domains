#!/usr/bin/env python3
"""Stage 3 - Common Crawl harvest (zero SERP quota), then clean + write directory.
 - domain-mode: enumerate custom-domain docs across ALL tenants of a help platform
 - host-mode  : recover docs for a known host even when it has no sitemap
Proxy-safe: fl=url,status,mime + page-by-page pagination + retry/backoff.
For the true web-scale path (scan EVERY host, not just platform tenants) use the
columnar index instead - see ../common-crawl-scale-recipe.md.

Env:
  DATA_DIR   (optional)  default ./data
  CC_INDEX   (optional)  crawl id, default latest-known
  CA_BUNDLE  (optional)  extra CA file
  CC_BUDGET  (optional)  wall-clock seconds, default 540
IO: reads DATA_DIR/expanded.json -> writes DATA_DIR/full.json and ./directory.csv
"""
import os, ssl, json, re, time, csv, urllib.request, urllib.parse
from collections import Counter

START=time.time(); BUDGET=float(os.environ.get("CC_BUDGET","540")); DEADLINE=START+BUDGET
def left(): return DEADLINE-time.time()
DATA=os.environ.get("DATA_DIR","data")
IDX=os.environ.get("CC_INDEX","CC-MAIN-2026-30")
BASE=f"https://index.commoncrawl.org/{IDX}-index"
ctx=ssl.create_default_context()
ca=os.environ.get("CA_BUNDLE")
if ca and os.path.exists(ca):
    try: ctx.load_verify_locations(ca)
    except Exception: pass
opener=urllib.request.build_opener(urllib.request.ProxyHandler(urllib.request.getproxies()),
    urllib.request.HTTPSHandler(context=ctx))
UA={"User-Agent":"saas-docs-directory/1.0 (Common Crawl harvester)"}

def cdx(params, retries=3):
    url=BASE+"?"+urllib.parse.urlencode(params)
    for i in range(retries):
        if left()<15: return ""
        try:
            with opener.open(urllib.request.Request(url, headers=UA), timeout=45) as r:
                return r.read().decode("utf-8","replace")
        except Exception: time.sleep((i+1)*2)
    return ""
def num_pages(u,m):
    try: return int(json.loads(cdx({"url":u,"matchType":m,"showNumPages":"true","output":"json"})).get("pages",0))
    except Exception: return 0
def records(u,m,max_pages):
    for p in range(min(num_pages(u,m),max_pages)):
        for ln in cdx({"url":u,"matchType":m,"fl":"url,status,mime","page":str(p),"output":"json"}).splitlines():
            ln=ln.strip()
            if ln.startswith("{"):
                try: yield json.loads(ln)
                except Exception: pass
        time.sleep(0.3)

KW=re.compile(r"(custom[-_]?domain|custom[-_]?hostname|connect[-_]?(a[-_]?|your[-_]?)?domain|"
    r"add[-_]?(a[-_]?)?(custom[-_]?)?domain|your[-_]?own[-_]?domain|bring[-_]?your[-_]?own[-_]?domain|"
    r"cname[-_]?record|cname|point[-_]?(your[-_]?)?domain|verify[-_]?(your[-_]?)?domain|"
    r"domain[-_]?verification|vanity[-_]?domain|apex[-_]?domain|nameserver|name[-_]?server)", re.I)
NOISE=re.compile(r"/(t|topic|questions|discussions|posts|thread)/", re.I)
NOISE_HOST=re.compile(r"(^|\.)(answers|forum|forums|community|discuss|repost|ideas|status)\.", re.I)
PLATFORM_TLD={"zendesk.com","freshdesk.com","gitbook.io","readme.io","readme.com","document360.io",
    "helpscoutdocs.com","notion.site","helpjuice.com","zohodesk.com","mintlify.app"}
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
    for sig,name in [("zendesk.com","Zendesk"),("/hc/","Zendesk"),("intercom.help","Intercom"),("gitbook.io","GitBook"),
        ("readme.io","ReadMe"),("mintlify","Mintlify"),("freshdesk.com","Freshdesk"),("helpscout","HelpScout"),
        ("document360","Document360"),("notion.site","Notion"),("helpjuice","Helpjuice")]:
        if sig in s: return name
    return ""
def ok(rec):
    if rec.get("status")!="200" or "html" not in rec.get("mime",""): return None
    u=rec.get("url","")
    if not u or u.endswith(".md") or not KW.search(u) or NOISE.search(u): return None
    return u.split("?")[0].split("#")[0].rstrip("/")

rows=json.load(open(os.path.join(DATA,"expanded.json")))
seen={re.sub(r"[#?].*$","",r["doc_url"]).rstrip("/") for r in rows}
def add(u,src):
    if u in seen: return False
    seen.add(u)
    rows.append({"product":product_of(u),"vendor_host":reg_domain(host_of(u)),
        "doc_url":u,"doc_title":"","doc_platform":platform(u),"discovery_source":src}); return True

PLATFORMS=["intercom.help","readme.io","gitbook.io","document360.io","mintlify.app",
           "zendesk.com","freshdesk.com","helpscoutdocs.com","helpjuice.com"]
cc=0
print("== CC domain-mode (cross-tenant discovery) ==", flush=True)
for d in PLATFORMS:
    if left()<60: print("  [budget] stop"); break
    g=sum(add(u,"commoncrawl-domain(free)") for u in (ok(r) for r in records(d,"domain",8)) if u)
    print(f"  {d:20} +{g}", flush=True); cc+=g

# final clean + write
final=[]; fseen=set()
for r in sorted(rows,key=lambda x:(x["product"],x["doc_url"])):
    if NOISE_HOST.search(host_of(r["doc_url"])) or NOISE.search(urllib.parse.urlparse(r["doc_url"]).path): continue
    if r["discovery_source"]!="serp" and not KW.search(r["doc_url"]): continue
    k=re.sub(r"[#?].*$","",r["doc_url"]).rstrip("/")
    if k in fseen: continue
    fseen.add(k); final.append(r)

cols=["product","vendor_host","doc_url","doc_title","doc_platform","discovery_source"]
with open("directory.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); [w.writerow(r) for r in final]
json.dump(final, open(os.path.join(DATA,"full.json"),"w"), indent=2)
print(f"\nCC added: {cc} | final rows: {len(final)} | products: {len({r['product'] for r in final})}")
print("by source:", dict(Counter(r['discovery_source'] for r in final)))
