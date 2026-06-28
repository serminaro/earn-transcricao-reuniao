---
documento: DEC-005
titulo: Falante em dois campos no JSON (speaker_raw imutável + speaker mapeado)
versao: v1
status: proposto
data: 2026-06-16
autor: Bruno Serminaro
supersede: —
referencia: SPEC-006, SPEC-002, DEC-004
---

# DEC-005 · Falante em dois campos no JSON

> Decisão atômica que define como o falante é representado no JSON fonte de verdade
> ao longo do pipeline: dois campos, `speaker_raw` (label cru do pyannote,
> imutável) e `speaker` (nome real, nulo até o passo 02), em vez de renomear um
> único campo no lugar. Torna o passo 02 idempotente e re-executável, e o
> mapeamento auditável. É a segunda das duas decisões de contrato de dados que
> sustentam a SPEC-006 (a primeira é a DEC-004, sobre o envelope).

---

## 1. Contexto

O pyannote.audio devolve labels genéricos de falante (`SPEAKER_00`, `SPEAKER_01`),
e o passo 02 do pipeline (`02_aplicar_mapeamento.py`) os converte para nomes reais
via o YAML da reunião (SPEC-002 §3.1, decisão herdada D8). O JSON regenerado passa
a ter os nomes corretos.

A SPEC-006 precisa fixar como esse falante vive no schema. A questão concreta é o
que o passo 02 faz com o label cru: substitui o valor no mesmo campo, ou preserva
o cru e escreve o nome real num campo separado.

A escolha tem consequência operacional direta. O passo 02 é descrito como rodável
"quantas vezes forem necessárias até o mapeamento ficar correto" (SPEC-002 §4.1).
Para isso ser verdade sem re-transcrever, o passo 02 precisa de uma entrada estável
para ler a cada nova tentativa de mapeamento. Se ele sobrescreve o label cru na
primeira passada, a segunda passada perde a referência original.

A decisão precisa ser tomada antes de escrever a SPEC-006 e os scripts 01 e 02.

---

## 2. Decisão

**Representar o falante em dois campos, em cada segmento e em cada palavra:
`speaker_raw` (o label cru do pyannote, escrito pelo passo 01 e imutável dali em
diante) e `speaker` (o nome real, nulo após o 01 e preenchido pelo passo 02 a
partir do YAML). Um campo de estágio em `metadata`, `speakers_mapped`, registra se
o mapeamento já foi aplicado.**

A decisão inclui:

- o passo 01 escreve `speaker_raw` com o label do pyannote (ou `null` se a
  diarização não atribuiu falante ao trecho) e deixa `speaker` em `null`;
- o passo 02 lê `speaker_raw`, consulta o `speaker_mapping` do YAML e escreve
  `speaker`, sem nunca tocar em `speaker_raw`; ao final, marca
  `metadata.speakers_mapped = true`;
- o passo 02 é idempotente e re-executável: rodar de novo com um YAML corrigido
  recalcula `speaker` a partir do `speaker_raw` intacto, sem re-transcrever;
- o passo 03 (ata) só consome `speaker` e exige `speakers_mapped = true` (guardrail
  detalhado na SPEC-006 §6).

---

## 3. Origem / rastro

| Artefato | Como sustenta esta decisão |
|---|---|
| **SPEC-002 §3.1 / D8** | Fixa o mapeamento de falantes via YAML por reunião e o passo 02 como rodável várias vezes até ficar certo. Esta DEC é o que torna esse "várias vezes" barato. |
| **DEC-004** | Define o envelope e o campo de estágio `metadata.speakers_mapped` que esta DEC usa. |
| **SPEC-006** | Consome esta decisão: os dois campos aparecem no schema de segmento e de palavra. |
| **SPEC-002 C-02** | "Nenhum `SPEAKER_` residual quando o mapeamento foi aplicado": esta DEC sustenta a verificação ao separar cru de mapeado. |

---

## 4. Alternativas consideradas

### 4.1 Renomear no lugar (um único campo `speaker`)

O passo 01 escreve `speaker = "SPEAKER_00"`; o passo 02 substitui o valor pelo nome
real no mesmo campo.

**Descartada porque:**
- Destrói a entrada estável do passo 02. Uma segunda passada de mapeamento (YAML
  corrigido) não teria mais o label cru para consultar, forçando re-transcrever
  (caro) só para recuperar o `SPEAKER_XX`. Contradiz SPEC-002 §4.1.
