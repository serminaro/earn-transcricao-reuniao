---
documento: SPEC-001
titulo: Taxonomia Documental do Projeto earn-transcricao-reuniao
versao: v1
status: proposto
data: 2026-06-14
autor: Bruno Serminaro
supersede: —
referencia: REP-001, DEC-001, SPEC-002
---

# SPEC-001 · Taxonomia Documental do Projeto earn-transcricao-reuniao

> Define os tipos de documento produzidos neste projeto, suas funções, audiências, gatilhos de produção e regras de versionamento. Estabelece a taxonomia documental como peça de arquitetura do projeto, não como ornamento administrativo. É a primeira das peças de fundação previstas pela DEC-001, junto com REP-001 (Síntese da Fundação) e SPEC-002 (Descrição do Projeto). Toda a documentação produzida no escopo deste projeto observa esta taxonomia, e todo material precedente que não a observe é migrado para conformidade conforme oportunidade.

---

## 1. Propósito

### 1.1 Por que uma taxonomia documental

Este projeto é uma ferramenta operacional, não um produto. Mesmo assim, ele produz materiais que cumprem funções diferentes ao longo do tempo: descrever como o pipeline de transcrição está construído, justificar por que cada parâmetro do WhisperX foi fixado de um jeito e não de outro, ensinar a operar a adição de uma reunião nova, registrar o que aconteceu quando o pipeline rodou em condições reais. Essas funções competem entre si quando comprimidas em um único arquivo. O sintoma é o documento que tenta ser, ao mesmo tempo, manual de operação, justificativa técnica e diário de execução, e que por isso não serve bem a nenhum desses propósitos.

A taxonomia adotada aqui separa os tipos de documento por função, audiência e momento de produção, e trata essa separação como restrição de projeto. A motivação é prática: este é um projeto solo, e a memória do autor sobre por que uma decisão foi tomada se dilui em semanas. O custo de documentar uma decisão no momento em que ela é tomada é pequeno; o custo de reconstruí-la meses depois, sem registro, é alto.

### 1.2 Princípio operacional fundamental

Cada documento tem uma função primária e uma audiência primária. Quando um documento começa a descrever a arquitetura, justificar uma escolha e ensinar um procedimento ao mesmo tempo, a regra é interromper e separar. Documentos curtos e focados são preferíveis a documentos longos e genéricos. Este princípio governa todas as decisões taxonômicas que se seguem.

### 1.3 Origem desta taxonomia

Esta SPEC adota a taxonomia canônica SERMI (SPEC-SERMI-001 v3, governança documental do autor), com adaptações ao contexto deste projeto. A adoção é deliberada: o autor mantém uma taxonomia documental compartilhada entre projetos, de modo que a competência operacional construída em um projeto se transfere para o próximo. Divergências entre esta SPEC e o canon SERMI, quando existirem, são pontuais e registradas em DEC.

A particularidade central deste projeto é que ele é solo. Não há equipe, não há cliente externo, não há SLA. Audiências como "direção" ou "stakeholder" da taxonomia genérica correspondem aqui ao próprio autor em momento futuro, ou eventualmente a quem herde a ferramenta. Essa condição é registrada formalmente: a SPEC-002 deste projeto contém a cláusula de Operação Solo, e esta SPEC-001 a exige (ver R-TAX-10).

---

## 2. Os tipos SERMI aplicados a este projeto

A taxonomia SERMI compreende cinco tipos. Todos são aplicáveis aqui, com pesos diferentes dado o caráter solo e operacional do projeto.

