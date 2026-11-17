# CR-2026-027 — Uma palavra comum sozinha não dispara o "não sei" automático

**Status:** APPROVED (mantenedor, 2026-11-17: "Lote H aprovado", decisão D1 do arquivo de conferência)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-17

## Motivo e contexto

A ausência tipada (ADR-0131) responde "não sei" pelo código quando a pergunta cita uma entrada que a pessoa não tem e nada do que ela pode dizer cita o mesmo nome. Até aqui, bastava **uma** palavra do título.

O lote H traz títulos com palavras comuns: "Vales" (também verbo, "quanto vale?"), "Mar da Lua", "Rei Azoun IV", "Magos de Guerra". O risco já existia com "Norte", "Floresta Alta" e "Costa da Espada". Para um NPC de Athkatla, que não tem os Vales nem o Mar da Lua:
- "Quanto vale uma espada?" viraria "Não sei te dizer.";
- "Você já viajou pelo mar?" também.

## DEC/ADR/SPEC/REQ afetados

- **ADR-0131:** a regra fica como está escrita. A pergunta precisa nomear algo do pacote, e uma palavra comum sozinha não é um nome.
- **CR-2026-026:** a busca pela menção também deixa de contar um nome de uma palavra só que seja comum ("Vales").
- **CR-2026-016:** inalterada. A ordem do prompt continua usando qualquer palavra do título.
- Nenhum ADR é editado.

## Diff proposto e impacto no comportamento

1. **`memory/common_knowledge.py`:**
   - **`common_words(pack)`:** as palavras de título que os textos do próprio pacote usam em minúscula. Hoje são 76, entre elas "vale", "mar", "rei", "norte", "floresta", "guerra", "cidade", "coroa" e "cobre". "Cormyr", "Mulmaster", "Elminster" e "Amn" ficam de fora.
   - **`says_whole_name`:** a pergunta diz um nome inteiro do título. Um nome de uma palavra só que seja comum não conta.
2. **`dialogue/absence.py`:** o `NOT_KNOWN` só vale se a pergunta disser um nome inteiro da entrada ("Mar da Lua", "Coroa de Cobre") ou uma palavra própria dela ("Mulmaster", "Dalelands", "Azoun").
3. **`named_in`:** usa a mesma regra para puxar pela menção.
4. **Serviço e bateria:** passam `common_words(pack)` adiante.
5. **Efeito:**
   - "Quanto vale uma boa espada aqui?" vai ao modelo ("Não vendo armas, só carrego coisas.").
   - "Você já viajou pelo mar?" também vai ao modelo ("Não, vivo nas Favelas.").
   - "E Mulmaster?" e "E o Mar da Lua?" continuam com a linha fixa de "não sei".
   - "O que sabe dos Vales?" vai ao modelo. O validador continua barrando nomes e afirmações sem base.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Menos "não sei" pelo código:** uma pergunta só com palavras comuns vai ao modelo. O modelo pode responder com o que não sabe; os verificadores de nomes e de afirmações sobre terceiros continuam valendo.
- **A lista sai dos textos:** uma entrada nova que use uma palavra em minúscula a torna comum. Isso é o comportamento desejado, e o teste mostra a lista.
- **Compatibilidade:** sem mudança no pacote, no pin ou no banco. Sem `common_words`, o comportamento é o anterior.

## Migração e rollback

- **Migração:** nenhuma.
- **Rollback:** passar `common=frozenset()` (o valor padrão) na ausência e tirar `says_whole_name` de `named_in`.

## Testes

- **`tests/test_absence.py`, caso novo:**
  - "quanto vale", "pelo mar", "o rei de Amn" e "dos Vales" vão ao modelo;
  - "o Mar da Lua", "os Dalelands" e "Azoun" continuam `NOT_KNOWN`;
  - sem a lista, "quanto vale" era `NOT_KNOWN`.
- **`tests/test_context_order.py`:** "quanto vale" não puxa Amn pela menção; a lista tem "vale", "mar", "rei" e "norte", mas não "cormyr", "mulmaster", "elminster" nem "amn".
- **Bateria:** `quanto-vale-nao-e-os-vales` e `pelo-mar-nao-e-o-mar-da-lua`, 3/3 cada. A bateria completa passou 46/46.
