# Índice por tópico

## padronizacao-documentacao

Padronização e curadoria de documentação assistida por IA — wiki Karpathy temporal, lints
determinísticos, integridade referencial git-aware, self-improvement loop.

- [2026-07-07 — Apanhado: padronização de documentação](padronizacao-documentacao/2026-07-07-apanhado-padronizacao-documentacao.md) —
  cronologia do que foi construído, mapa de artefatos, verificação de linkagem entre as peças e
  análise comparativa entre trilhas independentes de agentes com recomendações de adoção.
- [artefatos/](padronizacao-documentacao/artefatos/README.md) — pacote executável sanitizado:
  `docs/SCHEMA.md` (constituição), `scripts/` (docs-wiki-lint, ref-integrity), `githooks/pre-commit`,
  `loop.md`, skills (repo-wiki-curator, ref-integrity, delivery-council, adversarial-review),
  `hooks/lessons-inject.sh`, `tasks/lessons.md` e `CLAUDE.md` curado (workflow Boris Cherny §15 +
  self-improvement §16).

## governanca-da-wiki

Governança ativa deste repositório público.

- [scripts/wiki-lint.py](scripts/wiki-lint.py) — lint ativo da `guto-wiki`: indexação, log temporal,
  tags soltas, naming e política diff-aware.
- [wiki-tooling.conf](wiki-tooling.conf) — configuração central dos paths de wiki, pacote reutilizável e
  Understand/Anything LLM.
- [.github/workflows/wiki-integrity.yml](.github/workflows/wiki-integrity.yml) — CI com lint global e
  diff-aware contra a base do push/PR.
- [.pre-commit-config.yaml](.pre-commit-config.yaml) — hooks locais equivalentes para usuários de
  `pre-commit`.
- [.gitignore](.gitignore) — caches de ferramentas, incluindo `.understand-anything/`, fora do versionamento.
