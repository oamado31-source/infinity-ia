# DEC-094 — Detecção de deadlocks, starvation, reservas órfãs e recuperação segura

**Discovery v9.0 · ADR-0089 · Opção C APROVADA SOMENTE COMO ARQUITETURA · NÃO IMPLEMENTADA**  
**94 testes T094-01..T094-94 CANDIDATOS, TODOS NÃO EXECUTADOS.** Nenhum lock de banco, adaptação EEex, manipulação de NPC, POC host+2 clientes ou gate de runtime foi testado.

## 1. Problema, objetivos e limites

Complementar a DEC-093 sem substituí-la: coordenar operações paralelas é diferente de recuperar falhas de progresso. A recuperação deve identificar ciclos reais e espera excessiva, distinguir travas lógicas revogáveis de ações físicas em voo e preservar consentimentos. Nenhum deadlock pode ser resolvido por um algoritmo que apenas apaga reservas sem considerar efeitos já despachados.

**Invariantes:** (a) fato/efeito confirmado é imutável; (b) revisão de reserva ≠ mutação BG2:EE; (c) lock expirado ≠ posse física livre; (d) incerteza do host não libera nem reexecuta; (e) nenhum PC recebe obrigação nova por fairness; (f) sigilo e ramo/ano DR filtrados antes de LLM; (g) operações independentes podem continuar.

## 2. Domínios físicos e confiança

```text
knowledge/periods/<ANO>-DR/             # obrigatório: cânone fisicamente separado DEC-060
  ...                                    # nunca registrar aqui wait-for, projetos ou identidades secretas

campaign-overlays/<campaign>/<branch>/  # camadas lógicas candidatas ainda NÃO implantadas
  plans/, operations/, reservations/      # DEC-091–093, autoria e autorizações
  wait-for-graph/                        # arestas, recursos, revisões, evidências
  fairness-and-progress/                 # métricas de espera sem segredos
  lease-epochs-and-fencing/              # autorizações por scheduler e CAS
  deadlock-recovery/                     # avaliação, proposta, aprovação, decisão
  uncertain-host-actions/                # inbox/outbox/receipt, sem retry cego
  checkpoint-reconciliation/             # DEC-053, branch, build, sessão, restore
  audits-redacted/                       # logs por destinatário/ACL
```

Os caminhos de overlay são um **esquema lógico a especificar**, não diretórios de runtime instalados. Lore canônico permanece obrigatório por ano DR (DEC-060–063), com referências pinadas por campanha e ramo.

## 3. Contratos de dados candidatos

