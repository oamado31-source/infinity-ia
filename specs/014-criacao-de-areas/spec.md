# SPEC-014 — Criação, reconstrução e engenharia de áreas

**Status:** APROVADA COMO PROPOSTA (mantenedor, 2026-11-27: "Aprovar como proposta", D1 a D5 na opção recomendada). Corrigida antes do merge, a pedido do mantenedor: o navio da quest é um **mapa novo**, criado por nós, e não o navio de Balduran do BG1 (D4). Cada fase de código ou instalação ainda pede a sua ADR ou CR (ADR-0111).
**Rastreabilidade:** SPEC-010 (inventário geográfico: o catálogo das fontes); SPEC-013 (autoria de quests: quem consome as áreas); ADR-0146 (área nossa e passagens); ADR-0136 (gateway); CR-2026-030 (dados do jogo fora do repositório); CR-2026-032 (recursos de outros jogos só no laboratório); CR-2026-034 (o esconderijo, primeira área nossa).
**Origem:** a ideia do mantenedor ("Map Creation, Reconstruction & Area Engineering"), em 2026-11-27. A ideia numerava os módulos como 011.x, mas a SPEC-011 já existe.

## Objetivo

Criar áreas além das que existem nos jogos e expansões é um dos objetivos principais do Infinity AI. A SPEC-010 cataloga o que existe e com que direitos, e deixa a criação de áreas para "especificação posterior" (§9). Esta é essa especificação:
- **a SPEC-010 é o catálogo;**
- **a SPEC-014 é a oficina:** como criar um mapa novo, verificá-lo e entregá-lo a uma quest, e depois como um agente faz isso seguindo estas regras.

**O agente cria mapas novos** (mantenedor, 2026-11-27):
- ele monta uma cena 3D (planta, modelos e texturas de licença aberta), renderiza na câmera do jogo e gera a área;
- importar ou copiar mapas de outros jogos e módulos **não** é o caminho do agente. A reconstrução (014.2) fica como capacidade secundária, para um caso pontual aprovado pelo mantenedor.

**Invariantes:**
- nenhum byte de jogo ou de mod vai ao repositório (CR-2026-030, REQ-CANON-004). No repositório só há código, testes e **receitas**;
- a instalação vai só ao override do laboratório, com o jogo fechado, e com nomes nossos (`IA` e quatro dígitos, ADR-0146);
- nada de outro jogo fora do laboratório (CR-2026-032);
- nenhuma fonte sem direitos claros entra numa receita distribuível (REQ-AREA-007 da SPEC-010);
- uma área só é aprovada depois que o mantenedor anda nela no jogo.

## 1. A escada de complexidade

| Degrau | O que é | Situação |
|---|---|---|
| 1 | Copiar uma sala do mesmo jogo | feito: `IA0001`, a caverna sob o Farol (ADR-0146) |
| 2 | Trazer uma sala de outro jogo do mesmo motor | capacidade prevista (014.2), sem caso marcado |
| 3 | Compor uma área nova costurando tiles de salas existentes | alternativa |
| 4 | **Desenho novo, renderizado de uma cena 3D** | **o objetivo desta SPEC**; primeiro caso: o navio da quest dos reféns |

**Medido no laboratório (2026-11-27), em três salas do BG2:EE** (AR0310, AR0515 e AR1607):
- o `TIS` é da versão 2: cada tile de 64×64 aponta para uma página de textura `PVRZ` (DXT);
- o nome da página sai do nome do `TIS` (`A` + `0310` + número da página);
- no BIF, o `TIS` fica na tabela de tilesets, separada da de arquivos. O leitor de recursos de hoje (`_Resources`) ainda não a lê;
- o `MOS` é da versão 1 (paleta), e os `BMP` de busca, luz e altura têm 1/16 × 1/12 da área;
- os três `WED` declaram 5 camadas;
- os nomes de área do jogo (`AR####`) se repetem entre os jogos (o BG2 já tem `AR1400` a `AR1404`): toda área nossa usa nome próprio (`IA####`).

## 2. Os módulos

