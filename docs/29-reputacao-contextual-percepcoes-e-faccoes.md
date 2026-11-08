# Reputação contextual, percepções e observadores — desenho técnico preliminar

**Discovery v2.7** · **DEC-030 / ADR-0025 aprovada (opção B)**  
**Natureza:** arquitetura candidata para SPECS; **nenhum código implementado, integração/POC executada ou escala numérica aprovada**.

## Objetivo

Calcular e registrar percepções individuais e coletivas coerentes com **aquilo que o observador sabe**, o contexto e os interesses pertinentes. O sistema não pode tomar a verdade global, o conhecimento privilegiado do narrador ou um rumor como conhecimento automaticamente acessível a NPCs.

## Modelo de separação

```text
Event Log + fatos confirmados / canon da campanha (DEC-008/009)
                  |
                  v
Eventos presenciados e relatos legitimamente recebidos (DEC-028/029)
                  |
                  v
Beliefs / Claim Provenance (pode conter rumores falsos)
                  |
                  v
Rule-based Reputation Projector (por observador + alvo + contexto)
                  |
          +-------+-----------------------+
          |                               |
          v                               v
NPC / Faction / Region              Observed narrative projections
perceptions                         (fama, confiança, temor,
                                    hostilidade, respeito etc.)
          |                               |
          +---------------+---------------+
                          |
                          v
      Dialogue context filtered per NPC, safe social proposals
                          |
                          v
           DEC-027 risk -> DEC-012 gateway -> DEC-011 host receipt
                      (se houver efeito mecânico)
```

## Entidades lógicas sugeridas (não schemas finais)

| Entidade | Campos candidatos | Invariantes |
|---|---|---|
| `reputation_subject` | `campaign_id`, `subject_id`, `subject_type` (character/party/persona), `identity_links` | Indivíduo e grupo separados; aliases não expostos automaticamente |
| `reputation_observer` | `campaign_id`, `observer_id`, `observer_type` (npc/faction/region), `membership_context` | Região e facção não são oniscientes; divergências locais possíveis |
| `reputation_evidence` | `event_id`, `claim_id`, `belief_id`, `source_chain`, `observed_at_dr`, `confidence`, `visibility` | Fato e rumor separados; autorização DEC-028 |
| `reputation_projection` | `observer_id`, `subject_id`, `dimension`, `value`, `as_of_dr`, `rule_version`, `projection_version` | Projeção reconstruível; escalas/valores ficam para SPEC |
| `reputation_adjustment` | `adjustment_id`, `campaign_id`, `cause_event_id`, `rule_id`, `seed`, `idempotency_key`, `status` | Sem efeito duplo por save/replay |
| `reputation_policy` | `scope`, `allowed_dimensions`, `feature_flags`, `risk_level`, `requires_host_receipt` | Default-deny para efeito mecânico ou identidades sigilosas |

## Distinções semânticas

- `FAME / NOTORIETY`: quantas pessoas no escopo podem reconhecer nome/feitos, *não* aprovação moral.
- `TRUST`: expectativa de confiabilidade conforme experiência, interesses e crenças.
- `FEAR`: potencial de coerção/temor percebido, que pode coexistir com respeito.
- `HOSTILITY`: disposição adversarial, não significa obrigatoriamente agressão mecânica.
- `RESPECT / PRESTIGE`: reconhecimento de posição ou feitos sem implicar amizade.

A codificação exata dos eixos, número de dimensões, pesos, faixa ou escala será objeto de SPEC. Não assumir valores ilustrativos 0–100 como definição.

## Pipeline de atualização proposto

1. Receber acontecimento autorizado/confirmado ou alegação conhecida por observador.
2. Validar campanha, instante histórico, identidade efetivamente reconhecida, emissor/proveniência, nível de acesso e tipo de fonte.
3. Identificar avaliador e alvo (personagem, grupo ou persona) sem extrapolar atribuição de culpa para todos os membros.
4. Aplicar regra idempotente de alteração das **percepções**, respeitando afinidades e contexto. Uma fonte pode alterar fama sem alterar confiança.
5. Persistir causa e projeção vinculadas a versão de regra e checkpoint; recuperar via event sourcing + snapshots (DEC-008).
6. Disponibilizar a dimensão autorizada no contexto de diálogo de um NPC, sem dados de pessoas ou fatos secretos não conhecidos por ele.
7. Se a reputação motivar ação, avaliar risco DEC-027 e chamar DEC-012; resultados mecânicos exigem recibo do host DEC-011.
8. Processar regiões distantes por lotes e NPCs dormentes sob demanda, conforme DEC-021/022; sem LLM permanente.

## Proteções específicas

**Segredos e disfarces:** não inferir automaticamente que duas identidades são uma só; vazamentos por explicação ou por números de reputação também contam como vazamentos. Descobertas do jogo somente alteram identidade/atribuição com fato legítimo, autoridade e política de divulgação.

**Boatos falsos:** a reputação contextual pode ser injusta, mas suas causas permanecem crenças e rumores; NPCs não reescrevem o canon.

