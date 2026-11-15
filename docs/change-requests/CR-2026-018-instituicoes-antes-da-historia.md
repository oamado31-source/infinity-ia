# CR-2026-018 — No prompt, instituições antes dos costumes, e a história quando perguntada

**Status:** APPROVED (mantenedor, 2026-11-15: testado no jogo e aprovado para PR)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-15

## Motivo e contexto

O lote B põe no nível de Faerûn a história que o continente inteiro conhece: o Tempo das Perturbações, a Horda Tuigan, Zhentil Keep, Netheril. Pela ordem do CR-2026-014, os níveis de distância se alternam um item de cada vez. Para Bernard, o nível de Faerûn e o de Tethyr (a terra natal dele) passaram a ocupar quatro das 12 vagas com eventos, e os **Magos Encapuzados** saíram do prompt.

A pergunta "Posso usar magia na cidade?" não nomeia os Magos, então a recuperação pela pergunta (CR-2026-016) não os traria de volta, e Bernard diria que não sabe.

## DEC/ADR/SPEC/REQ afetados

- **CR-2026-014:** a ordem é refinada; a alternância entre níveis continua.
- **CR-2026-016:** inalterado. O que a pergunta nomeia continua subindo antes de tudo isso.
- **REQ-DISC-022:** a ordem continua sem usar o texto do jogador.
- Nenhum ADR é editado.

## Diff proposto e impacto no comportamento

1. **`memory/common_knowledge.py`, `context_order`:** depois do que é da pessoa, do lugar onde ela está e do que a pergunta nomeia, os itens entram em três grupos, nesta ordem:
   1. instituições (regiões e organizações);
   2. costumes e lugares (tópicos, lugares, personagens, relações);
   3. eventos.
   Dentro de cada grupo, os níveis de distância continuam se alternando. Regiões fora da cadeia e o continente continuam no fim (atlas).
2. **Efeito:** o prompt de quem mora em Athkatla tem a taverna, o bairro, Athkatla, Amn, o Conselho, a igreja de Waukeen, os Magos Encapuzados, as famílias mercantis e os lugares próximos. A história (de Amn e de Faerûn) entra quando é perguntada.
3. **Camada do Tempo das Perturbações:** a camada POPULAR passou a citar o nome "Tempo das Perturbações", que já estava no resumo. Sem isso, a pergunta pelo nome era recusada como se fosse um desconhecido (`THIRD_PARTY:STRANGER`).

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **A história some do prompt quando ninguém pergunta por ela:** o NPC não a puxa por conta própria. É aceitável: o nome de qualquer evento na pergunta o traz de volta (CR-2026-016).
- **Determinismo:** a ordem continua pura e estável.

## Migração e rollback

- **Migração:** nenhuma.
- **Rollback:** voltar à alternância única entre níveis, sem grupos.
