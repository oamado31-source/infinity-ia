# 105 — Propagação causal de correções e evolução falível das crenças de NPCs

**Decisão:** DEC-105/C aprovada (ADR-0100); **versão:** Discovery v10.1, 2026-11-07. **Estado:** aprovado apenas como arquitetura; nenhum canal de NPC, memória ou host BG2:EE/EEex integrado. **Invariantes anteriores:** DEC-060..104 e ADR-0001..0099 preservados.

## 1. Problema, autoridade e escopo

Correção de alegação não equivale a mudança universal de conhecimento nem restauração de reputação. DEC-104 cria `CommittedRectificationProof`/proposta de errata e preserva as consequências. DEC-105 governa a **comunicação da versão corrigida**, sua eventual percepção e a **proposta** de reavaliação de crença pelo destinatário. DEC-029/074/090 regem as rotas e a difusão; DEC-064/065 regem memória e crença falível; DEC-089 rege independência de evidências. DEC-095/099 protegem efeitos mecânicos e ownership. A DEC-106 tratará separadamente reabilitação reputacional.

As entidades do host, as transmissões, os receipts, a intenção de um NPC, a prova curada e os estados da campanha **não compartilham autoridade de escrita**. Uma LLM local pode produzir diálogo já filtrado, jamais decisão sobre credibilidade factual, entrega, mudança mecânica, cognição de PC ou permissão.

## 2. Pipeline obrigatório

```text
TrustedRectificationRegistry.COMMITTED (DEC-104) + fonte e classificação
  -> AUTHENTICATE / PIN branch, lineage, epochs, KPack, policy, propósito
  -> RESOLVE destinatário persistente e público efetivo, sem confiar no requester
  -> ACL / PRIVACY / REDACTION ANTES de prompt, cache, índice, canal e log
  -> PLAN MESSAGE (correction_ref + view revision; sem enviar ainda)
  -> AUTHORIZE channel, origem, alcance, custo, mundo DR e sequência causal
  -> COMMIT OUTBOX (quando houver serviço implementado e aprovado)
  -> TRANSMIT -> PENDING / IN_TRANSIT / LOST / DISPATCHED / UNCERTAIN / DELIVERED
  -> VERIFY DELIVERY RECEIPT (destinatário, canal, tempo, conteúdo e branch)
  -> VERIFY PERCEPTION/UNDERSTANDING (se necessário à regra)
  -> BELIEF REVIEW PROPOSAL (evidência + confiança + interesses + histórico)
  -> EXTERNAL APPROVAL / BOUND NPC STATE WRITER -> BELIEF REVISION RECEIPT
```

A existência de uma prova `COMMITTED` **não gera transmissão espontânea**. Cada seta representa estágio e contrato com própria política. O código didático só implementa o planejamento final de revisão a partir de stores *sintéticos* autenticados pelo fixture; não transmite mensagens, não avança DR, não altera memória ou NPC.

## 3. Modelo de dados versionado (candidato)

