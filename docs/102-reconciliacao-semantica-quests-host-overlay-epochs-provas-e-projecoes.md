# 102 — Reconciliação causal entre quests do host e overlay Living World

**Status:** DEC-102/C aprovada como arquitetura, 2026-11-07 · Discovery v9.8 · ADR-0097. **POCs com BG2:EE/EEex/bridge/host+dois clientes PENDENTES.** Todos os ADRs anteriores byte a byte imutáveis.

## 1. Objetivo e fronteira de autoridade

Evitar que marcos de quests originais detectados por observadores read-only (DEC-100) e interpretados por mapeamentos curados (DEC-101) entrem em divergência silenciosa com o overlay do Living World. A **autoridade mecânica pertence ao host** (DEC-011) e a autoridade de fatos confirmados pertence ao registro de eventos contextualizado. Reconciliação **não** implica escrita em globais, scripts ou instâncias originais; a LLM nunca escolhe o estado verdadeiro.

As cinco camadas não são equivalentes:

| Camada | Fonte de autoridade | Pode ser atualizada pela DEC-102? |
|---|---|---|
| `HostQuestSemanticObservation` | host + reader allowlisted + prova DEC-100 | **NÃO**, somente leitura; requer proof/coverage/capability |
| `CuratedSemanticAssertion` | catálogo de quest DEC-101, versionado por build | **NÃO**, interpretar somente quando verificado |
| `LivingWorldQuestProjection` | visão derivada do overlay, versionada | **PROPOSTA de nova revisão**, com CAS/autorização externa |
| `NarrativeFactLedger` | fatos confirmados e receipts com proveniência | **NÃO**, histórico append-only; correção é novo evento |
| `RecipientKnowledge` | aquisição causal, divulgação legítima e ACL | **NÃO**, interpretar não é transmitir nem fazer esquecer |

## 2. Contratos de entrada e origem de confiança

`QuestReconciliationCase` (contrato conceitual) combina envelopes protegidos, vindos de repositórios separados, nunca de um único prompt:

```yaml
request:
  operation_id: opaque; actor_id: opaque; purpose: RECONCILE
  campaign_id: opaque; branch_id: opaque; session_id: opaque; quest_key: opaque
  expected_overlay_revision: opaque
policy_from_trusted_store:
  acl_revision: opaque; allowed_audience: [host_operator]
  signature_or_attestation: verifier-owned; risk_gate: default-deny
host_observation_from_validated_adapter:
  observation_id: opaque; proof_id: opaque; coverage: FULL_FOR_SEMANTIC_PROOF
  host_epoch: integer; checkpoint_epoch: integer; observed_tick: integer
  semantic_status: MAPPED_MINIMAL; semantic_id: opaque
curated_mapping_from_registry:
  build_fingerprint: opaque; modpack_hash: opaque; script_digest: opaque
  mapping_revision: opaque; quest_variant: opaque
  transition_allowlist: [from_semantic_id, to_semantic_id]
overlay_from_private_ledger:
  campaign_id: opaque; branch_id: opaque; host_epoch: integer
  checkpoint_epoch: integer; revision: opaque; semantic_id: opaque
  facts_log_ref: append-only; prior_observations: opaque
host_receipts_from_gateway:
  actions: [operation_id, action_state, host_receipt_ref, epoch]
```

**Autenticidade real exige verificação externa**: assinatura, proofs do host, acesso ao repositório de políticas e clocks não podem ser validados por um protótipo que recebe objetos JSON sintéticos. O `examples/chronology/quest_reconciler_reference.py` recusa fixtures que não sejam sintéticas e não fornece segurança de produção.

## 3. Máquina de decisão

| Decisão | Prova mínima | Resultado seguro |
|---|---|---|
| `CONSISTENT` | marco observado e projetado coincidem; mesma build/branch/epoch | Sem ação; log opcional de avaliação |
| `PROPOSE_DERIVED_VIEW_REBASE` | avanço permitido por mapping curado, mesmo epoch, full proof, receipts conciliados, CAS esperado | **Proposta**, não gravação; aprovar e commitar em etapa separada |
| `RESTORE_REVIEW_REQUIRED` | timeline do overlay difere dos epochs do save/host | Quarentena do ramo antigo; propor fork/rescope autorizado |
| `UNKNOWN` | observação parcial, stale, sem prova, semântica incerta ou overlay não classificado | Não declarar progresso nem regressão |
| `QUARANTINED` | conflito de escopo, transição não curada, ledger `UNCERTAIN`, mismatch temporal, condições impossíveis | Bloquear novas consequências; solicitar evidências/receipt/revisão |
| `BLOCKED_MAPPING` | build/modpack/script/mapping sem curadoria ou pinning válido | Recertificar e reevaluar somente com consentimentos adequados |
| `BLOCKED_ACL` | operação ou destinatário sem permissão | Não divulgar dados e registrar apenas código opaco |

