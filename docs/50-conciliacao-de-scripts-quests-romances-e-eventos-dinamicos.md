# DEC-050 — Conciliação de scripts, quests, romances e eventos do Living World

**Versão:** Discovery v4.6 · **Estado:** opção C aprovada como arquitetura, SPEC/POCs pendentes.  
**ADR:** `decisions/ADR-0045-conciliacao-hibrida-de-roteiros-nativos-e-eventos-dinamicos.md`.

## 1. Objetivo e escopo

Definir a fronteira entre os **roteiros executáveis reais** do BG2:EE/mods e propostas narrativas do Infinity AI sem congelar o mundo no roteiro original. A fonte da verdade para ações do motor continua sendo o host (DEC-011), com interface segura (DEC-012); as divergências históricas estão sujeitas a políticas de risco e cânone (DEC-009/027/034). Não há implementações, capacidades de leitura de flags ou APIs de EEex comprovadas.

O objetivo não é copiar/reescrever scripts nem criar automaticamente romances: é obter uma decisão **auditável** sobre se uma proposta é compatível, precisa ser adaptada, adiada, bloqueada ou submetida a aprovação como divergência causal.

## 2. Camadas e autoridade

| Camada | Papel | Limite |
|---|---|---|
| Conteúdo nativo/mods | Scripts, estados reais, diálogos, cenas, banters, romances, áreas e quests do build | Não presumir que estejam acessíveis ou modificáveis por API |
| Inventário do build | Metadados de versões, arquivos/recursos e dependências curadas com proveniência | Inventário incompleto ≠ ausência de dependências |
| Observação do host | Retrato temporal de presença/party/flags conforme hooks comprovados | Snapshot pode ficar desatualizado; registrar revision/time |
| Reconciliador determinístico | Verifica conflito, pré-condições, cronologia, risco, prioridade, consentimento e estado | Não executa mutations e não usa LLM como juiz |
| Story Directors / LLM | Propõem eventos, novas falas, variantes e alternativas | Não escrevem flags, não inventam receipts e não decidem legitimidade sozinhos |
| Action Gateway | Aplica ações tipadas autorizadas, se disponíveis e testadas | Falha fechada; `UNCERTAIN` exige reconciliação |
| Log + projeções | Auditabilidade e reconstrução persistente | Um plano de evento não vira fato sem evidência suficiente |

## 3. Política de precedência por tipo de conflito

1. **Compatível:** um rumor ou diálogo autorizado, sem alterar fatos protegidos nem requerer flags inexistentes, pode ser apresentado depois dos filtros de lore e acesso.
2. **Quest/diálogo ativo:** não remover NPC, promover etapa, trocar alvo, mudar variável, alterar romance ou iniciar cena concorrente sem conhecer e satisfazer as pré-condições reais desse build.
3. **Evento original futuro:** reservar seu marco apenas quando houver evidência de condição/fonte; não marcar destino histórico como inevitável se os jogadores produzirem divergência legítima, nem prometer que moderação de roteiro suporte a branch.
4. **Ambiguidade/observabilidade faltante:** tratar como `UNKNOWN` e bloquear *mutação*, mantendo opção de texto neutro ou adiamento que não afirme um fato novo.
5. **Divergência causal:** fato confirmado de jogador permite propor desvio; preflight técnico, autorização especial quando pertinente, caminhos de fallback e regressão são obrigatórios.
6. **Conflito de mods:** não assumir propriedade de recursos compartilhados; inventário e política de conflitos precisarão resolver ordem/versão do build, ou bloquear intervenção.

## 4. Estados conceituais do ciclo

| Estado | Significado |
|---|---|
| `PROPOSED` | Intento narrativo de uma fonte identificada, sem efeito comprovado |
| `EVIDENCE_PENDING` | Necessárias observações, catálogo, contexto ou flags que ainda não existem |
| `PREFLIGHT` | Verificação de dependências, políticas, cronologia, permissões, riscos e versão do build |
| `ALLOW_NARRATIVE` | Apenas redação/publicação narrativa autorizada, sem alteração mecânica |
| `ADAPT` | Nova proposta sem colisão; requer novo preflight antes de publicar/aplicar |
| `DEFERRED` | Proposta adiada para condições verificáveis; não é acontecimento realizado |
| `BLOCKED` | Não executar por conflito, falta de suporte ou proibição de política |
| `DIVERGENCE_REVIEW` | Branch histórico causal em revisão com autorizações correspondentes |
| `MECHANICAL_PENDING` | Ação tipada solicitada; aguardar/observar resultado do host |
| `UNCERTAIN` | Resultado indistinto; conciliar sem retry cego |
| `COMMITTED` | Fato consolidado após confirmação da fonte autoritativa apropriada |

