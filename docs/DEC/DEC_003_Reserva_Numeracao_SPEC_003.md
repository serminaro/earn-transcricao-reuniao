---
documento: DEC-003
titulo: Reserva do número SPEC-003 ao eventual Contrato de Responsabilidade; SPECs técnicas a partir de SPEC-004
versao: v1
status: proposto
data: 2026-06-15
autor: Bruno Serminaro
supersede: —
referencia: SPEC-001, DEC-001, SPEC-004
---

# DEC-003 · Reserva do número SPEC-003 ao eventual Contrato de Responsabilidade

> Decisão atômica que reserva o número SPEC-003 para o Contrato de Responsabilidade, a ser produzido apenas se o projeto graduar do perfil solo para o de cinco peças, e fixa que as SPECs técnicas deste projeto começam em SPEC-004. Mantém livre o slot canônico do Contrato sem produzir documento vazio, e ajusta a R-TAX-03 da SPEC-001 para que a lacuna de numeração resultante seja legítima e auditável.

---

## 1. Contexto

A fundação deste projeto é solo (DEC-001): quatro peças (SPEC-001, REP-001, DEC-001, SPEC-002), com a SPEC-003 (Contrato de Responsabilidade) dispensada como documento e seu conteúdo absorvido pela cláusula "Operação Solo" da SPEC-002 §6. No canon SERMI (DEC-META-002), **SPEC-003 é o slot do Contrato de Responsabilidade**: na fundação de cinco peças é a quinta peça; no perfil solo não é produzida.

A Onda 2 do projeto produz SPECs técnicas e de processo — eval, schema de configuração, glossário de áudio/ASR, método de trabalho. Pela R-TAX-03 (numeração sequencial sem reuso), a próxima SPEC seria a de número 003. Isso ocuparia o slot canônico do Contrato com uma SPEC de outra natureza. Se o projeto graduar para cinco peças no futuro (DEC-001 §6: entrada de cliente, sócio, orientador, banca, ou risco a terceiros), o Contrato precisaria do número 003 e não o teria, forçando remanejo de numeração ou um Contrato fora de ordem canônica.

A decisão precisa ser tomada **antes** de criar a primeira SPEC técnica, sob pena de ela já nascer no número errado.

---

## 2. Decisão

**Reservar o número SPEC-003 ao Contrato de Responsabilidade, a ser produzido se e somente se o projeto graduar para a fundação de cinco peças (DEC-001 §6). As SPECs técnicas e de processo deste projeto são numeradas a partir de SPEC-004. Enquanto a graduação não ocorrer, não existe arquivo SPEC-003: o número fica formalmente reservado, não preenchido.**

A decisão inclui:

- ajustar a R-TAX-03 da SPEC-001 (e a §5) para admitir **número formalmente reservado por DEC vigente** como causa legítima de lacuna na numeração, ao lado de `superseded` e `descartado`, de modo que o gov-check não acuse a ausência da SPEC-003 como violação;
- registrar a reserva no INDEX_SPEC, para que a lacuna seja visível ao leitor humano;
- na eventual graduação, produzir a SPEC-003 como Contrato de Responsabilidade pleno e substituir a cláusula "Operação Solo" da SPEC-002 por referência a ela (encadeado com o gatilho de graduação da DEC-001 §6).

---

## 3. Origem / rastro

| Artefato | Como sustenta esta decisão |
|---|---|
| **DEC-001** | Fixou o perfil solo de quatro peças e o gatilho de graduação para cinco peças. Esta DEC protege o número que a graduação exigiria. |
| **SPEC-001 §5 e R-TAX-03** | Regra de numeração sequencial sem reuso que esta DEC ajusta para acomodar a reserva. |
| **DEC-META-002** | Canon SERMI que atribui ao SPEC-003 o papel de Contrato de Responsabilidade na fundação de cinco peças. |
| **SPEC-004** | Primeira SPEC produzida já sob a numeração a partir de 004 decidida aqui. |

---

## 4. Alternativas consideradas

### 4.1 Numerar a próxima SPEC como SPEC-003 (não reservar)