Além disso, falhas de autenticação, checksum, ACL, curation, clock e race podem produzir `BLOCKED_*` adicionais; nunca são tratadas como `CONSISTENT` por fallback genérico.

## 4. Algoritmo determinístico recomendado

```text
reconcile(case):
  authorize purpose/scope from INDEPENDENT trusted policy
  verify host attestation + allowlisted observation capability + coverage + TTL
  validate quest/build/modpack/adapter/script/mapping pinning
  validate campaign/branch/session + host_epoch/checkpoint_epoch
  fetch immutable overlay view + CAS revision + host receipts from trusted ledger
  if read incomplete, mapping ambiguous or unavailable: return UNKNOWN/BLOCKED
  if DISPATCHED/UNCERTAIN exists: QUARANTINE; reconcile host receipts first
  if overlay lineage epoch != active save epoch: RESTORE_REVIEW_REQUIRED
  if host.semantic_id == overlay.semantic_id: CONSISTENT
  if transition NOT curated/proven: QUARANTINE
  propose new DerivedView revision with provenance and expected CAS
  do NOT write host, fact ledger, knowledge store, scripts, inventory or NPCs
```

A função de referência demonstrativa **não efetua CAS nem persiste**; apenas devolve classificação/proposta sintética. CAS/fencing são obrigações de uma implementação futura e precisam de testes com host real.

## 5. Restore, branches e retroatividade

- `host_epoch` e `checkpoint_epoch` são parte da identidade do fato observado. Receber novo snapshot após restore não autoriza copiar efeitos de um save mais avançado.
- `RESTORE_REVIEW_REQUIRED` exige preservar os logs do ramo antigo, classificar a nova linha temporal e obter decisão sobre fork/rescope sem merge silencioso.
- Não se desfazem mortes, relacionamentos, quests ou segredos já observados no ramo anterior por operação de banco; eventuais compensações seguem DEC-095, com atos novos e receipts.
- O modo Original e o Living World usam saves/overlays segregados (DEC-004). Migrações entre packs/branch dependem de DEC-063 e validações específicas.
- O relógio DR híbrido (DEC-022) e o cânone fisicamente segregado (DEC-060) não são alterados pela atualização de projeção.

## 6. Privacidade, acesso e prevenção de spoilers

- Evidências com flags/scripts crus ficam no domínio observacional protegido; o reconciliador e seus logs públicos expõem IDs opacos, status e reason codes.
- Não enviar dados crus, hidden quest branches, romances privados, identidades, timestamps secretos ou keys de cache para narradores, NPCs, espectadores, dossiês ou LLMs sem ACL por destinatário/finalidade.
- Reconciliar internamente não estabelece que algum NPC ouviu a notícia. DEC-028/029/064/075/083/089/090 continuam governando divulgação e atribuição.
- Conteúdo de mods e nomes de variáveis são entradas não confiáveis; não podem executar instruções ou modificar políticas.

## 7. Autorizações e operações pendentes

- Host observation DEC-100 **não substitui receipt DEC-011/012**. `DISPATCH_PENDING`, `DISPATCHED`, `UNCERTAIN` e `ACK_UNKNOWN` exigem consulta/reconciliação; não retry cego nem desmobilização de recursos.
- Aprovar um `DerivedViewRebaseProposal` requer serviço confiável, escopo, expected revision, fencing, validação de ACL e revisão auditável. Essa decisão nunca autoriza escrita em quest scripts/globals do BG2:EE.
- Não invalidar checkpoints nem modificar fatos confirmados; a projeção pode ganhar uma nova versão `SUPERSEDED`, com ponte explícita ao estado anterior.
- A saída não produz evento ambiental, modificação econômica ou rumor. A DEC-103 decidirá política de admissão dos eventos narrativos derivados.

## 8. Schemas, exemplos e suíte sintética

- `examples/chronology/quest_reconciliation_v1.candidate.schema.json`: envelope de decisão e propostas auditáveis; **contrato candidato**.
- `examples/chronology/quest_reconciliation_v1.synthetic.json`: apenas duas fases de uma quest inteiramente inventada, com IDs `SYN-*`.
- `examples/chronology/quest_reconciler_reference.py`: Python puro, `host_calls=0`, `engine_writes=0`, `llm_calls=0`, `npc_knowledge_updated=False`.
- `examples/chronology/test_quest_reconciler_reference.py`: testes unitários **sintéticos**; nenhuma engine ligada.
- **NÃO** comprova API EEex, read-only real, transação de save, concorrência host+2 clientes, scripts originais ou modpacks. Requer POCs verificáveis por build.

