# guto-wiki

Wiki pessoal no padrão **Karpathy LLM Wiki temporal**: [`index.md`](index.md) é o catálogo por
tópico (orientado a conteúdo), [`log.md`](log.md) é a cronologia append-only (orientado a tempo),
e cada tópico vive em um diretório próprio. A dupla indexação é o que desambigua documento antigo
vs. recente — diante de dois docs sobre o mesmo tema, o log diz qual é o mais novo e o frontmatter
`status` diz qual vale.

Convenções completas de naming (classes temporais `living`/`event`/`sequenced`), frontmatter,
indexação e ciclo ingest/query/lint/prune:
[`padronizacao-documentacao/artefatos/docs/SCHEMA.md`](padronizacao-documentacao/artefatos/docs/SCHEMA.md).

Gate local desta wiki pública:

```bash
python3 scripts/wiki-lint.py
python3 scripts/wiki-lint.py --worktree
```

Paths de documentação, pacote e Understand/Anything LLM ficam centralizados em
[`wiki-tooling.conf`](wiki-tooling.conf), para evitar hardcode espalhado em scripts e docs.
O CI em [`.github/workflows/wiki-integrity.yml`](.github/workflows/wiki-integrity.yml) roda o lint global
e o modo diff-aware. A configuração [`.pre-commit-config.yaml`](.pre-commit-config.yaml) oferece os mesmos
checks para quem usa `pre-commit`.
