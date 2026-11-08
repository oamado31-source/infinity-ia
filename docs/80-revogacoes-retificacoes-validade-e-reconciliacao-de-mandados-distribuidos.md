# 80 — Revogações, retificações, validade e reconciliação de mandados distribuídos

**Discovery v7.6 — DEC-080/C aprovada, NÃO IMPLEMENTADA.** Referência normativa: `docs/decisions/ADR-0075-revogacoes-versionadas-e-contencao-de-mandados-desatualizados.md`. Os **64 testes T080-01..T080-64 são candidatos e NÃO EXECUTADOS**.

## 1. Fronteiras e dependências

A DEC-079/C registra pedidos e decisões entre jurisdições via canais reais do cenário. A DEC-080/C acrescenta **ciclo de vida versionado** (emissão, retificação, suspensão, revogação, expiração e reemissão), distinção entre *vigência real da ordem* e *conhecimento local do receptor*, e gate seguro para consequências coercitivas. Não se trata de lei moderna, extradição automática ou API funcional do BG2:EE.

- DEC-078: autoridade, procedimento, defesa, prova, jurisdição e decisão não se confundem.
- DEC-079: pedido, entrega, reconhecimento, recusa e execução são eventos separados.
- DEC-022/029/069/074: relógio, canal de notícia, rota/tempo e repercussões sociais.
- DEC-011/012/027/034/041/042/050/051/053/054/055/056: host, gateway, risco, salvaguardas, scripts nativos, compatibilidade, checkpoint e filas.
- DEC-060–063: lore **fisicamente particionado por ano DR**, fontes verificáveis, ingestão curada e Knowledge Pack por campanha; os novos atos ficam **somente no overlay da campanha/ramo**.
- DEC-064–077: identidade, crença individual, testemunhas, pseudônimos, investigação e autoria; não inferir conhecimento universal.

## 2. Modelo conceitual e ledger

```text
Case (campanha/branch/autoridade/caso)
  |
  +-- OrderVersion #1 ISSUE ---> status ACTIVE
  |
  +-- OrderVersion #2 SUSPEND ---> status SUSPENDED
  |
  +-- OrderVersion #3 REVOKE ---> status REVOKED [terminal/tombstone]

Recipient A: RECEIVED rev #1       (crença possivelmente desatualizada)
Recipient B: RECEIVED rev #1 + #3  (conhecimento atualizado)

Safety Gate: compara estado/competência autoritativos e provas atuais
             sem divulgar #3 a Recipient A como conhecimento narrativo.
```

Uma operação de proteção informada por ledger restrito **não deve produzir fala, lembrança ou decisão epistêmica** para NPC que ainda não recebeu mensagem. Mesmo o safety gate pode estar sem conectividade, prova ou capability suficiente; nesse caso, HIGH deve ser suspenso/fail-closed.

## 3. Tipos candidatos (não APIs existentes)

```text
LegalOrderEvent {
  campaign_id, branch_id, case_id, order_id,
  issuer_authority_id, issuer_competence_evidence_ref,
  revision, prior_revision_ref?, event_kind: ISSUE|AMEND|SUSPEND|REVOKE|EXPIRE|REISSUE|CORRECT,
  effect_scope, target_identity_ref?, persona_claim_ref?,
  effective_time_dr, expiry_rule_ref?, source_evidence_refs[],
  event_provenance, risk_class, acl_ref, policy_revision, checkpoint_epoch
}
AuthoritativeOrderState {
  order_id, revision, state: ACTIVE|SUSPENDED|REVOKED|EXPIRED|DISPUTED|UNKNOWN,
  issuing_authority_verified, chain_integrity, effective_time_dr,
  current_policy_ref, confirmation_evidence_refs[]
}
InterjurisdictionUpdate {
  update_id, order_id, revision, origin_authority, recipient_authority,
  channel_ref, route_ref, sent_at_dr, received_at_dr?,
  delivery_receipt_ref?, authenticity_result?, acl_ref, queue_priority,
  idempotency_key, status: PENDING|SENT|DELIVERED|STALE|REJECTED|UNCERTAIN
}
RecipientKnowledgeState {
  recipient_authority_id, order_id, last_verified_received_revision,
  locally_believed_status, received_evidence_refs[],
  valid_as_of_dr?, knowledge_acl_ref, branch_id, checkpoint_epoch
}
CoerciveActionGate {
  proposed_action_id, order_id, target_identity_verified_ref,
  issuer_and_recipient_competence_refs[], authoritative_status_evidence_ref?,
  freshness_policy_ref, host_build_and_capability_ref?,
  consent_and_risk_approvals[], gateway_operation_id?, host_receipt_ref?,
  gate_state: PASS|PENDING_EVIDENCE|BLOCKED_STALE|BLOCKED_RISK|UNCERTAIN
}
```

