# Arquitetura híbrida — regras determinísticas e IA sob demanda

**Discovery v0.9** · **Status: desenho preliminar (não é SPEC técnica aprovada)**  
**Fundamento aprovado:** DEC-014 / ADR-0008. **Outras dependências:** ADR-0007, DEC-005, DEC-006, DEC-008, DEC-012, DEC-015 e DEC-021.

## Objetivo

Minimizar inferência desnecessária em um jogo cooperativo 2D com muitos NPCs. A IA enriquece narrativa e improvisação; a engine e o código convencional continuam executando a simulação básica. A topologia lógica de especialistas não pressupõe modelo isolado por NPC nem serviços separados desde o MVP.

## Camadas previstas

```text
Game events (BG2:EE host) [não confiáveis até normalizados/validados]
        |
        v
Event ingress + contexto/autorização + isolamento por campanha
        |
        v
Rule Router / deterministic systems
   |          |               |
   |          +-> Behavior FSM / decision tables / event handlers
   |          +-> Cooldowns / templates / encounter rules
   |
   +--[apenas problema aberto]--> World Director (orquestrador)
                                |-- NPC Dialogue / Social (sob demanda)
                                |-- Quest / Backstory (planejamento)
                                |-- Encounter Narrative (não cálculo de combate)
                                |-- World / Factions (eventos de alto nível)
                                      |
                                Local LLM (preferencial, se apto)
                                      |
                                propostas com esquema e proveniência
        |                             |
        +---------------> Controller / Security Gate
                              |
                              v
                     EEex Bridge (allowlist)
                              |
                              v
                   BG2:EE host (efeito mecânico)
                              |
                              v
                  confirmação / reconciliação
                              |
                              v
             Persistence + Character/NPC knowledge
```

## Matriz de roteamento (proposta para refinamento)

| Situação | Primeiro caminho | IA necessária? | Observações |
|---|---|---|---|
| Jogador ataca NPC | regras de reação, ameaça, moral, combate | **Não**, para a reação tática normal | Alinhamento é só um dos fatores; host confirma dano e combate |
| NPC patrulha ou retorna à loja | FSM, agendador e regras de navegação | **Não** | Sem modelo permanentemente ativo |
| Guarda vê crime | tabela de facção, testemunhas, leis locais | **Não** para detecção e alerta | Diálogo complexo posterior pode chamar LLM |
| Mercador calcula preços ou troca inventário | tabela/economia validada pelo host | **Não** | LLM não transfere itens nem define saldo por conta própria |
| Grupo conversa livremente com taverneiro | recuperar perfil + fatos que o NPC conhece | **LLM local sob demanda** | Pode usar templates ou cache quando suficiente |
| Missão baseada em passado do personagem | filtro de ganchos + regras de agenda | **LLM local opcional** para compor conteúdo novo | Não confundir proposta com fato, respeitar segredos |
| Escolher encontro em estrada | tabelas por área, grupo e sistema de regras | **Não** para seleção mecânica | IA opcional para dar contexto narrativo |
| Criar masmorra nova | geração procedural + validação de mapa | **LLM local opcional** para tema e narrativa | Construção e solvabilidade testadas por código |
| Mundo inativo, sem jogadores próximos | política de simulação futura DEC-021 | **Não por padrão** | Proibição provisória de LLM em loop por NPC |

## Política de roteamento

1. `RULE`: algoritmo/tabela cobre o caso, inclusive aleatoriedade pseudodeterminística registrada quando desejada.
2. `TEMPLATE/CACHE`: dados reutilizáveis, somente se válidos para personagem, região, tempo e permissões.
3. `LOCAL_LLM`: interpretação ou criação realmente aberta, com contexto mínimo necessário, limites, esquemas, validação e timeout.
4. `REMOTE_LLM`: **não habilitado por implicação**; possível somente após DEC-006 (política de uso/privacidade/custos) e consentimento aplicável.
5. `FALLBACK`: resposta pré-aprovada/regra conservadora ou ausência de evento quando nenhum dos anteriores estiver disponível. Não bloquear o loop principal do jogo.

## Interfaces candidatas (a detalhar nas SPECS)

