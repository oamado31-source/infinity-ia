# SPEC-004 — Diálogo por texto: fluxo, estados, falhas e limites (etapa 1, single player)

**Status:** parte de texto implementada em `src/infinity_ai/dialogue/` com overlay Windows (`tools/windows-overlay/`) e serviço de laboratório (`tools/windows-lab/dialogue_service.py`). **Voz (REQ-VOICE-001..003) ainda não implementada.** Single player; não é evidência de multiplayer.

## Fluxo

1. O overlay (PowerShell + WPF, sempre por cima) pede `GET /v1/state` a cada 5 s e mostra área e companheiros presentes.
2. O jogador escolhe um companheiro e digita (≤ 500 caracteres). `POST /v1/dialogue` com token de sessão.
3. O serviço usa o ramo e o tempo de jogo da **última observação do jogo** (nunca valores enviados pelo jogador).
4. `build_context`: só companheiros presentes no grupo atual; fatos = `recall(npc, ramo, tempo, purpose=npc_dialogue, audience=NARRATIVE_CONTEXT)` renderizados como `F1..Fn`, com nomes de área curados (código nunca vai ao texto).
5. Prompt: regras + persona + fatos no papel `system`; texto do jogador **sempre** como `user`.
6. Modelo local (Ollama, `qwen3:30b-a3b` desde o CR-2026-007, `think: false`, resposta em JSON com schema). O `qwen3:8b` continua aceito com `--model` para máquinas com menos memória.
6a. Na caixa do jogo (ADR-0123), os últimos turnos da conversa em andamento entram como mensagens `user`/`assistant` antes da pergunta atual. Ficam só na memória do serviço e são descartados quando a caixa é reaberta ou o serviço reinicia.
7. Validação; se falhar, uma nova tentativa com o motivo; se falhar de novo, fala de reserva da persona.
8. Resposta ao overlay. Nada é escrito no jogo, na memória do NPC ou em disco; o console do serviço registra só metadados (NPC, status, motivo, nº de fatos, `unknown`, latência, flags).

## Estados

| Status | Motivo | Quando |
|---|---|---|
| `OK` | `OK` | resposta validada |
| `FALLBACK` | `VALIDATION_FAILED` | duas respostas recusadas pela validação |
| `FALLBACK` | `MODEL_UNAVAILABLE` | modelo fora do ar, timeout ou resposta inutilizável |
| `DENIED` | `BAD_INPUT` | texto vazio ou longo demais, NPC mal formado |
| `DENIED` | `NPC_NOT_PRESENT` | NPC fora do grupo atual no ramo ativo |
| `DENIED` | `PARTY_UNKNOWN` / `UNKNOWN_TIME` / `UNKNOWN_BRANCH` | sem observação suficiente |
| `DENIED` | `NO_OBSERVATION` | (serviço) jogo no menu, carregando ou fechado |

## Validação da saída (risco baixo: fala de personagem)

Recusa: JSON fora do formato; fala vazia ou > 400 caracteres; `used_facts` com ids que não foram fornecidos; códigos crus (`AR0602`, ids internos, `npc:`); metalinguagem (modelo de linguagem, prompt, sistema, IA); marcação; **nomes próprios fora do vocabulário do contexto** (persona, grupo, nomes de área). O NPC pode repetir nomes que o próprio jogador escreveu, com ou sem `unknown` (CR-2026-008), nunca outros. Se o nome não está em nada do que ele sabe, a fala precisa dizer que não conhece a pessoa, mandar perguntar a outro, recusar o assunto ou ser opinião ("Rogê Galê? Nunca ouvi falar."); "Ah, o Galê está na taverna." é recusada (`THIRD_PARTY:STRANGER`).

**Limites conhecidos (não detectados):**
- nome inventado no **início** de frase (não dá para separar de palavra comum sem dicionário);
- afirmações sem nome próprio que não estão nos fatos (ex.: "a masmorra é cheia de monstros");
- enfeites de personalidade ("comer doces").
A validação reduz invenção e vazamento; não prova que cada frase é verdadeira (ADR-0055: risco baixo, sem segundo LLM por interação, ADR-0059 item 7).

## Segurança

- Serviço ligado só em `192.168.150.1` (rede NAT do VMware), token aleatório por execução comparado em tempo constante, corpo ≤ 4 KB, sem endpoints de escrita.
- Contexto montado **depois** da ACL (REQ-VOICE-005): memória `HOST_ONLY` ou de outro NPC/ramo nunca chega ao prompt.
- Texto do jogador é dado não confiável: não altera regras, não aciona nada no jogo; pedidos de "ignorar regras" são só fala.
- Sem provedor remoto (ADR-0106 exige opt-in próprio).

## Fallback e rollback

- Modelo fora → fala de reserva imediata; jogo e gravação seguem.
- Jogo fora de observação → `DENIED NO_OBSERVATION`; o overlay mostra "Jogo não observado agora".
- Rollback: fechar o overlay e o serviço; reverter a PR. Não há dados novos a migrar.
