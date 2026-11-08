# DEC-091 — Planejamento operacional contextual com inteligência incerta e execução segura

**Infinity AI Discovery v8.7 · ADR-0086 · opção C aprovada · SOMENTE ARQUITETURA, NÃO IMPLEMENTADA.**  
**Evidência de testes:** 88 cenários candidatos T091-01..T091-88, **TODOS NÃO EXECUTADOS**. Nenhuma capacidade BG2:EE/EEex ou multiplayer host+dois clientes foi testada.

## 1. Objetivo e critérios de não-implementação

Viabilizar operações propostas a partir de dossiês DEC-090 **sem** confundir informações imperfeitas com fatos ou permitir que um diretor de IA controle a party. Um plano deve ser apresentável, verificável, revogável e separável do despacho e da confirmação host. Esta decisão **não** implementa IA planejadora autônoma, NPCs físicos, detenção, vigilância, escutas, pathfinding dinâmico, quest injection ou habilidades não testadas.

**Invariantes:**

1. Alegação ≠ verdade; plano ≠ execução; autorização ≠ receipt; recurso reservado ≠ recurso consumido.
2. Participante sem acesso ao dossiê não conhece seus segredos; consentimento de PC não é presumido.
3. LOW narrativo só produz proposta/efeito limitado confirmado; MEDIUM/HIGH aplicam DEC-027, DEC-034 e gates da mecânica.
4. Capacidade do motor é identificada e testada por build, não inferida por lore ou diálogos.
5. Idempotência, revisão, campanha/branch e checkpoint impedem duplicação/replay.

## 2. Separação física e lógica da informação

```text
knowledge/periods/<ANO>-DR/                  # cânone curado em diretórios físicos por ano DR, DEC-060
  events/, factions/, locations/, ...        # NÃO colocar aqui planos/segredos de campanha

campaign-overlays/<campaign>/<branch>/        # domínio LÓGICO CANDIDATO; layout físico ainda não implantado
  dossiers/                                  # DEC-090; versão/ACL e evidências DEC-089
  operational-proposals/                     # hipótese de ação e objetivos
  operational-plan-revisions/                # revisões imutáveis, validações e limitações
  resource-reservations/                     # orçamento/lease/TTL e concorrência
  approval-ledger/                           # decisões de PCs, NPCs competentes e host
  dispatch-ledger/                           # solicitações tipadas ao gateway
  execution-receipts/                        # evidências da engine, com status UNCERTAIN
  narrative-observations/                    # somente fatos após confirmação
  audit/                                     # justificativas redigidas, idempotência, versões
```

`knowledge/periods/<ANO>-DR/` é uma invariante **já aprovada** da DEC-060; as pastas ilustrativas `campaign-overlays/` não significam implementação. Knowledge Pack DEC-063 é fixado por campanha e instante; eventos futuros jamais são antecipados para melhorar planejamento.

## 3. Contratos candidatos — não implementados

```text
OperationalProposal {
  plan_id, revision, campaign_id, branch_id, initiator_actor_id,
  initiating_role, objective, operation_kind, description_for_audience,
  dossier_id?, dossier_revision?, disclosure_view_ref?, claim_assessment_refs[],
  uncertainty_notes[], contradicted_claim_refs[],
  target_actor_id?, site_ref?, start_window_dr?, end_window_dr?,
  required_participants[], target_audience_scope, sensitive_fields_acl,
  expected_outcome_conditions[], abort_conditions[],
  created_at_epoch, checkpoint_ref, world_snapshot_ref, knowledge_pack_binding,
  state: DRAFT|PENDING_VALIDATION|VALIDATED_CONDITIONAL|PRESENTED|BLOCKED|STALE
}
PlanValidation {
  validation_id, plan_id, plan_revision, policy_revision,
  precondition_results[], authority_scope, participant_access_checks[],
  risk_category, aggregate_risk_category, geographic_feasibility,
  temporal_feasibility, actor_identity_presence, build_capability_manifest,
  resource_requirements[], unique_resource_conflicts[],
  evidence_limitations[], authorization_requirements[],
  result: VALID|CONDITIONAL|BLOCKED|STALE, expiry_dr?, audit_ref
}
ApprovalRecord {
  approval_id, plan_id, plan_revision, approving_principal,
  authority_basis, participant_consent_refs[], risk_policy_revision,
  authorized_action_types[], upper_resource_bounds[],
  scope, expires_at_epoch?, checkpoint_ref, signature_or_receipt_ref,
  state: APPROVED|DENIED|REVOKED|EXPIRED
}
ResourceReservation {
  reservation_id, plan_id, plan_revision, resource_identity_id,
  resource_kind, quantity, scope, lease_token, fencing_epoch,
  expires_at_epoch, commitment_ref, status: RESERVED|CONSUMED|RELEASE_PENDING|RELEASED|UNCERTAIN
}
ActionDispatch {
  dispatch_id, plan_id, plan_revision, approved_action_id,
  action_gateway_operation, target_identity_id?,
  authorization_ref, reservation_refs[], build_manifest_ref,
  idempotency_key, checkpoint_ref, resolution_epoch,
  status: QUEUED|DISPATCHED|REJECTED|UNCERTAIN|CONFIRMED
}
HostExecutionReceipt {
  receipt_id, dispatch_id, observed_actor_identity_id,
  observed_action, observed_delta, build_manifest_ref,
  host_session_id, checkpoint_ref, confirmation_state,
  observed_at_dr, authoritative_source_ref
}
PlanOutcome {
  plan_id, revision, linked_receipt_ids[], narrative_evidence_refs[],
  outcomes_confirmed[], outcomes_unknown[], downstream_event_refs[],
  state: PARTIAL|CONFIRMED|FAILED|CANCELLED|STALE|UNCERTAIN,
  adjudication_policy_ref, audit_ref
}
```

