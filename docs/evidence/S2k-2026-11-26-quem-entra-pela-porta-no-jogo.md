# Evidência S2k — ADR-0148: quem dá a quest entra pela porta, e a entrega paga (2026-11-26)

**Gate:** etapa 1, single player, save descartável, Coroa de Cobre (AR0406).
**Resultado:** **aprovado no laboratório ARM64/VM**, na terceira rodada. O mantenedor confirmou no jogo o ouro e o XP ("Ouro e XP subiram"), e o jogo mostrou "A equipe ganhou experiência: 50" e "A equipe ganhou ouro: 100".

**Executado por:** mantenedor, no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`), e Claude Code.

**Preparação, com o jogo fechado:**
- `talk_poc.py --deploy` instalou o módulo `M_INFAIA.lua` com o andar até um ponto (`MoveToPoint`) e a recompensa (`GiveGoldForce`, `AddexperienceParty`);
- `build_templates.py --from-sheet` criou `IADORAN` / `INFAI_DORAN` com o corpo do nobre do jogo (`GNOBLEM1`, `NOBLE_MAN`), sem diálogo e sem sons;
- o manifesto foi refixado antes e depois de o serviço gravar a lista de quests: mesma build, só arquivos nossos mudaram;
- o serviço rodou com `--local-quests --quest-presence --claude`.

A quest de teste `teste-doran-porta` ficou fora do repositório e foi verificada sem erros nem avisos:
- Doran nasce na porta da Coroa e anda até o balcão, com `from: START` e `walk_to`;
- chama ajuda com uma frase do jogo;
- pede que o grupo olhe a rua das Favelas;
- na volta, paga 100 de ouro e 50 de XP e sai pela porta.

## O que passou (terceira rodada)

| # | Ponto | Log | No jogo |
|---|---|---|---|
| 1 | Doran nasce desde o começo, num save antigo | `ENTER IADORAN em AR0406`, confirmado | nasceu sem fugir e ficou parado perto do balcão de Bernard |
| 2 | O chamado de uma criatura nossa | `chamado teste-doran-porta: INFAI_DORAN … (frase 4889)`, confirmado | a frase sobre a cabeça dele |
| 3 | A oferta, terminando com a pergunta | `NarrativeQuestOffered` | "Preciso que vejam se há gente vigiando a Coroa de Cobre … Aceitam o trabalho?" |
| 4 | O aceite | `NarrativeQuestAccepted` | linha do diário |
| 5 | O passo nas Favelas e a entrega | `chegada … AR0400`, `NarrativeQuestResolved` | duas linhas do diário |
| 6 | A saída pela porta | `LEAVE INFAI_DORAN`, confirmado | Doran saiu |
| 7 | A recompensa, uma vez, confirmada | `recompensa … 100 de ouro, 50 de XP: HOST_CONFIRMED` | ouro 129 → 229; o líder ganhou 10 dos 50 de XP do grupo |

## O que apareceu no caminho

1. **Rodada 1: a oferta repetia uma ordem.**
   - Escrevi o fato da oferta como "Peça que o grupo dê uma olhada na rua … e pergunte se aceitam", e Doran repetiu isso como fala.
   - Corrigido no texto: o pedido ao grupo vem como desejo ("você quer que o grupo …"), com o fecho "Pergunte se o grupo aceita".
   - O verificador ganhou o aviso `FACT_ORDER` para pedidos ao grupo escritos como ordem ("Peça", "Mande", "Convide" …). Ordens sobre a fala da própria pessoa continuam valendo: Gregor, na quest de Sarevok, segue "Agradeça primeiro".
2. **Rodadas 1 e 2: Doran fugia ao nascer** ("Falha de Moral: Fuga" e depois andava pela taverna).
   - A ficha tinha moral 6, e o corpo base tem limite de quebra 7. Na rodada 1 isso fez Doran parecer "longe do balcão".
   - A ficha passou para moral 10.
   - O construtor agora recusa ficha com moral igual ou abaixo do limite do corpo (`MORALE_BELOW_BREAK`).
3. **Rodadas 1 e 2: a recompensa ficou retida.**
   - O jogo pagou (o ouro aparece no log do jogo), mas `m_nPartyGold` não deu número. A resposta saiu `UNVERIFIED`, e o serviço reteve e **não reenviou**, como manda a ADR-0148.
   - Ao recarregar um save anterior, a linha nova da campanha pagou uma vez, e também ficou retida.
   - O módulo agora lê o ouro como a interface do próprio jogo, com `game:GetPartyGold()`, e o XP pelos atributos ativos do líder.
   - A linha de diagnóstico da rodada 3: `INFAI-DIAG reward gold=129 via=1 xp=91964 via=1`, depois `gold=229 xp=91974`.
4. **O XP é o total da equipe.** `AddexperienceParty(50)` reparte entre os personagens, como numa quest do jogo. Ficou registrado na ADR-0148 e na SPEC-013.
5. **"Há vidas em jogo" não existe no `dialog.tlk`.** O mantenedor preferia essa frase, mas o chamado só mostra frases do jogo (ADR-0144). Foi usada a 4889, "Ajude-nos... por favor.". Frases nossas ficam para uma ADR própria, se a quest dos reféns pedir.
6. **Rodada 3: a fala da entrega saiu sem o agradecimento e o pagamento.**
   - O modelo deu uma resposta válida sem o fato da entrega, e a segunda tentativa repetiu as palavras do jogador (`ECHO`). Pela CR-2026-033, ficou a primeira resposta.
   - Nesta rodada eu tinha escrito a entrega como descrição ("você agradece …"). Na rodada 1, em forma de ordem ("Agradeça …, entregue …"), ela foi seguida.
   - O texto voltou à forma de ordem, e a regra entrou na skill de autoria.
   - A mecânica não dependeu disso: o diário, o ouro, o XP e a saída funcionaram.
7. **Entrada pela porta oeste.** O grupo costuma chegar pela porta sul, por isso o mantenedor não viu a entrada na rodada 1. Ele preferiu manter Doran onde ficou, perto do balcão de Bernard.

## Verificação do ramo

- Suíte com 700 testes OK, também com `lupa` e `jsonschema`; `pyflakes` sem avisos.
- `check_historical_adrs` e `check_public_files` OK.
- Testes novos ou mudados:
  - `tests/test_reward_and_entry.py`: o aviso `FACT_ORDER`, e a leitura do ouro e do XP como a interface do jogo, com o valor do EEex em `m_value`;
  - `tests/test_creatures.py`: `MORALE_BELOW_BREAK`;
  - `tests/test_actions.py`: duas leituras do EEex na lista permitida, as duas só de leitura.
- Arquivos copiados para o checkout do laboratório e conferidos byte a byte.
- A quest de teste será apagada antes da quest dos reféns, porque as duas usam `INFAI_DORAN`.
