# 108 — Cumprimento de acordos: obrigações, prazos DR, recibos e contestação causal

**Estado:** DEC-108/C aprovada como arquitetura, ADR-0103; Discovery v10.4, 2026-11-07. **Nenhuma implementação real BG2:EE/EEex/bridge/multiplayer comprovada.** DEC-060..107 e 102 ADRs anteriores preservados.

## 1. Objetivo e fronteiras

Monitorar obrigações voluntariamente pactuadas e committed conforme DEC-107, distinguir promessas, alegações, evidências, execução mecânica e conclusão, e gerar apenas **propostas não coercitivas** quando um prazo ou divergência exigir esclarecimento. Não autoriza cobrança, apreensão, sanção, restituição, reputação ou mudanças em quests. A operação é local-first, código determinístico primeiro, LLM apenas redatora de views autorizadas.

## 2. Componentes e domínios

1. `AgreementRegistry`: termo aceito, contrato committed, poderes das partes, revisões, impedimentos, revogações; **fonte autenticada independente da requisição**.
2. `ObligationScheduler`: calcula prazos pelo `world_tick` e modo DEC-022. `FROZEN` não avança automaticamente pelo relógio civil; precisão desconhecida vira `UNKNOWN`.
3. `PerformanceEvidenceRegistry`: recebe alegações e provas independentes. Um relato não é receipt de host; status de evidence `CONTESTED` não vira prova apenas porque foi repetido.
4. `HostReceiptVerifier`: autentica action id, quantidade, unidade, origem/destino, sucesso, time/campaign/branch/epochs, fingerprint da build, ownership/field permissions; não permite recibos não verificados.
5. `FulfillmentProjector`: agrega recibos CONFIRMED válidos e independentes por termo/revisão; não conta duplicados ou receipts de outra campanha; calcula saldo apenas como **quantidade ainda não comprovada**.
6. `ContestationService`: permite alegações e contraposição; canal de resposta DEC-107. Divergências não são vereditos, nem confissão por silêncio.
7. `RenegotiationPlanner`: cria proposta de revisão; novo prazo/quantidade/beneficiário só vigora com consentimentos independentes e `TermAmendmentCommit`.
8. `Outbox + Reconciliation`: propostas, fencing, CAS, idempotência; `DISPATCHED` e `UNCERTAIN` bloqueiam nova ação ou liberação de recurso.
9. `NarrativeViewBuilder`: minimiza e redige relatório de status para cada audiência, preservando fontes, pseudônimos e rotas protegidas; LLM recebe somente view autorizada.
10. `ActionGateway/Host`: **único** executor de consequências mecânicas e emissor de receipts. O avaliador exemplificativo não faz I/O ou operação no host.

## 3. Estados por obrigação

`DRAFT` → `ACCEPTED_PENDING_COMMIT` → `COMMITTED_PENDING` → `ACTIVE` → avaliações `WAITING`, `DUE_FOR_REVIEW`, `OVERDUE_UNVERIFIED`, `PARTIAL_CONFIRMED`, `FULFILLMENT_CANDIDATE`, `CONTESTED`, `UNCERTAIN`, `QUARANTINED`. Estados de **observação** não substituem o estado jurídico/ficcional `CLOSED`, `AMENDED`, `TERMINATED` ou `EXCUSED`, que exige autoridade e provas próprias.

- `DUE_FOR_REVIEW`: prazo atingido, nenhuma conclusão sobre culpa.
- `OVERDUE_UNVERIFIED`: o sistema não dispõe de evidência suficiente de cumprimento; não prova falta material.
- `PARTIAL_CONFIRMED`: pelo menos uma prestação receipt-confirmed e menos que a quantidade pactuada.
- `FULFILLMENT_CANDIDATE`: prestação total comprovada no escopo medido; fechamento pode exigir aceite/recebimento autorizado de beneficiário conforme termo.
- `CONTESTED`: discordância entre as partes ou evidências. Preservar alegações antagônicas.
- `UNCERTAIN`: comando em voo ou recibos inconclusivos; exige reconciliação antes de qualquer repetição.
- `QUARANTINED`: falta de fonte autenticada, ACL, build, poder ou estado temporal, ou prova inconsistente.

