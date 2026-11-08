# 69 — Itinerários hierárquicos, deslocamentos regionais e presença mecânica de NPCs

**Infinity AI / Discovery v6.5** · **DEC-069/C** · **ADR-0064** · **Aprovada como arquitetura; nada implementado ou testado no BG2:EE/EEex/multiplayer**

## 1. Objetivo e fronteiras

Conceder continuidade espacial e temporal a NPCs individuais DEC-066–068 quando migram entre cidades, regiões e rotas de Forgotten Realms. Evitar teleporte narrativo, contradição geográfica e duplicidade de presença, sem simular fisicamente cada passo. **Não presumir** que a engine suporta spawns, viagens fora de áreas carregadas, NPCs persistentes em regiões não visitadas ou sincronização automática em multiplayer.

## 2. Separação de domínios: canônico, campanha, motor

| Domínio | Conteúdo | Autoridade/validade |
|---|---|---|
| `knowledge/periods/<ano>-DR/` | Geografia, rotas e eventos de época com fontes/versões | DEC-060–062; não contêm memória individual nem atualizam automaticamente o passado de NPCs |
| Knowledge Pack fixado | Manifesto de revisões anuais por campanha | DEC-063; revisão por diff e autorização; preservar branch |
| World travel overlay | Plano de viagem, posição regional narrativa, etapas e dúvidas do NPC | Campaign/branch; event log e snapshots DEC-008/053 |
| EngineObservation | Área, instância e posição observadas quando disponíveis | Host BG2:EE; vincular fingerprint, epoch, checkpoint e identidade DEC-066 |
| NPC memória e crenças | Motivos para viagem, lembranças de paradas, rumores recebidos | Privada, ACL DEC-028, episódica DEC-064/065; sem conhecimento instantâneo |

**Invariante:** `lore_region != engine_area`. É possível uma cidade existir no lore sem mapa jogável na build instalada; nesse caso não há materialização mecânica prometida.

## 3. Grafo geográfico temporal e procedência

- Modelo candidato `WorldRouteGraph`: `graph_revision`, `knowledge_pack_ref`, `year_DR`, `source_claims[]`, `nodes[]`, `edges[]`, `resolution_status`.
- `PlaceNode`: ID lógico, tipo (cidade, porto, passagem, região), qualificadores de localização, intervalos de vigência, fontes e eventual mapeamento **verificado** a recursos do motor.
- `TravelEdge`: origem/destino, direcionalidade, meio (terra, mar, rio etc), contexto de estrada/porto/fronteira, evidência de disponibilidade no período, restrições e parâmetros temporais quando sustentados por evidência.
- `UNKNOWN` para distâncias, velocidades, custos ou conexão sem suporte. Proibir transformar lacunas em distância exata ou em trajeto *canônico* gerado pelo LLM.
- Modificadores dinâmicos de segurança, guerras, comércio e clima são overlays de eventos confirmados DEC-031/032/033; não modificam a fonte histórica base.
- Conflitos de fontes DEC-061 ficam `CURATION_REQUIRED`, sem consenso fabricado. Ingestão DEC-062 passa por staging, revisão e publicação na pasta do ano correto.

## 4. Contratos candidatos (não schema implementado)

```text
RoutePlan {
  plan_id, campaign_id, branch_id, npc_identity_id,
  knowledge_pack_revision, graph_revision, build_fingerprint,
  departure_place_ref, destination_place_ref, legs[],
  transport_modes[], proposal_reason, evidence_refs[],
  planned_world_time_window, clock_revision, checkpoint_id,
  approval_policy, acl_scope, plan_revision, status
}
TravelLeg {
  leg_id, origin_ref, destination_ref, travel_mode,
  path_evidence_refs[], constraints[], window_or_unknown,
  status, processed_world_time_cursor, event_ids[],
  idempotency_key
}
PresenceRecord {
  npc_identity_id, campaign_id, branch_id, area_or_region_ref,
  presence_kind: NARRATIVE_UNOBSERVED | NARRATIVE_VALIDATED | ENGINE_OBSERVED,
  observed_by_host_receipt?, checkpoint_id, engine_epoch?,
  world_time, source_event_id, confidence_gate
}
TravelEvent {
  event_id, plan_id, leg_id?, campaign_id, branch_id,
  world_time, kind, status: PROPOSED | APPROVED | CONFIRMED | UNCERTAIN,
  evidence_refs[], approval_ref?, host_receipt?,
  idempotency_key, revision, created_by
}
```

Nomes de campos e estados são candidatos para SPECS; os contratos não alegam existência de APIs EEex/BG2:EE. `NARRATIVE_VALIDATED` não é evidência de `ENGINE_OBSERVED`.