| Tipo | Campos mínimos | Validação e limites |
|---|---|---|
| `CorrectionProof` | `id`, `prior_claim`, `new_revision`, `source_family`, `grade`, `committed_at_dr`, `classification`, `privacy`, `lineage` | Referência autenticada ao DEC-104, não criada por prompt/requisição |
| `CorrectionContentView` | `envelope_id`, `proof_ref`, `audience`, `redaction_policy`, `content_hash`, `visibility` | Hash e IDs não podem expor identidade, autoria sigilosa ou corpo privado |
| `TrustedRecipientIdentity` | `persistent_npc_id`, `pseudonyms`, `faction_memberships`, `clearance`, `presence`, `permissions` | Autoridade por destinatário real, nunca por nome ou grupo textual |
| `CommunicationRoute` | `sender`, `channel`, `geographical_nodes`, `availability`, `time_cost_dr`, `limits`, `resources` | Não inventar viagem instantânea; exigir canais/capabilities verificáveis |
| `Transmission` | `envelope_ref`, `delivery_id`, `status`, `hops`, `sent_at_dr`, `recipient`, `fencing_key` | Retries limitados, dedup persistente, `UNCERTAIN` requer reconciliação |
| `DeliveryProof` | `delivery_ref`, `recipient_persistent_id`, `received_at_dr`, `receipt_kind`, `coverage`, `origin` | Diferencia entrega de recepção perceptiva e entendimento |
| `BeliefSnapshot` | `actor_id`, `prior_claim`, `belief_state`, `last_revision`, `evidence_refs`, `personal_context_ref`, `revision` | Memória histórica imutável; crença pode ser contraditória e falível |
| `BeliefReviewProposal` | `proposal_key`, `correction_ref`, `recipient`, `new_evidence`, `review_kind`, `cas_revision`, `risk` | Proposal only; não concede direito de reescrever memória |
| `BeliefRevisionReceipt` | `review_ref`, `authorized_actor`, `commit_time`, `prior_state`, `new_state`, `reasons`, `branch_epoch` | Só existe após aprovação e commit em serviço separado |

### Estados e semântica

- Mensagem: `DRAFT → AUTHORIZED → QUEUED → IN_TRANSIT → DELIVERED` ou `LOST / CANCELLED`; `DISPATCHED/UNCERTAIN` requer reconciliação. **Transmissão ≠ entrega**.
- Conhecimento: `NOT_HEARD → HEARD_PARTIAL/HEARD_CORRECTION` mediante percepção legítima; **entrega ≠ compreensão**.
- Crença: `BELIEVES_PRIOR`, `DOUBTS_PRIOR`, `CONTESTING`, `RECONSIDERING`, `BELIEVES_CORRECTION`, `UNCERTAIN`. **Compreensão ≠ aceitação**. Um destinatário pode manter crenças parcialmente contraditórias; não impor uma variável booleana única de verdade.
- Avaliação de evidência: `UNVERIFIED`, `CONTESTED`, `PARTIAL`, `CORROBORATED` com **famílias de proveniência**; três repetições derivadas de A continuam sendo uma família e não três confirmações independentes.
- `WorldFact` e `HostReceipt` não são alterados por receber errata, nem pelo surgimento de opinião em NPC.

## 4. Regras condicionais e confiança

```text
IF correction.status != COMMITTED: QUARANTINE
ELSE IF branch/lineage/epoch/policy/provenance invalid: QUARANTINE
ELSE IF audience/purpose/classification/actor not authorized: DENY
ELSE IF channel invalid or route/time not satisfied: DO NOT DELIVER
ELSE IF transmission UNCONFIRMED: DO NOT ASSUME KNOWLEDGE
ELSE IF delivery confirmed BUT perception not proved: DO NOT ASSUME UNDERSTANDING
ELSE IF evidence contested: propose HOLD_DISPUTED_CLAIM
ELSE IF prior claim never heard: propose RECORD_CORRECTION_AS_NEW_INFORMATION
ELSE IF evidence partial: propose PARTIAL_RECONSIDERATION
ELSE IF source confidence low: propose CONTESTED_REVIEW
ELSE propose EVIDENCE_BASED_RECONSIDERATION
NEVER auto-commit new belief, never alter PC consent, never send for free
```

`source_confidence` e `evidence_grade` devem vir de registros curados, não de campos da requisição. Não há taxa de crença, algoritmo de persuasão ou reputação implementado: as categorias são candidatas e as políticas de transição precisarão de SPECS e testes de comportamento ético/narrativo.

### Exemplo ilustrativo de NPCs divergentes

