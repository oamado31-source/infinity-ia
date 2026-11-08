# ADR-0099 — DEC-104/C: retificação causal não destrutiva de repercussões de quests

- **Data:** 2026-11-07.
- **Decisão:** DEC-104, opção **C**, escolhida e aprovada pelo idealizador.
- **Estado:** **APROVADA COMO ARQUITETURA**, sem integração comprovada ao BG2:EE/EEex/bridge/host+2 clientes.
- **Discovery:** v10.0. Todos os **98 ADRs anteriores (ADR-0001..0098) preservados byte a byte**; DEC-060..DEC-103 permanecem vinculantes.
- **Contrato normativo:** `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`.
- **Próxima discussão:** DEC-105 — distribuição de correções e atualização gradual de crenças após retificações.

## Contexto

DEC-100/101/102 separam observação read-only, interpretação curada e reconciliação sem mutação automática. DEC-103 admite um marco reconciliado e permite propostas de repercussão, notícias e efeitos mecânicos separados. Uma prova ou interpretação pode ser **retificada posteriormente**, inclusive após restauração de save, recertificação de um mapper, erro editorial, revisão de ramo ou evidência nova. Seus descendentes podem ter estados distintos: ainda propostos, despachados, host-confirmados, comunicados ou conhecidos por NPCs. Reverter todos é errado; continuar a propagar pressupostos revogados também é errado.

## Alternativas e decisão

- **A — rollback em cascata de todos os resultados:** **REJEITADA**; apaga fatos testemunhados, contradiz receipts do host, ignora irreversibilidade e memória de NPCs.
- **B — reescrita livre por LLM:** **REJEITADA**; autoriza onisciência, invenção de compensações, apagamento de conhecimento e overwrite de quests/mods.
- **C — grafo causal, contenção de pendentes, revisões versionadas e compensações verificadas:** **APROVADA**.

## Invariantes normativos

