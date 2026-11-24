# ADR-0145 — A chegada preparada

**Estado:** APROVADA (mantenedor, 2026-11-24: "Aprovar como proposta", D1 a D3 na opção recomendada).

**Origem:** o teste da quest "O diário perdido de Sarevok" no casarão das Favelas (AR0409), em 2026-11-24.
- **O que o mantenedor viu:** o grupo entrou e a casa estava vazia; Gregor apareceu depois, e os gigantes depois dele. "Gregor e os carcereiros já têm que estar no local."
- **Por que acontecia:** o diretor só agia depois de saber que o grupo entrou, uma ação por vez, com 8 a 12 s de ida e volta cada:
  1. contar Gregor;
  2. criar Gregor;
  3. contar os carcereiros;
  4. criar os carcereiros.

  Eram 30 a 45 s. O jogo só cria criaturas na área carregada, então não dá para criá-las antes.

**Relaciona-se com:** ADR-0136, ADR-0138, ADR-0139 (chegada), ADR-0140, ADR-0143 e ADR-0144.

**Gate:** etapa 1, single player, save descartável.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-24.

1. **Plano de chegada (D1):**
   - o serviço mantém no override um plano (`INFAIARR.lua`), só com literais validados pelo gateway (`render_arrival_plan`): para cada presença desejada numa área onde o grupo não está, a área, o nosso CRE, o nosso nome, o ponto e quantas cópias devem estar lá;
   - **uma presença que começa ao chegar** (o passo de chegada daquela área, ADR-0139) já entra no plano: os passos de chegada da área contam como feitos ao montar o plano. É o caso de Gregor e dos carcereiros (`cativeiro`) e da célula de Kalessia (`esconderijo`, a área nova IA0001);
   - **na quest do diário de Sarevok** (mantenedor, no teste de 2026-11-24): o plano vale desde o aceite. Gregor e os carcereiros (AR0409) e a célula de Kalessia (área nova IA0001) passam a existir desde que a quest entra no diário, como os NPCs de uma quest do jogo; as chegadas `cativeiro` e `esconderijo` não dependem mais dos passos anteriores;
   - **no jogo:** o módulo vê, a cada quadro, quando a área carregada muda, e espera o líder do grupo estar nela (pelo menos 300 ms e o líder com `m_pArea` na área nova). Se a nova área está no plano, conta e cria no mesmo instante o que falta de cada nome. Se o save já tem, não duplica. Cada entrada responde como um `SPAWN` (nossas e total da área, antes e depois), depois da espera de sempre;
   - **achado no laboratório:** no primeiro teste, o módulo agiu no quadro da troca de área. A contagem viu 1 criatura (o grupo ainda não tinha sido posto), e o `CreateCreature` não criou nada. O serviço reteve as duas presenças (`UNCERTAIN`), como devia. Daí a espera pelo líder;
   - **no serviço:** ao ver o grupo na área, lê essas respostas e as registra como o diretor faria (`record_arrival`). Um `SPAWN` das cópias criadas, ou um `COUNT` quando o save já tinha todas; resposta que não fecha retém a presença. Enquanto espera as respostas (até 12 s), o diretor não cria nada naquela área; sem resposta, ele cria como antes;
   - o plano é regravado só quando muda, e cada entrada vale uma vez (o módulo marca a usada).
2. **Segurança:**
   - cada entrada passa pela validação do `SPAWN` no serviço e de novo no módulo (só `IA*`, só `INFAI_*`, até 8 cópias);
   - o módulo cria só na área da entrada, pelo mesmo modelo de `CreateCreature`;
   - o plano está na lista de arquivos que mudam durante o jogo (`TRANSIENT_OVERRIDE`), como o pedido de ação; `talk_poc.py --deploy` instala o plano vazio.
3. **O texto de Gregor (D2):** o fato do passo `gregor-conta` manda agradecer e dá o lugar: "um galpão nos fundos de uma casa velha no meio das Docas, perto do cais".
4. **O esconderijo (D3):** a casa AR0330, por onde se entra no galpão AR0331, tem três criaturas do jogo ("Ogre", `ICMIN01`); no jogo, o mantenedor viu minotauros. A **AR0318**, tentada em seguida, tem pontos de surgimento de contrabandistas (`RDSMUG`), que atacaram o grupo, e nela nem o plano nem o diretor criaram a célula. As outras salas livres das Docas são do Thief Stronghold (AR0321 a AR0324), do Shadow Thief Stronghold (AR0328) ou de outra história (AR0304), e o BG2 não tem área do Trono de Ferro em Athkatla. O esconderijo passa para uma **área nova, `IA0001`** (CR-2026-034); até ela existir, a quest para nesse passo. Gregor fala de "um galpão vazio no norte das Docas".

## Consequências

- Quem a quest põe num lugar já está lá quando o grupo entra.
- O diretor continua com hostilidade, derrota, saída e remoção, e cria como antes quando não há plano (o grupo já estava na área quando o passo aconteceu).

## Verificação

- **`tests/test_actions.py`:** o módulo, com motor simulado, cumpre o plano ao carregar a área (cria só o que falta), responde como `SPAWN`, não repete ao reentrar e recusa nome que não é nosso.
- **`tests/test_quest_sarevok.py`:** depois da visão, o plano para a AR0409 traz Gregor e os dois carcereiros; as respostas do módulo viram `ENTER` confirmados, e o diretor não cria nada de novo.
- **No jogo:** evidência própria.
