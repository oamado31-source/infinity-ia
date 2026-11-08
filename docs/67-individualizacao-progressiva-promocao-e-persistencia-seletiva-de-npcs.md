# Desenho preliminar 67 — Individualização progressiva, promoção e persistência seletiva de NPCs

**Infinity AI / Discovery v6.3** · **DEC-067/C** · **ADR-0062** · **Status: decisão aprovada; contratos de SPECS propostos; nada implementado/testado**

## 1. Objetivo, motivação e limites

Permitir que NPCs comuns da cidade ou da estrada se tornem indivíduos relevantes por ações dos jogadores, sem implementar memória completa, agentes LLM ou simulação em tempo real para cada observação de NPC. A seleção envolve duas decisões independentes: (a) o NPC deve receber uma representação narrativa persistente? (b) há evidência para atrelar sua identidade às observações do motor BG2:EE? A resposta à segunda pergunta é regulada pela DEC-066, não pela criatividade do modelo.

Cenário de referência **hipotético**: um guarda genérico ajuda o grupo, recebe uma promessa confirmada e reaparece. O Infinity AI registra a promessa somente se o evento e o ator estiverem identificados com segurança. Não presumir que o motor disponibilize ID estável de guardas genéricos, suporte a spawn persistente ou callbacks de scripts. Validar POCs em Windows BG2:EE limpo, depois EEex, multiplayer, e posteriormente mods/EET em builds reproduzíveis DEC-003/051.

## 2. Modelo de população e estados distintos

| Camada | Representação | Persistência permitida | Custo e limites |
|---|---|---|---|
| `AGGREGATE` | População por região, função/facção e período, agregada por regras | Contagem, economia, eventos e projeções versionadas; sem biografia pessoal inventada | DISTANT/DORMANT com lotes DEC-021 |
| `EPHEMERAL` | Instância ou observação local de encontro sem identidade verificada | Cache temporário mínimo conforme retenção; sem herança de memória de homônimo | ACTIVE; não implica `NPCIdentity` |
| `PROMOTION_CANDIDATE` | Ator com interação significativa mas aguardando provas/autorizações | Evidências e pendências minimizadas, sem conexão a memória privada | Fila auditável, quotas e prazo para revisão em SPECS |
| `INDIVIDUAL_PERSISTENT` | Pessoa lógica identificada e autorizada | `NPCIdentity`, episódios, crenças, compromissos e relações segundo ACL | Simulação graduada por relevância, não LLM/tick |
| `SUSPENDED` | Identidade existente, vínculo runtime ou contexto incompatível | Preservar fato/identidade; interromper associação insegura | Revalidar após reload, migração ou fork |
| `ARCHIVED` | Identidade histórica persistida, fora de atividade | Registro acessível por política de retenção; nenhuma ação contínua compulsória | Política detalhada de DEC-068 ainda aberta |

**Nota:** estes estados de ciclo de vida não substituem os estados de evidência `UNSEEN/CANDIDATE/VERIFIED/AMBIGUOUS/STALE/REVOKED/SUPERSEDED` da DEC-066. Uma promoção exige vínculo verificado quando houver ligação com instância runtime. Um registro canônico único pode ser prioritário para cadastro lógico, mas sua correspondência com observações atuais continua sujeita a prova.

## 3. Critérios candidatos de promoção

| Sinal | Exemplo | Evidência necessária | Risco inicial |
|---|---|---|---|
| Relação recorrente confirmada | Encontros repetidos com um comerciante | Prova de ser a mesma pessoa entre observações | LOW–MEDIUM, conforme memória/ACL |
| Consequência moral/social | Guarda testemunha ação, espalha notícia | Evento confirmado e aquisição legítima DEC-029/064 | LOW–MEDIUM |
| Promessa/compromisso | PC deve favor a NPC | Identificação verificada, consentimento/agência quando afetada | MEDIUM |
| Participação em missão | Ajuda a resolver quest | Inventário de scripts/flags e receipts do host | MEDIUM–HIGH |
| Evento crítico | Morte, ressurreição, romance, facção, história canônica | Gates mecânicos/canônicos/consentimento e política HIGH | HIGH |
| Curadoria explícita | NPC único do jogo ou companion | Referência curada + reconciliação com instância/runtime | Classificar por efeito, não só por classe |

Saliência narrativa **não** é um `score` único do LLM nem comprovação de identidade. O host e as políticas por risco podem permitir promoção automática de nível LOW somente após testes e allowlist explícita; casos MEDIUM/HIGH são submetidos aos gates adequados, sem defaults permissivos. Recorrência aparente de homônimos não conta como confirmação de encontros sucessivos.