## 5. Máquina de estados de viagem

1. `DRAFT` — rota selecionada a partir de fontes e contexto, sem início de jornada.
2. `PENDING_AUTHORIZATION` — plano e motivo aprovados conforme risco/consentimentos antes de qualquer efeito.
3. `IN_TRANSIT_NARRATIVE` — evento de partida narrativo validado; **não implica** partida mecânica observada.
4. `PAUSED_OR_BLOCKED` — chuva, fronteira, script, evento regional ou restrição de evidência impede avanço e exige reavaliação.
5. `ARRIVED_NARRATIVE` — sequência de etapas temporais plausíveis e permitidas concluída no overlay causal; não há spawn automático.
6. `ENGINE_OBSERVED` — presença física determinada separadamente por observação/receipt do host, após correspondência DEC-066.
7. `UNCERTAIN/STALE/CANCELLED` — ação não deve ser promovida a fato válido, exceto por reconciliação ou decisão autorizada.

É possível observar mecanicamente um NPC antes de resolver seu plano narrativo: tal inconsistência **não** será escondida; exige reconciliação com host/script. Uma viagem pode permanecer narrativa e nunca se materializar numa área sem suporte da build.

## 6. Políticas de tempo e atividade

- `FROZEN`: tempo de campanha parado => nenhum deslocamento temporal motivado apenas por horas reais.
- `PARTIAL`: avançar somente janelas concedidas pelo relógio e pelo checkpoint.
- `REALTIME`: usar política configurada do relógio com catch-up delimitado e validação causal, nunca converter fila em viagem concluída.
- `ACTIVE`: observação e interação situadas no host; `NEAR`: checagens regionais; `DISTANT`: lotes por etapa e prioridades; `DORMANT`: conservar itinerário, marcas de progresso e pendências. Sem LLM por tick.
- Quando faltarem informações temporais, usar janela/estado desconhecido ou planejamento pendente. Não gerar números estimados sem fonte e apresentá-los como tempo oficial de viagem.
- Integração DEC-056: gameplay/host/consistência prioritários, backpressure para planejamentos distantes, limite de backlog e garantias de retomada.

## 7. Replanejamento e encontros

- Replanejar sob alteração legítima de guerra, bloqueios, relações entre facções, condições de transporte ou novas fontes curadas. Manter versões anteriores e explicar o motivo.
- Recomendar alternativas apenas dentre conexões/condições conhecidas; se não houver caminho verificado, estado `BLOCKED/UNKNOWN`, sem teleporte.
- **DEC-070 ficará responsável pela política de encontros, imprevistos, danos e incidentes fora de cena.** Nesta decisão, não autorizar automaticamente violência, morte, gravidez, casamento, prisões, perda de itens, mudança de quests ou danos.
- Locais fora da instalação jogável permanecem na camada narrativa, sem injunções ao motor. Em áreas jogáveis, materialização futura exige inventário DEC-050/051, POC e host/Action Gateway.

## 8. Sincronização e reconciliação

Preflight antes de cada commit ou retorno: (i) `campaign_id` e `branch_id`; (ii) `npc_identity_id=VERIFIED`; (iii) relógio/revisão e intervalos autorizados; (iv) Knowledge Pack e grafo; (v) fingerprint build/mod e inventário; (vi) epoch/área observada; (vii) ACL, risco, host receipt para alterações mecânicas; (viii) checkpoint consistente. `AMBIGUOUS`, `STALE` e `UNCERTAIN` são fail-closed. Replays idempotentes; divergências ficam auditadas e não dão origem a duplicação de presença.

## 9. Privacidade e segurança

Workers LAN recebem somente dados mínimos para planejamento, filtrados DEC-028/058. Históricos secretos, NPC private memory e detalhes de PC só são transmitidos quando explicitamente autorizados. Propostas e cache devem ser escopados à campanha e ao ramo; revogação impede novas publicações. Logs operacionais não revelam itinerários privados quando segredo narrativo.

## 10. Dependências e POCs

- BG2:EE nativo → inspeção read-only de observações e refs → EEex bridge offline controlada → testes de save/load → host + dois clientes → EET/mods conforme matriz. Nenhuma POC foi executada nesta etapa.
- Testar scripts nativos, transições de área, IDs reciclados, múltiplos clientes, eventos de quest/romance, migração de build, rewind, checkpoints e reentrada de personagens.
- Se não for possível comprovar correspondência e materialização, sistema limita-se a **planos narrativos não materializados**, com comunicação honesta dessa limitação.

## 11. Testes candidatos — não executados

