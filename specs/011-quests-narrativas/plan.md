# Plano de implementação — SPEC-011

1. **Formato curado** `infinity-ai.narrative-quest.v1` em `knowledge/quests/<id>.<idioma>.json`:
   - `giver` (NPC, palavras de oferta e de aceite, fatos de oferta e de espera, linha de diário);
   - `steps` (NPC, palavras do assunto, fato, linha de diário);
   - `turn_in` (palavras, fato, linha de diário);
   - `milestone` = `quest:<id>:RESOLVED`; `curation` conferida.
   - Palavras são palavras ou frases inteiras; com `*` no fim, o começo de uma palavra ("furt*").
2. **Motor** (`quests/narrative.py`): estado por ramo a partir dos eventos `NarrativeQuestOffered`, `…Accepted`, `…StepDone` e `…Resolved`; `advance` move as quests da pessoa pelo que o jogador disse e devolve os fatos do turno, as linhas de diário e o marco.
3. **Marco:** `record_overlay_milestone` grava `QuestMilestoneObserved` com origem `OVERLAY`, na mesma chave por ramo dos marcos do jogo (ADR-0134).
4. **Contexto:** `quest_facts` entra como fatos "SOBRE VOCÊ" do NPC no turno (contexto, motor de diálogo e bateria).
5. **Serviço:** avança a quest antes de revisar a confiança, passa os fatos ao modelo, anexa o diário à resposta e escreve `quests=[…]` e `quest_mudou=[…]` no log.
6. **Fichas:** Bernard, `quest:bernard-brooch:RESOLVED` → `INTIMO`.
