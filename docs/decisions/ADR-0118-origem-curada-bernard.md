# ADR-0118 — Origem curada de Bernard para o perfil do projeto

**Estado:** APROVADA (decisão explícita do mantenedor, 2026-11-10).
**Relaciona-se com:** ADR-0117 (identidade dos NPCs), ADR-0114 (conhecimento regional), ADR-0116 (INQUIRY) e SPEC-006.
**Escopo:** exclusivamente a curadoria do perfil de laboratório de Bernard (`npc:cre-bernard`); não altera a regra geral de proveniência da ADR-0117.

## Contexto

A ADR-0117 estabelece que a origem de um NPC oficial sem terra natal confirmada deve permanecer desconhecida, evitando transformar hipóteses de teste em biografia apresentada como fato canônico.

No teste S1e, Tethyr foi usada como origem para exercitar a matriz de identidade e os canais de conhecimento regional. O mantenedor decidiu explicitamente que essa origem deve ser mantida no perfil de Bernard, desde que a documentação deixe claro que se trata de uma escolha curatorial do projeto, e não de uma informação comprovada pela fonte externa.

A referência consultada — Forgotten Realms Wiki, artigo [Bernard](https://forgottenrealms.fandom.com/wiki/Bernard) — informa Home: Athkatla, Amn. Não declara a terra natal de Bernard nem fornece evidência de nascimento em Tethyr.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-10.

1. **Manter Tethyr** como `origin_region = region:tethyr` na curadoria de `npc:cre-bernard`.
2. A proveniência desse campo é **CURATED**, por decisão explícita do mantenedor. Não atribuir a origem à Forgotten Realms Wiki, ao jogo ou a outra fonte que não a comprove.
3. Manter Athkatla/Amn como residência (`home_region` obtida dos dados locais do jogo), sem confundir residência com terra natal.
4. A regra geral da ADR-0117 permanece inalterada: outros NPCs oficiais sem origem confirmada continuam com `origin_region = null`, salvo decisão curatorial específica e documentada.
5. O uso de Tethyr habilita para Bernard o conhecimento regional público correspondente ao canal `ORIGIN`, conforme ADR-0117/ADR-0114. Esse comportamento é intencional para o perfil do projeto e pode ser testado no S1f; não constitui prova de canon externo.
6. Em falas de laboratório, o perfil pode apresentar Tethyr como sua origem de acordo com a curadoria aprovada. Relatórios e documentação devem qualificá-la como **origem curada do projeto**, não como fato confirmado por fonte oficial.

## Consequências

- `knowledge/npcs/bernard.pt_BR.json` mantém `origin_region: region:tethyr` e registra a proveniência do mantenedor.
- O teste automatizado de curadoria verifica que o perfil publicado conserva `region:tethyr`.
- A residência em Athkatla permanece separada e continua fundamentada nos dados locais do jogo e na referência consultada.
- A ADR-0117 permanece append-only e não é editada por esta decisão.

## Evidências, riscos e limites

- Referência consultada: https://forgottenrealms.fandom.com/wiki/Bernard — Home: Athkatla, Amn; não informa a terra natal.
- Decisão do mantenedor: manter Tethyr no perfil de laboratório/projeto.
- Limite: a decisão não comprova que Tethyr seja a terra natal de Bernard no canon oficial de Forgotten Realms.
- Risco controlado: leitores podem confundir residência e origem ou interpretar a curadoria como canon oficial. Mitigação: proveniência explícita no JSON, nesta ADR e nos relatórios S1f.
