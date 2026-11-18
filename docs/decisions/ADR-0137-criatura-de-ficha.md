# ADR-0137 — P3b: uma criatura de outro jogo gerada a partir da ficha

**Estado:** APROVADA (mantenedor, 2026-11-18: "Aprovar como proposta", decisões D1 a D5 na primeira opção).

**Origem:** o portão P3 (ADR-0136) provou que o projeto cria e remove, no jogo, uma criatura feita de um arquivo nosso. O primeiro grande objetivo pede gente e criaturas de outros jogos. As fichas vêm das bases comunitárias registradas na SPEC-012, consultadas por entidade.

**Relaciona-se com:**
- ADR-0136 (gateway, arquivos de criatura nossos, `build_templates.py`);
- SPEC-012 e CR-2026-030 (ficha local, registro curado no repositório);
- SPEC-011 (a quest com presença, passo seguinte);
- REQ-KNOW-002 (cronologia: o que aconteceu antes de 1369).

**Gate:** etapa 1, single player, save descartável.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-18.

1. **Primeiro personagem (D1):** Tamoko, de BG1 (1368 DR), clériga de Kara-Tur.
   - No fim de BG1 ela pode ir embora viva. Mas o BG2 (Throne of Bhaal) diz que ela morreu antes de Shadows of Amn, sem que se saiba como, e o epílogo de Sarevok leva o corpo dela a Kara-Tur.
   - Por isso, em 1369 ela aparece como **visão** (o próprio BG2 usa visões no Plano de Bolso), e a causa da morte é o mistério de uma quest da campanha (mantenedor: "Mistério da morte dela").
2. **Ficha local** (`infinity-ai.creature-sheet.v1`, em `~/.infinity-ai/sheets/`):
   - números da ficha da TH.GL, com a URL e a data da consulta;
   - fora do repositório (CR-2026-030 e termos da fonte).
3. **Gerador** (`actions/creatures.py`, `build_templates.py --from-sheet`):
   - parte de um CRE vivo do BG2 (o corpo) e copia, nunca edita no lugar;
   - grava o nome a partir de um texto que o `dialog.tlk` já tem (strref), sem mexer no `dialog.tlk`, o que mudaria a build;
   - grava a animação do `ANIMATE.IDS`, os PV, o TACO, os ataques, os atributos, as salvaguardas, a moral, o XP, o ouro, o nível, a classe, a raça, o sexo e o alinhamento;
   - grava o nome nosso (`INFAI_*`);
   - a CA natural fica em 10 (sem armadura), e o jogo soma armadura e Destreza; o valor no jogo é conferido e comparado com o da ficha;
   - mantém a tabela de memorização da base, esvazia magias e efeitos, tira os scripts e o diálogo do jogo;
   - recusa ficha incompleta (com o campo), base morta, nome inexistente e animação inexistente.
4. **Itens (D2):** os da ficha, achados no BG2 pelo mesmo nome (strref do nome identificado) e postos nos espaços certos, já identificados. Item não achado fica de fora, com aviso.
5. **Sem magias (D3) e sem combate (D5):** neutra, sem script de combate, conversa só pela nossa caixa.
6. **Identidade:**
   - registro `character:tamoko` em `knowledge/encyclopedia/characters/bg1/` (BG1, `CROSS_REFERENCED`, fonte `thgl-bgee`);
   - ficha curada em `knowledge/npcs/tamoko.pt_BR.json`, com o id que a caixa dá pelo nome de script (`npc:infai_tamoko`);
   - a história é rascunho (D4): a visão sabe quem foi, que está morta, que não sabe como nem onde morreu e que o diário de Sarevok sumiu; só vale depois da aprovação do mantenedor, e até lá o carregamento das fichas a ignora.

7. **Aparência de visão** (mantenedor, 2026-11-18: "Ela, translúcida"):
   - o corpo é o dela no BG1: a animação de clériga humana (`CLERIC_FEMALE_HUMAN`, a mesma da wiki) e as sete cores do corpo, tiradas da imagem do BG1 e casadas com a paleta de gradientes da build (`MPAL256`); as cores ficam na ficha local;
   - `--vision` grava dois efeitos permanentes na criatura: translucidez (opcode 66) e um brilho pálido pulsando no corpo inteiro (opcode 50);
   - o resultado no jogo é conferido pelo mantenedor e vai para a evidência.
8. **A visão não é viajante:** no primeiro teste, com o estatuto `FORASTEIRO`, ela respondeu "estou de passagem". A curadoria passa a aceitar o estatuto `VISAO` (só curado, nunca gerado):
   - sabe o que um forasteiro sabe (a terra de origem, nada do lugar);
   - os fatos dizem que ela aparece no lugar como visão e de onde era em vida, sem "de passagem" nem "não conhece os costumes";
   - a validação recusa, numa visão, dizer que está de passagem ou que é viajante (`SELF_CLAIM:VISION`), além de dizer que mora aqui.

## Consequências

- O mesmo gerador serve para qualquer ficha de BG1/SoD (TH.GL) e depois para as de IWD.
- Heróis cujo arquivo de criatura já existe no BG2 (Drizzt, Elminster) não precisam de ficha: uma cópia com o nome nosso (ADR-0136) e uma ficha curada de 1369 bastam.
- A quest com presença (SPEC-011) passa a poder pôr Tamoko numa área, por decisão do código.

## Verificação

- **`tests/test_creatures.py`:**
  - a ficha completa e os campos ruins nomeados;
  - cada campo gravado no lugar certo;
  - neutralidade, sem scripts, sem diálogo, nome nosso;
  - a estrutura: memorização mantida, três itens nos espaços certos e identificados, arma selecionada, efeitos vazios;
  - as cores da ficha nos lugares certos e os dois efeitos da visão (opcode, alvo, valores, duração permanente, chance de 100%);
  - item ausente, base morta e base que não é CRE;
  - o rascunho da história não é usado antes da aprovação.
- **No jogo:** evidência própria.
