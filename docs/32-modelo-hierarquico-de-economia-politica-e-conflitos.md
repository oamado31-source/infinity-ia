# DEC-032 — Modelo preliminar de simulação hierárquica econômica, política e militar

**Discovery v2.9; ADR-0027 aprovada (opção B).**  
**Este documento é candidato para SPECS:** campos, ciclos e testes são propostas técnicas, não decisões de algoritmo/escala já aprovadas.

## Visão de arquitetura

```text
Canon FR + year DR + validated region/faction catalog + campaign historical overlay
                             |
                             v
                   Strategic State Ledger
      (regional nodes/routes, factions, objectives, resources, trust)
                             |
                Activity/importance scheduler
             ACTIVE / NEAR / DISTANT / DORMANT
                             |
                    Deterministic Systems
           Economy | Diplomacy | Logistics | Military
                             |
            Strategic proposal + predicted impact
                             |
            Canon and risk policy (DEC-009/027)
                       /              \
               Valid LOW/MEDIUM       HIGH/unknown
                    |                    |
         Narratives and gateway       BLOCK/PENDING
                    |
      Host confirmation only for in-game mechanical mutations
                    |
          Event log, checkpoint, causality, projections
                    |
        Knowledge/reputation/quests/encounter director
```

**O algoritmo não escreve diretamente no save de BG2:EE e não controla sua simulação mecânica.**

## Escalas de fidelidade e materialização

| Tier DEC-021 | Representação candidata | Gatilhos de recomputação | Resultado permitido |
|---|---|---|---|
| ACTIVE | Pessoas e grupos relevantes observados, condições de encontro, comércio local contextual | Host e eventos de jogadores, transações confirmadas | Propostas narrativas ou ações tipadas; mecânicas só com receipt |
| NEAR | Facções locais e forças agregadas, rotas adjacentes, indicadores de pressão | Evento, deslocamento, checkpoint | Atualizar contextos e candidatos de encounter/quest |
| DISTANT | Agregados por região/facção e lotes temporais limitados | Catch-up autorizado, evento canônico, dependência significativa | Projeções reversíveis e eventos de baixa/média criticidade |
| DORMANT | Snapshot + eventos/obrigações pendentes, sem processamento contínuo | Consulta ou reativação legitimada | Elaborar projeção limitada sob demanda, sem alegar fatos críticos |

Critérios exatos para promoção/demotion de tiers e frequência de atualização ainda serão especificados.

## Entidades e limites candidatos

| Tipo | Campos mínimos sugeridos | Invariantes |
|---|---|---|
| `region_node` | stable_id, DR active_range, neighbors, roads, waterways, terrain, control_source | Grafo histórico verificável; caminho não implica área carregável |
| `route_edge` | endpoints, kind, capacity_band, travel_time_band, safety, restrictions | Trânsito, calendário e fronteiras respeitados |
| `faction_strategic_state` | faction_id, campaign_id, objectives, influence_by_region, budget, reserves, forces_proxy | Não converter automaticamente para NPCs ou moedas de BG |
| `regional_economy` | supply_band, demand_band, trade_access, stability, prosperity_proxy, source_revision | Sem preço de loja nativo sem POC/host |
| `diplomatic_relationship` | parties, stance, trust, commitments, knowledge_scope | Alianças e hostilidades com datas/proveniência |
| `army_abstract_unit` | faction, regional_location, strength_band, readiness, upkeep_band, supply_band | Exército abstrato não é uma horda spawnada no mapa |
| `strategic_event` | event_id, cause_id, dr_time, actors, impact_type, classification, state, seed | Proposta vs confirmada, idempotência, aprovação HIGH |
| `world_projection` | from_revision, to_revision, tier, plan, simulated_range, commit_status | Replay auditável, derivação sem efeitos duplicados |

`*_band` sinaliza índice qualitativo ou faixa; nenhuma escala/quantidade foi aprovada.

## Regras candidatas — economia

