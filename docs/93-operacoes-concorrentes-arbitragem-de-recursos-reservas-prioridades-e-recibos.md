# DEC-093 — Operações concorrentes, arbitragem de recursos e justiça cooperativa

**Infinity AI Discovery v8.9 · ADR-0088 · Opção C APROVADA somente em arquitetura · NÃO IMPLEMENTADA**  
**92 testes candidatos T093-01..T093-92, TODOS NÃO EXECUTADOS.** Sem prova de transação distribuída, reserva atômica real, middleware operacional, EEex bridge ou host + dois clientes.

## 1. Escopo e não objetivos

- Permitir operações simultâneas com independência real de recursos e condições causais.
- Impedir reservas incompatíveis do mesmo NPC/item/veículo/orçamento/janela.
- Separar prioridades de CPU/LLM DEC-056 de prioridades da operação, com critérios previsíveis e proteção da agência PC.
- Permitir negociação, substituição ou adiamento, nunca transferir automaticamente escolhas do jogador.
- Reconciliar leases, ações em voo e receipts após falhas, restore, branch ou build diferente.
- **Não** implementar/garantir: host multiplayer, pausa da engine, pathfinding, CAS em banco escolhido, atomização middleware↔BG2:EE, locks nativos de inventário, teleporte, presença física remota ou preempção nativa.

## 2. Fronteiras de dados e autoridade

```text
knowledge/periods/<ANO>-DR/                   # cânone curado, fisicamente particionado DEC-060
  ...                                         # nunca armazenar escala de NPC/segredo de operação aqui

campaign-overlays/<campaign>/<branch>/        # DOMÍNIOS LÓGICOS CANDIDATOS; não implantados
  dossiers/, operational-plans/               # DEC-089–092, ACL e revisões
  operations/<operation_id>/                  # propostas, autorização, execução, receipts
  resource-catalog/                           # identidades persistentes e limites verificáveis
  resource-allocations/                       # janela DR, exclusividade, quantidades, titular
  reservation-ledger/                         # lease, CAS, epoch/fencing, idempotência
  operation-dependencies/                     # interseções, precedência e wait-for edges
  concurrency-decisions/                      # tie-break, fairness, bloqueios, propostas
  dispatch-ledger/                            # gateway DEC-012, situação in-flight
  host-receipts/                              # comprovação mecânica DEC-011
  checkpoint-reconciliation/                  # DEC-053/054, branch e sessão
  audit-redacted/                             # DEC-055, sem segredos de NPC/PC
```

O domínio e estrutura física final serão decididos na SPECS. `knowledge/periods/<ANO>-DR/` é **obrigatório como separação física canônica**, não um exemplo opcional. Nenhum segredo de dossiê ou operações deve ser publicado nele. Os jogadores e NPCs só conhecem recursos/fatos de acordo com ACL e tempo DR, não pela existência de um lock interno.

## 3. Esquemas candidatos (NÃO IMPLEMENTADOS)

