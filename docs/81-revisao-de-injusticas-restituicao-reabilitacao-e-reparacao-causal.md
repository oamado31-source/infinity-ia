# 81 — Revisão de injustiças, restituição, reabilitação e reparação causal

**Estado:** Discovery v7.7 · DEC-081/C aprovada como arquitetura · **NÃO IMPLEMENTADA** · ADR-0076. **66 testes candidatos T081-* NÃO EXECUTADOS.** Nenhuma capacidade de detenção, restituição, reputação mecânica, edição de quests ou reparação BG2:EE/EEex foi demonstrada.

## 1. Separação de domínios e requisitos

- `LegalOrder`/`LegalCase` DEC-078/079/080: validade, competência, decisões e revisões.
- `ConfirmedDamageEvent`: dano verdadeiramente ocorrido, com evidência e nexo causal, distinto da ordem que poderia tê-lo provocado.
- `RemedyCase`: pedido/processo de reparação, distinto da revogação e de seus possíveis resultados.
- `RemedyProposal`: resposta específica proposta, com autoridade, titular, classificação de risco, limitações e destinatário.
- `HostEffectReceipt`: evidência mecânica somente quando bridge/capability efetivamente testados e gateway autorizado DEC-011/012.
- `ReputationCorrection`: notícia/relação social contextual, com canais DEC-029/074, não reputação mecânica instantânea.
- **Fronteira canônica:** `knowledge/periods/<ANO>-DR/` permanece **fisicamente particionado** (DEC-060), evidência e curadoria DEC-061/062, packs por campanha DEC-063. Todos os danos de PCs/NPCs e reparações **no overlay de campanha/ramo**, isolados de lore.

## 2. Diferenças fundamentais

| Origem | O que prova | O que NÃO prova |
|---|---|---|
| Mandado emitido | Uma autoridade realizou ato administrativo narrativo | Que ocorreu prisão/transferência mecânica |
| Mandado revogado | Vigência/competência da ordem foi alterada | Que a ordem original era ilícita ou que houve prejuízo |
| Dano confirmado | Uma consequência ocorreu e tem prova | Que a ordem é a causa ou que há compensação obrigatória |
| Decisão reparatória | Autoridade decidiu por uma medida dentro da jurisdição | Que a engine aplicou item/XP/quest/reputação |
| Receipt do host | Uma operação mecânica específica foi verificada | Que NPCs distantes sabem dela ou que danos morais desapareceram |
| Retratação pública | Comunicação autorizada foi emitida | Que todos a receberam/acreditaram ou perderam memória da acusação |

## 3. Tipos/contratos candidatos — não APIs implementadas

```yaml
ConfirmedDamageEvent:
  campaign_id: string
  branch_id: string
  damage_id: string
  affected_actor_identity_ref: opaque
  causal_source_event_ids: [opaque]
  evidence_refs: [opaque]
  occurred_at_dr: string
  region_ref: opaque
  damage_kind: MATERIAL | ITEM_OR_CUSTODY | REPUTATIONAL | RELATIONAL | OPPORTUNITY | LIBERTY | QUEST_IMPACT | PERSONAL | UNKNOWN
  ownership_evidence_ref: opaque_or_null
  host_receipt_ref: opaque_or_null
  causality_status: CONFIRMED | DISPUTED | UNKNOWN
  checkpoint_epoch: integer
RemedyCase:
  remedy_case_id: string
  campaign_id: string
  branch_id: string
  linked_legal_case_id: string
  linked_order_ids: [opaque]
  linked_damage_ids: [opaque]
  claimant_actor_identity_ref: opaque
  current_jurisdiction_ref: opaque
  law_knowledge_pack_revision: opaque
  opened_at_dr: string
  state: PROPOSED | EVIDENCE_PENDING | ACCEPTED_FOR_REVIEW | AUTHORITY_DISPUTED | DECISION_PENDING | PARTIAL | CLOSED_CONFIRMED | REJECTED | UNCERTAIN | STALE
  checkpoint_epoch: integer
RemedyProposal:
  remedy_id: string
  remedy_case_id: string
  damage_id: string
  remedy_kind: ACKNOWLEDGEMENT | PUBLIC_CORRECTION | APOLOGY | SOCIAL_REHABILITATION | ITEM_RETURN | COMPENSATION_PROPOSAL | RELEASE_REQUEST | QUEST_REVIEW | NONE
  issuer_authority_id: opaque
  beneficiary_identity_ref: opaque
  payer_or_source_ref: opaque_or_null
  affected_owner_ref: opaque_or_null
  risk_class: LOW | MEDIUM | HIGH
  consent_receipts: [opaque]
  capability_evidence_ref: opaque_or_null
  authorization_ref: opaque_or_null
  status: PROPOSED | PENDING_EVIDENCE | PENDING_APPROVAL | AUTHORIZED_NARRATIVE | HOST_PENDING | HOST_CONFIRMED | REJECTED | UNCERTAIN
RemedyEffectLedger:
  campaign_id: string
  branch_id: string
  remedy_id: string
  damage_id: string
  affected_target_ref: opaque
  effect_kind: opaque
  rule_revision: opaque
  idempotency_key: opaque
  effect_receipt_ref: opaque_or_null
  resolution_epoch: integer
  commit_state: UNCOMMITTED | NARRATIVE_COMMITTED | HOST_CONFIRMED | UNCERTAIN
```

