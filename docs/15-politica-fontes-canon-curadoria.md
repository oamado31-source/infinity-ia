# Política de fontes, canon, precisão temporal e curadoria — pré-SPEC

**Discovery v1.3.** Política candidata operacionalizando DEC-008 + DEC-009; a política fina de precedência entre versões conflitantes ainda depende de decisão específica. Diretriz já aprovada: canon principal com divergência causal registrada.

## Princípios

- A **obra da WotC/TSR**, o conteúdo real dos jogos licenciados e dados oficiais são referências distintas; nenhum agregador de fãs equivale automaticamente a publicação original.
- A Forgotten Realms Wiki reconhece que não existe regra oficial universal simples para hierarquizar todo canon e propõe **uma política própria da wiki**. Nossa política pode usá-la como heurística, não como determinação legal ou editorial definitiva.
- Para **jogabilidade pessoal**, respeitar coerência acima de perfeição bibliográfica, mas deixar claro o grau de certeza; toda exceção importante deve ser verificável.
- Não atribuir a fontes oficiais datas extraídas exclusivamente de fóruns, wikis ou inferências. Primeiro registrar a hipótese; depois promover após conferir obra base com página/capítulo.
- Preservar metadados de proveniência e **resumos próprios**, evitando incorporar trechos extensos de textos protegidos em artefatos redistribuídos.
- Importação de **assets** é distinta de compatibilidade do **enredo**: NWNForBG documenta o jogo original, sem prometer SoU/HotU; IWD1_EET e IWD2_EET ainda são beta.

## Classes de fonte propostas

| Grau | Referência | Uso autorizado na Discovery |
|---|---|---|
| `S0_PRIMARY` | Livro/suplemento oficial, manual de jogo, texto interno verificado, documentação original | Fixar fatos específicos quando a obra e a seção forem identificadas |
| `S1_LICENSED` | Outro conteúdo oficial/licenciado com enredo potencialmente divergente | Fonte válida sobre o seu próprio enredo; conflitos com outros meios precisam revisão |
| `S2_INDEXED` | Wiki referenciada, cronologia com bibliografia, catálogo de jogo | Descobrir hipóteses, âncoras de data, fonte a conferir |
| `S3_COMMUNITY` | Discussão de fórum, modder, dedução cronológica | Apenas hipótese/prioridade de pesquisa; não fixar cronologia rígida |

## Estados e precisão obrigatórios

- `verification_status`: `RESEARCH_ONLY | CROSS_REFERENCED | SOURCE_CHECKED | DISPUTED | CAMPAIGN_CANON`.
- `date_precision`: `EXACT_DAY | MONTH_ONLY | YEAR_ONLY | RANGE | APPROX | UNKNOWN`.
- `canon_event_status`: `UPCOMING | DUE | ACTIVE | CONCLUDED | DIVERGED | SUPPRESSED_BY_BRANCH | SOURCE_CONFLICT`.
- `content_status`: `KNOWN_GAME_CONTENT | MOD_CLAIMED | ASSET_INSPECTED | INSTALL_TESTED | MP_TESTED | NOT_IMPORTED`.
- O estado `CAMPAIGN_CANON` significa válido **nesta campanha**, não alteração de cânone oficial publicado.

## Proposta de modelo de dados

```text
SourceReference(id, source_class, title, creator, publisher, edition,
                volume, page_or_chapter, source_uri, access_date, license_note)
ContentModule(id, game_id, content_type, origin_year_start, origin_year_end,
              year_precision, sources[], adaptation_id, integration_status)
LoreEvent(id, title, period_start_DR, period_end_DR, date_precision,
          location_ids[], actor_ids[], source_refs[], verification_status,
          variant_group_id, effects_template_version)
HistoricalEntity(id, identity_key, lineage, race, birth_range_DR,
                 death_range_DR, current_office, location,
                 timeline_validity, sources[], identity_confidence)
RegionVersion(region_id, epoch_start_DR, epoch_end_DR, geometry_ref,
              visual_variant, factions[], authority[], source_refs[])
CampaignBranch(campaign_id, branch_id, parent_event_id,
               evidence_receipt_ids[], divergence_reason, created_world_time)
CampaignLoreOverride(campaign_id, event_id, branch_id, override_type,
                     approval_record, supersedes_event_id)
NewsPropagation(event_id, origin_region, recipient_actor, channel,
                departure_DR, arrival_DR, knowledge_status)
```

IDs de uma instalação EET/NWNForBG não são IDs universais; exigiremos tabela de correspondência por versão de mod/build antes de instanciar entidades. A persistência narrativa deve ser independente dos saves Original.

## Procedimento SDD da curadoria histórica