```text
OperationConcurrencyRequest {
  request_id, operation_id, plan_revision, campaign_id, branch_id,
  initiator_id, owner_and_consent_refs[], priority_context,
  requested_resource_refs[], time_window_dr, location_constraints[],
  dependency_operation_ids[], mutually_exclusive_objectives[],
  knowledge_pack_binding, world_snapshot_ref, host_session_ref,
  checkpoint_ref, resolution_epoch, evidence_refs[], risk_label,
  state: PROPOSED|EVALUATING|ADMITTED|BLOCKED|STALE
}
ResourceDescriptor {
  resource_identity_id, resource_kind: NPC|PC|ITEM|CURRENCY|TRANSPORT|
    SERVICE|SITE_CAPACITY|TIME_SLOT|MIDDLEWARE_COMPUTE,
  verified_owner_id?, campaign_id, branch_id, presence_evidence_ref?,
  quantity_available_or_UNKNOWN, exclusivity_class, compatibility_rule_ref,
  reservation_policy_rev, capability_manifest_ref?, revision
}
ResourceClaim {
  operation_id, plan_revision, resource_identity_id, amount,
  world_interval_dr, exclusivity_mode: EXCLUSIVE|SHARED_IF_PERMITTED,
  usage_intent, authority_ref, owner_consent_ref?, claim_revision
}
ReservationLease {
  reservation_id, operation_id, plan_revision, resource_identity_id,
  campaign_id, branch_id, world_interval_dr, quantity,
  fence_token, lease_epoch, resource_revision_before_after,
  lease_deadline_monotonic, held_by_scheduler_instance,
  state: REQUESTED|HELD|DISPATCH_PENDING|COMMIT_IN_FLIGHT|
         CONSUMED_VERIFIED|RELEASE_PENDING|RELEASED|UNCERTAIN|STALE,
  approval_refs[], host_receipt_ref?, idempotency_key
}
ConflictAssessment {
  conflict_id, operation_refs[], resource_refs[], related_claims[],
  conflict_kind: EXCLUSIVE_RESOURCE|QUANTITY|TEMPORAL|GEOGRAPHIC|
    OWNERSHIP|CONSENT|OBJECTIVE|UNCERTAIN_DISPATCH|UNKNOWN_CAPABILITY,
  evidence_refs[], world_time_dr, risk_aggregate, acl_view_ref,
  actionable_alternatives[], blocking_reasons[], policy_revision
}
ArbitrationDecision {
  decision_id, operation_revision_refs[], conflict_assessment_refs[],
  queue_wait_age_metrics[], verified_urgency_evidence_refs[],
  fairness_tiebreak_key, previously_committed_reservation_refs[],
  decision: ADMIT|DEFER|PROPOSE_REPLAN|REQUEST_REAPPROVAL|
            REJECT|BLOCK_UNCERTAIN,
  rationale_redacted, required_approvers[], scheduler_revision,
  monotonic_decision_index, audit_ref
}
OperationDependencyEdge {
  waiter_operation_id, holder_operation_id, resource_identity_id,
  cause_claim_ref, expires_or_unknown, edge_state,
  checkpoint_ref, wait_for_graph_revision
}
ConcurrencyReconciliation {
  campaign_id, branch_id, checkpoint_ref, host_session_ref,
  resolution_epoch, resource_catalog_revision, active_lease_epochs[],
  dispatched_actions[], host_receipts[], uncertain_actions[],
  stale_claims[], release_eligible_claims[], unresolved_wait_cycles[],
  reconciliation_result: READY|BLOCKED|UNCERTAIN|STALE
}
```

Estes contratos são **hipóteses de design**. `lease_deadline_monotonic` determina validade **interna** de lease; não é prazo DR de ficção, confirmação de disponibilidade do ator, ou finalização de ação do BG2:EE. Para o mesmo ator persistente, `resource_identity_id` se baseia em DEC-066, nunca em aliases DEC-076.

## 4. Máquina de estados e handshakes candidatos

```text
PROPOSED
  ↓ validação de evidência/autoridade/recursos, sem mutação
EVALUATING
  ├─ conflitos/UNKNOWN ──> BLOCKED / WAITING_RESOURCE
  │                            └─ alteração de contexto ──> REVALIDATE
  ↓ aquisição lógica CAS+fencing e aprovação relevante
HELD_RESERVATION
  ↓ recheck: revisão, consentimento, presença, capacidade, sessão host
READY_TO_DISPATCH
  ↓ gateway tipado, receipt ainda pendente
DISPATCHED / UNCERTAIN
  ├─ receipt host confirmado ──> CONSUMED_VERIFIED / STAGE_CONFIRMED
  └─ sessão/receipt incerto ──> RECONCILIATION_REQUIRED (sem liberação)
  ↓ etapas finais e ausência de atos in-flight
RELEASE_ELIGIBLE ──> RELEASED
```

O protocolo tem **duas fronteiras não atômicas**: (1) ledger interno de reservas; (2) ação no motor. Sem transação distribuída provada, a ponte entre elas é o idempotency key + recibo + reconciliação. Adquirir lease não equivale à ação física. Se a engine não oferecer probes de dado necessário, o workflow bloqueia a etapa correspondente.