1. **T069-01:** Planejamento exige `campaign_id`, `branch_id` e `npc_identity_id` verificado.
2. **T069-02:** NPC AMBIGUOUS/UNCERTAIN não recebe plano nominal com memórias de homônimo.
3. **T069-03:** Rota sem ligação curada não produz caminho imaginário nem tempo garantido.
4. **T069-04:** Um nó de lore sem `engine_area` não autoriza spawn no mapa.
5. **T069-05:** Grafo 1369 DR não recebe informação futura via busca indiscriminada.
6. **T069-06:** Proveniência de cada aresta geográfica sobrevive à consolidação de dados.
7. **T069-07:** Mudança de Knowledge Pack de campanha revalida segmentos dependentes.
8. **T069-08:** Uma fonte contraditória de geografia permanece pendente de curadoria DEC-061.
9. **T069-09:** Evento de partida proposto não confirma saída física da área.
10. **T069-10:** Partida observada pelo host confirma a transição somente no checkpoint certo.
11. **T069-11:** FROZEN com sessão fechada não avança o progresso do itinerário.
12. **T069-12:** PARTIAL aplica somente o intervalo temporal autorizado.
13. **T069-13:** REALTIME não converte relógio real em chegada automática sem demais requisitos.
14. **T069-14:** Job atrasado não preenche viagem como acontecimento consumado.
15. **T069-15:** DISTANT progride por lotes sem LLM/tick ou pathfinding offscreen.
16. **T069-16:** DORMANT conserva roteiro e watermark sem processamento contínuo.
17. **T069-17:** Passar DISTANT→NEAR não reescreve etapas já confirmadas.
18. **T069-18:** Conflito de checkpoint gera STALE sem mutação.
19. **T069-19:** Replay de segmento com idempotency_key não duplica presença ou eventos.
20. **T069-20:** Restauração de save anterior descarta resultados de futuro e revalida plano.
21. **T069-21:** Fork de campanha isola viagens e encontros por branch.
22. **T069-22:** Mudança de build/mod invalida refs de engine e força reconciliação.
23. **T069-23:** Bloqueio de estrada com evidência registrada pausa trecho afetado.
24. **T069-24:** Rota replanejada registra motivo, revisão e autorização; não apaga história.
25. **T069-25:** Dados de guerra/facção não confirmados não bloqueiam percurso como fato.
26. **T069-26:** Rota marítima exige meio e trecho compatíveis; não inventa travessia.
27. **T069-27:** Custos e velocidades desconhecidos permanecem UNKNOWN, não números simulados como canônicos.
28. **T069-28:** Chegada narrativa validada não produz `ENGINE_PRESENT`.
29. **T069-29:** Observação host de presença exige identidade verificada e epoch da área.
30. **T069-30:** Duas áreas físicas incompatíveis não recebem presença simultânea confirmada.
31. **T069-31:** Worker LAN não pode confirmar movimentação nem receber segredo sem ACL.
32. **T069-32:** Revogação de nó invalida proposta ainda não publicada.
33. **T069-33:** Falha de comunicação deixa ação mecânica UNCERTAIN, sem repetir spawn.
34. **T069-34:** Conteúdo nativo de quest/romance bloqueia transferência incompatível.
35. **T069-35:** Proposta de ataque fatal em estrada não vira morte automática.
36. **T069-36:** Ausência de rota para área de mod não provoca teleporte em reencontro.
37. **T069-37:** NPC individual não é contado simultaneamente na população agregada.
38. **T069-38:** Checkpoint conserva plano, revisão de grafo, watermarks e recibos.
39. **T069-39:** Métricas de atraso distinguem planejado, validado e observado sem expor segredos.
40. **T069-40:** POC read-only BG2:EE limpo → EEex → ação offline segura → host+2 clientes verifica capacidades reais ou mantém narrativa limitada.

**Nenhum dos 40 testes foi executado.** Benchmarks, suporte a spawns/movimento e consistência real BG2:EE/EEex/multiplayer continuam não comprovados. Valores e thresholds ficam para SPECS.

## 12. Próxima discussão DEC-070

Como tratar **imprevistos, encontros e perigos em viagens fora de cena**: **A** itinerários sem eventos; **B** eventos e consequências resolvidos livremente; **C (recomendada)** propostas de incidentes de rota com regras e evidências por risco, automação LOW allowlisted, bloqueio/revisão de MEDIUM/HIGH e efeitos mecânicos apenas com autorização/receipt do host. Não antecipar a decisão sobre esses incidentes como já aprovada.

## Integração com DEC-070/C — Discovery v6.6

