---
documento: SPEC-004
titulo: Método de Trabalho — fluxo lean/kanban dirigido por SPEC e ponte GitHub ↔ SERMI
versao: v1
status: proposto
data: 2026-06-15
autor: Bruno Serminaro
supersede: —
referencia: SPEC-001, SPEC-002, DEC-002, DEC-003, GUIDE-001
---

# SPEC-004 · Método de Trabalho (lean/kanban dirigido por SPEC)

> Descreve como o trabalho deste projeto flui: um quadro kanban enxuto no GitHub, com limites de WIP, dirigido pelo método spec-driven (DEC-002, GUIDE-001). Estabelece a Definition of Ready e a Definition of Done, e a **ponte** entre o board vivo no GitHub (estado transitório do trabalho) e o acervo SERMI em `docs/` (conhecimento durável). É a primeira SPEC técnica/de processo do projeto, numerada a partir de 004 por força da reserva do slot SPEC-003 (DEC-003). Os artefatos de configuração do board (templates de issue) vivem em `.github/` e são referenciados na §6.

---

## 1. Propósito

### 1.1 Por que documentar o método de trabalho

O projeto vai sair da fundação e entrar em produção de SPECs técnicas, DECs de stack e código (Ondas 2 e 3). Sem um método declarado, o fluxo degrada de duas maneiras previsíveis: ou o trabalho vira uma lista informal na cabeça do autor (sem WIP, sem critério de pronto, sem rastro), ou o "plano de ondas" do README vira um backlog desatualizado que ninguém move. Um projeto solo é especialmente vulnerável a isso, porque não há cadência de equipe que force a disciplina.

Esta SPEC fixa o método como **restrição de projeto**, do mesmo modo que a SPEC-001 fixa a taxonomia documental: declarada uma vez, observada sempre, auditável.

### 1.2 A ponte: board transitório, acervo durável

A decisão de fundo (discutida e fixada aqui) é que **o board vivo não entra na taxonomia SERMI**. Os cinco tipos SERMI guardam *conhecimento que persiste* (o que algo é, o que aconteceu, o que foi decidido, como operar, vitrine). Um quadro kanban guarda *estado transitório de trabalho* — "onde cada item está agora" — que muda dezenas de vezes e não é conhecimento a preservar. Versionar um board em `docs/` seria poluir o histórico do Git com movimentação de cards.

Logo:

| Plano | Onde vive | Natureza | Fonte de verdade de… |
|---|---|---|---|
| **Board vivo** (kanban) | GitHub Projects + Issues | transitório, descartável | *onde* o trabalho está agora |
| **Acervo** (SERMI) | `docs/` versionado | durável, imutável por versão | *o que* foi especificado, decidido, construído |

A regra que liga os dois: **uma issue é uma unidade de fluxo; um documento SERMI é uma unidade de conhecimento.** Quando um item fica `Feito`, sua verdade passa a viver no artefato commitado (SPEC, DEC, código), e a issue é fechada. O board nunca é fonte de verdade do conteúdo — só do andamento.

---

## 2. Princípios

O método combina lean/kanban (gestão de fluxo) com spec-driven (disciplina de construção, DEC-002 e GUIDE-001). Cinco princípios:

1. **Puxar, não empurrar.** Um item só entra em execução quando há capacidade livre na coluna de destino. Não se começa o que não se pode terminar.
2. **WIP baixo.** Limitar trabalho-em-progresso é o coração do kanban. Num projeto solo, foco é o recurso escasso; muitos itens abertos ao mesmo tempo significam nenhum terminado.
3. **A SPEC dirige, o eval prova** (DEC-002, GUIDE-001 §2). Nenhum item de código entra em execução sem uma SPEC que o dirija (Definition of Ready), nem é dado por pronto sem a verificação que o mede (Definition of Done).
4. **Definition of Done verificável, não opinativa.** "Pronto" é um conjunto de condições checáveis, não a impressão do autor de que "ficou bom" (princípio P7 do harness: *aprovado não é verificado*).
5. **Tornar o fluxo visível.** O board mostra todo o trabalho e seus impedimentos. O que está bloqueado é marcado, não escondido.

---

## 3. O quadro

O quadro é um **GitHub Project** (board) cujo campo `Status` tem as colunas abaixo, na ordem do fluxo. Cada coluna tem um limite de WIP orientativo, calibrado para operação solo.

| Ordem | Coluna | O que contém | Limite de WIP |
|---|---|---|---|
| 1 | **Backlog** | Tudo que pode vir a ser feito, sem ordem rígida. | sem limite |
| 2 | **Especificando** | Item para o qual se está escrevendo a SPEC/DEC que o dirige. | ≤ 2 |
| 3 | **Pronto para codar** | Item com SPEC/DEC pronta, aguardando ser puxado (buffer). | ≤ 3 |
| 4 | **Codando** | Implementação em curso. | **≤ 1** |
| 5 | **Verificando** | Eval e/ou `gov-check` rodando; conferência da Definition of Done. | ≤ 2 |
| 6 | **Feito** | Definition of Done cumprida; issue fechada. | sem limite |

Notas:

