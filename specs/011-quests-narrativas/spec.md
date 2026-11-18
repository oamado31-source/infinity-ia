# SPEC-011 — Quests narrativas pela caixa de diálogo

**Status:** APROVADA para o primeiro corte (mantenedor, 2026-11-17: "Aprovar como proposta", decisões D1 a D4 na primeira opção).
**Rastreabilidade:** ADR-0135; ADR-0134 (marco e regra `MILESTONE`); ADR-0133 (confiança); ADR-0131 (divulgação); ADR-0107 (texto do jogador); ADR-0095 e ADR-0099 (sem tocar quests do jogo); doc. 24 (DEC-010, `STRUCTURED_QUEST`); doc. 26 (DEC-012).

## Objetivo

Dar ao grupo tarefas novas, curadas pelo projeto, que acontecem só nas conversas pela caixa e não escrevem nada no jogo. Ao terminar, a quest deixa um marco que pode mudar a confiança de quem pediu. É a primeira "missão sobre área existente" que o doc. 24 pede, no recorte sem escrita.

**Invariantes:**
- o código decide a oferta, o aceite, cada passo e o fim; o modelo só dá voz ao fato curado do turno;
- o fato de um passo nunca chega ao prompt antes da quest ser aceita;
- a quest não toca a quest original do jogo nem lê variáveis dele;
- os textos da quest são do projeto (campanha), não do jogo nem do pacote de cânone.

## Escopo do primeiro corte

- Uma quest curada, numa área existente (Coroa de Cobre), com NPCs já curados (etapa 3).
- Passos de conversa: pedir, aceitar, perguntar a outra pessoa, voltar a quem pediu.
- Estado por ramo; save antigo recarregado volta a quest ao ponto daquele save.
- Linha de diário na caixa ("(Diário: …)").
- **Fora:** diário do jogo, item, recompensa, criatura, variável do jogo (portão P3 e gateway, DEC-012); objetivo de área; quests geradas pelo modelo; multiplayer.

## Requisitos EARS

- **REQ-QUEST-001:** quando o jogador pedir trabalho ou ajuda a quem dá uma quest curada disponível, o sistema deve pôr no prompt a oferta curada, e só ela.
- **REQ-QUEST-002:** o sistema só deve marcar a quest como aceita quando o jogador aceitar a quem a ofereceu, por palavras curadas, depois da oferta.
- **REQ-QUEST-003:** quando o jogador perguntar à pessoa de um passo sobre o assunto do passo, com a quest aceita, o sistema deve marcar o passo e pôr o fato curado do passo no prompt dela.
- **REQ-QUEST-004:** quando o jogador voltar a quem pediu, com todos os passos feitos, e falar do assunto, o sistema deve resolver a quest e gravar o marco `quest:<id>:RESOLVED` (evento da ADR-0134, origem `OVERLAY`).
- **REQ-QUEST-005:** as fichas dizem o que o marco muda na confiança (regra `MILESTONE`).
- **REQ-QUEST-006:** enquanto a quest não for aceita, o fato de um passo não deve chegar ao prompt.
- **REQ-QUEST-007:** a quest nunca deve tocar a quest original do jogo nem ler variáveis dele.
- **REQ-QUEST-008:** cada mudança de estado deve ser um evento por ramo, idempotente, sem o texto do jogador.
- **REQ-QUEST-009:** quando a quest mudar de estado, a caixa deve mostrar uma linha de diário, sem escrever no diário do jogo.

## Critérios de aceite do primeiro corte

- `tests/test_narrative_quests.py`: formato, fluxo completo, ordem, outra área, save antigo, marco e confiança.
- Bateria: `bernard-oferece-o-broche`, `yarin-conta-do-batedor`, `bernard-intimo-conta-dos-escravos`.
- No jogo: a quest inteira pela caixa; antes, Bernard retém o segredo dos escravos; depois, `ÍNTIMO`, pode contá-lo.
