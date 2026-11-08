# 103 — Admissão e propagação causal de marcos de quests reconciliados

**Estado:** DEC-103/C **APROVADA COMO ARQUITETURA**, 2026-11-07 · Discovery v9.9 · ADR-0098. **Sem implementação testada em BG2:EE/EEex, sem hooks reais, sem multiplayer host+2 clientes.** As decisões DEC-060–102 e todos os ADRs anteriores continuam vinculantes.

## 1. Objetivo, escopo e limites

Conectar a conclusão de uma etapa/quest **realmente verificada** a propostas de consequências no Living World: rumores locais, ajustes narrativos, reações de facções, reputação, economia e oportunidades. O sistema não deve divulgar spoilers, fingir onisciência, reexecutar recompensas, duplicar spawns ou modificar quests originais. Precisa funcionar mesmo sem LLM e falhar fechado perante incerteza.

O **marco técnico observado** (DEC-100), sua **interpretação semântica** (DEC-101), a **reconciliação entre host/overlay** (DEC-102), a **admissão causal**, o **efeito de mundo mecânico**, o **rumor transmitido** e o **conhecimento do destinatário** são registros diferentes, com autoridades e processos de confirmação independentes.

## 2. Contratos de dados, autoridade e persistência

| Entidade | Campos mínimos | Fonte de autoridade | Significado e proibição |
|---|---|---|---|
| `VerifiedMilestoneProof` | `proof_id`, `quest_key`, `variant`, `milestone_id`, `occurrence_id`, `source_semantic_proof`, `coverage`, `freshness`, `mapping_revision`, `reconciliation_commit_id`, `host_epoch`, `checkpoint_epoch` | catálogos curados + observer/reconciler trusted store | Comprova marco pontual; **não** é host action receipt. Não confia em `proof` embutida no pedido |
| `QuestAdmissionRequest` | `operation_id`, `proof_ref`, `purpose`, `audience`, `campaign/branch`, `expected_ledger_revision` | cliente solicitante, **sem** direitos embutidos | Pede análise, não concede ACL, não prova resultados |
| `TrustedAdmissionPolicy` | `revision`, escopos, finalidades, audiência, limites de idade de observação, risk gates | serviço de ACL/policy aprovado | Permissões não são retornadas por LLM, prompt ou request |
| `PinnedQuestConsequenceRule` | `rule_id`, `revision`, `milestone_ref`, domain, time_window, region_ids, effects, prerequisites, `max_risk`, `visibility_policy` | curadoria editorial pinada à build e KPack | Define elegibilidade, nunca mutação direta |
| `AdmissionDecision` | `status`, `reason_code`, `dedup_key`, `rule_refs`, `ledger_revision`, `proof_digest` | avaliador determinístico e outbox transacional | `ADMITTED` autoriza registro lógico, não spawn ou rumor |
| `ConsequenceProposal` | `candidate_id`, `admission_id`, `rule_ref`, `scope`, `expected_impact`, `risk`, `required_gates` | ruleset e estado confirmado | Proposta sempre independente da execução host |
| `HostConsequenceReceipt` | `host_action_id`, `session_epoch`, `idempotency_key`, `result`, `effect_scope` | host/Action Gateway | Única confirmação mecânica autorizada; observação read-only não substitui receipt |
| `NewsTransmission` | `claim_id`, `source_actor`, `channel`, `sent_at_dr`, `recipient`, `scope`, `delivery_id` | módulo de propagação DEC-029/074/090 | Enviado não equivale a recebido nem a fato conhecido |
| `RecipientKnowledge` | `actor_id`, `claim_id`, `provenance`, `received_at_dr`, `confidence`, `scope` | entrega comprovada e ACL | Conhecimento/crença subjetivos; não alteram o cânone |

