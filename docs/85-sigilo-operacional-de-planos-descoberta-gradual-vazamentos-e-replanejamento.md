# 85 — Sigilo operacional de planos, descoberta parcial, vazamentos e replanejamento

**Discovery v8.1 · DEC-085/C · ADR-0080 · ARQUITETURA APROVADA, NÃO IMPLEMENTADA.**

**Evidências:** somente a escolha do usuário. **74 testes candidatos T085-01..T085-74, NÃO EXECUTADOS.** Não há interceptação, espionagem, abrigo, escolta ou descoberta mecânica validada no BG2:EE/EEex.

## 1. Escopo e relações contratuais

- **Decisão anterior DEC-083:** identidade confidencial, depoimento, prova e divulgação proporcional sob ACL.
- **DEC-084:** ameaças por prova, classificação de risco, plano de proteção, recursos e resultado confirmado.
- **DEC-077:** pistas com proveniência, cadeias de fontes independentes e contestação.
- **DEC-076:** identidade factual privada distinta de persona reconhecida.
- **DEC-029/030/061/064/074/075:** transmissão social, percepção, fonte, crença, mérito factual e repercussão.
- **DEC-068/069/070/071/072/073:** NPCs com presença/itinerários, incidentes e encontros confirmados/limpos sem duplicação.
- **DEC-011/012/022/027/034/041/045/046/053/054/055/056/057/058/059/060/063:** host, clock, risco, consentimento, checkpoint, segurança LAN e cânone anual.

**Não objetivo:** proibir absolutamente que NPC descubra planos, gerar cenas de espionagem ou combate pela LLM, garantir sigilo na UI do motor, autorizar sabotagem/contraespionagem ativa ou afirmar capabilities EEex não testadas.

## 2. Fronteira de dados: verdade privada, alegação, evidência e percepção

| Domínio conceitual | Conteúdo | Autoridade | Quem pode saber |
|---|---|---|---|
| `ProtectedPlanTruth` | localização, rota, horários, protetores, planos alternativos | entidade autoritativa da campanha/host quando mecânico | atores autorizados por campo |
| `PlanAccessGrant` | role, audiência, finalidade, intervalo e campos | política determinística de ACL/consentimento | subsistema de segurança |
| `IntelligenceClaim` | algo que investigador acredita ter descoberto | observador/fonte, não verdade factual | público que recebeu por canal |
| `DiscoveryEvidence` | observação, documento, informante e fontes | registro com proveniência | apenas investigadores autorizados |
| `AdversaryBelief` | visão de NPC/facção sobre local/rota | memória epistêmica contextual | observador e regras permitidas |
| `CompromiseAssessment` | exposição real/parcial/contestada de dado privado | reconciliador com regras determinísticas | proteção interna, nunca broadcast |
| `ProtectionRevision` | plano novo, cancelado, replanejado | autoridade/consentimento + recibos pertinentes | destinatários autorizados |
| `DisclosureOrObservationEvent` | quem recebeu o quê, canal e quando | ledger causal de transmissão | auditoria e destinatários permitidos |

Exemplo: a guilda conhece *"houve troca de escolta perto do cais"* por observação verificável. Não segue daí que conheça identidade do protegido, refúgio, rota completa ou horário preciso. Um defensor pode saber que houve um possível vazamento sem que essa informação seja transmitida automaticamente aos NPCs responsáveis.

## 3. Compartimentação e matriz de acesso candidata

**Campos protegidos:** `identity`, `refuge_location`, `route_segment[n]`, `departure_window`, `escort_identities`, `handoff_point`, `contingency`, `plan_revision`, `communication_channel`.