## 4. Modelo mínimo de dados e rastreabilidade

| Registro | Campos principais | Invariantes |
|---|---|---|
| `AgreementCommit` | `agreement_id`, `revision`, `case_ref`, `party_ids`, `commit_receipt`, `scope`, `policy_revision` | Sem commit: no monitoring |
| `AgreementTerm` | `term_id`, `revision`, `kind`, `obligor`, `beneficiary`, `amount`, `unit`, `due_tick`, `classification`, `purpose` | Não inferir propriedade ou existência de recursos |
| `ChronologyScope` | campaign/branch/lineage, build/modpack, host/checkpoint epochs, clock_mode, world_tick | Contexto host; nenhum relógio de parede no prazo |
| `PerformanceClaim` | `claim_id`, party, term, alleged_amount, evidence_ids, created_tick | Alegação não prova prestação |
| `HostPerformanceReceipt` | `receipt_id`, `action_id`, receipt_status, amount, unit, from/to, host identity, scope, tick, signature validation | Válido somente no escopo e em CONFIRMED |
| `DeliveryEvidence` | evidence_ref, provenance, independence, authentication, dispute_status | Corroboração ≠ recibo host |
| `FulfillmentProjection` | confirmed receipt IDs, sum, unproven remainder, status, revision, provenance | Não atribui status jurídico |
| `BreachAllegation` | allegation_id, author, grounds, evidence_refs, audience, risk | Nunca gera culpa nem sanção automaticamente |
| `DisputeNotice` | notice_id, redacted view hash, audience, outbox state, delivery/perception receipts | Sent ≠ delivered ≠ perceived ≠ agreed |
| `AmendmentProposal` | proposal_id, term revision parent, new_due_tick, terms, signers | Não modifica acordo atual |
| `AmendmentCommit` | term revision, party acceptances, authority receipts, idempotency key | Ativo somente depois de commit válido |
| `FulfillmentAudit` | event_id, source, timestamp DR, term revision, actor, safe reason, restricted evidence refs | Append-only, ACL, CAS |

## 5. Cálculo e passos de avaliação

```text
REQUEST(term_id, expected_revision)
  -> VALIDATE_SYNTHETIC_OR_TRUSTED_ENVELOPE   // aqui, somente fixtures sintéticas
  -> READ_VERIFIED_AGREEMENT_COMMIT           // não inferir de minuta
  -> VERIFY_PARTIES, ACL, POLICY, BUILD, BRANCH, EPOCH, MANDATE
  -> READ_TERM_AND_TIME_DR
  -> READ_RECEIPTS_AND_OPERATION_LEDGER
       - PENDING/DISPATCHED/UNCERTAIN? -> QUARANTINE + RECONCILE
       - CONFIRMED? -> verify cryptographic source / ledger semantics
       - duplicate receipt ID / action ID? -> dedup or reject conflicting versions
  -> AGGREGATE_CONFIRMED_AMOUNT (same unit, term, payer, beneficiary, revision)
  -> READ_CLAIMS_AND_DISPUTES (not authoritative over host)
  -> PROPOSE:
       WAIT_UNTIL_DUE | OBSERVE_FULFILLMENT_CANDIDATE
       PROPOSE_PARTIAL_CLARIFICATION | PROPOSE_EVIDENCE_REQUEST
       PROPOSE_CONTESTED_REVIEW | PROPOSE_RENEGOTIATION
       QUARANTINE_UNCERTAIN
  -> NO_HOST_ACTION, NO_REPUTATION_CHANGE, NO_SANCTION, NO_AUTOMATIC_NOTIFICATION
```

O avaliador sintético produz decisão limitada e **nunca** altera a lista de receipts. Pagamento em reais ou moedas não é inferido de texto; mercadorias só podem ser creditadas na camada mecânica após recibo válido do host. `remaining_unproven` é quantidade sem comprovação no conjunto observado, não alegação peremptória de não entrega.

