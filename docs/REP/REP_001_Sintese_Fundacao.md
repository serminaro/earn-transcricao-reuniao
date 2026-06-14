---
documento: REP-001
titulo: Síntese da Fundação do Projeto earn-transcricao-reuniao
versao: v1
status: proposto
data: 2026-06-14
autor: Bruno Serminaro
supersede: —
referencia: SPEC-001, DEC-001, SPEC-002
---

# REP-001 · Síntese da Fundação do Projeto earn-transcricao-reuniao

> Consolida em um único relatório de onde o projeto vem e em que estado a fundação documental começa. Registra o problema, o ponto de partida (script simples de Whisper puro), as decisões técnicas herdadas do briefing, os achados confirmados separados das hipóteses ainda em aberto, as premissas operacionais, os vieses identificados e as pendências organizadas em ondas. Este REP é a fonte primária que alimenta a DEC-001 (decisão fundacional) e a SPEC-002 (Descrição do Projeto), e serve de âncora para as DECs técnicas e SPECs de glossário, ambiente e schema previstas para a Onda 2.

---

## 1. Contexto

O projeto nasce de uma necessidade operacional concreta do autor: transcrever reuniões em português brasileiro com identificação de quem falou e timestamps, e, quando útil, gerar uma ata estruturada a partir da transcrição. As reuniões têm de 2 a 4 participantes no caso típico (até 8 ocasional), duração de 30 a 90 minutos, e tratam de discussões técnicas, planejamento e alinhamento. O volume estimado é de até 5 reuniões por semana. A saída desejada não é só texto corrido: é texto separado por falante com marcação de tempo, mais uma representação estruturada que permita reprocessar sem re-transcrever.

O ponto de partida já existe e é deliberadamente modesto. O script `Transcreve/transcreve_simples.py` carrega o Whisper puro (`openai-whisper`), modelo `medium`, transcreve um arquivo `.m4a` fixo com `language="pt"` e grava uma única saída `.txt` com o texto corrido inteiro. São 27 linhas, sem CLI, sem diarização, sem alinhamento word-level, sem timestamps por palavra, sem separação de falantes, sem tratamento de erro, com caminhos de arquivo escritos no código. Ele prova o conceito de transcrição local funcionando, e nada além disso.

A razão para evoluir para um pipeline é direta: o script simples resolve "transformar áudio em texto", mas não resolve o problema real, que é "saber quem disse o quê, quando, em um formato reaproveitável, com ata opcional". Whisper puro não diariza. Modelo `medium` perde qualidade em termos técnicos e nomes próprios frente ao `large-v3`. Saída única em TXT obriga a re-transcrever (operação cara) toda vez que se queira mudar formato, corrigir nome de falante ou gerar ata. O pipeline supera o script simples adicionando ASR de melhor qualidade, alinhamento, diarização, três saídas com o JSON como fonte de verdade, mapeamento auditável de falantes e geração de ata desacoplada. Há também um subobjetivo declarado de aprendizado técnico, registrado aqui de forma explícita porque ele é simultaneamente motivador e fonte de viés (ver §7).

---

## 2. Escopo da fundação

Esta onda fundacional cobre a base documental do projeto sob o padrão SERMI, não o código nem a automação.

**Dentro do escopo desta onda:**

- As quatro peças SERMI fundacionais em modalidade solo: SPEC-001 (Taxonomia documental), REP-001 (esta Síntese), DEC-001 (Decisão fundacional) e SPEC-002 (Descrição do Projeto).
- O scaffolding do repositório: estrutura de pastas `docs/SPEC, REP, DEC, GUIDE, BRIEF, assets, logs` e arquivos de índice.
- A consolidação do briefing disperso em material rastreável sob a taxonomia canônica.

**Fora do escopo desta onda (fica para ondas seguintes):**

- O código dos três scripts Python (`01_transcrever.py`, `02_aplicar_mapeamento.py`, `03_gerar_ata.py`), que é Onda 3.
- O `CLAUDE.md` na raiz, instrução para o Claude Code operar o pipeline neste Linux, que é Onda 4.
- As DECs técnicas individuais e as SPECs de glossário, ambiente e schema de configuração, que são Onda 2.
- A validação empírica das hipóteses técnicas (ver §5), que só ocorre quando o pipeline rodar em áudio real.

A separação entre fundação documental (esta onda) e código (ondas posteriores) é intencional: documentar como decidir e o que foi decidido precede escrever o que executa a decisão, e o conteúdo cognitivo das peças fundacionais merece revisão antes de qualquer linha de código depender dele.

---

## 3. Trabalho realizado e migração ao SERMI