| Papel lógico | Identidade | Refúgio | Segmento de rota | Horário | Evidência | Observação |
|---|---|---|---|---|---|---|
| Host autorizado | conforme política | conforme política | conforme política | conforme política | auditoria redigida | acesso de manutenção não torna o host personagem onisciente |
| Titular/PC consentido | próprio/escopo | se essencial | se autorizado | se autorizado | dados mínimos | DEC-019/041/045/046 |
| Protetor atribuído | alias mínimo | trecho operacional necessário | trecho designado | janela útil | apenas risco necessário | não conhece toda a missão por default |
| Autoridade investigadora | versão redigida | se competente e permitida | sob necessidade | sob necessidade | fonte e proveniência filtradas | DEC-078/083 |
| NPC de guilda hostil | **sem grant** | **sem grant** | **sem grant** | **sem grant** | só pistas obtidas no mundo | registro privado nunca acessível |
| Servidor/worker LAN | por ACL/finalidade | por ACL/finalidade | por ACL/finalidade | por ACL/finalidade | minimizado | acesso técnico não equivale a conhecer ficcionalmente |

ACL precisa considerar também **inferência indireta**: um bilhete com cor de carroça e horário, embora sem nome ou endereço, pode identificar a única rota plausível. Controles de *least privilege*, propósito, momento, cardinalidade e correlação são requisitos, não mecanismos implementados.

## 4. Contratos candidatos (não APIs nem schemas implementados)

```yaml
ProtectedPlanTruth:
  campaign_id: string
  branch_id: string
  protection_case_id: string
  plan_id: string
  revision: integer
  checkpoint_epoch: integer
  knowledge_pack_pin: string
  protected_actor_identity_ref: secret_ref
  created_at_dr: world_time
  secret_fields:
    refuge_location: secret_ref
    route_segments: [secret_ref]
    departure_window: secret_ref
    escort_refs: [secret_ref]
    contingencies: [secret_ref]
  state: DRAFT | APPROVED | ACTIVE | REPLANNING | FINISHED | CANCELLED

PlanAccessGrant:
  grant_id: string
  plan_revision: integer
  principal_ref: string
  purpose: string
  allowed_fields: [field_ref]
  expires_at_dr: world_time
  consent_ref: opaque_ref
  risk_policy_revision: string
  grant_state: ACTIVE | REVOKED | EXPIRED

DiscoveryEvidence:
  evidence_id: string
  intelligence_case_id: string
  originating_observer_ref: opaque_ref
  evidence_kind: OBSERVATION | MESSAGE | INFORMANT | DOCUMENT | OTHER
  observed_field_ref: secret_field_ref | null
  observed_claim_value_ref: opaque_ref
  source_event_ref: opaque_ref
  time_dr: world_time
  location_ref: opaque_ref
  source_ancestry_refs: [opaque_ref]
  evidence_status: ALLEGED | CORROBORATED | CONTESTED | INVALID | UNKNOWN
  visibility_acl_ref: opaque_ref

IntelligenceClaim:
  claim_id: string
  claimant_actor_ref: opaque_ref
  target_plan_hint_ref: opaque_ref | null
  discovered_fields: [field_ref]
  claim_content_ref: opaque_ref
  evidence_refs: [opaque_ref]
  epistemic_status: RUMOR | SUSPECTED | CORROBORATED | DISPUTED
  audience_scope: string
  channel_ref: opaque_ref
  learned_at_dr: world_time

CompromiseAssessment:
  plan_id: string
  plan_revision: integer
  assessed_fields: [field_ref]
  affected_audiences: [principal_ref]
  supporting_evidence_refs: [opaque_ref]
  contradictory_evidence_refs: [opaque_ref]
  state: SEALED | LEAD_REPORTED | PARTIALLY_EXPOSED | CORROBORATED_EXPOSURE | DISPUTED | STALE
  risk_class: LOW | MEDIUM | HIGH
  assessment_revision: integer
  audit_ref: opaque_ref

ProtectionRevision:
  parent_plan_revision: integer
  next_plan_revision: integer
  changed_fields: [field_ref]
  cause_assessment_ref: opaque_ref
  authorization_ref: opaque_ref
  resources_and_route_checks: [opaque_ref]
  host_receipt_ref: opaque_ref | null
  commit_state: PROPOSED | AUTHORIZED | COMMITTED | BLOCKED | UNCERTAIN

DisclosureOrObservationEvent:
  disclosure_id: string
  cause_event_ref: opaque_ref
  plan_id: string
  plan_revision: integer
  audience_principal_ref: opaque_ref
  field_scope: [field_ref]
  channel_ref: opaque_ref
  world_time_dr: world_time
  rule_revision: string
  checkpoint_epoch: integer
  idempotency_key: string
  status: PENDING | PUBLISHED | BLOCKED | UNCERTAIN
```