```text
WaitForEdge {
  campaign_id, branch_id, graph_revision,
  waiter_operation_id, holder_operation_id?, resource_identity_id,
  claim_id, reservation_id?, plan_revision, resource_revision,
  wait_kind: AND|OR, alternatives_evidence_refs[],
  dr_time_window, checkpoint_ref, observed_at_service_monotonic,
  edge_status: ACTIVE|STALE|RELEASED|UNKNOWN, acl
}
ProgressAssessment {
  assessment_id, campaign_id, branch_id, graph_revision,
  operation_ids[], dependency_edges[], existing_alternatives[],
  observed_progress_receipts[], service_wait_age, world_dr_wait_interval?,
  classification: RUNNABLE|WAITING|SUSPECTED_CYCLE|CONFIRMED_DEADLOCK|
                  STARVATION_RISK|ORPHAN_SUSPECTED|UNKNOWN_HOST_EFFECT,
  confidence_basis_refs[], policy_revision, audit_view_ref
}
RecoveryProposal {
  recovery_id, assessment_id, graph_revision, plan_revision_refs[],
  requested_action: WAIT|RESCHEDULE|NEGOTIATE|ALTERNATIVE_RESOURCE|
                    RELEASE_REVOCABLE_LOGICAL_LEASE|REQUEST_RECONCILIATION|
                    REQUEST_REAPPROVAL|BLOCK,
  candidate_reservation_ids[], affected_owners[], consent_requirements[],
  expected_effects[], irreversibility_risk, policy_revision,
  state: PROPOSED|APPROVAL_PENDING|APPROVED|REJECTED|STALE,
  acl_view_ref, evidence_refs[], rationale_redacted
}
LeaseRevocabilityProof {
  reservation_id, resource_identity_id, lease_epoch, fence_token,
  resource_revision, state, no_dispatch_proof_refs[],
  no_consumption_proof_refs[], checkpoint_ref, host_session_ref,
  proof_state: VERIFIED_REVOCABLE|IN_FLIGHT|UNCERTAIN|NOT_REVOCABLE,
  checked_at_revision, proof_expiration
}
RecoveryDecision {
  recovery_id, recovery_proposal_revision, approving_authority_refs[],
  selected_action, affected_reservation_ids[], prior_lease_epochs[],
  new_fencing_epoch?, cas_compare_revision, idempotency_key,
  state: ACCEPTED|BLOCKED|QUARANTINED|RELEASED_LOGICALLY|
         REPLAN_REQUIRED|RECONCILIATION_REQUIRED|UNCERTAIN,
  journal_ref, checkpoint_ref, branch_epoch, host_receipt_refs[]
}
RecoveryJournalEntry {
  sequence_id, recovery_id, operation_id, resource_identity_id?,
  actor_identity_ref?, event_kind, state_before, state_after,
  causal_refs[], timestamp_service, world_time_dr?,
  idempotency_key, authorization_refs[], acl, audit_redacted_ref
}
```

As entidades, names, métricas e estados são **candidatos**, não API existente. A prova negativa de dispatch exige **evidência positiva confiável** (outbox/host/reconciliação), não inferência por falta de receipt. Relógio monotônico de worker vale somente dentro da continuidade de sua sessão.

## 4. Grafo de espera, alternativas e detecção determinística

- Nós: operações e recursos/titulares versionados por campanha, branch e janela DR; evitar grafos globais cruzando mundos.
- Arestas: operação espera recurso que está validamente reservado por outro titular; citar `resource_revision`, causa e ACL; confirmar que a reserva está de fato viva.
- Ciclos: detectar `strongly connected components` (Tarjan/Kosaraju como opções para SPECS) e ciclos próprios; **ciclo detectado não basta** para afirmar deadlock se existir alternativa admissível que progrida ou recurso compatível compartilhável.
- Para solicitações `AND`, as dependências precisam todas ser satisfeitas; para `OR`, basta alternativa admissível comprovada; alternativa inventada por LLM não vale.
- A classificação `CONFIRMED_DEADLOCK` exige ausência de caminho de progresso admissível nas condições avaliadas. Sem metadados completos, `SUSPECTED_CYCLE/UNKNOWN`, não sacrificar operação.
- Atualizar/remover arestas quando revisões e recursos mudam; snapshot antigo não permite liberar recurso novo.

**Pseudocódigo ilustrativo NÃO EXECUTÁVEL:**

```python
snapshot = consistent_snapshot(campaign_id, branch_id, checkpoint_ref)
claims = filter_valid_claims(snapshot, current_fencing_epoch)
graph = build_wait_for_graph(claims, verified_resource_constraints)
for component in stable_order(find_cycles_and_sccs(graph)):
    if not independently_blocked(component, verified_OR_alternatives):
        record('WAITING_WITH_ALTERNATIVE')
        continue
    assessment = record_deadlock_assessment(component, graph.revision)
    candidates = safe_recovery_candidates(assessment)  # somente HELD e comprovadamente não despachado
    if not candidates:
        quarantine_or_request_reconciliation(assessment)
        continue
    proposal = select_proportional_candidate_by_policy(candidates)
    request_affected_owner_approval_when_required(proposal)
    # só após aprovação e recheck: CAS+fencing no ledger; jamais presumir effect host
```

