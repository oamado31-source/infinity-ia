# ADR-0107 — Interface de diálogo independente com voz bidirecional opcional

**Estado:** APROVADA COMO POLÍTICA / ESCOPO em 2026-11-07, com base no questionário Q01–Q28 ratificado pelo idealizador.  
**Decisões:** DEC-007, DEC-016 / Q07=B, Q20=B e observações. **Baseline:** Discovery v10.6 → SDD v11.0.  
**Referências anteriores:** DEC-007/014/016/028/041–046/055; Q07, Q20, Q26.  
**Gate:** documentação é política aprovada, **não uma capability comprovada no BG2:EE/EEex**.

## Contexto e alternativas

O questionário consolidado registrou escolhas explícitas para evitar bloqueio indefinido do Discovery. A opção escolhida não elimina mecanismos de segurança nem substitui ADRs anteriores: ela restringe a estratégia de implementação do MVP e da V1.

## Decisão vinculante

1. UI inicial em overlay ou janela externa; interface nativa só após POC do hook da build.
2. Texto sempre disponível e acessível; **push-to-talk** opcional (tecla configurável): jogador fala → STT local autorizado → texto mostrado para revisão → agente NPC produz resposta → resposta textual com TTS opcional.
3. Voz **não é obrigatória para a primeira gate de bridge**: adicionar STT/TTS sem bloquear observação read-only; Q07/Q20 ambas B com adendo expresso do usuário.
4. Microfone inativo por padrão; ativação humana, indicador perceptível, cancelamento, não gravar em repouso, política de retenção por campanha; remoto apenas com consentimento DEC-006.
5. A fala não inventa estado de quest, consentimento, comando ou conhecimento; narrator LLM e playback isolados do Action Gateway. 
6. Logs guardam apenas prova e metadados minimizados, não transcrições privadas em claro por padrão; modo texto mantém fallback. 

## Consequências

- Requisitos nas SPECs devem citar este ADR e a pergunta de origem, com critério de aceite observável.
- Recursos mecânicos dependem de capability verificada na build do host, consentimento, idempotência e recibos; caso contrário `UNKNOWN` ou `BLOCKED_CAPABILITY`.
- Qualquer modificação material desta política deverá criar um ADR novo, mantendo este arquivo inalterado.
- Testes unitários sintéticos nunca serão descritos como validação de bridge, jogo ou multiplayer real.
