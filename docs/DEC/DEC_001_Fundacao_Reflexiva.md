---
documento: DEC-001
titulo: Fundação reflexiva — adoção do padrão documental SERMI enxuto (perfil solo) para earn-transcricao-reuniao
versao: v1
status: proposto
data: 2026-06-14
autor: Bruno Serminaro
supersede: —
referencia: SPEC-001, REP-001, SPEC-002
---

# DEC-001 · Fundação reflexiva — adoção do padrão documental SERMI enxuto (perfil solo) para earn-transcricao-reuniao

> Decisão atômica que adota, para o projeto earn-transcricao-reuniao (pipeline local de transcrição de reuniões em PT-BR), o perfil solo de fundação documental SERMI definido em DEC-META-004: quatro peças (SPEC-001, REP-001, esta DEC, SPEC-002 com cláusula "Operação Solo"), dispensada a SPEC-003. É a primeira DEC do projeto e o ato fundador da sua governança documental. A síntese reflexiva que justifica e descreve a fundação está em REP-001. Esta DEC registra, em forma atômica e imutável, apenas a decisão de adotar tal padrão e seus desdobramentos diretos.

---

## 1. Contexto

O projeto nasceu de duas coisas concretas: um briefing auto-contido (BRIEFING_TRANSCRICAO_REUNIOES.md) que consolidou contexto, caso de uso, ambiente técnico e onze decisões técnicas já discutidas, e um script `transcreve_simples.py` (Whisper puro, modelo `medium`, saída única em TXT) vivendo em pasta plana, fora de qualquer estrutura de governança. O briefing já antecipava a intenção de organizar o repositório sob o padrão SERMI, mas o conteúdo ainda não tinha sido formalizado em peças fundacionais.

O autor adota SERMI em todos os seus projetos autorais. A questão de fundação, portanto, não é "adotar ou não SERMI", e sim qual nível de fundação aplicar a este projeto específico. A DEC-META-002 fixou que todo projeto autoral produz cinco peças fundacionais em ordem canônica (SPEC-001, REP-001, DEC-001, SPEC-002, SPEC-003). A DEC-META-004 refinou parcialmente essa regra, criando o perfil solo de quatro peças para projetos conduzidos por uma só pessoa, sem terceiros vinculados e de baixo risco a outros.

A decisão precisa ser tomada agora, antes de migrar o script para `src/01_transcrever.py` e antes de escrever as SPECs técnicas e DECs de stack (WhisperX, modelo, saídas, etc.). Toda a documentação derivada deve nascer sob o nível de fundação fixado aqui, sob pena de retrabalho de reclassificação depois.

Este é um projeto que se enquadra com folga no perfil solo. É ferramenta operacional pessoal e profissional, explicitamente declarada como "não é SaaS, não é produto público, não é serviço com SLA". Uma pessoa produz e opera. Não há cliente pagante, sócio, orientador ou banca que aprove entregas. O fracasso recai sobre o próprio autor, não sobre terceiros que não consentiram.

---

## 2. Decisão

**Adotar para earn-transcricao-reuniao a fundação documental SERMI no perfil solo definido em DEC-META-004: quatro peças produzidas na ordem canônica truncada SPEC-001 → REP-001 → DEC-001 → SPEC-002, com a SPEC-003 dispensada como documento e seu conteúdo essencial absorvido por uma cláusula "Operação Solo" na SPEC-002, confirmando que o projeto satisfaz simultaneamente as três condições de elegibilidade (autoral solo, sem terceiros vinculados, baixo risco a outros).**

A decisão inclui:

- Adotar a taxonomia SERMI de cinco tipos (SPEC, REP, GUIDE, BRIEF, DEC), frontmatter YAML obrigatório, convenções de nome e estrutura de pastas `docs/<TIPO>/`, conforme será fixado na SPEC-001 do projeto.
- Produzir quatro peças fundacionais, não cinco: SPEC-001 (taxonomia), REP-001 (síntese da fundação), esta DEC-001 e SPEC-002 (descrição do projeto com cláusula "Operação Solo").
- Dispensar a SPEC-003 (Contrato de Responsabilidade) como documento dedicado, por não haver cadeia de papéis entre pessoas a coordenar. O autor acumula todos os papéis (Autor, Gestor, Diretor, e os papéis de revisão Peer e Supervisor), fato a ser declarado na cláusula "Operação Solo" da SPEC-002.
- Substituir o freio humano externo (Peer Review e Supervisor, ausentes por desenho) pela auditoria recorrente de consistência contra as regras checáveis `R-*` declaradas nas SPECs, tornada freio compensatório obrigatório nos termos da DEC-META-004 §2.4.

---