**Partições:** `knowledge/periods/<YEAR>-DR/` permanece somente-leitura e físicamente segregado (DEC-060–063); os catálogos de regras e mapeamentos são publicados com hash. As admissões, propostas, receipts e notícias ficam em `campaign_id/branch_id/lineage/epoch`, sob políticas e auditoria. Nunca misturar overlays ou knowledge de campanhas diferentes.

### Identidade da ocorrência e chave de idempotência

```text
admission_key := H(campaign, branch, quest_variant, milestone_id,
                   certified_occurrence_id, canonical_branch_lineage,
                   curated_rule_revision, source_mapping_revision)
consequence_key := H(admission_key, rule_id, intended_scope, effect_kind)
```

`session_id`, ID de leitura, timestamp do processo e texto de rumor **NÃO** definem identidade de ocorrência: após sair e retornar ao mapa, o mesmo marco deve ser deduplicado. Um marco repetível só recebe `certified_occurrence_id` novo quando o host/curadoria conseguem comprovar repetição legítima. Restore/fork exige nova análise, nunca reemissão por simples troca de epoch. Chaves de conteúdo são persistidas com hash e revisões; não substituir uma regra sem migração explicitamente aprovada.

## 3. Pipeline determinístico (fluxo normativo)

```text
in(request):
    require authorized_request_identity(); check_campaign_branch_purpose()
    proof = trusted_registry.lookup(request.proof_ref)           # NUNCA da request
    require proof.source == DEC100_101 && proof.coverage == FULL
    require proof.semantic_status == MAPPED_MINIMAL && proof.fresh
    require proof.mapping_revision == pinned_mapping_revision
    reconciled = trusted_reconciliation.lookup(proof.reconciliation_commit_id)
    require reconciled == CONSISTENT_WITH_PROOF
         or reconciled == APPROVED_AND_COMMITTED_DERIVED_REBASE
    require same_lineage_epochs_build_modpack_checkpoint && !uncertain_dispatch
    require viewer_acl_and_source_secrecy_verified()
    admission_key = calculate_stable_occurrence_key(proof)
    if admission_key in admitted_or_pending: return DUPLICATE_SUPPRESSED
    rule_set = trusted_curated_catalog.lookup_pinned(proof.quest_key)
    for rule in rule_set.sorted_by_id:
        require rule.milestone_matches && time_and_branch_allow && geography_allow
        require typed_predicates(confirmed_state) == TRUE
        require risk_scope_resources_acl_rule_compatibility
        propose_only(rule, admission_key)   # sem host, sem LLM, sem send
    atomically append admission + outbox with CAS/fencing

outbox_worker(proposal):
    authorized_risk_check(); ownership_build_capability_check(); reserve_resources()
    if mechanical: ActionGateway -> host receipt -> append AppliedImpact
    if informational: distinct channel/send -> delivery proof -> RecipientKnowledge
    if UNCERTAIN: quarantine; no blind retry
```

`APPROVED_AND_COMMITTED_DERIVED_REBASE` não deve ser confundido com `PROPOSE_DERIVED_VIEW_REBASE` **pendente**. Se houver `UNKNOWN/AMBIGUOUS/QUARANTINED`, `BLOCKED_MAPPING`, `RESTORE_REVIEW_REQUIRED`, observação fora de época, mod incompatível ou ACL ausente: **não admitir**.

## 4. Estados e transições

- `NO_PROOF`, `BLOCKED_ACL`, `BLOCKED_MAPPING`, `BLOCKED_RULE`, `UNKNOWN`, `QUARANTINED`: zero admissão, zero evento novo. Motivo minimizado por audiência para não revelar segredo.
- `ELIGIBLE` → `ADMITTED`: somente mediante CAS/ledger/outbox; a decisão de admissão não comprova mutação, rumor ou descoberta por NPC.
- `ADMITTED` → `PROPOSED`: regra curada elegível; zero propostas é válido e pode ser final.
- `PROPOSED` → `RISK_VALIDATED` → `AUTHORIZED` → `DISPATCHED` → `HOST_CONFIRMED`: **somente** efeitos mecânicos; `DISPATCHED`/`UNCERTAIN` não pode ser repetido sem conciliação.
- `PROPOSED` → `CHANNEL_APPROVED` → `SENT` → `DELIVERED` → `KNOWLEDGE_ACQUIRED`: ramo **informacional separado**, com proof de entrega, tempo DR, audiência e direito de saber.
- `DUPLICATE_SUPPRESSED`: retorna o mesmo ID prévio; não gera novo outbox/efeito.
- `EXPIRED` e `REVOKED`: impedem novos eventos, sem apagar ações confirmadas; discussões de cascata na DEC-104.

