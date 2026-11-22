"""Fetch the current Roblox Studio API dump and list serializable property types."""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


CLIENT_VERSION_URLS = (
    # Roblox documents the v1 endpoint as the recommended alternative to v2.
    "https://clientsettings.roblox.com/v1/client-version/WindowsStudio64",
    # Keep the public v2 endpoint as a compatibility fallback.
    "https://clientsettingscdn.roblox.com/v2/client-version/WindowsStudio64",
)
DEPLOY_HISTORY_URL = "https://setup.rbxcdn.com/DeployHistory.txt"
SETUP_BASE_URL = "https://setup.rbxcdn.com"
CONNECT_TIMEOUT = 12
READ_TIMEOUT = 90


def create_session() -> requests.Session:
    """Create a reusable HTTPS session with retries for temporary API/CDN errors."""
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (compatible; RobloxDataTypeDumper/2.0)",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
    )

    retry = Retry(
        total=4,
        connect=4,
        read=2,
        status=3,
        backoff_factor=0.8,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=4, pool_maxsize=4)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def get_response_text(session: requests.Session, url: str) -> str:
    response = session.get(url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
    response.raise_for_status()
    return response.text


def get_response_json(session: requests.Session, url: str) -> dict[str, Any]:
    response = session.get(url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
    response.raise_for_status()

    try:
        data = response.json()
    except (requests.exceptions.JSONDecodeError, json.JSONDecodeError, ValueError) as exc:
        content_type = response.headers.get("Content-Type", "desconhecido")
        raise ValueError(
            f"A resposta de {url} não contém JSON válido "
            f"(Content-Type: {content_type})."
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(f"A resposta de {url} tem formato JSON inesperado.")
    return data


def extract_version_hash(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    value = value.strip()
    if re.fullmatch(r"version-[A-Za-z0-9]+", value):
        return value
    return None


def get_version_candidates(session: requests.Session) -> list[str]:
    """Get the current Studio version first, then use DeployHistory as fallback."""
    versions: list[str] = []
    errors: list[str] = []

    for version_url in CLIENT_VERSION_URLS:
        try:
            version_data = get_response_json(session, version_url)
            current_version = extract_version_hash(
                version_data.get("clientVersionUpload")
            )
            if current_version:
                versions.append(current_version)
                break
            errors.append(
                f"O endpoint {version_url} não retornou "
                "um clientVersionUpload válido."
            )
        except (requests.RequestException, ValueError) as exc:
            errors.append(f"Endpoint de versão do Studio ({version_url}): {exc}")

    # DeployHistory is a fallback only; the current Studio endpoint above is preferred.
    try:
        history = get_response_text(session, DEPLOY_HISTORY_URL)
        for line in reversed(history.splitlines()):
            match = re.search(r"\b(version-[A-Za-z0-9]+)\b", line)
            if match:
                version = extract_version_hash(match.group(1))
                if version and version not in versions:
                    versions.append(version)
    except requests.RequestException as exc:
        errors.append(f"DeployHistory: {exc}")

    if not versions:
        details = "\n".join(f"- {error}" for error in errors)
        raise RuntimeError(
            "Não foi possível obter uma versão do Roblox Studio.\n"
            f"{details or '- Nenhuma versão válida foi encontrada.'}"
        )

    return versions


def fetch_api_dump(session: requests.Session) -> dict[str, Any]:
    """Fetch and validate an API dump, trying supported public dump filenames."""
    versions = get_version_candidates(session)
    errors: list[str] = []

    for version in versions:
        # API-Dump is the documented public filename. Full-API-Dump is retained
        # as a compatibility fallback for builds that expose that variant.
        for suffix in ("API-Dump.json", "Full-API-Dump.json"):
            url = f"{SETUP_BASE_URL}/{version}-{suffix}"
            try:
                data = get_response_json(session, url)
                classes = data.get("Classes")
                if not isinstance(classes, list):
                    raise ValueError("o JSON não contém uma lista 'Classes'.")
                return data
            except (requests.RequestException, ValueError) as exc:
                errors.append(f"{url}: {exc}")

    details = "\n".join(f"- {error}" for error in errors[-12:])
    raise RuntimeError(
        "Não foi possível baixar um API Dump válido do Roblox. "
        "Verifique a conexão HTTPS, DNS ou bloqueios de rede.\n"
        f"{details}"
    )


def collect_datatypes(api_dump: dict[str, Any]) -> list[str]:
    datatypes: set[str] = set()

    for api_class in api_dump.get("Classes", []):
        if not isinstance(api_class, dict):
            continue

        members = api_class.get("Members", [])
        if not isinstance(members, list):
            continue

        for member in members:
            if not isinstance(member, dict) or member.get("MemberType") != "Property":
                continue

            serialization = member.get("Serialization")
            if not isinstance(serialization, dict):
                continue
            if not serialization.get("CanLoad") or not serialization.get("CanSave"):
                continue

            value_type = member.get("ValueType")
            if not isinstance(value_type, dict):
                continue

            value_type_name = value_type.get("Name")
            value_type_category = value_type.get("Category")
            if not isinstance(value_type_name, str) or not value_type_name:
                continue

            if value_type_category in {"Enum", "Class"}:
                value_type_name = value_type_category

            datatypes.add(value_type_name)

    if not datatypes:
        raise RuntimeError(
            "O API Dump foi baixado, mas nenhum tipo de propriedade serializável foi encontrado."
        )

    return sorted(datatypes)


def write_output(datatypes: list[str]) -> Path:
    script_directory = Path(__file__).resolve().parent
    output_path = script_directory / "Dump"
    output_text = "\n".join(datatypes) + "\n"

    # Write atomically so an interrupted run does not leave a partial Dump file.
    file_descriptor, temporary_path = tempfile.mkstemp(
        prefix="Dump.", suffix=".tmp", dir=str(script_directory)
    )
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8", newline="\n") as file:
            file.write(output_text)
        os.replace(temporary_path, output_path)
    except Exception:
        try:
            os.unlink(temporary_path)
        except OSError:
            pass
        raise

    return output_path


def main() -> int:
    try:
        with create_session() as session:
            api_dump = fetch_api_dump(session)

        datatypes = collect_datatypes(api_dump)
        write_output(datatypes)
        print("\n".join(datatypes))
        return 0
    except requests.RequestException as exc:
        print(
            "Erro de conexão com a API pública do Roblox. "
            "Confira a conexão com a internet, DNS, proxy ou bloqueio HTTPS.\n"
            f"Detalhes: {exc}",
            file=sys.stderr,
        )
        return 1
    except Exception as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