A estrutura final de banco, assinaturas, intervalos de validade, TTL, relógio e formato de recibo será definida nas SPECS. Os campos são apenas desenho para discussão, e **não** prova de funções já disponíveis.

## 4. Máquina de estados por ordem e por destinatário

### 4.1 Status do emissor

`DRAFT → VALIDATED → ACTIVE → (SUSPENDED | AMENDED | REVOKED | EXPIRED | DISPUTED)`; `REISSUE` cria nova cadeia formal ou nova revisão sujeita à regra adotada, **não** restaura silenciosamente uma ordem revogada. A política exata de autorização de atos em cada regime/cidade deve ter fonte no ano DR aplicável; status desconhecido bloqueia coerção.

### 4.2 Transmissão por autoridade receptora

`PROPOSED → VALIDATED_SOURCE → QUEUED → SENT → DELIVERED → ACKNOWLEDGED → REVIEWED → (RECOGNIZED | REJECTED | CONTESTED)`.

Chegada da informação, reconhecimento e execução não podem ser colapsados. `REVOKE` deve ser deduplicado e substituir a validade operativa local ao ser aceito, mas registro da crença antiga permanece no histórico. Mensagens atrasadas não podem ressuscitar status anterior, mesmo se receberem timestamp maior de processamento.

### 4.3 Execução de medida coercitiva

`INTENT → PRECONDITIONS_CHECK → AUTHORIZATION_GATE → HOST_PENDING → HOST_CONFIRMED`; ramos `BLOCKED_STALE`, `BLOCKED_RISK`, `PENDING_EVIDENCE`, `UNSUPPORTED`, `UNCERTAIN` **não** criam efeito. Evento narrativo LOW pode ser publicado separadamente quando autorizado; ele não significa prisão, hostilidade mecânica ou confisco.

## 5. Estados de tempo e conhecimento sem onisciência

| Situação | Estado do emissor | Conhecimento destinatário | Decisão segura |
|---|---|---|---|
| Mandado revogado, aviso em trânsito | `REVOKED` | Possivelmente `ACTIVE` | Destinatário pode acreditar em `ACTIVE`; gateway de coerção HIGH bloqueia se revogação é verificada ou atualidade é incerta |
| Mandado ativo com prova válida e recente | `ACTIVE` | `ACTIVE`, autenticação suficiente | Ação só passa após competência, risco, consentimento, build/host e políticas aplicáveis |
| Revogação recebida e validada | `REVOKED` | `REVOKED` | Impedir ação fundada na ordem; possível notícia de correção posterior |
| Falsificação de revogação | `ACTIVE` ou `UNKNOWN` | Rumor/alegação | Não altera estado autoritativo; proteção de risco continua ativa |
| Sistema de emissor indisponível | `UNKNOWN` operacionalmente | Pode crer `ACTIVE` | Coerção HIGH falha fechada, não notifica NPC automaticamente de revogação desconhecida |
| Sanção já executada antes da revogação | Mudança posterior | Conhecimento depende do canal | Manter evento e receipts históricos; reparação futura é DEC-081 |