**Reputação da facção:** valores agregados não determinam a opinião de cada membro. Membros podem desconfiar de uma pessoa aprovada pela facção e vice-versa. O ganho de confiança de um membro não vira ganho automático na facção.

**Economia e combate:** nenhuma chamada direta para alterar preço, agressividade, reputação nativa, itens ou objetivos de NPC no BG2:EE. Esses efeitos requerem feature, gateway e recibo host validados.

**Farming e repetição:** registrar identidade do evento causador, janelas e chaves de idempotência; impedir múltiplas recompensas sociais por repetição de evento/reconnect/saves. A política para ações genuinamente repetidas fica para SPECS.

**Retcons/revisões:** preservar crenças e causas historicamente observadas; correção de estado deve seguir DEC-020 e permitir reprocessamento auditável, nunca apagar desavenças automaticamente.

## Testes candidatos

| ID | Situação | Resultado esperado |
|---|---|---|
| REP-01 | Mercadores testemunham resgate e guardas não | Percepção distinta por observador |
| REP-02 | Facção criminosa recebe notícia do resgate | Hostilidade pode mudar sem implicar fama global |
| REP-03 | Região sem conexão/rumor | Reputação fica inalterada |
| REP-04 | Rumor negativo falso | Crença e opinião podem mudar; verdade oficial permanece |
| REP-05 | Personagem disfarçado age sem ser reconhecido | Não associar automaticamente à identidade real |
| REP-06 | Jogador A age sozinho | Jogador B/grupo não herdam culpa sem fonte/regra válida |
| REP-07 | NPC membro de facção discorda do grupo | Projeções não colapsam em reputação faccional |
| REP-08 | Fama aumenta e confiança não | Dimensões independentes |
| REP-09 | Segredo conhecido só pelo narrador | NPC não recebe aumento/queda de reputação induzido pelo segredo |
| REP-10 | Novo relato corrige rumor anterior | Trilha causal e crença histórica preservadas; ajuste controlado |
| REP-11 | Save reaberto, mesma alteração reexecutada | Nenhuma duplicidade de reputação |
| REP-12 | Outro save/campanha/Original | Isolamento completo; mecânica nativa preservada |
| REP-13 | Cliente multiplayer retorna | Estado de reputação coerente, sem cálculos divergentes |
| REP-14 | Reputação propõe spawn, agressão ou mudança em preços | Bloqueio sem gateway/host/feature compatível |
| REP-15 | Regiões DISTANT e DORMANT | Projeções em lotes/sob demanda, zero LLM por tick |
| REP-16 | Facção majoritária e NPC individual divergem | Consultas respeitam escopo e individualidade |
| REP-17 | Ação idêntica repetida sem novo fato | Idempotência e regras antifarm preservadas |
| REP-18 | Evento histórico futuro de Forgotten Realms | Nenhuma opinião antecipada sem notícia legitimamente recebida |

## Métricas candidatas

- Consistência de projeções após replay; percentagem de mudanças sem proveniência (esperado zero); vazamentos de dados por prompt/log; divergências de percepção host/cliente; tempo de processamento por lote; crescimento de memória de reputação; número de inferências LLM usadas para atualização determinística (alvo zero).

## Pendências e próxima discussão

- **DEC-031 em aberto:** estrutura e autonomia operacional de facções (objetivos, alianças, recursos, disputas, influência sobre territórios). Aprovar reputação contextual **não** aprova facções autônomas.
- Fórmulas, limites e taxas de mudança/correção, alinhamento moral, efeito mecânico sobre BG2, visualização para jogadores, identificação de disfarces, agrupamento regional/faccional, migração e persistência detalhada.
- Construção de código e testes com BG2:EE, EET, mods, EEex e 2 clientes multiplayer **não executados**.

## Integração DEC-063/C — percepção contextual não equivale a verdade editorial (v5.9)

O catálogo revisado pode alterar a evidência histórica disponível, mas reputação e crença de facções/NPCs continuam produtos de experiências e informação legitimamente adquirida. Não recomputar retroativamente percepção/reputação nem efeitos mecânicos a partir de uma revisão editorial. Mudanças de conhecimento individual ficam para DEC-064 e ações mecânicas exigem host/gateway.

## Integração DEC-064/C — aprendizado e crenças sem onisciência (v6.0)

A DEC-064/C permite que NPCs reconsiderem percepções conforme testemunhos, provas e experiências legítimas, preservando a memória de sua avaliação anterior. Isso não recalcula automaticamente reputação social, alinhamento, favores ou conflitos sem regras/contexto e gates próprios DEC-030/035–037. Correção editorial de cânone não implica reputação alterada nem ciência imediata da facção.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

Promover figurante DEC-067 não gera reputação inicial inventada. Relações e opinião derivam de eventos/rumores legitimamente recebidos e provados; status agregado não equivale a confiança individual.

## Integração com DEC-070/C — Discovery v6.6

