# 71 — Transição controlada de incidentes fora de cena para encontros jogáveis

**Estado:** Discovery v6.7, DEC-071/C **aprovada como arquitetura**, **não implementada**. **46 testes candidatos, nenhum executado.** Decisão normativa: `docs/decisions/ADR-0066-transicao-controlada-de-incidentes-para-encontros-jogaveis.md`.

## 1. Escopo, dependências e não objetivos

- **Objetivo:** permitir que uma proposta de incidente DEC-070 ancorada em itinerário DEC-069 se torne oportunidade de encontro local **apenas** quando a build, o host, os atores, os scripts e as políticas autorizarem, preservando uma única resolução causal.
- **Não objetivo:** prometer spawn, script injection, pathfinding, controle de câmera, área dinâmica, UI ou multiplayer já suportados. Todas essas hipóteses dependem de SPECS, inventário de conteúdo DEC-051 e POCs BG2:EE/EEex DEC-003/013/015.
- **Não objetivo:** tornar a IA árbitro mecânico. LLM propõe linguagem e dramaturgia; DEC-011/012/027 confirmam consequências através das regras e do host.
- **Pré-condições de narrativa:** DEC-008/009/022 para tempo e ramo; DEC-028/060/061/062/063 para conhecimento e fontes; DEC-064–068 para NPC, identidade, memória e atividade; DEC-005-E/033/050 para encontros, conflitos e scripts nativos; DEC-053/054/055/056 para segurança operacional.

## 2. Fronteiras de verdade

1. **Fato canônico:** corpus fisicamente segregado por `knowledge/periods/<ano>-DR/` com proveniência e curadoria. Nunca guardar incidente derivado ali.
2. **Estado narrativo da campanha:** `incident_id`, propostas, validações, decisões, eventos e efeitos narrativos permitidos no overlay do ramo.
3. **Estado mecânico:** exclusivamente observável pelo host BG2:EE e confirmado por receipt/bridge válido; um texto não equivale a NPC instanciado, HP alterado ou script concluído.
4. **Observações dos clientes:** podem contribuir como pedidos e sinais não autoritativos; nenhum voto ou RPC de cliente substitui observação do host/consentimento.
5. **Fonte regional:** uma emboscada sugerida pelo diretor DEC-005-E é possibilidade, não prova de que uma batalha já ocorreu; o gerador de viagem DEC-070 não cria mecânica por si.

## 3. Contratos candidatos, não APIs existentes

```text
EncounterHandoffCandidate {
  handoff_id, incident_id, idempotency_key,
  campaign_id, branch_id, itinerary_id, segment_id,
  world_time_window, clock_mode, checkpoint_epoch,
  incident_revision, resolution_epoch, fence_token,
  knowledge_pack_manifest_hash, build_manifest_hash,
  npc_identity_ids[], identity_evidence_refs[],
  proposed_area_ref?, party_presence_host_receipt?,
  supported_capabilities[], content_template_ref?,
  native_conflict_refs[], provenance_refs[], acl_scope,
  risk_class, aggregate_impact, required_consents[],
  host_operation_id?, host_receipt_ref?, state, audit_refs[]
}
```

- Todos os identificadores são escopados à campanha/ramo/sessão; IDs de engine e `CRE` são pistas, não identidades permanentes.
- `supported_capabilities` contém capacidades **medidas/confirmadas** na build; nunca uma lista de recursos que supomos existir.
- `party_presence_host_receipt` deve representar fato host observado, área/epoch/time e coerência com o itinerário; não uma inferência do modelo.
- `fence_token` e `incident_revision` impedem workers antigos de resolver depois que o controle migrou de nível de atividade.
- `host_operation_id` protege retry apenas após consulta/reconciliação do host; não tratar ausência de resposta como comando não aplicado.

## 4. Máquina de estados proposta

