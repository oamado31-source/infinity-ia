# DEC-089 — Verificação de informes: proveniência, independência, contradições e confiabilidade

**Discovery v8.5 · ADR-0084 · DEC-089/C aprovada SOMENTE COMO ARQUITETURA · NÃO IMPLEMENTADA**  
**84 testes candidatos T089-01..T089-84, todos NÃO EXECUTADOS. Nenhuma POC BG2:EE/EEex executada.**

## 1. Objetivo e limites

Desenvolver um método coerente para avaliar se relatos de informantes e NPCs são corroborados, contraditos, parcialmente confiáveis ou inconclusivos. A DEC-089 avalia **qualidade de informações já entregues**, não a negociação e o recrutamento DEC-088, nem a decisão de **quem receberá um dossiê** (DEC-090). Não cria um detector infalível de mentira, tribunal automatizado ou gerador de fatos. Fato privado da campanha, alegação, crença, evidência documental, informação difundida e mudança mecânica pertencem a autoridades distintas.

### Invariantes

- `DELIVERED` é estado de transporte/entrega, não status de verdade.
- `SOURCE_CLAIM` é uma alegação originada por um ator/fonte; pode ser verdadeira, errada, enganosa ou desconhecida.
- `CITED_EVIDENCE` identifica objeto/observação/documento com prova de existência e cadeia de origem, não atesta todo o conteúdo.
- `SOURCE_FAMILY` conta raízes independentes, não quantidade de cópias, depoimentos ou pseudônimos.
- `CLAIM_ASSESSMENT` tem resultado **escopado, revisável e audível**, e não é `WORLD_FACT` por mera pontuação.
- `OBSERVER_BELIEF` registra a perspectiva falível de um NPC; o host pode conhecer a realidade sem que o NPC a saiba.
- `ACTION_GATEWAY` e o host são os únicos caminhos para alterações mecânicas verificadas (DEC-011/012); avaliação não executa punições.

## 2. Separação de armazenamento, calendário e realidade

```text
knowledge/periods/<ANO>-DR/               # cânone por ano em partições físicas separadas
  events/, locations/, organizations/ ... # somente lore curado DEC-060–063

campaign-overlays/<campaign>/<branch>/   # domínio lógico CANDIDATO, não caminho implantado
  informants/                            # acordos DEC-088 e identidades DEC-076/083
  delivered-reports/                     # o que foi recebido realmente
  claims/                                # hipóteses, testemunhos e afirmações
  evidence-ledger/                       # fonte, origem, qualidade e visibilidade
  source-lineage-graph/                  # quem copiou ou ouviu quem
  evidence-families/                     # agrupamento de corroboração independente
  claim-assessments/                     # avaliações versionadas por recorte
  source-reliability/                    # histórico contextual, não verdade universal
  observer-beliefs/                      # o que cada NPC/facção acredita
  revisions-and-audit/                   # retratações, erros, checkpoint, causação
```

**Partições anuais físicas são invariantes da DEC-060:** a pasta canônica não recebe rumores de campanha. Fonte canônica com referência editorial legítima DEC-061 deve ser distinguida de depoimento *in-world* entregue em jogo. Ano DR do conhecimento de uma fonte não é o ano editorial da obra. Anos futuros não devem fornecer acontecimentos retroativos.

## 3. Entidades e contratos candidatos (não implementados)