## 6. Condições de tempo, consentimento e aditamento

- Prazo referenciado por `due_tick` do calendário DR curado. `FROZEN` preserva o tick, não exige que o NPC viaje ou cumpra tarefas durante o congelamento.
- `clock_mode` e `world_tick` não podem ser escritos por claims/request; vêm do estado host da campanha.
- Extensão de prazo sugerida é `AmendmentProposal`; só vale após aceites individuais por termo, poderes válidos, capacidade e recibo de commit.
- `grace_period` é uma regra curada/versionada quando acordada; não presumir tolerância ou multa arbitrária.
- Parte pode contestar quantidades, autenticidade, unidade, qualidade ou destinatário da entrega. Não forçar aceite.
- Força maior alegada é objeto para prova, não `EXCUSED` automática.
- Termos interdependentes e múltiplos credores exigirão DEC-109; a DEC-108 monitora cláusulas independentes ou dependências já explicitamente curadas.

## 7. Idempotência, ACL, riscos e observabilidade

- Chave de proposta estável `SHA256(campaign/branch/lineage/agreement/term/revision/expected_revision/epoch/action)`; `trace_id` de solicitação não altera dedup.
- Mesmo `receipt_id` não soma duas vezes; dois recibos com mesmo `action_id` e resultados contraditórios causam `QUARANTINED`.
- Recibos com status `DISPATCHED` ou `UNCERTAIN` exigem reconciliação, e o sistema não repete transferências automaticamente após timeout ou save/load.
- Termos de PC, propriedade de jogadores, mandatos de facções e ACL por destinatário exigem fontes externas autenticadas; requisição não concede autoridade a si mesma.
- Notificações e resumos respeitam classificação `PUBLIC/PARTIES/RESTRICTED/PROTECTED`; provas e metadados confidenciais não passam a prompts ou logs públicos.
- Propostas de comunicação não equivalem a notícia entregue. Propostas de retificação não mudam crenças. Propostas de mediação não vinculam contratos.
- Eventos de host comprovados permanecem mesmo após término/renegociação; eventual compensação DEC-095 precisa de procedimento próprio e novo receipt.
- Somente fórmulas e status com explicabilidade e evidências podem integrar o Discovery; nada é tratado como mecanismo real de engine sem POCs em build congelada + 2 clientes.

## 8. Casos adversariais essenciais

| Tentativa ou falha | Resposta obrigatória |
|---|---|
| LLM afirma pagamento realizado | `UNKNOWN` até recibo autenticado, sem crédito |
| Parte declara entrega de dez caixas | Alegação registrada, não quitação |
| Beneficiário declara não recebimento | Contraditório, não condenação do prestador |
| Seis unidades host-confirmed, quatro sem prova | Projeção `PARTIAL_CONFIRMED`, saldo não comprovado quatro |
| Forja de `receipt_id` | Rejeitar/quarentenar antes de agregação |
| Envio duplicado em timeout | `UNCERTAIN`, não novo dispatch |
| Save carregado de outro branch | Isolar e recertificar escopo/epoch |
| Vencimento durante `FROZEN` por wall-clock | Não avançar deadline |
| Beneficiário pede multa não prevista | Sem multa, abrir procedimento competente quando autorizado |
| Parte oferece pagar em ouro inexistente | Não criar ouro; validar recursos/host separadamente |
| Representante perde mandato | Bloquear aceites futuros, preservar fatos consumados |
| Termo foi emendado | Nenhuma confirmação atribuída retroativamente a versão diversa |

## 9. Integrações arquiteturais

