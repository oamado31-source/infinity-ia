# CR-2026-003 — Reordenar o desenvolvimento: single player primeiro, multiplayer na etapa 2

**Status:** APPROVED (mantenedor, 2026-11-08)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-08

## Motivo e contexto

Pedido do mantenedor: implementar e testar tudo em single player e integrar o multiplayer numa segunda etapa. Contexto técnico: P0–P2 aprovados no laboratório (CR-2026-001); o P4 exige segunda licença, segunda VM e esbarra na limitação do EEex em multiplayer (Bubb13/EEex#37). Decisão registrada no ADR-0113.

## DEC/ADR/SPEC/REQ afetados

- ADR-0001 item 1 e ADR-0108 itens 1, 2 e 5: substituídos parcialmente pelo ADR-0113 (ADRs antigos inalterados).
- SPEC-002: movida para a etapa 2.
- SPEC-001, SPEC-003, SPEC-004, SPEC-005: etapa 1, com testes reais em single player.
- `docs/architecture/roadmap.md`, `docs/architecture/testing.md`, `docs/architecture/context.md`, `docs/domain/context.md`, `docs/114-matriz-de-rastreabilidade-sdd.md`, `README.md`, `README-SDD.md`, `specs/002-autoridade-multiplayer/spec.md`.

## Diff proposto e impacto no comportamento

- Roadmap: etapa 1 single player (SPEC-001 → 003 → 004 → 005), etapa 2 multiplayer (SPEC-002, P4a/P4b).
- Gate P4 marcado como adiado para a etapa 2; nova linha de critério da etapa 1 em single player.
- Nenhuma mudança de código nem de schema. Os contratos continuam com host, PC, campanha, branch e época (ADR-0113 item 4).

## Riscos/ameaças, licenças, dados privados e compatibilidade

- Descobrir problemas de sincronização só na etapa 2; mitigado por contratos já preparados para coop e pela proibição de atalhos de single player.
- Nenhum novo dado privado, licença ou dependência.

## Migração e rollback

Sem migração. Rollback: novo ADR que restaure a ordem do ADR-0108; os ADRs antigos seguem intactos.

## Testes de regressão e evidência

Somente documentação: `scripts/check_historical_adrs.py` (ADRs antigos inalterados), suíte sintética e `scripts/check_public_files.py`.

## Aprovação do mantenedor / ADR substituto quando necessário

Aprovado pelo mantenedor em 2026-11-08 (pedido explícito na sessão de desenvolvimento). ADR: ADR-0113.