```text
DeliveredReport {
  campaign_id, branch_id, report_id, delivery_id, agreement_id?,
  deliverer_identity_ref, received_by_scope, transport_or_meeting_event_ref,
  delivered_at_dr, content_acl, message_or_item_receipt_ref,
  delivery_state: RECEIVED|PENDING|REJECTED|UNCERTAIN, checkpoint_epoch
}
SourceClaim {
  claim_id, report_id, predicate_or_proposition, subject_refs[],
  claimed_place_ref?, claimed_time_window_dr?, time_precision,
  asserted_confidence_label?, claimed_basis: DIRECT|HEARSAY|DOCUMENT|UNKNOWN,
  source_identity_ref?, persona_ref?, source_scope, evidence_refs[],
  privacy_acl, provenance_revision, status: ACTIVE|RETRACTED|DISPUTED
}
EvidenceRecord {
  evidence_id, kind: ENGINE_RECEIPT|WITNESS_ACCOUNT|DOCUMENT|OBSERVATION|CANON_REFERENCE|OTHER,
  event_or_document_ref?, origin_actor_ref?, obtained_at_dr,
  observed_at_dr?, place_ref?, chain_of_custody_refs[], source_provenance,
  authorization_scope, knowledge_pack_revision?, validation_state,
  contradictory_claim_refs[], validity_window?, privacy_acl, immutable_revision
}
OriginLineage {
  lineage_id, evidence_or_claim_ref, immediate_source_ref?, original_source_ref?,
  transmission_event_ids[], copy_of_refs[], derived_from_refs[],
  circularity_detected, unresolved_links[], source_scope, revision
}
EvidenceFamily {
  family_id, origin_set_fingerprint, root_evidence_refs[], member_claim_refs[],
  dependencies[], independent_of_family_ids[], independence_basis_refs[],
  uncertain_independence, evidence_family_revision
}
SourceReliabilityProfile {
  identity_ref, domain_scope, period_dr, supported_prior_assessments[],
  known_corrections[], observed_access_limits[], verified_conflicts[],
  reliability_state: CONTEXTUAL|INSUFFICIENT_DATA|DISPUTED,
  last_review_event_ref, acl, revision
}
ClaimAssessment {
  assessment_id, claim_id, verified_scope_fields[], excluded_scope_fields[],
  supporting_family_refs[], conflicting_family_refs[], unresolved_refs[],
  source_access_assessment, evidence_checks[], evaluator_rule_revision,
  state: UNVERIFIED|PARTIALLY_CORROBORATED|CORROBORATED_WITH_SCOPE|
         CONTRADICTED|INCONCLUSIVE|STALE,
  explanation_refs[], confidence_qualifier?, privacy_acl, checkpoint_epoch,
  review_authorization_ref?, assessment_revision, caused_by_event_ref
}
ObserverBelief {
  observer_ref, perceived_claim_ref, believed_status, known_sources[],
  last_learned_at_dr, communication_channel_ref, location_scope?,
  privacy_acl, belief_revision
}
```

IDs e enums são propostas de Discovery. Campos não conhecidos permanecem `UNKNOWN`, nunca preenchidos por criatividade da LLM. `EvidenceRecord` não pode ser fabricado a partir de texto sem comprovante ou fonte legítima. Referência a lore validado não prova que um NPC poderia conhecer esse lore.

## 4. Pipeline determinístico de avaliação

1. **Ingestão mínima:** validar `DeliveredReport` com prova de entrega, ator e escopo. Se não há entrega, **não** produzir `SourceClaim` como conteúdo recebido.
2. **Extração escopada:** estruturar afirmações atômicas por sujeito, atributo, local, tempo e natureza (observação, rumor, interpretação). A LLM local pode propor extração, sujeita a validação, não criar documentos ou pessoas.
3. **Fronteira de acesso:** verificar se fonte podia testemunhar ou receber legítima transmissão no intervalo DR; procurar `UNKNOWN` quando faltarem dados.
4. **Linhagem:** construir grafo de origem e transmissões; classificar cópias, citações de segunda mão, identidade compartilhada e ciclos. Fontes com raiz comum integram uma só `EvidenceFamily`.
5. **Corroboração:** comparar separadamente alegações de local, horário, participante, ação e documento. Uma evidência parcial não confirma toda a proposição.
6. **Conflito:** registrar evidências contraditórias e hipóteses concorrentes. Não confundir ausência de prova com prova negativa, nem anonimato com desonestidade.
7. **Contexto da fonte:** consultar desempenho verificável por domínio/época e motivos demonstrados, sem transformar reputação, cargo ou afiliação em probabilidade absoluta.
8. **Parecer:** produzir avaliação com referências autorizadas e estado revisável. Conclusão `INCONCLUSIVE` é válida e preferível a confiança inventada.
9. **Propagação restrita:** não divulgar automaticamente nada a NPCs, facções ou jogadores; emissão de dossiês e seus leitores ficam na DEC-090. Reações narrativas dependem de canal e permissões DEC-029/074/077.
10. **Consequências:** propostas mecânicas ou coercitivas acionam risk gate DEC-027, competência DEC-078–082, Action Gateway e host receipt, nunca apenas o estado de avaliação.

