---
documento: DEC-007
titulo: Motor de transcrição — WhisperX (large-v3, int8, VAD, condition_on_previous_text=False)
versao: v1
status: proposto
data: 2026-06-27
autor: Bruno Serminaro
supersede: —
referencia: SPEC-009, SPEC-002, SPEC-005, SPEC-006, DEC-002, DEC-008
---

# DEC-007 · Motor de transcrição

> Decisão atômica de stack: qual motor e quais parâmetros o `01_transcrever` usa
> para virar áudio em texto com tempos. Adota **WhisperX** com `large-v3`,
> `compute_type=int8`, VAD ativo e `condition_on_previous_text=False`. É uma das duas
> DECs de stack que a SPEC-009 referencia (a outra é a DEC-008, diarização). Não
> decide a forma do JSON (SPEC-006) nem o comportamento do script (SPEC-009): fixa só
> a escolha do motor e seus parâmetros, gravados em `metadata.params` (DEC-004).

---

## 1. Contexto

O `01_transcrever` (SPEC-009) precisa de um motor de ASR que: rode **local**, porque
o áudio nunca sai da máquina (SPEC-002 C-03/C-07); transcreva bem **PT-BR**, com nomes
próprios e jargão de reunião; e entregue **timestamps por palavra** e gancho de
diarização, porque o schema (SPEC-006) tem `words` com tempos e `speaker_raw` por
segmento. O ambiente-alvo é a GPU NVIDIA dedicada do autor (README).

A família **Whisper** é o estado da arte aberto para isso, mas "usar Whisper" ainda
deixa três escolhas em aberto: qual *implementação*, qual *modelo* e com quais
*parâmetros*. A Definition of Ready (SPEC-004 §5.1, R-FUN-02) proíbe codar o 01 antes
de essas dependências terem DEC. Esta é essa DEC.

---

## 2. Decisão

**Adotar o WhisperX como motor do passo 01, com o modelo `large-v3`,
`compute_type=int8`, detecção de atividade de voz (VAD) ativa e
`condition_on_previous_text=False`.**

A decisão inclui:

- **WhisperX** como orquestrador: ele junta num só pipeline a transcrição (via backend
  `faster-whisper`/CTranslate2), o **alinhamento word-level** e a costura da
  diarização — exatamente os três produtos que o schema da SPEC-006 exige;
- **`large-v3`** como modelo, pela acurácia em PT-BR: reuniões trazem nomes e termos
  que modelos menores erram mais (o que a TER do eval mede, SPEC-005 §4.2);
- **`int8`** como precisão, para o `large-v3` caber com folga na VRAM e rodar rápido;
- **VAD ativo**, para cortar silêncio e reduzir alucinação em trechos mudos;
- **`condition_on_previous_text=False`**, para um erro num segmento não contaminar os
  seguintes;
- gravar esses valores em `metadata`/`metadata.params` (DEC-004), para o eval saber
  com que configuração cada JSON foi gerado (SPEC-005 §6).

O `initial_prompt` por reunião **não** é fixado aqui: é configuração por execução
(SPEC-009 §3), não escolha de stack.

---

## 3. Origem / rastro

| Artefato | Como sustenta esta decisão |
|---|---|
| **SPEC-002 C-03/C-05/C-08** | Exige ASR local, JSON como fonte de verdade e transcrição utilizável; o motor tem de servir os três. |
| **SPEC-006** | Pede `words` com timestamps e `speaker_raw`; só um motor que produza word-level + diarização cabe. |
| **SPEC-005 §7.3** | Esses parâmetros são o que o eval mede; mudar qualquer um dispara nova rodada de eval. |
| **README** | Registra a stack já consolidada na prática; esta DEC a formaliza. |
| **SPEC-009** | Primeiro consumidor: o comportamento do 01 assume este motor. |

---

## 4. Alternativas consideradas

### 4.1 `openai-whisper` (implementação de referência) puro

Usar a implementação original da OpenAI, sem WhisperX.

