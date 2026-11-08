# Ratificação Q01–Q28 — decisões de escopo e desenvolvimento

**Data:** 2026-11-07. **Fonte:** escolhas explícitas do usuário nesta conversa. **Todas as 28 perguntas respondidas.**

| Pergunta | Escolha | Observação | Base de implementação |
|---|---|---|---|
| Q01 | **B** | — | SPEC / ADR temático conforme matriz |
| Q02 | **B** | — | SPEC / ADR temático conforme matriz |
| Q03 | **B** | — | SPEC / ADR temático conforme matriz |
| Q04 | **A** | — | SPEC / ADR temático conforme matriz |
| Q05 | **B** | — | SPEC / ADR temático conforme matriz |
| Q06 | **B** | — | SPEC / ADR temático conforme matriz |
| Q07 | **B** | Overlay; diálogo escrito e também voz bidirecional push-to-talk: jogador pressiona botão e fala, NPC responde (texto + TTS opcional). | SPEC / ADR temático conforme matriz |
| Q08 | **B** | — | SPEC / ADR temático conforme matriz |
| Q09 | **B** | — | SPEC / ADR temático conforme matriz |
| Q10 | **B** | Solicitou abrir repositório GitHub; conexão confirmada, ação de criar repo indisponível no conector atual. Política posterior: público, forks e PRs externos sem push direto. | SPEC / ADR temático conforme matriz |
| Q11 | **A** | — | SPEC / ADR temático conforme matriz |
| Q12 | **B** | — | SPEC / ADR temático conforme matriz |
| Q13 | **B** | — | SPEC / ADR temático conforme matriz |
| Q14 | **B** | — | SPEC / ADR temático conforme matriz |
| Q15 | **B** | — | SPEC / ADR temático conforme matriz |
| Q16 | **B** | Recorte por ano DR e mapas/regiões exploráveis no BG2:EE inicial; segunda região após inventário da build. | SPEC / ADR temático conforme matriz |
| Q17 | **B** | — | SPEC / ADR temático conforme matriz |
| Q18 | **B** | — | SPEC / ADR temático conforme matriz |
| Q19 | **B** | — | SPEC / ADR temático conforme matriz |
| Q20 | **B** | Voz além de texto, preservando fallback textual. STT e TTS bidirecionais após estabilidade do slice. | SPEC / ADR temático conforme matriz |
| Q21 | **B** | — | SPEC / ADR temático conforme matriz |
| Q22 | **B** | — | SPEC / ADR temático conforme matriz |
| Q23 | **B** | — | SPEC / ADR temático conforme matriz |
| Q24 | **B** | — | SPEC / ADR temático conforme matriz |
| Q25 | **B** | Servidor/LLM na máquina local, LAN/VPN autorizada. | SPEC / ADR temático conforme matriz |
| Q26 | **B** | — | SPEC / ADR temático conforme matriz |
| Q27 | **B** | Usuário pode propor enredo de evento paralelo para teste, sem alterar arcos canônicos automaticamente. | SPEC / ADR temático conforme matriz |
| Q28 | **B** | B; linha Q28 extra sem escolha foi tratada como linha vazia, não nova pergunta. | SPEC / ADR temático conforme matriz |

## Orientações adicionais

- Q07 e Q20 são B, **acrescidos da capacidade de voz falada de ida e volta**. Não reduzir a apenas TTS: capturar microfone por botão e transcrever com STT local, gerar resposta NPC e sintetizar opcionalmente com TTS; ambos sempre com versão escrita.
- Q16: começar pelo 1369 DR e mapas do BG2:EE efetivamente exploráveis, sem inventariar todo Forgotten Realms no MVP.
- Q25: o host físico fica na máquina local; multiplayer privado autenticado.
- Q27: receber futuramente enredo específico do usuário, manter campo pendente.
- Q10: não confundir logs/recuperação com política de repositório; repositório **público** decidido depois pelo usuário; estratégia de novo repositório independente ou fork permanece proposta até confirmação.
- Entrada final `Q28 -` sem alternativa ou conteúdo é interpretada como linha vazia, não uma 29ª decisão.

## Situação técnica

A ratificação define regras e backlog, mas não demonstra bridge EEex real, funcionamento de STT/TTS, distribuição de arquivos de jogo, 2 clientes ou rede. As POCs permanecem não executadas. Todos os ADRs anteriores à v10.6 devem permanecer byte a byte.
