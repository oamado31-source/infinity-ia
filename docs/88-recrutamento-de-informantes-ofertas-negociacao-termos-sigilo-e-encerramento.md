# DEC-088 — Recrutamento de informantes: propostas, negociação, termos, sigilo e encerramento

**Infinity AI Discovery v8.4 · ADR-0083 · Opção C APROVADA COMO ARQUITETURA · NÃO IMPLEMENTADA.**  
**82 testes candidatos T088-01..T088-82 — TODOS NÃO EXECUTADOS.**

## 1. Objetivo, fronteiras e não objetivos

Dar suporte arquitetural a **abordar, negociar, recusar, pactuar, suspender e encerrar** colaboração informativa voluntária de NPCs, respeitando valores, identidade, recursos e autoridade. Exigir lastro factual antes de tratar um informe como entregue e **não confundir verdade de conteúdo com existência do contrato**.

Fora do escopo nesta DEC: veredito de veracidade/credibilidade do informe (DEC-089), corrupção institucional (DEC-082), transporte físico de fontes (DEC-084), detecção mecânica de espiões, NPC novo em party, comércio de itens não verificado e qualquer script/hook BG2:EE sem POC.

## 2. Fonte de verdade e isolamento físico

```text
knowledge/periods/<ANO>-DR/                   # fatos canônicos anuais curados, DEC-060 a 063
campaign-overlays/<campaign>/<branch>/       # DESENHO LÓGICO candidato, não caminho implantado
    identities/                              # identidade persistente DEC-066 / personas DEC-076
    loyalties/                               # deveres, conflitos, vínculos privados DEC-087
    contact-opportunities/                   # oportunidades realmente verificadas
    informant-proposals/                     # propostas sem compromisso criado
    negotiations/                            # turnos e contrapropostas auditáveis
    informant-agreements/                    # contratos narrativos, ACL e revisões
    reservations-and-receipts/               # recursos finitos e host confirmations
    deliveries/                              # informes recebidos e seus estados epistêmicos
    observer-beliefs/                        # percepções dos NPCs e facções
    terminations-and-audit/                  # saída, revogação, checkpoints, efeitos
```

**Nunca** inserir os segredos, contratos ou relatórios de uma campanha nos diretórios canônicos por ano DR. Anos futuros não devem ser consultados para dar informações retroativas a informantes. Knowledge Pack pinado por ramo permanece a fonte canônica válida para fatos históricos.

## 3. Contratos de dados candidatos (não implementados)

```text
ContactOpportunity {
  campaign_id, branch_id, contact_id, candidate_npc_identity_id,
  verified_encounter_or_channel_ref, time_dr, locality, source_event_id,
  required_permissions, eligibility_state, evidence_refs, checkpoint_epoch
}
RecruitmentProposal {
  proposal_id, contact_id, proposer_actor_id, target_npc_identity_id,
  requested_information_scope, offered_terms[], intended_audience,
  privacy_class, expiry_dr, risk_tier, consent_policy_ref,
  state: DRAFT|OFFERED|COUNTERED|WITHDRAWN|DECLINED|EXPIRED|PENDING,
  proposal_revision, authorizing_actor_id, source_event_id
}
NegotiationTurn {
  negotiation_event_id, proposal_id, speaker_identity_ref,
  authorized_controller_ref?, utterance_or_term_delta, response_type,
  offered_resource_refs[], time_dr, provenance, model_proposal_ref?,
  applied_rules_revision, consent_evidence_ref?, checkpoint_epoch
}
InformantAgreement {
  agreement_id, proposal_id, source_npc_identity_id, beneficiary_refs[],
  scope_permissions[], allowed_topics[], prohibited_disclosures[],
  communication_channels[], valid_from_dr, valid_until_dr?,
  compensation_terms[], protection_requests[], cancellation_rules[],
  source_consent_ref, beneficiary_authorization_ref,
  signed_under_rule_revision, confidentiality_acl, state,
  agreement_revision, causal_event_refs[], checkpoint_epoch
}
CommitmentTerm {
  commitment_id, agreement_id, obligation_actor_id, kind,
  deliverable_description, performance_evidence_rule, due_dr?,
  cost_reservation_ref?, privacy_acl, prerequisites[], state, revision
}
ResourceReservation {
  reservation_id, agreement_id, owner_actor_or_faction_ref,
  resource_type, resource_ref?, quantity, claim_or_inventory_proof,
  conditional_milestone_ref?, expiry_dr, gateway_action_ref?,
  host_receipt_id?, state: PROPOSED|RESERVED|COMMITTED|REJECTED|UNCERTAIN,
  idempotency_key, checkpoint_epoch
}
InformationPromise {
  promise_id, agreement_id, promised_topic, known_scope_claim,
  source_knowledge_refs[], due_dr?, evidence_status, state, revision
}
DeliveryEvidence {
  delivery_id, agreement_id, deliverer_actor_ref, observed_message_or_item_ref,
  delivered_at_dr, recipient_scope, contents_acl, evidence_refs[],
  content_truth_status: UNVERIFIED|ALLEGED|CORROBORATED|CONTRADICTED|UNKNOWN,
  validation_policy_ref?, receipt_ref?, causal_event_id, revision
}
TerminationEvent {
  termination_id, agreement_id, initiator_identity_ref, reason,
  authorization_ref, terms_revision, terminated_at_dr,
  outstanding_deliveries[], outstanding_compensations[],
  state, causal_event_ref, checkpoint_epoch
}
```

