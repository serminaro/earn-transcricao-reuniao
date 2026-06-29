---
documento: SPEC-008
titulo: Inventário da reunião (contrato de configuração de entrada do pipeline)
versao: v1
status: proposto
data: 2026-06-28
autor: Bruno Serminaro
supersede: —
referencia: SPEC-009, SPEC-006, SPEC-002, DEC-005, DEC-006, DEC-007, SPEC-001
---

# SPEC-008 · Inventário da reunião (contrato de configuração de entrada)

> Fixa o **inventário** por reunião: um YAML que é a fonte única de configuração que
> o pipeline lê. O `01_transcrever` é chamado apenas com o caminho do inventário; ele
> declara o áudio (por nome), o idioma, o vocabulário ancorado e os participantes, e
> reserva o `speaker_mapping` que o passo 02 preenche **após** a transcrição. Numerada
> 008 pelo mapa da DEC-006 (007 glossário, 008 schema do YAML de configuração). Carrega
> o artefato executável `data/schema/reuniao.schema.json` (JSON Schema 2020-12), para
> que a conformidade do inventário seja medida, não descrita — mesmo padrão da SPEC-006.

---

## 1. Propósito

### 1.1 Por que um inventário por reunião

Cada reunião precisa de um punhado de informações para ser transcrita bem: o idioma, os
nomes e o jargão (que ancoram o ASR, DEC-007), e — depois — quem é cada falante. Sem um
lugar fixo para isso, esses dados ficam soltos na linha de comando ou na cabeça do autor,
e a reunião deixa de ser reproduzível. O inventário é esse lugar: **um arquivo por
reunião** que descreve o trabalho de ponta a ponta, de modo que rodar o pipeline seja
apontar para o inventário, não relembrar parâmetros.

### 1.2 O que esta SPEC fixa e o que delega

| Esta SPEC fixa | Esta SPEC delega |
|---|---|
| Os campos do inventário, seus tipos e o que é obrigatório. | A **forma do JSON de saída**: SPEC-006. |
| As convenções de caminho (`data/audios/`, `data/configs/`, saída por convenção). | O **comportamento** do `01_transcrever`: SPEC-009. |
| Os invariantes do inventário e os modos de falha de validação. | O **mapeamento de falantes em si** (como o 02 aplica): SPEC-010 (futura). |
| As regras checáveis `R-INV-NN`. | O **glossário** de termos do domínio: SPEC-007 (reservada). |

---

## 2. Posição no fluxo

O inventário é preenchido em dois momentos, e essa separação é a decisão central desta SPEC:

```
ANTES do 01 (você sabe):           audio, language, vocabulario, participantes
        │
        ▼
[01_transcrever <inventario>]   transcreve; a diarização ATRIBUI os rótulos SPEAKER_xx
        │
        ▼
DEPOIS do 01 (você vê e preenche): speaker_mapping (SPEAKER_xx → nome real)
        │
        ▼
[02_aplicar_mapeamento]   lê o speaker_mapping e preenche o campo `speaker` no JSON
```

**Por que o `speaker_mapping` não se pré-declara.** Os rótulos `SPEAKER_00/01/...` são
atribuídos **pela diarização durante o 01**, são arbitrários (o `SPEAKER_00` de uma rodada
pode ser outra pessoa noutra) e podem surpreender na contagem (uma entrevista de 2 pessoas
pode produzir um `SPEAKER_02` de uma voz de fundo). Logo, mapear falante a nome **antes** de
transcrever estaria adivinhando. O `speaker_mapping` é input do passo 02 e é preenchido
depois de o 01 revelar os rótulos (DEC-005).

---

## 3. Campos do inventário

