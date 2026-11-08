# 78 — Justiça e facções: jurisdição, acusações, contraditório e gates de consequência

> **Discovery v7.4 · DEC-078/C APROVADA · ADR-0073 · ARQUITETURA, NÃO IMPLEMENTADA.** Este documento é desenho candidato, não API ou código existente. **60 testes T078-01..60 não executados.**

## 1. Objetivo e fronteiras

Permitir que organizações ficcionais conduzam denúncias, investigações, acusações, decisões e respostas contextualizadas à época/local com rastreabilidade e limites de risco. Não implementar polícia ou sistema jurídico universal em Forgotten Realms; não pressupor direito processual moderno homogêneo nem poderes da engine inexistentes. Uma decisão oficial pode ser injusta ou incorreta na ficção; os *fatos confirmados* não são alterados por ela.

**Dependências:** DEC-027/028/029/030/031/032/033/034/041/042/045/046/050/051/053/054/055/056/060–077, especialmente DEC-077 (investigação), DEC-075/076 (autor/persona), DEC-011/012 (host/gateway), DEC-060–063 (cânone anual curado), DEC-074 (propagação causal).

## 2. Repositórios e autoridade de dados

```text
knowledge/periods/<ANO>-DR/           # CÂNONE CURADO e fisicamente segregado (DEC-060); somente fontes e regras fundamentadas
  organizations/, politics/, cities/, events/...  # ilustrativo; não afirmar que toda lei já foi importada
campaign-overlays/<campaign>/<branch>/   # domínio lógico candidato, caminho físico final por SPECS
  legal-cases/                         # denúncias e evidências versionadas
  authorities/                         # influência/competência em contexto da campanha
  procedure-events/                    # notificação, defesa, decisões e retificações
  consequence-ledger/                  # autorizações, host receipts, idempotência e auditoria
```

Não importar automaticamente leis para anos errados, nem persistir decisões de jogadores no corpus histórico. Os caminhos de overlay e esquemas são candidatos, não implementação. Knowledge Pack DEC-063 fixa as revisões anuais apropriadas e seus escopos; algumas regiões/autoridades podem ter política `UNKNOWN`.

## 3. Contratos candidatos (sem implementação)

```text
JurisdictionPolicy {
  jurisdiction_id, region_scope[], time_window_dr,
  claimed_authority_id, authority_role, canonical_source_refs[],
  competence_rules[], procedure_stages[], contested_rule_refs[],
  evidence_policy_ref, contestation_options[],
  possible_outcomes[], valid_rule_revision, provenance_acl, status
}
LegalCase {
  campaign_id, branch_id, case_id, case_revision,
  alleged_event_id?, investigation_id?, complainant_id?,
  accused_actor_id?, accused_persona_id?, identity_evidence_refs[],
  jurisdiction_policy_id?, world_time_dr, location_ref,
  evidence_for_refs[], evidence_against_refs[], allegation_refs[],
  charge_refs[], procedural_status, protected_acl,
  checkpoint_epoch, resolution_epoch, knowledge_pack_revision
}
AuthorityDecision {
  decision_id, case_id, authority_id, jurisdiction_policy_revision,
  authority_claimed_finding, underlying_fact_refs[],
  evidence_assessment_refs[], response_or_contestation_refs[],
  decision_time_dr, audience_scope, risk_class,
  policy_authorization_refs[], decision_revision, disposition
}
LegalConsequenceProposal {
  proposal_id, case_id, decision_id?, target_actor_id?,
  intended_effect: NOTICE|INVITATION|RUMOR|REPUTATION_SOCIAL|HOST_MECHANICAL|OTHER,
  type_specific_policy_ref, branch_id, checkpoint_epoch,
  aggregate_risk, consent_scope, host_capability_ref?,
  host_operation_id?, host_receipt_ref?, idempotency_key,
  state: PROPOSED|AUTHORIZED|PENDING|UNCERTAIN|HOST_CONFIRMED|REJECTED
}
```

**Não são contratos de runtime existentes.** O mapeamento físico e as enumerações finais, prazos legais, siglas históricas, algoritmos de prova e representantes de jurisdição dependem de SPECS/curadoria e POCs. Não inventar poderes para guardas nem usar o lore de outra época como norma vigente.

## 4. Máquina de estados candidata de procedimento

