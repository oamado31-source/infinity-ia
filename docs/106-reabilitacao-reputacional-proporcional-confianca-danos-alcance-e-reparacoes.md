# 106 — Reabilitação reputacional proporcional, reconstrução de confiança e reparações não automáticas

**Decisão:** DEC-106/C APROVADA, ADR-0101. **Versão:** Discovery v10.2, 2026-11-07. **Nível:** arquitetura / contratos candidatos; nenhuma integração real BG2:EE/EEex, nenhum efeito mecânico confirmado. **Imutabilidade:** DEC-060..105 e ADR-0001..0100 mantidos.

## 1. Escopo, dependências e fronteiras

DEC-105 distribui a correção por canais legítimos, podendo gerar prova de percepção e propostas para revisão de crença. DEC-106 trata de **reparar consequências reputacionais** depois que a acusação foi comprovadamente corrigida, sem assumir que correção da verdade, ciência de terceiros, confiança pessoal, contratos comerciais e reparação material são equivalentes.

O módulo se relaciona com DEC-030 (reputação contextual), DEC-064/065 (memória e crença falível), DEC-075/077/089 (autoria e evidência), DEC-078/080/081/082 (justiça, sanções, reparações e responsabilização), DEC-083–086 (fontes protegidas/desinformação), DEC-087/088 (lealdades e informantes), DEC-090 (dossiês), DEC-091–095 (planejamento, recursos, sagas e dedup), DEC-096/097 (cronologia/efeitos), DEC-099–104 (host/quest, admissão e retificações) e DEC-105 (comunicação). **Nenhuma cria autorização de reescrita por acoplamento.**

## 2. Modelo lógico de causas e consequências

```text
WorldFact / QuestMilestone         CommittedCorrectionProof (DEC-104)
               |                              |
         original allegation                trusted registry
               |                              |
          accusation dissemination     correction dissemination (DEC-105)
               |                              |
           per-recipient exposure       per-recipient perception
               |                              |
           reputation context      belief review / receipt (se autorizado)
               |                              |
           harm claims ledger     reconciliation of audience coverage
                \                            /
                 -> RehabilitationCase (subject + community + purpose)
                     -> DETERMINISTIC ELIGIBILITY / BOUNDARIES
                     -> Proposals (clarification, reply, trust review, remedy)
                     -> external authorization + outbox + Action Gateway
                     -> separate delivery/host/restitution receipts
```

O **caso não tem efeito de execução**. Estados confirmados no jogo são inalteráveis e qualquer compensação tem nova evidência causal e policy própria. Um anúncio público não é entregue a todos por default. Nenhuma projeção única controla a reputação de todas as facções simultaneamente.

## 3. Entidades candidatas (versionadas)

| Entidade | Principais campos | Invariantes |
|---|---|---|
| `SubjectIdentity` | `persistent_subject_id`, `kind: NPC/FAC/PC/ORG`, aliases, owner | Identidade real não inferida de apelido; PCs sempre controlados pelo titular |
| `RehabilitationCase` | `case_id`, `subject_id`, `principal`, `purpose`, `audience`, `consent`, `expected_revision` | Abertura legítima não confirma culpa/inocência por si só |
| `CorrectionProof` | `correction_ref`, `committed_revision`, `source_family`, `grade`, `classification`, `time_dr`, `claim_ref` | DEC-104; prova independente do pedido; nunca do prompt |
| `ExposureCohort` | `cohort_key`, `individual_recipient_ids`, `original_claim_views`, `received_at_dr` | Não estimar público total por contagem de NPCs não observados |
| `CorrectionAudienceLedger` | `recipient`, `correction_ref`, `delivery`, `perception`, `belief_review_ref` | Entrega ≠ percepção ≠ aceitação ≠ restauração de confiança |
| `ReputationDimension` | `region`, `community`, `relationship`, `dimension`, `revision`, `policy` | Contextos comerciais, pessoais, institucionais separados |
| `HarmAssessment` | `harm_id`, `kind`, `causal_parent`, `grade`, `proof_refs`, `source_family`, `realized_at_dr` | Alleged / disputed / proven / host-confirmed; valores monetários apenas se documentados |
| `TrustProposal` | `subject`, `recipient`, `context`, `new_evidence`, `CAS`, `approver` | Nunca sobrescrever crença NPC/PC; propor oportunidade, não forçar aceitação |
| `RemedyProposal` | `remedy_kind`, `resources`, `owner`, `case_scope`, `risk`, `consent`, `required_receipts` | Recurso deve existir, compensação aprovada separadamente |
| `RepairLedger` | `case_key`, `action_ref`, `status`, `branch`, `epoch`, `event_time`, `receipt` | Dedup, retenção histórica, sem apagar dano anterior |

