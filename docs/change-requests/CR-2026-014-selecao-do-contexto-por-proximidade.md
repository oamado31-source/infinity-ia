# CR-2026-014 — O que entra no prompt: seleção por proximidade, não por ordem alfabética

**Status:** APPROVED (mantenedor, 2026-11-15)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-15

## Motivo e contexto

O contexto de um NPC residente leva no máximo 12 itens de conhecimento (`MAX_KNOWLEDGE` em `dialogue/context.py`). Até aqui, esses 12 eram escolhidos pela **ordem alfabética do id** da entrada. Com o pacote pequeno isso não importava, porque cabia tudo.

O lote A da enciclopédia (34 entradas) expôs o defeito: os ids `event:` vêm antes de `place:` e `rel:` e tomam todas as vagas. Na bateria, Salvanas, sentado na Coroa de Cobre, recebeu 12 itens de história de Amn, ficou sem a própria taverna e perdeu o vínculo restrito com Bernard. Cada lote novo pioraria isso.

## DEC/ADR/SPEC/REQ afetados

- **SPEC-008 (REQ-KNOW-003):** a recuperação continua obedecendo campanha, ramo, ano, identidade, proveniência e canal **antes** do modelo. Este CR só ordena o que já é elegível.
- **SPEC-009 (REQ-DISC-022):** o texto do jogador **não** entra na seleção. A ordem depende só de dados do pacote e de onde a pessoa está.
- **ADR-0131:** a decisão de divulgação por item continua a mesma e vale para cada item escolhido.
- Nenhum ADR é editado.

## Diff proposto e impacto no comportamento

1. **`memory/common_knowledge.py`:** a função pura `context_order(pack, entry_ids, *, npc_id, area, home_region)` devolve os ids na ordem:
   1. o conhecimento restrito (vínculo ou função, `RESTRICTED`) e o que é sobre a própria pessoa (`subject_id`);
   2. o lugar onde a pessoa está (entrada `PLACE` com a área atual) e as relações que o citam;
   3. o resto pelos níveis de distância da cadeia de regiões de onde a pessoa está (cidade, reino, Faerûn e, por último, regiões fora dessa cadeia, como a terra natal distante). Os níveis **se alternam**, um item de cada vez, para que nenhum nível ocupe o prompt sozinho;
   4. dentro de um nível: a própria região, organizações, lugares, tópicos, personagens e relações antes de eventos, e eventos recentes antes de antigos (`valid_from_dr`); empate pelo id.

   **Refinamento depois do relatório "quem sabe o quê" (2026-11-15):** com a ordem estrita por distância, os seis bairros de Athkatla tomavam as vagas do morador da Coroa de Cobre e tiravam do prompt os Magos Encapuzados, que estavam lá antes. A alternância entre níveis resolve isso sem usar o texto do jogador.
2. **`dialogue/context.py`:** `build_resident_context(..., order=())` e `build_context(..., order=())` (companheiros, que tinham o mesmo corte alfabético) ordenam os itens por essa lista antes do corte de 12. Itens fora da lista vão depois.
   - **Sem lista**, vale uma reserva que não depende do pacote: o restrito e o que é sobre a pessoa primeiro; depois, pelo prefixo do id, lugares, relações, regiões, organizações, tópicos e personagens antes de eventos; empate pelo id.
3. **`dialogue/engine.py`, `dialogue/evaluation.py` e `tools/windows-lab/dialogue_service.py`:** calculam a ordem com o pacote e a passam adiante. Para o residente, a referência é a região de onde ele está; para o companheiro, a região onde o grupo está.

**Efeito hoje:** o NPC passa a ter primeiro o que é dele e o que está à sua volta (a taverna, o bairro, a cidade); a história distante só entra se sobrar vaga. Quem sabe o quê não muda: só muda o que cabe no prompt.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **A história distante some do prompt** quando o NPC sabe muita coisa local. Para isso, a recuperação pela pergunta (doc 27, recuperação seletiva) fica para uma etapa própria, com o cuidado do REQ-DISC-022.
- **Um item retido pela divulgação ainda ocupa vaga**, como antes. Pode ser revisto junto com a recuperação pela pergunta.
- **Determinismo:** a ordem é pura e estável, e não depende do texto do jogador nem de sorteio.
- **Nada do jogo ou dos livros entra no repositório.**

## Migração e rollback

- **Migração:** sem migração de banco nem de pacote.
- **Rollback:** voltar a ordem alfabética em `build_resident_context` e remover `context_order` e o parâmetro `order`.
