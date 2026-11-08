# DEC-084 — Proteção ativa de fontes: ameaças, abrigo, escolta e reconciliação segura

**Discovery v8.0 · ADR-0079 · DEC-084/C APROVADA somente como arquitetura; NÃO IMPLEMENTADA.**
**Validação:** 72 testes candidatos `T084-01..72` **NÃO EXECUTADOS**. Nenhuma capacidade mecânica de proteção no BG2:EE/EEex/multiplayer foi comprovada.

## 1. Objetivo e fronteiras

Definir **propostas de resposta gradual** a ameaças e retaliações contra testemunhas/denunciantes sob DEC-083, sem prometer invulnerabilidade, deslocamento imediato, captura, escolta gerada por IA ou NPCs oniscientes. Vincular ameaças aos sistemas de evidência DEC-077/078/082, risco DEC-027/034, identidade/ACL DEC-019/028/066/076/083 e NPCs/itinerários DEC-068–073. Respeitar autoridade mecânica DEC-011/012 e os gates das DEC-050/051/053/055/056.

Ameaça **alegada** pode justificar cautela limitada quando aprovada; não se deve tratá-la como agressão **confirmada** nem culpa do suposto agressor. As decisões técnicas exatas (pontos numéricos, adapters, engine hooks e modelos de simulação) ficam para SPECS/POCs.

## 2. Domínios de dados segregados

```text
knowledge/periods/<ANO>-DR/                   # cânone curado fisicamente por ano: DEC-060–063

campaign-overlays/<campaign>/<branch>/          # DOMÍNIO LÓGICO ILUSTRATIVO; SPECS definirá o armazenamento
  protected-sources/                          # referência sigilosa DEC-083, nunca pública por padrão
  threats/<threat_case_id>/
    reports/                                  # alegações com provenance, sem afirmação automática de fato
    evidence/                                 # provas, fontes e contradições, ACL
    assessments/                              # risco, vulnerabilidades, políticas de versão
    protection-requests/                     # titular/consentimento/competência
    plan-revisions/                          # opções, rotas, recursos, autorizações
    leases/                                  # reservas, fencing e expiração controlada
    action-receipts/                         # host confirmando apenas fatos observáveis
    reconciliations/                         # save/load, branch, crash, falhas e resultados
    observer-beliefs/                         # rumores/crenças, não conhecimento universal
```

A árvore de overlays é candidata, **não um backend já implantado**. Os dados de campanha não são migrados para o lore canônico de nenhum ano DR.

## 3. Contratos candidatos — não são APIs executáveis

```yaml
ThreatReport:
  campaign_id: string
  branch_id: string
  threat_case_id: string
  report_id: string
  protected_source_id: opaque_reference
  reported_perpetrator_or_faction_id: optional_opaque_reference
  claim: narrative_claim
  source_ref: protected_reference
  occurred_or_reported_at_dr: world_time_reference
  origin_region_ref: optional_region_reference
  evidence_refs: [protected_reference]
  epistemic_status: ALLEGED|CORROBORATED|DISPUTED|CONFIRMED|UNKNOWN
  acl_policy_ref: protected_reference

ThreatAssessment:
  threat_case_id: string
  assessment_revision: integer
  source_report_refs: [opaque_reference]
  risk_class: LOW|MEDIUM|HIGH|UNKNOWN
  evidence_confidence: UNVERIFIED|CORROBORATED|CONFIRMED|DISPUTED
  vulnerability_factors: [curated_rule_reference]
  adversary_resource_evidence_refs: [protected_reference]
  location_and_time_constraints: [rule_reference]
  cumulative_risk_refs: [opaque_reference]
  assessed_with_policy_revision: string
  state: PENDING_EVIDENCE|ASSESSED|BLOCKED_UNCERTAIN

ProtectionRequest:
  protection_case_id: string
  requested_for_actor_identity_id: protected_reference
  requested_by_actor_or_authority_id: protected_reference
  consent_ref: optional_reference
  authority_scope_ref: optional_reference
  campaign_branch_checkpoint_ref: protected_reference
  request_status: PROPOSED|CONSENT_PENDING|AUTHORIZED|DENIED|STALE

ProtectionPlan:
  protection_case_id: string
  plan_revision: integer
  threat_assessment_ref: protected_reference
  candidate_actions: [DISCRETION|VERIFY|SEEK_SHELTER|REQUEST_ESCORT|RELOCATE|CONTACT_ALLIES|NO_OP]
  actor_identity_refs: [protected_reference]
  required_resource_refs: [opaque_reference]
  location_route_refs: [sensitive_route_reference]
  consent_and_authorization_refs: [protected_reference]
  risk_gate_ref: protected_reference
  clock_mode: FROZEN|PARTIAL|REALTIME
  build_fingerprint: optional_string
  checkpoint_epoch: integer
  execution_capability_ref: optional_reference
  state: PROPOSED|GATED|RESERVED|ACTION_PENDING|UNCERTAIN|RECONCILED|CLOSED

ProtectionActionReceipt:
  protection_case_id: string
  action_id: string
  idempotency_key: string
  action_kind: typed_action
  authority_kind: HOST_ENGINE|NARRATIVE_RULES
  host_receipt_ref: optional_protected_reference
  resolution_epoch: integer
  observed_state_ref: protected_reference
  state: REQUESTED|CONFIRMED|REJECTED|UNCERTAIN
```