| Campo | Tipo | Obrigatório? | Preenchido | Significado |
|---|---|---|---|---|
| `audio` | string (só o nome do arquivo) | **sim** | antes | Áudio a transcrever, resolvido em `data/audios/`. Sem caminho (§4). |
| `language` | string (código ISO, ex.: `pt`) | não — default `pt` | antes | Idioma do ASR (SPEC-009). |
| `vocabulario` | lista de strings | não | antes | Nomes próprios e jargão; o 01 monta o `initial_prompt` a partir dela (DEC-007). |
| `initial_prompt` | string | não | antes | Prompt explícito; se presente, prevalece sobre `vocabulario`. |
| `participantes` | lista de strings | não | antes | Quem se espera na reunião; referência que ajuda a montar o `speaker_mapping`. |
| `speaker_mapping` | objeto `SPEAKER_NN: nome` | não | **depois do 01** | Mapa de falante para nome real; input do passo 02 (DEC-005). |

O inventário admite **campos adicionais** (`additionalProperties: true`): os passos 02 e 03
podem acrescentar campos próprios (ex.: parâmetros da ata) sem quebrar a validação do 01.

---

## 4. Convenções de caminho e nomenclatura

Decisões de organização, deliberadamente enxutas para operação solo:

- **Uma pasta de áudio:** `data/audios/` (gitignored). Não há `pendentes/processados` — é
  fila, que só paga em volume. **"Processado" deriva da saída:** um áudio é considerado
  transcrito quando existe `outputs/transcricoes/{nome}.txt` correspondente. O estado vive
  na saída, não na pasta (não duplicar estado).
- **Inventários:** `data/configs/<nome>.yml`, com `data/configs/reuniao.template.yml` como
  modelo auto-explicativo (cada campo com exemplo e comentário).
- **Saída:** `outputs/transcricoes/`, com nome **derivado do áudio** (`{nome}.json/.txt/.srt`).
  É convenção, não campo do inventário — é igual para toda reunião, então não se repete.
- **`audio` por nome, não por caminho:** o inventário guarda o nome do arquivo; o 01 o
  resolve em `data/audios/`. Caminho absoluto no inventário é divergência (R-INV-02): acopla
  a config ao layout de uma máquina (o anti-padrão que a REP-001 §1 já apontou).

---

## 5. Invariantes do contrato

| ID | Invariante |
|---|---|
| INV-1 | **Inventário conforme.** Valida contra `data/schema/reuniao.schema.json`; `audio` presente. |
| INV-2 | **Áudio resolvível.** O `audio` referenciado existe em `data/audios/` quando o 01 roda. |
| INV-3 | **Sem caminho absoluto.** Nenhum campo carrega caminho de filesystem; só nomes. |
| INV-4 | **`speaker_mapping` é pós-01.** Quando presente, suas chaves são rótulos que o 01 produziu; nunca é pré-condição da transcrição. |
| INV-5 | **Saída não é configurada.** A pasta/nome de saída deriva da convenção e do nome do áudio, não de um campo. |

---

## 6. Modos de falha e validação

| Situação | Comportamento esperado |
|---|---|
| Inventário não valida contra `reuniao.schema.json` (campo faltando, tipo errado) | **Falhar cedo**, com mensagem apontando o caminho do campo inválido. Não inicia a transcrição. |
| `audio` ausente em `data/audios/` | Falhar cedo, citando o nome procurado e a pasta. |
| `language` ausente | Não é erro: assume o default `pt`. |
| `speaker_mapping` ausente após o 01 | Não é erro para o 01 (é input do 02). O 02 é que exige (SPEC-006 §6). |

A validação do inventário usa a mesma mecânica da SPEC-006 (carrega o YAML, valida o
dicionário resultante com `jsonschema`).

---

## 7. Artefato executável e evolução

O contrato autoritativo e checável é `data/schema/reuniao.schema.json` (JSON Schema Draft
2020-12). As tabelas desta SPEC descrevem o mesmo contrato em prosa; havendo divergência,
prevalece o artefato (e a divergência se corrige como erro, não se interpreta).

O schema é **permissivo em campos extras** (`additionalProperties: true`), de propósito: o
inventário cresce conforme os passos 02 e 03 ganharem SPEC, sem quebrar a validação do 01.
Mudança incompatível (renomear/remover campo, tornar obrigatório o que era opcional) exige
nova versão desta SPEC e do artefato no mesmo passo.

---

