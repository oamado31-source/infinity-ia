# DEC-090 — Dossiês de inteligência: proveniência, versões, views autorizadas e difusão causal

**Discovery v8.6 · ADR-0085 · opção C aprovada · SOMENTE ARQUITETURA; NÃO IMPLEMENTADA.**  
**Evidências de testes:** **86 cenários T090-01..T090-86 candidatos; TODOS NÃO EXECUTADOS**. Nenhum POC de integração com BG2:EE/EEex/multiplayer é afirmado.

## 1. Objetivo e invariantes

O produto deve permitir organizar uma investigação em um dossiê confiável **sem** presumir que suas alegações são fatos, que todas as pessoas podem ver o mesmo material ou que a geração do documento equivale a transmiti-lo. Dossiês e views compartilhadas serão versionadas e auditáveis, mantendo fontes, incertezas e condições de distribuição.

Invariantes vinculantes:

1. **Fonte ≠ fato:** `SourceClaim` DEC-089 preserva origem, independência e contradições; dossiês não certificam as alegações.
2. **Dossiê ≠ entrega:** somente evento causal validado pode atualizar conhecimento do destinatário.
3. **Público restrito:** todos os campos, citações, anexos e metadados seguem ACL/consentimento/finalidade.
4. **Revisão ≠ amnésia:** retificação não apaga documentos já transmitidos nem crenças pretéritas.
5. **Conhecimento canônico ≠ inteligência da campanha:** ano DR físico DEC-060, overlay privado por campanha/branch.
6. **Texto ≠ mecânica:** sem gateway host e capability testada, o dossiê não é um item/journal/evento físico do BG2:EE.

## 2. Fronteiras de armazenamento e confiança

```text
knowledge/periods/<ANO>-DR/                # lore canônico CURADO; partições físicas anuais DEC-060
  events/, locations/, organizations/ ...  # nunca publicar aqui segredos/informes dinâmicos

campaign-overlays/<campaign>/<branch>/     # DOMÍNIO LÓGICO CANDIDATO, caminho não implementado
  informants/                              # acordos/entregas DEC-088
  claims/                                  # alegações e assessments DEC-089
  evidence-families/                       # proveniência e corroboração independentes
  dossiers/                                # estrutura, revisões e conteúdo restrito
  dossier-revisions/<revision>/            # snapshots e citações
  disclosure-views/                        # views filtradas por audiência/finalidade
  share-authorizations/                    # consentimento, risco e competência
  transmissions/                           # canais, tempo, envios e receipts
  observer-beliefs/                        # crenças localizadas e graduais
  corrections-and-audit/                   # revisões append-only e correções
```

A árvore de overlay é uma **proposta de domínio**, não diretório fisicamente implantado. Ela não substitui a segmentação física real do lore por ano DR já definida. Para referências canônicas, consultar o ano de origem legitimamente disponível com Knowledge Pack pinado DEC-063; nunca inserir os dados privados da campanha nesse corpus.

## 3. Contratos candidatos (tipos não implementados)

