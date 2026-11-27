#!/usr/bin/env python3
"""Validate Ciyue-Store catalog.yaml structure and metadata requirements."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

VALID_TYPES = {"dictionary", "hunspell", "audio"}
VALID_FORMATS = {
    "mdx",
    "stardict",
    "zim",
    "hunspell",
    "audio_mdd",
    "audio_zip",
    "audio_zips",
}
VALID_SOURCE_TYPES = {"github_release", "github_raw", "direct"}
REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
TRANSLATION_KEY_PATTERN = re.compile(r"^[a-z]{2,8}(?:_[a-z0-9]{1,8})*$")


def _is_non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_http_url(value: Any) -> bool:
    if not _is_non_empty_str(value):
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_catalog_data(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Catalog root must be a YAML mapping."]

    schema_version = data.get("schemaVersion")
    if not isinstance(schema_version, int) or schema_version < 1:
        errors.append("schemaVersion must be a positive integer.")

    items = data.get("items")
    if not isinstance(items, list):
        errors.append("'items' must be a list.")
        return errors

    seen_ids: set[str] = set()
    for idx, item in enumerate(items):
        prefix = f"items[{idx}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: must be a mapping.")
            continue

        item_id = item.get("id")
        if not _is_non_empty_str(item_id) or not ID_PATTERN.match(item_id.strip()):
            errors.append(
                f"{prefix}: 'id' must be a non-empty lowercase slug matching [a-z0-9_-]."
            )
            label = prefix
        else:
            item_id = item_id.strip()
            label = f"items[{idx}] ({item_id})"
            if item_id in seen_ids:
                errors.append(f"{label}: duplicate id '{item_id}'.")
            seen_ids.add(item_id)

        item_type = item.get("type")
        if item_type not in VALID_TYPES:
            errors.append(
                f"{label}: 'type' must be one of {sorted(VALID_TYPES)}, got {item_type!r}."
            )

        for field in ("name", "author", "license"):
            if not _is_non_empty_str(item.get(field)):
                errors.append(f"{label}: '{field}' must be a non-empty string.")

        if not _is_http_url(item.get("sourceUrl")):
            errors.append(
                f"{label}: 'sourceUrl' must be a valid http/https URL."
            )

        item_format = item.get("format")
        if item_format not in VALID_FORMATS:
            errors.append(
                f"{label}: 'format' must be one of {sorted(VALID_FORMATS)}, got {item_format!r}."
            )

        languages = item.get("languages")
        if languages is not None:
            if not isinstance(languages, list) or not all(
                _is_non_empty_str(lang) for lang in languages
            ):
                errors.append(
                    f"{label}: 'languages' must be a list of non-empty strings."
                )

        extract = item.get("extract")
        if extract is not None and not isinstance(extract, bool):
            errors.append(f"{label}: 'extract' must be a boolean if provided.")

        translations = item.get("translations")
        if translations is not None:
            if not isinstance(translations, dict):
                errors.append(f"{label}: 'translations' must be a mapping.")
            else:
                seen_translation_keys: set[str] = set()
                for raw_key, translation in translations.items():
                    if not _is_non_empty_str(raw_key):
                        errors.append(
                            f"{label}: translation keys must be non-empty strings."
                        )
                        continue
                    normalized_key = raw_key.strip().lower().replace("-", "_")
                    if not TRANSLATION_KEY_PATTERN.match(normalized_key):
                        errors.append(
                            f"{label}: translation key {raw_key!r} must be a base or region language tag."
                        )
                    if normalized_key in seen_translation_keys:
                        errors.append(
                            f"{label}: duplicate translation key {raw_key!r} after normalization."
                        )
                    seen_translation_keys.add(normalized_key)

                    if not isinstance(translation, dict):
                        errors.append(
                            f"{label}: translation {raw_key!r} must be a mapping."
                        )
                        continue

                    for field in ("name", "description"):
                        if field in translation and not _is_non_empty_str(
                            translation.get(field)
                        ):
                            errors.append(
                                f"{label}: translation {raw_key!r} field {field!r} must be a non-empty string."
                            )

                    if not any(
                        _is_non_empty_str(translation.get(field))
                        for field in ("name", "description")
                    ):
                        errors.append(
                            f"{label}: translation {raw_key!r} must provide a non-empty 'name' or 'description'."
                        )

        source = item.get("source")
        if not isinstance(source, dict):
            errors.append(f"{label}: 'source' must be a mapping.")
            continue

        source_type = source.get("type")
        if source_type not in VALID_SOURCE_TYPES:
            errors.append(
                f"{label}: source.type must be one of {sorted(VALID_SOURCE_TYPES)}."
            )
            continue

        if source_type == "github_release":
            repo = source.get("repo")
            if not _is_non_empty_str(repo) or not REPO_PATTERN.match(repo.strip()):
                errors.append(f"{label}: github_release requires 'repo' in owner/name form.")
            has_assets = any(
                [
                    _is_non_empty_str(source.get("assetPattern")),
                    isinstance(source.get("assets"), list) and len(source["assets"]) > 0,
                    isinstance(source.get("assetPatterns"), list)
                    and len(source["assetPatterns"]) > 0,
                ]
            )
            if not has_assets:
                errors.append(
                    f"{label}: github_release requires 'assetPattern', 'assetPatterns', or 'assets'."
                )

        elif source_type == "github_raw":
            repo = source.get("repo")
            if not _is_non_empty_str(repo) or not REPO_PATTERN.match(repo.strip()):
                errors.append(f"{label}: github_raw requires 'repo' in owner/name form.")
            files = source.get("files")
            if (
                not isinstance(files, list)
                or not files
                or not all(_is_non_empty_str(f) for f in files)
            ):
                errors.append(
                    f"{label}: github_raw requires a non-empty 'files' list."
                )

        elif source_type == "direct":
            url = source.get("url")
            files = source.get("files")
            valid_single = _is_http_url(url)
            valid_list = isinstance(files, list) and len(files) > 0 and all(
                _is_http_url(f)
                or (isinstance(f, dict) and _is_http_url(f.get("url")))
                for f in files
            )
            if not (valid_single or valid_list):
                errors.append(
                    f"{label}: direct source requires a valid 'url' or non-empty 'files' list."
                )

    return errors


def validate_file(path: Path) -> list[str]:
    content = path.read_text(encoding="utf-8")
    data = yaml.safe_load(content)
    return validate_catalog_data(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Ciyue-Store catalog.yaml")
    parser.add_argument(
        "catalog",
        nargs="?",
        default="catalog.yaml",
        help="Path to catalog YAML file (default: catalog.yaml)",
    )
    args = parser.parse_args(argv)

    catalog_path = Path(args.catalog)
    if not catalog_path.is_file():
        print(f"Error: catalog file not found: {catalog_path}", file=sys.stderr)
        return 1

    try:
        errors = validate_file(catalog_path)
    except yaml.YAMLError as exc:
        print(f"YAML parse error in {catalog_path}: {exc}", file=sys.stderr)
        return 1

    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    data = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    print(f"Validation passed: {len(data.get('items', []))} item(s) verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
