---
documento: SPEC-009
titulo: Contrato do script 01_transcrever (áudio → JSON fonte de verdade)
versao: v1
status: proposto
data: 2026-06-27
autor: Bruno Serminaro
supersede: —
referencia: SPEC-006, SPEC-002, SPEC-005, SPEC-004, GUIDE-001, DEC-006, DEC-007, DEC-008, SPEC-001
---

# SPEC-009 · Contrato do script 01_transcrever

> Primeira SPEC-contrato de módulo (DEC-006): fixa o que o script `01_transcrever`
> recebe, produz e garante. Recebe um áudio de reunião e a configuração da reunião,
> e produz o **JSON fonte de verdade** conforme a SPEC-006, mais os derivados TXT e
> SRT. É o único passo que invoca o ASR e a diarização; 02 e 03 vivem do JSON que
> ele grava. O contrato de dados (forma do JSON) é da SPEC-006 e não se repete aqui;
> a stack (motor, modelo, diarizador) é das DEC-007 e DEC-008; esta SPEC fixa o
> **comportamento** do módulo: etapas, invariantes, modos de falha e verificação.
> Numerada 009 pela reserva do slot SPEC-003 (DEC-003) e pelo mapa da DEC-006
> (007/008 reservadas a glossário e schema do YAML).

---

## 1. Propósito

### 1.1 O que o 01 faz

O `01_transcrever` é a porta de entrada do pipeline: transforma um arquivo de áudio
de reunião em texto com tempos e com a marca de **quem** falou, gravado no JSON que
é a fonte de verdade do projeto (SPEC-002 §4.3). Tudo o que vem depois (nomes reais
de falante no 02, ata no 03, e os derivados TXT/SRT) parte desse JSON, sem nunca
re-transcrever (SPEC-002 C-05).

### 1.2 O que esta SPEC fixa e o que delega

| Esta SPEC fixa | Esta SPEC delega |
|---|---|
| Entradas, saídas e parâmetros do script 01 (o contrato). | A **forma** do JSON (objeto raiz, segmentos, palavras): SPEC-006. |
| O comportamento: ordem das etapas, política para trecho sem falante, derivação de TXT/SRT. | A **escolha de stack** (WhisperX, `large-v3`, `int8`, VAD): DEC-007; **diarização** (pyannote): DEC-008. |
| Os invariantes do passo 01 e seus modos de falha. | O **schema do YAML** de configuração da reunião: SPEC técnica futura (slot 008). |
| Como o 01 é verificado (eval + teste) e as regras `R-TRANS-NN`. | O mapeamento de nomes (02) e a ata (03): SPECs próprias. |

---

## 2. Posição no pipeline

O 01 é o único produtor do JSON e o único passo que toca o ASR e o diarizador.

```
[áudio + YAML da reunião]
        │
        ▼
[01_transcrever]   transcreve, alinha word-level, diariza e embrulha no envelope:
                   metadata.speakers_mapped = false,
                   speaker_raw = label do pyannote (ou null),
                   speaker = null em todo nível
        │ grava {nome}.json (fonte de verdade) + {nome}.txt + {nome}.srt (derivados)
        ▼
[02_aplicar_mapeamento] · [03_gerar_ata]   leem o JSON; nunca re-invocam o ASR
```

Invariante de fronteira: o 01 escreve `speaker_raw` e o congela (DEC-005); ninguém
mais o reescreve. O 01 nunca preenche `speaker` (nome real) — isso é trabalho do 02.

---

## 3. Contrato

### 3.1 Entradas

| Entrada | Forma | Observação |
|---|---|---|
| Áudio da reunião | arquivo local (`.m4a`, `.ogg`, `.wav`, etc.) | Caminho passado ao script. Nunca versionado (R-TAX-09). |
| Configuração da reunião | YAML local | Mínimo usado pelo 01: `language` (ex.: `pt`) e `initial_prompt` (nomes e jargão da reunião, opcional). O schema completo do YAML é SPEC futura; o 01 lê só esses campos e ignora o resto sem falhar. |
| Parâmetros de stack | fixados em DEC-007/DEC-008 | Não são entrada de linha de comando: são os valores consolidados (`large-v3`, `int8`, VAD, `condition_on_previous_text=False`). Gravados em `metadata.params`. |
| `HF_TOKEN` | variável de ambiente | Necessário para baixar o modelo de diarização (pyannote, gated). Vive no ambiente conda, nunca em arquivo (R-TAX-09, DEC-008). |
| Flag `--cpu` (opcional) | argumento de linha de comando | Habilita execução consciente em CPU quando não há GPU. Ausente por padrão. Ver §6. |

### 3.2 Saídas

| Saída | Papel | Contrato |
|---|---|---|
| `{nome}.json` | **fonte de verdade** | Conforme `data/schema/transcricao.schema.json` `schema_version` 1.0 (SPEC-006). Com `speakers_mapped=false`, `speaker_raw` preenchido (ou null), `speaker=null`. |
| `{nome}.txt` | derivado legível | Texto por segmento, prefixado pelo `speaker_raw` (ex.: `SPEAKER_00: ...`) enquanto não há nome real. Derivado do JSON. |
| `{nome}.srt` | derivado de legenda | Legenda padrão com tempos do JSON. Derivado do JSON. |