```text
Dossier {
  campaign_id, branch_id, dossier_id, owner_scope, purpose,
  title_classified, scope_dr, dossier_acl, classification,
  status: DRAFT|CURATED|PUBLISHED_INTERNAL|ARCHIVED,
  current_revision_id, created_event_id, provenance_refs[]
}
DossierRevision {
  dossier_id, revision_id, based_on_revision_id?, immutable_snapshot_hash,
  claim_item_refs[], evidence_citations[], conflicting_evidence_refs[],
  knowledge_pack_binding, checkpoint_ref, resolution_epoch,
  policy_revision, source_assessment_revision_ids[], review_receipt_ref?,
  semantic_diff_refs[], created_at_dr, created_by_scope
}
DossierClaim {
  dossier_id, revision_id, claim_id, source_report_ref?,
  claim_assessment_id, assessment_revision, claim_scope,
  status: UNVERIFIED|PARTIALLY_CORROBORATED|CORROBORATED_WITH_SCOPE|
          CONTRADICTED|INCONCLUSIVE|STALE,
  supporting_evidence_family_ids[], contradictory_family_ids[],
  qualifier, source_acl, retained_uncertainty_refs[]
}
EvidenceCitation {
  citation_ref, evidence_record_id, evidence_revision,
  source_origin_lineage_ref, evidence_family_id,
  displayable_source_label?, disclosure_acl, quote_or_summary_scope,
  public_citation_alias?, validation_receipt_ref?
}
DisclosureView {
  dossier_id, source_revision_id, view_id, recipient_id,
  audience_scope, purpose, policy_revision, access_approval_ref,
  redaction_manifest_private_ref, included_claim_refs[],
  included_evidence_aliases[], included_annex_refs[], minimized_metadata,
  hidden_field_inference_risk_label, view_hash, sanitized_payload_ref,
  status: STAGED|VALIDATED|AUTHORIZED|REVOKED|STALE
}
ShareProposal {
  proposal_id, dossier_revision, view_id, sender_identity_ref,
  recipient_scope, purpose, proposed_channel_ref, proposed_time_dr,
  transfer_right_ref?, risk_classification, authorization_refs[],
  owner_consent_refs[], proposed_mechanical_effect?, status
}
ShareAuthorization {
  proposal_id, authorization_ref, policy_revision, actor_authority,
  recipient_id, purpose, allowed_view_hash, allowed_channel_ref,
  expires_at_dr?, risk_review_ref, capability_ref?, state
}
TransmissionEvent {
  transmission_id, authorization_ref, view_id, view_hash,
  sender_ref, recipient_scope, channel_ref, sent_at_dr,
  expected_arrival_dr?, cause_event_id, idempotency_key,
  checkpoint_ref, resolution_epoch,
  status: PREPARED|IN_TRANSIT|DELIVERED|REJECTED|UNCERTAIN|STALE
}
RecipientReceipt {
  transmission_id, receiver_ref, received_at_dr,
  content_view_hash, received_components[], ack_source,
  validation_receipt_ref, status: RECEIVED|PARTIAL|UNVERIFIED
}
CorrectionNotice {
  notice_id, corrected_dossier_revision_id,
  superseded_revision_refs[], affected_view_ids[],
  intended_recipient_scopes[], explanation_acl, channels[],
  authorized_by_ref, notice_event_id, status
}
ObserverBeliefUpdate {
  receiver_identity_ref, permitted_claim_refs[], transmitted_view_id,
  belief_delta_candidates[], acquired_at_dr, credibility_context,
  source_chain[], authorization_ref?, status: PROPOSED|APPLIED|REJECTED
}
```

Campos ausentes ficam `UNKNOWN`. IDs são referências lógicas, não evidência de observabilidade da engine. O mesmo `claim_id` pode constar em versões filtradas distintas, com citações públicas diferentes sem revelar identificadores internos.

## 4. Construção e curadoria do dossiê

1. **Entrada validada:** localizar registros de entrega DEC-088, alegações/avaliações DEC-089, provas DEC-077 e provenance DEC-061. Não criar alegação de documento inexistente.
2. **Snapshot temporal:** fixar `campaign_id`, `branch_id`, KPack, DR, revisão, checkpoint e política. Não incluir relatos de branches futuros ou outra campanha.
3. **Compor itens atômicos:** referenciar alegações por escopo de ator, lugar, tempo e ação, preservando incerteza. Documentar as famílias de evidências independentes; não usar número bruto de pessoas como grau de certeza.
4. **Revisão determinística:** verificar links, origem/linhagem, ACL, contradições, capacidade da fonte, coerência temporal e versionamento. Quando não resolvido, exibir `INCONCLUSIVE`.
5. **Redação opcional:** LLM local pode sugerir clareza, sumário, tradução ou estrutura usando apenas os campos já filtrados para o papel da operação; revalidação obrigatória antes de publicar o texto.
6. **Freeze:** criar `DossierRevision` imutável, com fingerprint do conteúdo, diff e histórico de auditoria; não atualizar um documento já entregue em lugar de criar revisão nova.

## 5. Views seletivas por destinatário e classificação

