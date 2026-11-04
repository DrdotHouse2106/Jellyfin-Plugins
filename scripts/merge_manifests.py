"""
Führt die Repository-Dateien (manifest.json) mehrerer Jellyfin-Plugins zu einer
gemeinsamen manifest.json zusammen.

- Quellen stehen in sources.json.
- Ist eine Quelle nicht erreichbar oder ungültig, behalten ihre Plugins den Stand der
  bestehenden manifest.json – so verschwindet nie ein Plugin, und die übrigen Quellen
  werden trotzdem aktualisiert. Der Fehler erscheint als Warnung im Actions-Lauf.
- Neue Versionen (noch nicht mit gleicher Prüfsumme im Katalog) werden heruntergeladen
  und ihre MD5-Prüfsumme kontrolliert; stimmt sie nicht, gilt die Quelle als fehlerhaft.
- Jede Quelle nennt in sources.json die GUIDs, die sie liefern darf ("guids"); eine GUID
  gehört genau einer Quelle. Fremde GUIDs werden abgelehnt – so kann ein anderes Repository
  keine Versionen für ein fremdes Plugin unterschieben.
- Pakete (sourceUrl) müssen aus dem Repository der Quelle selbst kommen.
- Kommt ein Plugin (gleiche GUID) in mehreren Quellen vor, werden die Versionen vereint.
- overrides.json überschreibt einzelne Felder (z. B. Logo, Beschreibung) dauerhaft.

Aufruf: python3 scripts/merge_manifests.py
"""

import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES_FILE = ROOT / "sources.json"
OVERRIDES_FILE = ROOT / "overrides.json"
OUTPUT_FILE = ROOT / "manifest.json"
REQUIRED_PLUGIN_KEYS = ("guid", "name", "versions")
REQUIRED_VERSION_KEYS = ("version", "targetAbi", "sourceUrl", "checksum")
# Nur Pakete aus den eigenen Repositories in den Katalog übernehmen
ALLOWED_SOURCE_PREFIXES = (
    "https://github.com/DrdotHouse2106/",
    "https://raw.githubusercontent.com/DrdotHouse2106/",
)


def version_key(entry):
    """Sortierschlüssel für Versionen wie 12.2.0.0 (neueste zuerst)."""
    return tuple(int(part) if part.isdigit() else 0 for part in entry["version"].split("."))


def download(url):
    # Zeitstempel anhängen: raw.githubusercontent.com hält Dateien sonst bis zu 5 Minuten im Cache.
    separator = "&" if "?" in url else "?"
    fresh_url = f"{url}{separator}t={int(time.time())}"
    request = urllib.request.Request(
        fresh_url, headers={"User-Agent": "jellyfin-plugins-merger", "Cache-Control": "no-cache"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def fetch(url):
    return json.loads(download(url))


def check_new_packages(plugins, known, url):
    """Prüft die MD5 aller Versionen, die noch nicht mit derselben Prüfsumme im Katalog stehen."""
    for plugin in plugins:
        for version in plugin["versions"]:
            checksum = str(version["checksum"]).lower()
            if (plugin["guid"].lower(), version["version"], checksum) in known:
                continue
            actual = hashlib.md5(download(version["sourceUrl"])).hexdigest()
            if actual != checksum:
                raise ValueError(
                    f"{url}: {plugin['name']} {version['version']}: MD5 {actual} statt {checksum}"
                )


def repo_prefixes(url):
    """Erlaubte Paket-Adressen einer Quelle: github.com bzw. raw.githubusercontent.com desselben Repositorys."""
    parts = url.split("/")
    if len(parts) < 5 or parts[2] not in ("raw.githubusercontent.com", "github.com"):
        raise ValueError(f"{url}: Quelle muss auf GitHub liegen")
    owner, repo = parts[3].lower(), parts[4].lower()
    return (f"https://github.com/{owner}/{repo}/", f"https://raw.githubusercontent.com/{owner}/{repo}/")


def load_sources():
    """sources.json lesen: Einträge {"url", "guids"}; jede GUID darf nur einer Quelle gehören."""
    entries = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))["sources"]
    sources, owner = [], {}
    for entry in entries:
        if isinstance(entry, str):
            raise ValueError(f"{entry}: bitte als {{\"url\", \"guids\"}} eintragen")
        guids = {g.lower() for g in entry.get("guids", [])}
        if not guids:
            raise ValueError(f"{entry['url']}: keine GUIDs angegeben")
        for guid in guids:
            if guid in owner:
                raise ValueError(f"GUID {guid} ist {owner[guid]} und {entry['url']} zugeordnet")
            owner[guid] = entry["url"]
        sources.append((entry["url"], guids))
    return sources


