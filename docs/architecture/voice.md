# Architecture — Voice UX (Q07 + Q20 ratificadas)

**Fluxo desejado:** controle push-to-talk → captação consciente → STT local → preview texto → resposta NPC filtrada por ACL → UI texto → TTS local opcional → áudio. Texto funciona sem som.

**Requisitos**
- Sempre mostrar estado do microfone e oferecer botão de parada/cancelamento. Não gravar continuamente.
- STT e TTS não executam comandos do jogo; transcrição é input não confiável, inclusive em ataques de prompt injection.
- Sem mic, TTS, hardware ou permissão: resposta textual sem bloqueio do jogo.
- Modelo/voz e runtime ainda por selecionar; medir RAM/latência, suporte PT-BR/EN e qualidade.
- NPC não recebe eventos privados/salvos fora de ACL ou sua cadeia causal de conhecimento.
- Fase 1: overlay texto e mocks; Fase 2: STT/TTS local com texto; Fase 3: avaliação de UI nativa se engine suportar.