## 9. Integrações com decisões anteriores

| Decisões | Consequência normativa da DEC-102 |
|---|---|
| 011/012/027 | Host mecânico soberano; gates, receipts e risco preservados |
| 019/028/041/045/046 | Segredos, PCs, delegação e consentimento não são deduzidos do estado de quest |
| 050/051/052/053/054 | Scripts/quest, coordenação de saves, checkpoint, recuperação e rollback não destrutivo |
| 059/060–063/064 | Contexto LLM mínimo, KPack por ano/branch e crenças de NPC separadas |
| 075/077/089/090 | Atribuição, evidência, fontes independentes e dossiês protegidos |
| 092–095 | Pausa, scheduler, deadlocks e Saga respeitam `UNCERTAIN`/receipts |
| 096–098 | Repercussões e materialização não se disparam de projeções não confirmadas |
| 099/100/101 | Ownership, observação e interpretação são responsabilidades separadas |

## 10. Matriz de 132 testes candidatos — TODOS NÃO EXECUTADOS

**Estes T102 são roteiros para futuras POCs com host, Windows BG2:EE/EEex e dois clientes. Não foram executados.**

| ID | Eixo | Cenário | Resultado esperado |
|---|---|---|---|
| T102-001 | Escopo e identidade | Campanha A versus B | Identidade/fingerprint verificado ou bloqueio; sem cross-branch nem escrita mecânica; **NÃO EXECUTADO** |
| T102-002 | Escopo e identidade | Branch principal versus fork | Identidade/fingerprint verificado ou bloqueio; sem cross-branch nem escrita mecânica; **NÃO EXECUTADO** |
| T102-003 | Escopo e identidade | Sessão host trocada | Identidade/fingerprint verificado ou bloqueio; sem cross-branch nem escrita mecânica; **NÃO EXECUTADO** |
| T102-004 | Escopo e identidade | Quest homônima em mods distintos | Identidade/fingerprint verificado ou bloqueio; sem cross-branch nem escrita mecânica; **NÃO EXECUTADO** |
| T102-005 | Escopo e identidade | Fingerprint BG2:EE divergente | Identidade/fingerprint verificado ou bloqueio; sem cross-branch nem escrita mecânica; **NÃO EXECUTADO** |
| T102-006 | Escopo e identidade | Hash modpack alterado | Identidade/fingerprint verificado ou bloqueio; sem cross-branch nem escrita mecânica; **NÃO EXECUTADO** |
| T102-007 | Escopo e identidade | Ordem de mods alterada | Identidade/fingerprint verificado ou bloqueio; sem cross-branch nem escrita mecânica; **NÃO EXECUTADO** |
| T102-008 | Escopo e identidade | Script digest da quest mudou | Identidade/fingerprint verificado ou bloqueio; sem cross-branch nem escrita mecânica; **NÃO EXECUTADO** |
| T102-009 | Escopo e identidade | Adapter observer antigo | Identidade/fingerprint verificado ou bloqueio; sem cross-branch nem escrita mecânica; **NÃO EXECUTADO** |
| T102-010 | Escopo e identidade | Mapping revision revogada | Identidade/fingerprint verificado ou bloqueio; sem cross-branch nem escrita mecânica; **NÃO EXECUTADO** |
| T102-011 | Escopo e identidade | Quest variant alternativa | Identidade/fingerprint verificado ou bloqueio; sem cross-branch nem escrita mecânica; **NÃO EXECUTADO** |
| T102-012 | Qualidade das observações | Sem probe allowlisted | Evidência suficiente ou UNKNOWN; ausência parcial nunca equivale a negação; **NÃO EXECUTADO** |
| T102-013 | Qualidade das observações | Cobertura parcial positiva | Evidência suficiente ou UNKNOWN; ausência parcial nunca equivale a negação; **NÃO EXECUTADO** |
| T102-014 | Qualidade das observações | Ausência com cobertura parcial | Evidência suficiente ou UNKNOWN; ausência parcial nunca equivale a negação; **NÃO EXECUTADO** |
| T102-015 | Qualidade das observações | Prova negativa insuficiente | Evidência suficiente ou UNKNOWN; ausência parcial nunca equivale a negação; **NÃO EXECUTADO** |
| T102-016 | Qualidade das observações | Probe indisponível | Evidência suficiente ou UNKNOWN; ausência parcial nunca equivale a negação; **NÃO EXECUTADO** |
| T102-017 | Qualidade das observações | TTL excedido | Evidência suficiente ou UNKNOWN; ausência parcial nunca equivale a negação; **NÃO EXECUTADO** |
| T102-018 | Qualidade das observações | Observação futura inválida | Evidência suficiente ou UNKNOWN; ausência parcial nunca equivale a negação; **NÃO EXECUTADO** |
| T102-019 | Qualidade das observações | Duas observações discordantes | Evidência suficiente ou UNKNOWN; ausência parcial nunca equivale a negação; **NÃO EXECUTADO** |
| T102-020 | Qualidade das observações | Envelope read-only sem assinatura | Evidência suficiente ou UNKNOWN; ausência parcial nunca equivale a negação; **NÃO EXECUTADO** |
| T102-021 | Qualidade das observações | Proveniência de flag opaca | Evidência suficiente ou UNKNOWN; ausência parcial nunca equivale a negação; **NÃO EXECUTADO** |
| T102-022 | Qualidade das observações | Prova positiva de marco desconhecido | Evidência suficiente ou UNKNOWN; ausência parcial nunca equivale a negação; **NÃO EXECUTADO** |
| T102-023 | Interpretação semântica | Sem catálogo pinado | Marco curado consistente ou UNKNOWN/AMBIGUOUS; nenhuma inferência LLM; **NÃO EXECUTADO** |
| T102-024 | Interpretação semântica | Catálogo de outra build | Marco curado consistente ou UNKNOWN/AMBIGUOUS; nenhuma inferência LLM; **NÃO EXECUTADO** |
| T102-025 | Interpretação semântica | Predicados incompletos | Marco curado consistente ou UNKNOWN/AMBIGUOUS; nenhuma inferência LLM; **NÃO EXECUTADO** |
| T102-026 | Interpretação semântica | Dois milestones mutuamente exclusivos | Marco curado consistente ou UNKNOWN/AMBIGUOUS; nenhuma inferência LLM; **NÃO EXECUTADO** |
| T102-027 | Interpretação semântica | Estado UNKNOWN | Marco curado consistente ou UNKNOWN/AMBIGUOUS; nenhuma inferência LLM; **NÃO EXECUTADO** |
| T102-028 | Interpretação semântica | Estado AMBIGUOUS | Marco curado consistente ou UNKNOWN/AMBIGUOUS; nenhuma inferência LLM; **NÃO EXECUTADO** |
| T102-029 | Interpretação semântica | Estado CONTRADICTORY | Marco curado consistente ou UNKNOWN/AMBIGUOUS; nenhuma inferência LLM; **NÃO EXECUTADO** |
| T102-030 | Interpretação semântica | Estado BLOCKED_SPOILER | Marco curado consistente ou UNKNOWN/AMBIGUOUS; nenhuma inferência LLM; **NÃO EXECUTADO** |
| T102-031 | Interpretação semântica | Regressão sem transição curada | Marco curado consistente ou UNKNOWN/AMBIGUOUS; nenhuma inferência LLM; **NÃO EXECUTADO** |
| T102-032 | Interpretação semântica | Avanço curado com prova | Marco curado consistente ou UNKNOWN/AMBIGUOUS; nenhuma inferência LLM; **NÃO EXECUTADO** |
| T102-033 | Interpretação semântica | Revisão de catálogo após patch | Marco curado consistente ou UNKNOWN/AMBIGUOUS; nenhuma inferência LLM; **NÃO EXECUTADO** |
| T102-034 | Epochs e restore | Mesmo host/checkpoint epoch | Escopo temporal preservado; restore exige revisão e não merge automático; **NÃO EXECUTADO** |
| T102-035 | Epochs e restore | Host epoch avançou | Escopo temporal preservado; restore exige revisão e não merge automático; **NÃO EXECUTADO** |
| T102-036 | Epochs e restore | Checkpoint epoch regressou | Escopo temporal preservado; restore exige revisão e não merge automático; **NÃO EXECUTADO** |
| T102-037 | Epochs e restore | Save antigo restaurado | Escopo temporal preservado; restore exige revisão e não merge automático; **NÃO EXECUTADO** |
| T102-038 | Epochs e restore | Fork de branch autorizado | Escopo temporal preservado; restore exige revisão e não merge automático; **NÃO EXECUTADO** |
| T102-039 | Epochs e restore | Merge de ramo sem política | Escopo temporal preservado; restore exige revisão e não merge automático; **NÃO EXECUTADO** |
| T102-040 | Epochs e restore | Observation recebida após restore | Escopo temporal preservado; restore exige revisão e não merge automático; **NÃO EXECUTADO** |
| T102-041 | Epochs e restore | Snapshot anterior a save | Escopo temporal preservado; restore exige revisão e não merge automático; **NÃO EXECUTADO** |
| T102-042 | Epochs e restore | Modo Original versus Living World | Escopo temporal preservado; restore exige revisão e não merge automático; **NÃO EXECUTADO** |
| T102-043 | Epochs e restore | Troca de campanha em sessão | Escopo temporal preservado; restore exige revisão e não merge automático; **NÃO EXECUTADO** |
| T102-044 | Epochs e restore | Transição temporal fora do ano DR | Escopo temporal preservado; restore exige revisão e não merge automático; **NÃO EXECUTADO** |
| T102-045 | Estado persistido | Overlay idêntico ao host | Correção apenas de projeção derivada com prova; fatos antigos append-only; **NÃO EXECUTADO** |
| T102-046 | Estado persistido | Overlay atrasado com prova | Correção apenas de projeção derivada com prova; fatos antigos append-only; **NÃO EXECUTADO** |
| T102-047 | Estado persistido | Overlay adiantado na mesma epoch | Correção apenas de projeção derivada com prova; fatos antigos append-only; **NÃO EXECUTADO** |
| T102-048 | Estado persistido | Overlay com revisão desatualizada | Correção apenas de projeção derivada com prova; fatos antigos append-only; **NÃO EXECUTADO** |
| T102-049 | Estado persistido | Fato já confirmado diverge | Correção apenas de projeção derivada com prova; fatos antigos append-only; **NÃO EXECUTADO** |
| T102-050 | Estado persistido | Projeção derivada sem ID | Correção apenas de projeção derivada com prova; fatos antigos append-only; **NÃO EXECUTADO** |
| T102-051 | Estado persistido | Snapshot corrompido | Correção apenas de projeção derivada com prova; fatos antigos append-only; **NÃO EXECUTADO** |
| T102-052 | Estado persistido | Evento narrativo citado por NPC | Correção apenas de projeção derivada com prova; fatos antigos append-only; **NÃO EXECUTADO** |
| T102-053 | Estado persistido | Overlay de quest paralela | Correção apenas de projeção derivada com prova; fatos antigos append-only; **NÃO EXECUTADO** |
| T102-054 | Estado persistido | Ledger de fatos append-only | Correção apenas de projeção derivada com prova; fatos antigos append-only; **NÃO EXECUTADO** |
| T102-055 | Estado persistido | Projeção cancelada mas divulgada | Correção apenas de projeção derivada com prova; fatos antigos append-only; **NÃO EXECUTADO** |
| T102-056 | Receipts e gateway | Comando NOT_DISPATCHED | Reconciliar despacho incerto com host; não duplicar nem transformar observação em receipt; **NÃO EXECUTADO** |
| T102-057 | Receipts e gateway | Comando DISPATCH_PENDING | Reconciliar despacho incerto com host; não duplicar nem transformar observação em receipt; **NÃO EXECUTADO** |
| T102-058 | Receipts e gateway | Comando DISPATCHED | Reconciliar despacho incerto com host; não duplicar nem transformar observação em receipt; **NÃO EXECUTADO** |
| T102-059 | Receipts e gateway | Comando UNCERTAIN | Reconciliar despacho incerto com host; não duplicar nem transformar observação em receipt; **NÃO EXECUTADO** |
| T102-060 | Receipts e gateway | Host receipt ACK_UNKNOWN | Reconciliar despacho incerto com host; não duplicar nem transformar observação em receipt; **NÃO EXECUTADO** |
| T102-061 | Receipts e gateway | Receipt HOST_CONFIRMED | Reconciliar despacho incerto com host; não duplicar nem transformar observação em receipt; **NÃO EXECUTADO** |
| T102-062 | Receipts e gateway | Receipt ausente após timeout | Reconciliar despacho incerto com host; não duplicar nem transformar observação em receipt; **NÃO EXECUTADO** |
| T102-063 | Receipts e gateway | Duplicate receipt replay | Reconciliar despacho incerto com host; não duplicar nem transformar observação em receipt; **NÃO EXECUTADO** |
| T102-064 | Receipts e gateway | Compensação Saga pendente | Reconciliar despacho incerto com host; não duplicar nem transformar observação em receipt; **NÃO EXECUTADO** |
| T102-065 | Receipts e gateway | Resolução de combate observada | Reconciliar despacho incerto com host; não duplicar nem transformar observação em receipt; **NÃO EXECUTADO** |
| T102-066 | Receipts e gateway | Receipt de outro host epoch | Reconciliar despacho incerto com host; não duplicar nem transformar observação em receipt; **NÃO EXECUTADO** |
| T102-067 | Autorização e CAS | Request forja concessão ACL | Autorização externa, CAS/fencing; race ou falta de permissão falha fechada; **NÃO EXECUTADO** |
| T102-068 | Autorização e CAS | Audience desautorizada | Autorização externa, CAS/fencing; race ou falta de permissão falha fechada; **NÃO EXECUTADO** |
| T102-069 | Autorização e CAS | Purpose diferente de RECONCILE | Autorização externa, CAS/fencing; race ou falta de permissão falha fechada; **NÃO EXECUTADO** |
| T102-070 | Autorização e CAS | Scope de request divergente | Autorização externa, CAS/fencing; race ou falta de permissão falha fechada; **NÃO EXECUTADO** |
| T102-071 | Autorização e CAS | Política de acesso revogada | Autorização externa, CAS/fencing; race ou falta de permissão falha fechada; **NÃO EXECUTADO** |
| T102-072 | Autorização e CAS | Revisão overlay CAS coincidente | Autorização externa, CAS/fencing; race ou falta de permissão falha fechada; **NÃO EXECUTADO** |
| T102-073 | Autorização e CAS | Revisão overlay CAS conflitante | Autorização externa, CAS/fencing; race ou falta de permissão falha fechada; **NÃO EXECUTADO** |
| T102-074 | Autorização e CAS | Dois clientes aprovam mesma revisão | Autorização externa, CAS/fencing; race ou falta de permissão falha fechada; **NÃO EXECUTADO** |
| T102-075 | Autorização e CAS | Aprovação do host ausente | Autorização externa, CAS/fencing; race ou falta de permissão falha fechada; **NÃO EXECUTADO** |
| T102-076 | Autorização e CAS | Lock expirado com ação incerta | Autorização externa, CAS/fencing; race ou falta de permissão falha fechada; **NÃO EXECUTADO** |
| T102-077 | Autorização e CAS | Token fencing de sessão antiga | Autorização externa, CAS/fencing; race ou falta de permissão falha fechada; **NÃO EXECUTADO** |
| T102-078 | Ownership e quests nativas | Flag original protegida | Sem mutação em scripts/quests/mods/PCs; ownership e capacidade respeitados; **NÃO EXECUTADO** |
| T102-079 | Ownership e quests nativas | Script de romance original | Sem mutação em scripts/quests/mods/PCs; ownership e capacidade respeitados; **NÃO EXECUTADO** |
| T102-080 | Ownership e quests nativas | Quest de mod terceiro | Sem mutação em scripts/quests/mods/PCs; ownership e capacidade respeitados; **NÃO EXECUTADO** |
| T102-081 | Ownership e quests nativas | NPC nativo usado no marcador | Sem mutação em scripts/quests/mods/PCs; ownership e capacidade respeitados; **NÃO EXECUTADO** |
| T102-082 | Ownership e quests nativas | Item inventário de PC | Sem mutação em scripts/quests/mods/PCs; ownership e capacidade respeitados; **NÃO EXECUTADO** |
| T102-083 | Ownership e quests nativas | Variável de campanha original | Sem mutação em scripts/quests/mods/PCs; ownership e capacidade respeitados; **NÃO EXECUTADO** |
| T102-084 | Ownership e quests nativas | Write action sem capability | Sem mutação em scripts/quests/mods/PCs; ownership e capacidade respeitados; **NÃO EXECUTADO** |
| T102-085 | Ownership e quests nativas | Propagação de rebase a engine | Sem mutação em scripts/quests/mods/PCs; ownership e capacidade respeitados; **NÃO EXECUTADO** |
| T102-086 | Ownership e quests nativas | Override proposto por LLM | Sem mutação em scripts/quests/mods/PCs; ownership e capacidade respeitados; **NÃO EXECUTADO** |
| T102-087 | Ownership e quests nativas | Tentativa de resurrect NPC | Sem mutação em scripts/quests/mods/PCs; ownership e capacidade respeitados; **NÃO EXECUTADO** |
| T102-088 | Ownership e quests nativas | Mismatch de ownership campo | Sem mutação em scripts/quests/mods/PCs; ownership e capacidade respeitados; **NÃO EXECUTADO** |
| T102-089 | Privacidade e conhecimento | Spoiler em nome de flag | Sem spoiler, divulgação ou conhecimento automático; ACL por finalidade/audiência; **NÃO EXECUTADO** |
| T102-090 | Privacidade e conhecimento | Ramo futuro no payload | Sem spoiler, divulgação ou conhecimento automático; ACL por finalidade/audiência; **NÃO EXECUTADO** |
| T102-091 | Privacidade e conhecimento | Identidade protegida de NPC | Sem spoiler, divulgação ou conhecimento automático; ACL por finalidade/audiência; **NÃO EXECUTADO** |
| T102-092 | Privacidade e conhecimento | Romance privado de companion | Sem spoiler, divulgação ou conhecimento automático; ACL por finalidade/audiência; **NÃO EXECUTADO** |
| T102-093 | Privacidade e conhecimento | Log de diagnóstico com segredo | Sem spoiler, divulgação ou conhecimento automático; ACL por finalidade/audiência; **NÃO EXECUTADO** |
| T102-094 | Privacidade e conhecimento | Cache de outro destinatário | Sem spoiler, divulgação ou conhecimento automático; ACL por finalidade/audiência; **NÃO EXECUTADO** |
| T102-095 | Privacidade e conhecimento | LLM recebe estado bruto | Sem spoiler, divulgação ou conhecimento automático; ACL por finalidade/audiência; **NÃO EXECUTADO** |
| T102-096 | Privacidade e conhecimento | NPC distante sem fonte | Sem spoiler, divulgação ou conhecimento automático; ACL por finalidade/audiência; **NÃO EXECUTADO** |
| T102-097 | Privacidade e conhecimento | Rumor derivado de rebase | Sem spoiler, divulgação ou conhecimento automático; ACL por finalidade/audiência; **NÃO EXECUTADO** |
| T102-098 | Privacidade e conhecimento | Dossiê sem ACL de fonte | Sem spoiler, divulgação ou conhecimento automático; ACL por finalidade/audiência; **NÃO EXECUTADO** |
| T102-099 | Privacidade e conhecimento | Sessão LAN com audience diferente | Sem spoiler, divulgação ou conhecimento automático; ACL por finalidade/audiência; **NÃO EXECUTADO** |
| T102-100 | Concorrência e idempotência | Mesmo operation_id duplicado | No máximo uma revisão elegível; repetição idempotente e auditável; **NÃO EXECUTADO** |
| T102-101 | Concorrência e idempotência | Retry após crash | No máximo uma revisão elegível; repetição idempotente e auditável; **NÃO EXECUTADO** |
| T102-102 | Concorrência e idempotência | Processamento em ordem inversa | No máximo uma revisão elegível; repetição idempotente e auditável; **NÃO EXECUTADO** |
| T102-103 | Concorrência e idempotência | Dois workers para mesma quest | No máximo uma revisão elegível; repetição idempotente e auditável; **NÃO EXECUTADO** |
| T102-104 | Concorrência e idempotência | Reserva host uncertain | No máximo uma revisão elegível; repetição idempotente e auditável; **NÃO EXECUTADO** |
| T102-105 | Concorrência e idempotência | Replay em branch diferente | No máximo uma revisão elegível; repetição idempotente e auditável; **NÃO EXECUTADO** |
| T102-106 | Concorrência e idempotência | Revisão simultânea de mapper | No máximo uma revisão elegível; repetição idempotente e auditável; **NÃO EXECUTADO** |
| T102-107 | Concorrência e idempotência | Revogação durante CAS | No máximo uma revisão elegível; repetição idempotente e auditável; **NÃO EXECUTADO** |
| T102-108 | Concorrência e idempotência | Ledger aplicado duas vezes | No máximo uma revisão elegível; repetição idempotente e auditável; **NÃO EXECUTADO** |
| T102-109 | Concorrência e idempotência | Diferentes clientes conectados | No máximo uma revisão elegível; repetição idempotente e auditável; **NÃO EXECUTADO** |
| T102-110 | Concorrência e idempotência | Reexecução após checkpoint | No máximo uma revisão elegível; repetição idempotente e auditável; **NÃO EXECUTADO** |
| T102-111 | POCs de integração | BG2:EE limpo Windows | Registrar capability e resultado observável; se não demonstrado, permanecer bloqueado; **NÃO EXECUTADO** |
| T102-112 | POCs de integração | EEex com build conhecida | Registrar capability e resultado observável; se não demonstrado, permanecer bloqueado; **NÃO EXECUTADO** |
| T102-113 | POCs de integração | Bridge read-only comprovada | Registrar capability e resultado observável; se não demonstrado, permanecer bloqueado; **NÃO EXECUTADO** |
| T102-114 | POCs de integração | Modpack com scripts alterados | Registrar capability e resultado observável; se não demonstrado, permanecer bloqueado; **NÃO EXECUTADO** |
| T102-115 | POCs de integração | Host com dois clientes | Registrar capability e resultado observável; se não demonstrado, permanecer bloqueado; **NÃO EXECUTADO** |
| T102-116 | POCs de integração | Save/load repetido | Registrar capability e resultado observável; se não demonstrado, permanecer bloqueado; **NÃO EXECUTADO** |
| T102-117 | POCs de integração | Restore após quest completa | Registrar capability e resultado observável; se não demonstrado, permanecer bloqueado; **NÃO EXECUTADO** |
| T102-118 | POCs de integração | Falha LAN durante leitura | Registrar capability e resultado observável; se não demonstrado, permanecer bloqueado; **NÃO EXECUTADO** |
| T102-119 | POCs de integração | Latência alta de observer | Registrar capability e resultado observável; se não demonstrado, permanecer bloqueado; **NÃO EXECUTADO** |
| T102-120 | POCs de integração | Desconexão do host | Registrar capability e resultado observável; se não demonstrado, permanecer bloqueado; **NÃO EXECUTADO** |
| T102-121 | POCs de integração | Modo FROZEN/PARTIAL/REALTIME | Registrar capability e resultado observável; se não demonstrado, permanecer bloqueado; **NÃO EXECUTADO** |
| T102-122 | Falhas e governança | Observação em quarentena | Histórico causal e logs seguros; conflito pendente até autorização/evidência; **NÃO EXECUTADO** |
| T102-123 | Falhas e governança | Mudança não autorizada de timeline | Histórico causal e logs seguros; conflito pendente até autorização/evidência; **NÃO EXECUTADO** |
| T102-124 | Falhas e governança | Tentativa de editar fatos passados | Histórico causal e logs seguros; conflito pendente até autorização/evidência; **NÃO EXECUTADO** |
| T102-125 | Falhas e governança | Confirmação narrativa sem receipt | Histórico causal e logs seguros; conflito pendente até autorização/evidência; **NÃO EXECUTADO** |
| T102-126 | Falhas e governança | Contradição não explicável | Histórico causal e logs seguros; conflito pendente até autorização/evidência; **NÃO EXECUTADO** |
| T102-127 | Falhas e governança | Curadoria de transição incompleta | Histórico causal e logs seguros; conflito pendente até autorização/evidência; **NÃO EXECUTADO** |
| T102-128 | Falhas e governança | Mapa canônico anual imutável | Histórico causal e logs seguros; conflito pendente até autorização/evidência; **NÃO EXECUTADO** |
| T102-129 | Falhas e governança | Plano de rollback global indevido | Histórico causal e logs seguros; conflito pendente até autorização/evidência; **NÃO EXECUTADO** |
| T102-130 | Falhas e governança | Auditoria de corroboração falsa | Histórico causal e logs seguros; conflito pendente até autorização/evidência; **NÃO EXECUTADO** |
| T102-131 | Falhas e governança | Sinalização de UNKNOWN no UI | Histórico causal e logs seguros; conflito pendente até autorização/evidência; **NÃO EXECUTADO** |
| T102-132 | Falhas e governança | Mudança de política em tempo real | Histórico causal e logs seguros; conflito pendente até autorização/evidência; **NÃO EXECUTADO** |

