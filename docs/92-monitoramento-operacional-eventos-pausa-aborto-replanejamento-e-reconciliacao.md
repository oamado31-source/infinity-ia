# DEC-092 — Monitoramento operacional, pausa, aborto e replanejamento seguro

**Discovery v8.8 · ADR-0087 · Opção C expressamente APROVADA como arquitetura · NÃO IMPLEMENTADA**  
**90 testes candidatos T092-01..T092-90, TODOS NÃO EXECUTADOS.** Sem POC de pausa do motor BG2:EE/EEex, cancelamento de comandos ou sincronização multiplayer host + dois clientes.

## 1. Objetivo e invariantes

- Operações derivadas de dossiês e planos DEC-089–091 devem reagir a **eventos confirmados** e não a improvisações de LLM.
- **Monitorar não é despachar**; **replanejar não é executar**; **pedir pausa não é confirmar pausa da engine**; **cancelar não é desfazer fatos já acontecidos**.
- Toda alteração material exige nova revisão do plano e revalidação de recursos, autoridade, conhecimento, consentimento e risco.
- Um comando in-flight/`UNCERTAIN` não pode ser reenviado ou presumido cancelado sem reconciliação com o host.
- O motor nativo e o cliente multiplayer não devem ser tratados como transação reversível.

## 2. Fronteiras de autoridade e armazenamento lógico candidato

```text
knowledge/periods/<ANO>-DR/                # PARTIÇÃO FÍSICA CANÔNICA aprovada DEC-060
  ...                                      # apenas lore curado com origem e ano válidos
campaign-overlays/<campaign>/<branch>/     # camadas lógicas candidatas, NÃO IMPLANTADAS
  dossiers/assessments                     # DEC-089/090
  operations/<operation_id>/
    baseline-plan-and-revisions/           # propostas e diffs imutáveis DEC-091
    monitored-events/                     # eventos confirmados e fonte
    impact-assessments/                    # precondições, mudança de risco/escopo
    pause-abort-requests/                  # intenções, não host receipt
    reapproval-and-consent/                # por ator/objetivo/revisão/tempo
    resource-leases-and-fences/            # reserva ≠ consumo
    dispatch-and-host-receipts/            # atos comprovados pelo host
    checkpoint-and-audit/                  # recuperação, idempotência e redaction
```

Caminhos do overlay acima são **ilustrativos**, dependem de SPECS. Nenhuma mudança de diretório físico da base canônica anual ou fusão de Knowledge Packs por época DR é autorizada.

## 3. Contratos candidatos (NÃO IMPLEMENTADOS)