**Regra:** `DisclosureView = project(snapshot, intersect(contentACL, purposeACL, recipientCapability, consent, jurisdiction, policy, risk))`.

A expressão descreve um contrato **candidato**, não função implementada. Proteger anexos e metadados pelo mesmo cálculo. A view de **autoridade competente** pode conter provas delimitadas por necessidade e legitimidade; a de **aliado** pode conter só o resumo e ressalvas. Mesmo a autoridade competente não possui passe livre para a identidade de informantes protegidos ou histórico secreto de PC.

| Campo no snapshot privado | View para autoridade | View para aliado | Regra |
|---|---|---|---|
| Alegação avaliada | Escopo necessário e autorizado | Resumo autorizado | Nunca fortalecer conclusão |
| Evidência e contradições | Citações autorizadas | Referências generalizadas/qualificadores | Provar origem sem expor segredo |
| Identidade de testemunha | Apenas se gate específico permitir | Suprimida | DEC-083; consentimento/competência |
| Refúgio e rota de escolta | Geralmente omitidos; exceções justificadas | Omitidos | DEC-084/085; metadados igualmente sigilosos |
| Contrato de informante | Somente termos essenciais e autorizados | Omitido | DEC-088 e recursos |
| Hipótese sobre persona | Atribuição por estado e ACL | Hipótese somente se permitida | DEC-076/077; suspeita não é fato |
| Operação de engano | Só se a audiência puder conhecer sua natureza | Omitida ou apresentada como alegação aparente se autorizado | DEC-086, sem vazar verdade privada |
| Citações/IDs/horário/quantidade | Pseudonimizados conforme risco | Generalizados conforme risco | Evitar reidentificação indireta |

Se suprimir uma evidência tornar a frase pública enganosa, **reformular ou retirar a conclusão**, em vez de publicar resumo mais forte do que o que os destinatários podem legitimamente avaliar. Se toda prova for protegida, entregar um resumo explicitamente qualificado ou negar divulgação.

## 6. Compartilhamento causal e atualização de conhecimento

```text
DossierRevision(CURATED)
  -> DisclosureView(STAGED)
  -> Validate ACL + metadata + inference risk
  -> DisclosureView(VALIDATED)
  -> ShareProposal
  -> Consent / jurisdiction / risk / channel / host gate
  -> ShareAuthorization
  -> TransmissionEvent(PREPARED / IN_TRANSIT)
  -> RecipientReceipt(RECEIVED / PARTIAL / UNVERIFIED)
  -> ObserverBeliefUpdate(PROPOSED / APPLIED / REJECTED)
```

- **Informação transmitida** não é **informação recebida**; `UNCERTAIN` não permite dedução positiva de leitura nem retry mecânico cego.
- **Destinatário que recebeu** não é automaticamente **destinatário que concordou**; crenças seguem DEC-064/065, origem e confiança percebida.
- **Facção informada** não é universalmente onisciente; difusão para membros requer canais DEC-029/074 e conhecimento local.
- **Anexo não entregue** não gera conhecimento: recibo contém componentes efetivamente recebidos.
- **Janela temporal:** mensageiros, itinerários e regiões DEC-069; o recebimento não pode anteceder envio e viagem plausível.
- **Risco:** se a publicação puder expor PC, fonte, abrigo ou provocar dano HIGH, exigir autorização e evitar as partes não necessárias.

## 7. Correção, revogação de permissão e vazamentos

- Uma revisão nova preserva o snapshot anterior. A correção posterior gera `CorrectionNotice`, que **pode** seguir os mesmos canais e chegar de modo desigual; não há apagamento retroativo das crenças e cópias legitimamente recebidas.
- Revogar uma permissão bloqueia **novas** transmissões e invalida jobs/payloads/cache pendentes; não apaga da memória do NPC a conversa legítima anterior.
- Encaminhamento autorizado exige novo `ShareProposal`; vazamento/narração de divulgação indevida não é possível apenas por acesso ao ledger privado, mas pode ocorrer mediante ação de NPC já informado e regras DEC-085/086/077, com rastreabilidade e risco.
- Retificação de mandado ou responsabilização DEC-080/081/082 segue seus próprios gates jurídicos; a circulação de um dossiê retificado não atualiza automaticamente sanções mecânicas.
- Anti-duplicação: `idempotency_key` inclui IDs de dossiê, revisão, view, receptor, propósito, canal e epoch; crash, reload, co-op e LAN requerem conciliação de receipt.

