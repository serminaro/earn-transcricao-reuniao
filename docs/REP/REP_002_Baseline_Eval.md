---
documento: REP-002
titulo: Baseline de primeira execução do eval (passo 01_transcrever)
versao: v1
status: proposto
data: 2026-06-28
autor: Bruno Serminaro
supersede: —
referencia: SPEC-005, SPEC-009, SPEC-002, REP-001, DEC-007, DEC-008
---

# REP-002 · Baseline de primeira execução do eval

> Registra a primeira execução real do eval do passo `01_transcrever` contra uma
> amostra de golden set conferida à mão. É o artefato que a SPEC-005 §5 prevê para
> a primeira rodada: documenta WER, TER e DER observados, a configuração que os
> produziu, e a decisão sobre os limiares provisórios. Fecha o portão DoD-2
> (SPEC-004 §5.2) do script 01 e confirma empiricamente hipóteses que o REP-001 §5
> deixou em aberto. Carrega apenas números e parâmetros, nenhum trecho de reunião
> (fronteira de privacidade, SPEC-005 §6).

---

## 1. Contexto

O `01_transcrever` foi implementado (SPEC-009, código em `src/transcrever.py`) e
passou nos testes determinísticos (DoD-3). Faltava o portão **DoD-2**: medir a
qualidade da transcrição, que é não-determinística, contra uma referência conferida
à mão (SPEC-005). Este REP registra essa primeira medição.

A SPEC-005 §5 prevê explicitamente este documento: "A primeira execução real do
pipeline produz um REP que registra as métricas observadas e propõe os limiares
calibrados." É o que segue.

---

## 2. A amostra

| Atributo | Valor |
|---|---|
| Identificador | `trecho_eval` (em `data/golden/trecho_eval/`, gitignored) |
| Duração | 5,0 min (299,8 s cobertos) |
| Falantes | 2 (`SPEAKER_00` = Gabriel Dorte, `SPEAKER_01` = Bruno Serminaro) |
| Referência | `ref.txt`, ~922 palavras, **conferida à mão** |
| Termos ancorados | 11 declarados em `meta.yml`; 28 ocorrências na referência |

**Procedência da referência (anti-circularidade, R-EVAL-03).** A referência foi
construída pelo procedimento da SPEC-005 §2.3: rodar o pipeline uma vez para obter um
rascunho e então **corrigir à mão, ouvindo o áudio**, palavra por palavra. Não é a
saída crua da pipeline sob avaliação — é gabarito humano.

**Desvio em relação à issue #10.** A issue previa usar o par `audio_padrao.{m4a,txt}`
como amostra 0. Optou-se por uma amostra nova (`trecho_eval`) porque o
`audio_padrao.txt` ainda não era uma referência conferida à mão, e usá-lo violaria a
anti-circularidade. A intenção da issue (baseline WER/TER a partir de amostra
conferida) é cumprida.

---

## 3. Configuração medida

Parâmetros efetivos da rodada, gravados no `metadata` do JSON (DEC-004) e relidos
pelo runner:

| Parâmetro | Valor | Origem |
|---|---|---|
| `model` | `large-v3` | DEC-007 |
| `compute_type` | `int8` | DEC-007 |
| `vad` | `true` | DEC-007 |
| `condition_on_previous_text` | `false` | DEC-007 |
| `initial_prompt_used` | `true` (derivado dos termos ancorados) | SPEC-005 §7.2 |
| `batch_size` | **4** | ajustado à VRAM (ver §5) |
| Diarização | `pyannote/speaker-diarization-community-1` | DEC-008 |

**Ajustes que a primeira execução real exigiu.** O código gerado assumia uma API do
WhisperX mais antiga; a primeira execução na GPU revelou e corrigiu:

- `whisperx.DiarizationPipeline` → `whisperx.diarize.DiarizationPipeline`;
- parâmetro `use_auth_token=` → `token=`;
- modelo de diarização real é o `speaker-diarization-community-1` (exige aceite de
  termos no Hugging Face), não o `speaker-diarization-3.1`;
- dependências faltantes adicionadas ao `environment.yml`: `jsonschema`, `pyyaml`;
- `batch_size` de 16 para 4 e liberação de cache da GPU entre etapas, por restrição
  de VRAM (§5).

Estes achados são candidatos a fixar a versão do WhisperX no `environment.yml` e a
detalhar na DEC-008 (pendência §8).

---

## 4. Resultados

| Métrica | Resultado | Detalhe | Limiar provisório | Veredito |
|---|---|---|---|---|
| **WER** | **3,66 %** | 34 erros / 929 (17 subst, 12 del, 5 ins) | ≤ 15 % | verde |
| **TER** | **0,0 %** | 0 errados / 28 ocorrências ancoradas | ≤ 10 % | verde |
| **DER** | n/d | sem `ref.json` com tempos de falante | — | — |