| NPC fictício | Corrigenda recebida? | Confiança e evidências | Resultado permitido |
|---|---|---|---|
| Mercador A | Sim, com percepção comprovada | Fonte confiável, prova corroborada | Propor reconsideração; não aceitar automaticamente |
| Mercador B | Sim, com percepção comprovada | Origem duvidosa, alegações conflitantes | Propor contestação ou investigação adicional |
| Mercador C | Não | Não aplicável | Não alterar memória nem crença |
| Mercador D | Entrega no canal, sem percepção comprovada | Não aplicável | `DELIVERY_NOT_CONFIRMED` para atualização cognitiva |

## 5. Temporalidade e geografia

- Vincular emissões à cronologia `DR` e à precisão da fonte. `FROZEN/PARTIAL/REALTIME` da DEC-022 rege avanço; não assumir relógio externo. Eventual `time_cost` deve derivar de rota e canal autorizados com recursos, presença e disponibilidade (DEC-069).
- Áreas offscreen (DEC-021/068) admitem avanço agregado **somente conforme políticas ativas**; não materializar uma conversa nem criar recepção sem evidência e capability. Eventos canônicos no passado não equivalem a rumor contemporâneo global.
- Envio posterior ao período de validade pode gerar notícia defasada, mas **não confirma** o efeito que ela descreve. Nunca reenviar para outros anos ou ramos por fallback de cache.

## 6. Privacidade e fluxo de dados

ACLs distintas para (i) prova, (ii) conteúdo da errata, (iii) destinatário, (iv) canal, (v) revisão de crença, (vi) eventual consequência social. IDs públicos opacos e views específicas evitam revelar conteúdo lateralmente; negar acesso antes de criar embeddings, prompt ou logs. Filtrar inclusive metadados de localização, quantidade de testemunhas e grafos de origem. Segredos de proteção DEC-083–085 e identidades DEC-076 têm prioridade sobre divulgação narrativa.

As fontes e registros confiáveis ficam separados da requisição; autenticação, consentimento e permissões **não podem ser declarados pelo próprio cliente**. O único `request` permitido aponta a correção e a finalidade; o executor obtém o restante dos stores autenticados. Preservar LGPD por projeto, embora nenhum dado real seja incluído nas fixtures.

## 7. Idempotência, concorrência e save/load

```text
correction_delivery_case_key = H(campaign, branch, lineage, epochs,
                                 committed_correction_revision, recipient_persistent_id,
                                 actual_delivery_id, authorized_policy_revision)
belief_review_key = H(correction_delivery_case_key, pinned_belief_snapshot_revision)
```

- Uma mensagem retransmitida pelo mesmo canal e com a mesma revisão não cria automaticamente outro fato de percepção ou revisão de crença.
- Diferentes destinatários criam revisões independentes; novas correções committed criam novas chaves e continuam relacionadas à original.
- `CAS` e outbox transacional com fencing protegem contra replay em multiplayer e após crash. Deduplicação não impede nova evidência legítima nem nova revisão explicitamente versionada.
- `DISPATCHED` e `UNCERTAIN` impedem resend cego; período de expiração não prova entrega ou perda. Em restore de save/branch fork, índices e recibos ficam presos à lineage correta.
- É proibido reemitir o rumor antigo somente para “corrigi-lo” se isso violar ACL/privacidade. O destinatário que nunca o ouviu recebe no máximo informação nova autorizada.

## 8. Efeitos, compensação e reputação

DEC-104 determina a contenção da causa e DEC-105 a difusão da correção; nenhuma dessas decisões desfaz por si só condenação, sanção, perda comercial, morte, inventário ou mudança mecânica já confirmada. Reparação e reabilitação exigem política DEC-078/081/095 e, se mecânica, Action Gateway/host. O estado epistêmico do NPC pode alimentar uma **proposta** social sem decidir reputação BG2:EE. A DEC-106 separará o tratamento específico do dano reputacional.

## 9. Segurança e cenários de falha