## 8. Privacidade, threat model e segurança técnica

| Ameaça | Contenção candidata |
|---|---|
| Nome da testemunha oculto, mas hash e filename a identificam | Remover/generalizar metadados; aliases públicos não vinculáveis; avaliar inferência por composição. |
| Sumário LLM revela conteúdo não autorizado | Filtrar input antes de inferência, conferir saída contra corpus permitido, rejeitar extrapolação. |
| Trabalhador LAN vê dados privados | Não lhe entregar payload; role, capability, finalidade e revogação DEC-058/059. |
| Compartilhamento para um aliado reusa view de autoridade | View por destinatário/finalidade e hash/autorização vinculantes. |
| Documento contém pistas falsas DEC-086 | Manter natureza epistemológica como alegação; never confirm from text. |
| Dossiê de outra campanha aparece após reload | Branch/checkpoint/epoch/KPack filter; invalidar jobs stale. |
| Várias correções duplicadas degradam reputação | Ledger idempotente DEC-074/075; efeito social não resulta diretamente da mera emissão. |
| Viewer cria item/quest involuntariamente | Somente ação do host no gateway DEC-012 com receipt; sem engine POC não há ação. |
| Fonte A replicada por B e C aumenta confiança | `EvidenceFamily` DEC-089 preservada em cada revisão e sumário. |
| Excesso de processamento local | Composição determinística e cache por revisão/política, sem LLM por tick. |

## 9. Relação com decisões aprovadas

- **DEC-060/C:** partição **física** do lore em `knowledge/periods/<ANO>-DR/`; não substituída por banco monolítico.
- **DEC-061–063/C:** proveniência e curadoria contextual, ingestão validada e Knowledge Packs pinados.
- **DEC-064–075/C:** memórias falíveis, identidade persistente, tempo/presença NPC, causalidade e autoria confirmada versus reconhecimento.
- **DEC-076–077/C:** personas privadas e investigações; jamais revelar identidade verdadeira por título de relatório.
- **DEC-078–082/C:** competência, mandados, versões/revogação, reparação, responsabilização e risco.
- **DEC-083–085/C:** identidade de testemunhas, risco de proteção e sigilo de refugio/rotas.
- **DEC-086–089/C:** enganos, lealdades, negociação e informes avaliados por dependência e evidência.
- **DEC-019/028/041/045/046:** visibilidade, agência, consentimento e delegação PC.
- **DEC-011/012/027/034/052/053/055/056/057–059:** host, gateway, riscos, canon irreversível, compatibilidade, checkpoints, observabilidade, filas, LAN e LLM local.
- **DEC-006/007/013/015/017/018:** pendentes conforme mapa; não presumir direitos/capacidades ou funcionalidades fechadas.

## 10. Matriz de testes candidatos — TODOS NÃO EXECUTADOS

Os testes abaixo são **propostas**, não resultados. Para a fase de SPECS, associar fixture sintética, permissão, evento comprovável, oracle de aceite/rejeição e evidência (inclusive testes host + 2 clientes quando aplicável).