### Estados

- **Prova:** `NOT_FOUND / CONTESTED / PARTIAL / CORROBORATED / COMMITTED / REVOKED`. O planejador só admite prova `COMMITTED` curada; documentos parciais geram investigação, não reconhecimento de inocência universal.
- **Causa reputacional:** `ALLEGED / LINKED / CONFIRMED / DISPUTED / UNKNOWN`; alegação de dano não é prova de dano nem de seu nexo causal.
- **Recepção:** `NOT_SENT / QUEUED / IN_TRANSIT / DELIVERED / PERCEIVED / UNCERTAIN` — mensagens e conhecimento são diferentes, conforme DEC-105.
- **Confiança contextual:** `UNREVIEWED / CONTESTING / RECONSIDERING / WILLING_TO_REENGAGE / UNCHANGED` — a aprovação de um caso não impõe transição; eventuais estados finais somente em recibos do controlador legítimo.
- **Propostas de remediação:** `DRAFT / ELIGIBLE / NEEDS_CONSENT / NEEDS_EVIDENCE / NEEDS_RESOURCE / QUARANTINED / REJECTED / AUTHORIZED / DISPATCHED / UNCERTAIN / CONFIRMED / COMPENSATED` — transições entre proposto e executado dependem de serviços separados.

## 4. Regras de elegibilidade e proporção

1. **Gate de prova:** `CommittedCorrectionProof` vinculada ao `OriginalAccusation`, com origem e revisão curadas, independentes do pedido, mesma campanha, branch, epochs e política.
2. **Gate de sujeito e escopo:** titular persistente, audiência, finalidade e reputação contextual identificados. Casos coletivos não autorizam automaticamente publicação de nomes privados nem edição de reputações individuais.
3. **Gate de ACL:** classificação, fontes protegidas e direito de resposta per audience; redigir prova sensível antes de gerar comunicado/LLM. Sob incerteza, falhar fechado.
4. **Gate de alcance real:** universo de destinatários da acusação ≠ destinatários que receberam errata. Não inferir aceitação por grupo; não inventar entrega para NPC offscreen.
5. **Gate de dano:** vincular cada prejuízo a ato observável e nexo causal. Separar perda material comprovada, desconfiança narrativamente observada, prejuízo alegado e consequências preexistentes da acusação. Não usar apenas uma porcentagem de reputação.
6. **Gate de autonomia:** uma vítima pode escolher não divulgar dados; NPC/facção pode negar reconciliação; um PC não oferece restituição ou confessa sem decisão explícita de seu jogador. Não configurar “dever de perdoar”.
7. **Gate de meios:** retratação pública exige emissor, canal, data, custo, audiência, recursos e recibo; compensação patrimonial DEC-081/095, ownership DEC-099, Action Gateway/host para mecânica.
8. **Gate de fairness:** critérios proporcionais de curadoria e políticas explícitas, sem percentuais inventados. Reabilitar não deve punir injustificadamente outras vítimas, criar evidências falsas ou esconder dano real ainda contestado.
9. **Gate de revisão:** provas novas podem alterar propostas anteriores; não apagar a história; ledger de remediações e recursos CAS/fencing por revisão.
10. **Gates de high risk:** coerção, condenação, absolvição formal, multas, indenizações obrigatórias, mudanças de quest e reputação nativa dependem de autoridade institucional/jogador/host, nunca apenas avaliação social.

## 5. Fluxo de decisão de referência

