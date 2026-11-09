# Tasks — SPEC-004

- [x] Definir tipos e payloads com schema versionado (SPEC-004) — `src/infinity_ai/dialogue/` (contexto, resposta JSON do modelo, `DialogueResponse`).
- [x] Implementar casos sintéticos de aceite e ataques (SPEC-004) — `tests/test_dialogue.py` (modelo falso; sem Ollama no CI).
- [x] Integrar componente isolado sem escrita em BG2:EE (SPEC-004) — serviço de diálogo + overlay Windows (texto).
- [x] Documentar estados UNKNOWN/erro/fallback e rollback (SPEC-004) — `estados-e-fallback.md`.
- [ ] Executar POC real em ambiente pinado e registrar evidência — **S1b (diálogo por texto) executada em single player no laboratório ARM64** ([evidência](../../docs/evidence/S1b-2026-11-09-laboratorio-arm64.md)); voz (REQ-VOICE-001..003) e Windows nativo pendentes.
- [ ] Voz: push-to-talk + STT local revisável, TTS opcional (ADR-0107 item 2), depois da UI de texto.
- [ ] Revisão de segurança, privacidade, licença e aprovação de merge.