**Descartada porque:**
- Não entrega timestamps **word-level** confiáveis nem diarização; seria preciso
  costurar alinhamento e atribuição de falante à mão, reimplementando o que o WhisperX
  já resolve.
- É mais lenta que o backend CTranslate2 que o WhisperX usa.

### 4.2 `faster-whisper` sozinho

Usar só o `faster-whisper` (CTranslate2), rápido e econômico de memória.

**Descartada porque:**
- Transcreve bem, mas **não** faz o alinhamento word-level nem a costura de
  diarização. O WhisperX usa o `faster-whisper` por baixo: adotá-lo dá a mesma
  velocidade **mais** as duas etapas que faltam, sem regressão.

### 4.3 ASR em nuvem (API de Google/AWS/OpenAI)

Mandar o áudio para um serviço gerenciado de transcrição.

**Descartada por princípio, não por qualidade:**
- Viola SPEC-002 **C-03**: o áudio de reunião não sai da máquina. Registrada aqui só
  para deixar explícito que a nuvem foi recusada por privacidade.

(Modelos menores — `large-v2`, `medium` — foram considerados como variação de
`large-v3`; ficam como alvo de calibração do eval, não como decisão separada.)

---

## 5. Consequências

### 5.1 Consequências positivas

- **Um pipeline, três produtos.** Transcrição, word-level e gancho de diarização sem
  costura manual — direto no formato que o schema espera.
- **Cabe na GPU.** `int8` + `large-v3` rodam rápido na VRAM da máquina-alvo.
- **Menos alucinação.** VAD e `condition_on_previous_text=False` reduzem invenções em
  silêncio e propagação de erro entre segmentos.
- **Tudo local.** Nenhuma dependência de rede em tempo de transcrição (R-TRANS-01).

### 5.2 Consequências negativas / custo aceito

- **Depende de `torch` + CUDA.** Instalação pesada e acoplada à versão de CUDA/driver;
  cada dependência entra no `environment.yml` no mesmo commit desta DEC (R-FUN-02).
- **`int8` troca acurácia marginal por velocidade/memória.** Aceito e **calibrável**:
  se o eval (SPEC-005) mostrar perda relevante, reavalia-se `float16` (gatilho §6).
- **`large-v3` exige GPU.** Liga-se ao modo de falha da SPEC-009 §6 (sem GPU, falha
  por padrão; CPU só sob `--cpu`).
- **Dependência de terceiro.** WhisperX evolui em ritmo próprio; uma versão pode
  quebrar a integração. Mitigado fixando versão no ambiente.

### 5.3 O que esta decisão NÃO resolve

- **Não decide a diarização** (qual diarizador): é a DEC-008.
- **Não define a forma do JSON** (envelope, campos): SPEC-006 / DEC-004.
- **Não fixa o `initial_prompt`** nem o comportamento do script: SPEC-009.
- **Não fixa os limiares de qualidade**: SPEC-005.

---

## 6. Critérios de reavaliação

| Gatilho | O que reavaliar |
|---|---|
| O eval mostrar WER/TER ruim atribuível a `int8` ou ao modelo | Testar `float16` ou outro modelo; recalibrar com o golden set antes de aceitar. |
| Surgir um modelo aberto melhor em PT-BR | Comparar contra o `large-v3` no eval. |
| WhisperX ser descontinuado ou quebrar numa atualização | Avaliar voltar ao `faster-whisper` + alinhamento próprio. |
| A GPU mudar (mais VRAM) | Reavaliar `compute_type` (ex.: `float16`). |
| O custo de manter `torch`/CUDA virar fonte recorrente de atrito | Reavaliar a stack de execução. |

---

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-06-27 | DEC-007 v1 produzida em status `proposto`. Sétima DEC do projeto; primeira de stack. Adota o WhisperX (`large-v3`, `int8`, VAD, `condition_on_previous_text=False`) como motor do passo 01, gravando os parâmetros em `metadata.params` (DEC-004). Descarta `openai-whisper` puro, `faster-whisper` sozinho e ASR em nuvem (esta por C-03). Sustenta a SPEC-009; complementada pela DEC-008 (diarização). |

---

*Fim do documento.*