| Sigla | Nome | Função primária | O que cobre neste projeto |
|---|---|---|---|
| **SPEC** | Especificação Estrutural | descrever o que algo é e como funciona | taxonomia documental, descrição do projeto, glossário de áudio e ASR, pipeline operacional, schema de configuração por reunião, ambiente técnico, privacidade e tratamento de dados |
| **REP** | Relatório | narrar o que aconteceu, com profundidade | síntese da fundação; futuras execuções relevantes do pipeline em reuniões reais; investigação de modos de falha (alucinação em silêncio, erro de diarização) |
| **DEC** | Registro de Decisão | documentar uma decisão, alternativas e consequências | adoção do WhisperX, escolha de modelo e compute_type, saídas JSON/TXT/SRT, mapeamento de falantes via YAML, LLM cloud para a ata, e cada decisão futura com trade-off explícito |
| **GUIDE** | Guia Operacional | descrever como operar algo, passo a passo | adicionar uma reunião nova ao pipeline; configurar HF_TOKEN no ambiente conda; refinar o mapeamento de falantes |
| **BRIEF** | Resumo / Vitrine | comunicar estado e valor em alto nível | o `README.md` na raiz, ponto de entrada do repositório público |

A divisão é exaustiva: qualquer documento legítimo do projeto cabe em um dos cinco tipos. Documentos que parecem caber em vários simultaneamente são segmentados antes de entrar no acervo.

### 2.1 SPEC

Documenta o que algo é e como funciona, no plano da descrição estrutural. Neste projeto, as SPECs descrevem o pipeline (decomposto em três scripts numerados), o schema de configuração por reunião, o ambiente conda, o tratamento de dados sensíveis. Toda SPEC é viva (ver §7): versionada explicitamente, com imutabilidade na granularidade da versão. O gatilho de produção é a primeira validação bem-sucedida do componente; para as SPECs de fundação, o gatilho é o início formal do projeto.

### 2.2 REP

Narra com profundidade o que aconteceu em uma fase, execução ou investigação. É o tipo mais denso. Produção episódica, nunca em ritmo regular. REP-001 é a Síntese da Fundação. REPs futuros são esperados quando o pipeline rodar pela primeira vez em condições reais (resultados quantitativos como RTF e qualitativos como erros de transcrição em termos técnicos) ou quando um modo de falha exigir investigação documentada.

### 2.3 DEC

Documenta uma decisão única, com alternativas, consequências aceitas e critérios de reavaliação. É o tipo mais importante para rastreabilidade. Opera sob atomicidade (uma decisão por DEC) e imutabilidade após aprovação (ver §7). O briefing técnico do projeto já consolida várias decisões aceitas (WhisperX, large-v3, int8, condition_on_previous_text=False, três saídas, mapeamento via YAML, LLM cloud para a ata); cada uma é candidata natural a uma DEC. DEC-001 é a Fundação reflexiva.

### 2.4 GUIDE

Descreve como operar algo, passo a passo, para transferir capacidade de execução. Produzido quando um procedimento é estável e tende a se repetir. O caso central aqui é "adicionar uma reunião nova": preparar o áudio, criar o YAML de configuração, rodar os três scripts na ordem, refinar o mapeamento de falantes. Procedimentos pontuais não justificam GUIDE.

### 2.5 BRIEF

Comunica estado e valor em alto nível, sem jargão. Neste projeto a forma relevante é o **BRIEF vitrine**: o `README.md` na raiz, que funciona como ponto de entrada do repositório público. As formas BRIEF de marco e BRIEF de período do canon SERMI são admissíveis, mas não há audiência que as demande hoje, dado o caráter solo.

---

## 3. Estrutura de pastas

Toda a documentação vive em `docs/`, com uma subpasta por tipo. A raiz do repositório contém também o código e os artefatos operacionais do pipeline.

```
earn-transcricao-reuniao/
├── README.md                         BRIEF vitrine (repositório público)
├── environment.yml                   ambiente conda
├── .gitignore
│
├── docs/
│   ├── SPEC/
│   │   ├── SPEC_001_Taxonomia_Documental.md
│   │   ├── SPEC_002_Descricao_do_Projeto.md
│   │   └── ...
│   ├── REP/
│   │   └── REP_001_Sintese_Fundacao.md
│   ├── DEC/
│   │   ├── INDEX_DEC.md
│   │   ├── DEC_001_Fundacao_reflexiva.md
│   │   └── ...
│   ├── GUIDE/
│   │   └── ...
│   ├── BRIEF/
│   │   └── ...
│   ├── assets/
│   │   ├── shared/
│   │   ├── SPEC/
│   │   ├── REP/
│   │   ├── GUIDE/
│   │   └── DEC/
│   └── logs/
│
├── src/
│   ├── 01_transcrever.py
│   ├── 02_aplicar_mapeamento.py
│   └── 03_gerar_ata.py
│
├── data/
│   └── configs/
│       ├── prompt_exemplo.txt
│       └── reuniao_template.yml
│
└── outputs/
    ├── transcricoes/
    └── atas/
```

