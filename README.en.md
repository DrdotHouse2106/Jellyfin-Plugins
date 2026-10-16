# Jellyfin-Plugins

*[Deutsche Version](README.md)*

Combined plugin repository for all Jellyfin plugins by DrdotHouse2106 – add **one** URL to Jellyfin instead of one per plugin.

## Plugins

- **Jellyfin Remote** – smartphone remote control and library browser at `/remote/` ([source](https://github.com/DrdotHouse2106/Jellyfin-Remote))
- **Local Recommendations** – personal recommendations based on local watch history ([source](https://github.com/DrdotHouse2106/Lokal-Vorschlag-Jellyfin))

## Installation

In the Jellyfin dashboard go to **Plugins → Repositories → "+"** and add

```
https://raw.githubusercontent.com/DrdotHouse2106/Jellyfin-Plugins/main/manifest.json
```

then install the plugins from the catalog and restart Jellyfin.

## How it works

Each plugin keeps its own repository file. The GitHub Action `update-manifest.yml` merges them into `manifest.json` every 15 minutes (or on demand via *Run workflow*). If a source is unreachable or invalid, `manifest.json` is left untouched. To add a plugin, append its repository-file URL to `sources.json`.
