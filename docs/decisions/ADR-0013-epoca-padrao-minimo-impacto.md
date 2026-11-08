# ADR-0013 — Época configurável e ano-base de testes por menor impacto

- **Decisão:** DEC-023
- **Estado:** **APROVADA — opção C com adendo de avaliação de custo histórico**
- **Data:** 2026-11-06
- **Referências:** DEC-003/ADR-0006; DEC-004/ADR-0002; DEC-008/ADR-0011; DEC-009/ADR-0012; DEC-011/ADR-0007; DEC-022/ADR-0010.
- **Fase:** Discovery; não é uma SPEC implementada nem validação de mods.

## Contexto e propósito

O objetivo não é escolher a época que possui mais episódios famosos, mas **aquela que exige menos ajustes para aproveitar a maior quantidade de recursos efetivamente disponíveis na instalação base BG2:EE/EET e nas expansões candidatas**. O usuário destacou 1369/1370 DR em vez de fixar 1372 e quer campanhas posteriores com época configurável.

## Decisão aprovada

1. **Opção C:** época inicial configurável por campanha, sujeita a períodos com conteúdo e cronologia efetivamente validados. Nenhuma campanha altera a linha temporal de outra.
2. **1369 DR é a referência inicial aprovada para testes do Living World**, por coincidir com `STARTYEAR 1369` em BG2:EE e o ano explicitamente declarado no manual de BG2. É uma **seleção de engenharia preliminar baseada no melhor conjunto de evidências disponível**, não uma prova de ótimo global por contagem de áreas/NPCs; confirmar após inventário real de recursos e regressões.
3. **1370 DR é alternativa de comparação**, mas não foi escolhido como default: a suposta conclusão de todos os episódios BG2/ToB no início desse ano não está confirmada de forma inequívoca, e seria necessário selecionar um estado pós-campanha. O ano 1369 evita um salto desnecessário do BG2; ambos antecedem grandes alterações regionais de 1371/1372.
4. **Data granular inicial (dia/mês) ainda não aprovada.** O BG2:EE contém um `STARTTIME` documentado e deveremos ler a data real do host; não atribuir arbitrariamente um dia a eventos identificados somente pelo ano.
5. **Reutilizar mapas não significa importar scripts/quests/NPCs sem triagem.** O Living World mantém seu estado separado do modo Original; campanhas pré-programadas serão desativadas, isoladas ou adaptadas por recurso, não reproduzidas automaticamente para os novos protagonistas.
6. **Peso maior para recursos comprovadamente disponíveis e utilizáveis no BG2:EE/EET**. A integração de IWD1/IWD2 e NWNForBG permanece sujeita a teste; a distância cronológica importa menos para arte/terreno que para NPCs, narrativas, governos, serviços e eventos.
7. **IWD1 e IWD2 permanecem décadas distantes em qualquer opção 1368–1372.** Primeiro priorizar arte/cenários plausíveis e encontros genéricos, depois recriar populações e missões conforme ano escolhido. Não conservar automaticamente pessoas mortas ou questlines da época.
8. **Não presumir compatibilidade de mods e recursos ainda não testados.** Usar manifestos de builds e validações da DEC-003, especialmente integração multiplayer de EEex/bridge.
9. **Reavaliação por evidência**: após extrair o inventário real de recursos, aplicar o método de pontuação de esforço descrito em `docs/16-avaliacao-do-ano-base-por-minimo-impacto.md`. Se os dados divergirem substancialmente, abrir nova revisão de ADR, sem trocar o default silenciosamente.
10. **Canon com divergências controladas** (DEC-009) e efeitos mecânicos confirmados pelo host (DEC-011) continuam obrigatórios.

## Comparação e justificativa sumária

| Ano candidato | BG1 / SoD | BG2/ToB | NWNForBG | IWD1/2 | Julgamento provisório |
|---|---|---|---|---|---|
| 1368 | BG1 contemporâneo, SoD em andamento | BG2 ainda futuro | NWN futuro (4 anos) | Muito antigos | Bom para BG1, ruim para motor/quest-state BG2 |
| **1369** | BG1 1 ano antes; SoD entre 1368–1369 | **BG2 contemporâneo e motor alinhado** | NWN futuro (3 anos) | Muito antigos | **Menor esforço esperado no núcleo prioritário BG/EET; referência de testes** |
| 1370 | BG1 2 anos antes | BG2 1 ano antes; ToB incerto | NWN futuro (2 anos) | Muito antigos | Próximo concorrente; exige desfechos BG2 mais definidos |
| 1372 | BG1 4 anos antes | BG2 3 anos antes | NWN contemporâneo | Muito antigos | Melhor para NWN, mas mais repercussões acumuladas para BG e Cormyr |