## 8. Relação com a SPEC-009 (mudança de contrato do 01)

Esta SPEC **altera a entrada do `01_transcrever`**. A SPEC-009 §3.1 declarava a entrada como
"áudio + YAML de configuração", com o áudio passado na linha de comando. Com o inventário, o
01 passa a ser chamado **apenas com o caminho do inventário**, que referencia o áudio por nome.

Consequência: a SPEC-009 §3.1 e o CLI do `01` devem ser revisados para refletir
`01_transcrever <inventario>` (revisão registrada no Histórico da SPEC-009 quando feita). Esta
SPEC-008 é o contrato de entrada; a SPEC-009 descreve o comportamento que o consome.

---

## 9. Regras checáveis

Declara regras `R-INV-NN`. **Ressalva de escopo de auditoria** (idêntica à SPEC-004 §8,
SPEC-005 §8, SPEC-006 §8, SPEC-009 §8): o `gov-check` lê regras `R-*` só das SPECs de
**fundação** (001/002). As `R-INV` abaixo não são lidas automaticamente; são verificadas por
**teste determinístico** (parte do DoD do 01), na **auditoria recorrente** (SPEC-002 §6), ou
migradas para as `R-FUN-*` quando estabilizarem.

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-INV-01** | Todo inventário valida contra `data/schema/reuniao.schema.json`; o campo `audio` é obrigatório (INV-1). | Validação programática do YAML contra o artefato | Alta |
| **R-INV-02** | Nenhum campo do inventário carrega caminho absoluto; `audio` é só o nome, resolvido em `data/audios/` (INV-3). | Inspeção dos inventários | Média |
| **R-INV-03** | `speaker_mapping`, quando presente, contém rótulos `SPEAKER_NN` produzidos pelo 01; não é pré-condição da transcrição (INV-4, DEC-005). | Inspeção cruzada inventário × saída do 01 | Média |
| **R-INV-04** | A pasta/nome de saída deriva da convenção e do nome do áudio, não de um campo do inventário (INV-5). | Inspeção do schema e do 01 | Baixa |
| **R-INV-05** | `data/audios/` é gitignored; nenhum áudio é versionado (reforça R-TAX-09/R-FUN-03 sob a nova estrutura de pasta única). | `.gitignore` e arquivos rastreados | Crítica |

As regras são v1 e devem ser calibradas conforme o inventário e os scripts evoluírem.

---

## 10. Critérios de revisão

Esta SPEC-008 é viva e versionável (SPEC-001 §7). Revisar quando:

- a primeira implementação do CLI do 01 com inventário revelar campos faltando ou demais;
- os passos 02 (SPEC-010) ou 03 (SPEC-011) precisarem de campos próprios no inventário,
  formalizando o que hoje é só `additionalProperties: true`;
- um helper de geração do inventário (`gerar_inventario`) for criado e impuser estrutura;
- a convenção de pasta única `data/audios/` se mostrar insuficiente (volume maior);
- as regras `R-INV` estabilizarem a ponto de migrarem para as `R-FUN-*` da SPEC-002.

---

## 11. Histórico

| Data | Versão | Evento |
|---|---|---|
| 2026-06-28 | v1 | SPEC-008 produzida em status `proposto`, ocupando o slot reservado pela DEC-006 (schema do YAML de configuração). Fixa o inventário por reunião: `audio` (por nome, em `data/audios/`), `language` (default `pt`), `vocabulario`/`initial_prompt`, `participantes` (pré-01) e `speaker_mapping` (pós-01, input do passo 02). Separa os campos "sei antes" dos "preencho depois" e justifica por que o falante não se pré-declara (diarização atribui os rótulos em runtime). Fixa as convenções de caminho (pasta única `data/audios/`, "processado = tem txt", saída por convenção). Carrega o artefato executável `data/schema/reuniao.schema.json` (permissivo em campos extras). Declara que a entrada do 01 passa a ser só o inventário, disparando revisão da SPEC-009. Cinco regras R-INV-01 a R-INV-05. Aguarda revisão e aprovação. |

---

*Fim do documento.*
