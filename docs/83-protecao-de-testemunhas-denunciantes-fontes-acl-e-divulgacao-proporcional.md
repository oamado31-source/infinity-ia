# 83 — Proteção de denunciantes, testemunhas e fontes: identidade, depoimentos, ACL e divulgação proporcional

**Discovery v7.9 — DEC-083/C aprovada; ADR-0078.** Especificação candidata de Discovery, **NÃO IMPLEMENTADA**. Todos os **70 testes T083-01..70 são candidatos e NÃO EXECUTADOS**.

## 1. Escopo e limites

**Objetivo:** permitir que investigações e procedimentos de justiça contextual (DEC-077–082) utilizem fontes confiáveis e contestáveis sem expor automaticamente identidades. Decidir separadamente quem pode consultar o **conteúdo**, **proveniência**, **identidade** e **avaliação de risco**. Propor cautelas de proteção sem criar invulnerabilidade ou mecânicas não testadas.

**Não objetivos:** criar lei uniforme contemporânea em Forgotten Realms; prometer tribunais, depoimentos forçados, proteção física, disfarce visual, prisão, transporte ou stealth engine, definir arbitrariamente absolvição/culpa, retirar agência de PCs ou fornecer anonimização matematicamente perfeita. DEC-084 discutirá respostas ativas a ameaças.

## 2. Fronteiras de confiança e dados

```text
knowledge/periods/<ANO>-DR/             # cânone físico por ano, DEC-060
  <categoria>/*                         # fontes curadas DEC-061/062; KPack DEC-063

campaign-overlays/<campaign>/<branch>/  # domínio lógico CANDIDATO, caminho físico não fixado
  protected-sources/                   # identidades/aliases DEC-066/076, sealed
  testimony/                           # versões de depoimentos, sem forçar identificação
  evidence/                            # proveniência/independência DEC-077
  permissions/                         # políticas e revisões ACL por campo
  access-audit/                        # decisões redigidas, sem segredos em claro
  disclosure-ledger/                   # audience, purpose, expiry, receipt, fencing
  threat-assessments/                  # ameaças alegadas/observadas e risco
  observer-beliefs/                    # narrativas de NPCs com informação limitada
```

O caminho `campaign-overlays` é **candidato**, não instalado. O banco canônico **não** incorpora depoimentos de campanha. DEC-060–082, todos os ADRs anteriores e os estados de decisões ainda abertas permanecem obrigatórios.

## 3. Contratos candidatos (não são APIs disponíveis)

```yaml
ProtectedSourceIdentity:
  campaign_id: string
  branch_id: string
  source_id: opaque
  actor_identity_id: opaque | null
  persona_refs: [opaque]
  identity_proof_refs: [opaque]
  source_kind: PC | NPC | INSTITUTIONAL | UNKNOWN
  owner_player_id: opaque | null
  scope_acl_ref: opaque
  protection_policy_revision: string
  lifecycle: SEALED | RESTRICTED | DISCLOSED_TO_SCOPE | UNKNOWN

TestimonyRecord:
  testimony_id: opaque
  investigation_id: opaque
  source_id_ref: opaque
  content_ref_sealed: opaque
  redacted_view_ref: opaque | null
  source_event_id: opaque | null
  world_time_dr: string
  created_revision: integer
  evidence_refs: [opaque]
  certainty: CLAIMED | CORROBORATED | CONTESTED | UNKNOWN
  statement_acl_ref: opaque

EvidenceProvenance:
  evidence_id: opaque
  origin_ref: opaque
  original_hash_ref: opaque | null
  evidence_chain_refs: [opaque]
  temporal_region_ref: opaque
  independence_group_ref: opaque | null
  authenticity: VERIFIED | PENDING | CHALLENGED | FALSE
  viewing_acl_ref: opaque

SourceProtectionPolicy:
  source_id: opaque
  privacy_class: SEALED | INVESTIGATOR_SCOPED | AUTHORITY_SCOPED | PARTY_SCOPED | PUBLIC_CLAIM_ONLY | PUBLIC_AUTHORIZED
  allowed_purposes: [opaque]
  allowed_audiences: [opaque]
  disallowed_exports: [opaque]
  consent_ref: opaque | null
  risk_caps_ref: opaque
  policy_revision: string

RetaliationRiskAssessment:
  source_id: opaque
  threat_evidence_refs: [opaque]
  alleged_adversary_refs: [opaque]
  severity: LOW | MEDIUM | HIGH | UNKNOWN
  confidence: CLAIMED | CORROBORATED | VERIFIED | UNKNOWN
  exposure_surface_refs: [opaque]
  gate_state: PENDING | ALLOWED | BLOCKED

DisclosureRequest:
  disclosure_id: opaque
  source_or_testimony_ref: opaque
  audience_scope: opaque
  purpose: opaque
  requested_fields: [opaque]
  authority_ref: opaque
  consent_ref: opaque | null
  risk_assessment_ref: opaque
  world_time_dr: string
  checkpoint_epoch: integer
  campaign_revision: integer
  rule_revision: string
  idempotency_key: string
  state: PROPOSED | DENIED | AUTHORIZED | UNCERTAIN | PUBLISHED

DisclosureReceipt:
  disclosure_id: opaque
  audience_scope: opaque
  published_redacted_payload_hash: string
  authorization_revision: string
  causal_event_id: opaque
  confirmation_ref: opaque
  ledger_revision: integer
```