## 4. Contratos candidatos — NÃO implementados

```text
PopulationAggregate
  campaign_id, branch_id, region_id, world_interval, cohort_id
  count_or_estimate, faction_refs, occupation_refs, simulation_revision
  seed, aggregate_state_revision, event_watermark

NPCPromotionCandidate
  candidate_id, campaign_id, branch_id, mode=LIVING_WORLD
  observed_actor_ref, observation_epoch, build_fingerprint
  source_event_ids, source_receipts, identity_evidence_refs
  region_id, world_time, risk_tier, proposed_reason
  knowledge_pack_revision, acl_policy_revision
  status (PENDING_EVIDENCE|PENDING_AUTH|APPROVED|REJECTED|STALE)

NPCIndividualization
  npc_identity_id, campaign_id, branch_id, identity_revision
  verified_identity_binding_ref, promotion_event_id, promotion_policy_rev
  lifecycle (INDIVIDUAL_PERSISTENT|SUSPENDED|ARCHIVED)
  source_aggregate_cohort_ref?, source_aggregate_transition_id?
  memory_anchor_refs, belief_projection_refs, consent_refs
  last_confirmed_world_time, checkpoint_id, host_watermark

PromotionReceipt
  operation_id, idempotency_key, campaign_id, branch_id
  precondition_revision, identity_verification_revision
  aggregate_transition_revision?, approval_ref?, host_receipt_ref?
  outcome (APPLIED|DEFERRED|DENIED|UNCERTAIN)
  committed_event_ref, timestamp_or_world_time
```

Os nomes e schemas são **hipóteses de desenho**, não formatos reais do motor nem SPEC/DB implementados. Um `PopulationAggregate` pode ser estimativa, e não 1:1 com NPCs materiais da engine. Portanto não se assume automaticamente subtrair uma unidade de toda contagem agregada quando houver promoção: precisa haver transição definida e prova de que o agente individual participava daquele mesmo cohort para evitar dupla contagem.

## 5. Fluxo de promoção controlada

1. **Observar sem assumir identidade:** host/bridge produz observação ou evento possível. Se for `UNCERTAIN`, continuar pendente. NPC pode usar diálogo genérico aprovado.
2. **Classificar saliência:** regras de fatos confirmados identificam interação recorrente, dívida, testemunho, missão ou vínculo. LLM apenas sugere interpretação/contexto; não confirma fatos, identidade, spawn nem recibo.
3. **Verificar identidade DEC-066:** testar correspondência positiva, escopo campanha/ramo, build, checkpoint/epoch e ausência de conflitos. Se `AMBIGUOUS` ou `STALE`, interromper promoção com vínculo a memórias privadas.
4. **Aplicar política por risco:** LOW sob allowlist aprovada e verificações; MEDIUM/HIGH com aprovações exigidas. A política considera titulares de PCs, consentimento, relações com companions e restrições de scripts.
5. **Avaliar quota e economia:** priorizar jogabilidade/host, verificar orçamento DEC-056, decidir persistir quando autorizado, adiar processamento não urgente. Saturação não transforma aprovação em ação mecânica automática nem autoriza descarte de eventos.
6. **Registrar transação narrativa idempotente:** produzir um único `promotion_event_id`; verificar precondições e revisão causal do estado, identidade, agregados, políticas e recibos. Se a contagem agregada representar essa pessoa, transferir sua representação uma só vez com reconciliação; não duplo spawn nem dupla população.
7. **Habilitar memória e agenda seletivas:** criar projeções DEC-064/065 somente com episódios de fato adquiridos, ACL e âncoras já confirmadas; demais detalhes continuam desconhecidos. Simulação individual em background depende de relevância/atividade e orçamento, sem LLM em cada tick.
8. **Reconciliar e auditar:** registrar `APPROVED/APPLIED/DEFERRED/UNCERTAIN/REJECTED`; em rollback, fork, reload ou migração invalidar candidatos não compatíveis e preservar apenas fatos ancestrais confirmados.

## 6. NPC único, companion e figurante: distinções

- **Personagem único/companheiro curado:** ingresso prioritário no cadastro narrativo quando há referência curada, mas não confirma automaticamente que a instância atual seja aquele ator nem autoriza sobrescrever quest, romance, controle ou script nativo DEC-047–051.
- **NPC genérico com interação de baixo impacto:** permanecer efêmero até que haja ganho real em persistência e evidência segura; aparência, CRE, nome e ocupação são pistas e podem ser reciclados.
- **NPC genérico relevante, mas impossível de rastrear:** `PROMOTION_CANDIDATE`/`SUSPENDED`; preservar apenas fatos com escopo correto, sem simular encontro futuro como a mesma pessoa. Pode solicitar reconciliação ao anfitrião quando política permitir.
- **NPC individual não visível:** não precisa permanecer materializado na engine. Pode existir como entidade narrativa somente se houver fonte causal/documental suficiente e transições sob regras; qualquer materialização futura requer host e prova de identidade.
- **NPC canônico na mesma região:** diretório físico anual é referência curada de lore, não fonte de memória pessoal. Ancoragem a um registro editorial não substitui ID lógico de campanha.

