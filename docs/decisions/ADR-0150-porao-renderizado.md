# ADR-0150 — Uma área renderizada: o porão da *Estrela de Waukeen*

**Estado:** APROVADA (mantenedor, 2026-11-27: "Aprovar como proposta", D1 a D6 na opção recomendada). Fase 3 da SPEC-014 (módulo 014.3b, criação por render 3D).

**Relaciona-se com:** SPEC-014 (REQ-MAP-004 a 008 e 012), ADR-0149 (os arquivos de uma área nova), ADR-0146 (passagens), quest dos reféns (fase 3 da SPEC-013), CR-2026-030.

**Gate:** etapa 1, laboratório, single player, save descartável.

## Contexto

A ADR-0149 escreve todos os arquivos de uma área a partir de uma receita, mas a sala de teste foi desenhada por código e não tem o estilo de BG. Esta ADR troca o desenho por um **render 3D no Blender**, na câmera do jogo, e faz o primeiro mapa novo de verdade: o porão do navio da quest dos reféns.

## A câmera do jogo (medida em 2026-11-27)

- **Ângulo:** inclinação 0,707 no contorno das salas no próprio desenho do jogo.
  - AR0070: 0,707, com 0,4 px de erro;
  - AR0313: 0,706 e 0,714;
  - AR0515: 0,702 e 0,705.
  - As salas são **giradas 45°**, e a câmera é **ortográfica, a 45° acima do horizonte** (o seno de 45° é 0,707).
  - A medição pela grade do mapa de busca dava 37°, puxada pela escada da grade de 16×12. Não vale.
- **Escala:** um humano tem cerca de 52,5 px do pé ao topo nas animações do jogo (`CHM*G1`); um elfo, 45 px; um anão, 34 px.
  - Com um humano de 1,8 m e câmera a 45°, isso dá **40 px por metro**.
- **Conferência no Blender:**
  - uma grade de 1 m caiu exatamente onde a projeção em Python prevê;
  - a coluna de 1,8 m tem 51 px de altura.

## Decisão

1. **Blender 4.5.17 LTS no Mac (D1):**
   - baixado de download.blender.org com o OK do mantenedor;
   - sha256 conferido contra o publicado, assinatura da Blender Foundation com notarização da Apple;
   - instalado em `~/Applications`;
   - roda sem tela. Nada vai para a VM além dos arquivos prontos.
2. **A câmera como conta** (`src/infinity_ai/areas/camera.py`): a mesma projeção do script do Blender, em Python testável sem Blender.
   - A pegada de cada objeto no chão vai para o mapa de busca.
   - O contorno de cada objeto que esconde vira uma parede, com a linha de base nos cantos laterais do pé (ADR-0149).
   - Uma pilha esconde de uma vez, do chão ao topo.
3. **A cena** `infinity-ai.area-scene.v1` (`knowledge/areas/scenes/`, D2):
   - em metros, com a câmera, as peças, as luzes e os marcadores;
   - as peças e os materiais são feitos pelo nosso script (`tools/area-author/blender/infai_render.py`), sem baixar modelos nem texturas;
   - **peças:** piso de tábuas, casco com cavernas, antepara, mastro, esteios, escada, cela de grades, caixotes com moldura e travessa, fardos de lona amarrados, barris bojudos com aros, cavaletes com redes de pesca e lanternas de ferro de parede.
4. **A receita do tipo `render`** (D3):
   - `picture: {kind: render, scene}`;
   - **o que sai da cena** (`scene.py`):
     - as regiões: o piso livre, e cada pé com o seu terreno;
     - as paredes;
     - as entradas e passagens, nomeadas pelos marcadores.
   - **terrenos:**
     - caixotes, fardos, mastro e esteios bloqueiam a passagem e a visão (`obstacle`, código 0);
     - grades, redes, barris e escada só bloqueiam a passagem (`open-obstacle`, código 8);
     - o casco é parede (`wall`), e o vazio em volta é obstáculo.
   - `render_area.py` renderiza (cerca de 16 s), e `build_new_area.py` lê o PNG (leitor nosso) e guarda no manifesto o `sha256` da cena e do desenho.
