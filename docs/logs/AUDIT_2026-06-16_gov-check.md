# Log de auditoria — gov-check 2026-06-16

Registro da rodada de auditoria de consistência (skill `gov-check`) do projeto
earn-transcricao-reuniao. Cumpre a cláusula "Operação Solo" da SPEC-002 §6: onde
um projeto com equipe teria ata de revisão humana, este projeto registra a
auditoria das regras `R-*`.

- **Data:** 2026-06-16
- **Gatilho:** por marco (primeiro item técnico da Onda 2: contrato de dados do pipeline).
- **Perfil detectado:** solo (4 peças).
- **Escopo:** SPEC-001 (R-TAX-01..10), SPEC-002 (R-FUN-01..08), estado real do repositório.
- **Entrega auditada:** DEC-004 (envelope de metadados), DEC-005 (falante em dois campos), SPEC-006 (schema do JSON fonte de verdade) + artefato `data/schema/transcricao.schema.json`; índices INDEX_DEC e INDEX_SPEC atualizados.
- **Branch:** `onda2/spec-006-schema-json` (sem commit no momento da auditoria).

## Resultado

Passada determinística: **limpa** (exit 0; 0 divergências estruturais/fundacionais).
Passada semântica: **limpa** (0 divergências).

### Regras auto (passada determinística)

Conforme em bloco: R-TAX-01 (frontmatter, sem `categoria:`), R-TAX-02
(nomenclatura snake_case ASCII), R-TAX-03 (numeração: DEC 001-005 contígua; SPEC
006 após o slot 003 reservado por DEC-003), R-TAX-04 (status válidos), R-TAX-05
(reciprocidade de supersede; nenhum superseded), R-TAX-06 (INDEX_DEC completo),
R-TAX-07 (estrutura de pastas), R-TAX-08 (N/A: nenhuma DEC `aprovado`), R-TAX-10
(quatro peças fundacionais com referência mútua e cláusula Operação Solo),
R-FUN-07 e R-FUN-08 (referência cruzada e cláusula Operação Solo com cadência).

### Regras semânticas

| Regra | Sev. | Veredito |
|---|---|---|
| R-TAX-09 privacidade | Crítica | Conforme. Nenhum áudio/output/`.env` rastreado; `.gitignore` cobre os padrões; sem segredo real em arquivo versionado (as ocorrências de `HF_TOKEN=hf_<seu_token>` em SPEC-001 §9 e no briefing são placeholder documentado, não token). |
| R-FUN-03 sensível fora do Git | Crítica | Conforme. Reforça R-TAX-09. O novo caminho versionado `data/schema/` carrega só estrutura (JSON Schema), não conteúdo de reunião. |
| R-FUN-04 sem ASR em nuvem | Crítica | N/A. Scripts `src/01-03` ainda não existem. |
| R-FUN-05 ata isolada no 03 | Alta | N/A. Idem. |
| R-FUN-02 dependência → DEC | Alta | Conforme. `environment.yml` inalterado nesta entrega (`python` + `pip`); nenhuma dependência nova introduzida. |
| R-FUN-01 trio JSON/TXT/SRT | Média | N/A. `outputs/transcricoes/` vazio (nenhuma reunião processada). |
| R-FUN-06 todo C-NN verificável | Média | Conforme. SPEC-002 §5 inalterada. |

### Verificações extras (o que regra nenhuma pega)

- Índices coerentes com os arquivos presentes (INDEX_DEC lista DEC-001..005;
  INDEX_SPEC lista SPEC-001/002/[003 reservada]/004/005/006).
- Nenhum documento com `status: aprovado` foi editado (todos seguem `proposto`).
- `versao`/`status`/Histórico coerentes nos três documentos novos.
- Reciprocidade de referência entre DEC-004/DEC-005 e SPEC-006.

## Nota de escopo (não é divergência)

As regras `R-SCHEMA-01..05` declaradas na SPEC-006 **não** são lidas pelo
`gov-check` (o skill lê regras `R-*` só das SPECs de fundação, SPEC-001/002).
Coerente com a ressalva explícita da SPEC-006 §8, igual à de SPEC-004 §8 e
SPEC-005 §8. Serão verificadas por teste determinístico quando os scripts
existirem, ou migradas para `R-FUN-*` da SPEC-002 quando estabilizarem.

## Estado pós-sessão

- Auditoria **verde**, nenhuma divergência aberta, nenhum caminho de correção a decidir.
- Pendência futura registrada (não é divergência atual): a dependência
  `jsonschema`, que o runner do eval usará para validar o artefato de schema,
  precisará de DEC própria quando o runner for escrito (R-FUN-02).
- Próxima auditoria: por calendário (mensal) ou por marco (próxima SPEC de módulo
  ou primeira execução real do pipeline).