```text
trusted fixture / request(ref + purpose + expected revision)
    -> authenticate principal + policy pinned
    -> resolve COMMITTED correction by registry, protected claim and exact subject
    -> bind branch, lineage, build/modpack, host/checkpoint epoch
    -> authorize purpose, audience, context and beneficiary consent
    -> verify actual exposure + correction delivery/perception; no audience inference
    -> examine actual harm ledger, provenance family and scope
    -> plan scoped informational / contestation / trust-review opportunities
       (depending on audience proof, confidence and real awareness)
    -> if harm proven: mark restitution review as separately eligible, NOT granted
    -> output proposals with stable idempotency key and CAS
    -> stop; NO message sent; NO currency, rep score, NPC memory or host writes
```

### Exemplos de resultados permitidos

| Evidência | Público | Proposta segura |
|---|---|---|
| Correção committed, público ouviu acusação mas não recebeu errata | Audiência autorizada | `PROPOSE_SCOPED_CORRECTION_NOTICE`, sem afirmar aceitação |
| Correção foi entregue, mas não percebida | Mesmo destinatário | `WAIT_FOR_PERCEPTION`, não revisar opinião |
| NPC percebeu correção e ainda contesta | NPC com crenças falíveis | `PROPOSE_OPTIONAL_TRUST_DIALOGUE`, nenhuma alteração efetiva |
| NPC recebeu e aceitou correção, relação comercial ainda abalada | Contexto comercial | `PROPOSE_REENGAGEMENT_OPTION`, sem restabelecer contrato automaticamente |
| Perda econômica alegada, sem recibos/prova | Interessado | `REQUEST_DAMAGE_EVIDENCE`; nenhuma restituição presumida |
| Perda comprovada com nexo causal | Protocolo de reparação | `REFER_TO_RESTITUTION_REVIEW`; sem transferência nem obrigação automática |
| Prova está contestada ou é de outro branch | Qualquer público | `QUARANTINED`, sem divulgação ou reparação |

### Exemplo fictício de guilda

Uma guilda mercantil de uma cidade fictícia foi acusada de financiar saqueadores e teve dois contratos rompidos. O host confirma apenas o rompimento de um contrato; a perda do segundo é mera alegação. Após retificação curada, alguns comerciantes recebem a prova, outros não, e parte daqueles que a recebe permanece desconfiada. A proposta poderá oferecer esclarecimento restrito a quem conheceu a acusação, uma oportunidade voluntária de diálogo com os comerciantes que receberam a prova e *revisão independente* da alegação de perda do segundo contrato. O contrato rompido confirmado **não será reintegrado automaticamente**. Nenhuma fonte protegida aparece nos comunicados.

## 6. Temporalidade, conhecimento e cobertura

- Uma notícia original pode alcançar públicos em meses DR diferentes. A correção tem rota própria, com seus próprios destinatários/horários e DEC-022 `FROZEN/PARTIAL/REALTIME`.
- Um evento de alcance regional não implica que todas as tavernas, guildas e NPCs daquela região foram expostos. A matriz DEC-096/097 define condições, não um broadcast.
- `RecipientBelief` não define `ReputationContext` por si só: confiança social, interesse econômico e reputação pública possuem histórias próprias.
- Restabelecer confiança pode exigir atos narrativos sucessivos e escolhas individuais; não basta estimar intervalo de “recuperação” com LLM.
- `WorldFact` e conhecimento canônico anual permanecem fisicamente isolados, conforme DEC-060–063; histórias de casos pertencem ao estado de campanha e seus ramos.

## 7. Segurança, dados e idempotência

```text
case_key = SHA256(campaign, branch, lineage, host_epoch, checkpoint_epoch,
                  policy_revision, correction_revision, accusation_ref,
                  subject_id, target_reputation_scope, case_revision)
remedy_key = SHA256(case_key, remedy_type, target_recipient_id_or_cohort,
                    harm_refs, expected_ledger_revision)
```

