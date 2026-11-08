# 107 — Direito de resposta, contraditório e mediação voluntária de controvérsias reputacionais

**Decisão vinculante:** DEC-107/C APROVADA; ADR-0102. **Discovery:** v10.3 (2026-11-07). **Escopo técnico:** contratos candidatos, nenhuma implementação real de UI/engine/EEex/multiplayer comprovada. **Integridade:** DEC-060..106 e ADR-0001..0101 anteriores preservados.

## 1. Domínios e separação de responsabilidades

- `DisputeRegistry`: casos, partes, alegações, períodos, jurisdição/autorização, branch, proteção; NÃO adjudica verdade.
- `EvidenceService` DEC-077/089: submissões independentes, origem, famílias de fontes, controvérsias, classificação; NÃO divulga sem ACL.
- `ReplyService`: propõe e acompanha direito de resposta, janelas em tempo DR, canais, recibos independentes de entrega/percepção DEC-105.
- `RepresentationRegistry`: mandato curado, identidade de PC, poderes de representantes e revogações DEC-041/079/080.
- `MediationCoordinator`: convite voluntário, verificação de facilitador e riscos, proposta de sessão, agenda e exclusividade DEC-093/094.
- `TermsService`: minutas imutáveis, cláusulas tipadas, aceites explícitos por parte e revisão; proposta ≠ acordo committed.
- `ActionGateway/Host`: único caminho para efeitos mecânicos aprovados. Nenhum componente acima modifica a reputação nativa do motor, quest, inventário ou moeda.
- `NarrativeViewBuilder`: gera views por destinatário, mínimo necessário e redação; LLM redige apenas essa view, sem acesso a evidence corpus protegido.

## 2. Entidades canônicas e campos sugeridos

| Registro | Contratos mínimos | Estados ou cuidados |
|---|---|---|
| `DisputeCase` | `case_id`, `campaign`, `branch`, `lineage`, `host_epoch`, `checkpoint_epoch`, `parties[]`, `topic_claim_refs[]`, `policy_revision`, `revision` | `OPEN`, `CLOSED`, `QUARANTINED`; caso não prova acusação |
| `Party` | `persistent_id`, `type(PC/NPC/ORG/FAC)`, `representation_ref`, `owner`, `clearance` | PC não é representável sem consentimento explícito |
| `ClaimSubmission` | `claim_ref`, `submitter`, `claim_type`, `proof_status`, `source_family`, `classification`, `time_dr` | `ALLEGED`, `DISPUTED`, `CORROBORATED`, `HOST_CONFIRMED`; `ALLEGED` nunca vira verdade por volume |
| `ReplyInvitation` | `notice_id`, `to`, `reply_scope`, `audience`, `redacted_view_hash`, `reply_deadline_tick`, `delivery_channel` | `DRAFT` não é `DELIVERED`; `UNCERTAIN` reconcilia |
| `DeliveryReceipt` | `notice_id`, `delivery_status`, `perception_status`, `world_tick`, `proof_ref` | `DELIVERED` não implica `PERCEIVED`; ausência ≠ recusa |
| `ReplyRecord` | `reply_id`, `author`, `signing_principal`, `content_hash`, `reply_revision`, `filing_receipt`, `audience` | Nunca gerado em nome do PC, nunca confissão inferida |
| `MediationInvitation` | `invitation_id`, `facilitator_id`, `case_revision`, `party_consents`, `purpose`, `time_window` | Convite não obriga comparecimento |
| `FacilitatorAttestation` | `id`, `license/mandate`, `conflict_score` ou `conflict_flag`, `source`, `rev`, `risk` | Qualquer vínculo incompatível suspende proposta |
| `SessionProposal` | `session_id`, `location`, `start_end_dr`, `participants`, `resources`, `privacy`, `revision` | Só após consentimento de todos os afetados e disponibilidade real |
| `SettlementDraft` | `draft_id`, `revision`, `term_ids[]`, `source_case`, `privacy`, `author` | Não tem efeito vinculante; revisões exigem novos aceites |
| `TermAcceptance` | `party_id`, `term_id`, `term_revision`, `accepted_at`, `authorized_rep`, `consent_receipt` | Aceite per-term; silencioso nunca vale |
| `AgreementCommit` | `agreement_id`, `case_id`, `scope`, `acceptance_set`, `commit_receipt`, `expiry`, `idempotency_key` | No host sem provas, no replay após reload |
| `DisputeAudit` | `actor`, `event_type`, `case_revision`, `world_tick`, `evidence_refs`, `redacted_summary`, `status` | Audit restrito; não divulgar fontes protegidas |