Funções acima não foram programadas. Este algoritmo não demonstra que BG2:EE suporta cancelamento, interrupção de script ou recurso transacional.

## 5. Máquina de estados de recuperação

```text
WAITING_RESOURCE / AGING_QUEUE
  ↓ snapshot do grafo/evidências
SUSPECTED_CYCLE | STARVATION_RISK | ORPHAN_SUSPECTED
  ├─ alternativas úteis ─> WAITING / REPLAN_PROPOSED
  ├─ dados insuficientes ─> UNKNOWN / QUARANTINED
  └─ impasse confirmado ─> RECOVERY_PROPOSED
                          ↓ ownership, revogabilidade, risco, ACL, consentimento
                     APPROVAL_PENDING / REJECTED
                          ↓ autorização + CAS + fence + ausência de dispatch comprovada
                     LOGICAL_LEASE_RELEASED
                          ↓ nova verificação e revisão de plano
                     REPLAN_REQUIRED -> READY_TO_ADMIT

DISPATCH_PENDING ambíguo / DISPATCHED / UNCERTAIN
   -> RECONCILIATION_REQUIRED -> HOST_RECEIPT_VERIFIED or BLOCKED_UNCERTAIN
```

Não há transição segura de `UNCERTAIN` diretamente para `RELEASED`, nem de `LOGICAL_LEASE_RELEASED` para reverter o BG2:EE. Host-confirmed effects não mudam por um update de banco interno.

## 6. Classificação da revogabilidade por etapa

| Estado de reserva | Ação do recovery | Evidência exigida |
|---|---|---|
| `REQUESTED` sem reserva | Retirar pedido quando autorizado, sem mexer em resource | Identidade/versão atual e prova de ausência de lease |
| `HELD` nunca despachado | Liberação lógica candidata com CAS/fencing | Prova positiva de não despacho, revogabilidade e autorização |
| `DISPATCH_PENDING` com entrega incerta | **QUARANTINE** | Reconciliar outbox/host antes de decidir |
| `DISPATCHED` | **QUARANTINE** | Receipt host ou prova robusta de não execução |
| `UNCERTAIN` | **BLOCK** e reconciliação | Não repetir/cancelar livremente |
| `CONSUMED_VERIFIED` | Não devolver item nem presença física | Somente compensação futura separada (DEC-095) |
| `RELEASE_PENDING` duplicado | Idempotência; um único commit | `recovery_id` + CAS/epoch |
| `RELEASED` | No-op para retry | Journal e mesma revisão de reserva |

## 7. Fairness e starvation

- Coletar indicadores de `service_wait_age`, quantidade de ultrapassagens, razão de admissão, períodos DR sem progresso e causa principal do bloqueio; os dois relógios não são intercambiáveis.
- Diferenciar **fila injustamente preterida** de pré-requisito impossibilitado, falta de consentimento ou recurso inexistente.
- Critérios estáveis: requisitos de segurança e ownership primeiro; depois compromissos legítimos, urgência comprovada, idade de fila/cotas, custo de replanejamento e desempate estável por ID. Futuros valores/limiares só após perfis reais de workload.
- Não tratar *aging* como permissão. Nenhum serviço ou jogador obtém o direito de suspender PCs, transferir itens, avançar cronologia ou executar HIGH por ter aguardado muito tempo.
- Monitorar e alertar starvation em vez de declarar uma garantia formal sem testes. Recuperação com progressão e eventos depende de disponibilidade real de recursos/host.

## 8. Falhas, restart e host