## 5. Algoritmo determinístico de admissão (pseudocódigo candidato)

```python
for requested_operation in stable_order(ready_operations):
    assert same_campaign_branch_epoch(requested_operation)
    if not authorized_at_current_revision(requested_operation):
        block('NO_AUTHORITY')
        continue
    observed = resolve_resources_with_evidence(requested_operation)
    if observed.has_unknown_or_unverified_ownership:
        block('UNKNOWN_RESOURCE')
        continue
    conflicts = detect_actual_overlap_and_incompatibility(observed, live_claims)
    if conflicts:
        emit_redacted_conflict_and_allowed_alternatives(conflicts)
        enqueue_wait_without_preempting_committed_effects(requested_operation)
        continue
    if not acquire_atomic_lease_with_fence(observed, expected_revisions):
        block('RACE_LOST_REVALIDATE')
        continue
    assert recheck_authority_and_host_session_before_dispatch(requested_operation)
    propose_typed_action_gateway_request(requested_operation)  # NÃO significa executar
```

O exemplo **não é código funcional**. `stable_order`, CAS/locks, registros e consultas são requisitos a especificar, não APIs existentes. A aquisição atômica de reservas internas não concede atomização da engine; auditoria verifica todos os eventos de aceitação/recusa.

## 6. Matriz de compatibilidade por recurso

| Recurso | Regra de conflito candidata | Verificação e cautela |
|---|---|---|
| NPC persistente singular | Ocupação mutuamente exclusiva em janelas DR sobrepostas | Identidade DEC-066, itinerário DEC-069 e receipt host; não duplicar CRE |
| PC titular ou delegado | Sobreposição de atos incompatíveis/sem consentimento | Autonomia DEC-041/045/046, nunca consumir sua ação compulsoriamente |
| Item único | Ownership e quantidade confirmados; item não alocado duas vezes | Inventário/quest/script DEC-050/051, suporte build/gateway |
| Ouro/matéria fungível | Somatório de reservas ≤ saldo verificado por conta e autoridade | Reservar não gasta; engine confirma gasto se aplicável |
| Transporte/montaria/veículo | Janela, local, capacidade e trajeto real disponíveis | DEC-069/070; não transportar de imediato por texto |
| Serviço de NPC/facção | Contrato, custo, quota, carga, aceitação e prioridade | DEC-031–033/088, sem obrigação automática |
| Local/área/slot | Proibição de sobreposição **somente** se existir capacidade física/risco comprovados | Compartilhar região ≠ conflito automático |
| CPU/RAM/LLM | Limites computacionais separados das reservas ficcionais | DEC-056/059, não cria direito sobre PC/item |

## 7. Prioridade, fairness e conflito cooperativo

1. Primeiro: bloquear violação de consentimento, host, ACL, risco, checkpoint e ação in-flight incerta.
2. Depois: preservar titularidade e compromissos confirmados; admitir tarefas independentes paralelamente.
3. Comparar urgência **sustentada por eventos** e risco; nunca permitir que score da LLM ou rumor isolado vire autoridade.
4. Aplicar antiguidade de espera/cotas e desempate reprodutível para evitar favorecer sempre um grupo de PCs ou uma facção. Ageing não sobrepõe direitos nem transforma LOW em HIGH autorizado.
5. Pedir negociação/replanejamento aos responsáveis quando houver mudança material; ninguém recebe controle sobre personagem ou item de outro sem autorização.
6. `P0–P4` DEC-056 são prioridade de processamento **de software**, não direito de sequestro de capacidade física, sanção ou de sobrepor os jogadores.
7. Se um ciclo de espera for detectado, bloquear nova aquisição de recursos e registrar impasse; a política de **resolução de deadlock/starvation/preempção emergencial** fica aberta como DEC-094.

