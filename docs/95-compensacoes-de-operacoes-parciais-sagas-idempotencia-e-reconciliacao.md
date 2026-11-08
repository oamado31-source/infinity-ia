# DEC-095 — Sagas e compensação segura de operações parcialmente concluídas

**Estado:** proposta técnica decorrente de DEC-095/C, APROVADA SOMENTE EM ARQUITETURA (v9.1), **sem implementação ou POC do jogo**. Fonte decisória: `decisions/ADR-0090-compensacao-segura-de-operacoes-parciais-com-sagas-rastreaveis.md`.

## 1. Objetivo e não objetivos

- Suportar operação composta com efeitos parciais host-confirmados, falhas, propostas de compensação e auditoria.
- Nunca presumir transação distribuída, rollback de história, comando EEex cancelável, disponibilidade de NPC, magia de ressuscitar, restauro de inventário ou reembolso automático.
- Separar recuperação de reservas DEC-094 de compensação de etapas DEC-095 e reparação jurídica DEC-081.

## 2. Contratos candidatos (lógicos, não APIs do jogo)

| Contrato | Campos mínimos | Garantia |
|---|---|---|
| `SagaPlan` | `saga_id`, `operation_id`, `campaign_id`, `branch_id`, `revision`, `host_epoch`, `knowledge_pack_pin`, `checkpoint_ref`, `owner_ids` | escopo e imutabilidade das revisões |
| `SagaStep` | `step_id`, `depends_on[]`, `resource_claims[]`, `required_receipt_type`, `risk_class`, `state`, `compensability` | estado distinto de ação executada |
| `StepEffect` | `effect_id`, `source_step_id`, `host_receipt_id`, `effect_kind`, `observed_at_dr`, `owner`, `immutable_event_ref` | efeito confirmado não desaparece |
| `CompensationPolicy` | `policy_id@rev`, `step_kind`, `prerequisites[]`, `required_authorities[]`, `required_consents[]`, `risk_class`, `max_actions` | reversibilidade e limites explícitos |
| `CompensationProposal` | `compensation_id`, `step_effect_refs[]`, `new_action`, `justification`, `owner`, `expires_at`, `plan_rev` | proposta sem efeito mecânico |
| `CompensationAttempt` | `idempotency_key`, `dispatch_id`, `epoch`, `outbox_ref`, `state`, `receipt_ref`, `checkpoint_ref` | dedup e reconciliação |
| `SagaJournal` | `event_seq`, `timestamp_dr`, `recorded_at`, `actor_id`, `event_type`, `evidence_refs[]`, `acl`, `hash` | trilha append-only auditável |

## 3. Estados

| Camada | Estados relevantes | Regra |
|---|---|---|
| Etapa | PROPOSED → VALIDATED → AUTHORIZED → DISPATCH_PENDING → DISPATCHED → HOST_CONFIRMED; exceções FAILED_VERIFIED, UNCERTAIN | nem despacho nem timeout atestam efeito |
| Compensação | PROPOSED → VALIDATED → AWAITING_CONSENT → AUTHORIZED → DISPATCH_PENDING → DISPATCHED → HOST_CONFIRMED; exceções REJECTED, UNCERTAIN, FAILED_VERIFIED | compensação é nova ação, não apagar etapa |
| Saga | ACTIVE, PARTIALLY_COMPLETED, COMPENSATION_PROPOSED, COMPENSATING, PARTIALLY_COMPENSATED, COMPENSATED_WITH_RESIDUAL_EFFECTS, COMPLETED, ESCALATED, UNCERTAIN | falha com residuais é resultado legítimo |

Estados ilustrativos e transições pendentes de SPEC. A implementação deve proibir transições regressivas sem ledger de correção explicitamente autorizado.

## 4. Fluxo determinístico proposto

