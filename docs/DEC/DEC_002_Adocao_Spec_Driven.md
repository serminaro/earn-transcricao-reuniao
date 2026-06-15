---
documento: DEC-002
titulo: Adoção do desenvolvimento dirigido por SPEC (spec-driven) para construir o pipeline
versao: v1
status: proposto
data: 2026-06-14
autor: Bruno Serminaro
supersede: —
referencia: GUIDE-001, SPEC-002, GUIDE-META-001
---

# DEC-002 · Adoção do desenvolvimento dirigido por SPEC (spec-driven)

> Decisão atômica que adota, para a construção do pipeline de transcrição, o
> método de desenvolvimento dirigido por SPEC: a SPEC dirige o código e o eval
> prova. O método em si está descrito no GUIDE-001; esta DEC registra a decisão
> de adotá-lo, suas alternativas e consequências.

---

## 1. Contexto

A fundação documental do projeto está concluída (Onda 1). O que vem a seguir é
código: as SPECs e DECs técnicas da Onda 2 e os três scripts da Onda 3. Falta
decidir **como** construir, antes de escrever a primeira linha.

Duas características do projeto tornam essa decisão não-trivial. É um projeto
solo, sem revisor externo que contradiga uma escolha ruim. E o produto central é
um pipeline de ASR, que é não-determinístico: a mesma entrada pode gerar saídas
diferentes, e "funciona" não se reduz a um teste binário. O risco concreto é
construir por impressão ("a transcrição pareceu boa") sem medição, que é
exatamente o modo de falha que a fundação existe para evitar.

O GUIDE-META-001 (Engenharia de Harness) e a moldura SERMI dão a resposta: a SPEC
no comando, como contrato e como gabarito, e a verificação em dois planos
(documental e funcional). Esta DEC fixa essa resposta como método do projeto.

---

## 2. Decisão

**Adotar o desenvolvimento dirigido por SPEC (spec-driven) para toda a construção
do pipeline (Ondas 2 e 3), conforme operacionalizado no GUIDE-001: nenhum script
nasce sem uma SPEC que o dirija, e nenhum script é dado como pronto sem um eval
que o meça contra os critérios declarados na SPEC.**

A decisão inclui:

- escrever a SPEC técnica de cada módulo antes do código, com contrato (entradas,
  saídas com schema, parâmetros, invariantes, modos de falha);
- registrar toda escolha de stack ou dependência como DEC atômica antes de codar;
- verificar em dois planos distintos: `gov-check` para a coerência documental, e
  um eval (golden set, runner, grader, métrica) para a qualidade funcional do
  pipeline ASR;
- resolver divergências pelo fluxo de dois caminhos (atualizar a SPEC ou corrigir
  o código), com registro.

---

## 3. Origem / rastro

| Artefato | Como sustenta esta decisão |
|---|---|
| **GUIDE-META-001** (Engenharia de Harness) | Estabelece que harness e governança são o mesmo movimento; fornece os seis ciclos (com evals e loops de verificação) que o método aplica. |
| **GUIDE-001** | Operacionaliza esta decisão: descreve o ciclo SDD em sete passos, os dois planos de verificação e a Definition of Done. |
| **SPEC-002** | Já declara os critérios `C-NN` e as regras `R-FUN-NN` que o método usa como gabarito. |
| **skill gov-check** | Implementa o plano de verificação documental. |
| **Briefing §12.4** | "Não adicionar dependência sem registro em DEC" é parte do método (passo 2). |

---

## 4. Alternativas consideradas

### 4.1 Code-first / ad-hoc

Escrever os scripts direto e documentar depois, se necessário.

**Descartada porque:** inverte a ordem (código antes do contrato), perde o
gabarito contra o qual medir, e num projeto solo e não-determinístico degrada
para "pareceu bom" sem medição. É o anti-padrão que a fundação foi feita para
evitar.

### 4.2 TDD clássico (testes binários antes do código)

Escrever testes `assert igual` antes de cada função e implementar até passarem.

