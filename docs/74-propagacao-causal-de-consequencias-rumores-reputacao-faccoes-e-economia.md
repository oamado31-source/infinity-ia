# 74 — Propagação causal e contextual: encontros → relatos → consequências no Living World

> **Discovery v7.0 — DEC-074/C aprovada, NÃO IMPLEMENTADA.** Este documento registra requisitos e contratos **candidatos**, não APIs existentes. **52 testes candidatos não executados.** Ver ADR-0069.

## 1. Escopo, responsabilidades e decisões preservadas

- **Origem:** fatos do ledger após DEC-070/071/073 (`resolution_epoch` reconciliado e receipts mecânicos do host quando necessários).
- **Entrega:** redes sociais, rotas e comunicação DEC-029, conhecimento protegido DEC-028, memória/belief DEC-064/065, reputação DEC-030, facções DEC-031, economia DEC-032 e conflitos DEC-033.
- **Restrições:** DEC-011/012/027/034/041/053/054/055/056; sem comandos do motor por LLM, sem atualizações globais instantâneas, sem efeitos de quest/XP/inventário presumidos.
- **DEC-060–073 preservadas integralmente.** Cânone em diretórios físicos independentes `knowledge/periods/<ANO>-DR/`, com proveniência/curadoria DEC-061/062 e packs fixados por campanha DEC-063. Resultados ficam em `campaign/branch` overlay separado; NPCs têm identidade e memória verificadas DEC-064–069.

## 2. Separar quatro camadas sem misturá-las

| Camada | Tipo conceitual | Pergunta | Autoridade de registro |
|---|---|---|---|
| Fato ocorrido | `ConfirmedWorldEvent` | O que realmente aconteceu? | Ledger narrativo a partir de evidência/host |
| Mensagem/percepção | `ObservationReport` | Quem viu/contou e quando? | Observações ou mensagens com proveniência |
| Crença/conhecimento | `BeliefUpdate` | O destinatário acredita nisso? | Regras e memória epistêmica por NPC, com ACL |
| Efeito de domínio | `DomainEffect` | Algo deve mudar em relação/reputação/mercado/etc.? | Regra de domínio + risco; host se efeito mecânico |

**Invariantes:** conhecimento não equivale a verdade; efeitos não emergem automaticamente de noticia; rumores podem ser incorretos sem falsificar o ledger; não atribuir conhecimento ao público universal só porque um encontro foi fechado.

## 3. Grafo causal e difusão atrasada

1. Selecionar somente `ConfirmedWorldEvent` da revisão vigente, com `campaign_id`, `branch_id`, `event_id`, `incident_id`, `resolution_epoch`, `checkpoint` e evidência suficiente.
2. Avaliar observadores legítimos: PCs/NPCs realmente presentes, relato documentado ou acesso permitido a registro. Não inferir testemunhas só por proximidade narrativa.
3. Gerar `ObservationReport` com `claim_id`, `witness_id`, `observed_event_ref`, credibilidade atribuída, cidade, instante e ACL; rumores falsos mantêm `truth_status=UNVERIFIED` sem falsificar `source_event`.
4. Consultar grafo social/faccional e rotas DEC-029/069, tempo DEC-022, condições locais, permissões e canal concreto. Contemplar transmissão indireta e distorção, mas nunca teleporte de informação.
5. Enfileirar `PropagationJob` versionado e idempotente por destinatário/canal e instante; avaliar privacidade **antes** de recuperar dados ou chamar LLM.
6. Na recepção, atualizar memória/crença individual com verificação DEC-064/065; não sobrescrever opiniões por verdade de catálogo.
7. Avaliar `ImpactProposal` por domínio com regras determinísticas, evidência, autoria, relevância, magnitude e impacto cumulativo. Não assumir atualização econômica/host por simples difusão.
8. Verificar gates LOW/MEDIUM/HIGH, risco acumulado, ACL, consentimento, revisão, host, capability, receipt e checkpoint. Publicar uma única vez por `CausalImpactLedger`.
9. Em `UNCERTAIN`/`STALE` ou revogação, congelar operação, registrar pendência e reconciliar; não reaplicar mecanicamente cegamente.

## 4. Contratos de dados candidatos (não implementados)

