# Matriz decisória — ano-base com menor esforço de adaptação

**Discovery v1.4 | DEC-023 / ADR-0013 | 2026-11-06**  
**Resultado:** **1369 DR** selecionado para os **primeiros testes**, e **opção C** aprovada: época inicial configurável por campanha.  
**Limitação:** é uma decisão informada por evidências e prevalência do motor BG2/EET, **não uma medição real de arquivos `.ARE`, `.CRE`, scripts ou qualidade dos mods**. Os números abaixo são **diferenças cronológicas exatas em anos**, NÃO estimativas de horas de desenvolvimento.

## 1. Critério de decisão

Minimizar alterações obrigatórias em **recursos realmente disponíveis e prioritários**: áreas, geografia, NPCs, autoridades, facções, scripts, quests, objetos e eventos. O esforço de adaptação considera:

1. **Compatibilidade estrutural** (mesmo motor/recurso disponível no build, sem necessidade de reconstrução visual).
2. **Validade temporal** (idade, morte, cargo, estado físico de localidade, facção, comércio, epidemia, guerra).
3. **Isolamento narrativo** (scripts de BG1/BG2/NWN/IWD dependentes de protagonista, capítulo ou resultado da campanha original).
4. **Compatibilidade técnica** (ordem de instalação, conflitos de mods, multiplayer e bridge) — um custo **separado**, pois escolher o ano não corrige incompatibilidade de código.

### Hierarquia prática de reaproveitamento

- **Mais fácil:** texturas, cenários de interior, terreno natural, ruínas genéricas e criaturas sem identidade histórica.
- **Intermediário:** cidades, edifícios, comerciantes genéricos, guarnições e facções, conforme época.
- **Mais trabalhoso:** NPCs nomeados, governantes, quests da história principal, itens únicos associados a uma pessoa e enredos já resolvidos ou ainda futuros.

## 2. Matriz de distância entre obra e ano da campanha

Legenda: valores `+N` = N anos **depois** da obra; `−N` = N anos **antes**; `0` = contemporâneo **no nível de ano**, não necessariamente mês/dia. SoD e ToB são **intervalos incertos**, portanto não receberam distância exata como se houvesse consenso sobre data final.

| Conteúdo originário | Ano/intervalo da obra | 1368 DR | **1369 DR** | 1370 DR | 1372 DR |
|---|---:|---:|---:|---:|---:|
| Icewind Dale I | 1281 | +87 | **+88** | +89 | +91 |
| Heart of Winter | ~1281 | ~+87 | **~+88** | ~+89 | ~+91 |
| Trials of the Luremaster | ~1281 | ~+87 | **~+88** | ~+89 | ~+91 |
| Icewind Dale II | 1312 | +56 | **+57** | +58 | +60 |
| Baldur's Gate I + TotSC | 1368 | 0 | **+1** | +2 | +4 |
| Siege of Dragonspear | 1368–1369 (intervalo) | período coincidente | **período coincidente** | após | após |
| BG2: Shadows of Amn | 1369 (início; final controverso) | −1 | **0** | +1 | +3 |
| BG2: Throne of Bhaal | 1369/1370 (disputa) | anterior | **possivelmente coincidente** | possivelmente coincidente | posterior |
| NWN campanha principal | 1372 | −4 | **−3** | −2 | 0 |
| NWN: Shadows of Undrentide | ~1372 | ~−4 | **~−3** | ~−2 | ~0 |
| NWN: Hordes of the Underdark | ~1372 | ~−4 | **~−3** | ~−2 | ~0 |

**Atenção:** NWNForBG declara o enredo da campanha principal de NWN, mas não comprova SoU e HotU; essas expansões entram na matriz de **lore**, não no inventário de áreas já importadas.

## 3. Matriz qualitativa de esforço histórico

Definições: **Baixo** = adaptação temporal localizada; **Médio** = revisar estados e NPCs relevantes; **Alto** = recontextualização ampla de quests/personagens. A avaliação é **preliminar**, por família de conteúdo; nunca equivale a contagem de arquivos.

| Família de conteúdo | 1368 | **1369** | 1370 | 1372 | Racional |
|---|---|---|---|---|---|
| **Cenários BG1/SoD** | Baixo–médio | **Baixo–médio** | Médio | Médio–alto | 1368 contém Iron Crisis/SoD; 1369 exige repercussões, não reconstruir geografia |
| **Cenários BG2/ToB (motor-base)** | Alto | **Baixo–médio** | Médio | Médio–alto | BG2 começa em 1369; scripts da saga precisam isolamento em *todos* os anos |
| **NWNForBG principal** | Alto | **Alto** | Alto | Médio–alto* | 1372 contemporâneo, mas epidemia e plot original exigem estados específicos |
| **IWD1/HoW/ToL** | Alto | **Alto** | Alto | Alto | ~87–91 anos de diferença: preservar arte, não população de 1281 |
| **IWD2** | Alto | **Alto** | Alto | Alto | ~56–60 anos de diferença: preferir mapa plausível com população revisada |
| **Eventos globais e áreas afetadas** | Médio | **Médio** | Médio | Alto | 1371/1372 incluem eventos de grande impacto, especialmente Cormyr/Neverwinter |