**Caso:** operação A usa guarda escolta às 22h, B pede o mesmo guarda às 23h (overlap) e C investiga por conta própria. Admitir C; manter A se lease válida; bloquear B e sugerir outro guarda ou adiar, sem retirar recursos de PC ou forçar guardas a trocar de posição. Se A já enviou ação ao host, não liberar por expiração de lease sem receipt.

## 8. Recuperação, idempotência, incidentes e segurança

| Incidente | Comportamento seguro |
|---|---|
| Dois schedulers pedem o mesmo recurso | Só um CAS/fencing vence, outro revalida |
| Worker com token velho retorna | Rejeitar novas mutações e manter trilha de auditoria |
| Lease interna expira durante ação `DISPATCHED` | `UNCERTAIN`: não reatribuir nem repetir até receipt/reconciliação |
| PC retira consentimento | Bloquear novos despachos em seu nome; preservação do realizado |
| Prioridade HIGH sem autorização | Bloquear; urgência não cria consentimento |
| Host desconecta após despacho | Reconciliar sessão/receipt, não inferir conclusão |
| Save/branch/Knowledge Pack muda | Invalidar/fence leases e jobs obsoletos; respeitar DEC-053/063 |
| Duas operações aguardam recursos mutuamente | Detectar ciclo e alertar, sem cancelamento cego (DEC-094 aberta) |
| Fila cresce em alta carga | Backpressure e reduzir trabalho opcional DEC-056, preservar P0 de segurança |
| Log expõe nome de testemunha/refúgio | Filtrar por ACL e usar identificadores neutros; não exibir segredos a jogadores/LLM |

## 9. Observabilidade e limites de implementação

Métricas candidatas: operações ativas/admitidas/esperando; conflitos por tipo; taxa de CAS perdido; idade máxima de fila por categoria; tokens obsoletos; quantidade de ações `UNCERTAIN`; reconciliações pendentes; leases órfãs; exposição indevida de ACL (zero); tempo de decisão do scheduler e custo de CPU sem prejudicar BG2:EE. Não estimar metas de latência antes de benchmark. Todos os testes são sintéticos até haver POC com build limpa BG2:EE, depois EEex, gateway read-only e só posteriormente host+2 clientes.

## 10. Matriz de 92 testes candidatos — TODOS NÃO EXECUTADOS

Cada ID descreve o comportamento **esperado** em uma futura fixture; não é resultado observacional.