Seguir a R-TAX-03 ao pé da letra e dar à próxima SPEC técnica o número 003.

**Descartada porque:** ocupa o slot canônico do Contrato de Responsabilidade com um documento de outra natureza. Numa graduação futura, o Contrato não teria o número 003, quebrando a correspondência canônica do SERMI e forçando remanejo de numeração ou um Contrato fora de ordem — exatamente o retrabalho que a fundação existe para evitar.

### 4.2 Criar um arquivo SPEC-003 "stub", marcado como reservado ou não aplicável

Materializar um `SPEC_003_*.md` com frontmatter e status especial, declarando que está reservado.

**Descartada porque:** contradiz a R-TAX-10 ("não se exige SPEC-003") e a cláusula "Operação Solo", que dispensam o documento por desenho; reintroduz a "peça vazia por princípio" que a DEC-META-004 §4.2 rejeitou; e confunde a detecção de perfil do gov-check (quatro vs cinco peças), que poderia ler o stub como tentativa de fundação de cinco peças e cobrar um Contrato pleno. Reservar um número é mais barato e mais honesto que produzir um documento cujo único conteúdo é declarar-se vazio.

---

## 5. Consequências

### 5.1 Consequências positivas

- **Slot canônico preservado.** A graduação para cinco peças, se vier, encontra o número 003 livre para o Contrato, sem remanejo.
- **Sem documento vazio.** A reserva é um registro em DEC, não um arquivo ornamental.
- **Lacuna auditável.** O ajuste da R-TAX-03 torna a ausência da SPEC-003 uma lacuna *legítima e justificada*, não um falso-positivo de severidade Crítica do gov-check.
- **Coerência cross-projeto.** Mantém o significado canônico de SPEC-003 igual ao dos demais projetos do autor.

### 5.2 Consequências negativas / custo aceito

- **Numeração não-contígua de SPEC.** A sequência passa a ser 001, 002, [003 reservado], 004, … O leitor precisa saber da reserva para não ler a lacuna como erro. Mitigado pelo registro na R-TAX-03, no INDEX_SPEC e nesta DEC.
- **Mais uma regra de exceção na taxonomia.** A R-TAX-03 ganha um terceiro caso de lacuna legítima (reserva), aumentando levemente a carga cognitiva da regra.
- **Edição de uma peça de fundação.** Ainda que dentro da v1 (status `proposto`, §7), mexer na SPEC-001 para acomodar uma decisão de processo tem custo de cuidado.

### 5.3 O que esta decisão NÃO resolve

- **Não produz o Contrato de Responsabilidade** nem antecipa a graduação: apenas reserva o número. A graduação segue governada pela DEC-001 §6.
- **Não numera as demais SPECs técnicas** além de fixar o ponto de partida (004); cada SPEC recebe seu número na ordem em que for produzida.
- **Não altera o perfil solo** nem a R-TAX-10: SPEC-003 continua não exigida; passa apenas a estar reservada.

---

## 6. Critérios de reavaliação

| Gatilho | O que reavaliar |
|---|---|
| O projeto graduar para a fundação de cinco peças (DEC-001 §6) | A reserva se cumpre: produzir a SPEC-003 como Contrato de Responsabilidade pleno e substituir a cláusula "Operação Solo" da SPEC-002 por referência a ela. |
| O canon SERMI mudar a convenção de numeração ou o papel do SPEC-003 | Realinhar esta reserva à nova convenção. |
| A regra de lacuna por reserva gerar ambiguidade no gov-check (reservas múltiplas, reserva nunca cumprida) | Calibrar a R-TAX-03 ou registrar prazo/condição de expiração da reserva. |

---

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-06-15 | DEC-003 v1 produzida em status `proposto`. Reserva o número SPEC-003 ao eventual Contrato de Responsabilidade (produzido só na graduação para cinco peças, DEC-001 §6) e fixa as SPECs técnicas a partir de SPEC-004. Ajusta a R-TAX-03 e a §5 da SPEC-001 (dentro da v1, status `proposto`) para admitir número reservado por DEC como lacuna legítima de numeração. Terceira DEC do projeto. |

---

*Fim do documento.*