## 7. Autonomia, desempenho e relógio

- **ACTIVE:** priorizar NPCs confirmados na cena; resposta sob demanda; não alterar scripts mecânicos por conta própria.
- **NEAR:** planejar deslocamentos, compromissos e encontros possíveis por regras, sem simular cada passo. Limites de agenda e evidência a especificar.
- **DISTANT:** agregar resultados quando adequados e executar lotes limitados no relógio autorizado; não inventar destinos/resultado confirmado sem evento.
- **DORMANT:** pausar serviços não urgentes e retomar sob demanda com catch-up limitado DEC-022; consequências irreversíveis protegidas DEC-034.
- **Prioridade:** `P0` consistência/segurança e host, `P1` interações imediatas, `P2/P3` simulação próxima/distante; detalhes de prioridade e quotas dependem da DEC-056 e benchmarks de hardware.
- **Repressão de backlog:** fila durável, idempotência e descarte apenas de tarefas recalculáveis, não de eventos confirmados. Cache cancelado não equivale a memória apagada. DEC-068 detalhará hibernação da vida individual fora de cena.

## 8. Governança de conhecimento, privacidade e cronologia — DEC-060–066

1. **DEC-060:** pastas físicas `knowledge/periods/<ano>-DR/{chronology,events,organizations,guilds,characters,regions}` independentes; busca começa no ano confirmado, antecedentes válidos sob gates; futuro não vira fato presente. O novo registro `NPCIndividualization` não entra nessas pastas.
2. **DEC-061:** manter `Source/Claim/ConflictSet`, referências e curadoria; não preencher lacuna de biografia com síntese de fontes editoriais conflitantes.
3. **DEC-062:** ingestão via staging licenciado/curado por ano; não publicar saída bruta de LLM em lore ou perfil pessoal.
4. **DEC-063:** Knowledge Pack pinado por campanha, alterações editoriais sujeitas a diff e adoção controlada; não atualizar a mente de NPC promovido por simples alteração de pack.
5. **DEC-064:** memórias/convicções adquiridas via observação/comunicação legítima; crença ≠ fato e episódio ≠ concordância.
6. **DEC-065:** memória imediata/episódica/consolidada/crítica, revisão versionada, sem apagamento de episódio por resumo ou expiração cega.
7. **DEC-066:** `NPCIdentity` per-campaign/branch e `EngineObservation` efêmera, correspondente apenas se `VERIFIED`; qualquer `AMBIGUOUS`, `STALE`, revogação ou `UNCERTAIN` exige bloqueio de vinculação pessoal.
8. **DEC-028/029:** ACL antes de consulta/prompt/worker remoto; rumor, segredo e memória pertencem a seus destinatários autorizados. Eventos públicos não criam conhecimento universal.
9. **DEC-011/012:** Action Gateway com allowlist e receipt do host para mecânica; promoção narrativa não altera classe, inventário, presença física, scripts ou status de vida.
10. **DEC-051/052/053/054:** build, checkpoints, backups, fork e rollback são gates para índices de identidade e revisão da população. Modo Original sempre isolado.

## 9. Casos adversariais e segurança

| Caso | Resultado seguro esperado |
|---|---|
| Dois guardas homônimos aparecem em Athkatla | Nenhum vínculo entre histórias por nome; manter observações distintas ou `AMBIGUOUS` |
| CRE ou engine handle é reutilizado após respawn | Não transferir memória sem prova nova de continuidade |
| Jogador promete pagar NPC, mas evento do host é `UNCERTAIN` | Promessa não confirmada; promoção/relacionamento pendentes |
| Um mercador tem diálogo recorrente, mas identificação permanece incompleta | `PROMOTION_CANDIDATE`, sem projetar memórias no próximo mercador parecido |
| Engine cria duplicata por mod | Detectar múltiplos candidatos e negar merge automático |
| Worker LAN sugere que figurante é o mesmo NPC antigo | Proposta sem poder de vinculação; host/verificador decide por evidências |
| Quota de NPCs é atingida | Adiar novas individualizações não urgentes; proteger eventos/identidades já confirmados |
| População agregada pode incluir NPC recém-promovido | Reconciliar projeção com transição idempotente, sem dupla contagem |
| Campanha é restaurada antes de promoção | Evento de promoção posterior não aparece; branch irmão mantém isolamento |
| Ato altera reputação/quest/vida | Usar política de risco e Action Gateway; nenhuma alteração mecânica implícita |
| NPC promovido deixa a área/party | Preservar identidade e memórias; simulação ajustável por DEC-021 e futura DEC-068 |
| Conhecimento é de ano futuro em relação ao mundo | Negar uso factual e propagação automática; consultar ano atual e antecedentes válidos |