1. **Retificação não é negação automática do fato mecânico.** Registrar separadamente `OriginalClaim`, `CommittedRectificationProof`, `ConsequenceNode`, `HostEffectReceipt`, `DeliveryReceipt`, `RecipientKnowledge` e `CorrectionProposal`. Uma correção de mapeamento pode contestar a interpretação antiga sem afirmar que host não executou um efeito.
2. **Gatilho autêntico, não texto livre.** `CommittedRectificationProof` deriva da cadeia DEC-100/101/102/103 e de fontes curadas; identifica causa original, revisão corrigida, natureza da divergência (`SEMANTIC_CORRECTION`, `RESTORE_BRANCH_CHANGE`, `SOURCE_REVOKED`, `NEW_EVIDENCE`, `MAPPING_REVALIDATED`), tempo DR, build/modpack, campaign/branch/lineage, epochs e proveniência. Um pedido de LLM/usuário não constitui proof/receipt/autorização. Revisões apenas propostas não abrem cascata.
3. **Grafo causal por referências verificadas.** As dependências entre marcos admitidos, propostas, mensagens, entregas, crenças, projeções e efeitos são índices de um ledger append-only. Nós exigem IDs estáveis, tipo, causal parents, origem, escopo, classificação, revisão e status. Distinguir `DERIVES_FROM`, `ACTIVATED_BY`, `DELIVERED_FROM`, `APPLIED_FROM` e `CORRECTS`. Proibir ciclos, pais inexistentes e grafos cruzando ramos sem autorização; a cobertura incompleta leva a `QUARANTINED`, nunca a “não houve outras consequências”.
4. **Contenção precoce (future-only).** Após prova committed e verificação CAS/fencing, bloquear **novas** emissões e despachos descendentes que dependam da alegação contestada; não cancelar retroativamente ações já despachadas, não liberar reserva incerta, não emitir notícia/efeito em nome de PC. O planejador apenas propõe `HOLD_FUTURE_DISPATCH`; worker autorizado implementará contenção atômica em uma SPEC posterior.
5. **Classificação por estado causal real.** `PROPOSED/QUEUED/AUTHORIZED` → candidato à suspensão do próximo despacho. `DISPATCHED/UNCERTAIN` → reconciliação obrigatória com host ou ledger de canal antes de qualquer tentativa adicional. `HOST_CONFIRMED/APPLIED` → fato imutável, possível análise de compensação DEC-095 como **novo acontecimento**, nunca rollback do receipt. `DELIVERED/KNOWLEDGE_ACQUIRED` → memória preservada, possível comunicação retificadora posterior. `DERIVED_VIEW` → proposta de nova revisão CAS, sem reescrever fatos-fontes.
6. **Nem toda consequência depende exclusivamente do marco retificado.** Nós podem ter múltiplas causas (`parents[]`). Se outra causa independente e comprovada ainda sustentar um efeito, não o invalidar globalmente. Reavaliação de suporte é por domínio e regra de proveniência; casos sem evidência suficiente permanecem `MIXED/UNCERTAIN` para revisão. Contenção inicial não implica condenar todos os descendentes como falsos.
7. **Revisões são aditivas.** `RectificationCase` aponta para original e versões; gera `SupersedingRevision` com motivo e evidência, sem `DELETE` de fatos, snapshots, conversas, opiniões ou registros host. `CORRECTED` não equivale a `ERASED` e pode coexistir com história de confiança abalada.
8. **Memória humana e NPC falível.** Conhecer boato antigo é fato distinto de crer nele. Uma retificação não atualiza automaticamente todos os NPCs que ouviram a versão antiga. Canais/tempo/alcance/ACL e entregas DEC-029/074/090 precisam ser comprovados; DEC-064/065/089 autorizam crenças contraditórias. Detalhes sobre elegibilidade de correções por destinatário ficam para DEC-105.
9. **Compensações não são reversões.** Pagamentos, mortes, entregas, deslocamentos, reputação e efeitos históricos confirmados somente podem gerar ações compensatórias **específicas**, proporcionais, com ownership DEC-099, recursos DEC-093/094, risco DEC-027, consentimento DEC-041/046 e receipts DEC-011/012; nenhuma compensação é garantida, nem NPC “ressuscitado” por narrativa.
10. **Direito mecânico e autoria.** Host é soberano para mecânica. O Infinity AI só pode solicitar ações tipadas na allowlist com build-capability, preconditions, idempotency e autorização; efeitos irreversíveis HIGH ficam bloqueados sem autorização especial. Não sobrescrever flags de quests, scripts originais ou mods nem atribuir decisões a PCs ausentes.
11. **Ramos, saves e tempo.** Não confundir correção no ramo atual com rollback para outro save. `lineage_id`, epochs, snapshot, KnowledgePack pinned DEC-060..063 e relógio DEC-022 delimitam dependências. Se o branch divergiu, criar registro de revisão para o branch correto; não transportar rumores ou receipts entre campanhas.
12. **Outbox, revisão e concorrência.** Ledger append-only, `rectification_key` estável por causa, branch, source revision e proof revision; CAS/fencing e outbox transacional impedem dupla contenção, dupla compensação e duplicação de erratas em reentry/save/load/multiplayer. `DISPATCHED/UNCERTAIN` preserva quarentena até confirmação; nenhum retry cego.
13. **Segurança e anti-spoilers.** Mapeamentos internos, nomes de flags, identidade de testemunhas e causas privadas não são incluídos em relatório público, logs, IDs públicos, métricas ou prompts. As ACLs de prova, planejamento, compensação e comunicação são distintas; o pedido não pode se autoconceder privilégios. LLM local pode redigir uma versão permitida de errata, mas não decidir verdade, alcance ou apagar fatos.
14. **Desacoplamento e segurança offline.** A DEC-104 pode apenas produzir `RectificationPlanProposal` no planejador de referência, sem modificar host, snapshots, ledger real, rumor, crença ou inventário. Catálogos e workflows precisarão de SPECs, certificação por build e testes host+dois clientes.
15. **Limite de evidências.** O arquivo Python, JSON Schema, fixture e testes são sintéticos. Os cenários `T104-001..140` documentados são candidatos **NÃO EXECUTADOS** no jogo; testes unitários não demonstram funcionalidade real.

