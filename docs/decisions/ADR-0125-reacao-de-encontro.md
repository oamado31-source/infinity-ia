# ADR-0125 — Reação de encontro dos NPCs (primeira fatia do ADR-0122)

**Estado:** APROVADA (decisões explícitas do mantenedor, 2026-11-13). Aprova só a primeira fatia do ADR-0122, que continua em PROPOSTA para o restante: teste de moral, `Reaction()` nativa e iniciador comprovado.
**Origem:** todo NPC atendia o jogador com a mesma disposição. O ADR-0122 define que o código decide a reação e o modelo só a expressa. A sonda do PR #20 (evidência S1g) já lê o Carisma do personagem selecionado.
**Relaciona-se com:** ADR-0122 (reação social e moral), ADR-0018 (núcleo AD&D 2e), ADR-0115/SPEC-006 (personalidade), ADR-0123/0124 (conversa e lembrança), SPEC-003 (eventos) e SPEC-004 (fala).
**Gate:** etapa 1, single player. Nada é escrito no jogo.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-13.

1. **Escopo:** só a reação de encontro. O teste de moral (tentação, suborno, perigo) fica para a segunda fatia.
2. **Regra (AD&D 2e):**
   - **Tabela 59 do DMG:** 2d10, cruzados com a conduta observada dos personagens (amistosa, indiferente, ameaçadora, hostil), dão a disposição: fuga, amistoso, indiferente, cauteloso, ameaçador ou hostil. Total baixo é favorável; totais fora de 2–20 ficam limitados a esse intervalo.
   - **Ajuste de Carisma (Tabela 6 do PHB):** um ajuste positivo melhora a reação, por isso é **subtraído** do total.
   - **Fonte dos valores:** AD&D 2e Core Rules (DMG `dd00564`, PHB `dd01436`). O mantenedor confere os valores com o livro; os de Carisma 19 e 20 vieram menos legíveis na fonte.
3. **Carisma usado:** o do personagem selecionado. Com o grupo todo selecionado, entra o do líder (`selected_leader`, PR #20). Quem efetivamente inicia o diálogo no motor ainda não está comprovado (ADR-0122), e o evento registra de quem foi o Carisma aplicado.
4. **Conduta do jogador:** regras locais em português sobre as palavras de abertura do encontro, sem modelo:
   - insulto ou violência → hostil;
   - ameaça ou coação → ameaçadora;
   - cortesia → amistosa;
   - o resto → indiferente.
5. **Frequência:**
   - **uma vez por NPC por sessão do jogo:** reabrir a caixa não rerrola; reabrir o jogo é um novo encontro;
   - **rolagem determinística:** semente do mundo, campanha, ramo, pessoa e sessão;
   - **companheiros:** não rolam.
6. **Evento:** `NpcEncounterReactionResolved`, idempotente por pessoa e sessão, **sem texto**. Guarda conduta, dados, Carisma (de quem e quanto), ajuste, total, disposição e regra.
7. **Efeito na fala**, decidido por código antes do modelo:

   | Disposição | O que chega ao modelo | Comportamento pedido |
   |---|---|---|
   | amistoso | todo o conhecimento | conta o que sabe com boa vontade |
   | indiferente | todo o conhecimento | responde curto |
   | cauteloso | sem o conhecimento restrito | só o que foi perguntado, com reserva |
   | ameaçador / hostil | nenhum conhecimento | não ajuda e reage mal, só em palavras |
   | fuga | nenhum conhecimento | quer encerrar e ir embora |

   Sem conhecimento, nada é ensinado por INQUIRY. A disposição não muda nada no jogo: nem ações, nem reputação, nem save.

## Fora desta fatia

- teste de moral (Tabelas 49–50 e 71);
- conduta que muda no meio do encontro, ou seja, nova avaliação;
- valor da `Reaction()` nativa e cuidado para não aplicar Carisma ou reputação duas vezes;
- modificadores de criatura ou de alinhamento;
- influência numérica da personalidade (HEXACO).

## Consequências

- **Código:**
  - `src/infinity_ai/personality/reaction.py`;
  - `dialogue/context.py` e `engine.py` (`disposition`);
  - `tools/windows-lab/dialogue_service.py`, com o log `reacao=…`;
  - casos de disposição em `tests/dialogue_eval/cases.pt_BR.json`.
- **Testes:** `tests/test_reaction.py`.

## Evidência de laboratório (S1f, 2026-11-13)

| Caso | Log e fala |
|---|---|
| Bernard, "Olá, como vai?" (protagonista selecionado, Carisma 14) | `FRIENDLY(2d10=2+1 chr=+2 -> 1, coluna=FRIENDLY)`: "Vou bem, e você? Já passou por aqui antes?" |
| Bernard, segundo turno e depois da caixa reaberta | mesma reação, reaproveitada na sessão |
| Campesino, "Me diga agora o que está fazendo aqui, senão vou te colocar para fora!" | `CAUTIOUS(2d10=2+6 chr=+2 -> 6, coluna=THREATENING)`: "Carrego mercadorias pra cima e pra baixo. Não é da sua conta." |

**Testes de fala:** os casos de disposição passaram em 3/3: hostil não conta, cauteloso guarda o restrito, amistoso conta.

**Achado:** com disposição cautelosa, um NPC chegou a inventar um traço sem nome próprio na frase ("eu já vi ele passar o dia dormindo na mesa"). O validador do ADR-0121 só confere traços ligados a um nome.

