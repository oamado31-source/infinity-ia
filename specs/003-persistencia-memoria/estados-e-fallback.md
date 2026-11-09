# SPEC-003 — Estados, linhagem, falhas e rollback (etapa 1, single player)

**Status:** implementação inicial em `src/infinity_ai/state/` e `src/infinity_ai/memory/`; testes sintéticos e sessão de laboratório single player (ADR-0113). **Nada disso é evidência de multiplayer.**

## Armazenamento

- Um arquivo SQLite por campanha, fora do repositório (padrão `~/.infinity-ai/campaigns/<campaign_id>.sqlite3`). Um banco não aceita outra campanha (Constitution item 5).
- Migrations versionadas em `src/infinity_ai/state/migrations/`, registradas com sha256; migration alterada depois de aplicada impede a abertura do banco.
- **Append-only:** triggers abortam `UPDATE` e `DELETE` em `campaigns`, `branches`, `events`, `npc_experiences`, `belief_revisions` e `belief_revision_sources`. Correção é sempre uma linha nova.
- Idempotência: `events.idempotency_key` e `npc_experiences.idempotency_key` são únicos; repetir a mesma chave com o mesmo conteúdo devolve a linha existente; mesma chave com conteúdo diferente é recusada (`IdempotencyConflict`).
- **Nesta etapa nada `HOST_ONLY` vindo do jogo nem nada `SECRET` é gravado** (sem criptografia em repouso ainda). O gravador só aceita campos `PARTY`.

## O que vira evento (gravador)

| Evento | Categoria (ADR-0059) | Quando |
|---|---|---|
| `SessionStarted` | `RECONCILIATION` | primeira observação utilizável de uma época (load, reabertura do jogo ou do gravador) |
| `BranchForked` | `RECONCILIATION` | no ramo pai, quando uma sessão começa antes do último evento gravado |
| `AreaEntered` | `CAMPAIGN_OBSERVATION` | a área visível muda |
| `PartyChanged` | `CAMPAIGN_OBSERVATION` | a lista de companheiros muda |

Só transições são gravadas; polls sem mudança não geram linhas. Envelope `UNKNOWN`, `BLOCKED_CAPABILITY` ou `DENIED`, evidência `SYNTHETIC` (sem flag explícita), outra campanha, campo não `PARTY` ou épocas misturadas entre os envelopes → **nada é gravado** (REQ-BRIDGE-005: ausência não vira fato).

## Ramos e restauração de save (REQ-STATE-002)

- A bridge não sabe qual save foi carregado; sabe o tempo de jogo da primeira observação da nova época.
- `decide_branch`: se esse tempo é anterior ao último evento gravado no ramo ativo (tolerância de 2 ticks para o recuo de pausa do motor), cria-se um **ramo filho** (`lineage = INFERRED_FROM_ACTIVE`) com `fork_seq` e `fork_game_time`. Caso contrário, a sessão continua no mesmo ramo.
- Um ramo enxerga o próprio histórico e, de cada ancestral, só eventos com `seq ≤ fork_seq` **e** `game_time ≤ fork_game_time` (o limite mais apertado da cadeia). Linhas antigas nunca mudam: deixam de fazer parte da nova linha do tempo.
- Se nada foi gravado depois do ponto do save, um reload **não** cria ramo (nenhum histórico ficou "no futuro").
- Sem tempo observado, a decisão é `UNKNOWN`: nenhum ramo é criado e nada é gravado.
- **Limite conhecido:** carregar um save de um ramo antigo é registrado como filho do ramo ativo (linhagem inferida). Identificar o save exige campo novo.

## Memória de NPC (REQ-MEM-001, REQ-MEM-002)

- Identidade do NPC: `npc:<script name em minúsculas>` lido do jogo; o protagonista (script `None`) é PC e não entra na memória de NPC.
- `NpcExperience` (imutável): só para um evento visível no ramo do NPC, com `game_time` igual ou posterior ao do evento (ninguém aprende o futuro, nem fatos de outra linha do tempo). Canal hoje: `presence:party` (companheiro presente quando o grupo entrou na área ou mudou).
- `BeliefRevision` (append-only): exige ao menos uma experiência do **próprio** NPC disponível naquele momento; precisa estender a cabeça atual da cadeia (`StaleRevision` caso contrário); `authored_by = RULES` (LLM não grava).
- `recall`: finalidade em `narrative_context`/`npc_dialogue`, audiência válida, ramo existente e tempo conhecido; devolve só experiências do NPC, na linhagem, até o tempo pedido, com visibilidade permitida à audiência, e crenças cujas provas também estão visíveis. Resultado vazio significa "nada conhecido", nunca "não aconteceu".

## Falhas e fallback

| Situação | Comportamento |
|---|---|
| Jogo fechado / log parado | bridge `ADAPTER_UNAVAILABLE` → gravador pula; banco intacto |
| Menu principal (sem área) | envelopes `UNKNOWN` → nada gravado |
| Grupo ilegível ou de outra época | `PartyChanged` não é gravado e ninguém é creditado como testemunha |
| Gravador reiniciado na mesma partida | `SessionStarted` novo, sem duplicar área ou grupo (estado reconstruído do banco) |
| Jogo reiniciado (época volta a 0) | comparação por tempo de jogo detecta restauração mesmo com época repetida |
| Banco de outra campanha | abertura recusada |

## Backup e rollback

- `backup()` usa a API de backup do sqlite3 (consistente com o banco aberto) e registra sha256, último `seq` e contagens; `verify_restore()` abre a cópia somente leitura e confere `integrity_check`, hash, contagens e `seq`.
- Rollback de dados: abrir um backup verificado como banco da campanha. Rollback de código: reverter a PR (sem migração destrutiva; o schema só cresce).
