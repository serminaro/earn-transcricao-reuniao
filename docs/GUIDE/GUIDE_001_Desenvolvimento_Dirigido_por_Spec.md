---
documento: GUIDE-001
titulo: Desenvolvimento dirigido por SPEC (spec-driven) para o pipeline de transcrição
versao: v1
status: proposto
data: 2026-06-14
autor: Bruno Serminaro
supersede: —
referencia: DEC-002, SPEC-002, SPEC-001, GUIDE-META-001
---

# GUIDE-001 · Desenvolvimento dirigido por SPEC (spec-driven)

> Descreve como construir o pipeline de transcrição deste projeto com a SPEC no
> comando: a SPEC dirige o código, e o eval prova que o código faz o que a SPEC
> promete. É a aplicação, a este projeto, da engenharia de harness do
> GUIDE-META-001 (os seis ciclos) e da moldura SERMI. É guia operacional,
> descreve *como fazer*; a decisão de adotar o método está na DEC-002.

---

## 1. Objetivo

Ao final, o projeto tem um método repetível para construir cada parte do
pipeline (`01_transcrever`, `02_aplicar_mapeamento`, `03_gerar_ata`) de modo que
nenhum script nasça sem uma SPEC que o dirija nem sem um eval que o meça.

A motivação é a mesma do harness (GUIDE-META-001 §2): tornar confiável um
executor falível. Aqui há três executores falíveis ao mesmo tempo:

| Executor falível | Por que falha | Andaime que a SPEC oferece |
|---|---|---|
| O LLM que ajuda a codar | gera código plausível, nem sempre correto | a SPEC é o contrato contra o qual o código é conferido |
| O autor solo | sem revisor externo, viés de confirmação | a SPEC é o freio impessoal; o eval mede no lugar do par humano |
| O pipeline ASR | não-determinístico, erra transcrição e diarização | a SPEC declara o critério, o eval quantifica o erro |

A SPEC é o andaime para os três. Sem ela, "solo" degrada para "ninguém olhando"
e "funciona" degrada para "pareceu bom".

---

## 2. Princípio: a SPEC dirige o código, o eval prova

Dois movimentos, um só princípio (P7 do harness: *aprovado não é verificado*).

1. **A SPEC é a fonte.** O que o script faz, suas entradas e saídas, seus
   invariantes e modos de falha vivem na SPEC antes de existir código. O código e
   os testes derivam da SPEC, nunca o contrário. Código sem SPEC que o anteceda é
   débito, não entrega.
2. **O eval é a prova.** A SPEC declara critérios de sucesso `C-NN` e regras
   auditáveis `R-FUN-NN`. Cumprir a SPEC não é opinião do autor: é medição contra
   um gabarito. Um script "pronto" sem eval que o meça está aprovado, não
   verificado.

> A SPEC é, ao mesmo tempo, **contrato** (o que construir) e **gabarito** (contra
> o que medir). Essas duas funções são o que liga este método aos Ciclos 4 e 6
> do harness.

---

## 3. O ciclo SDD, ancorado no harness

Sete passos, por script ou módulo. Cada passo realiza um ciclo de harness
(GUIDE-META-001).

