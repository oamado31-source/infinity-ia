# ADR-0149 — Os arquivos de uma área nova

**Estado:** APROVADA (mantenedor, 2026-11-27: "Aprovar como proposta", D1 a D5 na opção recomendada). Fase 2 da SPEC-014 (o básico do módulo 014.4).

**Relaciona-se com:** SPEC-014 (REQ-MAP-001 a 012), SPEC-010, ADR-0146 (área nossa e passagens), ADR-0136 (gateway), CR-2026-030.

**Gate:** etapa 1, laboratório, single player, save descartável.

## Contexto

Até aqui só sabíamos **copiar** uma sala do jogo (`IA0001`, ADR-0146): o `WED` continuava apontando para o desenho original, e o `ARE` era o do jogo com partes zeradas. Um mapa novo precisa que **todos os arquivos sejam escritos por nós**. A SPEC-014 decidiu que o agente cria mapas novos, e esta ADR faz a base disso, provada com uma sala desenhada só por código antes de qualquer Blender.

**Medido no laboratório (2026-11-27)**, em AR0310, AR0515 e AR1607:
- `TIS` da versão 2: 12 bytes por tile (página, x, y), tiles de 64×64. No BIF, fica na tabela de tilesets, sem cabeçalho;
- páginas `PVRZ`:
  - DXT1 em PVR3 com `zlib`, em potências de 2 até 1024, não necessariamente quadradas (a da AR0515 tem 1024×512);
  - nome = 1ª letra do `TIS` + 4 últimas + página;
  - nenhuma página do jogo começa com `I`;
- `WED`:
  - 5 camadas declaradas; as vazias têm 0×0 e apontam para o fim dos dados;
  - paredes com marca 1 (ou 9 e 5), altura -1;
  - grupos de 640×480;
- `SR` e `HT` de 4 bits, `LM` de 8, todos com largura/16 × altura/12. Piso plano = altura 8;
- `MOS` versão 1, a 1/6,4 da área, em blocos de 64;
- `ARE` de interior: tipo 0, as cinco músicas 0 e as cinco alternativas -1, volumes 100, sem mapa de exploração.

## Decisão

1. **Ler o que o jogo tem** (`src/infinity_ai/gamedata/`):
   - o `KEY` guarda o índice de tileset do localizador;
   - o leitor de recursos lê a tabela de tilesets do BIF e monta o cabeçalho do `TIS` (`_Resources.tis`);
   - o leitor nunca mais tira um `TIS` da tabela de arquivos. Antes, ele devolvia outro recurso no lugar (um áudio).
2. **Escrever uma área nova** (`src/infinity_ai/areas/`), só com a biblioteca padrão, a partir da documentação pública dos formatos (IESDP):
   - `dxt` (DXT1 sempre no modo de 4 cores; leitura de DXT1 e DXT5);
   - `tis` (`TIS` v2 e páginas);
   - `wed` (5 camadas, um tile por célula, paredes e grupos; **sem portas**, D4);
   - `maps` (`SR`, `HT`, `LM`);
   - `mos`;
   - `are` (sala vazia com as entradas);
   - `procedural` (desenho por código, determinístico);
   - `png` e `preview` (prévias locais).
3. **A receita** `infinity-ai.area-recipe.v1`:
   - os arquivos: o leitor estrito `areas/recipe.py` e o esquema `knowledge/areas/area-recipe.v1.schema.json`;
   - os campos: nome `IA####`, tipo, tamanho em tiles, piso, desenho `procedural` (o `render` fica para a fase 3), regiões (o que se desenha e onde se anda), paredes, entradas, pontos de passagem, luz e proveniência;
   - a saída vai para `~/.infinity-ai/areas/<IA####>/`, com um `manifest.json` que guarda o `sha256` da receita e de cada arquivo.
4. **O verificador** (`areas/check.py`, `tools/area-author/check_area.py`) relê os arquivos como o motor leria e recusa com erro nomeado:
   - **erros:** `AREA_NAME`, `PAGE_NAME`, `WED_OVERLAYS`, `MAP_SIZE`, `TILE_COUNT`, `ENTRANCE_BLOCKED`, `NO_PATH` (busca na grade), `MISSING_REF` e `WALL_OUTSIDE`;
   - **avisos:** `NO_WALLS`, `BIG_AREA` e `WALL_BASELINE` (achado no jogo, abaixo).
   - **A linha de base de uma parede são os seus dois primeiros pontos** (o pé da parede). O motor desenha a parede por cima de quem está acima dessa linha. Um retângulo da receita começa pela borda de baixo, como as paredes do jogo.