## 10. POCs e critérios de aceitação futuros

- **POC-ID-1:** observar dois NPCs genéricos com mesmo nome/CRE e testar quais campos, se houver, discriminam as instâncias com estabilidade; documentar limites.
- **POC-ID-2:** reload, teleporte, mudança de área, respawn, clone, party join/leave e host+dois clientes; medir falso positivo de associação, com prioridade para impedir vazamento.
- **POC-PROMO-1:** cenário controlado de figurante que recebe promessa confirmada; demonstrar promoção lógica e persistência sem edit indevido de save/mod.
- **POC-PROMO-2:** promoção/rollback/fork/checkpoint, event sourcing e recuperação sem duplicar NPC ou aplicar evento duas vezes.
- **POC-PROMO-3:** reconcile de população agregada em cena e depois de viagem, sem inflar contagens sociais/econômicas nem forçar spawn novo.
- **POC-PERF-1:** workloads com muitos NPCs efêmeros, promoção seletiva e concorrência LLM; coletar FPS, latência do host, memória, CPU, fila e custo I/O. Valores limites só em SPECS.
- **POC-SEC-1:** testes ACL de segredos, atravessamento de campanha/branch, dados LAN e dados do Original Mode.

Sem POC, **não** alegar identidade persistente de spawns, hooks de engine, transferência atômica de agregado, spawn/migração e controle individual de offscreen como capacidades disponíveis.

## 11. Testes candidatos — TODOS NÃO EXECUTADOS

1. **T067-01:** NPC único curado entra no cadastro lógico sem assumir correspondência de engine.
2. **T067-02:** NPC de fundo inicia `AGGREGATE` sem biografia inventada.
3. **T067-03:** Instância efêmera não recebe memória pessoal automaticamente.
4. **T067-04:** Evento relevante confirmado cria apenas um candidato à promoção.
5. **T067-05:** LLM propõe importância, mas não certifica identidade nem evento.
6. **T067-06:** Mesmo nome não une guardas de origens distintas.
7. **T067-07:** Mesmo portrait/CRE não basta para promoção persistente.
8. **T067-08:** ID reciclado após respawn não restaura memória de outro indivíduo.
9. **T067-09:** `AMBIGUOUS` bloqueia vínculo de memória/segredo ao candidato.
10. **T067-10:** `STALE` por migração exige nova confirmação antes de promoção.
11. **T067-11:** `UNCERTAIN` do host não autoriza evento nem promoção.
12. **T067-12:** Prova de identidade `VERIFIED` e evento válido permitem iniciar gate de promoção.
13. **T067-13:** LOW sem allowlist explícita não publica individualização automática.
14. **T067-14:** MEDIUM exige política e autorizações aplicáveis.
15. **T067-15:** HIGH com morte/quest/romance não contorna gateway/host.
16. **T067-16:** Duas requisições concorrentes não criam identidades duplicadas.
17. **T067-17:** Retry do mesmo `promotion_event_id` é idempotente.
18. **T067-18:** Transição agregado→indivíduo não duplica contagem quando cohort comprovado.
19. **T067-19:** Agregado apenas estimado não perde um membro sem evidência.
20. **T067-20:** Nenhum spawn mecânico é criado por promoção narrativa isolada.
21. **T067-21:** Memória pessoal inclui somente episódios com aquisição legítima.
22. **T067-22:** NPC promovido não herda passado inventado por LLM.
23. **T067-23:** Âncoras críticas DEC-065 sobrevivem à redução de simulação.
24. **T067-24:** Quotas e saturação adiam promoções não urgentes sem descartar fatos.
25. **T067-25:** NPC em ACTIVE recebe prioridade sobre simulação DISTANT.
26. **T067-26:** NPC DORMANT não exige LLM por tick.
27. **T067-27:** Fork não transfere episódios posteriores entre branches.
28. **T067-28:** Restore anterior à promoção invalida vínculo derivado futuro.
29. **T067-29:** Original Mode não acessa overlay de Living World.
30. **T067-30:** Partições físicas anuais DEC-060 não recebem memória NPC.
31. **T067-31:** Fonte editorial conflitante DEC-061 não preenche biografia automaticamente.
32. **T067-32:** Ingestão DEC-062 e atualização de Pack DEC-063 não promovem NPCs sozinhas.
33. **T067-33:** Mudança de ACL impede exfiltração via modelo ou worker LAN.
34. **T067-34:** Diálogo genérico continua possível quando identidade não é comprovada.
35. **T067-35:** Revogar vinculação errada invalida projeções e caches dependentes.
36. **T067-36:** Relatório de POC explicita limites não comprovados BG2:EE/EEex/multiplayer.