| ID | Área | Cenário e resultado esperado | Estado |
|---|---|---|---|
| T093-01 | Conflitos e identidades | Duas operações usam o mesmo NPC singular na mesma janela incompatível: somente uma reserva válida. | NÃO EXECUTADO |
| T093-02 | Conflitos e identidades | Operações usando NPCs diferentes e horários independentes progridem simultaneamente. | NÃO EXECUTADO |
| T093-03 | Conflitos e identidades | Mesmo NPC com dois pseudônimos não recebe duas reservas concorrentes. | NÃO EXECUTADO |
| T093-04 | Conflitos e identidades | Dois NPCs homônimos mantêm identidades e agendas independentes. | NÃO EXECUTADO |
| T093-05 | Conflitos e identidades | Identidade lógica AMBIGUOUS impede exclusividade falsa ou spawn. | NÃO EXECUTADO |
| T093-06 | Conflitos e identidades | Duas operações na mesma região sem exclusão física não são bloqueadas automaticamente. | NÃO EXECUTADO |
| T093-07 | Conflitos e identidades | Operações com objetivos relacionados mas não excludentes podem coexistir. | NÃO EXECUTADO |
| T093-08 | Conflitos e identidades | Objetivos mutuamente contraditórios geram conflito explícito, não efeito simultâneo. | NÃO EXECUTADO |
| T093-09 | Conflitos e identidades | NPC com localização/horário não observável mantém disponibilidade UNKNOWN. | NÃO EXECUTADO |
| T093-10 | Conflitos e identidades | Overlap de janelas DR no mesmo recurso singular é detectado na borda do intervalo. | NÃO EXECUTADO |
| T093-11 | Conflitos e identidades | Janelas DR sem interseção podem ser reservadas sem conflitar. | NÃO EXECUTADO |
| T093-12 | Conflitos e identidades | Uma instância CRE reutilizada não prova que houve duplicação de ator persistente. | NÃO EXECUTADO |
| T093-13 | Reservas, leases e fencing | Reserva lógica não altera HP, ouro, inventário, posição ou missão. | NÃO EXECUTADO |
| T093-14 | Reservas, leases e fencing | Reserva concorrente CAS permite um vencedor e uma rejeição rastreável. | NÃO EXECUTADO |
| T093-15 | Reservas, leases e fencing | Fencing token obsoleto é rejeitado após troca de titular da reserva. | NÃO EXECUTADO |
| T093-16 | Reservas, leases e fencing | Lease expirada rejeita novo despacho com epoch antigo. | NÃO EXECUTADO |
| T093-17 | Reservas, leases e fencing | TTL monotônico do scheduler não altera relógio DR do mundo. | NÃO EXECUTADO |
| T093-18 | Reservas, leases e fencing | Expiração de lease não prova fim de deslocamento de NPC. | NÃO EXECUTADO |
| T093-19 | Reservas, leases e fencing | Um recurso divisível não pode ser reservado acima da quantidade disponível comprovada. | NÃO EXECUTADO |
| T093-20 | Reservas, leases e fencing | Dois consumos prometidos do mesmo item singular são bloqueados antes da engine. | NÃO EXECUTADO |
| T093-21 | Reservas, leases e fencing | Moeda fungível exige conta/recurso fonte e saldo comprovado antes da reserva. | NÃO EXECUTADO |
| T093-22 | Reservas, leases e fencing | Reserva compartilhável só é admitida quando o tipo de recurso explicitamente permite. | NÃO EXECUTADO |
| T093-23 | Reservas, leases e fencing | Revisão de plano invalida reserva que não é compatível com a revisão nova. | NÃO EXECUTADO |
| T093-24 | Reservas, leases e fencing | Conflitos de autorização impedem acúmulo de recurso de outro dono. | NÃO EXECUTADO |
| T093-25 | Prioridades, fairness e conflitos | Prioridade P0 computacional DEC-056 não confere controle sobre NPC ou PC. | NÃO EXECUTADO |
| T093-26 | Prioridades, fairness e conflitos | Urgência sem evidência não cancela automaticamente compromisso prévio. | NÃO EXECUTADO |
| T093-27 | Prioridades, fairness e conflitos | Urgência corroborada pode alterar ordem de avaliação, não consentimento. | NÃO EXECUTADO |
| T093-28 | Prioridades, fairness e conflitos | Duas propostas equivalentes seguem tie-break determinístico e auditável. | NÃO EXECUTADO |
| T093-29 | Prioridades, fairness e conflitos | Aging de fila não autoriza HIGH nem altera personagem de jogador. | NÃO EXECUTADO |
| T093-30 | Prioridades, fairness e conflitos | Múltiplas solicitações do mesmo grupo não monopolizam permanentemente o árbitro. | NÃO EXECUTADO |
| T093-31 | Prioridades, fairness e conflitos | Operação de segurança não recebe recurso pessoal sem permissão. | NÃO EXECUTADO |
| T093-32 | Prioridades, fairness e conflitos | Alteração de prioridade material gera nova validação do escopo afetado. | NÃO EXECUTADO |
| T093-33 | Prioridades, fairness e conflitos | Pedido de adiamento é apresentado sem forçar PC a aceitar. | NÃO EXECUTADO |
| T093-34 | Prioridades, fairness e conflitos | Reserva antiga é mantida enquanto nova negociação está pendente. | NÃO EXECUTADO |
| T093-35 | Prioridades, fairness e conflitos | Replanejamento independente preserva operações não conflitantes. | NÃO EXECUTADO |
| T093-36 | Prioridades, fairness e conflitos | Ausência de substituto é registrada, não inventa NPC novo. | NÃO EXECUTADO |
| T093-37 | Agência e permissões | Jogador A não pode mover PC B para satisfazer compromisso compartilhado. | NÃO EXECUTADO |
| T093-38 | Agência e permissões | Saída de um PC bloqueia novos despachos em seu nome. | NÃO EXECUTADO |
| T093-39 | Agência e permissões | Delegação DEC-045/046 sem permissão não autoriza novo gasto ou risco. | NÃO EXECUTADO |
| T093-40 | Agência e permissões | Repriorização LOW que somada ultrapassa risco HIGH exige gate. | NÃO EXECUTADO |
| T093-41 | Agência e permissões | Autorização de revisão anterior não autoriza alvo ou local novos. | NÃO EXECUTADO |
| T093-42 | Agência e permissões | NPC autônomo pode recusar compromisso quando regras permitem. | NÃO EXECUTADO |
| T093-43 | Agência e permissões | Aprovação host não substitui consentimento exigido de PC. | NÃO EXECUTADO |
| T093-44 | Agência e permissões | Consentimento parcial só autoriza os recursos e prazos aprovados. | NÃO EXECUTADO |
| T093-45 | Agência e permissões | Proposta LLM de redistribuição nunca concede lease automaticamente. | NÃO EXECUTADO |
| T093-46 | Agência e permissões | Vínculo secreto entre NPC e missão não vaza durante pedido de consentimento. | NÃO EXECUTADO |
| T093-47 | Estados e scheduler | Operação independente não é bloqueada por um conflito de outra. | NÃO EXECUTADO |
| T093-48 | Estados e scheduler | Duas operações com recursos exclusivos permanecem ambas propostas até arbitragem. | NÃO EXECUTADO |
| T093-49 | Estados e scheduler | Fila registra BLOCKED_RESOURCE sem tratá-la como falha mecânica. | NÃO EXECUTADO |
| T093-50 | Estados e scheduler | Apenas reserva válida habilita avaliação de despacho, não autoexecução. | NÃO EXECUTADO |
| T093-51 | Estados e scheduler | Operação pode liberar reserva ainda não despachada após cancelamento autorizado. | NÃO EXECUTADO |
| T093-52 | Estados e scheduler | Pedido de pausa do orquestrador não promete pausar engine BG2:EE. | NÃO EXECUTADO |
| T093-53 | Estados e scheduler | Alteração de horário que cria overlap gera conflito e revisão. | NÃO EXECUTADO |
| T093-54 | Estados e scheduler | Consulta de disponibilidade é read-only e não realiza mutação. | NÃO EXECUTADO |
| T093-55 | Estados e scheduler | Demanda por compute é separada de recurso NPC/inventário. | NÃO EXECUTADO |
| T093-56 | Estados e scheduler | Operation revision stale não participa de rodada de admissão. | NÃO EXECUTADO |
| T093-57 | Host, execução e incerteza | Reserva vencedora sem capability engine não cria ação mecânica. | NÃO EXECUTADO |
| T093-58 | Host, execução e incerteza | Despacho ao gateway com sessão host errada é rejeitado. | NÃO EXECUTADO |
| T093-59 | Host, execução e incerteza | Receipt host válido confirma somente efeito observado. | NÃO EXECUTADO |
| T093-60 | Host, execução e incerteza | DISPATCHED sem receipt não confirma que NPC chegou. | NÃO EXECUTADO |
| T093-61 | Host, execução e incerteza | UNCERTAIN impede reatribuição de recurso singular antes de conciliação. | NÃO EXECUTADO |
| T093-62 | Host, execução e incerteza | Cancelamento enviado após despacho não apaga receipt confirmado. | NÃO EXECUTADO |
| T093-63 | Host, execução e incerteza | Repetição de receipt não duplica consumo ou recompensa. | NÃO EXECUTADO |
| T093-64 | Host, execução e incerteza | Dois clients não podem criar duas mutações de mesmo recurso. | NÃO EXECUTADO |
| T093-65 | Host, execução e incerteza | Perda de conexão com host força reconciliação antes de novos despachos conflitantes. | NÃO EXECUTADO |
| T093-66 | Host, execução e incerteza | Build sem API de pausa não recebe falsa confirmação de cancelamento. | NÃO EXECUTADO |
| T093-67 | Host, execução e incerteza | Item com owner/quest script protegido não é usado por scheduler sem teste. | NÃO EXECUTADO |
| T093-68 | Host, execução e incerteza | Host receipt de outra operação/campanha não libera a reserva atual. | NÃO EXECUTADO |
| T093-69 | Restauração e impasses | Restore de checkpoint antigo invalida tokens de fencing futuros. | NÃO EXECUTADO |
| T093-70 | Restauração e impasses | Revisão de Knowledge Pack incompatível marca reserva STALE. | NÃO EXECUTADO |
| T093-71 | Restauração e impasses | Mudança de branch não herda reservas privadas de outro ramo. | NÃO EXECUTADO |
| T093-72 | Restauração e impasses | Save antigo não reconstitui viagem futura nem deixa NPC duplicado. | NÃO EXECUTADO |
| T093-73 | Restauração e impasses | Crash antes de adquirir lease não consome recurso. | NÃO EXECUTADO |
| T093-74 | Restauração e impasses | Crash após envio e antes de receipt permanece UNCERTAIN. | NÃO EXECUTADO |
| T093-75 | Restauração e impasses | Retorno tardio de worker com epoch velho é rejeitado. | NÃO EXECUTADO |
| T093-76 | Restauração e impasses | Grafo wait-for detecta ciclo entre operações que aguardam recursos. | NÃO EXECUTADO |
| T093-77 | Restauração e impasses | Detecção de ciclo não cancela comandos já despachados. | NÃO EXECUTADO |
| T093-78 | Restauração e impasses | Starvation gera alerta/métrica, sem punição automática à operação concorrente. | NÃO EXECUTADO |
| T093-79 | Privacidade e conhecimento | Log de conflito revela recurso anonimizado sem divulgar identidade de testemunha. | NÃO EXECUTADO |
| T093-80 | Privacidade e conhecimento | NPC sem ACL não lê objetivo secreto de outra operação. | NÃO EXECUTADO |
| T093-81 | Privacidade e conhecimento | A mesma guilda não conhece automaticamente plano rival por dividir scheduler. | NÃO EXECUTADO |
| T093-82 | Privacidade e conhecimento | Job de LAN não autorizado não recebe dados completos de dossiê ou rota. | NÃO EXECUTADO |
| T093-83 | Privacidade e conhecimento | Fonte rumor não é promovida a fato só por urgência operacional. | NÃO EXECUTADO |
| T093-84 | Privacidade e conhecimento | Destino verdadeiro de escolta não aparece em diagnóstico de fila pública. | NÃO EXECUTADO |
| T093-85 | Privacidade e conhecimento | Informação aprendida por NPC requer transmissão, não mera reserva de scheduler. | NÃO EXECUTADO |
| T093-86 | Privacidade e conhecimento | Retirada de permissão invalida views sensíveis em jobs ainda pendentes. | NÃO EXECUTADO |
| T093-87 | Desempenho e integração | Scheduler dorme sem eventos e não executa LLM por tick de jogo. | NÃO EXECUTADO |
| T093-88 | Desempenho e integração | Sob pressão computacional, trabalho opcional é degradado, não recibos críticos. | NÃO EXECUTADO |
| T093-89 | Desempenho e integração | Backpressure limita fila crescente sem perder ações mutativas incertas. | NÃO EXECUTADO |
| T093-90 | Desempenho e integração | Métrica P0/P1 de compute não é confundida com prioridade de missão. | NÃO EXECUTADO |
| T093-91 | Desempenho e integração | Teste em build limpa/EEex com dois clientes precede ativação de despacho concorrente. | NÃO EXECUTADO |
| T093-92 | Desempenho e integração | Falha de POC mantém ação/lock lógico em modo proposal-only sem fingir sucesso. | NÃO EXECUTADO |