## 3. Origem / rastro

Conforme princípio SERMI de rastreabilidade DEC × artefato:

| Artefato | Como sustenta esta decisão |
|---|---|
| **BRIEFING_TRANSCRICAO_REUNIOES.md** | Briefing original do projeto. Consolidou contexto, caso de uso, ambiente, decisões técnicas e a intenção de organizar o repositório sob SERMI. Origem material do projeto e ponto de partida da fundação. |
| **DEC-META-002** | Fixou a fundação documental obrigatória em cinco peças e a ordem canônica. É a regra-mãe que define o que cada peça contém e em que sequência são produzidas. |
| **DEC-META-004** | Criou o perfil solo de quatro peças, refinando parcialmente a DEC-META-002 §2.3/§4.4. Define as três condições de elegibilidade, a dispensa da SPEC-003, a cláusula "Operação Solo" e a auditoria recorrente como freio. É a base direta desta decisão. |

---

## 4. Alternativas consideradas

### 4.1 Pasta plana, sem governança documental

Manter o estado atual: o script em pasta plana, o briefing como único documento de contexto, sem SPECs, DECs ou REP versionados. Evoluir o código diretamente, documentando só se e quando surgir necessidade.

**Descartada porque:**
- Perde rastreabilidade e auditabilidade desde o início. As onze decisões técnicas já tomadas (WhisperX, large-v3, int8, saídas JSON/TXT/SRT, etc.) ficariam sem registro atômico do porquê, e qualquer reavaliação futura careceria de ponto-fixo a comparar.
- Contradiz a prática consolidada do autor, que adota SERMI em todos os projetos autorais. O próprio briefing já declarava a intenção de migrar para o padrão.
- O briefing alerta que "não adicionar dependências sem registro em DEC" e que toda decisão de stack passa por avaliação. Sem estrutura de DEC, essa disciplina não tem onde se materializar.

### 4.2 Fundação completa de cinco peças, com SPEC-003 e papéis atribuídos a pessoas

Aplicar a fundação plena da DEC-META-002: produzir também a SPEC-003 (Contrato de Responsabilidade), com cadeia Diretor → Gestor → Supervisor → Peer Review → Autor e atribuição de cada papel a uma pessoa.

**Descartada porque:**
- Overhead injustificado para projeto de uma pessoa só. A SPEC-003, neste caso, descreveria uma cadeia que não existe: o autor acumula todos os papéis e o documento se reduziria a declarar esse acúmulo, informação que cabe numa cláusula, não num documento dedicado.
- Reproduz exatamente o "custo afundado documental" e a peça vazia por princípio que a DEC-META-004 §4.2 rejeitou. Manter um contrato onde não há contrato é forçar a forma onde falta a substância.
- O projeto satisfaz as três condições de elegibilidade do perfil solo (autoral solo, sem terceiros vinculados, baixo risco a outros). Aplicar cinco peças seria ignorar a regra específica (DEC-META-004) que existe justamente para este caso.

### 4.3 Adotar SERMI mas adiar a fundação para depois do código

Migrar primeiro o script para `src/`, escrever os dois scripts que faltam (mapeamento e geração de ata), validar o pipeline ponta a ponta, e só então produzir as peças fundacionais.

**Descartada porque:**
- Inverte a ordem canônica. A DEC-META-002 §2.2 fixa que a fundação precede a execução substantiva justamente porque cada peça tem dependência lógica sobre a anterior, e porque a documentação derivada deve nascer já sob o padrão fixado. Documentar depois força reclassificação retroativa.
- A decisão de fundação é barata e o adiamento não compra nada: as quatro peças do perfil solo são leves e não bloqueiam o código, que pode evoluir em paralelo assim que o nível de fundação está fixado.

---

## 5. Consequências

### 5.1 Consequências positivas

- **Fundação proporcional ao projeto.** Quatro peças onde a quinta seria vazia. Mesma disciplina epistêmica da fundação completa, sem o atrito de manter um contrato de responsabilidade que só declararia acúmulo de papéis.
- **Rastreabilidade desde o início.** As decisões técnicas do briefing passam a ter lugar canônico (DECs de stack a produzir), e qualquer decisão futura pode ser justificada por referência a DEC anterior.
- **Projeto nasce auditável.** As regras checáveis `R-TAX-NN` (SPEC-001) e `R-FUN-NN` (SPEC-002) dão ao skill genérico de auditoria um ponto de entrada uniforme, igual ao dos demais projetos autorais.
- **Coerência cross-projeto.** Quem conhece a fundação de qualquer outro projeto do autor sabe ler a deste, e vice-versa. O perfil solo é um invariante declarado, não uma exceção ad-hoc.
- **Invariante claro para o freio.** A auditoria recorrente vira condição de legitimidade do perfil, e o registro de cada rodada é o rastro objetivo do freio compensatório.

