---
documento: DEC-008
titulo: Diarização de falantes — pyannote.audio
versao: v1
status: proposto
data: 2026-06-27
autor: Bruno Serminaro
supersede: —
referencia: SPEC-009, SPEC-002, SPEC-005, SPEC-006, DEC-002, DEC-007, SPEC-001
---

# DEC-008 · Diarização de falantes

> Decisão atômica de stack: quem responde "quem falou" no passo 01. Adota
> **pyannote.audio**, integrado ao WhisperX (DEC-007). Os labels crus que ele produz
> alimentam `speaker_raw` no schema (SPEC-006/DEC-005). Segunda das duas DECs de stack
> que a SPEC-009 referencia. Não decide o motor de transcrição (DEC-007) nem como o
> falante vira nome real (isso é o passo 02 + YAML, DEC-005).

---

## 1. Contexto

A SPEC-002 **C-02** exige saber **quem** falou em cada trecho (diarização), não só o
texto. O schema (SPEC-006, DEC-005) reserva para isso o campo `speaker_raw` — o label
cru do diarizador, imutável — que o passo 02 depois traduz em nome real (`speaker`).

O motor escolhido na DEC-007 (WhisperX) orquestra a diarização, mas precisa de um
**diarizador** por baixo. Esta DEC fixa qual, antes de codar o 01 (DoR, R-FUN-02).

---

## 2. Decisão

**Adotar o `pyannote.audio` como diarizador do passo 01, integrado ao WhisperX
(DEC-007).** Os labels crus do pyannote (`SPEAKER_00`, `SPEAKER_01`…) são gravados em
`speaker_raw` e congelados ali (DEC-005); o passo 02 os lê para preencher `speaker`,
sem nunca reescrevê-los.

A decisão inclui assumir que o modelo do pyannote é **gated** no Hugging Face: exige
aceitar os termos uma vez e um `HF_TOKEN` para baixar os pesos. O token vive em
variável de ambiente do conda, **nunca** em arquivo versionado (SPEC-002 §9,
R-TAX-09); sua ausência é modo de falha tratado na SPEC-009 §6.

---

## 3. Origem / rastro

| Artefato | Como sustenta esta decisão |
|---|---|
| **SPEC-002 C-02** | Exige diarização ("quem falou"); sem diarizador o critério não se cumpre. |
| **SPEC-006 / DEC-005** | `speaker_raw` é exatamente o label cru que o pyannote produz. |
| **DEC-007** | O WhisperX integra o pyannote; a escolha do diarizador encaixa no motor já decidido. |
| **README** | Registra o pyannote como stack consolidada; esta DEC formaliza. |
| **SPEC-009** | Consumidora: o comportamento e os modos de falha do 01 (incl. `HF_TOKEN`) assumem este diarizador. |

---

## 4. Alternativas consideradas

### 4.1 NeMo (NVIDIA) para diarização

Usar o toolkit NeMo, que também faz diarização de boa qualidade.

**Descartada porque:**
- Traz uma stack adicional pesada e menos integrada ao WhisperX; o ganho não se
  justifica num projeto solo, onde simplicidade de manutenção pesa mais que o último
  ponto percentual de DER.

### 4.2 Sem diarização (só transcrição)

Entregar o texto com tempos, sem atribuir falante.

**Descartada porque:**
- Viola **C-02** e esvazia o passo 02 e a ata (03), que precisam de "quem falou". O
  `speaker_raw` do schema ficaria sempre nulo.

### 4.3 Diarizador "default" opaco, sem fixar versão/token

Aceitar o que o WhisperX usar por baixo sem adotar o pyannote explicitamente.

**Descartada porque:**
- Por baixo já é o pyannote; não adotá-lo de forma explícita nos tira o controle de
  **versão** e a clareza sobre o `HF_TOKEN`, e deixa o rastro da decisão implícito —
  o oposto do que o método pede (DEC-002).

---

## 5. Consequências

### 5.1 Consequências positivas

- **Cumpre C-02.** Produz o `speaker_raw` que o schema espera, integrado ao motor.
- **Estado da arte aberto.** Boa qualidade de diarização sem serviço de nuvem.
- **Rastro de versão sob controle.** Adoção explícita permite fixar a versão do modelo.

### 5.2 Consequências negativas / custo aceito

- **Introduz o `HF_TOKEN` e um passo manual de setup** (aceitar termos do modelo
  gated). É o custo de usar um modelo gated; tratado como modo de falha claro na
  SPEC-009 §6 e protegido pela regra de privacidade (R-TAX-09).
- **Diarização é imperfeita.** Pode trocar ou perder falante. Mitigado pelo desenho do
  schema: `speaker_raw` separado de `speaker`, e o passo 02 corrige nomes a partir de
  um `speaker_raw` estável (DEC-005). Trecho sem falante fica `speaker_raw=null`
  (SPEC-009 §4.1), não erro.
- **Qualidade ainda não medida.** A DER depende de referência word-level com falantes
  (`ref.json`), que o golden set ainda não tem (SPEC-005 §4.3): por ora a diarização
  não tem número de eval.
- **Roda melhor em GPU**, herdando o mesmo acoplamento da DEC-007.

### 5.3 O que esta decisão NÃO resolve

- **Não nomeia o falante real.** Isso é o passo 02 + YAML (DEC-005).
- **Não mede a qualidade da diarização** (DER): depende de `ref.json` (SPEC-005).
- **Não decide o motor de transcrição**: DEC-007.

---

## 6. Critérios de reavaliação

| Gatilho | O que reavaliar |
|---|---|
| O eval ganhar `ref.json` e a DER ficar ruim | Testar outro diarizador ou ajustar parâmetros do pyannote. |
| Surgir diarizador aberto melhor, ou sem gating | Comparar custo/qualidade contra o pyannote. |
| O pyannote mudar licença/gating de forma que atrapalhe o setup | Reavaliar a dependência e o passo de token. |
| O WhisperX trocar o diarizador padrão | Realinhar a integração. |

---

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-06-27 | DEC-008 v1 produzida em status `proposto`. Oitava DEC; segunda de stack. Adota o `pyannote.audio` como diarizador do passo 01, integrado ao WhisperX (DEC-007); labels crus vão para `speaker_raw` e são congelados (DEC-005). Assume o modelo gated e o `HF_TOKEN` em ambiente (R-TAX-09). Descarta NeMo, ausência de diarização (C-02) e diarizador default opaco. Sustenta a SPEC-009. |

---

*Fim do documento.*
