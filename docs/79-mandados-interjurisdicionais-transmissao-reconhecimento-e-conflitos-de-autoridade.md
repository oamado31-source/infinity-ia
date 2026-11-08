# 79 — Solicitações, mandados e conflitos de jurisdição entre regiões

**Estado:** Discovery v7.5, DEC-079/C **APROVADA apenas como arquitetura; NÃO IMPLEMENTADA**. Base normativa: `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md`. **62 testes candidatos T079-01..62, nenhum executado**. Sem demonstração de mandados, guardas perseguidores, prisão, captura, teleporte ou integração BG2:EE/EEex multiplayer.

## 1. Escopo e decisões preservadas

DEC-078 disciplina processo e competência local. DEC-079 define trânsito de pedidos, reconhecimento, recusa e negociação **entre** autoridades. Não define automaticamente execução de captura ou scripts de perseguição. Dependências: DEC-011/012 (host/gateway), DEC-019/022/027/028/029/030/031/032/033/034, DEC-041/042/045/046 (coop/consentimento), DEC-050–056 (build/checkpoints/recursos), DEC-060–063 (fontes e Knowledge Packs), DEC-064–069 (NPC/tempo/viagem), DEC-070–077 (incidentes, reputação, identidade, investigação), DEC-078 (justiça local).

**Imutabilidade histórica:** diretórios de lore canônico separados **fisicamente por ano DR**, como `knowledge/periods/1369-DR/` e `knowledge/periods/1370-DR/`. O sistema de mandados e seus relacionamentos de campanha ficam em overlay específico de `campaign_id/branch_id`. Fontes e direitos devem ser curados; nenhuma instituição/tratado/regra local é presumida factual em 1369 DR sem evidência.

## 2. Fronteiras de verdade e autoridade

| Camada | Objeto | Significado e limite |
|---|---|---|
| Fato investigado | `ConfirmedEvent`, `CaseEvidence` | Denúncia não equivale a crime, nem a prova de autoria |
| Decisão local | `LocalCaseDecision` | Competência da autoridade emissora, não poder mundial |
| Pedido entre regiões | `InterjurisdictionRequest` | Documento/ato de cooperação, não sentença no destino |
| Comunicação | `DeliveryEvent` | Indica transmissão/recepção quando há evidência, não aceitação |
| Avaliação destinatária | `RecognitionAssessment` | Aceitar, negar, negociar ou contestar sob política própria |
| Efeito de campanha | `InterjurisdictionConsequence` | Apenas efeito narrativo autorizado, não alteração mecânica automática |
| Efeito no motor | `HostEffectReceipt` | Só host via gateway tipado/adapter comprovado |

## 3. Modelo de dados candidato (não APIs existentes)