Este contrato é um **rascunho lógico** sem banco, API, schema de rede ou engine implementados. `approval_id`, `receipt_id` e `reservation_id` não são intercambiáveis. A validação precisa de provas determinísticas quando possíveis, não score arbitrário criado pelo modelo.

## 4. Pipeline de planejamento por eventos

```text
DossierRevision / DisclosureView / SourceClaim/ClaimAssessment (DEC-089/090)
    ↓ ACL por participante, finalidade e momento DR (DEC-019/028/041)
OperationalProposal [DRAFT]
    ↓ verificação sem mutação: fatos, presença, tempo, recursos, competência, build
PlanValidation [VALID / CONDITIONAL / BLOCKED / STALE]
    ↓ apresentação a quem pode realmente decidir; alternativa de investigação
ApprovalRecord [APPROVED / DENIED / REVOKED / EXPIRED]
    ↓ reserva com lease/TTL e resolução de conflito (não é consumo)
ResourceReservation [RESERVED]
    ↓ Action Gateway: allowlist, risco, consentimento, session/branch, idempotência
ActionDispatch [QUEUED / DISPATCHED / UNCERTAIN]
    ↓ ação mecânica realmente observada, se POC comprovar capability
HostExecutionReceipt [CONFIRMED / REJECTED / UNKNOWN]
    ↓ reconciliação causal; relatos seletivos por observador; dedup
PlanOutcome [CONFIRMED / PARTIAL / FAILED / CANCELLED / UNCERTAIN]
```

Não saltar de DRAFT a CONFIRMED; `DISPATCHED` não comprova ato; execução sem receipt/observação é `UNCERTAIN`, sem repetir às cegas. Aprovação anterior perde validade quando alvo, localização, participantes, dossiê, risco, recursos, ACL, tempo ou checkpoint mudam.

## 5. Prioridade por risco e informação

| Tipo de plano hipotético | Incerteza | Controle candidato | Efeito real possível |
|---|---|---|---|
| Pesquisar registros acessíveis | Requer acesso legítimo, dados existentes | LOW/condicional, ACL e limites | Proposta e leitura autorizada; sem inventar documentos |
| Conversar com informante | NPC pode recusar; DEC-088 | Agência/consentimento/risco contextual | Apenas diálogo/recepção confirmados |
| Visitar dois armazéns | Reunião não confirmada, tempo de viagem | Aceite de cada PC, presença e geografia | Movimento somente se host+build demonstrados |
| Observar local fora de cena | Capacidade de observador e acesso incertos | DEC-068–071/072, riscos e handoff | Relato após evento validado; não inferir encontro |
| Entrar em área não autorizada | Risco, jurisdição, quest e PvP potenciais | MEDIUM/HIGH, autorização explicitamente aplicável | Bloqueado até autorização/capability |
| Intervir ou prender suspeito | Identidade e culpa podem ser incertas | HIGH default-deny; DEC-077–080 e 034 | Nenhuma prisão/apreensão por LLM |
| Usar isca de contraespionagem | Informação plantada ≠ fato | DEC-086, ACL, autorizador e anti-retcon | Somente difusão e efeitos com origem causal |
| Gasto de ouro, item ou XP | Inventário e saldo podem divergir | reserva, gateway, host receipt | Sem alteração presumida de engine |

