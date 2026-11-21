#!/usr/bin/env python3
"""ينشئ ملف source.json من آخر إصدارات GitHub التي تحتوي على ملفات IPA."""
import json, os, plistlib, re, sys, tempfile, urllib.request, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = "https://raw.githubusercontent.com/za7ef/apps-source/main/"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
MAX_VERSIONS = 5


def api(path):
    req = urllib.request.Request("https://api.github.com/" + path,
                                 headers={"Accept": "application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def read_info(url):
    with tempfile.NamedTemporaryFile(suffix=".ipa") as f:
        with urllib.request.urlopen(url, timeout=600) as r:
            while True:
                b = r.read(1 << 20)
                if not b:
                    break
                f.write(b)
        f.flush()
        with zipfile.ZipFile(f.name) as z:
            name = next(n for n in z.namelist()
                        if re.fullmatch(r"Payload/[^/]+\.app/Info\.plist", n))
            return plistlib.loads(z.read(name))


def main():
    cfg = json.load(open(os.path.join(ROOT, "apps.json"), encoding="utf-8"))
    old_path = os.path.join(ROOT, "source.json")
    old = {}
    if os.path.exists(old_path):
        for a in json.load(open(old_path, encoding="utf-8")).get("apps", []):
            old[a["bundleIdentifier"]] = a
    known = {v["downloadURL"]: v for a in old.values() for v in a.get("versions", [])}

    apps = []
    for app in cfg["apps"]:
        versions = []
        for rel in api(f"repos/{app['repo']}/releases?per_page=30"):
            if rel["draft"] or (rel["prerelease"] and not app["includePrereleases"]):
                continue
            ipa = next((a for a in rel["assets"] if a["name"].lower().endswith(".ipa")), None)
            if not ipa:
                continue
            url = ipa["browser_download_url"]
            if url in known:
                v = known[url]
            else:
                info = read_info(url)
                v = {
                    "bundleIdentifier": info["CFBundleIdentifier"],
                    "version": info.get("CFBundleShortVersionString", "1.0"),
                    "buildVersion": str(info.get("CFBundleVersion", "")),
                    "date": rel["published_at"],
                    "localizedDescription": (rel.get("body") or rel["name"] or rel["tag_name"]).strip()[:2000],
                    "downloadURL": url,
                    "size": ipa["size"],
                    "minOSVersion": info.get("MinimumOSVersion", "15.0"),
                }
            versions.append(v)
            if len(versions) >= MAX_VERSIONS:
                break
        if not versions:
            print("لا توجد ملفات IPA في", app["repo"], file=sys.stderr)
            continue
        bundle = versions[0]["bundleIdentifier"]
        versions = [v for v in versions if v["bundleIdentifier"] == bundle]
        latest = versions[0]
        apps.append({
            "name": app["name"],
            "bundleIdentifier": bundle,
            "developerName": "za7ef",
            "subtitle": app["subtitle"],
            "localizedDescription": app["localizedDescription"],
            "iconURL": RAW + app["icon"],
            "tintColor": app["tintColor"],
            # حقول مسطّحة للتوافق مع الصيغ القديمة (ESign/Feather)
            "version": latest["version"],
            "versionDate": latest["date"],
            "versionDescription": latest["localizedDescription"],
            "downloadURL": latest["downloadURL"],
            "size": latest["size"],
            "versions": versions,
            "appPermissions": {},
        })

    src = {k: cfg[k] for k in ("name", "identifier", "subtitle", "description",
                                "website", "iconURL", "tintColor")}
    src["sourceURL"] = RAW + "source.json"
    src["apps"] = apps
    src["news"] = []
    with open(old_path, "w", encoding="utf-8") as f:
        json.dump(src, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("تم تحديث", len(apps), "تطبيقات")


if __name__ == "__main__":
    main()
