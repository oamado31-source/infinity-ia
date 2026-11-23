# ADR-0139 — Hora do dia e chegada a um lugar

**Estado:** APROVADA (mantenedor, 2026-11-22: "Aprovar como proposta", decisões D1 a D4 na opção recomendada).

**Origem:** a quest "O diário perdido de Sarevok" (v4) precisa de duas coisas.
- **A hora:** a visão de Tamoko aparece no Cemitério **à noite**.
- **A chegada:** a quest anda quando o grupo **chega** a um lugar (o cativeiro de Gregor nas Favelas, o esconderijo nas Docas), sem conversa.

Esta é a peça B.

**Relaciona-se com:**
- ADR-0138 (presença decidida pela quest);
- ADR-0135/SPEC-011 (quests narrativas, estado por ramo, o código decide);
- SPEC-001/P2 (o probe lê a área e o tempo de jogo);
- REQ-QUEST-006 (nenhum fato de passo antes de aceitar).

**Gate:** etapa 1, single player, save descartável. Nada novo é lido nem escrito no jogo.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-22.

1. **Relógio do jogo** (`quests/clock.py`, puro):
   - hora = (tempo de jogo ÷ 4500) mod 24;
   - a unidade foi conferida no laboratório contra o relógio do próprio jogo. O tempo do probe conta ticks do motor, 15 por segundo de jogo: uma hora tem 4500 e um dia 108000. A suposição antiga, de 300 por hora, estava errada (tempo 497541: o jogo mostrou 14h; 300 por hora dariam 2h);
   - **pendência fora desta ADR:** `dialogue/recall.py` (`DAY = 7200`) e o limite de residência (`DEFAULT_RESIDENCE_THRESHOLD = 7200`) supõem um dia de 7200, que na verdade é cerca de 1h36 de jogo. Pedem uma correção própria;
   - sem tempo de jogo não há noite, e o que pede a noite não acontece.
2. **Noite (D1):** das 21h às 5h59, anoitecer e noite, quando o mapa escurece.
3. **Presença só à noite:** o item de `presence` ganha `when` (`ANY`, o padrão, ou `NIGHT`). Uma presença `NIGHT` só é querida à noite.
4. **Ao amanhecer (D2):** a presença `NIGHT` deixa de ser querida, e o diretor remove o que a quest pôs quando o grupo está na área. Se o grupo estiver fora, ela sai na próxima entrada de dia. Na noite seguinte, volta.
5. **Passo de chegada:**
   - um passo pode trazer `arrive: {area, night}` em vez de pessoa, frases e fato;
   - é feito quando o grupo entra na área, com a quest aceita, sem resolver, os passos de `after` feitos e, se pedir, à noite;
   - grava o mesmo `NarrativeQuestStepDone`, uma vez por ramo, sem texto do jogador.
6. **O diário da chegada:** como chegar não tem conversa, a linha do diário vai na próxima resposta da caixa ("(Diário: …)"). O evento `NarrativeQuestJournalShown` registra que ela já foi mostrada.
7. **Ordem dos passos (`after`):** em qualquer passo, a lista dos passos que precisam estar feitos antes. Só pode citar passos anteriores na lista, e assim a ordem nunca fecha um ciclo. Sem `after`, vale como antes.
8. **Quest em várias áreas:** o `area` da quest continua opcional. Um passo de conversa pode dizer a sua área. A quest do diário passa por quatro lugares.
9. **Quem registra a chegada (D3):** o observador do serviço, a cada leitura. Como não escreve no jogo, fica sempre ligado; a presença continua sob `--quest-presence`.
10. **Teste (D4):** quest local, fora do repositório, na Coroa de Cobre e nas Favelas, no Capítulo 2.

## Consequências

- A quest do diário pode ser montada com o Cemitério à noite e as chegadas às Favelas e às Docas, depois das peças C, D, F e G.
- O serviço mostra a hora calculada nos logs de chegada e de presença, para conferência.
- **Limite:** como na ADR-0138, um save posterior de outra linha não abre ramo novo. A contagem no módulo (peça G) protege a presença. Até lá, cada rodada de teste corre numa linha só de saves.

## Verificação

- **`tests/test_quest_arrival.py`:**
  - o relógio, com noite das 21h às 5h59 e tempo desconhecido sem noite;
  - o formato estrito de `arrive`, de `after` e de `when`;
  - chegar faz o passo uma vez, só depois de aceitar e na área certa;
  - o diário pendente aparece uma vez;
  - a chegada noturna e a ordem;
  - o passo de conversa espera a sua ordem e a sua área;
  - a visão da noite vem à noite, some ao amanhecer e volta na noite seguinte.
- **No jogo:** os sete pontos da proposta, com evidência própria.
