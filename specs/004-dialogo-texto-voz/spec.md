# SPEC-004 — Diálogo contextual por texto e voz push-to-talk

**Status:** APROVADA COMO SPEC INICIAL (Q01–Q28), **POC REAL NÃO EXECUTADA**.  
**Rastreabilidade:** DEC-006/007/016/028/055/059; ADR-0106/0107; Q06/07/20/26.

## Objetivo / escopo

- Overlay/janela externa primeiro; UI nativa em experimento separado.
- Etapas: UI texto → STT/PTT offline → TTS offline → teste de UX/latência → UI nativa opcional.
- Áudio real e modelos STT/TTS ainda não integrados.

## Requisitos EARS

- REQ-VOICE-001: ENQUANTO o botão push-to-talk não estiver pressionado/ativado, microfone DEVERÁ permanecer inativo.
- REQ-VOICE-002: QUANDO o usuário falar, STT autorizado DEVERÁ produzir texto revisável, nunca comando mecânico executável.
- REQ-VOICE-003: QUANDO NPC responder, DEVERÁ haver texto e, se TTS autorizado/disponível, áudio opcional.
- REQ-VOICE-004: SE o STT/TTS/modelo falhar ou não houver hardware, diálogo por texto DEVERÁ continuar sem travar o host.
- REQ-VOICE-005: QUANDO contexto for preparado, DEVERÁ filtrar segredos pela ACL e conhecimento causal do NPC.

## Critérios de aceite

1. Cenário sintético com dados válidos e validação dos requisitos.
2. Cenário adversarial com `UNKNOWN` / usuário não autorizado / divergência de época.
3. Evidência **real** somente após gate correspondente, build registrada, dois clientes quando necessário, save descartável e zero mutação não autorizada.
4. Verificação de proteção de secrets, logs, copyright e rollback.

## Não objetivos da primeira implementação

Não substituir o jogo, não alterar quest original arbitrariamente, não invocar LLM para decidir host state, não afirmar hooks existentes sem POC.