```text
REPORT_RECEIVED
    -> JURISDICTION_CHECK
         +-- UNKNOWN/DISPUTED -> MANUAL_REVIEW / NARRATIVE_PENDING (sem punição)
         +-- ELIGIBLE -> EVIDENCE_REVIEW
                             -> NOTICE_OR_CONTACT (quando política contextual permitir)
                             -> OPPORTUNITY_TO_RESPOND (quando prevista/possível)
                             -> DECISION_PROPOSED
                             -> RISK_AND_AUTHORIZATION_GATE
                                 +-- REJECTED / UNCERTAIN / PENDING
                                 +-- APPROVED -> AUTHORITY_DECISION_RECORDED
                                                     -> CONSEQUENCE_PROPOSED
                                                     -> [SOCIAL_ONLY | HOST_GATE]
                                                     -> CLOSED_OR_APPEAL_PENDING
```

- `REPORT_RECEIVED` e `CHARGE_ASSERTED` não significam que a acusação é verdadeira.
- `AUTHORITY_DECISION_RECORDED` representa posição de autoridade, não atestado de verdade objetiva ou punição.
- O direito de resposta/contestação depende da cultura e autoridade cadastradas. O Infinity AI deve **preservar possibilidade narrativa de contestação quando compatível**, sem afirmar que todas as cidades possuem audiência formal.
- `HOST_GATE` é obrigatório para qualquer alteração de engine; se a build não oferecer adapter confirmado, a decisão permanece no plano narrativo/pendente, jamais executada ficticiamente.

## 5. Sistema orientado a regras (código primeiro)

Em vez de invocar agente para cada guarda, gatilho ou denúncia, usar regras determinísticas com expressões/IF sobre dados autorizados. Exemplo de pseudocódigo:

```python
if case.branch_id != active_branch or case.checkpoint_epoch != host_epoch:
    return STALE
if not authority_policy.is_valid_for(case.region, case.year_dr):
    return JURISDICTION_UNKNOWN
if policy.has_contested_jurisdiction(case):
    return JURISDICTION_DISPUTED
if not evidence.allows_procedure_step(case, 'decision_proposal'):
    return PENDING_EVIDENCE
if aggregate_risk == 'HIGH' and not approvals.special_gate:
    return BLOCKED_HIGH
if effect.requires_engine and not host_capability.poc_verified_for(build):
    return BLOCKED_UNSUPPORTED
return PROPOSAL_FOR_AUTHORIZED_GATE  # não é execução
```

Esse exemplo descreve requisitos, não biblioteca executável. LLM local pode gerar falas contextualizadas, argumentos e descrições **após ACL**, mas não decidir culpa/competência/efeito. Qualquer exceção não implementável por regras deve ser tratada como proposta revisável.

## 6. Integridade, distinção epistêmica e autoridade

| Questão | Dados e decisão seguros |
|---|---|
| O crime ocorreu? | Somente evento confirmado por origem válida; denúncia não equivale a fato |
| Quem o praticou? | DEC-066/075/076/077, identidade e evidências; `UNKNOWN` é permitido |
| Quem acusa? | Ator/facção identificada com crença, reputação e motivo próprio |
| Quem pode julgar? | `JurisdictionPolicy` por região/época/fonte; disputa bloqueia consequências irreversíveis |
| Há defesa? | Aplicar procedimento conforme fonte histórica e regras de mesa; não inventar garantia universal |
| Autoridade é honesta? | Pode ser corrupta/enganada em narrativa, sem alterar fatos objetivos |
| Há impacto social? | DEC-029/030/074, com canais, risco e idempotência |
| Há impacto mecânico? | DEC-011/012, adapter tipado, capability testada, host receipt, consentimento e gates |

## 7. Casos de teste narrativos exemplificativos

**Denúncia não comprovada em Athkatla:** dois testemunhos podem compartilhar uma fonte original; o guarda não recebe automaticamente ordem de prisão. Avaliar jurisdição **somente após** curadoria de fontes adequadas ao ano DR. Um suspeito pode ser convidado a se explicar, se a política permitir; se não houver prova ou competência, deixar pendente.

**Conflito entre guilda e guarda:** uma guilda pode reivindicar competência interna e guardas reivindicar jurisdição territorial. Sem política aplicável e evidências de precedência, `JURISDICTION_DISPUTED`. Não escolher a autoridade que parecer mais conveniente a um LLM; DEC-079 fará a política detalhada de precedência e cooperação.

**Autoridade corrupta:** é possível um governante ficcional proferir decisão injusta. Registrar `authority_claimed_finding`, evidências e consequências com seu risco próprio. O motor não executará confisco/prisão sem gate mesmo que a autoridade tenha ordenado tais atos na ficção. Conteúdo de corrupção e licenças de fontes dependem de corpus curado.