Notas sobre a estrutura:

- `docs/DEC/` contém obrigatoriamente o `INDEX_DEC.md` (ver §8).
- `docs/assets/shared/` recebe ativos reaproveitados entre documentos; subpastas numéricas por documento (por exemplo `assets/SPEC/002/`) são criadas conforme demanda.
- `docs/logs/` arquiva logs de execuções relevantes do pipeline quando merecem ser preservados como evidência.
- Na raiz, `src/` guarda os três scripts numerados do pipeline, `data/configs/` guarda templates e configuração por reunião, `outputs/` guarda as transcrições e atas geradas.
- `environment.yml` define o ambiente conda; `README.md` é o BRIEF vitrine.

A separação entre `docs/` (versionado e público) e os artefatos operacionais sensíveis (áudios, outputs, segredos) é tratada na §9.

---

## 4. Frontmatter YAML obrigatório

Todo documento da taxonomia abre com um bloco YAML de metadados. O campo `categoria:` foi removido por DEC-META-003: não existe mais distinção entre "SPEC estrutural estável" e "SPEC viva", **toda SPEC é viva** e o campo `versao:` é o único mecanismo de evolução de SPEC.

```yaml
---
documento: <SIGLA-NNN ou SIGLA-AAAA-MM>
titulo: <Título do documento>
versao: <v1, v2, ...>
status: <proposto | aprovado | superseded | descartado>
data: <AAAA-MM-DD>
autor: <nome>
supersede: <SIGLA-NNN ou —>
referencia: <SIGLA-NNN ou —>
---
```

Campos, valores aceitos e obrigatoriedade:

| Campo | Valores aceitos | Obrigatório |
|---|---|---|
| `documento` | identificador no formato `SIGLA-NNN` (ou `SIGLA-AAAA-MM` para BRIEF de período) | sim |
| `titulo` | texto livre, descritivo | sim |
| `versao` | `v1`, `v2`, ... (incremento inteiro) | sim para SPEC, REP, GUIDE, DEC; opcional para BRIEF de período |
| `status` | `proposto`, `aprovado`, `superseded`, `descartado` | sim |
| `data` | `AAAA-MM-DD` | sim |
| `autor` | nome | sim |
| `supersede` | `SIGLA-NNN` quando substitui outro documento, ou `—` | sim (preenchido com `—` quando não aplicável) |
| `referencia` | um ou mais `SIGLA-NNN` separados por vírgula, ou `—` | sim (preenchido com `—` quando não aplicável) |

O frontmatter é parte da identidade do documento e é mantido atualizado em qualquer modificação. O valor `—` em `supersede` e `referencia` é literal e indica ausência de relação, não campo vazio.

---

## 5. Convenção de numeração e nomes de arquivo

Cada tipo tem padrão de nomenclatura próprio, observado obrigatoriamente:

| Tipo | Padrão de nome | Exemplo |
|---|---|---|
| SPEC | `SPEC_NNN_descricao_curta.md` | `SPEC_001_Taxonomia_Documental.md` |
| REP | `REP_NNN_descricao_curta.md` | `REP_001_Sintese_Fundacao.md` |
| GUIDE | `GUIDE_NNN_descricao_curta.md` | `GUIDE_001_Adicionar_Reuniao_Nova.md` |
| BRIEF de marco | `BRIEF_NNN_descricao_curta.md` | `BRIEF_001_Primeira_Execucao_Real.md` |
| BRIEF de período | `BRIEF_AAAA_MM.md` | `BRIEF_2026_06.md` |
| BRIEF vitrine | `README.md` | `README.md` |
| DEC | `DEC_NNN_descricao_curta.md` | `DEC_001_Fundacao_reflexiva.md` |