Os três saem em `outputs/transcricoes/`, gitignored (SPEC-002 §4.4, R-FUN-03). O JSON
é a fonte; TXT e SRT são funções puras dele (R-TRANS-04): regerá-los nunca re-invoca
o ASR.

### 3.3 Parâmetros efetivos gravados

O 01 grava em `metadata` (DEC-004) os valores realmente usados: `model`,
`compute_type`, `language`, e em `metadata.params` ao menos
`condition_on_previous_text`, `vad` e `initial_prompt_used`. Metadado mentiroso é pior
que ausente (SPEC-006 INV-6): o que está gravado tem de ser o que rodou.

---

## 4. Comportamento

O 01 executa, em ordem, sobre uma só carga do áudio:

1. **Carregar e segmentar (VAD).** Detecção de atividade de voz delimita os trechos
   com fala, descartando silêncio (DEC-007).
2. **Transcrever.** Motor da DEC-007 (`large-v3`, `int8`,
   `condition_on_previous_text=False`), com o `initial_prompt` do YAML quando houver.
   `metadata.params.initial_prompt_used` reflete se um prompt não-vazio foi aplicado.
3. **Alinhar (word-level).** Timestamps por palavra. Onde o alinhamento não posiciona
   uma palavra, `start`/`end`/`score` ficam nulos e `words` pode ficar vazio no
   segmento — isso é válido (SPEC-006 §6), não erro.
4. **Diarizar.** Diarizador da DEC-008 atribui um label cru a cada trecho; vai para
   `speaker_raw`. Trecho sem atribuição fica `speaker_raw=null` (política do §4.1
   abaixo).
5. **Embrulhar e gravar.** Monta o envelope (DEC-004) com `schema_version=1.0`,
   `metadata` (incl. `speakers_mapped=false`) e `segments`; valida contra o schema
   **antes** de gravar; deriva TXT e SRT do JSON validado.

### 4.1 Política para trecho sem falante

Quando a diarização não atribui falante a um segmento, o 01 **mantém o segmento** com
`speaker_raw=null` (texto não se perde por falta de diarização). Não inventa um label,
não funde com o vizinho. Cabe ao 02/03 e ao revisor humano decidir o que fazer com
texto sem dono.

### 4.2 Determinismo

A transcrição é não-determinística (DEC-002): re-rodar o 01 sobre o mesmo áudio pode
gerar JSON diferente, e **sobrescreve** as saídas. As etapas de embrulho e derivação
(passo 5) são determinísticas e testáveis (§7).

---

## 5. Invariantes

| ID | Invariante |
|---|---|
| INV-01-1 | **Áudio não sai da máquina.** O 01 não envia áudio a serviço de transcrição/diarização em nuvem. Baixar pesos de modelo (HF) é download de modelo, não envio de áudio (SPEC-002 C-03, R-FUN-04). |
| INV-01-2 | **Saída conforme.** O JSON gravado valida contra o schema 1.0 (SPEC-006 R-SCHEMA-01); JSON inválido não é gravado nem derivado. |
| INV-01-3 | **Estágio 01.** Na saída do 01, `metadata.speakers_mapped=false` e `speaker` é nulo em todo nível. Nomear é trabalho do 02. |
| INV-01-4 | **`speaker_raw` nasce aqui e congela.** Escrito só pelo 01; imutável dali em diante (DEC-005, SPEC-006 INV-4). |
| INV-01-5 | **JSON é a fonte; TXT/SRT são derivados.** TXT e SRT são função do JSON, nunca de re-transcrição (SPEC-002 C-05). |
| INV-01-6 | **Proveniência fiel.** `metadata` reflete `model`, `compute_type`, `language` e `params` realmente usados (SPEC-006 INV-6), insumo da regressão do eval (SPEC-005 §6). |

---

## 6. Modos de falha

O princípio é **falhar cedo, com mensagem que aponta a causa**; nunca gravar um JSON
parcial ou inválido.

| Situação | Comportamento esperado |
|---|---|
| Áudio ausente, ilegível ou em formato não suportado | Falha antes de transcrever, citando o arquivo. |
| GPU/CUDA indisponível | Por padrão, **falha cedo** dizendo que o 01 exige GPU NVIDIA (ambiente-alvo, README) e que existe a flag `--cpu` para forçar CPU. **Não** cai para CPU sozinho. Com `--cpu`, roda em CPU avisando que a duração é de ordem de grandeza maior (`large-v3`); é escolha deliberada para áudio curto sem GPU. |
| `HF_TOKEN` ausente ou sem acesso ao modelo gated | Falha cedo na etapa de diarização, apontando a variável de ambiente (DEC-008). |
| Diarização não retorna nenhum falante | **Não é erro.** Todos os `speaker_raw=null`; o JSON é válido e segue. |
| Alinhamento não posiciona palavras | **Não é erro.** Timestamps/score nulos, `words` possivelmente vazio (SPEC-006 §6). |
| JSON montado não valida contra o schema | Falha antes de gravar, apontando o caminho do campo inválido. Bug do 01, não do dado. |