1. Região possui produção/capacidade agregada, demanda, reserva e rotas elegíveis em determinado período DR.
2. Entrada/saída de bens só atravessa caminhos válidos; impedir comunicação instantânea e teletransporte econômico sem regra aprovada.
3. Perdas de segurança ou bloqueios podem reduzir trânsito; reduzir trânsito pode elevar escassez; aumento da escassez pode desencadear oferta de missões, pressão política ou compra de suprimentos.
4. Custos de recrutamento/expedição geram obrigações de recursos; não gerar dinheiro ou tropas infinitas por recálculo.
5. Indicadores simbólicos devem distinguir fato confirmado (ex.: rota assaltada pelo grupo), inferência de modelo (ex.: risco de escassez) e evento aprovado (ex.: comerciante envia pedido de escolta).
6. Mudança em inventário, preços reais das lojas ou acesso a equipamentos exige operação definida, autorização e confirmação mecânica — não é efeito automático de índices.

## Regras candidatas — política e diplomacia

- Avaliar objetivos de facção por contexto: preservar território, garantir abastecimento, manter alianças, influenciar autoridades, responder a ameaças.
- Separar `proposal` de `commitment` e `confirmed_outcome` para evitar tratados, guerras ou golpes declarados pela própria IA.
- Negociações representam decisões calculadas por regras e reações de acordo com confiança, recursos, personalidade e compromissos; LLM só redige diálogo autorizado quando há interlocutor relevante.
- A cronologia e a identidade política de Forgotten Realms não são apagadas por simulação macro.
- Conhecimento de movimentações militares, boatos e negociações é distribuído por rotas/tempo de acordo com DEC-028/029, não é universal.

## Regras candidatas — militar e conflito

- Exércitos distantes são **reservas abstratas** com suprimento, prontidão, localização regional e custos; não criar cada soldado.
- Transporte/ação militar consome tempo e pode ser bloqueado por rotas, território ou disponibilidade.
- Confrontos menores podem gerar projeções narrativas e encontros opcionais, dependendo de risco e autoridade; **mudança histórica irreversível (`HIGH`) permanece PENDING/BLOCKED**.
- Conflito próximo ao jogador pode gerar patrulhas, emboscadas e oportunidades de negociação **somente após validar recursos e operação mecânica do host**.
- **A resolução final de guerras, cercos, exércitos e a transição entre batalha abstrata e BG2:EE é tema da DEC-033 (aberta).** Esta ADR não autoriza autoresolver guerras canônicas.

## Exemplo causal — ilustrativo, sem fórmulas estabelecidas

```text
[Confirmed] jogadores protegem caravana em estrada importante
   -> rumor/segurança local: atualização narrativa permitida
   -> simulação avalia melhoria potencial de acesso comercial
   -> ledger agrega indicador de abastecimento da cidade
   -> facção mercantil pode propor nova rota ou contrato
   -> Encounter Director gera encontros contextuais validados
   -> gateway requisita, host confirma ações mecânicas locais
   -> event log e snapshot persistem apenas efeitos autorizados
```

Exemplo negativo: uma guilda decide atacar um reino. O módulo estratégico **pode gerar uma proposta para análise**, mas não declarar automaticamente guerra, matar o monarca ou ocupar uma cidade do cânone porque o risco pode ser `HIGH`.

## Regras para tempo, catch-up e reversão

- Regras e seeds devem ser versionadas por campanha; reabrir save não pode avançar a economia duas vezes.
- Se o relógio está `FROZEN`, não se aplicam lotes estratégicos; se `PARTIAL` ou `REALTIME`, respeitar limites previamente autorizados (DEC-022).
- Um batch de simulação não produz efeitos irrevogáveis por inferência; resultados dependentes de confirmação ficam `PROPOSED` ou `UNCERTAIN` e passam pela reconciliação.
- Mudança de tier não pode criar exércitos, mercadorias ou conhecimento novos sem trilha de causalidade.
- Multiplayer: o host define relógio/autoridade mecânica e os clientes consultam projeção autorizada; não permitir simulações estratégicas concorrentes com commits múltiplos.

## Instrumentação e testes candidatos

