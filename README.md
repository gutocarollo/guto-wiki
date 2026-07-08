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

## Como preparar um projeto para IA

Para uma IA entender o projeto com baixo risco de seguir documentação velha, mantenha estes pontos:

1. Um arquivo de configuração central (`wiki-tooling.conf` neste repo, `docs-tooling.conf` no pacote
   reutilizável) com paths de wiki, lints, hooks, CI e grafo Understand/Anything LLM.
2. Uma LLM Wiki temporal: `index.md` como mapa por tópico, `log.md` append-only como autoridade temporal,
   frontmatter com `status/updated/scope` e docs vivos separados de registros históricos.
3. Um grafo Understand Anything quando disponível, com cache local ignorado pelo Git. O grafo acelera
   navegação e blast radius, mas conclusão operacional ainda volta ao código, ao log/índice e às evidências.
4. Gates locais e remotos: `python3 scripts/wiki-lint.py`, `python3 scripts/wiki-lint.py --worktree`,
   pre-commit opcional e CI diff-aware.

Pré-requisitos práticos: Git, Python 3.12+ para os lints, `pre-commit` se o time quiser hooks gerenciados,
e Understand Anything/Anything LLM instalado quando o projeto for usar grafo navegável. O primeiro roteiro de
leitura para agentes deve ser: `README.md` → `index.md` → `log.md` → arquivo de config → docs relevantes →
código/evidência real.
