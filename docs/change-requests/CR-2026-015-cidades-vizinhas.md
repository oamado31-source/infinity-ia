# CR-2026-015 — Cidades vizinhas: quem é de um reino conhece o núcleo popular das suas cidades

**Status:** APPROVED (mantenedor, 2026-11-15)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-15

## Motivo e contexto

O lote A2 trouxe as cidades de Amn (Murann, Crimmor, Esmeltaran, Trademeet…) como sub-regiões de `region:amn`. Pela regra atual (ADR-0117, CR-2026-012), a residência ensina só a própria região e as que estão acima dela.

O efeito é que quem mora em Athkatla não sabe que Murann existe: as cidades vizinhas ficam conhecidas só por quem nasceu em Amn, mora nelas ou passou por elas. Bernard não saberia dizer o que é Murann, o que não condiz com um amniano.

## DEC/ADR/SPEC/REQ afetados

- **ADR-0117 e ADR-0120:** os canais continuam os mesmos. Este CR acrescenta um núcleo popular, do mesmo jeito que a viagem já dá (CR-2026-012). Nenhum ADR é editado.
- **SPEC-008:** ampliada por este CR.

## Diff proposto e impacto no comportamento

1. **`memory/common_knowledge.py`, `identity_knowledge`:** a pessoa recebe a camada `POPULAR` de toda **região** (entrada `REGION`) abaixo do seu reino quando:
   - mora no reino como `HABITANTE`; ou
   - nasceu nele (origem curada ou gerada).
2. **Reino:** é a região mais alta da cadeia abaixo da raiz `region:faerun`. Para quem está em Athkatla, é Amn.
3. **Alcance:** só as entradas de região, ou seja, a cidade em si. Os lugares, eventos e tópicos de dentro de Murann continuam exigindo origem, residência ou viagem. O detalhe (`INFORMED`/`STUDIED`) também.
4. **Sem efeito** para viajantes e forasteiros que não são do reino, e para quem está fora do pacote.

**Efeito hoje:** quem mora em Athkatla ou nasceu em Amn passa a saber o núcleo popular das 12 regiões do lote A2 ("Murann é o porto dos marinheiros de Amn").

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Conhecimento demais:** contido pelo núcleo popular e por valer só para entradas de região.
- **Prompt:** as cidades entram na fila de seleção do CR-2026-014 no nível do reino e alternam com os outros níveis, sem tomar todas as vagas.
- **Revisão do pacote:** não muda. Muda só a regra de quem sabe o quê, calculada quando a pessoa fala e nunca gravada.

## Migração e rollback

- **Migração:** nenhuma.
- **Rollback:** remover o trecho do reino em `identity_knowledge`.
