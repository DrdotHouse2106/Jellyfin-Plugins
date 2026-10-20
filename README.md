# Jellyfin-Plugins

[![Spendier mir einen Kaffee](https://img.shields.io/badge/☕_Spendier_mir_einen_Kaffee-PayPal-0070ba?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/DrdotHouse)

*[English version](README.en.md)*

Gemeinsames Plugin-Repository für alle Jellyfin-Plugins von DrdotHouse2106. Statt jedes Plugin-Repository einzeln einzutragen, genügt in Jellyfin **eine** Adresse.

## Enthaltene Plugins

| Plugin | Beschreibung | Quelle |
| --- | --- | --- |
| **Jellyfin Remote** | Fernbedienung und Mediathek-Browser für Smartphones unter `/remote/` | [Jellyfin-Remote](https://github.com/DrdotHouse2106/Jellyfin-Remote) |
| **Quallenkino** (Quallenkinoplugin für Jellyfin, früher Local Recommendations) | Persönliche Empfehlungen, Live-TV mit eigenem EPG-Anbieter, Erinnerungen, Profile und Oberfläche im Quallenkino-Stil | [Lokal-Vorschlag-Jellyfin](https://github.com/DrdotHouse2106/Lokal-Vorschlag-Jellyfin) |

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

## Logo und Beschreibung anpassen

In [`overrides.json`](overrides.json) lassen sich einzelne Felder eines Plugins (Schlüssel: GUID) dauerhaft überschreiben, z. B. `imageUrl`, `description` oder `overview`. Die Werte werden bei jedem Zusammenführen angewendet. Logos liegen im Ordner [`images/`](images/).

## Neues Plugin hinzufügen

Die Adresse der Repository-Datei des Plugins in [`sources.json`](sources.json) ergänzen und committen – die Action läuft dann automatisch.

Lokal testen:

```bash
python3 scripts/merge_manifests.py
```

## Unterstützen

Die Entwicklung kostet Zeit und Geld (Server, Testgeräte, KI-Werkzeuge). Wenn dir das Projekt gefällt, freue ich mich über eine kleine Spende:

[![Spenden via PayPal](https://img.shields.io/badge/Spenden-PayPal-0070ba?logo=paypal&logoColor=white)](https://paypal.me/DrdotHouse)

### 🎮 Auch eine Zocker-Ader?

Dann ist vielleicht mein anderes Projekt genau das Richtige für dich: **[ZockerDB](https://zockerdb.de)** –
deine Spielesammlung an einem Platz. Spiele, Konsolen und Zubehör erfassen (auch per Barcode-Scan mit
dem Handy), bewerten und verwalten, mit Preisverlauf, Editionen und PAL/USK-Angaben. Direkt auf
[zockerdb.de](https://zockerdb.de) nutzen oder als [ZockerDB Basis](https://github.com/DrdotHouse2106/ZockerDBBasis) auf dem eigenen Server hosten.

## Lizenz

[GPL-3.0](LICENSE)