Campos e algoritmos exatos serão especificados posteriormente. Referências opacas não são identidade pública nem prova de autorização. `VERIFIED` de prova não equivale a autoria ou culpa. Não existe API ou sistema implantado nesta etapa.

## 4. Separar as camadas epistemológicas

| Camada | O que comprova | O que NÃO comprova |
|---|---|---|
| Fonte identificada privadamente | Ator associado à fonte quando a prova é suficiente | Que todos têm direito ao nome |
| Depoimento recebido | Alguém apresentou uma afirmação | Que a afirmação é verdadeira |
| Prova autenticada | Integridade/proveniência da peça | Que a acusação foi comprovada |
| Risco de retaliação | Hipótese/probabilidade de exposição ou ameaça | Que a ameaça ocorreu ou quem é culpado |
| Divulgação autorizada | Conteúdo alcançou audiência específica | Publicidade global ou permanência da autorização |
| Consequência confirmada | Efeito causal conforme ledger/host | Mérito de outras alegações, direito a nova sanção |

## 5. Fluxo proposto de coleta, proteção e consulta

1. **Registrar origem e consentimento**: verificar se fonte é NPC/PC e se há ação voluntária autorizada, identity proof DEC-066, persona DEC-076 e competência DEC-078/082. Não inventar testemunhos do PC ausente.
2. **Fragmentar dados e políticas**: armazenar identidade separada do depoimento, do material comprobatório e do extrato publicável; aplicar ACL por campo/audiência/finalidade e revisão.
3. **Preservar cadeia de origem**: registrar se vários relatos derivam da mesma denúncia, autenticidade, cópias, cronologia, alterações e contradições DEC-061/077; não deduzir veracidade de sigilo.
4. **Avaliar exposição e risco**: adotar critérios com contexto local, capacidade do potencial adversário, existência de ameaças e público proposto; risco pode permanecer UNKNOWN; várias divulgações pequenas podem acumular exposição HIGH.
5. **Solicitar consulta**: recebedor apresenta função, competência, finalidade, escopo e campos necessários; caso `UNKNOWN`, suspender acesso a identidade, sem inviabilizar extratos filtrados quando autorizados.
6. **Filtrar antes do modelo**: consultar política de permissão antes de texto, RAG, cache, embedding, LAN, saída ou export. Redação protege também metadados indiretamente identificadores.
7. **Separar contraditório**: autoridade e acusado podem receber conteúdo/questões/proveniência no escopo permitido, mas não necessariamente o nome. Solicitar revelação é operação independente, com gate e contestação contextual.
8. **Propor divulgação**: `DisclosureRequest` com audiência, propósito, tempo, checkpoint, competência, consentimento aplicável, revisão, classificação e risco acumulado; LOW/MEDIUM/HIGH e default-deny de segredos críticos DEC-027.
9. **Publicar no escopo correto**: operação idempotente por ledger; quando pública, somente payload redigido autorizado. NPCs aprendem apenas por canal DEC-029/074, não pela existência do banco privado.
10. **Reconciliar e manter história**: falha/timeout `UNCERTAIN` não autoriza reenvio cego; revogação evita acessos futuros, mas não apaga crença legítima já recebida; logs de auditoria são minimizados.

