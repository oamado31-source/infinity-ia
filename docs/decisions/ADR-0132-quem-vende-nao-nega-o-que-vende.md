# ADR-0132 — Quem vende não nega o que vende: as lojas do jogo como fatos do NPC

**Estado:** APROVADA (mantenedor, 2026-11-17: "Aprovar a ADR-0132").

**Origem:** no teste do lote H (evidência S1p), Bernard respondeu sobre o preço de uma espada com "150 a 200 golds" e "tenho uma no estoque". O mantenedor pediu: "um NPC que venda itens ou serviços, se perguntado sobre isso, não pode responder que não oferece ou que não sabe". O laboratório mostrou que Bernard vende armas de verdade, e que o modelo não sabia nem o que ele vende nem os preços.

**Relaciona-se com:**
- ADR-0116 e ADR-0117: a pessoa no jogo e os fatos sobre si;
- ADR-0119 e ADR-0120: vínculos e posição social;
- ADR-0121: o verificador;
- REQ-CANON-004: nada do jogo no repositório;
- CR-2026-028: preços e moedas sem base.

**Gate:** etapa 1, single player. O overlay só lê o jogo; nada é escrito no estado do jogo.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-17.

1. **A fonte é a loja do jogo.**
   - O diálogo da criatura (`DLG`, pelo campo de diálogo do `CRE`) diz, pelas ações `StartStore("X")`, que lojas ela abre.
   - A loja (`STO`) dá o tipo (loja, taverna, estalagem, templo), o nome, a margem de venda, os quartos e preços, as bebidas e preços, os itens à venda e as curas. Itens, bebidas e curas só contam quando as flags da loja dizem que ela os vende.
   - Os itens (`ITM`) dão o nome em pt-BR (pelo `dialog.tlk`), o preço base e a categoria.
2. **Só local (REQ-CANON-004):**
   - `tools/windows-lab/build_area_inventory.py --stores` lê a cópia do jogo da VM por SSH, só em memória;
   - grava o resultado em `~/.infinity-ai/knowledge/install-<fp>/stores.<idioma>.json`, para os habitantes já inventariados;
   - recusa gravar dentro do repositório. Nos testes e na bateria, as lojas são inventadas.
3. **Várias lojas de uma pessoa** (Bernard abre duas, conforme o capítulo) **viram uma só oferta**: a união do que vendem, pela menor margem. Escolher a loja pelo estado do jogo fica para depois.
4. **O NPC recebe fatos sobre si,** como os da ficha:
   - uma linha com o que vende, como "Você vende na Taverna de Teste: quartos (camponês 2, mercador 7 peças de ouro por noite); bebidas (…); armas, escudos…" (valores inventados; os reais ficam só no inventário local);
   - quando a pergunta cita uma categoria ("espadas", "escudo"), as linhas dos itens dela com o preço (até 8).
   Os preços vêm do jogo: o dos itens já com a margem da loja.
5. **O verificador ganha a regra `SELF_CLAIM:OFFER`:**
   - recusa a fala que nega o que a loja oferece ("não temos quartos", "não vendo armas");
   - recusa a fala que diz não saber, quando a pergunta é sobre algo que a pessoa vende;
   - a nova tentativa recebe a dica em português.
   Se o modelo insistir, a fala de reserva passa a ser a do vendedor, montada pelo código com o que a loja tem ("Temos quartos, sim: …").
6. **Quem não tem loja não muda:** pode dizer que não vende.
7. **Fora desta decisão:**
   - abrir a loja do jogo pela conversa, que seria agir no jogo;
   - os ajustes de preço por carisma e reputação;
   - a criatura embutida na área, sem arquivo `CRE` próprio;
   - quem é `STAFF` de uma loja sem abri-la (ADR-0119): a curadoria pode dar isso depois.

## Consequências

- Bernard e outros 18 vendedores do laboratório passam a responder com o que vendem de fato, e com os preços da loja.
- O preço dito sobre o que a pessoa vende tem base nos fatos, o que fecha boa parte da brecha da S1p. A CR-2026-028 cuida das moedas e dos preços sem base no resto.
- O prompt do vendedor ganha uma ou duas linhas de fatos.

## Verificação

- **`tests/test_store_offers.py`:** leitores de `CRE`, `DLG`, `STO` e `ITM` com bytes inventados; a união de duas lojas; o inventário fora do repositório; os fatos, a negação e a fala de reserva do vendedor; o verificador e o motor.
- **Bateria:** `loja-quartos`, `loja-cerveja`, `loja-espada` e `sem-loja-nao-vende`, com uma "Taverna de Teste" inventada.
- **Laboratório:** 19 vendedores entre 358 habitantes, entre eles Bernard (estalagem "Coroa de Cobre": dois tipos de quarto, cinco bebidas, armas, escudos, armaduras e pergaminhos).
