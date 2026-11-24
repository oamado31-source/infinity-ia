# ADR-0144 — O chamado sobre a cabeça e a saída pela porta

**Estado:** APROVADA (mantenedor, 2026-11-24: "Aprovar como proposta", D2 a D4 na opção recomendada; D1 revista para a frase 102877).

**Origem:** a montagem da quest "O diário perdido de Sarevok", aprovada em 2026-11-24, pediu duas coisas:
- **D1:** Garoll oferece a quest sozinho, com uma legenda sobre a cabeça pedindo ajuda, como em outras quests do jogo;
- **D3:** Gregor, depois de contar, anda até a porta do casarão e some ali, como se tivesse saído.

**Relaciona-se com:**
- ADR-0136 (gateway e módulo) e ADR-0138 (presença);
- ADR-0142 e ADR-0143 (ações na hora e cópias);
- SPEC-011 (quests narrativas).

**Gate:** etapa 1, single player, save descartável.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-24.

1. **Operação `CALL`, só exibição (D1, D2):**
   - o módulo mostra sobre a cabeça de uma criatura do jogo uma frase do `dialog.tlk`, pela mensagem que o jogo usa nas falas de ambiente (`EEex_Sprite_DisplayTextRef`, com `overHead`). Nada muda no jogo nem no save;
   - a frase de Garoll é a **102877, "Alguém pode me ajudar?!"**, sem voz. A 4167, recomendada antes, traz a voz de Quayle, e a função do EEex não deixa desligar o som (`playSound or true` é sempre verdadeiro). O mantenedor escolheu uma frase sem voz em vez de o módulo montar a mensagem campo a campo;
   - a quest declara o chamado: `call: {script_name, area, strref, every}`. O gateway só aceita o par (nome de script, strref) que uma quest curada declara, e nunca um nome nosso;
   - o diretor pede o chamado com o grupo na área de quem oferece, ao entrar e depois a cada `every` ticks (1500, cerca de 100 s), só enquanto a quest não foi aceita;
   - nada é retido: sem a criatura (`NOT_FOUND`) ou sem resposta, o chamado só tenta de novo na vez seguinte. O chamado não entra na contagem das nossas.
2. **Operação `ESCAPE` (D3):**
   - o módulo enfileira `EscapeArea()`, ação do próprio jogo, de modelo fixo, nas criaturas vivas com aquele nome nosso;
   - elas andam até a saída mais próxima e somem ao chegar, sem passar para outra área;
   - a ação não é instantânea (a criatura anda), então vai na fila da própria criatura, nossa e fora de combate. É a única ação enfileirada do módulo;
   - o módulo conta a cada segundo, por até 30 s, e o pedido vale quando a contagem chega a zero;
   - a presença ganha `leave`: `DESPAWN` (o padrão) ou `ESCAPE`. Quando a janela fecha com o grupo na área, o diretor pede a saída escolhida (regra `LEAVE`);
   - só nomes nossos que o ramo conhece, como o `DESPAWN`.
3. **Vários passos de conversa para a mesma pessoa** (achado da montagem):
   - na quest, Tamoko tem dois passos (`visao` e `descanso`), e o formato aceitava um só por pessoa;
   - agora aceita vários quando cada passo seguinte vem depois do anterior pelo `after`, direto ou não. Assim só um passo da pessoa fica aberto de cada vez;
   - a pessoa responde pelo passo aberto quando o jogador diz as palavras dele; senão, repete o último fato que já contou.
4. **Segurança:**
   - `CALL` é a primeira operação sobre uma criatura do jogo e só exibe. Um teste estático garante uma chamada só de `EEex_Sprite_DisplayTextRef`, com `{ overHead = true }` e nada mais;
   - `EscapeArea()` aparece uma vez só, e é a única ação na fila;
   - `lab_action.py call` e `lab_action.py escape` servem para o mantenedor conferir.
5. **A quest:** `knowledge/quests/sarevok-diary.pt_BR.json`, com as curadorias revistas de Garoll (coveiro; o marco o deixa `INTIMO`) e de Tamoko (quem a matou fica só no passo `visao`).
   - **O cativeiro é a AR0409**, uma casa vazia das Favelas (nenhum NPC, script de área vazio), com a porta no norte do mapa. A AR0416 da proposta v4 fica dentro da AR0415, que se entra pelas Docas e tem NPC e script; o mantenedor escolheu a AR0409 em 2026-11-24;
   - o esconderijo segue na AR0331 (Docas, pela AR0330, sem script).

## Consequências

- A quest "O diário perdido de Sarevok" está montada, com todas as peças.
- Uma quest pode chamar o grupo como as do jogo, só com frases que a build já tem.
- **Fora:** texto livre sobre a cabeça (o EEex só mostra frases do `dialog.tlk`) e falas de ambiente para outros NPCs.

## Verificação

- **`tests/test_actions.py`:**
  - `CALL` só para o par declarado, nunca um nome nosso; `ESCAPE` só para as nossas do ramo;
  - as confirmações; uma saída confirmada zera a contagem;
  - o módulo, com motor simulado, mostra a frase só sobre quem oferece, sem outra ação;
  - recusa nome nosso no `CALL`;
  - enfileira `EscapeArea()` e confirma quando ninguém sobra, ou responde no prazo sem confirmar.
- **`tests/test_quest_sarevok.py`:**
  - a quest inteira com o jogo simulado: o chamado até o aceite, a visão só à noite, o cativeiro com as cópias juntas, Gregor saindo pela porta, a célula hostil, o descanso e o marco;
  - dois passos abertos da mesma pessoa, chamado inválido e saída inválida são recusados.
- **No jogo:** evidência própria.
