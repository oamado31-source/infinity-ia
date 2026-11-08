# SPEC-003 — SQLite, eventos e memória contextual

**Status:** APROVADA COMO SPEC INICIAL (Q01–Q28), **POC REAL NÃO EXECUTADA**.  
**Rastreabilidade:** DEC-008/018/028/053/060/064–066; ADR-0110; Q08/10/15/24.

## Objetivo / escopo

- SQLite local por campanha, migrations registradas, backups e event log append-only.
- Sem plaintext de segredos e transcrições por padrão.
- Regra sintética testável; persistência real após schema/benchmark.

## Requisitos EARS

- REQ-STATE-001: QUANDO evento narrativo confirmado for registrado, DEVERÁ ter campaign_id, branch_id, epoch e idempotency key.
- REQ-STATE-002: QUANDO um save for restaurado, DEVERÁ preservar linha antiga e criar reconciliação, sem reescrita de evidência anterior.
- REQ-MEM-001: SE o NPC solicitar recordação, DEVERÁ recuperar apenas fatos permitidos pela ACL, tempo e proveniência.
- REQ-MEM-002: QUANDO uma correção chegar, DEVERÁ separar recebimento, percepção e revisão de crença.

## Critérios de aceite

1. Cenário sintético com dados válidos e validação dos requisitos.
2. Cenário adversarial com `UNKNOWN` / usuário não autorizado / divergência de época.
3. Evidência **real** somente após gate correspondente, build registrada, dois clientes quando necessário, save descartável e zero mutação não autorizada.
4. Verificação de proteção de secrets, logs, copyright e rollback.

## Não objetivos da primeira implementação

Não substituir o jogo, não alterar quest original arbitrariamente, não invocar LLM para decidir host state, não afirmar hooks existentes sem POC.