- **GameEvent:** `event_id`, `campaign_id`, `session_id`, `kind`, `entity_ids`, `observed_at`, `payload`, `host_evidence`.
- **DecisionContext:** `event_id`, `world_revision`, `ruleset_version`, `knowledge_scope`, `actor_attributes`, `region_state`, `seed`.
- **ActionProposal:** `proposal_id`, `event_id`, `source=RULE|LOCAL_LLM|REMOTE_LLM|FALLBACK`, `action_type`, `arguments`, `preconditions`, `expires_at`, `provenance`.
- **ActionOutcome:** `proposal_id`, `execution_id`, `status=PENDING|CONFIRMED|REJECTED|UNCERTAIN`, `host_evidence`, `world_revision`.
- **InferenceRecord:** `model`, `model_version`, `latency_ms`, `token_usage`, `estimated_cost`, `validation_result` — logs não armazenam segredos desnecessários.

Esses campos são modelos conceituais, não interfaces implementadas. Assinar/validar a origem de eventos e definir a capacidade da bridge são testes pendentes.

## Exemplo de árvore de decisão em pseudocódigo (sem engine)

```text
when NPC_ATTACKED(event):
  if not is_confirmed_host_event(event): return IGNORE
  npc = get_npc_state(event.target)
  if not npc.alive: return IGNORE
  if npc.is_guard and attacker_committed_crime: return RULE(DEFEND_AND_ALERT)
  if npc.morale_low and npc.has_escape_route: return RULE(FLEE)
  if npc.outmatched and npc.can_surrender: return RULE(SURRENDER)
  if npc.has_defensive_ability: return RULE(DEFEND)
  return RULE(RETREAT_OR_CALL_HELP)
```

As regras efetivas precisarão de prioridades, exceções, perfis e testes. A reação escolhida não modifica o jogo até ser validada e confirmada pelo domínio autoritativo (ADR-0007). Avaliar alinhamento sem contexto não substitui personalidade ou objetivos.

## Proteções e limites

- Nunca entregar Lua, prompts ou texto de jogador ao interpretador externo como comandos executáveis.
- Não enviar histórico secreto integral ao LLM se os trechos necessários podem ser selecionados; separar conhecimento do narrador e do NPC.
- Evitar inferência em cada tick/frame, ataque, deslocamento, inventário ou trade; preferir eventos e cooldowns.
- Modelos locais têm limites de CPU, RAM, GPU, contexto e qualidade; poderão rodar em serviço separado do cliente de jogo.
- Em perda de conexão/timeout, manter jogo ativo e usar fallback; não inventar confirmação de efeitos.
- Orçamentos, TTL de cache, modelos e tempos máximos ficam **em aberto** para DEC-006/SPECS.
- Logs devem registrar a **origem da decisão** e sua validação, mas não vazar segredo de jogador.

## Gatilhos de agentes especializados (hipóteses)

- `NPC Dialogue`: diálogo livre não coberto por template, com memória e conhecimento filtrados.
- `Quest/Backstory`: criação/revisão de ganchos em horários de baixa atividade ou sob demanda, com proposta para validação.
- `Encounter Narrative`: contextualizar encontro selecionado por regras; tática/combat resolvidos por código.
- `World/Factions`: planejamento episódico de acontecimentos com prioridades, cooldowns e persistência; não simulação LLM em loop.

**Não decidido:** se eventos distantes avançam em tempo real, em lotes ou apenas quando revisitados (DEC-021). **Não testado:** sincronização multiplayer da bridge, desempenho local e eficácia de modelos.

## DEC-055 — Modo degradado da orquestração (Discovery v5.1)

Sem LLM local, suspender novas gerações dependentes dele e utilizar diálogos/roteiros nativos somente se a independência for verificada; não produzir fatos fictícios como fallback. Workers determinísticos não assumem autorização para salvar ou modificar flags. O World Health Monitor observa filas, timeouts e falhas com limites e circuit breaker a especificar. DEC-006 e DEC-056 ainda decidirão runtime e budgets.

## Integração DEC-056 — filas e orçamento adaptativo (Discovery v5.2)

O orquestrador DEC-014 passa a depender conceitualmente de um **Resource & Performance Director** que admissiona chamadas LLM sob demanda e batches determinísticos com prioridades P0–P4; não deve executar inferências por NPC/tick. Diálogos ativos têm prioridade sobre pregen, mas aguardam gate de segurança, ACL e autorização. Saturação limita concorrência e pode oferecer apenas fallback já validado; não muda a política de API remota (DEC-006 aberta) nem a autoridade de host. LLM com timeout não gera efeito mecânico ou fato narrativo. O scheduler considera estado do World Health Monitor DEC-055, transição de build/branch e invalidação de cache. Ver ADR-0051/documento 56.

