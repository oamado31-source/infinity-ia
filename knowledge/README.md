# knowledge/ — o que entra e o que nunca entra

**Entra (texto nosso, curto, com fonte):**
- `periods/<ano>-DR/` — partição por ano DR (doc 60a). Uma entrada JSON por fato, entidade PLACE, tópico TOPIC ou relação RELATIONSHIP, schema `src/infinity_ai/canon/schemas/canon_entry_v1.schema.json`. Só o ano pedido é carregado.
- `sources/` — registro bibliográfico das obras (classes S0–S3) e da curadoria explícita do projeto (S4_MAINTAINER_CURATED). S4 não é fonte externa e só fundamenta entradas CAMPAIGN_CANON aprovadas.
- `personas/`, `areas/` — curadoria provisória da SPEC-004 (traços e nomes escritos por nós).
- `npcs/` — identidade curada de NPCs oficiais (ADR-0117): ofício, origem, fatos sobre si, afiliações explícitas a lugares (ADR-0119) e estatuto local `standing` (`HABITANTE`, `VIAJANTE` ou `FORASTEIRO`, ADR-0120); só vale depois da conferência do mantenedor.

**Nunca entra:**
- Texto, imagem, mapa ou tabela copiados de livros ou do jogo (só resumo próprio ≤ 280 caracteres e página; citação no máximo 15 palavras).
- Dados extraídos da instalação do jogo (inventário de áreas, strings do `dialog.tlk`): ficam em `~/.infinity-ai/knowledge/install-<fingerprint>/`, fora do repositório (REQ-CANON-004). O extrator recusa gravar dentro do repo e um teste falha se algum inventário for commitado.

**Estados:** RESEARCH_ONLY nunca é afirmado como fato; SOURCE_CHECKED exige conferência do mantenedor com obra e página; CAMPAIGN_CANON pode usar S4_MAINTAINER_CURATED, que registra uma decisão explícita do mantenedor e não equivale a verificação externa. O gate ainda exige ano coincidente e região mapeada na build. Cânone não vira memória de NPC sem canal de aquisição (ADR-0059).

**`access_scope`:** `COMMON_REGIONAL` marca o que é de conhecimento público numa região e pode ser adquirido pelos canais do ADR-0114: origem curada (`background_regions` na persona), residência de NPC de fora do grupo e, depois, investigação ativa. Companheiros nunca aprendem por tempo de permanência. `CANON_REFERENCE` (por exemplo, organizações secretas) só serve de referência e nunca é adquirido por esses canais.

**`secrecy`** (opcional, ADR-0131): classe de sigilo, `PUBLIC`, `PERSONAL`, `PROFESSIONAL`, `CONFIDENTIAL`, `FACTION_SECRET` ou `ABSOLUTE`. Só uma entrada `RESTRICTED` pode ter classe acima de `PUBLIC`. Sem o campo, `COMMON_REGIONAL`/`CANON_REFERENCE` contam como `PUBLIC` e `RESTRICTED` como `PROFESSIONAL`, que é o comportamento de antes. A classe decide o que o NPC conta antes do prompt (reação favorável e moral nunca abrem `CONFIDENTIAL`, `FACTION_SECRET` ou `ABSOLUTE`) e é curada e conferida pelo mantenedor.

**Regiões (CR-2026-012):** toda região descende da raiz `region:faerun`. O que é público na raiz é sabido por qualquer NPC com origem ou residência no pacote. Uma região **sem área no jogo** (Águas Profundas, Calimshan…) só passa no gate se descender da raiz e serve apenas ao diálogo, nunca ao motor (REQ-CANON-002). Quem visitou uma região (`places_visited`) sabe só a camada `POPULAR` do que é público lá. Quem é de um reino (mora nele como `HABITANTE` ou nasceu nele) sabe a camada `POPULAR` das regiões abaixo desse reino, as cidades vizinhas, mas não do que há dentro delas (CR-2026-015).

**`knowledge_layers`** (opcional, ADR-0117): os fatos do resumo conferido redistribuídos por dificuldade — `POPULAR` (o que todo mundo sabe), `INFORMED` (atenção, vivência, ofício) e `STUDIED` (história, causas, política) —, em texto nosso de até 200 caracteres cada e **sem fatos novos**. A Sabedoria e a Inteligência do NPC decidem até onde ele chega.

**Relações (ADR-0119):** RELATIONSHIP registra subject_id, predicate, object_id e context_id opcional. COMMON_REGIONAL + REGIONAL_PUBLIC usa ORIGIN/RESIDENCE/INQUIRY; RESTRICTED exige afiliação curada (STAFF, REGULAR etc.) ou allowlist explícita. Estar na mesma área não concede acesso. INQUIRY compartilha apenas relações públicas; relações restritas não são propagadas por padrão.

**Tópicos (CR-2026-013):** `TOPIC` (prefixo `topic:`, pasta `topics/`) guarda costumes, moedas, línguas, modos de falar e religião, o que não é região, lugar, evento, organização, personagem nem relação. Exige `region_id` (onde o costume é conhecido), não tem área do jogo e não é ponta de relação. É conhecido pelas mesmas regras regionais.

**Validade e eventos passados (decisão do mantenedor, 2026-11-15):** `valid_from_dr`/`valid_to_dr` dizem em que anos de campanha o fato vale, não quando aconteceu. Um evento passado usa `valid_from_dr` = ano do evento e `valid_to_dr` vazio (o fato continua verdadeiro), com a data no texto. Uma entrada de livro ambientado em outro ano (por exemplo, *Lands of Intrigue*, 1370) precisa de validade explícita, ou o gate a recusa (`SETTING_YEAR_MISMATCH`). Nunca `valid_from_dr` depois do ano da partição: livro posterior não antecipa eventos.

**Divergências com o jogo (decisão do mantenedor, 2026-11-15):** para o que o jogo mostra (quem trabalha onde, nomes de bairros), o jogo prevalece (`game-data-local`); o livro entra só no que não o contradiz. Bairros de Athkatla usam o nome do jogo com o conteúdo do *Volo's Guide to Baldur's Gate II* onde coincidem.

Para pedir uma entrada nova: `templates/canon-entry.md`.
