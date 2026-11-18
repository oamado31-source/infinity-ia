# ADR-0136 — Portão P3: a primeira escrita reversível no jogo

**Estado:** APROVADA (mantenedor, 2026-11-18: "Aprovar como proposta", decisões D1 a D5 na primeira opção).

**Origem:** o mantenedor definiu como primeiro grande objetivo do projeto as quests novas com personagens, criaturas e heróis que não existem no BG2, trazidos de outros jogos ou criados a partir das fichas disponíveis. Para alguém estar de fato no mapa, o projeto precisa escrever no jogo. Até aqui o laboratório só lia (P0 a P2).

**Relaciona-se com:**
- doc. 07 (P3: "ação permitida e reversível", com o estado anterior e o posterior);
- doc. 26 e ADR-0022 (DEC-012, gateway de ações seguras);
- doc. 73 e ADR-0068 (limpeza só do que é nosso); ADR-0094 (propriedade por instância);
- SPEC-011 e SPEC-012 (quests e enciclopédia, que vão usar isto).

**Gate:** etapa 1, single player, save descartável. Multiplayer (P4) fora.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-18.

1. **O P3 prova uma coisa só (D1):** criar e remover uma criatura que já existe no BG2, num save descartável, com o antes e o depois registrados.
2. **Gateway mínimo** (`actions/gateway.py`):
   - operações permitidas: `SPAWN_CREATURE` (um arquivo de criatura nosso, área, ponto ou perto do líder, direção) e `DESPAWN` (só criatura nossa);
   - o código valida cada campo e recusa antes do jogo, com um código (`UNKNOWN_CRE`, `BAD_POINT`, `NOT_OURS`, `NOT_OWNED`…);
   - estados do doc. 26: `HOST_CONFIRMED`, `DENIED` ou `UNCERTAIN`. Sem a palavra do jogo nada conta como feito, e nada é reenviado às cegas.
3. **Só o mantenedor dispara no P3 (D2):** `tools/windows-lab/lab_action.py spawn|despawn|owned`. Nem o modelo de linguagem, nem a quest, nem a caixa.
4. **Módulo próprio (D3):** `M_INFAIA.lua`, com o menu oculto `INFAIAM.menu`, separado da caixa de diálogo, que continua só de leitura.
   - Relê `override/INFAIACT.lua` (literais validados, como a resposta da caixa) a cada meio segundo.
   - Monta a ação de um modelo fixo: `CreateCreature("<CRE nosso>",[x.y],<dir>)` no líder do grupo, ou `DestroySelf()` na criatura nossa.
   - Responde no log com `INFAI-ACT {…}`: `ACCEPTED` ao enfileirar e `DONE`, com quantas criaturas com o nosso nome a área tinha antes e tem depois. Uma a mais (criar) ou nenhuma (remover) é a confirmação do host.
   - O mesmo `action_id` nunca roda duas vezes na mesma execução do jogo. O arquivo de pedido volta a vazio depois de cada ação.
5. **Propriedade nos nossos arquivos (correção do laboratório, S1x):**
   - no BG2:EE, `CreateCreature` não recebe nome de script (`ACTION.IDS`: criatura, ponto, direção). A primeira versão passava um quarto argumento, e o jogo descartou a ação sem aviso; o gateway ficou em `UNCERTAIN`, como devia;
   - o nome nosso vai dentro do arquivo da criatura: `build_templates.py` copia um CRE da build com um resref nosso (`IA*`) e grava no campo de nome de script um nome nosso (`INFAI_*`);
   - esses arquivos são dados do jogo: vão só para o override da VM e para um registro local (`~/.infinity-ai/templates/`), nunca para o repositório (CR-2026-030);
   - como o motor só acha arquivos do override presentes na abertura, eles são instalados com o jogo fechado, e o manifesto é fixado de novo;
   - `SPAWN` só aceita os nossos arquivos instalados; `DESPAWN` só aceita nomes `INFAI_` e remove as criaturas com esse nome na área. Nada do jogo original é tocado.
6. **Eventos por ramo:** `GameActionRequested`, `GameActionConfirmed` e `GameActionFailed`, sempre com o tempo de jogo, lido no probe; o gateway recusa ação sem ele (`NO_GAME_TIME`). A lista das nossas criaturas presentes sai do ramo e ignora registro sem tempo: um save antigo recarregado não as tem (S1x: sem o tempo, o ramo do save antigo herdava a criatura).
7. **Criatura do teste (D4):** um camponês genérico e vivo do BG2 (`MTOWN6`), copiado como `IAP3TEST`, com o nome `INFAI_P3TEST`.
   - A primeira escolha, `DPMALE`, é um corpo do cerco de Saradush, gravado como morto. O jogo o criou deitado, e a contagem não o achou, porque o seletor do jogo não vê criaturas mortas; o gateway ficou em `UNCERTAIN`, como devia (S1x).
   - Desde então, `build_templates.py` recusa como modelo uma criatura gravada em estado de morte (`DEAD_SOURCE_CRE`).
   - Com o camponês vivo (`MTOWN6`), a criatura apareceu e conversou, e a caixa mostrou o nome `INFAI_P3TEST`. A contagem ainda dava zero: o EEex trata o argumento de linha de visão como `bCheckForLineOfSight or 1`, e `false` a ligava, a partir do canto do mapa. O módulo passa `0`, que desliga a checagem; um teste estático impede o `false`.
   - O raio de busca do motor é de 16 bits com sinal: 65535 virava -1. O módulo usa 30000, espera 3 segundos antes de contar e informa quantas criaturas a busca viu ao todo (`seen`), para separar busca quebrada de criatura ausente.
8. **O depois (D5):** o P3b gera uma criatura nova a partir de uma ficha curada, começando por um vilão de BG1 que pode ter sobrevivido, consultado na TH.GL por entidade (CR-2026-030).

## Consequências

- O arquivo de pedido (`INFAIACT.lua`) é transitório e não muda o hash dos mods. O módulo e o menu novos mudam, e a instalação pede manifesto fixado de novo.
- `talk_poc.py --deploy` passa a copiar o módulo, o menu e o pedido vazio.
- Quests com presença (SPEC-011), heróis que conversam e criaturas de outros jogos passam a depender deste gateway, com a criação decidida por código e a limpeza no fim.

## Verificação

- **`tests/test_actions.py`:**
  - validação e recusas do gateway, nome nosso, pedido sem injeção e recibos estritos;
  - só `DONE` com a criatura presente confirma a criação, e só `DONE` com zero confirma a remoção;
  - propriedade por ramo;
  - o módulo Lua com motor simulado: cria, confirma, não repete, remove, recusa nome alheio, área errada e criatura ausente;
  - só funções do motor permitidas, ações de modelo fixo, nenhuma atribuição ao motor.
- **No jogo (S1x):** os sete pontos da proposta. O gateway recusou os pedidos inválidos antes do jogo, e o módulo recusou a área errada com o jogo aberto.
