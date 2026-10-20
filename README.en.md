# Jellyfin-Plugins

[![Buy me a coffee](https://img.shields.io/badge/☕_Buy_me_a_coffee-PayPal-0070ba?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/DrdotHouse)

*[Deutsche Version](README.md)*

Combined plugin repository for all Jellyfin plugins by DrdotHouse2106 – add **one** URL to Jellyfin instead of one per plugin.

## Plugins

- **Jellyfin Remote** – smartphone remote control and library browser at `/remote/` ([source](https://github.com/DrdotHouse2106/Jellyfin-Remote))
- **Quallenkino** (Quallenkinoplugin für Jellyfin, formerly Local Recommendations) – personal recommendations, live TV with own guide provider, reminders, profiles and a Quallenkino-style UI ([source](https://github.com/DrdotHouse2106/Lokal-Vorschlag-Jellyfin))

## Installation

In the Jellyfin dashboard go to **Plugins → Repositories → "+"** and add

```
https://raw.githubusercontent.com/DrdotHouse2106/Jellyfin-Plugins/main/manifest.json
```

then install the plugins from the catalog and restart Jellyfin.

## How it works

Each plugin keeps its own repository file. The GitHub Action `update-manifest.yml` merges them into `manifest.json` every 15 minutes (or on demand via *Run workflow*). If a source is unreachable or invalid, `manifest.json` is left untouched. To add a plugin, append its repository-file URL to `sources.json`. Single fields such as logo or description can be overridden permanently in `overrides.json` (keyed by plugin GUID).

## Support the project

Development costs time and money (servers, test devices, AI tools). If you like the project, a small donation is very welcome:

[![Donate via PayPal](https://img.shields.io/badge/Donate-PayPal-0070ba?logo=paypal&logoColor=white)](https://paypal.me/DrdotHouse)

### 🎮 Got a gamer streak too?

Then my other project might be just right for you: **[ZockerDB](https://zockerdb.de)** – your game
collection in one place. Track games, consoles and accessories (including barcode scanning with your
phone), rate and manage them, with price history, editions and PAL/USK details. Use it directly at
[zockerdb.de](https://zockerdb.de) or self-host [ZockerDB Basis](https://github.com/DrdotHouse2106/ZockerDBBasis) on your own server.

## License

[GPL-3.0](LICENSE)
