# SPEC-001 — Bridge read-only, versionada e allowlisted

**Status:** APROVADA COMO SPEC INICIAL (Q01–Q28), **POC REAL NÃO EXECUTADA**.  
**Rastreabilidade:** DEC-003/011/012/099/100; ADR-0108; Q01/02/03/04/05/10/11.

## Objetivo / escopo

- BG2:EE vanilla Windows instalado localmente; EEex loader da versão pinada no manifesto.
- Backend synthetic stub isolado do jogo, não confere capability real.
- P0 manifesto, P1 EEex loader, P2 read-only, P4 host+2 clientes com save/load.
- Não modificar flags, entregar itens ou NPCs.

## Requisitos EARS

- REQ-BRIDGE-001: QUANDO conectar a uma sessão, DEVERÁ validar build fingerprint, modpack hash, versão do adapter e host epoch; incompatibilidade → `BLOCKED_CAPABILITY`.
- REQ-BRIDGE-002: QUANDO uma consulta read-only autorizada for feita, DEVERÁ retornar envelope tipado, provenance, coverage e valor observado ou `UNKNOWN`.
- REQ-BRIDGE-003: SE uma chamada tentar modificar quest/script/inventário, DEVERÁ rejeitar sem tocar o host.
- REQ-BRIDGE-004: QUANDO um dado revelar spoiler/segredo, DEVERÁ filtrar por ACL e finalidade antes de divulgação.
- REQ-BRIDGE-005: QUANDO bridge/LLM cair, NÃO DEVERÁ converter ausência de dados em afirmação de estado.

## Critérios de aceite

1. Cenário sintético com dados válidos e validação dos requisitos.
2. Cenário adversarial com `UNKNOWN` / usuário não autorizado / divergência de época.
3. Evidência **real** somente após gate correspondente, build registrada, dois clientes quando necessário, save descartável e zero mutação não autorizada.
4. Verificação de proteção de secrets, logs, copyright e rollback.

## Não objetivos da primeira implementação

Não substituir o jogo, não alterar quest original arbitrariamente, não invocar LLM para decidir host state, não afirmar hooks existentes sem POC.