## 5. Relação com matriz e outros módulos

1. **DEC-096** (matriz temporal/geográfica): um marco técnico de quest não assume mês desconhecido ou aplica evento global; ruleset avalia ano DR, fase, hora, região, tipo de local e divergência histórica. Mapeamento de área precisa build certificada.
2. **DEC-097** (compositor): várias causas na mesma variável usam política por domínio, caps, dedup e decaimento. Uma contribuição de quest não apaga impacto canônico anterior nem modifica indicador por LLM.
3. **DEC-098** (materialização): diferenças de estado usam snapshots host-confirmed e identidade NPC persistente; não nascer mais guardas a cada save/load/reentry.
4. **DEC-099** (ownership): nem a conclusão de quest autoriza editar scripts, romance, itens de PC ou mods; campos/instâncias precisam capabilities e gates próprios.
5. **DEC-074/075/029**: fatos e atribuição, conhecimento propagado e rumores são distintos; não inventar testemunhas nem conceder reconhecimento a PC ausente.
6. **DEC-076/083/085/090**: identidades reais, testemunhas, fontes confidenciais e dossiês são filtrados por ACL antes de qualquer rumor/LLM. Acesso técnico de host não é direito narrativo.
7. **DEC-091–095**: propostas dependem da disponibilidade de recursos, consentimento, planejamento, concorrência, handling de deadlocks e compensações como novos fatos.
8. **DEC-100/101/102**: identidade exata da quest/mod/version, prova read-only, catálogo semântico curado e resultado de reconciliação comprometido formam *prérequisitos*, não autorizações mecânicas.
9. **DEC-060–063**: canon por ano DR nunca recebe escrita de outcomes da campanha. `KnowledgePack` pinado e branches isolados.

## 6. Privacidade, segurança e anti-spoilers

- **Proibir vazamento por derivação:** não usar `semantic_id` secreto como nome de evento público, ID de outbox visível, métricas indexáveis, nome de arquivo, erro ou prompt. IDs publicados são opacos; erros usam código minimizado.
- **Separar escopos:** ACL de quem pode iniciar admissão ≠ ACL de rule ≠ ACL de rumor ≠ direito de interpretar flag técnica. Um diretor narrativo só recebe projeção apropriada após autorização e canal de entrega comprovado.
- **Não interpretar silêncio como ausência:** ausência com cobertura parcial ou delay não torna quest `FALSE` ou concluída.
- **Critérios anti-onisciência:** o rumor requer observador/canal e custo temporal/geográfico; NPC pode acreditar em informação errada sem alterar verdade factual.
- **Proteção multiplayer:** somente host autoridade de mutação; non-host não publica receipt; revisão e fencing garantem idempotência em concorrência. Falhas entre outbox e effect receipt levam a `UNCERTAIN`/reconciliation.
- **Threat model:** replay entre branches; forging de `proof_id` em pedido; injeção de acesso por `is_admin` na request; confusão de namespace de quest entre mods; cap de efeitos desatualizado; duplicação após restore; inferência de spoiler por status/contagem; LLM comandando escrita; falso `DELIVERED`; timestamps reais usados para aplicar regras DR; uso de dados de outro ano DR.

## 7. Exemplos sintéticos (nenhum evento oficial de FR)