### 5.2 Consequências negativas / custo aceito

- **Overhead documental antes de uma linha de código nova rodar.** Produzir quatro peças fundacionais consome tempo que poderia ir direto para adaptar os scripts. Aceito porque o custo das quatro peças no perfil solo é baixo e a fundação habilita o resto sem bloquear o código.
- **Risco de viés de confirmação sem freio externo humano.** O autor acumula todos os papéis, inclusive os de revisão. Não há Peer Review nem Supervisor que contradiga uma decisão ruim. A compensação (auditoria recorrente) é procedimental, não humana, e só funciona se for efetivamente rodada. Se a auditoria for declarada e nunca executada, o freio some e o perfil solo fica descaracterizado (DEC-META-004 §2.4).
- **Risco de aderência cerimonial.** Produzir as quatro peças "para cumprir" o padrão do autor, sem reflexão real sobre o que cada uma precisa conter neste projeto. Vigiável pela própria auditoria e pela revisão das regras `R-*`.
- **Mais de um invariante de fundação no ecossistema do autor.** Coexistem agora dois perfis (quatro e cinco peças). Custo de distinção empurrado para o skill de auditoria e para a leitura humana, que precisam checar a declaração de elegibilidade antes de julgar a ausência da SPEC-003.

### 5.3 O que esta decisão NÃO resolve

- **Não garante a qualidade do pipeline.** Decidir o nível de fundação documental não diz nada sobre a acurácia da transcrição, da diarização ou da ata. Qualidade de pipeline se afere por teste empírico, não por governança documental.
- **Não substitui teste empírico.** As decisões técnicas do briefing (WhisperX, large-v3, int8, mapeamento via YAML, LLM cloud para ata) seguem dependendo de validação em reuniões reais, conforme o próprio briefing exige (por exemplo, TER comparativa em pelo menos 3 reuniões antes de trocar de ASR).
- **Não decide o conteúdo material das SPECs nem das DECs de stack.** Define apenas o nível e a estrutura da fundação, não o que cada peça vai afirmar.
- **Não define o provider de LLM para a ata** nem outras pendências técnicas em aberto no briefing (VRAM real, volume efetivo, sensibilidade de conteúdo).
- **Não constrói o skill genérico de auditoria.** Pressupõe sua existência como freio compensatório, à semelhança da DEC-META-004.

---

## 6. Critérios de reavaliação

Esta decisão deve ser revisitada, e potencialmente substituída por nova DEC com `supersede:`, quando uma ou mais das seguintes condições se verificarem:

| Gatilho | O que reavaliar |
|---|---|
| Qualquer condição de elegibilidade da DEC-META-004 §2.1 deixar de valer (entra cliente, sócio, orientador ou banca; o resultado passa a vincular terceiros; o risco a outros cresce) | O projeto **gradua** para a fundação completa de cinco peças: a cláusula "Operação Solo" da SPEC-002 é substituída por uma SPEC-003 plena, com papéis atribuídos a pessoas. A graduação é registrada em DEC nova neste projeto (DEC-META-004 §2.5). |
| A auditoria recorrente das regras `R-*` deixar de ser executada | O freio compensatório que legitima a dispensa da SPEC-003 some. Auditoria declarada e nunca rodada **descaracteriza** o perfil solo e reativa a exigência de SPEC-003 (DEC-META-004 §2.4). Resposta: retomar a auditoria ou produzir a SPEC-003. |
| Aderência cerimonial virar sintoma observável (peças produzidas sem reflexão real, regras `R-*` que ninguém checa) | Reduzir o escopo das peças ao mínimo efetivamente usado, ou revisar as regras checáveis para que capturem divergência real em vez de ruído. |
| SERMI evoluir para versão que altere tipos ou estrutura de fundação | Revisão alinhada à nova versão. |

---

## 7. Histórico

| Data | Evento |
|---|---|
| 2026-06-14 | DEC-001 v1 produzida em status `proposto`. Primeira DEC do projeto earn-transcricao-reuniao. Adota a fundação documental SERMI no perfil solo de quatro peças (DEC-META-004): SPEC-001, REP-001, esta DEC, SPEC-002 com cláusula "Operação Solo", dispensada a SPEC-003. Confirma a elegibilidade solo do projeto (autoral solo, sem terceiros vinculados, baixo risco a outros) e fixa a auditoria recorrente das regras `R-*` como freio compensatório obrigatório. Decorre do briefing original, da DEC-META-002 e da DEC-META-004. |

---

*Fim do documento.*