| ID | Categoria | Verificação esperada | Status |
|---|---|---|---|
| T090-01 | Composição e epistemologia | Criar dossiê privado não envia informação a qualquer NPC ou jogador. | NÃO EXECUTADO |
| T090-02 | Composição e epistemologia | Dossiê distingue `SourceClaim` de `WorldFactReference` comprovado. | NÃO EXECUTADO |
| T090-03 | Composição e epistemologia | Um informe entregue sem avaliação mantém estado UNVERIFIED na compilação. | NÃO EXECUTADO |
| T090-04 | Composição e epistemologia | Alegação parcialmente corroborada não vira afirmação plenamente confirmada. | NÃO EXECUTADO |
| T090-05 | Composição e epistemologia | Duas fontes com a mesma EvidenceFamily não contam como comprovação independente. | NÃO EXECUTADO |
| T090-06 | Composição e epistemologia | Relatos contraditórios aparecem com fontes, escopo temporal e estado INCONCLUSIVE. | NÃO EXECUTADO |
| T090-07 | Composição e epistemologia | Citação de evidência inexistente bloqueia a conclusão ou a deixa UNKNOWN. | NÃO EXECUTADO |
| T090-08 | Composição e epistemologia | Um documento forjado continua alegação; não vira fato por entrar no dossiê. | NÃO EXECUTADO |
| T090-09 | Composição e epistemologia | DossierRevision nova preserva hash, origem e referência à revisão anterior. | NÃO EXECUTADO |
| T090-10 | Composição e epistemologia | Dossiê não altera retrospectivamente fatos já confirmados no ledger. | NÃO EXECUTADO |
| T090-11 | Composição e epistemologia | Mesmo informe permite diferentes avaliações de local, horário e participantes. | NÃO EXECUTADO |
| T090-12 | Composição e epistemologia | Depoimento com cadeia de transmissão circular não aumenta corroboração. | NÃO EXECUTADO |
| T090-13 | Composição e epistemologia | Resumos não escondem contradições necessárias para interpretar a conclusão. | NÃO EXECUTADO |
| T090-14 | Composição e epistemologia | O texto da LLM que extrapola a avaliação validada é rejeitado. | NÃO EXECUTADO |
| T090-15 | Composição e epistemologia | Ausência de evidência mantém INCONCLUSIVE, não comprovadamente falso. | NÃO EXECUTADO |
| T090-16 | Composição e epistemologia | Corroboração posterior gera revisão sem reescrever a view antiga já enviada. | NÃO EXECUTADO |
| T090-17 | Permissões e privacidade | Aliança entre facções não autoriza acesso ao relatório bruto por si só. | NÃO EXECUTADO |
| T090-18 | Permissões e privacidade | ACL da fonte prevalece sobre ACL genérica da pasta do dossiê. | NÃO EXECUTADO |
| T090-19 | Permissões e privacidade | Política de finalidade impede uso de view de investigação para divulgação pública. | NÃO EXECUTADO |
| T090-20 | Permissões e privacidade | Autoridade sem competência recebe recusa mesmo se o remetente tem acesso. | NÃO EXECUTADO |
| T090-21 | Permissões e privacidade | Proteção DEC-083 remove identidade da fonte no payload, não só na UI. | NÃO EXECUTADO |
| T090-22 | Permissões e privacidade | Horário exclusivo de escolta capaz de reidentificar fonte é minimizado. | NÃO EXECUTADO |
| T090-23 | Permissões e privacidade | Nome e caminho de arquivo sigiloso não aparecem nos metadados da view. | NÃO EXECUTADO |
| T090-24 | Permissões e privacidade | Quantidade de testemunhas pode ser suprimida quando singulariza uma pessoa. | NÃO EXECUTADO |
| T090-25 | Permissões e privacidade | Pseudônimo protegido DEC-076 não é vinculado a nome verdadeiro por citação. | NÃO EXECUTADO |
| T090-26 | Permissões e privacidade | Posição de refúgio DEC-085 não sai em hiperlinks, notas ou metadados. | NÃO EXECUTADO |
| T090-27 | Permissões e privacidade | Termos de um informante DEC-088 são omitidos da view de um aliado. | NÃO EXECUTADO |
| T090-28 | Permissões e privacidade | A view gerada para autoridade não é reutilizada para membro da party. | NÃO EXECUTADO |
| T090-29 | Permissões e privacidade | ACL revogada invalida geração e publicação pendente de nova view. | NÃO EXECUTADO |
| T090-30 | Permissões e privacidade | Revogar acesso não tenta apagar lembrança já adquirida por um NPC. | NÃO EXECUTADO |
| T090-31 | Permissões e privacidade | Owner de PC deve autorizar informação de sua titularidade conforme DEC-019. | NÃO EXECUTADO |
| T090-32 | Permissões e privacidade | Delegado de PC não recebe permissão implícita de divulgar seu segredo. | NÃO EXECUTADO |
| T090-33 | Permissões e privacidade | A party não recebe segredos de um membro automaticamente. | NÃO EXECUTADO |
| T090-34 | Permissões e privacidade | Compartilhamento de duas views aparentemente inofensivas é testado contra inferência agregada. | NÃO EXECUTADO |
| T090-35 | Permissões e privacidade | Documentos anexos recebem a mesma filtragem que sumários textuais. | NÃO EXECUTADO |
| T090-36 | Permissões e privacidade | Logs, traces e cache não expõem campos cortados pela ACL. | NÃO EXECUTADO |
| T090-37 | Permissões e privacidade | Embeddings/RAG acessíveis a outro papel não recuperam a identidade protegida. | NÃO EXECUTADO |
| T090-38 | Permissões e privacidade | Worker LAN sem papel autorizado não recebe nem cacheia conteúdo confidencial. | NÃO EXECUTADO |
| T090-39 | Compartilhamento e percepção | Montar dossiê não produz TransmissionEvent sem ShareProposal autorizado. | NÃO EXECUTADO |
| T090-40 | Compartilhamento e percepção | Aceite de proposta sem canal legítimo não equivale a entrega. | NÃO EXECUTADO |
| T090-41 | Compartilhamento e percepção | Mensagem enviada em trânsito não concede conhecimento ao destinatário. | NÃO EXECUTADO |
| T090-42 | Compartilhamento e percepção | Falha de entrega mantém RecipientReceipt pendente, não confirmada. | NÃO EXECUTADO |
| T090-43 | Compartilhamento e percepção | Entrega confirmada não implica crença ou entendimento do NPC. | NÃO EXECUTADO |
| T090-44 | Compartilhamento e percepção | NPC recebe apenas os campos realmente presentes em sua DisclosureView. | NÃO EXECUTADO |
| T090-45 | Compartilhamento e percepção | Líder informado não atualiza instantaneamente as crenças de todos os subordinados. | NÃO EXECUTADO |
| T090-46 | Compartilhamento e percepção | O mesmo dossiê dá views diferentes a autoridade e aliado. | NÃO EXECUTADO |
| T090-47 | Compartilhamento e percepção | Divulgação a uma pessoa não concede cópia automática a outra facção. | NÃO EXECUTADO |
| T090-48 | Compartilhamento e percepção | Retransmissão autorizada produz novo evento com causa e destinatário. | NÃO EXECUTADO |
| T090-49 | Compartilhamento e percepção | Transmissão não autorizada pelo software é rejeitada com auditoria redigida. | NÃO EXECUTADO |
| T090-50 | Compartilhamento e percepção | Vazamento narrativo legítimo não é apagado por mera revogação posterior. | NÃO EXECUTADO |
| T090-51 | Compartilhamento e percepção | Fonte C que ouviu A aparece como relato derivado na view autorizada. | NÃO EXECUTADO |
| T090-52 | Compartilhamento e percepção | Canal com deslocamento de mensageiro respeita tempo e região DEC-069. | NÃO EXECUTADO |
| T090-53 | Compartilhamento e percepção | Transmissão em época posterior não retrocede conhecimento à DR anterior. | NÃO EXECUTADO |
| T090-54 | Compartilhamento e percepção | Recebimento de anexos difere do recebimento somente do resumo. | NÃO EXECUTADO |
| T090-55 | Ciclo de vida e concorrência | Retry de ShareAuthorization com mesma idempotency key não duplica envio. | NÃO EXECUTADO |
| T090-56 | Ciclo de vida e concorrência | Reenvio de um receipt já aplicado não duplica crença nem reputação. | NÃO EXECUTADO |
| T090-57 | Ciclo de vida e concorrência | PENDING/UNCERTAIN não são convertidos automaticamente em RECEIVED. | NÃO EXECUTADO |
| T090-58 | Ciclo de vida e concorrência | Restore anterior bloqueia transmissão originada após o checkpoint. | NÃO EXECUTADO |
| T090-59 | Ciclo de vida e concorrência | Jobs stale de outra campanha ou branch são descartados. | NÃO EXECUTADO |
| T090-60 | Ciclo de vida e concorrência | Correção posterior não altera snapshot imutável já entregue. | NÃO EXECUTADO |
| T090-61 | Ciclo de vida e concorrência | CorrectionNotice aponta versão e público corretos, não todas as facções. | NÃO EXECUTADO |
| T090-62 | Ciclo de vida e concorrência | Notificação de correção sem canal legítimo permanece pendente. | NÃO EXECUTADO |
| T090-63 | Ciclo de vida e concorrência | Uma retificação não apaga crença histórica errônea do NPC. | NÃO EXECUTADO |
| T090-64 | Ciclo de vida e concorrência | Nova revisão de ACL invalida caches e views pendentes da anterior. | NÃO EXECUTADO |
| T090-65 | Ciclo de vida e concorrência | Deduplicação inclui destinatário e propósito, sem suprimir outra entrega legítima. | NÃO EXECUTADO |
| T090-66 | Ciclo de vida e concorrência | Dossiê velho não consulta Knowledge Pack diferente do pinado no checkpoint. | NÃO EXECUTADO |
| T090-67 | Ciclo de vida e concorrência | Dossiê de campanha não é ingerido em conhecimento canônico anual. | NÃO EXECUTADO |
| T090-68 | Ciclo de vida e concorrência | Comparação do arquivo anual DR impede vazamento de fonte futura no dossiê do passado. | NÃO EXECUTADO |
| T090-69 | Ciclo de vida e concorrência | Cópia de servidor LAN não se torna autoridade mestre do conteúdo. | NÃO EXECUTADO |
| T090-70 | Ciclo de vida e concorrência | Queda no meio de publicação é reconciliada sem retry cego. | NÃO EXECUTADO |
| T090-71 | Host, custo e implementação | Criar dossiê não cria item físico na engine sem gateway e receipt. | NÃO EXECUTADO |
| T090-72 | Host, custo e implementação | Exportar view não altera journal/quest por inferência da LLM. | NÃO EXECUTADO |
| T090-73 | Host, custo e implementação | Reputação mecânica não muda apenas por leitura ou entrega de dossiê. | NÃO EXECUTADO |
| T090-74 | Host, custo e implementação | Informe INCONCLUSIVE não autoriza prisão ou hostilidade automática. | NÃO EXECUTADO |
| T090-75 | Host, custo e implementação | Divulgar dado de risco HIGH sem autorização do host permanece bloqueado. | NÃO EXECUTADO |
| T090-76 | Host, custo e implementação | Falha de POC multiplayer impede declarar sincronização de documentos funcional. | NÃO EXECUTADO |
| T090-77 | Host, custo e implementação | Compilação determinística funciona sem chamadas obrigatórias a LLM. | NÃO EXECUTADO |
| T090-78 | Host, custo e implementação | Sumário LLM só recebe a view pré-filtrada e output passa por validação. | NÃO EXECUTADO |
| T090-79 | Host, custo e implementação | Fallback para modelo alternativo preserva ACL e autorização por finalidade. | NÃO EXECUTADO |
| T090-80 | Host, custo e implementação | Filas e caches não geram nova inferência a cada tick de NPC. | NÃO EXECUTADO |
| T090-81 | Host, custo e implementação | Indisponibilidade do host não faz o dossiê criar fatos ou executar efeitos. | NÃO EXECUTADO |
| T090-82 | Host, custo e implementação | Uma `PlantedClaim` autorizada não é promovida a verdade na redação do dossiê. | NÃO EXECUTADO |
| T090-83 | Host, custo e implementação | Reenvio de pacote com hash de view divergente é rejeitado antes de confirmar entrega. | NÃO EXECUTADO |
| T090-84 | Host, custo e implementação | Um campo protegido omitido em view não aparece por texto alternativo da LLM. | NÃO EXECUTADO |
| T090-85 | Host, custo e implementação | Proposta de enviar dossiê para autoridade com competência expirada falha fechada. | NÃO EXECUTADO |
| T090-86 | Host, custo e implementação | Mesmo destinatário recebe apenas a revisão explicitamente autorizada na transmissão. | NÃO EXECUTADO |

