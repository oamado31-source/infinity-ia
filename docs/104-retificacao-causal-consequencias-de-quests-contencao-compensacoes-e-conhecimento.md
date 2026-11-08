# 104 — Retificação causal, contenção e compensação de consequências de quests

**Decisão vinculante:** DEC-104/C, ADR-0099. **Versão:** Discovery v10.0 (2026-11-07). **Estado:** aprovado como arquitetura, NÃO IMPLEMENTADO em BG2:EE/EEex. **Dependências:** DEC-011/012/022/027/028/029/053/060–065/074/083/089/090/095–103.

## 1. Escopo

Objetivo: após correção autêntica de prova/mapeamento de quest, identificar e conter efeitos derivados indevidos sem apagar acontecimentos mecânicos confirmados nem o conhecimento já adquirido por NPCs. A obrigação é **não destrutiva, sensível a tempo, ramo, evidência e autoridade**. Não transformar o motor de retificação em escrita direta de flags, apagamento de save ou geração por LLM.

### Fronteiras explícitas

- `HostFact` pertence ao host/ledger de recibos. `QuestInterpretation` é uma assertiva curada e revisável. `WorldConsequence` é fato ou proposta derivada. `RecipientBelief` pertence à memória epistêmica do NPC. `Rectification` é uma nova asserção causal, **não uma operação DELETE**.
- `provenance/source_revision` e `causal_parents` podem ser consultados apenas com ACL. Os nós públicos recebem IDs opacos; nomes de flags, witness IDs e arquivos de save não são serializados para LLM.
- A DEC-095 rege compensações; DEC-100–102 autenticam a mudança da interpretação e DEC-103 fornece o ledger de admissão. DEC-096/097 continuam fontes do cálculo de impactos e DEC-098/099 de materialização/ownership.

## 2. Contrato de retificação e grafo causal

| Registro lógico | Campos candidatos | Responsabilidade |
|---|---|---|
| `RectificationProof` | `proof_id`, `supersedes_revision`, `new_revision`, `reason`, `evidence_refs`, `committed_at_dr`, `host_epoch`, `checkpoint_epoch`, `campaign/branch/lineage`, `signer_scope` | Registry curado; proof `COMMITTED` separado da request |
| `CausalNode` | `node_id`, `type`, `status`, `parents[]`, `edge_kinds[]`, `origin`, `classification`, `scope`, `time_dr`, `rule_revision` | Ledger append-only DEC-103 com links tipados |
| `LineageBoundary` | `campaign`, `branch`, `save_lineage`, `epoch`, `pinned_kpack`, `build_hash`, `modpack_hash` | Bloquear contaminação entre ramos e épocas |
| `ContainmentPlan` | `case_key`, `affected_nodes`, `revision`, `hold_candidates`, `uncertain_actions`, `review_queue`, `proposed_corrections`, `approval_refs` | **Apenas proposta**, nunca execução direta |
| `HostConfirmedEffect` | `receipt_ref`, `engine_instance`, `ownership_ref`, `field_scope`, `side_effects`, `irreversible` | Não pode ser revertido sem saga tipada e receipt novo |
| `DeliveryProof` | `recipient`, `claim_ref`, `channel`, `arrived_at_dr`, `scope`, `provenance` | Comprova exposição, não aceitação da nova correção |
| `CorrectionRevision` | `prior_claim_ref`, `new_claim_ref`, `reason`, `evidence_refs`, `created_at_dr`, `audience_policy` | Convive com histórico anterior; não apaga prova original |

Os stores de prova, autorização, status de gateway e ledger são **autoridades independentes**, acessadas via servidores/serviços locais validados. O cliente envia somente referências e finalidade. A fixture didática pode reunir tudo num arquivo, mas **não autoriza** usar valores enviados pelo cliente como fonte de verdade.

### Grafo e múltiplas causas

`QuestMilestoneAdmission -> ConsequenceProposal -> [HostReceipt | NewsTransmission -> Delivery -> RecipientKnowledge | DerivedView]` representa apenas um caso; na prática o grafo pode ter muitos pais. Uma aresta `DERIVED_FROM` não significa `SOLE_CAUSE`. Em efeito sustentado também por outro evento independente, a retificação elimina **somente** a contribuição contestada quando regras determinísticas comprovarem a decomposição. Grafo cíclico, incompleto, cruzado entre branches ou com proveniência não autenticada: `QUARANTINED`.

## 3. Classificação do estado e estratégia

