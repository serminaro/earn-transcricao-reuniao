# earn-transcricao-reuniao

Pipeline local para transcrever reuniões em português brasileiro, com identificação de quem falou (diarização) e geração eventual de ata estruturada. Ferramenta operacional pessoal e profissional, projeto solo. Não é SaaS, não é produto público, não é serviço com SLA.

O áudio é processado na máquina do autor (GPU NVIDIA dedicada). Apenas a etapa de ata usa um LLM em nuvem, e somente com o texto já transcrito, nunca com o áudio bruto.

## Estado atual

Fundação documental (Onda 1) concluída. O código do pipeline ainda não foi escrito; ver o plano de ondas abaixo.

| Onda | Entrega | Estado |
|---|---|---|
| 1. Fundação documental | 4 peças SERMI (SPEC-001, REP-001, DEC-001, SPEC-002) e estrutura do repositório | Concluída (status `proposto`) |
| 2. Documentação técnica | DECs de stack (D1 a D11) e SPECs de glossário, ambiente e schema de configuração | A fazer |
| 3. Código | `01_transcrever.py`, `02_aplicar_mapeamento.py`, `03_gerar_ata.py` | A fazer |
| 4. Integração Cowork | `COWORK.md` na raiz | A fazer |

## Como o pipeline vai funcionar

Três scripts numerados, executados em ordem. O JSON é a fonte de verdade; TXT, SRT e ata derivam dele, de modo que reprocessar não exige re-transcrever.

```
audio  ──►  01_transcrever.py    ──►  {nome}.json / .txt / .srt   (com SPEAKER_XX)
                                          │
            02_aplicar_mapeamento.py  ──► {nome}.json / .txt / .srt   (nomes reais, via YAML)
                                          │
            03_gerar_ata.py           ──► {nome}_ata.md               (LLM em nuvem, sob demanda)
```

Stack consolidada (a formalizar em DECs na Onda 2): WhisperX com modelo `large-v3`, `compute_type=int8`, `condition_on_previous_text=False`, VAD ativo, `initial_prompt` por reunião; diarização via pyannote.audio; ata via API Anthropic.

## Estrutura do repositório

```
docs/
  SPEC/   especificações estruturais  (+ INDEX_SPEC.md)
  REP/    relatórios
  DEC/    registros de decisão        (+ INDEX_DEC.md)
  GUIDE/  guias operacionais
  BRIEF/  resumos e vitrine
  assets/ insumos (inclui o briefing original em assets/shared/)
  logs/   logs de auditoria e execução
src/      os três scripts do pipeline (Onda 3)
data/     configs por reunião; áudio fica fora do Git
outputs/  transcrições e atas; fora do Git
```

## Privacidade

Repositório público, mas o conteúdo das reuniões nunca entra no Git. Ficam fora via `.gitignore`: áudio (`*.ogg`, `*.m4a`, etc.), saídas do pipeline (`outputs/`) e segredos (`.env`). O `HF_TOKEN` da Hugging Face vive em variável de ambiente do conda, jamais em arquivo versionado. Regra auditável em SPEC-001 R-TAX-09 e SPEC-002 R-FUN-03.

## Governança documental (SERMI)

O projeto segue o padrão documental SERMI em perfil solo (quatro peças de fundação, ver DEC-001). Pontos de entrada:

- [SPEC-001 Taxonomia Documental](docs/SPEC/SPEC_001_Taxonomia_Documental.md)
- [SPEC-002 Descrição do Projeto](docs/SPEC/SPEC_002_Descricao_do_Projeto.md)
- [REP-001 Síntese da Fundação](docs/REP/REP_001_Sintese_Fundacao.md)
- [DEC-001 Fundação reflexiva](docs/DEC/DEC_001_Fundacao_Reflexiva.md)

## Ambiente

Python 3.10+, gerenciado por conda. O `environment.yml` é mínimo de propósito na fundação: as dependências pesadas entram nas Ondas 2 e 3, cada uma rastreada por uma DEC.

```bash
conda env create -f environment.yml
conda activate earn-transcricao-reuniao
```
