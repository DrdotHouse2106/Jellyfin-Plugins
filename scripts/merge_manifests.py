"""
Führt die Repository-Dateien (manifest.json) mehrerer Jellyfin-Plugins zu einer
gemeinsamen manifest.json zusammen.

- Quellen stehen in sources.json.
- Ist eine Quelle nicht erreichbar oder ungültig, bricht das Skript ab und
  lässt die bestehende manifest.json unverändert – so verschwindet nie ein Plugin.
- Kommt ein Plugin (gleiche GUID) in mehreren Quellen vor, werden die Versionen vereint.

Aufruf: python3 scripts/merge_manifests.py
"""

import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES_FILE = ROOT / "sources.json"
OUTPUT_FILE = ROOT / "manifest.json"
REQUIRED_PLUGIN_KEYS = ("guid", "name", "versions")
REQUIRED_VERSION_KEYS = ("version", "targetAbi", "sourceUrl", "checksum")


def version_key(entry):
    """Sortierschlüssel für Versionen wie 12.2.0.0 (neueste zuerst)."""
    return tuple(int(part) if part.isdigit() else 0 for part in entry["version"].split("."))


def fetch(url):
    # Zeitstempel anhängen: raw.githubusercontent.com hält Dateien sonst bis zu 5 Minuten im Cache.
    separator = "&" if "?" in url else "?"
    fresh_url = f"{url}{separator}t={int(time.time())}"
    request = urllib.request.Request(
        fresh_url, headers={"User-Agent": "jellyfin-plugins-merger", "Cache-Control": "no-cache"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def validate(plugins, url):
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


def main():
    sources = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))["sources"]
    merged = {}

    for url in sources:
        try:
            plugins = fetch(url)
            validate(plugins, url)
        except Exception as error:  # noqa: BLE001 – jede Störung soll den Lauf abbrechen
            print(f"FEHLER bei {url}: {error}", file=sys.stderr)
            return 1

        for plugin in plugins:
            guid = plugin["guid"].lower()
            if guid not in merged:
                merged[guid] = {**plugin, "versions": list(plugin["versions"])}
            else:
                known = {v["version"] for v in merged[guid]["versions"]}
                merged[guid]["versions"] += [v for v in plugin["versions"] if v["version"] not in known]
        print(f"{url}: {', '.join(p['name'] for p in plugins)}")

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