Os campos são ilustrações de contratos, não identificação de capacidades disponíveis no motor, nomes de tabelas implantadas nem endpoints. Metadados mais sensíveis devem ser referenciados por identificadores opacos e sujeitos a ACL.

## 4. Máquina de estados candidata e invariantes

```text
THREAT_REPORTED
    |-- evidence/ACL --> THREAT_ASSESSED (ou PENDING_EVIDENCE/DISPUTED)
    |-- proposta --> PROTECTION_PROPOSED
    |-- competência/consentimento --> GATED
    |-- disponibilidade/recursos --> RESERVATION_PENDING
    |-- reserva exclusiva --> RESERVED
    |-- ação narrativa autorizada OR ação host suportada --> ACTION_PENDING
    |-- receipt e reobservação --> RECONCILED
    |-- resultado confirmado/encerramento seguro --> CLOSED

Exceções: DENIED, UNSUPPORTED, NO_RESOURCES, NO_ROUTE, NOT_CONSENTED,
           BLOCKED_HIGH_RISK, STALE, UNCERTAIN, ABORTED_WITHOUT_EFFECTS.
```

**Invariantes:**

1. `ThreatReport` é declaração de fonte; risco é avaliação; `ProtectionActionReceipt` é confirmação de operação autorizada. Não converter relatos ou planos em resultados.
2. Um caso pode ter múltiplos planos/revisões, mas ação efetiva não é duplicada por reentrega ou múltiplas fontes.
3. Um único `incident_id` não é resolvido simultaneamente no sistema fora de cena e na área local (DEC-070/071).
4. Efeito de engine (HP, inventário, presença, spawn, deslocamento, morte, combate, quest) exige host receipt e adapter validado pelo build, não LLM.
5. Toda medida respeita ACL de identidade/rota e privacidade do PC; a parte pública do plano não expõe refúgio nem horários secretos.
6. Em `UNCERTAIN`, `STALE`, build/branch/checkpoint divergente ou ausência de proof-of-capability: parar, reconciliar e não repetir ações destrutivas.
7. NPC só pode atuar se houver recursos, região, tempo e identidade confirmados; ausência de agente não é motivo para surgimento arbitrário.
8. Retaliação HIGH é falha fechada; não confundir possibilidade narrativa com autorização para matar/capturar testemunha.

## 5. Avaliação de ameaças

| Informação recebida | Evidência | Interpretação | Ação segura candidata |
|---|---|---|---|
| Boato de pessoas procurando testemunha | Sem fontes independentes | `ALLEGED` | Verificar, manter discrição, nunca gerar perseguidor mecânico |
| Avisos independentes com procedência | Parcialmente corroborados | `CORROBORATED` | Planejar proteção de baixo impacto sob política/consentimento |
| Ataque confirmado pelo host | Receipt mecânico com origem verificável quando disponível | `CONFIRMED` para o fato do ataque, não necessariamente para a autoria | Registrar dano, classificar risco, opções de proteção e resposta sem duplicar combate |
| Suspeita de conluio de protetor | Evidência contestada | `DISPUTED` | Não dar acesso irrestrito a planos/segredos; buscar proteção alternativa |
| Informação de outro branch ou época | Revisão incompatível | `STALE` | Rejeitar/retificar a proposta sem alterar mundo atual |

