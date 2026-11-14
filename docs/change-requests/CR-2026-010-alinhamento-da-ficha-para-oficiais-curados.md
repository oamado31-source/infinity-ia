# CR-2026-010 — Oficiais curados sem script name usam o alinhamento da ficha

**Status:** APPROVED (mantenedor, 2026-11-14)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-14

## Motivo e contexto

O ADR-0117 diz que personagens oficiais usam o alinhamento da ficha do jogo como orientação de fala, sem sorteio. Isso já vale para quem tem script name: Salvanas, Lehtinan e Jierdan entram como `CANONICAL`, e o serviço usa o alinhamento da ficha na orientação (`orientation_from_game_alignment`) e no teste de moral (`ethical_axis`, ADR-0126).

**Lacuna:** um oficial com curadoria conferida, mas sem script name, entra como encontro (`ENCOUNTER`) e ganha um perfil sorteado pela SPEC-006, com alinhamento sorteado que ignora a ficha. É o caso de Bernard (`npc:cre-bernard`), taverneiro da Coroa de Cobre, cuja ficha traz um alinhamento definido. O perfil sorteado tem precedência na orientação e na moral, então Bernard podia falar e reagir como leal e mau num encontro e caótico em outro.

**Decisão do mantenedor:** cumprir a tarefa da SPEC-006 "usar o alinhamento da ficha do jogo como `alignment_initial` de NPCs oficiais" (pedida em 2026-11-14).

## DEC/ADR/SPEC/REQ afetados

- SPEC-006 (`alignment_initial`) e ADR-0117 (alinhamento dos oficiais): ampliado por este CR; o ADR permanece inalterado.

## Diff proposto e impacto no comportamento

- **`personality/generator.py`:** `generate_new_npc_profile(..., fixed_alignment="LN")` usa o código dado em `alignment_initial`, com `provenance: GAME_DATA`. O sorteio continua sendo feito, para que traços, valores e impulsos fiquem iguais aos de antes.
- **`personality/first_contact.py`:** `begin(..., game_alignment=<código da ficha>)` converte o código de ALIGNMEN.IDS e o passa ao gerador, tanto no perfil de encontro quanto no persistente. Código ausente ou inválido (0, valores fora da tabela) mantém o sorteio. Um perfil persistente já atribuído não muda (append-only).
- **`personality/in_game.py`, `profile_for`** e **`tools/windows-lab/dialogue_service.py`:** o serviço passa o alinhamento da ficha só quando a pessoa tem curadoria conferida. Pessoas genéricas continuam com alinhamento sorteado.
- **Sem efeito no jogo:** nada muda na ficha, no `engine_alignment` nem no save.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **A personalidade continua sorteada por encontro:** os seis traços de Bernard ainda variam entre sessões, porque ele não tem identidade verificada. Curar a personalidade dos oficiais é outra tarefa da SPEC-006.
- **Dado do jogo:** o código de alinhamento vem do inventário local, fora do repositório (REQ-CANON-004).

## Migração e rollback

Sem migração. Rollback: não passar `game_alignment` em `profile_for` no serviço.