```yaml
JurisdictionPolicy:
  jurisdiction_id: string
  authority_id: string
  region_scope: [region_ref]
  faction_scope: [faction_ref]
  valid_dr_interval: [start_dr, end_dr]
  evidence_refs: [opaque_source_ref]
  knowledge_pack_revision: string
  authority_kind: TERRITORIAL | FACTIONAL | INSTITUTIONAL | DISPUTED | UNKNOWN
  powers_supported_by_sources: [opaque_policy_ref]
  competence_status: VERIFIED | UNKNOWN | DISPUTED | STALE
  policy_revision: string

AuthorityRelation:
  issuer_jurisdiction_id: string
  receiver_jurisdiction_id: string
  request_kind: INFORMATION | INVESTIGATION | NOTICE | ENFORCEMENT | EXTRADITION_REQUEST
  relation_state: COOPERATES | NEGOTIATES | REFUSES | CONTESTED | UNKNOWN
  valid_dr_interval: [start_dr, end_dr]
  source_evidence_refs: [opaque_source_ref]
  interaction_rule_ref: string | null
  revision: string

InterjurisdictionRequest:
  request_id: string
  source_case_id: string
  source_decision_id: string | null
  campaign_id: string
  branch_id: string
  issuer_authority_id: string
  receiver_authority_id: string
  issued_dr: dr_time_ref
  issuer_policy_revision: string
  case_evidence_refs: [opaque_ref]
  target_actor_identity_ref: opaque_ref | null
  target_persona_claim_ref: opaque_ref | null
  request_kind: INFORMATION | INVESTIGATION | NOTICE | ENFORCEMENT | EXTRADITION_REQUEST
  asserted_scope: opaque_scope
  risk_class: LOW | MEDIUM | HIGH
  required_authorizations: [opaque_ref]
  purpose_and_audience_acl: opaque_ref
  request_revision: integer
  expiry_or_revocation_refs: [opaque_ref]
  checkpoint_epoch: integer
  world_clock_mode: FROZEN | PARTIAL | REALTIME
  idempotency_key: string
  state: PROPOSED

DeliveryEvent:
  delivery_id: string
  request_id: string
  channel_ref: opaque_ref
  route_or_courier_evidence: [opaque_ref]
  sent_dr: dr_time_ref
  received_dr: dr_time_ref | null
  receiver_verified: boolean
  branch_id: string
  status: QUEUED | IN_TRANSIT | DELIVERED | FAILED | UNCERTAIN

RecognitionAssessment:
  assessment_id: string
  request_id: string
  recipient_policy_revision: string
  request_revision: integer
  issuer_validity: VERIFIED | UNKNOWN | DISPUTED | REJECTED
  local_competence: VERIFIED | UNKNOWN | DISPUTED | REJECTED
  evidence_and_contradiction_refs: [opaque_ref]
  result: PENDING | ACCEPTED | PARTIAL | CONDITIONAL | NEGOTIATE | REFUSED | DISPUTED
  approved_scope: opaque_scope | null
  recipient_authorization_ref: opaque_ref | null
  checkpoint_epoch: integer
  audit_ref: opaque_ref

InterjurisdictionConsequence:
  consequence_id: string
  case_id: string
  request_id: string
  recognition_assessment_id: string
  target_identity_ref: opaque_ref | null
  effect_kind: NARRATIVE_NOTICE | RELATION_CHANGE | GAME_ENGINE_ACTION
  risk_class: LOW | MEDIUM | HIGH
  gate_decision_ref: opaque_ref
  idempotency_key: string
  host_operation_ref: opaque_ref | null
  host_receipt_ref: opaque_ref | null
  state: PENDING | NARRATIVE_COMMITTED | ENGINE_PENDING | ENGINE_CONFIRMED | UNCERTAIN
```

IDs, estado jurídico detalhado, semântica criptográfica, storage, interfaces e matriz de confiança são candidatos de SPECS. Nenhum campo indica que o host tem hoje uma API de mandados ou prisão.

## 4. Máquina de estados de pedido e reconhecimento

```text
LOCAL_CASE_DECISION
     | proposta de comunicação + ACL + autoridade emissora
     v
REQUEST_PROPOSED --> ISSUER_VALIDATION --falha--> REJECTED/PENDING_EVIDENCE
     | autenticidade, conteúdo, risco, época e destinatário verificados
     v
QUEUED -> IN_TRANSIT -> DELIVERED (receipt de canal, não host)
                             |
                             v
                   RECEIVER_ASSESSMENT
                   /       |        \
               REFUSED   CONTESTED  ACCEPTED/PARTIAL/CONDITIONAL
                  |          |         |
               archive     negotiate   v
                                    EFFECT_GATE
                                      | LOW narrativo autorizado
                                      | MEDIUM/HIGH política especial
                                      v
                              NARRATIVE_COMMITTED | ENGINE_PENDING
                                                  | receipt host validado
                                                  v
                                            ENGINE_CONFIRMED
```

`UNCERTAIN` pode surgir em qualquer transmissão/operação e demanda reconciliação; `STALE/REVOKED` bloqueia execução posterior. Negociação é resposta com revisão e motivo, não aceitação automática. `DELIVERED` significa apenas recepção comprovada e **não** autorização de captura. O fluxo não implica que uma mensagem consiga ser entregue em qualquer região.

