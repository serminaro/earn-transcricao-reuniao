# earn-transcricao-reuniao

Pipeline local para transcrever reuniões em português brasileiro, com identificação de quem falou (diarização) e geração eventual de ata estruturada. Ferramenta operacional pessoal e profissional, projeto solo. Não é SaaS, não é produto público, não é serviço com SLA.

O áudio é processado na máquina do autor (GPU NVIDIA dedicada). Apenas a etapa de ata usa um LLM em nuvem, e somente com o texto já transcrito, nunca com o áudio bruto.

## Estado atual

O andamento do trabalho vive no **board do fluxo** (GitHub Project), não neste README — que é vitrine, não rastreador de status (SPEC-004 §3, regra R-FLOW-04):

➡️ **Board:** https://github.com/users/serminaro/projects/1

A fundação documental e o método de trabalho (fluxo lean/kanban + protocolo de eval) estão concluídos. A construção técnica — SPECs de módulo, DECs de stack, código do pipeline e o golden set do eval — é puxada pelo board, cada item dirigido por uma SPEC e medido por um eval antes de ser dado por pronto.

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
data/     inventário por reunião (configs/) + áudio (audios/, fora do Git) + schema/ que valida ambos
outputs/  transcrições e atas; fora do Git
```

## Privacidade

Repositório público, mas o conteúdo das reuniões nunca entra no Git. Ficam fora via `.gitignore`: áudio (`*.ogg`, `*.m4a`, etc.), saídas do pipeline (`outputs/`) e segredos (`.env`). O `HF_TOKEN` da Hugging Face vive em variável de ambiente do conda, jamais em arquivo versionado. Regra auditável em SPEC-001 R-TAX-09 e SPEC-002 R-FUN-03.

## Governança documental (SERMI)

O projeto segue o padrão documental SERMI em perfil solo (quatro peças de fundação, ver DEC-001). Pontos de entrada:

Fundação:

- [SPEC-001 Taxonomia Documental](docs/SPEC/SPEC_001_Taxonomia_Documental.md)
- [SPEC-002 Descrição do Projeto](docs/SPEC/SPEC_002_Descricao_do_Projeto.md)
- [REP-001 Síntese da Fundação](docs/REP/REP_001_Sintese_Fundacao.md)
- [DEC-001 Fundação reflexiva](docs/DEC/DEC_001_Fundacao_Reflexiva.md)

Método e processo:

- [DEC-002 Adoção do spec-driven](docs/DEC/DEC_002_Adocao_Spec_Driven.md) · [GUIDE-001 Desenvolvimento dirigido por SPEC](docs/GUIDE/GUIDE_001_Desenvolvimento_Dirigido_por_Spec.md)
- [SPEC-004 Método de Trabalho (lean/kanban)](docs/SPEC/SPEC_004_Metodo_de_Trabalho.md) · [SPEC-005 Protocolo de Avaliação (eval)](docs/SPEC/SPEC_005_Protocolo_de_Avaliacao.md)
- [DEC-003 Reserva do número SPEC-003](docs/DEC/DEC_003_Reserva_Numeracao_SPEC_003.md) (SPECs técnicas a partir de SPEC-004)

## Ambiente

Python 3.10+, gerenciado por conda. O `environment.yml` é mínimo de propósito na fundação: as dependências pesadas entram nas Ondas 2 e 3, cada uma rastreada por uma DEC.

```bash
conda env create -f environment.yml
conda activate earn-transcricao-reuniao
```