Datas de IWD: 1281 e 1312 DR; BG1: 1368; BG2: 1369; NWN: 1372. SoD e ToB têm graus de precisão temporal distintos. Veja a matriz completa e sua política de fontes em `docs/13-*`, `docs/14-*`, `docs/15-*` e `docs/16-*`.

## Consequências para as futuras SPECS

- O criador de campanha terá campo `start_year_dr` (padrão inicial de **teste: 1369**), preservando a possibilidade de `start_date` quando fonte/dia forem conhecidos.
- O catálogo de recursos deve separar `visual_asset`, `map_geometry`, `spawn`, `npc_identity`, `quest_script`, `worldstate` e `canonical_event`.
- Metadados de ano de origem e compatibilidade temporal devem ser armazenados, com custo de adaptação por recurso; estados não conhecidos ficam **não verificados**, não implicitamente compatíveis.
- Baseline de testes de 1369 deve demonstrar pelo menos um mapa BG1 e um mapa BG2 revisados, sem flags de campanha herdadas, um NPC com memória e um evento oficial condicionado a calendário.
- A criação em 1368/1370/1372 é objetivo de design, não promessa de cobertura equivalente no MVP.

## Critérios de aceite candidatos (a transformar em SPEC)

1. A base BG2:EE informa 1369 DR e o save inicial do Living World segue uma política de data definida, sem dia inventado.
2. Jogo com época 1369 não dispara automaticamente a Wailing Death (1372), a morte de Azoun IV (1371), nem a conclusão desconhecida de ToB.
3. Um mapa BG1 de 1368 é carregado em 1369 com flags e personagens tratados pela política Living World, sem imposição de protagonista Bhaalspawn.
4. NPC humano de IWD1 1281 não é importado vivo em 1369 sem validação explícita de idade/estado.
5. Nunca assumir que SoU/HotU estão presentes em NWNForBG sem detecção de recursos reais.
6. A mesma campanha configurada para 1372 deve aplicar apenas eventos oficiais anteriores/atuais verificados, sem editar saves de 1369 ou Original.
7. A comparação de esforço deve registrar inventário real e fontes por build, separando custo cronológico de instalação/compatibilidade.

## Fonte / evidências iniciais

- **BG2 Manual, p. 64 (fonte original do jogo):** https://www.dosdays.co.uk/media/games/baldur/BG2_Manual.pdf — 1369 como ano corrente.
- **IESDP (formato YEARS.2DA de BG2:EE):** https://github.com/gibberlings3/iesdp/blob/master/files/2da/2da_bgee/years.htm — `STARTYEAR 1369`.
- **EET, projeto:** https://github.com/Gibberlings3/EET — motor BG2:EE como base, integração das campanhas BG.
- **Siege of Dragonspear Field Report, Beamdog:** https://files.beamdog.com/files/SoD-FieldReport_en.pdf — referências a 1368, datas de relatórios e Crise do Ferro; ainda requer triagem de dia/etapa.
- **NWNForBG, mantenedor:** https://github.com/abalabokhin/NWNForBG — adaptação da campanha principal de NWN; existência da área não equivale à contemporaneidade do enredo.
- **IWD1/IWD2 e NWN, cronologias secundárias:** https://forgottenrealms.fandom.com/wiki/List_of_video_games_in_chronological_order e https://forums.beamdog.com/discussion/65246/timeline-of-the-bg-iwd-nwns-and-planescape-games
- **Cormyr 1371, fonte secundária a cotejar com obras primárias:** https://forgottenrealms.fandom.com/wiki/History_of_Cormyr_%28timeline%29
- **Divergências BG2/ToB:** https://forgottenrealms.fandom.com/wiki/1369_DR e https://forums.larian.com/ubbthreads.php?Number=653392&ubb=showflat

## Questão subsequente

**DEC-024 — Estado narrativo inicial do Living World em 1369 DR:** quais eventos da saga BG1/SoD considerar realizados, quais estados de BG2/ToB manter em aberto e quais scripts/quests de campanha isolar? A discussão vem antes de determinar uma data exata de início e do inventário de NPCs.
