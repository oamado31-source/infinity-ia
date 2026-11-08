# Matriz cronológica — jogos, expansões e conteúdo reaproveitável

**Versão:** Discovery v1.4, levantamento atualizado em 2026-11-06. **Status:** matriz de pesquisa, sujeita a validação em fontes primárias e nos mods; não é SPEC aprovada.  
**Legenda:** DR = Dalereckoning; `F` = data sustentada por jogo/manual ou fontes secundárias convergentes; `P` = provável / intervalo aproximado; `D` = disputa entre referências; `?` = não verificado. O rótulo não certifica que os arquivos do jogo foram importados, instalados ou testados.

## Decisão de época para testes (DEC-023, aprovada)

**1369 DR** é o ano inicial **dos testes**; **o ano será configurável por campanha** (opção C). A escolha é provisoriamente a de menor impacto **para o núcleo prioritário BG2:EE/EET**, pois o motor BG2:EE inicia em 1369 e BG1 está a apenas um ano. **1370 é alternativa próxima**. O inventário real de mapas/NPCs e scripts ainda será necessário para confirmar o mínimo efetivo.

A coluna histórica de 1372 abaixo foi mantida como **cenário comparativo anterior**, não como recomendação de ano inicial. A análise de custo por 1368/1369/1370/1372, com matriz por conteúdo e distinção entre arte e scripts, está em [`16-avaliacao-do-ano-base-por-minimo-impacto.md`](16-avaliacao-do-ano-base-por-minimo-impacto.md). Documento decisório: [`ADR-0013`](decisions/ADR-0013-epoca-padrao-minimo-impacto.md).

## Matriz de períodos e expansões

| ID | Obra / conteúdo | Época narrativa (DR) | Precisão/confiança | Relação com o motor BG2/EET | Exemplo comparativo: ajustes em 1372 DR (não baseline atual) |
|---|---|---|---|---|---|
| G-IWD1 | **Icewind Dale (original/EE)** | **1281** | F — ano convergente | `IWD1_EET` existe; compatibilidade multiplayer/EEex pendente | **91 anos** depois: revisar população, idade/morte de NPCs, facções, consequências da crise de Belhifet e infraestrutura; manter arte quando plausível |
| G-IWD1-HOW | **Heart of Winter** | **1281** | F — ano informado por índice especializado | Conteúdo declarado no `IWD1_EET`; há `HoW_EET` distinto; validar build | Verificar personagens do Vale e consequências da aventura antes de situá-los em 1372 |
| G-IWD1-TOL | **Trials of the Luremaster** | **c.1281** | P — ligado à campanha IWD1/HoW; dia/ano exato do módulo não confirmado independentemente | Declarado incluído no `IWD1_EET`; testar disponibilidade | Recursos de masmorra podem servir como cenário atemporal; personagens/eventos requerem triagem |
| G-IWD2 | **Icewind Dale II** | **1312** | F — ano registrado em compêndios do jogo | `IWD2_EET` existe (beta); compatibilidade pendente | **60 anos** depois: atualizar Targos, Kuldahar, Legion of the Chimera, pessoas e edificações |
| G-BG1 | **Baldur's Gate I / BG:EE** | **1368** | F — cronologias convergentes | Base de EET | Quatro anos depois: revisar consequências da Iron Crisis, Iron Throne, personagens principais e flags de quest |
| G-BG1-TOTSC | **Tales of the Sword Coast** | **1368 (relativo ao BG1)** | P — expansão contemporânea, sem dia fixo universal | Base de EET | Tratar conteúdo como aventura anterior; rever quem ainda vive e que locais foram alterados |
| G-BG-SOD | **Siege of Dragonspear** | **1368–1369** | P — intervalo frequente em cronologias detalhadas | EET suporta SoD conforme dependências do BG:EE/SoD | Não assumir que o exército/crise estão presentes em 1372; avaliar consequências e personagens sobreviventes |
| G-BG2-SOA | **Shadows of Amn** | **1369**, possivelmente avançando até 1370 | F para 1369 (**manual do próprio jogo**), D para data final | BG2:EE é motor-base | Em 1372 revisar quests do enredo, Irenicus, guildas e personagens; não reutilizar flags de campanha como se o protagonista atual fosse o Bhaalspawn |
| G-BG2-TOB | **Throne of Bhaal** | **1369/1370** | D — referência de ano 1369 em cronologias resumidas, interpretação de 1370 em reconstruções de fãs | Conteúdo de BG2:EE/EET | Tratar resultados da saga Bhaalspawn com versão de lore e decisões explícitas; não inventar data para ativação automática |
| G-BG-BP1 | **The Black Pits** | **c.1368** | P — campanha separada, canon controverso | Conteúdo extra BG:EE/EET | Espaços/itens reutilizáveis; roteiro e NPCs sujeitos a flag de canon |
| G-BG-BP2 | **The Black Pits II: Gladiators of Thay** | **c.1369** | P — fontes comunitárias | Conteúdo extra BG2:EE/EET | Mesmas ressalvas; não fundir enredos automaticamente com a trama principal |
| G-NWN-OC | **Neverwinter Nights — campanha original** | **1372** | F — guia da campanha + cronologias | `NWNForBG` documenta a adaptação do **enredo original**; verificar conteúdo instalado | A epidemia Wailing Death e sua recuperação afetam diretamente a cidade |
| G-NWN-SOU | **Shadows of Undrentide** | **1372** | F — convergência de cronologias; granularidade de meses incerta | **Não assumir** que NWNForBG importa esta expansão; buscar adaptação específica | Personagens e acontecimentos próprios; protagonista de SoU tem continuidade com HotU, não necessariamente OC |
| G-NWN-HOTU | **Hordes of the Underdark** | **1372**, possível margem cronológica | P — atribuída a 1372, sem data granular segura | **Não assumir** que NWNForBG importa esta expansão; buscar adaptação específica | Relevância de Underdark, Waterdeep e Silêncio de Lolth; testar fatos sem confundir enredo de SoU com OC |
| G-NWN-PREM | **Módulos premium oficiais/adicionais NWN** (e.g. Pirates of the Sword Coast, Wyvern Crown of Cormyr, Darkness over Daggerford, Tyrants of the Moonsea) | **c.1372–1373 ou não definida** | Misto: precisa ser apurado por módulo | Nenhuma importação presumida em NWNForBG | Catalogar **cada módulo separadamente**, com seu ano, tipo, local, recursos e licença |
| G-NWN2 | **Neverwinter Nights 2 e suas expansões** (fora do pacote inicial) | **a partir de c.1374** | Pesquisa futura | **Não** integra automaticamente NWNForBG ou EET | Apenas radar de futuro; motor e recursos diferentes |

