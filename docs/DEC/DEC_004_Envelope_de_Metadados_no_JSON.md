---
documento: DEC-004
titulo: Envelope de metadados no JSON fonte de verdade (schema_version + metadata + segments)
versao: v1
status: proposto
data: 2026-06-16
autor: Bruno Serminaro
supersede: —
referencia: SPEC-006, SPEC-002, SPEC-005, DEC-002
---

# DEC-004 · Envelope de metadados no JSON fonte de verdade

> Decisão atômica que define a forma do JSON fonte de verdade do pipeline: um
> envelope com `schema_version`, um bloco `metadata` de execução e a lista
> `segments`, em vez do output cru do WhisperX. Habilita autodescrição e rastreio
> de proveniência (lineage) para o eval. É uma das duas decisões de contrato de
> dados que sustentam a SPEC-006 (a outra é a DEC-005, sobre o campo de falante).

---

## 1. Contexto

O JSON é a fonte de verdade do pipeline (SPEC-002 §4.3): TXT, SRT e ata derivam
dele, e reprocessar não exige re-transcrever. A SPEC-006 fixa o schema desse JSON,
e a primeira decisão de forma é o que o objeto raiz contém.

O WhisperX entrega um output cru com `segments`, `words` e `language`, sem registro
de qual modelo, precisão ou parâmetros geraram aquela saída. O eval (SPEC-005 §6)
precisa detectar regressão, ou seja, comparar rodadas e saber se uma mudança
piorou a transcrição. Sem saber com que `model`, `compute_type` e parâmetros cada
JSON foi produzido, a comparação fica cega: dois JSON podem divergir só porque um
rodou em `large-v3` e o outro em `medium`, e nada no arquivo registra isso.

A decisão precisa ser tomada antes de escrever a SPEC-006 e o script 01, sob pena
de o schema nascer sem o lugar onde a proveniência mora.

---

## 2. Decisão

**Adotar para o JSON fonte de verdade um envelope com três campos de topo:
`schema_version` (versão do contrato, MAJOR.MINOR), `metadata` (bloco de
proveniência da execução) e `segments` (a transcrição propriamente dita). O JSON
do projeto não é o output cru do WhisperX: o script 01 embrulha o resultado do
WhisperX neste envelope.**

A decisão inclui:

- registrar em `metadata` ao menos: `audio_source`, `created_at`, `model`,
  `compute_type`, `language`, `params` (com os parâmetros de stack fixados) e
  `speakers_mapped` (flag de estágio, ver DEC-005);
- carregar `pipeline_version` (commit/versão do código gerador) em `metadata`
  quando disponível, para amarrar cada JSON ao código que o produziu;
- versionar o próprio schema via `schema_version`, de modo que mudanças futuras de
  forma sejam rastreáveis (a evolução do schema é detalhada na SPEC-006 §7);
- manter o conteúdo de `segments`/`words` compatível com o que o WhisperX produz,
  sem reescrever a estrutura de transcrição além do necessário.

---

## 3. Origem / rastro

| Artefato | Como sustenta esta decisão |
|---|---|
| **SPEC-002 §4.3** | Declara o JSON como fonte de verdade da qual tudo deriva; esta DEC fixa a forma desse JSON. |
| **SPEC-005 §6** | O registro de resultados do eval depende de proveniência (modelo, parâmetros, commit) para detectar regressão. É o motivo direto do bloco `metadata`. |
| **DEC-002** | O método spec-driven exige que toda escolha com trade-off vire DEC antes do código. |
| **SPEC-006** | Primeira SPEC a consumir esta decisão: o envelope é o objeto raiz do schema. |

---

## 4. Alternativas consideradas

### 4.1 JSON cru do WhisperX, sem envelope

Gravar diretamente o dicionário que o WhisperX retorna (`segments`, `words`,
`language`), sem metadados de execução.

**Descartada porque:**
- Não registra proveniência. O eval (SPEC-005 §6) não consegue distinguir
  regressão real de diferença de configuração entre rodadas, que é exatamente o
  que precisa medir.
