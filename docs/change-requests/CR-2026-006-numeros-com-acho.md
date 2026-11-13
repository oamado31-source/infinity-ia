# CR-2026-006 — Números e durações com "acho" também precisam de base

**Status:** APPROVED (mantenedor, 2026-11-13)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-13

## Motivo e contexto

**O caso:** o ADR-0121 aceita a opinião própria do NPC ("acho que…"). O conjunto de testes de fala mostrou que isso deixava passar números e durações sem base, ditos como opinião. Minsc, que só conhece o núcleo popular sobre o Conselho, disse "Conselho governa Amn há séculos, eu acho." O caso `companheiro-rudimentar-sem-duracao` caiu para 1 de 3.

**Decisão do mantenedor:** recusar números e durações ditos com "acho" quando não estão no conhecimento.

## DEC/ADR/SPEC/REQ afetados

- ADR-0121, item 1 (opinião passa): refinado por este CR, só para números e durações. O ADR permanece inalterado.
- SPEC-004 (validação da fala).

## Diff proposto e impacto no comportamento

- **Regra `THIRD_PARTY:NUMBER`** (`src/infinity_ai/dialogue/claims.py`): passa a valer mesmo em frase com marca de opinião ("acho", "dizem que", "parece").
- **Continua passando:**
  - papel, traço e regra geral ditos como opinião ("Acho que Lehtinan é um cara duro.");
  - durações vagas ("há muito tempo").
- **Testes:** em `tests/test_third_party.py`, mais o caso de Minsc no conjunto de testes de fala.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Mais segundas tentativas:** a recusa pode levar a uma segunda tentativa quando o NPC arrisca um número. A explicação em português já orienta a não dar números fora das seções.
- Nenhum dado novo, licença ou dependência.

## Migração e rollback

Sem migração. Rollback: voltar a pular frases com marca de opinião na regra `NUMBER`.