**Tipos são candidatos.** Não existem esses serviços/APIs no jogo. O `opaque` indica referencial de permissão controlada, não identificador de CRE ou recurso de engine assumido.

## 4. Máquina de estados e fluxos

```text
LegalOrder(REVOKED/ANNULLED/CORRECTED) ou reclamação documentada
                          |
                          v
                  REMEDY_PROPOSED
                          |
                     validação de dano + causalidade + titular
                          |
               +----------+-----------+
               |                      |
        EVIDENCE_PENDING     AUTHORITY_DISPUTED
               |                      |
               +----------+-----------+
                          |
                    REVIEW_ELIGIBLE
                          |
                    decisão competente
                          |
                 REMEDY_DECISION
                /         |         \
          REJECTED     PARTIAL    APPROVED
                         |          |
                         +-- plano por efeito
                                   |
                        gate de risco / consentimento
                                  / \
                          NARRATIVE  ENGINE_IF_SUPPORTED
                              |               |
                        commit overlay   host request
                                              |
                                 HOST_CONFIRMED | UNCERTAIN
```

- `APPROVED` significa autorização condicionada de remédio; **não** significa que o host já executou um efeito.
- `UNCERTAIN` congela reenvio de mutações. `REJECTED` ou `PARTIAL` é resultado possível de ficção, não implica erro de execução.
- A conclusão do caso pode ocorrer com remédios narrativos confirmados e pendências mecânicas não executadas explicitamente documentadas; não dizer `FULLY_REMEDIED` enquanto restar obrigação não cumprida.

## 5. Algoritmo conceitual de revisão

1. **Receber proposta:** decisão/anulação DEC-080 ou queixa vinculada, com quem solicita, contexto, branch, relógio, competência, fatos e danos alegados.
2. **Validar prova de dano:** cruzar receipts DEC-011, evento de encontro DEC-071/073, fontes DEC-061/074 e identidade DEC-066. Pedido sem dano confirmado não inventa dano.
3. **Avaliar causalidade:** data, agente, decisão, exposição causal, existência de causas concorrentes e magnitude; hipóteses incertas ficam pendentes. Não estimar valor econômico por texto LLM.
4. **Consultar política local curada:** autoridade e mecanismo reparatório dependem do ano DR/região/tutela/facção DEC-078/079/060–063. Se política não existe, `PENDING_POLICY`.
5. **Propor alternativas por dano:** diferentes medidas para item, liberdade, reputação ou relações, com titulares, condições, origem de recursos, riscos e capacidades; não presumir reparação universal.
6. **Revalidar privacidade e vontade:** PC dono/delegado, personagens ausentes, consentimento, ACL da audiência e sigilo de testemunhas DEC-019/028/041/045/046/076/077.
7. **Analisar impacto cumulativo:** recursos devolvidos, custo para outro titular/mercado, reputação ou quest; LOW/MEDIUM/HIGH e gates DEC-027/034/050.
8. **Registrar decisão:** pode aceitar, rejeitar, condicionar, suspender, dividir ou requerer nova evidência; autoridades ficcionais podem discordar de forma narrativa, sem alterar o ledger factual.
9. **Executar somente o permitido:** efeitos narrativos LOW allowlisted em overlay; mecânicos via Action Gateway tipado, capabilities de build e host receipt. `HOST_PENDING` não é sucesso.
10. **Publicar correções sem onisciência:** retratação via rede e relógio DEC-029/074; não resetar memórias nem mudar reputação instantaneamente em todos os NPCs.
11. **Deduplicar e reconciliar:** ledger de dano/remédio/beneficiário/efeito/regra por branch; replays ou várias autoridades não duplicam item, ouro, reputação nem restauração de quests.
12. **Auditar e preservar histórico:** manter evento original, reclamação, provas, revisão, decisão e receipts, com ACL e checkpoint, inclusive em resultado parcial ou contestado.