## 3. Fluxo e estados operacionais

```text
DISPUTE_REQUESTED
  -> VALIDATE_PARTY_AND_REPRESENTATION
  -> PREPARE_SCOPED_NOTICE  [não envia]
  -> APPROVE_OUTBOX_DISPATCH [canal e audiência legítimos]
  -> RECONCILE_DELIVERY [WAITING/DELIVERED/PERCEIVED/UNCERTAIN]
  -> OPEN_REPLY_WINDOW [data DR observável]
  -> REPLY_FILED / REPLY_DECLINED / NO_REPLY_OBSERVED
  -> OFFER_VOLUNTARY_MEDIATION
  -> VERIFY_BOTH_CONSENTS_AND_FACILITATOR
  -> PROPOSE_SESSION [não convoca host por si]
  -> DRAFT_TERMS [não vinculante]
  -> COLLECT_PER_PARTY_PER_TERM_ACCEPTANCES
  -> REQUEST_COMMIT_GATE [não é commit]
  -> HOST_OR_AUTHORIZED_RECEIPT -> COMMITTED
```

`NO_REPLY_OBSERVED` não significa `REFUSED` e nem culpa. `REPLY_DECLINED` não impede defesa em outro canal, salvo regra curada e autorizada. Revogar participação impede novos compromissos, mas não apaga entrega ou termo já committed. Se ação enviada permanece `UNCERTAIN`, conter e reconciliar antes de repetir.

## 4. Regras determinísticas e incerteza

1. `case.phase/revision` e `policy.revision` são fixados antes de propor qualquer fluxo.
2. Principal autenticado, papéis e mandatos são consultados em registry **externo ao request**; request contém apenas referências e finalidade.
3. Prova do objeto da disputa não é construída pelo mediador. Pode permanecer controversa. Somente evidência curada e contestável pode sustentar parecer; nenhuma sentença automática.
4. Observar notícia não prova percepção, e percepção não prova aceitação ou concordância.
5. Se falta notificação: `PROPOSE_SCOPED_NOTICE`, não declarar contumácia.
6. Se notificação em trânsito: `WAIT_NOTICE_DELIVERY`.
7. Se notificação ambígua/`UNCERTAIN`: `QUARANTINED` e reconcile.
8. Se notificação recebida e resposta ausente: `OFFER_RIGHT_OF_REPLY`, preservando janela DR; prazo transcorrido oferece possível extensão, não punição automática.
9. Se resposta protocolada, ainda não há acordo: `OFFER_MEDIATION`; sem consenso das partes `WAIT_VOLUNTARY_CONSENT` ou encerramento legítimo.
10. Facilitador com potencial conflito: `REVIEW_FACILITATOR_CONFLICT` e não agendar sessões.
11. Assentimento de ambas as partes permite somente `PROPOSE_SESSION`, sujeito a agenda/capacidade.
12. Um `SettlementDraft` sem todos os consentimentos por termo e revisão mantém status `DRAFT`.
13. Uma pessoa pode concordar com correção factual e recusar retratação; não traduzir crença em aceite.
14. Publicação exige autorização de audiência distinta do consentimento de mediação; provas confidenciais podem permitir mediação privada, sem publicação.
15. Valores monetários, inventário, reputação, sanção, reparação, quests ou missão exigem poderes específicos e receipts do host.
16. Ordem de recebimento das provas não altera reconhecimento de independência; fonte ecoada é uma família.
17. `FROZEN` não progride janelas por relógio de parede; `PARTIAL`/`REALTIME` seguem tick autorizado.
18. Envio e receipt são persistidos em outbox com `case_id`, `revision`, `notice_id`, scope/epochs, destino e `idempotency_key`.
19. Impedir cruzamento de versões de mesma minuta após mudança unilateral: comparar `term_revision` com aceite.
20. Qualquer insuficiência de ACL, consentimento, fonte, host capability ou legitimidade leva a `DENIED`, `UNKNOWN` ou `QUARANTINED`; nunca executar por default.

## 5. Ameaças, política de privacidade e casos adversariais