## 5. Regras determinísticas antes de LLM

1. Consultar autoridade emissora e destinatária em fontes por ano DR via Knowledge Pack fixado na campanha. Se não houver regra curada, registrar `JURISDICTION_UNKNOWN`.
2. Vincular pedido ao caso DEC-078 com fonte, revisão e alvo; não converter rumor em fato nem acusação em condenação.
3. Validar identidade alvo DEC-066 e personas DEC-076/077 sem expor secret linkage a outros públicos sem autorização.
4. Verificar que a relação dirigida entre autoridades e a competência abrangem o **tipo específico** de solicitação. Ex.: colaboração administrativa ≠ extradição.
5. Exigir ACL para cada destinatário antes de enfileirar; redigir segredos de PC e testemunhas.
6. Registrar rota e canal real de transmissão, com tempo DEC-022 e DEC-069. Sem comunicação plausível: `CHANNEL_UNAVAILABLE`/`PENDING`.
7. Reavaliar vigência de pedido e autoridade na emissão, recebimento **e antes de qualquer execução**; divergência bloqueia.
8. Aplicar política de aceite/recusa/condição/negociação do destinatário, com evidência de sua própria competência. LLM não arbitra.
9. Produzir consequência LOW narrativa permitida de maneira idempotente, ou encaminhar MEDIUM/HIGH aos gates DEC-027/034/041/042.
10. Ações mecânicas só por Action Gateway/host e adapter realmente testado por build. `UNCERTAIN` não permite repetição cega.
11. Monitorar revogações/retificações e sua entrega limitada. O protocolo de atualização distribuída é o objeto da DEC-080; não supor propagação instantânea.

## 6. Exemplos hipotéticos (não tratá-los como cânone confirmado)

**Athkatla → Baldur's Gate:** uma autoridade pede investigação relacionada a roubo. Sem tratado ou competência comprovada entre elas no ano DR, a autoridade destinatária recebe **pedido**, não obrigação de capturar. Uma resposta negativa é coerente. Se aceitar, ainda precisa de gates específicos para qualquer ação coercitiva. Não presumir políticas locais reais sem importar e curar as fontes apropriadas.

**Guildas rivais:** guilda mercantil oferece pistas a facção aliada, mas não possui automaticamente jurisdição territorial. Uma facção rival pode contestar a autenticidade do pedido ou recusar colaboração; distinguir crença/alegação de validade objetiva.

**Mensageiro atrasado, mandado revogado:** pedido entregue muito depois pode estar obsoleto. Antes de coerção, verificar revisão; se não for possível provar vigência, bloquear. O reconciliador e prioridade de avisos de revogação são DEC-080 futura.

**Guarda como NPC:** para encontrar o alvo fisicamente, a autoridade deve ter NPCs identificados e jornadas plausíveis DEC-066/069/071. Se a engine não permitir instanciar personagens/testar scripts, não afirmar que guardas iniciaram perseguição ou prenderam alguém.

## 7. Proteções de riscos, recuperação e multiplayer

- `HIGH` nunca autoriza automaticamente prisão, confisco, morte, reputação mecânica, flags de quest, spawn ou teleporte. A intenção da autoridade narrativa não é ação no BG2:EE.
- Ações múltiplas exigem classificação de risco acumulado; sanções associadas a casos distintos não se somam por retry da mesma requisição.
- Não imputar culpa a PC apenas porque outro membro do grupo foi acusado; consentimento e autoria DEC-041/075.
- `FROZEN/PARTIAL/REALTIME` e branch/checkpoint são gates antes de enviar, receber ou agir; backup/restore não transmite notícia futura.
- Receipts de envio, entrega, reconhecimento e efeito host são artefatos separados. Confundir assinatura de mensageiro com host receipt é falha de segurança.
- Revogação de worker LAN, mismatch de mod/build, personagem homônimo, conflito de autoridade e segredo sem ACL geram `PENDING`/`REJECTED`, não retry agressivo.
- Health Monitor DEC-055 registra filas paradas e incongruência, mas não autoriza operações coercitivas.