**Cenário SYN-Q-A:** uma quest de teste chega a `SYN-MILESTONE-COMPLETE` com `MAPPED_MINIMAL`, cobertura completa, mesmo lineage/build e reconciliação `CONSISTENT_WITH_PROOF`. O ruleset fictício tem duas regras: `SYN-R-RUMOR`, propondo notícia em um estabelecimento se existir um informante elegível, e `SYN-R-FACTION`, propondo alteração de atitude de facção local. O avaliador lógico produz uma admissão e **duas propostas**, com `engine_writes=0` e `npc_knowledge_updated=false`. Nenhuma facção muda até autorização/receipts; nenhuma notícia é conhecida antes da prova de entrega.

**Cenário SYN-Q-B:** a mesma quest é observada novamente após sair e entrar no mapa, com novo `observation_id`, mas mesmo `certified_occurrence_id`. A chave de admissão é igual: `DUPLICATE_SUPPRESSED`, zero novas propostas/outbox.

**Cenário SYN-Q-C:** a observação é válida, porém o reconciliador apenas **propôs** um rebase e não há CAS de commit. Não admitir nada: `QUARANTINED/REBASE_NOT_COMMITTED`.

**Cenário SYN-Q-D:** um rumor é permitido narrativamente, mas a identidade real da testemunha está protegida. A proposta recebe apenas a alegação pública curada; informação protegida não chega aos prompts nem aos outros NPCs.

## 8. Contratos candidatos e POCs

- `examples/chronology/quest_consequence_admission_v1.candidate.schema.json`: contratos sintéticos de request, prova, política e catálogo; **não** schema de uma API do EEex.
- `examples/chronology/quest_consequence_admission_v1.synthetic.json`: fixture inteiramente fictícia, sem quests oficiais.
- `examples/chronology/quest_consequence_admission_reference.py`: avaliador puro *fail-closed*, sem rede, sem host, sem mutações, sem LLM.
- `examples/chronology/test_quest_consequence_admission_reference.py`: testes unitários sintéticos; não substituem POCs.
- **Não executados:** todos os 136 cenários `T103-001..T103-136` abaixo, dependentes de fixtures verificadas de builds, segurança/privacidade, host+dois clientes e capacidades reais. Aprovação de arquitetura não afirma compatibilidade funcional.

### Critérios de aceite de integração futura

**GATE-Q103.1 — Read-only real:** provar que observações usam somente allowlist DEC-100, inclusive após restart/patch e multiplayer.

**GATE-Q103.2 — Semântica e rebase:** demonstrar prova curada DEC-101 e reconciliação efetivamente committed DEC-102, com epoch/branch/save.

**GATE-Q103.3 — Segurança ACL:** nenhum spoiler de raw flags/identidades reais nos logs, prompts, erros ou dossiês.

**GATE-Q103.4 — Dedup de sessão/branch:** repetir reads/reentries/save/load/replays não duplica eventos; fork válido não mistura estados.

**GATE-Q103.5 — Efeito host:** propostas não mutam jogo; effects mecânicos só via Action Gateway, receipts e idempotência.

**GATE-Q103.6 — Conhecimento:** divulgação somente após canal e entrega provada; nenhum rumor instantâneo global.

**GATE-Q103.7 — Compatibilidade:** mods, quests e ownership sem alterações indevidas, detectar mudanças em build/modpack.

**GATE-Q103.8 — Performance e recuperação:** orçamentos, no deadlocks, reprocessamento de outbox com fencing e `UNCERTAIN`/restore.

## 9. Matriz de testes candidatos (todos NÃO EXECUTADOS)

As linhas a seguir definem **cenários de POC** para implementação futura. **Nenhum é resultado experimental**. IDs únicos e estabilidade para rastrear a futura validação.


### 1. Fonte e prova

| ID | Cenário candidato | Verificação esperada |
|---|---|---|
| T103-001 | source adapter adulterado | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-002 | ausência de proof_ref | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-003 | origem do proof incompatível | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-004 | cobertura parcial | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-005 | observação stale | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-006 | prova com timestamp futuro | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-007 | mesmo milestone com proof novo | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-008 | prova de ocorrência repetível ausente | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |

### 2. Quest e versões

| ID | Cenário candidato | Verificação esperada |
|---|---|---|
| T103-009 | build fingerprint divergente | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-010 | modpack diferente | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-011 | quest variante não mapeada | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-012 | mapping revision revogada | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-013 | script digest incompatível | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-014 | rulepack não pinado | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-015 | quest duplicada em outro mod | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-016 | migração de build sem certificação | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |

### 3. Reconciliação DEC-102

| ID | Cenário candidato | Verificação esperada |
|---|---|---|
| T103-017 | CONSISTENT com prova válida | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-018 | CONSISTENT sem prova suficiente | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-019 | rebase apenas proposto | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-020 | rebase aprovado ainda não committed | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-021 | rebase CAS committed | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-022 | RESTORE_REVIEW_REQUIRED | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-023 | estado QUARANTINED | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-024 | marco AMBIGUOUS | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |

### 4. Branch e epochs

| ID | Cenário candidato | Verificação esperada |
|---|---|---|
| T103-025 | host epoch anterior | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-026 | checkpoint epoch divergente | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-027 | lineage restaurada | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-028 | fork paralelo | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-029 | save antigo reaberto | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-030 | session id novo mesma occurrence | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-031 | branch A vs branch B | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-032 | host não confirma identidade | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |

### 5. Permissões ACL

| ID | Cenário candidato | Verificação esperada |
|---|---|---|
| T103-033 | usuário sem finalidade | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-034 | audience ALL_NPCS | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-035 | solicitação forja is_admin | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-036 | solicitação forja grant | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-037 | policy registry não confiável | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-038 | fonte PROTECTED sem permissão | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-039 | regra pública com fonte protegida | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-040 | publicação em contexto remoto não autorizado | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |

### 6. Spoilers e segredos

| ID | Cenário candidato | Verificação esperada |
|---|---|---|
| T103-041 | flag bruta em prompt | nenhum dado sensível em saída, prompt, log ou índice acessível sem ACL |
| T103-042 | nome oculto em candidate ID | nenhum dado sensível em saída, prompt, log ou índice acessível sem ACL |
| T103-043 | segredo em reason_code | nenhum dado sensível em saída, prompt, log ou índice acessível sem ACL |
| T103-044 | metadado privado em ledger público | nenhum dado sensível em saída, prompt, log ou índice acessível sem ACL |
| T103-045 | romance secreto | nenhum dado sensível em saída, prompt, log ou índice acessível sem ACL |
| T103-046 | identidade protegida DEC-083 | nenhum dado sensível em saída, prompt, log ou índice acessível sem ACL |
| T103-047 | quest futura não vista | nenhum dado sensível em saída, prompt, log ou índice acessível sem ACL |
| T103-048 | log contém raw script | nenhum dado sensível em saída, prompt, log ou índice acessível sem ACL |

### 7. Clock DR

| ID | Cenário candidato | Verificação esperada |
|---|---|---|
| T103-049 | mês dentro da janela | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-050 | mês fora da janela | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-051 | ano diferente | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-052 | evento YEAR_ONLY sem mês | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-053 | modo FROZEN | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-054 | evento AFTERMATH sem pai | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-055 | dia intercalar | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-056 | horário do sistema não altera DR | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |

### 8. Geografia

| ID | Cenário candidato | Verificação esperada |
|---|---|---|
| T103-057 | região correta | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-058 | região errada | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-059 | área não mapeada | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-060 | tipo local incompatível | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-061 | scope global não implica mapa | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-062 | dungeon isolada de cidade | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-063 | rota inacessível | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-064 | actor sem presença comprovada | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |

### 9. Pré-condições