**Ressalvas:** `secret_ref` e `opaque_ref` são placeholders conceituais; não criam armazenamento criptografado, motor de ACL, lista de observadores do BG2:EE nem protocolos seguros já existentes. `world_time` respeita DEC-022/060. Sem receipt e capability por build, `host_receipt_ref` permanece nulo e não se afirma alteração física.

## 5. Fluxo determinístico candidato

```text
Plano privado ACTIVE + ACL por campo
          |
          v
NPC adversário propõe investigação contextual
          |
          +--sem motivação/recurso/presença/canal--> NO_OP
          |
          v
Acontecimento verificável de observação / interceptação / informante
          |
          +--sem fonte verificável--> CLAIM_UNVERIFIED
          |
          v
EvidenceLedger privado + lineage / cronologia / validação de ACL
          |
          +--conflito / circularidade--> DISPUTED ou PENDING_EVIDENCE
          |
          v
AdversaryBelief recebe SOMENTE informação que alcançou observador
          |
          v
CompromiseAssessment por CAMPO e AUDIÊNCIA (interno)
          |
          +--sem exposição factual--> MONITOR / NO_OP
          |
          +--exposição parcial--> PROTECTION_REPLAN_PROPOSED
          |
          v
Autorização + consentimento + recursos + geografia + risco
          |
          +--bloqueio / UNCERTAIN--> PENDING / RECONCILE
          |
          v
Novo plano revisionado; execução física apenas após receipt host
```

O plano alterado não apaga fatos anteriores nem provoca esquecimento instantâneo. A guilda adversária **não** recebe o novo trajeto. O protetor **não** é automaticamente notificado quando o avaliador interno identifica exposição: alertas informacionais também precisam de canal/permissão/tempo, salvo bloqueio técnico fail-closed que não simule conhecimento de NPC.

## 6. Descobertas graduais e desinformação não autorizada

Exemplo hipotético: um informante diz à guilda que a testemunha sairá da cidade. A guilda pode passar a suspeitar de uma partida, mas **não** aprende destino, identidade ou horário exato. Outro observador pode relatar erroneamente uma carroça diferente; preservar rumor e proveniência sem modificar a localização confirmada da testemunha. DEC-086 ainda decidirá se o Infinity AI pode **plantar deliberadamente pistas falsas/iscas**. Até lá, o sistema não fabrica documento enganoso, identidade falsa ou prova artificial por sugestão livre da IA.

**Estados distintos:**

- `SEALED`: nenhuma divulgação/observação comprovada sobre o campo.
- `LEAD_REPORTED`: alegação ou pista não verificada, potencialmente incompleta.
- `PARTIALLY_EXPOSED`: subconjunto de campos divulgado/observado com prova e audiência definida.
- `CORROBORATED_EXPOSURE`: exposição de campos bem fundamentada, sem inferir automaticamente sucesso adversário.
- `DISPUTED`: evidências contraditórias, requer análise/curadoria.
- `STALE`: revisão/branch/época anterior; não pode controlar ação atual.

Não há estado global *"guilda conhece tudo"* sem provas específicas de cada campo e receptor.

## 7. Contramedidas e replanejamento seguro

