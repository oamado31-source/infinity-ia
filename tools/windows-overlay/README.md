# Overlay de diálogo (Windows) — SPEC-004, ADR-0107

Janela WPF sempre por cima do jogo, feita só com PowerShell e .NET do Windows (nada a instalar). Cliente fino: mostra a área e os companheiros presentes, envia o texto ao serviço de diálogo e exibe a resposta. Não toca no jogo e não grava nada em disco; o histórico some ao fechar.

- **Configuração:** `%LOCALAPPDATA%\InfinityAI\overlay.json` com `url` e `token` (gerado pelo serviço a cada execução; use `--reuse-token` para manter).
- **Abrir:** duplo clique em `Start-InfinityOverlay.cmd`.
- **Jogo em tela cheia esconde o overlay:** use modo janela ou janela sem borda (Alt+Enter nas Enhanced Editions).
- **Mensagens:** `[resposta de reserva: ...]` indica fala de reserva (validação recusou ou modelo fora); "(não foi possível falar com ...)" indica negação (NPC fora do grupo, jogo não observado).

Serviço: `tools/windows-lab/dialogue_service.py`. Estados e limites: `specs/004-dialogo-texto-voz/estados-e-fallback.md`.