- `request` não inclui `trusted_policy`, `trusted_store`, `grant_access`, `damage_proof`, `already_paid`, `host_receipt`, `consent`; todos são obtidos de registros autenticados separados. Fixture de teste não substitui atestação de produção.
- Compatibilidade por build/modpack e ACL de sources/vítimas devem valer antes de consulta à LLM e antes de logs públicos. Tamanho do dossiê ou key não deve expor identidades.
- Dedup e CAS impedem múltiplos propostas para o mesmo caso/revisão; despesas com `DISPATCHED/UNCERTAIN` jamais são repetidas automaticamente. Retirada de consentimento invalida propostas futuras sem revogar retrospectivamente atos já confirmados.
- Sem integração comprovada com store real, qualquer saída do algoritmo sintético é *proposal only*, não uma ação habilitada no jogo.

## 8. Compatibilidade com sistemas anteriores

| Domínio | Limite normativo |
|---|---|
| DEC-030 | contextualidade da reputação por facção/indivíduo e relacionamento |
| DEC-064/065 | memória falível, persistência, sem reescrita forçada |
| DEC-075/077/089 | autoria, prova, fonte independente, alegação ≠ fato |
| DEC-078/080/081/082 | procedimento institucional, revisão jurídica e reparações |
| DEC-083–086 | identidades e fontes protegidas, falsas alegações, desinformação |
| DEC-090/095 | dossiês redigidos, compensação Saga com recurso e novo receipt |
| DEC-096/097 | efeitos históricos por domínio, tempo, região, sem escalada global |
| DEC-099/100/101 | ownership e observação/semântica do host, proteção de spoilers |
| DEC-102/103/104 | reconciliação, admissão de repercussões e retificação não destrutiva |
| DEC-105 | entrega/percepção/belief review separadas de confiança/reputação |

## 9. Evidências de implementação pendentes

- Testar capability REAL de reputação BG2:EE e ownership de campos, sem alterar NPC original, script, romance, quest ou estado de outro mod.
- Verificar transporte e percepção de comunicações em campanha com host e dois clientes; on/off-screen; geografia e relógio DR; sem conhecimento universal.
- Testar procedimento de retratação e consentimento de NPC/PC e ausência de coerção automática.
- Testar contratos, inventário, economia e indenizações em ambiente de teste, com recibos e idempotência, nunca em save real sem autorização.
- Validar proteção de fontes, alias, NPC identity, auditoria, branch/epoch, restaurações, migrações de modpack e capacidade de offline-first.
- Medir custo e latência dos registries e retenção de históricos. Não há porcentagem de reputação ou algoritmo de confiança calibrado em dados reais.
- T106-001..T106-148 são **cenários candidatos de integração, NÃO EXECUTADOS**; exemplos sintéticos aprovam somente contratos didáticos.

## 10. Testes candidatos — T106-001..T106-148 (NÃO EXECUTADOS)

**Todos os casos desta seção representam critérios de aceite propostos, não testes executados em BG2:EE/EEex ou multiplayer.**

### Prova de retificação e causalidade

| ID | Cenário candidato — NÃO EXECUTADO no jogo |
|---|---|
| T106-001 | prova DEC-104 committed e curada vinculada à acusação original. |
| T106-002 | correção ainda draft não é aceita como prova. |
| T106-003 | prova contestada exige investigação e não restauração automática. |
| T106-004 | fonte não atribuída permanece em quarentena. |
| T106-005 | ramo divergente não reutiliza a retificação de outra campanha. |
| T106-006 | prova revogada exige revisão e não notificação automática. |
| T106-007 | duas correções encadeadas preservam versões e suas referências. |
| T106-008 | correção sem origem independente não cria absolvição universal. |
| T106-009 | mapeamento semântico de quest divergente não atesta inocência. |
| T106-010 | receipt de retificação com epoch errado não confere autoridade. |
| T106-011 | retificação de rumor não altera fatos originalmente confirmados pelo host. |
| T106-012 | correção não apaga a acusação do histórico epistêmico. |

### Alcance de acusações e correções