Não estabelecer *threshold* numérico universal que converta qualquer percentual de confiança em permissão. Ações meramente informativas podem ser propostas em contexto incerto, com ressalvas; ações graves devem ser bloqueadas até fundamentos verificáveis e gates.

## 6. Coop, NPCs, facções e divisão de autoridades

- **PCs:** jogador/titular decide ações e consentimentos; delegação DEC-045/046 não concede autorização genérica de operação ou exposição de segredo.
- **NPCs:** motivações, personalidade, memória e divergência DEC-047/048/064–068 condicionam propostas/decisões; NPC não recebe recursos ou teletransportes por texto.
- **Facções:** autonomia DEC-031/032 com recursos agregados e cronologia; sem comando instantâneo mundial, conhecimento por DEC-029/074 e competência jurídica DEC-078–080.
- **Host:** estado da mecânica é autoritativo DEC-011; gateway tipado DEC-012, default-deny, idempotência, receipt e reconcile. O modelo nem o cliente secundário escrevem diretamente em CRE/saves.
- **LLM local:** pode sumarizar opções e narrar planos, não substituir autorização humana, avaliação de competência ou verificações de build. Nós LAN recebem vista minimizada.

## 7. Reserva, validade e cancelamento

- O planejador só considera recursos realmente observáveis (inventário, unidades, localização, dinheiro, materiais, conexões), identificados por origem e revision de mundo.
- Reservas são exclusivas/conflitantes conforme categoria; concorrência requer `fencing_epoch`, TTL e arbitragem determinística. Reservar não reduz automaticamente o inventário físico; confirmar gastos exige recibo.
- Uma mudança de dados críticos marca `NEEDS_REVALIDATION/STALE`. Consentimento revogado impede novos despachos; operação já em `UNCERTAIN` precisa reconciliação, não reversão automática.
- Plano pode ser abandonado sem produzir evento do mundo, desde que não tenha começado uma ação confirmada.
- Restauro DEC-053/054/055: reconciliar manifest/hash/checkpoint, revogar tokens de leases antigos, segregar branches e conter operações pendentes. Nunca importar ação de outra linha temporal.

## 8. Segurança e anti-autonomia indevida

- Entrada de dossiê e texto LLM são dados não confiáveis; descartar tentativas de instruir ferramenta, host, sistema de permissões ou sinalizar aprovação fictícia.
- A soma de atos LOW que gera consequência HIGH deve ser reclassificada e bloqueada antes da realização.
- Citações e URLs em relatórios não conferem acesso a documentos secretos. Salientar quando a fonte não poderia saber o local, data, identidade ou equipamento alegado.
- Redigir logs/audit que possam ser vistos por NPCs/jogadores ou workers com papel insuficiente; preservar cópia protegida para reconciliação host.
- Sem mecânica comprovada de observação, escolta, prisão, intercepção, diálogos ou criação de CRE no BG2:EE/EEex; construir SPECS/POCs gradualmente, sem declarar capacidade com base em documentação ou hipótese.

## 9. Cenário de aceitação ilustrativo

**Entrada:** relatório de informante A aponta Armazém Norte, B aponta Sul, C repete A. Dossiê DEC-090 apresenta ambas hipóteses; nenhum encontro é fato.

**Planos propostos:** (1) consultar registro acessível; (2) visitar livremente o entorno do Norte; (3) visitar livremente o entorno do Sul; (4) solicitar confirmação adicional; (5) intervir coercitivamente. O sistema pode comparar **precondições** e pedir decisão. A alternativa (5) é HIGH e falha no gate enquanto insuficiente/autorização ausente; as demais dependem de acesso, participantes, recursos e horário.

**Coop:** um PC aceita visitar o Norte, outro recusa. A IA não move o segundo. Um NPC aliado pode se recusar a acompanhar; não se cria um observador virtual sem recurso/POC. Dossiê não atualiza conhecimento de rivais automaticamente.

**Resultado:** somente após receipt/observação admissível registrar presença, pistas ou ausência limitada. Se outro documento muda o horário, planos ainda pendentes ficam STALE. Nenhuma execução de exemplo foi realizada.

