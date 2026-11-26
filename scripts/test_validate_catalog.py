import unittest
from pathlib import Path

from validate_catalog import validate_catalog_data, validate_file


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


if __name__ == "__main__":
    unittest.main()
