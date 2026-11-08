# 82 — Investigações institucionais, abuso de poder, cadeia de comando e medidas seguras

**Discovery v7.8 — DEC-082/C aprovada como arquitetura, não implementada. ADR-0077.**  
**68 testes T082-01..T082-68 candidatos, TODOS NÃO EXECUTADOS.** Nenhuma POC ou mod/bridge BG2:EE/EEex/multiplayer comprovou efeitos de investigação ou medidas institucionais.

## 1. Problema e fronteiras

O Living World pode representar corrupção, fiscalização, conflitos políticos, acusações e revisão de decisões de autoridades **sem** converter boatos em culpa, decidir penas por LLM ou alterar a engine quando uma medida existe apenas em texto. DEC-081 cuida da vítima e de remédios; DEC-082 trata de agentes, chefias, organizações e reformas. Uma decisão institucional ficcional é distinta de verdade factual e de efeito mecânico no host.

**Relações:** DEC-019/022/027–034/041–046/050–059/060–081. DEC-060 preserva o cânone em `knowledge/periods/<ANO>-DR/` **fisicamente separados**, DEC-061/062 asseguram proveniência e curadoria, DEC-063 fixa Knowledge Packs por campanha. Investigação fica em overlay de campanha/branch, não no corpus editorial.

## 2. Entidades conceituais e fronteiras de autoridade

| Entidade candidata | Papel | Não autoriza sozinha |
|---|---|---|
| `InstitutionProfile` | Região, época, função, fonte, estrutura e poderes de organização | Impor norma moderna ou competências presumidas |
| `AuthorityMandate` | Poderes específicos e delegações por intervalo/escopo | Culpa da chefia nem mandado universal |
| `MisconductAllegation` | Alegação de vítima, denunciante ou testemunha, com ACL | Responsabilidade factual ou punição |
| `EvidenceRecord` | Fonte/prova com validade, independência e contradições | Veredito automático por número de relatos |
| `InstitutionalInvestigation` | Caso, investigador, alvo, competência, evento, estado e versões | Concluir má-fé ou condenação |
| `ActorResponsibilityAssessment` | Ação individual e atribuição causal por evidência | Culpar organização inteira |
| `CommandResponsibilityAssessment` | Ordem, delegação, ciência e omissão demonstradas | Imputar comando por cargo somente |
| `InstitutionalPracticeAssessment` | Padrões documentados e controle organizacional | Reforma ou mudança de governo instantânea |
| `InstitutionalMeasureProposal` | Proposta por autoridade, risco, escopo, recurso e efeito | Qualquer execução de motor |
| `InstitutionalEffectLedger` | Idempotência, estado, receipts e correções | Assumir receipt onde não existe |

## 3. Contratos candidatos (não APIs existentes)