| Estado verificado do descendente | Resultado candidato | Limite de autoridade |
|---|---|---|
| `PROPOSED`, `QUEUED`, `AUTHORIZED` (não despachado) | `HOLD_FUTURE_DISPATCH` | Travar novos despachos via CAS/fencing; reserva só liberada se inequivocamente livre |
| `DISPATCHED`, `UNCERTAIN`, `ACK_UNKNOWN` | `RECONCILE_HOST_BEFORE_ANY_CHANGE` | Não retry, não liberar, não compensar até receipt ou diagnóstico confiável |
| `HOST_CONFIRMED`, `APPLIED` | `PROPOSE_AUTHORIZED_SAGA_COMPENSATION_REVIEW` | Fato anterior imutável; compensação é novo efeito DEC-095, não rollback |
| `DELIVERED`, `KNOWLEDGE_ACQUIRED` | `PROPOSE_CAUSAL_CORRECTION_DELIVERY` | Memória não apagada; correção só depois de canal, entrega e ACL |
| `DERIVED_VIEW`, `PROJECTED` | `PROPOSE_VERSIONED_CAS_REBASE` | Rebase apenas da visão, sem reescrever fontes ou receipts |
| `REJECTED`, `EXPIRED`, `REVOKED` | `PRESERVE_TERMINAL_HISTORY` | Manter auditoria, sem ressuscitar emissão antiga |

Um nó pode permanecer confirmado no host e, simultaneamente, ter sua **justificativa narrativa contestada**. Essa discordância é representada como retificação versionada; não existe obrigação de apagar a consequência materializada. Alta gravidade requer gate HIGH e autorização adicional do titular afetado.

## 4. Pipeline determinístico e transações

```text
request(case_ref, scope, purpose):
    assert request authenticated; require signed purpose/audience policy
    proof = TrustedRectificationRegistry.get(case_ref)
    require proof.state == COMMITTED and proof.source in CURATED_DEC100_103
    require same campaign/branch/lineage/build/modpack/checkpoint/epoch
    graph = TrustedCausalLedger.get_descendant_dag(proof.origin)
    require complete/provenance-valid/acyclic/bounded graph
    require CAS(version) and exactly one active containment case per root/revision
    for node in topological_order(graph):
        classify node by confirmed stage and independent supporting causes
        if undispatched: propose hold by revision/fencing
        elif dispatched/uncertain: quarantine and reconcile host/channel receipt
        elif confirmed: propose saga-compensation review (never undo)
        elif delivered: propose scoped correction message (never unlearn)
        elif derived: propose CAS revision (never rewrite source)
    atomically commit containment/outbox when authorized and implementation tested
    workers for host, communication and projections require separate ACL/gates
```

**Ordem segura:** conter novas emissões antes de iniciar eventual compensação, se a contenção puder ser implementada com transação e verificação. Até lá, o próprio **plano** não altera ledger nem host. A implementação real exige persistência idempotente de `case_key` e `child_action_key`, pin de policy/revision, fenced lease e recuperação pós-crash. Leases expirados **não** liberam efeitos `UNCERTAIN`.

### Keying e idempotência

```text
rectification_case_key = H(campaign_id, branch_id, lineage_id,
                          root_admission_key, committed_rectification_revision,
                          source_revision)
child_action_key = H(rectification_case_key, causal_node_id, action_type,
                     validated_policy_revision)
```

Não usar ID de mensagem, id de observação, timestamp real ou session id como identidade de ocorrência. Repetições na mesma linhagem devem produzir `DUPLICATE_SUPPRESSED`; correções sucessivas devem gerar revisões distintas. Save restore/fork demanda revisão de escopo antes de reaproveitar uma chave. `FROZEN/PARTIAL/REALTIME` não autoriza avançar o relógio da campanha a partir do tempo de CPU.

## 5. Retificação informacional

Uma mensagem que foi recebida permanece no histórico do destinatário. Nova notícia pode informar que a alegação anterior foi corrigida, mas não prova automaticamente aceitação ou descrença; isso depende da capacidade perceptiva e histórico do NPC (DEC-064/065/089). O módulo de comunicação DEC-029/090 usa canais/rotas/tempo DR com entrega e ACL. Não comunicar identidade de fonte protegida como “prova” pública, nem revelar origem privada em contagem de métricas. DEC-105 detalhará políticas de alcance e atualização de crenças.

## 6. Exemplo fictício e resultados esperados

