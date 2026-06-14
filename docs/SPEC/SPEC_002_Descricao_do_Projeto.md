---
documento: SPEC-002
titulo: Descrição do Projeto earn-transcricao-reuniao
versao: v1
status: proposto
data: 2026-06-14
autor: Bruno Serminaro
supersede: —
referencia: SPEC-001, REP-001, DEC-001
---

# SPEC-002 · Descrição do Projeto earn-transcricao-reuniao

> Declara o que o projeto earn-transcricao-reuniao se compromete a entregar: propósito, escopo, decomposição do pipeline, critérios de sucesso auditáveis e não-objetivos. É a peça contra a qual se afere se o projeto entregou o que prometeu, e é a quarta das quatro peças de fundação deste projeto (SPEC-001, REP-001, DEC-001, SPEC-002), conforme DEC-001 e a taxonomia da SPEC-001. Como o projeto opera em perfil solo (DEC-META-004), não há SPEC-003 (Contrato de Responsabilidade): a atribuição de papéis vive na cláusula "Operação Solo" da §6 desta SPEC. A reflexão consolidada que justifica esta descrição vive em REP-001; esta SPEC fixa a forma estável que serve de régua.

---

## 1. Propósito e o que é o projeto

O earn-transcricao-reuniao é um pipeline de software local para transcrever reuniões em português brasileiro, com identificação de quem falou (diarização) e geração eventual de ata estruturada. Roda na máquina do autor, nesta estação Linux (Ubuntu/Debian, descrita e governada em `~/Projetos/learn-manutencao-linux`) com GPU NVIDIA dedicada, combinando WhisperX (ASR Whisper, alinhamento word-level e diarização via pyannote.audio) com uma chamada a LLM em nuvem (Anthropic) apenas para a etapa de ata.

O projeto é uma ferramenta operacional pessoal e profissional. Não é SaaS, não é produto público, não é serviço com SLA. A entrada são arquivos de áudio de reuniões reais do autor (2 a 4 participantes típico, até 8 ocasional, 30 a 90 minutos, até cinco reuniões por semana); a saída são transcrições legíveis com falantes nomeados e, quando solicitada, uma ata em Markdown. O ganho prático é deixar de depender de memória ou de anotação manual durante a reunião, preservando o teor sem enviar o áudio bruto para serviços de transcrição de terceiros.

O aprendizado técnico é subobjetivo declarado, não objetivo principal. O projeto serve para o autor consolidar competência em ASR, diarização e operação de modelos locais com GPU; esse ganho é bem-vindo, mas a régua de sucesso é a utilidade operacional (§5), não o aprendizado em si.

---

## 2. Papéis (régua abstrata)

Esta SPEC é régua para os papéis abaixo. Os papéis são descritos de forma abstrata; a atribuição de pessoa física a cada um vive na cláusula "Operação Solo" da §6, que neste projeto concentra todos eles em uma única pessoa.

| Papel | Função frente a esta SPEC |
|---|---|
| **Autor** | Produz a SPEC, mantém-na em dia, escreve e opera o pipeline conforme o que ela declara. |
| **Revisão técnica (Peer)** | Revisa os artefatos do projeto (scripts, configs, saídas) frente ao que esta SPEC declara. |
| **Validação (Supervisor)** | Valida o conjunto da produção frente aos critérios de sucesso da §5. |
| **Gestor** | Lê esta SPEC para alinhar escopo e prioridade do que será construído e quando. |
| **Diretor** | Lê esta SPEC para decidir sobre continuidade, descontinuação ou redirecionamento do projeto. |

A separação entre Autor, Revisão técnica e Validação é deliberada: cobre três níveis distintos de controle de qualidade. Em um projeto com equipe, esses papéis seriam pessoas diferentes. Aqui, pela natureza solo do projeto, todos recaem sobre o autor, e a compensação contra a ausência de freio externo é tratada na §6.

---

## 3. Escopo

### 3.1 O que o projeto entrega

O projeto entrega, por reunião processada, um conjunto de artefatos derivados do áudio:

1. **Transcrição word-level** do áudio em PT-BR, produzida por WhisperX com modelo `large-v3`, em três formatos: JSON (fonte de verdade, com segmentos, palavras, timestamps, falantes e scores), TXT (texto por falante com timestamps, para leitura humana) e SRT (legenda com prefixo de falante, para reprodução sincronizada).
2. **Diarização**: separação de "quem falou quando", com labels genéricos (`SPEAKER_00`, `SPEAKER_01`, etc.) atribuídos pelo pyannote.audio.
3. **Mapeamento de falantes**: conversão dos labels genéricos para nomes reais, aplicada via arquivo YAML específico da reunião, regenerando JSON, TXT e SRT com os nomes corretos.
4. **Ata estruturada em Markdown**, quando solicitada, gerada por LLM em nuvem (Anthropic) a partir do JSON já nomeado.

A operação de adição de uma reunião nova ao pipeline (preparar áudio, criar YAML, rodar os scripts na ordem, refinar o mapeamento) é procedimento estável, candidato a GUIDE próprio; esta SPEC declara o que o pipeline entrega, não o passo a passo de operá-lo.

### 3.2 Fora de escopo e não-objetivos

O projeto **não** se compromete a, e **se recusa a otimizar por**, o seguinte (limites consolidados a partir do briefing técnico §12):

- **Migrar para serviço cloud de transcrição** (AssemblyAI, Deepgram ou equivalente). Reuniões podem conter material sensível; a transcrição roda local com GPU como escolha consciente de privacidade. Só a etapa de ata usa LLM em nuvem, e por decisão registrada (a ser DEC própria).
- **Acoplar a geração de ata ao script de transcrição.** São responsabilidades diferentes, com modos de falha e ciclos de iteração distintos. Sumarizar uma transcrição ruim produz erro com aparência de acerto.
- **Usar embedding de voz pré-cadastrado** para identificar falantes. O mapeamento é feito por arquivo YAML editável, opção mais simples e auditável; embedding fica fora do escopo inicial.
- **Expor qualquer API pública.** Este é projeto pessoal e profissional, operado por uma pessoa, não produto.
- **Trocar o Whisper por outro ASR** sem evidência empírica de ganho mensurável em PT-BR (taxa de erro comparativa em pelo menos três reuniões reais).
- **Adicionar dependência sem registro em DEC.** Toda biblioteca nova passa por avaliação documentada antes de entrar no `environment.yml`.

A separação entre fora de escopo (o que o projeto não faz) e não-objetivo (critério contra o qual o projeto não otimiza) é tênue neste projeto solo e operacional; ambos são tratados aqui na mesma lista, porque a consequência prática é idêntica: nenhuma das linhas acima é trabalho a fazer, e qualquer pressão para cruzá-las exige DEC.

---

## 4. Decomposição

O pipeline decompõe-se em três scripts numerados, executados em ordem. A decomposição é deliberada: cada script tem modo de falha e ciclo de iteração próprios, e nunca se mistura transcrição com sumarização no mesmo arquivo. Re-derivar TXT e SRT com nomes corretos não exige re-transcrever, que é a etapa cara.

### 4.1 Fluxo de dados

```
audio.m4a
   │
   ▼
[01_transcrever.py]        ASR (large-v3) + alinhamento word-level + diarização (pyannote)
   │
   ├──► {nome}.json        fonte de verdade (segmentos, palavras, timestamps, SPEAKER_XX, scores)
   ├──► {nome}.txt         texto por falante com SPEAKER_XX
   └──► {nome}.srt         legenda com SPEAKER_XX
              │
              ▼
[02_aplicar_mapeamento.py] lê config YAML, renomeia SPEAKER_XX → nomes reais
   │
   ├──► {nome}.json        JSON regenerado com nomes reais
   ├──► {nome}.txt         TXT regenerado
   └──► {nome}.srt         SRT regenerado
              │
              ▼
[03_gerar_ata.py]          LLM em nuvem (Anthropic) lê o JSON nomeado
   │
   └──► {nome}_ata.md      ata estruturada em Markdown
```

O script 01 roda uma vez por reunião. O script 02 roda quantas vezes forem necessárias até o mapeamento de falantes ficar correto. O script 03 roda apenas quando a transcrição nomeada está boa, e apenas quando a ata é solicitada (`ata.generate: true` na config).

### 4.2 Scripts, saídas e papéis

| Etapa | Script | Entrada | Saída | Onde roda |
|---|---|---|---|---|
| Transcrição | `src/01_transcrever.py` | áudio + (opcional) `initial_prompt` | `{nome}.json`, `.txt`, `.srt` com `SPEAKER_XX` | local, GPU |
| Mapeamento | `src/02_aplicar_mapeamento.py` | JSON do passo 1 + config YAML da reunião | `{nome}.json`, `.txt`, `.srt` com nomes reais | local |
| Ata | `src/03_gerar_ata.py` | JSON nomeado do passo 2 | `{nome}_ata.md` | LLM em nuvem (Anthropic) |