Campos, enums e nomes de diretórios são **candidatos ao desenho de SPECS**, não banco de dados implantado. `ConsentEvidence` não é um texto livre que LLM possa fabricar. Nomes de NPC e aliases não são chaves de identidade.

## 4. Modelo de etapas e autoridade

```text
Contato validado
  -> proposta (DRAFT/OFFERED)
  -> [recusa/expiração/retirada] OU negociação (COUNTERED/PENDING)
  -> aceite autorizado e voluntário -> acordo ACTIVE
  -> tarefa específica e possível promessa de informe
  -> registro separado de ENTREGA, se realmente ocorrida
  -> [renegociação / suspensão / expiração / rescisão / cumprimento]
  -> fechamento auditável sem apagamento de fatos passados
```

- Toda transição consulta fatos, políticas, estado do NPC e regras determinísticas antes de recorrer à LLM local.
- `PENDING` é resultado legítimo; não existe obrigação de resolver toda negociação imediatamente.
- Uma oferta feita por PC precisa de intenção validada do jogador titular ou delegação expressamente autorizada.
- `ACTIVE` certifica os termos narrativos, **não** que o NPC conhece os dados, que o pagamento ocorreu ou que a engine alterou algo.
- Informação fornecida pode ser incorreta ou inventada **dentro da ficção**, mas a IA não deve afirmar que dado sem prova é verdade factual.

## 5. Elegibilidade e motivação do NPC

Entradas candidatas: `npc_identity_id` verificada DEC-066, motivações/âncoras canônicas ou fatos do overlay, `LoyaltyBond` DEC-087, objetivos atuais, obrigações, risco da tarefa, disponibilidade, alcance geográfico e canal válido. Sem identidade/posição verificáveis ou sem recursos, a proposta pode permanecer pendente/indisponível. A LLM **não pode criar fome, dívida, luto, histórico ou acesso a segredo** para forçar uma negociação.

Uma aproximação narrativa poderá ser descrita se existir oportunidade. Não se assume que todo NPC tenha diálogo dinâmico em BG2:EE. Companheiros canônicos mantêm limites de romances, quests e ações nativas DEC-047–050.

## 6. Termos do acordo e segurança contratual

Um acordo deve delimitar: escopo de informações, pessoas autorizadas a solicitá-las e recebê-las, canais de contato, obrigações de cada parte, prazo, condições de término, riscos relevantes, termos de pagamento e proteção eventualmente solicitada. O sistema distingue:

1. **Promessa:** obrigação ainda não cumprida (ou alegação não verificada).
2. **Reserva de recurso:** intenção com saldo/asset possível, não transferência concluída.
3. **Cumprimento narrativo:** acontecimento confirmado no log e conhecimento permitido.
4. **Cumprimento mecânico:** somente ação tipada do gateway e recibo do host, quando o build permitir.

