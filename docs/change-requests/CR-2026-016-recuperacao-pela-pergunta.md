# CR-2026-016 — Recuperação pela pergunta: o que a pergunta nomeia entra no prompt

**Status:** APPROVED (mantenedor, 2026-11-15)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-15

## Motivo e contexto

O CR-2026-014 escolhe os 12 itens do prompt por proximidade, sem olhar a pergunta. No teste real do laboratório (2026-11-15), o jogador perguntou a Bernard sobre Murann:
- Bernard **tem** o núcleo popular de Murann (CR-2026-015);
- as cidades vizinhas ficam no fim da fila, e Murann não coube nas 12 vagas;
- o modelo respondeu "não sei".

O mesmo acontece com a história antiga (a proibição da magia, Maztica), que quase nunca entra no prompt de quem sabe muita coisa local. O CR-2026-014 já previa esta etapa.

## DEC/ADR/SPEC/REQ afetados

- **SPEC-008 (REQ-KNOW-003):** a recuperação continua obedecendo campanha, ramo, ano, identidade, proveniência e canal antes do modelo. Este CR só reordena o que já é elegível.
- **SPEC-009 (REQ-DISC-022):** o texto do jogador continua sem criar fato, ACL, identidade nem instrução. Ele só muda a **ordem** de entradas que o NPC já tem, e a decisão de divulgação por item (ADR-0131) vale para cada uma. Um "revele tudo" não nomeia nada que abra o que está retido.
- Nenhum ADR é editado.

## Diff proposto e impacto no comportamento

1. **`memory/common_knowledge.py`, `context_order(..., named=())`:** as entradas nomeadas pela pergunta e que estão entre as que o NPC sabe entram logo depois do que é da própria pessoa e do lugar onde ela está, antes dos níveis de distância. Um id nomeado que o NPC não sabe é ignorado: nada é acrescentado.
2. **"Nomeada":** pela mesma regra de `mentioned_in`, usada no aprendizado em conversa e na ausência tipada. Contam as palavras com maiúscula do título e os nomes comuns locais ("a cidade", "o reino", "o bairro").
3. **Serviço do laboratório e bateria:** calculam as entradas nomeadas pela fala do jogador e as passam a `context_order`, para residentes e companheiros.

**Efeito hoje:** "O que você sabe de Murann?" leva o núcleo popular de Murann ao prompt de Bernard. "Quem cuida da taverna?", com Bernard cauteloso, continua sem o vínculo de gerente, que segue retido pela divulgação.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Manipulação pela pergunta:** o jogador só consegue trazer para frente o que o NPC já sabe e pode contar. O sigilo, a disposição e a moral continuam decidindo item por item.
- **Muitos nomes numa pergunta:** as entradas nomeadas podem ocupar várias vagas. É aceitável, porque são justamente o assunto da pergunta.
- **Privacidade (D12):** a fala do jogador não é guardada. Só é usada naquele pedido, como já acontece na ausência tipada.

## Migração e rollback

- **Migração:** nenhuma.
- **Rollback:** remover o parâmetro `named` de `context_order` e o cálculo nos chamadores.