def validate(plugins, url, guids=None):
    if not isinstance(plugins, list):
        raise ValueError(f"{url}: erwartet wird eine Liste von Plugins")
    for plugin in plugins:
        missing = [key for key in REQUIRED_PLUGIN_KEYS if key not in plugin]
        if missing:
            raise ValueError(f"{url}: Plugin ohne {', '.join(missing)}")
        for version in plugin["versions"]:
            missing = [key for key in REQUIRED_VERSION_KEYS if key not in version]
            if missing:
                raise ValueError(f"{url}: {plugin['name']} {version.get('version')} ohne {', '.join(missing)}")
            if not str(version["sourceUrl"]).startswith(ALLOWED_SOURCE_PREFIXES):
                raise ValueError(f"{url}: {plugin['name']} {version['version']}: sourceUrl außerhalb von DrdotHouse2106 ({version['sourceUrl']})")
            if not str(version["sourceUrl"]).lower().startswith(repo_prefixes(url)):
                raise ValueError(f"{url}: {plugin['name']} {version['version']}: Paket nicht aus dem Repository der Quelle ({version['sourceUrl']})")
        if guids is not None and plugin["guid"].lower() not in guids:
            raise ValueError(f"{url}: {plugin['name']} ({plugin['guid']}) gehört laut sources.json nicht zu dieser Quelle")


def main():
    sources = load_sources()
    previous = json.loads(OUTPUT_FILE.read_text(encoding="utf-8")) if OUTPUT_FILE.exists() else []
    known = {
        (plugin["guid"].lower(), version["version"], str(version["checksum"]).lower())
        for plugin in previous
        for version in plugin.get("versions", [])
    }
    merged = {}
    failed = False

    for url, guids in sources:
        try:
            plugins = fetch(url)
            validate(plugins, url, guids)
            check_new_packages(plugins, known, url)
        except Exception as error:  # noqa: BLE001 – jede Störung zählt als fehlerhafte Quelle
            # GitHub zeigt ::warning:: als Hinweis am Lauf an
            print(f"::warning::Quelle übersprungen, bisheriger Stand bleibt: {url}: {error}", file=sys.stderr)
            failed = True
            continue

        for plugin in plugins:
            guid = plugin["guid"].lower()
            if guid not in merged:
                merged[guid] = {**plugin, "versions": list(plugin["versions"])}
            else:
                # Gleiche GUID zweimal in derselben Quelle: Versionen vereinen (nicht „known“ überschreiben)
                seen = {v["version"] for v in merged[guid]["versions"]}
                merged[guid]["versions"] += [v for v in plugin["versions"] if v["version"] not in seen]
        print(f"{url}: {', '.join(p['name'] for p in plugins)}")

    if failed:
        # Plugins der übersprungenen Quellen mit ihrem bisherigen Stand behalten
        for plugin in previous:
            guid = plugin["guid"].lower()
            if guid not in merged:
                merged[guid] = plugin

    overrides = {}
    if OVERRIDES_FILE.exists():
        overrides = {
            guid.lower(): fields
            for guid, fields in json.loads(OVERRIDES_FILE.read_text(encoding="utf-8")).items()
            if not guid.startswith("_")
        }
    for guid, fields in overrides.items():
        if guid in merged:
            merged[guid].update({key: value for key, value in fields.items() if key != "versions"})

    result = sorted(merged.values(), key=lambda p: p["name"].lower())
    for plugin in result:
        plugin["versions"].sort(key=version_key, reverse=True)

    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if OUTPUT_FILE.exists() and OUTPUT_FILE.read_text(encoding="utf-8") == text:
        print("manifest.json ist bereits aktuell.")
    else:
        OUTPUT_FILE.write_text(text, encoding="utf-8")
        print(f"manifest.json aktualisiert ({len(result)} Plugins).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