Não criar contrato unilateral de NPC ou PC por silêncio, fala improvisada, intimidação não consentida ou disponibilidade ilusória. Encerramento não revoga retroativamente divulgação realmente ocorrida; pode restringir divulgações futuras.

## 7. Informação, entregas e avaliação futura

Exemplo: informante promete relatar o horário de uma reunião. O acordo não concede ao NPC acesso ao relógio do evento se ele não tem canal para conhecê-lo. Após um fato de entrega verificado, registrar `DeliveryEvidence` com cadeia de origem, destinatário, horário DR e marca `UNVERIFIED` quando a veracidade do conteúdo não foi provada. Verificação de fontes independentes, contradições e reputação de confiabilidade será tratada pela DEC-089. DEC-077 rege a investigação dos vínculos e provas, preservando separação entre indício e fato.

Ao receber um informe, jogadores não podem adquirir automaticamente conhecimento de NPCs distantes que não participaram da entrega; vice-versa, a guilda não obtém conhecimento do contato por acesso a registros de auditoria privados.

## 8. Economia, remuneração e antibloqueio

- Saldo/asset de ouro, item ou serviço validado conforme domínio real; oferecer algo não gera o bem.
- Limites configuráveis de capacidade por fonte, tempo, tipo de informe, campanha/ramo e budgets; proposta repetida ou persona alternativa não duplica recursos.
- Gasto/recompensa `MEDIUM/HIGH` ou em engine usa host Gateway DEC-011/012 com idempotency key, recepção e reconciliação.
- Ajuda, abrigo e escolta dependem de DEC-084–085; acordo não instancia guardas e não teleporta NPC.
- A economia DEC-032 não deve ser contornada por diálogo, pagamento fantasma ou duplicação de itens/XP.

## 9. ACL, segredos, co-op, IA e LAN

| Agente / contexto | Pode saber/produzir |
|---|---|
| Host/auditoria autorizados | Vínculo factual, escopos e receipts necessários sob ACL, **sem tornar NPC onisciente**. |
| NPC informante | Termos que recebeu legitimamente, conhecimento próprio e informações difundidas ao NPC. |
| NPC de outra facção | Somente contato/acordo/delivery que descobriu por meio causal verificável. |
| Titular de PC contratante | Próprias ofertas/aceites; não lê automaticamente segredo de outro PC. |
| PC ausente/delegado | Sem autorização implícita para pacto, pagamento, revelação ou mudança de facção. |
| LLM local | Apenas contexto minimizado; saída proposta, sempre validada por regras e ACL. |
| Worker LAN | Escopo do papel e job/epoch autorizado; nenhum compartilhamento de acordos por pareamento simples. |
| Logs/RAG/embeddings | IDs e conteúdo minimizado/segregado por finalidade, sem metadados reveladores desnecessários. |

## 10. Concorrência, saves, temporalidade e falhas

| Evento de falha | Comportamento seguro |
|---|---|
| Perda de resposta NPC | Manter OFFERED/PENDING sem presumir aceite. |
| Modelo retorna acordo inventado | Rejeitar, preservar estado factual anterior. |
| Duplicidade de clique ou retry | Deduplicar por proposal/agreement/revision/idempotency key. |
| Pagamento UNKNOWN/UNCERTAIN | Não executar segundo débito; reconciliar recibo real. |
| Checkpoint restaurado | Invalidar proposals/receipts de epoch futura; manter branch isolado. |
| Source NPC retorna de DORMANT | Catch-up baseado em eventos alcançáveis, sem decisões retroativas inventadas. |
| Identidade NPC não reconciliada | Suspender contrato/entrega, não associar novo NPC por nome. |
| Conhecimento futuro DR indevido | Bloquear retrieval e marcar inconsistência. |
| Campo de segredo não autorizado | Cortar antes de RAG/LLM/UI, registrar recusa segura. |
| Termo contraditório ou impossível | Solicitar renegociação narrativamente; não criar recurso automático. |

## 11. Matriz de testes candidatos — TODOS NÃO EXECUTADOS

