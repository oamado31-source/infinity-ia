# 70 — Incidentes e riscos em viagens de NPCs: proposta, validação e confirmação segura

**Status:** Discovery v6.6; DEC-070/C aprovada, **sem implementação**, testes de integração e benchmarks **não executados**. Referência normativa: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md`.

## 1. Objetivo e não objetivos

- **Objetivo:** dar continuidade plausível a viagens DEC-069 com encontros, contratempos e perigos regionalmente fundamentados, diferenciando narrativas, fatos objetivos, propostas e alterações mecânicas confirmadas.
- **Não objetivo:** resolver automaticamente combate, prisão, morte, inventário, reputação mecânica ou quest fora do jogo. Nenhuma garantia de funcionalidade EEex/BG2:EE/multiplayer nesta fase.
- **Não objetivo:** reescrever fonte canônica para justificar acontecimentos do overlay privado; NPCs não são oniscientes; boatos não equivalem a fatos.

## 2. Contexto mínimo obrigatório para candidatar incidente

Toda proposta deve ser tipada e carregar, quando aplicável, os seguintes campos candidatos (não são API já implementada):

```text
TravelIncident {
  incident_id, idempotency_key, campaign_id, branch_id,
  npc_identity_id, identity_evidence_ref, itinerary_id, segment_id,
  world_time_window, clock_mode, checkpoint_epoch,
  build_manifest_ref, knowledge_pack_revision,
  evidence_refs[], source_provenance[], rumor_or_fact,
  incident_type, proposed_effects[], aggregate_impact,
  risk_class: LOW | MEDIUM | HIGH,
  required_permissions[], consent_receipts[],
  host_receipt_ref?, narrative_event_ref?,
  status, state_revision, queue_priority, created_at
}
```

- Identidade verificada DEC-066; região/segmento/tempo DEC-069; fonte temporal DEC-060–063; evento/risk DEC-027; state revision e host DEC-011/053.
- Fonte sem intervalo temporal confiável não pode dar certeza de evento em um dia definido.
- Ausência de confirmação do host não significa falha de transmissão resolvida; representa `UNKNOWN` ou `UNCERTAIN` conforme o contrato.

## 3. Origens e qualificação de incidentes

1. **Candidato factual:** observação confirmada no host, evento regional previamente adotado, rota interditada com evidência e validade no tempo/ramo.
2. **Candidato narrativo:** encontro social compatível, rumor, relato de viajante, sugestão do diretor de encontros DEC-005-E — explicitamente PROPOSED até ser validado.
3. **Candidato de facção/economia:** acontecimentos com efeito sobre comércio, segurança ou fronteiras só após simulação regional autorizada DEC-031–033; não inferir guerra ou perda pelo texto de LLM.
4. **Candidato de IA:** uso eventual do roteador DEC-059 para variantes narrativas autorizadas; sempre passa por DEC-060 e gateway DEC-012/027.
5. **Candidatos inválidos:** período futuro, conhecimento inacessível, rota inventada, NPC não identificado, build incompatível, duplicidade, segredo sem ACL.

## 4. Matriz de risco — exemplos, não classificação final de SPECS

| Classe | Exemplo | Política mínima |
|---|---|---|
| LOW | Conversa inofensiva entre viajantes, avistamento sem efeito, rumor corretamente rotulado | Regras curadas, allowlist, ACL, idempotência, commit **apenas narrativo**, orçamento; nenhuma mutação de engine |
| MEDIUM | Atraso relevante, rota bloqueada comprovada, pacto comercial/social com consequências significativas | Evidência, impacto agregado, validação contextual, autorização aplicável, eventual pausa/replanejamento antes de publicar consequências |
| HIGH | Morte, captura, perda de equipamento, ferimentos mecânicos, combate decidido fora de cena, alteração de quest/romance, colapso histórico | **Bloqueado por padrão**; autorização especial, precondições da engine e recibo host para efeitos mecânicos, sem auto-commit |

- A taxonomia exata por consequência é definida em SPECS. Uma sequência de LOW com efeito agregado MEDIUM/HIGH não herda autorização LOW.
- **Simular probabilidade de encontro** não implica **simular resultado mecânico do encontro**; a primeira pode propor, a segunda requer gate compatível, ou permanece indisponível.
- Eventos narrativos LOW autorizados podem alimentar memória pessoal DEC-064/065 ou rumores DEC-029 **somente** depois de publish validado, sem propagação instantânea.

## 5. Máquina de estados candidata

```text
DETECTED -> PROPOSED -> VALIDATING
                           |-> REJECTED
                           |-> PENDING_AUTHORIZATION
                           |-> APPROVED_NARRATIVE -> NARRATIVE_COMMITTED
                           |-> APPROVED_ENGINE    -> ENGINE_PENDING
                                                     |-> ENGINE_CONFIRMED
                                                     |-> UNCERTAIN -> RECONCILIATION