### Pseudocódigo candidato (não é implementação)

```python
def assess(report, viewer, checkpoint, rules):
    require_receipt(report.delivery_id)
    require_checkpoint_match(report, checkpoint)
    claims = extract_claim_candidates(report)        # sem autoridade da LLM
    for claim in validate_claims(claims):
        access = verify_epistemic_access(claim)
        lineage = trace_source_lineage(claim)
        families = group_by_independent_origin(lineage)
        evidence = filter_visible_evidence(families, viewer)
        contradictions = find_scoped_conflicts(claim, evidence)
        result = deterministic_epistemic_review(access, evidence, contradictions, rules)
        append_assessment_revision(claim, result, source_refs=evidence)
    # NÃO publicar, NÃO criar WorldFact, NÃO modificar engine.
```

Funções ilustrativas. A política final de revisão, edição humana autorizada, scores e tempos de reavaliação depende de SPECS. A filtragem do trecho exibido a um leitor não significa que a engine/narrativa adquirirá esse conhecimento.

## 5. Exemplo completo: três relatos sobre uma reunião

| Fonte | Alegação | Origem conhecida | Valor epistêmico inicial |
|---|---|---|---|
| **A** | Reunião amanhã, meia-noite, Armazém Norte | Declarou ter ouvido um oficial; acesso ainda não comprovado | `UNVERIFIED` |
| **B** | Reunião no Armazém Sul | Diz ter visto outro aviso; documento precisa ser confirmado | `UNVERIFIED` |
| **C** | Reunião no Armazém Norte | Ouviu exatamente de A | Família de origem **A**, não corroborador independente |

A e C **não** contam como duas provas de Norte. B diverge quanto ao lugar, não necessariamente quanto à existência da reunião. A hora 'amanhã' deve ser resolvida a partir da data absoluta do relato, evitando que o futuro se mova com cada consulta. **Estado apropriado sem novos dados:** `INCONCLUSIVE` e hipóteses distintas. Não criar evento de reunião no mundo por mera fala. Possíveis verificações futuras: observação válida do local, confirmação documental autenticada, recibo de evento de engine ou informação canônica curada pertinente ao ano e conhecida por meio admissível.

## 6. Revisões, falseamento e confiabilidade longitudinal

- Uma fonte pode corrigir a própria declaração; registrar `SourceClaim` original e evento `RETRACTED`, sem apagá-lo.
- Prova independente nova pode promover uma avaliação escopada de `UNVERIFIED` para `CORROBORATED_WITH_SCOPE`, mas não confirma campos que não foram investigados.
- Prova contraditória posterior pode devolver a conclusão para `INCONCLUSIVE` ou `CONTRADICTED`, conservando a cadeia anterior.
- A confiabilidade longitudinal do NPC é contextual: temas, época, acesso efetivo, histórico de confirmações e contradições. Nunca usar um número global fixo como detector mágico de mentira.
- Motivos e lealdades DEC-087 permitem formular hipóteses de viés, não declarar mentira ou traição como fato.
- O tempo de entrega, observação e validade do conteúdo são campos distintos. Rumores não se transformam em observações diretas após repetição.

## 7. Segurança e permissões por finalidade