```yaml
InstitutionalInvestigation:
  investigation_id: opaque
  campaign_id: opaque
  branch_id: opaque
  institution_id: opaque
  jurisdiction_id: opaque
  investigator_authority_id: opaque_or_null
  mandate_revision: opaque_or_null
  knowledge_pack_revision: opaque
  world_time_dr: opaque
  allegations: [opaque]
  event_refs: [opaque]
  evidence_refs: [opaque]
  checkpoint_epoch: integer
  status: PROPOSED | JURISDICTION_PENDING | EVIDENCE_PENDING | IN_REVIEW | DISPUTED | DECISION_PENDING | CLOSED_INCONCLUSIVE | CLOSED_CONFIRMED | REOPENED | UNCERTAIN | STALE
MisconductAllegation:
  allegation_id: opaque
  actor_or_institution_ref: opaque
  claimant_ref: opaque
  source_claim_id: opaque
  alleged_act_kind: ABUSE | BRIBERY | UNLAWFUL_ORDER | NEGLIGENCE | FAVORITISM | OTHER | UNKNOWN
  event_ref: opaque_or_null
  testimony_refs: [opaque]
  provenance_refs: [opaque]
  sensitivity_acl_ref: opaque
  claim_state: ALLEGED | CORROBORATED | DISPUTED | WITHDRAWN | UNVERIFIED
AuthorityMandate:
  institution_id: opaque
  authority_id: opaque
  authority_type: EXECUTIVE | DISCIPLINARY | RELIGIOUS | GUILD | MILITARY | OTHER
  law_or_custom_source_refs: [opaque]
  competent_actions: [opaque]
  delegation_refs: [opaque]
  valid_from_dr: opaque
  valid_to_dr: opaque_or_null
  verification_state: VERIFIED | UNKNOWN | STALE | DISPUTED
ResponsibilityAssessment:
  assessment_id: opaque
  target_ref: opaque
  kind: ACTOR_ACTION | DIRECT_ORDER | SUPERVISORY_OMISSION | INSTITUTIONAL_PRACTICE
  causal_event_refs: [opaque]
  supporting_evidence_refs: [opaque]
  contradicting_evidence_refs: [opaque]
  reviewer_policy_revision: opaque
  status: PENDING | CORROBORATED | DISPUTED | VERIFIED_PRIVATE | REJECTED
InstitutionalMeasureProposal:
  measure_id: opaque
  investigation_id: opaque
  target_ref: opaque
  issuing_authority_ref: opaque
  effect_kind: NOTICE | REOPEN | REQUEST_INFO | HEARING | CORRECTION | DISCIPLINARY_REVIEW | REMOVAL_PROPOSAL | POLICY_CHANGE_PROPOSAL | NO_ACTION
  supporting_assessment_refs: [opaque]
  risk: LOW | MEDIUM | HIGH
  consent_gate_ref: opaque_or_null
  authority_gate_ref: opaque_or_null
  engine_capability_ref: opaque_or_null
  status: PROPOSED | EVIDENCE_PENDING | APPROVAL_PENDING | NARRATIVE_AUTHORIZED | ENGINE_PENDING | HOST_CONFIRMED | REJECTED | UNCERTAIN
InstitutionalEffectLedger:
  campaign_id: opaque
  branch_id: opaque
  investigation_id: opaque
  target_ref: opaque
  measure_id: opaque
  rule_revision: opaque
  cause_event_id: opaque
  idempotency_key: opaque
  resolution_epoch: integer
  host_receipt_ref: opaque_or_null
  commit_state: NOT_COMMITTED | NARRATIVE_COMMITTED | HOST_CONFIRMED | UNCERTAIN
```

Os contratos são rascunhos candidatos de SPECS. `VERIFIED_PRIVATE` refere-se a avaliação privada sustentada por evidência e procedimento, **não** a comprovação de culpa universal ou a sentença obrigatória. Não há schema, API de BG2:EE ou banco implantados.

## 4. Estados e fluxo proposto

```text
DENUNCIA/ALLEGATION
       |
       v
CHECK_ISSUER_AND_JURISDICTION ----sem fonte/competência----> PENDING_POLICY
       |
       v
EVIDENCE_GATHERING ---> DISPUTED / INSUFFICIENT (sem culpa implícita)
       |
       v
INDIVIDUAL_CAUSALITY / CHAIN_OF_COMMAND / INSTITUTIONAL_PATTERN
       |
       v
REVIEW_RIGHTS_AND_CONTEXT  ---> PENDING_APPROVAL / REJECTED
       |
       v
AUTHORITY_DECISION (ficção, pode estar equivocada)
       |
       v
RISK_GATE + HISTORY + CAMPAIGN_LEDGER
       |
       +----> narrativa autorizada  ---> repercussão contextual DEC-029/074
       |
       +----> mecânica comprovada   ---> Action Gateway ---> host receipt
                                     (se POC existe; caso contrário UNSUPPORTED)
```

**Não há transação distribuída engine/ledger comprovada.** Usar checkpoint DEC-053 e reconciliar qualquer `UNCERTAIN` sem retry destrutivo. Revogação DEC-080 e reparação DEC-081 permanecem operações independentes.

## 5. Distinção de responsabilidade

1. **Agente:** prova de que uma ação foi realizada por identidade verificada (DEC-066) sem extrapolar autoria baseada em nome ou cargo.
2. **Superior:** apenas ordens, delegações, omissões sob competência demonstrada e histórico de conhecimento verificável sustentam vínculo de chefia; organograma não basta.
3. **Organização:** evidências de procedimentos, padrões ou decisões efetivamente institucionais podem sustentar análise, sem responsabilidade coletiva automática por desvio isolado.
4. **Jurisdição:** vigência de norma/competência no ano e região; autoridade de facção não se torna autoridade universal. DEC-078/079/080 controlam alcance, reconhecimento e validade.
5. **Observadores:** rumores de corrupção e crenças de NPCs não são equivalentes a proof de responsabilidade; repercussão exige canal e contexto DEC-029/030/074.
6. **Remédios:** reparação da vítima DEC-081 e responsabilização institucional não dependem de que uma anule ou comprove a outra.

## 6. Exemplos ilustrativos de medidas e riscos

