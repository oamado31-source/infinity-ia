# CR-2026-036 — O banco que não trava e o aceite da oferta certa

**Estado:** APROVADA (mantenedor, 2026-11-27: "Aprovar como proposta", D1 a D3 na opção recomendada).

**Origem:** dois problemas vistos nos testes do navio (evidências S2l, S2m e S2n).
- O serviço registrou `OperationalError` duas vezes: uma fala de Bernard e uma rodada das presenças. Nas duas, a operação seguinte funcionou.
- Um "sim" aceitou também o broche de Bernard, oferecido num teste antigo. Os testes passaram a usar só "vamos" e "topamos".

**Relaciona-se com:** SPEC-003 (persistência), ADR-0110 (cópias de segurança), SPEC-011 (quests narrativas), SPEC-013 (autoria de quests) e CR-2026-033 (fatos da quest na fala).

## Mudança

### 1. O banco (`src/infinity_ai/state/store.py`)

**Causa:**
- o diálogo, as presenças e o registro do jogo abrem cada um a sua conexão;
- no modo de diário antigo do SQLite, uma leitura trava as gravações, e as leituras crescem com a campanha;
- passados os 5 s de espera padrão do Python, a gravação desistia ("database is locked").

**Correção:**
- o banco abre em **modo WAL** (leituras e gravações não se bloqueiam);
- a espera pela trava sobe para **30 s** (`timeout` e `busy_timeout`);
- as cópias de segurança (ADR-0110) já usam a cópia do próprio SQLite, que funciona com WAL;
- os arquivos `-wal` e `-shm` ficam ao lado do banco, fora do repositório.
- **O registro do serviço:** passa a mostrar a mensagem dos erros de banco. Outros erros continuam só pelo nome, para nenhum texto do jogador chegar ao log.

### 2. A oferta em foco (`src/infinity_ai/quests/narrative.py`, `offer_in_focus`)

**Causa:**
- cada quest oferecida pelo mesmo NPC conferia sozinha as próprias palavras de aceite;
- o fato de todas as ofertas pendentes ia para a fala dele.

**Correção:**
1. Entre as ofertas do NPC ainda não aceitas, só uma está em foco: **a que o jogador menciona** nesta fala (pelas palavras da oferta) ou, sem menção, **a oferecida mais recentemente** (D2).
2. Só a quest em foco pode ser aceita, e **só o fato dela** vai para a fala (D3).
3. Quando o jogador pede uma oferta nova, nenhuma oferta antiga fica em foco naquela fala.
4. Voltar a mencionar uma oferta antiga a traz de volta ao foco. Nada é registrado de novo.

## Verificação

- **`tests/test_state_store.py`:**
  - o banco abre em WAL;
  - uma leitura em andamento não trava uma gravação;
  - uma gravação espera a outra terminar em vez de falhar.
- **`tests/test_narrative_quests.py`:**
  - com duas ofertas do mesmo NPC, um "sim" aceita só a mais recente;
  - mencionar a antiga a aceita;
  - só o fato da oferta em foco aparece, e a outra continua oferecida.
- A suíte inteira passa. A quest com uma só oferta não muda.
- **No jogo:** evidência própria. Bernard com o broche e uma quest de teste oferecidos; um "sim" aceita só a mais recente; nenhum `OperationalError` na sessão.

## Rollback

Reverter o PR:
- **o banco:** volta ao modo antigo, e o SQLite volta o diário ao abrir;
- **o aceite:** volta a valer para todas as ofertas pendentes.