**Descartada como método principal porque:** `assert igual` não serve a software
não-determinístico (a transcrição varia, não há saída única "correta"). A forma
adequada para ASR é o eval, uma métrica sobre um golden set, não um teste binário.
O TDD continua válido para as partes **determinísticas** do pipeline (parsing do
JSON, aplicação do mapeamento YAML, geração do SRT), e o GUIDE-001 o acomoda
nessas partes; mas TDD sozinho não cobre a qualidade da transcrição, que é o
cerne do projeto.

### 4.3 Confiar apenas no gov-check

Tratar a auditoria documental como verificação suficiente.

**Descartada porque:** a `gov-check` mede coerência documental, não qualidade
funcional. Uma transcrição péssima passa nela sem divergência. Confundir os dois
planos é o erro conceitual que o GUIDE-001 §5 existe para impedir.

---

## 5. Consequências

### 5.1 Positivas

- **Gabarito explícito.** A qualidade deixa de ser impressão e passa a ser número
  medido contra uma referência conferida à mão.
- **Regressão detectável.** Métrica por rodada permite ver se uma mudança piorou
  a transcrição.
- **Freio funcional além do documental.** O eval cumpre, na qualidade, o papel
  que o par humano cumpriria; complementa o freio documental da auditoria.
- **Coerência com o harness e o SERMI.** O método é a aplicação direta do
  GUIDE-META-001; reaproveita o vocabulário e as skills já existentes.
- **Aprendizado técnico ancorado.** O subobjetivo de aprender ASR ganha um trilho
  disciplinado em vez de tentativa e erro solta.

### 5.2 Negativas / custo aceito

- **Custo de montar e manter o golden set.** Exige reuniões curtas com
  transcrição de referência conferida à mão, material sensível que vive fora do
  Git. É trabalho recorrente e não trivial.
- **Overhead de escrever a SPEC antes de cada script.** Atrasa o início do
  código em troca de um contrato verificável.
- **Eval de ASR é trabalhoso.** WER e erro em nomes exigem referência cuidada;
  qualidade da ata não tem gabarito objetivo e fica para julgamento.
- **Risco de cerimônia.** SPEC ou eval produzidos "para cumprir" e nunca usados
  reproduzem o viés cerimonial que a fundação combate.

### 5.3 O que NÃO resolve

- **Não garante que o pipeline fique bom.** O método mede a qualidade, não a
  produz; transcrição ruim continua ruim, apenas deixa de passar despercebida.
- **Não substitui as decisões técnicas de stack.** WhisperX, modelo,
  `compute_type` e demais seguem sendo DECs próprias (Onda 2).
- **Não escreve as SPECs técnicas.** Define o método; o conteúdo de cada SPEC é
  trabalho da Onda 2.

---

## 6. Critérios de reavaliação

| Gatilho | O que reavaliar |
|---|---|
| O eval virar ritual oco (montado e não rodado, ou referência gameada) | O freio funcional some. Retomar o eval de fato, ou rever o que está sendo medido para que volte a poder surpreender. |
| Alguma etapa do pipeline ser inteiramente determinística | Para essa etapa, TDD clássico pode bastar; ajustar o método sem abandoná-lo para o restante. |
| O projeto deixar de ser solo (entra cliente, sócio, orientador) | Revisitar junto com a graduação da fundação (DEC-001): com revisor humano, o equilíbrio entre eval e revisão de par muda. |
| GUIDE-META-001 ou a moldura SERMI evoluírem de forma que altere os ciclos de verificação | Alinhar o método à nova versão. |

---

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-06-14 | DEC-002 v1 produzida em status `proposto`. Adota o desenvolvimento dirigido por SPEC (spec-driven) para a construção do pipeline (Ondas 2 e 3), operacionalizado no GUIDE-001 e ancorado no GUIDE-META-001 (Engenharia de Harness). Registra três alternativas descartadas (code-first, TDD clássico como método principal, confiar só na gov-check) e a distinção entre os dois planos de verificação. Segunda DEC do projeto, posterior à DEC-001 (fundação). |

---

*Fim do documento.*