| Proposta | Condições narrativas | Efeito proibido sem POC |
|---|---|---|
| Receber denúncia | Fonte e ACL, competência de recepção | Mandado automático contra agente |
| Solicitar registro de serviço | Disponibilidade documental fundamentada | Gerar script/quest no motor |
| Realizar audiência fictícia | Costume, competência, agência dos PCs | Confissão compulsória de jogador |
| Corrigir notícia oficial | Decisão competente e canal de comunicação | Reputação universal instantânea |
| Investigar disciplina de oficial | Prova e procedimento regional | Remover NPC da área por texto |
| Propor substituição de liderança | Autoridade e política, gate HIGH | Alterar governante histórico/quest |
| Contestar rede de corrupção | Evidências e alçadas diversas | Punir guilda inteira sem nexo |
| Propor reparação ao lesado | Usar DEC-081 separadamente | Duplicar item ou ouro sem receipt |

## 7. Proteção da campanha, segredos e reversões

- Campanha/branch: `campaign_id` e `branch_id` em cada entidade, revisão de Knowledge Pack e checkpoint; restore não importa sanção do futuro.
- Cronologia: não consultar fato de ano DR posterior e não reescrever pastas físicas anuais de lore; fatos do jogo ficam somente no overlay.
- Direitos dos PCs: consentimento e autoria em falas, confissão, controle delegado DEC-041/042/045/046. Não coagir declaração de jogador por decisão LLM.
- Segredos: ACL na coleta, na análise, em cada prompt, worker LAN, log e notícia; sem exposição de denunciante por status público da investigação.
- Provas: anexar proveniência e fonte independente; falsificação/duplicação são hipóteses verificáveis, não automáticas.
- Recuperação: snapshots e replays não duplicam efeitos. `UNCERTAIN` pausa operações de risco e exige reconciliação sem retry cego.
- NPCs/instituições: preservar identidades, memorias e relações; sanção narrada não autoriza exclusão de recurso nativo nem reescrita de arquivo `.CRE` ou script.

## 8. POCs e critérios de evidência futura

1. **G82-0** — Fixtures offline: administração, jurisdição, norma/competência, denúncia, falsa denúncia, provas/contraprovas, cadeia de comando, erro e má-fé.
2. **G82-1** — Validadores determinísticos de autorização, risco, consistência temporal, ACL, revogação de mandados, idempotência e `UNKNOWN` sem engine.
3. **G82-2** — Simulação narrativa com identidade/segredo, reparação separada e impacto social de notícias atrasadas.
4. **G82-3** — Inventário read-only de conteúdo/scripts/quest BG2:EE limpo e interfaces disponíveis, sem supor intervenção mecânica.
5. **G82-4** — Caso isolado de efeito mecânico de baixo risco, somente se capability/adapter forem testados e autorizado, seguido de save/load/crash/restore.
6. **G82-5** — Host + dois clientes, mods/builds, divergência, reconexão, dedup e rollback isolado. Qualquer falha revoga capability.

**Nenhum gate ou teste executado.** Os 68 cenários são candidatos e não validam a engine.

## 9. Matriz de testes candidatos — TODOS NÃO EXECUTADOS