O insumo principal desta fundação é o documento `docs/assets/shared/BRIEFING_TRANSCRICAO_REUNIOES.md`, um briefing auto-contido (versão 1, maio de 2026) que já consolidava o caso de uso, o ambiente técnico, as decisões discutidas e justificadas, o glossário didático e os limites explícitos do projeto. O trabalho desta onda foi migrar esse material de uma pasta plana para a estrutura SERMI canônica e separar, dentro do próprio briefing, o que é decisão consolidada do que ainda é hipótese.

Dois pontos de divergência entre o briefing e o estado atual precisam ficar registrados, para não propagar inconsistência:

1. **Nomenclatura e ambiente.** O briefing chama o projeto de `learn-reunioes-pipeline` e referencia caminhos Windows (`C:\Users\...`). O projeto canônico atual é `earn-transcricao-reuniao`. O slug do briefing está superado pelo slug atual; onde houver conflito, vale o nome `earn-transcricao-reuniao`. Quanto ao ambiente, a suposição de Windows do briefing está superada: o pipeline roda nesta estação Linux (Ubuntu/Debian) do autor, a mesma descrita e governada no projeto `~/Projetos/learn-manutencao-linux`. A descrição detalhada da estação (distribuição, GPU NVIDIA, salvaguardas de driver e kernel) vive naquele projeto e não é reproduzida aqui; este projeto a assume como dada. As SPECs de ambiente da Onda 2 detalham apenas o que é específico do pipeline de transcrição (conda env, modelos, HF_TOKEN), referenciando o learn-manutencao-linux para o resto.

2. **Estrutura SERMI ingênua do briefing.** O §7 do briefing propõe uma estrutura SERMI própria (sete SPECs e sete DECs numeradas com títulos específicos). Essa proposta está superada pelo padrão canônico SERMI definido em DEC-META-002 e DEC-META-004. A numeração, a ordem de criação e a reserva dos primeiros números seguem o padrão canônico, não a sugestão do briefing. O conteúdo conceitual do §7 do briefing permanece como insumo, mas a forma documental é a canônica.

O briefing permanece como referência interna (anotações de campo do autor) em `docs/assets/shared/`, não como peça SERMI ativa. Seu conteúdo é absorvido por este REP, pela DEC-001 e pela SPEC-002.

---

## 4. Decisões técnicas herdadas do briefing

As decisões abaixo já foram discutidas, justificadas e aceitas no briefing (§4.1 a §4.11). Estão listadas aqui para rastreabilidade, com justificativa curta. Cada uma será formalizada como DEC atômica na Onda 2. Até lá, valem como decisões herdadas, não como DECs ainda.

| ID | Decisão | Justificativa curta | Formalização |
|---|---|---|---|
| D1 | Stack WhisperX (não `openai-whisper` puro nem `faster-whisper` standalone). | Integra ASR, alinhamento word-level e diarização via pyannote em um pipeline. Diarização é o diferencial para múltiplos falantes. | A formalizar como DEC na Onda 2 |
| D2 | Modelo Whisper `large-v3` como default. | Melhor qualidade em PT-BR, ganho perceptível sobre `medium` em termos técnicos e nomes próprios. Viável por haver GPU dedicada. | A formalizar como DEC na Onda 2 |
| D3 | `compute_type=int8` como default, com flag CLI para `float16`. | Reduz VRAM em cerca de 50% com perda desprezível em PT-BR. Escolha de precaução sobre VRAM (ver §5). | A formalizar como DEC na Onda 2 |
| D4 | `condition_on_previous_text=False` hardcoded, sem expor em CLI. | Evita loops alucinatórios em silêncios longos no PT-BR ("e foi e foi e foi"). | A formalizar como DEC na Onda 2 |
| D5 | VAD (Voice Activity Detection) ativo, default do WhisperX. | Pula trechos sem voz, ataca alucinação em silêncio puro. Complementar a D4, não redundante: atacam falhas diferentes. | A formalizar como DEC na Onda 2 |
| D6 | `initial_prompt` parametrizável por reunião, via arquivo `.txt` na CLI. | Ancora vocabulário (nomes, jargão), reduz erro em termos próprios em 10% a 30%. Melhor relação custo benefício. | A formalizar como DEC na Onda 2 |
| D7 | Três saídas por reunião: JSON, TXT, SRT, com JSON como fonte de verdade. | TXT e SRT são derivados do JSON. Sem JSON, qualquer reprocessamento exige re-transcrever, que é caro. Custo de JSON é trivial. | A formalizar como DEC na Onda 2 |
| D8 | Mapeamento de falantes via arquivo YAML por reunião. | pyannote devolve labels genéricos (`SPEAKER_00`). YAML editável é a opção mais simples e auditável. Inferência por LLM e embedding de voz descartados. | A formalizar como DEC na Onda 2 |
| D9 | LLM em nuvem para gerar a ata (não local). | Qualidade superior e simplicidade. Conteúdo das reuniões não tem sensibilidade que impeça. Trade-off aceito: dados saem da máquina. | A formalizar como DEC na Onda 2 |
| D10 | Claude Code (neste Linux) como orquestrador, não executor da transcrição. Supera a escolha do briefing por Cowork. | WhisperX precisa de GPU local e modelo pesado; o orquestrador não transcreve, coordena. O Claude Code já opera nesta estação Linux (ver learn-manutencao-linux), lê `CLAUDE.md` na raiz, organiza pastas, move áudio de pendentes para processados, chama o LLM da ata e roda os scripts. Dispensa instalar e manter o Cowork. | A formalizar como DEC na Onda 2 |
| D11 | `HF_TOKEN` lido de variável de ambiente do conda env, validado com try/except, falha cedo. | Sem `.env`, sem dependência extra. Token necessário para baixar modelos pyannote, que exigem aceite de termos. | A formalizar como DEC na Onda 2 |