A classificação do risco não decide sozinha que o alegado agressor é culpado ou que haverá confronto. Coerência com DEC-077/078/082, provas de canais e reputação DEC-029/030/074.

## 6. Medidas candidatas e gates por tipo

| Medida proposta | Requisitos | Capacidade e restrição |
|---|---|---|
| Sigilo operacional | Política DEC-083, ACL e contexto mínimo | Não remove conhecimento prévio de NPCs nem prova invisibilidade |
| Pedir ajuda/protetor | Autoridade legítima, consentimento, disponibilidade do NPC | Não cria guarda do nada, não obriga NPC a aceitar |
| Procurar abrigo | Lugar plausível e acessível, direitos e recursos | Não significa estar mecanicamente dentro do local sem receipt |
| Escolta | Protetores existentes, itinerário, disponibilidade e recursos reservados | Não produz combate/transferência se adapter não for testado |
| Realocação | Rota, tempo, risco, novo contexto e consentimento | Sem teleporte, sem alterar NPC em save diretamente |
| Alerta limitado | Emissor, destinatário, canal e ACL | Não publica identidade nem posição a todos |
| Investigação de ameaça | Pistas/identidades verificadas DEC-077 | Não cria ataque nem punição por denúncia |
| Reação a ataque local | Handoff DEC-070/071, gateway host, risk gate | Somente capabilities demonstradas e receipt host; HIGH default-deny |

## 7. Autoridade, recursos, geografia e orçamento

- **Agente protegido:** PC com titular/controle/consentimento, NPC com identidade lógica e motivos; nenhum PC forçado a fugir ou testemunhar.
- **Protetor:** ator com capacidade contextual comprovada, localização, agenda, disponibilidade e possível conflito de interesse; não presumir guilda confiável.
- **Autoridade:** política por região e ano DR, fonte curada DEC-060–063/078–082, sem um direito internacional universal inventado.
- **Recursos:** abrigo, suprimentos, transporte e escolta precisam de recursos pré-existentes verificados; reservas por lease/fencing e quotas DEC-056.
- **Tempo:** DEC-022, DEC-068/069 definem clocks e atividades; rotas têm condições/restrições. Narrativa de chegada não é presença física comprovada.
- **Adversários:** apenas recursos e informações adquiridos por canais legítimos. Não há detector de safehouse global; a DEC-085 decidirá sigilo e descoberta adversarial de planos.

## 8. Ações fora de cena e encontro local

Uma ameaça ou possível emboscada pode ser simulada narrativamente em níveis distantes somente sob DEC-070. Ao entrar em área jogável, handoff DEC-071 exige presença validada, reserva exclusiva, incident lease, epochs e receipts. DEC-072 não permite scripts dinâmicos não testados ou spawn arbitrário. Encerrar encontros mantém consequências e prova DEC-073 sem apagar NPC protegido.

## 9. ACL, sigilo, coerência e privacidade

- Identidade, pseudônimo, rota, refúgio, agenda de escolta e testemunhos podem permitir reidentificação mesmo após substituir nomes. Filtrar metadados e não só o texto.
- `ProtectedSourceIdentity`, `ProtectionPlan`, logs, cache, índices, workers LAN e prompts respeitam ACL por finalidade, ator e campanha. Uma conta de host possui autoridade sobre ações mecânicas, não conhecimento automático de todas as personas no universo narrativo.
- Agentes que não receberam a informação não a usam como motivação. O plano de proteção não é uma fonte pública para um perseguidor. Não simular que ele ouviu sem canal causal.
- Estado de revogação, segredo descoberto ou plano alterado não apaga memória histórica de NPC; retificações seguem DEC-064/080.
- Tratamento de casos sensíveis mantém trilha auditável redigida para operação, com separação física canônica por ano DR e overlays de campanha por ramo.

## 10. Falhas, checkpoint e observabilidade

| Falha | Resposta fail-closed |
|---|---|
| `UNCERTAIN` após pedido mecânico | Consultar host e recibo antes de qualquer retry; não duplicar escolta ou viagem |
| `STALE` após restore | Invalidar plano pendente de outro checkpoint/branch; não importar futuro |
| Protetor indisponível | Negar reserva, não materializar NPC |
| Abrigo sem evidência de existência/acesso | Proposta bloqueada ou apenas ficção declarada sem efeito de engine |
| Adversário sem canal válido | Sem descoberta implícita da rota/fonte |
| Conhecimento de fonte vazou legitimamente | Preservar memória do observador e gerir risco, não reverter ficção à força |
| Incompatibilidade de mod/build | Invalidar adapters e não executar ação mecânica |
| Falha em proteção HIGH | Não aplicar captura/morte/repercussão irreversível por narrativa automática; encaminhar gate |