Os resultados abaixo são **critérios desejados de SPECS**, não evidências empíricas de funcionamento.

| ID | Grupo | Cenário de aceitação candidato | Situação |
|---|---|---|---|
| T088-01 | Elegibilidade e autonomia | NPC sem identidade lógica DEC-066 não se torna fonte comprovada por nome. | **NÃO EXECUTADO** |
| T088-02 | Elegibilidade e autonomia | NPC insatisfeito pode recusar oferta sem obrigação de sucesso. | **NÃO EXECUTADO** |
| T088-03 | Elegibilidade e autonomia | Oferta generosa não altera lealdade automaticamente. | **NÃO EXECUTADO** |
| T088-04 | Elegibilidade e autonomia | NPC comprometido com duas facções não é declarado traidor sem prova. | **NÃO EXECUTADO** |
| T088-05 | Elegibilidade e autonomia | NPC canônico preserva limites de história, romance e scripts nativos. | **NÃO EXECUTADO** |
| T088-06 | Elegibilidade e autonomia | NPC DORMANT sem canal válido não negocia remotamente em tempo real. | **NÃO EXECUTADO** |
| T088-07 | Elegibilidade e autonomia | NPC inacessível por geografia/tempo permanece UNAVAILABLE, sem teleporte. | **NÃO EXECUTADO** |
| T088-08 | Elegibilidade e autonomia | NPC não é convertido em companion por firmar acordo de informante. | **NÃO EXECUTADO** |
| T088-09 | Elegibilidade e autonomia | A proposta de terceiro não gera compromisso em nome do NPC. | **NÃO EXECUTADO** |
| T088-10 | Elegibilidade e autonomia | Retirada da proposta permite que NPC conserve lembrança do contato ocorrido. | **NÃO EXECUTADO** |
| T088-11 | Agência de jogadores, consentimento e delegação | PC não aceita ser informante sem decisão do titular. | **NÃO EXECUTADO** |
| T088-12 | Agência de jogadores, consentimento e delegação | PC ausente não confessa nem promete segredo automaticamente. | **NÃO EXECUTADO** |
| T088-13 | Agência de jogadores, consentimento e delegação | Delegação tática não permite assinatura de acordo narrativo sem permissão. | **NÃO EXECUTADO** |
| T088-14 | Agência de jogadores, consentimento e delegação | Consentimento para conversar não equivale a consentimento para entregar provas. | **NÃO EXECUTADO** |
| T088-15 | Agência de jogadores, consentimento e delegação | Recusa de NPC ou PC não é substituída pela LLM. | **NÃO EXECUTADO** |
| T088-16 | Agência de jogadores, consentimento e delegação | Silêncio de PC não constitui aceite tácito. | **NÃO EXECUTADO** |
| T088-17 | Agência de jogadores, consentimento e delegação | Ameaça registrada não é mascarada como consentimento voluntário. | **NÃO EXECUTADO** |
| T088-18 | Agência de jogadores, consentimento e delegação | Impacto em outro PC exige verificação das políticas DEC-041/042. | **NÃO EXECUTADO** |
| T088-19 | Agência de jogadores, consentimento e delegação | Acordo que requer divulgação de segredo de terceiro exige ACL independente. | **NÃO EXECUTADO** |
| T088-20 | Agência de jogadores, consentimento e delegação | Risco HIGH em recrutamento coercitivo é fail-closed sem autorização. | **NÃO EXECUTADO** |
| T088-21 | Negociação e contratos | Contato inicial não cria agreement_id ativo. | **NÃO EXECUTADO** |
| T088-22 | Negociação e contratos | Contraproposta modifica apenas termos propostos e versão. | **NÃO EXECUTADO** |
| T088-23 | Negociação e contratos | Aceite exige evidência, contexto e confirmação de regra aplicável. | **NÃO EXECUTADO** |
| T088-24 | Negociação e contratos | Negociação parcial pode terminar sem contrato. | **NÃO EXECUTADO** |
| T088-25 | Negociação e contratos | Termo sem duração ou vigência legível permanece pendente. | **NÃO EXECUTADO** |
| T088-26 | Negociação e contratos | Beneficiário, escopo, canal e finalidade ficam registrados por cláusula. | **NÃO EXECUTADO** |
| T088-27 | Negociação e contratos | Proposta de contrato contraditória fica DISPUTED e não é executada. | **NÃO EXECUTADO** |
| T088-28 | Negociação e contratos | LLM não inventa assinatura NPC nem compromisso de PC. | **NÃO EXECUTADO** |
| T088-29 | Negociação e contratos | Duas propostas concorrentes não produzem acordo duplicado. | **NÃO EXECUTADO** |
| T088-30 | Negociação e contratos | Alteração de termos após aceite gera revisão, não sobrescrita silenciosa. | **NÃO EXECUTADO** |
| T088-31 | Recursos, economia e anti-exploit | Pagamento prometido não é pagamento realizado. | **NÃO EXECUTADO** |
| T088-32 | Recursos, economia e anti-exploit | Saldo insuficiente bloqueia reserva de ouro. | **NÃO EXECUTADO** |
| T088-33 | Recursos, economia e anti-exploit | Reserva repetida com mesma chave não é contada duas vezes. | **NÃO EXECUTADO** |
| T088-34 | Recursos, economia e anti-exploit | Moeda da engine só é debitada após host receipt de gateway. | **NÃO EXECUTADO** |
| T088-35 | Recursos, economia e anti-exploit | Entrega de item inexistente é rejeitada sem criar inventário. | **NÃO EXECUTADO** |
| T088-36 | Recursos, economia e anti-exploit | Acordo não gera XP ou loot por si só. | **NÃO EXECUTADO** |
| T088-37 | Recursos, economia e anti-exploit | Novos aliases não reiniciam caps de remuneração por NPC. | **NÃO EXECUTADO** |
| T088-38 | Recursos, economia e anti-exploit | Acordos em loop não geram segredos infinitos ou recompensas. | **NÃO EXECUTADO** |
| T088-39 | Recursos, economia e anti-exploit | Falha UNCERTAIN no débito bloqueia retry cego. | **NÃO EXECUTADO** |
| T088-40 | Recursos, economia e anti-exploit | Milestone não cumprido não libera automaticamente pagamento condicionado. | **NÃO EXECUTADO** |
| T088-41 | Entrega, conhecimento e prova | Informação prometida fica distinta de informação entregue. | **NÃO EXECUTADO** |
| T088-42 | Entrega, conhecimento e prova | Informante não fornece conteúdo que ainda não conhece. | **NÃO EXECUTADO** |
| T088-43 | Entrega, conhecimento e prova | Fonte sem prova de acesso a documento não o materializa. | **NÃO EXECUTADO** |
| T088-44 | Entrega, conhecimento e prova | Documento entregue pode ser suspeito de falsificação sem virar fato. | **NÃO EXECUTADO** |
| T088-45 | Entrega, conhecimento e prova | Entrega de rumor permanece alegação com proveniência. | **NÃO EXECUTADO** |
| T088-46 | Entrega, conhecimento e prova | Duas fontes que repetem mesma origem não são corroboração independente. | **NÃO EXECUTADO** |
| T088-47 | Entrega, conhecimento e prova | Recebimento de informe não aciona automaticamente quest ou acusação. | **NÃO EXECUTADO** |
| T088-48 | Entrega, conhecimento e prova | A informação entregue pode permanecer não verificada sem forçar conclusão. | **NÃO EXECUTADO** |
| T088-49 | Entrega, conhecimento e prova | LLM não usa conhecimento do host para completar lacunas do informante. | **NÃO EXECUTADO** |
| T088-50 | Entrega, conhecimento e prova | Relatório de informante aponta estado epistêmico e fonte de conhecimento. | **NÃO EXECUTADO** |
| T088-51 | Confidencialidade, fonte e segurança | Identidade secreta do NPC não vaza na versão pública do acordo. | **NÃO EXECUTADO** |
| T088-52 | Confidencialidade, fonte e segurança | Destinatário recebe só campos autorizados do informe. | **NÃO EXECUTADO** |
| T088-53 | Confidencialidade, fonte e segurança | Logs e métricas não expõem dados selados de identidade. | **NÃO EXECUTADO** |
| T088-54 | Confidencialidade, fonte e segurança | Índices RAG não retornam segredos a usuário sem ACL. | **NÃO EXECUTADO** |
| T088-55 | Confidencialidade, fonte e segurança | Worker LAN sem papel não recebe cláusulas sigilosas. | **NÃO EXECUTADO** |
| T088-56 | Confidencialidade, fonte e segurança | Mudança do roteador LLM não altera ACL da fonte. | **NÃO EXECUTADO** |
| T088-57 | Confidencialidade, fonte e segurança | Ameaça à fonte não equivale a autorização de divulgar seu refúgio. | **NÃO EXECUTADO** |
| T088-58 | Confidencialidade, fonte e segurança | Cancelamento do acordo não apaga memórias de NPC que realmente soube. | **NÃO EXECUTADO** |
| T088-59 | Confidencialidade, fonte e segurança | Informante duplo não revela plano de escolta só por vínculo com rival. | **NÃO EXECUTADO** |
| T088-60 | Confidencialidade, fonte e segurança | Exfiltração indireta por metadados de hora/rota é bloqueada por campo. | **NÃO EXECUTADO** |
| T088-61 | Encerramento, temporalidade e continuidade | NPC pode recusar tarefa posterior mesmo com acordo inicial ativo. | **NÃO EXECUTADO** |
| T088-62 | Encerramento, temporalidade e continuidade | Contrato expirado não permite nova coleta automática. | **NÃO EXECUTADO** |
| T088-63 | Encerramento, temporalidade e continuidade | Rescisão não apaga entregas anteriores confirmadas. | **NÃO EXECUTADO** |
| T088-64 | Encerramento, temporalidade e continuidade | Rescisão não causa mudança automática de facção. | **NÃO EXECUTADO** |
| T088-65 | Encerramento, temporalidade e continuidade | Restauração de save pré-acordo não importa contrato futuro. | **NÃO EXECUTADO** |
| T088-66 | Encerramento, temporalidade e continuidade | Branch alternativo não herda identidade e pagamento do informante. | **NÃO EXECUTADO** |
| T088-67 | Encerramento, temporalidade e continuidade | Novo Knowledge Pack não reescreve contratos da campanha. | **NÃO EXECUTADO** |
| T088-68 | Encerramento, temporalidade e continuidade | Ano DR futuro não informa negociação no passado. | **NÃO EXECUTADO** |
| T088-69 | Encerramento, temporalidade e continuidade | Repetição de evento após reload não assina contrato novamente. | **NÃO EXECUTADO** |
| T088-70 | Encerramento, temporalidade e continuidade | Fenced epoch bloqueia resposta atrasada de negociação em ramo errado. | **NÃO EXECUTADO** |
| T088-71 | Integração e limites de capacidades | Sem hook comprovado a negociação permanece apenas camada narrativa. | **NÃO EXECUTADO** |
| T088-72 | Integração e limites de capacidades | Sem capacidade de pagamento não se afirma débito de ouro. | **NÃO EXECUTADO** |
| T088-73 | Integração e limites de capacidades | Sem suporte de party não se altera controle de NPC. | **NÃO EXECUTADO** |
| T088-74 | Integração e limites de capacidades | Host+dois clientes exigidos antes de alegar sincronização multiplayer. | **NÃO EXECUTADO** |
| T088-75 | Integração e limites de capacidades | Recibo de host inconsistente não é tratado como sucesso. | **NÃO EXECUTADO** |
| T088-76 | Integração e limites de capacidades | Save/checkpoint e overlay devem coincidir antes de execução. | **NÃO EXECUTADO** |
| T088-77 | Integração e limites de capacidades | Acordo de informante não altera diretório canônico por ano DR. | **NÃO EXECUTADO** |
| T088-78 | Integração e limites de capacidades | Fala gerada sem fonte não vira evento factual de contrato. | **NÃO EXECUTADO** |
| T088-79 | Integração e limites de capacidades | Mudança de reputação sem causação é rejeitada. | **NÃO EXECUTADO** |
| T088-80 | Integração e limites de capacidades | Falha de LLM não paralisa a engine nem cria compromisso. | **NÃO EXECUTADO** |
| T088-81 | Integração e limites de capacidades | Fallback para regra determinística pode produzir REJECTED/PENDING sem fingir aceite. | **NÃO EXECUTADO** |
| T088-82 | Integração e limites de capacidades | Teste de regressão protege DEC-060–087 e direitos de decisões prévias. | **NÃO EXECUTADO** |