```json
{
  "ConfirmedWorldEvent": {
    "campaign_id": "campaign-example", "branch_id": "branch-example", "event_id": "event-example",
    "incident_id": "incident-example", "encounter_id": "encounter-example",
    "resolution_epoch": 1, "campaign_revision": 1, "checkpoint_epoch": 1,
    "knowledge_pack_revision": "pin-example", "occurred_at_dr": "1369-DR",
    "region_id": "region-example", "host_receipt_refs": ["host-confirmed-example"],
    "factual_state": "CONFIRMED", "participant_identity_refs": [], "evidence_refs": []
  },
  "ObservationReport": {
    "claim_id": "claim-example", "source_event_id": "event-example",
    "observer_identity_id": "npc-example", "recipient_identity_id": "guild-example",
    "medium": "TRADER_REPORT", "observed_at_dr": "1369-DR",
    "received_at_dr": null, "channel_evidence_refs": [], "truth_status": "REPORTED",
    "confidence": "NOT_YET_ASSESSED", "acl_policy_ref": "policy-example"
  },
  "PropagationJob": {
    "job_id": "job-example", "source_claim_id": "claim-example",
    "campaign_id": "campaign-example", "branch_id": "branch-example",
    "clock_mode": "PARTIAL", "earliest_delivery_ref": "pending-route-validation",
    "campaign_revision": 1, "idempotency_key": "example-key", "status": "PENDING"
  },
  "ImpactProposal": {
    "source_event_id": "event-example", "target_entity_id": "guild-example",
    "effect_kind": "SOCIAL_TRUST", "rule_revision": "rule-example",
    "evidence_refs": [], "proposed_delta": null, "risk_class": "PENDING_CLASSIFICATION",
    "gate_state": "PENDING", "mechanical_action": false
  },
  "CausalImpactLedger": {
    "campaign_id": "campaign-example", "branch_id": "branch-example",
    "source_event_id": "event-example", "target_entity_id": "guild-example",
    "effect_kind": "SOCIAL_TRUST", "rule_revision": "rule-example",
    "commit_state": "UNCOMMITTED", "effect_receipt_ref": null
  }
}
```

IDs, fórmulas, políticas de indexação, disponibilidade dos eventos do host, canal/custos e schema operacional são assuntos de SPECS. **`host_receipt_refs` nos exemplos são apenas marcadores ilustrativos e não evidência real**.

## 5. Fluxo de estados proposto

`EVENT_CANDIDATE` → `SOURCE_CONFIRMED` → `OBSERVERS_VALIDATED` → `REPORT_PENDING` → `DELIVERY_ELIGIBLE` → `DELIVERED_AS_CLAIM` → `BELIEF_PROCESSED` → `DOMAIN_EFFECT_PROPOSED` → `GATED` → `COMMITTED_CONFIRMED`.

Ramificações: `NO_WITNESS`, `CHANNEL_UNAVAILABLE`, `PENDING_EVIDENCE`, `ACL_DENIED`, `BLOCKED_RISK`, `BLOCKED_UNSUPPORTED`, `STALE_REVISION`, `UNCERTAIN`, `NO_OP`.

Para notícias sem efeito pretendido, o fluxo pode encerrar em `BELIEF_PROCESSED` ou `NO_OP`. Não é necessária uma etapa de impacto econômico ou reputacional para que um rumor legitimamente exista. `COMMITTED_CONFIRMED` não é sinal de mudança mecânica se o efeito aprovado era estritamente narrativo.

## 6. Regras de impacto por domínio

| Domínio | Evidência mínima | Efeito permitido inicialmente | Gate adicional |
|---|---|---|---|
| Memórias/crenças | Identidade verificada, notícia legitimamente recebida, ACL | Atualização epistêmica sem alegar certeza | DEC-064/065 e política de segredos |
| Relações | Participação/relato legítimo + vínculo relevante | Proposta narrativa localizada | Identidade DEC-066, risco acumulado |
| Reputação social | Contexto da região/facção, autoria, testemunho | Variação narrativa contextual por regra validada | DEC-030, não mexer na reputação mecânica |
| Organização/facção | Notícias recebidas, recursos, objetivos e estado da facção | Oportunidade/reação proposta e autorizada | DEC-031, risco MEDIUM/HIGH |
| Economia/rotas | Causalidade, escala, disponibilidade e dados verificáveis | Proposta agregada, nunca mudança por boato só | DEC-032, limites e validação |
| Política/militar | Evidências estratégicas, calendário e autorização | Simulação agregada de baixo risco quando curada | DEC-033/034, HIGH default-deny |
| Engine BG2:EE | Receipt, adapter tipado por build e host | Nenhum até POC específica | DEC-011/012/051/053, host+dois clientes |