1. Avaliar se a informação realmente ficou exposta e para quem, mantendo `UNCERTAIN` quando relevante.
2. Elaborar propostas proporcionais: mudar canal, limitar acesso, revisar janela, reforçar discrição ou solicitar outro percurso/abrigo.
3. Verificar competência do responsável, agência e consentimento de PCs, disponibilidade de abrigo e guardas, custo e risco acumulado.
4. DEC-069 valida rota/tempo; DEC-070/071 bloqueiam duplicação de incidentes; DEC-072/073 exigem templates e ownership comprovados.
5. Ação narrativa pode ser registrada como proposta sem mudar posição no motor. Mudança física requer Action Gateway, capability por build e host receipt; nenhuma automação de teleporte ou invulnerabilidade.
6. Nova revisão invalida grants/caches antigos; não apaga o conhecimento legítimo de NPC que já recebeu mensagem anterior.
7. A descoberta do adversário não permite ataque HIGH: classificar e aguardar autorização aplicável.

## 8. Integridade, privacidade e ameaça técnica

- **Principalidade:** acesso de backend/administrador/worker não é conhecimento de NPC; permissionamento por rol/finalidade/campo/audiência.
- **Proveniência:** observar um comboio só autoriza afirmar o que foi observável; não preencher atores ausentes, horários ou rotas através de LLM.
- **Cross-context:** leaks de índice semântico, caches, filenames, logs, desenhos, screenshots, mapas e mensagens podem permitir correlação da fonte sem revelar o nome.
- **Checkpoint:** persistir evidência, revisão de segredo, grants e event ledger coerentes com save/branch; restore não herda descoberta futura.
- **Segurança de LLM:** filtrar contexto antes da chamada. Saída que contém campo restrito deve ser bloqueada/redigida, não enviada ao observador.
- **Scheduler:** jobs assíncronos limitados; incerteza ou queda da LAN não remove ACL nem executa replay cego.
- **Armazenamento físico:** `knowledge/periods/<ANO>-DR/` é cânone anual separado. Segredos de proteção e pistas são exclusividade de overlay de campanha/ramo; nunca indexar em base geral de lore.

## 9. Riscos e SPECS/POCs pendentes

| Risco | Mitigação candidata | Evidência a obter |
|---|---|---|
| Onisciência adversarial | ACL e `AdversaryBelief` sem acesso ao plano real | Fixtures de papéis e perguntas adversariais |
| Reidentificação indireta | minimização de campos, cardinalidade e contexto | Testes de vazamento por arquivos/prompts/índices |
| Rumores circulares | ancestry e dedup de origem | Testes de transmissão por grafo |
| Descoberta de campo errada | estado parcial e `DISPUTED` | Casos com contradições e alias |
| Retaliação automática | separação descoberta versus efeito e HIGH default-deny | Simulações de gates sem engine |
| Falsos recursos/presença | tempo/rota/atores e gateway host | POC read-only, host+dois clientes |
| Replay e branch | fencing, checkpoint e idempotência | Restore, crash, failover e LAN revogada |
| Contaminação do cânone | separar fisicamente ano DR e overlay | Diff de diretórios anuais por build |

## 10. Roteiro futuro de validação (não autorizado como implementação)

1. Construir dados **sintéticos** de um abrigo, rota em segmentos, NPC da guilda, três informantes e dois relatórios conflitantes.
2. Testar ACL por segredo/campo, associação indireta, redaction e abuso por query/prompt, incluindo trabalhadores LAN.
3. Testar grafo de rumores, rota/tempo, estados parciais e atribuição de identidade por proveniência.
4. Testar plano v1→v2 com revogação de grants/caches, save/restore e dedup.
5. Inventariar capacidades reais de observação/posição/itens/stealth na build BG2:EE limpa + EEex/bridge somente leitura, sem assumir API.
6. Se e somente se autorizado e validado, testar efeitos mecânicos benignos num save descartável, host + 2 clientes, sem afetar saves pessoais.

## 11. Matriz de **74 testes candidatos, NÃO EXECUTADOS**