```text
OFFSCREEN_PROPOSED
    | validar elegibilidade
    v
ELIGIBILITY_CHECK
    +-- invalid/unsupported --------------------> NARRATIVE_ONLY | PENDING | REJECTED
    +-- viable ---------------------------------> RESERVING
                                                    |
                                             reserva CAS durável
                                                    v
                                              LOCAL_RESERVED
                                                    |
                                         consentimento + gateway
                                                    v
                                             HANDOFF_READY
                                                    |
                                         chamada host se suportada
                                                    v
                                            ENGINE_PENDING
                                               /         \
                                  host receipt OK       timeout/ambíguo
                                      |                       |
                                      v                       v
                                ENGINE_CONFIRMED           UNCERTAIN
                                      |                       |
                               commit idempotente       RECONCILIATION
                                      v
                                INCIDENT_RESOLVED
```

- **O primeiro estado de `LOCAL_RESERVED` desloca o direito de resolver**, não comprova que encontro ou combate começaram.
- `NARRATIVE_ONLY` pode apresentar informação compatível e previamente validada sem simular efeitos físicos.
- `REJECTED`, `PENDING`, `UNCERTAIN`, `STALE` não equivale a `RESOLVED`; sem reconciliação, não há efeitos novos.
- Cancelamento/reversão de reserva somente com prova de que nenhuma operação mecânica foi enviada ou depois de reconciliar sua ausência.
- `INCIDENT_RESOLVED` fecha a mesma `incident_id` em ambas as trilhas; nunca permitir `OFFSCREEN_RESOLVED` e `LOCAL_RESOLVED` para o mesmo causal event.

## 5. Fluxo de elegibilidade prévia

| Verificação | Evidência exigida | Falha segura |
|---|---|---|
| Party próxima | Observação verificável do host, área/instância, tempo | Não promover; manter proposta |
| Região/rota | Segmento e janela de DEC-069 válidos, sem teleporte | Não promover |
| Conteúdo instalado | Inventário por build DEC-051, área e capacidades verificadas | Narrativa permitida ou pendente |
| Scripts e quests | Ausência de conflito com conteúdo nativo DEC-050 | Bloquear integração local |
| Atores | Identidades DEC-066 verificadas; instâncias reconciliadas | Não vincular memória/spawn |
| Cânone e cronologia | Manifest DEC-063 e fonte do ano conforme DEC-060/061 | Não usar contexto inadequado |
| Segredos | DEC-028 ACL aplicável antes de roteamento à IA | Redação/bloqueio de contexto |
| Risco e agência | DEC-027/034/041/042/046/070 e consentimento aplicáveis | Não enviar ação |
| Orçamento e resiliência | DEC-056/053/055, sem erro crítico | Ficar pendente |

**Sem POC positiva para criação/ativação de encontro, a capacidade mecânica deve constar como `UNSUPPORTED`.** Inventário não é prova de API de spawn. A possibilidade de reutilizar um encontro nativo depende da DEC-072 e testes, não de mera presença do arquivo.

## 6. Trava de resolução, idempotência e handoff

1. O coordenador compara `incident_revision` e `resolution_epoch` ao ledger durável sob campanha/ramo.
2. Apenas um resolvedor (offscreen ou local) recebe um token de fencing para aquela revisão; retirar o direito offscreen **antes** de enviar qualquer ação ao host.
3. Reserva gera checkpoint/ponto de consistência quando a política exige; não confiar em locks exclusivamente em RAM nem em prazo de lease isolado.
4. A operação local carrega `host_operation_id`, idempotency key e precondições do host; ações de efeito só em allowlist tipada DEC-012.
5. Receipt válido do host altera estado para `ENGINE_CONFIRMED`; efeitos narrativos e memória NPC são publicados depois, como projeções derivadas idempotentes.
6. Se falha de rede/save/load/crash ocorrer, congelar, observar host e reconciliar. Não reenviar operação mecanicamente ambígua.
7. Em `INCIDENT_RESOLVED`, trabalhadores offscreen e locais arquivam suas propostas não vencedoras; evento não reaparece após restart, catch-up ou restore.
8. A estrutura de ledger/DB e garantias reais (compare-and-swap, fencing e atomicidade em múltiplos serviços) dependem de SPECS/POC; estes contratos são requisitos, não capacidades declaradas.