Regras:

- A descrição curta usa **snake_case ASCII**: minúsculas e maiúsculas separadas por underline, sem acentos, sem cedilha, sem espaços, sem hífen. `Adicionar_Reuniao_Nova`, não `Adicionar Reunião Nova` nem `adicionar-reuniao-nova`. A restrição a ASCII evita problemas de portabilidade entre sistemas de arquivos (o repositório é desenvolvido em ambiente Windows e versionado em Git).
- O número `NNN` é sequencial dentro de cada tipo e **nunca é reutilizado**. Documentos descartados ou substituídos mantêm seu número; o próximo documento do mesmo tipo recebe o número seguinte. Isso garante que referências cruzadas como "conforme DEC-002" permaneçam unívocas por toda a vida do projeto.
- Não há sufixo de versão no nome do arquivo. A versão vive no frontmatter (`versao:`) e no Histórico do documento, não no nome. Nomes como `SPEC_001_..._v2.md` violam a convenção.

---

## 6. Markdown canônico e derivados

Todos os documentos são escritos originariamente em Markdown. As justificativas:

- **Texto puro versionável.** O Git produz `diff` legível, e cada alteração é auditável linha a linha.
- **Independência de ferramenta.** Markdown é renderizado por inúmeras ferramentas, sem dependência de software proprietário.
- **Conversão sob demanda.** Quando um documento precisa ser distribuído em `.docx` ou `.pdf`, a conversão é feita a partir do Markdown na hora da distribuição. O `.docx` ou `.pdf` é tratado como derivado, não como fonte.

A consequência é que, no repositório, **a versão canônica e única de cada documento é o arquivo `.md`**. Derivados `.docx` ou `.pdf` não são versionados no Git. Dado o caráter solo e operacional deste projeto, a geração de derivados é rara: o caso plausível é distribuir uma ata específica em `.docx`, partindo sempre do Markdown gerado pelo pipeline.

---

## 7. Imutabilidade de DEC, SPEC viva versionável

A taxonomia opera com dois regimes distintos de imutabilidade, um para DEC e outro para SPEC.

**DEC aprovada é imutável.** Uma DEC com status `aprovado` não é editada. Decisões que mudam dão origem a uma nova DEC, que substitui (`supersede`) a anterior. A DEC anterior tem o status alterado para `superseded`, mas seu conteúdo permanece intacto e seu número nunca é reutilizado. A motivação é a rastreabilidade: o registro de por que o projeto foi como foi, em cada momento, precisa sobreviver às mudanças posteriores.

**SPEC é viva e versionável.** Toda SPEC evolui. A imutabilidade opera na granularidade da versão, não do documento:

- Cada versão (`v1`, `v2`, ...) é congelada quando aprovada. Edições retroativas sobre uma versão já aprovada são proibidas.
- Mudanças geram nova versão no mesmo arquivo. A versão anterior é registrada na seção Histórico ao final do documento.
- Enquanto a SPEC está em status `proposto`, pode ser editada livremente dentro da mesma versão; ajustes pré-aprovação são anotados no Histórico.
- Quando uma DEC modifica materialmente uma SPEC, a próxima versão da SPEC incorpora a mudança e cita a DEC, evitando que documento e estado real divirjam por longos períodos.

Esse modelo preserva a trilha auditável de cada estado aprovado sem exigir uma DEC supersedente para cada ajuste menor de uma SPEC de longa vida.

---

## 8. INDEX_DEC obrigatório

Para navegação no acervo, índices são mantidos nos tipos de maior volume. O nome carrega o tipo no sufixo (`INDEX_<TIPO>.md`).

