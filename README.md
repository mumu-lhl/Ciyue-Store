# Ciyue-Store

Official resource catalog for [Ciyue](https://github.com/mumu-lhl/Ciyue), providing legally licensed dictionaries, Hunspell morphological data, and pronunciation audio packs.

## Branch & Release Workflow

- **`dev`**: Default integration branch for commits and pull requests.
- **`main`**: Production branch consumed by Ciyue clients. Direct pushes to `main` should be disabled via branch protection; `.github/workflows/sync-main.yml` automatically syncs `dev` to `main` daily (and via manual `workflow_dispatch`) only after all validation checks pass.

## Validation

Using [uv](https://docs.astral.sh/uv/):

```bash
uv run --with pyyaml python scripts/validate_catalog.py catalog.yaml
uv run --with pyyaml python -m unittest discover -s scripts -p "test_*.py" -v
```