1. **Spoiler por corpo/ID:** potencial de revelar nomes de quest flags, fontes secretas, testemunhas e refúgios; ACL/redação e hash opaco antes do prompt.
2. **Falso conhecimento:** `SENT`, `DELIVERED` sem percepção e rumor indireto não comprovam entendimento nem concordância.
3. **Convergência forçada:** crença não é variável global; NPC pode duvidar ou contestar legitimamente.
4. **Proveniência falsa:** eco de rumor não aumenta suporte independente; revisão de evidências versionada e source family.
5. **Restauração/fork:** erro de branch ou epoch gera quarentena.
6. **Duplicação:** revisão/receipt idempotente por destinatário, event/revision e ledger CAS.
7. **Privacidade:** sem fan-out global, leak de alcance, metadados, caches, logs, embeddings ou contexto LLM.
8. **Falta de capacidade técnica:** nenhuma ação no motor sem POC específica para build/EEex e testes host+2 clientes.

## 10. Código e esquema didáticos

- `examples/chronology/correction_diffusion_reference.py` implementa exclusivamente uma **proposta pura**. `host_calls=0`, `engine_writes=0`, `deliveries_sent=0`, `npc_memories_changed=0`, `npc_beliefs_committed=0` e `ledger_mutated=False` são garantias da função de teste, **não evidência sobre host real**.
- `examples/chronology/correction_diffusion_v1.synthetic.json`: registros inteiramente fictícios, todos prefixados `SYN-`.
- `examples/chronology/correction_diffusion_v1.candidate.schema.json`: valida o envelope de fixture sintética e tipa limites. **Não é API do jogo**.
- `examples/chronology/test_correction_diffusion_reference.py`: testes unitários negativos e positivos, sem IA, rede, EEex ou save.

## 11. Critérios para futura SPEC/POC

| Gate | Evidência exigida |
|---|---|
| G105-01 | Prova committed/assinada de DEC-104, leitura independente de registry, ausência de self-grant |
| G105-02 | Catálogo de canais realmente existentes e suas latências, posição e recursos |
| G105-03 | ACL/redaction por destinatário, escopo, privacidade e histórico de pseudônimos |
| G105-04 | Entrega/percepção comprovadas com receipts distintos de aceite de crença |
| G105-05 | Políticas determinísticas NPC, aceitação não garantida e respeito a PCs ausentes |
| G105-06 | Dedup/CAS/outbox e reconciliação de mensagens incertas em host + 2 clientes |
| G105-07 | Simulação de tempo DR (`FROZEN/PARTIAL/REALTIME`) e regiões offscreen |
| G105-08 | Preservação de crenças anteriores em restore, fork e nova correção de correção |
| G105-09 | Prova de nenhum vazamento por logs/LLM/cache/IDs e nenhum host write ilegítimo |

## 12. Matriz de testes candidatos

**T105-001..T105-144: todos são CANDIDATOS NÃO EXECUTADOS no BG2:EE/EEex/bridge, host+2 clientes.** Podem ser planejados como POCs futuras. A cobertura de unit tests sintéticos é reportada separadamente e não atende esses gates.


### Prova e proveniência

| ID | Cenário candidato de integração — NÃO EXECUTADO |
|---|---|
| T105-001 | prova de retificação committed com origem DEC-104 autenticada. |
| T105-002 | prova ainda em DRAFT impede preparo de envio. |
| T105-003 | proof revogado não reativa correção antiga. |
| T105-004 | contradição entre versões committed exige revisão curada. |
| T105-005 | fonte de baixa credibilidade não transforma boato em fato. |
| T105-006 | dois relatos derivados de uma mesma testemunha contam como uma origem. |
| T105-007 | evidência nova independente permite nova revisão sem apagar a anterior. |
| T105-008 | correção de correção mantém DAG temporal sem ciclos. |
| T105-009 | prova com origem ausente permanece em quarentena. |
| T105-010 | referência de prova não permite acessar texto original protegido. |
| T105-011 | credibilidade não é declarada por request nem por LLM. |
| T105-012 | proveniência inconsistente gera resposta segura sem divulgação. |

### ACL, identidades e sigilo

