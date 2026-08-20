#!/usr/bin/env python3
"""Stage 2 - free sitemap expansion (the multiplier).
For every host discovered in stage 1, fetch its sitemap(s) and keep the URLs whose
slug looks like a custom-domain / DNS setup doc. Zero SERP quota.

Env:
  DATA_DIR   (optional)  default ./data
  CA_BUNDLE  (optional)  extra CA file (e.g. a corporate/proxy CA)
IO: reads DATA_DIR/seed.json -> writes DATA_DIR/expanded.json
"""
import os, ssl, json, re, urllib.request, urllib.parse

DATA = os.environ.get("DATA_DIR", "data")
ctx = ssl.create_default_context()
ca = os.environ.get("CA_BUNDLE")
if ca and os.path.exists(ca):
    try: ctx.load_verify_locations(ca)
    except Exception: pass
opener = urllib.request.build_opener(
    urllib.request.ProxyHandler(urllib.request.getproxies()),
    urllib.request.HTTPSHandler(context=ctx))
UA = {"User-Agent":"saas-docs-directory/1.0 (sitemap harvester)"}

KW = re.compile(r"(custom[-_]?domain|connect[-_]?domain|add[-_ ]?(a[-_ ])?domain|cname|nameserver|"
    r"apex|your[-_]?own[-_]?domain|verify[-_]?domain|domain[-_]?(setup|verification|connect)|"
    r"point[-_]?(your[-_]?)?domain|dns[-_]?record|dns[-_]?setting)", re.I)
LOC = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>", re.I)

def fetch(u, t=15):
    with opener.open(urllib.request.Request(u, headers=UA), timeout=t) as r:
        return r.read().decode("utf-8","replace")
def host_of(u): return urllib.parse.urlparse(u).netloc.lower()
def reg_domain(h):
    p=h.split("."); two={"co.uk","com.au","co.jp","com.br","co.in","co.nz","com.mx","co.za"}
    if len(p)>=3 and ".".join(p[-2:]) in two: return ".".join(p[-3:])
    return ".".join(p[-2:]) if len(p)>=2 else h

rows = json.load(open(os.path.join(DATA,"seed.json")))
seen = {re.sub(r"[#?].*$","",r["doc_url"]).rstrip("/") for r in rows}
hosts = sorted({host_of(r["doc_url"]) for r in rows if host_of(r["doc_url"])})
SKIP = ("google.com","youtube.com","facebook.com","reddit.com","amazon.com","microsoft.com","adobe.com")
hosts = [h for h in hosts if not any(s in h for s in SKIP)]

added=0
for h in hosts:
    xml=""
    for c in (f"https://{h}/sitemap.xml", f"https://{h}/sitemap_index.xml", f"https://{h}/sitemap-0.xml"):
        try: xml=fetch(c); break
        except Exception: continue
    if not xml: print(f"[--] {h}: no sitemap"); continue
    locs=LOC.findall(xml)
    nested=[l for l in locs if l.lower().endswith(".xml") or "sitemap" in l.lower()]
    pages=[l for l in locs if l not in nested]
    for nx in nested[:6]:
        try: pages += LOC.findall(fetch(nx))
        except Exception: pass
    kept=0
    for p in pages:
        if not KW.search(p): continue
        key=re.sub(r"[#?].*$","",p).rstrip("/")
        if key in seen: continue
        seen.add(key)
        rows.append({"product":reg_domain(host_of(p)).split(".")[0],"vendor_host":reg_domain(host_of(p)),
            "doc_url":p,"doc_title":"","doc_platform":"","discovery_source":"sitemap(free)"})
        kept+=1; added+=1
    print(f"[ok] {h}: pages={len(pages)} kept={kept}")

json.dump(rows, open(os.path.join(DATA,"expanded.json"),"w"), indent=2)
print(f"sitemap-added: {added} | total rows: {len(rows)} -> {DATA}/expanded.json")