## 7. Eventos de risco e alternativas honestas

- **LOW:** anúncio, conversa ou oportunidade narrativa inofensiva aprovada; mesmo que próximo à party, não representa NPC materializado nem exige alteração de engine.
- **MEDIUM:** incidentes com custo, atraso ou efeito social exigem evidência, validação, política aplicável e decisão específica. Não ativar script de maneira silenciosa.
- **HIGH:** combate, dano, morte, saque, captura, alterações de quest/romance ou marcos históricos exigem gates especiais, compatibilidade efetiva e receipt mecânico; caso contrário permanecem propostas.
- **Sem recurso local:** registrar `UNSUPPORTED`, sugerir narrativa compatível ou deixar pendente. Não gerar inimigo, HP, loot ou diálogo mecanicamente inexistente por texto de IA.
- **Jogadores interrompem:** evento pode permanecer sem efeito, desde que cancelamento seja reconciliado; nunca voltar à simulação offscreen após host possivelmente ter executado uma ação desconhecida.

## 8. Concorrência multiplayer, recuperação e privacidade

- Host coordena as observações e os efeitos; dois clientes em áreas distintas não garantem duas cópias da mesma ocorrência.
- DEC-041 e política PvP/ausentes protegem decisões dos controladores. Nenhum encontro compulsório invoca o consentimento de jogador ausente.
- Logs do handoff registram decisão e cause, mas não gravam segredos no texto público ou telemetria externa. LAN autorizada DEC-057/058/059 recebe contexto mínimo e não pode declarar `ENGINE_CONFIRMED`.
- Restores e forks têm `branch_id`, build/hash/checkpoint distintos e não transportam ledger/receipts incompatíveis entre mundos alternativos.
- Watchdog DEC-055 encontra incidentes em `LOCAL_RESERVED`/`UNCERTAIN`; apenas alerta e ações seguras permitidas, não executa spawn automaticamente.

## 9. Plano incremental de comprovação (a executar, não executado)

1. **POC G71-0:** demonstrar ledger isolado em simulador, duas filas concorrentes e idempotência em crash/restart, sem motor.
2. **POC G71-1:** enumerar builds/áreas/atores e mapear capacidades *somente leitura* do bridge; registrar incompatibilidades.
3. **POC G71-2:** validar host + dois clientes em área de teste, detectando presença e estado sem modificar saves.
4. **POC G71-3:** demonstrar uma interação local controlada em build isolada com adapter prevalidado; consentimento explícito e backup/checkpoint testados; sem tocar campanhas reais.
5. **POC G71-4:** reproduzir crash, reconexão, restore, mods divergentes, dois clientes e comandos incertos, demonstrando ausência de efeito duplo.
6. **Gate de produto:** habilitar somente o conjunto de capabilities que passou nos testes, com fallback desativando materialização em caso de qualquer incerteza.

## 10. Matriz de 46 testes candidatos — NÃO EXECUTADOS

