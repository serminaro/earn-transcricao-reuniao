---
documento: GUIDE-002
titulo: Como transcrever uma reunião (uso do 01_transcrever)
versao: v1
status: proposto
data: 2026-06-29
autor: Bruno Serminaro
supersede: —
referencia: SPEC-008, SPEC-009, SPEC-006, DEC-005, DEC-007, DEC-008, GUIDE-001
---

# GUIDE-002 · Como transcrever uma reunião (uso do `01_transcrever`)

> O passo-a-passo concreto para transcrever um áudio de reunião com o pipeline já
> pronto (módulo 01). Onde o GUIDE-001 ensina *como construir* dirigido por SPEC,
> este ensina *como operar* o que foi construído. Reflete o contrato vigente da
> SPEC-008 (entrada = só o inventário) e da SPEC-009 (comportamento do 01).

---

## 1. Objetivo e quando usar

Use este guia quando tiver um áudio de reunião gravado e quiser a transcrição com
marcação de **quem falou**. O `01_transcrever` produz, a partir do áudio:

- **`{nome}.json`** — a **fonte de verdade** (envelope com metadados e segmentos, SPEC-006);
- **`{nome}.txt`** — texto legível, cada fala prefixada pelo rótulo do falante (`SPEAKER_00: ...`);
- **`{nome}.srt`** — legenda com tempos.

O que **ainda é manual** nesta fase do projeto: trocar `SPEAKER_00/01/...` pelos nomes
reais e gerar a ata. Os módulos 02 (mapeamento) e 03 (ata) ainda não existem (§10).

---

## 2. Pré-requisitos

Confira uma vez, antes da primeira transcrição:

| Requisito | Como garantir |
|---|---|
| Ambiente conda ativo | `conda activate earn-transcricao-reuniao` |
| GPU NVIDIA com CUDA | Recomendado (GTX 1660 SUPER 6 GB é o alvo). Sem GPU, é possível rodar com `--cpu`, ordens de grandeza mais lento. |
| `HF_TOKEN` no ambiente | Vive em variável de ambiente do conda (nunca em arquivo). Necessário para baixar o modelo de diarização (gated). |
| Modelo de diarização aceito | Aceitar os termos de `pyannote/speaker-diarization-community-1` na Hugging Face (uma vez, com a mesma conta do `HF_TOKEN`). |

Rodar **da raiz do projeto** (`/home/bruno/Projetos/earn-transcricao-reuniao/`).

---

## 3. Passo 1 — Colocar o áudio

Copie o arquivo de áudio (`.m4a`, `.wav`, `.ogg`, `.mp3`, ...) para **`data/audios/`**:

```bash
cp ~/Downloads/reuniao_gabriel.m4a data/audios/
```

`data/audios/` é a **pasta única** de áudio (SPEC-008 §4), gitignored — o áudio nunca
entra no Git. Não há pasta de "pendentes/processados": um áudio é considerado
**transcrito** quando já existe o `outputs/transcricoes/{nome}.txt` correspondente.

---

## 4. Passo 2 — Criar o inventário

O inventário é o YAML que descreve a reunião — a **única** entrada do 01. Copie o
template e preencha:

```bash
cp data/configs/reuniao.template.yml data/configs/reuniao_gabriel.yml
```

Preencha os campos (o template traz exemplo e explicação em cada um):

```yaml
audio: reuniao_gabriel.m4a        # OBRIGATÓRIO: só o nome do arquivo em data/audios/
language: pt                      # opcional; default é pt
vocabulario:                      # nomes próprios e jargão — ancoram o ASR nesses termos
  - Bruno Serminaro
  - Gabriel Dorte
  - Azul
  - CCO
participantes:                    # referência sua; ajuda a montar o speaker_mapping depois
  - Bruno Serminaro
  - Gabriel Dorte
```

Notas:

- **`audio` é só o nome**, sem caminho (`data/audios/...` é divergência). O 01 resolve
  o arquivo em `data/audios/`.
- O 01 monta o `initial_prompt` a partir do `vocabulario` — liste aí os nomes e termos
  que costumam sair errados, que a transcrição acerta mais. Se quiser controlar o prompt
  inteiro, preencha `initial_prompt:` explicitamente (ele prevalece sobre `vocabulario`).
- **`speaker_mapping` fica para depois** (Passo 4): os rótulos `SPEAKER_xx` só existem
  após a diarização rodar.
- O inventário é gitignored (carrega nomes); só o `reuniao.template.yml` é versionado.

---

## 5. Passo 3 — Rodar o 01

Da raiz, com o ambiente ativo:

```bash
python -m src.transcrever data/configs/reuniao_gabriel.yml
```

Sem GPU, force CPU conscientemente:

```bash
python -m src.transcrever data/configs/reuniao_gabriel.yml --cpu
```

A saída vai por convenção para **`outputs/transcricoes/`**, com o nome derivado do áudio:

```
outputs/transcricoes/reuniao_gabriel.json   (fonte de verdade)
outputs/transcricoes/reuniao_gabriel.txt    (legível, com SPEAKER_xx)
outputs/transcricoes/reuniao_gabriel.srt    (legenda)
```

