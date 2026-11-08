# ADR-0096 — DEC-101/C: catálogo semântico curado e versionado de estados técnicos de quests

- **Data:** 2026-11-07.
- **Decisão:** DEC-101, alternativa **C**, expressamente aprovada.
- **Estado:** **APROVADA COMO ARQUITETURA**; implementações e POCs com BG2:EE/EEex/bridge ainda não realizadas.
- **Discovery:** v9.7. **ADR-0001 a ADR-0095 permanecem byte a byte inalterados**, assim como todas as decisões DEC-060 a DEC-100.
- **Contrato normativo:** `docs/101-mapeamento-semantico-curado-quests-transicoes-ambiguidade-e-divulgacao.md`.
- **Próxima decisão:** DEC-102 — reconciliação semântica entre progresso de quests do host e overlay persistente do Living World.

## Contexto

A DEC-100/C admite apenas observações autorizadas, read-only e comprovadas por build, produzindo envelopes técnicos privados e projeções narrativas mínimas. Entretanto, uma variável numérica como `QUEST_STAGE=4` **não tem significado universal**: scripts diferentes, versões de mods, diálogos e condições suplementares podem lhe atribuir semânticas distintas. Interpretá-la genericamente pode inventar uma conclusão, produzir spoilers, desfazer uma quest ou induzir um NPC a alegar conhecimento impossível.

O problema não é apenas transformar números em descrições; é estabelecer **prova técnica, temporal, causal e editorial** de que um conjunto observado permite um marco semântico particular, sem expor a observação bruta ao narrador ou sobrepor fatos do host.

## Alternativas

- **A — heurísticas de variáveis e valores entre quests/builds:** rejeitada. Nomes e números semelhantes não são evidência de semântica idêntica; gera falsos positivos e vazamentos.
- **B — LLM interpreta flags/scripts e decide marcos:** rejeitada. Interpretação não determinística e inferências sem evidência podem antecipar bifurcações ou confundir dado interno com conhecimento de personagem.
- **C — mapeamentos curados e versionados, transições verificáveis, ambiguidades explícitas, saída mínima autorizada:** **APROVADA**.

## Decisão normativa

