# Desenho preliminar — simulação por níveis de atividade (DEC-021)

**Discovery v1.0** · **Estado:** desenho preliminar, não SPEC aprovada · **Fundamento:** ADR-0009.

## Objetivo

Dar continuidade ao mundo entre visitas do grupo sem gastar recursos para simular continuamente regiões que não estão sendo exploradas. Preservar a distinção entre fatos narrativos persistidos pelo Infinity AI e resultados mecânicos confirmados pelo host (DEC-011).

## Política lógica dos níveis

| Nível | Entrada típica | Execução prioritária | Evitar | Saída/transferência |
|---|---|---|---|---|
| `ACTIVE` | Jogadores presentes; host carregou área | Comportamentos existentes no jogo, eventos de jogador, NPCs relevantes, respostas IA sob demanda | Simulação paralela concorrente de combate/inventário | Registrar eventos confirmados e reduzir atividade quando jogadores partirem |
| `NEAR` | Região ligada à rota/evento de jogadores, mas não carregada | Agendas e transições por regras, filas de rumores e perseguições, gatilhos leves | Pathfinding por NPC/frame, combate detalhado fora de cena | Reavaliar prioridade e materializar sob validação se houver entrada |
| `DISTANT` | Região longe sem jogadores, porém com linhas narrativas relevantes | Eventos por lotes, evolução de facções, trajetos e comércio em nível agregado | Inferência contínua e duplicação de entidades reais | Guardar resultados, cursor e dependências para reidratação |
| `DORMANT` | Região sem atividade nem ganchos prioritários | Nenhum loop por NPC; atualização sob demanda e com orçamento | Recriar todo histórico ao reentrar | Recuperar snapshot + processar lote limitado se política de tempo permitir |

**Nota:** `NEAR` não é distância euclidiana obrigatória; pode ser vizinhança de viagem, relevância narrativa ou vínculo de facção. Os thresholds e a frequê​ncia de transições estão pendentes de SPEC.

## Modelo de dados candidato

```text
RegionRuntimeState
  campaign_id, region_id, mode (ACTIVE|NEAR|DISTANT|DORMANT)
  state_revision, ruleset_version, seed
  last_simulated_world_time, last_processed_event_id
  checkpoints, relevant_story_threads, pending_mechanical_effects

OffscreenEvent
  event_id, campaign_id, region_id, trigger, interval_start, interval_end
  actor_ids, target_ids, preconditions, outcome_kind, origin (RULE|LOCAL_LLM)
  canon_scope, knowledge_provenance, approval_status
  mechanical_materialization (NONE|PENDING|CONFIRMED|REJECTED|UNCERTAIN)

SimulationBatch
  batch_id, campaign_id, region_id, from_revision, to_revision
  interval, seed, ruleset_version, status, checkpoint_id, metrics
```

São sugestões de contrato, não tabelas SQL ou mensagens implementadas. Quotas, locks, regras de conflito e formato final serão especificados após DEC-008, DEC-009 e DEC-022.

## Exemplo operacional

Os jogadores saem de Neverwinter rumo a outra região. Um mercador deixa de ser entidade ativa e passa a ter agenda agregada. Ao longo do **tempo do mundo autorizado**, regras podem marcar que ele iniciou uma viagem. Quando o grupo retorna, o serviço consulta o último checkpoint e calcula apenas os acontecimentos necessários: o mercador pode ter retornado, contratado escolta ou espalhado um rumor. A narrativa explica a mudança sem exigir um NPC simulado continuamente.

Se o lote propuser a existência de guardas ou criaturas no mapa, a criação real deverá ser requisitada e confirmada pelo host ao carregar a área; a persistência narrativa não pode assumir que o spawn foi bem-sucedido. Uma mudança drástica, como morte de NPC canônico, não é automaticamente autorizada.

## Controle de carga e concorrência (proposta)

1. Processar primeiro `ACTIVE`, depois `NEAR`; `DISTANT` apenas dentro do orçamento; `DORMANT` sob demanda.
2. Usar chave idempotente por campanha/região/intervalo/versão e revisão de estado para evitar duplicações.
3. Recalcular um lote com seed fixo deve recuperar o mesmo resultado de regras; conteúdos livres gerados por LLM podem precisar ser armazenados para replay, sem assumir determinismo da inferência.
4. Nunca confiar que um evento de outro cliente foi executado até obter evidência do host.
5. Congelar/apartar dados de sessão de cada campanha; o modo Original não acessa mutações do Living World.
6. Usar filtros de conhecimento por NPC/ator para impedir vazamento de históricos privados.
7. Fazer catch-up limitado e paginado após inatividade longa; não aplicar milhares de eventos de uma só vez.

