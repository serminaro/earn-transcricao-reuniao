---
documento: SPEC-005
titulo: Protocolo de Avaliação (eval) do pipeline de transcrição
versao: v1
status: proposto
data: 2026-06-16
autor: Bruno Serminaro
supersede: —
referencia: SPEC-002, DEC-002, GUIDE-001, SPEC-004, SPEC-001
---

# SPEC-005 · Protocolo de Avaliação (eval) do pipeline de transcrição

> Define como a qualidade do pipeline é medida contra um padrão-ouro conferido à mão: o golden set, as métricas, o runner, o grader e os critérios de aprovação. É a metade de *verificação* do método spec-driven — "a SPEC dirige, o eval prova" (DEC-002, GUIDE-001 §2) — e operacionaliza os critérios provisórios C-08 e C-09 da SPEC-002 §5 em medição reprodutível. Sem esta SPEC, a Definition of Done da SPEC-004 (DoD-2: "eval verde contra o threshold") aponta para um threshold que nenhum documento define. Numerada a partir de 005 por força da reserva do slot SPEC-003 (DEC-003).

---

## 1. Propósito

### 1.1 Por que um protocolo de avaliação

O produto central deste projeto é um pipeline de ASR, que é **não-determinístico**: a mesma entrada pode gerar saídas diferentes, e "funciona" não se reduz a um teste binário (DEC-002 §1). Num projeto solo, sem revisor externo, o modo de falha concreto é construir por impressão — "a transcrição pareceu boa" — sem medição. O freio funcional contra isso é o eval: uma métrica sobre um conjunto de referência conferido à mão, que substitui, na qualidade, o papel que o par humano cumpriria (DEC-002 §5.1).

Esta SPEC fixa esse freio como protocolo declarado e reprodutível, do mesmo modo que a SPEC-001 fixa a taxonomia e a SPEC-004 fixa o fluxo. Cumprir a qualidade deixa de ser opinião do autor e passa a ser **número medido contra um gabarito** (GUIDE-001 §2).

### 1.2 O que esta SPEC operacionaliza

A SPEC-002 §5 declara dois critérios de sucesso marcados **(provisório)**:

- **C-08** — a transcrição é utilizável: o autor a reconhece como fiel ao teor, mesmo com erros pontuais;
- **C-09** — o `initial_prompt` com nomes e jargão reduz erros em termos próprios frente à transcrição sem prompt.

Ambos foram deixados provisórios "até a primeira execução real". Esta SPEC dá a eles uma forma medível: C-08 vira um limiar de WER (§4.1); C-09 vira uma comparação de Term Error Rate com e sem `initial_prompt` (§4.2, §7.2).

---

## 2. O golden set

### 2.1 Definição

O golden set é o conjunto de **amostras de referência** contra as quais a qualidade do pipeline é medida. Cada amostra é um par:

```
(áudio de reunião,  transcrição de referência conferida à mão)
```

A referência é o "gabarito": o que o pipeline *deveria* ter produzido. A qualidade de uma rodada é a distância entre a saída do pipeline (hipótese) e essa referência.

### 2.2 Estrutura e localização (fora do Git)

O golden set contém conteúdo de reuniões reais e **nunca é versionado** (SPEC-001 §9, SPEC-002 §4.4). Vive em `data/golden/`, gitignored, com uma subpasta por amostra:

```
data/golden/                         (gitignored — sensível)
├── <id_amostra>/
│   ├── audio.<ext>                  o áudio da amostra
│   ├── ref.txt                      transcrição de referência (texto por falante)
│   ├── ref.json                     (opcional) referência word-level com falantes, p/ DER
│   └── meta.yml                     vocabulário ancorado, falantes, duração, fonte
└── ...
```

A semente já existente é o par `data/audios_processados/audio_padrao.{m4a,txt}`: um áudio com transcrição de referência em texto corrido. Migra para `data/golden/audio_padrao/` como a **amostra 0** (referência só de texto: habilita WER e TER, ainda não DER — ver §4.3).

### 2.3 Como uma amostra de referência é construída

1. Escolher um áudio curto e representativo (recorte de 2 a 10 minutos basta; o custo de conferir cresce com a duração).
2. Rodar o pipeline uma vez para obter um rascunho, **e então corrigir à mão** até a referência estar fiel — palavra a palavra, com os nomes e o jargão corretos.
3. Registrar em `meta.yml` o vocabulário ancorado da reunião (nomes próprios, termos técnicos) que a TER (§4.2) vai medir, e os falantes.

A referência é **conferida por humano**; nunca é a saída crua da própria pipeline sob avaliação (isso seria circular — mediria a pipeline contra si mesma; ver R-EVAL-03).

---

## 3. O runner