\* Em 1372, NWNForBG fica contemporâneo, mas o Living World precisaria reconciliar Wailing Death, progressão da campanha original e alterações de cenário. A classificação **não** implica que o NWNForBG já foi testado no multiplayer ou que não há mudanças na cidade.

### Comparação direta 1369 vs. 1370

| Pergunta | **1369** | 1370 |
|---|---|---|
| Coincide com ano inicial do BG2:EE e manual? | **Sim** | Não |
| Requer projetar BG2 um ano adiante? | **Não** | Sim; desfecho(s) não devem ser presumidos |
| Exige retomar BG1 de 1368? | Sim, +1 ano | Sim, +2 anos |
| Aproxima-se de NWN (1372)? | Diferença de 3 anos | Diferença de 2 anos |
| Resolve o salto temporal de IWD? | Não | Não |
| Evita consequências históricas de 1371–1372 já consumadas? | **Sim** | **Sim** |
| Evita conflito com scripts originais? | **Não** (requer Free Roam/isolamento) | **Não** (requer Free Roam/isolamento) |
| Decisão para **primeiro teste do motor BG2/EET** | **Preferido** | Alternativa de comparação |

### Resultado

**1369 DR** oferece o melhor alinhamento com a base técnica prioritária **BG2:EE** e mantém BG1 apenas um ano atrás, sem exigir antecipar as grandes mudanças canônicas de 1371/1372. **1370 DR** é concorrente próximo — fica um ano mais perto de NWN, porém afasta-se do estado de origem do motor-base e aumenta o número de desfechos de BG2/ToB que precisaríamos resolver.

Esta conclusão é **condicional** à prioridade aprovada de começar pelo BG2:EE + EET e à ausência de contagem real dos arquivos dos mods. Em uma instalação dominada por conteúdo NWNForBG, a preferência poderá mudar após o inventário.

## 4. Exemplos de exceções para um Living World em 1369

| Região/entidade | Situação inicial pretendida | Adaptação mínima proposta | Validação pendente |
|---|---|---|---|
| Baldur's Gate (cidade) | Um ano após a Crise do Ferro (BG1 1368) | Manter ruas/interiores; remover scripts de capítulo; atualizar rumores, facções e destinos de NPCs conforme canon escolhido | Inventário `.ARE/.CRE/.DLG`, história dos personagens |
| Costa da Espada / Dragonspear | SoD ocorreu em 1368–1369, mas fim e cronologia fina incertos | Manter estrada, vilas e fortificações; tratar cruzada/ocupação segundo **data e desfecho validados**, não presumir evento completo em janeiro | Cronologia SoD; datas precisas de canon |
| Athkatla / Amn | BG2 se inicia em 1369 | Manter cenário, comerciantes e população plausível; **isolar** quests da história de Irenicus/filho de Bhaal | Lista de quests/flags/atores + política DEC-024 |
| Cormyr | Azoun IV vivo em 1369; atentado Abraxus Affair no ano | Não introduzir regência de Alusair (1371) como fato consumado | Fonte do atentado, mapa realmente importado |
| Neverwinter | 3 anos antes da campanha de NWN e Wailing Death | Reutilizar geometria plausível do mod; **não** ativar peste/quests de 1372 | Quais áreas/NPCs NWNForBG instala |
| Kuldahar / Icewind Dale | Décadas depois de 1281 e 1312 | Preservar arte/terreno onde plausível; NPCs históricos não são recriados automaticamente; preferir estados de época mais recente quando comparáveis | Inventário de mapas duplicados, história de cada local |
| Underdark / Lolth | Antes do Silêncio de Lolth (1372–1373) | Não aplicar Silêncio antes do calendário devido | Fonte histórica, facções e scripts |

**Correção de método:** um cenário 2D relativamente estável pode ser reaproveitado em um ano distante, mas um NPC humano, enredo fechado ou cidade reconstruída não pode. **A distância entre anos não é um multiplicador uniforme de esforço.**

## 5. Método para converter estimativa em medição no build real

