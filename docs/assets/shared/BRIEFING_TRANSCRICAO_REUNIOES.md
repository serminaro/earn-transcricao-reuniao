# Briefing: Pipeline de Transcrição de Reuniões (`learn-reunioes-pipeline`)

> Documento de contexto para alimentar outra conversa ou outro assistente.
> Auto-contido. Lê de cima para baixo sem dependências externas.
> Versão: 1, maio de 2026.

---

## 0. Como o assistente deve operar nesta conversa

Antes de qualquer coisa técnica, o assistente que receber este documento
deve seguir os princípios abaixo, que vêm das preferências consolidadas
do usuário (Decision Architect):

1. **Tom direto, técnico, sem floreio**. Sem otimismo artificial, sem
   linguagem motivacional, sem validação automática das escolhas do
   usuário.
2. **Português brasileiro**. Termos técnicos em inglês quando pertinente.
3. **Não usar travessões como pontuação estilística**. Usar vírgulas,
   pontos, dois-pontos e parênteses.
4. **Prosa para raciocínio, tabelas e listas para dados estruturados**.
   Bullet point só quando agrega.
5. **Sempre tornar explícitos**: premissas, incertezas, trade-offs,
   vieses, critérios de decisão, limitações dos dados e modelos,
   hipóteses candidatas (separadas dos achados confirmados).
6. **Calibração de extensão**: suficiente, curto sem perder rigor.
   Sem padding.
7. **Antes de criar arquivo com mais de 30 linhas ou fazer mudança
   estrutural significativa, perguntar primeiro**. Mostrar esqueleto,
   validar abordagem, depois codar.
8. **Toda análise termina com recomendação executável e próximos
   passos**.
9. **Patologias a recusar**:
   - Romantização dos dados ("os dados mostram que..." sem dizer quem
     coletou e como)
   - Esconder incerteza (previsão pontual quando há intervalo)
   - Tratar modelo como realidade
   - Vender complexidade desnecessária
   - Achado inflado (hipótese sugestiva apresentada como conclusão)

Defaults do usuário: **conda** para Python, **Markdown** para
documentação, **Git** para versionamento.

---

## 1. O que é o projeto

Pipeline de software para transcrever reuniões em português, com
identificação de falantes e geração eventual de ata estruturada,
operado por uma única pessoa, em ambiente Windows, com GPU dedicada,
seguindo o padrão documental SERMI do usuário.

O projeto não é SaaS, não é produto público, não é serviço com SLA.
É ferramenta operacional pessoal/profissional, com aprendizagem
técnica como subobjetivo declarado.

---

## 2. Caso de uso típico

| Item | Valor |
|---|---|
| Idioma | Português brasileiro |
| Participantes por reunião | 2 a 4 típico, até 8 ocasional |
| Volume | Até 5 reuniões por semana |
| Duração média da reunião | 30 a 90 minutos |
| Conteúdo | Discussões técnicas, planejamento, alinhamento |
| Saída desejada | TXT com falantes e timestamps + JSON estruturado + ata em markdown |

---

## 3. Ambiente técnico

- **SO**: Windows 10/11
- **Linguagem**: Python 3.10+
- **Gerenciador de ambiente**: conda (não pip puro, não poetry)
- **Hardware**: GPU NVIDIA dedicada (assumido cenário modesto de VRAM
  por precaução, ver decisões abaixo)
- **Caminho local do repo**: `C:\Users\BrunoAlexandredeCarv\Projetos\learn-reunioes-pipeline`

---

## 4. Decisões técnicas consolidadas, com justificativa

Cada decisão abaixo já foi discutida, justificada e aceita. **Não
revisitar** sem motivo concreto. Caso o assistente identifique algo
que invalide a decisão, deve dizer explicitamente o que mudou.

### 4.1. Stack: WhisperX

**Decisão**: usar WhisperX (não `openai-whisper` puro, não
`faster-whisper` standalone).

**Por quê**: WhisperX combina três coisas em um pipeline integrado:
ASR (Whisper), alinhamento word-level (forced alignment), e
diarização (separação de quem falou) via `pyannote.audio`. Para
reuniões com múltiplos falantes, esses três componentes juntos são o
diferencial. `faster-whisper` sozinho é mais rápido mas não diariza.
`openai-whisper` é a referência didática mas é o mais lento.

**Trade-off aceito**: WhisperX exige token Hugging Face e aceite de
termos de uso em dois modelos pyannote (`pyannote/speaker-diarization-3.1`
e `pyannote/segmentation-3.0`).