Incidente DEC-070 pode influenciar percepção/rumor apenas sob regras DEC-029/030; mudança mecânica de reputação ou alinhamento exige gate específico, nunca efeito lateral de LOW.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Reputação DEC-074 deriva de exposição legítima, participação e crença regional; não é mudança instantânea global nem alteração da variável nativa de BG2:EE. DEC-075 definirá autoria e distribuição de crédito. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Reputação DEC-075 recebe propostas de reconhecimento por observador e facção; participação factual não equivale a fama, e fama não altera a variável mecânica do BG2:EE sem gate.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Reputação contextual pode se associar a persona pública e público local, separada de fato privado do ator. Descobrir pseudônimo não funde automaticamente reputações; efeito exige origem, testemunho, risco e idempotência.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação e consentimento (Discovery v7.3; não implementada)

A DEC-077/C distingue hipótese investigativa e reputação percebida de prova de identidade; acusações podem ser falsas. Não aplicar fama, culpa ou efeito mecânico como se a suspeita fosse fato comprovado. Correções preservam o histórico de crenças e exigem efeitos causais autorizados. Cânone permanece fisicamente particionado por ano DR; investigação só no overlay privado da campanha/ramo. ADR-0072 e documento técnico 77, 58 testes não executados.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Uma decisão de autoridade DEC-078 pode influenciar percepções locais mediante provas/rumores e gate, sem alterar reputação mecânica do BG2:EE ou misturar fatos com crenças.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Boato de ser procurado DEC-079 pode alterar percepção contextual autorizada, mas não é culpa factual, condenação nem reputação mecânica nativa; impacto por fonte/risco e dedup.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Retificação/revogação DEC-080 não funde reputação ou desmente rumor globalmente na mesma hora; correções de crença e reputação seguem DEC-029/030/074 e critérios próprios.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Reabilitação social DEC-081 não reseta universalmente reputações; altera propostas localizadas por evidência, conhecimento e regra, preservando memória do dano anterior.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Reputação de agente e instituição separadas; notícia sobre abuso não gera punição ou má-fama global automática, e provas controlam propostas por região.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Reputação de fonte, acusado ou facção não muda pelo simples sigilo; requer fatos/relatos causalmente recebidos e regras contextuais.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Proteger fonte ou ser acusado de retaliação não altera reputação global automaticamente; consequências só com fatos, relatos e regra contextual.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Descoberta de possível abrigo é percepção localizada e não altera confiança, fama ou hostilidade automaticamente; efeitos exigem origem e regra válida.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Crenças sobre falsidades podem afetar percepções localmente após evento legítimo, não reputação mecânica host nem culpa confirmada. Descoberta do engano pode revisar crenças sem retcon.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Confiança e reputação atribuídas por observador diferem de lealdade factual; boatos de traição não colapsam todas as reputações instantaneamente.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Contratar informante não gera reputação positiva/negativa automática; consequências sociais exigem fatos de descoberta e atribuição comprovada.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Reputação de uma fonte não é certificação de veracidade; boato sobre guilda sem prova não gera mudança automática de confiança, temor ou alinhamento.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Relatórios podem alterar crenças e reputação social apenas por exposição, avaliação e consequência causal autorizadas; o ato de compilar um relatório não concede reputação mecânica.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Reputação não muda porque plano de vigilância foi proposto; somente eventos confirmados/percebidos podem gerar impacto social localizado.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Mudança de plano e abandono não apagam reputações ou rumores anteriores; só atos confirmados geram novas consequências contextuais.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Disputar recursos operacionais ou entrar na mesma região não altera reputação automaticamente; efeitos sociais requerem acontecimentos/observações confirmados.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

A matriz cronológica proposta DEC-096 pode sugerir alterações de reputação locais, nunca atribuir culpa global ou reputação automática sem evento confirmado, observador e canais.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

DEC-096/C separa ocorrência de transmissão: rumor local surge só via canal verificável/atraso, não por escala GLOBAL do evento.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Compor impactos DEC-097/C NÃO distribui conhecimento do evento a NPCs automaticamente; difusão usa canais causais.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Materializar patrulha não produz conhecimento global: rumor/relato exige difusão causal e atraso mesmo quando efeito local foi host-confirmed.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Conhecimento de NPC só decorre de canais de comunicação/observação legítimos, nunca do acesso interno da engine.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração DEC-102/C (Discovery v9.8)

Rebase de quest DEC-102 não altera reputação nem crenças até evidência e propagação autorizadas. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** a conclusão técnica de uma quest não concede automaticamente conhecimento ou crença a NPCs/facções. `QuestMilestoneAdmission` pode gerar proposta de notícia/reputação somente por regras, proveniência, tempo, geografia, visibilidade e ACL; notícia requer fonte/canal/delivery, e seus destinatários podem conhecer apenas versões parciais. Não expor identidades secretas, fontes protegidas ou raw flags por prompts/logs/dossiês. Ações mecânicas derivadas dependem de recibos host, sem atribuição presumida de PC. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **rumores e difusão**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para reputação social não se restaura automaticamente quando correção circula, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para reputação social e restauração não automática, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Aviso enviado é distinto de entregue, percebido e aceito. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Mensagem de condição atendida não é notícia automaticamente entregue. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Inadimplemento contestado de garantia não significa fraude nem perda automática de reputação.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