Observabilidade monitora pendências, custos e risco sem logar rotas/identidades em claro para destinatários não autorizados.

## 11. Sequência de POCs futuras

1. Fixtures sintéticas com rumor falso, testemunha protegida, guilda hostil, abrigo, escolta, NPC indisponível, recusas e segredo vazado.
2. Testes unitários determinísticos de risco, ACL, provenance, consentimento, plano versionado, rota/tempo e idempotência.
3. Simulação concorrente, crash, restore, branch e falso `CONFIRMED` sem host; validar fail-closed.
4. Inventário read-only das capacidades BG2:EE limpo + EEex/bridge por build: NPC identity, estado, localização, logs e limites.
5. POC em sandbox isolado de ação mecânica *benigna* apenas se adapter testado, com checkpoints/restauração, não em saves reais.
6. Host+dois clientes e configuração de mods; nenhuma capability declarada sem evidência e decisão release DEC-015.

## 12. Matriz de testes candidatos — 72 casos, nenhum executado

| ID | Cenário esperado | Execução |
|---|---|---|
| T084-01 | Ameaça apenas relatada é ALLEGED, não ataque confirmado. | NÃO EXECUTADO |
| T084-02 | Depoimento corroborado não identifica automaticamente o agressor. | NÃO EXECUTADO |
| T084-03 | Informação de facção hostil sem prova não gera perseguição mecânica. | NÃO EXECUTADO |
| T084-04 | Risco HIGH preventivo não converte acusação em culpa factual. | NÃO EXECUTADO |
| T084-05 | Prova contraditória mantém avaliação DISPUTED até revisão. | NÃO EXECUTADO |
| T084-06 | Ameaça falsa pode permanecer como rumor com fonte rastreada. | NÃO EXECUTADO |
| T084-07 | Identity de PC homônimo não vincula alvo por nome. | NÃO EXECUTADO |
| T084-08 | Persona sob pseudônimo permanece sigilosa sem divulgação autorizada. | NÃO EXECUTADO |
| T084-09 | Fonte protegida recebe plano apenas dentro da ACL aplicável. | NÃO EXECUTADO |
| T084-10 | PC ausente não aceita escolta automaticamente. | NÃO EXECUTADO |
| T084-11 | PC delegado não tem segredo do titular exposto por default. | NÃO EXECUTADO |
| T084-12 | NPC pode recusar abrigo sem violar agência de PC. | NÃO EXECUTADO |
| T084-13 | LLM não decide vontade ou confissão de PC. | NÃO EXECUTADO |
| T084-14 | Plano narrativo de abrigo não altera presença física na engine. | NÃO EXECUTADO |
| T084-15 | Medida de discrição narrativa não concede invisibilidade mecânica. | NÃO EXECUTADO |
| T084-16 | Nenhuma invulnerabilidade é aplicada por política narrativa. | NÃO EXECUTADO |
| T084-17 | Deslocamento proposto não produz teleporte. | NÃO EXECUTADO |
| T084-18 | Rota inviável bloqueia transferência física. | NÃO EXECUTADO |
| T084-19 | Viagem respeita relógio FROZEN sem avanço indevido. | NÃO EXECUTADO |
| T084-20 | Viagem respeita modo PARTIAL e limite de catch-up. | NÃO EXECUTADO |
| T084-21 | Viagem respeita modo REALTIME dentro do scheduler. | NÃO EXECUTADO |
| T084-22 | Escolta exige disponibilidade do NPC protetor verificada. | NÃO EXECUTADO |
| T084-23 | NPC protetor que está em outra área não surge sem presença confirmada. | NÃO EXECUTADO |
| T084-24 | Recurso de abrigo ocupado não pode ser duplicado por replanejamento. | NÃO EXECUTADO |
| T084-25 | Protetor de outra facção exige autorização/competência pertinente. | NÃO EXECUTADO |
| T084-26 | Autoridade suspeita não obtém automaticamente nome da fonte. | NÃO EXECUTADO |
| T084-27 | Papel administrativo LAN não concede acesso ao esconderijo. | NÃO EXECUTADO |
| T084-28 | Logs de auditoria não incluem nome e rota em claro para papéis não autorizados. | NÃO EXECUTADO |
| T084-29 | Prompt enviado a modelo não contém identidade secreta desnecessária. | NÃO EXECUTADO |
| T084-30 | Índice/caches respeitam escopo de campanha e ACL da rota. | NÃO EXECUTADO |
| T084-31 | Revogação de permissão invalida jobs futuros de divulgação. | NÃO EXECUTADO |
| T084-32 | Divulgação já conhecida por NPC não é apagada magicamente da memória. | NÃO EXECUTADO |
| T084-33 | Guardas antagonistas sem canal de notícia não conhecem destino da fonte. | NÃO EXECUTADO |
| T084-34 | Ameaça real validada ainda precisa de recursos do antagonista. | NÃO EXECUTADO |
| T084-35 | NPC agressor não ganha teleporte para interceptar escolta. | NÃO EXECUTADO |
| T084-36 | Rumor de agressor não gera ataque ou dano mecânico. | NÃO EXECUTADO |
| T084-37 | Emboscada HIGH não é autorizada por LLM. | NÃO EXECUTADO |
| T084-38 | Risco agregado de várias medidas LOW exige reclassificação se atingir HIGH. | NÃO EXECUTADO |
| T084-39 | Plano proteção para jogador não pode induzir PvP sem consentimento. | NÃO EXECUTADO |
| T084-40 | Solicitação de escolta não confere recursos infinitos. | NÃO EXECUTADO |
| T084-41 | Leases concorrentes impedem duas reservas do mesmo guarda. | NÃO EXECUTADO |
| T084-42 | Reentrega de solicitação não cria duas escoltas. | NÃO EXECUTADO |
| T084-43 | Save/load com plano pendente exige revalidar recursos. | NÃO EXECUTADO |
| T084-44 | Crash durante deslocamento com receipt incerto bloqueia replay cego. | NÃO EXECUTADO |
| T084-45 | Restore de branch antigo descarta movimento do futuro abandonado. | NÃO EXECUTADO |
| T084-46 | Build mismatch invalida adapter de movimento ou presença. | NÃO EXECUTADO |
| T084-47 | Host receipt de outra campanha não confirma acolhimento. | NÃO EXECUTADO |
| T084-48 | Cliente multiplayer não é autoridade para confirmação de movimento. | NÃO EXECUTADO |
| T084-49 | Worker LAN não executa decisão mecânica contra fonte. | NÃO EXECUTADO |
| T084-50 | Handoff offscreen/local preserva mesmo incident_id e fencing. | NÃO EXECUTADO |
| T084-51 | Incidente local e distante não podem processar duas emboscadas. | NÃO EXECUTADO |
| T084-52 | Testemunha morta confirmada não reaparece por retry de proteção. | NÃO EXECUTADO |
| T084-53 | NPC protegido não é apagado ao terminar encounter temporário. | NÃO EXECUTADO |
| T084-54 | Objeto de quest nativo não é limpo como recurso de escolta. | NÃO EXECUTADO |
| T084-55 | Loot recebido não se perde ao fechar plano de segurança. | NÃO EXECUTADO |
| T084-56 | Falha de plano gera relatório factual sem inventar captura. | NÃO EXECUTADO |
| T084-57 | Sucesso parcial de abrigo é registrado separadamente de segurança garantida. | NÃO EXECUTADO |
| T084-58 | Medida encerrada não apaga memória de ameaça nem provas. | NÃO EXECUTADO |
| T084-59 | Host indisponível bloqueia alteração mecânica e permite NO_OP seguro. | NÃO EXECUTADO |
| T084-60 | Plano não causa alteração de reputação global automática. | NÃO EXECUTADO |
| T084-61 | Relato de ameaça não altera estado canônico por ano DR. | NÃO EXECUTADO |
| T084-62 | Conhecimento do ano futuro não é utilizado para decidir risco pretérito. | NÃO EXECUTADO |
| T084-63 | Overlay de uma branch não aparece em outra branch. | NÃO EXECUTADO |
| T084-64 | Knowledge Pack atualizado não altera ameaça passada sem migração. | NÃO EXECUTADO |
| T084-65 | Versão de política de risco stale impede aplicação automática. | NÃO EXECUTADO |
| T084-66 | Descrição de local privado não aparece em resposta pública da IA. | NÃO EXECUTADO |
| T084-67 | Definição de abrigo no catálogo não prova que abrigo existe na build. | NÃO EXECUTADO |
| T084-68 | Nenhum hook de perseguição é declarado sem POC em engine. | NÃO EXECUTADO |
| T084-69 | Testes host+dois clientes são pré-condição para capability multiplayer. | NÃO EXECUTADO |
| T084-70 | Backpressure posterga monitoramento não crítico sem perder eventos causais. | NÃO EXECUTADO |
| T084-71 | Auditoria de caso de ameaça registra decisões negadas de forma redigida. | NÃO EXECUTADO |
| T084-72 | Plano de proteção em estado UNCERTAIN não gera retaliação automática. | NÃO EXECUTADO |

