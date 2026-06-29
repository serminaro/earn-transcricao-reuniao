# Golden set — estrutura (SPEC-005 §2)

> **Esta pasta inteira é gitignored** (`.gitignore` → `data/golden/`). Áudio e
> transcrição de referência contêm teor de reuniões reais (conteúdo sensível) e
> **nunca** são versionados (SPEC-005 §2.2, R-EVAL-01, SPEC-001 §9, SPEC-002 §4.4).
> Estes arquivos de estrutura (`README.md`, `meta.template.yml`) também ficam
> apenas no working tree local — servem de guia para montar amostras à mão.
>
> Só o **sumário agregado de métricas** (números e veredito, sem texto de reunião)
> é versionável, e vive em `docs/logs/` ou num REP (SPEC-005 §6, R-EVAL-04).

## O que é

O golden set é o conjunto de **amostras de referência** contra as quais a qualidade
do pipeline de transcrição é medida (WER, TER, e DER quando houver referência rica).
Cada amostra é um par `(áudio, transcrição de referência conferida à mão)` — o
"gabarito": o que o pipeline *deveria* ter produzido (SPEC-005 §2.1).

## Estrutura por amostra

Uma subpasta por amostra, nomeada por um `<id_amostra>` curto e estável:

```
data/golden/                         (gitignored — sensível)
├── README.md                        este guia (estrutura)
├── meta.template.yml                template comentado de meta.yml
│
├── <id_amostra>/
│   ├── audio.<ext>                  o áudio da amostra (.m4a, .wav, .mp3, ...)
│   ├── ref.txt                      transcrição de referência (texto por falante)
│   ├── ref.json                     (opcional) referência word-level com falantes, p/ DER
│   └── meta.yml                     vocabulário ancorado, falantes, duração, fonte
│
└── audio_padrao/                    amostra 0 (semente) — só texto: habilita WER e TER
    ├── audio.m4a
    ├── ref.txt
    └── meta.yml
```

### Arquivos de cada amostra

| Arquivo | Obrigatório | Conteúdo |
|---|---|---|
| `audio.<ext>` | sim | O áudio da amostra. Recorte de 2 a 10 min basta (SPEC-005 §2.3). |
| `ref.txt` | sim | Transcrição de referência em texto, conferida à mão, palavra a palavra, com nomes e jargão corretos. Habilita **WER** e **TER**. |
| `ref.json` | opcional | Referência *word-level* com segmentos rotulados por falante. Habilita **DER** ("quem falou quando"). Enquanto ausente, a DER fica fora de escopo e é registrada como `n/d` (SPEC-005 §4.3). |
| `meta.yml` | sim | Metadados da amostra: vocabulário ancorado (que a TER mede), falantes, duração, fonte. Ver `meta.template.yml`. |

## Como construir uma amostra (SPEC-005 §2.3)

1. **Escolher** um áudio curto e representativo (2–10 min; o custo de conferir cresce com a duração).
2. **Rascunhar**: rodar o pipeline uma vez para obter um rascunho, **e então corrigir à mão** até a referência ficar fiel — palavra a palavra, com os nomes e o jargão corretos.
3. **Registrar** em `meta.yml` o vocabulário ancorado (nomes próprios, termos técnicos) que a TER vai medir, e os falantes.

> **R-EVAL-03 (crítica):** a referência é **conferida por humano**; nunca é a saída
> crua da própria pipeline sob avaliação. Referência auto-gerada e não revisada é
> circular — mediria a pipeline contra si mesma.

## Amostra 0 (semente)

A semente é o áudio `data/audios/audio_padrao_morgado.m4a` (pasta única, SPEC-008 §4);
o `ref.txt` é a transcrição de referência **conferida por humano** (R-EVAL-03), não a
saída crua da pipeline. Migra para `data/golden/<amostra>/` como **amostra 0**:
referência só de texto, habilita **WER** e **TER**, ainda não **DER** (SPEC-005 §2.2).
A amostra-0 do baseline (REP-002) é `trecho_eval`. Para montar uma amostra localmente
(não versionado):

```bash
mkdir -p data/golden/audio_padrao
cp data/audios/audio_padrao_morgado.m4a data/golden/audio_padrao/audio.m4a
# ref.txt: transcreva e CONFIRA à mão (R-EVAL-03); nunca a saída crua da pipeline
$EDITOR data/golden/audio_padrao/ref.txt
cp data/golden/meta.template.yml data/golden/audio_padrao/meta.yml
# depois: editar meta.yml com o vocabulário ancorado, falantes, duração e fonte reais
```

## Referências

- `docs/SPEC/SPEC_005_Protocolo_de_Avaliacao.md` — protocolo de eval (golden set, métricas, runner, thresholds, R-EVAL-01..05).
- `docs/SPEC/SPEC_006_Schema_JSON_Contrato_de_Dados.md` e `data/schema/transcricao.schema.json` — forma do JSON de hipótese; `ref.json` segue o mesmo word-level com falantes.