**Retificação tardia:** nova evidência refuta acusação e justifica apelação/revisão. Manter ledger histórico, noticiar correção por canais reais, nunca editar saves ou devolver inventário presumido.

## 8. Política de risco de consequências

| Impacto candidato | Tratamento base |
|---|---|
| Rumor, diálogo, notificação narrativa LOW | Allowlist e validação temporal/ACL |
| Investigação, intimação, publicação localizada | Validação de contexto, autoria e risco, com audiência autorizada |
| Hostilidade de guarda, mandado, expatriação/banimento, reputação mecânica | MEDIUM/HIGH conforme impacto; autorização específica, compatibilidade por build e receipt host |
| Prisão, teleporte, perda de itens, XP, alteração de quests, morte ou execução | Impacto grave/HIGH default-deny; sem POC + consentimento/gate adequado, apenas narrativa segura ou pendência |
| Reação política/econômica de facção | Regras DEC-031/032/033; rumor não implica mudança automática |

Impactos acumulados são reavaliados antes de publicar. Sem capability real, **não prometer prisão/guardas perseguidores/flag de procurado** na engine.

## 9. Concorrência, replay, segurança e recuperação

1. Ledger por `(campaign, branch, case, decision, target, effect_kind, rule_revision)` impede duas sanções pela repetição de processo ou notícia.
2. Cada transição deve registrar versão anterior e precondições; dois NPCs/autoridades concorrentes não alteram caso sem confronto de revisões. Não resolver conflito jurisdicional com `last-write-wins`.
3. Host/overlay podem divergir após save/load, crash ou mod update: `UNCERTAIN` bloqueia retry mecânico. Usar checkpoints DEC-053/054 e reconciliação antes de emitir novas ordens.
4. Apenas a audiência do processo recebe detalhes permitidos; dados secretos do PC são filtrados antes da UI, prompts, embeddings, workers LAN e logs.
5. Roteadores locais preferenciais DEC-059 e filas DEC-056 reduzem tokens; regras computáveis não disparam agentes individuais.
6. Decisões retificadas/contestadas não são apagadas; manter encadeamento de eventos com acesso contextual e redigido.

## 10. Plano de validação futuro (não executado)

1. **G78-0 — Curadoria:** políticas sintéticas e fontes por ano/organização, com contradições e intervalos incompletos; validação de modelo sem regras globais inventadas.
2. **G78-1 — Motor de regras offline:** estados, gates, competência, evidência, contestação, alto risco, decisão injusta, sem engine.
3. **G78-2 — Host read-only:** investigar flags de missões e atores sem alterar save, com manifesto de build.
4. **G78-3 — Sandbox de consequências benignas:** somente se gateway por build suportar ação autorizada; backups/checkpoint e cancelamento testados.
5. **G78-4 — Multiplayer:** host+dois clientes, replay, caso contestado, rollback/restore, guardas/quests de mods, observação de efeitos confirmados.
6. **G78-5 — Aprovação:** habilitar por capability testada e tipo de efeito; ausência de suporte bloqueia a parte mecânica.

## 11. Matriz de 60 testes candidatos — NÃO EXECUTADOS