É possível publicar fala sem mutação; o receipt do host se aplica quando há efeito mecânico. Publicar uma fala nunca confirma automaticamente um estágio de quest.

## 5. Contratos de dados candidatos (não schemas finais)

```text
InstalledContentManifest
  build_id, game_version, eeex_version?, mods[] (id, version, order, checksum?)
  content_unit[] (resource_id, type, source, owner?, canon_period?, precedence?)
  known_dependencies[] (resource_ref, condition_ref, confidence, evidence)
  known_quest_states[], companion_story_refs[], coverage_level, limitations
  generated_at, content_hash, validation_status

NarrativeConflictProposal
  proposal_id, campaign_id, origin_director, npc_id?, intended_location?
  narrative_type (DIALOGUE | QUEST | ROMANCE | TRAVEL | RECRUIT | DEPART | HISTORY)
  causal_event_refs[], expected_canon_refs[], observed_host_revision?
  required_conditions[], affected_resources[], affected_party_slots[]
  affected_relationships[], secrecy_acl, risk_class, idempotency_key
  expected_effects[], fallback_plan, candidate_text?

ReconciliationDecision
  decision_id, proposal_id, rules_version, build_manifest_hash
  observed_state_refs[], unknown_conditions[], conflict_refs[], chronology_refs[]
  decision (ALLOW | ADAPT | DEFER | BLOCK | DIVERGENCE_REVIEW)
  explanation_codes[], risk_approval_refs[], host_receipt_id?
  revalidation_required, journal_event_id?, phase, timestamp
```

**Cuidados:** uma `flag` referida em inventário não equivale à possibilidade de leitura/escrita em runtime; `confidence` não autoriza uma mutação. Documentos de instalação e compatibilidade não devem carregar conteúdo proprietário para redistribuição.

## 6. Algoritmo conceitual de reconciliação

```text
1. Receber proposta identificada, com proveniência e impacto esperado.
2. Validar campanha Living World, versão/build e políticas; checar ACL e autoria.
3. Classificar: narrativa sem efeito, evento world-state ou modificação do motor.
4. Recuperar apenas evidências permitidas: build, cenário, time DR, flags/party
   realmente observadas, compromissos de quest, canon, romance/banter e snapshots.
5. Se leitura relevante não existe ou diverge: EVIDENCE_PENDING / BLOCK de mutação.
6. Detectar colisão de condições, presença, tempo, eventos e compromissos.
7. Escolher por regra:
   - sem conflito e sem mutação: ALLOW_NARRATIVE
   - conflito contornável: ADAPT (gerar nova proposta → voltar a 2)
   - conflito temporário: DEFERRED (guardar precondições e janela, não marcar fato)
   - conflito proibido ou não reparável: BLOCKED (explicar e oferecer fallback)
   - alteração histórica causal e permitida: DIVERGENCE_REVIEW
8. Em mutação aprovada/testada: gateway tipado -> host -> observar poscondição.
9. Somente após confirmação: registrar fato no event log e atualizar projeções.
10. Se timeout/desacordo: UNCERTAIN -> reconciliação; jamais retry cego.
```

LLM pode ajudar a redigir um `ADAPT` e elaborar diálogos compatíveis, mas a avaliação de estado e autorização permanece determinística.

## 7. Exemplo guiado: companion necessário em Athkatla

Um companion com um diálogo/quest original ativo está em Athkatla. A agenda de facção e a DEC-049 propõem deslocá-lo para outra cidade.

- `POST_PARTY_LOCATION` só existe se saída da party foi confirmada. Se ele ainda pertence à equipe, a proposta de viagem é bloqueada.
- O inventário indica dependência com uma cena original. Se o estado da cena/flag for **confirmado**, a viagem que impossibilita a cena deverá ser adaptada/adiada/bloqueada.
- Se o estado da cena for **desconhecido**, não inferir que ela acabou; bloquear mutação até obter evidência.
- Uma proposta adaptada pode manter o NPC em Athkatla enquanto recebe contatos/rumores plausíveis, sem criar presença em outro mapa.
- Se jogadores criarem causa legítima para alterar a trajetória, solicitar a política de divergência; apenas aprovar mudança física quando for viável e testada.
- Um aviso textual "o NPC viajou" não substitui o recibo do motor nem efetua flag/area change.

## 8. Proteções específicas