## DEC-057 — Implantação local-first com extensão LAN opcional (v5.3)

A topologia do diagrama de especialistas é **lógica**, não requer um processo por agente. O baseline é orquestrador/serviços desacoplados no PC Windows com BG2:EE host; inferência local e simulação podem ser realizadas em **nó LAN opcional** após cadastramento/autorização e controle de escopo, sem tornar o nó autoridade mecânica. O RPD DEC-056 decide admissão e orçamento por worker; resultados são propostas schema-validated e revision-bound. ACL antes de contexto e nenhum fallback cloud/telemetria externa sem DEC-006. A segurança concreta da conexão ficará para DEC-058. Ver ADR-0052/doc. 57.

## DEC-059 — AI Model Router entre orquestrador e workers

O `AI Model Router` não é agente separado com autoridade, mas componente lógico que envia propostas para serviços locais ou workers LAN. Pipeline: regras primeiro → classificação da tarefa → ACL/minimização antes do prompt → destinos com permissão e capacidade aferidas → ranking por adequação/qualidade/recursos/latência dentro do orçamento RPD → resposta não autoritativa → validação de política e fatos → possíveis ações tipadas via gateway/host. Ausência de nó é suportada em single-host; fallback não viola escopos e não inclui cloud sem a DEC-006. Ver ADR-0054/doc. 59, nenhum componente implementado.


## DEC-060 — saída gerada não é fato

O orquestrador exige validação determinística e contextual proporcional ao risco; LLM revisor é auxiliar. Conteúdo histórico depende de proveniência e estado do ramo, e efeitos mecânicos permanecem no gateway/host. Falha do validador não libera publicação crítica.

## DEC-060 — partições temporais como fonte de contexto (v5.6.1)

Agentes narrativos recebem somente o contexto recuperado da partição física do ano DR relevante (`knowledge/periods/{year}-DR/`), referências históricas selecionadas, overlay da campanha e conhecimento ACL-filtrado do falante. A seleção/validação de tempo antecede qualquer inferência LLM, inclusive no modo distribuído. Regras seguem prioritárias para tempo e propagação; informação futura não se torna verdade presente por contaminação de corpus. O esquema e os mecanismos de busca concretos permanecem abertos em SPECS.

## DEC-061/C — proveniência e conflito como gate anterior à geração

O orquestrador utiliza contexto procedente da partição **fisicamente separada por ano DR** (DEC-060), selecionando alegações, fontes e resoluções curatoriais válidas no escopo atual, mais overlay da campanha e ACL do falante. Se houver contradição não resolvida, não ordenar ao LLM que invente consenso: expor apenas a incerteza permitida, usar fallback já validado ou deferir/escalar. Um LLM auxiliar pode sugerir análise, nunca publicar resolução canônica ou modificar fatos confirmados. Ver ADR-0056 e doc. 61.

## DEC-062/C — IA de importação propõe; não publica

O especialista de extração poderá sugerir entidades, datas e alegações a partir de fontes legitimamente recebidas, via roteamento DEC-059/limites DEC-056. A revisão de fontes pertence ao pipeline curatorial DEC-062 e **não** ao runtime mecânico ou a um comando livre de LLM. Somente validadores de direitos, ano, proveniência e política de risco permitem promover candidatos a partições físicas DEC-060, preservando conflitos DEC-061. Importação não altera diretamente o host/saves; resultados de workers LAN não são autoridades editoriais. Ver ADR-0057/doc. 62.

## Integração DEC-064/C — aprendizado e crenças sem onisciência (v6.0)

DEC-064/C: inferência local pode propor fala ou interpretação de prova, mas a aquisição de episódio e a transição de crença exigem evidência/ACL/clock e processamento versionado por regras. A saída LLM é validada DEC-060; rumor não é narrador confiável. Model Router DEC-059 deve enviar projeção mínima e vinculada a ano/pack/branch; nunca LLM contínuo por NPC/tick.


### Memória contextual de NPCs — DEC-065/C (Discovery v6.1)

O orquestrador recupera poucas lembranças relevantes por NPC/scene/branch/ACL, combinando memória imediata, episódios, sínteses validadas e âncoras críticas. Consolidação em lote e nunca LLM por NPC/tick; fonte ausente/stale provoca DEFER, não memória fabricada. O Model Router DEC-059 recebe apenas contexto permitido e o verificador DEC-060 avalia a saída. Knowledge Pack e cânone permanecem segregados por ano DR DEC-060–063; crenças DEC-064 não são substituídas por resumos.