| ID | Cenário candidato — NÃO EXECUTADO no jogo |
|---|---|
| T106-013 | NPC não exposto à acusação não recebe mudança automática de reputação. |
| T106-014 | correção emitida não é automaticamente entregue. |
| T106-015 | entrega de correção não implica percepção. |
| T106-016 | percepção não implica aceitação da versão corrigida. |
| T106-017 | destinatário que ouviu apenas resumo não conhece anexos. |
| T106-018 | coorte regional não significa todos NPCs da região. |
| T106-019 | canal comercial alcança apenas destinatários com prova de entrega. |
| T106-020 | rumor ecoado de mesma fonte não cria prova de exposição independente. |
| T106-021 | mensageiro em trânsito não pode ser presumido entregue. |
| T106-022 | modo FROZEN impede avanço implícito do canal. |
| T106-023 | correção a grupo não comprova percepção de cada membro. |
| T106-024 | correção futura não é propagada em data DR passada. |

### Crenças, confiança e autonomia

| ID | Cenário candidato — NÃO EXECUTADO no jogo |
|---|---|
| T106-025 | NPC aceita prova mas recusa renegociar contrato por razão independente. |
| T106-026 | NPC contesta correção sem que o sistema reescreva sua memória. |
| T106-027 | NPC acredita em versões parcialmente contraditórias com incerteza preservada. |
| T106-028 | personagem de jogador não recebe perdão decidido pela IA. |
| T106-029 | companheiro canônico preserva valores e relações existentes. |
| T106-030 | lealdade faccional influencia propostas sem criar verdade histórica. |
| T106-031 | mudança de belief não implica alteração de confiança comercial. |
| T106-032 | confiança restaurada em comunidade não se transmite automaticamente a outra. |
| T106-033 | pedido de desculpas não implica perdão do destinatário. |
| T106-034 | NPC ausente não aceita conversa que não ocorreu. |
| T106-035 | retiro de consentimento interrompe novas propostas futuras. |
| T106-036 | proposta de diálogo voluntário não despacha ação mecânica. |

### Reputação contextual e não global

| ID | Cenário candidato — NÃO EXECUTADO no jogo |
|---|---|
| T106-037 | reputação comercial em um distrito permanece distinta da reputação política. |
| T106-038 | reputação de pessoa não modifica reputação de toda a organização. |
| T106-039 | alias não se torna sujeito independente quando referir a mesma pessoa. |
| T106-040 | alteração de relação familiar não altera reputação mercantil por padrão. |
| T106-041 | uma desculpa para um cliente não atualiza confiança de outros clientes. |
| T106-042 | reputação antiga de guilda não é zerada por retificação pontual. |
| T106-043 | indicador social proposto não vira valor BG2:EE sem host receipt. |
| T106-044 | dimensão não curada resulta em bloqueio do plano. |
| T106-045 | revisão stale do contexto impede corrida entre clientes. |
| T106-046 | relação NPC possui proprietário e consentimento independentes. |
| T106-047 | ausência de dano conhecido não implica reputação íntegra. |
| T106-048 | escore de popularidade nunca é inventado por LLM. |

### Danos, evidências e indenizações

| ID | Cenário candidato — NÃO EXECUTADO no jogo |
|---|---|
| T106-049 | prejuízo financeiro alegado não é automaticamente provado. |
| T106-050 | contrato rompido exige origem e receipt para reconhecimento confirmado. |
| T106-051 | mesmo contrato não é contabilizado duas vezes por relatórios ecoados. |
| T106-052 | dano de outra causa não é imputado à acusação corrigida. |
| T106-053 | dano comprovado permite propor revisão separada de reparação. |
| T106-054 | dano contestado permanece contestado e revisável. |
| T106-055 | indenização não é presumida igual à perda estimada. |
| T106-056 | cobrança de indenização exige legitimidade da autoridade. |
| T106-057 | ouro inexistente não é criado para pagar reparação. |
| T106-058 | itens de terceiro não são transferidos sem ownership. |
| T106-059 | pagamento já confirmado não é apagado por novas evidências. |
| T106-060 | acordo comercial não é restaurado por manipulação de flag. |

### Contraditório e legitimidade

