---
documento: SPEC-006
titulo: Schema do JSON fonte de verdade (contrato de dados do pipeline)
versao: v1
status: proposto
data: 2026-06-16
autor: Bruno Serminaro
supersede: —
referencia: SPEC-002, GUIDE-001, SPEC-005, DEC-004, DEC-005, DEC-003, SPEC-001
---

# SPEC-006 · Schema do JSON fonte de verdade (contrato de dados)

> Fixa o schema do JSON que é a fonte de verdade do pipeline: a estrutura que o
> `01_transcrever` produz e que `02_aplicar_mapeamento` e `03_gerar_ata` consomem.
> É a espinha do contrato spec-driven: a SPEC de cada módulo (a produzir) declara
> entradas e saídas referenciando este schema, em vez de redescrever a forma do
> JSON. Sem este contrato, a exigência do GUIDE-001 §4 de "saídas com schema
> explícito" fica sem referente. O schema é carregado também como artefato
> executável em `data/schema/transcricao.schema.json` (JSON Schema Draft 2020-12),
> para que a conformidade seja medida, não descrita. Numerada a partir de 006 por
> força da reserva do slot SPEC-003 (DEC-003).

---

## 1. Propósito

### 1.1 Por que um contrato de dados explícito

O JSON é a fonte de verdade do pipeline (SPEC-002 §4.3): TXT, SRT e ata derivam
dele, e reprocessar não exige re-transcrever. Três scripts dependem da mesma
estrutura: o 01 a produz, o 02 a reescreve com nomes de falante, o 03 a lê para
gerar a ata. Se cada script carregar na cabeça do autor a sua própria ideia de
como o JSON é, eles divergem em silêncio, e o erro só aparece quando um campo
esperado falta em produção.

O método spec-driven (DEC-002, GUIDE-001) manda que a SPEC declare o contrato antes
do código. Para os três módulos, esse contrato tem um núcleo comum: a forma do JSON.
Esta SPEC fixa esse núcleo uma vez, e as SPECs de módulo o referenciam, evitando
três descrições concorrentes da mesma coisa.

### 1.2 O que esta SPEC fixa e o que delega

| Esta SPEC fixa | Esta SPEC delega |
|---|---|
| A estrutura do JSON fonte de verdade: objeto raiz, metadados, segmentos, palavras, falante. | O schema do **YAML de configuração** por reunião (SPEC técnica futura). |
| Os invariantes do JSON e os modos de falha de validação. | O formato da **ata** `_ata.md` (responsabilidade da SPEC do script 03). |
| O versionamento do próprio schema. | Os **parâmetros de stack** e seus valores (WhisperX, `large-v3`, `int8`): cada um é DEC própria; aqui só se fixa que os valores usados são gravados no JSON. |
| As regras checáveis `R-SCHEMA-NN` sobre conformidade. | O **comportamento** de cada script (diarização, alinhamento, chamada de LLM): das SPECs de módulo. |

Duas decisões de forma deste schema têm trade-off e por isso são DEC próprias,
referenciadas aqui: o **envelope com metadados** (DEC-004) e o **falante em dois
campos** (DEC-005).

---

## 2. Posição no pipeline

O JSON é produzido uma vez pelo script 01 e consumido pelos passos seguintes sem
re-transcrição. O que muda entre as etapas é apenas o campo de falante.

```
[01_transcrever]   produz o JSON: metadata.speakers_mapped = false,
                   speaker_raw preenchido (label do pyannote), speaker = null
        │
        ▼
[02_aplicar_mapeamento]   lê speaker_raw, escreve speaker a partir do YAML,
                          marca metadata.speakers_mapped = true; NÃO toca speaker_raw
        │
        ▼
[03_gerar_ata]   lê speaker (exige speakers_mapped = true); nunca re-invoca o WhisperX
```

Invariante de fluxo: nenhum consumidor (02, 03) re-invoca o ASR. Tudo que precisam
está no JSON. Essa é a razão de o JSON existir como fonte de verdade (SPEC-002
C-05).