| ID | Cenário | Aceitação candidata |
|---|---|---|
| STRAT-01 | 200 organizações catalogadas, poucas relevantes | Simular apenas entidades elegíveis por tier e budget |
| STRAT-02 | Região distante DORMANT | Não manter loop de NPC individual / LLM |
| STRAT-03 | Bloqueio confirmado de estrada | Abastecimento/segurança mudam no modelo, sem invenção de alteração mecânica |
| STRAT-04 | Bloqueio removido | Estado deriva de eventos reais, não duplica recursos ao reprocessar |
| STRAT-05 | Recrutamento | Recursos agregados sofrem custo; não surgem tropas gratuitas |
| STRAT-06 | Avanço de campanha congelado | Nenhuma atualização de projeção fora de operações explicitamente autorizadas |
| STRAT-07 | Ausência longa e catch-up limitado | Apenas lotes permitidos; checkpoint evita repetição |
| STRAT-08 | Reabertura repetida de save | Estado estável e idempotente; mesmo seed/revisão => mesma projeção |
| STRAT-09 | Facção fundada após 1369 DR | Não atua no ano-base |
| STRAT-10 | Guerra canônica futura antes do gatilho temporal | NÃO antecipar guerra |
| STRAT-11 | Proposta de golpe contra figura canônica | HIGH bloqueado sem política especial |
| STRAT-12 | Simulação declara vitória sem battle do host | Proibido tratar como resultado mecânico confirmado |
| STRAT-13 | Região promovida DISTANT→ACTIVE | Materialização consistente com registros e assets disponíveis |
| STRAT-14 | Falta de área instalada para facção | Influência abstrata pode existir, NPC físico não |
| STRAT-15 | Dois clientes em jogo | Não divergir regra de estratégia nem duplicar transações |
| STRAT-16 | Rumor falso de guerra | Conhecimento individual pode mudar; estado de guerra real não |
| STRAT-17 | Mercado local supostamente encareceu | Loja BG permanece sem alteração automática sem contrato mecânico |
| STRAT-18 | Simulador de economia executado repetidamente | Testar ausência de inflação artificial e invariantes de estoque |
| STRAT-19 | Carga com muitas regiões e facções | CPU, memória, filas e latências medidos versus baseline; limites numéricos a definir |
| STRAT-20 | Modo Original vs Living World | Sem contaminação de saves, NPCs ou cálculos |

## Provas de conceito propostas (ainda não executadas)

1. **POC-STRAT-01:** simulação externa determinística de três regiões e duas facções com rotas, segurança e recursos agregados, totalmente sem BG2:EE.
2. **POC-STRAT-02:** persistência com snapshots e eventos, replay e catch-up FROZEN/PARTIAL, incluindo alteração de tier.
3. **POC-STRAT-03:** validação de conhecimento/cânone/autorização de eventos e preço contextual **somente narrativo**.
4. **POC-STRAT-04:** gateway e host em BG2:EE/EEex quando POCs da DEC-003 permitirem, ativando efeitos locais isolados.
5. **POC-STRAT-05:** multiplayer de dois clientes, falhas/reconexões, equivalência de estado, rollback e rastreabilidade.

## Pendências de SPECS

Definir unidades e categorias de recursos, atualização estratégica por calendário, critérios de distância e relevância, orçamento de processamento, modelos de confiança e prosperidade, fonte canônica do grafo, regra de inflação, resolução de guerras (DEC-033) e critérios de teste em Windows/EEex.

## Integração DEC-056 — limites e prioridade por região (Discovery v5.2)

A simulação econômica/militar de DEC-032 é gerenciada por classes P2/P3 conforme atividade da região, com coalescência de lotes somente quando preserva as mesmas dependências/causalidade. Produção, recursos e objetivos têm revisões/checkpoints auditáveis; backlog não permite inventar batalhas, mudanças de território ou efeitos no motor. Sob carga, reduzir detalhe em regiões distantes antes de comprometer interação local e recibos do gateway. Fairness limitada e limites de catch-up impedem crescimento infinito de trabalho. Parâmetros e tempos de ciclo ficam para SPECS; ver ADR-0051/doc.56.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

Em DEC-068, simulação estratégica DISTANT opera por agregados/lotes, sem forçar decisões individuais permanentes de todos os comerciantes ou membros de facções. Resultados estratégicos não geram automaticamente consequências mecânicas sobre NPCs persistentes: verificar risco e host.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: rotas comerciais e mobilidade NPC são grafos/eventos regionais versionados; bloqueios e custos precisam de evidência. Não simular pathfinding contínuo nem reescrever economia automaticamente.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

