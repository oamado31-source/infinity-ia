# CR-2026-028 — Preço e moeda em inglês precisam de base no que a pessoa sabe

**Status:** APPROVED (mantenedor, 2026-11-17: "Aprovar e abrir PR")  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-17

## Motivo e contexto

No laboratório de 2026-11-17, Bernard, o taverneiro curado da Coroa de Cobre, ouviu "Quanto vale uma boa espada aqui?" e respondeu:

> "A espada de qualidade custa 150 a 200 golds, dependendo da qualidade. Eu tenho uma no estoque, mas é de segunda mão."

- **Primeira tentativa:** recusada por `UNBACKED_DETAIL:prata`.
- **Nova tentativa:** passou, com dois problemas:
  - um preço inventado ("150 a 200");
  - a gíria em inglês "golds".
- **"Eu tenho uma no estoque" é verdade:** os dados de loja do jogo, lidos no laboratório, mostram que o diálogo de Bernard abre a loja da Coroa de Cobre, e essa loja vende armas, espadas entre elas. O preço de uma espada ali fica muito abaixo de "150 a 200". A parte inventada da fala é o valor, não o estoque.

A checagem de metais (lab de 2026-11-15) só conhece os metais em português: ouro, prata, cobre, platina, electro, mithral e adamantina. Por isso, deixa passar:
- **moedas em inglês e abreviações de mesa:** "gold", "golds", "200 po", "50gp";
- **números de preço:** "peças de ouro" passa porque o ouro tem base no item das moedas amnianas (`topic:amnian-currency`), e o número ao lado não é checado.

Esta CR implementa a moeda e o preço e não cria nenhuma checagem de posse ou estoque. Vale a regra do mantenedor de 2026-11-17: **quem vende bens ou serviços nunca diz que não os oferece nem que não sabe**.

## DEC/ADR/SPEC/REQ afetados

- **SPEC-004 (validação da saída):** `UNBACKED_DETAIL` ganha o motivo `PRICE` e passa a reconhecer moedas em inglês e abreviações de mesa.
- **ADR-0117, regra 8:** inalterada. A afirmação de estoque não vira `SELF_CLAIM`.
- **ADR-0132 (loja do NPC lida do jogo, já em `main`):** os preços da loja entram nos fatos do vendedor e dão base aos preços desta CR. Um teste confirma: "A Espada de Ferro custa 20 peças de ouro" passa quando a loja diz 20; "150 a 200 golds" é recusado.
- **ADR-0121:** inalterada. Números sobre terceiros continuam em `THIRD_PARTY:NUMBER`.
- Nenhum ADR é editado.

## Diff proposto e impacto no comportamento

1. **`dialogue/validate.py`, moedas (`UNBACKED_DETAIL:<palavra>`):**
   - "gold", "silver", "copper", "platinum", "electrum" e "coin", no singular e no plural, contam como moeda.
   - As abreviações de mesa contam logo depois de um número: "po", "pp", "pc", "pe", "pl", "gp", "sp", "cp", "ep". Exemplos: "200 po", "50gp". Sem o número, "po" não conta.
   - Cada uma só tem base em si mesma: precisa aparecer no que a pessoa sabe ou no que o jogador disse. "golds" tem base se o jogador disse "gold". O ouro do item das moedas não serve de base para "gold".
   - Os metais em português continuam como antes. "Peças de ouro" e "moedas de prata" já caíam no metal.
2. **`dialogue/validate.py`, preço (`UNBACKED_DETAIL:PRICE`):**
   - É preço um número ao lado de uma moeda: "150 a 200 golds", "dez peças de ouro", "5 moedas", "30 fandars".
   - Também é preço um número logo depois de uma palavra de preço: "custa 150", "vale 50", "sai por 30", "cobro 5", "preço de 20".
   - Cada número do preço precisa estar no que a pessoa sabe ou no que o jogador disse.
     - "Te pago 10 moedas" do jogador dá base a "10 moedas? É pouco".
     - Um fato "a caneca custa 2 fandars" dá base a "custa 2 fandars".
   - Os nomes de moeda do pacote (danter, fandar, taran, decime, roldon) contam como moeda para achar o preço. O item `topic:amnian-currency` dá base aos nomes, não aos valores.
   - Fala sem número não é preço: "custa caro", "não sei o preço", "vale a pena". Número que não é dinheiro também não: "moro aqui há 3 anos".
3. **Dicas para a nova tentativa, em português simples:**
   - `PRICE`: "você deu um preço com números que não estão no que você sabe; responda de novo sem dizer valores nem números de preço".
     - A dica pede só para tirar os números. Ela não manda dizer "não sei" nem "não vendo", porque um vendedor perguntado pelo preço do que vende continua oferecendo.
   - A dica das moedas ganha "com os nomes que aparecem lá", para o modelo trocar "golds" pelo nome da moeda que ele sabe.
