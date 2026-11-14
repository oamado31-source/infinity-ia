# CR-2026-008 — Nomes escritos pelo jogador valem sem a marca `unknown`

**Status:** APPROVED (mantenedor, 2026-11-14)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-14

## Motivo e contexto

**S1d (2026-11-09):** Jaheira, sem conhecimento de Amn, respondeu à pergunta "quem governa Amn?" repetindo "Amn", mas com `unknown = false`. O validador recusou (`UNKNOWN_NAMES`), e a fala caiu na reserva. Pela regra da SPEC-004, um nome que o jogador escreveu só podia ser repetido com `unknown = true`. A marca é escolha do modelo, que nem sempre a acerta.

**Brecha encontrada ao revisar a regra:** com `unknown = true`, qualquer coisa sobre o nome passava. "Ah, o Galê está na taverna." ou "Gorion é muito rico." inventavam fatos sobre alguém que o NPC não conhece.

**Decisão do mantenedor:** tirar da lista de pendências da SPEC-004 o item "aceitar nomes vindos da pergunta do jogador também quando o NPC responde sem se declarar sem conhecimento" (pedido em 2026-11-14).

## DEC/ADR/SPEC/REQ afetados

- SPEC-004, validação da saída (nomes próprios).
- ADR-0121 (afirmações sobre terceiros): ampliado por este CR; o ADR permanece inalterado.

## Diff proposto e impacto no comportamento

- **Nomes do jogador** (`dialogue/validate.py`, `player_names`): os nomes que o jogador escreveu entram no vocabulário permitido com ou sem `unknown`. Palavras de pergunta com maiúscula ("Quem", "Você", "Onde"…) não contam como nome, por uma lista curta escrita por nós.
- **Afirmações sobre esses nomes** (`dialogue/claims.py`, `third_party_claim(..., asked)`): as regras do ADR-0121 (papel, traço, número) valem também para eles. Um nome que não aparece em nada do que o NPC sabe, nem no vocabulário do contexto, é um **desconhecido**:
  - qualquer "X é o/um …" ou "X, o …" sobre ele é `THIRD_PARTY:ROLE` ("Gorion? É o mago da fortaleza.");
  - a fala que cita um desconhecido precisa dizer que não o conhece, mandar perguntar a outra pessoa, recusar o assunto ou ser opinião. Senão: `THIRD_PARTY:STRANGER` ("Ah, o Galê está na taverna."). A nova tentativa pede, em português, que o NPC diga que não conhece a pessoa.
- **Continua recusado:** nome que nem o jogador nem o contexto trouxeram (`UNKNOWN_NAMES`).
- **Com `unknown = true`:** passa a valer a mesma regra, o que é mais estrito que antes (a brecha acima fecha).
- **Testes de fala:** novo caso `nome-desconhecido-do-jogador` ("Você viu o Gorion por aqui?"): o NPC responde sem reserva e sem inventar nada sobre Gorion.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Afirmações sem padrão:** uma fala que admite não saber e, na mesma resposta, afirma algo sobre o desconhecido fora dos padrões ("Gorion? Não sei. Mas saiu cedo.") ainda passa. Antes, com `unknown = true`, passava tudo.
- **Recusas a mais:** uma resposta boa sem as palavras de ignorância da lista pode ser recusada e ir à nova tentativa.
- Sem dados do jogo, sem dependência nova.

## Migração e rollback

Sem migração. Rollback: voltar `vocabulary = context.vocabulary | (player_names(player_text) if unknown else frozenset())` em `validate_reply` e chamar `third_party_claim` sem `asked`.