| Consumidor | Informação disponível | Proibição |
|---|---|---|
| Auditor privado autorizado | Evidências e vínculos necessários ao parecer, com log seguro | Publicar segredos a NPC/cliente por acesso de auditoria |
| Jogador titular | Relatórios e fontes dentro de sua ACL | Ler identidade reservada de outro PC sem permissão |
| NPC investigador | O que observou/recebeu por canal causal | Consultar verdade privada do host ou outros NPCs |
| Facção | Declarações recebidas legitimamente | Difusão automática global de conclusões privadas |
| LLM local | Recorte autorizado, filtrado por campo | Completar origem, narrar como verdadeiro o que é incerto |
| Worker LAN | Dados mínimos conforme role, campanha e finalidade | Retirar fonte original de índice/telemetria fora de ACL |
| Engine BG2:EE/EEex | Apenas interações suportadas e testadas | Converter parecer em flags, facções, ataque ou quest livremente |

Redação aplicada a URLs, ID de fonte, arquivo, horário e localização, não só nome público. `UNKNOWN` explícito preserva a inteligibilidade mesmo quando fonte é omitida. Filtragem de relatórios deve evitar inferências indiretas por tamanho, ordenação ou contagem de prova confidencial.

## 8. Gates, falhas e reconciliação

| Falha | Resolução segura |
|---|---|
| Cadeia de origem desconhecida | `UNVERIFIED/INCONCLUSIVE`, sem contar fonte como independente |
| Origem circular A→B→A | Interromper traversal, marcar ciclo, sem sumarizar múltiplas provas |
| Contradição ainda não resolvida | Manter alternativas, não escolher pela fluência do texto |
| Ausência de documento alegado | Registrar afirmação sem validar existência mecânica do documento |
| Host receipt indisponível | `UNCERTAIN`; sem ação mecânica por suposição ou retry cego |
| Fonte identifica testemunha protegida sem autorização | Filtrar campo e contexto antes de indexar/gerar resposta |
| Informação de outro ano/branch | Rejeitar ou marcar `STALE`, sem importação retroativa |
| Novas provas após checkpoint | Nova revisão de avaliação; restore não mantém futuro |
| LLM gera certeza não sustentada | Validador determinístico rejeita e retorna estado anterior/inconclusivo |
| Overload de grafo/recursos | Priorizar jogo, paginar e executar offline; não simplificar tornando rumor verdade |

A decisão não exige rodar modelo por tick de NPC. `RuleRevision` e `AssessmentRevision` sustentam idempotência. Estado privado do host não é divulgado por mera conclusão do avaliador.

## 9. Matriz de validação futura — **84 testes candidatos NÃO EXECUTADOS**

Todos os resultados abaixo são **cenários esperados**, não observações empíricas, testes reais ou capacidades existentes.