- **`docs/DEC/INDEX_DEC.md`** é **obrigatório**. Lista todas as DECs com número, título, status e descrição curta. A obrigatoriedade decorre da função de rastreabilidade do tipo: sem índice, decisões importantes se perdem à medida que o número cresce. O INDEX_DEC inclui, no mínimo, a tabela de DECs ativas (`aprovado`), a de descartadas, a de superseded com ponteiro para a sucessora, e, quando houver, a relação SPEC × DEC supersedente.
- **`docs/SPEC/INDEX_SPEC.md`** é **recomendado** já no início do projeto, dado que as SPECs de fundação são produzidas de saída.
- Índices para GUIDE, REP e BRIEF são recomendados apenas quando o volume do tipo ultrapassa cerca de meia dúzia de documentos, situação improvável neste projeto a curto prazo.

Os índices são documentos versionados, mas não recebem numeração de tipo (não são SPECs nem DECs).

---

## 9. Privacidade

O repositório é **público**. Isso impõe uma fronteira rígida entre o que é versionado e o que nunca pode entrar no Git.

O conteúdo das reuniões é potencialmente sensível, e o pipeline lida com três classes de material que **ficam fora do repositório** via `.gitignore`:

| Classe | Onde fica | Por que fora do Git |
|---|---|---|
| Áudio de reunião | `data/audios_pendentes/`, `data/audios_processados/` | conteúdo bruto sensível, peso alto |
| Outputs do pipeline | `outputs/transcricoes/`, `outputs/atas/` | transcrições e atas contêm o teor das reuniões |
| Segredos | qualquer `.env` | não há segredo versionado |

O `.gitignore` deve cobrir explicitamente essas pastas e padrões. Apenas a estrutura é versionada (via `.gitkeep` nas pastas que precisam existir vazias), nunca o conteúdo.

O `HF_TOKEN` (token Hugging Face, necessário para baixar os modelos pyannote da diarização) **não** vive em arquivo nenhum do repositório. Ele é lido de variável de ambiente do ambiente conda, configurada uma vez:

```bash
conda env config vars set HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
conda deactivate
conda activate <nome_do_env>
```

O código valida a presença da variável com try/except e falha cedo com mensagem útil se ela estiver ausente. Não há `.env`, não há dependência extra para gerenciar segredos. A documentação em `docs/` (SPEC, DEC, GUIDE, REP) descreve o pipeline sem reproduzir conteúdo de reuniões reais; exemplos usam dados fictícios.

---

## 10. Conventional Commits

Documentos versionados no Git observam a convenção de Conventional Commits, com tipo `docs` e escopo correspondente ao tipo do documento:

| Operação | Padrão de mensagem | Exemplo |
|---|---|---|
| Adicionar nova SPEC | `docs(spec): adiciona SPEC-NNN ...` | `docs(spec): adiciona SPEC-001 taxonomia documental` |
| Atualizar SPEC viva | `docs(spec): SPEC-NNN vX → vY (motivo)` | `docs(spec): SPEC-001 v1 → v2 (ajuste de regras)` |
| Adicionar novo REP | `docs(rep): adiciona REP-NNN ...` | `docs(rep): adiciona REP-001 sintese da fundacao` |
| Adicionar novo DEC | `docs(dec): adiciona DEC-NNN ...` | `docs(dec): adiciona DEC-001 fundacao reflexiva` |
| Atualizar GUIDE | `docs(guide): atualiza GUIDE-NNN ...` | `docs(guide): atualiza GUIDE-001 com passo de validacao` |
| Substituir documento | `docs(SIGLA): supersede SIGLA-XXX por SIGLA-YYY` | `docs(dec): supersede DEC-002 por DEC-005` |
| Adicionar imagem | `docs(assets): adiciona <descrição> em <local>` | `docs(assets): adiciona diagrama do pipeline em SPEC/003` |

Commits de código seguem a mesma convenção com escopos próprios (`feat`, `fix`, `chore` etc.), fora do escopo desta SPEC, que governa apenas a documentação.

---