| ID | Cenário candidato | Verificação esperada |
|---|---|---|
| T103-065 | flag confirmada verdadeira | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-066 | flag confirmada falsa | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-067 | flag ausente/UNKNOWN | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-068 | predicado string vs inteiro | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-069 | predicado tipado inválido | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-070 | dependência do effect pai | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-071 | precondição revogada | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-072 | llm tenta inventar uma flag | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |

### 10. Composição DEC-097

| ID | Cenário candidato | Verificação esperada |
|---|---|---|
| T103-073 | duas causas independentes | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-074 | mesma causa repetida | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-075 | caps superiores | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-076 | caps inferiores | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-077 | precedência curada | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-078 | empate sem precedência | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-079 | decaimento no relógio DR | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-080 | modificador expirado | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |

### 11. Idempotência

| ID | Cenário candidato | Verificação esperada |
|---|---|---|
| T103-081 | mesmo observation id | mesma ocorrência → mesma dedup key, salvo nova ocorrência certificada; zero duplicação |
| T103-082 | observation id diferente mesmo occurrence | mesma ocorrência → mesma dedup key, salvo nova ocorrência certificada; zero duplicação |
| T103-083 | save/load repetido | mesma ocorrência → mesma dedup key, salvo nova ocorrência certificada; zero duplicação |
| T103-084 | reentrada no mapa | mesma ocorrência → mesma dedup key, salvo nova ocorrência certificada; zero duplicação |
| T103-085 | mesmo milestone com nova operação | mesma ocorrência → mesma dedup key, salvo nova ocorrência certificada; zero duplicação |
| T103-086 | duplo request simultâneo | mesma ocorrência → mesma dedup key, salvo nova ocorrência certificada; zero duplicação |
| T103-087 | outbox pendente | mesma ocorrência → mesma dedup key, salvo nova ocorrência certificada; zero duplicação |
| T103-088 | nova ocorrência genuinamente comprovada | mesma ocorrência → mesma dedup key, salvo nova ocorrência certificada; zero duplicação |

### 12. Receipts host

| ID | Cenário candidato | Verificação esperada |
|---|---|---|
| T103-089 | proposta sem execução | não confundir observação/read-only/dispatch com receipt host-confirmed |
| T103-090 | DISPATCH_PENDING | não confundir observação/read-only/dispatch com receipt host-confirmed |
| T103-091 | DISPATCHED sem receipt | não confundir observação/read-only/dispatch com receipt host-confirmed |
| T103-092 | UNCERTAIN após timeout | não confundir observação/read-only/dispatch com receipt host-confirmed |
| T103-093 | HOST_CONFIRMED com chave correta | não confundir observação/read-only/dispatch com receipt host-confirmed |
| T103-094 | receipt de outra campanha | não confundir observação/read-only/dispatch com receipt host-confirmed |
| T103-095 | retry cego negado | não confundir observação/read-only/dispatch com receipt host-confirmed |
| T103-096 | compensação DEC-095 distinta | não confundir observação/read-only/dispatch com receipt host-confirmed |

### 13. NPC e comunicação

| ID | Cenário candidato | Verificação esperada |
|---|---|---|
| T103-097 | rumor sem testemunha | sem aquisição de conhecimento até entrega legítima comprovada e autorização |
| T103-098 | mensageiro enviado não entregue | sem aquisição de conhecimento até entrega legítima comprovada e autorização |
| T103-099 | canal cortado | sem aquisição de conhecimento até entrega legítima comprovada e autorização |
| T103-100 | destinatário fora da região | sem aquisição de conhecimento até entrega legítima comprovada e autorização |
| T103-101 | recebimento confirmado | sem aquisição de conhecimento até entrega legítima comprovada e autorização |
| T103-102 | crença contradiz fato | sem aquisição de conhecimento até entrega legítima comprovada e autorização |
| T103-103 | informante mente | sem aquisição de conhecimento até entrega legítima comprovada e autorização |
| T103-104 | sem broadcast instantâneo global | sem aquisição de conhecimento até entrega legítima comprovada e autorização |

### 14. Ownership e materialização