Incidentes de viagem DEC-070 podem afetar transporte/economia somente após efeito autorizado e sem duplicar perdas agregadas; risco da rota é variável contextual, não saque consumado ou colapso de mercado.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Um evento estratégico que propõe encontro local DEC-071 mantém causalidade e seu identificador de ocorrência. Exibição local não autoriza mudar balanços de poder/frotas/economia sem resultado validado; uma simulação distante não resolve simultaneamente o mesmo evento sob reserva.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Impactos econômicos e geopolíticos DEC-074 requerem regras de domínio, causa e escala verificáveis, limites agregados e autorização de risco; boato sozinho não cria comércio ou desabastecimento real. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Julgamentos e litígios DEC-078 não mudam mercados, poder militar, tesouros ou controle de território de forma automática; todo efeito estratégico requer regra causal e limites DEC-032/033.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Conflito entre autoridades DEC-079 pode gerar propostas políticas/econômicas apenas por regra causal proporcional; pedido isolado não altera preços, frotas ou guerras.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Restituição de ouro/bens DEC-081 requer orçamento/fonte/propriedade reais; não criar dinheiro sem mecanismo econômico autorizado nem aplicar compensação em duplicidade.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Mudanças macroeconômicas e políticas por investigação exigem causalidade/evidência distinta, limites de risco e DEC-034 para eventos irreversíveis.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Denúncia confidencial isolada não desencadeia mudança de poder ou economia; atribuição institucional e efeitos estratégicos têm gates próprios.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Recursos de abrigo, guardas e transporte não são infinitos; reservas de proteção afetam apenas estado validado e não geram automaticamente mudança econômica.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Custo de vigilância, proteção e mudança de abrigo depende de recursos verificados; vazamento não cria economia nem guerras e não contorna gates HIGH.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Operações de isca têm custo e risco, não orçamento infinito; não propagar efeito político/econômico por rumor não confirmado sem causalidade e gates.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Incentivos, pagamentos e dívidas ligados a informantes são compromissos sob recursos e provas; o sistema não deve cunhar moeda ou custo sem host receipt, nem inferir lealdade comprável.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Promessas de ouro, bens, favores e serviço devem respeitar budgets, saldos, reservas, origem e confirmations; contrato não cria riqueza infinita nem empréstimos automáticos.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Simulação estratégica não deriva decisão de guerra/economia de informe inconclusivo. Perfis de fontes são contextualizados por época, tema e conflitos de interesse.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Inteligência distribuída pode orientar análise política, mas informações inconclusivas em dossiê não geram automaticamente transferências econômicas ou ações estratégicas irreversíveis.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Recursos estratégicos utilizados por planos têm identidade/ledger e disputas; reserva não equivale a consumo em mundo ou no motor.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Recursos econômicos reservados para plano antigo não são restituídos por texto de abortar; contratos de lease, consumo, release e receipt mantêm consistência.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-094/C (Discovery v9.0)

Reserva em conflito não é recurso gastado; relés de starvation e liberação só afetam disponibilidade lógica e não podem criar ouro ou serviços de facção.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Proposta DEC-096 separa efeitos diretos/indiretos econômicos por prazo, região e limites; caps/decay e receipts evitam inflação infinita, sem criar recursos por narrativa.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Eventos históricos DEC-096/C podem propor oferta/risco/preço com limites; jamais alteração econômica automática sem composição DEC-097, resources/gates e confirmação.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Para economia regional, DEC-097/C requer política dimensional, caps, proveniência e agregação sem stacking de impactos correlacionados.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Variáveis econômicas projetadas e valores de mundo devem respeitar campos protegidos e comprovados por build.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Simulação estratégica não lê flags privadas indiscriminadamente nem usa spoiler para antecipar impacto econômico.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para economia regional não muda apenas por rumor retificado, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para economia não retorna a estado anterior só por retratação, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-109/C — Obrigações condicionais multipartes

Simulação econômica não gera caixa e bens para cumprir contratos. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
