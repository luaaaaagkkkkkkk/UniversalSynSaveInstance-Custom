"""Run every Python dumper in this directory tree and report failures."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    tools_dir = Path(__file__).resolve().parent
    runner_path = Path(__file__).resolve()
    scripts = sorted(
        (path for path in tools_dir.rglob("*.py") if path.resolve() != runner_path and path.name != "roblox_api.py"),
        key=lambda path: str(path).casefold(),
    )

    if not scripts:
        print("Nenhum dumper Python foi encontrado.")
        return 0

    failures: list[tuple[Path, int]] = []
    for script in scripts:
        print(f"\n=== Executando: {script.relative_to(tools_dir)} ===", flush=True)
        try:
            result = subprocess.run([sys.executable, str(script)], cwd=script.parent, check=False)
            if result.returncode == 0:
                print(f"[OK] {script.name}")
            else:
                failures.append((script, result.returncode))
                print(f"[FALHOU] {script.name} (código {result.returncode})")
        except OSError as exc:
            failures.append((script, -1))
            print(f"[ERRO] Não foi possível iniciar {script.name}: {exc}")

    print(f"\nResumo: {len(scripts) - len(failures)}/{len(scripts)} dumper(s) concluído(s).")
    if failures:
        for script, code in failures:
            print(f" - {script.relative_to(tools_dir)}: código {code}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