| ID | Caso/expectativa | Execução |
|---|---|---|
| T085-01 | Plano privado criado com identidade da fonte protegida não é consultável por guilda adversária. | NÃO EXECUTADO |
| T085-02 | Consulta de guilda com apenas nome do abrigo sem grant é negada. | NÃO EXECUTADO |
| T085-03 | Campo rota e campo horário possuem permissões independentes. | NÃO EXECUTADO |
| T085-04 | Saber que existe escolta não revela os nomes dos guardas. | NÃO EXECUTADO |
| T085-05 | Saber um horário aproximado não revela destino. | NÃO EXECUTADO |
| T085-06 | Saber destino não revela identidade factual do protegido. | NÃO EXECUTADO |
| T085-07 | Membro da party sem consentimento não recebe mapa operacional completo. | NÃO EXECUTADO |
| T085-08 | Controlador delegado de PC não recebe segredo fora do escopo de delegação. | NÃO EXECUTADO |
| T085-09 | Worker LAN pareado e sem role correta não lê rota. | NÃO EXECUTADO |
| T085-10 | Administrador da plataforma não é autorizado narrativamente como NPC conhecedor. | NÃO EXECUTADO |
| T085-11 | Prompt de NPC não contém coordenadas/rota fora de seu conhecimento. | NÃO EXECUTADO |
| T085-12 | Fallback entre modelos não amplia ACL nem inclui segredos extras. | NÃO EXECUTADO |
| T085-13 | Cache de prompt após revogação não retorna plano antigo. | NÃO EXECUTADO |
| T085-14 | Índice/RAG não devolve documento de refúgio por consulta de alias não autorizado. | NÃO EXECUTADO |
| T085-15 | Log de observabilidade não expõe endereço do abrigo. | NÃO EXECUTADO |
| T085-16 | Nome de arquivo sensível não entrega identidade por metadados. | NÃO EXECUTADO |
| T085-17 | Correlação entre horário e local é tratada como possível vazamento indireto. | NÃO EXECUTADO |
| T085-18 | Resposta agregada não revela comboio único por cardinalidade. | NÃO EXECUTADO |
| T085-19 | Plano com dois segmentos não divulga segundo ao observador do primeiro. | NÃO EXECUTADO |
| T085-20 | Investigador hostil sem acesso a canal não recebe notícia por onisciência. | NÃO EXECUTADO |
| T085-21 | Observador legítimo de mudança de guarda pode gerar pista parcial com proveniência. | NÃO EXECUTADO |
| T085-22 | NPC sem presença geográfica compatível não testemunha a saída do abrigo. | NÃO EXECUTADO |
| T085-23 | Observação real não confere automaticamente conhecimento de destino. | NÃO EXECUTADO |
| T085-24 | Documento interceptado só gera prova se interceptação e origem forem demonstradas. | NÃO EXECUTADO |
| T085-25 | Suposto informante inventado por LLM não cria descoberta. | NÃO EXECUTADO |
| T085-26 | Informante com acesso limitado não fornece campo protegido que desconhece. | NÃO EXECUTADO |
| T085-27 | Guilda com recursos indisponíveis não cria vigilância gratuita. | NÃO EXECUTADO |
| T085-28 | Descoberta exige tempo de viagem de mensagem compatível com DR e clock. | NÃO EXECUTADO |
| T085-29 | FROZEN não permite divulgação dependente de avanço temporal não autorizado. | NÃO EXECUTADO |
| T085-30 | PARTIAL aplica limites de catch-up à notícia. | NÃO EXECUTADO |
| T085-31 | REALTIME não extrapola limite de filas do sistema. | NÃO EXECUTADO |
| T085-32 | Rumor falso permanece claim sem modificar o plano factual. | NÃO EXECUTADO |
| T085-33 | Dez fontes repetindo mesmo relato não equivalem a dez provas independentes. | NÃO EXECUTADO |
| T085-34 | Origem circular de rumores é detectada por linhagem causal. | NÃO EXECUTADO |
| T085-35 | Pista contraditória deixa avaliação em DISPUTED. | NÃO EXECUTADO |
| T085-36 | Evidência parcial promove PARTIALLY_EXPOSED somente para campos justificados. | NÃO EXECUTADO |
| T085-37 | Grau de suspeita não equivale a localização confirmada. | NÃO EXECUTADO |
| T085-38 | Um NPC pode acreditar no refúgio errado sem alterar o registro privado. | NÃO EXECUTADO |
| T085-39 | Uma guilda pode saber caminho antigo sem conhecer nova rota. | NÃO EXECUTADO |
| T085-40 | Atualização de plano não apaga memória anterior do NPC. | NÃO EXECUTADO |
| T085-41 | Atualização do abrigo gera revisão versionada e não altera época anterior. | NÃO EXECUTADO |
| T085-42 | Revogação de permissão invalida futuras divulgações, não remove conhecimento já recebido. | NÃO EXECUTADO |
| T085-43 | Conhecimento privado de risco não é automaticamente enviado aos guardas protetores. | NÃO EXECUTADO |
| T085-44 | Alerta de comprometimento exige canal autorizado para alcançar protetores. | NÃO EXECUTADO |
| T085-45 | Proteção pode propor nova rota sem transferir NPC mecanicamente. | NÃO EXECUTADO |
| T085-46 | Plano revisado exige recursos e itinerário existentes. | NÃO EXECUTADO |
| T085-47 | Novo abrigo indisponível bloqueia realocação, não cria refúgio. | NÃO EXECUTADO |
| T085-48 | Proteção não garante invisibilidade, teleporte nem invulnerabilidade. | NÃO EXECUTADO |
| T085-49 | Descoberta de local não autoriza criação de emboscada mecânica. | NÃO EXECUTADO |
| T085-50 | LLM não decreta sequestro, morte ou invasão. | NÃO EXECUTADO |
| T085-51 | HIGH cumulativo de observações LOW exige gate apropriado. | NÃO EXECUTADO |
| T085-52 | Caso com outro PC exige consentimento/segredo conforme política. | NÃO EXECUTADO |
| T085-53 | Descoberta parcial não altera reputação global automaticamente. | NÃO EXECUTADO |
| T085-54 | Cliente multiplayer não escreve receipt host de perseguição. | NÃO EXECUTADO |
| T085-55 | Build incompatível rejeita uso de adapter mecânico. | NÃO EXECUTADO |
| T085-56 | Nenhum hook de escuta/interceptação é presumido só por existir em mod. | NÃO EXECUTADO |
| T085-57 | Incidente offscreen não duplica encontro local com mesma causa. | NÃO EXECUTADO |
| T085-58 | Vários relatos do mesmo campo não duplicam efeito no ledger causal. | NÃO EXECUTADO |
| T085-59 | Retry idempotente após timeout não publica segredo duas vezes. | NÃO EXECUTADO |
| T085-60 | UNCERTAIN suspende reenvio cego de informação confidencial. | NÃO EXECUTADO |
| T085-61 | Restore antigo não recebe descobertas do checkpoint futuro. | NÃO EXECUTADO |
| T085-62 | Branch divergente não herda informações de abrigo da outra branch. | NÃO EXECUTADO |
| T085-63 | Campanha diferente não tem acesso a plano pelo mesmo ID textual. | NÃO EXECUTADO |
| T085-64 | Knowledge Pack novo não publica segredos da campanha ao cânone. | NÃO EXECUTADO |
| T085-65 | Arquivo de ano DR canônico permanece byte a byte imutável. | NÃO EXECUTADO |
| T085-66 | Informação de futuro DR não é recuperada em ano passado. | NÃO EXECUTADO |
| T085-67 | NPC dormente só recebe comunicação legítima após retomar. | NÃO EXECUTADO |
| T085-68 | Revogação de nó LAN invalida job pendente com dados privados. | NÃO EXECUTADO |
| T085-69 | Backpressure segura investigação não crítica sem abrir ACL. | NÃO EXECUTADO |
| T085-70 | Decisão corretiva mantém histórico de rumor, canal e audiência. | NÃO EXECUTADO |
| T085-71 | Mensagem de pista falsa sem política de engano autorizada não é fabricada pelo LLM. | NÃO EXECUTADO |
| T085-72 | Pistas falsas previamente existentes são crenças contestáveis, não fatos mecânicos. | NÃO EXECUTADO |
| T085-73 | Health Monitor produz métricas redigidas e alerta sem revelar local. | NÃO EXECUTADO |
| T085-74 | POC host+dois clientes exigida antes de afirmar interceptação/stealth mecânicos. | NÃO EXECUTADO |

