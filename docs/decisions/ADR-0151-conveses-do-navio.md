# ADR-0151 — Os outros conveses da *Estrela de Waukeen*

**Estado:** APROVADA (mantenedor, 2026-11-27: "Aprovar como proposta", D1 a D8 na opção recomendada, com o ajuste dos camarotes dos mercadores sob o tombadilho). SPEC-014, fase 4.

**Relaciona-se com:** ADR-0150 (área renderizada, câmera, peças e estilo), ADR-0149 (arquivos), ADR-0146 (passagens), quest dos reféns (fase 3 da SPEC-013).

**Gate:** etapa 1, laboratório, single player, save descartável.

## Contexto

A quest dos reféns pede o navio inteiro, ligado convés por convés. O porão (`IA0004`, ADR-0150) já existia. Faltavam:
- o convés do meio;
- os camarotes dos mercadores: o mantenedor pediu que um navio mercante os tivesse, no estilo da AR0515, sob a parte alta do convés onde fica o leme;
- o convés superior: o primeiro exterior, com o mar e a noite.

## Decisão

1. **As três áreas**, no mesmo estilo do porão: madeira avermelhada, lanternas de ferro, caixotes, fardos, barris e redes. Câmera, script e verificador são os da ADR-0150, e cada área passou por prévias até a aprovação do mantenedor.

   | Área | O que é | Tamanho | Aprovada na |
   |---|---|---|---|
   | `IA0003` | convés do meio: o alojamento da tripulação, com redes de dormir, baús, a **mesa posta** (no modelo das mesas da AR0515 e da Coroa de Cobre), um cavalete de redes, a escada que sobe e o alçapão que desce | 960 × 768 | prévia 4 |
   | `IA0005` | camarotes dos mercadores: corredor, dois camarotes pequenos com divisórias e vãos de porta, e um camarote grande com as **janelas de popa**; camas de colunas, **tapetes no modelo da AR0515** (borda trançada com nós, filetes e miolo manchado), mesa de cartas, armário | 640 × 576 | prévia 5 |
   | `IA0002` | convés superior: o navio inteiro com o casco e a amurada, o **tombadilho** com a escada, o leme e a porta dos camarotes, o mastro com o cordame, o alçapão com grade, o mar à noite e o **barco a remo** (no modelo do barco das Docas) onde o grupo chega | 2560 × 1920 | prévia 4, ajustada no jogo |

2. **Peças novas no script:**
   - redes de dormir, mesa, banco e baú;
   - alçapão no piso e alçapão com grade;
   - mesa posta;
   - divisória com vão de porta, cama de colunas, tapete, cadeira, armário e janela de popa;
   - casco em polígono com amurada, mar, tombadilho, escada de degraus, porta dupla;
   - cordame, roda do leme, cabrestante, rolo de corda, poste de lanterna;
   - escada de corda e **rede de abordagem**;
   - barco a remo.
3. **Engenharia nova na cena** (`scene.py`, `camera.py`):
   - **Contornos em polígono:** o casco, o barco, o tombadilho e a escada são pintados no mapa de busca como polígonos, em uma ordem fixa: pisos, casco, peças no convés, corpo do tombadilho, tampo, escada, peças lá em cima e balaustrada.
   - **Piso elevado:**
     - o tampo do tombadilho, projetado na altura dele, é onde se anda lá em cima;
     - a frente e o corpo bloqueiam;
     - a escada liga os dois.
     - Peças podem ficar em cima dele (`floor`), e os marcadores têm altura (`z`).
   - **Subir a bordo:** a faixa de subida vai do barco, cerca de 2,15 m abaixo do convés, até o convés, e cobre a escada de corda e as redes de abordagem ao lado (`climb_half`). O resto do casco bloqueia.
   - **`open_sight`:** no convés aberto, nada tapa a visão; o que bloqueia a passagem continua bloqueando (código 8).
4. **A área entregue explorada (`explored` na receita):**
   - o `ARE` leva um mapa de exploração todo marcado;
   - o tamanho foi medido num save: um bit por quadrado de 32 px numa grade de (largura/32 + 1) × (altura/32 + 1). Bateu em AR0300, AR0406, AR0069, AR0311 e IA0090.
   - Assim o mar e o navio aparecem inteiros desde a chegada; fora da visão do grupo, o jogo só escurece, como em qualquer área.
5. **As passagens** (uma quest local de teste abre todas):
   - cais das Docas → barco;
   - alçapão do convés superior ↔ pé da escada do convés do meio;
   - porta sob o tombadilho ↔ porta dos camarotes;
   - alçapão do convés do meio ↔ pé da escada do porão.

   Cada uma volta pelo mesmo ponto.
6. **`render_area.py`:** apaga o desenho anterior antes de renderizar e pede ao Blender que saia com erro se o script falhar. Uma falha deixava o desenho antigo sem aviso (achado no laboratório).

## No jogo (evidência S2n)

Aprovado em 2026-11-27, depois de três ajustes no convés superior:
1. **Recorte em volta do navio e tela sem mar.** Era a névoa de guerra da área não explorada, mais as sombras de visão do mastro e da carga, numa área menor que a tela. **Correção:** área de 2560 × 1920, entregue explorada, com visão livre no convés. O círculo de visão do grupo continua, como em toda área do jogo, mais visível à noite.
2. **O grupo subia pelo casco.**
   - A faixa de subida era inclinada e larga; depois ficou estreita demais (uma célula), e o motor empurrava quem esperava a vez para o casco ao lado.
   - Uma escada larga também não resolveu.
   - **Correção, pela ideia do mantenedor:** escada estreita e **redes de abordagem** dos dois lados, com a faixa de subida cobrindo escada e redes. Quem sai da linha da escada sobe pela rede.
3. **A rede saiu cinza e lisa:** a malha era fina demais na escala do jogo. Ficou uma malha de 20 cm, com o vão da escada no meio.

## Consequências

- O navio da quest dos reféns está completo: quatro áreas, ligadas.
- **O que fica para o agente de áreas:**
  - exterior com mar;
  - casco em polígono;
  - pisos em alturas diferentes;
  - cômodos com divisórias;
  - mesa posta;
  - escada e redes de abordagem;
  - área entregue explorada.
- **Fora desta ADR:**
  - a troca de dia e noite do motor;
  - portas do motor;
  - balanço e animações;
  - a quest dos reféns em si.

## Verificação

- **`tests/test_area_scene.py`:**
  - as quatro receitas do navio passam no verificador sem erro nem aviso;
  - tombadilho (tampo andável, frente bloqueada, escada);
  - chegada no barco e subida pela escada e pelas redes, com o casco bloqueado além delas;
  - peça e marcador na altura do tombadilho;
  - tamanho do mapa de exploração comparado com o jogo, área entregue explorada;
  - visão livre no convés aberto.
- **No laboratório, fora da suíte:**
  - todos os cômodos alcançáveis a partir da entrada: os três camarotes, a mesa, as redes, a proa, o tombadilho;
  - o mapa de onde se anda conferido em recortes.
- **No jogo:** evidência S2n.