## 11. Regras checáveis

Esta seção declara as regras concretas que o skill genérico de auditoria de consistência verifica contra o estado real do projeto. Cada regra tem identificador `R-TAX-NN`, enunciado, onde verificar e severidade orientativa: divergências `Crítica` exigem decisão imediata; `Alta` exigem decisão na sessão de auditoria; `Média` e `Baixa` podem ser registradas como dívida e endereçadas em ciclo subsequente.

O skill é genérico: lê esta SPEC-001, descobre as regras `R-TAX-NN` declaradas e aplica cada uma. A cada divergência, apresenta o achado e oferece dois caminhos, (a) atualizar esta SPEC para refletir a realidade observada, ou (b) corrigir o pedaço do projeto que diverge. O skill nunca corrige sozinho; a escolha é do autor e o resultado é registrado.

**Nota de escopo deste projeto.** Este é um projeto solo cuja fundação documental tem quatro peças: SPEC-001 (esta), REP-001 (Síntese da Fundação), DEC-001 (Fundação reflexiva) e SPEC-002 (Descrição do Projeto). **Não existe SPEC-003** (Contrato de Responsabilidade), porque não há divisão de papéis a contratualizar: o autor responde por tudo. A condição de operação solo é registrada como cláusula explícita na SPEC-002, e a regra R-TAX-10 exige tanto a presença e referência mútua das quatro peças quanto a presença dessa cláusula.

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-TAX-01** | Todo arquivo `.md` em `docs/<TIPO>/` (exceto `INDEX_<TIPO>.md`) tem frontmatter YAML preenchido com os campos obrigatórios da §4: `documento`, `titulo`, `versao`, `status`, `data`, `autor`, `supersede`, `referencia`. Frontmatter ausente ou campo obrigatório vazio sinaliza divergência. O campo `categoria:` não deve existir (removido por DEC-META-003); sua presença sinaliza divergência. | Parse do frontmatter de cada arquivo | Alta |
| **R-TAX-02** | Nome de arquivo obedece o padrão da §5 por tipo: `SPEC_NNN_*.md`, `REP_NNN_*.md`, `GUIDE_NNN_*.md`, `BRIEF_NNN_*.md` (marco), `BRIEF_AAAA_MM.md` (período), `DEC_NNN_*.md`, com descrição em snake_case ASCII (sem acentos, sem hífen, sem espaços). Sufixo de versão incrustado no nome (`_v1`, `_v2`) ou caracteres não-ASCII sinalizam divergência. | Listagem de `docs/<TIPO>/` confrontada com regex do padrão | Alta |
| **R-TAX-03** | Numeração sequencial dentro de cada tipo, sem reuso (§5). Lacunas só são legítimas se houver documento com status `superseded` ou `descartado` ocupando o número. Número repetido, ou número faltante sem registro de descarte/supersedição, sinaliza violação grave. | Cruzamento entre nome do arquivo, campo `documento:` do frontmatter e status | Crítica |
| **R-TAX-04** | Valor do campo `status` pertence ao conjunto fixado na §4: `proposto`, `aprovado`, `superseded`, `descartado`. Variações de grafia (`proposta`, `aprovada`, `em revisão`) sinalizam divergência. | Parse do campo `status` | Média |
| **R-TAX-05** | Reciprocidade de supersede: documento com `status: superseded` é apontado pelo campo `supersede:` de ao menos um documento ativo do mesmo tipo; inversamente, todo `supersede:` aponta para documento existente e com status coerente. Quebras de reciprocidade sinalizam divergência de rastreabilidade. | Inspeção dos campos `supersede:` em toda a documentação | Alta |
| **R-TAX-06** | `docs/DEC/INDEX_DEC.md` existe (obrigatório, §8) e lista todas as DECs presentes em `docs/DEC/`. DEC ausente do INDEX, ou entrada de DEC inexistente, sinaliza divergência. | Cruzamento entre arquivos físicos e entradas do INDEX | Média |
| **R-TAX-07** | Estrutura de pastas conforme §3: existem `docs/SPEC/`, `docs/REP/`, `docs/DEC/`, `docs/GUIDE/`, `docs/BRIEF/`, `docs/assets/`. Pastas adicionais dentro de `docs/` não previstas sinalizam divergência estrutural a registrar, regularizar ou justificar em DEC. | Listagem de `docs/` | Baixa |
| **R-TAX-08** | Toda DEC com status `aprovado` contém as cinco seções obrigatórias da estrutura SERMI: Contexto, Decisão, Alternativas consideradas (pelo menos duas, com justificativa de descarte), Consequências (com seção explícita de consequências negativas), Critérios de reavaliação. Ausência de qualquer uma sinaliza DEC incompleta. | Parse estrutural do markdown de cada DEC aprovada | Alta |
| **R-TAX-09** | Privacidade: o repositório não versiona áudio de reunião, outputs do pipeline (`outputs/transcricoes/`, `outputs/atas/`) nem arquivos `.env`; o `.gitignore` cobre essas pastas e padrões; nenhum `HF_TOKEN` ou segredo aparece em arquivo versionado (§9). Qualquer arquivo sensível rastreado pelo Git sinaliza violação grave. | Inspeção do `.gitignore` e varredura dos arquivos versionados por conteúdo sensível | Crítica |
| **R-TAX-10** | As quatro peças fundacionais existem e se referenciam mutuamente: SPEC-001 (esta), REP-001 (Síntese da Fundação), DEC-001 (Fundação reflexiva) e SPEC-002 (Descrição do Projeto). Não se exige SPEC-003. Além disso, a SPEC-002 contém a cláusula explícita de **Operação Solo**. Ausência de qualquer das quatro peças, ausência de referência cruzada entre elas, ou ausência da cláusula de Operação Solo na SPEC-002 sinaliza divergência fundacional. | Listagem de `docs/SPEC/`, `docs/REP/` e `docs/DEC/` cruzada com inspeção de `referencia:` no frontmatter, e parse da SPEC-002 atrás da cláusula | Crítica |