Decorrência arquitetural de D7 e D8: o pipeline se decompõe em três scripts (transcrever, aplicar mapeamento, gerar ata), de modo que re-derivar TXT/SRT com nomes corretos não exige re-transcrever. Essa decomposição é consequência das decisões acima e será detalhada na SPEC de pipeline operacional da Onda 2.

---

## 5. Achados confirmados versus hipóteses candidatas

A separação abaixo é deliberada. O briefing apresenta as decisões como "discutidas, justificadas e aceitas", mas justificativa de projeto não é o mesmo que medição empírica. Nada do pipeline novo foi ainda rodado em áudio real neste projeto.

**Achados confirmados:**

- O script simples (`transcreve_simples.py`, Whisper puro, modelo `medium`) transcreve áudio PT-BR e gera TXT. Isso roda hoje. É o piso comprovado.
- Whisper puro não faz diarização nem alinhamento word-level. Isso é fato da ferramenta, não hipótese.
- WhisperX integra ASR, alinhamento e diarização, e exige token Hugging Face com aceite de termos em dois modelos pyannote (`speaker-diarization-3.1` e `segmentation-3.0`). Isso é requisito documentado da ferramenta.

**Hipóteses candidatas, a confirmar empiricamente:**

- **VRAM.** A hipótese é que `large-v3` em `int8` cabe na GPU disponível (GTX 1660 SUPER, 6 GB). O briefing assumiu "cenário modesto de VRAM por precaução" porque a GPU específica não estava confirmada no momento da redação. Cabe ou não, e com qual `batch_size`, é a confirmar rodando.
- **Ganho de qualidade de `large-v3` sobre `medium` em PT-BR.** Tratado como perceptível, mas não medido neste projeto. Confirmar com comparação em reuniões reais antes de fixar como conclusão.
- **Redução de erro de 10% a 30% via `initial_prompt`.** Faixa de melhoria citada, sem medição local. A confirmar.
- **Adequação da diarização do pyannote ao caso típico.** Quão bem separa 2 a 4 vozes, e como degrada com sobreposição de fala, é a observar nas primeiras reuniões.
- **Suficiência da geração de ata por LLM cloud.** Qualidade da ata depende da qualidade da transcrição e do mapeamento. Ata sobre transcrição ruim é resumo errado com aparência de certo. A avaliar caso a caso.

Não se deve tratar nenhuma das hipóteses como fato até haver medição em pelo menos algumas reuniões reais. O número exato de reuniões para considerar uma hipótese confirmada será definido nas SPECs/DECs da Onda 2.

---

## 6. Premissas operacionais

Premissas que servem de base para as peças subsequentes. Mudança em qualquer destas dispara reavaliação.

| ID | Premissa |
|---|---|
| P1 | Estação Linux do autor (Ubuntu/Debian), descrita e governada em `~/Projetos/learn-manutencao-linux`, com GPU NVIDIA GTX 1660 SUPER de 6 GB de VRAM. A VRAM é o teto de memória que condiciona modelo, `compute_type` e `batch_size`; o SO é Linux, não Windows como supunha o briefing. |
| P2 | Ambiente Python gerenciado por conda (não pip puro, não poetry). Python 3.10 ou superior. |
| P3 | `HF_TOKEN` fornecido por variável de ambiente do conda env, com aceite prévio dos termos dos modelos pyannote. |
| P4 | Provider de LLM para a ata: Anthropic, conforme exemplo de configuração do briefing (`llm_provider: "anthropic"`). |
| P5 | Volume de até 5 reuniões por semana, com 2 a 4 participantes típico (até 8 ocasional) e 30 a 90 minutos de duração. |
| P6 | Conteúdo das reuniões sem sensibilidade jurídica ou financeira declarada (discussões técnicas, planejamento, alinhamento). É essa premissa que sustenta a decisão D9 de enviar dados a LLM cloud. Se mudar, D9 deve ser reavaliada. |
| P7 | Operação solo. O sistema precisa ser leve para uma única pessoa manter e operar. |
| P8 | Ferramenta operacional pessoal/profissional, não SaaS, não produto público, não serviço com SLA. Sem exposição de API pública. |