| Vetor | Mitigação |
|---|---|
| Pedido inventa `mediation_approved=true` | Contract request com `additionalProperties:false`, registry autenticado independente |
| Incluir fonte em anexos públicos | Redação e ACL por campo e audience antes de prompts/serialização |
| Facilitador ligado a uma parte | Registrar conflito; bloquear sessões até revisão independente |
| NPC obrigado a declarar culpa | Falta `PartyAcceptance` = sem confissão, punição ou reparação |
| PC ausente assina por delegação narrativa | Owner grant explícito, por termo, específico, temporal |
| Uma guilda tem porta-voz sem poderes | Mandate scope por obrigação; não aceitar transferência financeira |
| Dossiê contém duas declarações de mesma fonte | Source-family dedup; corroboration não inferida |
| `UNCERTAIN` após envio | Fence/outbox reconcile; sem retry cego |
| Jogador restaura save e reapresenta acordo | Branch, checkpoint, epochs, ledger e CAS impedem duplicação |
| Mediação ameaça testemunha/refúgio | Fail closed, no private source route or location in view/logs |
| Consentimento de mediação tratado como aceite de termos | Registros e assinaturas diferentes |
| Controvérsia gera reputação negativa por silêncio | Proibir regra; silêncio não é culpa |

## 6. Integração com decisões já aprovadas

- DEC-030: reputação contextual pode receber **novas propostas** de revisão por terceiros, nunca modificação global.
- DEC-041/042/045/046: PC/party, ausência, consentimento e autoridade individual.
- DEC-064/065: memória e falibilidade não são apagadas por mediação.
- DEC-075/076/077/089/090: autoria legítima, identidade, evidência, contradições, fontes independentes e view redigida.
- DEC-078–082: mediação não substitui procedimento judicial, jurisdição, mandado ou reparação.
- DEC-083–086: sigilo de testemunhas e informações operacionais.
- DEC-087/088: lealdades e compromissos não mudam automaticamente.
- DEC-091–095: propostas, cancelamento, reservas, Sagas de reparação, `UNCERTAIN` e host receipts.
- DEC-096/097/103–105: tempo DR, difusão informacional causal, correções, reputações e fatos distintos.
- DEC-099–102: ownership e observações de quests sem escrita indevida.
- DEC-106: reabilitação é resultado possível e separado de mediação.

## 7. Matriz de validação candidata — INTEGRAÇÃO NÃO EXECUTADA

Casos `T107-001` a `T107-152` são candidatos especificados, não resultados observados no BG2:EE/EEex. Avaliador/fixture unitários são sintéticos e não executam I/O ou ações de jogo.

## 8. Cenários T107-001..152 (TODOS NÃO EXECUTADOS NO MOTOR)