## 6. Política de remédios e gates por domínio

| Medida | Evidência requerida | Gate e resultado seguro |
|---|---|---|
| Pedido de desculpas | Autoridade e decisão contextual | Narrativa segura autorizada, sem alterar inventário ou reputação mecânica |
| Retratação local | Fonte e audiência definidas | Disseminação temporal, reputação contextual, sem onisciência |
| Reabilitação social | Rumor/relato original com proveniência | Correções/novas crenças; memórias antigas persistem |
| Item devolvido | Prova de confisco, ownership atual, item e fonte | HIGH para alteração mecânica; adapter/host receipt, sem duplicar itens |
| Indenização em moeda | Dano e custo/provedor verificados | Economia/ownership, risco, aprovação e receipt; valor não inventado |
| Liberdade recuperada | Detenção realmente ocorrida + competência | Não presumir capacidade de libertação/movimento de NPC/PC na engine |
| Reparação de quest | Flags/contratos nativos conhecidos | DEC-050/051/052; HIGH default-deny, sem editar save ou script arbitrário |
| Danos irreversíveis | História/capacidade/consentimento | Reconhecer limites; sem ressurreição, tempo retroativo ou reset integral |
| Responsabilização da autoridade | Prova de autoria/competência e normas curadas | Proposta e revisão futura DEC-082; nenhuma punição automática |

## 7. Coop, privacidade, identidade e facções

- PC ausente ou sob delegação não aceita compensação unilateralmente; distinguir titular de controlador e alcance de consentimento.
- A vítima pode escolher não buscar reparação, ou aceitar parte, conforme sua agência; o sistema não impõe perdão nem redefine alinhamento.
- Retratação de acusação feita sob pseudônimo pode ser publicada sem expor identidade factual privada; segredo DEC-076/077 protegido por público/finalidade.
- Autoridade corrupta pode recusar reparação e ser contestada ficcionalmente; não inventar tribunal legítimo ou desfecho em região não documentada.
- Facções podem receber notícias corretivas com atrasos e reagir conforme interesses, recursos e regras DEC-030–034/074, sem mudança econômica global automática.

## 8. Segurança operacional e desconhecidos técnicos

- **Sem implementação:** não supor APIs EEex para prisão, confisco, entrega de itens, gold, reputação, scripts, quests ou memória/relacionamentos. Documentar capabilities como `UNTESTED/UNSUPPORTED` até POC.
- **Fronteira host:** somente BG2:EE host atesta efeitos mecânicos com receipts; ação narrativa não se transforma em item de inventário.
- **Consistency:** checkpoint/branch/build/kpack/clock DEC-022/053–055/063; snapshot anterior invalida proposta futura. Operação `UNCERTAIN` não deve ser reemitida cegamente.
- **Backpressure:** priorizar proteção de jogador e evitar dano futuro; reparações complexas podem ficar em fila sem fabricar sentença ou pagamento.
- **Direitos e segredos:** logs de danos e itens com acesso mínimo e redação; nenhuma telemetria de vítima exportada por padrão.
- **Pontos para SPECS:** schemas finais, política de autorização/reparação por região, cálculos, custódia/ownership, antifraude, UI de pedido/contestação, limites de latência e verificações no multiplayer.