| ID | Cenário candidato — NÃO EXECUTADO no jogo |
|---|---|
| T106-061 | beneficiário pode solicitar esclarecimento sem expor fonte protegida. |
| T106-062 | pessoa acusada não se torna culpada por manter silêncio. |
| T106-063 | pessoa acusadora mantém direito de contestar alegada correção. |
| T106-064 | declaração em nome do PC exige ação explícita do titular. |
| T106-065 | retratação por guilda exige representante competente. |
| T106-066 | pedido de reabilitação não concede autorização de broadcast. |
| T106-067 | processo jurídico não é revertido apenas por revisão de crença. |
| T106-068 | correção formal não absolve outras condutas independentes. |
| T106-069 | consentimento retirado bloqueia novas publicações. |
| T106-070 | NPC pode recusar encontro de conciliação sem punição automática. |
| T106-071 | prova curada não elimina divergência de opinião legítima. |
| T106-072 | interesses de terceiros não conferem direito de alterar reputação alheia. |

### Proteção de identidade e privacidade

| ID | Cenário candidato — NÃO EXECUTADO no jogo |
|---|---|
| T106-073 | identidade real de informante não aparece em anúncio público. |
| T106-074 | pseudônimo protegido mantém vínculo privado restrito por ACL. |
| T106-075 | refúgio e roteiro de escolta não são revelados como metadado de reparação. |
| T106-076 | dossiê privado não é integralmente anexado à retratação pública. |
| T106-077 | logs e métricas omitem vítima e detalhes sensíveis. |
| T106-078 | LLM recebe somente view redigida e autorizada. |
| T106-079 | cache por audiência não migra para público diferente. |
| T106-080 | origem do recibo não expõe fonte testemunhal no título. |
| T106-081 | descrição de prejuízo não revela localização de NPC protegido. |
| T106-082 | erro de autorização não retorna payload de acusações. |
| T106-083 | contagem de fontes não revela número de testemunhas sigilosas. |
| T106-084 | alteração de ACL invalida views de divulgação pendentes. |

### Tempo, espaço e conhecimento

| ID | Cenário candidato — NÃO EXECUTADO no jogo |
|---|---|
| T106-085 | calendário DR mantém precisão da fonte histórica. |
| T106-086 | modo PARTIAL só progride com tempo permitido. |
| T106-087 | modo REALTIME usa tick do mundo e não relógio de CPU para efeitos. |
| T106-088 | rumor local não chega a outra região por teleport narrativo. |
| T106-089 | conhecimento atrasado permite reabilitação atrasada e contextual. |
| T106-090 | mensagem de revisão não retroage conhecimento a data anterior. |
| T106-091 | notícia recebida por facção não comprova conhecimento de cada integrante. |
| T106-092 | ciclo anual canônico não cria reabilitação automática em outro ano. |
| T106-093 | região offscreen só progride sob orçamento e políticas válidas. |
| T106-094 | evento futuro não pode ser usado como dano passado. |
| T106-095 | mudança de local exige nova elegibilidade para retratação. |
| T106-096 | ramo restaurado não herda público alcançado de fork anterior. |

### Idempotência, replay e concorrência

| ID | Cenário candidato — NÃO EXECUTADO no jogo |
|---|---|
| T106-097 | mesma revisão do caso produz mesma chave sem depender do trace. |
| T106-098 | múltiplos pedidos simultâneos não geram múltiplos pagamentos. |
| T106-099 | CAS impede revisão de reputação stale. |
| T106-100 | fencing protege commit após troca de worker. |
| T106-101 | pedido já pendente retorna ALREADY_PLANNED. |
| T106-102 | caso já registrado retorna ALREADY_REGISTERED. |
| T106-103 | despacho UNCERTAIN não sofre repetição cega. |
| T106-104 | save/load preserva ledger sem reemissão automática. |
| T106-105 | fork de campanha não reutiliza recibo de outra linhagem. |
| T106-106 | mudança de epoch exige revalidação de reservas. |
| T106-107 | mudança de modpack exige novo fingerprint de capacidade. |
| T106-108 | nova correção legitimamente versionada gera possibilidade de nova análise. |

### Gates mecânicos e ownership

