# loop.md — manutenção autônoma do repo (rodar com /loop sem argumentos)

Você está no loop de manutenção (Loop Engineering — CLAUDE.md §16). Uma passada = os checks abaixo,
na ordem, consertando o que for barato e reportando o que não for. Estado durável: se `.claude/runs/ACTIVE`
existir, a marathon tem prioridade — execute a "Próxima ação" do RUN.md e encerre a passada.

## Checks da passada

1. **Lessons pendentes de promoção** — `tasks/lessons.md`: alguma lição repetida 2×+ ainda sem
   `[PROMOVIDA → destino]`? Se sim, promover (regra no CLAUDE.md §apropriada ou hook via hookify) e marcar.
2. **Wiki/documentação do repo íntegra** — `python3 scripts/docs-wiki-lint.py`. FAIL → corrigir
   `docs/index.md`, `docs/log.md` ou índice da categoria (regidos por `docs/SCHEMA.md`) e re-rodar.
   Se houver diff local, rode também `python3 scripts/docs-wiki-lint.py --worktree` para confirmar que
   Markdown novo/movido/removido veio com log/índice no mesmo diff.
3. **Frescor de mining especializado** — rode `SPECIALIZED_MINING_CHECK_CMD` de `docs-tooling.conf`.
   Stale → rode `SPECIALIZED_MINING_REGEN_CMD`, stage, e rode `SPECIALIZED_MINING_INGEST_CMD` quando
   existir.
4. **Árvore git suja de artefato órfão** — `git status --short`: arquivo gerado que não deveria ser
   commitado (PDF, JSON >1MB, print solto em docs/)? Reportar com path; não deletar nada tracked sem ordem.
5. **Gates especializados** — rode `SPECIALIZED_GATE_CMD` de `docs-tooling.conf` (ratchet anti-hardcode).
   Regressão → reportar cluster e path:linha.
6. **Integridade referencial (backstop de rename/delete)** — `python3 scripts/ref-integrity.py --since <ref-da-última-passada-verde>`
   (report-only; o pre-commit já pega no commit, este pega bypass `--no-verify` e edição manual). Achado
   `[link]`/`[stale]` → corrigir per skill `ref-integrity` (repoint / desativar / allowlist).

## Regras do loop

- Ação irreversível (push, delete tracked, deploy, prod) = FORA do loop; apenas reportar.
- Cada passada termina com resumo de 3-6 linhas: o que passou, o que consertou, o que precisa do Augusto.
- Nada a fazer em 2 passadas seguidas → encerrar o loop (self-paced: não agendar próxima).