### 4.2. Modelo Whisper: `large-v3`

**Decisão**: usar `large-v3` como modelo default.

**Por quê**: melhor qualidade em português atualmente. Em PT-BR, o
ganho sobre `medium` é perceptível em termos técnicos e nomes
próprios. Como há GPU dedicada, é viável.

**Trade-off aceito**: maior consumo de VRAM. Mitigado pela escolha de
`compute_type=int8` (ver 4.3).

### 4.3. `compute_type=int8` como default

**Decisão**: rodar quantizado em int8 por padrão, com flag CLI para
subir para `float16` se houver folga de VRAM.

**Por quê**: int8 reduz consumo de VRAM em cerca de 50% com perda de
qualidade desprezível em PT-BR. Assumiu-se cenário modesto por
precaução (a GPU específica do usuário não foi confirmada).

### 4.4. `condition_on_previous_text=False` hardcoded

**Decisão**: forçado a False, sem expor em CLI.

**Por quê**: em PT-BR, o default True ocasionalmente causa loops
alucinatórios em silêncios longos ("e foi e foi e foi..."). False
evita esse modo de falha.

### 4.5. VAD ativo (default do WhisperX)

**Decisão**: manter VAD (Voice Activity Detection) ativo.

**Por quê**: VAD pula trechos sem voz, atacando outro modo de falha
(alucinação em silêncio puro, tipo "obrigado por assistir" porque o
Whisper foi treinado em vídeos do YouTube). VAD e
`condition_on_previous_text=False` **não são redundantes**, atacam
problemas diferentes e são complementares.

### 4.6. `initial_prompt` parametrizável por reunião

**Decisão**: aceitar um arquivo .txt com prompt inicial via CLI.

**Por quê**: Whisper aceita um texto curto que ancora vocabulário.
Para reuniões corporativas, passar nomes dos participantes e jargão
recorrente reduz erros de transcrição em 10% a 30% em termos próprios.
É o ajuste com melhor relação custo benefício.

### 4.7. Três saídas: JSON, TXT, SRT (JSON é fonte de verdade)

**Decisão**: gerar três arquivos por reunião.

- **JSON**: estrutura completa com segmentos, palavras, timestamps,
  falantes, scores. Fonte de verdade do pipeline.
- **TXT**: texto formatado por falante com timestamps. Para leitura
  humana.
- **SRT**: legendas com prefixo de falante. Para reprodução
  sincronizada com áudio.

**Por quê**: TXT e SRT são derivados do JSON. Sem JSON, qualquer
reprocessamento (refinar formato, gerar ata, exportar) exige
re-transcrever, o que é caro. Custo de JSON é trivial (300 KB a 2 MB
por hora de reunião).

### 4.8. Mapeamento de falantes via arquivo YAML por reunião

**Decisão**: pyannote retorna labels genéricos (`SPEAKER_00`,
`SPEAKER_01`, etc). O mapeamento para nomes reais é feito via arquivo
YAML específico daquela reunião, editado manualmente ou pelo Cowork.

**Por quê**: opção mais simples e auditável. Alternativas descartadas:
inferência via LLM (frequentemente erra em pessoas pouco faladoras),
embedding de voz pré-cadastrado (complexo, fora de escopo inicial).

### 4.9. LLM cloud para a ata (não local)

**Decisão**: usar API de LLM em nuvem (Anthropic, OpenAI ou Google) para
gerar a ata a partir do JSON. Provider específico a definir.

**Por quê**: qualidade superior, simplicidade. Conteúdo das reuniões
do usuário não tem sensibilidade que impeça essa escolha. Trade-off
aceito: dados saem da máquina local.

### 4.10. Cowork como orquestrador, não executor da transcrição

**Decisão**: a transcrição roda em Python local (com GPU). O Cowork
(produto Anthropic) é usado para orquestrar fluxo, organizar arquivos,
gerar ata, e eventualmente atualizar mapeamento de falantes.

**Por quê**: WhisperX precisa de GPU local e modelo pesado. Cowork
não é o lugar para isso. Cowork agrega valor na coordenação:
agendamento, organização de pastas, chamada de LLM.

### 4.11. Token HF via variável de ambiente conda

**Decisão**: ler `HF_TOKEN` de variável de ambiente do conda env,
validar com try/except, falhar cedo com mensagem útil. Sem `.env`,
sem dependência extra.

**Comando para configurar**:
```bash
conda env config vars set HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
conda deactivate
conda activate <nome_do_env>
```

---

## 5. Arquitetura: três scripts numerados