| Passo | O que fazer | Ciclo / princípio de harness |
|---|---|---|
| 1. SPEC primeiro | Escrever a SPEC do módulo: contrato (entradas, saídas, invariantes, parâmetros, modos de falha). Zero código antes. | Ciclo 6 (a SPEC é o gabarito) · P7 |
| 2. Decisão vira DEC | Toda escolha com trade-off (dependência, parâmetro de stack, formato de saída) entra como DEC atômica antes de codar. | Ciclo 2 (atomicidade) · briefing §12.4 |
| 3. Derivar a verificação | Da SPEC saem os `C-NN` (aceitação funcional) e as `R-FUN-NN` (invariantes auditáveis). | Ciclo 6 (golden set, runner, grader, métrica) · P4 |
| 4. Implementar contra a SPEC | O código realiza a SPEC, cita a SPEC, e nada faz fora dela. | P2 (menor privilégio) · Ciclo 1 (contexto) |
| 5a. Verificar o documental | Rodar `gov-check`: a SPEC declara regras, o projeto as cumpre. Determinístico. | Ciclo 4 (loops de verificação) |
| 5b. Verificar o funcional | Rodar o eval do pipeline sobre o golden set; conferir os `C-NN`. | Ciclo 6 (evals) · Ciclo 4 (P5: achado é hipótese até refutar) |
| 6. Divergência → dois caminhos | Realidade diferente da SPEC: (a) atualizar a SPEC (viva) ou (b) corrigir o código. Nunca corrigir sozinho; registrar. | DEC-META-002 §7.4 · Ciclo 4 |
| 7. Registrar o marco | REP quando houver execução real relevante; BRIEF no fechamento; AUDIT no registro de auditoria. | Ciclo 5 (persistência) · P6 |

> O passo 5 tem duas metades que medem coisas diferentes (§5). Pular a 5b é o erro
> mais fácil de cometer e o mais caro: o pipeline parece pronto e ninguém mediu se
> transcreve bem.

---

## 4. A SPEC como contrato e gabarito

A SPEC técnica de cada script (a produzir na Onda 2) declara, no mínimo:

| Elemento do contrato | Conteúdo |
|---|---|
| Entradas | o que o script consome (áudio, JSON do passo anterior, config YAML, `initial_prompt`) |
| Saídas | o que produz, com **schema** explícito (ex.: a estrutura do JSON fonte de verdade) |
| Parâmetros | o que é configurável por CLI e o que é fixo por decisão (ex.: `condition_on_previous_text=False` hardcoded) |
| Invariantes | o que sempre vale (JSON é fonte de verdade; nenhuma chamada de rede a ASR externo) |
| Modos de falha | como falha e o que faz nesse caso (HF_TOKEN ausente → falhar cedo com mensagem útil) |

Da SPEC derivam dois tipos de verificação, que **não** se confundem:

- **`C-NN` (critério de sucesso)**: aceitação funcional, conferida pelo eval (ex.:
  "gera JSON, TXT e SRT com a mesma raiz").
- **`R-FUN-NN` (regra auditável)**: invariante de coerência, conferida pela
  `gov-check` ou por inspeção (ex.: "nenhum áudio versionado no Git").

A SPEC-002 já declara `C-01` a `C-09` e `R-FUN-01` a `R-FUN-08`. As SPECs técnicas
da Onda 2 refinam esses critérios por etapa do pipeline.

---

## 5. Os dois planos de verificação

A confusão entre os dois planos é o erro conceitual mais comum. São
complementares e medem coisas distintas.

### 5.1 Plano documental: gov-check

A skill `gov-check` confronta o que as SPECs declaram com o estado real dos
documentos e do repositório: frontmatter, numeração, referências cruzadas,
regras `R-*`, peças fundacionais. É determinística (exit 0/1/2). Responde: *o
projeto está coerente com o que ele mesmo declarou?*

O que ela **não** responde: se a transcrição está boa. Uma transcrição péssima
passa na `gov-check` sem um arranhão.

### 5.2 Plano funcional: o eval do pipeline

Software de ASR é não-determinístico: não se testa com `assert igual`
(GUIDE-META-001 §9). Mede-se com um eval, uma métrica sobre um conjunto de casos
com gabarito conhecido. As quatro peças do eval, aplicadas a este pipeline:

| Peça | Neste projeto |
|---|---|
| **Golden set** | uma a três reuniões curtas (5 a 10 min) com transcrição de referência conferida à mão e mapeamento de falantes conhecido. É material sensível: vive local, fora do Git (gitignored), como o resto do áudio |
| **Runner** | o próprio pipeline (`01` → `02` → `03`) rodando sobre o golden set |
| **Grader** | métricas de erro: WER global, erro em termos próprios e nomes (o que mais importa em reunião técnica), acerto de diarização (fração de fala atribuída ao falante certo). Onde dá, grader programático (saída × referência); a qualidade da ata, que não tem gabarito objetivo, fica para julgamento |
| **Métrica** | um número agregado por rodada, comparável ao longo do tempo para flagrar regressão |

Princípios do eval (Ciclo 6, obrigatórios):

1. **Grader programático onde der.** WER e erro em nomes são contáveis em código;
   não terceirize ao LLM-juiz o que um diff resolve.
2. **Gabarito independente da ferramenta.** A referência do golden set é conferida
   à mão, nunca gerada pelo próprio pipeline. Medir o pipeline contra a saída dele
   mesmo não prova nada.
3. **Um eval só vale se pode surpreender.** Se ele nunca pode falhar, não mede
   nada.
4. **Nunca gamear.** Ao divergir, investigar de que lado está o erro. Jamais
   ajustar a referência para o pipeline "passar". Gamear o próprio teste é o
   pecado capital (P7).

> O eval é o que substitui, em projeto solo, o par humano que diria "essa
> transcrição está ruim". Sem ele, a qualidade funcional não tem freio.

---

## 6. Persistência: congelar o "sempre-faça-assim"

Comportamento recorrente não mora na cabeça do autor nem na memória do agente:
vira hook, skill ou cron (Ciclo 5, P6). Candidatos neste projeto:

- **Hook (determinístico):** barrar `03_gerar_ata` quando o JSON ainda contém
  `SPEAKER_XX` (sinal de que o mapeamento do passo 02 não foi aplicado). É um
  invariante do pipeline, então é guardrail de harness, não lembrete.
- **Skill / script de eval:** rodar o runner sobre o golden set e imprimir a
  métrica, para virar um comando único e repetível.
- **gov-check:** já é a persistência do plano documental (§5.1).

> A regra `R-*` é a memória do que deve ser verdade; a skill ou o hook que a
> verifica é a automação. Quando se pegar dizendo "da próxima vez, lembrar de
> X", o lugar de X é um hook ou uma skill, não uma boa intenção.

---

## 7. Encaixe nas Ondas

| Onda | Papel no SDD |
|---|---|
| 2. Documentação técnica | escreve os **contratos**: a(s) SPEC(s) técnica(s) que dirigem `01/02/03` e as DECs de stack (D1 a D11). Aqui nascem os `C-NN` e `R-FUN` por etapa |
| 3. Código | **implementa** cada script contra a sua SPEC e fecha o ciclo de verificação (5a + 5b) |
| 4. Integração do orquestrador | **persiste** a operação no `CLAUDE.md` (Claude Code orquestra o pipeline neste Linux) |

A ordem do método é a ordem das ondas: contrato antes do código, código antes da
prova, prova antes do "pronto". O mapa exato de qual SPEC dirige qual script é
fixado na Onda 2.

---

## 8. Definition of Done por script

Um script só está pronto quando **todos** os itens são verdadeiros:

- [ ] A SPEC do script existe e está em `proposto` ou `aprovado`, com contrato
      completo (entradas, saídas com schema, parâmetros, invariantes, modos de
      falha).
- [ ] Toda dependência e todo parâmetro de stack do script têm DEC; o
      `environment.yml` foi atualizado no mesmo commit da DEC que autoriza.
- [ ] Os `C-NN` de aceitação e as `R-FUN` auditáveis estão derivados da SPEC.
- [ ] A implementação cita a SPEC e não faz nada fora dela.
- [ ] O eval roda sobre o golden set e a métrica foi registrada (baseline na
      primeira vez, comparação com a rodada anterior depois).
- [ ] `gov-check` retorna exit 0 (coerência documental).
- [ ] Toda divergência foi resolvida pelos dois caminhos (atualizar SPEC ou
      corrigir código), com o resultado registrado.

