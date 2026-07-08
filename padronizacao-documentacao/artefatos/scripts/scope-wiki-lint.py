#!/usr/bin/env python3
"""Compatibilidade: o lint canônico agora é repo-wide.

Use `python3 scripts/docs-wiki-lint.py --scope <LEGACY_WIKI_SCOPE>`.
Este wrapper existe para chamadas antigas durante a migração; o scope vem de `docs-tooling.conf`.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_config() -> dict[str, str]:
    values: dict[str, str] = {}
    for path in (ROOT / "docs-tooling.conf", ROOT / ".docs-tooling.conf", ROOT / "wiki-tooling.conf"):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if not line or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
        break
    return values


def main() -> int:
    scope = load_config().get("LEGACY_WIKI_SCOPE", "specialized")
    return subprocess.call(
        [sys.executable, str(ROOT / "scripts" / "docs-wiki-lint.py"), "--scope", scope],
        cwd=ROOT,
    )


if __name__ == "__main__":
    sys.exit(main())