| ID | Caso de teste / expectativa |
|---|---|
| T071-01 | Uma proposta de incidente sem `incident_id` não é elegível e não cria encontro. |
| T071-02 | Aproximação aparente relatada por cliente sem host não habilita promoção. |
| T071-03 | Party confirmada em área compatível habilita apenas avaliação, não spawn. |
| T071-04 | Cidade do cânone sem mapa na build falha de modo seguro. |
| T071-05 | Área presente mas inacessível/carregamento inválido cancela handoff. |
| T071-06 | Quest nativa ativa conflitante impede encontro. |
| T071-07 | Romance/script protegido impede inserção de evento inconsistente. |
| T071-08 | Dois NPCs homônimos são tratados como identidades distintas. |
| T071-09 | Identidade do NPC `AMBIGUOUS` impede materialização e memória. |
| T071-10 | NPC já presente na área não recebe duplicata por proposta. |
| T071-11 | Incidente resolvido offscreen antes da reserva não é reapresentado. |
| T071-12 | Reserva local obtida impede resolução paralela offscreen. |
| T071-13 | Duas reservas concorrentes: apenas uma transição de revisão vence. |
| T071-14 | Worker com fencing antigo perde permissão mesmo após reconexão. |
| T071-15 | Lease expirado não leva a retry de ação mecânica desconhecida. |
| T071-16 | Timeout da bridge após operação passa para `UNCERTAIN`. |
| T071-17 | `UNCERTAIN` impede reenvio de comando de spawn ou combate. |
| T071-18 | Reconciliação posterior com receipt válido confirma uma única vez. |
| T071-19 | Receipt de outra campanha/branch é rejeitado. |
| T071-20 | Receipt de checkpoint obsoleto é rejeitado. |
| T071-21 | Receipt de operação distinta do evento não autoriza commit. |
| T071-22 | Narrativa LOW permitida não modifica HP, inventário, XP ou quests. |
| T071-23 | Uma proposta MEDIUM sem autorização permanece pendente. |
| T071-24 | Uma consequência HIGH sem autorização especial falha fechada. |
| T071-25 | Múltiplas ações LOW com efeito HIGH são reclassificadas e bloqueadas. |
| T071-26 | Oferta narrativa é apresentada apenas com ACL e sem fabricar presença física. |
| T071-27 | Conteúdo privado de outro PC não entra no prompt do encontro. |
| T071-28 | Host offline impede spawn e não autoriza efeitos mecânicos. |
| T071-29 | Cliente tenta concluir evento sozinho e é rejeitado. |
| T071-30 | Reconexões de dois clientes não aplicam o mesmo impacto duas vezes. |
| T071-31 | Jogador ausente não recebe ação/consentimento fictício. |
| T071-32 | Evento cancelado antes de qualquer chamada engine pode voltar a offscreen após reconciliação. |
| T071-33 | Cancelamento com operação em voo não libera o resolvedor offscreen. |
| T071-34 | Save/load entre reserva e receipt suspende handoff e revalida epoch. |
| T071-35 | Fork de campanha não herda receipt indevido de outra branch. |
| T071-36 | Migração de build que remove assets invalida oferta pendente. |
| T071-37 | Worker LAN revogado perde direito de propor/resolver o incidente. |
| T071-38 | Rota e localização geográfica inválidas impedem encontro por teleporte. |
| T071-39 | Mudança FROZEN/PARTIAL/REALTIME não cria resolução retrospectiva. |
| T071-40 | Incidente antigo e já encerrado não reaparece após catch-up. |
| T071-41 | Handoff de conflito estratégico DEC-033 não equivale à resolução da guerra. |
| T071-42 | Backpressure de recursos rebaixa para pendente/narrativo sem efeitos inventados. |
| T071-43 | Falha do checkpoint mantém ledger consistente e sem duplicidade. |
| T071-44 | Restauro de backup reapresenta ledger correspondente, não efeitos futuros. |
| T071-45 | Log redacta segredos e registra motivos de rejeição e decisões de autorização. |
| T071-46 | POC host + dois clientes valida correlação de evento e ausência de dupla resolução. |

Todos os `T071-*` são hipóteses de validação para SPECS/POCs; nenhuma capacidade da engine foi demonstrada por esta documentação. Critérios de aceitação, datasets, logs, tempos e tecnologias de teste deverão ser especificados antes da execução.

## 11. Próxima decisão em aberto — DEC-072

**Catálogo e composição de encontros por build:** A) somente encontros nativos já presentes; B) gerar/criar qualquer encontro e scripts em runtime; **C, recomendada)** catálogo modular de componentes/templates curados por build, com adapters pré-testados, inclusão offline controlada e sem geração dinâmica de engine até prova de viabilidade, compatibilidade e autorização. A DEC-071 disciplina *quando e como transferir* um incidente, não *como construir* seu encontro.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

