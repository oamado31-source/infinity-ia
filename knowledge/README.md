# knowledge/ — o que entra e o que nunca entra

**Entra (texto nosso, curto, com fonte):**
- `periods/<ano>-DR/` — partição por ano DR (doc 60a). Uma entrada JSON por fato, schema `src/infinity_ai/canon/schemas/canon_entry_v1.schema.json`. Só o ano pedido é carregado.
- `sources/` — registro bibliográfico das obras (classe S0–S3, ano da ambientação). Os dados ficam `TO_CONFIRM` até o mantenedor conferir o exemplar.
- `personas/`, `areas/` — curadoria provisória da SPEC-004 (traços e nomes escritos por nós).
- `npcs/` — identidade curada de NPCs oficiais (ADR-0117): ofício, origem e fatos sobre si, em texto nosso e curto, com fonte; só vale depois da conferência do mantenedor.

**Nunca entra:**
- Texto, imagem, mapa ou tabela copiados de livros ou do jogo (só resumo próprio ≤ 280 caracteres e página; citação no máximo 15 palavras).
- Dados extraídos da instalação do jogo (inventário de áreas, strings do `dialog.tlk`): ficam em `~/.infinity-ai/knowledge/install-<fingerprint>/`, fora do repositório (REQ-CANON-004). O extrator recusa gravar dentro do repo e um teste falha se algum inventário for commitado.

**Estados:** `RESEARCH_ONLY` nunca é afirmado como fato; `SOURCE_CHECKED` exige conferência do mantenedor com obra e página; o gate (`src/infinity_ai/canon/gate.py`) ainda exige ano coincidente e região com áreas na build. Cânone não vira memória de NPC sem canal de aquisição (ADR-0059).

**`access_scope`:** `COMMON_REGIONAL` marca o que é de conhecimento público numa região e pode ser adquirido pelos canais do ADR-0114: origem curada (`background_regions` na persona), residência de NPC de fora do grupo e, depois, investigação ativa. Companheiros nunca aprendem por tempo de permanência. `CANON_REFERENCE` (por exemplo, organizações secretas) só serve de referência e nunca é adquirido por esses canais.

**`knowledge_layers`** (opcional, ADR-0117): os fatos do resumo conferido redistribuídos por dificuldade — `POPULAR` (o que todo mundo sabe), `INFORMED` (atenção, vivência, ofício) e `STUDIED` (história, causas, política) —, em texto nosso de até 200 caracteres cada e **sem fatos novos**. A Sabedoria e a Inteligência do NPC decidem até onde ele chega.

Para pedir uma entrada nova: `templates/canon-entry.md`.