### 4.3 Saídas e fonte de verdade

São três saídas de transcrição por reunião, mais a ata opcional:

| Saída | Papel | Por que existe |
|---|---|---|
| JSON | **fonte de verdade** | estrutura completa; TXT, SRT e ata derivam dela. Sem JSON, qualquer reprocessamento exige re-transcrever (caro). Custo de armazenamento trivial (300 KB a 2 MB por hora). |
| TXT | leitura humana | texto formatado por falante com timestamps. |
| SRT | reprodução sincronizada | legenda com prefixo de falante, sincronizável com o áudio. |
| `_ata.md` | síntese | ata estruturada, gerada sob demanda a partir do JSON nomeado. |

### 4.4 Diretórios

| Diretório | Conteúdo | Versionado? |
|---|---|---|
| `src/` | os três scripts numerados | sim |
| `data/configs/` | `reuniao_template.yml`, `prompt_exemplo.txt`, e a config YAML de cada reunião | template sim; configs reais conforme sensibilidade |
| `data/audios_pendentes/`, `data/audios_processados/` | áudio bruto | não (gitignored) |
| `outputs/transcricoes/` | `{nome}.{json,txt,srt}` | não (gitignored) |
| `outputs/atas/` | `{nome}_ata.md` | não (gitignored) |

A fronteira entre o que é versionado (estrutura, scripts, templates) e o que nunca entra no Git (áudio, transcrições, atas, segredos) é fixada pela SPEC-001 §9 e auditada pela regra R-TAX-09 daquela SPEC.

### 4.5 Configuração por reunião

Cada reunião tem um arquivo `data/configs/reuniao_{data}_{topico}.yml` que declara: metadados da reunião (data, tópico, dica de contexto, nome do áudio), participantes (nome, papel, dica de voz), vocabulário a ancorar no `initial_prompt`, o `speaker_mapping` de `SPEAKER_XX` para nomes reais, e os parâmetros da ata (`generate`, `llm_provider`). O nome do áudio segue a mesma raiz do arquivo de config, mudando só a extensão, o que permite localizar a config a partir do áudio sem ambiguidade.

---

## 5. Critérios de sucesso

Os critérios abaixo são auditáveis: cada um aponta para artefato concreto ou método de verificação objetivo. Critérios marcados **(provisório)** serão calibrados após a primeira execução do pipeline em reunião real.

| ID | Critério | Como verificar |
|---|---|---|
| **C-01** | Cada reunião processada gera os três artefatos de transcrição: JSON, TXT e SRT. | Listagem de `outputs/transcricoes/` para a reunião: três arquivos com a mesma raiz. |
| **C-02** | Os falantes são mapeados de `SPEAKER_XX` para nomes reais via o YAML da reunião; os artefatos regenerados não contêm rótulo `SPEAKER_` quando o mapeamento foi aplicado e completado. | Inspeção do JSON/TXT/SRT após `02_aplicar_mapeamento.py`; nenhum `SPEAKER_\d\d` residual quando o `speaker_mapping` está totalmente preenchido. |
| **C-03** | O pipeline transcreve e diariza localmente, sem enviar áudio a serviço de transcrição em nuvem. Só a etapa de ata (script 03) usa LLM em nuvem, e apenas com o JSON textual nomeado, nunca com o áudio. | Inspeção dos scripts 01 e 02: nenhuma chamada de rede a serviço de ASR; o áudio nunca sai da máquina. |
| **C-04** | Cada dependência presente no `environment.yml` tem DEC correspondente ou está coberta por uma DEC de stack. Dependência sem rastro de decisão sinaliza dívida documental. | Cruzamento de `environment.yml` com `docs/DEC/INDEX_DEC.md`. |
| **C-05** | O JSON é a fonte de verdade: TXT, SRT e ata são derivados dele, e re-derivar não exige re-transcrever. | Inspeção dos scripts 02 e 03: ambos leem do JSON, nenhum re-invoca o WhisperX. |
| **C-06** | A geração de ata é desacoplada da transcrição: vive no script 03, separado de 01 e 02, e roda só quando solicitada (`ata.generate: true`). | Inspeção da estrutura de `src/`: a sumarização não aparece em 01 nem em 02. |
| **C-07** | Nenhum áudio de reunião, transcrição, ata ou segredo (`HF_TOKEN`, `.env`) é versionado no Git. | Varredura dos arquivos rastreados pelo Git e do `.gitignore` (cf. SPEC-001 R-TAX-09). |
| **C-08** **(provisório)** | A transcrição é utilizável: em reunião real, o autor reconhece a transcrição como fiel ao teor, mesmo com erros pontuais em termos técnicos ou nomes próprios. | Confirmação escrita do autor após primeira execução real; calibração da métrica de qualidade (taxa de erro em termos próprios). |
| **C-09** **(provisório)** | O `initial_prompt` com nomes e jargão da reunião reduz erros em termos próprios frente à transcrição sem prompt. | Comparação de duas transcrições da mesma reunião, com e sem `initial_prompt`, após primeira execução real. |

