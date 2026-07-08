#!/usr/bin/env python3
"""Lint da guto-wiki.

Regras:
- todo arquivo relevante precisa estar citado em README/index/log ou coberto por colecao indexada;
- logs ficam em ordem temporal decrescente e com heading temporal;
- Markdown novo/movido/removido em diff precisa mexer no log no mesmo diff;
- caches de ferramentas e diretorios git/venv ficam fora do scan.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "wiki-tooling.conf"


def load_config() -> dict[str, str]:
    values: dict[str, str] = {}
    if not CONFIG.exists():
        return values
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


CONF = load_config()


def config_csv(key: str, default: set[str]) -> set[str]:
    value = CONF.get(key)
    if not value:
        return set(default)
    return {item.strip() for item in value.split(",") if item.strip()}

STRUCTURAL_NAMES = {"README.md", "index.md", "log.md", "SCHEMA.md", "SKILL.md", "CLAUDE.md"}
CAPS_OK = {
    "README.md",
    "INDEX.md",
    "SCHEMA.md",
    "SKILL.md",
    "CLAUDE.md",
    "AGENTS.md",
    "LICENSE",
    "LICENSE.md",
}
IGNORED_PARTS = {
    ".git",
    ".venv",
} | config_csv(
    "IGNORED_TOOL_DIRS",
    {".understand-anything", ".anythingllm", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"},
)
GENERIC_DIRS = {"docs", "scripts", "skills", "hooks", "tasks", "artefatos", "github-workflows", "githooks"}

NAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}-|\d+-)?[a-z0-9]+([a-z0-9.\-]*[a-z0-9])?\.[a-z0-9]+$")
LOG_HEADING_RE = re.compile(r"^## \[(\d{4}-\d{2}-\d{2}|sem-data)\] [^·]+ · .+")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STRAY_TOOL_RE = re.compile(r"^\s*</(content|invoke|antml:invoke|antml:parameter)>\s*$")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def is_ignored(path: Path) -> bool:
    try:
        parts = path.relative_to(ROOT).parts
    except ValueError:
        return True
    return any(part in IGNORED_PARTS for part in parts)


def tracked_or_local_files() -> list[Path]:
    files: set[Path] = set()
    for raw in subprocess.run(["git", "ls-files"], cwd=ROOT, text=True, capture_output=True).stdout.splitlines():
        if raw:
            files.add(ROOT / raw)
    for raw in subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    ).stdout.splitlines():
        if raw:
            files.add(ROOT / raw)
    return sorted(path for path in files if path.is_file() and not is_ignored(path))


def collect_index_corpus() -> str:
    parts: list[str] = []
    for path in tracked_or_local_files():
        if path.name in {"README.md", "index.md", "log.md"}:
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def mentioned(path: Path, corpus: str) -> bool:
    r = rel(path)
    return r in corpus or path.name in corpus


def collection_mentioned(path: Path, corpus: str) -> bool:
    parts = path.relative_to(ROOT).parts[:-1]
    for i in range(len(parts), 0, -1):
        leaf = parts[i - 1]
        if leaf in GENERIC_DIRS:
            continue
        ancestor = "/".join(parts[:i])
        if f"{ancestor}/" in corpus or ancestor in corpus or f"`{leaf}`" in corpus:
            return True
    return False


def naming_ok(path: Path) -> bool:
    name = path.name
    return name in CAPS_OK or name in STRUCTURAL_NAMES or bool(NAME_RE.match(name))


def check_indexing(errors: list[str], warnings: list[str]) -> None:
    corpus = collect_index_corpus()
    for path in tracked_or_local_files():
        if path.suffix == ".pyc":
            continue
        if path.name in STRUCTURAL_NAMES and path.suffix == ".md":
            continue
        if not (mentioned(path, corpus) or collection_mentioned(path, corpus)):
            errors.append(f"{rel(path)}: nao aparece em README/index/log nem em colecao indexada")
        if path.suffix == ".md" and not naming_ok(path):
            warnings.append(f"{rel(path)}: naming fora do padrao")


def check_frontmatter(errors: list[str]) -> None:
    for path in tracked_or_local_files():
        if path.suffix != ".md" or path.name in STRUCTURAL_NAMES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("---\n"):
            continue
        end = text.find("\n---\n", 4)
        if end == -1:
            errors.append(f"{rel(path)}: frontmatter nao fechado")
            continue
        frontmatter = text[4:end]
        updated = re.search(r"^updated:\s*[\"']?([^\"'\n]+)[\"']?\s*$", frontmatter, flags=re.M)
        if updated and not DATE_RE.match(updated.group(1)):
            errors.append(f"{rel(path)}: updated fora de YYYY-MM-DD: {updated.group(1)!r}")


def check_log_format(errors: list[str]) -> None:
    for log in sorted(ROOT.rglob("log.md")):
        if is_ignored(log):
            continue
        text = log.read_text(encoding="utf-8", errors="replace")
        previous: str | None = None
        headings = [line for line in text.splitlines() if line.startswith("## ")]
        if not headings:
            errors.append(f"{rel(log)}: sem entradas ## [YYYY-MM-DD]")
        for line in headings:
            if not LOG_HEADING_RE.match(line):
                errors.append(f"{rel(log)}: heading fora do formato temporal: {line}")
                continue
            date = line.split("]", 1)[0].removeprefix("## [")
            if date != "sem-data":
                if previous and previous != "sem-data" and date > previous:
                    errors.append(f"{rel(log)}: log fora de ordem temporal decrescente: {line}")
                previous = date
            else:
                previous = "sem-data"


def check_stray_tool_tags(errors: list[str]) -> None:
    for path in tracked_or_local_files():
        if path.suffix != ".md":
            continue
        for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if STRAY_TOOL_RE.match(line):
                errors.append(f"{rel(path)}:{i}: tag de ferramenta solta -> {line.strip()!r}")


def git_diff_name_status(diff_base: str | None, staged: bool, worktree: bool, errors: list[str]) -> list[tuple[str, list[str]]]:
    if not diff_base and not staged and not worktree:
        return []
    cmd = ["git", "diff", "--name-status", "--find-renames"]
    if staged:
        cmd.insert(2, "--cached")
    elif worktree:
        cmd.append("HEAD")
    else:
        cmd.append(f"{diff_base}...HEAD")
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        errors.append(f"git diff falhou: {proc.stderr.strip() or proc.stdout.strip()}")
        return []
    entries: list[tuple[str, list[str]]] = []
    for raw in proc.stdout.splitlines():
        parts = raw.split("\t")
        if len(parts) >= 2:
            entries.append((parts[0], parts[1:]))
    if worktree:
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        entries.extend(("A", [path]) for path in untracked.stdout.splitlines() if path)
    return entries


def check_diff_policy(errors: list[str], diff_base: str | None, staged: bool, worktree: bool) -> None:
    entries = git_diff_name_status(diff_base, staged, worktree, errors)
    if not entries:
        return
    log_changed = any("log.md" in paths for _, paths in entries)
    index_changed = any("index.md" in paths or "README.md" in paths for _, paths in entries)
    for status, paths in entries:
        old_path = paths[0]
        new_path = paths[-1]
        if any(path.endswith(".md") for path in {old_path, new_path}) and status[0] in {"A", "D", "R"}:
            if not log_changed:
                errors.append(f"{new_path}: markdown novo/removido/renomeado exige atualizar log.md no mesmo diff")
            if status.startswith(("A", "R")) and not index_changed:
                errors.append(f"{new_path}: markdown novo/renomeado exige atualizar index.md/README.md no mesmo diff")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict-naming", action="store_true")
    parser.add_argument("--diff-base")
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--worktree", action="store_true")
    args = parser.parse_args(argv)

    errors: list[str] = []
    warnings: list[str] = []
    check_indexing(errors, warnings)
    check_frontmatter(errors)
    check_log_format(errors)
    check_stray_tool_tags(errors)
    check_diff_policy(errors, args.diff_base, args.staged, args.worktree)

    if args.strict_naming:
        errors.extend(warnings)
        warnings = []

    if warnings:
        print(f"wiki-lint: {len(warnings)} aviso(s) de naming:")
        for warning in warnings[:60]:
            print(f"  ~ {warning}")
        if len(warnings) > 60:
            print(f"  ... +{len(warnings) - 60} outros")
    if errors:
        print("wiki-lint: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("wiki-lint: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