5. **As páginas de textura guardam blocos do desenho** (achado no jogo, abaixo):
   - cada página leva um bloco de até 16×16 tiles exatamente como está no desenho;
   - depois das bordas direita e de baixo, os pixels da borda são repetidos;
   - é o que fazem as páginas do jogo (AR0310 e AR0515).
6. **O estilo** (D5), com referência só nas salas do BG2, sem copiar nada:
   - **luz:** Cycles com Metal, luz baixa e quente das lanternas, luz fria fraca do alçapão;
   - **enquadramento:** vazio preto em volta, paredes da frente cortadas;
   - **escolhas do mantenedor:**
     - madeira avermelhada com relevo e pilares escuros, e lanternas de ferro de parede, no estilo da AR0515, como padrão de todos os conveses do navio;
     - caixotes, fardos e barris no estilo do armazém das Docas (AR0318);
     - três cavaletes com redes de pesca, como as redes secando da AR0318.
7. **Portas do motor** ficam para quando a quest v2 precisar da porta da cela (D4). A escada é uma passagem.

## O porão `IA0004`

- **Tamanho e orientação:** 22 × 8 m, girado 45°, em 960 × 768 px (15 × 12 tiles).
- **Arquivos:** oito, com cerca de 137 KB.
- **Conteúdo:**
  - costado com cavernas e antepara com a escada até o alçapão;
  - mastro e dois esteios;
  - pilhas de caixotes e fardos, barris e três cavaletes com redes;
  - a cela dos reféns num canto: fechada por grades em dois lados, pelo costado e pela borda da frente;
  - três lanternas.
- **Aprovação:** o mantenedor aprovou o desenho na prévia v10, depois de quatro rodadas de ajuste (madeira, lanternas, carga, redes).

## No jogo (evidência S2m)

Aprovado em 2026-11-27, na segunda instalação. Funcionaram:
- a passagem do cais das Docas até o pé da escada e a volta;
- o desenho;
- os bloqueios e a linha de visão;
- as paredes (quem passa atrás das pilhas, do mastro e dos cavaletes fica translúcido);
- o mapa da área.

**Achado: listas horizontais a cada 64 px.**
- Na primeira instalação, os tiles iam em filas de 16 nas páginas, sem seguir a largura do desenho (15 tiles). O vizinho de baixo na página não era o vizinho de baixo no desenho.
- Ao ampliar, o motor mistura a borda do tile com o pixel seguinte da página e puxava uma linha de outro lugar da sala. A sala `IA0090`, de 12 tiles de largura, tinha o mesmo defeito, mais fraco.
- **Correção:** a peça 5. Depois dela, as listas sumiram.

## Consequências

- Primeiro mapa que não existe em jogo nenhum, no estilo do jogo, feito só de código e de uma cena em texto: distribuível como receita.
- Os outros dois conveses do navio reaproveitam a câmera, as peças, os materiais e as lanternas.
- O agente de áreas (fase 5) monta cenas com o mesmo vocabulário de peças.
- **Fora desta ADR:**
  - portas do motor;
  - dia e noite;
  - animações (chamas) e sons;
  - balanço do navio;
  - texturas externas.

## Verificação

- **`tests/test_area_camera.py`:**
  - projeção de ida e volta;
  - inclinação igual ao seno da elevação;
  - alturas pelo cosseno;
  - pé de um objeto;
  - parede com a linha de base nos cantos laterais do pé.
- **`tests/test_area_scene.py`:**
  - a cena do porão e o marcador no desenho;
  - o piso primeiro;
  - paredes com a base no pé;
  - peças desconhecidas recusadas;
  - pilha que esconde do chão;
  - esquema das duas receitas;
  - o porão pede o desenho e passa no verificador sem erro nem aviso;
  - entrada livre e mastro bloqueado;
  - cena e receita precisam concordar;
  - leitor de PNG (ida e volta, filtros Sub e Up, RGBA).
- **`tests/test_area_files.py`:**
  - página como bloco do desenho;
  - vizinho de baixo na página igual ao do desenho;
  - borda repetida;
  - uma página por bloco.
- **`check_area`:** o aviso `WALL_BASELINE` só aparece quando algum ponto da parede fica abaixo da linha de base, para não acusar os objetos girados 45°.
- **No jogo:** evidência S2m.
