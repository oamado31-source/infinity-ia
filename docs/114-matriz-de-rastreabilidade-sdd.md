# Matriz inicial de rastreabilidade SDD

| Fonte aprovada | ADR de operacionalização | SPEC | Critério / Gate |
|---|---|---|---|
| Q01–Q05, Q11, Q28 | ADR-0108 | SPEC-001/002/003 | P0–P4; 2 clientes read-only/save-load |
| Q06 | ADR-0106 | SPEC-004 | local-first, opt-in remoto |
| Q07/Q20 | ADR-0107 | SPEC-004 | overlay texto; push-to-talk STT/TTS planejado |
| Q08/Q09/Q10/Q15/Q24/Q25/Q26 | ADR-0110 | SPEC-002/003 | SQLite, ACL, recibo, logs, LAN local |
| Q12 | ADR-0111 | Todas | CR + diff + teste + aprovação |
| Q14/Q16/Q19/Q27 | ADR-0109 | SPEC-005 | 1369 DR, BG2EE mapas validados, sem assets distribuídos |
| Decisão do mantenedor (2026-11-08) | ADR-0113 / CR-2026-003 | SPEC-001/003/004/005 (etapa 1), SPEC-002 (etapa 2) | S1 single player antes de P4 |
| Decisão do mantenedor (2026-11-09) | ADR-0114 | SPEC-003/004/005 | S1d: conhecimento comum regional só por canal legítimo |
| Solicitação do mantenedor (2026-11-09; proposta) | ADR-0115 (PROPOSTO), ADR-0030–0032/0042/0062 | SPEC-006 + integração futura SPEC-003/004/005 | Gerador e primeiro contato sintéticos; alinhamento 3x3; persistência via evento para identidade verificada; clique in-game/POC pendentes |
| Q13/Q17/Q18/Q21/Q22/Q23 | ADRs anteriores + roadmap | Backlog futuro | Capabilities específicas pendentes |

**Estratégia de repositório independente vs fork:** `docs/architecture/repository_strategy.proposed.md` — recomendação em discussão, não ratificada como ADR.