| ID | Cenário candidato de integração — NÃO EXECUTADO |
|---|---|
| T105-013 | destinatário público não recebe errata PROTECTED. |
| T105-014 | NPC protegido recebe somente view explicitamente autorizada. |
| T105-015 | identidade de testemunha não aparece em título ou ID público. |
| T105-016 | pseudônimo não confere permissão de acesso à identidade verdadeira. |
| T105-017 | lista de membros de facção não é concessão automática de ACL. |
| T105-018 | propósito diverso do autorizado nega acesso. |
| T105-019 | actor não autenticado não consegue self-grant. |
| T105-020 | cópia em cache não migra entre audiências. |
| T105-021 | LLM recebe somente envelope filtrado. |
| T105-022 | logs e métricas não revelam número de testemunhas ou local de abrigo. |
| T105-023 | comunicação parcial omite metadados privados de fontes. |
| T105-024 | alteração do consentimento/ACL exige revalidação antes do envio. |

### Canais, presença e alcance

| ID | Cenário candidato de integração — NÃO EXECUTADO |
|---|---|
| T105-025 | mensageiro deve existir e ter recurso de viagem disponível. |
| T105-026 | rota bloqueada impede confirmar entrega. |
| T105-027 | canal social indisponível mantém envio pendente. |
| T105-028 | destinatário ausente impede encontro físico automático. |
| T105-029 | origem e destino exigem geografia válida. |
| T105-030 | entrega por facção não comprova recepção de cada integrante. |
| T105-031 | limite de hops bloqueia cadeia social excessiva. |
| T105-032 | custo de transporte não é gerado gratuitamente. |
| T105-033 | mensagem perdida não converte NPC em conhecedor. |
| T105-034 | canal não testado para build permanece indisponível. |
| T105-035 | comunicação possível em área offscreen respeita simulação autorizada. |
| T105-036 | envio sem emissor legítimo não é confirmado. |

### Tempo DR e calendários

| ID | Cenário candidato de integração — NÃO EXECUTADO |
|---|---|
| T105-037 | modo FROZEN não avança relógio DR automaticamente. |
| T105-038 | modo PARTIAL aplica apenas avanço de tempo autorizado. |
| T105-039 | modo REALTIME exige tick de mundo válido, não tempo de CPU. |
| T105-040 | arrival antes do dispatch é rejeitado. |
| T105-041 | despacho anterior ao committed proof é rejeitado. |
| T105-042 | boato recebido anos depois permanece informação histórica datada. |
| T105-043 | janela temporal com mês desconhecido não cria data fictícia. |
| T105-044 | envio futuro em tick atual é rejeitado. |
| T105-045 | mensagem fora da janela exige nova política, não teleport. |
| T105-046 | recebimento após fork não é herdado implicitamente. |
| T105-047 | delay estimado não equivale a receipt de recebimento. |
| T105-048 | eventos cronológicos oficiais não se difundem universalmente no mesmo tick. |

### Envio e recibos

| ID | Cenário candidato de integração — NÃO EXECUTADO |
|---|---|
| T105-049 | QUEUED não prova entrega. |
| T105-050 | IN_TRANSIT não prova entrega. |
| T105-051 | LOST mantém ausência de conhecimento novo. |
| T105-052 | UNCERTAIN bloqueia retry cego. |
| T105-053 | DISPATCHED exige reconciliação antes de dedup. |
| T105-054 | DELIVERED para outro destinatário não é válido. |
| T105-055 | receipt de revisão errada não autoriza atualização. |
| T105-056 | receipt sem origem autenticada é rejeitado. |
| T105-057 | receipt de data posterior ao tick atual é rejeitado. |
| T105-058 | envio cancelado não cria conhecimento. |
| T105-059 | outbox pós-crash reconcilia sem duplicar recebimentos. |
| T105-060 | receipt idempotente preserva entrega anterior após save/load. |

### Percepção e entendimento

