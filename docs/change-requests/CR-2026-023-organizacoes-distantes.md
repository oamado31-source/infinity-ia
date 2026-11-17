# CR-2026-023 — Organizações distantes só sobem quando perguntadas

**Status:** APPROVED (mantenedor, 2026-11-16: lote F aprovado; efeito visto nos testes)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-16

## Motivo e contexto

O lote F põe no nível de Faerûn seis organizações que o continente inteiro conhece: os Harpistas, a Zhentarim, os Magos Vermelhos, o Culto do Dragão, a Aliança dos Lordes e Szass Tam. Põe também o Trono de Ferro, que é da Costa da Espada.

Pela ordem do prompt (CR-2026-014 e CR-2026-018), as instituições entram primeiro e os níveis de distância se revezam, um item de cada vez. Para quem está em Athkatla, isso significa um revezamento entre Athkatla, Amn, Faerûn e as terras de fora da cadeia. Assim, as organizações de longe tomaram as vagas das de perto, e os **Magos Encapuzados saíram das 12 vagas do prompt**. É o mesmo problema que a CR-2026-018 tinha resolvido para a história.

## DEC/ADR/SPEC/REQ afetados

- **CR-2026-014 e CR-2026-018:** a ordem é refinada. O revezamento continua para costumes e eventos.
- **CR-2026-016:** inalterada. O que a pergunta nomeia continua subindo antes de tudo.
- **REQ-DISC-022:** a ordem continua sem usar o texto do jogador, exceto o que a pergunta nomeia (CR-2026-016).
- Nenhum ADR é editado.

## Diff proposto e impacto no comportamento

1. **`memory/common_knowledge.py`, `context_order`:** uma `ORGANIZATION` do nível de Faerûn, ou de uma região fora da cadeia de onde a pessoa está, vai para o fim da fila, junto com as regiões distantes (o "atlas").
2. **Efeito:**
   - o prompt de quem está em Athkatla volta a ter as instituições de perto (o Conselho, os Magos Encapuzados, a igreja de Waukeen, a Ordem do Coração Radiante);
   - os Harpistas, a Zhentarim e as outras sobem quando a pergunta as nomeia ("Quem são os Harpistas?").

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **O NPC não puxa por conta própria as organizações distantes:** é aceitável, pelo mesmo raciocínio da CR-2026-018. Basta o nome na pergunta para elas voltarem.
- **Determinismo:** a ordem continua pura e estável.

## Migração e rollback

- **Migração:** nenhuma.
- **Rollback:** tirar o ramo `ORGANIZATION` do atlas.

## Testes

- **`tests/test_context_order.py`, caso novo:** as organizações distantes vêm depois do Tempo das Perturbações, e "Quem são os Harpistas?" as traz para as 12 vagas.
- **Caso antigo:** "instituições antes de costumes e eventos" passa a valer para as organizações de perto.
- **Bateria:** casos novos `organizacao-distante-pela-pergunta` e `ordem-local-no-prompt`.