---

## 3. Visão geral do schema

O objeto raiz tem três campos de topo (DEC-004):

| Campo | Tipo | Papel |
|---|---|---|
| `schema_version` | string `MAJOR.MINOR` | Versão do contrato; esta SPEC define a `1.0`. |
| `metadata` | objeto | Proveniência da execução: áudio, modelo, parâmetros, estágio. |
| `segments` | array de segmento | A transcrição, em ordem temporal não-decrescente. |

A forma autoritativa e checável é o artefato `data/schema/transcricao.schema.json`.
As tabelas abaixo descrevem o mesmo contrato em prosa; em caso de divergência entre
a prosa e o artefato, prevalece o artefato (e a divergência é corrigida como erro,
não interpretada).

---

## 4. Schema detalhado por nível

### 4.1 Objeto raiz

Campos `schema_version`, `metadata`, `segments`, todos obrigatórios. Sem campos
adicionais no topo (`additionalProperties: false`): um campo desconhecido no raiz é
erro de conformidade, não extensão tolerada.

### 4.2 Bloco `metadata` (proveniência da execução)

Registra como a transcrição foi gerada (DEC-004). Mínimo obrigatório:

| Campo | Tipo | Significado |
|---|---|---|
| `audio_source` | string | Nome do arquivo de áudio de origem, sem caminho absoluto. |
| `created_at` | string ISO 8601 | Instante de geração do JSON. |
| `model` | string | Modelo Whisper usado (ex.: `large-v3`). |
| `compute_type` | string | Precisão usada (ex.: `int8`, `float16`). |
| `language` | string | Código do idioma (ex.: `pt`). |
| `speakers_mapped` | booleano | `false` após o 01; `true` após o 02 (DEC-005). |
| `params` | objeto | Parâmetros de stack efetivamente usados (abaixo). |
| `pipeline_version` | string ou null | Commit/versão do código gerador; null se indisponível. |

`metadata.params` exige no mínimo `condition_on_previous_text`, `vad` e
`initial_prompt_used` (booleanos), e admite extensão (ex.: `batch_size`). O bloco
admite campos adicionais (`additionalProperties: true`): proveniência futura pode
crescer sem quebrar o contrato.

### 4.3 Segmento

Cada item de `segments` é um objeto com todos os campos obrigatórios e sem campos
adicionais:

| Campo | Tipo | Significado |
|---|---|---|
| `start` | número ≥ 0 | Início do segmento, em segundos. |
| `end` | número ≥ 0 | Fim do segmento, em segundos; `end >= start`. |
| `text` | string | Texto do segmento. |
| `speaker_raw` | string ou null | Label cru do pyannote; null se não atribuído (DEC-005). |
| `speaker` | string ou null | Nome real; null até o 02 (DEC-005). |
| `words` | array de palavra | Palavras word-level; pode ser vazio se o alinhamento falhar. |

### 4.4 Palavra (word-level)

Cada item de `words`:

| Campo | Tipo | Significado |
|---|---|---|
| `word` | string | A palavra. |
| `start` | número ≥ 0 ou null | Início; null se o alinhamento não a posicionou. |
| `end` | número ≥ 0 ou null | Fim; null se o alinhamento não a posicionou. |
| `score` | número em [0,1] ou null | Confiança do alinhamento; null se indisponível. |
| `speaker_raw` | string ou null | Label cru do pyannote para a palavra. |
| `speaker` | string ou null | Nome real para a palavra; null até o 02. |

Obrigatórios: `word`, `speaker_raw`, `speaker`. Os timestamps e o score são
admitidos nulos porque o WhisperX nem sempre alinha toda palavra (números,
pontuação, trechos de baixa confiança); tratá-los como sempre presentes seria
mentir sobre a saída real da ferramenta.

### 4.5 Falante e sua evolução

O falante vive em dois campos em cada nível (DEC-005):