A conclusão do encontro não altera a reputação mecânica do BG2:EE, XP, itens, quest flags, alinhamento, governo ou preços por inferência textual. Determinar consequências de uma ação coletiva exige autoria, presença e atribuição (DEC-075 ainda aberta).

## 7. Exclusividade, idempotência e reconciliação

- **Fonte única:** evento do encontro reconciliado com `incident_id`/`resolution_epoch`; DEC-071/073 protegem fechamento único.
- **Notícias múltiplas:** mensagens diversas podem compartilhar `source_event_id`, mas não criam eventos independentes. Diferentes relatos podem alterar graus de confiança de forma limitada, sem multiplicar o impacto material.
- **Ledger deduplicado:** chave causal conceitual `(campaign, branch, source_event, target, effect_kind, rule_revision)`; o banco transacional, locks e semântica exata ficarão em SPECS.
- **Fencing:** jobs defasados, duas mensagens em paralelo, mudança de branch, restore, revogação LAN e alteração de build/pack invalidam as propostas que precisam ser revistas.
- **Compensação:** correção documentada pode gerar efeito corretivo novo que referencia original, mas não reescreve histórico confirmado ou aplica rollback do save às cegas.
- **Privacy-by-design:** mínimo contexto por destinatário; ausência de logs de segredo em telemetria por padrão.

## 8. Riscos e limites

- Rumores falsos e agentes maliciosos: tratar como *alegações*; a confiança em um emissor não substitui evidência do evento.
- Efeitos desproporcionais: definir caps e amortecimento por região/facção, considerar janela temporal e acumulado, rejeitar alterações globais sem base.
- Onisciência: distinguir quem presenciou, quem ouviu e quem não teve acesso; evitar preenchimento por LLM de participantes fictícios.
- Cronologia: sem acesso intertemporal arbitrário, mensagens não podem voltar a ano anterior. A separação física por ano DR DEC-060 nunca é enfraquecida.
- Incidentes sem suporte: narrativas propostas podem existir sem spawn/combat/cleanup; não alegar conteúdo executado quando não houver host receipt.
- Desempenho: quotas, prioridade, filas e backpressure DEC-056; evento distante não bloqueia jogador.
- Segurança: assinaturas e segredos, ACL, campanha/branch, rate limits e defaults seguros. Handoff para engine somente com POCs.

## 9. Roteiro de implementação futura (ainda não autorizado)

1. SPEC de eventos e proveniência; fixtures sintéticas com eventos confirmados e falsos.
2. Provar idempotência do ledger e separação de crenças em simulação determinística puramente local.
3. Definir grafo social/rotas/canais, regras de entrega, clock e quotas com cenários conflitantes.
4. Definir e testar difusão e atualizações sociais e propostas de facção SEM engine.
5. POC read-only do host e reconcile de receipts, check de compatibilidade por build.
6. Só após POCs e gate de autorização tentar um efeito mecânico benigno isolado, testar save/load/crash/restore/host+dois clientes; manter HIGH bloqueado.

## 10. Matriz de testes candidatos — **52 cenários, nenhum executado**