## 10. Matriz de testes candidatos — TODOS NÃO EXECUTADOS

As 88 linhas abaixo especificam **testes futuros**, não evidência de funcionamento atual. Casos de motor exigem instalação de teste e POC host+dois clientes antes de qualquer liberação.

| ID | Grupo | Comportamento esperado | Status |
|---|---|---|---|
| T091-01 | Entrada, evidência e veracidade | Plano referencia dossier_id e revisão imutável, sem copiar claim como WorldFact. | NÃO EXECUTADO |
| T091-02 | Entrada, evidência e veracidade | Relato UNVERIFIED não vira confirmação por estar no plano. | NÃO EXECUTADO |
| T091-03 | Entrada, evidência e veracidade | Duas fontes que derivam da mesma origem não contam como duas provas. | NÃO EXECUTADO |
| T091-04 | Entrada, evidência e veracidade | Contradição Norte versus Sul produz alternativas, não uma localização factual fabricada. | NÃO EXECUTADO |
| T091-05 | Entrada, evidência e veracidade | Fonte sem acesso epistêmico plausível mantém valor UNKNOWN. | NÃO EXECUTADO |
| T091-06 | Entrada, evidência e veracidade | Dossiê vencido/STALE exige validação temporal antes de plano. | NÃO EXECUTADO |
| T091-07 | Entrada, evidência e veracidade | Novo relatório contraditório invalida precondições antigas. | NÃO EXECUTADO |
| T091-08 | Entrada, evidência e veracidade | Modelo propõe investigação adicional sem transformar lacuna em certeza. | NÃO EXECUTADO |
| T091-09 | ACL, identidade e confidencialidade | Participante não autorizado não recebe identidade real de fonte protegida. | NÃO EXECUTADO |
| T091-10 | ACL, identidade e confidencialidade | Prompt LLM é filtrado antes de recebimento e não apenas na UI. | NÃO EXECUTADO |
| T091-11 | ACL, identidade e confidencialidade | Plano parcial de escolta não vaza abrigo, horário e rota secreta. | NÃO EXECUTADO |
| T091-12 | ACL, identidade e confidencialidade | Mesmo grupo cooperativo não herda todos os segredos dos demais PCs. | NÃO EXECUTADO |
| T091-13 | ACL, identidade e confidencialidade | Trabalhador LAN revogado não recebe plano/cache sensível. | NÃO EXECUTADO |
| T091-14 | ACL, identidade e confidencialidade | Documentos do dossiê com instruções maliciosas não alteram gates. | NÃO EXECUTADO |
| T091-15 | ACL, identidade e confidencialidade | Destino exportado remove metadados capazes de reidentificar testemunha. | NÃO EXECUTADO |
| T091-16 | ACL, identidade e confidencialidade | Correção do dossiê não divulga automaticamente segredo antes omitido. | NÃO EXECUTADO |
| T091-17 | Agência do PC, delegação e facção | Propor missão não move PC sem escolha de seu controlador autorizado. | NÃO EXECUTADO |
| T091-18 | Agência do PC, delegação e facção | Anfitrião não interpreta silêncio de PC ausente como consentimento. | NÃO EXECUTADO |
| T091-19 | Agência do PC, delegação e facção | Delegado sem escopo não gasta item nem aceita risco HIGH pelo dono. | NÃO EXECUTADO |
| T091-20 | Agência do PC, delegação e facção | Líder de party não obriga outros PCs a aceitar operação. | NÃO EXECUTADO |
| T091-21 | Agência do PC, delegação e facção | NPC pode recusar plano incompatível com personalidade e compromisso DEC-087. | NÃO EXECUTADO |
| T091-22 | Agência do PC, delegação e facção | Facção não pode executar plano que viole competência ou escopo. | NÃO EXECUTADO |
| T091-23 | Agência do PC, delegação e facção | Conflito de consentimento interrompe apenas partes não autorizadas de plano. | NÃO EXECUTADO |
| T091-24 | Agência do PC, delegação e facção | Autoria do plano não é autoria de atos futuros ainda não praticados. | NÃO EXECUTADO |
| T091-25 | Risco e operações permitidas | Observação narrativa LOW pode ser proposta sem afirmar sucesso. | NÃO EXECUTADO |
| T091-26 | Risco e operações permitidas | Pedido MEDIUM sem política/host receipt não se publica como efeito. | NÃO EXECUTADO |
| T091-27 | Risco e operações permitidas | Prisão baseada em rumor permanece HIGH default-deny. | NÃO EXECUTADO |
| T091-28 | Risco e operações permitidas | Emboscada com dano significativo exige política HIGH, mesmo quando narrada como patrulha. | NÃO EXECUTADO |
| T091-29 | Risco e operações permitidas | Soma de etapas LOW com resultado agregado HIGH exige reclassificação. | NÃO EXECUTADO |
| T091-30 | Risco e operações permitidas | PvP e dano a PC exigem regras de consentimento DEC-042. | NÃO EXECUTADO |
| T091-31 | Risco e operações permitidas | Alterar canon/quest irreversible é barrado por DEC-034/050. | NÃO EXECUTADO |
| T091-32 | Risco e operações permitidas | Texto LLM tentando declarar autorização HIGH não é autorização. | NÃO EXECUTADO |
| T091-33 | Recursos e reserva | Recursos inexistentes produzem BLOCKED em vez de ser criados. | NÃO EXECUTADO |
| T091-34 | Recursos e reserva | Duas missões não podem reservar a mesma unidade exclusiva simultaneamente. | NÃO EXECUTADO |
| T091-35 | Recursos e reserva | Reserva expirada perde validade e obriga nova revisão. | NÃO EXECUTADO |
| T091-36 | Recursos e reserva | Release de reserva falha UNCERTAIN e não duplica estoque. | NÃO EXECUTADO |
| T091-37 | Recursos e reserva | Ouro prometido sem recibo não vira gasto confirmado. | NÃO EXECUTADO |
| T091-38 | Recursos e reserva | Item inventariado como insuficiente não é retirado nem duplicado. | NÃO EXECUTADO |
| T091-39 | Recursos e reserva | NPC fisicamente indisponível não aparece automaticamente como escolta. | NÃO EXECUTADO |
| T091-40 | Recursos e reserva | Mudança de recursos após aprovação invalida despacho. | NÃO EXECUTADO |
| T091-41 | Geografia e cronologia | NPC distante não aparece em Athkatla sem deslocamento verificado. | NÃO EXECUTADO |
| T091-42 | Geografia e cronologia | Tempo de deslocamento respeita relógio DR e rota plausível. | NÃO EXECUTADO |
| T091-43 | Geografia e cronologia | Atividade DORMANT não realiza ações locais ao vivo sem wake/handoff. | NÃO EXECUTADO |
| T091-44 | Geografia e cronologia | Encontro não é instanciado sem catálogo e capability por build. | NÃO EXECUTADO |
| T091-45 | Geografia e cronologia | Dossiê do futuro não é usado no planejamento do ano anterior. | NÃO EXECUTADO |
| T091-46 | Geografia e cronologia | Planos de outra campanha ou ramo são rejeitados. | NÃO EXECUTADO |
| T091-47 | Geografia e cronologia | Checkpoint anterior não herda ações de plano criado depois. | NÃO EXECUTADO |
| T091-48 | Geografia e cronologia | Reunião em hora já passada não dispara operação como se ainda fosse futura. | NÃO EXECUTADO |
| T091-49 | Autorização, execução e host | PLANNED não significa HOST_AUTHORIZED. | NÃO EXECUTADO |
| T091-50 | Autorização, execução e host | Aprovação do jogador não é recibo de movimento no motor. | NÃO EXECUTADO |
| T091-51 | Autorização, execução e host | Reserva de unidade não comprova sua presença ou deslocamento. | NÃO EXECUTADO |
| T091-52 | Autorização, execução e host | Gateway rejeita operação fora da allowlist tipada. | NÃO EXECUTADO |
| T091-53 | Autorização, execução e host | Capability inexistente bloqueia mudança mecânica proposta. | NÃO EXECUTADO |
| T091-54 | Autorização, execução e host | Host receipt confirma só campos efetivamente observados. | NÃO EXECUTADO |
| T091-55 | Autorização, execução e host | Execução UNCERTAIN não é repetida automaticamente. | NÃO EXECUTADO |
| T091-56 | Autorização, execução e host | Cliente multiplayer isolado não confirma ação para toda a campanha. | NÃO EXECUTADO |
| T091-57 | Versões, concorrência e idempotência | Mesmo idempotency key não aplica operação duas vezes. | NÃO EXECUTADO |
| T091-58 | Versões, concorrência e idempotência | Mudança do alvo invalida approval vinculado à revisão antiga. | NÃO EXECUTADO |
| T091-59 | Versões, concorrência e idempotência | Mudança de risco exige gate atualizado. | NÃO EXECUTADO |
| T091-60 | Versões, concorrência e idempotência | Jobs de checkpoint obsoleto são marcados STALE. | NÃO EXECUTADO |
| T091-61 | Versões, concorrência e idempotência | Lease vencido não permite consumo em worker atrasado. | NÃO EXECUTADO |
| T091-62 | Versões, concorrência e idempotência | Concorrência de duas ordens resolve disputa determinística ou host decision. | NÃO EXECUTADO |
| T091-63 | Versões, concorrência e idempotência | Restart reconcilia recibos antes de dar plano por concluído. | NÃO EXECUTADO |
| T091-64 | Versões, concorrência e idempotência | Ação cancelada após dispatch UNKNOWN não executa rollback cego. | NÃO EXECUTADO |
| T091-65 | Resultados e aprendizagem | Envio de observador não confirma reunião nem culpa. | NÃO EXECUTADO |
| T091-66 | Resultados e aprendizagem | Vigilância sem achados é registrada como observação limitada, não prova negativa total. | NÃO EXECUTADO |
| T091-67 | Resultados e aprendizagem | NPC não aprende resultado não testemunhado ou comunicado. | NÃO EXECUTADO |
| T091-68 | Resultados e aprendizagem | Sucesso narrativo não altera inventário/facção mecanicamente. | NÃO EXECUTADO |
| T091-69 | Resultados e aprendizagem | Relatório corrigido não reescreve crenças antigas retroativamente. | NÃO EXECUTADO |
| T091-70 | Resultados e aprendizagem | Fracasso de operação não é atribuído a PC ausente sem ato confirmado. | NÃO EXECUTADO |
| T091-71 | Resultados e aprendizagem | Reconhecimento de mérito DEC-075 depende de evidência individual. | NÃO EXECUTADO |
| T091-72 | Resultados e aprendizagem | Proposta recusada não gera reputação ou recompensa por execução. | NÃO EXECUTADO |
| T091-73 | Falhas, segurança e auditoria | Perda de conexão host mantém operação PENDING/UNCERTAIN sem fingir sucesso. | NÃO EXECUTADO |
| T091-74 | Falhas, segurança e auditoria | Crise de recursos DEC-056 não remove verificações críticas de ACL. | NÃO EXECUTADO |
| T091-75 | Falhas, segurança e auditoria | Log de plano protegido não expõe rota, nomes ou horários sensíveis. | NÃO EXECUTADO |
| T091-76 | Falhas, segurança e auditoria | Worker LAN com permissão menor recebe apenas projeção sanitizada. | NÃO EXECUTADO |
| T091-77 | Falhas, segurança e auditoria | Prompt injection em evidência não muda objetivo autorizado. | NÃO EXECUTADO |
| T091-78 | Falhas, segurança e auditoria | Timeout do validador preserva default-deny para efeito HIGH. | NÃO EXECUTADO |
| T091-79 | Falhas, segurança e auditoria | Restaurar save não mistura receipts de outra branch. | NÃO EXECUTADO |
| T091-80 | Falhas, segurança e auditoria | Auditoria distingue proposta, aprovação, reserva, despacho e fato confirmado. | NÃO EXECUTADO |
| T091-81 | Integração e limites de POC | Fixture offline Norte/Sul/C valida incerteza e independência. | NÃO EXECUTADO |
| T091-82 | Integração e limites de POC | Teste por build demonstra observabilidade read-only antes de expor operação. | NÃO EXECUTADO |
| T091-83 | Integração e limites de POC | POC host+2 clientes mede sincronização antes de ativar ação mecânica. | NÃO EXECUTADO |
| T091-84 | Integração e limites de POC | Comparação entre builds impede capability indevidamente reutilizada. | NÃO EXECUTADO |
| T091-85 | Integração e limites de POC | Diretor por regras funciona sem LLM em caso LOW determinístico. | NÃO EXECUTADO |
| T091-86 | Integração e limites de POC | Modelo local indisponível degrada para saída segura e não cria missões sozinho. | NÃO EXECUTADO |
| T091-87 | Integração e limites de POC | Política DEC-092 ainda aberta impede auto replanejamento pós-despacho. | NÃO EXECUTADO |
| T091-88 | Integração e limites de POC | Teste de regressão confirma intacto isolamento anual do canon DEC-060. | NÃO EXECUTADO |