| ID | Cenário esperado | Estado |
|---|---|---|
| T078-01 | Denúncia com fonte não confirmada não gera culpa factual. | NÃO EXECUTADO |
| T078-02 | Duas cópias do mesmo boato não contam como testemunhas independentes. | NÃO EXECUTADO |
| T078-03 | Caso de outro branch não pode fundamentar decisão no atual. | NÃO EXECUTADO |
| T078-04 | Autoridade desconhecida para região/época produz JURISDICTION_UNKNOWN. | NÃO EXECUTADO |
| T078-05 | Guarda fora de sua jurisdição não recebe poderes presumidos. | NÃO EXECUTADO |
| T078-06 | Cargo de uma organização não equivale à autoridade judicial universal. | NÃO EXECUTADO |
| T078-07 | Poder de facto é armazenado separadamente de competência jurídica alegada. | NÃO EXECUTADO |
| T078-08 | Duas facções reivindicando a área produzem JURISDICTION_DISPUTED. | NÃO EXECUTADO |
| T078-09 | Período DR divergente invalida regulamento de época posterior. | NÃO EXECUTADO |
| T078-10 | Fonte com vigência não comprovada bloqueia aplicação de regra jurídica. | NÃO EXECUTADO |
| T078-11 | Inexistência de norma curada não é preenchida livremente pelo LLM. | NÃO EXECUTADO |
| T078-12 | Regras de transição de caso executam sem chamada de agente. | NÃO EXECUTADO |
| T078-13 | LLM local pode redigir diálogo sem decidir culpa ou punição. | NÃO EXECUTADO |
| T078-14 | Acusação permanece diferente de fato confirmado no ledger. | NÃO EXECUTADO |
| T078-15 | Decisão de autoridade não altera a verdade factual automaticamente. | NÃO EXECUTADO |
| T078-16 | Investigação inconclusiva permite arquivamento ou pendência, não punição fictícia. | NÃO EXECUTADO |
| T078-17 | Prova de identidade ambígua bloqueia imputação individual definitiva. | NÃO EXECUTADO |
| T078-18 | Persona suspeita não é vinculada a PC sem prova DEC-076/077. | NÃO EXECUTADO |
| T078-19 | PC ausente não é declarado culpado por mera pertença ao grupo. | NÃO EXECUTADO |
| T078-20 | Controlador delegado não se torna titular do histórico do PC. | NÃO EXECUTADO |
| T078-21 | Prova favorável à defesa é preservada com mesma proveniência. | NÃO EXECUTADO |
| T078-22 | Contradição não é descartada por resposta confiante do LLM. | NÃO EXECUTADO |
| T078-23 | Política sem contraditório formal comprovado não inventa audiência moderna. | NÃO EXECUTADO |
| T078-24 | Procedimento com possibilidade de defesa mantém registro da resposta. | NÃO EXECUTADO |
| T078-25 | Testemunha mentirosa pode influenciar decisão ficcional sem virar verdade factual. | NÃO EXECUTADO |
| T078-26 | Autoridade corrupta pode decidir erroneamente sem alterar ledger de fatos. | NÃO EXECUTADO |
| T078-27 | Decisão de arquivamento não apaga acusação pretérita auditável. | NÃO EXECUTADO |
| T078-28 | Reabertura por nova evidência cria revisão sem retcon silencioso. | NÃO EXECUTADO |
| T078-29 | Retificação de veredito não remove inventário por inferência narrativa. | NÃO EXECUTADO |
| T078-30 | Sanção LOW narrativa só executa sob allowlist e contexto. | NÃO EXECUTADO |
| T078-31 | Sanção MEDIUM sem autorização fica pendente. | NÃO EXECUTADO |
| T078-32 | Sanção HIGH sem autorização especial é bloqueada. | NÃO EXECUTADO |
| T078-33 | Várias consequências LOW cumulativas HIGH acionam novo gate. | NÃO EXECUTADO |
| T078-34 | Prisão mecânica não ocorre sem adapter testado e receipt de host. | NÃO EXECUTADO |
| T078-35 | Confisco não altera inventário sem autorização e receipt. | NÃO EXECUTADO |
| T078-36 | Hostilidade de guarda não é disparada por rumor sem gate. | NÃO EXECUTADO |
| T078-37 | Execução ou morte não ocorre automaticamente por condenação ficcional. | NÃO EXECUTADO |
| T078-38 | Moral/alinhamento de PC não muda sem regras independentes e host. | NÃO EXECUTADO |
| T078-39 | Reputação mecânica não muda com a reputação social da facção. | NÃO EXECUTADO |
| T078-40 | FLAG de quest não muda por acusação narrativa. | NÃO EXECUTADO |
| T078-41 | NPC preso ou acusado continua com identidade persistente e memória. | NÃO EXECUTADO |
| T078-42 | Guarda não aparece em área inacessível por teleporte narrativo. | NÃO EXECUTADO |
| T078-43 | Notícia de acusação não chega instantaneamente a cidades distantes. | NÃO EXECUTADO |
| T078-44 | Públicos não autorizados não recebem backstory privado do acusado. | NÃO EXECUTADO |
| T078-45 | Prompt e log redigem informações sigilosas do caso. | NÃO EXECUTADO |
| T078-46 | Worker LAN revogado não assina decisão ou recibo. | NÃO EXECUTADO |
| T078-47 | Cliente multiplayer não autoriza sentença mecânica sozinho. | NÃO EXECUTADO |
| T078-48 | Dupla entrega de anúncio não multiplica dívida, reputação ou efeitos. | NÃO EXECUTADO |
| T078-49 | Duas autoridades julgando o mesmo caso não aplicam automaticamente sanções concorrentes. | NÃO EXECUTADO |
| T078-50 | Idempotency key impede repetir operação após reload. | NÃO EXECUTADO |
| T078-51 | Timeout UNCERTAIN de operação do host não dispara retry cego. | NÃO EXECUTADO |
| T078-52 | Restauro de checkpoint anterior não herda condenação posterior. | NÃO EXECUTADO |
| T078-53 | Atualização de Knowledge Pack não recalcula automaticamente julgamentos. | NÃO EXECUTADO |
| T078-54 | Arquivo de cânone anual 1369 DR não recebe condenação privada de gameplay. | NÃO EXECUTADO |
| T078-55 | Região sem política definida adota fallback narrativo honesto ou pendência. | NÃO EXECUTADO |
| T078-56 | Backpressure permite adiar processo sem mudar relógio artificialmente. | NÃO EXECUTADO |
| T078-57 | Snapshot de save e caso incoerentes suspendem consequências. | NÃO EXECUTADO |
| T078-58 | Mandado local não tem validade extraterritorial presumida. | NÃO EXECUTADO |
| T078-59 | Risco de ação contra PC observa consentimento e regras de PVP. | NÃO EXECUTADO |
| T078-60 | POC host+dois clientes é obrigatória antes de habilitar punição mecânica. | NÃO EXECUTADO |

