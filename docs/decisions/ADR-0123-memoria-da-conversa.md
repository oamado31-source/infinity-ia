# ADR-0123 — Memória da conversa enquanto a caixa está aberta

**Estado:** APROVADA (decisões explícitas do mantenedor, 2026-11-13).
**Origem:** avaliação do que melhorar só com código e IA local (item 1) e evidência S1f. Cada pergunta da caixa era respondida isolada, então as de seguimento perdiam o sentido: "E quem é então?" virou "Sou Lorde Jierdan…", e "ele" não tinha a quem se referir.
**Relaciona-se com:** SPEC-004 (fluxo, segurança e validação), ADR-0116 (caixa no jogo), ADR-0106 (local primeiro) e ADR-0121 (INQUIRY com a pergunta como contexto).
**Gate:** etapa 1, single player. Os testes sintéticos não comprovam a fala no jogo.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-13.

1. **Uma conversa é uma abertura da caixa com uma pessoa.**
   - A caixa cria um id ao abrir (`"<sessão>-<relógio>"`) e o envia em cada pedido (`conv`).
   - Fechar e reabrir a caixa começa uma conversa nova, como o jogador vê na tela.
   - Pedido sem id, vindo de caixa antiga, segue sem histórico.
2. **Só na memória do serviço.**
   - Os últimos 4 turnos de cada conversa ficam na RAM do serviço: a pergunta e a fala que o jogador viu, incluída a de reserva, com até 300 caracteres cada.
   - Cabem no máximo 64 conversas abertas; a mais antiga é descartada primeiro.
   - Nada vai para disco nem para o banco da campanha, e reiniciar o serviço apaga tudo.
   - Lembrar entre conversas é outra decisão, que exige registro estruturado e sem texto.
3. **Como turnos de chat, nunca no `system`.** Os turnos anteriores entram como mensagens `user`/`assistant` antes da pergunta atual, e o texto do jogador continua só no papel `user` (segurança da SPEC-004). Uma regra 10 aparece no prompt apenas quando há histórico: usar a conversa para entender a pergunta ("ele", "e então?"), não repetir o que já disse e não tratar o que o jogador afirmou como fato.
4. **INQUIRY:** o contexto da pergunta passa a ser a pergunta atual mais a anterior da mesma conversa. Assim, "E quem é então?", depois de "Quem governa Amn?", conta o nome dito antes. A fala continua tendo de trazer conteúdo (ADR-0121).
5. **Validação inalterada.** O que o jogador disse antes não entra no vocabulário permitido, e só as seções do contexto valem como fato.

## Consequências

- **Código:**
  - `tools/eeex-probe/M_INFAIT.lua` (id da conversa);
  - `src/infinity_ai/bridge/talk.py` (`conversation_id`);
  - `src/infinity_ai/dialogue/conversation.py` (`ConversationMemory`);
  - `engine.py` (`history` em `respond`/`respond_resident`);
  - `tools/windows-lab/dialogue_service.py` (log `turno=N`, sem texto).
- **Testes:** `tests/test_conversation.py` e `tests/test_talk.py`.
- **Laboratório:** a caixa nova exige reabrir o jogo uma vez.
- **Overlay:** o diálogo com companheiros pelo overlay não ganha histórico nesta etapa.

## Riscos e limites

- **Tamanho do prompt:** cada turno anterior aumenta o prompt e o tempo de resposta. O teto de 4 turnos e de 300 caracteres limita isso.
- **Afirmações do jogador:** o modelo pode tomar uma afirmação do jogador como verdade. A regra 10 e o validador, que só aceita o que está nas seções, reduzem o risco, mas não o eliminam.

## Evidência de laboratório (S1f, 2026-11-13)

Teste feito na campanha `lab-s1f`, com a caixa nova carregada depois de reabrir o jogo:

| Caso | Resultado |
|---|---|
| Lorde Jierdan: "Quem governa Amn?" → "E quem é então?" | `turno=2`: "Não sei dizer. Ninguém sabe quem são." (antes, sem memória, respondia sobre si mesmo) |
| Campesino: "Quem é o dono da taverna?" → "Ele trabalha aqui?" | `turno=2`: "Não, ele é dono. Trabalho eu." ("ele" = Lehtinan) |
| Fechar e reabrir a caixa | `turno=1`; sem os turnos anteriores, "ele" voltou a ficar sem referência |

**Achados:**
- **Vínculo de trabalho pelo contexto:** "Trabalho eu" afirma vínculo com a taverna só pelo contexto da pergunta anterior, e o validador de vínculo (ADR-0120), que procura formas como "trabalho aqui", não pega.
- **INQUIRY e a fala anterior:** quando o nome só aparece na fala anterior do NPC, o INQUIRY não o conta.