```text
ON verified operation interruption:
  1. load SagaPlan revision and immutable host receipts;
  2. freeze new dependent dispatches, not the engine BG2:EE;
  3. classify each completed step by *validated* compensation policy;
  4. exclude non-compensable/uncertain effects from automatic compensation;
  5. generate candidate compensation DAG respecting dependencies and ownership;
  6. validate current branch/checkpoint/epoch, balances, risk and consent;
  7. emit proposal; require explicit approvals where appropriate;
  8. dispatch only allowlisted actions through host Action Gateway;
  9. record effect only on verified receipt; reconcile UNCERTAIN without blind retry;
 10. finalize with residual effects and outstanding obligations, not global rollback.
```

## 5. Invariantes

- **I095-01:** a ação compensatória é um novo evento; `StepEffect` original imutável.
- **I095-02:** `UNCERTAIN` bloqueia reenvio e reutilização sem reconciliação confiável.
- **I095-03:** KPack/cânone por ano DR nunca é regravado por Saga.
- **I095-04:** não transformar `Authorized` em `HostConfirmed` sem recibo.
- **I095-05:** reembolso exige titular, saldo, regra e confirmação; não gerar itens ou ouro.
- **I095-06:** morte, memória, conhecimento obtido e passagem de tempo não são desfeitos.
- **I095-07:** autorização material/consentimento não é delegada à LLM.
- **I095-08:** restore e fork invalidam jobs/autorizações vinculados a epoch antiga.
- **I095-09:** resultado pode ser parcial sem corromper histórico nem travar operação independente.
- **I095-10:** logs/telemetria ocultam informações privadas por DEC-083–090.

## 6. Exemplo de Saga de escolta (fictício)

| Etapa | Resultado confirmado | Compensação candidata | Limite |
|---|---|---|---|
| S1 — assinar contrato | acordo confirmado | rescisão negociada | não apagar assinatura passada |
| S2 — pagar adiantamento | 10 moedas removidas em receipt host | reembolso se previsto, houver saldo e consentimento | novo recibo obrigatório |
| S3 — iniciar percurso | trecho percorrido e visto por NPCs | cancelar trechos futuros | não desfazer geografia, tempo ou memória |
| S4 — entregar testemunha | não executada | nenhuma | não marcar como sucesso |

Falha de S3 não devolve S2 automaticamente; reembolso é nova transação. Se recibo não chegou, não reenviar pagamento ou reembolso por timeout. A história da escolta continua registrada mesmo quando o acordo termina.

## 7. Segurança e plano de testes

96 cenários candidatos abaixo, **NÃO EXECUTADOS**. POCs necessárias: persistência/outbox, Saga com host mock, adapter/EEex em build conhecida, perda de conexão, save/load e host + dois clientes. Nenhuma chamada foi feita ao jogo real.