## Futuras SPECS / features candidatas

- `SPEC-SIM-001` — Classificação de atividade e transição de regiões.
- `SPEC-SIM-002` — Simulação de rotinas próximas sem LLM.
- `SPEC-SIM-003` — Simulação distante em lotes reproduzíveis.
- `SPEC-SIM-004` — Reidratação de região e reconciliação com o host.
- `SPEC-SIM-005` — Orçamento de simulação, medição e degradação controlada.

IDs são sugestões, não SPECS aprovadas. Implementação depende dos testes de bridge/multiplayer e decisões sobre relógio/persistência/canon.

## Pendências rastreadas

- **DEC-022 (próxima discussão):** evolução do relógio do mundo durante ausência dos jogadores e com o jogo fechado.
- **DEC-008:** quais estados são persistidos e como recuperar um checkpoint.
- **DEC-009:** limites canônicos para NPCs famosos, morte, saque e acontecimentos irrevogáveis.
- **DEC-006:** configuração de modelos locais, hardware e limites de inferência.
- **DEC-015:** testes de aceite para simulação, desempenho e sincronização multiplayer.

**Nenhum algoritmo, mod ou infraestrutura de simulação foi executado nesta atualização.**


## Companheiros fora da party — DEC-049 (v4.5)

A mesma divisão ACTIVE/NEAR/DISTANT/DORMANT passa a abranger ex-companheiros NPC após **saída confirmada**, com identidade e objetivos persistentes. Projeção distante é um checkpoint auditável, não posição física do motor; reidratação para reencontro depende de recurso/área, reconciliação de host, cronologia e ausência de duplicidade. Nenhuma inferência por NPC por tick. Ver ADR-0044/doc. 49.

## Integração posterior — DEC-055 (Discovery v5.1)

Se um worker regional falhar, suspender avanços dependentes dele sem inventar ticks concluídos. Catch-up após retorno só usa relógio, checkpoints, filas e evidências coerentes, respeitando DEC-021/022/032 e proteção de eventos HIGH. O monitor deve distinguir worker ativo de simulação confirmada. Ver ADR-0050/doc. 55.

## Integração DEC-056 — prioridade, backlog e catch-up (Discovery v5.2)

Os níveis ACTIVE/NEAR/DISTANT/DORMANT são entradas do orçamento adaptativo, não garantias de ticks. Sob combate/pressão, lotes distantes cedem capacidade, mas devem preservar intervalo de mundo, seed/versão/revisão de regras e watermark para retomada determinística; não há evolução de relógio por espera em fila. Fairness limitado evita starvation, condicionado à proteção da partida e do estado. Jobs obsoletos por rewind/build/ACL não podem publicar eventos. O RPD não autoriza spawns nem resultados mecânicos offscreen. Ver ADR-0051/documento 56.

## Integração DEC-064/C — aprendizado e crenças sem onisciência (v6.0)

Nas regiões ACTIVE/NEAR, aprendizagem depende de encontro, documento ou canal validado; DISTANT processa transmissões e reavaliações em lotes delimitados; DORMANT aguarda reidratação segura. DEC-064/C não cria boatos ou aprendizagem instantânea quando nível muda; respeita clock DEC-022 e priorização DEC-056. Não presumir memória ilimitada; DEC-065 definirá consolidação.


### Memória de NPC em níveis de atividade — DEC-065/C (Discovery v6.1)

Regiões DISTANT/DORMANT podem acumular somente eventos resumidos autorizados por regras/eventos confirmados, sem invenção de experiências detalhadas. Consolidação de memória episódica é agendada sob demanda/conforme orçamento DEC-056; ao despertar, validar fontes/clock/ACL, não reconstruir falsa presença do NPC. Âncoras críticas persistem conforme política; seu conteúdo não é broadcast. Não alterar pastas do cânone por ano DEC-060.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

A DEC-067 distingue NPC agregado/efêmero de individual persistente. Um NPC promovido continua submetido a ACTIVE/NEAR/DISTANT/DORMANT e orçamento DEC-056; promoção NÃO significa simulação/LLM por tick. Reconciliar agregados e individuais sem dupla contagem. Políticas de hibernação de promovidos são a DEC-068 aberta.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