*Importante:* o sistema de segurança pode consultar dados com finalidade restrita, mas não pode apresentar essa consulta interna como conhecimento narrativo de NPCs.

## 6. Política de reconciliação e ordem causal

1. Identificar a cadeia com campanha, branch, caso, emissor competente e `order_id`.
2. Validar fonte/competência, versão monotônica, precondições temporal-geográficas, ACL e KPack pinado.
3. Registrar evento imutável e recusar revisões obsoletas ou conflitantes; ordem `REVOKED/EXPIRED` recebe tombstone protegido.
4. Produzir mensagem de atualização por canal legítimo, com revisão, público e validade; pendência de envio não representa entrega.
5. Worker de comunicação prioriza correções críticas dentro do orçamento; mensagem pode permanecer em trânsito, e `ACKNOWLEDGED` exige evidência.
6. Autoridade receptora mantém crença conforme mensagens efetivamente recebidas; pode exigir autenticação/contestação própria.
7. Quando houver intenção coercitiva, o **safety gate** obtém evidência de vigência/competência atual ou retorna `BLOCKED_STALE/PENDING_EVIDENCE`, sem telepatia de NPC.
8. Gateway DEC-012 verifica risco, direitos do PC, build/adapter e host para qualquer efeito mecânico, e registra receipt consistente.
9. Em `UNCERTAIN`/disconnect/restore, reconciliar antes de retry; não executar sanção ou reemitir ordem por erro de fila.
10. Revogação futura pode desencadear pedidos de correção, mas não desfaz automaticamente eventos anteriores.

## 7. Idempotência, checkpoints, multijogador e mod compat

- Chave conceitual de atualização `(campaign, branch, order, revision, issuer, recipient, event_kind)`, mais `idempotency_key` por publicação. O efeito tem chave distinta `(case, order, action, actor, resolution_epoch, rule_revision)`.
- Duas fontes entregam o mesmo evento ao destinatário: uma única alteração de crença/estado; relatórios podem manter proveniência múltipla sem multiplicar cumprimento.
- Restores/forks usam o estado do branch/checkpoint correto, não alteram o histórico de outras campanhas; revogações futuras tornam-se `STALE` no ramo restaurado.
- Reavaliação de competência por alteração de governante, relação política, facção ou período DR não equivale a nova ordem ativa.
- Host+dois clientes e capacidades em BG2:EE/EEex são **POCs futuras**, não evidências atuais. Guardas/npcs não materializados não recebem movimento, captura nem teleporte.
- Logs redigidos e segredos DEC-028/075–077, acesso por finalidade; workers LAN sem direito de emitir ou executar atos oficiais.

## 8. Riscos, estratégia de entrega e escopo excluído

- Risco de ordem revogada ainda percebida como válida em cidade remota: garantir *segurança do efeito*, sem imputar onisciência a guardas.
- Risco de perseguição infinita por retry/duplicidade: cadeia de revisões e tombstones.
- Risco de documento falsificado: autenticidade/competência separadas da aparência do selo.
- Risco de ordem realmente injusta porém ainda tecnicamente válida: o sistema pode representar conflito narrativo e contestação DEC-078, mas política de coerção sobre PC segue HIGH default-deny.
- Risco de perda de contexto canônico: fontes por ano DR DEC-060–063; nem atualizar diretórios físicos nem assumir tratados contemporâneos.
- A DEC-080 **não** aprova reparação automática, restituição de itens, soltura mecânica, rollback de save ou mudança de quest — tema DEC-081.

## 9. Escada de POCs futuras — nenhuma executada

