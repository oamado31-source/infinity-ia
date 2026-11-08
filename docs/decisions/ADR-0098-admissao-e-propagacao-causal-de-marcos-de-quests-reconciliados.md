# ADR-0098 — DEC-103/C: admissão e propagação causal de marcos de quests ao Living World

- **Data:** 2026-11-07.
- **Decisão:** DEC-103, alternativa **C**, expressamente aprovada pelo idealizador.
- **Estado:** **APROVADA COMO ARQUITETURA**, sem evidência de integração com BG2:EE/EEex/bridge/multiplayer.
- **Discovery:** v9.9; ADR-0001..ADR-0097 anteriores preservados integralmente e byte a byte. DEC-060..DEC-102 permanecem vinculantes.
- **Contrato normativo:** `docs/103-admissao-e-propagacao-causal-de-marcos-de-quests-reconciliados.md`.
- **Próxima decisão proposta:** DEC-104 — tratamento de retificações posteriores e efeitos derivados já propagados.

## Contexto e problema

As DEC-099, DEC-100, DEC-101 e DEC-102 distinguem proteção de ownership, observação técnica somente-leitura, interpretação semântica curada e reconciliação não destrutiva com o overlay. Entretanto, **um marco de quest observado ou reconciliado não equivale a uma repercussão já ocorrida no Living World**. O sistema precisa admitir marcos em um pipeline controlado para alimentar rumores, reputação, reações de facções, oportunidades e efeitos locais sem transformar informações privadas em notícias públicas, sem supor que um personagem tomou conhecimento do marco e sem repetir recompensas/spawns após reentrada no mapa, checkpoint ou save/load.

Um resultado `PROPOSE_DERIVED_VIEW_REBASE` da DEC-102 **é apenas proposta**: não habilita emissão de evento antes de aprovação e commit CAS da revisão derivada. `CONSISTENT` só é utilizável se acompanhado de prova semântica válida DEC-100/101, não meramente pela palavra `CONSISTENT`. Observação somente-leitura é prova de estado de uma quest, **não recibo de mutação** do host e **não evento de aquisição de conhecimento**.

## Alternativas

- **A — repercutir imediatamente cada marco de quest:** **REJEITADA** por risco de spoilers, alcance geográfico indiscriminado, instâncias duplicadas e descompasso entre host e campanha.
- **B — deixar LLM selecionar os desdobramentos:** **REJEITADA** por riscos de inventar fatos/atribuição, ignorar estados e consumir recursos sem autoridade.
- **C — admitir e propagar somente por regras determinísticas com proveniência, escopo, ACL, idempotência e confirmação do host:** **APROVADA**.

## Decisão normativa e invariantes

