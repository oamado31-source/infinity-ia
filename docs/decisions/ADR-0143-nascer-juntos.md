# ADR-0143 — Nascer juntos

**Estado:** APROVADA (mantenedor, 2026-11-23: "Aprovar como proposta", decisões D1 a D4 na opção recomendada).

**Origem:** a evidência S2d (ADR-0142) registrou dois problemas.
- **Cópias criadas uma a uma no meio da luta.** O diretor pedia uma cópia por ciclo, com cerca de 14 s entre elas. O primeiro carcereiro nasceu hostil e a luta começou. O 2º pedido não criou ninguém (o total da área ficou em 46), mas saiu confirmado, porque o 1º carcereiro não foi contado no instante do pedido ("antes 0, depois 1").
- **Hostilidade uma presença por vez.** Os agentes ficaram hostis 25 s depois de Kalessia, porque o diretor vigiou a derrota dela antes.

**Relaciona-se com:** ADR-0136 (gateway), ADR-0138 (presença), ADR-0140 (contagem e cópias) e ADR-0142 (combate).

**Gate:** etapa 1, single player, save descartável.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-23.

1. **Cópias num pedido só (D1):**
   - o `SPAWN_CREATURE` ganha `count`, de 1 a 8, o mesmo limite de `copies`. Só a criação o aceita; nas outras operações, `count` é 1;
   - o diretor pede de uma vez as cópias que faltam (`copies` menos a contagem);
   - o módulo executa os `CreateCreature` no mesmo instante, um por cópia. Os pontos seguem um modelo fixo: o ponto do pedido, ou perto do líder, com 40 pixels para o lado a cada cópia.
2. **Dupla contagem (D2):**
   - o módulo informa o total de criaturas da área antes e depois (`seen_before` e `seen`);
   - a criação vale (`HOST_CONFIRMED`) só quando as nossas com o nome **e** o total da área sobem exatamente `count`. Um recibo sem os totais não confirma;
   - se algo mais entra na área nos 3 s (uma invocação, por exemplo), o pedido fica `UNCERTAIN` e a presença é retida, como na ADR-0138: o mantenedor olha e retoma;
   - os totais vão para o evento confirmado, para investigar uma contagem estranha.
3. **Hostilidade antes da vigia (D3):** na decisão do diretor, a regra `HOSTILE` de qualquer presença da área vem antes das outras regras. Quando um passo deixa várias presenças hostis, os pedidos saem em ciclos seguidos, antes de qualquer contagem.
4. **Sem mudança no resto:**
   - continua uma ação por vez, e um pedido não confirmado retém a presença;
   - nunca se recria depois que todas as cópias estiveram no mapa (ADR-0140);
   - `lab_action.py spawn --count N`, para o mantenedor conferir.
5. **Teste (D4):** a quest local `teste-combate` numa linha nova de saves, e um pedido de 3 cópias pelo `lab_action.py`.

## Consequências

- A criação de várias cópias não depende mais de o jogo estar calmo entre um ciclo e outro.
- Uma confirmação falsa como a da S2d passa a reter a presença em vez de valer.
- **Fora:** descobrir por que o 1º carcereiro não foi contado naquele instante. Os totais registrados ajudam se acontecer de novo.

## Verificação

- **`tests/test_actions.py`:**
  - `count` validado (1 a 8, só na criação) e escrito no pedido;
  - os totais lidos do recibo com rigor;
  - a confirmação exige as duas contagens subindo exatamente `count`, e recusa o caso da S2d;
  - o módulo, com motor simulado, cria 3 cópias no mesmo instante, um passo ao lado a cada uma, e recusa `count` acima do limite.
- **`tests/test_combat.py`:**
  - 3 guardas num pedido só;
  - o líder e os guardas ficam hostis em ciclos seguidos, antes de qualquer vigia;
  - um recibo em que o total da área não sobe retém as presenças, sem pedir de novo.
- **No jogo:** evidência própria.