PAUSED / STALE / REJECTED nunca equivale a efeito ocorrido.
``` 

- `APPROVED_NARRATIVE` só permite fatos narrativos dentro da permissão e sem alteração de HP/inventário/quest.
- `APPROVED_ENGINE` é intenção sob contrato; **sem host receipt não há efeito mecânico confirmado**.
- Falhas de conexão mantêm `UNCERTAIN`, exigindo reconciliar o estado real antes de repetição de qualquer comando.
- Replays e restaurações usam IDs, epochs e revisões; cada consequência tem no máximo um commit lógico para a campanha/ramo.

## 6. Autorizações e consentimento

- **DEC-027:** LOW curado pode ter execução automática pré-aprovada; MEDIUM submetido à política contextual; HIGH bloqueado salvo gates especiais documentados.
- **DEC-034:** fatos canônicos e marcos históricos não mudam apenas porque uma rota possui perigo.
- **DEC-041/042/046:** incidentes que afetem controle ou patrimônio de personagens de jogador respeitam consentimentos existentes; ausência de jogadores não é consentimento.
- **DEC-050:** scripts/quests/romances nativos têm precedência até prova de compatibilidade.
- **DEC-011/012:** gateway tipado, allowlist e receipt do host para efeito físico; nenhuma chamada direta arbitrária de Lua/shell por LLM.

## 7. Continuidade espacial/temporal e escalabilidade

- Itinerário versão X e segmento Y são pré-condições. Se o trecho foi alterado por bloqueio, o incidente antigo vira `STALE` e não aplica efeito em outro trecho.
- `FROZEN/PARTIAL/REALTIME` DEC-022 e catch-up bounded; tempo real decorrido e jobs atrasados não garantem eventos de mundo.
- ACTIVE/NEAR/DISTANT/DORMANT DEC-021/068 modulam profundidade; regras regionais são preferidas a LLM por tick.
- RPD DEC-056 poderá adiar propostas não críticas preservando ordem e watermarks; não ultrapassar eventos pendentes com efeitos incompatíveis ou consumir futuro.
- Não criar presença física, NPCs, áreas, combate ou rotas fora dos recursos confirmados na instalação DEC-051/052/069.

## 8. Consistência, observabilidade e recuperação

- Guardar `incident_id`, `idempotency_key`, status, `segment_id`, revisões, evidence refs, classificação/razão, receipt narrativo ou mecânico, aprovação e cursor temporal no overlay da campanha.
- Checkpoint DEC-053 captura proposta, fila, conflitos e receipts, sem assumir que save BG2:EE registrou efeito de worker. Backups DEC-054 e restauros aplicam invalidação de futuro.
- Health Monitor DEC-055 mede pendências/uncertainty sem acesso desnecessário a segredos, sem cura por repetir comando desconhecido.
- Node LAN DEC-057/058/059 pode propor conteúdos dentro da ACL, nunca publicar efeito mecânico unilateralmente.
- Observabilidade distingue eventos vistos, propostos, aprovados, narrativos confirmados e efeitos host confirmados; nenhum log de segredo em claro por padrão.

## 9. Impacto sobre NPCs, reputação e facções

- Episódios e crenças DEC-064 dependem de observação ou comunicação plausível; um rumor sobre ataque na rota não registra ataque como fato.
- Conteúdos candidatos podem influenciar simulações econômicas/facções somente após confirmação e autorização pertinente; não duplicar perdas contabilizadas pelos mecanismos regionais.
- Mudanças de reputação/alinhamento não são efeitos colaterais LOW; precisam dos gates DEC-030/035–037.
- NPC individual DEC-067 mantém registro próprio sem duplicação no agregado; morte/captura não podem ser inferidas ao reativar NPC DORMANT.

## 10. Interfaces/contratos candidatos para SPECS

```text
proposeIncident(itinerary_ref, segment_ref, evidence_refs) -> IncidentProposal
assessRisk(incident, projected_cumulative_effects) -> RiskAssessment
validateIncident(proposal, campaign_snapshot, knowledge_pack) -> GateDecision
requestAuthorization(gate_decision, actor_permissions) -> AuthorizationReceipt?
commitNarrativeLow(approved, checkpoint_epoch) -> NarrativeEventReceipt
requestEngineEffect(approved, host_bridge) -> PendingHostOperation
reconcileHostReceipt(operation_id, engine_observation) -> Confirmed | Uncertain
pauseOrReplanTravel(validated_route_disruption) -> ItineraryRevision
```

Esses contratos são candidatos, não APIs existentes. `commitNarrativeLow` significa criação controlada de registro *narrativo* na campanha, nunca escrita no motor; qualquer efeito persistente de maior risco exige o gate aplicável.

## 11. POCs propostas — nenhuma executada

- **POC-070-A:** simular apenas propostas/deduplicação em harness externo determinístico com dois NPCs, rotas e boatos, sem engine.
- **POC-070-B:** distinguir `NARRATIVE_COMMITTED` de `ENGINE_CONFIRMED`, com falhas de rede e replays, sem comandos mecânicos reais.
- **POC-070-C:** baseline BG2:EE limpo em read-only: inspecionar se existem evidências úteis de encontros/posições; inventariar limites da bridge/EEex.
- **POC-070-D:** apenas após autorização e backup: testar mutações offline seguras/allowlisted em área de teste, com receipt e restauração.
- **POC-070-E:** host + dois clientes, save/reload, desconexão, mods e reconciliação; desabilitar efeitos não comprovados.

## 12. Matriz de testes candidata (NÃO EXECUTADA)

1. **T070-01:** Rota de risco elevado sem evidência de ataque gera contexto/proposta, nunca incidente confirmado.
2. **T070-02:** Boato sobre estrada bloqueada não pausa itinerário como fato objetivo.
3. **T070-03:** Fato regional com ano DR incompatível não gera incidente na campanha de 1369 DR.
4. **T070-04:** Consulta às fontes utiliza partição física `knowledge/periods/<ano>-DR/` sem fusão temporal.
5. **T070-05:** Conflito de fontes não resolvido pela curadoria permanece incerto, sem evento factual.
6. **T070-06:** Incidente registra fonte, temporalidade, trecho, evento regional e confiança sem inventar coordenadas.
7. **T070-07:** Incidente LOW exclusivamente social pode ser aceito após allowlist, ACL e deduplicação.
8. **T070-08:** LOW sem allowlist fica pendente ou rejeitado; não é automaticamente aplicável.
9. **T070-09:** LOW não cria loot, XP, HP, ferimento nem altera engine ou save.
10. **T070-10:** Série de ocorrências LOW com efeito agregado MEDIUM/HIGH sofre reclassificação.
11. **T070-11:** Prompt LLM que afirma “já autorizado” não modifica a classificação nem obtém aprovação.
12. **T070-12:** Worker LAN sem permissão para segredos não recebe contexto privado de NPC.
13. **T070-13:** Revogação de pareamento LAN invalida proposta ainda não adotada.
14. **T070-14:** Incidente MEDIUM sem autorização exigida permanece pendente sem commit.
15. **T070-15:** Bloqueio de estrada comprovado altera rota apenas após política de alteração e evidência.
16. **T070-16:** Bloqueio não comprovado não força rerouting e mantém status UNKNOWN/PROPOSED.
17. **T070-17:** Proposta HIGH de ataque letal nunca equivale a morte de NPC fora de cena.
18. **T070-18:** Proposta HIGH de roubo de inventário não altera itens de jogo sem confirmação host.
19. **T070-19:** Quest/romance nativo afetado bloqueia até verificação de scripts e autorizações DEC-050.
20. **T070-20:** Evento histórico protegido DEC-034 permanece bloqueado sem autorização especial.
21. **T070-21:** Relato ficcional de luta não é traduzido em recibo de combate da engine.
22. **T070-22:** Derrota/vitória simulada sem host não cria recompensas, perdas nem XP.
23. **T070-23:** Operação mecânica UNCERTAIN não é repetida cegamente após timeout.
24. **T070-24:** Receipt do host pertencente a outra área/instância é recusado.
25. **T070-25:** Observação mecânica exige NPCIdentity VERIFIED da DEC-066 e sessão/epoch compatíveis.
26. **T070-26:** NPC homônimo em mesma rota não recebe incidentes ou consequências de outro.
27. **T070-27:** FROZEN com sessão fechada impede avançar eventos no relógio do mundo.
28. **T070-28:** PARTIAL aplica somente intervalo de simulação permitido e registrado.
29. **T070-29:** REALTIME não presume que perigo provável ocorreu em horário de mundo não confirmado.
30. **T070-30:** Job DISTANT processado atrasado não altera a ordem causal nem consuma a etapa futura.
31. **T070-31:** DORMANT preserva incidentes pendentes sem resolução ou IA/tick.
32. **T070-32:** Backpressure e quotas impedem fila infinita ou starvation de incidentes críticos.
33. **T070-33:** Evento duplicado (idempotency_key) não duplica rumor, custo, perda ou bloqueio.
34. **T070-34:** Restore anterior ao incidente invalida resolução futura e reabre apenas revisão compatível.
35. **T070-35:** Fork da campanha isola incidentes e seus resultados por branch.
36. **T070-36:** Checkpoint inclui incidentes, autorizações, states, refs de segmento e watermarks.
37. **T070-37:** Mudança de build/mod invalida contratos que requerem áreas/CRE/scripts inexistentes.
38. **T070-38:** Viagem narrativa concluída não garante presença mecânica no destino.
39. **T070-39:** NPC individualizado não é contado em agregado e indivíduo após incidente.
40. **T070-40:** Publicação de evento narrativo aprovado não dá ao NPC conhecimento instantâneo sem canal social.
41. **T070-41:** Logs operacionais distinguem DETECTED, PROPOSED, APPROVED, COMMITTED e UNCERTAIN sem expor segredo.
42. **T070-42:** Original Mode e campanhas paralelas não compartilham acontecimentos privados.
43. **T070-43:** Proximidade de jogador durante incidente pendente não gera encontro físico automático (DEC-071 em aberto).
44. **T070-44:** POC em fases: BG2:EE limpo read-only → EEex → offline controlado → host+2 clientes confirma ou bloqueia efeitos reais.

**Os 44 testes acima são candidatos, e nenhum foi executado.** Não existe nesta etapa medição, capacidade de disparar encontros físicos ou prova de EEex/BG2:EE/multiplayer. Regras finais, thresholds e probabilidade de acontecimentos são escolhas futuras de SPECS e POCs.

## 13. Próxima discussão — DEC-071 (EM ABERTO)

**Handoff seguro de incidentes offscreen para oportunidades de encontro jogável** quando os jogadores se aproximarem de uma rota: **A** somente narrativa; **B** converter automaticamente tudo em evento físico; **C (recomendada)** oferecer/ativar seletivamente se compatível, autorizado e host-confirmado, bloqueando simultaneamente resolução offscreen para impedir dupla consequência. Essa política ainda não está aprovada e não se confunde com a DEC-033 sobre encontros locais em guerras estratégicas.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

O fluxo DEC-070 agora tem política de handoff DEC-071/C (ADR-0066): reservar resolução local para o mesmo `incident_id`, pausar offscreen, validar área/build/party/identidade/gates e exigir recibo do host para efeito mecânico. Se incompatível, manter evento narrativo/pending; se `UNCERTAIN`, reconciliar. O presente documento 70 não é permissão para spawn.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

INCIDENTE DEC-070 pode motivar proposta de composição DEC-072, mas hazard, ataque e loot não ocorrem até validação de risco, reserva DEC-071 e eventual receipt mecânico.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Conclusão de incidente exige receipt/ledger; risco do cleanup é avaliado independentemente do risco do evento de viagem.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Evento de viagem DEC-070 pode gerar rumor DEC-074, mas somente se originado em fato confirmado para efeitos factuais; boato sobre emboscada não prova combate. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Incidente narrativo/hipotético não prova autoria. Somente ocorrência confirmada sustenta contribuição factual, e consequência negativa continua sob gates.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Rumor de que um viajante mascarado é PC conhecido é alegação contextual, não fato confirmado; exposição de segredo exige risco, ACL e consentimento.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Crime relatado durante viagem pode iniciar denúncia DEC-078, mas risco e presença host continuam, sem prender viajante por rumor offscreen.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Incidente em rota DEC-070 não é prova de crime/mandado DEC-079; qualquer captura exige gates, fontes e host. Não simular detenção automaticamente.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Incidente de viagem só origina dano indenizável quando consequência confirmada e nexo causal demonstrado; rumor de ataque não prova perda de inventário.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Ameaça a denunciante pode ser incidente alegado; evento HIGH não executa ataque/captura sem host e gates. Risco não é ocorrência.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Rumor de emboscada contra testemunha não materializa combate; classificação de risco, incident_id e host confirmam somente fatos e efeitos permitidos.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Descobrir rota por inteligência parcial não dispara emboscada: incidente exige risco, precondições e autoria confirmada conforme DEC-070.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Engano pode ser pista de incidente, não autorização automática de emboscada; resolução por risco e confirmação do host permanece obrigatória.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Incidentes de viagem envolvendo informantes precisam causa, oportunidade e risco; culpa de agente duplo não é inferida de boato.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Promessa de informação sobre incidente não cria emboscada, resgate, entrega ou perseguição; efeitos dependem de risco, causalidade e presença.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Rumor de incidente em viagem não cria ataque confirmado. A avaliação de risco diferencia alegação, ocorrência e relato testemunhal.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Relatórios podem conter notícia de incidentes verificados, mas não criam incidente mecânico ao serem compartilhados. Divulgação de rota protegida exige risk gates.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Plano de viagem pode gerar hipótese de incidente, nunca ocorrência confirmada; classificação de risco e regras offscreen seguem vinculantes.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Incidente de viagem confirmado pode gerar revisão segura; rumor de incidente não equivale a desfecho e não autoriza emboscada adicional.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Incidente de viagem compete por participantes e recursos sem dupla resolução; aviso de urgência não anula gates de risco nem direitos de outro PC.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Deadlock com viagem e escolta pode produzir proposta de remarcação, mas não incidente violento fictício ou movimento host não confirmado.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Impacto de guerra/saque em rota DEC-096 pode propor mudança de risco, não forçar encontro, morte, batalha ou saque sem política e gates.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Aumento de risco por guerra DEC-096/C não dispara automaticamente assalto/morte; precisa templates e gates de risco DEC-070.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Risco rodoviário agregado DEC-097/C não dispara saques, morte ou combate sem regras e gates DEC-070.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Incidente de viagem não ganha resolução repetida por reentrada; comprovantes e risco governam passagem para área ativa.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Incidentes em viagem não editam livremente guardas, criaturas e scripts originais.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Incidentes de viagem não usam future branches de quests como precondições narrativas.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Regional simulation and materialization cannot treat ambiguous quest flags as facts. Protect quest-owned actors/objects and persistent NPC identities; semantic milestones need curated proof and do not grant spawn, despawn, cleanup, loot or irreversible effects without existing host gates. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **incidentes offscreen**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para incidentes de viagem não são implícitos no modelo de rumor, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para incidente offscreen exige origem factual, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Incidente de viagem pode impedir entrega; nunca provar culpa automaticamente. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Incidentes fora de cena não demonstram automaticamente má-fé contratual. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
