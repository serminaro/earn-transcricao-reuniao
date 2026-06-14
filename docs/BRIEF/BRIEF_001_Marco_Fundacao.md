---
documento: BRIEF-001
titulo: Marco de fechamento da fundação documental do projeto earn-transcricao-reuniao
versao: v1
status: proposto
data: 2026-06-14
autor: Bruno Serminaro
supersede: —
referencia: SPEC-001, REP-001, DEC-001, SPEC-002
---

# BRIEF-001 · Marco de fechamento da fundação documental

> Comunica, em alto nível, o que foi entregue na Onda 1 (fundação documental) do
> projeto earn-transcricao-reuniao e o que isso habilita. É um BRIEF de marco:
> registra o fechamento de uma fase, não substitui as peças que sintetiza.

---

## O marco

A fundação documental do projeto está montada. Em 2026-06-14, o repositório
nasceu sob o padrão SERMI em perfil solo, com as quatro peças fundacionais
escritas e publicadas, antes de qualquer linha do pipeline de transcrição. O
projeto deixou de ser um briefing em pasta plana mais um script simples e passou
a ter governança documental rastreável.

Repositório público: `github.com/serminaro/earn-transcricao-reuniao`.

---

## O que foi entregue

| Entrega | Conteúdo |
|---|---|
| SPEC-001 Taxonomia Documental | tipos SERMI, estrutura de pastas, frontmatter, numeração, privacidade do repo público, 10 regras checáveis R-TAX |
| REP-001 Síntese da Fundação | contexto, 11 decisões técnicas herdadas (D1-D11), 8 premissas (P1-P8), achados vs hipóteses, vieses, plano em ondas |
| DEC-001 Fundação reflexiva | decisão de adotar o perfil solo de 4 peças, 3 alternativas descartadas, consequências e gatilhos de reavaliação |
| SPEC-002 Descrição do Projeto | propósito, escopo, decomposição do pipeline, 9 critérios de sucesso C-01-09, cláusula Operação Solo, 8 regras checáveis R-FUN |
| Estrutura do repositório | `docs/` por tipo, `INDEX_DEC`, `INDEX_SPEC`, `README` vitrine, `.gitignore`, `environment.yml` mínimo |

O briefing original foi preservado como insumo histórico em
`docs/assets/shared/`. O áudio de reunião e as saídas do pipeline ficam fora do
Git por desenho.

---

## A decisão central do marco

O projeto adotou a **fundação SERMI de perfil solo**, de quatro peças, em vez das
cinco da fundação completa. A quinta peça (SPEC-003, Contrato de
Responsabilidade) seria vazia num projeto de uma pessoa só, então seu conteúdo
essencial virou a cláusula **Operação Solo** dentro da SPEC-002. Como não há
revisor externo, o freio contra viés é a auditoria recorrente das regras `R-*`,
com cadência por marco, mensal e por mudança de premissa.

A elegibilidade ao perfil solo foi confirmada: projeto autoral solo, sem
terceiros vinculados, baixo risco a outros. Se isso mudar (entra cliente, sócio
ou orientador), o projeto gradua para a fundação de cinco peças.

---

## Estado em números

| Indicador | Valor |
|---|---|
| Peças fundacionais | 4 de 4 (perfil solo) |
| Regras checáveis declaradas | 18 (10 R-TAX + 8 R-FUN) |
| Critérios de sucesso | 9 (C-01 a C-09, sendo 2 provisórios) |
| Decisões técnicas a formalizar | 11 (D1 a D11, Onda 2) |
| Status das peças | `proposto` (aguardando aprovação) |
| Auditoria gov-check | conforme, sem divergências |

---

## O que isto habilita (próximas ondas)

| Onda | Entrega | Estado |
|---|---|---|
| 2. Documentação técnica | DECs de stack (D1-D11) e SPECs de glossário, ambiente e schema de configuração | a fazer |
| 3. Código | os três scripts `01_transcrever`, `02_aplicar_mapeamento`, `03_gerar_ata` | a fazer |
| 4. Integração do orquestrador | `CLAUDE.md` na raiz (Claude Code neste Linux) | a fazer |

Pendência de qualidade que nenhuma onda documental resolve: validar o pipeline
ponta a ponta em reunião curta e confirmar as hipóteses técnicas (com destaque
para `large-v3` em int8 caber nos 6 GB de VRAM) antes de usar em reuniões reais.

---

## Histórico

| Data | Versão | Evento |
|---|---|---|
| 2026-06-14 | v1 | BRIEF-001 produzido em status `proposto`. Marca o fechamento da Onda 1 (fundação documental) do projeto earn-transcricao-reuniao: quatro peças fundacionais (SPEC-001, REP-001, DEC-001, SPEC-002) sob perfil solo da DEC-META-004, repositório público criado, auditoria gov-check conforme. Sintetiza as peças, não as substitui. |

---

*Fim do documento.*
