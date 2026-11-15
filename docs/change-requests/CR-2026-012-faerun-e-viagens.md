# CR-2026-012 — Região raiz de Faerûn, regiões fora do mapa e o que as viagens ensinam

**Status:** APPROVED (mantenedor, 2026-11-15)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-15

## Motivo e contexto

**Pedido do mantenedor (2026-11-15):** uma enciclopédia base ampla, com lore, cronologia e informações de outras partes do mundo. Um NPC em Amn pode ter ouvido falar de lugares distantes ou ter viajado. Também decidiu que quem viajou para uma região sabe **só o núcleo popular** do que é público lá.

Três coisas impediam isso:

1. **Não existe um "mundo" no pacote.** Amn e Tethyr são raízes soltas, e não há onde pôr o que se sabe em todo o continente (o Tempo das Perturbações, por exemplo).
2. **O gate recusa regiões sem área no jogo** (`UNMAPPED_REGION`). Águas Profundas, Calimshan ou a Costa da Espada nunca passariam. O REQ-CANON-002 só exige que uma região fora do mapa não **materialize consequências no motor**, e conhecimento em diálogo não é consequência no motor.
3. **`places_visited` é validado mas não ensina nada** (ADR-0117).

## DEC/ADR/SPEC/REQ afetados

- **SPEC-005 (REQ-CANON-002) e SPEC-008:** ampliados por este CR. Nenhum ADR é editado.
- **ADR-0114 e ADR-0117:** os canais continuam os mesmos (origem, residência e INQUIRY). A viagem dá só o núcleo popular, como o viajante (`VIAJANTE`) já recebe do lugar onde está.

## Diff proposto e impacto no comportamento

1. **`region:faerun`** (`knowledge/periods/1369-DR/regions/faerun.json`): `CAMPAIGN_CANON`, com fonte `maintainer-curation`, sem área. `region:amn` e `region:tethyr` passam a ter `region_id: region:faerun`. Constante `WORLD_REGION` em `canon/pack.py`.
2. **Gate (`canon/gate.py`):** uma região **sem área** que descende da raiz (ou é a própria raiz) passa no gate, porque é conhecida só em diálogo. Uma região sem área fora da raiz continua `UNMAPPED_REGION`, e nada fora do mapa toca o motor (REQ-CANON-002).
3. **O nível de Faerûn** (`memory/common_knowledge.py`, `identity_knowledge` e a aquisição de companheiros):
   - o que é público na raiz vale para quem tem origem ou residência numa região do pacote, qualquer que seja o estatuto;
   - o residente já recebia pela cadeia de regiões, e o companheiro recebe por origem.
4. **A raiz não é lugar de ninguém:**
   - `personality/identity.py` exclui a raiz da cadeia de residência, dos sorteios de origem e de viagem dos NPCs gerados e dos nomes do "sou de…" (`home_names`);
   - `local_aliases` ignora a raiz, então "reino" continua sendo Amn e "cidade" continua sendo Athkatla.
5. **Viagens dão o núcleo popular:** `identity_knowledge(..., visited=...)` dá a camada `POPULAR` do que é público nas regiões visitadas (e abaixo delas), se o NPC não as conhecer por origem ou residência. `NpcIdentity.visited_regions` leva as regiões visitadas, de curadoria ou geradas, ao serviço e à bateria.

**Efeito hoje:** todo NPC passa a saber a entrada "Faerûn" ("Faerûn é o continente onde ficam Amn, Tethyr e as terras vizinhas"), e os NPCs gerados que já tinham viagens sorteadas ganham o núcleo popular dessas regiões. Os sorteios dos NPCs gerados não mudam, porque a raiz é excluída deles.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Conhecimento demais por viagem:** contido pelo núcleo popular. O detalhe (`INFORMED`/`STUDIED`) continua exigindo origem ou residência.
- **O nível de Faerûn vira "conhecimento de todos":** cada entrada nesse nível precisa ser algo realmente sabido em todo o continente. A curadoria decide caso a caso, com fonte e conferência.
- **Revisão do pacote:** muda a revisão. Campanhas fixadas não recebem o conhecimento novo até um novo pin explícito (REQ-REL-012). No laboratório: `tools/windows-lab/pin_canon_pack.py` na campanha `lab-s1f`.
- **Nada do jogo ou dos livros entra no repositório.**

## Migração e rollback

- **Migração:** sem migração de banco. Novo pin do pacote nas campanhas que quiserem o conhecimento novo.
- **Rollback:** remover `faerun.json`, voltar `region_id: null` em Amn e Tethyr e reverter o gate, as regras de viagem e o nível de Faerûn.
