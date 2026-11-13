# CR-2026-005 — Regra de vínculo de trabalho reconhece o nome do lugar

**Status:** APPROVED (mantenedor, 2026-11-13)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-13

## Motivo e contexto

O conjunto fixo de testes de fala (`tools/dialogue-eval/`) achou a frase "Trabalho na Coroa de Cobre, sim." dita por um habitante sem afiliação `STAFF`. A regra de vínculo do ADR-0120 (item 5) só reconhecia "trabalho aqui", "na taverna", "na casa" e "para o dono", e não o nome do lugar onde a pessoa está. Com o caso ajustado, `sem-staff-trabalho` passou a falhar em 3 de 6 rodadas.

**Pedido do mantenedor:** corrigir na mesma branch dos testes de fala.

## DEC/ADR/SPEC/REQ afetados

- ADR-0120, item 5 (validador de origem, moradia e trabalho): refinado por este CR. O ADR permanece inalterado.
- SPEC-004 (validação da fala).

## Diff proposto e impacto no comportamento

- **Recusa nova:** sem afiliação `STAFF`, "trabalho [aqui] na/no/em <lugar onde a pessoa está>" passa a ser recusado como `SELF_CLAIM:WORK`. O lugar vem de `DialogueContext.resident_of`, por exemplo "a Coroa de Cobre".
- **Continua aceito:**
  - "Não trabalho na Coroa de Cobre.";
  - "Trabalho na cidade, perto da Coroa de Cobre.";
  - quem tem `STAFF`, como Bernard.
- **Testes:** em `tests/test_identity.py` (`OriginClaimTests`), com o caso `sem-staff-trabalho` do conjunto de testes de fala.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- Paráfrases como "sirvo mesas na Coroa" continuam fora do alcance das regras por padrão de texto.
- Nenhum dado novo, licença ou dependência.

## Migração e rollback

Sem migração. Rollback: remover `_works_at_place` do validador.
