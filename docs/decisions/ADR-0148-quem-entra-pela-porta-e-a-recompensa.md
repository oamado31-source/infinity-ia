# ADR-0148 — Quem dá a quest entra pela porta, e a entrega paga

**Estado:** APROVADA (mantenedor, 2026-11-26: "Aprovar como proposta" da quest "Os Reféns da Estrela de Waukeen", D1 a D7 na opção recomendada). Peças 1 e 2 dessa proposta; fase 1 da D1.

**Origem:** a quest dos reféns pede duas coisas que o sistema não faz.
- **Doran Vell, o feitor da casa Argrim, é uma pessoa nova.** Hoje uma presença só nasce no aceite (ADR-0138), mas quem dá a quest precisa estar no mundo antes, para oferecê-la. O mantenedor quer o efeito contrário da saída pela porta (ADR-0144): ele surge na porta da Coroa de Cobre, caminha até o balcão, fica ali e chama ajuda com uma frase sobre a cabeça, como Garoll.
- **A família paga.** Hoje a entrega só muda a confiança (ADR-0134).

**Relaciona-se com:** SPEC-011, SPEC-013, ADR-0134, ADR-0136, ADR-0138, ADR-0140, ADR-0143, ADR-0144 e ADR-0145.

**Gate:** etapa 1, single player, save descartável.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-26.

1. **Presença desde o começo (`from: "START"`):**
   - uma presença pode existir desde o começo da campanha, antes da oferta e do aceite, até o seu `until`;
   - serve para quem dá a quest ser uma pessoa nova (um `INFAI_` com curadoria);
   - a chegada preparada (ADR-0145) também vale: se o grupo está em outra área, a pessoa é criada no momento em que a área dela carrega.
2. **Andar até um ponto ao nascer (`walk_to`):**
   - a presença com `x`, `y` (o ponto onde nasce, por exemplo a porta) e `walk_to: {x, y}` anda até esse ponto logo depois de criada, e fica lá;
   - usa a ação do próprio jogo `MoveToPoint`, de modelo fixo, na fila da criatura nossa;
   - vale só na criação (pedido do serviço ou chegada preparada); quem já está no save não anda de novo;
   - o pedido de criação leva o ponto de destino; o módulo recusa ponto fora do mapa.
3. **Chamado de uma criatura nossa:**
   - o chamado (ADR-0144) pode sair da cabeça de uma criatura nossa (`INFAI_`), desde que seja uma presença da mesma quest;
   - continua só exibição, com uma frase que já existe no `dialog.tlk`, e só o par que a quest declara.
4. **A recompensa (`turn_in.reward`):**
   - `{gold, xp}`: ouro de 0 a 10.000 e XP de 0 a 50.000, ao menos um maior que zero;
   - o `xp` é o total da equipe: `AddexperienceParty` reparte entre os personagens, e o jogo mostra o total (no laboratório, 50 com um grupo de cinco deram 10 ao líder);
   - com a quest resolvida, o serviço pede uma vez a operação `REWARD`, e o líder executa na hora as ações do próprio jogo `GiveGoldForce` e `AddexperienceParty`, de modelo fixo;
   - **nunca duas vezes:** o pedido é registrado antes, com a causa (a quest); se o jogo não confirmar, a recompensa fica suspensa até o mantenedor olhar o jogo, e nunca é reenviada às cegas;
   - **a confirmação** é a diferença do ouro do grupo, quando o módulo consegue lê-lo; sem a leitura, a resposta não confirma, e a recompensa fica suspensa (D1 de segurança: melhor perder um pagamento no laboratório do que pagar duas vezes);
   - o texto do jogador nunca escolhe o valor: ele vem da quest curada.
5. **Verificador (SPEC-013):** aceita `START`, `walk_to` e `reward` com os mesmos limites do carregador, e avisa quando quem dá a quest é uma pessoa nova sem presença `START` na área dela.

## Consequências

- Uma quest pode ser oferecida por uma pessoa criada pelo projeto, que entra em cena sozinha.
- A presença `START` existe em qualquer save, também nos antigos, quando o grupo entra na área.
- **Fora:** andar por um caminho com vários pontos; voltar a andar depois; itens como recompensa; recompensa por passo.

## Verificação

- `tests/test_reward_and_entry.py`:
  - o carregador aceita e recusa `START`, `walk_to` e `reward`;
  - a presença `START` é querida antes do aceite e entra no plano de chegada com o destino;
  - o chamado aceita a nossa presença e recusa um `INFAI_` que não é da quest;
  - a recompensa é pedida uma vez, só com a quest resolvida, e fica suspensa sem confirmação;
  - o módulo, com motor simulado, anda até o ponto e paga só com o modelo fixo.
- **No jogo:** evidência S2k, com Doran na Coroa de Cobre.
- **Lições do primeiro teste no laboratório (2026-11-26):**
  - `m_nPartyGold` não deu número, e a recompensa ficou suspensa como previsto. O módulo passa a ler o ouro como a interface do próprio jogo (`game:GetPartyGold()`), com os outros caminhos como reserva, e o XP pelos atributos ativos do líder; a linha `INFAI-DIAG` do log diz qual caminho leu;
  - uma ficha com moral igual ou abaixo do limite de quebra do corpo base foge assim que nasce (Doran com moral 6 e quebra 7): o construtor de criaturas recusa (`MORALE_BELOW_BREAK`).