### Integração DEC-066/C — roteamento de IA condicionado à identidade (v6.2)

Antes de gerar fala pessoal, resolver identidade NPC por evidência positiva da sessão/build/branch. Apenas `VERIFIED` pode solicitar memória pessoal, e ACL/tempo ainda são necessários. LLM pode propor correspondência, não certificar observações do motor; `AMBIGUOUS` limita a fala ao contexto público autorizado. Cânone anual DEC-060 permanece isolado.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

A seleção/promoção de NPCs DEC-067 começa com eventos verificados e regras. LLM pode sugerir relevância, nunca certificar identidade DEC-066, atribuir memórias nem criar automaticamente personagem no motor. Agregado/efêmero por padrão; individualização sob demanda.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

A hibernação DEC-068/C usa regras por evento/lote e LLM somente sob demanda. `DORMANT` não executa LLM por NPC/tick; worker/model router recebe apenas contexto autorizado e resultados de revisão compatível. Produção narrativa não equivale a confirmação mecânica; ver doc. 68.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: planejador de rota usa regras/grafo curado e políticas do mundo; LLM opcional explica ou propõe um percurso, jamais inventa links geográficos, valida identidade ou confirma chegada mecânica.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

O gerador de incidentes DEC-070 usa regras e fontes verificáveis em primeiro lugar, LLM somente para formulação contextual autorizada; modelo não arbitra classificação de risco, verdade histórica ou efeitos de engine.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

O diretor de encontros/LLM pode **propor** eventos DEC-071. Elegibilidade, conteúdo por build, reserva de incidente, autorização e receipts seguem regras e gateway; linguagem gerada não cria engine sprites/scripts, HP, NPCs ou loot. A promoção local depende de capacidades testadas, e não de inferência LLM.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Model Router e diretor podem escolher parâmetros de templates DEC-072 somente entre componentes allowlisted e dentro de contexto temporal/ACL; LLM não gera código de engine executável ou confere capability.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

LLM/diretor podem sugerir closure, mas somente regras/gateway/host e receipts podem comprovar efeitos mecânicos e autorizar limpeza.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Após o encontro, DEC-074 permite propostas de notícias e efeitos por regras; LLM pode elaborar falas e interpretações filtradas, mas não confirmar evento, determinar magnitudes mecânicas ou atualizar mundo inteiro. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

IA pode ajudar a redigir justificativas e diálogos de reconhecimento, não inventar telemetria individual, classificar definitivamente responsabilidade ou alterar fatos confirmados sem evidências.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Filtros determinísticos e ACL devem resolver quais personas e vínculos podem entrar no contexto da inferência antes do modelo. LLM pode redigir suspeitas ou falas, nunca decidir unilateralmente verdadeira identidade/revelação.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação por evidências (Discovery v7.3; não implementada)

A investigação de personas DEC-076 usará ledger privado por campanha/ramo, com pistas e hipóteses revisáveis, origem/independência de fontes, contraprovas e estados inconclusivos. Suspeita ou fala LLM não confirma identidade e não permite divulgação; vínculo factual restrito exige evidências/DEC-066, e revelação exige ACL/consentimento/risk gate por audiência (DEC-019/028/041/045/046). Rumores e repercussões DEC-029/074/075 são separados de fato e punição. **Preservar `knowledge/periods/<ANO>-DR/` fisicamente por ano, sem evidências privadas no cânone.** ADR-0072/documento 77; 58 testes não executados, sem POC BG2:EE/EEex/multiplayer.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

DEC-078 mantém código primeiro para estados processuais, elegibilidade da jurisdição, provas, risco, ACL e comandos; IA local pode formular diálogos de guardas ou acusados, mas não decidir culpabilidade nem sanção.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Jurisdições e pedidos DEC-079 usam regras curadas determinísticas para competência e risco; LLM local apenas redige diálogos/negociação autorizados, nunca julga autoridade ou executa captura.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Revisões/precedência/risco de mandados são regras determinísticas DEC-080; LLM local só redige diálogos filtrados, não arbitra validade, competência ou revogação.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Causalidade de dano, competência, idempotência, gates e consentimento seguem código/regras determinísticas; LLM local somente para petições/diálogos com ACL, não para impor reparação ou inventar danos.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Cadeia de comando, validade de lei e idempotência são determinísticos; LLM local apoia texto contextual filtrado por ACL, não decide responsabilidade ou medida sozinho.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

