# Tasks — SPEC-005

- [x] Definir tipos e payloads com schema versionado (SPEC-005) — `canon_entry_v1.schema.json`, `knowledge/sources/*.json`, inventário `infinity-ai.area-inventory.v1`.
- [x] Implementar casos sintéticos de aceite e ataques (SPEC-005) — `tests/test_gamedata.py`, `tests/test_canon.py`.
- [x] Integrar componente isolado sem escrita em BG2:EE (SPEC-005) — leitura KEY/BIFF/WMP/TLK da instalação local; nomes de área no diálogo.
- [x] Documentar estados UNKNOWN/erro/fallback e rollback (SPEC-005) — `estados-e-fallback.md`.
- [ ] Executar POC real em ambiente pinado e registrar evidência — **inventário real e primeiro lote de curadoria no laboratório ARM64** ([evidência](../../docs/evidence/S1c-2026-11-09-laboratorio-arm64.md)); curadoria dos livros e Windows nativo pendentes.
- [x] Curadoria: primeiro lote conferido pelo mantenedor (Athkatla, Amn, Conselho dos Seis, Ladrões das Sombras, Magos Encapuzados; ano da campanha = 1369 DR por decisão de 2026-11-09).
- [x] Segundo lote conferido (Tethyr com Saradush ligada à build, fim das Guerras de Reconquista, navios Vemmil, retorno dos exilados); FR3e brasileiro legível registrado.
- [ ] Próximos lotes: famílias/casas mercantis (*Lands of Intrigue*), Costa da Espada; confirmação bibliográfica.
- [x] `access_scope` revisado: 6 entradas `COMMON_REGIONAL`, 4 `CANON_REFERENCE`; Copper Coronet (`AR0406`) ligada a Athkatla/Amn (ADR-0114).
- [ ] REQ-CANON-003 (eventos pessoais N1/N2) e escolha da segunda região.
- [ ] Revisão de segurança, privacidade, licença e aprovação de merge.
