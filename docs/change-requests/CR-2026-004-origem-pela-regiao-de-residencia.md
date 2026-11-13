# CR-2026-004 — Regra de origem aceita as regiões onde o habitante vive

**Status:** APPROVED (mantenedor, 2026-11-13)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-13

## Motivo e contexto

**O que aconteceu:** no laboratório S1f, Salvanas foi perguntado "O que você faz em Amn?" e caiu duas vezes na recusa `SELF_CLAIM:ORIGIN`, terminando na fala de reserva.

**Causa provável:** o modelo disse algo como "sou de Amn". Os fatos de Salvanas dizem "Você vive em Athkatla e está na Coroa de Cobre" e não citam Amn. A afirmação é verdadeira, porque Athkatla fica em Amn, mas a regra de origem do ADR-0120 (item 5) só aceitava nomes presentes nos fatos.

**Pedido do mantenedor:** aceitar também as regiões que contêm o lugar onde a pessoa vive (para quem vive em Athkatla, isso inclui Amn), e o mesmo para o reino de qualquer cidade do pacote. Uma origem diferente, como "vim de Tethyr", continua barrada sem o fato correspondente.

## DEC/ADR/SPEC/REQ afetados

- ADR-0120, item 5 (validador de origem): refinado por este CR. O ADR permanece inalterado.
- SPEC-004 (validação da fala).

## Diff proposto e impacto no comportamento

- **`NpcIdentity.home_names`:** guarda o nome da região onde o habitante vive e das regiões acima dela, por exemplo `('Athkatla', 'Amn')`. Viajante e forasteiro ficam sem esses nomes.
- **Contexto:** `DialogueContext.home_names` repassa esses nomes ao validador.
- **Validador:** passa a aceitar "sou de X" quando X está em `home_names`.
  - "nasci em X", "vim de X" ou "venho de X" com essas regiões só valem para quem tem o fato "nasceu e cresceu aqui";
  - qualquer outro lugar continua precisando estar nos fatos.
- **Testes:** em `tests/test_identity.py`, os casos "sou de Amn" (aceito), "vim de Tethyr" (recusado), "nasci em Amn" (recusado sem o fato de ter nascido ali) e a ausência desses nomes para viajantes.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Risco:** um habitante imigrante (fato "Você veio de Tethyr e vive aqui há N anos") pode dizer "sou de Amn". É aceitável, porque é onde ele vive hoje; dizer que nasceu em Amn continua barrado.
- Nenhum dado novo, licença ou dependência.

## Migração e rollback

Sem migração. Rollback: remover `home_names` do validador; o restante continua como no ADR-0120.