- O JSON deixa de ser autodescritivo: para saber como uma transcrição foi gerada,
  é preciso reconstruir o contexto de fora do arquivo, que se perde com o tempo
  (o mesmo problema de memória diluída que a fundação combate).
- Acopla o contrato do projeto ao formato exato de uma versão do WhisperX, sem uma
  camada própria onde versionar mudanças.

### 4.2 Metadados num arquivo lateral (sidecar `.meta.yml`)

Manter o JSON cru e gravar a proveniência num arquivo separado ao lado, por
exemplo `{nome}.meta.yml`.

**Descartada porque:**
- Quebra a autossuficiência da fonte de verdade: passam a ser dois arquivos que
  precisam andar juntos, e a separação convida à dessincronização (um copiado sem
  o outro, um regenerado sem o outro).
- Multiplica artefatos por reunião sem ganho: o custo de algumas dezenas de bytes
  de metadados dentro do próprio JSON é trivial (SPEC-002 §4.3 já trata o custo de
  armazenamento do JSON como desprezível).
- Complica a validação por schema: validar uma unidade lógica espalhada em dois
  arquivos é mais frágil que validar um objeto só.

---

## 5. Consequências

### 5.1 Consequências positivas

- **JSON autodescritivo.** Cada transcrição carrega como foi gerada; a proveniência
  sobrevive ao tempo dentro do próprio arquivo.
- **Eval habilitado.** O bloco `metadata` é o que torna o registro de regressão da
  SPEC-005 §6 possível de fato, não só no papel.
- **Schema versionável.** `schema_version` dá um eixo próprio de evolução,
  independente da versão do WhisperX.
- **Validação por unidade única.** Um objeto, um schema, uma validação (coerente
  com a DEC-004 de artefato executável da SPEC-006 §8).

### 5.2 Consequências negativas / custo aceito

- **Divergência do formato cru.** O script 01 precisa embrulhar o output do
  WhisperX; código de quem consome um JSON cru de WhisperX não lê o nosso sem
  conhecer o envelope. Aceito: é uma camada fina e o ganho de proveniência paga.
- **Acoplamento ao nosso schema.** Ferramentas externas que esperem o formato cru
  precisam do `segments` aninhado no envelope. Mitigado por `segments` manter a
  estrutura interna familiar do WhisperX.
- **Mais um campo a manter coerente.** `metadata` precisa refletir os parâmetros
  realmente usados; metadado mentiroso é pior que ausente. Vigiável por regra
  checável (SPEC-006 R-SCHEMA-04).

### 5.3 O que esta decisão NÃO resolve

- **Não define o campo de falante** (`speaker_raw` vs `speaker`): isso é a DEC-005.
- **Não fixa o conjunto fechado de parâmetros** em `metadata.params`: a SPEC-006
  fixa o mínimo obrigatório e admite extensão.
- **Não decide a stack** (WhisperX, `large-v3`, `int8`): essas seguem como DECs
  próprias; esta DEC só registra que os valores usados são gravados no JSON.

---

## 6. Critérios de reavaliação

| Gatilho | O que reavaliar |
|---|---|
| O eval deixar de precisar de proveniência para detectar regressão (improvável) | O bloco `metadata` perde a justificativa principal; reavaliar o que mantém. |
| O WhisperX mudar o formato de saída de modo que o envelope atrapalhe a integração | Realinhar o envelope ao novo formato cru, bumpando `schema_version`. |
| O custo de manter `metadata` coerente virar fonte recorrente de divergência no eval | Reduzir `metadata` ao subconjunto que o eval efetivamente usa. |

---

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-06-16 | DEC-004 v1 produzida em status `proposto`. Primeira de duas decisões de contrato de dados da SPEC-006. Adota o envelope (`schema_version` + `metadata` + `segments`) para o JSON fonte de verdade, em vez do output cru do WhisperX, para habilitar autodescrição e proveniência (lineage) ao eval (SPEC-005 §6). Descarta o JSON cru e o sidecar de metadados. Quarta DEC do projeto. |

---

*Fim do documento.*