| ID | Cenário esperado |
|---|---|
| T074-01 | Evento de caravana confirmado pelo host dispara uma única cadeia de repercussão. |
| T074-02 | Proposta de evento não confirmada não propaga fato. |
| T074-03 | Rumor sem recibo nunca se converte em evento confirmado. |
| T074-04 | Evento UNCERTAIN bloqueia efeitos até reconciliar. |
| T074-05 | Evento STALE com revision antiga não produz impacto. |
| T074-06 | Chegada de notícia não antecede evento original. |
| T074-07 | Relógio FROZEN bloqueia progresso temporal não permitido. |
| T074-08 | Relógio PARTIAL respeita configuração da campanha. |
| T074-09 | Relógio REALTIME respeita limites de catch-up. |
| T074-10 | NPC sem testemunho ou canal não ganha conhecimento automaticamente. |
| T074-11 | Testemunha identificada pode relatar apenas informação observável. |
| T074-12 | Relato exige origem, destinatário, momento e meio identificados. |
| T074-13 | Canal indisponível suspende entrega sem inventar mensageiro. |
| T074-14 | Viagem de mensagem não teleporta dados por regiões. |
| T074-15 | Dois relatos diferentes do mesmo fato não criam dois fatos. |
| T074-16 | Dois relatos contraditórios preservam proveniência e dúvida. |
| T074-17 | NPC recebe rumor mas mantém crença divergente de forma legítima. |
| T074-18 | NPC revisa crença com evidência sem apagar história da crença anterior. |
| T074-19 | ACL impede vazamento de segredo pessoal no rumor. |
| T074-20 | ACL impede vazamento de segredo entre PCs em cooperativo. |
| T074-21 | Worker LAN sem permissão não recebe conteúdo sigiloso. |
| T074-22 | Logs redigidos não expõem segredos nem fontes protegidas. |
| T074-23 | Atualização de fama local não vira automaticamente reputação mecânica. |
| T074-24 | Guilda remota sem notícia não altera confiança. |
| T074-25 | Facção com informação validada pode apenas propor reação autorizada. |
| T074-26 | Mudança econômica exige evidência e regra distinta de rumor. |
| T074-27 | Bloqueio de rota com prova pode afetar simulação regional validada. |
| T074-28 | Rumor de bloqueio sem prova não fecha rota mecanicamente. |
| T074-29 | Mudança política HIGH permanece default-deny. |
| T074-30 | Perda irreversível de recurso HIGH não resulta de rumor. |
| T074-31 | Múltiplos LOW acumulados elevam revisão de risco. |
| T074-32 | Entrega duplicada de job mantém um único impacto por chave causal. |
| T074-33 | Falha após commit e retry não duplica reputação. |
| T074-34 | Restore antigo não herda repercussões de branch futuro. |
| T074-35 | Checkpoint incompatível rejeita efeito stale. |
| T074-36 | Branch paralelo isola reputações e notícias. |
| T074-37 | Migração de Knowledge Pack exige verificação de versão. |
| T074-38 | Informação canônica de ano futuro não é recuperada no ano anterior. |
| T074-39 | Diretórios anuais canônicos permanecem intocados pela repercussão. |
| T074-40 | Overlay de campanha recebe somente registros dessa campanha. |
| T074-41 | Item e loot dependem do host, não do evento narrativo. |
| T074-42 | Alteração de quest sem adapter testado não é executada. |
| T074-43 | Cliente multiplayer não confirma efeito mecânico sozinho. |
| T074-44 | Revogação de nó LAN invalida emissão de efeito pendente. |
| T074-45 | Relações entre NPCs respondem a testemunho e identidade verificada. |
| T074-46 | NPC anônimo não recebe lembrança de identidade ambígua. |
| T074-47 | Conflito de causalidade entre incidente local e offscreen impede duplo evento. |
| T074-48 | Limpeza pós-encontro não apaga evento confirmado nem seus relatos. |
| T074-49 | Correção curada cria evento compensatório em vez de apagar recibos. |
| T074-50 | Fila de propagação limitada prioriza gameplay e mantém durabilidade. |
| T074-51 | Fonte desconhecida resulta PENDING_EVIDENCE, sem impacto inventado. |
| T074-52 | Benchmark de integração host+dois clientes permanece gate antes de alegar suporte. |

## 11. DEC-075 — Próxima escolha em aberto

**Crédito e responsabilidade de ações cooperativas:** A) crédito idêntico a todo o grupo; B) somente ao ator individual observado; C) atribuição contextual com trilhas de participação confirmada, testemunhas e informação dos destinatários, distinguindo fama pública de autoria factual e respeitando consentimento/ausências. Recomendação preliminar: **C**. A aprovação desta DEC não está implícita na DEC-074.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Inserir plano explícito de autoria: evento confirmado ≠ contribuição factual ≠ testemunho ≠ reconhecimento/efeito. DEC-075 define a avaliação antes da reputação; rumores não provam atos.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Nova notícia sobre ligação entre identidades segue audiência, canal e relógio; fama/reputação de personas não se combina globalmente sem causa, autorização e ledger idempotente.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação por evidências (Discovery v7.3; não implementada)

A investigação de personas DEC-076 usará ledger privado por campanha/ramo, com pistas e hipóteses revisáveis, origem/independência de fontes, contraprovas e estados inconclusivos. Suspeita ou fala LLM não confirma identidade e não permite divulgação; vínculo factual restrito exige evidências/DEC-066, e revelação exige ACL/consentimento/risk gate por audiência (DEC-019/028/041/045/046). Rumores e repercussões DEC-029/074/075 são separados de fato e punição. **Preservar `knowledge/periods/<ANO>-DR/` fisicamente por ano, sem evidências privadas no cânone.** ADR-0072/documento 77; 58 testes não executados, sem POC BG2:EE/EEex/multiplayer.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Acusação/decisão DEC-078 vira relato contextual, não prova de crime; repercussão só por canal, tempo e idempotência com risco.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