1. **Catálogo por fingerprint completo.** `QuestSemanticCatalog` liga `quest_key` interno opaco, `mapping_revision`, `build_fingerprint`, `EEex/bridge`, `modpack_hash`, ordem e revisões de mods, `script_digest`, `quest_variant`, revisão de `ObservationCapabilityManifest`, fontes de curadoria, estado `CURATED/REVIEW_PENDING/REVOKED`, e janela de compatibilidade. Não existe fallback genérico entre versões nem herança implícita de scripts de mesmo nome.
2. **Predicados tipados e semântica verificável.** Um `SemanticMilestoneRule` usa conjunto allowlisted de `probe_id` e predicados `eq/in/all/any` com domínio finito, prova de cobertura, freshness, ordem temporal, dependências e `semantic_id` opaco. O avaliador determinístico não executa código dinâmico, expressões livres ou comandos de mod. O compilador de regras valida determinismo, referências, conflitos e versões antes da publicação.
3. **Fases compostas, exclusividade e revisão.** Marcos `NOT_STARTED`, `STARTED`, `OBJECTIVE_DONE`, `RESOLVED`, `FAILED`, `BRANCH_X` são exemplos de vocabulário; **nenhuma dessas fases autoriza interpretação de quest real sem catálogo curado**. Regras mutuamente exclusivas detectadas simultaneamente produzem `AMBIGUOUS`/`CONTRADICTORY`; **não** prevalece a última lida, a mais numerosa nem a escolha da LLM.
4. **Transições causais.** `MilestoneTransition` declara origens, destinos e pré-condições de transição, identidade da quest, evidência observacional suficiente, sequência monotônica/epoch e evento reconhecido do host. Progressão, repetição, retorno de save, ramo alternativo e reset de quest são tratados distintamente; `RESOLVED` não implica que o PC concluiu a quest, foi o autor ou descobriu seus segredos.
5. **Cobertura e negação.** Uma prova positiva pode usar observação parcial quando **todos os predicados positivos necessários** foram comprovados no escopo. Falta de campo, scanner parcial, `UNAVAILABLE`, `STALE`, `NOT_OBSERVED`, ou etapa não mapeada **não** provam `FALSE`, `NOT_STARTED` ou falha. Atestar ausência exige mapeamento negativo explícito e cobertura completa de todas as alternativas autorizadas.
6. **Incerteza de primeira classe.** Resultados: `MAPPED_MINIMAL`, `UNKNOWN`, `AMBIGUOUS`, `CONTRADICTORY`, `STALE`, `UNAVAILABLE`, `BLOCKED_BUILD`, `BLOCKED_MAPPING`, `BLOCKED_TRANSITION`, `BLOCKED_ACL`, `BLOCKED_SPOILER`. Resultados incertos jamais geram fatos, rumores, atualizações de reputação ou gatilhos mecânicos.
7. **Estanqueidade e disclosure independente.** `TechnicalObservationEnvelope` permanece no domínio protegido DEC-100. Apenas um `SemanticMilestoneAssertion` validado poderá produzir, mediante ACL de finalidade/audiência, `SafeQuestMilestoneProjection` mínima, sem valor bruto, nome de variável, IDs de ramos futuros, script, pistas ocultas, aliases ou secrets. A projeção disponibilizada **não** confirma entrega nem conhecimento de um NPC; DEC-028/029/064/083/090 regem a divulgação causal.
8. **Proveniência e revisão.** Cada afirmação segura mantém IDs opacos de regra, hash de catálogo, dependências de probe, cobertura, versão, campaign/branch, host/checkpoint epoch, `observed_at` e status de revisão. Corrigir um mapping produz nova versão e registro de correção, **sem reescrever** diálogos/fatos já observados.
9. **Compatibilidade e migração.** Atualização de BG2:EE/EEex/bridge/modpack/ordem/script/observador ou catálogo invalida avaliações e caches. Sem prova de equivalência semântica, persistir em `UNKNOWN/BLOCKED_MAPPING` até curadoria e POC. Save/load, alternância de campanha e restore invalidam transições que dependeram da antiga timeline.
10. **Separação entre etapas e execução.** Interpretar uma flag não dá permissão para modificá-la; não executa quest, não escreve global, não confirma ação ou recebimento, não despacha comando. DEC-011/012/050/053/099/100 mantêm ownership, host receipts e controle de ações independente.
11. **Segurança multilayer.** Logs, caches, LAN, UI e prompts não contêm dados brutos protegidos; usar chaves segmentadas por build/modpack/mapping/campaign/branch/audience/purpose/epoch. Proveniência legível somente por autoridade de auditoria, logs com IDs opacos. Textos de mods/scripts são dados não confiáveis, nunca instruções a LLM.
12. **Preservação cronológica.** O catálogo de interpretação de quest é metadado técnico versionado **separado** de `knowledge/periods/<ANO>-DR/` e do overlay de campanha; não altera cânone nem cria eventos históricos DEC-096/097. Uma quest semântica concluída pode alimentar um filtro temporal apenas após derivação e autorização verificadas.
13. **Teste e evidência.** O avaliador e schema em `examples/chronology/` operam **apenas com fixtures sintéticas**; não são integrações reais, não interpretam quests oficiais e não demonstram hook EEex. Os **128 casos T101-001..T101-128 são candidatos NÃO EXECUTADOS**. POCs Windows/host + dois clientes, snapshots, save/load, mods e spoilers seguem obrigatórias.

## Consequências

**Benefícios:** progressão semântica auditável, extensível por build, independente da LLM e compatível com privacidade. **Custos:** curadoria por versão e quest, POCs de cobertura, catálogo e testes de transições, política de invalidacão e divergências. **Risco residual:** metadados de mapeamento podem ser spoilers; seu acesso é mais restrito do que a projeção narrativa.

## Critérios para implementação futura

- Adapters read-only demonstrados por build e sem efeitos colaterais (DEC-100).
- Catálogos curados assinados/versionados, predicados completos e exclusividade testada.
- Ausência/scan parcial sem falso negativo; conjuntos simultâneos incompatíveis sem precedência arbitrária.
- Projeções apenas para destinatários autorizados, sem vazamentos de valores, nomes e caminhos futuros.
- Restore, patch, mod incompatível e sequência regressiva bloqueados até prova de transição/recertificação.
- Nenhuma leitura, mudança de quest ou receipt de host executado nos exemplos Python.
