---
title: Apanhado — padronização de documentação assistida por IA
status: historico
updated: 2026-07-07
scope: padronizacao-documentacao
---

# Apanhado — padronização de documentação assistida por IA (2026-07-06 → 07-07)

Registro (event doc, imutável) de tudo que foi criado/modificado em um repositório de produto privado em
torno de: wiki Karpathy, lint de documentação, integridade de referências, naming, curadoria,
índices temporais, lessons.md e workflow Boris Cherny. O pacote executável correspondente está em
[`artefatos/`](artefatos/README.md) (cópias sanitizadas; paths configuráveis anotados lá).

## 1. Por que isso existe

Documentação bagunçada = **IA tomando decisão errada**. Quando lixo legado e verdade atual
convivem sem marcação temporal, o agente escolhe o documento errado e propaga o erro. Dois
incidentes-gatilho no repo de origem: (a) um artefato de 10 MB anexado ao contexto matou a sessão
("prompt too long") — dado grande virou tabela SQL consultável, não leitura; (b) uma onda de
renames/deletes de curadoria deixou **38 referências quebradas** que nenhuma ferramenta acusava.
A resposta foi tornar a curadoria **contínua, indexada temporalmente e guardada por lints
determinísticos** — não um mutirão pontual.

## 2. Cronologia do que foi construído

| Quando | Entrega | Artefatos |
|---|---|---|
| 2026-07-06 (noite) | Gatilho: JSON de mineração 10 MB → camada relacional Postgres; lição "artefato >1MB nunca entra inteiro no contexto" registrada | `tasks/lessons.md` (1ª lição) |
| 2026-07-07 (madrugada) | Curadoria agressiva de uma categoria especializada e **generalização da wiki Karpathy para o repositório inteiro**: constituição, skill de curadoria, lint repo-wide com shim de compatibilidade, naming standard de 3 classes temporais | `docs/SCHEMA.md`, skill `repo-wiki-curator` (substitui a antiga skill de escopo estreito), `scripts/docs-wiki-lint.py` (+ `scope-wiki-lint.py` como wrapper configurável) |
| 2026-07-07 | **Workflow Boris Cherny** (§15 do CLAUDE.md: plan-first, subagents liberais, verification-before-done, demand elegance, autonomous bug fixing) + **self-improvement loop** (§16: capturar → injetar → promover → consolidar) com hook determinístico de injeção | `CLAUDE.md` §15/§16, `hooks/lessons-inject.sh` (SessionStart), `tasks/lessons.md`, `loop.md` |
| 2026-07-07 (tarde) | **ref-integrity**: varredura git-aware achou 38 refs quebradas por rename/delete (zeradas); ferramenta de fonte única com 3 consumidores; allowlist determinística; lint ganhou WARN de data-em-sufixo | `scripts/ref-integrity.py`, `githooks/pre-commit`, skill `ref-integrity`, `loop.md` check 6, `ref-integrity-allowlist` |
| 2026-07-07 (noite) | **Adversarial loops por subagent OBRIGATÓRIO** no council (self-review inline proibido; rodada N+1 continua o mesmo subagent; relatório atribui executor via linha `REVISORES:`) | skills `delivery-council` + `adversarial-review`, blocos council do CLAUDE.md/AGENTS.md |
| 2026-07-07 (esta análise) | **Fix de linkagem**: a skill de curadoria não citava o ref-integrity — corrigido em 3 pontos (validação pós-rename, gate verde, saída esperada) | skill `repo-wiki-curator` (passos 3 e 7 + saída) |
| 2026-07-08 | **Camada diff-aware/generalizada**: política `--worktree`/`--staged`/`--diff-base`, CI com histórico completo, configs centrais, cache Understand ignorado e regra "grafo acelera navegação, não substitui fonte viva" | `scripts/wiki-lint.py` nesta wiki + artefatos `docs-tooling.conf`, `docs-wiki-lint.py`, `docs/SCHEMA.md`, `github-workflows/docs-integrity.yaml`, `pre-commit-config.yaml`, `repo-wiki-curator` |

## 3. Mapa de artefatos

