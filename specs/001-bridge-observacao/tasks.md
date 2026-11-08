# Tasks — SPEC-001

- [x] Definir tipos e payloads com schema versionado (SPEC-001) — `src/infinity_ai/bridge/domain.py`, `schemas/observation_envelope_v1.schema.json`, `schemas/build_manifest_v1.schema.json`.
- [x] Implementar casos sintéticos de aceite e ataques (SPEC-001) — `tests/test_bridge_spec001.py` (sintéticos; não são evidência P0–P4).
- [x] Integrar componente isolado sem escrita em BG2:EE (SPEC-001) — `ReadOnlyBridge` + `SyntheticAdapter`; nenhum adapter real.
- [x] Documentar estados UNKNOWN/erro/fallback e rollback (SPEC-001) — `estados-e-fallback.md`.
- [ ] Executar POC real em ambiente pinado e registrar evidência (P0–P4) — **P0, P1 e P2 aprovados no laboratório ARM64/VM** ([P0](../../docs/evidence/P0-2026-11-08-laboratorio-arm64.md), [P1](../../docs/evidence/P1-2026-11-08-laboratorio-arm64.md), [P2](../../docs/evidence/P2-2026-11-08-laboratorio-arm64.md)); P4 NÃO EXECUTADO; P0–P2 nativos pendentes.
- [x] Adapter read-only real (P2): probe `tools/eeex-probe/` + `src/infinity_ai/bridge/eeex_log.py`; testes `tests/test_eeex_probe.py` e `tests/test_eeex_log_adapter.py`.
- [ ] Revisão de segurança, privacidade, licença e aprovação de merge.
