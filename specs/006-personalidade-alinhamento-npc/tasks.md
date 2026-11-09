# Tasks — SPEC-006

- [x] Publicar proposta de matriz P1–P4, alinhamento 3x3 e referência aos ADRs existentes (documentação de proposta).
- [x] Criar gerador puro e exemplo de snapshot `infinity-ai.personality.v1`.
- [x] Cobrir reprodução por seed/identidade, seis traços, nove alinhamentos, pesos inválidos e recusa de origem canônica com testes sintéticos.
- [ ] Aprovar ADR-0115 e calibrar pesos/limiares de design com mantenedor (não inferir aprovação pelo PR).
- [x] Implementar atribuição append-only/idempotente via eventos existentes da SPEC-003 **para identidades já verificadas por evidência sintética**; schema JSON formal e prova real da identidade permanecem pendentes.
- [x] Testar sinteticamente reabertura de DB e forks antes/depois da atribuição, sem confundir perfis entre ramos.
- [ ] Curar personalidade e alinhamento de NPCs oficiais com referência conferida e compatibilidade de classe.
- [x] Integrar perfil-base em um **diálogo genérico de laboratório separado** (texto, estilo, alinhamento inicial, fatos vazios, validador e fallback), sem substituir o DialogueEngine da party.
- [ ] Integrar estado dinâmico, crenças e reações à SPEC-004 após aquisição legítima de fatos e memória individual.
- [ ] Implementar avaliação contextual e auditável da evolução (ADR-0030–0032); preservar `engine_alignment` até autorização/POC.
- [x] Implementar `FirstContactService` e rota experimental `/v1/encounter-dialogue` com evento gravado e sessão observada.
- [ ] Desenvolver POC do clique em qualquer ator do BG2:EE (inclusive NPC sem diálogo nativo), identidade/instância e geração real de `NpcDialogueStarted`.
- [ ] Executar teste real em laboratório BG2:EE e publicar evidência de interação com pessoas comuns, sem afetar diálogos originais.
