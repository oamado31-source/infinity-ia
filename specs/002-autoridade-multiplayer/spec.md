# SPEC-002 — Autoridade host e dois clientes

**Status:** APROVADA COMO SPEC INICIAL (Q01–Q28), **POC REAL NÃO EXECUTADA**.  
**Rastreabilidade:** DEC-001/011/012/041–046/053/057/058; ADR-0108/0110; Q05/09/25/28.

## Objetivo / escopo

- Game native coop private host and two clients.
- Testes de consentimento por PC, dispensa de ação e retry sem duplicação.
- POCs multiplayer pendentes em todas as builds.

## Requisitos EARS

- REQ-AUTH-001: QUANDO um PC solicitar efeito mecânico, DEVERÁ existir consentimento do titular e aprovação do host por capability.
- REQ-AUTH-002: QUANDO um receipt repetir action_id, DEVERÁ ser deduplicado.
- REQ-AUTH-003: SE branch ou epoch divergir, DEVERÁ bloquear a propagação e solicitar reconciliação.
- REQ-AUTH-004: QUANDO houver save/load ou reconexão, os dois clientes DEVERÃO comparar estado confirmado sem revelar segredos privados.

## Critérios de aceite

1. Cenário sintético com dados válidos e validação dos requisitos.
2. Cenário adversarial com `UNKNOWN` / usuário não autorizado / divergência de época.
3. Evidência **real** somente após gate correspondente, build registrada, dois clientes quando necessário, save descartável e zero mutação não autorizada.
4. Verificação de proteção de secrets, logs, copyright e rollback.

## Não objetivos da primeira implementação

Não substituir o jogo, não alterar quest original arbitrariamente, não invocar LLM para decidir host state, não afirmar hooks existentes sem POC.
