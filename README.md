# Jellyfin-Plugins

*[English version](README.en.md)*

Gemeinsames Plugin-Repository für alle Jellyfin-Plugins von DrdotHouse2106. Statt jedes Plugin-Repository einzeln einzutragen, genügt in Jellyfin **eine** Adresse.

## Enthaltene Plugins

| Plugin | Beschreibung | Quelle |
| --- | --- | --- |
| **Jellyfin Remote** | Fernbedienung und Mediathek-Browser für Smartphones unter `/remote/` | [Jellyfin-Remote](https://github.com/DrdotHouse2106/Jellyfin-Remote) |
| **Local Recommendations** | Persönliche Empfehlungen auf Basis des lokalen Wiedergabeverlaufs | [Lokal-Vorschlag-Jellyfin](https://github.com/DrdotHouse2106/Lokal-Vorschlag-Jellyfin) |

## Installation

1. Im Jellyfin-Dashboard **Plugins → Repositories → „+“** wählen.
2. Name: `DrdotHouse2106`, URL:

   ```
   https://raw.githubusercontent.com/DrdotHouse2106/Jellyfin-Plugins/main/manifest.json
   ```
3. Unter **Plugins → Katalog** die gewünschten Plugins installieren und Jellyfin neu starten.

Hast du bisher die Repositories der einzelnen Plugins eingetragen, kannst du diese danach entfernen – die Plugins und ihre Einstellungen bleiben erhalten, Updates kommen dann über dieses Repository.

## So funktioniert es

- Jedes Plugin pflegt weiterhin seine eigene Repository-Datei in seinem eigenen GitHub-Repository.
- Die GitHub Action [`update-manifest.yml`](.github/workflows/update-manifest.yml) liest diese Dateien **alle 15 Minuten** ein (GitHub kann zeitgesteuerte Läufe verzögern) und fügt sie zu `manifest.json` zusammen. Sofort aktualisieren: **Actions → Manifest aktualisieren → Run workflow**.
- Ist eine Quelle nicht erreichbar oder fehlerhaft, bleibt `manifest.json` unverändert – es verschwindet nie ein Plugin aus dem Katalog.

## Neues Plugin hinzufügen

Die Adresse der Repository-Datei des Plugins in [`sources.json`](sources.json) ergänzen und committen – die Action läuft dann automatisch.

Lokal testen:

```bash
python3 scripts/merge_manifests.py
```
