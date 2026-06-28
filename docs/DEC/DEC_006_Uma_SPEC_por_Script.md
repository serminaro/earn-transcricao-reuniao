---
documento: DEC-006
titulo: Uma SPEC-contrato por script do pipeline (mapa SPEC ↔ script)
versao: v1
status: proposto
data: 2026-06-16
autor: Bruno Serminaro
supersede: —
referencia: SPEC-002, SPEC-006, GUIDE-001, SPEC-004
---

# DEC-006 · Uma SPEC-contrato por script do pipeline

> Decisão atômica que fixa o mapa SPEC ↔ script deixado em aberto pelo GUIDE-001
> §7: cada um dos três scripts do pipeline tem a sua própria SPEC-contrato, em vez
> de uma SPEC única de pipeline. As SPECs de módulo são numeradas SPEC-009
> (`01_transcrever`), SPEC-010 (`02_aplicar_mapeamento`) e SPEC-011
> (`03_gerar_ata`), e todas referenciam o contrato de dados da SPEC-006.

---

## 1. Contexto

O método spec-driven exige que cada script nasça de uma SPEC que o dirija (DEC-002,
GUIDE-001 §2, SPEC-004 R-FLOW-01). O GUIDE-001 §7 deixou explicitamente para a Onda
2 a decisão de **qual SPEC dirige qual script**: "o mapa exato de qual SPEC dirige
qual script é fixado na Onda 2". Antes de escrever a primeira SPEC de módulo, é
preciso fixar esse mapa, sob pena de as SPECs nascerem com granularidade
inconsistente.

A SPEC-002 §4 já decompõe o pipeline em três scripts numerados, cada um com modo de
falha e ciclo de iteração próprios: o 01 transcreve (caro, roda uma vez), o 02
mapeia falantes (roda várias vezes até ficar certo), o 03 gera a ata (sob demanda,
chama LLM em nuvem). O contrato de dados comum que os três compartilham já está
fixado na SPEC-006 (o schema do JSON fonte de verdade). Falta decidir se o contrato
de comportamento de cada script vive numa SPEC própria ou numa SPEC única.

---

## 2. Decisão

**Cada script do pipeline tem a sua própria SPEC-contrato. Serão três SPECs de
módulo, numeradas na ordem dos scripts: SPEC-009 para `01_transcrever`, SPEC-010
para `02_aplicar_mapeamento` e SPEC-011 para `03_gerar_ata`. Cada uma declara o
contrato do seu script (entradas, saídas, parâmetros, invariantes, modos de falha) e
referencia o contrato de dados da SPEC-006 em vez de redescrever a forma do JSON.**

A decisão inclui:

- alinhar a granularidade da SPEC à granularidade do script: como cada script é
  iterável de forma independente (SPEC-002 §4), sua SPEC também é versionável de
  forma independente;
- numerar as SPECs de módulo a partir de 009, deixando 007 e 008 para as demais
  SPECs técnicas da Onda 2 (o glossário do domínio e o schema do YAML de
  configuração da reunião), conforme o plano da Onda 2;
- cada SPEC de módulo refletir, no campo `referencia:`, a SPEC-006 (contrato de
  dados) e a SPEC-002 (critérios `C-NN` que o script cumpre);
- manter a SPEC-002 como descrição do projeto, não como contrato de implementação
  dos scripts: ela diz o que o pipeline entrega, as SPECs de módulo dizem como cada
  script o entrega.

---

## 3. Origem / rastro

| Artefato | Como sustenta esta decisão |
|---|---|
| **GUIDE-001 §7** | Deixou o mapa SPEC ↔ script para a Onda 2; esta DEC o fixa. |
| **SPEC-002 §4** | Já decompõe o pipeline em três scripts com modos de falha e ciclos próprios; a granularidade da SPEC segue a do script. |
| **SPEC-006** | Contrato de dados comum que as três SPECs de módulo referenciam, evitando três descrições concorrentes do JSON. |
| **SPEC-004 R-FLOW-01** | Exige que todo `src/*.py` tenha uma SPEC que o dirija; esta DEC define quantas e quais. |

---

## 4. Alternativas consideradas

### 4.1 Uma SPEC única de pipeline para os três scripts

Uma só SPEC técnica descrevendo o contrato dos três scripts juntos.

