from __future__ import annotations

from src.governance.release_governance import (
    changelog_contains_version,
    is_valid_semver,
    read_version,
)


def test_version_is_valid_semver_and_changelog_is_aligned() -> None:
    version = read_version()
    assert is_valid_semver(version)
    assert changelog_contains_version(version)