| ID | Grupo | Cenário candidato | Estado |
|---|---|---|---|
| T095-01 | Identidade/etapas | saga inclui campanha e branch | **NÃO EXECUTADO** |
| T095-02 | Identidade/etapas | revision incorreta bloqueia etapa | **NÃO EXECUTADO** |
| T095-03 | Identidade/etapas | host epoch divergente | **NÃO EXECUTADO** |
| T095-04 | Identidade/etapas | ordem DAG válida | **NÃO EXECUTADO** |
| T095-05 | Identidade/etapas | ciclo DAG rejeitado | **NÃO EXECUTADO** |
| T095-06 | Identidade/etapas | ID de etapa duplicado | **NÃO EXECUTADO** |
| T095-07 | Identidade/etapas | etapa sem owner | **NÃO EXECUTADO** |
| T095-08 | Identidade/etapas | etapa sem fonte de autorização | **NÃO EXECUTADO** |
| T095-09 | Identidade/etapas | dependência anterior pendente | **NÃO EXECUTADO** |
| T095-10 | Identidade/etapas | etapa em branch arquivado | **NÃO EXECUTADO** |
| T095-11 | Identidade/etapas | marco mecânico não comprovado | **NÃO EXECUTADO** |
| T095-12 | Identidade/etapas | revisão obsoleta após replanejamento | **NÃO EXECUTADO** |
| T095-13 | Estados e provas | proposta não produz efeito | **NÃO EXECUTADO** |
| T095-14 | Estados e provas | validado não implica autorizado | **NÃO EXECUTADO** |
| T095-15 | Estados e provas | autorizado não implica dispatch | **NÃO EXECUTADO** |
| T095-16 | Estados e provas | dispatch não implica sucesso | **NÃO EXECUTADO** |
| T095-17 | Estados e provas | receipt confirmado aplica efeito uma vez | **NÃO EXECUTADO** |
| T095-18 | Estados e provas | receipt negativo mantém failure | **NÃO EXECUTADO** |
| T095-19 | Estados e provas | receipt inválido rejeitado | **NÃO EXECUTADO** |
| T095-20 | Estados e provas | receipt em outra sessão rejeitado | **NÃO EXECUTADO** |
| T095-21 | Estados e provas | resultado UNCERTAIN preservado | **NÃO EXECUTADO** |
| T095-22 | Estados e provas | timeout não vira failure | **NÃO EXECUTADO** |
| T095-23 | Estados e provas | receipt duplicado dedup | **NÃO EXECUTADO** |
| T095-24 | Estados e provas | prova parcial não vira total | **NÃO EXECUTADO** |
| T095-25 | Classificação de compensação | etapa COMPENSABLE com política | **NÃO EXECUTADO** |
| T095-26 | Classificação de compensação | CONDITIONALLY requer condições | **NÃO EXECUTADO** |
| T095-27 | Classificação de compensação | NON_COMPENSABLE permanece | **NÃO EXECUTADO** |
| T095-28 | Classificação de compensação | UNKNOWN sem efeito por default | **NÃO EXECUTADO** |
| T095-29 | Classificação de compensação | proteção de morte confirmada | **NÃO EXECUTADO** |
| T095-30 | Classificação de compensação | segredo já divulgado não apagado | **NÃO EXECUTADO** |
| T095-31 | Classificação de compensação | distância percorrida permanece | **NÃO EXECUTADO** |
| T095-32 | Classificação de compensação | terceiros já informados permanecem | **NÃO EXECUTADO** |
| T095-33 | Classificação de compensação | danos reputacionais não retcon | **NÃO EXECUTADO** |
| T095-34 | Classificação de compensação | compensação social exige autoridade | **NÃO EXECUTADO** |
| T095-35 | Classificação de compensação | compensação sem cobertura negada | **NÃO EXECUTADO** |
| T095-36 | Classificação de compensação | novo evento separado do original | **NÃO EXECUTADO** |
| T095-37 | Consentimentos e recursos | PC não consente restituição | **NÃO EXECUTADO** |
| T095-38 | Consentimentos e recursos | ouro do terceiro indisponível | **NÃO EXECUTADO** |
| T095-39 | Consentimentos e recursos | inventário host diverge | **NÃO EXECUTADO** |
| T095-40 | Consentimentos e recursos | escopo de delegação insuficiente | **NÃO EXECUTADO** |
| T095-41 | Consentimentos e recursos | consentimento revogado antes de despacho | **NÃO EXECUTADO** |
| T095-42 | Consentimentos e recursos | dois owners têm decisão divergente | **NÃO EXECUTADO** |
| T095-43 | Consentimentos e recursos | póliza exige competência inexistente | **NÃO EXECUTADO** |
| T095-44 | Consentimentos e recursos | risk HIGH sem gate | **NÃO EXECUTADO** |
| T095-45 | Consentimentos e recursos | compensação sem saldo | **NÃO EXECUTADO** |
| T095-46 | Consentimentos e recursos | reserva concorrente já consumiu recurso | **NÃO EXECUTADO** |
| T095-47 | Consentimentos e recursos | reembolso autorizado gera novo receipt | **NÃO EXECUTADO** |
| T095-48 | Consentimentos e recursos | não duplicar item em reembolso | **NÃO EXECUTADO** |
| T095-49 | Sequência e falhas | saga interrompida propõe ordem reversa | **NÃO EXECUTADO** |
| T095-50 | Sequência e falhas | etapa paralela em DAG | **NÃO EXECUTADO** |
| T095-51 | Sequência e falhas | dependência exige inversão distinta | **NÃO EXECUTADO** |
| T095-52 | Sequência e falhas | compensação 1 falha | **NÃO EXECUTADO** |
| T095-53 | Sequência e falhas | compensação 2 UNCERTAIN | **NÃO EXECUTADO** |
| T095-54 | Sequência e falhas | retentativa sem receipt bloqueada | **NÃO EXECUTADO** |
| T095-55 | Sequência e falhas | falha técnica não dá rollback | **NÃO EXECUTADO** |
| T095-56 | Sequência e falhas | compensação recursiva bloqueada | **NÃO EXECUTADO** |
| T095-57 | Sequência e falhas | nova proposta após fracasso parcial | **NÃO EXECUTADO** |
| T095-58 | Sequência e falhas | saga final com efeitos residuais | **NÃO EXECUTADO** |
| T095-59 | Sequência e falhas | operações independentes avançam | **NÃO EXECUTADO** |
| T095-60 | Sequência e falhas | aborto preserva fatos confirmados | **NÃO EXECUTADO** |
| T095-61 | Recuperação, outbox e idempotência | replay idempotente do saga_id | **NÃO EXECUTADO** |
| T095-62 | Recuperação, outbox e idempotência | compensation_id único por epoch | **NÃO EXECUTADO** |
| T095-63 | Recuperação, outbox e idempotência | crash antes do envio | **NÃO EXECUTADO** |
| T095-64 | Recuperação, outbox e idempotência | crash após envio sem receipt | **NÃO EXECUTADO** |
| T095-65 | Recuperação, outbox e idempotência | restart invalida token obsoleto | **NÃO EXECUTADO** |
| T095-66 | Recuperação, outbox e idempotência | outbox reconcilia acknowledgment | **NÃO EXECUTADO** |
| T095-67 | Recuperação, outbox e idempotência | fencing impede worker antigo | **NÃO EXECUTADO** |
| T095-68 | Recuperação, outbox e idempotência | checkpoint difere do save host | **NÃO EXECUTADO** |
| T095-69 | Recuperação, outbox e idempotência | restore save anterior aos efeitos | **NÃO EXECUTADO** |
| T095-70 | Recuperação, outbox e idempotência | fork cria nova revisão isolada | **NÃO EXECUTADO** |
| T095-71 | Recuperação, outbox e idempotência | transação local não garante engine | **NÃO EXECUTADO** |
| T095-72 | Recuperação, outbox e idempotência | UNKNOWN permanece em quarentena | **NÃO EXECUTADO** |
| T095-73 | Tempo, canon e facções | ação em 1369 não altera pack 1370 | **NÃO EXECUTADO** |
| T095-74 | Tempo, canon e facções | ano DR trocado invalida plano | **NÃO EXECUTADO** |
| T095-75 | Tempo, canon e facções | relógio FROZEN preserva pendência | **NÃO EXECUTADO** |
| T095-76 | Tempo, canon e facções | relógio PARTIAL sem catchup indevido | **NÃO EXECUTADO** |
| T095-77 | Tempo, canon e facções | reconciliação após REALTIME | **NÃO EXECUTADO** |
| T095-78 | Tempo, canon e facções | evento canon irreversível intacto | **NÃO EXECUTADO** |
| T095-79 | Tempo, canon e facções | NPC offscreen não teleporta | **NÃO EXECUTADO** |
| T095-80 | Tempo, canon e facções | facção não recebe ouro criado | **NÃO EXECUTADO** |
| T095-81 | Tempo, canon e facções | reparação jurídica DEC-081 separada | **NÃO EXECUTADO** |
| T095-82 | Tempo, canon e facções | reputação não é resetada | **NÃO EXECUTADO** |
| T095-83 | Tempo, canon e facções | fonte histórica de outro ano bloqueada | **NÃO EXECUTADO** |
| T095-84 | Tempo, canon e facções | ação não cria quest canônica | **NÃO EXECUTADO** |
| T095-85 | Segurança, coop e integração | ACL oculta rota de testemunha | **NÃO EXECUTADO** |
| T095-86 | Segurança, coop e integração | log redige identidade protegida | **NÃO EXECUTADO** |
| T095-87 | Segurança, coop e integração | LLM não escolhe restituição | **NÃO EXECUTADO** |
| T095-88 | Segurança, coop e integração | LLM não inventa receipt | **NÃO EXECUTADO** |
| T095-89 | Segurança, coop e integração | host offline impede claim de sucesso | **NÃO EXECUTADO** |
| T095-90 | Segurança, coop e integração | dois clientes não duplicam ação | **NÃO EXECUTADO** |
| T095-91 | Segurança, coop e integração | bridge sem capability bloqueia mutação | **NÃO EXECUTADO** |
| T095-92 | Segurança, coop e integração | sandbox sem save real | **NÃO EXECUTADO** |
| T095-93 | Segurança, coop e integração | diagnóstico não revela segredos | **NÃO EXECUTADO** |
| T095-94 | Segurança, coop e integração | auditoria de alteração material | **NÃO EXECUTADO** |
| T095-95 | Segurança, coop e integração | custo computacional limitado | **NÃO EXECUTADO** |
| T095-96 | Segurança, coop e integração | fallback de indisponibilidade seguro | **NÃO EXECUTADO** |