O pipeline é decomposto em três scripts para que cada um possa ser
iterado independentemente. Nunca misturar transcrição com sumarização
no mesmo script (modos de falha diferentes, ciclos de iteração
diferentes).

```
audio.m4a
   │
   ▼
[01_transcrever.py]    ASR + alinhamento + diarização
   │
   ├──► {nome}.json    fonte de verdade
   ├──► {nome}.txt     texto com SPEAKER_XX
   └──► {nome}.srt     legenda com SPEAKER_XX
              │
              ▼
[02_aplicar_mapeamento.py]    aplica config YAML, renomeia SPEAKER_XX → nomes reais
   │
   ├──► {nome}.json    JSON atualizado com nomes reais
   ├──► {nome}.txt     TXT regenerado
   └──► {nome}.srt     SRT regenerado
              │
              ▼
[03_gerar_ata.py]    LLM cloud lê JSON nomeado, gera ata
   │
   └──► {nome}_ata.md
```

**Vantagem dessa decomposição**: re-derivar TXT/SRT com nomes corretos
não exige re-transcrever (que é caro). Você roda 01 uma vez, 02
quantas vezes precisar até o mapping ficar certo, 03 só quando estiver
bom.

---

## 6. Schema de configuração por reunião (YAML)

Arquivo `data/configs/reuniao_{data}_{topico_em_snake}.yml`, exemplo:

```yaml
meeting:
  date: 2026-05-04
  topic: "Planejamento Q2"
  context_hint: "Reunião de planejamento trimestral, tom técnico."
  audio_file: "reuniao_2026-05-04_planejamento_q2.m4a"

participants:
  - name: "Bruno"
    role: "Tech lead"
    voice_hint: "voz masculina grave"
  - name: "Ana"
    role: "PM"
    voice_hint: "voz feminina aguda"
  - name: "Carlos"
    role: "Eng senior"
    voice_hint: "voz masculina média"

vocabulary:
  - "WhisperX"
  - "pyannote"
  - "SPEC-001"

speaker_mapping:
  SPEAKER_00: null
  SPEAKER_01: null
  SPEAKER_02: null

ata:
  generate: true
  llm_provider: "anthropic"
```

Convenção: o nome do áudio segue a mesma raiz do arquivo de config,
só muda extensão. Isso permite encontrar config a partir do áudio sem
ambiguidade.

---

## 7. Estrutura do repositório (padrão SERMI)

```
learn-reunioes-pipeline/
├── README.md                          BRIEF (vitrine, mesmo sendo privado)
├── COWORK.md                          instrução para o agente Cowork
├── environment.yml                    ambiente conda
├── .gitignore
│
├── docs/
│   ├── SPEC/
│   │   ├── SPEC_001_Contexto_e_Objetivo.md
│   │   ├── SPEC_002_Glossario_Audio_e_ASR.md
│   │   ├── SPEC_003_Pipeline_Operacional.md
│   │   ├── SPEC_004_Ambiente_Tecnico.md
│   │   ├── SPEC_005_Schema_Config_Reuniao.md
│   │   ├── SPEC_006_Integracao_Cowork.md
│   │   └── SPEC_007_Privacidade_e_Tratamento_de_Dados.md
│   ├── DEC/
│   │   ├── INDEX_DEC.md
│   │   ├── DEC_001_Adocao_WhisperX.md
│   │   ├── DEC_002_Modelo_e_Compute_Type.md
│   │   ├── DEC_003_Condition_on_Previous_Text_False.md
│   │   ├── DEC_004_Saidas_JSON_TXT_SRT.md
│   │   ├── DEC_005_Mapeamento_via_Arquivo_Config.md
│   │   ├── DEC_006_Cowork_Como_Orquestrador.md
│   │   └── DEC_007_LLM_Cloud_para_Ata.md
│   ├── GUIDE/
│   │   └── GUIDE_001_Adicionar_Reuniao_Nova.md
│   └── assets/
│
├── data/
│   ├── audios_pendentes/              inbox (gitignored, .gitkeep)
│   ├── audios_processados/            arquivados (gitignored, .gitkeep)
│   └── configs/
│       ├── prompt_exemplo.txt
│       └── reuniao_template.yml       template de config por reunião
│
├── src/
│   ├── 01_transcrever.py
│   ├── 02_aplicar_mapeamento.py
│   └── 03_gerar_ata.py
│
└── outputs/
    ├── transcricoes/                  {nome_reuniao}.{json,txt,srt}
    └── atas/                          {nome_reuniao}_ata.md
```

### Sobre o padrão SERMI