ACL e minimização aplicadas por regras determinísticas **antes** do LLM; modelo pode redigir extrato permitido, não decidir acesso ou inventar testemunho de PC.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Gates de risco, ACL, horário, recursos e reservas são determinísticos. LLM local pode propor diálogos e planos, não provocar perseguição ou deslocamento não confirmado.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Gates determinísticos restringem contexto antes de LLM local. O modelo pode elaborar hipóteses e texto, mas nunca fabricar quem descobriu rota, espionagem ou autorização mecânica.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Verificação determinística resolve consentimento, autoria, recursos, difusão e ACL antes do modelo; LLM só sugere redação ou hipótese, não decide engano bem-sucedido nem valida prova.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Avaliação de lealdades usa regras determinísticas e evidências primeiro; a LLM local opcional pode redigir falas de dúvidas, negociação ou recusa, sem escolher desfechos arbitrários.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

LLM local DEC-014/059 sugere fala/termo, mas regras determinísticas avaliam elegibilidade, agência, ACL, custos, aceitabilidade e transição contratual.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

LLM pode sugerir hipóteses e resumir alegações acessíveis, mas validadores determinísticos decidem lineage, fonte independente, ACL, estados e thresholds configurados; não rodar LLM em todo tick.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Compor, redigir ACL, selecionar audiência, validar citações, deduplicar e propagar são tarefas determinísticas; sumarização LLM opcional usa somente `DisclosureView` sanitizada, com output revalidado.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Diretor central pode orquestrar avaliações tipadas por código, chamar LLM local sob demanda para apresentação de opções, nunca para autorização ou execução autônoma.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Código determina triggers, diffs, autorização e estado; a LLM local pode propor revisões textuais sob demanda e ACL, sem decidir mudança de estratégia ou executar.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

O árbitro de recursos/tempo/compatibilidade é determinístico; LLM apenas sugere negociação e texto pós-ACL, nunca concede lease, transfere recurso, muda prioridade autoritativa ou controla personagem.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Grafo de espera, starvation, revogabilidade de lease e desempates são lógica determinística versionada; LLM pode sugerir negociação textual após ACL, jamais libertar recursos ou sacrificar operação.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

DEC-095 usa política determinística de Saga, LLM somente explicação/proposta. A matriz condicional proposta DEC-096 aplica ano DR, precisão, geografia, tags, estados e dependências por filtro indexado, não LLM como motor de história.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

DEC-096/C usa relógio DR DEC-022 e intervalos explícitos por fase; `YEAR_ONLY` não inventa mês. Estado histórico legado é baseline curado, nunca replay de combate/história.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

DEC-097/C é matemática determinística e de baixo custo; LLM só narra uma projeção filtrada por ACL e época, nunca arbitra valores.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

LLM local só refina texto autorizado; não decide identidades engine, inexistência, spawn nem estado de quest ao carregar região.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

LLM nunca determina quem é proprietário de instâncias nem substitui contratos de scripts; classifica ou descreve somente dados permitidos, sem executar writes.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Divergência de canon não pode ser deduzida de flag oculto, nem altera conhecimento histórico curado DEC-060–063.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração DEC-102/C (Discovery v9.8)

Reconciliador de quest DEC-102 determinístico; LLM não escolhe qual estado prevalece. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** marcos confirmados de quests originais são **origens candidatas** de regras históricas/regionais, não fatos canônicos escritos em `knowledge/periods/<ANO>-DR/`. A admissão exige prova reconciliada DEC-100/101/102, clock DR e branch adequados; a matriz DEC-096 filtra local, fase e precondições e DEC-097 compõe impactos. Escopo global não dá conhecimento universal. Evento proposto, evento host-confirmed e rumor entregue são distintos; nenhum efeito mecânico sem Action Gateway/receipt. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **cânone cronológico**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para LLM local somente para expressão de correção filtrada, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para código determinístico primeiro, LLM apenas para texto autorizado, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-109/C — Obrigações condicionais multipartes

Código primeiro para avaliação de DAG e LLM apenas para explicação narrativa autorizada. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

LLM local narra ou sugere termos; planejador determinístico avalia owner, receipts e condições, sem executar transferência de recursos.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