O runner é o **andaime determinístico em volta do ASR não-determinístico**: dado o golden set, produz métricas reprodutíveis. Para cada amostra:

```
data/golden/<id>/audio   ──►  [pipeline: 01_transcrever.py]  ──►  hipótese (JSON/TXT)
                                                                      │
ref.txt / ref.json  ─────────────────────────────────────────────────┤
                                                                      ▼
                                          [grader: normaliza → alinha → mede]
                                                                      │
                                                                      ▼
                                  registro de métricas (WER, TER, [DER]) + veredito
```

O runner roda o **mesmo** comando de transcrição usado em produção (script 01), com os **mesmos** parâmetros fixados (large-v3, int8, `condition_on_previous_text=False`, VAD, `initial_prompt` da amostra) — senão o eval não mede o pipeline real. Para C-09, o runner roda a amostra **duas vezes**, com e sem `initial_prompt`, e compara (§7.2).

---

## 4. Métricas

### 4.1 WER — Word Error Rate (métrica primária)

Mede a qualidade geral da transcrição. Sobre a sequência de palavras alinhada por distância de edição entre referência e hipótese:

```
WER = (S + D + I) / N
```

onde `S` = substituições, `D` = deleções, `I` = inserções, `N` = nº de palavras da referência. Menor é melhor. Cumpre **C-08**.

### 4.2 TER — Term Error Rate (métrica de termos próprios)

WER trata toda palavra igual, mas neste projeto os erros que mais doem são em **nomes próprios e jargão técnico** — exatamente o que o `initial_prompt` tenta ancorar. A TER mede só o vocabulário declarado em `meta.yml`:

```
TER = termos_ancorados_errados / termos_ancorados_totais
```

A TER é o que torna **C-09** medível: comparar TER com e sem `initial_prompt` (§7.2).

### 4.3 DER — Diarization Error Rate (secundária, exige referência rica)

Mede "quem falou quando": fração do tempo atribuída ao falante errado (ou a fala/silêncio errados). Requer `ref.json` com segmentos rotulados por falante. Enquanto as amostras tiverem só `ref.txt` (caso da amostra 0), a DER fica **fora de escopo da rodada** e é registrada como `n/d`.

### 4.4 Normalização antes de medir

Para não punir diferenças irrelevantes, referência e hipótese passam pela mesma normalização antes do alinhamento: minúsculas, remoção de pontuação, colapso de espaços, normalização de numerais por extenso vs dígitos. **Acentuação é preservada** (em PT-BR o acento é distintivo). A função de normalização é fixada junto ao runner e é parte do protocolo: mudá-la muda as métricas e exige nota no Histórico.

---

## 5. Critério de aprovação (thresholds)

Um item de código de transcrição (script 01) está **verificado** quando, em pelo menos uma amostra do golden set, as métricas ficam dentro dos limiares:

| Métrica | Limiar | Estado |
|---|---|---|
| WER | ≤ 15% | **(provisório)** |
| TER (termos ancorados) | ≤ 10% | **(provisório)** |
| DER | a definir quando houver `ref.json` | **(provisório)** |

Os limiares são **provisórios e calibráveis**: são chutes iniciais, a serem ajustados após a primeira execução real (coerente com C-08/C-09 provisórios na SPEC-002). O que **não** é provisório é a regra: uma pipeline "pronta" sem métrica registrada contra um limiar declarado está **aprovada, não verificada** (GUIDE-001 §2; R-EVAL-05). Calibrar o limiar é legítimo; dispensar a medição não é.

A primeira execução real do pipeline produz um **REP** (SPEC-001 §2.2) que registra as métricas observadas e propõe os limiares calibrados; a calibração entra como nova versão desta SPEC.

---

## 6. Registro de resultados

Cada rodada registra um **registro de métricas** com: id da amostra, versão/commit do pipeline, parâmetros usados, WER, TER, DER (ou `n/d`), veredito (verde/vermelho) e data. O registro permite detectar **regressão** — ver se uma mudança piorou a transcrição (DEC-002 §5.1).

Fronteira de privacidade, em dois níveis:

- **Detalhe por erro** (listas de palavras erradas, trechos) pode conter teor da reunião → vive em `outputs/eval/`, **gitignored**.
- **Sumário agregado** (apenas números e veredito, sem texto de reunião) é versionável → entra em `docs/logs/` ou num REP de execução. Números não são conteúdo sensível; trechos transcritos são.

## 7. Quando rodar o eval

### 7.1 Como Definition of Done

O eval é o portão DoD-2 da SPEC-004 §5.2: o script 01 não chega a `Feito` sem uma rodada verde registrada. Itens **determinísticos** do pipeline (parsing de JSON, aplicação do mapeamento YAML, geração de SRT — scripts 02 e partes do 01) são verificados por **teste binário/TDD** (DoD-3), não por eval; o eval cobre a qualidade da transcrição, que é o cerne não-determinístico.

