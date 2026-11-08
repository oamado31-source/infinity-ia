# Desenho preliminar 68 — Vida persistente, atividade adaptativa e retomada de NPCs fora de cena

**Infinity AI / Discovery v6.4** · **DEC-068/C** · **ADR-0063** · **Status: arquitetura aprovada, contratos candidatos; nada implementado/testado**

## 1. Problema e fronteiras

A DEC-067 permite que NPCs inicialmente comuns adquiram identidade lógica persistente. A DEC-068 decide apenas o **ciclo de vida de processamento** quando esses indivíduos saem da cena: preservar identidade, memórias e compromissos sem manter IA ou simulação física contínua. O mundo não deve congelar semanticamente todos os indivíduos, mas também não pode inventar seu histórico de cinco anos ou produzir ações mecânicas sem o BG2:EE e o host. A atividade computacional é distinta de identidade, presença física, conhecimento e tempo do mundo.

O modelo abaixo é conceitual. Qualquer API, hook, estabilidade de referência de NPC, spawn, pathfinding, multiplayer, mudança em save ou diálogo no motor está **PENDENTE de POCs**. Nenhuma programação do Infinity AI é iniciada neste Discovery.

## 2. Estado ortogonal: representação, processamento, identidade e presença

| Eixo | Estados representativos | Autoridade / restrição |
|---|---|---|
| Tipo de representação | `AGGREGATE`, `EPHEMERAL`, `PROMOTION_CANDIDATE`, `INDIVIDUAL_PERSISTENT` | DEC-067; só o último possui biografia persistente individual autorizada |
| Identidade lógica | `VERIFIED`, `CANDIDATE`, `AMBIGUOUS`, `STALE`, `UNCERTAIN` | DEC-066; nenhum vínculo pessoal por semelhança de nome/sprite |
| Nível de atividade | `ACTIVE`, `NEAR`, `DISTANT`, `DORMANT` | DEC-021; granularidade de processamento, **não** fato físico |
| Presença mecânica | `HOST_OBSERVED`, `NOT_OBSERVED`, `UNKNOWN` | DEC-011/012; estado de BG2:EE confirmado pelo host quando disponível |
| Proposta narrativa | `PENDING`, `PROPOSED`, `VALIDATED`, `CONFIRMED`, `REJECTED`, `UNCERTAIN` | `CONFIRMED` apenas por política explícita/receipt válido |
| Relógio da campanha | `FROZEN`, `PARTIAL`, `REALTIME` | DEC-022; sem relógio paralelo por NPC |

**Invariante:** passar a `DORMANT` não altera o tipo `INDIVIDUAL_PERSISTENT`, nem rebaixa direitos, âncoras, `NPCIdentity`, estado de quest ou registros de eventos. Também não gera um `HOST_OBSERVED` para uma área não carregada.

## 3. Regimes funcionais

### ACTIVE — cena / NPC observado

- Priorizar interações dos jogadores; se efeitos dependerem do motor, exigir identidade verificada, precondições e receipt do host.
- Somente conteúdo de contexto autorizado alimenta a IA; regras/roteiros nativos prevalecem na fronteira mecânica.
- A presença mecânica e a atividade narrativa não são presumidamente equivalentes. O motor pode deixar de expor a instância.

### NEAR — proximidade / relevância

- Rotinas ou acontecimentos próximos podem ser avaliados sob regras determinísticas e lotes modestos; dependências de quest/facção e interações especiais permanecem protegidas.
- Relevância pode elevar nível; ninguém recebe memória de acontecimentos ainda não observados/acessíveis.

### DISTANT — longe / evolução agregada e limitada

- Manter cursor temporal por NPC/ramo e aceitar apenas intervalos de `world_time` aprovados, calculados conforme DEC-022.
- Regras podem gerar **propostas** ou mudanças de baixo risco explicitamente permitidas e justificadas; não interpretar silêncio do motor como aprovação de morte, casamento, deslocamento garantido, recrutamento ou estado de quest.
- Reusar informação regional agregada sem duplicar a contagem/efeitos do indivíduo (DEC-067).

### DORMANT — hibernação operacional

- Não executar agentes/LLMs por tick. Reter estado mínimo, índices de retomada, última revisão consistente, pendências e memórias críticas, sob controles de privacidade e retenção.
- Reativar somente por encontro observado, interesse narrativo autorizado, evento de mundo com dependência real ou solicitação validada. O simples carregar do save não implica todos os NPCs despertem.

