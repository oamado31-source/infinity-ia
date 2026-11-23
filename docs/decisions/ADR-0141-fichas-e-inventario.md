# ADR-0141 — Fichas de Gregor, Kalessia e dos carcereiros, e o diário no inventário

**Estado:** APROVADA (mantenedor, 2026-11-22: "Aprovar como proposta", decisões D1 a D6 na opção recomendada, os fatos de Gregor e Kalessia como escritos).

**Origem:** as peças F e C da quest "O diário perdido de Sarevok":
- três novas criaturas nossas: Gregor (o desertor preso), Kalessia (a líder da célula) e os carcereiros (verbeegs);
- o diário de Sarevok na mochila de Kalessia.

**Relaciona-se com:**
- ADR-0137 (criatura de ficha e o gerador);
- ADR-0140 (cópias e passo de derrota);
- CR-2026-030 (ficha local, registro curado no repositório).

**Gate:** etapa 1, single player, save descartável. Neutros e sem combate; hostilidade e magias são a peça D.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-22.

1. **Fontes (D1, D2):**
   - Gregor e Kalessia: a wiki do BG (`bg-fandom-wiki`), com todos os campos;
   - o verbeeg: o **Complete Compendium** (`complete-compendium`, novo em `sources.json`), que transcreve o *Monstrous Manual* do AD&D 2ª edição e indexa todos os monstros da edição. O mantenedor achou a página e pediu o registro do site inteiro para consultas futuras;
   - as fontes abertas de Icewind Dale não tinham números;
   - os números ficam só nas fichas locais (`~/.infinity-ai/sheets/`), consultadas por entidade, sem texto copiado.
2. **Nomes que já existem no `dialog.tlk`:** "Gregor", "Kalessia" e **"Carcereiro"**. "Verbeeg" não existe em português, e "Carcereiro" é o papel deles.
3. **Três campos opcionais na ficha**, para criaturas que não são personagens:
   - `natural_ac`: CA sem armadura, 10 por padrão;
   - `str_extra`: força excepcional, 18/xx;
   - `race: "BASE"`: fica a raça e o tipo geral do corpo, como gigante para o ogro.
4. **Escolha de item segura (D4):**
   - entre os itens do jogo com o nome da ficha, ficam só os de tipo compatível com o espaço;
   - se ainda sobrar mais de um, o gerador recusa (`ITEM_AMBIGUOUS`) e lista os candidatos, e a ficha local fixa o `resref`;
   - um resref fixado precisa ser um dos candidatos (`ITEM_PIN_MISMATCH`);
   - motivo, achado no laboratório: "Espada Curta +1" incluía flechas e virotes, e "Cajado" incluía o cajado de um chefe de ToB, que a ordem alfabética escolhia.
5. **Mochila (peça C):**
   - itens `INVENTORY` na ficha ocupam os 16 espaços da mochila, em ordem;
   - `--carry ITM` acrescenta um item da campanha. É o caso do **diário de Sarevok (`SCRL3F`) na mochila de Kalessia**: identificado, sem a marca de "não larga", então cai no chão quando ela cai (D5).
6. **As três criaturas:**
   - **`IAGREGOR` / `INFAI_GREGOR`:** ladrão humano de nível 6, prisioneiro sem armas nem armadura (D3), animação `THIEF_MALE_HUMAN`;
   - **`IAKALESS` / `INFAI_KALESSIA`:** maga humana de nível 5, com o traje de resistência ao frio, o cajado (`STAF01`) e o diário na mochila; sem magias por enquanto; animação `MAGE_FEMALE_HUMAN`;
   - **`IACARCER` / `INFAI_CARCEREIRO`:** a ficha do verbeeg sobre o corpo de um meio-ogro vivo do BG2 (`OGRHAL01`), com a animação **`GIANT_VERBEEG`**, do tamanho de um gigante. O caminho até ela:
     - primeiro a animação de verbeeg pura: o BG2:EE tem a definição (`E251.INI`, desenhos `MGVE`), mas não os desenhos, e os carcereiros ficaram invisíveis (contados, mas sem desenho);
     - depois o meio-ogro (`HALF_OGRE`), que desenha, mas tem porte humano: o motor não escala criaturas (mantenedor: "se ele é um gigante, deveria ser maior");
     - por fim, pela CR-2026-032 (aprovada), os desenhos e sons do verbeeg do **Infinity Animations** (33 arquivos, 5,2 MB, baixados do GitHub com a permissão do mantenedor). Eles foram instalados **só no override da VM** com os nomes que o `E251.INI` espera (`3dc*.bam` como `MGVE*.BAM`, `t-ver*.wav` como `VERBEE*.WAV`). Desenharam, com porte de gigante. Nada disso vai para o repositório.

     Conversão:
     - CA natural 4;
     - 28 PV (a média de 5d8+5);
     - TACO 15 e dois ataques;
     - Força 18/76;
     - inteligência 10, moral 13, 270 de XP, neutro e mau;
     - salvaguardas de guerreiro de nível 5;
     - clava (`BLUN01`) e escudo médio (`SHLD03`).
7. **Identidade (D6):**
   - **Gregor** (`knowledge/npcs/gregor.pt_BR.json`), forasteiro, de Baldur's Gate: filho de Brunos, entrou na célula para vingar o pai, recusa a nova guerra, desertou quando soube da morte de Tamoko e foi entregue aos carcereiros. **Onde fica o esconderijo não é fato dele**: vem da quest, só depois do resgate;
   - **Kalessia** (`knowledge/npcs/kalessia.pt_BR.json`), forasteira, de Sembia: emissária junto ao Trono de Ferro, reorganizou a célula em Athkatla para retomar o plano de guerra, guarda o diário e não o entrega;
   - registros `character:gregor` e `character:kalessia` em `knowledge/encyclopedia/characters/bg1/`;
   - os carcereiros não têm identidade própria.

8. **Animação sem desenhos é recusada** (laboratório, 2026-11-22). O BG2:EE lista no `ANIMATE.IDS` animações de Icewind Dale cujos desenhos só o IWD:EE traz: verbeeg, gigante do gelo, gigante da colina e gigante do fogo de IWD. `build_templates.py` lê o `<código>.INI` da animação e recusa quando nenhum desenho com aquele prefixo está na build nem no override.

## Consequências

- A quest do diário tem todas as criaturas. Falta a peça D (hostilidade e combate) e montar a quest.
- O gerador serve a qualquer monstro do AD&D 2ª edição que tenha uma animação **desenhada** no BG2:EE, sobre um corpo vivo de tamanho parecido.
- **As animações de Icewind Dale que o BG2:EE só define** (verbeeg, gigantes do gelo, da colina e do fogo de IWD, entre outras) passam a ter um caminho testado: os desenhos de um projeto de conversão, instalados no override do laboratório com os nomes do INI, uma criatura por vez (CR-2026-032).
- Um item com nome repetido não entra mais por acidente.

## Verificação

- **`tests/test_creatures.py`:**
  - os campos novos e o resref fixado, estritos;
  - corpo, raça mantida, CA natural e força excepcional nos lugares certos;
  - mochila e item da campanha, identificados e sem a marca de "não larga";
  - a escolha pelo tipo do espaço, a recusa do ambíguo e o resref fixado;
  - Gregor e Kalessia curados, sem o esconderijo nos fatos de Gregor.
- **No jogo:** os sete pontos da proposta, com evidência própria.