```text
OperationInstance {
  campaign_id, branch_id, operation_id, plan_id, plan_revision,
  initiator_identity_id, participant_owner_refs[], approved_scope,
  approved_objective, approved_targets[], approved_sites[], window_dr,
  risk_policy_revision, approval_refs[], reservation_refs[],
  world_snapshot_ref, dossier_revision_refs[], knowledge_pack_binding,
  checkpoint_ref, resolution_epoch, host_session_ref, build_manifest_ref,
  state, last_confirmed_event_watermark, audit_ref
}
OperationTrigger {
  trigger_id, type: NEW_CONFIRMED_EVIDENCE|CONTRADICTION|TARGET_MOVED|
    PARTICIPANT_WITHDREW|NPC_UNAVAILABLE|RESOURCE_UNAVAILABLE|
    RISK_ESCALATED|APPROVAL_REVOKED|ACL_CHANGED|HOST_SESSION_CHANGED|
    CHECKPOINT_CHANGED|CAPABILITY_REVOKED|OPERATION_STAGE_CONFIRMED,
  cause_event_id, cause_evidence_refs[], observed_at_dr,
  ingestion_checkpoint_ref, source_revision, observer_acl,
  causal_parent_ids[], dedup_key, confirmation_state
}
OperationMonitorSnapshot {
  operation_id, plan_revision, checkpoint_ref, resolution_epoch,
  host_session_ref, known_world_fact_watermark, pending_dispatches[],
  confirmed_receipts[], reservations[], participant_consent_status[],
  resource_status[], risk_snapshot, stale_or_uncertain_flags[], version
}
OperationImpactAssessment {
  assessment_id, operation_id, based_on_revision, trigger_ids[],
  evidence_validity_diff[], scope_diff[], objective_diff[], target_diff[],
  participant_diff[], resource_diff[], temporal_diff[], acl_diff[],
  risk_diff, high_risk_aggregate, in_flight_dispatches[],
  decision: CONTINUE_WITHIN_SCOPE|PAUSE_NEW_DISPATCH|
    PROPOSE_REVISION|REQUEST_ABORT|BLOCK_UNCERTAIN,
  requires_new_approvals, expiry_dr?, policy_revision, audit_ref
}
OperationControlRequest {
  request_id, operation_id, requested_action: PAUSE|ABORT|RESUME,
  requested_by, authority_basis, plan_revision, checkpoint_ref,
  resolution_epoch, current_state, affected_dispatched_actions[],
  result: REQUESTED|ACK_ORCHESTRATOR|HOST_CONFIRMED_WHEN_SUPPORTED|
    REJECTED|UNCERTAIN, idempotency_key, receipt_ref?
}
PlanRevisionProposal {
  new_plan_revision, parent_plan_revision, cause_trigger_refs[],
  proposed_diff, evidence_refs[], accepted_by_pc_refs[],
  proposed_resource_reservations[], required_authority_refs[],
  plan_validation_ref?, risk_assessment_ref?, state:
    DRAFT|CONDITIONAL|BLOCKED|READY_FOR_REAPPROVAL|APPROVED|STALE
}
ReauthorizationRecord {
  operation_id, plan_revision, consenting_owner_identity_id?,
  controller_authorization_ref?, participant_choice,
  approval_scope, maximum_resource_commitment, approved_risk,
  expires_dr?, host_authority_ref?, validation_ref, signature_or_receipt
}
OperationReconciliation {
  operation_id, checkpoint_ref, host_session_ref, resolution_epoch,
  dispatched_idempotency_keys[], authoritative_host_receipts[],
  uncertain_actions[], confirmed_effects[], resource_fence_resolutions[],
  remaining_actions[], next_allowed_state, audit_ref
}
```

Os nomes são hipóteses de contrato: **nenhuma API**, endpoint de pausa da engine, estado remoto ou banco real foi demonstrado. Implementação deve especificar schemas, transações, limites de filas, replay e testes.

## 4. Máquina de estados e transições

```text
APPROVED/RESERVED (DEC-091)
     │ início autorizado e receipt adequado
     ▼
 RUNNING ──trigger confirmado─► REVIEW_REQUIRED
   │                               │
   │ recebida alteração irrelevante│ avaliação determinística do impacto
   │◄──────────── CONTINUE_WITHIN_SCOPE
   │                               ├── PAUSE_REQUESTED ──► PAUSED_ORCHESTRATION
   │                               │                         │
   │                               │                   REPLAN_PROPOSED
   │                               │                         ▼
   │                               │                   REAPPROVAL_REQUIRED
   │                               │                         ▼
   │                               │                     RESUME_READY
   │                               │                         │ revalidação final
   │◄───────────────────────────────┴─────────────────────────┘
   ├── ABORT_REQUESTED ──reconcile in-flight──► ABORTED_CONFIRMED
   ├── COMPLETE (todos outcomes verificados)
   ├── FAILED (falha comprovada, não confundir UNCERTAIN)
   └── UNCERTAIN/STALE (bloqueio e reconciliação antes de novo ato)
```

- `PAUSE_REQUESTED` é pedido; `PAUSED_ORCHESTRATION` significa parar **novos despachos do middleware**. **Não** equivale a pausar jogo, combate ou atores nativos.
- `ABORTED_CONFIRMED` significa que novos despachos foram impedidos e pendências avaliadas. Pode haver efeitos irreversíveis já confirmados antes do aborto.
- `RESUME_READY` requer autorizações e reservas atuais; a retomada só passa a `RUNNING` após gate. `UNCERTAIN` não é `FAILED`.

## 5. Detecção de mudanças materiais

