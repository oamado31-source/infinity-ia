# ADR-0140 — Contagem no jogo

**Estado:** APROVADA (mantenedor, 2026-11-22: "Aprovar como proposta", decisões D1 a D4 na opção recomendada).

**Origem:** a peça G da quest "O diário perdido de Sarevok". O código precisa perguntar ao jogo quantas criaturas nossas estão numa área, sem mudar nada, por três motivos:
- o registro do ramo pode estar errado depois de um save de outra linha do tempo (S1z, duas vezes);
- o resgate de Gregor só vale quando os carcereiros caíram;
- os verbeegs e os agentes são várias cópias do mesmo arquivo, com o mesmo nome.

**Relaciona-se com:**
- ADR-0136 (gateway e módulo `M_INFAIA.lua`);
- ADR-0138 (presença, item 9);
- ADR-0139 (chegada e ordem dos passos).

**Gate:** etapa 1, single player, save descartável.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-22.

1. **Operação `COUNT` no módulo, só de leitura:**
   - mesmo arquivo de pedido e mesmo nome nosso (`INFAI_*`), na área carregada;
   - responde na hora, `DONE` com a contagem (`observed` e `before` iguais), sem enfileirar nenhuma ação do jogo;
   - área errada: `WRONG_AREA`;
   - **só os vivos contam** (laboratório, 2026-11-22). O seletor do jogo devolve também os corpos: dois camponeses mortos pelo console seguiam contando 2. O módulo tira da conta quem tem o estado de morte do próprio jogo (bit 0x800, a mesma checagem que a caixa já usa), na contagem, na criação e na remoção. A ADR-0136 dizia que o seletor não vê criatura morta, mas isso vinha do teste do `DPMALE`, quando a busca ainda estava quebrada.
2. **A contagem é a palavra do ramo** (`creature_counts`). Vale a última palavra confirmada do jogo para cada nome: depois de um `SPAWN`, um `DESPAWN` ou um `COUNT`. Um ou mais é presente; zero é ausente. `owned_creatures` passa a sair dela.
3. **O diretor conta antes de confiar no ramo (D1):** uma presença que a quest quer é contada quando a palavra do ramo é anterior à última entrada na área, ao último carregamento ou ao último ramo aberto (`AreaEntered`, `SessionStarted`, `BranchForked`). Depois disso:
   - se a contagem diz que falta, ele cria (regra `VERIFY` e depois `ENTER`);
   - se já há, ele não cria.

   Uma criação confirmada é palavra nova e dispensa contar de novo na mesma entrada.
4. **Várias cópias (D2):** `copies` no item de presença, de 1 a 8. O diretor cria uma de cada vez, cada uma confirmada (de N para N+1), até a contagem chegar a `copies`. Um `DESPAWN` remove todas as cópias com aquele nome.
5. **Passo de derrota (D3):** `defeated: {presence}`, uma por presença, e a presença precisa existir na quest. Enquanto a janela da presença está aberta, com a quest aceita, a ordem cumprida e todas as cópias tendo estado lá (`filled`), o diretor conta a cada 90 ticks de jogo (cerca de 6 s), só com o grupo na área (regra `DEFEAT_WATCH`).
   - Contagem zero: o passo é feito (regra `DEFEAT`, sem pedido ao jogo), e a presença não volta.
   - Uma presença com passo de derrota **não é recriada** depois de completa. Uma cópia que cai é baixa, não falta a repor.
   - Quando a quest fecha a janela da presença (o `until`), é remoção (`LEAVE`), nunca derrota.
   - Morte, fuga ou outra saída contam igual: o jogo não distingue para nós.
6. **O diário da derrota** vai na próxima resposta da caixa, como o da chegada (ADR-0139), antes das linhas da própria resposta.
7. **Eventos:** os do gateway, com a operação `COUNT` e a causa (`VERIFY` ou `DEFEAT_WATCH`), mais o passo como `NarrativeQuestStepDone`. Nenhum texto do jogador.
8. **`lab_action.py count`** para o mantenedor conferir, só de leitura.
9. **Instalação:** o módulo novo muda o hash dos mods. Instalar com o jogo fechado (`talk_poc.py --deploy`), fixar o manifesto de novo e reabrir o jogo.

## Consequências

- Fecha o risco da ADR-0138 e da ADR-0139: um save de outra linha não leva mais a uma segunda criatura nem a uma criatura que falta.
- **A quest do diário passa a ter tudo para:**
  - os carcereiros (verbeegs, `copies`), com o passo de derrota antes de Gregor falar;
  - os agentes da célula.
- **Custo:** cada contagem passa pelo arquivo de pedido e pelo log, em cerca de 3 a 4 segundos.

## Verificação

- **`tests/test_actions.py`:** o módulo com motor simulado conta sem enfileirar nada, não conta os corpos e recusa a área errada.
- **`tests/test_quest_count.py`:**
  - o formato estrito de `copies` e `defeated`;
  - a contagem como palavra do ramo;
  - contar antes de confiar: falta, cria; já há, não cria;
  - um save que já tem a criatura não ganha uma segunda;
  - cópias uma a uma, e sem passo de derrota a que falta é reposta;
  - a derrota pela queda a zero, nunca desfeita nem recriada;
  - a quest removendo não é derrota.
- **No jogo:** os sete pontos da proposta, com evidência própria.
