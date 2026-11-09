# knowledge/ — o que entra e o que nunca entra

**Entra (texto nosso, curto, com fonte):**
- `periods/<ano>-DR/` — partição por ano DR (doc 60a). Uma entrada JSON por fato, schema `src/infinity_ai/canon/schemas/canon_entry_v1.schema.json`. Só o ano pedido é carregado.
- `sources/` — registro bibliográfico das obras (classe S0–S3, ano da ambientação). Os dados ficam `TO_CONFIRM` até o mantenedor conferir o exemplar.
- `personas/`, `areas/` — curadoria provisória da SPEC-004 (traços e nomes escritos por nós).

**Nunca entra:**
- Texto, imagem, mapa ou tabela copiados de livros ou do jogo (só resumo próprio ≤ 280 caracteres e página; citação no máximo 15 palavras).
- Dados extraídos da instalação do jogo (inventário de áreas, strings do `dialog.tlk`): ficam em `~/.infinity-ai/knowledge/install-<fingerprint>/`, fora do repositório (REQ-CANON-004). O extrator recusa gravar dentro do repo e um teste falha se algum inventário for commitado.

**Estados:** `RESEARCH_ONLY` nunca é afirmado como fato; `SOURCE_CHECKED` exige conferência do mantenedor com obra e página; o gate (`src/infinity_ai/canon/gate.py`) ainda exige ano coincidente e região com áreas na build. Cânone não vira memória de NPC sem canal de aquisição (ADR-0059).

Para pedir uma entrada nova: `templates/canon-entry.md`.