## 6. Matriz de política de acesso (candidata)

| Destinatário | Identidade real | Extrato de prova | Material íntegro | Condição |
|---|---|---|---|---|
| Fonte titular (PC) | Seu próprio escopo legítimo | Conforme acesso do caso | Conforme direitos comprovados | Nunca revelar automaticamente segredos de terceiros |
| Investigador autorizado | Negado por padrão ou restrito | Pode receber versão redigida | Exige finalidade e competência | ACL/cadeia de evidência |
| Autoridade com competência comprovada | Solicitação separada | Conforme legislação contextual | Escopo mínimo | Risco, consentimento e autorização |
| Parte acusada | Não presumido | Extrato contestável quando permitido | Sem segredos desnecessários | Contraditório contextual, privacidade preservada |
| Outro PC da mesma party | Negado por padrão | Somente se permitido | Não presumido | DEC-019/041/045/046 |
| NPC/facção distante | Negado sem canal e ACL | Só notícia/alegação alcançada | Não presumido | DEC-029/074, cronologia |
| LLM/worker LAN | Contexto minimizado | Apenas filtro autorizado | Nunca por pareamento sozinho | Políticas DEC-058/059 |
| Logs/exports | Redigida | Hash/IDs opacos | Nunca por padrão | Retenção e auditoria |

## 7. Exemplo: funcionário da guilda em Athkatla

Um funcionário NPC, se isso se ajustar a suas motivações e conhecimento, oferece registros de pagamentos a um investigador. O investigador poderá ver os documentos e obter uma testemunha pseudônima em contexto permitido. A guilda investigada não recebe a identidade automaticamente. A autoridade que deseje revelar o nome precisa verificar competência, interesse probatório, risco acumulado, revogações e audiência, abrindo operação `DisclosureRequest`. Se a prova for contraditória, ela pode ser contestada sem assumir que o sigilo comprova a denúncia. Um risco de retaliação não invoca proteção física ou teleporte de NPC não implementado.

## 8. Falhas, restauração e contraexemplos

- **LLM em prompt sem filtro:** revelar nome no corpo da resposta é vazamento, mesmo se depois removido da UI; aplicar filtro antes da chamada, incluindo resumos e RAG.
- **Metadados reidentificantes:** anonimização textual não basta quando hora exata, cargo raro, rota e família revelam a fonte; bloquear ou generalizar se autorizado.
- **Cache público indevido:** ACL revogada deve invalidar consultas e jobs pendentes, não apagando a memória de uma pessoa que já teve acesso legítimo.
- **Worker revogado:** não aceitar publicação de resposta antiga; descartar cache e job da revisão anterior.
- **Save/restore:** efeitos e divulgações futuros de branch diferente não se aplicam; recibos precisam de checkpoint/epoch corretos.
- **Mecânica não comprovada:** não afirmar invisibilidade, proteção de HP, mudança de aparência, escort NPC, confisco de provas ou ação de host sem POCs.
- **Retaliação narrativa:** possíveis ameaças devem nascer de evidências/canais legítimos; atos coercitivos HIGH não são executados por rumor de ameaça.

## 9. Plano incremental futuro

1. Fixture sintética com três fontes, duas independentes e uma circular, documentos com e sem procedência, dois possíveis pseudônimos.
2. Testes de privacidade por campo, consentimento, funções de autoridade, redactions/metadados e cenários de falsa denúncia.
3. Audit trail seguro e ledger de disclosure idempotente, inclusive corrida de revogação e retry após timeout.
4. Roteador de modelos, índices, logs, APIs e trabalhadores LAN com redaction antes do processamento; testes adversariais de exfiltração.
5. Testar difusão de rumores por canais/relógio e integração com NPC memory DEC-064/065 em simulação offline.
6. Medir observabilidade real do motor por build, depois host+dois clientes, somente para capability específica; não inferir proteção física.
7. Produzir SPECS dos limiares e políticas de retenção, revisão humana, segurança de testemunhas e consentimento; até então efeitos HIGH bloqueados.

