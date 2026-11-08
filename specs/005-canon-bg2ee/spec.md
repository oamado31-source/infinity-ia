# SPEC-005 — Pacote canônico regional BG2:EE

**Status:** APROVADA COMO SPEC INICIAL (Q01–Q28), **POC REAL NÃO EXECUTADA**.  
**Rastreabilidade:** DEC-009/023/025/026/060–063/096–098; ADR-0109; Q14/16/18/19/27.

## Objetivo / escopo

- Recorte inicial: 1369 DR, Athkatla e áreas BG2:EE confirmadas por inventário.
- Segunda região de Q16 pendente de escolha após inspeção do mapa; não inventar cobertura.
- O usuário poderá propor enredo paralelo, a ser documentado como feature após escopo.

## Requisitos EARS

- REQ-CANON-001: QUANDO evento histórico for considerado, DEVERÁ coincidir ano DR, região e fonte curada; ausência de evidência → UNKNOWN.
- REQ-CANON-002: QUANDO a região não estiver mapeada na build inicial, NÃO DEVERÁ materializar consequências do motor.
- REQ-CANON-003: QUANDO evento pessoal for proposto, DEVERÁ ser opcional N1/N2, sem assumir protagonista clássico ou resultado irreversível.
- REQ-CANON-004: SE usar recursos protegidos, DEVERÁ referenciar instalação local, sem copiar para o repo.

## Critérios de aceite

1. Cenário sintético com dados válidos e validação dos requisitos.
2. Cenário adversarial com `UNKNOWN` / usuário não autorizado / divergência de época.
3. Evidência **real** somente após gate correspondente, build registrada, dois clientes quando necessário, save descartável e zero mutação não autorizada.
4. Verificação de proteção de secrets, logs, copyright e rollback.

## Não objetivos da primeira implementação

Não substituir o jogo, não alterar quest original arbitrariamente, não invocar LLM para decidir host state, não afirmar hooks existentes sem POC.
