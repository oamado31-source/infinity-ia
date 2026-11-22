# ADR-0138 — Presença decidida pela quest

**Estado:** APROVADA (mantenedor, 2026-11-18: "Aprovar como proposta", decisões D1 a D4 na opção recomendada).

**Origem:**
- A quest "O diário perdido de Sarevok" (SPEC-011, segundo corte, v4 aprovada) põe três grupos no mapa por decisão do código:
  - a visão de Tamoko no Cemitério;
  - Gregor e os carcereiros nas Favelas;
  - Kalessia e os agentes nas Docas.
- Até aqui só o mantenedor criava ou removia uma criatura nossa (ADR-0136, D2). Esta é a peça A da quest.

**Relaciona-se com:**
- ADR-0136 (gateway, `HOST_CONFIRMED`, propriedade por ramo);
- ADR-0137 (criaturas de ficha, `IATAMOKO`);
- ADR-0135 e SPEC-011 (quests narrativas: estado por ramo, o código decide);
- doc. 26 (DEC-012: nada é reenviado às cegas);
- ADR-0107 (eventos sem o texto do jogador).

**Gate:** etapa 1, single player, save descartável.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-18.

1. **A quest declara a presença como conteúdo curado.** O arquivo da quest ganha `presence`, opcional: uma lista de itens com:
   - `presence_id`;
   - `cre` (um arquivo de criatura nosso, `IA*`) e `name` (o nome dentro dele, `INFAI_*`);
   - `area`;
   - `from` (`ACCEPTED`, o padrão, ou um passo da quest) e `until` (`RESOLVED`, o padrão, ou um passo);
   - opcionalmente `x`, `y` e `facing`.

   Qualquer campo estranho derruba a quest inteira, como o resto do formato. A condição "à noite" é da peça B e entra no mesmo campo depois.
2. **O diretor de presença** (`quests/presence.py`) compara, a cada leitura do jogo, o que a quest quer com o que o ramo tem:
   - **deve estar e não está**, e o grupo está na área: `SPAWN` pelo gateway (regra `ENTER`);
   - **não deve mais estar, e foi a quest que a pôs ali**, com o grupo na área: `DESPAWN` (regra `LEAVE`). O jogo só remove na área carregada. Uma criatura posta pelo mantenedor nunca é removida pela quest;
   - **o grupo fora da área:** nada. A criatura que ficou lá continua no save.
3. **Uma ação por vez, nunca às cegas (D3):**
   - o que o jogo não confirma (`DENIED` ou `UNCERTAIN`) suspende aquela presença no ramo (`QuestPresenceSuspended`), e o serviço avisa no log;
   - um pedido gravado sem resposta (o serviço parou no meio) também a retém;
   - a presença só volta a agir quando o mantenedor, depois de olhar o jogo, a libera: `lab_action.py resume --quest … --presence …` (`QuestPresenceResumed`);
   - o gateway recusa antes do jogo, e também suspende, o arquivo de criatura que não está instalado (`UNKNOWN_TEMPLATE`) ou que guarda outro nome (`TEMPLATE_NAME_MISMATCH`);
   - a única exceção é a recusa do módulo por área errada (`WRONG_AREA`): o módulo não fez nada, o grupo tinha acabado de sair, e a presença volta a agir na próxima entrada.
4. **Quem dispara (D1, muda a D2 da ADR-0136):**
   - o código da quest, pelo diretor, e o mantenedor, como antes;
   - nunca o modelo de linguagem nem o texto do jogador. A fala só faz a quest avançar pelas regras que já existem (ADR-0135), e é o avanço que muda o que deve estar no mapa.
5. **Desligado por padrão:** o serviço do laboratório só cria a thread do diretor com `--quest-presence`.
6. **Eventos:**
   - os da ADR-0136 (`GameActionRequested`, `GameActionConfirmed`, `GameActionFailed`) levam a causa: a política, a quest, a presença e a regra;
   - mais `QuestPresenceSuspended` e `QuestPresenceResumed`;
   - nenhum guarda texto do jogador.
7. **Onde aparece (D2):** perto do líder ao entrar na área, como no P3. O ponto fixo é opcional e pode ser curado quando o mantenedor souber o lugar.
8. **Recarregar o save:**
   - um save de antes da criação abre um ramo sem a criatura, e o diretor a cria de novo se a quest a quiser ali;
   - um save que já a tem está num ramo que a registra, e nada se repete (como no S1x).
9. **O registro pode estar errado depois de um save de outra linha do tempo** (laboratório, 2026-11-22):
   - o ramo admite os eventos do ramo pai até o tempo de jogo do save. Um save de outra linha do tempo, com tempo posterior ao de uma criação, herda o registro de uma criatura que ele não tem. O diretor então não a cria;
   - a contagem do jogo corrige: o `despawn` do mantenedor recebe do módulo `NOT_FOUND` com contagem 0 (o módulo só conta na área certa), e isso passa a valer como confirmação de que não sobrou nenhuma (`HOST_CONFIRMED`). Na leitura seguinte, o diretor a cria;
   - **o mesmo vale ao carregar um save posterior de outra linha:** o serviço só abre ramo quando o tempo de jogo volta. Um save de outra linha, com tempo maior, passa por continuação do ramo atual (laboratório, 2026-11-22: o save do ponto 3, carregado depois do ANTES-ACEITAR). O diretor só age pelo que o ramo acredita. Nesse estado trocado, aceitar a quest de novo criaria uma segunda criatura, e o jogo confirmaria (de 1 para 2);
   - a verificação automática, ao entrar na área e antes de criar, precisa de uma operação de contagem no módulo: se já houver uma, o diretor só registra. Ela entra com a peça G (carcereiros derrotados), que também conta. Até lá, no laboratório, cada rodada de teste corre numa linha só de saves.
10. **Quest de teste (D4):** só local, fora do repositório (`--local-quests`), na Coroa de Cobre, com Bernard e a visão de Tamoko. Uma quest local nunca substitui uma do repositório com o mesmo id.

## Consequências

- **O pedido ao jogo é o mesmo arquivo do P3** (`INFAIACT.lua`). Com `--quest-presence` ligado, o mantenedor não usa `lab_action.py spawn|despawn` ao mesmo tempo; `owned` e `resume` continuam livres.
- **As peças seguintes usam o mesmo campo:** B ("à noite", objetivos de área), D (inimigos hostis) e G (carcereiros derrotados).
- **Multiplayer (P4):** fora.

## Verificação

- **`tests/test_quest_presence.py`:**
  - o formato estrito e os dois pontos de cada presença;
  - aceitar cria, sair e voltar não repete, resolver remove;
  - a causa vai nos eventos, sem texto do jogador;
  - o save anterior segue o seu ramo;
  - o que o jogo não confirma suspende até ser liberado;
  - arquivo ausente suspende antes do jogo;
  - pedido sem resposta retém; área errada não suspende;
  - o que o mantenedor pôs nunca é removido pela quest.
  - um save de outra linha do tempo é corrigido pela contagem do jogo (`NOT_FOUND` com contagem 0), e a quest volta a criar.
- **No jogo:** os sete pontos da proposta, com evidência própria.