- O limite **≤ 1 em "Codando"** é deliberado: solo, um módulo por vez. Se algo trava, vai para `bloqueado` (não se abre outra frente para "aproveitar"; isso só esconde o impedimento).
- Itens de **documentação pura** (escrever uma SPEC, registrar uma DEC) podem ir direto de `Especificando` para `Verificando` (a verificação é o `gov-check`), pulando `Codando`.
- O **plano de ondas** (Ondas 1–4), que hoje vive no `README.md`, migra para este board como agrupamento (label `onda:N` ou campo próprio). O README volta a ser BRIEF vitrine puro (SPEC-001 §2.5) e aponta para o board, em vez de manter a tabela de status — ver R-FLOW-04.

---

## 4. Mapa GitHub ↔ SERMI

Cada issue declara seu **tipo de trabalho** por label, e referencia no corpo o **documento SERMI** que produz ou que a dirige. Isso mantém o board transitório rastreável ao acervo durável.

| Label | Tipo de trabalho | Produz / referencia | Template |
|---|---|---|---|
| `tipo:spec` | escrever ou alterar uma SPEC | produz uma `SPEC-NNN` (a partir de 004) | `spec.yml` |
| `tipo:dec` | registrar uma decisão | produz uma `DEC-NNN` | `dec.yml` |
| `tipo:code` | implementar/alterar módulo | **referencia** a `SPEC-NNN` que o dirige | `code.yml` |
| `tipo:guide` | escrever um guia operacional | produz uma `GUIDE-NNN` | (usa `spec.yml` adaptado ou issue livre) |
| `tipo:eval` | golden set, runner, grader, métrica | referencia a SPEC de eval que o define | `code.yml` |
| `tipo:chore` | infra, repositório, ambiente, board | — | `chore.yml` |

Labels auxiliares: `onda:2`, `onda:3`, `onda:4` (mapeiam o plano de ondas); `bloqueado` (impedimento explícito).

**Princípio de rastreabilidade:** toda issue `tipo:code` cita, no corpo, o número da SPEC que a dirige (campo obrigatório no template). Toda issue que *produz* um documento é fechada apenas quando o documento está commitado **e** registrado no índice correspondente (INDEX_SPEC ou INDEX_DEC).

As labels precisam existir no repositório; criar uma vez com `gh label create` (ou pela interface) antes do primeiro uso.

---

## 5. Definition of Ready e Definition of Done

A passagem entre colunas é governada por dois conjuntos de condições checáveis.

### 5.1 Definition of Ready (para entrar em "Codando")

Um item de código só é puxado para `Codando` quando:

- existe uma **SPEC que o dirige**, com contrato declarado (entradas, saídas com schema, parâmetros, invariantes, modos de falha);
- o item tem **critério de aceitação** claro, rastreável a um `C-NN` (SPEC-002 §5) ou ao contrato da SPEC;
- toda **dependência de stack** que o item introduz já tem DEC registrada (DEC-002; SPEC-002 R-FUN-02).

### 5.2 Definition of Done (para chegar a "Feito")

Um item está `Feito` quando **todas** as condições aplicáveis valem:

| # | Condição | Aplica a |
|---|---|---|
| DoD-1 | A SPEC/DEC que dirige o item existe, está coerente e registrada no índice. | todos |
| DoD-2 | **Eval verde** contra o threshold declarado na SPEC de eval (qualidade do pipeline ASR). | `tipo:code` não-determinístico |
| DoD-3 | **Testes passam** (parsing, mapeamento YAML, geração de SRT — partes determinísticas). | `tipo:code` determinístico |
| DoD-4 | **`gov-check` limpo** (coerência documental, SPEC-001 §11 e SPEC-002 §7). | todos |
| DoD-5 | Commit em **Conventional Commits** com escopo correto (SPEC-001 §10). | todos |

A DoD é a síntese do método: o lean diz *quando* parar (todas as condições verdes), o spec-driven diz *como provar* que se pode parar (eval + gov-check). Um item "pronto" sem DoD-2/DoD-3 verde está **aprovado, não verificado** (GUIDE-001 §2).

---

## 6. Templates de issue

Os formulários de issue vivem em `.github/ISSUE_TEMPLATE/` e forçam, na abertura, o link ao acervo SERMI:

| Arquivo | Issue | Reforça |
|---|---|---|
| `spec.yml` | SPEC técnica | número a partir de 004 (DEC-003); contrato; registro no INDEX_SPEC |
| `dec.yml` | Registro de decisão | atomicidade; ≥ 2 alternativas (R-TAX-08); registro no INDEX_DEC |
| `code.yml` | Implementação de módulo | **campo obrigatório "SPEC que dirige"** (Definition of Ready); natureza determinística vs não-determinística (forma de verificação) |
| `chore.yml` | Tarefa operacional | critério de aceitação |
| `config.yml` | (configuração) | desabilita issue em branco; aponta para SPEC-001 e esta SPEC-004 |

O `code.yml` é o ponto onde o método spec-driven é forçado no nível do board: **não se abre uma issue de código sem declarar a SPEC que a dirige**. Sem SPEC, o fluxo manda abrir primeiro uma issue `tipo:spec`.