| Módulo | Responsabilidade | O que já existe |
|---|---|---|
| **014.1 Fontes** | a biblioteca do agente: **modelos 3D e texturas de licença aberta** (CC0, CC BY), cada um com autor, URL, licença e `sha256`. As salas do jogo servem de referência de escala, câmera e estilo, não de matéria-prima. O catálogo da SPEC-010 só entra para a reconstrução | catálogo da SPEC-010 (proposta) |
| **014.2 Reconstrução** (secundária) | trazer uma área que existe em outro jogo do mesmo motor, com nomes nossos e referências limpas, só num caso pontual aprovado; não é o caminho do agente | cópia de sala do BG2 (`build_area.py`) |
| **014.3 Criação** (o centro da SPEC) | mapas novos: (b) **render 3D** no Blender a partir de uma cena montada pelo agente; (a) composição com tiles de salas existentes, como alternativa | nada |
| **014.4 Engenharia** | os formatos: `ARE`, `WED` (camadas, paredes, portas), `TIS` v2 e páginas `PVRZ`, `MOS`, `SR`/`HT`/`LM`, dia e noite, portas, luz e onde se anda | `make_area` (o `ARE` sem nada do jogo agindo) |
| **014.5 Validação e integração** | verificadores automáticos, instalação no override do laboratório, pin, evidência no jogo com capturas, entrega dos nomes e pontos para a quest (SPEC-013) | gateway, `TRAVEL`, pin e passagens |

### 2.1 A receita da área

A peça central é a **receita**.
- **O que é:** um JSON no repositório, sem nenhum byte de jogo, que diz como produzir a área:
  - os nomes nossos e o tipo (interior, exterior, subterrâneo);
  - a cena: a planta, os modelos e texturas (com autor, URL, licença e `sha256`), as posições, a luz e a câmera;
  - os pavimentos e as ligações entre eles;
  - o que é parede, porta e onde se anda, quando não sai sozinho do render;
  - as passagens e os pontos que a quest vai usar;
  - só na reconstrução ou na composição: as fontes do jogo, com build (impressão digital) e `sha256`, e o que é renomeado ou limpo.
- **Quem faz o quê:** o agente escreve a receita; a ferramenta renderiza no Blender e gera os arquivos da área.
- **Por quê:**
  - um mapa renderizado de modelos de licença aberta é **arte nossa**, que não depende do jogo de ninguém;
  - a receita reproduz o mapa inteiro, e os arquivos gerados (grandes) ficam fora do repositório;
  - um dia, receita e créditos dos modelos podem ser distribuídos.

## 3. Requisitos

- **REQ-MAP-001, interiores e exteriores:** a receita declara o tipo (interior, exterior ou subterrâneo). Um exterior tem dia e noite (`N`); um interior não precisa.
- **REQ-MAP-002, vários pavimentos:** cada pavimento é uma área própria (`IA####`). A receita declara a pilha, de cima para baixo, e as ligações entre os pavimentos.
- **REQ-MAP-003, escadas, escotilhas, elevadores e transições:**
  - toda ligação é uma passagem nossa (ADR-0146), com ponto de saída e de chegada em célula onde se anda;
  - uma porta do motor (alçapão, porta) mantém juntas a porta do `ARE` e a do `WED`, com os tiles de aberta e de fechada;
  - um elevador é uma passagem com condição.
- **REQ-MAP-004, mar e embarcações:**
  - embarque e desembarque por passagem, a partir de um ponto do cais;
  - o mar visível é cenário, sem células onde se anda;
  - inclinação e balanço ficam fora da v1.
- **REQ-MAP-005, reaproveitar geometria e tiles:**
  - a composição copia tiles inteiros de 64×64, sem recomprimir (os blocos DXT têm 4×4);
  - as páginas são remontadas com o nome derivado do nosso `TIS`;
  - na vertical, os pedaços têm múltiplos de 3 tiles, para o mapa de busca (escala 16×12) encaixar.
- **REQ-MAP-006, perspectiva do jogo:**
  - o render usa a câmera e a escala medidas no próprio jogo, com o tamanho de um personagem como referência;
  - uma área composta não mistura salas de escalas ou perspectivas diferentes. O verificador compara as escalas.
- **REQ-MAP-007, onde se anda e bloqueios:**
  - o mapa de busca tem largura/16 × altura/12, arredondado para cima;
  - toda entrada, ponto de passagem e ponto de presença cai em célula onde se anda;
  - existe caminho entre as entradas, verificado por busca no mapa;
  - as paredes cobrem o que deve esconder personagens.
- **REQ-MAP-008, versão e proveniência:**
  - cada receita tem versão;
  - cada arquivo gerado registra a receita e as fontes (`sha256`);
  - modelos e texturas guardam autor, URL e licença.
- **REQ-MAP-009, referências:** nada citado no `ARE` (sons, animações, músicas, scripts, criaturas, itens, `WED` e `TIS`) pode faltar na build de destino.
- **REQ-MAP-010, formato seguro:**
  - `WED` sempre com 5 camadas declaradas;
  - nomes de 6 caracteres para os `TIS` (assim as páginas ficam com 8);
  - nenhum nome nosso colide com recurso da build.