**Todos os T084 são candidatos para SPECS/POCs, NÃO foram executados.** Critérios quantitativos, disponibilidade real do motor, revisão de regras e aceitação pelo host permanecem para a fase técnica posterior.

## 13. Próxima DEC-085 (em aberto)

**Sigilo operacional e vazamento de planos de proteção.** A) todo abrigo/rota se torna inalcançável e indetectável; B) LLM decide vazamento e acesso adversário livremente; **C (recomendação)** audiência/ACL e evidência de descoberta causal, minimização, risco e auditoria por plano, permitindo vazamentos legítimos sem metaconhecimento da IA nem ataque automático. Não selecionar esta opção sem autorização expressa.


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

DEC-085 define que planos de refúgio, horários e itinerários ficam protegidos por campo; adversários podem saber apenas evidência recebida, não o plano total. Replanejar requer recursos, autorização e host.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Operação de isca não garante segurança, teleporte, escolta ou fuga; exige recursos, risco, host e incidentes confirmados para efeitos mecânicos.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Ameaças a NPC com dupla lealdade podem gerar proteção contextual, não teleporte, invulnerabilidade ou ação hostil automática.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Solicitar proteção ao contratar não gera abrigo/escolta sem recursos, disponibilidade, consentimento e confirmação mecânica quando necessário.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Indício de ameaça a informante pode motivar análise de proteção, mas não confirma agressor ou emboscada; contexto e recurso físico DEC-084 obrigatórios.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Propostas de proteção podem citar informações de dossiê apenas com view autorizada; não revelar planos de escolta a receptores sem necessidade.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Plano de escolta deve verificar risco, NPCs presentes, recursos e consentimento; não implica invulnerabilidade ou teleporte.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Alterações de escolta/abrigo requerem recursos, consentimento, risco e geografia; proteger fonte não equivale a pausa mecânica nem invulnerabilidade.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Escolta e investigação que pedem o mesmo NPC em janelas incompatíveis demandam negociação/replanejamento; nenhuma escolta duplicada ou teleporte.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Carroça/guarda com lease `UNCERTAIN` não pode ser duplicado para escolta; negociação de proteção requer recursos e consentimento.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-096/C — Discovery v9.2