DEC-070: itinerários poderão receber candidatos de imprevistos rastreados por segmento e janela temporal; LOW narrativo validado pode ser registrado, MEDIUM exige gate, HIGH não resolve combate/morte/loot offscreen. Qualquer pausa/replanejamento precisa de fato comprovado. Presença engine segue independente e host-confirmada.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Uma proposta de incidente DEC-070 em itinerário DEC-069 pode candidatar encontro local DEC-071, mas deve respeitar segmento, janela temporal e chegada narrativa diferente de presença mecânica. Não teleportar o NPC nem duplicar viagem.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Itinerário DEC-069 pode fornecer região/segmento para filtro de templates DEC-072, mas chegada narrativa jamais prova que uma área/ator existe na build.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Ao concluir encounter em itinerário, limpar componentes temporários somente com prova; localizações narrativas não são instâncias deletáveis.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Notícias e viajantes DEC-074 usam itinerários, rotas, velocidades/capacidades verificadas e relógio; não presumir entrega de mensagem nem presença mecânica. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Participação ou testemunho em uma rota exige localização/tempo e identidade coerentes; não atribuir crédito a NPC que não poderia estar presente.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

NPC em viagem pode mudar de nome social conforme contexto sem alterar sua identidade persistente. Conhecimento dos outros sobre alias requer contato/canal legítimo.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Guarda que atua em processo DEC-078 depende de presença coerente com região/itinerário; decisão narrativa não causa teleporte mecânico.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

A transmissão de mandados DEC-079 percorre rotas/canais plausíveis; perseguidores mecânicos precisam de rota, identidade e host. Nenhum teleporte narrativo.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Mensageiros/guardas de DEC-080 dependem de rota/clock e presença mecânica verificada; aviso em trânsito não teleporta NPC ou conhecimento.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Mensagens de retificação e atos de restituição via mensageiro respeitam tempo/região/roteiro; chegada narrativa não garante encontro ou entrega física.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Reuniões/convocações/mensageiros de fiscalização seguem tempo e lugar; aviso narrativo não confirma presença de oficial no motor.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Fonte/guarda em viagem tem presença temporal/geográfica; testemunho não comprova deslocamento nem autoriza teleporte ou proteção física.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Escolta e realocação obedecem itinerários, recursos, tempo e presença host; narrativa de chegada é distinta de posição mecânica validada.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Vigilância, percurso de informante e escolta respeitam itinerário/tempo; avistar saída não implica conhecer destino ou presença instantânea em outra região.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Mensageiro, isca visível ou pista em estrada exige itinerário e presença verificáveis, não teleporte nem criação de personagem por texto.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Traição não cria deslocamento onipresente; reuniões secretas exigem localização, itinerários e presença observável quando mecânico.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Contato e entrega física/por mensageiro consideram tempo, rota, local e presença real; contrato não teleporta fonte.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Presença/local/itinerário da fonte condiciona alegação de testemunho ocular; depoimento de evento distante exige canal legítimo.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Mensageiros, documentos e encontros para entrega de dossiê exigem rota/tempo plausíveis; o relatório não teleporta conhecimento entre cidades.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Viabilidade de presença e distância limita os planos; não colocar NPC distante fisicamente no local só pelo interesse narrativo.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Rota e localização novas exigem grafo geográfico temporal e presença mecânica observada, sem teletransporte narrativo.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Dois compromissos em pontos incompatíveis do espaço/tempo DR geram conflito e replanejamento; reserva de disponibilidade não teletransporta NPC.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Tempo DR e presença validada são distintos de TTL interno de lease; recuperação não teleporta NPC para resolver conflito.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Influência de eventos de estrada DEC-096 só vale para rota/região/janela e presença validada; efeitos indiretos de viagem exigem evento resolvido.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Impacto de estrada DEC-096/C é limitado por região/tempo/presença e só afeta itinerário via planejamento/receipt host validado.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Aumento agregado de patrulhas DEC-097/C não teleporta guardas ou altera rotas sem disponibilidade e validação host.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Itinerário e presença são separados do objeto físico: DEC-098 verifica posição/tempo antes de propor instância, sem teleporte narrativo.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Viagens e presença mecânica devem reconciliar actor ID, região, instância e estado de quest antes de materializar.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Presença regional do NPC não implica conhecimento de quest flag oculto.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Regional simulation and materialization cannot treat ambiguous quest flags as facts. Protect quest-owned actors/objects and persistent NPC identities; semantic milestones need curated proof and do not grant spawn, despawn, cleanup, loot or irreversible effects without existing host gates. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **tempo geográfico**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para itinerários e disponibilidade de mensageiros na cronologia DR, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para viagem, presença e canal de informação social, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Deslocamento real e agenda DR limitam entregas de mercadorias. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Viagens de escoltas obedecem distância, recurso e hora DR. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