| ID | Cenário candidato de integração — NÃO EXECUTADO |
|---|---|
| T105-061 | entrega em caixa postal não confirma leitura. |
| T105-062 | npc inconsciente não percebe mensagem automaticamente. |
| T105-063 | receipt de percepção parcial não equivale a aceitação total. |
| T105-064 | recebimento em idioma desconhecido não garante compreensão. |
| T105-065 | mensagem com visão redigida não permite inferir conteúdo removido. |
| T105-066 | NPC percebe somente conteúdo disponibilizado no canal. |
| T105-067 | percepção contestada permanece UNKNOWN. |
| T105-068 | fala ouvida por múltiplos NPCs exige alcance/percepção individual. |
| T105-069 | conversa interrompida não prova mensagem completa. |
| T105-070 | eco por informante não equivale a percepção direta da fonte original. |
| T105-071 | inferência sobre ausência de resposta não é prova de descrença. |
| T105-072 | aceitação da retificação só pode vir de revisão epistêmica separada. |

### Memória, crença e agência

| ID | Cenário candidato de integração — NÃO EXECUTADO |
|---|---|
| T105-073 | NPC pode manter crença anterior após ouvir correção. |
| T105-074 | NPC pode questionar versão antiga sem aceitar plenamente a nova. |
| T105-075 | NPC que nunca ouviu rumor antigo não ganha memória retroativa dele. |
| T105-076 | conhecimento factual não modifica opinião pessoal automaticamente. |
| T105-077 | história de crenças permanece imutável e versionada. |
| T105-078 | perfil de confiança curado, não inferido de prompt. |
| T105-079 | crença contraditória pode coexistir quando evidências são insuficientes. |
| T105-080 | NPC altamente confiante na fonte pode reavaliar, não obrigatoriamente aceitar. |
| T105-081 | NPC leal a facção pode contestar a correção sem alterar fatos. |
| T105-082 | decisão de crença de PC requer jogador titular. |
| T105-083 | ausência de controlador de PC não concede autonomia a LLM. |
| T105-084 | memória NPC não é apagada ao sair da área. |

### Evidências e independência

| ID | Cenário candidato de integração — NÃO EXECUTADO |
|---|---|
| T105-085 | fonte A repetida por B e C não vira três confirmações. |
| T105-086 | prova parcial gera apenas reconsideração parcial. |
| T105-087 | prova contestada não produz aceitação automática. |
| T105-088 | prova sem origem permanece em quarentena. |
| T105-089 | correção baseada em rumor não autenticado é bloqueada. |
| T105-090 | duas fontes independentes contraditórias mantêm incerteza. |
| T105-091 | contexto de fonte desatualizado não assegura confiança atual. |
| T105-092 | correção válida pode não alterar reputação estabelecida. |
| T105-093 | conteúdo manipulado por agente duplo exige ledger de autoria. |
| T105-094 | LLM não classifica verdade sem fonte curada. |
| T105-095 | mudança de confiança requer revisão contextual explícita. |
| T105-096 | novos fatos não apagam registro de depoimentos anteriores. |

### Idempotência e concorrência

| ID | Cenário candidato de integração — NÃO EXECUTADO |
|---|---|
| T105-097 | dois pedidos idênticos geram uma proposta lógica. |
| T105-098 | mesma entrega com diferente trace ID mantém chave idêntica. |
| T105-099 | nova revisão committed gera chave independente. |
| T105-100 | dois destinatários produzem chaves diferentes. |
| T105-101 | envio repetido no multiplayer não duplica crença. |
| T105-102 | CAS detecta revisão antiga da memória. |
| T105-103 | fencing impede commit de worker abandonado. |
| T105-104 | mensagem UNCERTAIN não libera reserva de mensageiro. |
| T105-105 | cancelamento aplica somente a envios futuros elegíveis. |
| T105-106 | outbox transacional recupera após crash. |
| T105-107 | ordem de processamento dos destinatários não muda decisões isoladas. |
| T105-108 | reentrada em área não força retransmissão da mesma errata. |