Uma quest sintética `SYN-QUEST-A` teve marco `SYN-MILESTONE-1` admitido, produzindo: uma mudança pendente, uma alteração já confirmada, um boato entregue e uma visão derivada. Uma revisão semântica committed informa que o marco estava mal interpretado. A avaliação retorna quatro **propostas**, sem tocar host ou NPC. Reentrada na área ou novo request com mesmo `case_key` não cria nova ação. Novo documento probatório que não é committed mantém caso `QUARANTINED`.

## 7. Evidências, testes e limites de POC

- `examples/chronology/rectification_reference.py`: planejador de **propostas** em Python puro, exclusivamente sintético.
- `examples/chronology/rectification_v1.synthetic.json`: fixture sem nomes de quests, scripts ou canon oficial.
- `examples/chronology/rectification_v1.candidate.schema.json`: contrato candidato de fixture; não corresponde a uma API do EEex.
- `examples/chronology/test_rectification_reference.py`: testes unitários negativos e positivos sem acesso ao jogo.
- **Integração:** todos os 140 casos T104-* abaixo são **CANDIDATOS NÃO EXECUTADOS** no BG2:EE/EEex/host+2 clientes.

### Gates de implantação futura

1. **G-104-01 — Proveniência:** comprovar prova committed curada e validação de ACL por serviço, não request.
2. **G-104-02 — DAG:** demonstrar detecção de multi-parent, ciclo, falta de pais, cross-branch e escopo privado.
3. **G-104-03 — Contenção:** demonstrar CAS/fencing e bloqueio de futuro despacho antes de gerar novos efeitos.
4. **G-104-04 — Host:** demonstrar reconciliador para `DISPATCHED/UNCERTAIN` e respeito a receipts anteriores.
5. **G-104-05 — Saga:** demonstrar compensação não destrutiva autorizada e seus próprios receipts.
6. **G-104-06 — Conhecimento:** demonstrar nova comunicação com entrega sem apagar crenças.
7. **G-104-07 — Replay:** host+2 clientes, save/load/restore/fork e crash recovery sem duplicação.
8. **G-104-08 — Segurança:** nenhuma mutação de scripts, spoilering, leak de identidade, ACL escalation ou LLM comandando ações.

### Matriz de 140 testes candidatos — TODOS NÃO EXECUTADOS no jogo