### 7.2 Como experimento (C-09)

Para sustentar C-09, rodar a mesma amostra com e sem `initial_prompt` e comparar a TER. A hipótese só é confirmada se a TER com prompt for materialmente menor.

### 7.3 Por mudança de premissa

Qualquer revisão de decisão técnica consolidada (modelo, `compute_type`, VAD, troca de ASR — DECs de stack) dispara uma rodada de eval contra o golden set, para medir se a mudança ajudou ou piorou, antes de aceitá-la.

---

## 8. Regras checáveis

Esta seção declara regras `R-EVAL-NN`. **Ressalva de escopo de auditoria** (idêntica à da SPEC-004 §8): o `gov-check` atual lê regras `R-*` apenas das SPECs de **fundação** (SPEC-001, SPEC-002, e SPEC-003 se existisse). Esta é a SPEC-005, técnica: as `R-EVAL` abaixo **não são lidas automaticamente** pelo skill — são verificadas **manualmente na auditoria recorrente** (SPEC-002 §6), ou migradas para as `R-FUN-*` da SPEC-002 numa versão futura dela quando estabilizarem.

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-EVAL-01** | O golden set (áudio + referência) vive fora do Git: `data/golden/` e qualquer referência transcrita são gitignored; nenhuma referência de reunião é versionada. Reforça R-TAX-09 e R-FUN-03. | `.gitignore` e varredura dos arquivos rastreados | Crítica |
| **R-EVAL-02** | O script de transcrição (01) só é dado por `Feito` (DoD-2, SPEC-004 §5.2) após rodar contra ≥ 1 amostra do golden set com métricas registradas contra os limiares da §5. | Registro de resultados (§6) cruzado com o board | Alta |
| **R-EVAL-03** | A referência de cada amostra é conferida à mão por humano, nunca a saída crua da própria pipeline sob avaliação. Referência auto-gerada e não revisada é circular e descaracteriza o eval. | Inspeção de `meta.yml`/procedimento §2.3 | Alta |
| **R-EVAL-04** | Cada rodada registra id da amostra, versão/commit do pipeline, parâmetros, métricas e veredito (§6). Sumário agregado sem teor de reunião pode ser versionado; detalhe por erro fica gitignored. | `docs/logs/` e `outputs/eval/` | Média |
| **R-EVAL-05** | Os limiares da §5 estão declarados (ainda que provisórios). Pipeline "aprovada" sem métrica registrada contra limiar é aprovado-não-verificado. Calibrar o limiar é legítimo; dispensar a medição não. | Esta §5 cruzada com os registros de §6 | Média |

As regras acima são v1 e devem ser calibradas conforme o eval for usado.

---

## 9. Critérios de revisão

Esta SPEC-005 é viva e versionável (SPEC-001 §7). Deve ser revisitada quando:

- a **primeira execução real** produzir métricas que permitam calibrar os limiares provisórios da §5 (gatilho principal; gera REP e nova versão desta SPEC);
- alguma amostra ganhar `ref.json` com falantes, habilitando a DER e exigindo definir seu limiar;
- a função de normalização (§4.4) mudar — toda mudança altera as métricas e precisa de nota no Histórico;
- as regras `R-EVAL` estabilizarem a ponto de valer migrá-las para as `R-FUN-*` da SPEC-002 (para o `gov-check` passar a verificá-las);
- uma decisão de stack (modelo, `compute_type`, troca de ASR) mudar o que está sendo medido.

---

## 10. Histórico

| Data | Versão | Evento |
|---|---|---|
| 2026-06-16 | v1 | SPEC-005 produzida em status `proposto`. Primeira SPEC de verificação do projeto; operacionaliza os critérios provisórios C-08 (utilidade → WER) e C-09 (initial_prompt → TER) da SPEC-002 §5 e fecha a metade "o eval prova" do método spec-driven (DEC-002, GUIDE-001). Define o golden set fora do Git (`data/golden/`, semente em `audio_padrao`), o runner em volta do script 01, as métricas WER/TER/DER (DER fora de escopo enquanto a referência for só texto), a normalização, os limiares provisórios (WER ≤ 15%, TER ≤ 10%) e o registro de resultados com fronteira de privacidade (números versionáveis, trechos gitignored). É o portão DoD-2 da SPEC-004. Declara cinco regras R-EVAL-01 a R-EVAL-05, com a ressalva de que o gov-check atual não as lê automaticamente. Aguarda revisão e a calibração dos limiares após a primeira execução real. |

---

*Fim do documento.*
