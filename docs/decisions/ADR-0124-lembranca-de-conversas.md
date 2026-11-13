# ADR-0124 — Lembrança de conversas anteriores, sem guardar texto

**Estado:** APROVADA (decisões explícitas do mantenedor, 2026-11-13).
**Origem:** item 2 da avaliação do que melhorar só com código e IA local. Com o ADR-0123, a conversa só vale enquanto a caixa está aberta, e ao reabrir o NPC esquece que já falou com o jogador. Os companheiros também não diziam de quem ouviram algo, embora o INQUIRY registre quem falou.
**Relaciona-se com:** SPEC-003 (eventos, ramos e memória), SPEC-004 (diálogo), ADR-0114/0116 (INQUIRY), ADR-0117 (fatos "SOBRE VOCÊ") e ADR-0123 (conversa em andamento).
**Gate:** etapa 1, single player. Os testes sintéticos não comprovam a fala no jogo.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-13.

1. **O que se guarda.** Cada turno respondido grava um evento `NpcConversationTurn` com:
   - quem falou (`npc_key`);
   - a conversa (`conversation_id`, uma abertura da caixa);
   - o pedido;
   - as entradas do pacote que o NPC usou na fala validada (lista vazia na fala de reserva).

   O tempo de jogo vem do próprio evento. **Nada do que o jogador ou o NPC disse é gravado.** O evento é idempotente por pedido.
2. **O que o NPC lembra.** Numa conversa nova, ele recebe como fatos "SOBRE VOCÊ":
   - quantas vezes já conversou com o jogador e quando foi a última (por exemplo "2 vezes, a última há 1 dia");
   - até 4 assuntos, os mais recentes primeiro ("Vocês falaram sobre: Conselho dos Seis, Coroa de Cobre").

   A conversa em andamento não conta como anterior.
3. **Ramos.** A lembrança lê os eventos visíveis no ramo. Carregar um save anterior à conversa faz o NPC não se lembrar dela.
4. **Quem é lembrado:**
   - **sempre:** quem tem script name, curadoria ou é companheiro;
   - **só na mesma sessão:** genéricos sem script name, lembrados pela instância que o jogo dá àquela pessoa no mapa (`<id>@<sessão>#<instância>`). Ao reabrir o jogo, é outra pessoa. Isso evita misturar cópias diferentes do mesmo tipo de criatura.
5. **Fonte do INQUIRY.**
   - O evento `KnowledgeShared` passa a guardar o nome de quem falou e a área.
   - O companheiro recebe o item como "Conselho dos Seis (você ouviu isso de Bernard, na Coroa de Cobre): …".
   - A regra 7 permite dizer de quem ouviu quando o item traz essa informação.
   - **Fonte usada:** a vez mais recente em que o companheiro ouviu aquele assunto de alguém com nome registrado. O registro do conhecimento guarda só a primeira vez, que pode ser anterior a esta decisão e não ter nome.
   - **Sem fonte registrada:** a regra 7 pede para não inventar de quem ouviu. No laboratório, Jaheira, sem fonte, atribuiu a informação a "um cara que trabalha na Casa do Conselho".

## Consequências

- **Código:**
  - `src/infinity_ai/dialogue/recall.py` (`record_turn`, `recall`, `recall_lines`, `npc_key`);
  - `context.py` (`recall_lines` e fonte do INQUIRY);
  - `engine.py`;
  - `memory/common_knowledge.py` (`speaker_name` e `area` em `share_knowledge`);
  - `tools/windows-lab/dialogue_service.py`, com o log `lembra=N`, sem texto.
- **Testes:** `tests/test_conversation_recall.py`.

## Riscos e limites

- **Assuntos:** são só as entradas que o NPC usou; o que o jogador perguntou e o NPC não soube responder não fica registrado.
- **Tempo:** usa a conversão de 7200 unidades de tempo de jogo por dia, a mesma da SPEC-003. Ainda falta confirmar essa unidade no laboratório.

## Evidência de laboratório (S1f, 2026-11-13)

| Caso | Resultado |
|---|---|
| Bernard: falar do Conselho, fechar e reabrir a caixa, "Já conversamos antes?" | `lembra=1`: "Já conversamos, sim." |
| Bernard: "Sobre o que falamos mesmo?" | "Falamos sobre o Conselho dos Seis." |
| Jaheira, sem fonte registrada (antes da correção): "De quem você ouviu falar sobre o Conselho?" | inventou "um cara que trabalha na Casa do Conselho" |
| Jaheira, depois da correção (fonte pela vez mais recente e regra 7) | "Ouvi de Bernard, na Coroa de Cobre." |

**Pendente:** o cliente genérico lembrando só na mesma sessão. Está coberto pelos testes sintéticos, mas ainda não foi testado no jogo.