## 8. Plano progressivo de comprovação (todos pendentes)

1. **G79-0:** corpus mínimo *sintético* de autoridades, competência, relações entre regiões e pedidos por tipo/ano; testar conflitos e ausência de fonte.
2. **G79-1:** parser de solicitação/ACL e transmissão em simulador determinístico com relógio e canais; sem engine.
3. **G79-2:** duplo processamento, falsificação, desatualização, revogação, restore e reconciliação de efeitos no ledger.
4. **G79-3:** inventário BG2:EE/EEex somente leitura: possíveis observações de área/NPC/quest; nenhuma mutação em save.
5. **G79-4:** sandbox isolado com uma consequência LOW se a bridge suportar; depois host+dois clientes, save/load e failure injection.
6. **G79-5:** habilitar apenas capabilities comprovadas e autorizadas. Spawn/captura/confisco exigirão POCs próprias; continuar desabilitados até lá.

## 9. Matriz de 62 testes candidatos — NÃO EXECUTADOS

| ID | Cenário esperado | Execução |
|---|---|---|
| T079-01 | Decisão local de origem não cria reconhecimento global automático. | NÃO EXECUTADO |
| T079-02 | Solicitação sem case_id existente no ramo é rejeitada. | NÃO EXECUTADO |
| T079-03 | Solicitação com emissor não verificado permanece PENDING_VERIFICATION. | NÃO EXECUTADO |
| T079-04 | Autoridade de Athkatla sem política curada no ano DR fica UNKNOWN. | NÃO EXECUTADO |
| T079-05 | Autoridade receptora usa sua própria política, não a da emissora. | NÃO EXECUTADO |
| T079-06 | Relação COOPERATES não dá automaticamente competência de prisão. | NÃO EXECUTADO |
| T079-07 | Relação REFUSES permite negar pedido sem alterar evento de origem. | NÃO EXECUTADO |
| T079-08 | Relação NEGOTIATES permite resposta não coercitiva e revisionada. | NÃO EXECUTADO |
| T079-09 | Duas autoridades rivais permanecem COMPETENCE_DISPUTED. | NÃO EXECUTADO |
| T079-10 | Política de comércio não autoriza extradição criminal. | NÃO EXECUTADO |
| T079-11 | Fonte canônica sem vigência temporal não valida acordo internacional. | NÃO EXECUTADO |
| T079-12 | Ano DR posterior não cria tratado em ano anterior. | NÃO EXECUTADO |
| T079-13 | Conhecimento de outra branch não entra em reconhecimento atual. | NÃO EXECUTADO |
| T079-14 | Alteração de Knowledge Pack exige revalidação de precondições. | NÃO EXECUTADO |
| T079-15 | Autoridade de facto é distinta de mandato jurídico curado. | NÃO EXECUTADO |
| T079-16 | Rumor da ordem não equivale a ordem documental autenticada. | NÃO EXECUTADO |
| T079-17 | Selo forjado permanece alegação, não autoridade confirmada. | NÃO EXECUTADO |
| T079-18 | Identidade do mensageiro ambígua impede prova de entrega. | NÃO EXECUTADO |
| T079-19 | Entrega sem destinatário comprovado permanece pendente. | NÃO EXECUTADO |
| T079-20 | Entrega confirmada não concede aceitação automática. | NÃO EXECUTADO |
| T079-21 | Acusação recebida não vira culpa factual na outra cidade. | NÃO EXECUTADO |
| T079-22 | Pedido de informação não se transforma em mandado de captura. | NÃO EXECUTADO |
| T079-23 | Pedido de investigação não se transforma em ordem de execução. | NÃO EXECUTADO |
| T079-24 | Reconhecimento parcial não permite efeitos fora de seu escopo. | NÃO EXECUTADO |
| T079-25 | Reconhecimento condicional não executa até satisfazer precondições. | NÃO EXECUTADO |
| T079-26 | Reconhecimento revogado antes de execução bloqueia ação futura conhecida. | NÃO EXECUTADO |
| T079-27 | Revogação ainda em trânsito não cria onisciência instantânea. | NÃO EXECUTADO |
| T079-28 | Pedido STALE na fila não pode produzir nova operação coercitiva. | NÃO EXECUTADO |
| T079-29 | Retificação preserva proveniência do pedido inicial sem retcon. | NÃO EXECUTADO |
| T079-30 | Múltiplas cópias do mesmo pedido não geram múltiplos efeitos. | NÃO EXECUTADO |
| T079-31 | Dois mensageiros repetem notícia mas não contam como autoridades distintas. | NÃO EXECUTADO |
| T079-32 | Replay após restore não aplica efeitos de branch futuro. | NÃO EXECUTADO |
| T079-33 | Checkpoint divergente invalida operação de gateway. | NÃO EXECUTADO |
| T079-34 | Timeout de operação mecânica produz UNCERTAIN, nunca retry cego. | NÃO EXECUTADO |
| T079-35 | Worker LAN revogado não pode autorizar reconhecimento. | NÃO EXECUTADO |
| T079-36 | Cliente multiplayer não confirma prisão ou hostilidade sozinho. | NÃO EXECUTADO |
| T079-37 | Pseudônimo não identificado não é automaticamente associado ao PC. | NÃO EXECUTADO |
| T079-38 | Dados sigilosos do acusado não vazam no pedido a público não autorizado. | NÃO EXECUTADO |
| T079-39 | Logs de pedidos redigem origem sigilosa e aliases protegidos. | NÃO EXECUTADO |
| T079-40 | Consulta anual não escreve pedidos em knowledge/periods/<ANO>-DR/. | NÃO EXECUTADO |
| T079-41 | Notícia via rota usa janela temporal plausível, sem teleporte. | NÃO EXECUTADO |
| T079-42 | FROZEN impede avanço indevido de entrega. | NÃO EXECUTADO |
| T079-43 | PARTIAL mantém limites de processamento autorizados. | NÃO EXECUTADO |
| T079-44 | NPC mensageiro DORMANT não caminha fisicamente sem capacidade validada. | NÃO EXECUTADO |
| T079-45 | Guarda de outra cidade não surge mecanicamente ao receber pedido. | NÃO EXECUTADO |
| T079-46 | Área inexistente na build não recebe perseguidor. | NÃO EXECUTADO |
| T079-47 | NPC persistent identity ambíguo impede associação ao caso. | NÃO EXECUTADO |
| T079-48 | Pedido aceito sem host receipt não altera inventário ou quests. | NÃO EXECUTADO |
| T079-49 | Prisão mecânica é bloqueada sem adapter tipado por build. | NÃO EXECUTADO |
| T079-50 | Confisco não ocorre sem autorização e receipt do host. | NÃO EXECUTADO |
| T079-51 | Execução ou morte HIGH são negadas por padrão. | NÃO EXECUTADO |
| T079-52 | Ações LOW acumuladas que implicam HIGH sofrem reclassificação. | NÃO EXECUTADO |
| T079-53 | PC ausente não consente automaticamente em efeito prejudicial. | NÃO EXECUTADO |
| T079-54 | Guarda corrupto pode mentir na narrativa sem alterar ledger factual. | NÃO EXECUTADO |
| T079-55 | Facção hostil pode negar legitimidade de outra sem apagar o pedido. | NÃO EXECUTADO |
| T079-56 | Relação entre governos pode mudar durante trânsito, exigindo revalidação. | NÃO EXECUTADO |
| T079-57 | Notícia posterior de revogação não apaga que o destinatário já agiu. | NÃO EXECUTADO |
| T079-58 | Receipts de reconhecimento têm audience, issuer, branch e revision corretos. | NÃO EXECUTADO |
| T079-59 | Fila com backpressure conserva pedido sem inventar conclusão. | NÃO EXECUTADO |
| T079-60 | LLM local redige resposta, não decide competência ou sanção. | NÃO EXECUTADO |
| T079-61 | Duas autoridades aceitam solicitações sem aplicar automaticamente punição duplicada. | NÃO EXECUTADO |
| T079-62 | POC real host+dois clientes continua pré-requisito para suporte mecânico. | NÃO EXECUTADO |