| ID | Família | Cenário candidato | Resultado esperado |
|---|---|---|---|
| T104-001 | Prova | prova ausente | bloquear quando prova insuficiente; considerar apenas proof curada committed |
| T104-002 | Prova | prova proposta | bloquear quando prova insuficiente; considerar apenas proof curada committed |
| T104-003 | Prova | prova autenticada | bloquear quando prova insuficiente; considerar apenas proof curada committed |
| T104-004 | Prova | origem de LLM | bloquear quando prova insuficiente; considerar apenas proof curada committed |
| T104-005 | Prova | prova revogada | bloquear quando prova insuficiente; considerar apenas proof curada committed |
| T104-006 | Prova | nova evidência contraditória | bloquear quando prova insuficiente; considerar apenas proof curada committed |
| T104-007 | Prova | revisão semântica committed | bloquear quando prova insuficiente; considerar apenas proof curada committed |
| T104-008 | Revisão | marco antigo | preservar origem e revisão, sem sobrescrita retroativa |
| T104-009 | Revisão | revisão duplicada | preservar origem e revisão, sem sobrescrita retroativa |
| T104-010 | Revisão | versão nova | preservar origem e revisão, sem sobrescrita retroativa |
| T104-011 | Revisão | correção concorrente | preservar origem e revisão, sem sobrescrita retroativa |
| T104-012 | Revisão | rebase proposto | preservar origem e revisão, sem sobrescrita retroativa |
| T104-013 | Revisão | rebase confirmado | preservar origem e revisão, sem sobrescrita retroativa |
| T104-014 | Revisão | histórico de versões | preservar origem e revisão, sem sobrescrita retroativa |
| T104-015 | DAG | nó sem pai | quarentena quando necessário; distinguir contribuição independente |
| T104-016 | DAG | ciclo causal | quarentena quando necessário; distinguir contribuição independente |
| T104-017 | DAG | pais múltiplos | quarentena quando necessário; distinguir contribuição independente |
| T104-018 | DAG | efeito sem causalidade exclusiva | quarentena quando necessário; distinguir contribuição independente |
| T104-019 | DAG | família de evidências dependentes | quarentena quando necessário; distinguir contribuição independente |
| T104-020 | DAG | grafo parcial | quarentena quando necessário; distinguir contribuição independente |
| T104-021 | DAG | ramo isolado | quarentena quando necessário; distinguir contribuição independente |
| T104-022 | Pendente | proposta ainda em fila | conter apenas futuros despachos idempotentemente |
| T104-023 | Pendente | autorizado não despachado | conter apenas futuros despachos idempotentemente |
| T104-024 | Pendente | reserva lógica | conter apenas futuros despachos idempotentemente |
| T104-025 | Pendente | cancelamento tardio | conter apenas futuros despachos idempotentemente |
| T104-026 | Pendente | outbox duplicado | conter apenas futuros despachos idempotentemente |
| T104-027 | Pendente | hold concorrente | conter apenas futuros despachos idempotentemente |
| T104-028 | Pendente | evento dependente suspenso | conter apenas futuros despachos idempotentemente |
| T104-029 | Host | efeito confirmado | manter receipts; reconciliar incertos; nenhuma escrita direta |
| T104-030 | Host | comando despachado | manter receipts; reconciliar incertos; nenhuma escrita direta |
| T104-031 | Host | ACK perdido | manter receipts; reconciliar incertos; nenhuma escrita direta |
| T104-032 | Host | receipt duplicado | manter receipts; reconciliar incertos; nenhuma escrita direta |
| T104-033 | Host | host epoch alterado | manter receipts; reconciliar incertos; nenhuma escrita direta |
| T104-034 | Host | capability revogada | manter receipts; reconciliar incertos; nenhuma escrita direta |
| T104-035 | Host | efeito irreversível | manter receipts; reconciliar incertos; nenhuma escrita direta |
| T104-036 | Sagas | pagamento confirmado | propor compensações específicas somente com autorização |
| T104-037 | Sagas | recompensa recebida | propor compensações específicas somente com autorização |
| T104-038 | Sagas | deslocamento iniciado | propor compensações específicas somente com autorização |
| T104-039 | Sagas | morte confirmada | propor compensações específicas somente com autorização |
| T104-040 | Sagas | reputação alterada | propor compensações específicas somente com autorização |
| T104-041 | Sagas | compensação negada | propor compensações específicas somente com autorização |
| T104-042 | Sagas | compensação parcial | propor compensações específicas somente com autorização |
| T104-043 | Boato | notícia só enviada | não apagar memórias nem concluir correção sem entrega |
| T104-044 | Boato | notícia entregue | não apagar memórias nem concluir correção sem entrega |
| T104-045 | Boato | canal interceptado | não apagar memórias nem concluir correção sem entrega |
| T104-046 | Boato | NPC esquece? não | não apagar memórias nem concluir correção sem entrega |
| T104-047 | Boato | fonte protegida | não apagar memórias nem concluir correção sem entrega |
| T104-048 | Boato | correção contraditória | não apagar memórias nem concluir correção sem entrega |
| T104-049 | Boato | recebimento posterior | não apagar memórias nem concluir correção sem entrega |
| T104-050 | Balanço epistêmico | verdade contestada | crença diferente de fato; revisão gradual |
| T104-051 | Balanço epistêmico | crença equivocada | crença diferente de fato; revisão gradual |
| T104-052 | Balanço epistêmico | informante confiável | crença diferente de fato; revisão gradual |
| T104-053 | Balanço epistêmico | duas fontes dependentes | crença diferente de fato; revisão gradual |
| T104-054 | Balanço epistêmico | boato falso | crença diferente de fato; revisão gradual |
| T104-055 | Balanço epistêmico | corrigenda parcial | crença diferente de fato; revisão gradual |
| T104-056 | Balanço epistêmico | opinião persistente | crença diferente de fato; revisão gradual |
| T104-057 | Visões | indicador derivado | revisar apenas visão derivada com CAS e preservar host |
| T104-058 | Visões | snapshot antigo | revisar apenas visão derivada com CAS e preservar host |
| T104-059 | Visões | materialização concluída | revisar apenas visão derivada com CAS e preservar host |
| T104-060 | Visões | rollback indevido | revisar apenas visão derivada com CAS e preservar host |
| T104-061 | Visões | rebase CAS perdido | revisar apenas visão derivada com CAS e preservar host |
| T104-062 | Visões | cálculo de diferença | revisar apenas visão derivada com CAS e preservar host |
| T104-063 | Visões | perfil temporal vencido | revisar apenas visão derivada com CAS e preservar host |
| T104-064 | Chronology | ano DR antigo | não inventar datas; alcance geográfico e temporal válido |
| T104-065 | Chronology | mês desconhecido | não inventar datas; alcance geográfico e temporal válido |
| T104-066 | Chronology | modo FROZEN | não inventar datas; alcance geográfico e temporal válido |
| T104-067 | Chronology | modo PARTIAL | não inventar datas; alcance geográfico e temporal válido |
| T104-068 | Chronology | calendário realtime | não inventar datas; alcance geográfico e temporal válido |
| T104-069 | Chronology | região distante | não inventar datas; alcance geográfico e temporal válido |
| T104-070 | Chronology | efeito tardio | não inventar datas; alcance geográfico e temporal válido |
| T104-071 | Multiplayer | host e cliente | agência de PCs e host authority preservadas |
| T104-072 | Multiplayer | dois clientes | agência de PCs e host authority preservadas |
| T104-073 | Multiplayer | PC ausente | agência de PCs e host authority preservadas |
| T104-074 | Multiplayer | consentimento retirado | agência de PCs e host authority preservadas |
| T104-075 | Multiplayer | novo líder | agência de PCs e host authority preservadas |
| T104-076 | Multiplayer | reconexão | agência de PCs e host authority preservadas |
| T104-077 | Multiplayer | conflito de autorização | agência de PCs e host authority preservadas |
| T104-078 | Build | BG2EE alterado | fail-closed e recertificação por build |
| T104-079 | Build | EEex alterado | fail-closed e recertificação por build |
| T104-080 | Build | modpack alterado | fail-closed e recertificação por build |
| T104-081 | Build | script curado revogado | fail-closed e recertificação por build |
| T104-082 | Build | quest variant errada | fail-closed e recertificação por build |
| T104-083 | Build | probe parcial | fail-closed e recertificação por build |
| T104-084 | Build | prova stale | fail-closed e recertificação por build |
| T104-085 | Save | save/load | isolar branches e reconciliar antes de despacho |
| T104-086 | Save | restore antigo | isolar branches e reconciliar antes de despacho |
| T104-087 | Save | fork legítimo | isolar branches e reconciliar antes de despacho |
| T104-088 | Save | snapshot parcial | isolar branches e reconciliar antes de despacho |
| T104-089 | Save | epoch desatualizado | isolar branches e reconciliar antes de despacho |
| T104-090 | Save | lineage divergente | isolar branches e reconciliar antes de despacho |
| T104-091 | Save | duplicação de outbox | isolar branches e reconciliar antes de despacho |
| T104-092 | Segredos | spoiler de quest | ACL por audiência e minimização sem declassificação automática |
| T104-093 | Segredos | romance secreto | ACL por audiência e minimização sem declassificação automática |
| T104-094 | Segredos | testemunha protegida | ACL por audiência e minimização sem declassificação automática |
| T104-095 | Segredos | ID público de rumor | ACL por audiência e minimização sem declassificação automática |
| T104-096 | Segredos | logs públicos | ACL por audiência e minimização sem declassificação automática |
| T104-097 | Segredos | prompt de LLM | ACL por audiência e minimização sem declassificação automática |
| T104-098 | Segredos | métrica de privacidade | ACL por audiência e minimização sem declassificação automática |
| T104-099 | Recursos | guarda reservado | não liberar recurso incerto ou duplicar consumo |
| T104-100 | Recursos | carroça reservada | não liberar recurso incerto ou duplicar consumo |
| T104-101 | Recursos | lease expirado | não liberar recurso incerto ou duplicar consumo |
| T104-102 | Recursos | recurso exclusivo | não liberar recurso incerto ou duplicar consumo |
| T104-103 | Recursos | starvation | não liberar recurso incerto ou duplicar consumo |
| T104-104 | Recursos | deadlock | não liberar recurso incerto ou duplicar consumo |
| T104-105 | Recursos | dupla compensação | não liberar recurso incerto ou duplicar consumo |
| T104-106 | Atribuição | PC não envolvido | não atribuir autoria ou decisões por inferência |
| T104-107 | Atribuição | NPC delegado | não atribuir autoria ou decisões por inferência |
| T104-108 | Atribuição | fato sem testemunha | não atribuir autoria ou decisões por inferência |
| T104-109 | Atribuição | autoria disputada | não atribuir autoria ou decisões por inferência |
| T104-110 | Atribuição | confissão não autorizada | não atribuir autoria ou decisões por inferência |
| T104-111 | Atribuição | prova falsificada | não atribuir autoria ou decisões por inferência |
| T104-112 | Atribuição | facção rival | não atribuir autoria ou decisões por inferência |
| T104-113 | Política | risco LOW | permitir apenas proposta válida dentro de gates |
| T104-114 | Política | risco MEDIUM | permitir apenas proposta válida dentro de gates |
| T104-115 | Política | risco HIGH | permitir apenas proposta válida dentro de gates |
| T104-116 | Política | gate revogado | permitir apenas proposta válida dentro de gates |
| T104-117 | Política | policy expirou | permitir apenas proposta válida dentro de gates |
| T104-118 | Política | ownership terceiro | permitir apenas proposta válida dentro de gates |
| T104-119 | Política | sem consentimento | permitir apenas proposta válida dentro de gates |
| T104-120 | Ledger | cas conflict | atomicidade, dedup e historicidade verificável |
| T104-121 | Ledger | operação repetida | atomicidade, dedup e historicidade verificável |
| T104-122 | Ledger | outbox crash | atomicidade, dedup e historicidade verificável |
| T104-123 | Ledger | ordem diferente | atomicidade, dedup e historicidade verificável |
| T104-124 | Ledger | fencing desatualizado | atomicidade, dedup e historicidade verificável |
| T104-125 | Ledger | escrita parcial | atomicidade, dedup e historicidade verificável |
| T104-126 | Ledger | audit trail | atomicidade, dedup e historicidade verificável |
| T104-127 | Limites | mil descendentes | limite de fan-out e quarentena sem silenciar risco |
| T104-128 | Limites | profundidade excessiva | limite de fan-out e quarentena sem silenciar risco |
| T104-129 | Limites | DAG cíclico | limite de fan-out e quarentena sem silenciar risco |
| T104-130 | Limites | leitura incompleta | limite de fan-out e quarentena sem silenciar risco |
| T104-131 | Limites | nó malformado | limite de fan-out e quarentena sem silenciar risco |
| T104-132 | Limites | dependência invisível | limite de fan-out e quarentena sem silenciar risco |
| T104-133 | Limites | budget esgotado | limite de fan-out e quarentena sem silenciar risco |
| T104-134 | Recovery | restart de host | sem perda de fatos, sem retry cego e com protocolo de recuperação |
| T104-135 | Recovery | saga compensada | sem perda de fatos, sem retry cego e com protocolo de recuperação |
| T104-136 | Recovery | correção reaberta | sem perda de fatos, sem retry cego e com protocolo de recuperação |
| T104-137 | Recovery | novas provas | sem perda de fatos, sem retry cego e com protocolo de recuperação |
| T104-138 | Recovery | mudança de horário | sem perda de fatos, sem retry cego e com protocolo de recuperação |
| T104-139 | Recovery | compensação incerta | sem perda de fatos, sem retry cego e com protocolo de recuperação |
| T104-140 | Recovery | finalização segura | sem perda de fatos, sem retry cego e com protocolo de recuperação |