1. Identificar jogo/expansão/área/NPC e data presumida, com fonte ligada.
2. Pesquisar datas oficiais e eventos regionais que caiam entre a origem do asset e a data da campanha.
3. Marcar alterações por categoria: sobrevivência, idade, governo, facção, religião, função, estrutura física, população, quests.
4. Separar **diferença comprovada** de **hipótese de ambientação**.
5. Resolver pela menor adaptação suficiente: manter arte/geografia, substituir NPCs ou diálogos específicos quando necessário.
6. Criar regras verificáveis de repercussão e de propagação de informação; testes não dependem de LLM.
7. Garantir que o evento histórico está confirmado para **essa campanha** e que não existe ramo causal conflitante.
8. Só então permitir propostas de efeitos mecânicos mediante autorização do host e registro idempotente.

## Fontes consultadas como ponto de partida (2026-11-06)

**Primária verificada:**
- BioWare/Black Isle, *Baldur's Gate II: Shadows of Amn — Game Manual*, seção *Time in the Realms*, p.64: 1369 DR como ano atual. Cópia acessível: https://www.dosdays.co.uk/media/games/baldur/BG2_Manual.pdf (verificação visual de p.64 feita na pesquisa).

**Secundárias e índices (pendente conferir livros/trechos originais):**
- Forgotten Realms Wiki, lista cronológica dos jogos: https://forgottenrealms.fandom.com/wiki/List_of_video_games_in_chronological_order
- Forgotten Realms Wiki, política editorial sobre canon (não é política oficial WotC): https://forgottenrealms.fandom.com/wiki/Forgotten_Realms_Wiki:Canon
- História de Cormyr: https://forgottenrealms.fandom.com/wiki/History_of_Cormyr_(timeline)
- 1372 DR: https://forgottenrealms.fandom.com/wiki/1372_DR
- Silêncio de Lolth: https://forgottenrealms.fandom.com/wiki/Silence_of_Lolth
- IWD2: https://forgottenrealms.fandom.com/wiki/Icewind_Dale_II
- NWN campanha original: https://nwn.fandom.com/wiki/Original_campaign
- Cronologia de comunidade: https://forums.beamdog.com/discussion/65246/timeline-of-the-bg-iwd-nwns-and-planescape-games
- Pesquisa cronológica detalhada de fã (apenas inferência especialmente para ToB): https://forums.larian.com/ubbthreads.php?Number=814548&ubb=showflat

**Documentação de mods (prova apenas do escopo declarado pelo autor, não de testes nossos):**
- IWD1 EET + expansões: https://github.com/The-Gate-Project/IWD1_EET
- IWD2 EET: https://github.com/The-Gate-Project/IWD2_EET
- NWNForBG: https://github.com/abalabokhin/NWNForBG

**Obras primárias candidatas para consulta posterior:**
- *The Grand History of the Realms* (Wizards of the Coast, 2007): **não foi consultada integralmente nesta rodada**.
- *Cormyr: A Novel* e *Death of the Dragon* (para sucessão em Cormyr).
- *Forgotten Realms Campaign Setting* (3ª edição, marco 1372 DR), aventuras e materiais oficiais relacionados aos eventos.
- Livros da saga *War of the Spider Queen* (verificar intervalo do Silêncio de Lolth).
- Textos internos dos jogos/expansões para datar missões e desfechos com precisão.

## Tarefas de pesquisa antes da SPEC de canon

- Fixar corte de data inicial DEC-023 ou oferecer política configurável com intervalos autorizados.
- Localizar fonte primária para ano exato de Trials of Luremaster, limites cronológicos de SoD/ToB e módulos premium NWN.
- Identificar para cada NPC crítico `alive_at_start`, `role_at_start`, `faction_at_start`, `location_at_start` e `knows_event_ids`.
- Definir precedência de fontes **para a campanha do usuário**, sem apagar divergências documentadas.
- Efetuar POCs com BG2:EET + mods antes de prometer NPCs, diálogos, transições e estado cronológico dentro do jogo.

## Emenda DEC-060 — proveniência nas partições anuais (v5.6.1)

A curadoria oficial/hipotética passa a ser organizada **fisicamente por ano DR** em `knowledge/periods/{year}-DR/`, com categorias `chronology`, `events`, `organizations`, `guilds`, `characters`, `regions`. A localização de um registro **não prova a data exata de ocorrência** nem seu valor canônico: fonte, precisão, intervalo de validade, status e ramo continuam obrigatórios. O conteúdo futuro não é recuperado como fato conhecido de um NPC de período anterior; história pregressa exige busca delimitada e autorização. Conflitos entre duas fontes **do mesmo período** ainda dependem da **DEC-061**, que segue aberta. Não presumir prioridade universal entre edições ou romances; o layout de diretórios não resolve contradições editoriais.