## 11. Sequência de implementação proposta (não iniciada)

1. Criar fixtures offline de dossiês contraditórios DEC-089/090, usuários sem ACL, jogadores ausentes e recursos disputados.
2. Implementar contratos tipados candidato e validação determinística read-only por branch/ano DR/política.
3. Especificar UI para propostas, revisões, aceites por PC, explicitamente sem execução ao clicar somente em "planejar".
4. Testar reservas e dedup com falhas e crash; testar fallback local/sem LLM.
5. Inventariar capabilities por build BG2:EE limpa, EEex e bridge inicialmente read-only, sem assumir comandos de movimento ou eventos de NPC.
6. Somente após POC, habilitar progressivamente um conjunto mínimo de ações tipadas em host+dois clientes e reconciliar resultados.
7. Integrar roteamento de eventos e observabilidade com auditoria de risco e sigilo.
8. Definir DEC-092 para monitoramento, pausa, abortos e replanejamento operacional após despacho, sem liberar IA para mutações autônomas.

## 12. Dependências e fronteiras preservadas

- DEC-011/012/027/034: host authoritative, Action Gateway, níveis de risco e proteção de marcos irreversíveis.
- DEC-019/028/041/042/045/046: agência do PC, confidencialidade, delegação e consentimento.
- DEC-022/053–059: cronologia FROZEN/PARTIAL/REALTIME, checkpoints, recuperação, filas, modelos locais e LAN.
- DEC-060–063: cânone em pastas **físicas anuais** e Knowledge Packs curados/pinados.
- DEC-064–075: memórias e crenças NPC, identidade persistente, itinerários, handoff de incidentes, encounters, consequências e autoria.
- DEC-076–090: personas, investigações, autoridade, mandados, proteção de fontes, desinformação, agentes duplos, informantes, confiabilidade e dossiês seletivos.
- DEC-006/007/013/015/017/018 continuam abertas onde aplicável; decisões específicas de ferramentas e POCs não foram substituídas.
- **DEC-092 aberta:** acompanhamento e replanejamento de operações em andamento — A manter plano fixo, B LLM replana livremente, **C replanejamento controlado por eventos, risk gates, autorizações, recursos e checkpoints**.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