| ID | Área | Cenário | Status |
|---|---|---|---|
| T107-001 | Legitimidade e registro de caso | caso inexistente não vira disputa | **NÃO EXECUTADO** |
| T107-002 | Legitimidade e registro de caso | um caso de outro branch fica isolado | **NÃO EXECUTADO** |
| T107-003 | Legitimidade e registro de caso | revisão stale bloqueia nova etapa | **NÃO EXECUTADO** |
| T107-004 | Legitimidade e registro de caso | parte contestada não vira culpada | **NÃO EXECUTADO** |
| T107-005 | Legitimidade e registro de caso | status CLOSED impede nova mediação | **NÃO EXECUTADO** |
| T107-006 | Legitimidade e registro de caso | identidades persistentes não se confundem com nomes iguais | **NÃO EXECUTADO** |
| T107-007 | Legitimidade e registro de caso | requerente não cria poderes ao pedir abertura | **NÃO EXECUTADO** |
| T107-008 | Legitimidade e registro de caso | mandato expirado não representa guilda | **NÃO EXECUTADO** |
| T107-009 | Notificação e contraditório | notificação preparada não equivale a enviada | **NÃO EXECUTADO** |
| T107-010 | Notificação e contraditório | notificação enviada não equivale a entregue | **NÃO EXECUTADO** |
| T107-011 | Notificação e contraditório | entrega não implica percepção | **NÃO EXECUTADO** |
| T107-012 | Notificação e contraditório | canal impossível não prova ciência | **NÃO EXECUTADO** |
| T107-013 | Notificação e contraditório | período de resposta segue tempo DR | **NÃO EXECUTADO** |
| T107-014 | Notificação e contraditório | no FROZEN prazo não progride por relógio real | **NÃO EXECUTADO** |
| T107-015 | Notificação e contraditório | ausência de resposta não demonstra culpa | **NÃO EXECUTADO** |
| T107-016 | Notificação e contraditório | pedido de extensão não pune parte ausente | **NÃO EXECUTADO** |
| T107-017 | Resposta e autoria | LLM não redige confissão como fato sem assinatura | **NÃO EXECUTADO** |
| T107-018 | Resposta e autoria | PC ausente não é forçado a responder | **NÃO EXECUTADO** |
| T107-019 | Resposta e autoria | recusa expressa é distinta de falta de entrega | **NÃO EXECUTADO** |
| T107-020 | Resposta e autoria | resposta privada não torna conteúdo público | **NÃO EXECUTADO** |
| T107-021 | Resposta e autoria | resposta submetida mantém revision e receipt | **NÃO EXECUTADO** |
| T107-022 | Resposta e autoria | assinatura de NPC não assume assinatura de PC | **NÃO EXECUTADO** |
| T107-023 | Resposta e autoria | manifestação em outro idioma exige canal compatível | **NÃO EXECUTADO** |
| T107-024 | Resposta e autoria | resposta a uma alegação não confessa outras | **NÃO EXECUTADO** |
| T107-025 | Consentimentos | mediação só proposta com voluntariedade | **NÃO EXECUTADO** |
| T107-026 | Consentimentos | consentimento de uma parte não supre outra | **NÃO EXECUTADO** |
| T107-027 | Consentimentos | consentimento revogado impede novas sessões | **NÃO EXECUTADO** |
| T107-028 | Consentimentos | consentimento de mediação não é aceite de acordo | **NÃO EXECUTADO** |
| T107-029 | Consentimentos | aceite de minuta anterior invalida após revisão | **NÃO EXECUTADO** |
| T107-030 | Consentimentos | mandato de representação não é consentimento de PC | **NÃO EXECUTADO** |
| T107-031 | Consentimentos | silêncio não é consentimento | **NÃO EXECUTADO** |
| T107-032 | Consentimentos | coação detectada bloqueia compromisso | **NÃO EXECUTADO** |
| T107-033 | Facilitador e imparcialidade | facilitador autor de acusação é conflito | **NÃO EXECUTADO** |
| T107-034 | Facilitador e imparcialidade | beneficiário direto não media sem revisão | **NÃO EXECUTADO** |
| T107-035 | Facilitador e imparcialidade | facilitador ligado a testemunha protegida requer proteção | **NÃO EXECUTADO** |
| T107-036 | Facilitador e imparcialidade | conflito não é curado por solicitação do interessado | **NÃO EXECUTADO** |
| T107-037 | Facilitador e imparcialidade | desconhecer filiação resulta em revisão pendente | **NÃO EXECUTADO** |
| T107-038 | Facilitador e imparcialidade | facilitador não decide veracidade sem provas | **NÃO EXECUTADO** |
| T107-039 | Facilitador e imparcialidade | troca de facilitador versiona sessão | **NÃO EXECUTADO** |
| T107-040 | Facilitador e imparcialidade | facilitador não tem authority sobre ouro do host | **NÃO EXECUTADO** |
| T107-041 | Evidências | alegação não se torna fato apenas por registro | **NÃO EXECUTADO** |
| T107-042 | Evidências | depoimentos ecoados não corroboram independentemente | **NÃO EXECUTADO** |
| T107-043 | Evidências | documentos contestados permanecem contestados | **NÃO EXECUTADO** |
| T107-044 | Evidências | prova protegida não é transmitida em convite | **NÃO EXECUTADO** |
| T107-045 | Evidências | contradições não são apagadas por relato final | **NÃO EXECUTADO** |
| T107-046 | Evidências | prova parcial não autoriza sentença | **NÃO EXECUTADO** |
| T107-047 | Evidências | fonte que não poderia saber não é confirmada | **NÃO EXECUTADO** |
| T107-048 | Evidências | acordar não altera fatos do mundo | **NÃO EXECUTADO** |
| T107-049 | ACL e sigilo | público não recebe evidência PROTECTED | **NÃO EXECUTADO** |
| T107-050 | ACL e sigilo | pseudônimo não revela identidade real | **NÃO EXECUTADO** |
| T107-051 | ACL e sigilo | refúgio não consta em metadado público | **NÃO EXECUTADO** |
| T107-052 | ACL e sigilo | resumo redigido não inclui anexos privados | **NÃO EXECUTADO** |
| T107-053 | ACL e sigilo | log não contém depoimento confidencial | **NÃO EXECUTADO** |
| T107-054 | ACL e sigilo | prompt não inclui provas não autorizadas | **NÃO EXECUTADO** |
| T107-055 | ACL e sigilo | cache de uma audiência não vaza para outra | **NÃO EXECUTADO** |
| T107-056 | ACL e sigilo | revogação ACL invalida views pendentes | **NÃO EXECUTADO** |
| T107-057 | Agendamento e geografia | participantes não teleportam para sessão | **NÃO EXECUTADO** |
| T107-058 | Agendamento e geografia | NPC offscreen precisa de deslocamento | **NÃO EXECUTADO** |
| T107-059 | Agendamento e geografia | duas sessões não usam mesmo NPC simultaneamente | **NÃO EXECUTADO** |
| T107-060 | Agendamento e geografia | local protegido não é revelado pela agenda | **NÃO EXECUTADO** |
| T107-061 | Agendamento e geografia | conflito de recursos bloqueia sessão | **NÃO EXECUTADO** |
| T107-062 | Agendamento e geografia | FROZEN impede avanço de prazo independente | **NÃO EXECUTADO** |
| T107-063 | Agendamento e geografia | evento em outro DR não entra em disputa atual | **NÃO EXECUTADO** |
| T107-064 | Agendamento e geografia | fuso fictício não é inferido de relógio real | **NÃO EXECUTADO** |
| T107-065 | Compromissos e termos | rascunho não transfere dinheiro | **NÃO EXECUTADO** |
| T107-066 | Compromissos e termos | termo exige partes claramente determinadas | **NÃO EXECUTADO** |
| T107-067 | Compromissos e termos | compromissos por termo possuem aceites independentes | **NÃO EXECUTADO** |
| T107-068 | Compromissos e termos | alteração de termo exige novo aceite | **NÃO EXECUTADO** |
| T107-069 | Compromissos e termos | reparação material não tem valor automático | **NÃO EXECUTADO** |
| T107-070 | Compromissos e termos | pedido de desculpas não é escrito por NPC ausente | **NÃO EXECUTADO** |
| T107-071 | Compromissos e termos | retração pública exige aprovação separada | **NÃO EXECUTADO** |
| T107-072 | Compromissos e termos | acordo não equivale a perdão | **NÃO EXECUTADO** |
| T107-073 | Host e efeitos mecânicos | não altera reputação nativa sem receipt | **NÃO EXECUTADO** |
| T107-074 | Host e efeitos mecânicos | não muda flag de quest sem ownership | **NÃO EXECUTADO** |
| T107-075 | Host e efeitos mecânicos | não cria moeda | **NÃO EXECUTADO** |
| T107-076 | Host e efeitos mecânicos | não transfere item por texto | **NÃO EXECUTADO** |
| T107-077 | Host e efeitos mecânicos | não aplica sanção por silêncio | **NÃO EXECUTADO** |
| T107-078 | Host e efeitos mecânicos | não gera NPC mediador sem capability | **NÃO EXECUTADO** |
| T107-079 | Host e efeitos mecânicos | não altera score de facção automaticamente | **NÃO EXECUTADO** |
| T107-080 | Host e efeitos mecânicos | nenhuma proposta é commit automático | **NÃO EXECUTADO** |
| T107-081 | Idempotência e retry | duas solicitações idênticas criam proposta estável | **NÃO EXECUTADO** |
| T107-082 | Idempotência e retry | trace ID não altera chave de dedup | **NÃO EXECUTADO** |
| T107-083 | Idempotência e retry | notificação pending não é reenviada | **NÃO EXECUTADO** |
| T107-084 | Idempotência e retry | notificação committed não é duplicada | **NÃO EXECUTADO** |
| T107-085 | Idempotência e retry | DISPATCHED permanece em reconciliação | **NÃO EXECUTADO** |
| T107-086 | Idempotência e retry | UNCERTAIN impede retry cego | **NÃO EXECUTADO** |
| T107-087 | Idempotência e retry | novo draft revision muda escopo de aceites | **NÃO EXECUTADO** |
| T107-088 | Idempotência e retry | save/load não multiplica reparações | **NÃO EXECUTADO** |
| T107-089 | Relógio, branch e checkpoints | outra campanha não compartilha casos | **NÃO EXECUTADO** |
| T107-090 | Relógio, branch e checkpoints | outro branch não herda consentimento | **NÃO EXECUTADO** |
| T107-091 | Relógio, branch e checkpoints | lineage antigo não autoriza presente | **NÃO EXECUTADO** |
| T107-092 | Relógio, branch e checkpoints | host epoch divergente bloqueia | **NÃO EXECUTADO** |
| T107-093 | Relógio, branch e checkpoints | checkpoint epoch divergente bloqueia | **NÃO EXECUTADO** |
| T107-094 | Relógio, branch e checkpoints | relógio DR não retrocede por solicitação | **NÃO EXECUTADO** |
| T107-095 | Relógio, branch e checkpoints | build atualizada exige recertificação capability | **NÃO EXECUTADO** |
| T107-096 | Relógio, branch e checkpoints | modpack divergente não usa mapeamento antigo | **NÃO EXECUTADO** |
| T107-097 | Justiça e instituições | mediação voluntária não produz mandado | **NÃO EXECUTADO** |
| T107-098 | Justiça e instituições | jurisdição inexistente não é inventada | **NÃO EXECUTADO** |
| T107-099 | Justiça e instituições | ordem judicial não é substituída por minuta | **NÃO EXECUTADO** |
| T107-100 | Justiça e instituições | sanção requer decisor competente | **NÃO EXECUTADO** |
| T107-101 | Justiça e instituições | vítima pode contestar reparação | **NÃO EXECUTADO** |
| T107-102 | Justiça e instituições | acordo privado não altera lei | **NÃO EXECUTADO** |
| T107-103 | Justiça e instituições | representante sem mandato não compromete guilda | **NÃO EXECUTADO** |
| T107-104 | Justiça e instituições | recusa de mediação não é evidência de delito | **NÃO EXECUTADO** |
| T107-105 | Memória e crenças | receber resposta não obriga acreditar | **NÃO EXECUTADO** |
| T107-106 | Memória e crenças | NPC mantém memória de acusação anterior | **NÃO EXECUTADO** |
| T107-107 | Memória e crenças | correção recebida não apaga rumor | **NÃO EXECUTADO** |
| T107-108 | Memória e crenças | partes podem continuar discordando | **NÃO EXECUTADO** |
| T107-109 | Memória e crenças | não inventar lembrança de encontro inexistente | **NÃO EXECUTADO** |
| T107-110 | Memória e crenças | desculpa aceita por um NPC não vincula facção | **NÃO EXECUTADO** |
| T107-111 | Memória e crenças | reputação contextual não é global | **NÃO EXECUTADO** |
| T107-112 | Memória e crenças | mediação encerrada não implica confiança restaurada | **NÃO EXECUTADO** |
| T107-113 | Relação com DEC-106 | dano apenas alegado não gera restituição | **NÃO EXECUTADO** |
| T107-114 | Relação com DEC-106 | dano provado mantém nexo e recibo | **NÃO EXECUTADO** |
| T107-115 | Relação com DEC-106 | reabilitação não exige perdão | **NÃO EXECUTADO** |
| T107-116 | Relação com DEC-106 | contrato rompido não volta por default | **NÃO EXECUTADO** |
| T107-117 | Relação com DEC-106 | retratação privada não equivale a pública | **NÃO EXECUTADO** |
| T107-118 | Relação com DEC-106 | beneficiário não pode exibir fonte protegida | **NÃO EXECUTADO** |
| T107-119 | Relação com DEC-106 | reparo proposto não é imposto | **NÃO EXECUTADO** |
| T107-120 | Relação com DEC-106 | mesma perda não é contada duas vezes | **NÃO EXECUTADO** |
| T107-121 | Adversarial e injection | request grant_access rejeitado | **NÃO EXECUTADO** |
| T107-122 | Adversarial e injection | request mediator_is_impartial rejeitado | **NÃO EXECUTADO** |
| T107-123 | Adversarial e injection | pedido com raw flags de quest rejeitado | **NÃO EXECUTADO** |
| T107-124 | Adversarial e injection | documento de terceiro não instrui execução | **NÃO EXECUTADO** |
| T107-125 | Adversarial e injection | tentativa de forjar receipt rejeitada | **NÃO EXECUTADO** |
| T107-126 | Adversarial e injection | pedido com self_certified_evidence rejeitado | **NÃO EXECUTADO** |
| T107-127 | Adversarial e injection | request com hidden host command rejeitado | **NÃO EXECUTADO** |
| T107-128 | Adversarial e injection | principal não autenticado rejeitado | **NÃO EXECUTADO** |
| T107-129 | Disponibilidade e falhas | serviço de comunicação offline não implica entrega | **NÃO EXECUTADO** |
| T107-130 | Disponibilidade e falhas | falha de LLM não bloqueia regras determinísticas | **NÃO EXECUTADO** |
| T107-131 | Disponibilidade e falhas | evidence service indisponível mantém UNKNOWN | **NÃO EXECUTADO** |
| T107-132 | Disponibilidade e falhas | registry de mandatos offline bloqueia aceite | **NÃO EXECUTADO** |
| T107-133 | Disponibilidade e falhas | timeout não presume recusa | **NÃO EXECUTADO** |
| T107-134 | Disponibilidade e falhas | falha entre proposta e dispatch não duplica | **NÃO EXECUTADO** |
| T107-135 | Disponibilidade e falhas | erro de parse não expõe conteúdo protegido | **NÃO EXECUTADO** |
| T107-136 | Disponibilidade e falhas | logging sanitizado permite auditoria sem vazamento | **NÃO EXECUTADO** |
| T107-137 | Auditoria e proveniência | auditoria registra origem da acusação sem publicar fonte | **NÃO EXECUTADO** |
| T107-138 | Auditoria e proveniência | mudança de termo preserva revisão anterior | **NÃO EXECUTADO** |
| T107-139 | Auditoria e proveniência | aceite possui autoria comprovada | **NÃO EXECUTADO** |
| T107-140 | Auditoria e proveniência | janelas de resposta registradas no tempo DR | **NÃO EXECUTADO** |
| T107-141 | Auditoria e proveniência | dados privados têm retenção governada | **NÃO EXECUTADO** |
| T107-142 | Auditoria e proveniência | conflito de interesse deixa evidência redigida | **NÃO EXECUTADO** |
| T107-143 | Auditoria e proveniência | relato de LLM é marcado sugestão | **NÃO EXECUTADO** |
| T107-144 | Auditoria e proveniência | status final preserva divergências | **NÃO EXECUTADO** |
| T107-145 | Prontidão e aceite | somente teste local sintético não prova EEex | **NÃO EXECUTADO** |
| T107-146 | Prontidão e aceite | UI de diálogo exige POC dedicado | **NÃO EXECUTADO** |
| T107-147 | Prontidão e aceite | host com dois clientes requer prova de sincronização | **NÃO EXECUTADO** |
| T107-148 | Prontidão e aceite | capabilities dependem de build/modpack | **NÃO EXECUTADO** |
| T107-149 | Prontidão e aceite | reputação mecânica requer teste isolado | **NÃO EXECUTADO** |
| T107-150 | Prontidão e aceite | pagamento requer teste host de transação | **NÃO EXECUTADO** |
| T107-151 | Prontidão e aceite | recuperação após save/load exige receipt | **NÃO EXECUTADO** |
| T107-152 | Prontidão e aceite | política HIGH falha fechada sem aprovação | **NÃO EXECUTADO** |

## 9. Limitações da demonstração

Os testes Python e fixtures são puramente sintéticos: não possuem referência real a flags, mapas, inventário, NPC, canal de diálogo ou local do BG2:EE/EEex. O esquema candidato valida apenas dados de laboratório, não autentica permissões em produção. Abrir o direito de resposta é uma oportunidade narrativa, não uma sentença ou um cumprimento imposto.

### Integração DEC-108/C — Cumprimento de obrigações e monitoramento não coercitivo

Minuta, aceite por termo e acordo committed são pré-condições distintas da prestação; silêncio não é descumprimento provado. Fonte: ADR-0103/doc.108; claims ≠ comprovantes, prazos DR ≠ culpa, status `UNCERTAIN` bloqueia nova ação, sem mutações do host. POCs BG2:EE/EEex e T108-001..160 **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Mediação e aceite por termo são precondições separadas de cumprimento. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Mediação pode propor custódia como cláusula, mas assinatura de acordo não comprova depósito, consentimento do titular ou liberação.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