## 11. Plano candidato de POCs, bloqueios e evidência

1. **Offline:** construir fixtures com dez depoimentos, três documentos, fontes repetidas, contestação e duas audiências; testar filtro, ACL, hash, diff, redaction manifest e inferências cruzadas.
2. **Privacidade:** simular testemunha protegida, PC ausente, delegado, informante remunerado, alias, abrigo e operação de engano; verificar vazamento por anexos, metadados e LLM.
3. **Causalidade:** simular mensageiros, entregas parciais, correções, atrasos, retransmissões, revogações, filas stale e atualização seletiva de crenças.
4. **Consistência:** campanha/branch/DR e KPack pinados; rewind, save/load, simulação de crash e dedup; conservar os documentos históricos.
5. **Engine read-only:** inventariar se há interface legítima no BG2:EE/EEex para journal, documentos, actor recipients e entrega de item sem alterar instalação principal.
6. **Gates:** somente após provas em build reproduzível, host + dois clientes e gateway/autorização considerar publicação em interface de jogo ou item mecânico. Caso contrário, manter o dossiê como overlay narrativo externo.

## 12. Próxima DEC-091 (ABERTA)

**Planos e ações operacionais baseadas em inteligência incerta.** A) dossiês corroborados disparam ações automaticamente; B) LLM decide e executa planos; **C (recomendada)** separar hipótese/planejamento de execução, graduar decisões por evidência atual, risco, recursos, agência dos jogadores, tempo e autorização do host. Resumo ambíguo pode gerar perguntas e missões investigativas, nunca coerção automática.