DEC-072/C define catálogo modular por build e adapters testados para a etapa de composição. Uma reserva/handoff DEC-071 não implica que exista template/asset/capability mecânica; impedir efeitos em caso de divergência ou incerteza.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

DEC-073 complementa o handoff exclusivo: após resultado único, preservar owner/effects, reconciliar cleanup pendente sem reativar resolvedor offscreen.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Somente um resultado confirmado após handoff DEC-071 alimenta o ledger causal DEC-074; exclusividade e fencing impedem duplicação por fluxos locais e distantes. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Atribuição depende do resolvedor único do incidente; uma duplicata offscreen/local não pode gerar crédito ou culpa duas vezes.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Handoff incidente→encontro não autoriza trocar identity/runtime ou revelar alias; identidade persistente/ownership e receipts do host permanecem separados da persona.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Encontro com guardas/autoridade DEC-078 exige handoff único e host; acusação não pode criar spawn e resolução duplicados.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Pedido de auxílio/captura DEC-079 não cria encounter local sem handoff DEC-071, compatibilidade de área, exclusividade e receipt host; não duplicar guardas.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Dano de encontro offscreen/local DEC-081 usa `incident_id` e ledger exclusivo DEC-071; nenhum segundo pagamento por evento de combate duplicado.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-084/C — Discovery v8.0

Ameaças durante escolta seguem reserva exclusiva e handoff local/offscreen, sem criar duas emboscadas nem repetir proteção/loot.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Uma tentativa de interceptação de comboio não pode ser resolvida em duplicidade offscreen/local; ledger, reservation e host receipt mantidos.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Isca não gera encontro automático. Handoff conserva exclusiva resolução local/offscreen e requer precondições e reserva idempotente.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Handoff offscreen/local conserva identidade NPC e evento de compromisso sem spawn ou actor ownership arbitrário.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Handoff offscreen/local não repete reunião ou entrega; ledger de compromisso e receipt host mantém exclusividade com idempotência.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Handoff incidente offscreen→local não promove boato em spawn nem aceita documento ficcional como receipt mecânico; somente host confirma a presença.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-091/C — Discovery v8.7

Handoff de incidente/observador a cena local deve validar reserva, identidade, ownership e host receipt antes de instanciar encontro.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Handoff offscreen→local usa token/fencing por instância; pause/replan não resolve duas vezes o mesmo incidente.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Reservation/fencing de handoff offscreen↔local é específico ao incidente e deve compor as regras gerais de concorrência DEC-093, sem dois tokens confirmarem o mesmo encontro.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Reserva de handoff confirmada não é liberada por TTL isolado; resolver ownership offscreen/local e receipts antes de reutilização.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Rule DEC-096 de evento regional não inicia encontro nativo sem handoff/receipt DEC-071; registrar resolução única.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Aplicação DEC-096/C de encontro histórico só ocorre após handoff/offscreen DEC-071 e recibo único, não dupla resolução.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Materialização eventual de risco DEC-097/C usa handoff offscreen-local e receipt único, nunca dupla resolução.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Lease de handoff impede que o mesmo incidente seja resolvido offscreen e novamente via spawn local; DEC-098 consulta esse ledger.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Handoff offscreen→local não instancia novamente ator/encounter do host; ownership antes de cada mutação.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Handoff de encontros precisa usar eventos host-confirmed e estados de quest semanticamente permitidos.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Regional simulation and materialization cannot treat ambiguous quest flags as facts. Protect quest-owned actors/objects and persistent NPC identities; semantic milestones need curated proof and do not grant spawn, despawn, cleanup, loot or irreversible effects without existing host gates. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **retorno de offscreen para mapa**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para handoff offscreen-local evita duplicar entrega após load, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para handoff offscreen/local evita duplicação de rumor e conversa, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Handoff de entrega offscreen para local requer uma única resolução. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Handoff local evita dupla resolução da mesma obrigação em trânsito. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
