# Tarefas — SPEC-008

- [x] Estrutura do mundo (CR-2026-012): raiz `region:faerun`, regiões fora do mapa só para diálogo e viagens com o núcleo popular. `tests/test_world_root.py`.
- [ ] Curar o corpus de Athkatla em 1369 DR até a meta da fase (30 entradas e 10 relações), com conferência do mantenedor.
- [ ] Curar identidade e função dos NPCs oficiais da Coroa de Cobre, só com fatos públicos e de função (os segredos esperam a taxonomia da SPEC-009).
- [ ] Resolvedor único da projeção de conhecimento por NPC, com canal e evidência, sem mudar o comportamento (testes de equivalência).
- [ ] Eventos biográficos na curadoria de identidade, por migração versionada do schema.
- [ ] Aprendizado do NPC abordado (`DIRECT_DIALOGUE`): só a fala publicada e validada; casamento determinístico com a fala do jogador; evento idempotente; nenhum texto do jogador persistido.
- [ ] Recordação com atribuição no contexto e no validador.
- [ ] Notoriedade curada, sem rolagens e sem o nível como fator.
- [ ] Testes sintéticos dos critérios de aceite; bateria de diálogo sem regressão.
- [ ] Teste no laboratório (`lab-s1f`) e evidência.
- [ ] Revisão de segurança, privacidade, licença e aprovação de merge.
