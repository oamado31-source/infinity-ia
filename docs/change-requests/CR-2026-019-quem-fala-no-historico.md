# CR-2026-019 — Quem fala em cada turno do histórico

**Status:** APPROVED (mantenedor, 2026-11-16: aprovado para PR)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-16

## Motivo e contexto

O caso `conversa-e-quem-e` da bateria falhava de vez em quando por eco (`ECHO`): o modelo devolvia a pergunta do jogador como fala. A instabilidade apareceu com mais frequência nas últimas rodadas. Ele usa o histórico da conversa (ADR-0123): "Quem governa Amn?" e depois "E quem é então?".

## Investigação (qwen3:30b-a3b, eco na 1ª tentativa / falha final)

| Variação | Eco | Falha final |
|---|---|---|
| Como está (temperatura 0,6) | 5/10 | 2/10 |
| Temperatura 0,2 | 10/10 | 5/10 |
| Fala anterior do NPC em JSON no histórico | 3/10 | 5/10 |
| Sem o exemplo "e então?" da regra 10 | 6/10 | 2/10 |
| Regra explícita "nunca devolva a pergunta" | 6/10 | 4/10 |
| Campo `resposta` no lugar de `speech` | 5/10 | 3/10 |
| Nova tentativa mostrando a resposta errada | 5/12 | 5/12 |
| Nova tentativa com temperatura mais alta (1,0 e 1,3) | 8–10/12 | 4–7/12 |
| Regra 10 sem "não repita o que já disse" | 7/12 | 4–6/12 |
| Nota de sistema antes da fala curta | 4–9/10 | 5–7/10 |
| **Turnos marcados ("Jogador: …", "Você: …")** | **0/10** | **0/10** |

**O eco depende da pergunta:**
- só acontece com seguimentos **curtos e elípticos** depois de um histórico, como "E quem é então?" (5/8) e "Por quê?" (4/8);
- sem histórico, com uma pergunta mais clara ("E quem são eles, então?") ou com outro seguimento ("E eles mandam em tudo?"), o eco foi 0/8;
- com temperatura baixa vira 10/10, ou seja, é a escolha mais provável do modelo, não acaso.

## DEC/ADR/SPEC/REQ afetados

- **ADR-0123:** as falas do jogador continuam em turnos `user`, nunca no prompt de sistema. Só ganham um rótulo de quem fala. Nenhum ADR é editado.
- **SPEC-004 (formato das mensagens):** ampliada.

## Diff proposto e impacto no comportamento

1. **`dialogue/engine.py`:**
   - **Com histórico:** cada turno anterior do jogador vai como `"Jogador: <fala>"`, cada turno anterior do NPC como `"Você: <fala>"`, e a fala atual do jogador como `"Jogador: <fala>"`.
   - **Sem histórico:** nada muda.
2. **O verificador de eco** continua comparando com a fala original do jogador, sem o rótulo.
3. **Efeito medido:**
   - `conversa-e-quem-e`: 6/6, sem nenhuma recusa;
   - "Por quê?": 6/6;
   - nenhum rótulo vazou para as respostas.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Rótulo copiado na resposta:** não aconteceu nas amostras. Se aparecer, o verificador pode removê-lo depois.
- **Injeção:** o rótulo não muda o papel da mensagem. O texto do jogador continua sendo entrada não confiável (REQ-DISC-022).

## Migração e rollback

- **Migração:** nenhuma.
- **Rollback:** voltar os turnos sem rótulo.