- **REQ-MAP-011, só no laboratório:**
  - instalação no override do laboratório, com o jogo fechado;
  - o verificador de arquivos públicos recusa também `.tis` e `.pvrz`.
- **REQ-MAP-012, evidência:** uma área só é aprovada depois de andar nela no jogo (entradas, paredes, portas e passagens), com capturas da VM.

## 4. Ferramentas externas

| Ferramenta | Licença (2026-11-27) | Papel |
|---|---|---|
| [MapSmithEE](https://github.com/sad0/MapSmithEE) 0.2.6 | CC BY-NC-SA 4.0; o README diz que o que se faz com ele herda a licença | **referência e ferramenta do mantenedor** no laboratório. Mostra que o degrau 4 é viável: render no Blender na câmera do jogo, paredes pelos contornos de cada peça, desenho e mapas derivados do render. Prévia, com um bug conhecido de `WED`. Nenhum código dele entra no Infinity AI |
| [Near Infinity](https://github.com/Argent77/NearInfinity) | LGPL-2.1 | ferramenta do mantenedor para abrir e conferir áreas geradas |
| DLTCEP | — | ferramenta do mantenedor, editor antigo de recursos do motor |
| IETME | — | já no catálogo da SPEC-010; editor antigo de mapas de tiles |
| Blender | GPL | roda sem tela (`blender -b -P script.py`), **no Mac**. Os scripts são nossos (Apache 2.0, compatível com a GPLv3) |

O pipeline do agente é **nosso**, escrito a partir da documentação pública dos formatos (IESDP), com modelos CC0.

## 5. O navio da quest dos reféns

O navio, a *Estrela de Waukeen*, é o **primeiro mapa novo** do Infinity AI: um mapa que não existe em jogo nenhum, feito por nós. Não usa o navio de Balduran nem outro mapa do BG1, que o mantenedor não tem instalado.

| Caminho | Módulos | Resultado |
|---|---|---|
| **B. conveses renderizados no Blender** (o caminho) | 014.3b + 014.4 | mapa novo, distribuível como receita mais modelos CC0 |
| C. conveses compostos com tiles do BG2 | 014.3a + 014.4 | alternativa, se o render travar |

**A ordem dentro do navio:**
1. **um pavimento primeiro, o porão**, que é a geometria mais simples (piso de tábuas, casco, carga, a cela dos reféns), como teste do pipeline inteiro;
2. depois o convés do meio e o convés superior, reaproveitando a câmera, o casco e os modelos do porão;
3. a quest dos reféns (fase 3 da SPEC-013) usa os três pavimentos.

## 6. Fases

1. Esta SPEC, registrada como proposta, e as ferramentas no catálogo da SPEC-010.
2. **014.4 básico** (ADR):
   - gravar `TIS` v2 e páginas `PVRZ` com nome nosso, e lê-los (da tabela de tilesets do BIF) para conferir e para as salas do BG2 de referência;
   - `WED` com 5 camadas, paredes e portas;
   - `SR`, `HT` e `LM` a partir de uma grade;
   - verificador de referências e de onde se anda;
   - formato da receita;
   - testes que leem e regravam as salas do BG2 sem perda.
3. **O porão do navio** (ADR):
   - medir a câmera e a escala do jogo;
   - script do Blender sem tela, no Mac, com modelos CC0;
   - desenho, paredes e mapa de busca derivados do render;
   - evidência no jogo.
4. **Os outros dois conveses**, e a quest dos reféns montada pelo agente (fase 3 da SPEC-013).
5. **Agente de áreas:** skill de autoria de áreas, como a de quests. A partir do que a quest pede (tipo, tamanho, pavimentos, pontos), ele:
   - monta a cena com a biblioteca de modelos;
   - escreve a receita;
   - renderiza;
   - roda os verificadores;
   - entrega os nomes e os pontos para a quest.

## 7. Decisões tomadas (2026-11-27)

- **D1:** SPEC própria, separada da SPEC-010.
- **D2:** MapSmithEE, Near Infinity e DLTCEP entram no catálogo da SPEC-010 como `MODDING_TOOL`.
- **D3:** MapSmithEE só como referência e ferramenta do mantenedor; o pipeline do agente é nosso, Apache 2.0.
- **D4 (corrigida antes do merge):** o navio é um mapa novo renderizado no Blender (caminho B), começando pelo porão. Nada do BG1.
- **D5:** o Blender roda no Mac; só os arquivos prontos vão para a VM.
