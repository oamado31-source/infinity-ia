# CR-2026-022 — Um nome que o NPC já disse na conversa continua conhecido

**Status:** APPROVED (mantenedor, 2026-11-16: falha vista no jogo com Darromar)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-16

## Motivo e contexto

No teste do lote E com Bernard (2026-11-16):
- no primeiro turno, ele falou da rainha Zaranda, e a resposta foi validada;
- na pergunta seguinte, "E Darromar?", o prompt trouxe Darromar, mas não a entrada de Zaranda, porque a pergunta não a nomeava (CR-2026-016);
- Bernard repetiu o nome que ele mesmo tinha acabado de dizer, e o verificador o recusou duas vezes (`UNKNOWN_NAMES:Zaranda`);
- a resposta caiu na fala de reserva.

O verificador só aceita nomes que estejam:
- nas entradas que foram ao prompt daquela pergunta;
- no que o jogador acabou de escrever (CR-2026-008).

Ele não olha o histórico da conversa (ADR-0123).

## DEC/ADR/SPEC/REQ afetados

- **ADR-0123 e CR-2026-019:** inalterados. O histórico continua indo só em turnos `user`/`assistant`.
- **CR-2026-008:** inalterado. Um nome que só o jogador escreveu em turnos anteriores continua desconhecido.
- Nenhum ADR é editado.

## Diff proposto e impacto no comportamento

1. **`dialogue/engine.py`, `_converse`:** quando há histórico, os nomes que o próprio NPC disse nos turnos anteriores entram no vocabulário do verificador naquela pergunta. Esses nomes passaram pela validação no turno em que foram ditos.
2. **Efeito:** num seguimento, o NPC pode repetir quem ou o que já citou ("Darromar é a cidade da rainha Zaranda") sem ser recusado.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Um nome inventado que passou num turno passaria de novo:** só se tivesse escapado do verificador antes. O risco é o mesmo de hoje, sem nada novo.
- **Injeção:** as falas do jogador não entram no vocabulário. Só as do NPC, já validadas.
- **Dados privados:** nenhum. O histórico continua só na memória (ADR-0123).

## Migração e rollback

- **Migração:** nenhuma.
- **Rollback:** tirar o bloco do `_converse`.

## Testes

- **`tests/test_conversation.py`, dois casos novos:**
  - um nome que o NPC já disse é aceito;
  - um nome que só o jogador disse antes continua recusado. Sem a correção, o primeiro caso falha.
- **Bateria:** caso novo `nome-ja-dito-na-conversa`. O histórico tem a rainha Zaranda, a pergunta é "E Darromar?", e o resultado foi 3/3 sem recusas.
