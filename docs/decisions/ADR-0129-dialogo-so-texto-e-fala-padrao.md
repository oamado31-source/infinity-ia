# ADR-0129 — Diálogo só em texto e fala padrão do jogo ao abrir a caixa

**Estado:** APROVADA (plano aprovado pelo mantenedor, 2026-11-15). Substitui o [ADR-0128](ADR-0128-voz-dos-npcs-tts-local.md).
**Origem:** as vozes sintetizadas em português (ADR-0128) puxavam para o sotaque de Portugal ou para o inglês, e isso incomodou o mantenedor. No jogo original, o diálogo é escrito, e a criatura só diz falas curtas do próprio conjunto de sons.
**Relaciona-se com:** ADR-0107 (política de voz), ADR-0116 (caixa no jogo), ADR-0127 (voz do jogador), SPEC-004 (REQ-VOICE-003 e 004) e REQ-CANON-004.
**Gate:** etapa 1, single player. Nada é escrito no estado do jogo.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-15.

1. **Diálogo só escrito:** a resposta do NPC aparece em português na caixa, sem voz sintetizada. O REQ-VOICE-003 fica atendido pelo texto, e o áudio continua opcional, como diz a SPEC-004.
2. **Voz do jogador mantida:** o botão Falar continua transcrevendo a fala para o campo de texto, para revisão, como no ADR-0127.
3. **Fala padrão ao abrir a caixa:** no clique direito ou no F9, a criatura diz uma fala do próprio conjunto de sons, como no clique esquerdo do jogo.
   - **Companheiro:** sorteia uma das falas de seleção (`SELECT_COMMON1..6`).
   - **Outros:** uma fala de seleção ou, sem ela, a de primeiro encontro (`INITIAL_MEETING`).
   - **Slots:** são achados pelo nome em `SNDSLOT.IDS` do próprio jogo, que guarda as posições na ficha (`EEex_Resource_LoadIDS`), sem números fixos no código. O `SOUNDOFF.IDS` só entra para um nome que falte no `SNDSLOT.IDS`. Ele é a tabela do `VerbalConstant`, com números diferentes: usá-lo deixou os companheiros sem fala no primeiro teste. O primeiro encontro coincidia por ser o slot 0 nas duas tabelas.
   - **O strref:** vem do cabeçalho da ficha (`m_baseStats.m_speech`).
   - **Como toca:** `EEex_Sprite_DisplayTextRef(..., {overHead = true})` põe uma mensagem na fila do motor. O jogo toca o próprio áudio e mostra o próprio texto sobre a cabeça.
   - **Silêncio:** criatura morta, sem fala no conjunto de sons ou com leitura falha (tudo em `pcall`).
4. **O que a fala padrão não faz:**
   - não põe ação na fila da criatura nem mexe em variável, diálogo, diário ou save;
   - nenhum áudio ou texto do jogo sai do motor, é copiado para o repositório ou é analisado (REQ-CANON-004);
   - a caixa só passa o strref, que o próprio jogo resolve.
5. **Latência mantida:** as melhorias da evidência S1i continuam. São elas o PowerShell permanente na VM, a leitura incremental do log, o `whisper-server`, a lista de microfones guardada, as regras fixas no início do prompt e o `keep_alive`.

## Consequências

- **Código:**
  - `tools/eeex-probe/M_INFAIT.lua`: `infai_greet`, `infai_sound_slot`, `infai_strref` e a referência ao objeto da criatura, que nunca vai para o JSON;
  - remoção do TTS (veja o ADR-0128).
- **Testes:** `tests/test_talk.py`.
  - A allowlist ganhou `EEex_Resource_LoadIDS`, `EEex_Resource_IterateUnpackedIDSEntries` e `EEex_Sprite_DisplayTextRef`.
  - Com `lupa`: companheiro diz fala de seleção; outro cai na de primeiro encontro; morto, sem fala ou protagonista ficam em silêncio; o objeto não entra no pedido.
- **Laboratório:** com `INFAI_TALK_DEBUG`, o log registra `fala padrao: N opcoes (...)`, sem texto. Quando não há fala, registra as posições preenchidas e o índice de cada nome, só com números. O nome do campo e o som com o jogo pausado foram conferidos na build pinada (evidência S1j).

## Riscos e limites

- **Falas de diálogo dos plebeus:** muitos plebeus dizem a fala curta do clique esquerdo pelo arquivo de diálogo deles, não pelo conjunto de sons. Esses ficam em silêncio por decisão do mantenedor.
- **Campo do EEex:** se `m_speech` mudar numa versão futura, a leitura falha dentro de `pcall`, e só a fala padrão se perde. A caixa continua funcionando.