## 8. Integrações e separações

- DEC-011/012: host/Action Gateway; DEC-027/028: risk/ACL; DEC-041/045/046: coop/consentimento/delegação; DEC-050/051: scripts/inventário; DEC-053/054: checkpoint/restore; DEC-060–063: lore particionado; DEC-074: efeitos causais; DEC-081: reparação jurídica distinta; DEC-091–094: lifecycle/concorrência/fencing.
- A proposta histórica e geográfica do usuário foi registrada **separadamente**, como **DEC-096 em aberto**, em `96-proposta-matriz-cronologica-condicional-de-eventos-e-repercussoes.md`.

## Integração DEC-096/C — Discovery v9.2

DEC-096/C não apaga impactos históricos host-confirmed; eventual compensação DEC-095 precisa novo ato autorizado e auditável.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Reverter projection DEC-097/C não é Saga DEC-095; compensação de host-confirmed exige novo efeito confirmado.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Compensações Saga DEC-095 são atos novos com receipts, não reverse automático do snapshot quando uma repercussão expira.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Saga compensatória não apaga fatos passados nem reverte flags de quests sem licença e receipt.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Saga compensatória registra ações novas sem inferir rollback pelo valor de quest flag.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** DEC-101 interpretation is read-only, version-pinned and independent of gateway/host execution. A confirmed semantic milestone does not authorize actions or prove a command receipt; mod upgrades, checkpoint restore, revised mapping, epoch mismatch or contradictory states cause fail-closed reconciliation. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

DEC-102 não executa compensações; ajustes históricos exigem novo evento Saga autorizado. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **sagas como novos fatos, sem rollback**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para compensação é nova ação autorizada, nunca esquecimento forçado, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para Saga de compensação como novo evento autorizado, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Compensação é novo evento com receipt, nunca rollback global. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Compensar etapa parcial produz novo ato confirmado, sem desfazer história. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Restituição de depósito é compensação nova autorizada e com receipt, não apagar evento anterior.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