## 12. Próxima DEC-086 — ainda não aprovada

**Contraespionagem ativa e engano defensivo (iscas, pistas plantadas e desinformação).** A) não permitir engano planejado; B) permitir manipulação e criação arbitrária de falsas provas pela LLM; **C (recomendada)** autorizar apenas engano contextual limitado, com origem, recursos, custo, consentimento, risco e distinção permanente entre ficção/informação plantada e eventos factuais confirmados. Nenhuma decisão sobre a DEC-086 está implícita na aprovação da DEC-085.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

DEC-086/C autoriza criar pistas plantadas sob controle, não confundi-las com dados verdadeiros do refúgio; descobrir a isca não revela o plano real automaticamente.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Descoberta do esconderijo de um suposto agente duplo requer informação verificável; vínculo secreto não torna planos acessíveis.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Plano de proteção e contatos secretos do informante não se tornam conhecidos por guilda rival por simples contratação; possíveis descobertas graduais precisam de prova.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Dados de abrigo/rota e timing contidos nos relatos têm ACL própria; lineage não expõe plano de segurança de forma indireta.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Resumo, anexos e metadados são tratados como risco de vazamento de abrigo/rota; reenvio de dossiê requer evento e destinatário legítimos.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Planejamento a partir de plano de abrigo usa somente campos autorizados; descobrir escolta não é descobrir refúgio.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Revisão de refúgio, rota e horário deve preservar sigilo operacional em logs, prompts e mensagens e verificar risco de descoberta causal.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Diagnóstico público de reserva não revela rotas ou abrigo de operação concorrente; regras de ACL filtram metadata de tempo/local se sensível.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Grafo de dependência pode conter rota confidencial: divulgar apenas alternativa de agendamento redigida, não plano ou abrigo.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-096/C — Discovery v9.2