| ID | Cenário esperado | Execução |
|---|---|---|
| T082-01 | Uma acusação contra guarda cria caso investigativo, não condenação. | NÃO EXECUTADO |
| T082-02 | Revogação da prisão não prova automaticamente corrupção de oficial. | NÃO EXECUTADO |
| T082-03 | Reparação da vítima não prova culpa do superior nem da instituição. | NÃO EXECUTADO |
| T082-04 | Um documento sem origem autenticada permanece PENDING_EVIDENCE. | NÃO EXECUTADO |
| T082-05 | Relatos copiados da mesma fonte não contam como provas independentes. | NÃO EXECUTADO |
| T082-06 | Testemunhos contraditórios preservam ambas as versões com provenance. | NÃO EXECUTADO |
| T082-07 | Indício de suborno sem prova da transferência não gera finding confirmado. | NÃO EXECUTADO |
| T082-08 | Prova de erro administrativo não é automaticamente prova de dolo. | NÃO EXECUTADO |
| T082-09 | Conjunto de incidentes distintos pode gerar hipótese de padrão sem condenação. | NÃO EXECUTADO |
| T082-10 | Uma infração individual não reduz automaticamente reputação de toda guilda. | NÃO EXECUTADO |
| T082-11 | Organograma sem vínculo causal não prova ordem dada pelo superior. | NÃO EXECUTADO |
| T082-12 | Uma ordem com assinatura e competência ausentes fica em disputa. | NÃO EXECUTADO |
| T082-13 | Delegação expirada não concede competência contemporânea. | NÃO EXECUTADO |
| T082-14 | Autoridade investigadora inexistente no lore mantém caso pendente. | NÃO EXECUTADO |
| T082-15 | Cargo com poderes desconhecidos não obtém competência por inferência. | NÃO EXECUTADO |
| T082-16 | Leis de região diferente não são aplicadas como universais. | NÃO EXECUTADO |
| T082-17 | Norma de ano DR posterior não é importada em época anterior. | NÃO EXECUTADO |
| T082-18 | Dados históricos são buscados em partição física anual apropriada. | NÃO EXECUTADO |
| T082-19 | Caso da campanha não altera conhecimento canônico anual. | NÃO EXECUTADO |
| T082-20 | Knowledge Pack alterado não muda retroativamente decisão sem migração. | NÃO EXECUTADO |
| T082-21 | Chefe pode discordar de acusação sem alterar fatos confirmados. | NÃO EXECUTADO |
| T082-22 | Autoridade corrupta pode mentir como comportamento ficcional, não como fato. | NÃO EXECUTADO |
| T082-23 | Confissão inventada por LLM não altera verdade ou autoria de PC. | NÃO EXECUTADO |
| T082-24 | Falas voluntárias de PC exigem sua ação autorizada. | NÃO EXECUTADO |
| T082-25 | PC ausente não confessa automaticamente por estar no grupo. | NÃO EXECUTADO |
| T082-26 | PC delegado mantém titular e controlador distintos. | NÃO EXECUTADO |
| T082-27 | Pessoa com identidade secreta não é desmascarada por processo público. | NÃO EXECUTADO |
| T082-28 | Fonte confidencial não é publicada a observador sem ACL. | NÃO EXECUTADO |
| T082-29 | Worker LAN não recebe provas privadas sem finalidade e role autorizadas. | NÃO EXECUTADO |
| T082-30 | Prompt do LLM recebe versão minimizada de depoimento sigiloso. | NÃO EXECUTADO |
| T082-31 | Logs redigidos não expõem nome de denunciante sem necessidade. | NÃO EXECUTADO |
| T082-32 | Pedido de investigação não cria mandado ou ordem coercitiva automaticamente. | NÃO EXECUTADO |
| T082-33 | Relatório narrativo não altera facção, inventário nem quests. | NÃO EXECUTADO |
| T082-34 | Proposta de afastamento não remove NPC de área/engine. | NÃO EXECUTADO |
| T082-35 | Mudança de governo HIGH é bloqueada sem gate específico. | NÃO EXECUTADO |
| T082-36 | Proposta de prisão de autoridade sem capability é rejeitada. | NÃO EXECUTADO |
| T082-37 | Proposta de perda de itens sem host receipt não é confirmada. | NÃO EXECUTADO |
| T082-38 | Boato sobre corrupção só afeta crenças de quem recebeu canal legítimo. | NÃO EXECUTADO |
| T082-39 | Reputação social regional não vira reputação mecânica de BG2:EE. | NÃO EXECUTADO |
| T082-40 | Dois rumores do mesmo fato não geram sanção material duplicada. | NÃO EXECUTADO |
| T082-41 | Duas autoridades em disputa de competência não decidem como uma só. | NÃO EXECUTADO |
| T082-42 | Medida emitida por autoridade não competente é rejeitada ou contestada. | NÃO EXECUTADO |
| T082-43 | Revisão formal preserva histórico de acusações e conclusões. | NÃO EXECUTADO |
| T082-44 | Nova prova válida gera reabertura, não edição silenciosa de findings. | NÃO EXECUTADO |
| T082-45 | Revogação da medida não apaga danos confirmados anteriormente. | NÃO EXECUTADO |
| T082-46 | Reparação independente evita segunda compensação do mesmo dano. | NÃO EXECUTADO |
| T082-47 | Dois jobs concorrentes não aplicam a mesma medida. | NÃO EXECUTADO |
| T082-48 | Retry após timeout UNCERTAIN não aplica segundo efeito. | NÃO EXECUTADO |
| T082-49 | Receipt de cliente não confirma execução mecânica do host. | NÃO EXECUTADO |
| T082-50 | Receipt de outro branch/checkpoint não confirma mudança atual. | NÃO EXECUTADO |
| T082-51 | Restore antigo não incorpora sanções de futuro abandonado. | NÃO EXECUTADO |
| T082-52 | Migração de mods invalida adapter antigo de demissão/quest. | NÃO EXECUTADO |
| T082-53 | Medidas de impacto acumulado HIGH exigem gate agregado. | NÃO EXECUTADO |
| T082-54 | Combinação de LOW não contorna aprovação HIGH para mudança política. | NÃO EXECUTADO |
| T082-55 | Consequências contra outros PCs respeitam consentimento e agência. | NÃO EXECUTADO |
| T082-56 | Oficial não conhece automaticamente acusações de cidade distante. | NÃO EXECUTADO |
| T082-57 | Investigações de outras facções precisam de transmissão e competência. | NÃO EXECUTADO |
| T082-58 | Pista falsificada mantém origem e indicador de disputa. | NÃO EXECUTADO |
| T082-59 | Interesse de guilda não prova que a guilda ordenou delito. | NÃO EXECUTADO |
| T082-60 | Uma cadeia de comando pode variar no tempo sem alterar história pregressa. | NÃO EXECUTADO |
| T082-61 | Incapacidade de ler estado da engine não é interpretada como demissão aplicada. | NÃO EXECUTADO |
| T082-62 | Condição de recurso computacional reduzido mantém fila em PENDING. | NÃO EXECUTADO |
| T082-63 | Monitoramento alerta sobre ações HIGH pendentes sem executá-las. | NÃO EXECUTADO |
| T082-64 | Caso INCONCLUSIVE pode terminar sem punição ou absolvição declarada. | NÃO EXECUTADO |
| T082-65 | Modelo privado sem fontes necessárias não cria lei local fictícia. | NÃO EXECUTADO |
| T082-66 | Organização com autoridade parcial não altera instituição externa. | NÃO EXECUTADO |
| T082-67 | POC read-only não prova suporte multiplayer de mudanças mecânicas. | NÃO EXECUTADO |
| T082-68 | Teste host+dois clientes é gate obrigatório antes de alegar integração. | NÃO EXECUTADO |

