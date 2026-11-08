# Architecture — Estratégia de testes (SPEC/POC)

| Gate | Ambiente | Critério de aceite | Situação atual |
|---|---|---|---|
| P0 | BG2:EE limpo, Windows | manifesto, teste base e save descartável | APROVADO no laboratório ARM64/VM em 2026-11-08 ([evidência](../evidence/P0-2026-11-08-laboratorio-arm64.md), CR-2026-001); NÃO EXECUTADO em Windows x86-64 nativo |
| P1 | EEex pinado | loader inicializa sem falhas na build | APROVADO no laboratório ARM64/VM em 2026-11-08 com EEex v1.3.1 Minimal ([evidência](../evidence/P1-2026-11-08-laboratorio-arm64.md), CR-2026-001); NÃO EXECUTADO em Windows x86-64 nativo |
| P2 | Bridge read-only | dados allowlisted, UNKNOWN, nenhuma escrita | NÃO EXECUTADO |
| P3 | Mutação opcional isolada | autorização+receipt+rollback em save descartável | NÃO EXECUTADO |
| P4 | Host + 2 clientes | consistência após save/load/reconnect, logs, sem desync | NÃO EXECUTADO |

**Testes de Python em CI:** somente sintéticos; não contam como P0–P4. Todo relatório deve registrar resultado, comando, ambiente, data, SHA, build e evidência.

- Unit test para regras puras com dados sintéticos e cenários adversariais.
- Contract test dos JSON envelopes e estados.
- Regression tests dos 100+ ADRs e snapshots relevantes.
- Integração somente com instalações autorizadas de BG2:EE/EEex; nunca em save real sem permissão.
- Voz: mic inativo default, push-to-talk, fallback texto, STT indisponível, TTS indisponível, permissão revogada, latência e sem retenção involuntária.
- PR checks: unittest+syntax/JSON+ADR append-only+arquivo proibido/segredo, sem credenciais de escrita.
