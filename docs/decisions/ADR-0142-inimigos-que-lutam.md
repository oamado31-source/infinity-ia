# ADR-0142 — Inimigos que lutam

**Estado:** APROVADA (mantenedor, 2026-11-23: "Aprovar como proposta", decisões D1 a D4 na opção recomendada).

**Origem:** a peça D da quest "O diário perdido de Sarevok". A quest tem duas lutas:
- nas Favelas, contra os carcereiros que guardam Gregor;
- nas Docas, contra a célula de Kalessia, depois de uma conversa de intimidação.

Até aqui nossas criaturas eram neutras, sem script e sem magias (ADR-0137).

**Relaciona-se com:**
- ADR-0136 (gateway e módulo), ADR-0138 (presença) e ADR-0140 (contagem e derrota);
- ADR-0137 e ADR-0141 (gerador e fichas).

**Gate:** etapa 1, single player, save descartável.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-23.

1. **Combate com o que o jogo já tem** (gerador):
   - a ficha local ganha `scripts` (por espaço: `override`, `class`, `race`, `general`, `default`, com nomes de BCS da build) e `spells` (resref e quantidade memorizada);
   - o gerador grava os scripts nos espaços da CRE, as magias na tabela de conhecidas e na de memorizadas, e atualiza as entradas de memorização do corpo (quantas por nível e onde começam). Sem magias, as entradas ficam com nível e tipo, e sem contagem;
   - `build_templates.py` lê o tipo e o nível de cada magia no próprio SPL e recusa script ou magia que não está na build (`UNKNOWN_SPELL`, `NO_SPELL_SLOT`);
   - nada de BAF nosso: os scripts são os genéricos que os inimigos do jogo usam, como `WTASIGHT` (atacar ao ver), `GPSHOUT` (chamar o grupo) e os de mago por nível (`MAGE5`…).
2. **Nascer hostil (D1):** `build_templates.py --hostile` grava a criatura já inimiga (EA 255). Os **carcereiros** nascem hostis: quando o grupo chega ao cativeiro, a luta começa.
3. **Ficar hostil por decisão da quest (D1):**
   - operação nova do gateway, **`SET_HOSTILE`**: o módulo executa `Enemy()` (ação do próprio jogo, de modelo fixo) em cada criatura **viva** com aquele nome nosso, na área carregada;
   - depois de 3 segundos, o módulo conta as vivas (`before`) e as hostis (`observed`, aliança de 200 para cima, lida no EEex). O pedido vale (`HOST_CONFIRMED`) quando todas as vivas são hostis;
   - a presença ganha `hostile_from` (`ACCEPTED` ou um passo). Quando o ponto é atingido e todas as cópias estão no mapa, o diretor pede `SET_HOSTILE` (regra `HOSTILE`), uma vez por criação;
   - atacar uma criatura neutra continua a torná-la hostil pelo próprio jogo.
4. **Ações na hora, sem fila (laboratório):**
   - `CreateCreature`, `Enemy()` e `DestroySelf()` estão no `INSTANT.IDS` da build. O módulo as executa na hora pelo EEex (`EEex_Action_ExecuteResponseStringOnAIBaseInstantly`), em vez de pô-las na fila de quem age;
   - **motivo:** no teste, o primeiro carcereiro nasceu hostil, o jogo pausou e o grupo entrou em combate. O segundo `CreateCreature`, na fila do líder, se perdeu, e o diretor reteve a presença (`UNCERTAIN`), como devia.
5. **Segurança:**
   - `SET_HOSTILE` só aceita nomes nossos (`INFAI_*`) que o ramo conhece, como o `DESPAWN`, e nunca muda o lado de alguém do jogo;
   - não há volta para neutro nesta peça;
   - um teste estático garante `Enemy()` uma vez só no módulo, e nenhuma outra ação de aliança;
   - `lab_action.py hostile` serve para o mantenedor conferir.
6. **As criaturas da quest (D2, D3):**
   - **Kalessia:** `MAGE5`, `GPSHOUT` e `WTASIGHT`, com as magias dela do BG1 memorizadas (Imagem Espelhada, 2 Horror e 2 Míssil Mágico);
   - **os agentes:** "Guarda do Trono de Ferro", com os números de um bandido guerreiro do BG2, `WTASIGHT` e `GPSHOUT`, em cópias;
   - **os carcereiros:** a ficha do verbeeg com `WTASIGHT` e `GPSHOUT`, nascidos hostis.
7. **Teste (D4):** quest local nas Favelas, numa linha só de saves.

## Consequências

- A quest "O diário perdido de Sarevok" tem todas as peças (A a G).
- O XP e o ouro das lutas vêm das próprias criaturas (D6 da quest).
- **Volta para neutro e combate em multiplayer:** fora.
- **Criar cópias durante o combate não é confiável** (evidência S2d): o diretor completa o grupo no ciclo seguinte, mas uma criação pode sair com confirmação falsa. A correção ("nascer juntos") fica para uma decisão própria.

## Verificação

- **`tests/test_combat.py`:**
  - os scripts nos espaços certos;
  - as magias nas tabelas de conhecidas e memorizadas, e as entradas de memorização por nível;
  - o lado (neutro ou inimigo) na criação;
  - fichas com script ou magia ruins são recusadas;
  - magia desconhecida da build e corpo sem espaço para o nível são recusados;
  - a célula fica hostil no passo da quest, uma vez só.
- **`tests/test_actions.py`:**
  - o módulo, com motor simulado, executa `Enemy()` só nas nossas, nunca em Bernard, e não usa fila;
  - conta vivas e hostis;
  - confirma só quando todas viraram;
  - recusa nome ausente e nome do jogo.
- **No jogo:** os sete pontos da proposta, com evidência própria.
