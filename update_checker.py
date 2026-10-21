"""Checks GitHub Releases for newer public application versions."""

from dataclasses import dataclass
import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class UpdateCheckResult:
    """Represents the outcome of a GitHub release check."""

    status: str
    current_version: str
    latest_version: str = ""
    release_url: str = ""
    error: str = ""


def _version_key(version: str) -> tuple[int, int, int, int, int, int]:
    """Returns a comparable key for stable, hotfix, RC, beta, and alpha versions."""
    match = re.search(r"([0-9]+)[.]([0-9]+)(?:[.]([0-9]+))?", version, re.IGNORECASE)
    if match is None:
        raise ValueError(f"Unsupported version string: {version}")

    major, minor, patch = int(match[1]), int(match[2]), int(match[3] or 0)
    lowered = version.lower()
    prerelease_match = re.search(r"(alpha|beta|rc)[. -]*([0-9]+)?", lowered)
    if prerelease_match is None:
        stability = 3
        prerelease_revision = 0
    else:
        stability = {"alpha": 0, "beta": 1, "rc": 2}[prerelease_match[1]]
        prerelease_revision = int(prerelease_match[2] or 0)

    hotfix_revision = 1 if re.search(r"[0-9]+h", lowered) or "hotfix" in lowered else 0
    return major, minor, patch, stability, prerelease_revision, hotfix_revision


def is_newer_version(current_version: str, latest_version: str) -> bool:
    """Returns whether the release version is newer than the installed version."""
    return _version_key(latest_version) > _version_key(current_version)


def _select_latest_release(payload, include_prereleases: bool):
    """Selects the highest valid release allowed by the configured update channel."""
    releases = payload if isinstance(payload, list) else [payload] if isinstance(payload, dict) else []
    candidates = []

    for release in releases:
        if not isinstance(release, dict) or release.get("draft", False):
            continue
        if release.get("prerelease", False) and not include_prereleases:
            continue

        tag_name = str(release.get("tag_name", "")).strip()
        release_url = str(release.get("html_url", "")).strip()
        if not tag_name or not release_url.startswith("https://github.com/"):
            continue

        try:
            version_key = _version_key(tag_name)
        except ValueError:
            continue
        candidates.append((version_key, tag_name, release_url))

    if not candidates:
        raise ValueError("GitHub returned no matching published releases.")

    _, tag_name, release_url = max(candidates, key=lambda item: item[0])
    return tag_name, release_url


def check_for_updates(
    current_version: str,
    api_url: str,
    timeout: float = 5.0,
    include_prereleases: bool = False,
) -> UpdateCheckResult:
    """Queries GitHub Releases and compares versions allowed by the update channel."""
    request = Request(
        api_url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "melcoms-ffmpeg-audio-normalizer",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))

        latest_version, release_url = _select_latest_release(payload, include_prereleases)
        status = "available" if is_newer_version(current_version, latest_version) else "current"
        return UpdateCheckResult(status, current_version, latest_version, release_url)
    except (HTTPError, URLError, OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return UpdateCheckResult("error", current_version, error=str(exc))