## 12. Sequência proposta para validação futura (não executada)

1. Criar fixtures sintéticas de NPCs com compromissos diversos, oportunidades de contato, recusas e contrapropostas.
2. Implementar apenas protótipos offline de negociação tipada, consentimento, revisão, caps, ACL e `UNCERTAIN` antes da engine.
3. Criar ledger de reservas mock e simulação de entregas com informação verdadeira, falsa, incompleta e desconhecida, sem assumir que a IA sabe a resposta.
4. Ensaiar multiplayer lógico, papéis de host/clientes, PC delegado/ausente, ocultação de fonte, branch, checkpoint, replay e NPC DORMANT.
5. Inventariar capacidades de BG2:EE clean build/EEex (primeiro read-only); criar POC de diálogo/receipts/troca real somente onde demonstrado; validar host e dois clientes.
6. Medir dedup, ausência de exposições, custo de recursos, capacidade de recusa, preservação de scripts/quests canônicos e consistência de chronologia/KPack.

## 13. Decisões relacionadas e DEC-089 em aberto

- DEC-060–063: lore fisicamente separado por ano DR, fonte curada e Knowledge Pack por campanha.
- DEC-064–068: memória, crença, identidade persistente e vida offscreen de NPCs.
- DEC-069–075: geografia, presença mecânica, causalidade, autoria e reputações.
- DEC-076–087: identidade/segredo, investigação, justiça, proteção, decepção e lealdades múltiplas.
- DEC-011/012/014/019/027/028/032/034/041/042/045–059: autoridade host, gateway, consentimento, recursos, riscos, autonomia, persistência, performance e privacidade.
- DEC-006/007/013/015/017/018 seguem abertas em seus escopos; não declaramos funcionalidades BG2:EE não verificadas.
- **DEC-089 (em aberto):** avaliar credibilidade de **informes já entregues**. **A)** aceitar automaticamente informação de fonte recrutada; **B)** LLM decidir livremente o que é verdadeiro; **C)** avaliar proveniência/independência, corroboração, contradições, escopo epistêmico, ACL e risco, sem tornar rumor fato ou aplicar consequências automáticas.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