| Caso | Grupo | Cenário / resultado esperado | Estado |
|---|---|---|---|
| T089-01 | Acesso da fonte e temporalidade | Fonte sem presença na cidade não vira testemunha ocular. | **NÃO EXECUTADO** |
| T089-02 | Acesso da fonte e temporalidade | Fonte com apenas rumores tem acesso limitado ao relato de terceiros. | **NÃO EXECUTADO** |
| T089-03 | Acesso da fonte e temporalidade | Fonte sem acesso a arquivo secreto não afirma ter lido documento válido. | **NÃO EXECUTADO** |
| T089-04 | Acesso da fonte e temporalidade | Dois atores homônimos não são equiparados por nome de persona. | **NÃO EXECUTADO** |
| T089-05 | Acesso da fonte e temporalidade | NPC dormindo não presencia evento sem mecanismo de observação legítimo. | **NÃO EXECUTADO** |
| T089-06 | Acesso da fonte e temporalidade | Informação de ano DR futuro não é usada na data atual. | **NÃO EXECUTADO** |
| T089-07 | Acesso da fonte e temporalidade | Relato "amanhã" mantém data absoluta de referência da transmissão. | **NÃO EXECUTADO** |
| T089-08 | Acesso da fonte e temporalidade | Conhecimento do host não é copiado para a memória do informante. | **NÃO EXECUTADO** |
| T089-09 | Acesso da fonte e temporalidade | Conversa privada sem participantes testemunhais não é conhecida globalmente. | **NÃO EXECUTADO** |
| T089-10 | Acesso da fonte e temporalidade | Fonte que viajou conserva evidência de quando e onde observou. | **NÃO EXECUTADO** |
| T089-11 | Acesso da fonte e temporalidade | Documento recebido após evento não é tratado como observado antes. | **NÃO EXECUTADO** |
| T089-12 | Acesso da fonte e temporalidade | Fonte com acesso duvidoso permanece UNVERIFIED sem preencher lacuna por LLM. | **NÃO EXECUTADO** |
| T089-13 | Origem, linhagem e independência | A e C compartilham mesma informação original e contam como uma família. | **NÃO EXECUTADO** |
| T089-14 | Origem, linhagem e independência | Cópia de documento idêntico não dobra peso de evidência. | **NÃO EXECUTADO** |
| T089-15 | Origem, linhagem e independência | Cadeia A→B→C preserva origem A em todos os relatos. | **NÃO EXECUTADO** |
| T089-16 | Origem, linhagem e independência | Ciclo A→B→A é detectado e não multiplica fontes. | **NÃO EXECUTADO** |
| T089-17 | Origem, linhagem e independência | Duas fontes observando independentemente um evento podem ser separadas mediante prova. | **NÃO EXECUTADO** |
| T089-18 | Origem, linhagem e independência | Fonte que muda de pseudônimo não se torna segunda testemunha independente. | **NÃO EXECUTADO** |
| T089-19 | Origem, linhagem e independência | Repostagem de rumor em duas guildas conserva a mesma origem. | **NÃO EXECUTADO** |
| T089-20 | Origem, linhagem e independência | Linhagem desconhecida permanece UNKNOWN, não independente por padrão. | **NÃO EXECUTADO** |
| T089-21 | Origem, linhagem e independência | Relato de pessoa que citou jornal não se soma ao próprio jornal como prova nova. | **NÃO EXECUTADO** |
| T089-22 | Origem, linhagem e independência | Documentos com hash diferente mas conteúdo copiado não são automaticamente independentes. | **NÃO EXECUTADO** |
| T089-23 | Origem, linhagem e independência | Fonte com referências circulares gera sinalização de conflito e contenção. | **NÃO EXECUTADO** |
| T089-24 | Origem, linhagem e independência | Ingestão repetida de mesmo evento não aumenta contagem de famílias. | **NÃO EXECUTADO** |
| T089-25 | Evidência, escopo e estados | Relatório entregue é registrado sem criar WorldFact. | **NÃO EXECUTADO** |
| T089-26 | Evidência, escopo e estados | Acordo ativo DEC-088 não confirma a veracidade da entrega. | **NÃO EXECUTADO** |
| T089-27 | Evidência, escopo e estados | Promessa sem entrega não cria avaliação de documento inexistente. | **NÃO EXECUTADO** |
| T089-28 | Evidência, escopo e estados | Relato parcialmente correto permanece PARTIALLY_CORROBORATED no recorte. | **NÃO EXECUTADO** |
| T089-29 | Evidência, escopo e estados | Local confirmado não valida automaticamente hora e participantes. | **NÃO EXECUTADO** |
| T089-30 | Evidência, escopo e estados | Ausência de prova não converte relato em falso. | **NÃO EXECUTADO** |
| T089-31 | Evidência, escopo e estados | Contradição no horário preserva local possivelmente correto. | **NÃO EXECUTADO** |
| T089-32 | Evidência, escopo e estados | Contradição entre fontes registra ambas sem escolher arbitrariamente. | **NÃO EXECUTADO** |
| T089-33 | Evidência, escopo e estados | Duas fontes de grupos independentes não bastam sem conteúdo e contexto admissíveis. | **NÃO EXECUTADO** |
| T089-34 | Evidência, escopo e estados | Fonte retrata alegação sem apagar seu registro e impactos já confirmados. | **NÃO EXECUTADO** |
| T089-35 | Evidência, escopo e estados | Relato proveniente de desinformação autorizada fica rotulado como PlantedClaim. | **NÃO EXECUTADO** |
| T089-36 | Evidência, escopo e estados | Parecer INCONCLUSIVE é resultado permitido sem confirmação automática. | **NÃO EXECUTADO** |
| T089-37 | Histórico e confiabilidade | Fonte que acertou anteriormente pode fornecer relato incorreto. | **NÃO EXECUTADO** |
| T089-38 | Histórico e confiabilidade | Fonte suspeita pode fornecer evidência documental válida. | **NÃO EXECUTADO** |
| T089-39 | Histórico e confiabilidade | Reputação social positiva não é selo de verdade. | **NÃO EXECUTADO** |
| T089-40 | Histórico e confiabilidade | Lealdade à guilda não é prova de desinformação deliberada. | **NÃO EXECUTADO** |
| T089-41 | Histórico e confiabilidade | Histórico por tema não é extrapolado universalmente. | **NÃO EXECUTADO** |
| T089-42 | Histórico e confiabilidade | Erro antigo retificado preserva contexto histórico da avaliação. | **NÃO EXECUTADO** |
| T089-43 | Histórico e confiabilidade | Alteração de confiabilidade não altera automaticamente fatos confirmados. | **NÃO EXECUTADO** |
| T089-44 | Histórico e confiabilidade | Conflito de interesse conhecido é registrado, não usado como culpa automática. | **NÃO EXECUTADO** |
| T089-45 | Histórico e confiabilidade | Incapacidade de verificar perfil retorna UNKNOWN. | **NÃO EXECUTADO** |
| T089-46 | Histórico e confiabilidade | Fonte coagida não recebe voluntariedade inventada. | **NÃO EXECUTADO** |
| T089-47 | Histórico e confiabilidade | Prova independente prevalece sobre mera afirmação de prestígio da fonte. | **NÃO EXECUTADO** |
| T089-48 | Histórico e confiabilidade | Estado de confiabilidade não é derivado de um escore inventado pela IA. | **NÃO EXECUTADO** |
| T089-49 | Segredos, ACL e agência | Identidade real do informante permanece oculta em relatório sem permissão. | **NÃO EXECUTADO** |
| T089-50 | Segredos, ACL e agência | Metadados de hora/rota que identificam refúgio são filtrados. | **NÃO EXECUTADO** |
| T089-51 | Segredos, ACL e agência | Sumário por LLM não revela alias privado sem autorização. | **NÃO EXECUTADO** |
| T089-52 | Segredos, ACL e agência | Log de erro não imprime identidade privada da fonte. | **NÃO EXECUTADO** |
| T089-53 | Segredos, ACL e agência | RAG não retorna documento fora do campo permitido. | **NÃO EXECUTADO** |
| T089-54 | Segredos, ACL e agência | Nó LAN sem privilégio recebe apenas conteúdo permitido. | **NÃO EXECUTADO** |
| T089-55 | Segredos, ACL e agência | Cliente de outro jogador não recebe segredo por estar na mesma party. | **NÃO EXECUTADO** |
| T089-56 | Segredos, ACL e agência | PC ausente não autoriza divulgação de histórico ou testemunho. | **NÃO EXECUTADO** |
| T089-57 | Segredos, ACL e agência | PC delegado mantém consentimento específico do titular. | **NÃO EXECUTADO** |
| T089-58 | Segredos, ACL e agência | Citação filtrada não expõe IDs reversíveis de fonte protegida. | **NÃO EXECUTADO** |
| T089-59 | Segredos, ACL e agência | Aviso de contradição não expõe texto proibido do depoimento de outra fonte. | **NÃO EXECUTADO** |
| T089-60 | Segredos, ACL e agência | Revogação de ACL invalida tarefas futuras e caches sem apagar conhecimento já adquirido legitimamente. | **NÃO EXECUTADO** |
| T089-61 | Consequências e autoridade | Informe UNVERIFIED não emite mandado por conta própria. | **NÃO EXECUTADO** |
| T089-62 | Consequências e autoridade | Rumor repetido não gera prisão, ataque ou sanção automática. | **NÃO EXECUTADO** |
| T089-63 | Consequências e autoridade | Avaliação CORROBORATED_WITH_SCOPE não altera inventário ou XP. | **NÃO EXECUTADO** |
| T089-64 | Consequências e autoridade | Acusação contra PC exige gates de risco e prova específica. | **NÃO EXECUTADO** |
| T089-65 | Consequências e autoridade | Informação de autoridade corrupta não vira verdade do host. | **NÃO EXECUTADO** |
| T089-66 | Consequências e autoridade | Fato mecânico exige receipt do host e capability verificada. | **NÃO EXECUTADO** |
| T089-67 | Consequências e autoridade | Proposta LLM de veredito não é publicada sem avaliação determinística. | **NÃO EXECUTADO** |
| T089-68 | Consequências e autoridade | Alegação falsa não altera facção mecânica ou alinhamento. | **NÃO EXECUTADO** |
| T089-69 | Consequências e autoridade | Erro de validação bloqueia ação HIGH e conserva suspeita como incerteza. | **NÃO EXECUTADO** |
| T089-70 | Consequências e autoridade | Disfarce não revela identidade verdadeira por heurística nominal. | **NÃO EXECUTADO** |
| T089-71 | Consequências e autoridade | Fonte que teme represália não gera emboscada automaticamente. | **NÃO EXECUTADO** |
| T089-72 | Consequências e autoridade | Dossiê futuro não é transmitido automaticamente a facções por avaliar relatório. | **NÃO EXECUTADO** |
| T089-73 | Persistência, limites e segurança | Restauração pré-relato não importa avaliação futura. | **NÃO EXECUTADO** |
| T089-74 | Persistência, limites e segurança | Branch alternativo não herda parecer secreto do ramo original. | **NÃO EXECUTADO** |
| T089-75 | Persistência, limites e segurança | Knowledge Pack atualizado não reescreve evento da campanha. | **NÃO EXECUTADO** |
| T089-76 | Persistência, limites e segurança | Correção cria revisão sem apagar alegação antiga. | **NÃO EXECUTADO** |
| T089-77 | Persistência, limites e segurança | Retry de entrega duplicada não duplica família de evidência. | **NÃO EXECUTADO** |
| T089-78 | Persistência, limites e segurança | Falha UNCERTAIN exige reconciliação sem retry cego. | **NÃO EXECUTADO** |
| T089-79 | Persistência, limites e segurança | Grafo de proveniência com ciclo é detectado sem loop infinito. | **NÃO EXECUTADO** |
| T089-80 | Persistência, limites e segurança | Grande volume de relatos respeita orçamento de memória e CPU. | **NÃO EXECUTADO** |
| T089-81 | Persistência, limites e segurança | Falta de LLM não bloqueia status INCONCLUSIVE por regras. | **NÃO EXECUTADO** |
| T089-82 | Persistência, limites e segurança | Resposta tardia de worker para checkpoint antigo é descartada. | **NÃO EXECUTADO** |
| T089-83 | Persistência, limites e segurança | Conteúdo de relatórios não é escrito em knowledge/periods/<ANO>-DR. | **NÃO EXECUTADO** |
| T089-84 | Persistência, limites e segurança | Integração host+2 clientes fica pendente até POC reproduzível por build. | **NÃO EXECUTADO** |

