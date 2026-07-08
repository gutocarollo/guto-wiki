---
name: adversarial-review
description: "Revisor adversarial fundamentado em evidencia para o repo. Use quando o usuario pedir revisar, auditar, criticar, encontrar gaps, validar plano, PR, diff, implementacao, arquitetura, UI, testes ou execucao. A auditoria deve confrontar explicitamente: docs configurados em docs-tooling.conf, codigo real, texto do plano e o que foi executado. Toda acusacao precisa ser confirmada ou refutada com evidencia concreta."
---

# Adversarial Review

Revisor que ataca plano e implementacao para descobrir onde quebram, mas paga o preco de provar cada acusacao. Acusacao sem prova e ruido. Concordancia sem prova tambem e ruido.

## Modo de execucao (self-review inline proibido)

Se o artefato auditado foi produzido NESTA conversa pelo proprio agente (plano/diff/execucao proprios — caso dos loops do `delivery-council`), esta skill NAO roda inline: ela e o CONTRATO do prompt do subagent definido por `ADVERSARIAL_REVIEWER_AGENT` (contexto isolado; Claude Code: Agent tool, Codex: custom agent thread). Rodar inline so e legitimo quando o auditor nao e o autor — ex.: usuario pede review de commit antigo, PR de terceiro ou artefato externo.

## 0. Escopo

Esta skill revisa o repo atual. Leia `docs-tooling.conf` quando existir para resolver `CODE_ROOTS`,
`ARCHITECTURE_*`, `SPECIALIZED_*`, `DOCS_*` e nomes de subagents. Ela nao revisa apenas o diff. Ela revisa
a aderencia entre cinco fontes obrigatorias:

1. **Plano** - texto enviado pelo usuario ou arquivo de plano citado. Se o plano nao foi fornecido, reconstruir a intencao a partir de commits, diffs, docs de execucao e pedido do usuario, declarando a limitacao.
2. **Execucao** - arquivos alterados, diff, logs, comandos rodados, relatorios de execucao, testes e evidencia visual quando existir.
3. **Arquitetura** - documentos canonicos apontados por `ARCHITECTURE_*`.
4. **Categoria especializada/UI** - documentos canonicos apontados por `SPECIALIZED_*`, quando aplicavel.
5. **Codigo real do app** - caminhos configurados em `CODE_ROOTS`, migrations, scripts, testes, configs e estilos.

Auditoria que ignora qualquer uma dessas fontes e incompleta. Docs definem contrato; codigo e execucao provam aderencia ou desvio.

## 1. Fontes obrigatorias

### 1.1 Arquitetura

Antes de avaliar decisao arquitetural, seguranca, dados, tenancy, runtime, deploy, performance, integracao ou fluxo de dominio, leia os docs relevantes em `ARCHITECTURE_DOCS`.

Entrada obrigatoria:

- `ARCHITECTURE_INDEX` - mapa e ordem de leitura.

Escolha os documentos conforme o tema auditado:

- docs vivos, ADRs, threat model, visao runtime/deploy, qualidade, dominio e integracoes listados no índice.

Regra: se o gap citado toca arquitetura, cite pelo menos um doc de `ARCHITECTURE_DOCS` e um trecho/arquivo de codigo que confirma aderencia ou desvio.

### 1.2 Categoria especializada/UI

Antes de avaliar UI, tema, tokens, contraste, componentes, motion, dashboards, responsividade, className/Tailwind ou evidencia visual, leia os docs relevantes em `SPECIALIZED_DOCS` quando configurado.

Entrada obrigatoria:

- `SPECIALIZED_INDEX` - catalogo canonico.

Escolha os documentos conforme o tema auditado:

- páginas vivas, contratos, workflows, decisions e auditorias atuais listadas no índice especializado.

Codigo obrigatorio para conferir o contrato:

- `SPECIALIZED_TOKEN_SOURCE` - fonte viva dos tokens, quando configurada.
- `SPECIALIZED_UI_COMPONENTS` - componentes locais, quando configurados.
- Componentes e telas alteradas no diff.
- Guardas/scripts quando aplicavel: `SPECIALIZED_GATE_CMD`, `SPECIALIZED_MINING_CHECK_CMD` e comandos correlatos configurados.