Níveis de NPC individualizado usam ACTIVE/NEAR/DISTANT/DORMANT sem alterar a arquitetura regional DEC-021; `DORMANT` hiberna processamento, conserva identidade/memória, e `DISTANT` processa apenas lotes causais permitidos. Retomada exige identidade DEC-066, build, host e checkpoint, com nenhum LLM por tick. DEC-060–067 preservadas; ver ADR-0063/doc. 68.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: ACTIVE permite observação física do host; NEAR/DISTANT escalonam segmentos temporais; DORMANT conserva plano sem tick. Nível de atividade não comprova localização física nem permite teleporte.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

Os incidentes DEC-070 seguem ACTIVE/NEAR/DISTANT/DORMANT: processamento por lotes e políticas de risco; nunca chamar LLM a cada NPC/tick nem aplicar resultado de combate ao resolver uma viagem longe dos jogadores.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Ao passar de DISTANT/NEAR a ACTIVE por presença dos jogadores, incidentes de rota DEC-070 podem ser candidatos a DEC-071. A transição do resolvedor offscreen para o local requer reserva durável versionada e fencing. Se incompatível ou sem recursos, deixar pendente sem duplo catch-up/LLM tick.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Um encontro em região ACTIVE pode consultar catálogo DEC-072, porém DISTANT/DORMANT não instanciam scripts/atores por inferência. Transição local depende de DEC-071 e capacidades reais.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Um encontro termina causalmente uma única vez; limpeza pendente não pode ser repetida ou reprocessada em catch-up distante.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

DEC-074 difunde informações em ACTIVE/NEAR/DISTANT/DORMANT por quotas e canais, sem rodar LLM a cada NPC/tick. Dormência não equivale a notícia recebida. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Atribuição social pode ser agendada conforme nível de atividade; ausência de simulação ativa não autoriza reputação onisciente ou culpa coletiva.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Autoridades em DISTANT/DORMANT não precisam de LLM por tick; DEC-078 event-driven usa regras e filas. Um guarda ausente não se materializa ou prende alguém sem estado host.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Solicitações entre regiões são tarefas event-driven com orçamento DEC-056. Nenhum agente/LLM por tick ou perseguidor físico na região DISTANT sem itinerário e host confirmado.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Notificações DEC-080 e crenças locais via filas por nível de atividade; NPC DORMANT pode receber informação apenas por canal válido sem execução per-tick ou atualização onisciente.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Danos e procedimentos reparatórios de NPCs fora de cena podem ficar pendentes em filas por atividade, sem inferir pagamento nem mudar tempo/campanha automaticamente.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Fontes em regiões distantes ou hibernadas não recebem automaticamente notícia de divulgação nem proteção física; avaliar filas e canal legítimo.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Proteção pode ter andamento narrativo distante por eventos e catch-up limitado, jamais simular combates/hostilidades HIGH ou presença física inexistente.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

NPC distante/dormente não consulta plano de proteção; atualização de crença e descoberta de trecho dependem de comunicação legítima e orçamento do scheduler.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

NPC com compromissos secretos não recebe simulação contínua e caras chamadas de IA por tick; níveis ACTIVE/NEAR/DISTANT/DORMANT continuam limitados a eventos relevantes e autorização.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

NPC em atividade distante pode transmitir informação somente por canal/tempo comprovado, não por leitura onisciente de eventos globais. Evidência conserva origem e validade DR.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-091/C — Discovery v8.7

Setores DORMANT/DISTANT não ganham NPCs físicos nem eventos locais por plano narrativo; catch-up não cria execução irreversível sem gate.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Matriz proposta DEC-096 filtra por atividade ACTIVE/NEAR/DISTANT/DORMANT e limita catchup; não simula todos os locais a cada tick nem materializa efeitos mecânicos fora da cena sem capability.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-097/C — Discovery v9.3

DEC-097/C usa cache por métrica/região, reavaliação em transição e catch-up bounded para DORMANT, sem simular a cada frame.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Zonas ACTIVE/NEAR/DISTANT/DORMANT produzem snapshots e projeções com fidelidade/cotas diferentes; `DORMANT` não exige NPCs físicos carregados.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Conteúdo procedural respeita marcos de quests liberados e não utiliza branches futuros de scripts para decidir cenas.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para regiões em níveis de atividade sem broadcast instantâneo, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para atividade de NPCs e disseminação offscreen sem onisciência, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