- Perde auditabilidade: depois do mapeamento, não há como conferir qual label cru
  virou qual nome, nem detectar um mapeamento trocado.
- Torna a operação não idempotente: o resultado de rodar o 02 duas vezes depende do
  estado anterior do campo.

### 4.2 Histórico de mapeamentos (lista de versões de falante por trecho)

Guardar, além do cru, toda a cadeia de mapeamentos aplicados (uma lista por
segmento/palavra).

**Descartada porque:**
- Overkill para o caso de uso. O que importa é o par (cru, atual); o histórico de
  tentativas de mapeamento não tem consumidor no pipeline.
- Infla o JSON e a complexidade do schema sem necessidade declarada, exatamente o
  viés de "aprendizado inflando complexidade" que o REP-001 §7 marca como risco.
- A rastreabilidade de quando cada mapeamento entrou já vive no Git (o YAML é
  versionado conforme sensibilidade) e no `created_at` do JSON.

---

## 5. Consequências

### 5.1 Consequências positivas

- **Passo 02 idempotente e barato.** Re-mapear é reescrever `speaker` a partir do
  `speaker_raw` intacto, sem re-transcrever. Cumpre SPEC-002 §4.1 de fato.
- **Mapeamento auditável.** O par (`speaker_raw`, `speaker`) deixa conferir qual
  label virou qual nome, e flagrar mapeamento incorreto.
- **Verificação de C-02 direta.** A regra "sem `SPEAKER_` residual após mapeamento"
  vira a checagem de que, com `speakers_mapped = true`, todo `speaker` com mapping
  definido está preenchido (SPEC-006 R-SCHEMA-03).
- **Guardrail simples para o 03.** A flag `speakers_mapped` e a ausência de
  `speaker` nulo dão um gate determinístico para barrar a ata prematura.

### 5.2 Consequências negativas / custo aceito

- **JSON levemente maior.** Duplica o rótulo de falante em cada segmento e palavra.
  Aceito: o custo de armazenamento do JSON já é tratado como trivial (SPEC-002
  §4.3) e a duplicação é de strings curtas.
- **Dois campos a manter coerentes.** O schema e os scripts precisam garantir que
  `speaker` só é escrito pelo 02 e `speaker_raw` nunca é reescrito. Vigiável por
  regra checável (SPEC-006 R-SCHEMA-02).
- **Estado em dois lugares.** A condição "mapeado" vive na flag `speakers_mapped` e
  implicitamente no preenchimento de `speaker`; a SPEC-006 fixa a flag como fonte
  primária e o preenchimento como invariante coerente com ela.

### 5.3 O que esta decisão NÃO resolve

- **Não define o formato do `speaker_mapping`** no YAML: isso é da SPEC do schema de
  configuração por reunião (SPEC técnica futura).
- **Não trata sobreposição de fala** nem o caso de um trecho com dois falantes; o
  schema admite `speaker_raw` nulo, mas a política de diarização é da SPEC do
  script 01.
- **Não decide a qualidade da diarização**, só como o resultado é representado.

---

## 6. Critérios de reavaliação

| Gatilho | O que reavaliar |
|---|---|
| O re-mapeamento sem re-transcrever nunca for usado na prática | O segundo campo perde a justificativa principal; reavaliar se vale manter os dois. |
| O tamanho do JSON virar problema mensurável (improvável dado SPEC-002 §4.3) | Reavaliar a duplicação por palavra, mantendo-a só por segmento. |
| Surgir necessidade de mapeamento por embedding de voz (hoje fora de escopo, SPEC-002 §3.2) | Reavaliar como o falante inferido convive com `speaker_raw`/`speaker`. |

---

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-06-16 | DEC-005 v1 produzida em status `proposto`. Segunda de duas decisões de contrato de dados da SPEC-006. Representa o falante em dois campos (`speaker_raw` imutável + `speaker` mapeado) com a flag `metadata.speakers_mapped`, em vez de renomear um único campo no lugar, para tornar o passo 02 idempotente e re-executável sem re-transcrever e o mapeamento auditável. Descarta o rename-no-lugar e o histórico de mapeamentos. Quinta DEC do projeto. |

---

*Fim do documento.*
