# ADR-0135 — Quests narrativas curadas, sem escrita no jogo

**Estado:** APROVADA (mantenedor, 2026-11-17: "Aprovar como proposta", decisões D1 a D4 na primeira opção).

**Origem:** o mantenedor pediu para começar as quests novas e testar junto a confiança por marco. O diagnóstico mostrou que nenhuma SPEC tratava de quests novas e que escrever no jogo depende do portão P3 (escrita reversível em save descartável), do gateway de ações (DEC-012) e da política de publicação (DEC-027), que ainda não existem.

**Relaciona-se com:**
- SPEC-011 (quests narrativas pela caixa);
- doc. 24 (DEC-010, `STRUCTURED_QUEST`) e doc. 26 (DEC-012);
- ADR-0134 (marco por ramo e regra `MILESTONE`), ADR-0133 (confiança), ADR-0131 (divulgação);
- ADR-0095 e ADR-0099 (a quest original e o estado do jogo não são tocados);
- ADR-0107 (o texto do jogador não é guardado).

**Gate:** etapa 1, single player. Nada é escrito no estado do jogo.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-17.

1. **O primeiro tipo de quest nova é o narrativo (D1):** acontece só nas conversas pela caixa. Diário do jogo, item, recompensa, criatura e variável ficam para depois do portão P3 e do gateway.
2. **Política de publicação deste corte (D3):** só quests curadas pelo mantenedor valem. O modelo não propõe quests; só dá voz ao fato curado que o código põe no prompt do turno. É o recorte mínimo da DEC-027 para conteúdo sem efeito mecânico.
3. **O código decide cada mudança de estado** por palavras curadas da quest, nunca pela interpretação do modelo:
   - oferta (pedir trabalho ou ajuda a quem dá a quest);
   - aceite (depois da oferta);
   - passo (perguntar à pessoa do passo sobre o assunto, com a quest aceita);
   - fim (voltar a quem pediu, com todos os passos feitos).
4. **Estado por ramo,** por eventos idempotentes (`NarrativeQuestOffered`, `…Accepted`, `…StepDone`, `…Resolved`) sem o texto do jogador. O fim grava o marco `quest:<id>:RESOLVED` como `QuestMilestoneObserved` com origem `OVERLAY` (ADR-0134).
5. **Os fatos de um passo** só entram no prompt de quem faz o passo, e só depois do aceite.
6. **A caixa mostra o diário (D4):** uma linha "(Diário: …)" depois da fala, quando a quest muda de estado. O diário do jogo não é tocado.
7. **Os textos da quest são do projeto:** conteúdo da campanha, fora do pacote de cânone, sem nada copiado do jogo. A quest de exemplo é "O broche de Bernard" (Bernard pede, Yarin ajuda; o marco deixa Bernard `ÍNTIMO`).
8. **O marco e a regra `MILESTONE` da ADR-0134 vão no mesmo PR (D2).**

## Consequências

- Bernard, depois da quest, fica `ÍNTIMO` com o grupo e pode contar o segredo dos escravos da arena, que é da casa (`CONFIDENTIAL`, ADR-0133 D2).
- Novas quests narrativas são só arquivos curados em `knowledge/quests/`.
- Se o modelo falhar no turno, a quest continua avançada, e a fala de reserva sai com a linha de diário.

## Verificação

- `tests/test_narrative_quests.py`: formato, palavras, fluxo completo, ordem, outra área, save antigo, eventos sem texto, marco `OVERLAY` e Bernard `ÍNTIMO` com o segredo da casa no contexto.
- Bateria: `bernard-oferece-o-broche`, `yarin-conta-do-batedor` e `bernard-intimo-conta-dos-escravos` (3/3 cada).
- No jogo: evidência própria.
