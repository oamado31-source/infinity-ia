# Tasks — SPEC-003

- [x] Definir tipos e payloads com schema versionado (SPEC-003) — `src/infinity_ai/state/migrations/0001_initial.sql`, `src/infinity_ai/memory/model.py`.
- [x] Implementar casos sintéticos de aceite e ataques (SPEC-003) — `tests/test_state_store.py`, `tests/test_recorder.py`, `tests/test_npc_memory.py` (sintéticos; não são evidência real).
- [x] Integrar componente isolado sem escrita em BG2:EE (SPEC-003) — `ObservationRecorder` consome envelopes da bridge read-only; probe ganhou `party.companion_ids`.
- [x] Documentar estados UNKNOWN/erro/fallback e rollback (SPEC-003) — `estados-e-fallback.md`.
- [ ] Executar POC real em ambiente pinado e registrar evidência — **S1a (persistência + memória de companheiros) executada em single player no laboratório ARM64** ([evidência](../../docs/evidence/S1a-2026-11-09-laboratorio-arm64.md)); troca de área real e Windows nativo pendentes; multiplayer na etapa 2 (ADR-0113).
- [x] Conhecimento comum regional (ADR-0114): `src/infinity_ai/memory/common_knowledge.py`, migração `0002_npc_canon_knowledge.sql`, `tests/test_common_knowledge.py` (sintéticos); mecânica executada no laboratório ([S1d](../../docs/evidence/S1d-2026-11-09-laboratorio-arm64.md)).
- [x] Canal `INQUIRY` (ADR-0116): habitantes colocados pelo jogo sabem desde o pin; `share_knowledge` ensina só os companheiros ouvintes e só as entradas usadas; companheiro não ensina companheiro. Testes sintéticos; laboratório pendente.
- [ ] `INQUIRY` por pesquisa/leitura (livros, bibliotecas) e estadias curadas de NPCs de fora do grupo para `RESIDENCE`.
- [ ] Corrigir leituras transitórias do tempo de jogo na troca de área, que hoje criam ramos falsos (evidência S1d).
- [ ] Revisão de segurança, privacidade, licença e aprovação de merge.
