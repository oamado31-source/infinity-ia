# CR-2026-026 — Uma pergunta sobre um nome distante traz o que a pessoa sabe dele por outras entradas

**Status:** APPROVED (mantenedor, 2026-11-17: "Puxar pela menção")  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-17

## Motivo e contexto

No teste do lote G no jogo, Salvanas mora em Athkatla e não tem as entradas do Norte. Duas perguntas deram respostas incoerentes.

1. **"O que você sabe de Águas Profundas?"** Ele respondeu "Isso eu não sei". Logo depois, perguntado sobre Khelben, disse que ele é "o arquimago de Águas Profundas".
   - Águas Profundas fica no Norte, que não é vizinho de Amn (CR-2026-021, CR-2026-025).
   - Khelben só entrava no prompt quando a pergunta o nomeava (CR-2026-016).
   - Assim a cidade virava "não tida", e a ausência tipada (ADR-0131) respondia pelo código.
2. **"O que sabe sobre Silvery Moon e sobre Alustriel?"** A resposta caiu na fala de reserva. O verificador recusou as duas tentativas (`THIRD_PARTY:STRANGER` e `THIRD_PARTY:ROLE`).
   - O jogador escreveu o nome em inglês e em duas palavras. A entrada de Alustriel diz "Lua Prateada".
   - Nada do que Salvanas sabe dizia que os dois nomes são o mesmo lugar. Por isso ligar Alustriel a "Silvery Moon" parecia invenção.
   - No laboratório, perguntado só por "Silverymoon", ele respondia "não sei", mesmo conhecendo a Grande Senhora de Lua Prateada.

## DEC/ADR/SPEC/REQ afetados

- **CR-2026-016:** ampliada. Quando a pergunta diz o nome inteiro de uma entrada que a pessoa não tem, contam também as entradas que ela tem e cuja camada popular diz um dos nomes dessa entrada.
- **ADR-0131:** a regra fica como está escrita, "só quando a pergunta é sobre o que a pessoa não pode responder". O código agora cumpre isso em dois casos que escapavam:
  - o outro nome do lugar está no que ela diz;
  - a pergunta cita também algo que ela pode dizer.
- **Regra dos nomes em pt-BR e inglês (mantenedor):** o título de cada entrada com os dois nomes passa a valer também para ligar os nomes na conversa.
- Nenhum ADR é editado.

## Diff proposto e impacto no comportamento

1. **`memory/common_knowledge.py`:**
   - **`spoken_words`:** duas palavras seguidas valem também juntas. "Silvery Moon" nomeia "Silverymoon", e "Never Winter" nomeia "Neverwinter".
   - **`title_names` e `asked_names`:** os nomes de um título são o de pt-BR e os ingleses entre parênteses. Quem diz um nome inteiro diz todos. Uma parte de um nome ("Lordes" de "Lordes de Águas Profundas") vale só por ela.
   - **`named_in`:** quando a pergunta diz um nome inteiro de uma entrada não tida, as entradas tidas cuja camada popular traz um dos nomes dela entram como nomeadas.
     - Vale só o nome inteiro: "magia na cidade" não puxa nada por causa de "Dez Cidades". Na primeira versão puxava, e os Magos Encapuzados saíram do prompt (a bateria pegou).
     - A palavra que já nomeia uma entrada tida não conta. Em "Quem governa Amn?", "Amn" é respondido pela entrada de Amn, e não por tudo o que cita Amn.
     - Vale só a camada popular, que todo mundo que tem a entrada recebe. Na primeira versão, que olhava o resumo, a bateria pegou "Alustriel também é de lá": só a camada erudita dela fala da irmã que vive em Águas Profundas.
     - Como antes, isso só reordena o prompt e nunca acrescenta uma entrada que a pessoa não tem.
2. **`dialogue/context.py`:** quando a pergunta diz um nome e o que a pessoa diz traz outro nome da mesma entrada, entra no prompt uma linha tirada do título: "Silverymoon: é o mesmo que Lua Prateada, com o nome em outra língua.". A linha não é entrada do pacote e não aparece em `entradas`.
3. **`dialogue/absence.py`:** `NOT_KNOWN` só quando nenhum nome da entrada perguntada está no que a pessoa diz e a pergunta não cita nada que ela possa dizer.
   - "E Luskan? E Khelben?" vai ao modelo, que responde sobre Khelben e diz que não conhece Luskan.
   - "E Luskan?" sozinho continua com a linha fixa de "não sei".
4. **Efeito no laboratório, com a ficha do Salvanas:**
   - "O que você sabe de Águas Profundas?": responde pelo que sabe de Khelben, da Aliança dos Lordes e da Costa da Espada ("É uma cidade grande, mas não sei muito. Só que é lá que o Khelben Blackstaff mora.").
   - "O que sabe sobre Silvery Moon e sobre Alustriel?": "Silvery Moon é o mesmo que Lua Prateada. Alustriel é a Grande Senhora de lá, uma feiticeira bondosa." 8/8 sem reserva; antes eram 2/4 na reserva.
   - "Mas sobre Waterdeep você sabe algo? E sobre Khelben?": liga Waterdeep a Águas Profundas e a Khelben. Em 2 de 8 rodadas caiu na reserva, porque o modelo insistiu em enfeitar a cidade ("o lugar mais rico da Costa da Espada"), e o verificador (`THIRD_PARTY:TRAIT`) recusou. Falha para o lado seguro.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Prompt:** mais entradas sobem para o começo quando a pergunta diz um nome distante. O limite (`MAX_KNOWLEDGE`) é o mesmo, e a linha dos nomes é uma a mais.
- **Palavras juntas:** um par comum que, junto, formasse o nome de uma entrada seria lido como esse nome. Não há caso no pacote hoje.
- **Invenção sobre a cidade:** o modelo tende a enfeitar o lugar distante. O verificador recusa traços sem base, e a reserva é o lado seguro.
- **Ainda fora daqui:** "cidade" nomeia "Dez Cidades (Ten-Towns)" para quem a tem (CR-2026-016). Isso só reordena e não muda a resposta, mas pode ser tratado com o lote seguinte.
- **Compatibilidade:** sem mudança no pacote, no pin ou no banco.

## Migração e rollback

- **Migração:** nenhuma.
- **Rollback:** voltar `named_in`, `spoken_words` e `classify_absence` ao que eram e tirar a linha dos nomes de `build_resident_context`.

## Testes

- **`tests/test_context_order.py`:**
  - sem o Norte, "Águas Profundas" traz Khelben, mas não a cidade, nem o que não a cita, nem Alustriel; "Silvery Moon" traz Alustriel; "magia na cidade" não traz nada;
  - no contexto montado, Khelben entra e não há ausência;
  - para "Silvery Moon", a linha dos nomes entra e não há ausência.
- **`tests/test_absence.py`:** o outro nome, o nome em duas palavras, a pergunta que cita também algo sabido, Luskan sozinho e a parte de um nome.
- **Bateria:**
  - `cidade-distante-pelo-que-se-sabe`: 5/5 (Salvanas, "O que você sabe de Águas Profundas?"; responde pelo modelo e não cita Alustriel);
  - `cidade-pelo-outro-nome`: 3/3 (a pergunta do jogo sobre Silvery Moon e Alustriel; liga a Lua Prateada);
  - bateria completa: 41/42 numa rodada. A falha foi `sem-staff-trabalho`, a instabilidade conhecida, que passou 3/3 em seguida.