Acessar regra temporal DEC-096/C não equivale a descobrir operação secreta de proteção; estado privado não entra em índice público.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Projeção DEC-097/C não pode permitir inferência de refúgio ou plano a adversário por leak em painel.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Revisão de região não permite deduzir localização de abrigo/rota secreta para facções sem canal causal de descoberta.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Sigilo de planos também cobre logs e manifestos de ownership, não apenas texto da narrativa.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Observações técnicas de refúgios e itinerários são dados de alta sensibilidade e não chegam ao LLM sem ACL.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Quest state, mapping rule names and even flag metadata may expose future branches, romance or hidden identities; they remain private technical evidence. Dossiers, sources and NPCs receive only authorized safe milestones through independently confirmed disclosure; no belief is promoted to fact from ambiguous observations. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** a conclusão técnica de uma quest não concede automaticamente conhecimento ou crença a NPCs/facções. `QuestMilestoneAdmission` pode gerar proposta de notícia/reputação somente por regras, proveniência, tempo, geografia, visibilidade e ACL; notícia requer fonte/canal/delivery, e seus destinatários podem conhecer apenas versões parciais. Não expor identidades secretas, fontes protegidas ou raw flags por prompts/logs/dossiês. Ações mecânicas derivadas dependem de recibos host, sem atribuição presumida de PC. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **sigilo de fontes nas retificações**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para sigilo de refúgios/rotas inclui metadados de entrega e comprovantes, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para proteção de rotas e abrigos em registros públicos, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Endereços protegidos e rotas não são vazados em recibos públicos. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Rotas de refúgio permanecem sob ACL apesar de constarem em uma proposta. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
