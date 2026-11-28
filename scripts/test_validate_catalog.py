import unittest
from pathlib import Path

from validate_catalog import validate_catalog_data, validate_file


def _item(**overrides):
    item = {
        "id": "translated",
        "type": "hunspell",
        "name": "默认名称",
        "description": "默认描述",
        "author": "Tester",
        "license": "MIT",
        "sourceUrl": "https://example.com",
        "format": "hunspell",
        "source": {
            "type": "github_raw",
            "repo": "a/b",
            "files": ["a.aff", "a.dic"],
        },
    }
    item.update(overrides)
    return item


class ValidateCatalogTest(unittest.TestCase):
    def test_repo_catalog_is_valid(self) -> None:
        catalog_path = Path(__file__).resolve().parent.parent / "catalog.yaml"
        errors = validate_file(catalog_path)
        self.assertEqual(errors, [])

    def test_missing_required_fields_are_reported(self) -> None:
        errors = validate_catalog_data(
            {
                "schemaVersion": 1,
                "items": [
                    {
                        "id": "bad-item",
                        "type": "hunspell",
                        "name": "Missing License",
                        "author": "Tester",
                        "sourceUrl": "https://example.com",
                        "format": "hunspell",
                        "source": {
                            "type": "github_raw",
                            "repo": "a/b",
                            "files": ["a.aff", "a.dic"],
                        },
                    }
                ],
            }
        )
        self.assertTrue(any("license" in e for e in errors))

    def test_duplicate_ids_are_rejected(self) -> None:
        item = {
            "id": "dup",
            "type": "audio",
            "name": "Audio",
            "author": "Tester",
            "license": "MIT",
            "sourceUrl": "https://example.com",
            "format": "audio_zips",
            "source": {"type": "direct", "url": "https://example.com/a.zips"},
        }
        errors = validate_catalog_data({"schemaVersion": 1, "items": [item, item]})
        self.assertTrue(any("duplicate id" in e for e in errors))

    def test_translations_are_accepted(self) -> None:
        errors = validate_catalog_data(
            {
                "schemaVersion": 1,
                "items": [
                    _item(
                        translations={
                            "en": {
                                "name": "English name",
                                "description": "English description",
                            },
                            "zh_TW": {"name": "繁體名稱"},
                            "ja": {"description": "日本語の説明"},
                        }
                    )
                ],
            }
        )
        self.assertEqual(errors, [])

    def test_invalid_translations_are_reported(self) -> None:
        errors = validate_catalog_data(
            {
                "schemaVersion": 1,
                "items": [
                    _item(
                        translations={
                            "en": "not-a-map",
                            "zh_TW": {"name": ""},
                            "bad key": {"name": "Invalid key"},
                            "zh-TW": {"name": "Duplicate"},
                        }
                    )
                ],
            }
        )
        self.assertTrue(any("must be a mapping" in e for e in errors))
        self.assertTrue(
            any(
                "must provide a non-empty 'name' or 'description'" in e
                for e in errors
            )
        )
        self.assertTrue(any("language tag" in e for e in errors))
        self.assertTrue(any("duplicate translation key" in e for e in errors))

    def test_translations_must_be_a_mapping(self) -> None:
        errors = validate_catalog_data(
            {
                "schemaVersion": 1,
                "items": [_item(translations=["en"])],
            }
        )
        self.assertTrue(any("'translations' must be a mapping" in e for e in errors))

    def test_top_level_name_validation(self) -> None:
        valid = validate_catalog_data(
            {"schemaVersion": 1, "name": "Community Store", "items": []}
        )
        self.assertEqual(valid, [])

        invalid = validate_catalog_data(
            {"schemaVersion": 1, "name": "   ", "items": []}
        )
        self.assertTrue(any("'name'" in e for e in invalid))


if __name__ == "__main__":
    unittest.main()