1. `lease_epoch` e `fence_token` impedem novos comandos de worker desatualizado, dentro de um ledger durável com CAS implementado futuramente.
2. A engine pode não expor suporte para fencing; até POC host+2 clientes, o middleware não assume cancelamento de ações tardias já enviadas.
3. O relógio monotônico reiniciado tem novo domínio; restaurar epoch, logs e checkpoints antes de julgar leases antigos.
4. Confirmar `host_session_id`, `build_id`, `checkpoint_ref`, `branch_id`, `world_time_dr`, `operation_revision`, receipts e outbox. Sem evidência, `UNCERTAIN`.
5. Restores/branch splits DEC-053/063 devem invalidar jobs stale, sem reaplicar consequências do futuro.
6. Conflitos de retomada não autorizam movimentação duplicada de NPC persistente DEC-066/069 nem mudança de itens DEC-051.
7. Logs filtrados: scheduler pode saber IDs privados para segurança mas respostas para NPCs e players revelam apenas informações permitidas; não registrar dossiê ou refúgio em texto aberto.

## 9. Integrações e limites de POCs

| Dependência | Integração |
|---|---|
| DEC-011/012 | Ação mecânica apenas tipada, autorizada e confirmada no host |
| DEC-022/053/054 | Tempo DR, checkpoint, recuperação e rollback de save distintos de deadline interno |
| DEC-027/034/041/045/046 | Gates de risco, cânone irreversível, titularidade e consentimento dos PCs |
| DEC-050/051/066/069 | Scripts/quest, itens, identidade persistente e posição não alterados por lease |
| DEC-056/059 | Recursos computacionais separados dos recursos do jogo, LLM opcional |
| DEC-060–063 | Cânone físico por ano DR, curadoria e Knowledge Pack pinado; sem misturar estado de operação |
| DEC-071/074 | Handoff de encontro e consequências causais com own receipt, sem duplicação |
| DEC-083–090 | Proteção de testemunhas, dossiês e informes sob ACL e minimização |
| DEC-091/092/093 | Planos, monitoramento e concorrência existentes somente como arquitetura; esta DEC detalha impasses |

**POCs futuras:** implementar sandbox determinístico de grafo/locks e testes de concorrência/restart com banco escolhido; depois bridge read-only BG2:EE, ações testadas isoladamente, reconciliação de crash e sessão host+dois clientes; classificar locks por classe de recurso e custo de recuperação. Nenhuma dessas POCs ocorreu.

## 10. Matriz de testes candidatos — TODOS NÃO EXECUTADOS