---

## 6. Operação Solo

Esta seção substitui a SPEC-003 (Contrato de Responsabilidade), dispensada como documento neste projeto por força do perfil solo de fundação definido em **DEC-META-004**. O projeto satisfaz simultaneamente as três condições de elegibilidade daquela DEC: é autoral solo (uma só pessoa produz e responde por tudo), sem terceiros contratualmente vinculados ao resultado (não há cliente, orientador, sócio, banca ou patrocinador), e de baixo risco a outros (o conteúdo é do próprio autor e o fracasso não recai sobre quem não consentiu).

**Acúmulo de papéis.** Bruno Serminaro acumula todos os papéis da §2: Diretor, Gestor, Autor e os papéis de revisão (Revisão técnica e Validação). Não há divisão de papéis a contratualizar.

**Ausência de revisão humana externa, por desenho.** O projeto opera sem revisão humana externa não por omissão temporária, mas por desenho deliberado e permanente. Não existe par técnico nem supervisor independente; assumir o contrário seria descrever uma cadeia que não existe.

**Freio compensatório: auditoria recorrente das regras `R-*`.** A compensação contra o viés de confirmação e contra a ausência de freio externo não é humana: é a auditoria recorrente de consistência contra as regras checáveis declaradas nas SPECs deste projeto, a saber, as `R-TAX-*` da SPEC-001 e as `R-FUN-*` da §7 desta SPEC. A auditoria é executada por três gatilhos:

- **Por marco**, a cada entrega relevante (fundação concluída, primeira execução real, novo script estável);
- **Por calendário**, em cadência mensal;
- **Por mudança de premissa**, sempre que uma decisão técnica consolidada (briefing §4) for revista ou um pressuposto de ambiente mudar.

O resultado de cada rodada é registrado em log de auditoria, em `docs/logs/` ou em BRIEF de período. Onde um projeto com equipe teria ata de revisão humana, este projeto tem o registro da auditoria.

**Descaracterização do perfil.** A dispensa da SPEC-003 só é legítima enquanto a auditoria existir de fato. Auditoria declarada e nunca executada descaracteriza o perfil solo e reativa, por força da DEC-META-004 §2.4, a obrigatoriedade de uma SPEC-003 plena com papéis atribuídos. Do mesmo modo, se qualquer condição de elegibilidade deixar de valer (entrada de colaborador, herança da ferramenta, surgimento de terceiro vinculado), o projeto gradua para a fundação de cinco peças, registrando a graduação em DEC própria.

---

## 7. Regras checáveis pelo skill de auditoria

Esta seção declara as regras `R-FUN-NN` que o skill genérico de auditoria de consistência (cf. SPEC-001 §11) verifica contra o estado real do projeto, especificamente sobre o que esta SPEC declara. Cada regra aponta para artefato concreto, e cada divergência ativa o fluxo interativo "atualizar SPEC ou ajustar projeto". A severidade orienta a decisão: `Crítica` exige decisão imediata; `Alta` exige decisão na sessão de auditoria; `Média` pode ser registrada como dívida.