## 11. Critérios de aceitação futura

1. POC Windows com BG2:EE clean → EEex → bridge; baseline reproduzível por build/modpack/quest.
2. Observadores DEC-100 com cobertura de flags/sinais demonstrada sem efeitos colaterais e mapeadores DEC-101 curados sem spoilers.
3. Snapshots e receipts host confiáveis, save/load e restore em duas linhas temporais; nenhuma reescrita automática de flags, scripts, inventários, fatos ou memória.
4. Quarentena sem deadlock para `UNCERTAIN`, migrações, branch fork e transições desconhecidas; reconciliação sob autorização independente.
5. Com dois clientes, CAS/fencing real mantém uma única revisão elegível, e nenhuma divulgação cross-client de segredos.
6. Registro de métricas sem vazamento, prova de independência de LLM, testes adversariais e regressões após mudanças de modpack.

**Próxima DEC-103 em aberto:** política causal de admissão de marcos reconciliados como insumos para rumores, eventos, reputação ou cronologia; opções A eager autoemit, B LLM livre, C pipeline versionado com proof, audiences, gates e dedup.


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** observar DEC-100, interpretar DEC-101 e reconciliar DEC-102 não são eventos automaticamente propagáveis. Apenas prova semântica atual e reconciliação `CONSISTENT_WITH_PROOF` ou `APPROVED_AND_COMMITTED_REBASE` habilita pedido de admissão lógica por ruleset pinado; rebase `PROPOSE_*` não permite emissão. Proposta, autorização, receipt host e conhecimento de NPC permanecem entidades separadas. Não reabrir quest, editar flags, alterar scripts nem assumir ownership por narrativa. Dedup por occurrence/lineage, sem duplicação após save/load ou observação repetida. Consultar `docs/103-admissao-e-propagacao-causal-de-marcos-de-quests-reconciliados.md`. **Sem POC no motor.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **proof committed e escopo da reconciliação**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para reconciliação de quest não cria conhecimento social automático, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para reconciliação de quest preserva histórico narrativo, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de obrigações e monitoramento não coercitivo

Reconciliação de save, epochs e host não reescreve recibo de transferência confirmado. Fonte: ADR-0103/doc.108; claims ≠ comprovantes, prazos DR ≠ culpa, status `UNCERTAIN` bloqueia nova ação, sem mutações do host. POCs BG2:EE/EEex e T108-001..160 **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Reconciliação de quest mantém os receipts prévios imutáveis. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