---

## 7. Vieses identificados

Listados deliberadamente, porque tornar o risco visível é parte de mitigá-lo. Os dois primeiros são os mais relevantes neste projeto.

| Viés | Manifestação no projeto | Mitigação |
|---|---|---|
| Aprendizado inflando complexidade | O aprendizado técnico é subobjetivo declarado. Pode empurrar o projeto a adotar componentes (mais scripts, mais parâmetros, mais saídas) por interesse técnico, não por necessidade operacional. | Toda adição de complexidade tem de se justificar pela necessidade do caso de uso, não pela curiosidade. Os limites explícitos do briefing (§12) funcionam como freio. |
| Ausência de freio externo em projeto solo | Não há revisor independente. Decisões técnicas passam sem contestação de um par. | Separar achado de hipótese (§5) por disciplina escrita. Exigir medição empírica antes de fechar hipótese como fato. Registrar critérios de reavaliação nas DECs. |
| Tratar justificativa como medição | O briefing apresenta decisões como "aceitas", o que pode soar como validado. Justificativa de projeto não é dado empírico. | Manter o §5 separando confirmado de candidato. Não promover hipótese a conclusão sem medir. |
| Custo afundado documental | Tendência de manter a estrutura ingênua do briefing (§7 dele) só porque já existe. | A estrutura canônica SERMI prevalece (ver §3). Divergir do briefing onde fizer sentido. |
| Romantização de número citado | Faixas como "ganho perceptível" ou "10% a 30%" vêm de fontes externas, não de medição local. | Não usar esses números como prova local. Tratá-los como expectativa a verificar. |

---

## 8. Pendências e próximos passos

O projeto segue um plano em quatro ondas, validando entre cada uma.

| Onda | Entrega | Estado |
|---|---|---|
| 1. Fundação documental | SPEC-001, REP-001 (este), DEC-001, SPEC-002 e scaffolding de pastas. | Em andamento |
| 2. Documentação técnica | DECs técnicas (formalizando D1 a D11) e SPECs de glossário, ambiente técnico e schema de configuração por reunião. | A fazer |
| 3. Código | Os três scripts Python: `01_transcrever.py` (evolui do `transcreve_simples.py`), `02_aplicar_mapeamento.py` e `03_gerar_ata.py`. | A fazer |
| 4. Integração do orquestrador | `CLAUDE.md` na raiz, instrução para o Claude Code operar o pipeline neste Linux. | A fazer |

**Próximos artefatos imediatos:**

| Artefato | Descrição |
|---|---|
| DEC-001 | Síntese atômica deste REP e decisão de adoção do padrão fundacional. Em fila imediata. |
| SPEC-002 | Descrição do Projeto, alimentada por este REP. |
| DECs técnicas (Onda 2) | Uma DEC atômica por decisão D1 a D11, com contexto, alternativas, consequências e critério de reavaliação. |
| SPECs de glossário, ambiente e schema (Onda 2) | Glossário de áudio e ASR, ambiente técnico (conda, GPU, HF_TOKEN) e schema YAML de configuração por reunião. |

**Pendência de validação empírica.** Antes de declarar o pipeline pronto, testar ponta a ponta em reunião curta (5 a 10 minutos) e confirmar as hipóteses do §5, com destaque para a de VRAM (P1 versus D2/D3).

---

## 9. Histórico

| Data | Evento |
|---|---|
| 2026-06-14 | REP-001 v1 produzido em status `proposto`. Consolida o material disperso em `docs/assets/shared/BRIEFING_TRANSCRICAO_REUNIOES.md` (versão 1, maio de 2026) e o ponto de partida `Transcreve/transcreve_simples.py`. Registra 11 decisões técnicas herdadas (D1 a D11, a formalizar como DEC na Onda 2) e 8 premissas operacionais (P1 a P8). Marca a estrutura SERMI ingênua do §7 do briefing como superada pelo padrão canônico (DEC-META-002, DEC-META-004) e o slug `learn-reunioes-pipeline` como superado por `earn-transcricao-reuniao`. Alimenta DEC-001 (síntese atômica) e SPEC-002 (Descrição do Projeto). |
| 2026-06-14 | Ajuste em v1 (pré-aprovação). Ambiente-alvo fixado como a estação Linux (Ubuntu/Debian) descrita em `~/Projetos/learn-manutencao-linux`, superando a suposição de Windows do briefing (§3, P1). Orquestrador passa de Cowork para o Claude Code rodando neste Linux (D10); a Onda 4 passa a entregar `CLAUDE.md` em vez de `COWORK.md` (§2, §8). |

---

*Fim do documento.*