Dezoito arquivos, mapa detalhado (papel + destino sugerido) em [`artefatos/README.md`](artefatos/README.md):
config central ([`docs-tooling.conf`](artefatos/docs-tooling.conf)) · constituição
([`docs/SCHEMA.md`](artefatos/docs/SCHEMA.md)) · lints ([`docs-wiki-lint.py`](artefatos/scripts/docs-wiki-lint.py),
[`ref-integrity.py`](artefatos/scripts/ref-integrity.py), shim) · consumidores ([`githooks/pre-commit`](artefatos/githooks/pre-commit),
[`pre-commit-config.yaml`](artefatos/pre-commit-config.yaml), [skill ref-integrity](artefatos/skills/ref-integrity/SKILL.md),
[`loop.md`](artefatos/loop.md)) ·
[`ref-integrity-allowlist`](artefatos/ref-integrity-allowlist) · skills de processo
([curator](artefatos/skills/repo-wiki-curator/SKILL.md), [council](artefatos/skills/delivery-council/SKILL.md),
[adversarial-review](artefatos/skills/adversarial-review/SKILL.md)) · self-improvement
([`lessons-inject.sh`](artefatos/hooks/lessons-inject.sh), [`lessons.md`](artefatos/tasks/lessons.md)) ·
[`CLAUDE.md` curado](artefatos/CLAUDE.md).

## 4. Como as peças se linkam (verificado em 2026-07-07)

```
docs/SCHEMA.md  (constituição: naming/status/índices temporais/prune)
   └── repo-wiki-curator  (procedimento operacional da constituição)
         ├── docs-wiki-lint.py   guard FORWARD: órfão sem índice (FAIL), naming §2 (WARN), não-md
         └── ref-integrity.py    guard GIT-AWARE: link morto + citação a nome renomeado/deletado
               ├── pre-commit (--staged, resolve contra o INDEX)   ← bloqueia o commit
               ├── skill ref-integrity (--range A..B)              ← varredura sob demanda
               └── loop.md check 6 (--since)                       ← backstop de --no-verify
meta-loop: tasks/lessons.md ──lessons-inject.sh (SessionStart)──▶ contexto de toda sessão
           lição repetida 2× ──▶ regra no CLAUDE.md ou guard determinístico (padrão hookify)
```

Auditoria de linkagem feita hoje (grep em todos os pontos): `SCHEMA.md` §5 cita o ref-integrity ✓;
`loop.md` check 6 ✓; **`repo-wiki-curator` tinha ZERO menções ✗** — exatamente a skill que orquestra
renames (a operação que cria refs órfãs) não mandava rodar o detector. Corrigido em 3 pontos no
mesmo dia. Sobre hookify: é o mecanismo de promoção de lição recorrente a guard executável
(PreToolUse/Stop); no repo de origem existiam 5 guards locais desse tipo (nenhum de docs — para
referências, o `pre-commit` versionado em `.githooks/` cumpre o papel, cobrindo humano e agente).

## 5. Convergência independente: duas trilhas de agentes

No mesmo dia, outro repositório resolveu o mesmo problema por uma trilha independente. Comparação
feita lendo o código real da outra trilha (`scripts/docs-wiki-lint.py`, função `check_dead_references`
L242-275, e workflow de CI):

| Dimensão | Trilha Codex | Trilha Claude |
|---|---|---|
| Link markdown morto | `check_dead_references` dentro do próprio docs-wiki-lint; full-scan | `ref-integrity.py` check A; full-scan dos `.md` rastreados |
| Citação a nome antigo | regex de nomes × set de basenames REAIS do repo (full-scan; exige exclusões `narrative_only`) | `git diff --diff-filter=RD` (incremental; sabe o nome NOVO e sugere a correção) |
| Falso-positivo em código de exemplo | `blank_code_fences` antes do scan (L251) | ausente |
| Link com espaço/acento (%20) | `urllib.parse.unquote` (L262) — a auditoria deles achou 9 desses | ausente |
| Índice vivo linkando arquivo morto/arquivado | `check_no_foreign_live_links` (L278) | ausente |
| CI | job roda o lint na raiz (ci.yml L33) | só pre-commit + skill + loop |
| Autoteste do gate | casos negativos A/B recriados e confirmados FAIL | teste negativo manual (não institucionalizado) |
| Semântica de index | working tree | `--staged` resolve contra o INDEX (`git cat-file -e :path`, `git grep --cached`) |
| Arquitetura | 2 lints coexistem com escopos disjuntos | 2 scripts SRP — **convergência independente** na decisão de não fundir |