## 10. Matriz de testes — 70 cenários candidatos, TODOS NÃO EXECUTADOS

Nenhum teste abaixo comprova funcionamento da engine ou implementação; cada cenário é **critério futuro de aceitação**, exigindo fixtures, resultado esperado e revisão humana nas áreas críticas.

| ID | Teste candidato | Status |
|---|---|---|
| T083-01 | Criar depoimento confidencial não publica nome real da fonte. | NÃO EXECUTADO |
| T083-02 | Publicar versão anonimizada não expõe actor_identity_id. | NÃO EXECUTADO |
| T083-03 | NPC de outra facção sem ACL não recebe dados selados. | NÃO EXECUTADO |
| T083-04 | PC da mesma party sem escopo não lê depoimento protegido de terceiro. | NÃO EXECUTADO |
| T083-05 | Host autoritativo não transforma leitura de auditoria em conhecimento narrativo. | NÃO EXECUTADO |
| T083-06 | Investigador com papel válido recebe somente extrato autorizado. | NÃO EXECUTADO |
| T083-07 | Autoridade distante sem competência provada não obtém identificação. | NÃO EXECUTADO |
| T083-08 | Investigador com competência contestada fica bloqueado para identidade HIGH. | NÃO EXECUTADO |
| T083-09 | Pseudônimo público não é automaticamente vinculado ao ator privado. | NÃO EXECUTADO |
| T083-10 | Homônimo de fonte não é correlacionado por nome de recurso ou retrato. | NÃO EXECUTADO |
| T083-11 | Fonte com identidade não verificada fica UNKNOWN sem associação definitiva. | NÃO EXECUTADO |
| T083-12 | PC ausente não é obrigado pela IA a denunciar ou testemunhar. | NÃO EXECUTADO |
| T083-13 | Controlador delegado não recebe direito de revelar segredo do titular. | NÃO EXECUTADO |
| T083-14 | Depoimento gerado por LLM sem autorização de PC é rejeitado. | NÃO EXECUTADO |
| T083-15 | NPC pode prestar relato dentro de conhecimento e agency sem fatos fabricados. | NÃO EXECUTADO |
| T083-16 | Várias cópias da mesma denúncia não contam como corroboradoras independentes. | NÃO EXECUTADO |
| T083-17 | Fontes distintas com prova independente mantêm proveniência separada. | NÃO EXECUTADO |
| T083-18 | Documento falso permanece alegação, sem comprovar instituição corrupta. | NÃO EXECUTADO |
| T083-19 | Contraprova é registrada sem apagar depoimento anterior. | NÃO EXECUTADO |
| T083-20 | Testemunha mentirosa não reescreve fatos mecânicos confirmados. | NÃO EXECUTADO |
| T083-21 | Confidencialidade da fonte não equivale a prova de credibilidade. | NÃO EXECUTADO |
| T083-22 | Suspeita de retaliação não afirma que houve ataque efetivo. | NÃO EXECUTADO |
| T083-23 | Ameaça confirmada não implica culpa global da instituição. | NÃO EXECUTADO |
| T083-24 | Avaliação de risco considera o alcance da audiência e do canal. | NÃO EXECUTADO |
| T083-25 | Risco acumulado de duas divulgações LOW exige novo gate quando alcançar HIGH. | NÃO EXECUTADO |
| T083-26 | Revelação pública HIGH é recusada por padrão sem autorização. | NÃO EXECUTADO |
| T083-27 | Pedido com destinatário indefinido não é autorizado. | NÃO EXECUTADO |
| T083-28 | Pedido com finalidade ausente não é autorizado. | NÃO EXECUTADO |
| T083-29 | Destinatário válido só recebe conteúdo estritamente necessário. | NÃO EXECUTADO |
| T083-30 | Competência válida em outra época não autoriza acesso no ano DR atual. | NÃO EXECUTADO |
| T083-31 | Evento de ano futuro não revela identidade em ano anterior. | NÃO EXECUTADO |
| T083-32 | Clock FROZEN impede propagação de informação não permitida. | NÃO EXECUTADO |
| T083-33 | Canal de comunicação indisponível mantém entrega pendente. | NÃO EXECUTADO |
| T083-34 | Entrega a uma autoridade não faz notícia chegar instantaneamente a outra. | NÃO EXECUTADO |
| T083-35 | Nova revisão de ACL invalida job pendente com autorização antiga. | NÃO EXECUTADO |
| T083-36 | Revogação de acesso bloqueia consultas futuras, sem apagar memórias legítimas. | NÃO EXECUTADO |
| T083-37 | Cache com segredo é invalidado após revogação/branch change. | NÃO EXECUTADO |
| T083-38 | Índice de busca não revela ID confidencial em resultados não autorizados. | NÃO EXECUTADO |
| T083-39 | Prompt enviado à LLM contém somente persona e conteúdo minimizados. | NÃO EXECUTADO |
| T083-40 | Fallback para modelo alternativo não contorna ACL. | NÃO EXECUTADO |
| T083-41 | Worker LAN pareado sem role não recebe prova confidencial. | NÃO EXECUTADO |
| T083-42 | Worker LAN revogado não publica resposta antiga com segredo. | NÃO EXECUTADO |
| T083-43 | Log de erro de acesso negado não inclui nome da testemunha. | NÃO EXECUTADO |
| T083-44 | Export de investigação remove metadados indiretos altamente identificadores. | NÃO EXECUTADO |
| T083-45 | Relação entre cargo raro/rota/hora é tratada como risco de reidentificação. | NÃO EXECUTADO |
| T083-46 | Anonimização com insuficiência de proteção é sinalizada e bloqueada. | NÃO EXECUTADO |
| T083-47 | Restauração de branch anterior não herda revelação futura. | NÃO EXECUTADO |
| T083-48 | Divulgação de outro branch não se aplica à campanha atual. | NÃO EXECUTADO |
| T083-49 | Duplo envio de mesma divulgação não multiplica efeito reputacional. | NÃO EXECUTADO |
| T083-50 | Timeout de publicação gera UNCERTAIN e reconciliação sem retry cego. | NÃO EXECUTADO |
| T083-51 | Ledger de divulgação preserva revisão, audiência e cadeia causal. | NÃO EXECUTADO |
| T083-52 | Recepção de relato não concede reputação mecânica de BG2 automaticamente. | NÃO EXECUTADO |
| T083-53 | Proteger a testemunha não concede HP, invisibilidade ou imortalidade. | NÃO EXECUTADO |
| T083-54 | Plano narrativo de abrigo não teleporta ator na engine. | NÃO EXECUTADO |
| T083-55 | Escolta narrativa não movimenta NPC sem capability do host. | NÃO EXECUTADO |
| T083-56 | NPC perseguidor não recebe localização confidencial pelo diretor. | NÃO EXECUTADO |
| T083-57 | Confisco de documentos não ocorre por intenção de LLM. | NÃO EXECUTADO |
| T083-58 | Alteração de quest vinculada a fonte requer gateway e receipt host. | NÃO EXECUTADO |
| T083-59 | Migração de build/mod invalida capability mecânica antiga. | NÃO EXECUTADO |
| T083-60 | Arquivo canônico por ano DR não recebe depoimento da campanha. | NÃO EXECUTADO |
| T083-61 | Knowledge Pack pinado não recebe vazamento de identidade privada. | NÃO EXECUTADO |
| T083-62 | Evento de retaliação HIGH exige autorização e não é disparado por rumor. | NÃO EXECUTADO |
| T083-63 | Proteção de testemunha não impõe decisão voluntária a PC. | NÃO EXECUTADO |
| T083-64 | Fonte NPC pode recusar depoimento respeitando conhecimento e objetivos. | NÃO EXECUTADO |
| T083-65 | Contexto de investigação permite contestar prova sem revelar nome selado. | NÃO EXECUTADO |
| T083-66 | Conflito insolúvel de proveniência termina PENDING_EVIDENCE sem condenação. | NÃO EXECUTADO |
| T083-67 | Backpressure adia entrega sem abrir ACL ou descartar segredo. | NÃO EXECUTADO |
| T083-68 | Backup/restauração mantém ACL da fonte e invalidadores de revogação. | NÃO EXECUTADO |
| T083-69 | Host+dois clientes é gate obrigatório para alegar qualquer integração mecânica. | NÃO EXECUTADO |
| T083-70 | POC read-only não implica proteção física, detecção ou ocultação implementadas. | NÃO EXECUTADO |