## 11. Sequência de provas futuras

1. Fixtures sintéticas offline de 2–50 operações, recursos singulares/fungíveis, overlaps DR, homônimos, aliases e falha de autorizações; verificar determinismo, fairness e ausência de duplicação.
2. Provar aquisição/revisão atômica com fencing e crash/restore de um storage escolhido, antes de qualquer bridge. Modelar `UNCERTAIN`, host receipt, branch e revision mismatch.
3. Separar ensaios de carga e prioridade computacional DEC-056 do scheduling narrativo, minimizando CPU/RAM/LLM.
4. Testar BG2:EE limpo e EEex por build/manifest, inicialmente somente leitura para presença, inventário e coordenadas realmente observáveis. Sem pressupor APIs.
5. Em cópias de saves descartáveis, habilitar um único tipo de ação tipada, confirmar host + dois clientes, idempotência, checkpoint e rollback de dados externos sem apagar fatos.
6. Ativar somente capabilities com prova; falha mantém operação como proposta e não declara execução.

## 12. Decisões preservadas e próxima etapa

- **DEC-011/012:** host e Action Gateway seguem autoridade mecânica exclusiva.
- **DEC-022/053/063:** tempo DR, branch e revisões de checkpoints/Knowledge Pack, sem propagação de futuro.
- **DEC-019/028/041/045/046:** privacidade, agência dos PCs, delegações e consentimento.
- **DEC-051/056:** inventário e scheduler de **custo computacional**, distintos de reservas narrativas.
- **DEC-066–074:** identidade, presença, itinerários, handoff de incidentes e encontros e consequências confirmadas.
- **DEC-083–090:** proteção de testemunhas, refúgios, dossiês e informação incompleta, sem onisciência.
- **DEC-091/092:** planejamento, revisão, pausa lógica, despachos e receipts; DEC-093 complementa, não substitui.
- **DEC-060–092 preservadas integralmente; ADR-0001..0087 bit a bit inalterados.**
- **DEC-094 — EM ABERTO:** política de desbloqueio de deadlocks/starvation/reservas órfãs; A cancelar todos, B LLM arbitrar, **C recuperação determinística com wait-for graph, liberação só de atos revogáveis, fairness, consentimento, recibos e reconciliação**.