- `speaker_raw`: escrito pelo 01 com o label do pyannote, **imutável** dali em
  diante. O 02 nunca o reescreve.
- `speaker`: nulo após o 01; preenchido pelo 02 a partir do `speaker_mapping` do
  YAML, lendo `speaker_raw`. Re-rodar o 02 com um YAML corrigido recalcula
  `speaker` a partir do `speaker_raw` intacto, sem re-transcrever.

A flag `metadata.speakers_mapped` é a fonte primária do estágio. Coerência exigida:
quando `speakers_mapped = true`, todo `speaker_raw` com mapeamento definido no YAML
tem `speaker` preenchido (R-SCHEMA-03, cumpre SPEC-002 C-02).

---

## 5. Invariantes do contrato

O que sempre vale num JSON conforme:

| ID | Invariante |
|---|---|
| INV-1 | **O JSON é a fonte de verdade.** 02 e 03 leem dele; nenhum re-invoca o WhisperX (SPEC-002 C-05). |
| INV-2 | **Tempos coerentes.** Em todo segmento, `0 <= start <= end`. A sequência de `segments` é não-decrescente por `start`. |
| INV-3 | **Palavra dentro do segmento.** Quando os timestamps da palavra existem, ficam dentro de `[start, end]` do segmento que a contém. |
| INV-4 | **`speaker_raw` imutável.** Escrito só pelo 01; nunca alterado pelo 02 ou 03 (DEC-005). |
| INV-5 | **Estágio coerente.** Se `speakers_mapped = true`, nenhum `speaker` é nulo onde o YAML define mapeamento para o seu `speaker_raw`. |
| INV-6 | **Proveniência presente.** `metadata` declara `model`, `compute_type` e `params` realmente usados (DEC-004); metadado incoerente é divergência, não detalhe. |

INV-2, INV-3 e os tipos são checados pelo artefato de schema mais validação
programática; INV-1 e INV-4 são invariantes de comportamento dos scripts,
verificados nas SPECs de módulo e por teste determinístico.

---

## 6. Modos de falha e validação

| Situação | Comportamento esperado |
|---|---|
| JSON não valida contra `transcricao.schema.json` da sua `schema_version` | Falhar cedo, com mensagem que aponta o caminho do campo inválido. Um JSON inválido não segue para o passo seguinte. |
| Diarização não atribui falante a um trecho | `speaker_raw = null` é válido; não é erro. A política de o que fazer com trechos sem falante é da SPEC do script 01. |
| Alinhamento não posiciona uma palavra | `start`/`end`/`score` nulos são válidos; `words` pode ser vazio no segmento. |
| O 03 é chamado com `speakers_mapped = false`, ou com `speaker` nulo onde havia mapeamento | **Barrar a geração da ata.** É o guardrail determinístico previsto no GUIDE-001 §6 (hook que impede ata sobre transcrição não nomeada). |

O guardrail do 03 é candidato natural a hook de harness (GUIDE-001 §6): um
invariante do pipeline, não um lembrete. A SPEC do script 03 fixa sua forma exata.

---

## 7. Evolução do schema

O `schema_version` versiona o próprio contrato, no formato `MAJOR.MINOR`:

- **Mudança compatível (incrementa MINOR):** adicionar campo opcional, afrouxar uma
  restrição, acrescentar proveniência em `metadata`. JSON antigo continua válido.
- **Mudança incompatível (incrementa MAJOR):** renomear ou remover campo, tornar
  obrigatório um campo antes opcional, mudar tipo. Exige DEC própria e nova versão
  desta SPEC, e o artefato de schema é atualizado no mesmo passo.

Esta SPEC define a `schema_version` **1.0**. O artefato `transcricao.schema.json`
acompanha a versão; mudar um sem o outro é divergência (R-SCHEMA-01).

---

## 8. Regras checáveis