## 11. DEC-084 — Próxima escolha em aberto

**Medidas de proteção ativa e resposta à retaliação contra denunciantes/testemunhas.** A) tornar protegidos invulneráveis e transportá-los automaticamente; B) permitir reação/perseguição/proteção livres do LLM; **C (recomendada)** registrar ameaças por evidência, classificar urgência e risco, oferecer escolta/abrigo/realocação narrativos ou mecânicos somente com recursos, consentimento, cronologia, autoridade e capability do host comprovados. Sem obrigação de sucesso, sem coerção automática, sem spawn/teleporte não validado.

## Integração DEC-084/C — Discovery v8.0

DEC-084 complementa o sigilo de fonte com medidas ativas graduais: avaliar ameaça, planejar abrigo/escolta sem invulnerabilidade, recursos/presença verificados e resultados só com receipts host. Próxima DEC-085 tratará sigilo operacional.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

DEC-085 especifica segredo por campo e descobertas parciais, inclusive vazamento indireto por metadata; disclosure autorização e evidência não concedem identidade privada universal.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Isca defensiva não revela a identidade privada da fonte ou metadados que a reidentifiquem; consentimento e ACL por destinatário continuam necessários.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Fonte que informa sobre espionagem mantém proteção de identidade, depoimento e ACL; alegação de traição não justifica expor o denunciante.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Identidade do informante e termos são selados por finalidade/audiência; entregar relato filtrado não exige expor fonte a todo o grupo.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Identidade de fonte é separada do conteúdo do depoimento e da avaliação; variações de metadados podem identificar a pessoa e precisam de filtro.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