## Integração DEC-062/C — ingestão sem republicar obras protegidas

A política de classes de fonte permanece uma **heurística de pesquisa** e não dá licença de ingestão, distribuição nem prevalência automática entre versões. A DEC-062/C (ADR-0057; doc. 62) requer fonte legitimamente acessada, registro de direitos/escopo, quarantena, `Source/Claim` por trecho, validação determinística, classificação por IA apenas como proposta e curadoria auditada antes de publicar. Novos fatos canônicos exigem revisão humana inicial; futura allowlist automática somente LOW e versionada, com SPECS/POCs.

**DEC-060 continua exigindo diretórios físicos por ano DR** e **DEC-061 continua exigindo preservar conflitos e proveniência**. O índice de busca não pode recuperar material de todas as épocas e filtrar somente depois do prompt. Sem incorporar livros ou assets ao Discovery.

## Integração DEC-063/C — curadoria publicada não impõe retcon a campanha (v5.9)

A proveniência DEC-061 e a ingestão curada DEC-062 continuam produzindo revisões anuais **independentes**. Uma revisão no catálogo não substitui automaticamente o pack já escolhido pela campanha. Diferenças entre versões precisam manter claims e resoluções curatoriais rastreáveis; conflito `UNRESOLVED` não se torna fato por migração. Atualizações por campanha são pinadas, avaliadas e autorizadas conforme ADR-0058; passado confirmado permanece no overlay do respectivo ramo.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: grafo de rotas tem proveniência por ano DR e adota revisão de Knowledge Pack curada; fontes conflitantes permanecem explícitas. Rotas privadas da campanha ficam fora do corpus canônico.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

O corpus histórico canônico continua fisicamente separado por ano DR (DEC-060): identidades secretas e pseudônimos gerados por uma campanha jamais alteram os arquivos de cânone; declarações editoriais têm sua fonte DEC-061, e descobertas privadas ficam no overlay.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Proveniência de depoimentos de campanha não equivale a material canônico; fontes editoriais continuam curadas por ano DR e segredos não são publicados na base.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Fontes sobre lugares históricos ficam no corpus anual; informações de rota/refúgio criadas durante a campanha têm proveniência e ACL no overlay privado.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

PlantedClaim não constitui nova fonte curada: documentos ficcionalmente forjados são evidências de uma tentativa de engano na campanha, não atualização de lore canônico.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Lealdades históricas dos NPCs canônicos dependem de fontes e validade temporal; relações dinâmicas de campanha não alteram o cânone curado nem suas partições anuais.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Nenhum diálogo de NPC contratado é usado para preencher lacunas de lore canônico. Acordos são eventos locais; a fonte pode relatar rumor com proveniência.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Fonte editorial curada DEC-061 é distinta de fala de NPC: relatos no overlay não corrigem cânone por repetição. Conhecimento histórico permanece fisicamente por ano DR.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Separar fonte canônica curada e citação no dossiê de campanha. Não confundir evidência editorial de lore com prova de um depoimento ou conhecimento de NPC.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Lore curado informa plausibilidade regional/jurídica, não é dossiê/ordem de operação de campanha; separar fontes DEC-061.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Fontes canônicas não podem virar evidência de eventos reais na campanha; notificações DEC-092 consultam Knowledge Pack válido e facts do overlay.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Planejamento e agendas de operações não entram no lore canônico físico por ano DR; permanecem em overlays privados e só referenciam Knowledge Packs curados quando relevante.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

O catálogo proposto DEC-096 exige fonte primária/secundária classificada, precisão de data, disputa explicitada e revisão; a publicação de lore DEC-062 é independente de publicar regra de impacto.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-097/C — Discovery v9.3

Fontes de eventos e efeitos DEC-097/C preservam proveniência; famílias de impactos exigem validação editorial para evitar dupla contagem causal.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Fonte canônica é provenance de lore, não autoridade de edição de flags nem de recursos da engine.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Plano de testes futuro precisa validar zero side effect por probe e isolamento de spoilers com 1 host e 2 clientes.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração DEC-102/C (Discovery v9.8)

A DEC-102/C trata divergências entre milestone validado do host e projeção derivada do Living World: exigir mapeamento DEC-101, observação DEC-100, epoch/branch e receipts, e preservar o host, facts ledger e conhecimento dos NPCs. Somente proposta de revisão CAS/autorizada; detalhes em ADR-0097/doc. 102. **Sem POC mecânica.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para curadoria de fonte, proveniência e precisão temporal da retificação, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para fontes curadas, alcance, proveniência e precisão da prova, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.