**Quests:** não usar texto para avançar estados; dependências por versão e flags observáveis, sem escrita arbitrária. **Romances:** não criar ou substituir flags/relacionamentos nativos; cenas adicionais com consentimento, período, identidade e estado compatíveis. **Banters:** evitar competir com diálogos obrigatórios e respeitar gatilhos originais que tenham sido verificados. **Mods:** aplicar inventário e regressões por build; desconhecimento de outro mod bloqueia mutações que podem afetá-lo. **Modo Original:** nenhuma persistência, log ou runtime do Living World altera o modo original.

## 9. Interação com as decisões aprovadas

- **DEC-003:** instalação em fases; POC no BG2:EE limpo antes de EEex, EET e imports.
- **DEC-008/009/022/023/024/025/026/034:** evidência cronológica, arcos paralelos, política de divergências e risco HIGH protegido.
- **DEC-011/012/027:** host é autoritativo; gateway seguro, default-deny e idempotência.
- **DEC-014/021/032:** código determinístico e carga por relevância, sem LLM por NPC/tick.
- **DEC-028/029/030:** limites de leitura, segredos, rumores e reputação distintos de fatos.
- **DEC-039/040/041:** Story Directors não forçam PCs, não expõem segredo indevido e respeitam histórias pessoais.
- **DEC-047/048/049:** companions com personalidade, abandono legítimo e continuidade externa, mas sem duplicação de instâncias ou destruição de quests.

## 10. Riscos e mitigação

| Risco | Mitigação / validação candidata |
|---|---|
| Script/flag de mod desconhecido | Marcar `UNKNOWN`, bloquear mutação e abrir tarefa de inventário |
| Agenda externa sequestra NPC de quest nativa | Verificar party/posição/quest; `DEFER` ou `BLOCK`; nunca assumir teleporte |
| Romance incongruente ou quebrado | Inventário de progressão, autorizações, comportamento nativo preservado |
| Duplicação de NPC, spawn ou recrutamento | `npc_id` único, revisão host e pós-condições de membership |
| Divergência entre clientes multiplayer | Host receipt, observação de 2 clientes, replays idempotentes, snapshot |
| Flag presumida por LLM | Dados gerados sem autoridade; preflight determinístico e fontes |
| Mudança no build / ordem de mods | Fingerprint, invalidação, regressão por versão |
| Divergência de canon sem permissão | Classificação HIGH e revisão obrigatória; fallback seguro |
| Texto vaza segredos ou inventa fatos | ACL antes do LLM e checagem de proveniência/publicação |
| Corrupção de save | Builds imutáveis de testes, cópia/backup, rollback experimentado |

## 11. Testes candidatos de aceitação (não executados)

1. Evento narrativo compatível publicado sem escrever flags.
2. Cena original ativa impede deslocamento que a invalidaria.
3. Flag de quest desconhecida não é tratada como `false`.
4. Quest concluída e confirmada libera proposta antes adiada, após novo preflight.
5. NPC ainda recrutado não entra na agenda de vida externa.
6. NPC removido do grupo pelo host inicia agenda uma única vez.
7. Outro mod usa recurso relacionado: sem inventário, mutação bloqueada.
8. Romance original em andamento não é sobrescrito por conteúdo dinâmico.
9. Banter original pendente não é marcado como executado pela IA.
10. Quest original progride sem regressões quando módulo Living World está desativado.
11. Evento de jogador confirmado gera proposta de divergência, não escrita imediata.
12. Divergência HIGH não autorizada é recusada, com registro de motivo.
13. Divergência com autorização e POC só consolida após confirmação do host.
14. `ADAPT` volta ao preflight e não carrega aprovação indevida da proposta anterior.
15. `DEFER` preserva janela e causa, sem emitir fato confirmado.
16. Timeout do gateway produz `UNCERTAIN`, sem retry cego ou duplicação.
17. Save/load reconcilia proposta pendente sem avançar estado incorretamente.
18. Dois clientes veem efeitos mecânicos confirmados idênticos.
19. Alteração de versão/ordem de mods invalida garantias e exige novos testes.
20. Rumor de localização não transforma NPC em entidade física no mapa.
21. Narrativa não vaza segredo do histórico de PC em diálogo/LLM.
22. Modo Original nunca recebe flags, snapshots ou eventos do Living World.
23. Colisão de duas propostas no mesmo quest marker é serializada por revisão.
24. Falta de hook de leitura/escrita gera fallback narrativo sem mutação.

## 12. Gates de implantação e perguntas para SPECS

