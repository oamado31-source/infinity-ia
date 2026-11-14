# CR-2026-009 — A pergunta do jogador repetida não é afirmação sobre si

**Status:** APPROVED (mantenedor, 2026-11-14)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-14

## Motivo e contexto

**Bateria de fala (2026-11-14, `qwen3:30b-a3b`):** à pergunta "Você trabalha aqui?", o modelo costuma começar repetindo-a: "Trabalho aqui? Não, só passo por aqui." As regras do ADR-0120 e do CR-2026-005 liam "Trabalho aqui" como afirmação e recusavam com `SELF_CLAIM:WORK`. Duas recusas seguidas levavam à fala de reserva; o caso `sem-staff-trabalho` falhou numa rodada por isso.

**Decisão do mantenedor:** corrigir o falso alarme (pedido em 2026-11-14).

## DEC/ADR/SPEC/REQ afetados

- ADR-0120 (afirmações sobre a própria origem) e CR-2026-005 (trabalho no lugar pelo nome): ajustados por este CR; o ADR permanece inalterado.

## Diff proposto e impacto no comportamento

- **`dialogue/validate.py`, `_stated`:** uma afirmação sobre si (`AWAY`, `HOME`, `BORN`, `WORK`, inclusive "trabalho na Coroa de Cobre") seguida logo de "?", com no máximo duas palavras antes dela na frase, é a pergunta repetida e não conta.
- **Continua recusado:** "Trabalho aqui, não é?", "Você sabia que eu trabalho aqui?" e uma afirmação depois da pergunta repetida ("Trabalho aqui? Sim. Trabalho aqui.").
- **Testes de fala:** as expressões regulares de `sem-staff-trabalho` e `viajante-nao-mora` também ignoram a pergunta repetida.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Pergunta retórica afirmativa:** "Trabalho aqui? Claro." passa a ser aceita, embora afirme. A resposta seguinte ("Claro") não é lida pelas regras de padrão.
- Sem dados do jogo, sem dependência nova.

## Migração e rollback

Sem migração. Rollback: voltar às chamadas `_AWAY_CLAIM.search(...)`, `_HOME_CLAIM.search(...)`, `_BORN_CLAIM.search(...)` e `_WORK_CLAIM.search(...)` em `_origin_contradicts` e ao `re.search` em `_works_at_place`.