Risco de evento histórico DEC-096/C pode gerar hipótese de proteção, nunca mobilizar escolta sem autorização/recursos.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Aumento de risco DEC-097/C pode motivar revisão de proteção, mas não mobiliza escolta automaticamente.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Abrigos, escoltas e proteção ativa exigem disponibilidade/recursos reais e consentimento; reentrar na área não reativa equipes já retiradas.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Plano de proteção não faz teleport/spawn de guardas ou fontes sob domínio de quests/mods.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Plano de proteção não aciona escolta por flags não liberadas aos responsáveis.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Quest state, mapping rule names and even flag metadata may expose future branches, romance or hidden identities; they remain private technical evidence. Dossiers, sources and NPCs receive only authorized safe milestones through independently confirmed disclosure; no belief is promoted to fact from ambiguous observations. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

A DEC-102/C trata divergências entre milestone validado do host e projeção derivada do Living World: exigir mapeamento DEC-101, observação DEC-100, epoch/branch e receipts, e preservar o host, facts ledger e conhecimento dos NPCs. Somente proposta de revisão CAS/autorizada; detalhes em ADR-0097/doc. 102. **Sem POC mecânica.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **risco e proteção após errata**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para proteção ativa não é automaticamente alterada por mero rumor, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para proteção ativa e sigilo durante audiências, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Proteção física de informantes não é requisito presumido por cobrança. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Planos de proteção não se tornam obrigação mecânica por contrato. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