| ID | Cenário candidato — NÃO EXECUTADO no jogo |
|---|---|
| T106-109 | planejador não escreve valor de reputação nativo no host. |
| T106-110 | planejador não altera flags de quest original. |
| T106-111 | planejador não remove NPC ou revive personagem morto. |
| T106-112 | planejador não modifica romance ou party por recomposição social. |
| T106-113 | planejador não gera item ou moeda de restituição. |
| T106-114 | planejador não move recurso entre inventários sem Action Gateway. |
| T106-115 | compensação DEC-095 exige confirmação separada. |
| T106-116 | alto risco não autorizado bloqueia a proposta. |
| T106-117 | ownership de reputação desconhecido bloqueia alterações. |
| T106-118 | capability de engine não validada impede execução de alteração. |
| T106-119 | recibo de host não pode ser sintetizado pelo LLM. |
| T106-120 | nenhum dano narrativo autoriza sanção punitiva automática. |

### Resiliência e estados incompletos

| ID | Cenário candidato — NÃO EXECUTADO no jogo |
|---|---|
| T106-121 | prova ausente gera QUARANTINED e não presunção de veracidade. |
| T106-122 | identidade de sujeito inválida gera UNKNOWN ou QUARANTINED. |
| T106-123 | consentimento ausente gera DENIED. |
| T106-124 | índice de audiência parcial impede inferência global. |
| T106-125 | fonte de dano desconhecida exige prova adicional. |
| T106-126 | canal de retratação indisponível não entrega mensagem. |
| T106-127 | falha de verificador ACL produz negação segura. |
| T106-128 | receipt de entrega atrasado não cria crença instantânea. |
| T106-129 | cache com política desatualizada não atende audiência. |
| T106-130 | revisão de ledger errada não dispara plano. |
| T106-131 | dados estruturais incompletos não causam exceção não tratada. |
| T106-132 | alto custo de processamento pode adiar análise sem alterar reputação. |

### Integração com regras anteriores

| ID | Cenário candidato — NÃO EXECUTADO no jogo |
|---|---|
| T106-133 | DEC-030 mantém reputação contextual sem reset global. |
| T106-134 | DEC-064 preserva crenças falíveis no NPC. |
| T106-135 | DEC-075 exige autoria comprovada antes de responsabilização. |
| T106-136 | DEC-077/089 preservam independência de evidências. |
| T106-137 | DEC-078 protege devido processo antes de sanções. |
| T106-138 | DEC-081 trata reparação como procedimento próprio. |
| T106-139 | DEC-090 publica somente visão redigida do dossiê. |
| T106-140 | DEC-095 vincula compensação a Saga autorizada. |
| T106-141 | DEC-099 exige ownership de campo e capacidade da build. |
| T106-142 | DEC-104 mantém histórico de causas retificadas. |
| T106-143 | DEC-105 exige entregas e percepções independentes. |
| T106-144 | DEC-096/097 não produzem restauração automática de economia. |

### Segurança de mediação e condição de validação

| ID | Cenário candidato — NÃO EXECUTADO no jogo |
|---|---|
| T106-145 | publicação mediada não cria automaticamente retratação de PC ausente. |
| T106-146 | proposta de reconciliação não força perdão de testemunha. |
| T106-147 | origem do dano é independente da fonte que divulgou a correção. |
| T106-148 | nenhum teste sintético deste pacote equivale a integração BG2:EE/EEex ou multiplayer. |

## 11. Próxima decisão — DEC-107 (EM ABERTO)

**Direito de resposta e mediação de conflitos reputacionais.** A: retratação uniforme obrigatória para todos; B: LLM decide qual narrativa prevalece e quem deve se desculpar; **C recomendada:** direito de resposta e mediação voluntária com provas curadas, competência, canais e audiência legítimos, consentimento de PC/NPC, sigilo, devido processo, versionamento e recibos. Nenhuma fala forçada, memória apagada ou absolvição automaticamente disseminada.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de obrigações e monitoramento não coercitivo

Atraso alegado ou falta de prova não determina por si deterioração reputacional ou reparação. Fonte: ADR-0103/doc.108; claims ≠ comprovantes, prazos DR ≠ culpa, status `UNCERTAIN` bloqueia nova ação, sem mutações do host. POCs BG2:EE/EEex e T108-001..160 **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Reabilitação reputacional não decorre automaticamente de pacto cumprido. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
