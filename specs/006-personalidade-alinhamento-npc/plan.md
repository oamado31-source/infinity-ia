# Plano — SPEC-006 (personalidade e alinhamento de NPCs)

1. Registrar a matriz HEXACO fictícia, os 9 alinhamentos AD&D e sua separação de reputação, estado e motor (ADR-0115).
2. Criar protótipo de gerador Python determinístico e teste sintético: identidade/seed, seis traços, nove alinhamentos e distribuição ponderada.
3. Definir contrato v1 e exemplo de snapshot em `templates/npc-personality-v1.example.json`.
4. Revisar ADR-0115 com mantenedor; definir distribuições e restrições de geração autorizadas.
5. Implementar persistência do snapshot em campanha/ramo, idempotência, herança de fork, versionamento e ACL (SPEC-003).
6. Adicionar perfis oficiais **somente** com fonte/curadoria (SPEC-005), sem substituir seu comportamento nativo.
7. Integrar perfil filtrado ao contexto SPEC-004, mantendo observação e conhecimento legítimos; regras de reações determinísticas primeiro.
8. Testar reações divergentes ao mesmo evento observado, contradições, reload/fork, limites mecânicos, carga/performance e POC single player.

**Não objetivos desta entrega:** psicometria real, inventário HEXACO-PI-R, modificação de BG2:EE, agente LLM por NPC, alinhamento mecânico automático, comportamento canônico alterado.