Regra: claim visual exige evidencia renderizada (`ui-evidence`) quando a conclusao depende de pixels. Claim de token/contraste exige doc + ponto de uso + guarda/script quando disponivel.

### 1.3 Codigo, plano e execucao

Sempre cruzar:

- O que o plano prometeu.
- O que foi realmente alterado.
- O que os docs canonicos exigem.
- O que os testes/evidencias cobrem.
- O que o codigo faz em runtime.

Comandos uteis:

- `git diff --stat` e `git diff -- <paths>` para escopo real.
- `rg` para encontrar padroes, usos existentes, invariantes e testes.
- Testes especificos do modulo alterado antes de conclusao.
- Banco dev em Postgres local quando o gap depende de dados reais.

Nao declare "feito", "certo" ou "100%" sem evidencias desta sessao.

## 2. Lei Zero como criterio de review

Reinvenção da roda e gap de primeira classe. Para feature nao trivial, avalie se havia biblioteca, padrao, componente local, skill, doc, ADR ou implementacao OSS madura que deveria ter sido reutilizada.

Trilha obrigatoria:

- Buscar padrao local primeiro: `rg`, componentes existentes, docs de arquitetura/categoria especializada e skills do projeto.
- Para libs/frameworks/APIs/CLI/cloud: usar Context7 via `ctx7` conforme `AGENTS.md`.
- Para solucao OSS madura: buscar GitHub/awesome-lists/referencias recentes quando a decisao for nao trivial.

Se existe solucao madura/local ignorada e a implementacao artesanal aumenta custo ou risco, o gap e REAL mesmo que o codigo compile.

## 3. Protocolo sequencial

### Etapa 1 - Inventariar artefatos

Liste o que esta sendo auditado:

- Plano ou requisito original.
- Arquivos alterados.
- Docs de execucao ou relatorios.
- Testes/evidencias existentes.
- Docs de arquitetura/categoria especializada que governam o tema.

Sem inventario, nao ha auditoria.

### Etapa 2 - Montar matriz de aderencia

Para cada item relevante do plano ou da implementacao:

```md
Item | Prometido | Executado | Contrato arquitetura | Contrato especializado/UI | Codigo/teste/evidencia | Hipotese
```

Use a matriz para gerar hipoteses. Nao pule direto para opiniao.

### Etapa 3 - Levantar hipoteses agressivamente

Ataque o artefato por:

- Divergencia plano x execucao.
- Violacao de `ARCHITECTURE_DOCS`.
- Violacao de `SPECIALIZED_DOCS`.
- Bug de codigo/logica.
- Falha de dado real.
- Performance.
- Seguranca/privacidade/tenancy.
- Teste ausente ou insuficiente.
- Evidencia visual ausente quando obrigatoria.
- Reinvenção da roda.

### Etapa 4 - Classificar e provar cada hipotese

Cada hipotese recebe uma ou mais classes. A classe define a prova obrigatoria.

| Classe | Quando usar | Prova obrigatoria |
|---|---|---|
| **PLANO/ESCOPO** | Item prometido nao aparece na execucao, ou execucao diverge do plano | Texto do plano + diff/arquivo/log que mostra o executado |
| **ARQUITETURA** | Desvio de tenancy, runtime, deploy, dominio, ADR, qualidade, threat model | Doc em `ARCHITECTURE_DOCS` + codigo/config/teste que adere ou viola |
| **UI/ESPECIALIZADO** | Token, tema, contraste, componente, chart, responsividade, motion, className | Doc em `SPECIALIZED_DOCS` + codigo de componente/estilo + evidencia visual ou guarda quando aplicavel |
| **CODIGO/LOGICA** | Branch faltando, estado invalido, race, erro de validacao, autorizacao, tratamento de erro | Trecho literal de codigo + caminho de execucao + caso concreto que quebra |
| **DADO/DB** | Premissa sobre cardinalidade, NULL, status, volume, integridade, distribuicao real | Query no banco dev/real disponivel + resultado literal. Sem query, nao e REAL |
| **PERFORMANCE** | N+1, full scan, indice ausente, render excessivo, asset pesado | EXPLAIN/metricas/perfil quando possivel + volume real ou estimativa declarada |
| **SEGURANCA** | Auth, RBAC, tenant isolation, injection, PII, LGPD, secrets | Codigo + threat model/OWASP/doc aplicavel + caso de exploracao concreto |
| **FONTE/OSS** | Reinvenção, API/lib usada fora do contrato, dependencia inadequada | Context7/doc oficial + repo/lib/padrao local comparado |
| **TESTE/EVIDENCIA** | Ausencia de teste, teste que nao cobre bug, claim visual sem PNG | Arquivo de teste/log/manifest ou ausencia comprovada por busca |

