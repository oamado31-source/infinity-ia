# Plano de implementação — SPEC-008

**Ordem do CR-2026-011:** a divulgação por item (SPEC-009) vem antes do aprendizado. O aprendizado precisa saber o que o NPC pode retransmitir.

1. **Curadoria em paralelo** (fase de corpus):
   - meta de Athkatla em 1369 DR, por exemplo 30 entradas e 10 relações, cada uma com resumo próprio de até 280 caracteres e conferência do mantenedor;
   - lote da Coroa de Cobre para identidade e biografia: primeiro os fatos públicos e de função; os segredos esperam a taxonomia de sigilo da SPEC-009.
2. **Projeção de conhecimento por NPC:**
   - um resolvedor único reúne o que hoje vem de `ORIGIN`, `RESIDENCE`, `INQUIRY` e das relações por afiliação, com o canal e a evidência de cada item;
   - nada muda no comportamento, só a forma auditável (refatoração com testes de equivalência).
3. **Biografia:** campo de eventos biográficos na curadoria de identidade, por migração versionada do schema `npc-identity-curation`, com respaldo obrigatório para os oficiais.
4. **Aprendizado do NPC abordado** (depois da SPEC-009, fase 5):
   - estender `memory/common_knowledge.py` (`mentioned_in`, `share_knowledge`) para ter o próprio NPC abordado como ouvinte;
   - **fala do NPC:** só o que foi dito e validado;
   - **fala do jogador:** casamento determinístico com entradas curadas e falha fechada;
   - evento novo, só acrescentado (append-only) e idempotente por fala, ouvinte, entrada e ramo;
   - na v1, nenhum texto do jogador persistido.
5. **Recordação:** o contexto do NPC inclui o que ele aprendeu, com a atribuição. O validador aceita "você me contou" ou "Bernard me disse" só para entradas aprendidas.
6. **Notoriedade curada** (fase 4a): registros de persona e feitos públicos como entradas do pacote, sem rolagens. "Você conhece X?" consulta só o que o NPC tem.
7. **Validação:** testes sintéticos dos critérios de aceite; bateria de diálogo; laboratório na campanha `lab-s1f`, com o manifesto fixado de novo se a caixa mudar.