**Todos os 36 testes acima são candidatos NÃO EXECUTADOS.** Critérios de aprovação, evidências e fixtures devem ser definidos em SPECS; nenhum resultado foi inferido ou produzido aqui.

## 12. Próxima discussão — DEC-068

Como reduzir atividade de um NPC já individualizado quando fica fora de cena sem descartar sua identidade? **A:** manter execução detalhada contínua; **B:** desindividualizar e apagar memórias quando perder relevância; **C (recomendada):** atividade adaptativa/habitação operacional, memória persistente e retomada reconciliada por tempo, região, branch, host e checkpoints. Não decidir taxas ou limites sem benchmarks.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

A DEC-068 resolve o ciclo operacional do NPC promovido: conservar individualidade e memórias, reduzir atividade em DISTANT/DORMANT, usar filas/catch-up delimitado e validar retorno contra identidade/branch/host. Arquivamento não é desindividualização nem descarte; ADR-0063/doc. 68.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: indivíduo promovido muda de região sem reentrar simultaneamente no agregado de origem/destino; percursos não geram clones de NPC.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070: incidentes LOW confirmados podem contribuir para relevância de promoção, mas incidente candidato não cria automaticamente NPC individual nem duplica população agregada.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Participar de encontro DEC-071 efetivamente confirmado pode candidatar NPC genérico à promoção DEC-067; proposta não vivenciada não justifica memórias ou promoção. Deduplicar contagem agregado/individual.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Um ator genérico em template DEC-072 não vira automaticamente NPC persistente DEC-067; promoção depende de interação confirmada, identidade comprovada e política de risco.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

NPC promovido individualmente não pode ser desindividualizado ou apagado como cleanup de encontro; continuidade por branch.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

NPC genérico promovido só ganha memórias de mérito se sua identidade e participação forem comprovadas, sem herdar credenciais/feitos de figurantes indistintos.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Promover NPC efêmero não confirma que todo pseudônimo visto pertence a ele; criação de persona exige identidade verificada/ACL e bloqueio de homônimos.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

NPC promovido a persistente pode ganhar histórico de compromissos sob prova; promoção não inventa passado de agente duplo.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Promover NPC genérico para persistente não cria automaticamente elegibilidade ou competência para oferecer segredos; fatos e alcance avaliados.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Promoção de NPC efêmero não valida retroativamente seus rumores ou torna depoimentos múltiplas fontes; conservar proveniência.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-091/C — Discovery v8.7

Promover NPC efêmero para persistente não implica que aceitou plano ou possua recursos/compromissos.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

NPC promovido a persistente não herda automaticamente aprovação/posição de um NPC genérico do plano antigo.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Promover NPC transitório não duplica vagas/identidades reserváveis em duas operações; associar a registro persistente antes de compromisso durável.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Promoção seletiva cria identidade persistente distinta de leases; não permite recuperar automaticamente NPC apagando instância ou inventando substituto.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

NPC promovido mantém identidade e escopo de recursos; snapshot de região não cria nova pessoa cada vez que o jogador retorna.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Promover um NPC genérico a persistente não adota automaticamente scripts ou assets de terceiros.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Promoção de NPC offscreen não permite sondar flags protegidas de outros recursos sem capability/ACL.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Regional simulation and materialization cannot treat ambiguous quest flags as facts. Protect quest-owned actors/objects and persistent NPC identities; semantic milestones need curated proof and do not grant spawn, despawn, cleanup, loot or irreversible effects without existing host gates. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

A DEC-102/C trata divergências entre milestone validado do host e projeção derivada do Living World: exigir mapeamento DEC-101, observação DEC-100, epoch/branch e receipts, e preservar o host, facts ledger e conhecimento dos NPCs. Somente proposta de revisão CAS/autorizada; detalhes em ADR-0097/doc. 102. **Sem POC mecânica.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **promoção de NPC**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para promoção NPC não pode criar lembranças retroativas de rumores, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para promoção de NPC não cria histórico reputacional retroativo, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