---

## 7. Verificação (Definition of Done)

O 01 mistura uma parte não-determinística (qualidade da transcrição) e uma parte
determinística (embrulho e derivação). Cada uma tem seu portão (SPEC-004 §5.2):

| Portão | Cobre | Como |
|---|---|---|
| **DoD-2 — eval** | qualidade da transcrição (não-determinística) | Rodar o 01 contra ≥ 1 amostra do golden set (SPEC-005); WER ≤ 15% e TER ≤ 10% (provisórios) registrados (R-EVAL-02). |
| **DoD-3 — teste** | embrulho, validação de schema, derivação TXT/SRT (determinísticas) | Testes binários: JSON montado valida contra o schema; TXT/SRT derivam corretamente de um JSON fixo de fixture. |
| **DoD-4 — gov-check** | coerência documental | `gov-check` limpo. |
| **DoD-5 — commit** | rastreabilidade | Conventional Commits, escopo correto. |

Antes de qualquer `Feito`, a Definition of Ready (SPEC-004 §5.1) já exige que esta
SPEC e as DEC-007/008 existam — é o que este lote entrega.

---

## 8. Regras checáveis

Declara regras `R-TRANS-NN`. **Ressalva de escopo de auditoria** (idêntica à SPEC-004
§8, SPEC-005 §8, SPEC-006 §8): o `gov-check` atual lê regras `R-*` apenas das SPECs de
**fundação** (001/002, e 003 se existisse). Esta é a SPEC-009, técnica: as `R-TRANS`
abaixo **não são lidas automaticamente** pelo skill. São verificadas por **teste
determinístico** (DoD-3), pelo **eval** (DoD-2) e na **auditoria recorrente**
(SPEC-002 §6), ou migradas para as `R-FUN-*` da SPEC-002 quando estabilizarem.

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-TRANS-01** | O 01 não faz chamada de rede a ASR/diarização em nuvem; áudio nunca sai da máquina. Download de pesos de modelo (HF) é permitido (modelo, não áudio). Cumpre C-03/R-FUN-04. | Inspeção do script e de suas chamadas de rede | Crítica |
| **R-TRANS-02** | A saída do 01 valida contra o schema 1.0 com `speakers_mapped=false` e `speaker` nulo em todo nível (INV-01-2, INV-01-3). | Validação programática do JSON gerado | Alta |
| **R-TRANS-03** | `metadata`/`metadata.params` refletem os parâmetros realmente usados (INV-01-6, DEC-007), insumo do eval (R-SCHEMA-04). | Cruzamento de `metadata` com a rodada | Alta |
| **R-TRANS-04** | TXT e SRT são derivados do JSON, sem re-invocar o ASR (INV-01-5, C-05). | Regerar derivados sem rede; diff contra os originais | Média |
| **R-TRANS-05** | O 01 só é dado por `Feito` após eval verde registrado contra os limiares (DoD-2, R-EVAL-02). | Registro do eval cruzado com o board | Alta |

As regras são v1 e devem ser calibradas conforme o script for escrito e avaliado.

---

## 9. Critérios de revisão

Esta SPEC-009 é viva e versionável (SPEC-001 §7). Revisar quando:

- a primeira implementação revelar que o output real do WhisperX exige ajuste de
  comportamento ou de schema (pode disparar `schema_version` 1.1 na SPEC-006);
- uma decisão de stack mudar (DEC-007/008 reavaliadas): modelo, `compute_type`,
  diarizador, ou troca de ASR;
- surgir a necessidade de tornar a execução em CPU um caminho de primeira classe (e
  não só o escape via `--cpu`), ou de outro ambiente-alvo;
- o schema do YAML de configuração (SPEC futura) fixar campos que o 01 passe a ler;
- as regras `R-TRANS` estabilizarem a ponto de valer migrá-las para as `R-FUN-*` da
  SPEC-002.

---

## 10. Histórico

| Data | Versão | Evento |
|---|---|---|
| 2026-06-27 | v1 | SPEC-009 produzida em status `proposto`. Primeira SPEC-contrato de módulo (DEC-006). Fixa o contrato do `01_transcrever`: entradas (áudio + YAML da reunião + `HF_TOKEN` + flag `--cpu`), saídas (JSON fonte de verdade conforme SPEC-006 + TXT/SRT derivados), parâmetros gravados em `metadata`, o comportamento em cinco etapas (VAD, transcrição, alinhamento word-level, diarização, embrulho/validação), a política para trecho sem falante, seis invariantes, os modos de falha (falhar cedo) e a verificação em dois portões (eval DoD-2 + teste DoD-3). Sem GPU, falha por padrão com escape explícito via flag `--cpu` (execução consciente em CPU); fallback silencioso para CPU é descartado. Delega a forma do JSON à SPEC-006 e a stack às DEC-007 (motor) e DEC-008 (diarização). Declara cinco regras R-TRANS-01 a R-TRANS-05, com a ressalva de que o gov-check atual não as lê. Aguarda revisão e aprovação. |

---

*Fim do documento.*
