"""Release and semantic version governance utilities."""

from __future__ import annotations

from pathlib import Path
import re

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"
OUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
VERSION_FILE = PROJECT_ROOT / "VERSION"
CHANGELOG_FILE = PROJECT_ROOT / "CHANGELOG.md"

SEMVER_PATTERN = r"^\d+\.\d+\.\d+$"


def read_version() -> str:
    if not VERSION_FILE.exists():
        return "0.0.0"
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def is_valid_semver(version: str) -> bool:
    return bool(re.match(SEMVER_PATTERN, version))


def changelog_contains_version(version: str) -> bool:
    if not CHANGELOG_FILE.exists():
        return False
    changelog = CHANGELOG_FILE.read_text(encoding="utf-8")
    return f"## [{version}] " in changelog


def write_release_governance_artifacts() -> None:
    OUT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    OUT_TABLES_DIR.mkdir(parents=True, exist_ok=True)

    version = read_version()
    semver_ok = is_valid_semver(version)
    changelog_ok = changelog_contains_version(version)

    manifest = pd.DataFrame(
        [
            {
                "version": version,
                "semver_valid": semver_ok,
                "changelog_aligned": changelog_ok,
                "release_readiness": semver_ok and changelog_ok,
            }
        ]
    )
    manifest.to_csv(OUT_TABLES_DIR / "release_manifest.csv", index=False)

    lines = [
        "# Release Governance",
        "",
        "## Current Release",
        f"- Version: `{version}`",
        f"- SemVer valid: `{semver_ok}`",
        f"- Changelog aligned: `{changelog_ok}`",
        "",
        "## Policy",
        "- Use semantic versions (`MAJOR.MINOR.PATCH`) in `VERSION`.",
        "- Every released version must have a matching `## [x.y.z] - YYYY-MM-DD` section in `CHANGELOG.md`.",
        "- Release tag format: `vX.Y.Z`.",
        "- Release tags should be created only after pipeline + tests + QA are green.",
        "",
        "## Output Files",
        "- `VERSION`",
        "- `CHANGELOG.md`",
        "- `outputs/tables/release_manifest.csv`",
        "- `outputs/reports/release_governance.md`",
    ]
    (OUT_REPORTS_DIR / "release_governance.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
