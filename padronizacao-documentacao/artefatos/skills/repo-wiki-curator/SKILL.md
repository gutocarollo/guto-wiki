---
name: repo-wiki-curator
description: Use para indexar, curar, auditar, renomear e reorganizar QUALQUER documentação do repositório LearnHouse (não só design-system) no padrão Karpathy LLM Wiki temporal. Cobre planos, auditorias, ADRs, arquitetura, design-system, commercial, developers, reuniões, qa-evidence. Aciona quando a tarefa mencionar: curadoria de docs, indexação temporal, naming de arquivos, documento órfão/ambíguo, doc legado vs atual, limpar docs/, Karpathy, LLM wiki.
---

# Repo Wiki Curator

Curadoria contínua da documentação do repositório inteiro. Objetivo estratégico e regras: **leia primeiro
[`docs/SCHEMA.md`](../../../docs/SCHEMA.md)** — este SKILL é o procedimento operacional daquela constituição.

## Escopo

Todo `docs/` — `planos/`, `auditorias/`, `adr/`, `architecture/`, `design-system/`, `commercial/`,
`developers/`, `reunioes/`, `qa-evidence/`, `_arquivo/`. Não é só design-system (esse é apenas uma
categoria, com sub-schema próprio em `docs/design-system/SCHEMA.md`).

## Contrato

1. **Ler `docs/SCHEMA.md`** antes de tocar em qualquer doc.
2. **Ler `docs-tooling.conf`** quando existir. Paths de docs/lints/hooks e Understand Anything ficam ali
   (`DOCS_*`, `REF_INTEGRITY*`, `UNDERSTAND_*`, `IGNORED_TOOL_DIRS`), não espalhados em skills.
3. **Naming (SCHEMA §2):** `kebab-case` minúsculo; classe temporal define a data no nome —
   `living` = `slug.md` (sem data), `event` = `YYYY-MM-DD-slug.md` (prefixo), `sequenced` = `NNNN-slug.md`.
   Exceções em caps: `README/SCHEMA/CLAUDE/AGENTS/LICENSE`. FULL-CAPS e Title-Case são violação.
4. **Frontmatter** (SCHEMA §3): `title/status/updated/scope`. `status ∈ {canon, active, superseded, historico, proposta}`.
5. **Dupla indexação temporal** (SCHEMA §4): todo `.md` no `index.md` da categoria + no `docs/log.md` de repo.
6. **Prune = git é o arquivo** (SCHEMA §5): `superseded`/`historico` resolvido, PDF render, JSON regenerável e
   print de QA saem do working tree (git preserva); nunca deletar o que ainda informa o estado atual.
7. **Nunca marcar `canon` plano que o código atual não confirma.** Verdade viva = código, não doc.
8. **Understand/grafo é acelerador, não autoridade.** Use para navegar relações e blast radius, mas confirme
   qualquer conclusão em código vivo, índices/logs e evidências do repo.

## Procedimento

1. `find docs -name "*.md"` + `find docs -type f ! -name "*.md"` — inventário; compare contra `docs/index.md`,
   `docs/log.md` e o `index.md` de cada categoria.
2. Para cada doc: leia título, veredicto, data, status de execução ANTES de classificar. Ambíguo/legado →
   confira contra o código real (o doc mente? o código confirma?).
3. **Naming:** renomeie violações com `git mv` (preserva história), **uma por vez**, atualizando TODAS as
   refs a ela (`grep -rl` no repo) antes de seguir — migração sequencial (LEI ZERO §6), nunca batch.
   Após a passada de renames/deletes, valide com `python3 scripts/ref-integrity.py --range <base>..HEAD`
   (detector git-aware de refs órfãs; protocolo de correção na skill `ref-integrity`) — é o guard que
   pega a citação esquecida que o `grep -rl` manual deixou passar.
4. Atualize `index.md` (categoria) + `docs/log.md` (`## [YYYY-MM-DD] tipo · categoria`, append-only).
5. Sub-wiki densa (design-system): atualize também `wiki/` e o SCHEMA especializado.
6. Prune o superseded/resolvido (git rm) e registre no log.
7. `python3 scripts/docs-wiki-lint.py` — deve ficar verde (ou justificar exceção no próprio script).
   Use `--worktree` durante revisão local, `--staged` antes do commit e `--diff-base <ref>` em CI/PR
   quando a pergunta for "este diff manteve log/índice atualizados?".
   Se a passada renomeou/deletou arquivos: `python3 scripts/ref-integrity.py --range <base>..HEAD`
   também verde (o pre-commit `.githooks/` re-checa no commit; o loop roda `--since` como backstop).

## Saída esperada

- docs adicionados/reclassificados no índice (status);
- docs renomeados (de→para) e refs atualizadas;
- docs pruned (com como recuperar via git);
- backlog de naming restante (o que fica para próximas passadas do loop);
- resultado de `python3 scripts/docs-wiki-lint.py`;
- resultado de `python3 scripts/docs-wiki-lint.py --worktree` quando houver diff local relevante;
- resultado de `python3 scripts/ref-integrity.py --range <base>..HEAD` quando houve rename/delete.

## Guardrail

Curadoria é incremental e contínua (roda no `.claude/loop.md`). Não fazer mutirão de 80 renames num turno —
1 categoria por passada, testada. O objetivo é o repo ficar navegável para IA, não perfeito de uma vez.