Esta seção declara regras `R-SCHEMA-NN`. **Ressalva de escopo de auditoria**
(idêntica à da SPEC-004 §8 e SPEC-005 §8): o `gov-check` atual lê regras `R-*`
apenas das SPECs de **fundação** (SPEC-001, SPEC-002, e SPEC-003 se existisse). Esta
é a SPEC-006, técnica: as `R-SCHEMA` abaixo **não são lidas automaticamente** pelo
skill. São verificadas por **teste determinístico** (parte da Definition of Done do
módulo, SPEC-004 DoD-3) e na **auditoria recorrente** (SPEC-002 §6), ou migradas
para as `R-FUN-*` da SPEC-002 quando estabilizarem.

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-SCHEMA-01** | Todo JSON em `outputs/transcricoes/` valida contra `data/schema/transcricao.schema.json` da `schema_version` que declara; o artefato e a versão desta SPEC andam juntos. | Validação programática do JSON contra o artefato | Alta |
| **R-SCHEMA-02** | `speaker_raw` é escrito só pelo passo 01 e nunca reescrito pelo 02 ou 03 (INV-4, DEC-005). | Inspeção dos scripts 02/03 e diff de `speaker_raw` antes/depois do 02 | Alta |
| **R-SCHEMA-03** | Com `metadata.speakers_mapped = true`, nenhum `speaker` é nulo onde o YAML define mapeamento para o `speaker_raw` correspondente. Cumpre SPEC-002 C-02. | Cruzamento do JSON mapeado com o `speaker_mapping` do YAML | Alta |
| **R-SCHEMA-04** | `metadata` declara `model`, `compute_type`, `language` e `params` efetivamente usados na transcrição (INV-6, DEC-004), insumo da regressão do eval (SPEC-005 §6). | Inspeção de `metadata` contra os parâmetros da rodada | Média |
| **R-SCHEMA-05** | Invariantes temporais valem: `start <= end` em todo segmento, `segments` não-decrescente por `start`, palavra com timestamp dentro do segmento (INV-2, INV-3). | Validação programática sobre o JSON | Média |

As regras acima são v1 e devem ser calibradas conforme as SPECs de módulo e os
scripts forem escritos.

---

## 9. Critérios de revisão

Esta SPEC-006 é viva e versionável (SPEC-001 §7). Deve ser revisitada quando:

- a primeira implementação do script 01 revelar que o output real do WhisperX não
  cabe no schema sem ajuste (gatilho mais provável; pode gerar `schema_version` 1.1);
- alguma amostra do eval ganhar referência word-level com falantes (`ref.json`,
  SPEC-005 §4.3), exigindo do schema o que a DER precisa medir;
- uma decisão de stack (modelo, `compute_type`, troca de ASR) mudar os campos de
  `metadata.params`;
- a DEC-004 ou a DEC-005 forem reavaliadas e substituídas, alterando o envelope ou
  o tratamento de falante;
- as regras `R-SCHEMA` estabilizarem a ponto de valer migrá-las para as `R-FUN-*` da
  SPEC-002, para o `gov-check` passar a verificá-las.

---

## 10. Histórico

| Data | Versão | Evento |
|---|---|---|
| 2026-06-16 | v1 | SPEC-006 produzida em status `proposto`. Primeira SPEC de contrato de dados do projeto e referência comum das futuras SPECs de módulo (01/02/03). Fixa o schema do JSON fonte de verdade: envelope com `schema_version` + `metadata` + `segments` (DEC-004), falante em dois campos `speaker_raw`/`speaker` com flag `speakers_mapped` (DEC-005), schema de segmento e palavra com timestamps e score admitindo nulos, seis invariantes, os modos de falha de validação e o guardrail do passo 03, e o versionamento do próprio schema (`schema_version` 1.0). Carrega o schema como artefato executável em `data/schema/transcricao.schema.json` (JSON Schema Draft 2020-12). Declara cinco regras R-SCHEMA-01 a R-SCHEMA-05, com a ressalva de que o gov-check atual não as lê automaticamente. Numerada a partir de 006 (reserva do slot 003, DEC-003). Aguarda revisão e aprovação. |

---

*Fim do documento.*