- **G0 — Inventário:** registrar game build, ordem de mods, checksum/versões, recursos e limites de observabilidade; cobertura nunca será automaticamente completa.
- **G1 — Somente leitura:** inspecionar recursos/flags com método verificado e comparar snapshots sem mutações.
- **G2 — Narrativa segura:** permitir apenas propostas sem efeito mecânico e testar colisões com quests/romances.
- **G3 — Comandos tipados isolados:** mutations de baixo risco com backup, preflight e host receipts; não inferir rollback perfeito.
- **G4 — Multiplayer e persistência:** testar dois clientes, save/load, reconexões, idempotência, seqüências de diálogos e regressões do Original.
- **G5 — Novos builds:** repetir testes em EET/IWD/NWNForBG conforme viabilidade de importação, sem declarar compatibilidade automaticamente.

**DEC-051 candidata:** como produzir e manter o inventário dos scripts, flags, quests, romances e dependências do jogo e mods: catálogo manual, descoberta automática ou inventário híbrido curado por build.  
**Status:** design de reconciliação decidido; ferramentas, fórmulas, cobertura real, hooks e implementações ainda não comprovados.

## 10. Dependência resolvida no Discovery: DEC-051 — inventário híbrido

A DEC-051 foi aprovada na **opção C** (ADR-0046/doc. 51). O preflight de scripts e quests deve usar manifesto por build, cobertura/curadoria, proveniência, dependências e observações runtime separadas. Varredura estática não confirma flags atuais ou andamento de quests. `UNKNOWN`/`CONFLICTED` e mudança de build impedem ações dependentes inseguras. Ferramentas, runtime hooks, desempenho e suporte a mods/multiplayer permanecem sem validação; a DEC-052 decidirá como tratar atualização de builds em campanhas em curso.

## Complemento DEC-052 — Regressão entre builds (Discovery v4.8)

A conciliação DEC-050 deve ser reexecutada diante de novas versões/ordens de mods. Validar dados e condições de quests/romances por build/campanha com evidências; mudanças não mapeadas não podem ser promovidas como seguras. A decisão de migrar é separada (DEC-052); adiar/bloquear propostas narrativas é preferível a aceitar estado runtime desconhecido.


## DEC-060 — gate narrativo antes da publicação

Propostas de IA devem ser validadas contra estados de quests e romances da build/ramo antes de prometer deslocamentos, recompensas ou mudanças de scripts. Conteúdo desconhecido não é considerado compatível por padrão; validação de texto não equivale a confirmação do motor.

## Integração DEC-063/C — lore novo não altera quests confirmadas (v5.9)

A troca de *knowledge pack* requer diff que reconheça missões, romances, scripts e diálogos já ocorridos. Uma descrição posterior de evento canônico não reescreve automaticamente estado de quest ou variável BG2:EE. Se uma atualização exigir capacidade mecânica, encaminhar às POCs/gates DEC-050/052/053; em caso de incompatibilidade, manter pacote antigo ou adiar/rejeitar alterações acopladas.

### Integração DEC-066/C — scripts/quests não provam identidade sozinhos (v6.2)

Flags, script names e arquivos de CRE inventariados na build podem complementar a evidência de identificação, mas não são automaticamente chaves únicas ou estáveis. Conflitos de duplicata e ID reciclado bloqueiam propostas de romance, recruta, quest ou reencontro dependentes de identidade até validação. Reconciliador continua aplicando preflight e host receipts para ações mecânicas.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

A promoção individual DEC-067 é apenas narrativa: nunca criar/sobrescrever scripts, quests ou romances nativos sem inventário da build e confirmação do host. NPC único/curado não é automaticamente observação `VERIFIED`.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

NPC offscreen DEC-068 não avança automaticamente flags, romances, quests e scripts nativos. Reencontro exige leitura/reconciliação do estado real, compatibilidade da build e receipt do host. `UNCERTAIN` mantém pendência e não executa replay cego.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: plano de deslocamento não se sobrepõe a movimentação/quests/scripts nativos; divergência gera reconciliação ou suspensão, sem override tácito.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070 não permite incidente offscreen avançar scripts/quests/romances nativos, alterar recursos ou resolver combate sem contratos e receipts host; desconhecimento de script -> bloquear proposta.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Antes de encontro DEC-071, inspecionar scripts/quest flags/romances e capacidades por build; proteger conteúdo nativo e rejeitar handoff com conflito. Não editar scripts/save ao vivo nem iniciar trecho de quest sem autorização/POC/receipt host.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Componentes DEC-072 devem declarar precondições/conflitos de scripts/flags/quests/romances de DEC-050; conflito desconhecido bloqueia ativação local, ainda que asset esteja presente.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Ownership de encontro não se estende a scripts/quests/romances nativos. Cleanup não pode remover atores/itens relacionados a conteúdo protegido.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Notícia pós-encontro DEC-074 não altera flags de missões ou romances nativos por inferência; somente contratos tipados testados e receipts do host. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Decisão de autoridade DEC-078 não aplica flag de quest, romance, script de guarda ou reputação mecânica sem testes de conflito nativo, gateway/host e precondições.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Autoridade de guilda não altera automaticamente script/quest nativos. Efeito de pedido DEC-079 é bloqueado sem precondições, capacidade comprovada e host receipt; não sobrepor AI de guardas.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Suspender/revogar ordem DEC-080 não altera automaticamente flags de quests ou scripts nativos; qualquer mudança precisa de adapter comprovado, precondições e receipt do host.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Reparação de quests/romances DEC-081 requer inspeção de script nativo e contrato testado; caso contrário decisão narrativa/pendência, nunca mudança direta em save ou flag.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-084/C — Discovery v8.0

