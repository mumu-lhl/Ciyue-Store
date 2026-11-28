# Ciyue-Store

[English](README.md) | [简体中文](README.zh.md)

Official resource catalog for [Ciyue](https://github.com/mumu-lhl/Ciyue), providing legally licensed dictionaries, Hunspell morphological data, and pronunciation audio packs.

## Catalog Format (`catalog.yaml`)

`catalog.yaml` is a YAML document with the following top-level structure:

```yaml
schemaVersion: 1
name: Ciyue Official  # Optional; display name for this catalog source
items:
  - ...
```

### Item Fields

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `id` | string | Yes | Unique lowercase slug (`^[a-z0-9][a-z0-9_-]*$`). |
| `type` | string | Yes | Resource category: `dictionary`, `hunspell`, or `audio`. |
| `name` | string | Yes | Display name shown in the store. |
| `description` | string | No | Short description (supports YAML multiline `\|`). |
| `translations` | object | No | Optional per-language overrides for `name`/`description`. Keys are base or region language tags (e.g. `en`, `zh`, `zh_TW`). Missing fields fall back to the item's default `name`/`description`. |
| `author` | string | Yes | Author or maintainer name. |
| `license` | string | Yes | License identifier (e.g. `MIT`, `GPL-3.0`, `CC-BY-SA-4.0`). |
| `sourceUrl` | string | Yes | Upstream homepage or repository URL (`http://` or `https://`). |
| `languages` | list[string] | No | ISO language codes (e.g. `["en", "zh"]`, `["ja"]`). |
| `format` | string | Yes | `mdx`, `stardict`, `zim`, `hunspell`, `audio_mdd`, `audio_zip`, or `audio_zips`. |
| `extract` | bool | No | Whether downloaded `.zip` files should be extracted. Defaults to `false` (keep `false` for `audio_zip` / `audio_zips` and `hunspell` raw files; set `true` for zipped dictionaries). |
| `source` | object | Yes | Download source configuration (see below). |

### Multilingual metadata

`name` and `description` are the item's default text. Write them in the resource's own language: a Chinese Hunspell uses Chinese, a Japanese Hunspell uses Japanese, an English dictionary uses English, and so on.

Add `translations` for other UI languages:

```yaml
name: 中文简繁/异体字与新字体通查 (Hunspell)
description: 用于中文简繁转换……
translations:
  en:
    name: Chinese Simplified/Traditional & Variant Lookup (Hunspell)
    description: Hunspell morphology data for Chinese script conversion...
  zh_TW:
    name: 中文簡繁/異體字與新字體通查 (Hunspell)
    description: 用於中文簡繁轉換……
```

Ciyue resolves the text in this order:

1. Exact UI language tag (e.g. `zh_TW`, `en_US`)
2. Base language (e.g. `zh`, `en`)
3. The item's default `name` / `description`

There is no forced English fallback. A translation may provide only `name` or only `description`; the missing field falls back to the item's default. `translations` is optional and additive, so `schemaVersion` stays `1`.

### Source Types

#### 1. `github_release`

Downloads matching assets from a GitHub Release (latest release by default, or a specific `tag`):

```yaml
source:
  type: github_release
  repo: owner/repo
  # tag: v1.0.0          # Optional; omit to use the latest release
  assetPattern: "*.zip"  # Supports wildcard patterns, or use `assets: [file.zip]`
```

#### 2. `github_raw`

Downloads specific files directly from a GitHub repository branch:

```yaml
source:
  type: github_raw
  repo: owner/repo
  branch: main           # Optional; defaults to "main"
  files:
    - zh_CN.aff
    - zh_CN.dic
```

#### 3. `direct`

Downloads one or more direct HTTP/HTTPS URLs:

```yaml
source:
  type: direct
  url: https://example.com/en_us.zips
```

Or multiple files with explicit filenames:

```yaml
source:
  type: direct
  files:
    - url: https://example.com/dict.mdx
      filename: dict.mdx
    - url: https://example.com/dict.mdd
      filename: dict.mdd
```

## Branch & Release Workflow

- **`dev`**: Default integration branch for commits and pull requests.
- **`main`**: Production branch consumed by Ciyue clients. Direct pushes to `main` are blocked by branch rulesets; `.github/workflows/sync-main.yml` syncs `dev` to `main` via pull request after all validation checks pass.

## Validation

Using [uv](https://docs.astral.sh/uv/):

```bash
uv run --with pyyaml python scripts/validate_catalog.py catalog.yaml
uv run --with pyyaml python -m unittest discover -s scripts -p "test_*.py" -v
```