| ID | Área | Caso esperado | Execução |
|---|---|---|---|
| T094-01 | Grafo de espera e confirmação do impasse | Aguarda simples sem ciclo permanece WAITING, não DEADLOCK. | NÃO EXECUTADO |
| T094-02 | Grafo de espera e confirmação do impasse | Ciclo A↔B entre duas reservas incompatíveis é detectado. | NÃO EXECUTADO |
| T094-03 | Grafo de espera e confirmação do impasse | Ciclo A→B→C→A é detectado com versão imutável do grafo. | NÃO EXECUTADO |
| T094-04 | Grafo de espera e confirmação do impasse | Aresta obsoleta de lease REVOKED não gera falso impasse. | NÃO EXECUTADO |
| T094-05 | Grafo de espera e confirmação do impasse | Aresta de outro branch não integra o mesmo grafo. | NÃO EXECUTADO |
| T094-06 | Grafo de espera e confirmação do impasse | Uma operação esperando por si mesma gera diagnóstico contextual. | NÃO EXECUTADO |
| T094-07 | Grafo de espera e confirmação do impasse | Recurso alternativo comprovadamente livre evita classificação prematura de impasse. | NÃO EXECUTADO |
| T094-08 | Grafo de espera e confirmação do impasse | Alternativa apenas alegada por LLM não dissolve impasse confirmado. | NÃO EXECUTADO |
| T094-09 | Grafo de espera e confirmação do impasse | Arestas AND/OR são interpretadas corretamente antes de declarar bloqueio total. | NÃO EXECUTADO |
| T094-10 | Grafo de espera e confirmação do impasse | Ciclo confirmado não cancela ou libera recursos automaticamente. | NÃO EXECUTADO |
| T094-11 | Grafo de espera e confirmação do impasse | Concorrência entre detectores não produz duas resoluções conflitantes. | NÃO EXECUTADO |
| T094-12 | Grafo de espera e confirmação do impasse | Alteração de resource_revision força recomputar dependências. | NÃO EXECUTADO |
| T094-13 | Fairness, prioridade e starvation | Operação aguardando repetidamente recebe rastreio de antiguidade. | NÃO EXECUTADO |
| T094-14 | Fairness, prioridade e starvation | Fila envelhecida não ganha consentimento de PC inexistente. | NÃO EXECUTADO |
| T094-15 | Fairness, prioridade e starvation | Tarefa HIGH sem autorização permanece bloqueada apesar da espera. | NÃO EXECUTADO |
| T094-16 | Fairness, prioridade e starvation | Critério de desempate determinístico independe da ordem das chamadas da IA. | NÃO EXECUTADO |
| T094-17 | Fairness, prioridade e starvation | Operação urgente com prova pode subir na análise sem roubar reserva confirmada. | NÃO EXECUTADO |
| T094-18 | Fairness, prioridade e starvation | Urgência declarada apenas em rumor não preempta outra operação. | NÃO EXECUTADO |
| T094-19 | Fairness, prioridade e starvation | Tarefa independente progride enquanto o ciclo está em análise. | NÃO EXECUTADO |
| T094-20 | Fairness, prioridade e starvation | Uma fila com operações longas não impede indefinidamente todas as pequenas por política oculta. | NÃO EXECUTADO |
| T094-21 | Fairness, prioridade e starvation | Métrica de starvation usa tempo de serviço sem confundí-lo com DR. | NÃO EXECUTADO |
| T094-22 | Fairness, prioridade e starvation | Aging/quotas respeitam as preferências e fairness dos diferentes jogadores. | NÃO EXECUTADO |
| T094-23 | Fairness, prioridade e starvation | Pré-requisito indisponível não é classificado como starvation da fila. | NÃO EXECUTADO |
| T094-24 | Fairness, prioridade e starvation | Recursos CPU e NPC são tratados por arbitragens separadas. | NÃO EXECUTADO |
| T094-25 | Leases, expiração, orfandade e fencing | Reserva HELD comprovadamente não despachada pode ser candidata a revogação segura. | NÃO EXECUTADO |
| T094-26 | Leases, expiração, orfandade e fencing | Prazo expirado isolado não libera recurso mecânico. | NÃO EXECUTADO |
| T094-27 | Leases, expiração, orfandade e fencing | DISPATCH_PENDING com entrega ambígua fica QUARANTINED. | NÃO EXECUTADO |
| T094-28 | Leases, expiração, orfandade e fencing | DISPATCHED sem receipt não é liberada automaticamente. | NÃO EXECUTADO |
| T094-29 | Leases, expiração, orfandade e fencing | UNCERTAIN impede reatribuição do item/NPC. | NÃO EXECUTADO |
| T094-30 | Leases, expiração, orfandade e fencing | CONSUMED_VERIFIED não é tratado como lease inativo que devolve item. | NÃO EXECUTADO |
| T094-31 | Leases, expiração, orfandade e fencing | Token fencing antigo é rejeitado para nova reserva. | NÃO EXECUTADO |
| T094-32 | Leases, expiração, orfandade e fencing | Epoch do scheduler diferente invalida autorização de liberação antiga. | NÃO EXECUTADO |
| T094-33 | Leases, expiração, orfandade e fencing | Renovação de lease exige estado/revisão e autoridade atuais. | NÃO EXECUTADO |
| T094-34 | Leases, expiração, orfandade e fencing | Processo duplicado disputando lease produz apenas um vencedor via CAS candidato. | NÃO EXECUTADO |
| T094-35 | Leases, expiração, orfandade e fencing | Reserva órfã só é liberada com prova positiva de ausência de dispatch. | NÃO EXECUTADO |
| T094-36 | Leases, expiração, orfandade e fencing | Expiração de serviço não muda tempo ou presença narrativa DR. | NÃO EXECUTADO |
| T094-37 | Compensação inexistente, etapas e decisões | A liberação revoga só pretensão lógica futura, não gasto host-confirmed. | NÃO EXECUTADO |
| T094-38 | Compensação inexistente, etapas e decisões | Etapa concluída preserva efeitos após cancelamento do plano. | NÃO EXECUTADO |
| T094-39 | Compensação inexistente, etapas e decisões | Operação com NPC reservado não é automaticamente teleportada ou encerrada. | NÃO EXECUTADO |
| T094-40 | Compensação inexistente, etapas e decisões | Se há substituto real e autorizado, propor alternativa sem despachar. | NÃO EXECUTADO |
| T094-41 | Compensação inexistente, etapas e decisões | Replanejamento material exige nova revisão de plano. | NÃO EXECUTADO |
| T094-42 | Compensação inexistente, etapas e decisões | Reserva de outro jogador não pode ser unilateralmente preemptada. | NÃO EXECUTADO |
| T094-43 | Compensação inexistente, etapas e decisões | Recusa explícita do PC mantém operação aguardando ou falha segura. | NÃO EXECUTADO |
| T094-44 | Compensação inexistente, etapas e decisões | Titular de PC ausente não recebe consentimento presumido. | NÃO EXECUTADO |
| T094-45 | Compensação inexistente, etapas e decisões | Delegação tática não autoriza ceder inventário ou promessas de PC. | NÃO EXECUTADO |
| T094-46 | Compensação inexistente, etapas e decisões | Evento de risco HIGH permanece bloqueado apesar de deadlock. | NÃO EXECUTADO |
| T094-47 | Compensação inexistente, etapas e decisões | Quest original não é resetada por alteração do scheduler. | NÃO EXECUTADO |
| T094-48 | Compensação inexistente, etapas e decisões | Abortar operação não implica rollback de combatentes do BG2:EE. | NÃO EXECUTADO |
| T094-49 | Falhas, host, checkpoints e idempotência | Crash após reserva antes de dispatch reconhecidamente ausente permite revisão da lease. | NÃO EXECUTADO |
| T094-50 | Falhas, host, checkpoints e idempotência | Crash após emissão ambígua mantém UNCERTAIN até reconciliação. | NÃO EXECUTADO |
| T094-51 | Falhas, host, checkpoints e idempotência | Crash após receipt preserva resultado uma única vez. | NÃO EXECUTADO |
| T094-52 | Falhas, host, checkpoints e idempotência | Retry idêntico de recovery_id não duplica liberação. | NÃO EXECUTADO |
| T094-53 | Falhas, host, checkpoints e idempotência | Repetição de host receipt não duplica progresso. | NÃO EXECUTADO |
| T094-54 | Falhas, host, checkpoints e idempotência | Nova sessão host exige revalidação de capability. | NÃO EXECUTADO |
| T094-55 | Falhas, host, checkpoints e idempotência | Relógio monotônico reiniciado não prova que lease velho expirou sem risco. | NÃO EXECUTADO |
| T094-56 | Falhas, host, checkpoints e idempotência | Save antigo não herda reserva de branch futuro. | NÃO EXECUTADO |
| T094-57 | Falhas, host, checkpoints e idempotência | Restauro desautoriza worker do epoch mais recente que ficou stale. | NÃO EXECUTADO |
| T094-58 | Falhas, host, checkpoints e idempotência | Desconexão de cliente não implica abandono de ação confirmada. | NÃO EXECUTADO |
| T094-59 | Falhas, host, checkpoints e idempotência | Worker LAN sem resposta não faz liberação automática. | NÃO EXECUTADO |
| T094-60 | Falhas, host, checkpoints e idempotência | Falha do Action Gateway mantém bloqueio seguro e diagnóstico redigido. | NÃO EXECUTADO |
| T094-61 | Consentimento, ACL, sigilo e adversários | Relatório de conflito para jogador não expõe identidade de testemunha protegida. | NÃO EXECUTADO |
| T094-62 | Consentimento, ACL, sigilo e adversários | Resumo para NPC não revela dossiê secreto do outro grupo. | NÃO EXECUTADO |
| T094-63 | Consentimento, ACL, sigilo e adversários | Log de starvation redige localização e alvo de operação privada. | NÃO EXECUTADO |
| T094-64 | Consentimento, ACL, sigilo e adversários | LLM de sugestão não adquire poder de liberar leases. | NÃO EXECUTADO |
| T094-65 | Consentimento, ACL, sigilo e adversários | Operador LAN sem permissão não recebe resource metadata sensível. | NÃO EXECUTADO |
| T094-66 | Consentimento, ACL, sigilo e adversários | PC de outro jogador conserva autonomia sobre cancelamento. | NÃO EXECUTADO |
| T094-67 | Consentimento, ACL, sigilo e adversários | Rumor de risco não concede poder sobre recursos de facção rival. | NÃO EXECUTADO |
| T094-68 | Consentimento, ACL, sigilo e adversários | Pseudônimos DEC-076 não criam múltiplas reservas para o mesmo NPC persistente. | NÃO EXECUTADO |
| T094-69 | Consentimento, ACL, sigilo e adversários | Ocultação parcial de conflito preserva explicação útil sem reidentificar informante. | NÃO EXECUTADO |
| T094-70 | Consentimento, ACL, sigilo e adversários | Tentativa de forjar token de lease é recusada. | NÃO EXECUTADO |
| T094-71 | Geografia, tempo e recursos do mundo | Mesma região sem exclusividade não causa conflito automático. | NÃO EXECUTADO |
| T094-72 | Geografia, tempo e recursos do mundo | Dois intervalos DR não sobrepostos não conflitam. | NÃO EXECUTADO |
| T094-73 | Geografia, tempo e recursos do mundo | Um NPC em duas regiões incompatíveis tem conflito mesmo com aliases diferentes. | NÃO EXECUTADO |
| T094-74 | Geografia, tempo e recursos do mundo | Quantidade de ouro desconhecida bloqueia reserva duplicada. | NÃO EXECUTADO |
| T094-75 | Geografia, tempo e recursos do mundo | Transferência de carroça requer trajeto e disponibilidade real. | NÃO EXECUTADO |
| T094-76 | Geografia, tempo e recursos do mundo | Aguardar recurso externo offscreen não cria chegada instantânea. | NÃO EXECUTADO |
| T094-77 | Geografia, tempo e recursos do mundo | Ação física depende de receipt host, não de reserva interna. | NÃO EXECUTADO |
| T094-78 | Geografia, tempo e recursos do mundo | Capacidade desconhecida do engine mantém saída de bloqueio. | NÃO EXECUTADO |
| T094-79 | Geografia, tempo e recursos do mundo | Limite de capacidade de local é respeitado apenas com regra/registro verificável. | NÃO EXECUTADO |
| T094-80 | Geografia, tempo e recursos do mundo | Ressources computacionais DEC-056 não tornam itens de jogo disponíveis. | NÃO EXECUTADO |
| T094-81 | Observabilidade, progresso e reversibilidade | Alerta identifica ciclo e opções sem compartilhar segredo de grupo. | NÃO EXECUTADO |
| T094-82 | Observabilidade, progresso e reversibilidade | Diagnóstico distingue starvation de impossibilidade de recurso. | NÃO EXECUTADO |
| T094-83 | Observabilidade, progresso e reversibilidade | Motivo de CAS perdido produz revalidação, não loop de retry infinito. | NÃO EXECUTADO |
| T094-84 | Observabilidade, progresso e reversibilidade | Encaminhamento de alternativa mantém proveniência e autorizações. | NÃO EXECUTADO |
| T094-85 | Observabilidade, progresso e reversibilidade | Histórico de conflitos e propostas é append-only. | NÃO EXECUTADO |
| T094-86 | Observabilidade, progresso e reversibilidade | Decisão seleciona alternativa de menor impacto com desempate auditável. | NÃO EXECUTADO |
| T094-87 | Observabilidade, progresso e reversibilidade | Revogação de consentimento bloqueia novo dispatch do PC. | NÃO EXECUTADO |
| T094-88 | Observabilidade, progresso e reversibilidade | Nenhuma tentativa de recuperação cria eventos canônicos no knowledge/periods. | NÃO EXECUTADO |
| T094-89 | Observabilidade, progresso e reversibilidade | Knowledge Pack pinado preservado durante revisão de operação. | NÃO EXECUTADO |
| T094-90 | Observabilidade, progresso e reversibilidade | Reconciliação sem evidência preserva estado QUARANTINED. | NÃO EXECUTADO |
| T094-91 | Ataques e concorrência adversarial | Dois schedulers concorrentes não liberam simultaneamente o mesmo recurso. | NÃO EXECUTADO |
| T094-92 | Ataques e concorrência adversarial | Worker atrasado não consegue despachar após troca de fencing epoch. | NÃO EXECUTADO |
| T094-93 | Ataques e concorrência adversarial | Quarentena sob host offline não congela operações independentes. | NÃO EXECUTADO |
| T094-94 | Ataques e concorrência adversarial | POC host+dois clientes valida a ausência de liberação mecânica presumida. | NÃO EXECUTADO |