DossierDisclosureView deve minimizar inclusive metadados que reidentificam fontes protegidas; competência da autoridade não dispensa ACL e consentimento quando aplicáveis.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Fontes protegidas não são expostas em plano ou apresentação sem autorização; metadados e recursos também são sensíveis.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Plano revisto para entrevistar fonte exige ACL, consentimento e preservação de depoimentos filtrados; não divulgar identidades pelo diff.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Conflito de agenda de testemunha/guarda não divulga identidade nem local de refúgio; relatórios de disponibilidade são redigidos por público.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Logs de conflito sobre escolta ou abrigo devem omitir identidade de testemunha e localização; starvation não desclassifica sigilo.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

DEC-096: cronologia de grande evento não concede acesso a refúgios/identidade de testemunha pela simples coincidência de época.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Marcadores da matriz DEC-096/C não expõem rotas/refúgios/testemunhas através de logs, perfis de local ou prompts.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Composição DEC-097/C não expõe rotas/identidades protegidas em logs de metrics ou contexto da LLM.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Identidade de fonte protegida pode existir no registry privado, mas materialização não pode expô-la por UI/log/cliente não autorizado.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Metadados de ownership podem conter identidades de fontes; ACL e logs seguros necessários.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Proteção de testemunhas inclui metadados de quests e aliases reveláveis em flags/scripts.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Quest state, mapping rule names and even flag metadata may expose future branches, romance or hidden identities; they remain private technical evidence. Dossiers, sources and NPCs receive only authorized safe milestones through independently confirmed disclosure; no belief is promoted to fact from ambiguous observations. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** a conclusão técnica de uma quest não concede automaticamente conhecimento ou crença a NPCs/facções. `QuestMilestoneAdmission` pode gerar proposta de notícia/reputação somente por regras, proveniência, tempo, geografia, visibilidade e ACL; notícia requer fonte/canal/delivery, e seus destinatários podem conhecer apenas versões parciais. Não expor identidades secretas, fontes protegidas ou raw flags por prompts/logs/dossiês. Ações mecânicas derivadas dependem de recibos host, sem atribuição presumida de PC. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **privacidade de fontes**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para proteção de fontes e testemunhas exige redação e ACL pré-difusão, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para privacidade de fontes e testemunhas, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Fontes protegidas permanecem confidenciais no acompanhamento. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Fontes protegidas não são reveladas pelo grafo. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
