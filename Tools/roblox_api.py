"""Shared, resilient downloader for public Roblox Studio API dumps."""

from __future__ import annotations

import re
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

VERSION_ENDPOINTS = (
    "https://clientsettings.roblox.com/v1/client-version/WindowsStudio64",
    "https://clientsettingscdn.roblox.com/v2/client-version/WindowsStudio64",
)
DEPLOY_HISTORY_URL = "https://setup.rbxcdn.com/DeployHistory.txt"
SETUP_BASE_URL = "https://setup.rbxcdn.com"
TIMEOUT = (12, 90)


def _make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (compatible; UniversalSynSaveInstance-Tools/2.1)",
            "Accept": "application/json, text/plain, */*",
        }
    )
    retry = Retry(
        total=4,
        connect=4,
        read=2,
        status=3,
        backoff_factor=0.7,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=4, pool_maxsize=4)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def _valid_hash(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"version-[A-Za-z0-9]+", value) is not None


def _version_hashes(session: requests.Session, errors: list[str]) -> list[str]:
    hashes: list[str] = []
    for endpoint in VERSION_ENDPOINTS:
        try:
            response = session.get(endpoint, timeout=TIMEOUT)
            response.raise_for_status()
            payload = response.json()
            version_hash = payload.get("clientVersionUpload") if isinstance(payload, dict) else None
            if _valid_hash(version_hash):
                if version_hash not in hashes:
                    hashes.append(version_hash)
                break
            errors.append(f"{endpoint}: clientVersionUpload ausente ou inválido")
        except (requests.RequestException, ValueError) as exc:
            errors.append(f"{endpoint}: {exc}")

    # DeployHistory is strictly a fallback; do not assume its final line is current.
    try:
        response = session.get(DEPLOY_HISTORY_URL, timeout=TIMEOUT)
        response.raise_for_status()
        found = re.findall(r"\bversion-[A-Za-z0-9]+\b", response.text)
        for version_hash in reversed(found):
            if version_hash not in hashes:
                hashes.append(version_hash)
            if len(hashes) >= 9:
                break
    except requests.RequestException as exc:
        errors.append(f"{DEPLOY_HISTORY_URL}: {exc}")
    return hashes


def fetch_api_dump(*, prefer_full: bool = True) -> dict[str, Any]:
    """Download and validate the newest usable public Studio API dump."""
    errors: list[str] = []
    with _make_session() as session:
        hashes = _version_hashes(session, errors)
        if not hashes:
            details = "\n".join(f"- {item}" for item in errors[-8:])
            raise RuntimeError("Não foi possível obter uma versão pública do Studio.\n" + details)

        suffixes = ("Full-API-Dump.json", "API-Dump.json") if prefer_full else (
            "API-Dump.json",
            "Full-API-Dump.json",
        )
        for version_hash in hashes:
            for suffix in suffixes:
                url = f"{SETUP_BASE_URL}/{version_hash}-{suffix}"
                try:
                    response = session.get(url, timeout=TIMEOUT)
                    response.raise_for_status()
                    payload = response.json()
                    classes = payload.get("Classes") if isinstance(payload, dict) else None
                    if not isinstance(classes, list) or not classes:
                        raise ValueError("JSON sem uma lista 'Classes' válida")
                    return payload
                except (requests.RequestException, ValueError) as exc:
                    errors.append(f"{url}: {exc}")

    details = "\n".join(f"- {item}" for item in errors[-12:])
    raise RuntimeError(
        "Não foi possível baixar um API Dump válido. Confira DNS, HTTPS, proxy ou bloqueios de rede.\n"
        + details
    )