## 8. Proximidade com decisões anteriores e próxima etapa

- **DEC-095:** recuperação de operações parciais por Sagas; não confundir compensação com cancelamento atômico do motor.
- **DEC-096/097:** retirar contribuição contestada somente quando origem e domínio permitem; respeitar caps e tempo DR.
- **DEC-098/099:** preservar instâncias existentes, snapshots host-confirmed e ownership de outros mods.
- **DEC-100/101/102/103:** observação, mapeamento, reconciliação e admissão são fontes de prova, jamais autorização de escritura livre.
- **DEC-028/029/064/065/083/089/090:** conhecer uma notícia não garante acreditar na correção; sigilo e ACL continuam aplicáveis.
- **DEC-053/055/057–059:** epochs, checkpoints e privacidade de logs/prompts antes e depois de recuperação.

**Próxima DEC-105 (aberta):** política de publicação/entrega de retificações e atualizações graduais de crença em NPCs, evitando broadcasts universais e apagamento instantâneo de memória.

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para retificação committed gera candidatos a errata, sem transmissão ou unlearning, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para retificação de marco não apaga descendentes host-confirmed, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de obrigações e monitoramento não coercitivo

Retificação de evento não anula dinheiro/item entregue; compensação precisa de novo ato autorizado. Fonte: ADR-0103/doc.108; claims ≠ comprovantes, prazos DR ≠ culpa, status `UNCERTAIN` bloqueia nova ação, sem mutações do host. POCs BG2:EE/EEex e T108-001..160 **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Retificação de causa não invalida automaticamente pagamento confirmado. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