## 4. Contratos de dados CANDIDATOS (não código, não schema final)

```text
NPCOffscreenState {
  campaign_id, branch_id, npc_identity_id,
  identity_proof_ref, activity_tier, last_observed_world_time,
  processed_until_world_time, world_clock_revision,
  engine_observation_state, build_fingerprint,
  knowledge_pack_pin, checkpoint_id, epoch,
  active_anchors_refs[], pending_event_refs[],
  npc_memory_revision, acl_revision, schema_revision
}

OffscreenJob {
  job_id, idempotency_key, purpose, npc_identity_id,
  campaign_id, branch_id, epoch, checkpoint_id,
  interval_start_dr, interval_end_dr, ruleset_revision,
  knowledge_pack_pin, acl_revision, max_work_units,
  deadline_policy, output_state
}

OffscreenProposal {
  proposal_id, originating_job, evidence_refs[],
  event_type, affected_npc_identity_id,
  confidence_or_unknown, risk_class, requires_host_receipt,
  consent_requirements[], proposed_time_dr,
  status: PROPOSED|VALIDATED|CONFIRMED|REJECTED|UNCERTAIN
}
```

IDs e estados acima são nomes candidatos. Nenhum campo garante disponibilidade técnica no BG2:EE; `last_observed_world_time` não implica residência permanente na área. Datas e relatos exigem fonte ou evento confirmado. `confidence_or_unknown` jamais confere automaticamente autoridade mecânica.

## 5. Transições e precondições

| Origem → destino | Condição necessária | Se falhar |
|---|---|---|
| ACTIVE → NEAR/DISTANT | Fim da observação/interação, revisão consistente e eventos pendentes classificados | Manter pendente/UNCERTAIN, não fechar consequência incerta |
| NEAR → DISTANT | Diminuir relevância sem compromissos urgentes; budget DEC-056 | Adiar com watermark, sem avançar fatos |
| DISTANT → DORMANT | Sem evento elegível e checkpoint/estado mínimo confiável | Preservar agenda de reconciliação, não descartar identidade |
| DORMANT → DISTANT | Evento autorizável ou catch-up dentro da política de tempo | Aguardar; nenhum efeito implícito |
| DORMANT/DISTANT → ACTIVE | `NPCIdentity VERIFIED`, branch/pack/build/clock/host coerentes e instância observada quando exigir efeito mecânico | Narrativa genérica validada ou bloqueio explícito; sem spawn presumido |

Caso haja restauração de save, novo branch ou migração de build, índices, jobs e projeções devem ser revalidados e resultados obsoletos descartados ou mantidos como registros de auditoria, sem repetições cegas.

## 6. Reconciliador de retomada — proposta de sequência

1. Ler estado confirmado da campanha (`campaign_id`, `branch_id`, checkpoint, epoch e relógio DEC-022) e manifesto de build DEC-051/052.
2. Confirmar `NPCIdentity` DEC-066 e vínculo com estado persistente individual DEC-067; rejeitar homônimos, respawns e observações obsoletas.
3. Verificar versão pinada do Knowledge Pack DEC-063 e permissões/ACL; fatos e rumores consultados no cânone **físico por ano DR** (DEC-060/061/062), com filtro epistêmico DEC-064.
4. Comparar último intervalo **processado** e último intervalo **confirmado**; determinar se existe catch-up legitimamente autorizado. Não usar duração de fila como relógio.
5. Preparar lote delimitado e regras versionadas, sem LLM obrigatório; produzir apenas propostas com proveniência e riscos.
6. Aplicar gates narrativos/mecânicos (DEC-011/012/027/034/041/049/050) e consentimentos. Para mecânica, exigir confirmação/receipt do host e reconciliar estado dos clientes.
7. Persistir confirmação e cursor de progresso de modo coerente com checkpoint DEC-053/054; falha no meio deixa evento pendente ou `UNCERTAIN`, nunca fato duplo.
8. Recuperar memórias relevantes DEC-065 somente após autorização, limitando contexto, impedindo divulgação de segredos e mantendo eventos antigos reconstruíveis.

## 7. Exemplos e limites para eventos fora de cena