1. Fixtures determinísticas com emissor, dois destinatários, mensagens fora de ordem, clock e regra de competência.
2. Simular versão 1/2/3, suspensão/revogação e tombstones; provar ausência de resurrect de ordem por mensagens tardias.
3. Demonstrar distinção entre estado global restrito e conhecimento do NPC por relato, ACL e tempo.
4. Testar crash, retry, perda de mensageiro, restore, fork, revogação e desatualização de KPack; sem engine.
5. Inventariar capacidades do BG2:EE limpo + EEex/bridge em read-only; registrar explicitamente ausência de suporte.
6. Somente após aprovação: integração controlada em instalação isolada, host+dois clientes, com testes de idempotência e save/load para efeitos compatíveis.

## 10. Matriz de **64 testes candidatos T080 — NÃO EXECUTADOS**

| ID | Cenário / expectativa | Estado |
|---|---|---|
| T080-01 | Emissão inicial gera versão 1 e evento imutável de ordem. | NÃO EXECUTADO |
| T080-02 | Revogação cria novo evento, sem sobrescrever a emissão original. | NÃO EXECUTADO |
| T080-03 | Suspensão não é interpretada como revogação definitiva. | NÃO EXECUTADO |
| T080-04 | Expiração só ocorre quando critério temporal curado é satisfeito. | NÃO EXECUTADO |
| T080-05 | Reemissão de ordem revogada exige novo gate e não ressuscita versão antiga. | NÃO EXECUTADO |
| T080-06 | Retificação de alvo não troca identidade sem evidência DEC-066. | NÃO EXECUTADO |
| T080-07 | Retificação de nome alias não revela identidade secreta DEC-076. | NÃO EXECUTADO |
| T080-08 | Evento enviado não implica que destinatário o recebeu. | NÃO EXECUTADO |
| T080-09 | Recibo de entrega não implica reconhecimento pela autoridade de destino. | NÃO EXECUTADO |
| T080-10 | Reconhecimento da ordem não implica execução mecânica. | NÃO EXECUTADO |
| T080-11 | Autoridade destinatária sem competência pode negar mesmo com mandado autêntico. | NÃO EXECUTADO |
| T080-12 | Origem com competência UNKNOWN não habilita sanção. | NÃO EXECUTADO |
| T080-13 | Autoridade falsificada não altera estado autoritativo. | NÃO EXECUTADO |
| T080-14 | Selo forjado é evidência narrativa de tentativa, não autorização. | NÃO EXECUTADO |
| T080-15 | Dois emissores rivais com decisões incompatíveis criam COMPETENCE_DISPUTED. | NÃO EXECUTADO |
| T080-16 | Última mensagem recebida não prevalece sobre revisão anterior por simples chegada. | NÃO EXECUTADO |
| T080-17 | Mensagem de revogação chega antes de versão antiga e permanece terminal. | NÃO EXECUTADO |
| T080-18 | Mensagem atrasada de emissão não reativa mandado revogado. | NÃO EXECUTADO |
| T080-19 | Pacote de suspensão mais antigo não remove revogação posterior. | NÃO EXECUTADO |
| T080-20 | Evento de revogação repetido por dois mensageiros não é aplicado duas vezes. | NÃO EXECUTADO |
| T080-21 | Confirmação duplicada de entrega não duplica efeito social. | NÃO EXECUTADO |
| T080-22 | Chave idempotente em outra branch não compartilha estado. | NÃO EXECUTADO |
| T080-23 | Fork de campanha isola revogações e crenças. | NÃO EXECUTADO |
| T080-24 | Restore pré-revogação restaura contexto do ramo e invalida jobs futuros. | NÃO EXECUTADO |
| T080-25 | Replay pós-save não reexecuta ação coercitiva. | NÃO EXECUTADO |
| T080-26 | Autoridade sem notícia mantém crença antiga sem ter acesso a ledger privado. | NÃO EXECUTADO |
| T080-27 | NPC recebe atualização por canal válido e só então muda crença. | NÃO EXECUTADO |
| T080-28 | NPC não aprende revogação porque safety gate acessou ledger privado. | NÃO EXECUTADO |
| T080-29 | Safety gate bloqueia coerção quando mandado foi efetivamente revogado. | NÃO EXECUTADO |
| T080-30 | Safety gate bloqueia coerção quando vigência atual não pode ser verificada. | NÃO EXECUTADO |
| T080-31 | Estado ACTIVE conhecido apenas pelo NPC não basta para host executar prisão. | NÃO EXECUTADO |
| T080-32 | Captura host sem capability validada é bloqueada. | NÃO EXECUTADO |
| T080-33 | Confisco não é realizado sem autorização, ownership e receipt. | NÃO EXECUTADO |
| T080-34 | Guardas não são teleportados devido à existência da ordem. | NÃO EXECUTADO |
| T080-35 | Perseguição local depende de NPCIdentity e presença host verificadas. | NÃO EXECUTADO |
| T080-36 | Host receipt de outro checkpoint não confirma a mesma ação. | NÃO EXECUTADO |
| T080-37 | Host receipt de build antiga é recusado. | NÃO EXECUTADO |
| T080-38 | Comando mecânico em timeout vira UNCERTAIN sem retry cego. | NÃO EXECUTADO |
| T080-39 | Cliente multiplayer não revoga ordem nem executa captura sozinho. | NÃO EXECUTADO |
| T080-40 | Worker LAN revogado não publica nova versão de ordem. | NÃO EXECUTADO |
| T080-41 | Processos pendentes são revisitados após alteração de competência. | NÃO EXECUTADO |
| T080-42 | Tratado ausente no lore gera UNKNOWN em vez de cooperação inventada. | NÃO EXECUTADO |
| T080-43 | Ano DR futuro não define norma aplicável em campanha de ano anterior. | NÃO EXECUTADO |
| T080-44 | Knowledge Pack alterado exige revalidação e não substituição silenciosa. | NÃO EXECUTADO |
| T080-45 | Diretórios físicos anuais DEC-060 permanecem idênticos após revogação. | NÃO EXECUTADO |
| T080-46 | Revogação do caso A não apaga mandado independente do caso B. | NÃO EXECUTADO |
| T080-47 | Correção de status não apaga o evento factual de prisão anterior. | NÃO EXECUTADO |
| T080-48 | Evento de reparação não ocorre automaticamente ao revogar ordem. | NÃO EXECUTADO |
| T080-49 | Reputação só muda após regra e comunicação causal autorizadas. | NÃO EXECUTADO |
| T080-50 | Boato falso de revogação não libera ação mecânica por si só. | NÃO EXECUTADO |
| T080-51 | Difusão por canal sem tempo/região plausível fica pendente. | NÃO EXECUTADO |
| T080-52 | Informação secreta é filtrada antes de enviar mensagem entre facções. | NÃO EXECUTADO |
| T080-53 | Logs não expõem identidade protegida nem conteúdo integral do processo. | NÃO EXECUTADO |
| T080-54 | NPC sob pseudônimo homônimo não é confundido com alvo real. | NÃO EXECUTADO |
| T080-55 | PC ausente não sofre punição presumida baseada em ordem antiga. | NÃO EXECUTADO |
| T080-56 | Várias ações LOW com consequência agregada HIGH são reclassificadas. | NÃO EXECUTADO |
| T080-57 | Fila prioriza revogação crítica sem violar causalidade nem fabricar entrega. | NÃO EXECUTADO |
| T080-58 | Backpressure preserva jobs e não declara destinatário informado. | NÃO EXECUTADO |
| T080-59 | Watchdog detecta mandado em trânsito e ação bloqueada sem autocaptura. | NÃO EXECUTADO |
| T080-60 | Estado STALE não autoriza reconhecimento nem execução. | NÃO EXECUTADO |
| T080-61 | Migração de mod invalida capabilities sem produzir side-effects automáticos. | NÃO EXECUTADO |
| T080-62 | Mudança de autoridade após golpe político exige nova validação da competência. | NÃO EXECUTADO |
| T080-63 | POC host+dois clientes demonstraria que há um único efeito, antes de alegar suporte. | NÃO EXECUTADO |
| T080-64 | Ausência de POC mantém todos os efeitos mecânicos bloqueados e documentados. | NÃO EXECUTADO |