| ID | Cenário candidato | Verificação esperada |
|---|---|---|
| T103-105 | quest original dona do NPC | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-106 | mod terceiro dona da instância | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-107 | item pertence ao PC | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-108 | objeto previamente despawnado | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-109 | NPC persistente já instanciado | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-110 | spawn duplicado após reentry | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-111 | recurso faltante | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-112 | build não certificada | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |

### 15. Risco e consentimento

| ID | Cenário candidato | Verificação esperada |
|---|---|---|
| T103-113 | efeito LOW narrativo | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-114 | efeito HIGH sem autorização | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-115 | efeito HIGH com gate | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-116 | PC ausente sem consentimento | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-117 | PVP não autorizado | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-118 | prisão automatizada | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-119 | recurso compartilhado sem reserva | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-120 | cancelamento mantém fatos confirmados | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |

### 16. Concorrência e recuperação

| ID | Cenário candidato | Verificação esperada |
|---|---|---|
| T103-121 | CAS revisão diferente | CAS, fencing e reconciliação; não repetir nem publicar em estado incerto |
| T103-122 | fencing token expirado | CAS, fencing e reconciliação; não repetir nem publicar em estado incerto |
| T103-123 | duas instâncias outbox | CAS, fencing e reconciliação; não repetir nem publicar em estado incerto |
| T103-124 | outbox entrega pelo menos uma vez | CAS, fencing e reconciliação; não repetir nem publicar em estado incerto |
| T103-125 | ledger event append duplicado | CAS, fencing e reconciliação; não repetir nem publicar em estado incerto |
| T103-126 | crash entre outbox e host | CAS, fencing e reconciliação; não repetir nem publicar em estado incerto |
| T103-127 | restauração de checkpoint | CAS, fencing e reconciliação; não repetir nem publicar em estado incerto |
| T103-128 | reconciliação pós-restart | CAS, fencing e reconciliação; não repetir nem publicar em estado incerto |

### 17. Curadoria e validação

| ID | Cenário candidato | Verificação esperada |
|---|---|---|
| T103-129 | fonte canônica por ano DR | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-130 | revisão KPack antiga | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-131 | claim disputa histórica | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-132 | regra alterada sem pin | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-133 | fixture sintética marcada como cânone | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-134 | marco sem regra de repercussão | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-135 | POC com dois clientes | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |
| T103-136 | LLM indisponível e código determinístico ativo | admitir/propor só se todos os gates aplicáveis forem verdadeiros; caso contrário bloquear/quarentenar sem efeitos/entrega e preservar audit trail |

## 10. Próxima DEC-104 (EM ABERTO)

**Pergunta:** como retificar um marco posteriormente contestado quando suas consequências já foram propostas, comunicadas ou host-confirmed? **A** rollback em cascata; **B** LLM reescreve; **C recomendada** dependências, suspensão de novas derivações, versões corrigidas e compensações DEC-095 separadas, sem apagar fatos ou conhecimento já recebido. Esta seção **não aprova a DEC-104**.

## 11. Governança e conclusão

ADR-0098 vincula a DEC-103/C como arquitetura. Nenhuma integração técnica com BG2:EE/EEex/bridge foi demonstrada. A matriz de 136 cenários é **PENDENTE e NÃO EXECUTADA**. Exemplos e testes unitários abaixo são puramente sintéticos e não equivalem à validação do jogo.

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **admission/outbox e correções posteriores**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para admissão causal de quest gera propostas, não recepção universal, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para admissão de marco gera efeitos candidatos, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de obrigações e monitoramento não coercitivo

Marco de quest admitido não ativa cobrança, prazo, multa nem contrato automático. Fonte: ADR-0103/doc.108; claims ≠ comprovantes, prazos DR ≠ culpa, status `UNCERTAIN` bloqueia nova ação, sem mutações do host. POCs BG2:EE/EEex e T108-001..160 **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Admissão de marco de quest não satisfaz cláusula sem prova específica. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