| Trigger | Resposta segura padrão | O que exige nova aprovação |
|---|---|---|
| Nova pista não corroborada | Registrar hipótese e revisar validade das premissas sem mudar local automaticamente | Alteração de alvo, rota, atuação de PCs ou risco |
| Prova confirmada contradiz destino | Congelar novos despachos dependentes; sugerir opções | Mudança de local, objetivo e recursos |
| PC abandona a operação | Bloquear atos voluntários futuros desse PC, preservar o que já fez | Redistribuir funções a outros PCs exige seu aceite |
| NPC indisponível | Rever capacidade e presença; não inventar teletransporte | Substituto/recursos/objetivo/regras de risco |
| Resource lease expira | Bloquear consumo e revalidar ownership | Nova reserva ou compensação |
| Escalada para HIGH | **Default-deny** para novos despachos | Gate especial + consentimentos aplicáveis |
| Host desconecta/reinicia | `UNCERTAIN`, reconciliation | Retomar após host session, checkpoint e receipts consistentes |
| Revogação de ACL | Remover acesso futuro; bloquear publicação e despacho dependentes | Nova finalidade/novo destinatário requer autorização |
| Mudança de build/mod | Invalidar capability antiga | Nova prova técnica e aprovação de ação mecânica |
| Evento apenas cosmético | Atualizar status com audit; não disparar custo nem perda de consentimento | Nenhuma, se dentro do escopo aprovado |

Não existe percentual geral de confiança que autorize execução; os riscos e cada precondição prevalecem. Priorizar disparadores de consentimento/segurança em relação a otimizações.

## 6. Algoritmo determinístico candidato

```text
on_confirmed_event(event):
  verify_source_and_scope(event)
  if event.confirmation_state != CONFIRMED: record_as_claim_only(); return
  operations = subscriptions_matching(event, campaign, branch, time_dr)
  for op in operations:
    if op.checkpoint_invalid or op.branch_invalid: block_as_STALE(); continue
    if dedup(event, op): continue
    impact = evaluate_diff_deterministically(op.baseline_snapshot, event)
    if impact.has_revoked_consent or impact.is_high_risk or impact.stale_capability:
        block_new_dispatch(op)
    if impact.no_material_change and all_gates_still_valid:
        record_monitor_observation(); continue
    request_orchestrator_pause_for_new_actions(op)
    record_in_flight_UNCERTAIN_separately(op)
    propose_plan_revision_with_provenance(op, impact)  # LLM só sob demanda, após ACL
    require_validation_and_applicable_authorizations(op, new_plan_revision)
    reconcile_host_receipts_and_resource_fencing(op)
    resume_only_after_rechecks_and_host_gates(op)
```

Nenhum bloco concede à LLM poder de transmitir comandos. O monitor não usa tick de IA; a política DEC-056 define orçamento e fila. O Action Gateway DEC-012 continua único caminho de mutação mecânica.

## 7. Exemplo completo — missão do armazém

1. Jogadores autorizam `plan_revision=4`: observar Armazém Norte, dois PCs, observador NPC e uma janela de tempo DR, sem confisco/ataque.
2. O host confirma que uma parte da operação iniciou. Um `HostExecutionReceipt` confirma o deslocamento de determinado ator; movimento de outros permanece `UNKNOWN` quando a engine não expõe receipt.
3. Nova `DossierRevision` informa suspeita fundamentada de transferência para Armazém Sul. A hipótese pode precisar de nova prova; não é `WorldFact` automaticamente.
4. PC-A retira consentimento para seguir; novos atos voluntários de PC-A são bloqueados. PC-B mantém escolhas próprias, sem reautorizar a si mesmo destino novo.
5. `OperationImpactAssessment` indica mudança material no destino, no pessoal e nos recursos. Middleware entra em `PAUSE_REQUESTED` e deixa de despachar novos comandos dependentes. A simulação do BG2:EE pode continuar normalmente.
6. Planner propõe `plan_revision=5` com opções: confirmar a pista, observar outro armazém com consentimento, suspender ou cancelar. Nenhuma delas é realizada automaticamente.
7. Aprovações específicas, checagens de geografia, recursos, ACL, host session e capabilities são exigidas antes de `RESUME_READY` e do primeiro novo despacho.
8. Ações confirmadas do plano 4 permanecem históricas. Pendentes `UNCERTAIN` são reconciliadas e recursos com lease ativo não são liberados inadvertidamente.

## 8. Recursos e condições de corrida

- `Reservation` não é `Consumption`; recurso `UNCERTAIN` não volta ao pool automaticamente.
- Usar compare-and-swap por versão de plano, fencing token e idempotency key por ação; workers atrasados não podem aplicar alterações da revisão 4 após troca para revisão 5.
- Cancelamento tardio não causa duplicação nem apagamento de `HostExecutionReceipt` já publicado.
- Reconciliation percorre ações em voo e efeitos observados, não faz rollback global; consequências persistentes seguem DEC-073/074.
- A coordenação de planos concorrentes em **múltiplas operações** permanece tema **DEC-093**, sem assumir lock global único.

