# Índice de DECs

> Lista canônica das decisões registradas do projeto earn-transcricao-reuniao.
> Atualizado a cada nova DEC produzida, superseded ou descartada.
> Índice obrigatório por força da SPEC-001 §8 e da regra R-TAX-06.

## DECs vigentes

| Número | Título | Status | Resumo |
|---|---|---|---|
| [DEC-001](DEC_001_Fundacao_Reflexiva.md) | Fundação reflexiva: adoção do padrão documental SERMI enxuto (perfil solo) | proposto (v1) | Adota a fundação SERMI de perfil solo (DEC-META-004): quatro peças (SPEC-001, REP-001, DEC-001, SPEC-002 com cláusula Operação Solo), dispensada a SPEC-003. Fixa a auditoria recorrente das regras R-* como freio compensatório. |
| [DEC-002](DEC_002_Adocao_Spec_Driven.md) | Adoção do desenvolvimento dirigido por SPEC (spec-driven) | proposto (v1) | Adota o método spec-driven (operacionalizado no GUIDE-001, ancorado no GUIDE-META-001) para construir o pipeline: a SPEC dirige o código e o eval prova. Verificação em dois planos (gov-check documental, eval funcional). |
| [DEC-003](DEC_003_Reserva_Numeracao_SPEC_003.md) | Reserva do número SPEC-003 ao eventual Contrato de Responsabilidade | proposto (v1) | Reserva o slot SPEC-003 ao Contrato de Responsabilidade (só produzido se graduar para cinco peças, DEC-001 §6); SPECs técnicas a partir de SPEC-004. Ajusta R-TAX-03/§5 da SPEC-001 para admitir número reservado por DEC como lacuna legítima. |
| [DEC-004](DEC_004_Envelope_de_Metadados_no_JSON.md) | Envelope de metadados no JSON fonte de verdade | proposto (v1) | Adota o envelope (`schema_version` + `metadata` + `segments`) para o JSON fonte de verdade, em vez do output cru do WhisperX, habilitando proveniência (lineage) ao eval (SPEC-005 §6). Sustenta a SPEC-006. |
| [DEC-005](DEC_005_Falante_em_Dois_Campos.md) | Falante em dois campos no JSON (speaker_raw + speaker) | proposto (v1) | Representa o falante em dois campos (`speaker_raw` imutável + `speaker` mapeado) com flag `speakers_mapped`, em vez de renomear no lugar, tornando o passo 02 idempotente e re-executável sem re-transcrever. Sustenta a SPEC-006. |
| [DEC-006](DEC_006_Uma_SPEC_por_Script.md) | Uma SPEC-contrato por script do pipeline | proposto (v1) | Fixa o mapa SPEC ↔ script (GUIDE-001 §7): uma SPEC por script (SPEC-009 `01_transcrever`, SPEC-010 `02_aplicar_mapeamento`, SPEC-011 `03_gerar_ata`), cada uma referenciando o contrato de dados da SPEC-006. Descarta a SPEC única de pipeline. (007/008 ficam para glossário e schema do YAML, plano da Onda 2.) |
| [DEC-007](DEC_007_Motor_de_Transcricao.md) | Motor de transcrição — WhisperX (large-v3, int8, VAD) | proposto (v1) | Primeira DEC de stack: adota o WhisperX (`large-v3`, `compute_type=int8`, VAD ativo, `condition_on_previous_text=False`) como motor do passo 01, gravando os parâmetros em `metadata.params` (DEC-004). Descarta `openai-whisper` puro, `faster-whisper` sozinho e ASR em nuvem (por C-03). Sustenta a SPEC-009. |
| [DEC-008](DEC_008_Diarizacao_de_Falantes.md) | Diarização de falantes — pyannote.audio | proposto (v1) | Segunda DEC de stack: adota o `pyannote.audio` (integrado ao WhisperX, DEC-007) como diarizador do passo 01; labels crus vão para `speaker_raw` e congelam (DEC-005). Assume modelo gated e `HF_TOKEN` em ambiente (R-TAX-09). Descarta NeMo, ausência de diarização (C-02) e diarizador default opaco. Sustenta a SPEC-009. |

## DECs históricas (superseded ou descartadas)

(nenhuma ainda)

## Relação SPEC × DEC supersedente

(nenhuma registrada)