Regra: a prova tem que decidir a hipotese. Query de banco nao prova bug de UI. Screenshot nao prova isolamento de tenant. Use a trilha certa.

### Etapa 5 - Vereditar

Cada hipotese fecha em exatamente um status:

- **REAL** - evidencia confirma o gap e o impacto material.
- **TEORICO-descartado** - logicamente possivel, mas a prova mostra impacto nulo no estado real.
- **REFUTADO** - a premissa estava errada; o codigo/docs/testes ja cobrem.
- **NAO-PROVADO** - faltou acesso ou evidencia. Nao entra como acusacao, entra como risco/pendencia.

Refutar exige prova no mesmo nivel de acusar.

### Etapa 6 - Planejar correcao

Para gap REAL, proponha correcao minima aderente ao projeto. Se houver mais de uma correcao razoavel, use a skill `clarification-plan`: blocos D[n] com comportamento, exemplo aplicado bom, exemplo aplicado ruim e quando escolher.

Nao feche plano final para decisao que depende de escolha do usuario. Feche plano condicionado ou pare no bloco D[n].

## 4. Evidencia minima por achado

Um achado valido precisa conter:

```md
### [R[n]] [Afirmação direta]
- Severidade: BLOQUEANTE | ALTA | MEDIA | BAIXA
- Classe: PLANO/ESCOPO | ARQUITETURA | UI/ESPECIALIZADO | CODIGO/LOGICA | DADO/DB | PERFORMANCE | SEGURANCA | FONTE/OSS | TESTE/EVIDENCIA
- Veredicto: REAL | TEORICO-descartado | REFUTADO | NAO-PROVADO
- Contrato esperado:
  - Plano: [arquivo/trecho ou resumo fiel]
  - Arquitetura: [ARCHITECTURE_DOCS/... quando aplicavel]
  - Especializado/UI: [SPECIALIZED_DOCS/... quando aplicavel]
- Evidencia:
  - Codigo: [path + linha/trecho]
  - Execucao: [diff/log/teste/comando/manifest]
  - Dado/Fonte: [query/doc/repo/link quando aplicavel]
- Impacto: [caso real que quebra ou risco concreto]
- Correcao: [acao objetiva ou decisao D[n]]
```

Fechar com:

```md
PLACAR: N reais | M teoricos descartados | K refutados | P nao provados
PROXIMO PASSO: [acao de maior severidade]
```

## 5. Anti-padroes proibidos

| Anti-padrao | Por que e proibido |
|---|---|
| Auditar so o diff | O diff nao mostra o contrato do projeto nem o plano prometido |
| Ignorar `ARCHITECTURE_DOCS` | Pode aprovar codigo que viola tenancy, runtime, qualidade ou seguranca |
| Ignorar `SPECIALIZED_DOCS` | Pode aprovar UI que quebra tokens, temas, contraste ou padroes canonicos |
| Comparar execucao sem ler o plano | Nao da para medir aderencia ao que foi pedido |
| Declarar gap de dado sem query real | Achismo com roupa de rigor |
| Declarar UI correta sem evidencia visual quando pixels importam | Codigo nao prova render final |
| Citar docs sem conferir codigo | Doc e contrato; codigo prova estado real |
| Citar codigo sem conferir docs canonicos | Implementacao pode funcionar e ainda estar fora do padrao do repo |
| Concordar reflexamente | Refutacao tambem precisa de evidencia |
| Listar dezenas de hipoteses sem veredito | Adversarialidade sem fechamento vira ruido |
| Inventar numero, teste ou fonte | Fabricacao invalida a auditoria |

## 6. Saida esperada

Comece pelo veredicto tecnico. Depois liste achados em ordem de severidade. Inclua perguntas somente depois da exploracao e apenas quando uma decisao real permanecer aberta.

Formato recomendado:

1. Veredicto geral.
2. Inventario auditado.
3. Achados R[n].
4. Decisoes D[n], se houver.
5. Placar agregado.
6. Proximo passo concreto.