1. **Eventos têm tipos distintos, não intercambiáveis:** `HostQuestObservation` (DEC-100) → `CuratedMilestoneAssertion` (DEC-101) → `ReconciledMilestoneProof` (DEC-102) → `QuestMilestoneAdmission` (DEC-103) → `ConsequenceProposal` (DEC-096/097/074) → autorização e eventual `HostEffectReceipt` (DEC-011/012/098/099), e **separadamente** `NewsDelivery` e `RecipientKnowledge` (DEC-029/028/083/090). Nenhum estado anterior assume efeitos posteriores.
2. **Admissão exige prova de origem confiável e estado efetivamente reconciliado.** A prova deve vincular campanha, ramo, quest/variante, marco, session/host/checkpoint epochs, fingerprint BG2:EE/modpack, revisão curada do mapper, observação fresh/com cobertura válida, revisão overlay publicada, autorização vigente e checkpoint lineage compatível. `CONSISTENT` com prova ou **rebase já aplicado e confirmado por CAS** são elegíveis; `PROPOSE_DERIVED_VIEW_REBASE` pendente, `UNKNOWN`, `AMBIGUOUS`, `QUARANTINED`, `RESTORE_REVIEW_REQUIRED`, observação parcial ou revisão revogada **não** são elegíveis.
3. **Atributos de confiança não vêm da solicitação.** Serviços e políticas atestados separados fornecem `AdmissionPolicy`, `ReconciledProofRegistry`, `CuratedConsequenceRuleRegistry`, `ActorKnowledgeACL` e `HostReceiptLedger`; a requisição não pode conter/forjar concessões, receipts, confirmação de estágio, origem ou permissão. Exigir validation, sem execução dinâmica de código fornecido pelo evento.
4. **Respeito ao tempo histórico e ao ramo.** A admissão usa tempo de mundo DEC-022 (`FROZEN/PARTIAL/REALTIME`), não hora do sistema; clock DR e fase histórica devem ser compatíveis com o ruleset DEC-096 e com divergências locais DEC-009/025/026/060–063. Uma confirmação atual de quest não altera retroativamente cânone, não cria fatos em outros anos DR ou ramos e não reexecuta fatos anteriores após restore.
5. **Seleção determinística de regras de repercussão.** `QuestConsequenceRule` curada, pinada por build/quest/mapping/KPack e revisão, especifica marco, espaço, janelas, precondições, dependências de receipt, domínios, limites de efeitos DEC-097, risco DEC-027 e destinatários autorizáveis. Regras sem fonte validada ou sem condições suficientes produzem `BLOCKED/UNKNOWN` e **zero** ações.
6. **Fronteiras entre fato, informação e relato.** A ocorrência de uma quest pode justificar **proposta de consequência** sem que nenhum NPC tenha sido informado. Rumor precisa de testemunha, canal, transmissão, tempo, recebimento e ACL; `WORLD_OCCURRED ≠ NPC_KNOWS ≠ NPC_BELIEVES`. Mesmo `GLOBAL` na matriz não faz broadcast imediato.
7. **Permissões de segurança e de privacidade.** Flags brutas, IDs de scripts sensíveis, segredos de romance, identidades protegidas e revelações futuras não são serializados para contexto de LLM, dossiê ou rumor. ACL de evento é separada da ACL de audiência; a regra só pode reduzir exposição, nunca ampliar o que DEC-100/101/083 autorizam. A LLM local apenas redige variações dentro de fatos já divulgáveis; não escolhe veracidade, prioridade, recompensas ou destinatários.
8. **Proposta não é execução.** `QuestMilestoneAdmission` registra fato de **admissão lógica**, não spawn/alteração mecânica. Uma `ConsequenceProposal` exige análise de risco, ownership DEC-099, políticas DEC-091–095, capacidade por build e Action Gateway; o estado mecânico muda somente após receipt autêntico do host. `DISPATCHED/UNCERTAIN` fica em quarentena, sem retry cego ou reaplicação após load.
9. **Idempotência multi-session.** A chave de admissão inclui campanha, ramo, linhagem temporal, quest/variante, `semantic_milestone_id`, `occurrence_id` ou prova de transição, `ruleset_revision` e escopo. **Não** usar apenas o novo ID da observação ou session_id como identidade de ocorrência: leituras repetidas/saves na mesma linhagem não duplicam evento. Uma repetição legítima só pode ocorrer com novo `occurrence_id` certificado; caso contrário, `DUPLICATE_SUPPRESSED`.
10. **Lotes, replay e concorrência.** Ledger append-only + outbox transacional/commit CAS/fencing; no máximo uma emissão efetiva por dedup key. Divergências de epoch/branch suspendem emissões; dois clientes não emitem o mesmo evento simultaneamente. Um leitor não host apenas visualiza as versões de sua audiência.
11. **Efeitos indiretos exigem causalidade confirmada.** Reputação, preços, facções, encontros, incidentes, denúncias ou consequências tardias obedecem a DEC-074/096/097, precondições por ator/escopo/tempo, limites e, para efeitos mecânicos indiretos, receipt pai quando apropriado; não são aplicados por associação textual à quest.
12. **Materialização protegida.** Repercussões locais passam por DEC-098 (snapshots/deltas) e DEC-099 (ownership por instância/campo), sem recriar NPC original, reabrir quest resolvida, liberar recursos já consumidos ou repetir recompensa do motor. Mesmo uma quest concluída não confere permissão para escrever suas flags.
13. **Correções posteriores não apagam o passado.** Quando evidências ou mapeamento são corrigidos, o sistema mantém a prova, a versão e a cadeia de efeitos no ledger. Suspende novas ramificações questionáveis e gera caso de revisão; efeitos host-confirmed e conhecimento já recebido não podem ser silenciosamente removidos. Política detalhada de compensação/correção descendente será discutida em DEC-104; DEC-095 continua aplicável.
14. **Privacidade e LLM local-first.** Consultas ao modelo usam somente projeções por audiência/purpose, com minimização, rastreio de proveniência, confidencialidade e fail-closed; palavras na narrativa não constituem confirmação de transmissão/recebimento.
15. **Fronteira de prova experimental.** Código, JSON Schema, fixtures e testes em `examples/chronology/` são protótipos **SINTÉTICOS**. Nenhum script original, API EEex, host+2 clientes, bridge, multiplayer, economia, reputação, rumor real ou spawn foi executado. Os 136 testes `T103-*` do documento técnico são candidatos **NÃO EXECUTADOS**.