Veredito da rodada: **verde**. O `large-v3` transcreveu PT-BR de reunião com 96,3 %
de acerto de palavra e acertou todas as 28 ocorrências de termos do domínio (Azul,
CCO, D0/D14, etc.). O TER é **significativo, não vácuo**: havia 28 ocorrências
ancoradas na referência.

---

## 5. Hipóteses do REP-001 §5 que esta rodada confirma

Esta é a primeira medição empírica do projeto; converte três hipóteses candidatas em
achados confirmados:

| Hipótese (REP-001 §5) | Estado anterior | Achado desta rodada |
|---|---|---|
| `large-v3` em `int8` cabe na GPU (GTX 1660 SUPER, 6 GB) | candidata | **Confirmada com ressalva**: cabe com `batch_size=4` e liberação de cache entre etapas. Com `batch_size=16` (default do código) estourou (CUDA OOM). |
| Ganho de qualidade de `large-v3` em PT-BR | candidata | **Indício forte**: WER 3,66 % numa amostra limpa. Falta comparar contra `medium` para isolar o ganho. |
| `initial_prompt` reduz erro em termos próprios | candidata | **Indício forte**: TER 0 % com prompt. Falta o par sem prompt (C-09, §7.2) para medir o delta. |

A confirmação plena de cada uma exige mais amostras e os experimentos comparativos
(ver §8); este REP move o estado de "não medido" para "primeira medição favorável".

---

## 6. Ressalvas (o que este número NÃO garante)

- **n = 1, áudio limpo.** Conversa de dois falantes, fala clara, 5 min. Reunião com
  ruído, sobreposição e mais participantes tende a piorar. 3,66 % é quase-melhor-caso.
- **Não-determinismo.** Outra rodada do ASR dá número levemente diferente.
- **Depende da conferência.** O gabarito é tão bom quanto a correção à mão; erro na
  referência vira ruído na métrica.
- **DER não medida.** A diarização separou 2 falantes de forma aparentemente correta,
  mas sem `ref.json` com tempos de falante a qualidade da diarização não tem número.
- **Comparativos pendentes.** Sem rodada sem `initial_prompt` (C-09) e sem
  comparação contra `medium`, o ganho de cada componente não está isolado.

---

## 7. Decisão sobre os limiares

**Manter os limiares provisórios** (WER ≤ 15 %, TER ≤ 10 %) por ora; **não apertar**
com base em n = 1. Um único áudio limpo não representa o pior caso, e apertar o
limiar agora arriscaria reprovar amostras mais difíceis que ainda são aceitáveis.
Revisitar a calibração após 2-3 amostras diversas (com ruído, mais falantes,
sobreposição), conforme o gatilho da SPEC-005 §9. O que não se dispensa é a medição:
calibrar o limiar é legítimo, medir não é opcional (SPEC-005 §5, R-EVAL-05).

---

## 8. Pendências e próximos passos

| Pendência | Descrição |
|---|---|
| Mais amostras de golden set | 2-3 trechos diversos (ruído, ≥ 3 falantes, sobreposição) para calibrar limiares com base representativa. |
| `ref.json` para DER | Referência com tempos de falante numa amostra, para habilitar a medição de diarização (SPEC-005 §4.3). |
| Experimento C-09 | Rodar a mesma amostra com e sem `initial_prompt` e medir o delta de TER (SPEC-005 §7.2). |
| Fixar versão do WhisperX | Pin no `environment.yml` para que os ajustes de API desta sessão não se repitam noutra máquina. |
| Detalhar diarização na DEC-008 | Registrar que o modelo real é `speaker-diarization-community-1` e o aceite de termos correspondente. |
| Tornar `batch_size` configurável | Hoje fixo em 4; deveria ser parâmetro por máquina/VRAM. |

---

## 9. Histórico

| Data | Versão | Evento |
|---|---|---|
| 2026-06-28 | v1 | REP-002 produzido em status `proposto`. Primeira execução real do eval do passo 01 (SPEC-005 §5). Amostra `trecho_eval` (5 min, 2 falantes, referência conferida à mão; desvio justificado da issue #10, que previa `audio_padrao`). Resultados: WER 3,66 % (34/929), TER 0,0 % (0/28), DER n/d; veredito verde, dentro dos limiares provisórios. Registra a configuração medida e os ajustes de API/VRAM que a primeira execução exigiu (DiarizationPipeline, `token=`, modelo `community-1`, `jsonschema`/`pyyaml`, `batch_size=4`). Confirma com ressalva três hipóteses do REP-001 §5 (VRAM, qualidade do `large-v3`, `initial_prompt`). Decide manter os limiares provisórios até haver 2-3 amostras diversas. Fecha o DoD-2 do script 01. |

---

*Fim do documento.*