## Contratos conceituais

| Entidade | Campos mínimos | Garantia |
|---|---|---|
| `CommittedRectificationProof` | `rectification_id`, `original_admission_key`, `new_revision`, `reason`, `source_proof`, `branch/lineage`, `epoch`, `status=COMMITTED` | Não pode ser forjada pela requisição |
| `CausalDependencyNode` | `node_id`, `parent_ids`, `edge_types`, `kind`, `stage`, `scope`, `provenance`, `risk`, `audience` | DAG sem cruzar branch/autoridade |
| `RectificationCase` | `case_key`, `source_revision`, `target_branch`, `ledger_revision`, `review_status`, `affected_nodes` | Idempotente e versionado |
| `ContainmentDirective` | `target_ref`, `scope`, `type=HOLD_FUTURE_DISPATCH`, `status`, `fencing_token` | Só bloqueia futuros despachos elegíveis |
| `CompensationReview` | `receipt_ref`, `available_compensation`, `approval_refs`, `host_state`, `risk` | Proposta; efeito apenas com novo receipt |
| `CorrectionNoticeProposal` | `claim_ref`, `correction_ref`, `channel`, `audience`, `classification`, `delivery_status` | Não presume recebimento ou crença |

## Exemplo inteiramente fictício

`SYN-Q1` foi admitido como marco concluído e produziu quatro descendentes: (i) proposta de reajuste ainda em fila, (ii) modificação local confirmada pelo host, (iii) rumor efetivamente entregue a uma testemunha e (iv) projeção derivada. Posteriormente, o mapper curado recebeu uma revisão committed que altera a interpretação do marco. O sistema propõe **suspender o reajuste ainda não despachado**, **revisar se existe compensação autorizável para o efeito confirmado**, **produzir uma correção a ser entregue por canal real** e **revisar o indicador derivado por CAS**. Nenhum desses atos equivale a execução: `host_calls=0`, `npc_memories_changed=0` e `rumors_sent=0` na referência sintética.

## Impactos e riscos

- **Benefícios:** coerência histórica sem edição retroativa arbitrária; preservação de responsabilidade e evidências; contenção de novos efeitos incorretos; memória NPC realista.
- **Custos:** grafo causal e ledgers de proofs, deliveries, revisions, receipts, fan-out bounded, observabilidade e políticas de compensação; curadoria para efeitos com múltiplas causas.
- **Riscos residuais:** provas atrasadas, confiança perdida em fontes, loops de correção, grafo incompleto, node leak, races do outbox, save divergente e compatibilidade por build; resposta default-deny e quarentena.
- **Sem implementação de motor comprovada:** nenhuma API de BG2:EE/EEex, release de reservas, alterações de NPCs, recompensas, quest flags ou multiplayer foi testada.

## Critérios de aceite arquitetural

A DEC-104 somente poderá ser declarada implementada após testes reais: (1) prova curada/committed, (2) travamento antes do próximo despacho, (3) recibos do host e reconciliação, (4) saga autorizada, (5) preservação da memória e divulgação seletiva, (6) save/load/restore e fork, (7) dedup no host+2 clientes, (8) zero spoilers, (9) proteção de ownership de quests/mods, e (10) tratamento de múltiplas causas sem apagamento indevido.

## Próxima decisão em aberto

**DEC-105 — Distribuição de erratas e evolução das crenças após retificações**: A correção global imediata; B LLM reescreve memórias; **C comunicação contextual, com proveniência, canais, tempo de mundo, compreensão falível, ACL e auditoria da recepção**, sem broadcast onisciente.