## Ciclo de vida formal

`OBSERVED_READ_ONLY → SEMANTICALLY_CURATED → RECONCILED → ADMISSION_ELIGIBLE → ADMITTED_APPEND_ONLY → CONSEQUENCE_PROPOSED → RISK_VALIDATED → AUTHORIZED → DISPATCHED → HOST_CONFIRMED` (apenas operações mecânicas). Ramificações: `BLOCKED_ACL`, `BLOCKED_MAPPING`, `BLOCKED_RULE`, `UNKNOWN`, `QUARANTINED`, `DUPLICATE_SUPPRESSED`, `EXPIRED`, `REJECTED`, `UNCERTAIN`. O pipeline de comunicação é **outro fluxo**: `KNOWABLE_CANDIDATE → CHANNEL_APPROVED → SENT → DELIVERED → KNOWLEDGE_ACQUIRED` (recebimento comprovado); envio não implica entrega.

Transição `ADMITTED_APPEND_ONLY` **não** garante existência de proposta ou efeito executado. Um marco pode ser privado, não ter ruleset correspondente ou permanecer sem repercussão. A decisão de criar notícia não resulta de mera existência de um milestone.

## Consequências

- **Benefícios:** repercussões de quests oficiais contextualizadas e contínuas, sem onisciência, spoilers, duplicidade após save/load nem perda de ownership; integração controlada às matrizes DEC-096–099.
- **Custos:** curadoria adicional por quest/variante/build; store de proofs, ACL e lineage; ledger/outbox e reconciliação com host; testes negativos de sigilo/replay e múltiplos clientes.
- **Riscos residuais:** observação atrasada, mod incompatível, reçipt incerto, vazamentos por logs/metadados e semântica de quest ambígua; todos falham fechados.

## Dependências, revisão e próximos passos

Prioridade normativa de DEC-011/012/022/027/028/029/041/050/053/055/059/060–065/066/074–077/083/089/090/091–102. Pin da campanha/ramo; nenhum acesso físico não autorizado a `knowledge/periods/<ANO>-DR/`. Antes de implementar, validar em Windows BG2:EE básico → EEex → bridge → host + 2 clientes, com canário read-only e testes host-confirmed, privacy review, determinismo, rollback seguro e idempotência. A decisão arquitetural **não promete viabilidade mecânica**.

## Seguinte questão DEC-104 — retificações de repercussões já emitidas

**A:** rollback automático em cascata. **B:** LLM reescreve efeitos e memória. **C recomendada:** rastrear dependências e retificações; quarentenar projeções ainda não executadas; corrigir visões por nova revisão; para atos host-confirmed aplicar somente compensações específicas DEC-095 com nova autorização, sem apagar conhecimento legitimamente recebido.