---

## 9. Erros comuns

| Erro | Como evita |
|---|---|
| Código antes da SPEC | A SPEC é o passo 1. Código sem SPEC que o anteceda é débito. |
| SPEC ornamental, que não dirige nada | Se o código não pode ser conferido contra a SPEC, a SPEC está vaga demais; ela precisa declarar contrato e critérios verificáveis. |
| Confundir gov-check com eval | `gov-check` mede o documental; o eval mede o funcional. Passar num não diz nada sobre o outro (§5). |
| Gamear o eval | Nunca ajustar a referência para o pipeline passar. Ao divergir, achar de que lado está o erro. |
| Achado de uma rodada tratado como fato | Uma medição é hipótese até repetir ou refutar (P5). Variação de ASR entre rodadas existe; meça mais de uma vez antes de concluir. |
| Golden set gerado pelo próprio pipeline | O gabarito tem de ser independente: referência conferida à mão, não saída da ferramenta. |

---

## 10. Exemplo aplicado a `01_transcrever`

O loop inteiro, concreto, para o primeiro script.

1. **SPEC primeiro.** Contrato: entrada áudio (mais `initial_prompt` opcional);
   saída JSON (schema com `segments[]`, `words[]`, timestamps, `speaker`, score),
   TXT e SRT com `SPEAKER_XX`; parâmetros fixos `large-v3`, `int8`,
   `condition_on_previous_text=False`, VAD ativo; invariantes: JSON é fonte de
   verdade, nenhuma chamada de rede a ASR externo; modos de falha: `HF_TOKEN`
   ausente falha cedo, VRAM insuficiente reduz `batch_size`.
2. **Decisões viram DEC.** WhisperX (D1), `large-v3` (D2), `int8` (D3),
   `condition_on_previous_text=False` (D4), VAD (D5), `initial_prompt` (D6), três
   saídas (D7). Cada uma é DEC própria na Onda 2; o `environment.yml` ganha
   `whisperx`, `pyannote.audio` e `torch` no commit das respectivas DECs.
3. **Derivar verificação.** `C`: gera os três arquivos com a mesma raiz; processa
   local; o JSON é parseável conforme o schema. `R-FUN`: nenhuma chamada de rede
   a ASR; nenhum áudio versionado.
4. **Implementar contra a SPEC.** O script realiza exatamente o contrato; cada
   bloco corresponde a um item da SPEC.
5. **Verificar.** (5a) `gov-check` exit 0. (5b) eval: golden set de uma reunião de
   5 min com referência conferida à mão; grader mede WER e erro em nomes próprios;
   registra-se o baseline. Oportunidade: rodar também com `medium` e comparar,
   confirmando empiricamente a hipótese do REP-001 §5 (ganho do `large-v3` sobre
   `medium` em PT-BR) em vez de assumi-la.
6. **Dois caminhos.** Se o erro em nomes for alto, a correção pode ser refinar o
   `initial_prompt` (corrige o uso) ou revisar a SPEC do parâmetro (corrige o
   contrato). A escolha é registrada.
7. **Registrar.** A primeira execução real vira um REP, com RTF medido (tempo de
   processamento por duração de áudio) e os números do eval.

---

## 11. Histórico

| Data | Versão | Evento |
|---|---|---|
| 2026-06-14 | v1 | GUIDE-001 produzido em status `proposto`. Primeiro guia operacional do projeto. Descreve o desenvolvimento dirigido por SPEC (spec-driven) para construir o pipeline, em sete passos ancorados nos seis ciclos de harness do GUIDE-META-001. Fixa a distinção entre os dois planos de verificação (gov-check documental e eval funcional do pipeline ASR) e a Definition of Done por script. Operacionaliza a decisão registrada na DEC-002. Aguarda revisão e aprovação. |

---

*Fim do documento.*