Todos os `T079-*` são requisitos candidatos, **nenhum foi executado**. Não existem resultados de integração BG2:EE/EEex, métricas de rede, tabelas canônicas de tratados ou APIs de captura demonstrados nesta fase.

## 10. DEC-080 — Próxima decisão em aberto

**Revogações e correções de pedidos interjurisdicionais:** (A) atualização imediata e global; (B) revisões locais sem coordenação e retenção até consulta manual; (C, recomendada) versões causais assinadas/conferíveis, transmissão progressiva de correções/revogações, confirmação de recebimento, revalidação antes de coerção e contenção de ações potencialmente indevidas, sem onisciência e sem desfazer efeitos mecânicos à força. DEC-079 não aprova ainda essa política detalhada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

DEC-080/C complementa transmissão de mandados: revogações e retificações percorrem canais versionados; status autoritativo não coincide necessariamente com o conhecimento local. Safety gate bloqueia coerção HIGH incerta sem tornar NPC onisciente.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Reparação DEC-081 pode exigir competência de mais de uma autoridade; evitar dupla compensação entre jurisdições e respeitar transmissão de retratação por canal.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Órgão de fiscalização não recebe competência universal para punir autoridades de outra jurisdição; validar cooperação e reconhecimento DEC-079.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Pedido interjurisdicional não transporta identidade selada da fonte por padrão; envio de informação limitada por audiência, canal, finalidade e competência.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Proteção e realocação entre territórios dependem de autoridade destinatária, comunicação, calendário, rotas e recursos reais, não salvo-conduto global.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Mandados e pedidos não permitem consultar refúgio privado além de competência/ACL; transmissão regional não é conhecimento global instantâneo.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Pedido/mandado falso ficcional não constitui ordem autoritativa e não justifica cooperação mecânica; autenticação e jurisdição continuam verificadas.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Mandado baseado em suspeita de traição não é reconhecido globalmente; autoridade destinatária valida sua jurisdição e provas.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Acordo com informante não cria mandado reconhecido entre regiões nem canal de mensagem automático.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Mandado baseado em informe precisa origem, validade, competência e transmissão; destinatários distantes não recebem parecer privado automaticamente.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Receber dossiê não equivale a reconhecer mandado, nem a autoridade destinatária tem acesso automático à prova original ou aos dados privados.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Pedido interjurisdicional não vira ordem automática de ação; autoridade destinatária pode avaliar, recusar ou contestar.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Mandados e pedidos interjurisdicionais têm transmissão/cadência próprias; replanejar não cria cooperação instantânea.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Mandados concorrentes demandam avaliação de competência e recursos, sem criar guarda/transportador duplicado ou captura automática em outra jurisdição.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Reserva de mensageiro/guarda concorrida não autoriza teleportá-lo ou reconhecer mandado antecipadamente; transmissão e recebimento permanecem causais.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Mandados não conferem automaticamente acesso a flags de quests ou licença sobre personagens de mods.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Transmissão interjurisdicional só contém relatórios autorizados, não dumps de scripts de missão.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração DEC-102/C (Discovery v9.8)

A DEC-102/C trata divergências entre milestone validado do host e projeção derivada do Living World: exigir mapeamento DEC-101, observação DEC-100, epoch/branch e receipts, e preservar o host, facts ledger e conhecimento dos NPCs. Somente proposta de revisão CAS/autorizada; detalhes em ADR-0097/doc. 102. **Sem POC mecânica.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para transmissão interjurisdicional depende de canal e recibo, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para comunicações interjurisdicionais com recebimento legítimo, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Autoridades externas não obtêm competência geral sobre contratos. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Mandatos jurisdicionais não são equivalentes a assinatura de contrato. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