## Integração DEC-091/C — Discovery v8.7

DossierRevision é entrada privada; DisclosureView filtrada informa planejamento de cada participante sem ampliar ACL; transmissão ≠ conhecimento.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Dossiês versionados e views filtradas condicionam informação disponível em cada momento; envio sem receipt não altera conhecimento do destinatário.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Conflitos entre operações que consultam dossiês não expõem documentos de uma equipe à outra; o scheduler recebe apenas claims mínimos e ACL.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Diagnóstico de conflito deve ser uma view de ACL e não entregar dossiê privado a outro grupo por compartilhar recurso.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Regras propostas DEC-096 respeitam destinatário/ACL e não incluem lore futura ou fontes privadas só porque estão no índice cronológico.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Dossiês DEC-090 não exportam knowledge pack inteiro da DEC-096/C; cada destinatário recebe visão compatível com ACL e data.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Relatórios DEC-090 sobre impactos DEC-097/C exibem nível de certeza e resguardam origens/ACL por destinatário.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Dossiês não compartilham automaticamente snapshots privados ou IDs de entidades durante mudanças de área; ACL e transmissão continuam separadas.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Dossiês de inteligência não divulgam manifests ou estados privados de quests fora da ACL.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Dossiês de inteligência não exportam flags brutos; versões para cada público usam projeções com ACL.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Quest state, mapping rule names and even flag metadata may expose future branches, romance or hidden identities; they remain private technical evidence. Dossiers, sources and NPCs receive only authorized safe milestones through independently confirmed disclosure; no belief is promoted to fact from ambiguous observations. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Mudança de projeção DEC-102 não distribui versões novas de dossiês automaticamente. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** a conclusão técnica de uma quest não concede automaticamente conhecimento ou crença a NPCs/facções. `QuestMilestoneAdmission` pode gerar proposta de notícia/reputação somente por regras, proveniência, tempo, geografia, visibilidade e ACL; notícia requer fonte/canal/delivery, e seus destinatários podem conhecer apenas versões parciais. Não expor identidades secretas, fontes protegidas ou raw flags por prompts/logs/dossiês. Ações mecânicas derivadas dependem de recibos host, sem atribuição presumida de PC. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **versões de relatórios e avisos de errata**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para dossiês versionados geram views por destinatário e registros de entrega, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para dossiês redigidos por audiência, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Dossiês de execução têm views restritas por destinatário. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Dossiês mostram somente vistas de obrigações autorizadas. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