## 10. Plano de validação progressiva (futuro, não executado)

1. Criar fixtures sintéticas de A/B/C, cadeias de boatos, falsa independência, documentos forjados, acesso impossibilitado e fonte confiável porém enganada.
2. Implementar *prova offline* determinística para linhagem, dedup, `UNKNOWN`, estados escopados, correções append-only, perfil por domínio e revisão.
3. Auditar ACL com fontes confidenciais, nomes alternativos, dados indiretos, PCs ausentes/delegados, LLM, índices e workers LAN sem privilégio.
4. Testar clocks DR, restauração de checkpoint, branches concorrentes, caches stale, falhas `UNCERTAIN` e replay idempotente.
5. Inventariar capacidades reais BG2:EE limpo/EEex inicialmente read-only; só depois avaliar bridge mecânica em build isolada, host e dois clientes.
6. Medir latência, memória, limites de grafo, explicabilidade, não duplicação de famílias e a ausência de vazamento epistêmico.

## 11. Matriz de dependências e próxima DEC

- **DEC-060–063:** lore canônico fisicamente por ano DR, fontes curadas, pipeline de ingestão e KPack pinado.
- **DEC-064–075:** memória falível, identidades persistentes, comunicação temporal, atribuição/rumores e efeitos graduais.
- **DEC-076–088:** persona privada, investigação de pistas, justiça, proteção de fonte, contraespionagem, lealdades e entrega de informantes.
- **DEC-011/012/019/027/028/034/041/045/046/053–059:** host, gateway, riscos, consentimento, ACL, checkpoints, observabilidade e privacidade local-first.
- **DEC-006/007/013/015/017/018** permanecem abertas em seus escopos. Nada afirma detecção de mentira mecânica nem integração pronta.
- **DEC-090 aberta — dossiês e compartilhamento seletivo de inteligência.** A) repassar relatórios brutos universalmente a aliados; B) LLM decidir como compor/divulgar; **C recomendada:** dossiês rastreáveis, escopados e versionados, com citação de fontes permitidas, incerteza explícita, acesso por destinatário, publicação causal e opção de revisão/retificação.