## 9. Privacidade e separação canônica

- `knowledge/periods/<ANO>-DR/` continua como diretório físico do lore; planos, versões e eventos da campanha ficam só em overlay privado de `campaign_id`/`branch_id`.
- Leituras de NPC dependem de informação efetivamente recebida DEC-029/074/090, não do ledger factual privado do host.
- Planos de proteção/rotas/testemunhas DEC-083–085 e operações falsas DEC-086 exigem ACL também em diffs, prompts, logs, índices, alertas e notificações de monitor.
- **Nenhum estado de pausa** deve ser usado para contornar consentimento individual DEC-041/045/046, nem operar o motor por script gerado espontaneamente.

## 10. Falhas, limites de POCs e implementação futura

- Offline primeiro: simulador determinístico de eventos, motor de impacto, máquinas de estado, revisões, gates, duplicatas e race conditions.
- POC BG2:EE limpa → EEex/bridge read-only, por build/manifest, depois Action Gateway permitido, observação host e dois clientes. Provar separadamente se existe pausa de motor viável sem corromper multiplayer; **até lá há apenas pausa lógica**.
- Testar falha de sessão, pausa com dispatch in-flight, duplicação de receipt, retorno de cliente, restore pré-revisão, mudança de branch, resources e leak de informações.
- Não declarar implementado recurso algum: estes são critérios de aceitação candidatos para SPECS futuras, não relatórios de teste.

## 11. Matriz de 90 testes candidatos — TODOS NÃO EXECUTADOS

