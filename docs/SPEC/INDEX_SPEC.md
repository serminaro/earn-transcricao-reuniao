# Índice de SPECs

> Lista canônica das especificações do projeto earn-transcricao-reuniao.
> Atualizado a cada nova SPEC ou nova versão.
> Índice recomendado pela SPEC-001 §8.

## SPECs vigentes

| Número | Título | Versão | Status | Resumo |
|---|---|---|---|---|
| [SPEC-001](SPEC_001_Taxonomia_Documental.md) | Taxonomia Documental do Projeto | v1 | proposto | Define os tipos SERMI aplicados, estrutura de pastas, frontmatter, numeração, privacidade do repo público e as regras checáveis R-TAX-01 a R-TAX-10. |
| [SPEC-002](SPEC_002_Descricao_do_Projeto.md) | Descrição do Projeto | v1 | proposto | Propósito, escopo, decomposição do pipeline (3 scripts), critérios de sucesso C-01 a C-09, cláusula Operação Solo e regras checáveis R-FUN-01 a R-FUN-08. |
| *SPEC-003* | *(reservada — Contrato de Responsabilidade)* | — | reservado | Número reservado por **DEC-003** ao Contrato de Responsabilidade; só produzido se o projeto graduar para a fundação de cinco peças (DEC-001 §6). Não existe arquivo enquanto a reserva vigora. |
| [SPEC-004](SPEC_004_Metodo_de_Trabalho.md) | Método de Trabalho (lean/kanban dirigido por SPEC) | v1 | proposto | Fluxo lean/kanban no GitHub, limites de WIP, Definition of Ready/Done, ponte board ↔ acervo SERMI, mapa de labels/templates e regras checáveis R-FLOW-01 a R-FLOW-05. |
| [SPEC-005](SPEC_005_Protocolo_de_Avaliacao.md) | Protocolo de Avaliação (eval) | v1 | proposto | Golden set fora do Git, métricas WER/TER/DER, runner sobre o script 01, normalização, limiares provisórios (WER ≤ 15%, TER ≤ 10%) e registro de resultados. Operacionaliza C-08/C-09; é o portão DoD-2 da SPEC-004. Regras R-EVAL-01 a R-EVAL-05. |
| [SPEC-006](SPEC_006_Schema_JSON_Contrato_de_Dados.md) | Schema do JSON fonte de verdade (contrato de dados) | v1 | proposto | Fixa o schema do JSON que o 01 produz e o 02/03 consomem: envelope com metadados (DEC-004), falante em dois campos (DEC-005), invariantes, modos de falha e versionamento. Carrega o artefato executável `data/schema/transcricao.schema.json`. Referência comum das SPECs de módulo. Regras R-SCHEMA-01 a R-SCHEMA-05. |

## SPECs históricas (superseded ou descartadas)

(nenhuma ainda)