Taxonomia documental do usuário com cinco tipos:

| Tipo | Função |
|---|---|
| **SPEC** | Descrições estruturais (contexto, glossário, plano analítico, ambiente, narrativa, dados de referência) |
| **DEC** | Decisões com contexto, decisão, alternativas, consequências, critérios de reavaliação |
| **REP** | Relatórios de fechamento (uso ocasional) |
| **GUIDE** | Guias operacionais (uso ocasional) |
| **BRIEF** | Vitrine pública (README) |

Decisões aprovadas são imutáveis. Decisões que mudam dão origem a uma
DEC nova que substitui (supersedes) a anterior. SPECs também: alterações
estruturais são registradas em DECs subsequentes, preservando o
histórico.

---

## 8. Estado atual do projeto

### O que já existe

- **Script `transcrever.py` v1**, 292 linhas, em pasta plana (não SERMI
  ainda). Path: `/mnt/user-data/outputs/transcricao_reunioes/`.
  Contém: CLI argparse, validação de HF_TOKEN com try/except, defaults
  conservadores (`compute_type=int8`, `batch_size=8`, `model=large-v3`),
  detecção automática de GPU, três saídas (JSON, TXT, SRT), logs
  estruturados em inglês, tratamento de erros nas três etapas.
- **README.md** documentando setup conda, configuração de HF_TOKEN,
  uso, trade-offs.
- **requirements.txt** mínimo.
- **prompt_exemplo.txt** mostrando formato do initial_prompt.
- **Mapa de migração** do código atual para o padrão SERMI.
- **Esqueleto do repositório SERMI** (estrutura de pastas, lista de
  SPECs e DECs, schema YAML).

### O que falta

- Criar a estrutura SERMI no repo local (`learn-reunioes-pipeline`),
  ainda vazio.
- Escrever conteúdo das SPECs e DECs.
- Adaptar `transcrever.py` v1 para `src/01_transcrever.py` (path
  novo, mantém lógica).
- Escrever `src/02_aplicar_mapeamento.py` (não existe ainda).
- Escrever `src/03_gerar_ata.py` (não existe ainda).
- Escrever `COWORK.md` na raiz com instrução para o agente.

---

## 9. Plano de execução em quatro ondas

Estratégia: dividir entrega em quatro ondas, validando entre cada uma.

| Onda | O que entrega | Quem executa |
|---|---|---|
| **1. Fundação** | Estrutura de pastas, .gitignore, environment.yml, README rascunho, INDEX_DEC vazio | Cowork (com prompt produzido pelo chat) |
| **2. Documentação** | Conteúdo dos 7 SPECs e 7 DECs | Chat produz, usuário cola manualmente |
| **3. Código** | Adaptação dos três scripts Python | Chat produz, usuário cola manualmente |
| **4. Integração Cowork** | COWORK.md na raiz, com instrução de pasta para o agente | Chat produz, Cowork referencia |

Razão da divisão: Onda 1 é filesystem repetitivo, bom para Cowork.
Ondas 2 e 3 têm conteúdo cognitivo que o usuário quer revisar antes
de gravar. Onda 4 fecha o ciclo com o agente operando o que foi
construído.

---

## 10. Integração com o Cowork

O Cowork é um agente desktop da Anthropic que opera em uma pasta
local do filesystem. Plano de uso:

1. **Cowork como executor de tarefas repetitivas**: criar pastas,
   organizar arquivos, mover áudio de `pendentes/` para `processados/`
   após sucesso do pipeline.
2. **Cowork como gerador de ata** (alternativa ao
   `03_gerar_ata.py`): pode chamar LLM diretamente sem código
   adicional, lendo o JSON nomeado.
3. **Cowork como atualizador de mapeamento**: pode ler o JSON com
   `SPEAKER_XX`, ouvir trechos curtos, sugerir mapping no YAML.
4. **Cowork agendado**: rodar pipeline em cadência fixa (ex:
   segunda-feira de manhã, processar tudo que entrou na semana).

Arquivo `COWORK.md` na raiz do repo é a instrução de pasta que o
agente lê para entender o repositório. Estrutura mínima:

1. Identificação do repo e propósito.
2. Mapa das pastas relevantes.
3. Comportamento esperado quando aparece áudio novo em
   `data/audios_pendentes/`.
4. Comandos exatos para executar o pipeline Python.
5. Como editar/criar YAML de configuração.
6. Restrições: não apagar, não modificar `docs/SPEC/` ou `docs/DEC/`
   (imutáveis no padrão SERMI).

---