## 9. POCs futuras propostas — NENHUMA EXECUTADA

1. Simulador com dois mandados, um revogado e outro válido, danos confirmados e danos não comprovados; impedir compensações fictícias.
2. Testar procedimentos regionais curados de revisão, aceite, recusa, dano parcial e autoridade contestada, sem engine.
3. Aplicar ledger de idempotência/fencing a duas jurisdições sobre o mesmo dano, crashes e restores.
4. Ensaiar retratação em grafo de rumores sem apagar crenças e sem revelar a identidade secreta do PC.
5. Inspecionar BG2:EE/EEex **read-only** para verificar se existem receipts e hooks relevantes de item/reputação/quest, registrando explicitamente ausência.
6. Se autorizado, testar efeito mecânico benigno em instalação de teste isolada com backup/checkpoint, sem mexer em campanhas reais.
7. Host+dois clientes, diferentes mods, reconexão, save/load e idempotência antes de qualquer declaração de suporte.

## 10. Matriz de testes candidatos — 66 casos NÃO EXECUTADOS

| ID | Caso candidato e comportamento esperado | Status |
|---|---|---|
| T081-01 | Caso com mandado revogado sem prisão/dano confirmado não inventa detenção. | NÃO EXECUTADO |
| T081-02 | Revogação por mérito distinto de invalidade não presume culpa da autoridade. | NÃO EXECUTADO |
| T081-03 | Pedido de reparação sem titular confirmado permanece pendente. | NÃO EXECUTADO |
| T081-04 | Uma ordem vencida sem efeitos não gera compensação automática. | NÃO EXECUTADO |
| T081-05 | Dano observado exige vínculo de causalidade, não mera proximidade temporal. | NÃO EXECUTADO |
| T081-06 | Dano sem nexo com o processo é excluído ou marcado contestado. | NÃO EXECUTADO |
| T081-07 | Dano reputacional causado por rumor distingue alegação de fato. | NÃO EXECUTADO |
| T081-08 | Dano material confirmado tem fonte/proprietário rastreáveis. | NÃO EXECUTADO |
| T081-09 | Um item retirado mas já devolvido não pode ser restituído novamente. | NÃO EXECUTADO |
| T081-10 | Item transferido legitimamente a terceiro não é removido como reparação. | NÃO EXECUTADO |
| T081-11 | Proposta de ouro sem fonte de pagamento e regra permanece bloqueada. | NÃO EXECUTADO |
| T081-12 | Valor calculado sem tabela/fonte de época não é inventado pelo LLM. | NÃO EXECUTADO |
| T081-13 | Pedido de reabilitação não apaga reputações históricas das testemunhas. | NÃO EXECUTADO |
| T081-14 | Desculpas publicadas não chegam instantaneamente a todas as cidades. | NÃO EXECUTADO |
| T081-15 | Notícia de retratação segue canal, rota e horário DR plausíveis. | NÃO EXECUTADO |
| T081-16 | Autoridade sem competência curada não concede restituição. | NÃO EXECUTADO |
| T081-17 | Autoridade rival com competência contestada suspende decisão definitiva. | NÃO EXECUTADO |
| T081-18 | Regras modernas de julgamento não são projetadas em região sem fonte. | NÃO EXECUTADO |
| T081-19 | Queixa apresentada sob pseudônimo preserva identidade privada. | NÃO EXECUTADO |
| T081-20 | Publicação de reparação não revela segredo de PC sem ACL. | NÃO EXECUTADO |
| T081-21 | Titular do PC e controlador delegado continuam diferentes. | NÃO EXECUTADO |
| T081-22 | PC ausente não aceita acordo automaticamente. | NÃO EXECUTADO |
| T081-23 | Reconciliação narrativa não impõe perdão ao personagem jogador. | NÃO EXECUTADO |
| T081-24 | Reparação LOW allowlisted pode registrar reconhecimento apenas narrativo. | NÃO EXECUTADO |
| T081-25 | Pedido MEDIUM sem autorização aplicável não é executado. | NÃO EXECUTADO |
| T081-26 | Restituição HIGH sem gate específico e receipt host falha fechado. | NÃO EXECUTADO |
| T081-27 | Série de reparos LOW com magnitude HIGH aciona classificação agregada. | NÃO EXECUTADO |
| T081-28 | Recompensa mecânica não nasce de parecer ou diálogo LLM. | NÃO EXECUTADO |
| T081-29 | Quest nativa incompatível impede efeito mecânico de reparação. | NÃO EXECUTADO |
| T081-30 | Reputação mecânica não é alterada sem adapter/capability por build. | NÃO EXECUTADO |
| T081-31 | Prisão não confirmada no motor não permite afirmar soltura mecânica. | NÃO EXECUTADO |
| T081-32 | Perda de equipamento não comprovada não concede substituto. | NÃO EXECUTADO |
| T081-33 | Caso de reparação pode ter medidas aprovadas e outras negadas. | NÃO EXECUTADO |
| T081-34 | Reparação parcial não declara todos os danos inteiramente resolvidos. | NÃO EXECUTADO |
| T081-35 | Cancelamento de remédio sem efeito preserva histórico e justificativa. | NÃO EXECUTADO |
| T081-36 | Nova evidência gera revisão de caso sem apagar decisão anterior. | NÃO EXECUTADO |
| T081-37 | Um pedido repetido não cria segundo `RemedyCase` conflitante. | NÃO EXECUTADO |
| T081-38 | Múltiplos órgãos não pagam duas vezes o mesmo dano sem regra explícita. | NÃO EXECUTADO |
| T081-39 | Delivery duplicada de evento de retratação não duplica reputação. | NÃO EXECUTADO |
| T081-40 | Operation timeout `UNCERTAIN` não reenvia restituição às cegas. | NÃO EXECUTADO |
| T081-41 | Receipt de host em branch diferente não confirma restituição. | NÃO EXECUTADO |
| T081-42 | Receipt com checkpoint anterior incompatível não é aceito. | NÃO EXECUTADO |
| T081-43 | Receipt de cliente ou worker LAN não confirma transferência de item. | NÃO EXECUTADO |
| T081-44 | Restauração anterior à restituição invalida efeitos de ramo futuro. | NÃO EXECUTADO |
| T081-45 | Alteração de build/mod exige nova prova de capability e ownership. | NÃO EXECUTADO |
| T081-46 | Evento tardio de revisão antiga não sobrescreve reparação posterior. | NÃO EXECUTADO |
| T081-47 | Conflito entre danos estimados e comprovados permanece DISPUTED. | NÃO EXECUTADO |
| T081-48 | Perda de oportunidade sem prova não se converte em ouro automático. | NÃO EXECUTADO |
| T081-49 | Morte/lesão irreversível não é apagada por narrativa de reparação. | NÃO EXECUTADO |
| T081-50 | Reabilitação pública pode ser contestada sem alterar verdade factual. | NÃO EXECUTADO |
| T081-51 | Histórico de dano não é eliminado quando remédio é confirmado. | NÃO EXECUTADO |
| T081-52 | Rumor de autoridade corrupta não produz condenação da autoridade. | NÃO EXECUTADO |
| T081-53 | Autoridade corrupta pode recusar pedido ficcionalmente sem permissionar dano HIGH. | NÃO EXECUTADO |
| T081-54 | Correção de injustiça não altera cânone de Forgotten Realms. | NÃO EXECUTADO |
| T081-55 | Pasta canônica 1369-DR não recebe autos ou restituição da campanha. | NÃO EXECUTADO |
| T081-56 | Knowledge Pack fixado impede leitura anacrônica de normas futuras. | NÃO EXECUTADO |
| T081-57 | Caso de outra campanha não modifica proprietário ou contas locais. | NÃO EXECUTADO |
| T081-58 | Segredo de testemunha não é enviado ao LLM ou nó LAN sem ACL. | NÃO EXECUTADO |
| T081-59 | Logs de reparação redigem identidades, itens privados e razões protegidas. | NÃO EXECUTADO |
| T081-60 | Fila com backpressure mantém pedido pendente sem inventar concessão. | NÃO EXECUTADO |
| T081-61 | Prioridade para evitar dano iminente não cria recibo de mensageiro. | NÃO EXECUTADO |
| T081-62 | Monitor aponta casos em UNCERTAIN sem tentar confisco/restituição automática. | NÃO EXECUTADO |
| T081-63 | Host e dois clientes devem confirmar uma única operação antes de habilitar efeitos. | NÃO EXECUTADO |
| T081-64 | Build não testada reporta UNSUPPORTED sem declarar item devolvido. | NÃO EXECUTADO |
| T081-65 | Reparação narrativamente reconhecida sem motor é rotulada como narrativa, não mecânica. | NÃO EXECUTADO |
| T081-66 | Teste de regressão prova que nenhuma das DEC-060..080/ADRs foi alterada. | NÃO EXECUTADO |