**Os 60 itens acima são testes candidatos, não resultados.** Nenhuma capacidade BG2:EE/EEex, funcionalidade de prisão ou sistema de sanção foi demonstrada.

## 12. Próxima decisão DEC-079 (em aberto)

**Conflitos e cooperação entre jurisdições:** A) decisões não ultrapassam limites regionais; B) mandados/caça se aplicam globalmente de imediato; **C, recomendada)** circulação de mandados e pedidos de cooperação por canais legítimos, reconhecimento por autoridade e época, jurisdição contestada e autorização por risco, com presença de agentes só quando host e itinerários verificarem. A DEC-078 **não aprova previamente** nenhuma dessas opções.

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

DEC-079/C complementa a justiça local com pedidos entre autoridades distintos do caso, usando transmissão, competência do destinatário e negociações. Decisão local/mandado não viram sanção global nem prisão sem host.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

DEC-080 torna suspensão, revogação e retificação eventos de ordem com versão; decisão local e sua notícia em outras regiões diferem. HIGH coercion bloqueia quando validade não é verificável.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

DEC-081 dá continuidade a revisão de decisão local com pedido de reparação distinto, competência curada, prova de dano/nexo e host/gate para efeitos mecânicos.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

DEC-082 acrescenta atribuição individual, cadeia de comando e instituição ao procedimento jurídico; decisão de órgão ficcional não supera gates de segurança ou host.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Autoridade competente pode solicitar depoimento, mas não recebe automaticamente identidade; fontes protegidas e contestação contextual separadas de veredicto.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Proteger testemunha pode exigir autoridade local independente e consentimento, sem concluir crime ou competência universal por rumor.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Descoberta por guilda não confere competência judicial nem autoriza prisão; procedimentos e consequências seguem DEC-078.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Documento de engano não autoriza acusação, prisão, confisco ou processo automático. Competência e evidência real permanecem necessárias.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Procedimentos disciplinares por espionagem exigem competência, alegação verificada e possibilidade de contestação contextual; não há condenação automática.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Aceite de fonte não comprova crime nem instaura automaticamente procedimento jurídico; competência e contraditório preservados.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Autoridade não pode usar mera alegação/avaliação da LLM para aplicar sanção; contradição e competência local exigem procedimento/contexto.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Dossiê enviado a autoridade pode subsidiar apuração, mas sua compilação ou recibo não prova culpa nem autoriza sanção. Competência e contraditório permanecem.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Operação contra suspeito deve verificar competência, leis/região/DR, acusação versus culpa e autorização, sem prisão mecânica presumida.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Procedimentos jurídicos e medidas coercitivas replanejadas precisam de jurisdição, contraditório e autoridade, sem execução por LLM.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Autoridades não podem sobrepor ordens jurídicas a reservas de PCs sem competência, evidências e gates; agenda computacional não impõe detenção.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Impasse de recursos processuais não gera automaticamente culpa, prisão ou revogação legal. Pedidos de replanejamento sujeitos a competência e risco.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Justiça faccional não pode prender/remover/alterar instâncias protegidas sem preflight e receipts.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Justiça faccional não pode usar quest flags internas inacessíveis como provas públicas.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para justiça e acusação corrigida não produzem revogação instantânea, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para sanções e justiça não se revertem sem processo próprio, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Fiscalização não confere poder de sanção ou justiça à IA. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Justiça e poder coercitivo não vêm da elegibilidade de pagamento. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
