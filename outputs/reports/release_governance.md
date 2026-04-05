# Release Governance

## Current Release
- Version: `1.0.0`
- SemVer valid: `True`
- Changelog aligned: `True`

## Policy
- Use semantic versions (`MAJOR.MINOR.PATCH`) in `VERSION`.
- Every released version must have a matching `## [x.y.z] - YYYY-MM-DD` section in `CHANGELOG.md`.
- Release tag format: `vX.Y.Z`.
- Release tags should be created only after pipeline + tests + QA are green.

## Output Files
- `VERSION`
- `CHANGELOG.md`
- `outputs/tables/release_manifest.csv`
- `outputs/reports/release_governance.md`