| ID | Grupo | Expectativa verificável | Estado |
|---|---|---|---|
| T092-01 | Eventos e evidências | Somente ConfirmedWorldEvent com origem verificável dispara avaliação autoritativa. | NÃO EXECUTADO |
| T092-02 | Eventos e evidências | Rumor não corroborado não altera sozinho o destino autorizado. | NÃO EXECUTADO |
| T092-03 | Eventos e evidências | LLM não fabrica evento para provocar replanejamento. | NÃO EXECUTADO |
| T092-04 | Eventos e evidências | Evento duplicado causa uma avaliação de impacto, sem dois efeitos. | NÃO EXECUTADO |
| T092-05 | Eventos e evidências | Eventos fora de ordem são reconciliados pelo ledger e causalidade. | NÃO EXECUTADO |
| T092-06 | Eventos e evidências | Novas provas contraditórias alteram avaliação, mas não declaram WorldFact. | NÃO EXECUTADO |
| T092-07 | Eventos e evidências | Revisão do dossiê recebida após a janela temporal gera alerta STALE. | NÃO EXECUTADO |
| T092-08 | Eventos e evidências | Mudança de lugar com localização desconhecida bloqueia ação mecânica. | NÃO EXECUTADO |
| T092-09 | Eventos e evidências | Monitor recebe só acontecimentos aos quais seu escopo tem acesso. | NÃO EXECUTADO |
| T092-10 | Eventos e evidências | Evento posterior ao checkpoint restaurado não é aplicado ao passado. | NÃO EXECUTADO |
| T092-11 | Validação de mudanças | Alteração meramente cosmética pode continuar sob aprovação válida. | NÃO EXECUTADO |
| T092-12 | Validação de mudanças | Mudança de objetivo exige nova revisão e reautorização. | NÃO EXECUTADO |
| T092-13 | Validação de mudanças | Mudança de alvo exige nova revisão e gate. | NÃO EXECUTADO |
| T092-14 | Validação de mudanças | Mudança de região exige verificar tempo de viagem e capacidade. | NÃO EXECUTADO |
| T092-15 | Validação de mudanças | Mudança de janela DR invalida consentimentos temporalmente limitados. | NÃO EXECUTADO |
| T092-16 | Validação de mudanças | Escalada MEDIUM para HIGH bloqueia novos despachos sem aprovação. | NÃO EXECUTADO |
| T092-17 | Validação de mudanças | Sequência de LOW que produz impacto agregado HIGH exige gate. | NÃO EXECUTADO |
| T092-18 | Validação de mudanças | Alteração de ACL pode impedir distribuição do plano revisado. | NÃO EXECUTADO |
| T092-19 | Validação de mudanças | Mudança de build invalida capacidades previamente testadas. | NÃO EXECUTADO |
| T092-20 | Validação de mudanças | Evidência originalmente aceita vencida invalida premissas do plano. | NÃO EXECUTADO |
| T092-21 | Consentimento e co-op | Saída voluntária de PC impede novos despachos atribuídos a ele. | NÃO EXECUTADO |
| T092-22 | Consentimento e co-op | Retirada de um PC não cancela ações já confirmadas do restante da party. | NÃO EXECUTADO |
| T092-23 | Consentimento e co-op | Consentimento do host não substitui escolha do titular do PC. | NÃO EXECUTADO |
| T092-24 | Consentimento e co-op | Delegado não autoriza nova ação fora do escopo da delegação. | NÃO EXECUTADO |
| T092-25 | Consentimento e co-op | Personagem ausente não aceita replanejamento por silêncio. | NÃO EXECUTADO |
| T092-26 | Consentimento e co-op | Plano revisado não herda autorização da revisão anterior automaticamente. | NÃO EXECUTADO |
| T092-27 | Consentimento e co-op | Jogador pode rejeitar destino novo e manter seu PC fora da operação. | NÃO EXECUTADO |
| T092-28 | Consentimento e co-op | Facção NPC autônoma não gasta recursos de PCs sem autorização. | NÃO EXECUTADO |
| T092-29 | Consentimento e co-op | NPC pode recusar objetivo novo conforme valores e compromissos. | NÃO EXECUTADO |
| T092-30 | Consentimento e co-op | PC não recebe segredo de outro PC ao revisar plano compartilhado. | NÃO EXECUTADO |
| T092-31 | Pausa, aborto e retomada | PAUSE_REQUESTED interrompe novos despachos do orquestrador sem prometer pausa nativa. | NÃO EXECUTADO |
| T092-32 | Pausa, aborto e retomada | PAUSED_ORCHESTRATION não interrompe efeitos mecânicos já em andamento. | NÃO EXECUTADO |
| T092-33 | Pausa, aborto e retomada | PAUSE solicitado sem adapter testado não resulta em engine_paused=true. | NÃO EXECUTADO |
| T092-34 | Pausa, aborto e retomada | ABORT_REQUESTED não é ABORTED_CONFIRMED antes de reconciliar in-flight. | NÃO EXECUTADO |
| T092-35 | Pausa, aborto e retomada | Cancelamento depois de ataque confirmado não apaga o ataque. | NÃO EXECUTADO |
| T092-36 | Pausa, aborto e retomada | Retomada exige revalidar risco, consentimento, local e sessão do host. | NÃO EXECUTADO |
| T092-37 | Pausa, aborto e retomada | Retomada sem receipt necessário permanece UNCERTAIN. | NÃO EXECUTADO |
| T092-38 | Pausa, aborto e retomada | Idempotency key impede segunda execução de ação interrompida. | NÃO EXECUTADO |
| T092-39 | Pausa, aborto e retomada | Falta de confirmação de stop mecânico impede afirmar que engine parou. | NÃO EXECUTADO |
| T092-40 | Pausa, aborto e retomada | Plano integralmente concluído não aceita reativação por trigger atrasado. | NÃO EXECUTADO |
| T092-41 | Recursos e identidade | Pausa mantém reserva comprometida até reconciliar owner e lease. | NÃO EXECUTADO |
| T092-42 | Recursos e identidade | Abortar reserva livre confirma que recurso não foi consumido. | NÃO EXECUTADO |
| T092-43 | Recursos e identidade | Recurso em UNCERTAIN não pode ser reservado a outra operação. | NÃO EXECUTADO |
| T092-44 | Recursos e identidade | Fencing epoch antigo não libera reserva da época corrente. | NÃO EXECUTADO |
| T092-45 | Recursos e identidade | Mudança de NPC exige identidade persistente verificada DEC-066. | NÃO EXECUTADO |
| T092-46 | Recursos e identidade | Movimento narrativo não equivale a presença CRE no local. | NÃO EXECUTADO |
| T092-47 | Recursos e identidade | Mudança de localização exige rotas e cronologia DEC-069. | NÃO EXECUTADO |
| T092-48 | Recursos e identidade | Aborto de NPC fora de cena não o teletransporta para cena local. | NÃO EXECUTADO |
| T092-49 | Recursos e identidade | Risco de duplicação de ouro ou item é bloqueado por receipt host. | NÃO EXECUTADO |
| T092-50 | Recursos e identidade | Replanejamento de duas ações sobre mesmo item exclusivo detecta conflito. | NÃO EXECUTADO |
| T092-51 | Host, falhas e rede | Host restart invalida token de sessão usado para novos comandos. | NÃO EXECUTADO |
| T092-52 | Host, falhas e rede | Ack de dispatch sem receipt não cria WorldFact de execução. | NÃO EXECUTADO |
| T092-53 | Host, falhas e rede | Comando em timeout UNCERTAIN não é repetido às cegas. | NÃO EXECUTADO |
| T092-54 | Host, falhas e rede | Receipt posterior ao pedido de aborto ainda é reconciliado. | NÃO EXECUTADO |
| T092-55 | Host, falhas e rede | Reentrega de receipt idêntico não duplica efeito. | NÃO EXECUTADO |
| T092-56 | Host, falhas e rede | Dois clientes com vistas diferentes não podem aprovar ações de outro PC. | NÃO EXECUTADO |
| T092-57 | Host, falhas e rede | Reconexão LAN não restabelece autorizações revogadas. | NÃO EXECUTADO |
| T092-58 | Host, falhas e rede | Plano carregado de outro branch é marcado STALE. | NÃO EXECUTADO |
| T092-59 | Host, falhas e rede | Restore pré-operação não importa consequências futuras. | NÃO EXECUTADO |
| T092-60 | Host, falhas e rede | Capability ausente bloqueia movimento/pausa/scripts no motor. | NÃO EXECUTADO |
| T092-61 | Privacidade e informação | Mudança de refúgio não expõe localização aos perseguidores automaticamente. | NÃO EXECUTADO |
| T092-62 | Privacidade e informação | Plano revisado enviado ao LLM não contém nomes protegidos não necessários. | NÃO EXECUTADO |
| T092-63 | Privacidade e informação | Dossiê compartilhado com aliado é filtrado pela DisclosureView correta. | NÃO EXECUTADO |
| T092-64 | Privacidade e informação | Log de impacto não revela pseudônimo de fonte a público proibido. | NÃO EXECUTADO |
| T092-65 | Privacidade e informação | Worker LAN revogado não recebe próximo estado confidencial. | NÃO EXECUTADO |
| T092-66 | Privacidade e informação | Atualização enviada por mensageiro não é conhecida antes da entrega. | NÃO EXECUTADO |
| T092-67 | Privacidade e informação | NPC não usa fatos privados do host para antecipar mudança de lugar. | NÃO EXECUTADO |
| T092-68 | Privacidade e informação | Rumor proposital DEC-086 permanece PlantedClaim, não WorldFact. | NÃO EXECUTADO |
| T092-69 | Privacidade e informação | Alteração em índice/cache respeita revisão, ACL e checkpoint. | NÃO EXECUTADO |
| T092-70 | Privacidade e informação | Snapshot do monitor não inclui informações de campanha diversa. | NÃO EXECUTADO |
| T092-71 | Escalas, desempenho e recuperação | Cem eventos equivalentes são coalescidos sem remover causas distintas. | NÃO EXECUTADO |
| T092-72 | Escalas, desempenho e recuperação | Monitor não faz chamada LLM por frame ou tick. | NÃO EXECUTADO |
| T092-73 | Escalas, desempenho e recuperação | Pressão de fila DEC-056 não autoriza ignorar gates HIGH. | NÃO EXECUTADO |
| T092-74 | Escalas, desempenho e recuperação | Aprovação anterior expirada não é revalidada por fila atrasada. | NÃO EXECUTADO |
| T092-75 | Escalas, desempenho e recuperação | Falha do supervisor não altera outcome CONFIRMED previamente gravado. | NÃO EXECUTADO |
| T092-76 | Escalas, desempenho e recuperação | Duas avaliações simultâneas de mesmo plano respeitam CAS por revision. | NÃO EXECUTADO |
| T092-77 | Escalas, desempenho e recuperação | Eventos simultâneos de risco e evidência priorizam segurança. | NÃO EXECUTADO |
| T092-78 | Escalas, desempenho e recuperação | Backpressure descarta somente propostas duplicadas, não receipts críticos. | NÃO EXECUTADO |
| T092-79 | Escalas, desempenho e recuperação | Relatório de status reflete PAUSE_REQUESTED versus PAUSED_ORCHESTRATION. | NÃO EXECUTADO |
| T092-80 | Escalas, desempenho e recuperação | Retomada após restore reconcilia resource lease e host session. | NÃO EXECUTADO |
| T092-81 | Integração e decisões históricas | DEC-060 mantém pastas canônicas fisicamente separadas por ano DR. | NÃO EXECUTADO |
| T092-82 | Integração e decisões históricas | Planos dinâmicos permanecem em overlay privado por campanha e branch. | NÃO EXECUTADO |
| T092-83 | Integração e decisões históricas | KPack fixado não muda silenciosamente durante replanejamento. | NÃO EXECUTADO |
| T092-84 | Integração e decisões históricas | DEC-077 evidência SUSPECTED não se converte em fato por nova revisão. | NÃO EXECUTADO |
| T092-85 | Integração e decisões históricas | DEC-080 ordem revogada invalida coerção proposta. | NÃO EXECUTADO |
| T092-86 | Integração e decisões históricas | DEC-084 proteção de testemunha não garante invulnerabilidade. | NÃO EXECUTADO |
| T092-87 | Integração e decisões históricas | DEC-087 NPC não é obrigado a trair por meta-objetivo de plano. | NÃO EXECUTADO |
| T092-88 | Integração e decisões históricas | DEC-089 fontes dependentes não são somadas como provas independentes. | NÃO EXECUTADO |
| T092-89 | Integração e decisões históricas | DEC-090 dossiê transmitido mas não recebido não é conhecido pelo NPC. | NÃO EXECUTADO |
| T092-90 | Integração e decisões históricas | POC BG2:EE/EEex host+dois clientes necessária antes de habilitar pausa mecânica. | NÃO EXECUTADO |

