# Plano de implementação — SPEC-012

Fase 1 aprovada pelo mantenedor em 2026-11-18 ("Aprovar como proposta", D1 a D4 na primeira opção), com a CR-2026-030.

1. **Duas camadas (CR-2026-030):** registro curado no repositório (`knowledge/encyclopedia/`) e catálogo extraído local (`~/.infinity-ai/encyclopedia/install-<build>/`).
2. **Esquemas versionados** (`knowledge/encyclopedia/schemas/*.v1.schema.json`): núcleo comum (identidade, fontes, estado de validação, curadoria, relações) e campos mínimos por categoria. `additionalProperties: false`: um atributo extraído não cabe num registro curado.
3. **Manifesto e fontes** (`manifest.json`, `sources.json`): jogos do escopo e o que está instalado no laboratório; fontes comunitárias só registradas, com termos a confirmar.
4. **Validador** (`encyclopedia/catalog.py`): esquema, `canonical_id` único e com o prefixo da categoria, diretório certo, fontes conhecidas, ficha curada existente, relações existentes ou `pending:`.
5. **Registros iniciais:** os 27 NPCs que já têm ficha curada, em `characters/bg2/`, apontando para a ficha.
6. **Censo dos personagens (fase 2, primeiro corte):** `gamedata/census.py` e `tools/windows-lab/build_encyclopedia.py --characters`; catálogo local e relatório para o mantenedor, fora do repositório.
