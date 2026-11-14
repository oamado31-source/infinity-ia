# Tasks — SPEC-004

- [x] Definir tipos e payloads com schema versionado (SPEC-004) — `src/infinity_ai/dialogue/` (contexto, resposta JSON do modelo, `DialogueResponse`).
- [x] Implementar casos sintéticos de aceite e ataques (SPEC-004) — `tests/test_dialogue.py` (modelo falso; sem Ollama no CI).
- [x] Integrar componente isolado sem escrita em BG2:EE (SPEC-004) — serviço de diálogo + overlay Windows (texto).
- [x] Documentar estados UNKNOWN/erro/fallback e rollback (SPEC-004) — `estados-e-fallback.md`.
- [ ] Executar POC real em ambiente pinado e registrar evidência — **S1b (diálogo por texto) executada em single player no laboratório ARM64** ([evidência](../../docs/evidence/S1b-2026-11-09-laboratorio-arm64.md)); voz (REQ-VOICE-001..003) e Windows nativo pendentes.
- [x] Caixa de diálogo dentro do jogo para falar com qualquer pessoa (ADR-0116): `tools/eeex-probe/M_INFAIT.lua` + `INFAITLK.menu`, protocolo `src/infinity_ai/bridge/talk.py`, resposta por `override/INFAIRSP.lua`; testes sintéticos e estáticos. POC no laboratório pendente.
- [x] Caixa no jogo: abrir com o clique direito sobre a pessoa (F9 continua como alternativa) e pausar o jogo enquanto está aberta, como no diálogo nativo (pedido do mantenedor, 2026-11-10); laboratório pendente.
- [x] Validador: aceitar nomes vindos da pergunta do jogador também quando o NPC responde sem se declarar sem conhecimento (evidência S1d) — [CR-2026-008](../../docs/change-requests/CR-2026-008-nomes-escritos-pelo-jogador.md), com recusa de afirmações sobre quem o NPC não conhece.
- [x] Validador: afirmações sobre outras pessoas (papel, traço, número, regra geral) precisam estar no conhecimento de quem fala; opinião própria passa (ADR-0121); `tests/test_third_party.py`. Testado no laboratório S1f em 2026-11-13, com a segunda tentativa explicada em português.
- [x] Memória da conversa enquanto a caixa está aberta (ADR-0123): últimos 4 turnos só na RAM do serviço, como turnos de chat; `tests/test_conversation.py`. Testado no laboratório S1f em 2026-11-13.
- [x] Conjunto fixo de testes de fala com o modelo local (`tools/dialogue-eval/`, 3 rodadas, 2 acertos); no CI só a forma dos casos e o verificador (`tests/test_dialogue_eval.py`).
- [x] Lembrança de conversas anteriores sem texto (ADR-0124): quantas, quando e assuntos, por ramo; genéricos só na mesma sessão; companheiros dizem de quem ouviram (INQUIRY). Testado no laboratório S1f com Bernard e Jaheira; o genérico por sessão está coberto só pelos testes sintéticos.
- [ ] Voz: push-to-talk + STT local revisável, TTS opcional (ADR-0107 item 2), depois da UI de texto. A caixa do jogo já reserva o botão "aperte para falar" e o campo `input` (`VOICE`).
- [ ] Revisão de segurança, privacidade, licença e aprovação de merge.