5. **Laboratório:**
   - **`build_new_area.py`:**
     - gera os arquivos e verifica contra todos os nomes da build (lidos do `KEY` por SSH);
     - com `--apply` e o jogo fechado, grava no override;
     - recusa nome que não seja nosso.
   - **`area_preview.py`:** desenha qualquer área num PNG local (`~/.infinity-ai/previews`). Com `--roundtrip`, regrava uma sala do jogo pelos nossos escritores e compara.
6. **Repositório:**
   - `check_public_files` recusa também `.tis`, `.pvrz` e `.pvr`;
   - receitas e código ficam no repositório; arquivos gerados e prévias, não.
7. **A sala de teste `IA0090`** (D1), em `knowledge/areas/ia0090-sala-de-teste.json`:
   - **tamanho:** 12×9 tiles;
   - **desenho:** piso de tábuas, parede de pedra ao norte, bordas escuras e um pilar no meio;
   - **onde se anda:** o pé do pilar é obstáculo, e o pilar inteiro é parede (quem passa atrás fica translúcido);
   - **entrada:** uma, ao sul.
   - Gera 8 arquivos, com cerca de 34 KB, em cerca de 1 s.

## Conferência no laboratório

`area_preview.py --roundtrip` em AR0310, AR0515 e AR1607, em 2026-11-27:

| Sala | Desenho regravado | Mapa de busca | Paredes | Grupos de parede |
|---|---|---|---|---|
| AR0310 | 41,1 dB | igual | iguais (9) | iguais (4) |
| AR0515 | 42,9 dB | igual | iguais (24) | contêm os do jogo, 2 entradas a mais |
| AR1607 | 42,0 dB | igual | iguais (185) | contêm os do jogo, 15 entradas a mais |

**Duas lições:**
- **Grupos de parede:** o nosso grupo inclui todo polígono cuja caixa toca a célula, então às vezes tem um polígono a mais que o do jogo, nunca a menos. Um polígono a mais só custa uma conferência a mais ao motor.
- **Polígonos degenerados:** a AR1607 tem polígonos com menos de 3 pontos. Nas nossas áreas, o escritor os recusa (`WALL_OUTSIDE`). Só a conferência de salas do jogo os aceita (`strict=False`).

## No jogo (evidência S2l)

A sala `IA0090` foi aprovada no jogo em 2026-11-27, na segunda instalação. Funcionaram:
- a passagem do cais das Docas e a volta;
- o desenho, os bloqueios e a linha de visão (o pé do pilar faz sombra);
- o mapa da área;
- a entrega da quest de teste.

**Achados:**
- **A parede do pilar não escondia ninguém.**
  - A primeira versão do retângulo começava pelo lado de cima, então a linha de base ficava no topo e ninguém ficava acima dela.
  - A regra veio do GemRB, que reimplementa o motor (só lido, nada copiado), e das paredes das salas do jogo, que começam pelo canto de baixo.
  - **Correção:** o retângulo começa pela borda de baixo, e o verificador avisa com `WALL_BASELINE`.
- **Nas Enhanced Editions, quem está atrás de uma parede fica translúcido**, não some por inteiro.
- **O estilo dos mapas de BG vem na fase 3**, com o render. A sala desenhada por código só prova os formatos.

## Consequências

- Primeira área em que **nenhum byte é do jogo**: tudo sai da receita.
- A fase 3 (o porão do navio) só troca a origem do desenho (`render`) e passa a tirar as paredes do render.
- O agente de áreas (fase 5) já tem o formato da receita e os verificadores.
- **Fora desta ADR:** portas e escotilhas (fase 3, com o alçapão), dia e noite, luz variável, animações e sons ambientes.

## Verificação

- `tests/test_area_files.py`:
  - DXT1 (cor sólida exata, gradiente acima de 30 dB, sempre 4 cores);
  - páginas (nomes, potências de 2, mais de uma página);
  - `WED` (5 camadas, grupos);
  - mapas (tamanho, ida e volta de 4 e 8 bits);
  - `MOS` a 1/6,4;
  - `ARE` vazio;
  - PNG;
  - a tabela de tilesets de um BIF sintético, e a recusa de tirar `TIS` da tabela de arquivos.
- `tests/test_area_recipe.py`:
  - o esquema e a sala de teste, sem erro nem aviso;
  - mesma receita, mesmos bytes, e o manifesto;
  - o pilar bloqueia, e atrás dele há madeira;
  - um caso por erro nomeado e os avisos.
- `tests/test_area_recipe.py` também confere a linha de base do pilar e o aviso `WALL_BASELINE`.
- **No jogo:** evidência S2l.