## Integração DEC-094/C (Discovery v9.0)

DEC-094 especifica recuperação de ciclos/starvation/leases órfãs detectados pela DEC-093. Apenas reservations HELD comprovadamente não despachadas e autorizadas podem ser logicamente liberadas; `UNCERTAIN` exige conciliação.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Compensação DEC-095 é operação adicional e deve concorrer por recursos legitimamente. ImpactRule DEC-096 não cria disponibilidade de NPC ou item.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Patrulha proposta DEC-096/C não reserva NPC/recursos até DEC-093 validar concorrência; calendário não garante disponibilidade.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Duas repercussões DEC-097/C não podem reservar mesmo NPC ou recurso exclusivo sem arbitragem DEC-093.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Reservas concorrentes de atores/recursos não contam como instâncias no host; DEC-098 verifica compatibilidade antes de propor materialização.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Reserva concorrente não transfere titularidade do recurso; prioridade do scheduler não equivale a ownership.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Scheduler concorrente não amplia permissões de probes ao distribuir observações entre operações.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** DEC-101 interpretation is read-only, version-pinned and independent of gateway/host execution. A confirmed semantic milestone does not authorize actions or prove a command receipt; mod upgrades, checkpoint restore, revised mapping, epoch mismatch or contradictory states cause fail-closed reconciliation. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Reconciliador DEC-102 usa CAS/fencing; cliente não host não pode reescrever overlay unilateralmente. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **cancelamento seguro de reservas**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para recursos de mensageiros não se duplicam em operações concorrentes, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para reparação usa recursos com reserva sem duplicação, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Reservas de recursos e obrigações concorrentes exigem fencing. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Reservas e concorrência impedem dupla alocação de recursos e NPCs. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Reserva lógica e custódia real são estados diferentes; recursos em escrow não podem ser prometidos simultaneamente a duas operações.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