---

## 7. Cadência e registro durável do fluxo

O board é transitório; o registro durável do que fluiu vive no acervo SERMI, em dois lugares já previstos:

- **Auditoria recorrente** (SPEC-002 §6): por marco, mensal e por mudança de premissa. Cada rodada de `gov-check` gera log em `docs/logs/`. É também o momento de conferir as regras `R-FLOW` desta SPEC que o gov-check não cobre (§8).
- **BRIEF de período** (`BRIEF_AAAA_MM.md`, SPEC-001 §5): retrato mensal do fluxo — o que foi entregue, o que travou, o que mudou de prioridade. Produzido quando o primeiro mês de fluxo real fechar; não antes, sob pena de BRIEF vazio.

Onde um projeto com equipe teria reunião de revisão de fluxo, este projeto tem o log de auditoria e o BRIEF de período.

---

## 8. Regras checáveis

Esta seção declara regras `R-FLOW-NN` sobre o método de trabalho. **Ressalva honesta de escopo de auditoria**, em dois pontos:

1. O `gov-check` lê **arquivos locais do repositório**, não a API do GitHub. Não enxerga o estado do board (colunas, WIP, labels de issue). Regras sobre o board são verificadas **manualmente na auditoria recorrente** (§7), não automaticamente.
2. O `gov-check` lê regras `R-*` apenas das **SPECs de fundação** (SPEC-001, SPEC-002 e, se existisse, SPEC-003). Esta é a SPEC-004, técnica/de processo: as `R-FLOW` abaixo **não são lidas automaticamente** pelo skill atual. As que forem localmente auditáveis e merecerem automação devem ser migradas para as `R-FUN-*` da SPEC-002 numa versão futura dela (ver §9).

Severidade orienta a decisão na auditoria, como nas demais SPECs.

| ID | Regra | Onde verificar | Auditável por gov-check? | Severidade |
|---|---|---|---|---|
| **R-FLOW-01** | Todo arquivo `src/*.py` tem uma SPEC técnica que o dirige, citada no documento ou rastreável por número. Código sem SPEC é débito, não entrega (DEC-002). | Cruzamento de `src/` com `docs/SPEC/` | Parcial (local) — candidata a R-FUN | Alta |
| **R-FLOW-02** | Toda issue `tipo:code` referencia, no corpo, a SPEC que a dirige (Definition of Ready, §5.1). | Inspeção das issues no GitHub | Não (board) | Alta |
| **R-FLOW-03** | O limite de WIP de "Codando" (≤ 1) é respeitado; itens travados estão marcados `bloqueado`, não duplicados em frentes paralelas. | Inspeção do board | Não (board) | Média |
| **R-FLOW-04** | O plano de ondas/estado de trabalho vive no board, não no `README.md`; o README é vitrine e aponta para o board, sem manter tabela de status detalhada. | Inspeção do `README.md` | Sim (local) | Média |
| **R-FLOW-05** | A cada marco e a cada mês há um registro durável do fluxo (log de auditoria em `docs/logs/` ou BRIEF de período), conforme SPEC-002 §6 e §7 desta SPEC. | Listagem de `docs/logs/` e `docs/BRIEF/` | Sim (local) | Média |

As regras acima são v1 e devem ser calibradas conforme o método for usado.

---

## 9. Critérios de revisão

Esta SPEC-004 é viva e versionável (SPEC-001 §7). Deve ser revisitada quando:

- as colunas ou os limites de WIP se mostrarem mal calibrados na prática (itens parados, fila crescendo numa coluna);
- as regras `R-FLOW` localmente auditáveis (R-FLOW-01, R-FLOW-04, R-FLOW-05) estabilizarem a ponto de valer **migrá-las para as `R-FUN-*` da SPEC-002**, para que o `gov-check` passe a verificá-las automaticamente;
- o projeto deixar de ser solo (DEC-001 §6): com revisor humano, a Definition of Done ganha uma etapa de revisão de par, hoje ausente por desenho;
- o GitHub mudar o modelo de Projects/Issues de forma que afete o mapa da §4;
- o método spec-driven (DEC-002, GUIDE-001) evoluir e alterar a Definition of Ready/Done.

---

## 10. Histórico

| Data | Versão | Evento |
|---|---|---|
| 2026-06-15 | v1 | SPEC-004 produzida em status `proposto`. Primeira SPEC técnica/de processo do projeto, numerada a partir de 004 por força da reserva do slot SPEC-003 (DEC-003). Declara o método de trabalho lean/kanban dirigido por SPEC: o quadro (6 colunas, WIP baixo, ≤ 1 em "Codando"), o mapa GitHub ↔ SERMI (labels e templates), a Definition of Ready e a Definition of Done (eval/testes + gov-check + Conventional Commits), a cadência e o registro durável do fluxo. Fixa a ponte board-transitório/acervo-durável. Declara cinco regras checáveis R-FLOW-01 a R-FLOW-05, com ressalva explícita de que o gov-check atual não as lê automaticamente (só SPECs de fundação) nem enxerga o board. Aguarda revisão e aprovação. |

---

*Fim do documento.*
