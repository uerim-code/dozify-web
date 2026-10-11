#!/usr/bin/env python3
"""Tell Bing, Yandex and the other IndexNow engines about every URL in sitemap.xml.

  python3 tools/indexnow.py            # all sitemap URLs
  python3 tools/indexnow.py URL ...    # just these
The key file (<key>.txt at the site root) proves the site is ours; no account
or login is needed. Run after a deploy that adds or changes pages."""
import glob, json, pathlib, re, sys, urllib.request
ROOT = pathlib.Path(__file__).resolve().parent.parent
key = next(p.stem for p in ROOT.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", p.stem))
urls = sys.argv[1:] or re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
urls = list(dict.fromkeys(urls))
for i in range(0, len(urls), 10000):
    body = json.dumps({"host": "dozify.app", "key": key, "keyLocation": f"https://dozify.app/{key}.txt",
                       "urlList": urls[i:i + 10000]}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        r = urllib.request.urlopen(req); print(f"{len(urls[i:i+10000])} URLs → HTTP {r.status}")
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()[:300]}")