## 12. Dependências e próxima decisão

- DEC-091/C (planos/validação/autorizações/recursos/dispatch/receipt); DEC-089/090 (evidências e dossiês, transmissão por destinatário).
- DEC-011/012 (host e gateway); DEC-019/027/028/034/041/045/046 (consentimento, privacidade, risco); DEC-022/053/054 (tempo/checkpoints/backups); DEC-056–060 (scheduler/LAN/LLM/cânone); DEC-066–074 (presença, deslocamento, efeitos); DEC-080/083–088 (revogação, segredos, engano, lealdades).
- **DEC-060–091 permanecem intactas**, com 86 ADRs predecessores byte a byte preservados; nenhuma capacidade mecânica foi comprovada.
- **DEC-093 ABERTA:** coordenação de operações simultâneas sobre objetivos e recursos compartilhados. A) serializar todas, B) LLM arbitra livremente, **C) scheduler determinístico de conflitos por recursos/presença/tempo, fairness e risco, reaprovação específica e confirmações do host**.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

DEC-092 avalia mudança material dentro de uma operação; DEC-093 arbitra disputas ENTRE operações por recursos, tempo e objetivos, sem transferir compromissos ou liberar ação UNCERTAIN.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

DEC-094 detalha que pausa lógica/cancelamento de futuros comandos não desfaz ações host-confirmed e não libera lease in-flight; recuperação exige prova positiva e consentimento.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