A matriz v1.4 é uma **triagem documental**. Depois de instalar a primeira combinação funcional, registrar para cada recurso (não apenas por jogo):

| Campo candidato | Descrição |
|---|---|
| `build_id` / `mod_versions` | Proveniência do recurso, ordem e hash de instalação |
| `resource_id` / `resource_kind` | Identificador original e tipo: ARE/WED/TIS, CRE, DLG, BCS, item, worldmap etc. |
| `source_title` / `source_year_dr` | Obra e período de origem, com precisão e proveniência |
| `region_id` / `entity_id` | Região e identidade lógica estável |
| `visual_reuse` | `AS_IS`, `DECOR_UPDATE`, `MAJOR_REWORK`, `NOT_IMPORTED` |
| `npc_state` | `REUSE`, `RETIME`, `REPLACE`, `DISABLE`, `NOT_APPLICABLE` |
| `quest_script_state` | `ISOLATED`, `MIGRATED`, `REMOVED`, `UNKNOWN` |
| `historical_conflicts` | Lista de IDs de eventos e fatos afetados no ano-alvo |
| `effort_level` | `0` sem adaptação, `1` configuração, `2` script/NPC, `3` arte/quest importante, `4` inviável sem reconstrução, **estimativa revisada manualmente** |
| `verification` | `UNVERIFIED`, `RESOURCE_PRESENT`, `SINGLEPLAYER_TESTED`, `MULTIPLAYER_VERIFIED` |

Após inventariar, comparar candidatos com um somatório baseado em recursos **realmente presentes**, por exemplo, `Σ esforço_de_revisão_do_recurso` com pesos definidos pela importância/uso real; guardar subtotais de lore, scripts, geometria e compatibilidade. **Não publicar percentuais de compatibilidade ou 'economia de X horas' sem contagens e testes reais.**

## 6. Gates candidatos

- `GATE-TIME-001`: comparar export real de pelo menos uma região BG1, uma BG2, uma IWD e uma NWNForBG quando presentes, com identificadores verificáveis.
- `GATE-TIME-002`: 1369 não ativa eventos posteriores (1371 Cormyr, 1372 NWN) sem divergência/simulação apropriada.
- `GATE-TIME-003`: SoD/ToB sem dia oficial confirmado não recebem dia fabricado.
- `GATE-TIME-004`: áreas BG2 reutilizadas sem ativação automática de trama de Irenicus; salvar/carregar preserva Free Roam.
- `GATE-TIME-005`: NPC de IWD1 só aparece vivo após validação de identidade/idade.
- `GATE-TIME-006`: mudança de `start_year_dr` **na criação de outra campanha** não modifica estados existentes, e permanece possível escolher outros anos habilitados.
- `GATE-TIME-007`: recursos não importados ou não verificados não contam como cobertura efetiva.

## 7. Próxima pergunta arquitetural

**DEC-024 — Snapshot inicial do Living World:** em 1369 DR, o que já é história concluída (BG1/SoD), o que ainda está em curso (BG2) e como os recursos antigos recebem estados válidos sem assumir que os personagens dos jogadores são protagonistas das histórias originais?

## Fontes auditáveis

1. https://www.dosdays.co.uk/media/games/baldur/BG2_Manual.pdf (BG2 original, p. 64: 1369 DR).
2. https://github.com/gibberlings3/iesdp/blob/master/files/2da/2da_bgee/years.htm (`STARTYEAR 1369`).
3. https://github.com/Gibberlings3/EET (EET e integração BG1/2).
4. https://files.beamdog.com/files/SoD-FieldReport_en.pdf (SoD: ano 1368 nos relatórios/linha cronológica do jogo).
5. https://github.com/abalabokhin/NWNForBG (NWNForBG: escopo da adaptação e compatibilidade declarada).
6. https://forgottenrealms.fandom.com/wiki/List_of_video_games_in_chronological_order (cronologia secundária, não fonte primária).
7. https://forgottenrealms.fandom.com/wiki/History_of_Cormyr_%28timeline%29 (eventos 1369/1371, índice secundário).
8. https://forums.beamdog.com/discussion/65246/timeline-of-the-bg-iwd-nwns-and-planescape-games (linha do tempo comunitária).
9. https://forgottenrealms.fandom.com/wiki/1369_DR (notas sobre conflitos de data BG2/ToB).

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Snapshots e revisões de operação devem usar identificadores estáveis e lineage temporal; versões antigas não autorizam despacho novo após mudança material.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

A matriz condicional proposta DEC-096 respeita 1369 DR como baseline de testes sem fixar a campanha em 1369; YEAR_ONLY não significa primeiro dia/mês e efeitos de 1370 não surgem em 1369.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.