**Adoção no repo de origem** (implementado e commitado em 2026-07-07, revisão adversarial SATISFEITO):

1. **`blank_code_fences` + `unquote`** no check A/B do ref-integrity — elimina falso-positivo em
   exemplo de código e falso-negativo em link acentuado/com espaço. ✔ ADOTADO (fonte única de lógica
   de fence via `_fence_flags`, 1:1 por linha).
2. **`check_no_foreign_live_links`** no docs-wiki-lint — ✔ ADOTADO como **WARN** (não FAIL como na
   outra trilha): os índices do repo de origem usam links a `_arquivo/` como wayfinding rotulado legítimo;
   FAIL treinaria o time a ignorar o gate (divergência comunicada, §13.4).
3. **Wiring em CI** — ✔ ADOTADO (`.github/workflows/docs-integrity.yaml`, dispara no push já que o
   repo é commit-direto-na-main; roda wiki-lint + `--selftest` + range do push; expressões via `env:`).
4. **`--selftest`** no ref-integrity — ✔ ADOTADO (link morto real DEVE flagar; em code fence NÃO).

**Bug pego pelo dogfooding:** ao commitar, o próprio pre-commit bloqueou com 4 "links mortos" que
eram DIRETÓRIOS existentes — `git cat-file -e :dir` não resolve diretório no modo `--staged`.
Corrigido (`exists_in_index` agora cobre dir via `git ls-files -- <path>/`); modo index e working-tree
passaram a resolver o mesmo conjunto. É o valor do gate rodando contra si mesmo.

**Não copiar:** fusão dos dois lints num só (a outra trilha também manteve dois com escopos
disjuntos) e full-scan de citações como default (o incremental git-aware é o diferencial do
repo de origem: os pares rename old→new produzem a sugestão do nome novo no relatório). **O que uma
trilha paralela poderia levar daqui:** detecção git-aware de renames, semântica de index no pre-commit
e a allowlist determinística.

## 6. Como portar para um repositório novo

1. Copiar [`artefatos/docs-tooling.conf`](artefatos/docs-tooling.conf) e ajustar `DOCS_*`,
   `REF_INTEGRITY*`, `UNDERSTAND_*` e `IGNORED_TOOL_DIRS` para o repo destino.
2. Copiar [`artefatos/docs/SCHEMA.md`](artefatos/docs/SCHEMA.md) e ajustar as categorias de `docs/`.
3. Criar `docs/index.md` (catálogo) + `docs/log.md` (cronológico append-only `## [YYYY-MM-DD] tipo · categoria`).
4. Copiar `scripts/docs-wiki-lint.py`; ajustar `GENERIC_DIRS`/`CAPS_OK`/`IGNORED_DIRS` se o config não bastar.
5. Copiar `scripts/ref-integrity.py` + `.ref-integrity-allowlist` (começar vazia).
6. Copiar `.githooks/pre-commit` e ativar com `git config core.hooksPath .githooks`, ou copiar
   `.pre-commit-config.yaml` para times que já usam `pre-commit`.
7. Copiar as skills (`repo-wiki-curator`, `ref-integrity`) e um `loop.md` de manutenção contínua.
8. Criar `tasks/lessons.md` + hook SessionStart de injeção; adotar §15/§16 do
   [`CLAUDE.md` curado](artefatos/CLAUDE.md).
9. Adicionar CI com `fetch-depth: 0` e rodar `docs-wiki-lint.py` global + `--diff-base`, para que push/PR
   cobrem log/índice quando Markdown novo, movido ou removido entrar.

## 7. Publicação e sanitização

Este wiki é público. As cópias em `artefatos/` foram sanitizadas (nome de projeto e detalhes de
ambiente removidos); os índices reais do repo de origem (`docs/index.md`,
`docs/log.md`) ficaram fora por listarem conteúdo privado (o padrão deles está no
SCHEMA §4). A mesma trilha está espelhada em `github.com/gutocarollo/agent-swarm` (pasta
`claude/`, commit `76e9232`) — com uma diferença: a cópia do `repo-wiki-curator` de lá é
**anterior** ao fix de linkagem da seção 4; esta aqui é a atual.