## 10. DEC-083 — Próxima escolha em aberto

**Proteção de denunciantes, testemunhas e fontes em investigações institucionais:** A) publicidade irrestrita por padrão; B) sigilo imutável, mesmo para destinatário competente; **C recomendada)** proteção proporcional e contextual, identidade/ACL por audiência, consentimento e riscos, evidências rastreáveis e divulgação controlada sob competência; nenhum NPC torna-se invulnerável e nenhuma engine é alterada sem POC. Não está aprovada pela DEC-082.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

DEC-083 completa proteção de denunciantes já prevista: separar conteúdo e identidade de fonte; provar nexo individual/institucional, proteger sigilo sem impedir contestação contextual.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Instituição investigada não obtém sigilo de plano por ser autoridade; ameaças de retaliação devem ser provadas e analisadas sem pressupor corrupção coletiva.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Possível vazamento interno exige investigação de autoria por prova e competência; suspeita não torna toda organização culpada.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Boato fabricado de corrupção não confirma abuso institucional nem altera governo; apuração e autoria com prova necessária.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Cumplicidade institucional por agente duplo requer evidência distinta da responsabilidade individual; suspeitas e contatos não condenam a organização.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

NPC contratado não torna guilda inteira cúmplice ou culpada. Responsabilização institucional exige evidência independente e autoridade competente.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Denúncia de abuso requer distinguir relato, culpa individual/chefia/instituição e provas verificáveis; boato não altera governo.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Dossiê institucional compartilha avaliações separadas de agente, chefia e órgão com evidências adequadas e público legítimo; divulgação não condena automaticamente.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Planos contra agente acusado não implicam culpa institucional ou reforma automática; competência e fatos individuais distintos.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Mudança de plano de investigação institucional não autoriza sanções ou mudanças de liderança sem autoridade e gate próprio.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Reformas/investigações concorrentes não podem impor mudança de governo automaticamente por prioridade ou bloqueio de recursos.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Impasse de operações de fiscalização não gera culpa institucional nem reforma automática; priorização e replanejamento devem ser autorizados.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Investigações institucionais não usam omnisciente leitura de flags protegidas.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Apuração institucional não recebe acesso indiscriminado a estados privados de quests.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **accountability institucional**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para investigação institucional não apaga relatos prévios nem responsabilidade, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para accountability institucional após acusação indevida, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Accountability institucional não equivale a sanção automática. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Instituições contestam obrigações em procedimento próprio, não por sanção da IA. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