**Nota de escopo:** IWD2 não possui expansão comercial equivalente a Heart of Winter; NWN1 tem duas expansões narrativas principais (SoU e HotU). Módulos premium não são automaticamente a mesma coisa que expansões e devem ter inventário próprio. As possíveis expansões posteriores do acervo não significam integração técnica confirmada.

## Matriz cruzada resumida — períodos e continuidade de regiões

| Região/referência | 1281 DR (IWD1) | 1312 DR (IWD2) | 1368–1370 DR (BG) | 1371 DR | 1372–1373 DR (NWN) |
|---|---|---|---|---|---|
| Icewind Dale / Ten-Towns | Aventura de Belhifet; locais e NPCs de IWD1 | Conflito da Legion of the Chimera; IWD2 | Região existe, mas pessoas/locais requerem atualização | Intervalo histórico a curar | Paisagem reutilizável após revisão; população e economia não são cópia de 1281 |
| Costa da Espada / Baldur's Gate | Fora do período dos jogos BG | Fora do período dos jogos BG | Crise do ferro, saga Bhaalspawn e desdobramentos | Acontecimentos de FR entre campanhas | Quatro anos mais tarde que BG1, revisar quest flags, facções e rumos dos NPCs |
| Amn / Athkatla | Fora do BG2 | Fora do BG2 | Eventos de Shadows of Amn e ToB | Desdobramentos a curar | Cenário BG2 reutilizável com mudanças específicas |
| Cormyr / Suzail | História anterior | História anterior | Azoun IV vive; 1369 atentado atribuído a Abraxus Affair | **Azoun IV e Tanalasta morrem; Alusair assume regência** | Reino pós-guerra, Azoun V menor, notícias e estabilidade impactadas |
| Neverwinter / Luskan | Cenários em épocas históricas anteriores | Antes de NWN1 | Cidade existente antes de Wailing Death | Contexto de pré-epidemia | **1372 Wailing Death**; módulos em data própria; verificar recuperações |
| Underdark / culto de Lolth | Cultos anteriores | Cultos anteriores | Cultos antes do Silêncio | Antes do Silêncio | **1372–1373: Silêncio de Lolth**, impacto religioso/político |

## Classes de reaproveitamento (decisão de design)