DEC-079 usa canais DEC-074 para transportar pedidos; pedido recebido não equivale a reconhecimento, decisão da outra facção ou efeito de engine.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Revogações DEC-080 são novos eventos causais de informação, com difusão específica; conhecimento não é efeito imediato em toda facção nem apaga reputação anterior.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Retratação DEC-081 é novo evento causal que se difunde DEC-074; reconhecimento público não corrige instantaneamente crenças em todas as regiões.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Repercussão de denúncia segue cadeia de fatos/relatos/crenças separada; decisão disciplinar não atualiza mundo inteiro instantaneamente.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Publicação de depoimento para audiência limitada não replica o identificador real; difusão de denúncia usa channels, clock, ACL, idempotência.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Notícias sobre ataque/proteção se propagam gradualmente com proveniência e ACL; planos confidenciais não ficam publicamente visíveis por default.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Descoberta parcial segue fatos, canais e recepção contextual; exposição não difunde fama ou causa dano global sem regra/evidência.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

DeceptionOperation gera PlantedClaim, não WorldFact; disseminação e crenças por audiência podem desencadear apenas consequências causais autorizadas, sem certeza universal.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Boatos de deserção e descoberta de agentes duplos propagam-se causalmente por públicos; reputação não reage universalmente a suspeita.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Repercussões de acordo/entrega somente após evento realmente conhecido por testemunhas e propagado por canal, não pela existência privada do contrato.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Difusão preserva origem independente e estado de crença por NPC; repetir rumor em vários canais não faz verdadeiro. Efeitos de facção dependem de eventos causais.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Compartilhamento de dossiê é mensagem causal com destinatário e recibo; boatos/correções derivados não viram fatos globalmente, e efeitos não se duplicam por reenvio.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Repercussões de planos só ocorrem após evento confirmado e difundido a observadores legitimamente informados.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Reações sociais a mudanças de plano só seguem fatos confirmados; ordem causal e públicos não ficam sincronizados por monitor privado.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Fila/conflito operacional não gera notícia ou consequência pública por si; decisão de cancelamento/negociação pode gerar relato somente após fato e canal confirmados.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Resolução de impasse em ledger não cria rumor, sanção ou reputação; publicar somente causas e resultados narrativos confirmados e autorizados.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Proposta DEC-096 encaixa DirectImpact confirmado antes de IndirectImpact, ambos com rastreabilidade, delays/caps, sem broadcast/global knowledge ou cadeia infinita.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Efeito indireto DEC-096/C depende diretamente de AppliedImpact confirmado + atraso/escopo; difusão de notícia é outro pipeline causal, não broadcast global.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Efeitos indiretos DEC-097/C requerem pais confirmados, atraso e família causal; boato de guerra não é aplicação automática.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Efeitos diretos/indiretos e rumores mantêm causalidade; materialização confirmada não é canal automático de notícia para NPCs distantes.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Rumores e consequências não comprovam direitos de editar instâncias ou flags de quests.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Propagação de repercussões só ocorre após eventos legítimos de divulgação, não por leitura interna do motor.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** A quest milestone observed on the host is NOT NPC knowledge, player consent, authorship, rumor or dialogue entitlement. A curated, minimal safe milestone must pass ACL/spoiler checks and be delivered causally before appearing in dialogue or memory; no LLM inference from raw flags. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** a conclusão técnica de uma quest não concede automaticamente conhecimento ou crença a NPCs/facções. `QuestMilestoneAdmission` pode gerar proposta de notícia/reputação somente por regras, proveniência, tempo, geografia, visibilidade e ACL; notícia requer fonte/canal/delivery, e seus destinatários podem conhecer apenas versões parciais. Não expor identidades secretas, fontes protegidas ou raw flags por prompts/logs/dossiês. Ações mecânicas derivadas dependem de recibos host, sem atribuição presumida de PC. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **causalidade regional**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para consequências causais não confundem rumor recebido e reputação alterada, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para repercussões causais de acusações e reparações, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Inadimplemento alegado não desencadeia rumor ou reputação sem difusão causal. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Consequências socioeconômicas dependem de fatos confirmados, não espera de grafo. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