O 01 valida o inventário **antes** de transcrever: se faltar `audio` ou um campo
estiver com tipo errado, ele falha de cara apontando o campo, sem iniciar a transcrição.

---

## 6. Passo 4 — Conferir e mapear os falantes

Abra o `.txt` e veja quem é cada rótulo:

```
SPEAKER_00: Eu tenho uma conta da empresa, mas não consegui fazer a separação ainda.
SPEAKER_01: A gente separa o dinheiro, né? Como você recebe?
```

A diarização atribui `SPEAKER_00`, `SPEAKER_01`, ... em tempo de execução — os números
são arbitrários (o `SPEAKER_00` de uma rodada pode ser outra pessoa noutra). **Ela pode
achar um falante a mais** do que você esperava: numa entrevista de 2 pessoas pode surgir
um `SPEAKER_02` de uma voz de fundo real (aconteceu na entrevista com a Mariana, uma voz
de fora da conversa). Por isso o mapeamento é humano: ouça/leia e decida.

Depois, registre o mapeamento no inventário, para o futuro passo 02 (DEC-005):

```yaml
speaker_mapping:
  SPEAKER_00: Bruno Serminaro
  SPEAKER_01: Gabriel Dorte
```

Enquanto o 02 não existe, esse mapa é a sua anotação de quem é quem; a substituição
no texto ainda é manual (§10).

---

## 7. O que esperar na execução

O 01 roda, em ordem, sobre uma só carga do áudio (SPEC-009 §4): detecção de voz (VAD),
transcrição (WhisperX `large-v3`/`int8`), alinhamento palavra-a-palavra, diarização
(pyannote) e o empacotamento no JSON. O tempo é proporcional à duração do áudio (alguns
minutos para reuniões de dezenas de minutos na GPU alvo).

**Memória da GPU (6 GB):** o `batch_size` é fixado em 4 e o cache da GPU é liberado entre
as etapas para caber. Mesmo assim, em áudio longo a diarização pode estourar a VRAM —
nesse caso o 01 **cai sozinho para CPU só na diarização** (mais lenta, mas conclui),
mantendo transcrição e alinhamento na GPU. Você não precisa fazer nada; é automático.

---

## 8. Modos de falha comuns

O 01 **falha cedo** e com mensagem clara. Os casos mais comuns:

| Sintoma | Causa | O que fazer |
|---|---|---|
| "Inventário não-conforme em '...'" | Campo faltando/tipo errado no YAML | Corrija o campo apontado; `audio` é obrigatório. |
| "Áudio '...' não encontrado em data/audios/" | `audio` aponta para arquivo inexistente | Confira o nome e se o arquivo está em `data/audios/`. |
| "HF_TOKEN ausente no ambiente" | Token não exportado no conda | Defina o `HF_TOKEN` no ambiente (e aceite os termos do modelo no HF). |
| "CUDA indisponível: o 01 exige GPU NVIDIA" | Sem GPU e sem a flag | Rode com `--cpu` se quiser mesmo assim (ciente da lentidão). |

---

## 9. Privacidade

O repositório é público; o conteúdo das reuniões **nunca** entra no Git (R-TAX-09 / R-FUN-03):

- **Fora do Git:** os áudios (`data/audios/`), as saídas (`outputs/`) e as instâncias de
  inventário (`data/configs/*.yml`/`*.yaml`, que carregam nomes).
- **Versionados:** apenas o template `reuniao.template.yml` e o schema `reuniao.schema.json`.
- O `HF_TOKEN` vive em variável de ambiente, jamais em arquivo.

---

## 10. Limitações atuais

- **02 e 03 ainda não existem.** Trocar `SPEAKER_xx` pelos nomes reais e gerar a ata é
  manual por enquanto. O `speaker_mapping` no inventário já deixa o trabalho pronto para
  quando o 02 (SPEC-010) existir.
- **Reprocessar não re-transcreve.** O JSON é a fonte de verdade; TXT e SRT são derivados
  puros dele. Regerá-los (no futuro) não re-invoca o ASR — não há custo de re-transcrição.
- **A transcrição não é determinística** (DEC-002): re-rodar o 01 sobre o mesmo áudio pode
  dar pequenas variações. Para comparar versões, compare o JSON.

---

## 11. Histórico

| Data | Versão | Evento |
|---|---|---|
| 2026-06-29 | v1 | GUIDE-002 produzido em status `proposto`, puxado de três transcrições reais (Gabriel ~23 min; entrevista Mariana em duas partes). Descreve o uso operacional do `01_transcrever` sob o contrato vigente: entrada só pelo inventário (SPEC-008), áudio em `data/audios/`, saída por convenção em `outputs/transcricoes/`, mapeamento de falantes pós-01 (DEC-005), fallback GPU→CPU da diarização sob OOM e modos de falha. Cobre apenas o módulo 01; 02/03 ficam como trabalho manual até existirem. |

---

*Fim do documento.*