| Exemplo | Tratamento permitido no Discovery |
|---|---|
| Mercador deixa de atender clientes durante ausência do jogador | Pode ser uma projeção de rotina se não contradizer estado nativo e for autorizada por política de baixo risco |
| Mercador ampliou sua loja em cinco anos | **Proposta** dependente de tempo, recursos, região e evidências; não publicar como fato por default |
| Mercador casou, teve filho ou morreu | Consequência pessoal/irreversível requer política específica, evidência e gate de risco; **não é sorteada automaticamente** |
| Companion recrutável está em outra área após sair do grupo | A narrativa pode conservar vínculos; a movimentação/recrutamento mecânicos dependem de scripts, presença e POC host+clientes |
| Nova guerra alterou atividade da cidade | Simulação estratégica pode impactar a situação local apenas via regras confirmadas; sem criar encontros físicos sem bridge/host |
| NPC ouve boato em DORMANT | Somente quando regras de propagação DEC-029 + tempo/contato justificarem aquisição; não aprende por nova revisão do KPack |
| Personagem reencontrado com nome e sprite iguais | Sem `VERIFIED`, não usar sua memória; preferir resposta neutra ou revisão |

## 8. Filas, prioridades, fairness e limites

- P0/P1: integridade, confirmações e interação imediata prevalecem sobre simulação distante (DEC-056).
- Catch-up em lotes com limites; processar backlog conforme capacidade sem inventar resultados de períodos não cobertos. Expor atrasos com linguagem clara, não como eventos concluídos.
- `idempotency_key` incorpora branch, NPC, intervalo, regras e epoch; resultados de workers LAN só podem ser aceitos se identidade, ACL e revisões continuarem válidas.
- Quotas de memória, CPU, GPU, lotes por janela e tempo de resposta **não são números definidos aqui**: requerem SPECS, hardware e benchmarks; fallback testado pode devolver resposta curta validada.
- Não usar hibernação para contornar consentimento, evento HIGH, segurança, privacidade ou restrições de roteiro nativo.

## 9. Segurança, proveniência e privacidade

- Cânone: manter `knowledge/periods/<ano>-DR/` em partições físicas anuais, fontes concorrentes com proveniência DEC-061, staging DEC-062 e manifesto de versão por campanha DEC-063.
- Overlay privado: episódios DEC-064/065, identidade DEC-066 e promoção DEC-067 por campanha/ramo; não publicar dados íntimos no diretório anual.
- Contexto de LLM: liberar somente episódios que NPC poderia recordar e usuário/agente poderiam acessar; nó LAN deve estar pareado e autorizado DEC-057/058, roteamento DEC-059; nenhuma telemetria remota sem opt-in.
- Retenção: manter compromissos críticos segundo política, sem afirmar retenção eterna de dados pessoais. Expurgo legítimo e tombstones auditáveis tratados separadamente.
- Integridade: checkpoints/batches/ACL/revisões idempotentes, `UNKNOWN`, `STALE`, `AMBIGUOUS` e `UNCERTAIN` sempre bloqueiam ações potencialmente irreversíveis.

## 10. Dependências e aceitação futura

- **Preservadas integralmente:** DEC-060 (pastas anuais), 061 (fontes e conflitos), 062 (ingestão), 063 (Knowledge Packs), 064 (crenças), 065 (memórias), 066 (identidade), 067 (individualização). ADR-0055 a ADR-0062 não alterados.
- Demais dependências: DEC-008/011/012/021/022/027/029/032/034/049/050/051/052/053/054/055/056/057/058/059. DEC-006/007/013/015/017/018 ainda abertas.
- SPECS: parâmetros dos níveis, gatilhos de retomada, fontes de evento, TTL/retention, regras de reputação, temporalidade, UI e limites do motor.
- POCs: Windows BG2:EE limpo; EEex read-only, depois mutação offline segura; teste host e dois clientes; save/load, fork e recuperação; benchmark com regiões distantes e múltiplos NPCs.

## 11. Matriz de 36 testes CANDIDATOS — NÃO EXECUTADOS