DEC-088 separa acordo, promessa e entrega; a DEC-089/C agora exige lineage e corroboração depois da entrega e impede tratar oferta ou assinatura como prova de veracidade.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Informação entregue DEC-088 pode ser compilada no dossiê sem exibir automaticamente identidade/termos do recrutamento nem transformar promessa em entrega.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Acordo com informante não é promessa cumprida; plano não pode gastar recompensa ou supor acesso a documento inexistente.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Acordos com informantes possuem escopo/recursos/prazos; replanejamento não reescreve promessas nem obriga entrega de provas inexistentes.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Informante contratado para duas missões exclusivas ou mesmo horário deve negociar escopo/tempo; promessa de acesso não comprova disponibilidade física.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Acordos de informantes não podem ser rescindidos automaticamente por starvation do scheduler; pagamentos e compromissos confirmados persistem.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Acordo de informante não concede propriedade sobre NPC, inventário nem acesso a quest flag.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Contratos de informantes não incluem acesso automático a quest globals, romances ou scripts.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Quest state, mapping rule names and even flag metadata may expose future branches, romance or hidden identities; they remain private technical evidence. Dossiers, sources and NPCs receive only authorized safe milestones through independently confirmed disclosure; no belief is promoted to fact from ambiguous observations. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para informante não ganha acesso ou dever de retransmitir correção automaticamente, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para informante não assume obrigação automática de retratação, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Contratos com informantes exigem cumprimento provado sem execução oculta. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Acordo com informante depende de consentimento e recursos reais. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