DEC-092 complementa DEC-091: planos aprovados são revistos ao mudar risco, objetivo, consentimento ou recursos. `PAUSED_ORCHESTRATION` bloqueia novos despachos, não cancela atos `DISPATCHED` nem prova pausa do motor.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

DEC-093/C detalha reserva de recursos entre planos concorrentes: resource identity, janela, exclusividade, CAS/fencing e fairness; ResourceReservation DEC-091 não é consumo/host receipt.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Antes de replanejamento por deadlock, diferenciar proposta, autorização, reserva e host receipt; não usar `UNCERTAIN` como possibilidade de desocupação.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

DEC-096 (proposta): impacto territorial/cronológico gera sinais que podem motivar planos, mas não suprime validação de recursos/consentimento/host DEC-091.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

ImpactProposal DEC-096/C pode informar planejamento DEC-091 mas não assumir recursos, autorização ou execução mecânica.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Target composto DEC-097/C é contexto para plano DEC-091 e não despacho de ação.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Planejamento operacional da DEC-091 não gera spawn até autorização, capability validada e receipt do host; diffs são projeções.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Plano operacional precisa validar ownership e compatibilidade de cada delta antes do Action Gateway.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Planejamentos podem usar milestones autorizados e atualizados; UNKNOWN não satisfaz precondição de quest.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** DEC-101 interpretation is read-only, version-pinned and independent of gateway/host execution. A confirmed semantic milestone does not authorize actions or prove a command receipt; mod upgrades, checkpoint restore, revised mapping, epoch mismatch or contradictory states cause fail-closed reconciliation. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Planos não podem usar marco de quest ainda em quarentena pela DEC-102 como fato confirmado. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **plano derivado de prova revogada**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para planejamento operacional não toma correção recebida como autorização, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para reabilitação é proposta, não execução operacional, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Monitoramento de obrigação não é plano operacional executado. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Condição satisfeita gera oportunidade de planejar, não operação executada. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