Os testes T081-01..T081-66 são **candidatos**. Nenhuma simulação ou POC real com BG2:EE/EEex/multiplayer foi executada por esta entrega. Requisitos de integração e fórmulas serão tratados em SPECS.

## 11. Próxima escolha — DEC-082 (EM ABERTO)

**Responsabilização de autoridades e instituições após abuso/injustiça comprovados:** A) reparar apenas a vítima, sem examinar a autoridade; B) punir e substituir automaticamente agentes/instituições; **C recomendada)** investigação de accountability institucional com provas, competência, oportunidade de defesa e controles por risco, podendo gerar consequências graduais de reputação, fiscalização e mudança política somente após regras/autorizações e receipt de host quando mecânico. Nenhuma opção aprovada ainda.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

A reparação à vítima DEC-081 não conclui responsabilidade individual, supervisória ou institucional DEC-082; abrir caso separado com provas e competência próprias.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Retificar injustiça não exige revelar indiscriminadamente fonte ou denunciante; reparações e provas podem usar extratos com gates.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Riscos de retaliação decorrentes de reparação podem motivar proteção, mas restituição e avaliação de ameaça são processos independentes com recibos.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Vazamento indevido pode motivar avaliação de reparação apenas após dano e nexo causal confirmados; sem indenização/rollback mecânico automático.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Dano provocado por desinformação só pode levar a reparação com provas e nexos verificados, sem rollback automático ou prêmio por rumor.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Reparação por falsa acusação de agente duplo exige dano/nexo comprovados, não restauração mecânica global.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Promessas de reparação ou remuneração não implicam restituição efetiva; confirmação do dano/pagamento depende de regras e receipts.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Reparação por erro não presume que toda acusação era falsa; avaliação de danos e provas permanece independente e auditável.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Relatório retificado pode fundamentar pedido de reparação contextual, mas restituição não decorre automaticamente da nova redação e exige nexo, autorização e receipts.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Plano de reparação não confere restituição ou efeitos mecânicos automaticamente; requer dano provado, autorização e receipt.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Cancelamento de plano não substitui reparação de dano já confirmado; restituição/compensação seguem avaliação causal separada.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Reparações paralelas não podem pagar duas vezes mesmo dano/mesmo item; dedup e reserva de restituição exigem autoridade e evento mecânico comprovado.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Compensação de dano real difere de liberação de reserva lógica. Nenhum recovery restaura automaticamente bens, reputação ou quest.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Reparação/compensação cria eventos novos autorizados, sem patch retroativo de quest globals.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Reparações dependem de fatos e recibos, não de observação que adivinha responsabilidade.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **reparações**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para reabilitação e reparação precisam de procedimento próprio após correção, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para restituição e reparação exigem autoridade, recursos e recibos, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Reparações e compensações materiais requerem procedimento independente. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Compensação exige novo procedimento autorizado e não rollback automático. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Reparações e devoluções devem gerar novos acordos/ações autorizadas, nunca compensações automáticas a partir de um escrow contestado.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