## 11. DEC-095 — próxima decisão em aberto

**Compensações seguras após falhas de operações parcialmente concluídas**. Não é a mesma coisa que liberar reservas mortas: investigar *sagas* e efeitos já confirmados que não podem ser revertidos por simples edição de ledger.

- **A:** rollback automático global de toda a operação e seus efeitos.
- **B:** a LLM escolhe livremente como desfazer ações/compensar.
- **C (recomendada):** compensações específicas, somente para efeitos com contramedida testada e autorizada, com journal, receipts do host, idempotência, consentimento e marcação de `NON_COMPENSABLE/UNCERTAIN` quando necessário, sem apagar fatos históricos.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

DEC-095: liberar lease não compensa ato host-confirmed. Saga específica pode propor novo reembolso ou rescisão, condicionado a recursos/consentimentos/receipts. DEC-096 proposta só desencadeia candidatos de contexto histórico, não libera locks.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

DEC-096/C não libera lease/recursos bloqueados; recuperação DEC-094 segue host receipt e autorização, independentemente da fase histórica.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Expiração de composição DEC-097/C não libera leases INCERTOS; recovery DEC-094 segue reconciliação.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Recuperar deadlock não apaga materializações confirmadas nem libera recursos físicos com comando em voo; reconcile antes de reutilizar.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Resolver deadlock não pode liberar recurso em host ou instância protegida com estado incerto.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Deadlocks não justificam consulta global de flags ou elevação de audience.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** DEC-101 interpretation is read-only, version-pinned and independent of gateway/host execution. A confirmed semantic milestone does not authorize actions or prove a command receipt; mod upgrades, checkpoint restore, revised mapping, epoch mismatch or contradictory states cause fail-closed reconciliation. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Reserva `UNCERTAIN` preservada também durante reconciliação de quest DEC-102. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **reservas incertas e fencing durante contenção**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para reserva de entrega UNCERTAIN exige reconciliação em deadlocks, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para reservas incertas não são liberadas sem reconciliação, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Vencimento não libera reservas vinculadas a comandos incertos. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Ciclos e starvation exigem recuperação proporcional, nunca preempção indevida. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Liberação de reserva órfã não significa devolver ou reatribuir bens já depositados. Host uncertain exige reconciliação.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
