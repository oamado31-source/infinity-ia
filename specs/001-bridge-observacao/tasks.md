# Tasks — SPEC-001

- [x] Definir tipos e payloads com schema versionado (SPEC-001) — `src/infinity_ai/bridge/domain.py`, `schemas/observation_envelope_v1.schema.json`, `schemas/build_manifest_v1.schema.json`.
- [x] Implementar casos sintéticos de aceite e ataques (SPEC-001) — `tests/test_bridge_spec001.py` (sintéticos; não são evidência P0–P4).
- [x] Integrar componente isolado sem escrita em BG2:EE (SPEC-001) — `ReadOnlyBridge` + `SyntheticAdapter`; nenhum adapter real.
- [x] Documentar estados UNKNOWN/erro/fallback e rollback (SPEC-001) — `estados-e-fallback.md`.
- [ ] Executar POC real em ambiente pinado e registrar evidência (P0–P4) — **P0 e P1 aprovados no laboratório ARM64/VM** ([P0](../../docs/evidence/P0-2026-11-08-laboratorio-arm64.md), [P1](../../docs/evidence/P1-2026-11-08-laboratorio-arm64.md)); P2 e P4 NÃO EXECUTADOS; P0/P1 nativos pendentes.
- [ ] Revisão de segurança, privacidade, licença e aprovação de merge.