DEC-095 Saga registra efeitos parciais; DEC-096 proposta: mudança de fase histórica pode invalidar plano e pedir replanejamento, nunca modificar missões automaticamente.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Mudança de fase histórica DEC-096/C pode invalidar plano DEC-092; novas ações exigem revalidação, sem abortar ato já despachado.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Mudança de janela/decay DEC-097/C pode invalidar plano; exige revalidação DEC-092 antes de ato novo.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Após evento confirmado, replanejamento usa revisão coerente de região; reentrada não retoma comandos `UNCERTAIN` cegamente.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Replanejamento por evento não autoriza alterar entidades nativas ou recuperar campo sem licença.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Mudanças de planejamento por observação exigem revalidação, sem cancelar quest script nativo.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** DEC-101 interpretation is read-only, version-pinned and independent of gateway/host execution. A confirmed semantic milestone does not authorize actions or prove a command receipt; mod upgrades, checkpoint restore, revised mapping, epoch mismatch or contradictory states cause fail-closed reconciliation. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Rebase DEC-102 não valida automaticamente continuação de operação bloqueada. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **pausa futura e atualização do plano**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para replanejamento só após fato comprovado e gates próprios, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para replanejamento somente com novas autorizações, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Mudanças materiais exigem revalidação de prazos/consentimentos. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Replanejamento exige nova validação se impactar recursos ou termos. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