1. **T068-01:** Em ACTIVE, diálogo próximo respeita identidade verificada e evento confirmado, sem LLM por tick.
2. **T068-02:** NEAR permite transição por regras com orçamento de concorrência limitado.
3. **T068-03:** DISTANT processa apenas intervalo temporal autorizado e grava watermark por NPC/ramo.
4. **T068-04:** DORMANT mantém memória e identidade persistentes sem executar ticks individuais.
5. **T068-05:** Passagem ACTIVE→DORMANT não remove promessa crítica confirmada.
6. **T068-06:** Passagem DORMANT→ACTIVE requer preflight de identidade e branch.
7. **T068-07:** DORMANT não produz encontros, falas ou testemunhos retrospectivos inventados.
8. **T068-08:** FROZEN com jogo desligado não avança world_time nem a trajetória do NPC.
9. **T068-09:** PARTIAL limita catch-up conforme política da campanha e mantém backlog residual explícito.
10. **T068-10:** REALTIME não confirma por inferência resultados mecânicos retroativos.
11. **T068-11:** Deixar worker ocioso não equivale a tempo DR decorrido.
12. **T068-12:** Job repetido com mesmo idempotency_key não produz evento duplicado.
13. **T068-13:** Job LAN de epoch anterior é marcado STALE e não altera estado.
14. **T068-14:** Fork após evento pendente não transfere resultado futuro para ramo anterior.
15. **T068-15:** Restore pré-evento revalida projeções, marcações de progresso e idempotência.
16. **T068-16:** Alteração de build/mod invalida ações que exigem scripts/refs nativos.
17. **T068-17:** Knowledge Pack atualizado não ensina fato não observado ao NPC dormente.
18. **T068-18:** Busca de conhecimento canônico respeita partição física por ano DR e vigência.
19. **T068-19:** Rumor social em DISTANT só chega por canal e janela temporal plausíveis.
20. **T068-20:** Segredo pessoal não é enviado ao worker LAN sem ACL explícita e atual.
21. **T068-21:** Revogação de nó/modelo invalida proposta pendente ainda não autorizada.
22. **T068-22:** NPC com identidade AMBIGUOUS não recebe memória nem biografia de homônimo.
23. **T068-23:** NPC individualizado não é contabilizado simultaneamente em agregado e em indivíduo.
24. **T068-24:** NPC dormente não é materializado automaticamente na engine em reencontro.
25. **T068-25:** Retorno com NPC nativo ativo usa observação/receipt do host e não cópia narrativa.
26. **T068-26:** Falha de comunicação host interrompe commit mecânico e conserva UNCERTAIN.
27. **T068-27:** Proposta de morte fora de cena permanece bloqueada sem políticas de risco e autorização.
28. **T068-28:** Proposta de casamento, filho, romance ou mudança irrevogável não é fato automático.
29. **T068-29:** Quest ou romance nativo desconhecido bloqueia intervenção fora de cena.
30. **T068-30:** Evento canônico HIGH preserva proteção especial e ramo correto.
31. **T068-31:** Backpressure adia trabalho distante sem gerar salto causal ou starvation ilimitada.
32. **T068-32:** Checkpoint captura NPC state, watermark, jobs pendentes e revision compatíveis.
33. **T068-33:** Crash entre proposta e confirmação não publica evento nem replica ação incerta.
34. **T068-34:** Original Mode e outra campanha não acessam as memórias de NPC do Living World.
35. **T068-35:** Relatórios operacionais distinguem propostas, atrasos, confirmados e UNCERTAIN sem vazar segredos.
36. **T068-36:** POC BG2:EE limpo, EEex e host+dois clientes mede viabilidade real; sem êxito, manter modo narrativo limitado.

**Nenhum dos 36 testes foi executado.** Não se afirma suporte real de NPC offscreen, estabilidade de identificação, pathfinding, comandos EEex ou consistência multiplayer. Executabilidade e critérios deverão constar de SPECS e POCs.

## 12. Próxima DEC-069

Definir como representar **deslocamentos e presença entre regiões** de NPCs individuais quando não são observados, distinguindo itinerário narrativo, passagem do tempo, travessia plausível e presença mecânica confirmada. Alternativas: **A** localização flexível/teleporte narrativo; **B** simulação física detalhada sempre; **C (recomendada)** itinerário hierárquico por etapas, restrições temporais e host-gated materialização. A DEC-069 não altera a política de execução adaptativa DEC-068.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: atividade DISTANT/DORMANT mantém itinerário e cursor; sem evidência de travessia não consumar chegada ou projetar aparição física. Itinerário complementa hibernação DEC-068 sem mudar suas regras.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070 regula incidentes durante hibernação/retomada; HIGH fica bloqueado e DORMANT retém propostas/cursor sem resultados irreversíveis inventados ou simulação contínua.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