Proteção de NPC nativo não sobrescreve scripts/quests/romances, nem concede invisibilidade ou NPC escort sem POC/host.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Rumor ou possível descoberta de abrigo não manipula scripts, quests, romances ou flags nativos sem gateway/host e capability testados.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Ruptura ou mudança de vínculo não pode sobrescrever scripts, quest flags, romances ou recrutamento nativo sem validação por build e host; preservar recursos originais.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Termos de segredo/informe não podem sobrescrever scripts, quests, romances ou condições nativas de NPC canônico sem teste e autorização.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Nenhum relatório de informante modifica flags de quests, romances ou scripts canônicos sem gateway e capacidade validada; rumor pode propor gancho narrativo condicionado.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Produzir dossiê não muda flags de quest/romance/journal. Qualquer ação de engine precisa capability testada, pedido tipado, confirmação host e reconciliação por save.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Operações derivadas de dossiês não ignoram scripts/quests ou os reescrevem; qualquer mudança exige compatibilidade testada.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Scripts e quests nativas não se cancelam por alteração de `OperationalProposal`; qualquer mutação precisa de capability testada, gateway e receipt.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Recursos e etapas protegidos por scripts/quests nativos não podem ser consumidos por plano concorrente só porque o scheduler reservou um item/NPC lógico.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Recovery não pode cancelar script de quest, romance ou cena nativa por suposição. Comandos em voo requerem receipt e POC específica, não rollback narrativo.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

DEC-095: compensação não desexecuta script confirmado. DEC-096: matriz só aponta candidate impacts, sem alterar quest flags/arcos sem capacidade/receipt host.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Nenhum campo `effect` na DEC-096/C admite scripts livres; somente templates allowlisted e capabilities provadas por build, com recibo host para inventário ou spawns.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Limites calculados DEC-097/C não modificam inventário, preços, scripts nem atores sem capabilities/receipts validados.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Scripts originais/quests e estado de cutscene prevalecem em sua responsabilidade; DEC-098 preserva e bloqueia patch genérico, DEC-099 definirá conflitos.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Scripts, quests, banters e romances nativos/modded são protegidos por ownership e campo; adaptadores precisam de build validada.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Estado de progressão de quest deve ser observado por probes read-only allowlisted e semanticamente minimizado antes de diretor narrativo; não editar scripts.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Catalogues by exact build/modpack/quest/script fingerprint, curated proof of semantic milestone and valid transition; an observed flag or stage is never an authorized quest write or host receipt. On patch or restore, invalidate semantic cache and avoid generic stage inference. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

DEC-102 reconcilia apenas projections do overlay, sem sobrescrever scripts, quests, romances ou identidade de NPCs. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** observar DEC-100, interpretar DEC-101 e reconciliar DEC-102 não são eventos automaticamente propagáveis. Apenas prova semântica atual e reconciliação `CONSISTENT_WITH_PROOF` ou `APPROVED_AND_COMMITTED_REBASE` habilita pedido de admissão lógica por ruleset pinado; rebase `PROPOSE_*` não permite emissão. Proposta, autorização, receipt host e conhecimento de NPC permanecem entidades separadas. Não reabrir quest, editar flags, alterar scripts nem assumir ownership por narrativa. Dedup por occurrence/lineage, sem duplicação após save/load ou observação repetida. Consultar `docs/103-admissao-e-propagacao-causal-de-marcos-de-quests-reconciliados.md`. **Sem POC no motor.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **quests e scripts**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para quests originais não são alteradas por review de crenças, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para quest e scripts originais não são alterados por reabilitação narrativa, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