- DEC-030/074/104–106: status de acordo não restaura/reduz reputação, produz rumor ou altera crenças automaticamente.
- DEC-041–046: titularidade e consentimento de PCs e ausência.
- DEC-053/056/060–063: checkpoints, budgets, Knowledge Packs e isolamento de branches.
- DEC-075/077–083/089/090: provas, responsabilidades, jurisdição, reparações, legitimidade, documentos e redaction.
- DEC-091–095: planos, monitoramento, reservas, deadlocks e compensações; ações em voo permanecem fenced.
- DEC-096/097/098/099/100–103: tempo, efeitos causais, ownership e interpretação de recibos; ausência de flag mecânica não prova não cumprimento.
- DEC-107: cláusula voluntariamente aceita é pré-condição; mediação e cumprimento são estágios separados.

## 10. Matriz de testes candidatos (NÃO EXECUTADOS)

Os cenários T108-001..T108-160 são critérios de validação futuros. Os testes de referência executados com dados fictícios **não** são POCs de motor, UI, RPG, multiplayer ou campanha.

| ID | Área | Critério | Estado |
|---|---|---|---|
| T108-001 | Commit e representação | minuta sem commit bloqueia avaliação | **NÃO EXECUTADO** |
| T108-002 | Commit e representação | aceite por apenas uma parte não basta | **NÃO EXECUTADO** |
| T108-003 | Commit e representação | contrato committed permite proposta | **NÃO EXECUTADO** |
| T108-004 | Commit e representação | mandato expirado não permite aditamento | **NÃO EXECUTADO** |
| T108-005 | Commit e representação | PC sem grant de owner não é obrigado | **NÃO EXECUTADO** |
| T108-006 | Commit e representação | revisão incorreta bloqueia leitura | **NÃO EXECUTADO** |
| T108-007 | Commit e representação | acordo de outro caso não satisfaz termo | **NÃO EXECUTADO** |
| T108-008 | Commit e representação | revogação de mandato preserva entrega anterior | **NÃO EXECUTADO** |
| T108-009 | Identidade de termo | termo inexistente não vira dívida | **NÃO EXECUTADO** |
| T108-010 | Identidade de termo | id duplicado retorna decisão estável | **NÃO EXECUTADO** |
| T108-011 | Identidade de termo | obrigor distinto exige validação | **NÃO EXECUTADO** |
| T108-012 | Identidade de termo | beneficiário divergente bloqueia recibo | **NÃO EXECUTADO** |
| T108-013 | Identidade de termo | moeda e mercadoria não se somam | **NÃO EXECUTADO** |
| T108-014 | Identidade de termo | texto livre não cria recurso | **NÃO EXECUTADO** |
| T108-015 | Identidade de termo | escopo de um termo não vale para outro | **NÃO EXECUTADO** |
| T108-016 | Identidade de termo | revisão stale não altera saldo | **NÃO EXECUTADO** |
| T108-017 | Prazo e calendário | antes do due_tick não aciona cobrança | **NÃO EXECUTADO** |
| T108-018 | Prazo e calendário | no due_tick permite revisão sem sanção | **NÃO EXECUTADO** |
| T108-019 | Prazo e calendário | depois do prazo status não é culpa | **NÃO EXECUTADO** |
| T108-020 | Prazo e calendário | FROZEN sem mudança de tick não vence por wall-clock | **NÃO EXECUTADO** |
| T108-021 | Prazo e calendário | PARTIAL avança somente por tick autorizado | **NÃO EXECUTADO** |
| T108-022 | Prazo e calendário | REALTIME respeita DR autorizado | **NÃO EXECUTADO** |
| T108-023 | Prazo e calendário | prazo sem precisão deve ficar UNKNOWN | **NÃO EXECUTADO** |
| T108-024 | Prazo e calendário | mudança de calendário exige recálculo curado | **NÃO EXECUTADO** |
| T108-025 | Recibos host | CONFIRMED autenticado pode somar | **NÃO EXECUTADO** |
| T108-026 | Recibos host | DISPATCHED não conta prestação | **NÃO EXECUTADO** |
| T108-027 | Recibos host | UNCERTAIN exige reconciliação | **NÃO EXECUTADO** |
| T108-028 | Recibos host | FAILED não prova entrega | **NÃO EXECUTADO** |
| T108-029 | Recibos host | receipt sem assinatura é rejeitado | **NÃO EXECUTADO** |
| T108-030 | Recibos host | receipt de outra build é rejeitado | **NÃO EXECUTADO** |
| T108-031 | Recibos host | receipt do destinatário errado é rejeitado | **NÃO EXECUTADO** |
| T108-032 | Recibos host | receipt com tipo incompatível é rejeitado | **NÃO EXECUTADO** |
| T108-033 | Cumprimento parcial | seis de dez gera PARTIAL_CONFIRMED | **NÃO EXECUTADO** |
| T108-034 | Cumprimento parcial | quatro restantes sem prova não equivalem a fraude | **NÃO EXECUTADO** |
| T108-035 | Cumprimento parcial | recibos independentes 4 e 6 completam candidato | **NÃO EXECUTADO** |
| T108-036 | Cumprimento parcial | quantidade zero não extingue obrigação | **NÃO EXECUTADO** |
| T108-037 | Cumprimento parcial | sobreentrega não cria crédito automático | **NÃO EXECUTADO** |
| T108-038 | Cumprimento parcial | unidades fracionárias obedecem termo | **NÃO EXECUTADO** |
| T108-039 | Cumprimento parcial | prestação de qualidade contestada permanece aberta | **NÃO EXECUTADO** |
| T108-040 | Cumprimento parcial | recebimento parcial não implica aceite total | **NÃO EXECUTADO** |
| T108-041 | Duplicidade e idempotência | receipt_id repetido não duplica | **NÃO EXECUTADO** |
| T108-042 | Duplicidade e idempotência | action_id repetido por outros recibos bloqueia | **NÃO EXECUTADO** |
| T108-043 | Duplicidade e idempotência | proposta repetida mantém idempotency key | **NÃO EXECUTADO** |
| T108-044 | Duplicidade e idempotência | trace id diferente não cria segunda prestação | **NÃO EXECUTADO** |
| T108-045 | Duplicidade e idempotência | reload não paga duas vezes | **NÃO EXECUTADO** |
| T108-046 | Duplicidade e idempotência | concorrência entre termos não soma mesmo lote | **NÃO EXECUTADO** |
| T108-047 | Duplicidade e idempotência | compensação só com novo receipt | **NÃO EXECUTADO** |
| T108-048 | Duplicidade e idempotência | outbox pending não reenvia cegamente | **NÃO EXECUTADO** |
| T108-049 | Alegações e contraposição | alegação de pagou não prova pagamento | **NÃO EXECUTADO** |
| T108-050 | Alegações e contraposição | alegação de não recebeu não prova fraude | **NÃO EXECUTADO** |
| T108-051 | Alegações e contraposição | silêncio não equivale a inadimplência | **NÃO EXECUTADO** |
| T108-052 | Alegações e contraposição | dois depoimentos ecoados não são provas independentes | **NÃO EXECUTADO** |
| T108-053 | Alegações e contraposição | parte pode pedir esclarecimento | **NÃO EXECUTADO** |
| T108-054 | Alegações e contraposição | resposta do NPC não assina por PC | **NÃO EXECUTADO** |
| T108-055 | Alegações e contraposição | contestação não anula receipt automaticamente | **NÃO EXECUTADO** |
| T108-056 | Alegações e contraposição | disputa mantém versões contrárias | **NÃO EXECUTADO** |
| T108-057 | Renegociação | pedido de novo prazo não altera prazo atual | **NÃO EXECUTADO** |
| T108-058 | Renegociação | aceite de uma parte não basta | **NÃO EXECUTADO** |
| T108-059 | Renegociação | aceite de nova revisão exige consentimentos | **NÃO EXECUTADO** |
| T108-060 | Renegociação | substituir bem não ocorre por narrativa | **NÃO EXECUTADO** |
| T108-061 | Renegociação | proposta de parcelamento não cria moeda | **NÃO EXECUTADO** |
| T108-062 | Renegociação | força maior alegada não extingue obrigação | **NÃO EXECUTADO** |
| T108-063 | Renegociação | retirada do consentimento bloqueia novo acordo | **NÃO EXECUTADO** |
| T108-064 | Renegociação | acordo encerrado não renasce por nova minuta | **NÃO EXECUTADO** |
| T108-065 | Autoridade e jurisdição | coordenador não emite mandado | **NÃO EXECUTADO** |
| T108-066 | Autoridade e jurisdição | coordenador não confisca bens | **NÃO EXECUTADO** |
| T108-067 | Autoridade e jurisdição | sanção não decorre de cronômetro | **NÃO EXECUTADO** |
| T108-068 | Autoridade e jurisdição | reputação não diminui por atraso presumido | **NÃO EXECUTADO** |
| T108-069 | Autoridade e jurisdição | reparação usa procedimento competente | **NÃO EXECUTADO** |
| T108-070 | Autoridade e jurisdição | representante sem mandato não vincula facção | **NÃO EXECUTADO** |
| T108-071 | Autoridade e jurisdição | mediador não atua como juiz do host | **NÃO EXECUTADO** |
| T108-072 | Autoridade e jurisdição | PC não é compelido por silêncio | **NÃO EXECUTADO** |
| T108-073 | Provas e ACL | relatório público não expõe fonte protegida | **NÃO EXECUTADO** |
| T108-074 | Provas e ACL | identidade real protegida não aparece no título | **NÃO EXECUTADO** |
| T108-075 | Provas e ACL | anexo privado não vai ao prompt | **NÃO EXECUTADO** |
| T108-076 | Provas e ACL | observação limitada não prova ausência | **NÃO EXECUTADO** |
| T108-077 | Provas e ACL | prova PROTECTED não vai para usuário PARTIES | **NÃO EXECUTADO** |
| T108-078 | Provas e ACL | log contém apenas resumo redigido | **NÃO EXECUTADO** |
| T108-079 | Provas e ACL | revogação ACL invalida view pendente | **NÃO EXECUTADO** |
| T108-080 | Provas e ACL | documento de terceiro não instrui LLM a punir | **NÃO EXECUTADO** |
| T108-081 | Conflitos e ordem | recibo contraditório para action id bloqueia | **NÃO EXECUTADO** |
| T108-082 | Conflitos e ordem | soma independente não depende de ordem | **NÃO EXECUTADO** |
| T108-083 | Conflitos e ordem | quarentena bloqueia novas transferências | **NÃO EXECUTADO** |
| T108-084 | Conflitos e ordem | reserva em uso não fica livre por prazo | **NÃO EXECUTADO** |
| T108-085 | Conflitos e ordem | dois contratos não gastam mesmo item | **NÃO EXECUTADO** |
| T108-086 | Conflitos e ordem | deadlock não autoriza confisco | **NÃO EXECUTADO** |
| T108-087 | Conflitos e ordem | outbox enviada não é confirmação | **NÃO EXECUTADO** |
| T108-088 | Conflitos e ordem | epoch divergente exige revisão | **NÃO EXECUTADO** |
| T108-089 | Branches e saves | branch diferente nunca compartilha receipt | **NÃO EXECUTADO** |
| T108-090 | Branches e saves | lineage diferente não comprova termo | **NÃO EXECUTADO** |
| T108-091 | Branches e saves | host_epoch antigo não valida estado novo | **NÃO EXECUTADO** |
| T108-092 | Branches e saves | checkpoint antigo precisa reconciliar | **NÃO EXECUTADO** |
| T108-093 | Branches e saves | save restore preserva histórico anterior | **NÃO EXECUTADO** |
| T108-094 | Branches e saves | campaign diferente isola contrato | **NÃO EXECUTADO** |
| T108-095 | Branches e saves | modpack novo invalida capability | **NÃO EXECUTADO** |
| T108-096 | Branches e saves | falsificação de nome de branch é rejeitada | **NÃO EXECUTADO** |
| T108-097 | Notificações e difusão | aviso preparado não é enviado | **NÃO EXECUTADO** |
| T108-098 | Notificações e difusão | aviso enviado não é entregue | **NÃO EXECUTADO** |
| T108-099 | Notificações e difusão | aviso entregue não é percebido | **NÃO EXECUTADO** |
| T108-100 | Notificações e difusão | percepção não é aceite | **NÃO EXECUTADO** |
| T108-101 | Notificações e difusão | ausência de resposta não é culpa | **NÃO EXECUTADO** |
| T108-102 | Notificações e difusão | comunicação a facção distante exige canal | **NÃO EXECUTADO** |
| T108-103 | Notificações e difusão | disputa de sigilo não vira publicidade | **NÃO EXECUTADO** |
| T108-104 | Notificações e difusão | correção futura não apaga notícia anterior | **NÃO EXECUTADO** |
| T108-105 | Falhas de serviços | registry fora do ar causa UNKNOWN | **NÃO EXECUTADO** |
| T108-106 | Falhas de serviços | timeout host não vira sucesso | **NÃO EXECUTADO** |
| T108-107 | Falhas de serviços | erro parse falha fechado | **NÃO EXECUTADO** |
| T108-108 | Falhas de serviços | sem LLM regras ainda funcionam | **NÃO EXECUTADO** |
| T108-109 | Falhas de serviços | falta owner registry bloqueia alterações | **NÃO EXECUTADO** |
| T108-110 | Falhas de serviços | evidence offline não declara quitação | **NÃO EXECUTADO** |
| T108-111 | Falhas de serviços | queue offline não duplica notificação | **NÃO EXECUTADO** |
| T108-112 | Falhas de serviços | clock source indisponível não avança prazo | **NÃO EXECUTADO** |
| T108-113 | Segurança adversarial | request grant_authority rejeitado | **NÃO EXECUTADO** |
| T108-114 | Segurança adversarial | request receipt_confirmed rejeitado | **NÃO EXECUTADO** |
| T108-115 | Segurança adversarial | request change_due_tick rejeitado | **NÃO EXECUTADO** |
| T108-116 | Segurança adversarial | request new_balance rejeitado | **NÃO EXECUTADO** |
| T108-117 | Segurança adversarial | request self_signed_host rejeitado | **NÃO EXECUTADO** |
| T108-118 | Segurança adversarial | prova textual com comando não executa | **NÃO EXECUTADO** |
| T108-119 | Segurança adversarial | payload extra rejeitado pelo schema | **NÃO EXECUTADO** |
| T108-120 | Segurança adversarial | resultado de LLM não é host receipt | **NÃO EXECUTADO** |
| T108-121 | Registro e auditoria | todo claim mantém autor | **NÃO EXECUTADO** |
| T108-122 | Registro e auditoria | todo receipt mantém action id | **NÃO EXECUTADO** |
| T108-123 | Registro e auditoria | versão de termo permanece consultável | **NÃO EXECUTADO** |
| T108-124 | Registro e auditoria | status calculado mantém referências | **NÃO EXECUTADO** |
| T108-125 | Registro e auditoria | alteração gera novo revision | **NÃO EXECUTADO** |
| T108-126 | Registro e auditoria | mecanismo de audit redige segredo | **NÃO EXECUTADO** |
| T108-127 | Registro e auditoria | correção contesta sem apagar ledger | **NÃO EXECUTADO** |
| T108-128 | Registro e auditoria | proposta mostra motivo determinístico | **NÃO EXECUTADO** |
| T108-129 | Conhecimento do mundo | NPC distante não sabe de pagamento | **NÃO EXECUTADO** |
| T108-130 | Conhecimento do mundo | narrador não vê contas PROTECTED | **NÃO EXECUTADO** |
| T108-131 | Conhecimento do mundo | mensagem de disputa não revela refúgio | **NÃO EXECUTADO** |
| T108-132 | Conhecimento do mundo | mudança de crença exige percepção | **NÃO EXECUTADO** |
| T108-133 | Conhecimento do mundo | alegação não altera cânone por ano | **NÃO EXECUTADO** |
| T108-134 | Conhecimento do mundo | mudança de quest exige autoridade separada | **NÃO EXECUTADO** |
| T108-135 | Conhecimento do mundo | origem do rumor permanece rastreável | **NÃO EXECUTADO** |
| T108-136 | Conhecimento do mundo | retificação não altera fato host-confirmed | **NÃO EXECUTADO** |
| T108-137 | Mecânicas e economy | não há transferência ao apenas monitorar | **NÃO EXECUTADO** |
| T108-138 | Mecânicas e economy | não cria ouro por acordo | **NÃO EXECUTADO** |
| T108-139 | Mecânicas e economy | não altera inventário pela LLM | **NÃO EXECUTADO** |
| T108-140 | Mecânicas e economy | não altera quest flags de cobrança | **NÃO EXECUTADO** |
| T108-141 | Mecânicas e economy | não modifica reputação nativa | **NÃO EXECUTADO** |
| T108-142 | Mecânicas e economy | não invoca patrulha de cobradores | **NÃO EXECUTADO** |
| T108-143 | Mecânicas e economy | não utiliza capabilities não testadas | **NÃO EXECUTADO** |
| T108-144 | Mecânicas e economy | não cria punição econômica automática | **NÃO EXECUTADO** |
| T108-145 | Condições de encerramento | candidato de entrega total não fecha sem condições | **NÃO EXECUTADO** |
| T108-146 | Condições de encerramento | revisão de contrato não altera receipt histórico | **NÃO EXECUTADO** |
| T108-147 | Condições de encerramento | quitado narrativamente não altera host | **NÃO EXECUTADO** |
| T108-148 | Condições de encerramento | terminado não apaga danos anteriores | **NÃO EXECUTADO** |
| T108-149 | Condições de encerramento | obrigação revogada exige autoridade | **NÃO EXECUTADO** |
| T108-150 | Condições de encerramento | disputa pode ficar inconclusiva | **NÃO EXECUTADO** |
| T108-151 | Condições de encerramento | força maior provada exige procedimento curado | **NÃO EXECUTADO** |
| T108-152 | Condições de encerramento | saldo incerto não vira zero | **NÃO EXECUTADO** |
| T108-153 | Prontidão de integração | teste sintético não comprova EEex | **NÃO EXECUTADO** |
| T108-154 | Prontidão de integração | teste build fixa obrigatório | **NÃO EXECUTADO** |
| T108-155 | Prontidão de integração | teste 2 clientes obrigatório | **NÃO EXECUTADO** |
| T108-156 | Prontidão de integração | teste compra e venda exige recibos | **NÃO EXECUTADO** |
| T108-157 | Prontidão de integração | teste clock DR deve ser no jogo | **NÃO EXECUTADO** |
| T108-158 | Prontidão de integração | teste restore exige epochs reais | **NÃO EXECUTADO** |
| T108-159 | Prontidão de integração | teste ACL redaction exige canais reais | **NÃO EXECUTADO** |
| T108-160 | Prontidão de integração | HIGH fail closed até autorização | **NÃO EXECUTADO** |

## 11. Critérios de pronto para eventual implementação

1. Conhecimento do contrato e aceite não vem de texto não autenticado; registry curado e ownership por build validado.
2. Relógio de jogo, tempo DR e checkpoints testados em saves divergentes.
3. Receipts de host testados com carga duplicada, perda de rede e falha parcial.
4. Relatórios e negociações testados com dois clientes sem PC autoassinado.
5. Acordos e monitoramento permanecem utilizáveis com LLM desligada.
6. POCs reais precisam ser catalogados separadamente. **Nenhum desses 160 testes de integração foi executado.**

### Integração DEC-109/C — Obrigações condicionais multipartes

Entrega parcial só habilita downstream se o limiar estiver committed na cláusula. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

A DEC-108 monitora prestações; DEC-110 distingue receipt de depósito, saldo custodiado e comprovante de liberação. Alegação de pagamento ou vencimento não cria direito unilateral de execução.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