- `ART_REUSE`: cenário/arte pode ser reutilizado após verificar compatibilidade gráfica; não herda história.
- `STATIC_GEO`: topografia/localidade sem alteração relevante conhecida; pode receber outros NPCs.
- `CONDITIONAL_STATE`: arquitetura/objetos/serviços dependem do ano (ex.: cidade sob peste ou pós-cerco).
- `ENTITY_REVIEW`: NPC exige checagem de identidade, longevidade, cargos, paradeiro, morte, facção e proveniência.
- `QUEST_ARCHIVE`: missão da campanha original é memória histórica ou conteúdo isolado, **não** missão ativa por padrão.
- `OUT_OF_TIME`: assets transportáveis apenas após recriação narrativa específica ou como ruína/instância/flashback.
- `NOT_IMPORTED`: conteúdo existe no jogo original mas ainda não é comprovadamente adaptado ao BG2:EET.

## Verificações obrigatórias antes de promover uma linha a SPEC

1. Fonte primária ou documentação interna de jogo para data (evidência com edição/página/capítulo); sinalizar divergências.
2. Revisar entidades e locais do período de origem versus data selecionada para a campanha.
3. Verificar se o mod instala **aquele módulo/área** e quais ids/flags são criados.
4. Verificar transições, colisões, diálogos, scripts, saves e multiplayer após integração.
5. Marcar estado: `CANDIDATE` → `LORE_REVIEWED` → `ASSET_AVAILABLE` → `BUILD_TESTED` → `MULTIPLAYER_VERIFIED`.

## Fontes de referência iniciais

- Manual original BG2 (documento do próprio jogo): https://www.dosdays.co.uk/media/games/baldur/BG2_Manual.pdf — p. 64 situa a época em 1369 DR.
- Cronologia por jogo, wiki comunitária: https://forgottenrealms.fandom.com/wiki/List_of_video_games_in_chronological_order
- Linha cronológica comunitária de jogos: https://forums.beamdog.com/discussion/65246/timeline-of-the-bg-iwd-nwns-and-planescape-games
- Heart of Winter: https://forgottenrealms.fandom.com/wiki/Icewind_Dale%3A_Heart_of_Winter
- IWD2: https://forgottenrealms.fandom.com/wiki/Icewind_Dale_II
- Documentação de mods: https://github.com/The-Gate-Project/IWD1_EET ; https://github.com/The-Gate-Project/IWD2_EET ; https://github.com/abalabokhin/NWNForBG

**Limitação atual:** são referências iniciais, não corpus oficial completo. Não foram examinadas as instalações locais nem todos os livros de fonte primária; a data exata de cada expansão/módulo não deve ser inventada.

## Complemento DEC-060 — referência a partições anuais (v5.6.1)

Cada evento, personagem, organização ou recurso temporal da matriz deve apontar para sua **partição de ano DR**, fonte e intervalo de validade. Importações de jogos/expansões de outras épocas não entram automaticamente no diretório primário de 1369 DR como se fossem contemporâneas. Se uma entidade for relevante em vários anos, resolver sua versão vigente via referências/validade, sem duplicação descontrolada. Os diretórios em `knowledge/periods/` são andaimes vazios e não atestam que os respectivos jogos ou conteúdos tenham sido importados.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: conexões entre cidades e duração de viagens dependem de fontes do ano DR e do build; regiões de Forgotten Realms não são necessariamente áreas jogáveis, portanto sem percurso mecânico presumido.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Planos em andamento devem distinguir eventos confirmados de hipóteses narrativas; novos incidentes não assumem resultados para justificar trocar destino.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Proposta DEC-096: manter essa matriz como **fontes e compatibilidade de obras**, não como executor de eventos. Adicionar para cada evento precisão temporal (inclusive YEAR_ONLY), geografia, fonte e fase; produzir ruleset separado, nunca tratar data provável como mês/dia exatos.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-097/C — Discovery v9.3

Uma linha de evento elegível DEC-096 não altera diretamente variáveis; DEC-097/C agrega somente regras com escopo/tempo/fontes e política tipada.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Ao mapear conteúdos por build, diferenciar origem de CRE/asset e titularidade da instância que existe no host.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração DEC-102/C (Discovery v9.8)

A DEC-102/C trata divergências entre milestone validado do host e projeção derivada do Living World: exigir mapeamento DEC-101, observação DEC-100, epoch/branch e receipts, e preservar o host, facts ledger e conhecimento dos NPCs. Somente proposta de revisão CAS/autorizada; detalhes em ADR-0097/doc. 102. **Sem POC mecânica.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para cronologia oficial versus conhecimento efetivo de cada personagem, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para proveniência histórica versus percepção dos NPCs, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.