A migração de atividade DEC-068 para ACTIVE via DEC-071 exige reserva única de incidente. NPC DORMANT não surge fisicamente por narrativa e seu estado só muda após reconciliação de tempo/identidade/host.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

NPCs DORMANT/NEAR não passam a presença mecânica por um template DEC-072; DEC-071 e host precisam confirmar área, instância e handoff.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Remoção de ator temporário não é hibernação da identidade narrativa; DORMANT mantém memória e eventos confirmados.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Difusão DEC-074 respeita estados hibernados: NPC dormente não recebe onisciência; mensagens pendentes entram em fila e são validadas ao retomar. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

NPC hibernado não recebe notícias e reconhecimento retroativos sem canal/relógio; retomar não cria testemunho de evento não observado.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

NPC hibernado preserva crenças por persona e histórico de descobertas sem aprender identidades futuras durante dormência ou catch-up artificial.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Autoridade NPC DORMANT não recebe mensagens por onisciência DEC-079; filas de entrega e retomada respeitam tempo/ACL e não exigem IA contínua.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

NPC DORMANT preserva direito e narrativa de reparação pendente, sem pagamento automático por catch-up, nem atribuição de notícia não recebida.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

NPC informante dormente não recebe notícia de investigação automaticamente; crença e proteção narrativa mantêm continuidade ao retomar.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

NPC ameaçado pode buscar segurança/abrigo no contexto de vida persistente, mas não obter invulnerabilidade ou deslocamento mecânico sem confirmação.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

NPC distante/dormente só recebe pista por notícia válida; retomada não gera observação de comboio a que não esteve presente.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

NPC fora de cena só aprende isca por canal e tempo no catch-up; não simular instantaneamente conhecimento, reação ou ataque.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

NPC DORMANT guarda vínculos e tensões persistentes; só os reavalia por eventos relevantes com canais e intervalos autorizados, sem LLM por tick.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

NPC DORMANT não negocia nem entrega informação em tempo real sem canal; catch-up só a partir de eventos comprovados e disponibilidade.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

NPC DORMANT não presencia eventos nem obtém informes automaticamente; catch-up registra apenas comunicações causais com janelas e recursos verificáveis.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

NPC distante/hibernado não recebe automaticamente relatório. Mensagens em trânsito aguardam canais e tempo; catch-up limitado não concede novos fatos sem recibo.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Planos offscreen exigem atividade permitida e atualização limitada; retornar de dormência não inventa execução.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

NPC hibernado ou distante não participa instantaneamente de missão revisada; catch-up respeita tempo e recursos.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

NPC offscreen pode ser alocado apenas dentro de janela/recursos verificados e sem conflito com atividade persistente; catch-up não inventa duas presenças.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Offscreen catch-up não pode forçar conclusão de tarefa aguardando recurso ou presumir que lease expirada finalizou viagem.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Eventos condicionais DEC-096 propostos dependem nível de atividade e catchup limitado; não fabricar NPC/tempo em DORMANT.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Eventos históricos DEC-096/C entram como sinais candidatos offscreen, nunca simulação minuto a minuto ou surgimento de NPC DORMANT.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Catch-up de efeitos DEC-097/C em DORMANT recalcula projeções limitadas sem spawn automático.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Atividade offscreen usa catch-up bounded e níveis de simulação; retorno gera diff de estado, nunca materialização retroativa irrestrita.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

NPCs fora de cena não são materializados se já existem no host, se ownership é desconhecido ou sem capacidade.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Hibernação não recebe snapshots de quests fora do escopo e não inventa progresso durante unload.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Regional simulation and materialization cannot treat ambiguous quest flags as facts. Protect quest-owned actors/objects and persistent NPC identities; semantic milestones need curated proof and do not grant spawn, despawn, cleanup, loot or irreversible effects without existing host gates. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **hibernação de NPC**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para vida offscreen pode receber mensagens apenas sob canal validado, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para vida offscreen sem aceitação universal de retratação, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

NPC offscreen cumpre obrigações só com recursos/canal comprováveis. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Simulação offscreen não cria prestação mecânica sem capacidade e recursos. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