### Ramos, saves e persistência

| ID | Cenário candidato de integração — NÃO EXECUTADO |
|---|---|
| T105-109 | prova de outro branch não entra no contexto atual. |
| T105-110 | receipt de outra lineage não confirma mensagem. |
| T105-111 | mudança de host epoch invalida credencial anterior. |
| T105-112 | checkpoint divergente exige reconciliação. |
| T105-113 | Knowledge Pack pinado não aceita lore de outro ano DR sem curadoria. |
| T105-114 | restore de save não apaga fato de NPC ter conhecido notícia em ramo antigo. |
| T105-115 | mas ramo restaurado não herda conhecimento sem política de merge. |
| T105-116 | migração de modpack exige recertificação de canal e observação. |
| T105-117 | identidade persistente difere da instância engine. |
| T105-118 | posição offscreen não simula diálogo local sem capacidade. |
| T105-119 | stale cache de ramo errado é recusado. |
| T105-120 | comparação de mundos não confunde relógio real e DR. |

### Efeitos de jogo e limites de autoridade

| ID | Cenário candidato de integração — NÃO EXECUTADO |
|---|---|
| T105-121 | revisão de crença não altera reputação BG2:EE por conta própria. |
| T105-122 | resposta não edita flag de quest original. |
| T105-123 | receber correção não desfaz pagamento confirmado. |
| T105-124 | correção não remove sanção jurídica automaticamente. |
| T105-125 | alteração de relação NPC relevante exige política e gates. |
| T105-126 | não criar guardas, mensageiros ou facções inexistentes. |
| T105-127 | nenhuma compensação mecânica sem Saga autorizada. |
| T105-128 | nenhuma ação host sem capability testada. |
| T105-129 | ação HIGH exige autorização especial. |
| T105-130 | não alterar inventário pertencente a PC. |
| T105-131 | não forçar personalidade de companion canônico. |
| T105-132 | LLM só redige versão permitida, sem escolher destinatários. |

### Resiliência e observabilidade segura

| ID | Cenário candidato de integração — NÃO EXECUTADO |
|---|---|
| T105-133 | mensagem cifrada impossível de ler não é interpretada livremente. |
| T105-134 | falha de rede local mantém entrega pendente. |
| T105-135 | falha de serviço de ACL bloqueia acesso. |
| T105-136 | grafo causal incompleto não autoriza fanout. |
| T105-137 | limite de destinatários impede explosão de mensagens. |
| T105-138 | métrica agregada não vaza identidade de fonte. |
| T105-139 | erro de parse não transforma estado desconhecido em confirmado. |
| T105-140 | cache invalida após mudança de audience ou policy. |
| T105-141 | correção assinada em data futura é colocada em quarentena. |
| T105-142 | injeção textual em rumor não vira instrução para LLM. |
| T105-143 | arquivo de fixture sintética nunca aciona host real. |
| T105-144 | falha durante save/load preserva idempotência e histórico. |

## 13. Próxima decisão em aberto — DEC-106

**Reabilitação reputacional proporcional após retificações públicas.** A: restauração automática; B: LLM determina resultados; **C recomendada:** reclamação/prova, alcance real da acusação e da correção, danos, regras sociais e jurídicas, consentimento/ownership, capacidade, reparação opcional e recibos do host — sem fixação artificial de opiniões. Revisar sem sobrepor DEC-030/078/081/089/104/105.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para difusão da correção não é recuperação de confiança ou reputação, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de obrigações e monitoramento não coercitivo

Aviso de obrigação vencida é mensagem sujeita a entrega e percepção próprias, sem publicidade irrestrita. Fonte: ADR-0103/doc.108; claims ≠ comprovantes, prazos DR ≠ culpa, status `UNCERTAIN` bloqueia nova ação, sem mutações do host. POCs BG2:EE/EEex e T108-001..160 **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Notificação de condição satisfeita não significa recebimento por NPC. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