As regras acima são v1 e devem ser calibradas conforme o skill for utilizado e novas inconsistências aparecerem.

---

## 12. Critérios de revisão

Esta SPEC-001 deve ser revisitada quando:

- Aparecer documento legítimo do projeto que não caiba em nenhum dos cinco tipos SERMI. O caso é registrado em DEC antes da revisão da SPEC.
- A taxonomia canônica SERMI (SPEC-SERMI-001) evoluir de forma que afete convenções aqui adotadas (frontmatter, nomenclatura, regras checáveis).
- O conjunto de regras `R-TAX-NN` se mostrar insuficiente ou mal calibrado durante o uso do skill de auditoria, gerando falsos positivos ou deixando passar divergências reais.
- A condição de operação solo mudar (entrada de colaborador, herança da ferramenta), o que pode exigir reintroduzir um Contrato de Responsabilidade e ajustar R-TAX-10.

---

## 13. Histórico

| Data | Versão | Evento |
|---|---|---|
| 2026-06-14 | v1 | SPEC-001 produzida em status `proposto`. Primeira SPEC fundacional do projeto earn-transcricao-reuniao. Adota a taxonomia canônica SERMI (SPEC-SERMI-001 v3) adaptada ao contexto deste projeto: pipeline local solo de transcrição de reuniões PT-BR. Adaptações principais em relação ao canon: fundação de quatro peças (SPEC-001, REP-001, DEC-001, SPEC-002) sem SPEC-003, dado o caráter solo registrado na cláusula de Operação Solo da SPEC-002; regra R-TAX-09 específica de privacidade (repositório público, áudio/outputs/.env fora do Git, HF_TOKEN só em variável de ambiente conda); R-TAX-10 adaptada à fundação de quatro peças e à exigência da cláusula de Operação Solo. Declara dez regras checáveis R-TAX-01 a R-TAX-10. Aguarda revisão e aprovação. |

---

*Fim do documento.*