4. **Efeito na fala do laboratório:**
   - Ela é recusada por `UNBACKED_DETAIL:golds` e `UNBACKED_DETAIL:PRICE`, e a nova tentativa recebe as duas dicas.
   - "Eu tenho uma no estoque, mas é de segunda mão" passa, porque é verdade para ele.
   - A resposta esperada na nova tentativa é a oferta sem números: "Tenho uma boa espada no estoque. Venha ao balcão e acertamos o preço."
   - Um vendedor que oferece o que vende sem dar número passa: "Temos cerveja, sim, e quartos lá em cima".

## Avaliação: posse ou estoque como `SELF_CLAIM`

- **Conclusão:** não criar. A primeira versão desta CR propunha `SELF_CLAIM:STOCK`, liberado só por palavras da ocupação e dos FATOS ("vende", "loja", "armeiro"). Ela recusaria a frase verdadeira de Bernard e também "tenho cerveja à venda", o que fere a regra do mantenedor.
- **O que fica para a ADR da loja:**
  - a loja de cada NPC, lida do jogo, diz o que ele vende e por quanto;
  - com isso, o preço desta CR ganha base;
  - se um dia houver checagem de estoque, ela só recusa o que **não** está na loja da pessoa e nunca manda um vendedor negar o que vende.
- **Dados da loja:** são lidos do jogo no laboratório e ficam locais (REQ-CANON-004). Esta CR não traz nenhum dado de loja para o repositório.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Falso positivo:** nas 1.439 falas aceitas dos relatórios de bateria guardados em `~/.infinity-ai/dialogue-eval/`, as regras novas só acham "10 moedas" do caso do suborno. Ali, o número vem do jogador e tem base, então nenhuma dessas falas passa a ser recusada.
- **Vendedor sem loja no inventário:** quem vende mas não tem loja lida do jogo não pode dar número de preço. A dica pede para responder sem números, e não para dizer "não sei". Com a ADR-0132, Bernard e os outros 18 vendedores do laboratório têm os preços nos fatos.
- **O vendedor nega o que vende:** resolvido pela ADR-0132 (`SELF_CLAIM:OFFER`). O caso `preco-sem-lastro` agora dá a Bernard uma loja inventada e checa que ele não nega a venda.
- **Mais recusas e falas de reserva:** um NPC que gosta de dar preço vai ser recusado mais vezes. Quando a nova tentativa também falha, a fala de reserva é o lado seguro.
- **Lacunas que ficam:**
  - Preço com "um" ou "uma" ("custa uma moeda") não é checado, porque "uma moeda" aparece em frases comuns.
  - Estoque e venda não são checados (ver a avaliação acima).
  - Um preço por extenso que está nos fatos como dígito ("dez" contra "10") é recusado. Hoje nenhum fato do pacote tem preço.
- **Compatibilidade:** sem mudança no pacote, no pin, no banco nem no serviço.

## Migração e rollback

- **Migração:** nenhuma.
- **Rollback:**
  - tirar `_COIN_WORDS`, `_COIN_ABBREVIATIONS` e `_unbacked_price` do `validate_reply`;
  - tirar a dica `PRICE`.
  - A checagem de metais volta ao que era.

## Testes

- **`tests/test_price_and_coins.py`, arquivo novo, 12 testes:**
  - a fala exata do laboratório, recusada por moeda e preço, e a dica sem códigos;
  - a dica de preço não manda dizer "não sei" nem "não vendo";
  - um vendedor oferecendo o que vende passa: cerveja, quarto e a própria "Eu tenho uma no estoque, mas é de segunda mão";
  - a oferta da espada sem os números inventados passa;
  - "gold", "silver", "200 po" e "50gp" sem base, e "gold" dito antes pelo jogador;
  - preços sem base ("custa 150", "dez peças de ouro", "30 fandars") e com base (no fato e na fala do jogador);
  - números que não são preço;
  - os preços da loja nos fatos do vendedor (ADR-0132) dão base ao preço dito, e um preço inventado é recusado.
- **Bateria:** caso novo `preco-sem-lastro`, com Bernard, a pergunta do laboratório e uma loja inventada (Espada de Ferro, 20 peças de ouro). Ele recusa "gold", qualquer número além de 20 e a negação da venda. Resultado: 3/3, por exemplo "Espada de Ferro custa 20 peças de ouro."
- **Checagens:** refeito sobre o `main` com a ADR-0132. Suíte de 513 testes, pyflakes, `check_historical_adrs.py` e `check_public_files.py` verdes. Bateria completa com uma rodada: 51/51; os casos de loja passaram 3/3.