## Integração DEC-090/C — Discovery v8.6

DossierClaim referencia avaliação/versão da DEC-089 e EvidenceFamily; mudar o formato do relatório não muda a qualidade probatória nem a crença de quem ainda não recebeu a view.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Qualidade da informação DEC-089 preserva dependência entre fontes, contraditórios e acesso epistêmico; nenhum threshold universal libera ataque.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Atualização de informe com nova evidência ou contradição dispara avaliação de impacto; famílias dependentes não contam como prova adicional.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Relatos sobre urgência ou disponibilidade não são considerados fatos do scheduler sem prova da fonte e validação independente; rumor não retira reserva.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Rumores ou informantes não fornecem prova de que um recurso físico esteja livre; disponibilidade é verificada por ledger/host.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Proposta DEC-096 separa história curada de claims/rumores incertos; evento publicado não torna relato do informante automaticamente verdadeiro ou contemporâneo.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Data de rumor DEC-096/C não se torna fato só por múltiplos informantes derivados da mesma origem; verificar independência.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Corroboração independente DEC-089 orienta proveniência de impacto DEC-097/C, impedindo contar três relatos da mesma origem.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Confiança de um informe não é recibo de spawn: a materialização só opera sob evidência mecânica e autorização host.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Informe de fonte sobre uma instância não equivale a owner receipt verificável.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Informes podem ser comparados com marcos autorizados, mas estado técnico não equivale a prova acessível ao NPC.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Quest state, mapping rule names and even flag metadata may expose future branches, romance or hidden identities; they remain private technical evidence. Dossiers, sources and NPCs receive only authorized safe milestones through independently confirmed disclosure; no belief is promoted to fact from ambiguous observations. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Conflito semântico DEC-102 não vira informe corroborado por mera observação técnica. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** a conclusão técnica de uma quest não concede automaticamente conhecimento ou crença a NPCs/facções. `QuestMilestoneAdmission` pode gerar proposta de notícia/reputação somente por regras, proveniência, tempo, geografia, visibilidade e ACL; notícia requer fonte/canal/delivery, e seus destinatários podem conhecer apenas versões parciais. Não expor identidades secretas, fontes protegidas ou raw flags por prompts/logs/dossiês. Ações mecânicas derivadas dependem de recibos host, sem atribuição presumida de PC. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **retificação da credibilidade sem apagar relato**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para corroboração independente, fonte única e confiança são distintas, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para informes têm origem e corroboração independentes, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Relatos repetidos não substituem receipts de host. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Corroboração por rumor não substitui o host receipt. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