## 11. Glossário (didático)

Termos técnicos usados no projeto, em ordem de relevância:

| Termo | Significado |
|---|---|
| **ASR** | Automatic Speech Recognition. Converter áudio em texto. |
| **Whisper** | Modelo de ASR open-source da OpenAI. Multi-idioma. |
| **WhisperX** | Wrapper que combina Whisper + alinhamento + diarização. |
| **Diarização** | Identificar "quem falou quando", separando vozes ao longo do áudio. |
| **pyannote.audio** | Biblioteca Python para diarização, usada pelo WhisperX. |
| **VAD** | Voice Activity Detection. Detectar trechos com voz, ignorar silêncios. |
| **Alinhamento word-level** | Atribuir timestamp preciso a cada palavra (não só ao trecho). |
| **`initial_prompt`** | Texto curto que ancora vocabulário do Whisper para um contexto específico. |
| **`condition_on_previous_text`** | Parâmetro do Whisper que define se o modelo usa o texto anterior como contexto para gerar o próximo. Default True, problemático em PT-BR. |
| **`compute_type`** | Precisão numérica do modelo (`float16`, `int8`, etc). Afeta VRAM e qualidade. |
| **`batch_size`** | Quantos chunks de áudio processar em paralelo na GPU. |
| **RTF** | Real-Time Factor. Tempo de processamento dividido por duração do áudio. RTF=0.3 significa 1h de áudio em 18 min. |
| **HF_TOKEN** | Token de autenticação Hugging Face, necessário para baixar modelos pyannote. |
| **SERMI** | Taxonomia documental pessoal do usuário (SPEC, DEC, REP, GUIDE, BRIEF). |
| **Cowork** | Agente desktop da Anthropic para automação de tarefas em pastas locais. |
| **MCP** | Model Context Protocol. Padrão para conectar LLMs a ferramentas e dados externos. |

---

## 12. O que NÃO fazer neste projeto (limites explícitos)

1. **Não migrar para serviço cloud de transcrição** (AssemblyAI,
   Deepgram). Reuniões podem ter conteúdo sensível, custo de
   privacidade não é trivial. Local com GPU é a escolha consciente.
2. **Não acoplar geração de ata ao script de transcrição**. São
   responsabilidades diferentes. Sumarização de transcrição ruim é
   sumarização errada com aparência de certo (achado inflado).
3. **Não usar embedding de voz pré-cadastrado para mapeamento de
   falantes** no escopo inicial. Complexo, fora de escopo.
4. **Não adicionar dependências sem registro em DEC**. Toda nova
   biblioteca passa por avaliação.
5. **Não trocar Whisper por outro ASR** sem evidência empírica de
   ganho mensurável em PT-BR (TER comparativa em pelo menos 3
   reuniões reais).
6. **Não expor a API pública**. Este é projeto pessoal/profissional,
   não produto.

---

## 13. Próximos passos sugeridos (do ponto onde paramos)

1. **Validar Onda 1**: confirmar com o usuário se inicia pela criação
   da estrutura SERMI vazia no repo `learn-reunioes-pipeline`.
2. **Executar Onda 1**: chat produz pacote (arquivos vazios ou
   mínimos + prompt para Cowork), usuário aciona Cowork ou cola
   manualmente.
3. **Validar Onda 2**: chat redige conteúdo das 7 SPECs e 7 DECs,
   usuário revisa, ajusta e grava.
4. **Validar Onda 3**: chat adapta scripts Python, usuário grava em
   `src/`.
5. **Validar Onda 4**: chat redige `COWORK.md`, usuário grava na
   raiz.
6. **Testar pipeline ponta a ponta** em reunião curta (5 a 10 min)
   antes de usar em reuniões reais.

---

## 14. Perguntas que o assistente pode precisar fazer

Antes de avançar para qualquer etapa, vale o assistente confirmar:

1. **Provider de LLM para a ata**: Anthropic, OpenAI ou Google?
2. **VRAM disponível na GPU**: para decidir entre `int8` e `float16`.
3. **Volume real**: o usuário declarou até 5 reuniões/semana, mas o
   ritmo efetivo afeta priorização da geração de ata.
4. **Sensibilidade do conteúdo**: já marcado como "discussões
   técnicas, planejamento, alinhamento", sem alertas extras. Confirmar
   se há conteúdo de outra natureza (financeiro, jurídico, pessoal)
   antes de qualquer escolha que envolva dados saindo da máquina.

---

*Fim do briefing. Documento mantido como referência viva, atualizar a
cada revisão maior do projeto.*