| ID | Regra | Onde verificar | Severidade |
|---|---|---|---|
| **R-FUN-01** | Para cada reunião com transcrição em `outputs/transcricoes/`, existem os três artefatos JSON, TXT e SRT com a mesma raiz de nome. Cumprimento de C-01. | Listagem de `outputs/transcricoes/` por raiz de nome | Média |
| **R-FUN-02** | Toda dependência declarada em `environment.yml` tem DEC correspondente ou está coberta por DEC de stack. Dependência sem rastro de decisão sinaliza dívida documental. Cumprimento de C-04. | Cruzamento de `environment.yml` com `docs/DEC/INDEX_DEC.md` | Alta |
| **R-FUN-03** | Nenhuma saída de áudio, transcrição, ata ou segredo é versionada no Git; o `.gitignore` cobre `data/audios_*`, `outputs/` e `.env`. Cumprimento de C-07. Reforça e remete à R-TAX-09 da SPEC-001. | Inspeção do `.gitignore` e varredura dos arquivos rastreados | Crítica |
| **R-FUN-04** | Nenhum áudio de reunião é enviado a serviço de transcrição em nuvem; os scripts 01 e 02 não fazem chamada de rede a ASR externo; só o script 03 chama LLM em nuvem, e apenas com texto. Cumprimento de C-03. | Inspeção dos scripts 01, 02 e 03 por chamadas de rede | Crítica |
| **R-FUN-05** | A geração de ata vive isolada no script 03, separada de 01 e 02; nenhuma sumarização aparece nos scripts de transcrição e mapeamento. Cumprimento de C-06. | Inspeção da estrutura de `src/` | Alta |
| **R-FUN-06** | Para cada critério `C-NN` da §5, existe artefato concreto ou método de verificação descrito. Critério sem verificação possível é critério ornamental. | Inspeção da §5 cruzada com a estrutura real do projeto | Média |
| **R-FUN-07** | Esta SPEC-002 e a SPEC-001 referenciam-se mutuamente: a SPEC-001 aponta para a SPEC-002 (R-TAX-10) quanto à cláusula de Operação Solo; esta SPEC referencia a SPEC-001 quanto à taxonomia e às regras R-TAX. Ausência de referência cruzada sinaliza divergência de governança. | Inspeção dos campos `referencia:` e das seções citadas | Média |
| **R-FUN-08** | A cláusula "Operação Solo" (§6) existe nesta SPEC, declara o acúmulo de papéis, a ausência deliberada de revisão externa, e a cadência de auditoria das regras `R-*` (por marco, mensal, por mudança de premissa) com registro de resultado. Ausência da cláusula ou da cadência descaracteriza o perfil solo. Cumprimento conjunto com R-TAX-10 da SPEC-001 e DEC-META-004 §2.3/§2.4. | Parse da §6 desta SPEC | Crítica |

As regras acima são v1 e devem ser calibradas conforme o skill for utilizado e novas inconsistências aparecerem.

---

## 8. Critérios de revisão

Esta SPEC-002 é viva e versionável (SPEC-001 §7). Deve ser revisitada quando:

- Uma decisão técnica consolidada do briefing (§4: WhisperX, `large-v3`, `int8`, `condition_on_previous_text=False`, três saídas, mapeamento via YAML, LLM cloud para a ata) for revista, gerando DEC que afete o escopo ou a decomposição aqui descritos.
- Um quarto script, ou uma mudança estrutural no fluxo de dados, alterar a decomposição da §4.
- O conjunto de critérios `C-NN` ou de regras `R-FUN-NN` se mostrar insuficiente ou mal calibrado durante o uso do skill de auditoria.
- Os critérios marcados **(provisório)** forem calibrados após a primeira execução real do pipeline.
- Qualquer condição de elegibilidade do perfil solo (DEC-META-004 §2.1) deixar de valer, exigindo graduação para a fundação de cinco peças e substituição da cláusula da §6 por uma SPEC-003 plena.

---

## 9. Histórico

| Data | Versão | Evento |
|---|---|---|
| 2026-06-14 | v1 | SPEC-002 produzida em status `proposto`. Quarta e última peça da fundação documental do projeto earn-transcricao-reuniao (SPEC-001, REP-001, DEC-001, SPEC-002), alimentada por REP-001 e DEC-001. Descreve o pipeline local solo de transcrição de reuniões PT-BR (WhisperX + diarização pyannote + ata via LLM Anthropic). Adota o perfil solo de fundação da DEC-META-004: dispensa a SPEC-003 e absorve seu conteúdo essencial na cláusula "Operação Solo" (§6). Declara nove critérios de sucesso C-01 a C-09 (C-08 e C-09 provisórios) e oito regras checáveis R-FUN-01 a R-FUN-08. Aguarda revisão e aprovação. |

---

*Fim do documento.*