Todos os testes são **candidatos**, não resultados. Parâmetros, schemas finais, algoritmos de verificação de autenticidade, ambientes e critérios de aceite precisam de SPECS antes da execução.

## 11. Próxima escolha — DEC-081 (EM ABERTO)

**Reparação contextual de danos originados por decisões erradas, anuladas ou revogadas:** A) apenas cessar o efeito futuro; B) reverter automaticamente e por inteiro tudo o que ocorreu; **C, recomendada)** processo de revisão/reparação por caso e jurisdição, com eventos causais de correção, possível restituição autorizada e confirmada, registros imutáveis e sem assumir rollback seguro de BG2:EE. Não aprovar automaticamente a DEC-081.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

DEC-080 corrige a validade de mandado; DEC-081/C aprova reparação causal separada, sem rollback automático ou compensação por dano não comprovado. Novas decisões e retratações têm versões/receipts próprios.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Revisão de mandato ou decisão disciplinar é evento versionado independente da culpa comprovada. Uma revogação preserva história e não prova corrupção.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Correções/revogações versionadas podem afetar necessidade de divulgação; ordem obsoleta não concede acesso a identidade; atualizar ACL/jobs.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Revogar ordem ou ameaça não reverte deslocamento/proteção já confirmados; correções chegam por canais e planos stale são reconciliados.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Plano modificado revoga grants futuros e resiste a jobs stale; NPC não esquece notícia recebida anteriormente. Segurança de mandado permanece independente.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Mensagem de isca não pode reativar mandado revogado nem simular receipt oficial; versionamento autoritativo de ordens permanece inviolável.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Revogação de acusação de traição preserva versões, informação local e contenção de coerção desatualizada.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Revogar um mandado e encerrar um acordo são registros distintos; informações já transmitidas não desaparecem e pagamentos uncertain não são duplicados.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Atualização/revogação de ordem deve considerar revisões de evidência; relatório antigo não reativa mandado, ação HIGH exige autoridade vigente.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Dossier CorrectionNotice e revogação de mandado usam mecanismos próprios e não se implicam automaticamente; a autoridade precisa receber atualização por canal legítimo.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Mandado obsoleto ou vigência UNCERTAIN bloqueia coerção HIGH mesmo que NPC ainda não tenha recebido correção.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Revogação de ordem ou perda de vigência bloqueia novos atos coercitivos; mensagem ainda em trânsito não equivale a ciência de NPC.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Revogação de ordem invalida novos atos ligados ao plano, mas não libera recurso de ação host in-flight antes de receipt/reconciliação.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Conflito de despacho de revogação não torna ordem novamente válida nem permite executar sanção HIGH com validade incerta; priorização de análise mantém gates.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Revogação de mandados bloqueia futuros atos; não sobrescreve saves/quest scripts confirmados.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Revogação de mandados exige conhecimento causal e não pode depender de branch futura revelada por flag.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração DEC-102/C (Discovery v9.8)

A DEC-102/C trata divergências entre milestone validado do host e projeção derivada do Living World: exigir mapeamento DEC-101, observação DEC-100, epoch/branch e receipts, e preservar o host, facts ledger e conhecimento dos NPCs. Somente proposta de revisão CAS/autorizada; detalhes em ADR-0097/doc. 102. **Sem POC mecânica.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **revogação de mandato**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para revogação de mandado exige mensagens e recepções específicas, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para revogação de mandados não ocorre por rumor, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Mandatos revogados não assinam aditamentos. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Mandato revogado bloqueia etapas futuras não confirmadas. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
