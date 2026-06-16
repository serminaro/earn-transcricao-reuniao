# Log de auditoria — gov-check 2026-06-15

Registro da rodada de auditoria de consistência (skill `gov-check`) do projeto
earn-transcricao-reuniao. Cumpre a cláusula "Operação Solo" da SPEC-002 §6: onde
um projeto com equipe teria ata de revisão humana, este projeto registra a
auditoria das regras `R-*`.

- **Data:** 2026-06-15
- **Gatilho:** por marco (fundação documental concluída — Onda 1).
- **Perfil detectado:** solo (4 peças).
- **Escopo:** SPEC-001 (R-TAX-01..10), SPEC-002 (R-FUN-01..08), estado real do repositório.

## Resultado

Passada determinística: **limpa** (0 divergências estruturais/fundacionais).
Passada semântica: **1 divergência (Média)**, resolvida nesta sessão.

### Regras semânticas

| Regra | Sev. | Veredito |
|---|---|---|
| R-TAX-09 privacidade | Crítica | Conforme. Nenhum áudio/output/`.env` rastreado; `.gitignore` cobre os padrões; sem segredos em arquivos versionados. |
| R-FUN-03 sensível fora do Git | Crítica | Conforme. Reforça R-TAX-09. |
| R-FUN-04 sem ASR em nuvem | Crítica | Conforme. Único código versionado usava Whisper local; removido (ver D-01). |
| R-FUN-02 dependência → DEC | Alta | Conforme literal (`environment.yml` = `python` + `pip`). Pendência inversa tratada em D-01. |
| R-FUN-05 ata isolada no 03 | Alta | N/A — scripts `src/01-03` ainda não existem (trabalho de Onda 2/3). |
| R-FUN-01 trio JSON/TXT/SRT | Média | N/A — nenhuma reunião processada em `outputs/transcricoes/`. |
| R-FUN-06 todo C-NN verificável | Média | Conforme. C-01..C-09 com método de verificação; C-08/C-09 provisórios. |

**Nota (não é divergência):** SPEC-002 §4 declara `src/01-03`, que ainda não
existem. Coerente: a SPEC está `proposto` e descreve o compromisso de entrega; o
pipeline é Onda 2/3.

## Divergências e decisões

### D-01 · [Média] — Artefato legado `Transcreve/transcreve_simples.py`

Protótipo do setup Windows committado na fundação (39240a0), contradizendo a
régua e o ambiente-alvo recém-adotado:

- caminhos hardcoded `C:\Users\...` vs ambiente-alvo Linux (commit e21d6ff);
- `openai-whisper`/modelo `medium` vs WhisperX `large-v3` + diarização (SPEC-002 §1, §4);
- saída única `.txt` vs trio JSON/TXT/SRT (§3.1, §4.3);
- diretório top-level `Transcreve/` fora da estrutura declarada (`src/`, `data/`, `outputs/`) (§4.4);
- dependência `openai-whisper` sem DEC nem entrada em `environment.yml` (§3.2, R-FUN-02).

**Decisão do autor:** caminho (b) — corrigir o artefato. Script versionado
removido do Git (`git rm Transcreve/transcreve_simples.py`).

**Ressalva levantada na execução:** o diretório `Transcreve/` no disco também
continha dados locais **nunca versionados** (gitignored): `audio_padrao.m4a` (83 MB,
áudio de reunião real) e `transcricao.txt` (transcrição real). Não foram apagados —
são dados do autor, irreversíveis — e sim relocados para os diretórios canônicos
do pipeline (ambos gitignored):

- `audio_padrao.m4a` → `data/audios_processados/audio_padrao.m4a`;
- `transcricao.txt` → `outputs/transcricoes/audio_padrao.txt`.

Com `Transcreve/` esvaziado e removido, a linha morta `Transcreve/transcricao.txt`
foi retirada do `.gitignore`.

## Estado pós-sessão

- Removido do Git: `Transcreve/transcreve_simples.py`; diretório `Transcreve/` extinto.
- Dados locais preservados nos diretórios canônicos (gitignored): áudio em
  `data/audios_processados/`, transcrição em `outputs/transcricoes/`.
- `.gitignore`: linha morta `Transcreve/transcricao.txt` removida.
- D-01 fechada por completo. Demais regras: conformes ou N/A.
- Próxima auditoria: por calendário (mensal) ou por marco (primeira execução real do pipeline).

## Re-auditoria (mesma data, pós-correção)

Segunda passada da skill `gov-check` na mesma sessão, para confirmar que a
correção de D-01 fechou de fato e não abriu efeito colateral.

- Passada determinística: **limpa**.
- D-01: confirmada fechada (protótipo e dependência `openai-whisper` sumiram juntos; R-FUN-02 conforme).
- R-TAX-09 / R-FUN-03: dados locais relocados confirmados gitignored (`git check-ignore`).

### O-01 · [Baixa] — TXT solitário em `outputs/transcricoes/`

A relocação de D-01 havia posto a transcrição legada em
`outputs/transcricoes/audio_padrao.txt`, um TXT sem o par JSON/SRT. Pela letra da
R-FUN-01 isso lê como reunião meio-processada, embora seja leftover do protótipo,
não saída do pipeline (que ainda não existe).

**Decisão do autor:** caminho (b) — corrigir o artefato. A transcrição legada foi
movida para junto do seu áudio de origem em
`data/audios_processados/audio_padrao.txt` (diretório totalmente gitignored).
`outputs/transcricoes/` voltou a ficar vazio, reservado para saída real do
pipeline. Nenhuma mudança rastreável pelo Git (movimentação entre arquivos
ignorados).

### Veredito da re-auditoria

Auditoria **verde**. Nenhuma divergência aberta. Próxima auditoria: mensal ou por
marco (primeira execução real do pipeline).
