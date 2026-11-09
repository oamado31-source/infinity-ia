# ADR-0115 — Matriz multidimensional de personalidade e alinhamento dos NPCs

**Estado:** PROPOSTA — aguardando revisão/aceite explícito do mantenedor (2026-11-09).
**Motivação:** solicitação do mantenedor para diferenciar personalidade, interpretação e comportamento de cada NPC, incluindo alinhamento AD&D no sorteio inicial.
**SPEC:** [SPEC-006](../../specs/006-personalidade-alinhamento-npc/spec.md).
**Compatibilidade:** ADR-0018, ADR-0030–0032, ADR-0042, ADR-0059, ADR-0062, ADR-0113 e ADR-0114. Não modifica nenhum ADR aprovado.

## Problema

A persona da SPEC-004 hoje contém estilo, vocabulário e fallback. Esses campos não bastam para coerência psicológica, diferenças entre indivíduos, evolução e comportamento contextual. NPCs oficiais já possuem caracterizações e alinhamentos próprios. NPCs criados não devem nascer como clones sem identidade.

## Alternativas

1. Arquétipos fechados (bom, mau, heroico, tímido): simples, mas repetitivos e incoerentes.
2. Prompt de LLM gerar personalidade a cada conversa: barato de projetar, porém instável, sem persistência e com risco de onisciência.
3. **Proposta:** perfil-base determinístico multidimensional, sorteado e persistido uma vez para NPCs inéditos, alinhamento independente e estado narrativo evolutivo separado.

## Regra proposta

1. Seis traços contínuos inspirados no HEXACO; não são diagnóstico nem instrumento HEXACO-PI-R distribuído.
2. Alinhamento AD&D 2e como dois eixos separados, com nove combinações, sorteado com pesos explícitos apenas na criação de NPCs originais; sem derivação matemática de HEXACO.
3. Valores, necessidades, vulnerabilidades e estilo expressivo complementam a matriz; relações, emoções, crenças, reputação e experiências pertencem a estados distintos.
4. Personagens oficiais/curados preservam dados confirmados ou ficam `UNKNOWN`; nunca sortear em substituição ao jogo. A evolução só ocorre após eventos e política autorizada.
5. Identidade/seed/campanha/ramo/versão e snapshot imutável possibilitam repetição, forks e restauração sem remodelar personalidades.
6. Conhecimento e segredos seguem ACL/ADR-0059/0114: personalidade influencia **interpretação**, não concede fatos. A LLM redige, mas não decide regra, reputação, alinhamento mecânico nem mutações.
7. Uma divergência narrativa não equivale a `engine_alignment` alterado; qualquer efeito real exige host, POC, gateway e recibo.

## Decisões ainda abertas para aprovação

- Distribuições e pesos narrativos por contexto; limites de diversidade e combinações incoerentes; facetas opcionais.
- Qual granularidade persiste em NPCs de multidão vs. promovidos; contrato de gravação e recuperação.
- Política de evolução de traços e alinhamento, limiares, contestação e explicação; impacto por classe/kit.
- Interface de autoria/revisão para companheiros canônicos e NPCs criados.

O gerador anexado à SPEC é **experimental**, testado sinteticamente; nenhuma capacidade de reação, escrita BG2:EE ou POC real decorre deste ADR.