**Descartada porque:**
- Reacopla o que a SPEC-002 §4 separou de propósito. Os três scripts têm modos de
  falha e ciclos de iteração distintos; uma SPEC única forçaria versionar tudo junto
  a cada ajuste de um só script.
- Reproduz o anti-padrão que a SPEC-001 §1.2 combate: um documento que tenta
  descrever três comportamentos ao mesmo tempo serve mal a cada um.
- Dificulta a rastreabilidade fina entre uma issue `tipo:code` e a SPEC que a dirige
  (SPEC-004 §5.1), porque a issue apontaria sempre para a mesma SPEC monolítica.

### 4.2 Sem SPEC de módulo, reusando a SPEC-002 como contrato dos scripts

Tratar a SPEC-002 (Descrição do Projeto) como o contrato que dirige os scripts, sem
SPECs de módulo dedicadas.

**Descartada porque:**
- Confunde dois papéis: a SPEC-002 é régua de escopo e critérios de sucesso do
  projeto, não contrato de implementação com schema, parâmetros e modos de falha por
  script (GUIDE-001 §4).
- Sobrecarregaria a SPEC-002, que é peça de fundação, com detalhe técnico volátil;
  cada ajuste de um script forçaria versionar uma peça fundacional.
- Deixaria R-FLOW-01 sem referente concreto: "a SPEC que dirige o script" seria
  genérica demais para conferir o código contra ela.

---

## 5. Consequências

### 5.1 Consequências positivas

- **Granularidade coerente.** SPEC e script versionam juntos e no mesmo ritmo; ajuste
  num script toca só a sua SPEC.
- **Rastreabilidade fina.** Cada issue `tipo:code` aponta para a SPEC exata que a
  dirige (SPEC-004 §5.1), e R-FLOW-01 ganha referente concreto por script.
- **Contrato de dados reusado, não repetido.** As três SPECs referenciam a SPEC-006
  em vez de redescrever o JSON, evitando descrições concorrentes que divergem.
- **Foco por documento.** Cada SPEC descreve um comportamento, como manda a SPEC-001
  §1.2.

### 5.2 Consequências negativas / custo aceito

- **Três SPECs a manter em vez de uma.** Mais arquivos, mais frontmatter, mais
  entradas no INDEX_SPEC. Aceito: o custo é baixo e o ganho de foco e rastreabilidade
  paga.
- **Risco de repetição entre as SPECs.** Trechos comuns (validação do JSON, fronteira
  de privacidade) podem se repetir nas três. Mitigado referenciando a SPEC-006 e a
  SPEC-002 em vez de copiar.
- **Coordenação de versões.** Uma mudança no contrato de dados (SPEC-006) pode exigir
  tocar as três SPECs de módulo. Aceito: é a contrapartida de ter um contrato comum
  explícito.

### 5.3 O que esta decisão NÃO resolve

- **Não escreve as SPECs de módulo** nem fixa o conteúdo de cada contrato: define
  apenas que são três e como se numeram.
- **Não decide a stack** de cada script (WhisperX, modelo, LLM da ata): seguem como
  DECs próprias da Onda 2.
- **Não define a verificação da ata** (DoD do script 03) nem o gatilho de aprovação
  dos documentos: ficam para decisão posterior.

---

## 6. Critérios de reavaliação

| Gatilho | O que reavaliar |
|---|---|
| O pipeline ganhar ou perder um script (mudança na decomposição da SPEC-002 §4) | O número de SPECs de módulo acompanha; reavaliar o mapa. |
| Duas SPECs de módulo passarem a versionar sempre juntas, sinal de acoplamento real | Reavaliar se aquele par deve fundir-se numa SPEC só. |
| A repetição entre as SPECs de módulo virar fonte de divergência | Extrair o trecho comum para uma SPEC referenciada, ou para a SPEC-006. |

---

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-06-16 | DEC-006 v1 produzida em status `proposto`. Fixa o mapa SPEC ↔ script deixado em aberto pelo GUIDE-001 §7: uma SPEC-contrato por script (SPEC-009 para `01_transcrever`, SPEC-010 para `02_aplicar_mapeamento`, SPEC-011 para `03_gerar_ata`), cada uma referenciando o contrato de dados da SPEC-006. Os números 007 e 008 ficam para o glossário e o schema do YAML de configuração (plano da Onda 2). Descarta a SPEC única de pipeline e o reuso da SPEC-002 como contrato. Sexta DEC do projeto. |

---

*Fim do documento.*
