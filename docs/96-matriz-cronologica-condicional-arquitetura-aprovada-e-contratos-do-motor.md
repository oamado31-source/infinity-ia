# DEC-096/C — Especificação da matriz cronológica condicional e contratos de execução

> **Discovery v9.2 · ADR-0091 · APROVADA COMO ARQUITETURA; IMPLEMENTAÇÃO NÃO COMPROVADA.** Complementa a proposta inicial preservada em `docs/96-proposta-matriz-cronologica-condicional-de-eventos-e-repercussoes.md`. O schema `ruleset_v1.candidate.schema.json` é **candidato** e só contém dados sintéticos demonstrativos; integração EEex e canon FR real permanecem não testados.

## 1. Objetivo do sistema

Converter os eventos cronológicos curados de Forgotten Realms num **filtro de elegibilidade e proposta** baseado no relógio DR, no estado do ramo, no local e em regras explícitas. Separar: (a) fato histórico; (b) causalidade regional; (c) notícia conhecida; (d) efeito narrativo proposto; (e) mudança mecânica realmente confirmada. Nenhum livro ou cronologia é um script de spawn automático.

## 2. Três camadas, sete entidades

| Entidade | Fonte / storage | Campos principais | Responsabilidade e proibição |
|---|---|---|---|
| `CanonEvent` | `knowledge/periods/<ANO>-DR/` curado | `event_id`, `sources`, `date_assertions`, `date_precision`, `canon_status`, `region_ids`, `source_version` | Fato/lore; não mutar com o jogo; datas conflitantes não viram certeza |
| `HistoricalRuleSet` | catálogo versionado compilado e pinado ao KPack | `ruleset_id`, `revision`, `schema_version`, `pack_sha256`, `compatibility` | Regras editoriais de impacto; não é o texto do cânone |
| `ImpactRule` | `HistoricalRuleSet.rules` | `rule_id`, `canon_event_ref`, `phase`, `time_gate`, `scope`, `predicates`, `effects`, `risk`, `caps` | Elegibilidade declarativa; nunca executar código livre |
| `CampaignHistoricalState` | campanha/ramo/epoch | `campaign_id`, `branch_id`, `world_clock`, `known_facts`, `divergences`, `region_state_revision` | Estado causal privado; não contaminar outro ramo |
| `ImpactProposal` | candidato efêmero/outbox | `proposal_id`, `rule_ref`, `scope_id`, `why`, `needed_gates`, `dedup_key` | Proposta, **não** feito consumado |
| `AppliedImpact` | ledger imutável/append-only da campanha | `effect_id`, `host_receipt`, `applied_epoch`, `source_proposal`, `scope_id`, `actual_result` | Fato realmente aplicado; futuro indireto depende dele |
| `KnowledgeAcquisition` | memória/ACL por NPC | `actor_id`, `claim_id`, `source/channel`, `received_at_dr`, `scope`, `confidence` | O que alguém sabe; não equivale a ocorrência e é falível |

**Relações:** `CanonEvent 1:N ImpactRule`; `ImpactRule 1:N ImpactProposal` por ramo/área/revisão; `ImpactProposal 0..1 AppliedImpact` ou múltiplos receipts idempotentemente correlacionados; `AppliedImpact 0:N` repercussões posteriores dependentes; `KnowledgeAcquisition` é independente de aplicado, requer canal. `CanonEvent` não herda segredos de PC.

### Chaves e partições

- Cânone: `period_id/year_dr/source_id/event_id`, arquivos por ano DR **fisicamente separados** DEC-060, independentes de campanha; claim temporal conflitante guarda múltiplas fontes.
- Regras: `ruleset_id + revision + rule_id` com hash de conteúdo, listas de build/version apoiadas por provas.
- Estado: `campaign_id + branch_id + host_session_epoch + ruleset_pin + knowledge_pack_pin` e snapshots/checkpoints por DEC-053/054.
- A mesma realização não ocorre duas vezes após reload: dedup transacional candidata `campaign+branch+epoch+event+phase+rule+scope+effect+ruleset_rev`; para aplicabilidade host usar `resolution_id` e recibo confiável. O item de proposta pode ser recalculado sem multiplicar efeito.

## 3. Matriz de edição amigável (visual planilha)

| Coluna | Exemplo sintético | Regra |
|---|---|---|
| Evento e fonte | `SYN-PORT-ALERT-1`, `SYN-SOURCE` | Source refs obrigatórios em canon real; fixtures sintéticas nunca publicar |
| Ano DR, precisão | `1369`, `MONTH` | `YEAR_ONLY` não assume 1º mês; divergência fica `DISPUTED` |
| Mês, dia, duração | `7`, dia não informado, `1 mês` | Janela separada de precisão de ocorrência; meses Harptos |
| Abrangência histórica | `REGIONAL` | `GLOBAL` não significa afeta todos os mapas |
| Região, local, tag | `region-example`, `road` | IDs físicos mapeados por build; desconhecido bloqueia efeitos mecânicos |
| Fase | `OCCURRENCE` | `PRE`, `OCCURRENCE`, `AFTERMATH`, `LEGACY` |
| Condições | `regional_alert == true` | AST allowlisted; desconhecido = não elegível |
| Dependências | `event_confirmed` | Evento base/ramo/parent receipt confirmados |
| Efeito direto | `propose patrol_intensity +1` | `ImpactProposal` até gate/host |
| Efeito indireto | `propose robbery_risk -1` | só após `AppliedImpact` pai, delay e caps |
| Duração/decaimento | `1 mês`, `cap 2` | expiração/decay por política futura DEC-097 |
| Sensibilidade/ACL | `PUBLIC_IF_LEARNED` | não revelar fontes confidenciais |
| Versão e commit | `KPack hash`, `rule revision` | migração exige diff e autorização |

**Normalização:** tabelas de curadoria distintas para evento, fonte, data, fase, escopo e regra; a vista tabular é **apenas uma interface para preencher e filtrar**, não a fonte executável monolítica. Usar identificadores canônicos estáveis e índices explícitos de tempo/região/tag.

## 4. Modelo temporal e períodos de incerteza

1. Clock de jogo deve representar `year_dr, month_id, day_of_month`, `intercalary_festival` e `clock_mode` DEC-022; não converter datas gregorianas.
2. Harptos possui 12 meses de 30 dias e dias intercalares; implementar parser estático validado e sem confundir dia intercalar com o dia 31 de um mês. Anos bissextos/eventos calendáricos precisam prova de fonte e regra explícita.
3. Diferenciar **quando ocorreu o evento** (`date_precision`), **quando seu impacto pode surgir** (`effect_window`), **quando rumor chega** (`received_at_dr`), e **quando recebeu validação** (`host_receipt_time`).
4. `YEAR_ONLY`: fatos podem informar baseline de período posterior se curadoria especial confirmou legado; sem mês exato, **não** ligar um trigger de ocorrência mensal arbitrário.
5. `MONTH` permite janela mensal, jamais concluir dia; `EXACT_DAY` exige dia válido; `INTERVAL` possui limites tipados e fontes; `DISPUTED` aguarda escolha de versão autorizada ou bloqueio; `UNKNOWN` não ativa.
6. `catch_up`: ao entrar numa campanha posterior, utilizar **snapshot/baseline explícito** e no máximo simulações retrospectivas permitidas e limitadas; não reexecutar guerra ou decretar morte que deveria ter ocorrido no passado.
7. O relógio FROZEN/PARTIAL/REALTIME só progride conforme decisão host DEC-022; horário do sistema operacional não adianta guerras ou sucessões.

## 5. Modelo geográfico e alcance

- `scope.level`=`GLOBAL/REGIONAL/LOCAL` representa abrangência do acontecimento; efeito local precisa `region_ids` ou `location_ids` + `location_tags` definidos.
- Tags por enum editorial: `tavern`, `palace`, `dungeon`, `forest`, `road`, `temple`, `market`, `port`, `gate`, `settlement`, `wilderness`, `camp`, `fortress`; locais reais com IDs do adaptador e mapa por build, fallback `UNMAPPED` bloqueando ação mecânica.
- Hubs, mapas interconectados, rotas de viagem, entradas de dungeon e subregiões requerem grafos/versionamentos próprios; tag não é substituto de presença física.
- A política de `propagation` é separada: rumor em tavernas pode se difundir após mensageiro/contato verificado, nunca broadcast do acontecimento em todo o continente.

## 6. DSL de IF/ELSE e engine de avaliação

**Permitido:** AST de `all`, `any`, `not`, comparadores `EQ/NEQ/IN/GT/GTE/LT/LTE`, flags e métricas allowlisted de fatos confirmados (não scripts de mod); limites configuráveis de profundidade, quantidade de nós, tamanho de listas e custo. Validar tipo (por exemplo `int` não é `bool`). Exibir `why_matched`, `why_blocked` com proveniência redigida por ACL.

**Proibido:** `eval`, Python ou JavaScript em strings, shell, execução SQL ad hoc, regex arbitrária sem limites, chamadas de rede, `$ref` externo em runtime, prompts como predicado, acesso a diretórios de outros anos/ramo, side effect no cálculo das condições.

Pseudoalgoritmo:

```text
ON (world_clock_commit | region_enter | regional_flag_change | receipt_reconciled | KPack_diff_authorized):
  require pinned_KPack && pinned_ruleset && authorized_campaign_branch
  candidates = temporal_index.query(DR_date, precision) ∩ spatial_index.query(region, location)
  for rule in candidates.sorted_by(rule_id):
    require source curated, phase/time permitted, branch compatible, capabilities verifiable
    require typed_conditions(rule, confirmed_world_state) == TRUE
    require prereq_events_confirmed && exclusions_not_confirmed
    if INDIRECT: require parent.AppliedImpact.CONFIRMED + allowed_delay + same lineage/scope
    compute proposal_key, version, risk, limits; ignore if already applied/pending/UNCERTAIN
    enqueue ImpactProposal (NO MUTATION)
  only policy+ActionGateway+verified host receipt can create AppliedImpact
  KnowledgeAcquisition requires different delivery pipeline and real reception
```

**DEFINIÇÃO CRÍTICA:** `global_event` ∄ `global_NPC_knowledge`; `DIRECT` ∄ aplicado; `proposal` ∄ autorização; `host_dispatch` ∄ `host_confirmed`.

## 7. Ciclo de vida, efeitos e casos de falha

Estados do impacto: `INELIGIBLE -> ELIGIBLE -> PROPOSED -> VALIDATING -> AUTHORIZED -> DISPATCH_PENDING -> DISPATCHED -> CONFIRMED` ou `REJECTED/SUPPRESSED/EXPIRED/UNCERTAIN` (transições limitadas). `CONFIRMED` não volta a inexistente: eventual compensação DEC-095 é **novo efeito**. Uma divergência DEC-024–026/034 impede novos atos canônicos incompatíveis, nunca desfaz fatos anteriormente observados.

- **Direto:** `host_receipt` ou confirmação genuinamente adequada ao domínio. Ex.: patrulha candidata requer NPC spawn/adaptor testado, escalação, recursos e permissão.
- **Indireto:** exige registro do efeito-pai aplicado e limites de atraso/escopo; não criar causalidade circular automática; detector de ciclos em DAG de regras.
- **Composição:** conflitos entre guerra, crise e festival sobre patrulhas e preços exigem `conflict_policy` e limites explícitos; política numérica completa a discutir na DEC-097. Não acumular sem caps nem depender de ordem aleatória.
- **Retentativas:** mesmo ID/revision/epoch, `UNCERTAIN` não reenvia; esperar recibo, comparar checkpoint/save e reconciliar. Snapshots e migração KPack não reproduzem eventos.
- **Zonas offscreen:** FROZEN/DORMANT não geram NPCs por minuto; atualizar indicadores agregados só com autorização, resumos limitados e checkpoint.

## 8. Segurança, auditabilidade e privacidade

- Catálogo físico `knowledge/periods/1369-DR`, etc., separado do índice de regras; permissões canônicas nunca são as permissões de NPCs. Retrieval de LLM limitado a fatos aprendidos.
- Diferença explícita entre `CanonEvent`, `CampaignHistoricalState`, `KnowledgeAcquisition` e `NarrativeOutput`. Fatos de 1373 DR não aparecem automaticamente na memória de NPC em 1369 DR.
- Evidence chain aponta qual fonte sustentou ano/região e qual regra produziu proposta. Efeitos host possuem receipt, `action_id`, epochs e dedup; journaling redigido por audiência.
- Quest, combate, economia, reputação, morte e mudança de facção são operações mecânicas **capability-gated** e host-authoritative DEC-011/012/027/051/056/066–074.
- Não integrar dados pessoais reais; segredos de testemunhas, pseudônimos e refúgios são protegidos DEC-076/083–090.

## 9. Layout proposto sem quebrar layout atual

```text
knowledge/periods/<YEAR>-DR/       # EXISTENTE - CANON CURADO por ano, SEM sobrescrever
knowledge/campaigns/...            # EXISTENTE - estado privado / overlays
world-rules/chronology/...          # PROPOSTO - regras declarativas compiladas (não criadas como motor real)
indexes/chronology/...              # PROPOSTO - cache derivado por KPack/ruleset/branch/build
examples/chronology/...             # EXISTENTE - protótipos de fixtures sintéticas
```

**Contratos de versão:** `source_refs`, `source_hash`, `knowledge_pack_pin`, `ruleset_revision`, `campaign_branch`, `host_epoch`, `calendar_revision`, `region_mapping_version`, `build_adapter_capabilities`. É proibido migrar pack/regra ou reprocessar save sem diff e autorização.

## 10. Casos de validação sintética

Um evento `SYN-PORT-ALERT-1` (não é lore real) ocorre no mês 7 de 1369 DR, na `region-example`. O avaliador de referência propõe patrulha mais intensa em `road/gate`, não em `dungeon` nem em outro ano. Um impacto indireto de menor risco de saque só se torna elegível após pai confirmado. `YEAR_ONLY` não agenda ocorrência mensal. Se a campanha decide que o alerta não aconteceu nesse ramo, a regra é suprimida e a fonte do livro não é editada.

- `examples/chronology/event_rule.schema.json` / `evaluator_reference.py`: protótipo **v0.1 sintético** herdado da v9.1, não um engine nem schema normativo final.
- `examples/chronology/ruleset_v1.candidate.schema.json` / `ruleset_v1.synthetic.json`: **proposta mais normalizada** de contrato, com validação JSON Schema sintética e sem efeito no jogo.
- `examples/chronology/test_evaluator_reference.py` e `test_ruleset_v1_schema.py`: testes **unitários**, não realizam POC BG2:EE, controle de NPC, host receipts ou importação de eventos oficiais.

## 11. Matriz de aceite arquitetural — 100 testes candidatos NÃO EXECUTADOS

A lista T096-001 a T096-100 abaixo é o escopo de aceitação futuro para testes de sistema / integração e **não** o resultado dos testes unitários sintéticos dos exemplos. Nenhum item autoriza tratar funcionalidades como implementadas.

### 1. Tempo DR / Harptos

- **T096-001 — NÃO EXECUTADO:** ano DR anterior não antecipa evento futuro.
- **T096-002 — NÃO EXECUTADO:** ano DR posterior não reexecuta ocorrência passada.
- **T096-003 — NÃO EXECUTADO:** mês conhecido distinto bloqueia impacto.
- **T096-004 — NÃO EXECUTADO:** data de dia específico correta permite proposta.
- **T096-005 — NÃO EXECUTADO:** dia anterior à ocorrência bloqueia proposta.
- **T096-006 — NÃO EXECUTADO:** YEAR_ONLY não ativa em mês presumido.
- **T096-007 — NÃO EXECUTADO:** intervalo confirmado inicia somente no limite válido.
- **T096-008 — NÃO EXECUTADO:** intervalo confirmado termina sem efeito fora da janela.
- **T096-009 — NÃO EXECUTADO:** dia intercalar é representado sem mês 13 fictício.
- **T096-010 — NÃO EXECUTADO:** FROZEN impede avanço por relógio real.

### 2. Fontes, curadoria e pins

- **T096-011 — NÃO EXECUTADO:** evento sem `source_refs` curadas bloqueia publicação.
- **T096-012 — NÃO EXECUTADO:** fonte conflitante DISPUTED não vira verdade automática.
- **T096-013 — NÃO EXECUTADO:** source hash modificado exige nova curadoria.
- **T096-014 — NÃO EXECUTADO:** KPack sem pin bloqueia regra.
- **T096-015 — NÃO EXECUTADO:** ruleset sem pin bloqueia regra.
- **T096-016 — NÃO EXECUTADO:** upgrade de KPack requer diff e autorização.
- **T096-017 — NÃO EXECUTADO:** rule revision divergente invalida cache.
- **T096-018 — NÃO EXECUTADO:** evento sintético não entra em catálogo canônico.
- **T096-019 — NÃO EXECUTADO:** event_id duplicado é rejeitado por lint.
- **T096-020 — NÃO EXECUTADO:** fonte futura não aparece na consulta do ano corrente.

### 3. Geografia e escala

- **T096-021 — NÃO EXECUTADO:** GLOBAL não materializa efeito em toda Faerûn.
- **T096-022 — NÃO EXECUTADO:** REGIONAL respeita region_ids allowlisted.
- **T096-023 — NÃO EXECUTADO:** LOCAL respeita location_ids concretos.
- **T096-024 — NÃO EXECUTADO:** tag road não ativa em dungeon.
- **T096-025 — NÃO EXECUTADO:** tag tavern afeta apenas taverna mapeada.
- **T096-026 — NÃO EXECUTADO:** local UNMAPPED bloqueia efeito mecânico.
- **T096-027 — NÃO EXECUTADO:** mapa com build incompatível não recebe ação.
- **T096-028 — NÃO EXECUTADO:** subregião inexistente não usa nome livre.
- **T096-029 — NÃO EXECUTADO:** rota com segmentos não afetados mantém isolamento.
- **T096-030 — NÃO EXECUTADO:** efeito em Athkatla não aparece em Neverwinter sem regra.

### 4. DSL segura

- **T096-031 — NÃO EXECUTADO:** operador EQ com bool tipado.
- **T096-032 — NÃO EXECUTADO:** bool não é promovido silenciosamente a int.
- **T096-033 — NÃO EXECUTADO:** IN sobre lista finita funciona.
- **T096-034 — NÃO EXECUTADO:** all/any/not produzem resultado determinístico.
- **T096-035 — NÃO EXECUTADO:** operador desconhecido é rejeitado.
- **T096-036 — NÃO EXECUTADO:** campo ACL privado fora de allowlist é rejeitado.
- **T096-037 — NÃO EXECUTADO:** profundidade de AST excessiva falha fechado.
- **T096-038 — NÃO EXECUTADO:** predicado com `eval`/código é rejeitado.
- **T096-039 — NÃO EXECUTADO:** condição ausente não assume true.
- **T096-040 — NÃO EXECUTADO:** dois workers produzem proposals ordenadas igualmente.

### 5. Fases, pré-requisitos e divergências

- **T096-041 — NÃO EXECUTADO:** PRE só ativa pré-evento autorizado.
- **T096-042 — NÃO EXECUTADO:** OCCURRENCE só ativa na janela confirmada.
- **T096-043 — NÃO EXECUTADO:** AFTERMATH requer fase histórica adequada.
- **T096-044 — NÃO EXECUTADO:** LEGACY usa baseline curado sem reencenar.
- **T096-045 — NÃO EXECUTADO:** pré-requisito não confirmado bloqueia proposta.
- **T096-046 — NÃO EXECUTADO:** exclusão mútua válida bloqueia efeito.
- **T096-047 — NÃO EXECUTADO:** desfecho do arco divergente suprime linha canônica incompatível.
- **T096-048 — NÃO EXECUTADO:** dois ramos recebem overlays independentes.
- **T096-049 — NÃO EXECUTADO:** SAVE antigo não reescreve cânone.
- **T096-050 — NÃO EXECUTADO:** PC não é forçado a assumir papel de protagonista canônico.

### 6. Efeitos diretos e indiretos

- **T096-051 — NÃO EXECUTADO:** DIRECT só emite proposta sem side effect.
- **T096-052 — NÃO EXECUTADO:** INDIRECT sem pai confirmado não aparece.
- **T096-053 — NÃO EXECUTADO:** INDIRECT com pai em outro ramo não ativa.
- **T096-054 — NÃO EXECUTADO:** INDIRECT com parent receipt UNCERTAIN não ativa.
- **T096-055 — NÃO EXECUTADO:** delay de propagação precisa estar vencido.
- **T096-056 — NÃO EXECUTADO:** regra circular de efeitos é rejeitada.
- **T096-057 — NÃO EXECUTADO:** cap impede modificador ilimitado.
- **T096-058 — NÃO EXECUTADO:** dois efeitos incompatíveis exigem conflict_policy.
- **T096-059 — NÃO EXECUTADO:** nenhum evento cria ouro/NPC sem adapter.
- **T096-060 — NÃO EXECUTADO:** efeito HIGH requer gate e autorização específica.

### 7. Recebimento / informação

- **T096-061 — NÃO EXECUTADO:** evento histórico não equivale a conhecimento de NPC.
- **T096-062 — NÃO EXECUTADO:** rumor depende de mensageiro ou canal válido.
- **T096-063 — NÃO EXECUTADO:** carta em trânsito não equivale a recebimento.
- **T096-064 — NÃO EXECUTADO:** NPC distante sem canal não ganha rumor.
- **T096-065 — NÃO EXECUTADO:** fonte recebe apenas claim autorizado por ACL.
- **T096-066 — NÃO EXECUTADO:** anonimato de testemunha não vaza em narrativa.
- **T096-067 — NÃO EXECUTADO:** informação falsa de informante não altera fato canônico.
- **T096-068 — NÃO EXECUTADO:** notícia histórica pode chegar com atraso.
- **T096-069 — NÃO EXECUTADO:** LLM não tem acesso ao diretório de ano futuro.
- **T096-070 — NÃO EXECUTADO:** LLM desligada não afeta filtragem determinística.

### 8. Host / consistência / idempotência

- **T096-071 — NÃO EXECUTADO:** dispatch host não equivale a receipt confirmado.
- **T096-072 — NÃO EXECUTADO:** receipt duplicado não duplica efeito.
- **T096-073 — NÃO EXECUTADO:** timeout UNCERTAIN não reenvia cegamente.
- **T096-074 — NÃO EXECUTADO:** recovery usa epoch de host e checkpoint.
- **T096-075 — NÃO EXECUTADO:** reload do save não reexecuta aplicação passada.
- **T096-076 — NÃO EXECUTADO:** reserva DEC-093 não equivale a recurso consumido.
- **T096-077 — NÃO EXECUTADO:** cancelamento usa nova revisão de saga se necessário.
- **T096-078 — NÃO EXECUTADO:** host+dois clientes convergem para mesma aplicação.
- **T096-079 — NÃO EXECUTADO:** adapter que não comprova capability bloqueia dispatch.
- **T096-080 — NÃO EXECUTADO:** compensação DEC-095 é novo ato e não retcon.

### 9. Performance e prioridades

- **T096-081 — NÃO EXECUTADO:** índice temporal retorna apenas candidatos do ano.
- **T096-082 — NÃO EXECUTADO:** índice espacial restringe região+tag.
- **T096-083 — NÃO EXECUTADO:** evento irrelevante não é avaliado a cada frame.
- **T096-084 — NÃO EXECUTADO:** mudança de flag produz apenas invalidação focal.
- **T096-085 — NÃO EXECUTADO:** cache é separado por knowledge_pack_hash.
- **T096-086 — NÃO EXECUTADO:** cache por branch epoch não vaza entre sessões.
- **T096-087 — NÃO EXECUTADO:** DORMANT usa catch-up bounded em vez de simular infinitamente.
- **T096-088 — NÃO EXECUTADO:** ciclo de impacto recursivo tem limite.
- **T096-089 — NÃO EXECUTADO:** regra pesada excedendo budget falha fechado.
- **T096-090 — NÃO EXECUTADO:** log de decisões informa por que regra foi bloqueada.

### 10. Curadoria de FR e aceitação

- **T096-091 — NÃO EXECUTADO:** matriz de doze eventos preliminares não vira trigger automático.
- **T096-092 — NÃO EXECUTADO:** data histórica precisa de fonte de confiança revisada.
- **T096-093 — NÃO EXECUTADO:** eventos de Baldur Gate e Neverwinter permanecem cenários separados.
- **T096-094 — NÃO EXECUTADO:** sucessão política requer período/cargo corretamente mapeado.
- **T096-095 — NÃO EXECUTADO:** encontro de campanha clássica não cria protagonista NPC indevido.
- **T096-096 — NÃO EXECUTADO:** eventos em regiões distintas respeitam distâncias.
- **T096-097 — NÃO EXECUTADO:** efeito de guerra na taverna precisa canal ou presença local.
- **T096-098 — NÃO EXECUTADO:** migração de release mantém antigos ADRs imutáveis.
- **T096-099 — NÃO EXECUTADO:** nenhuma fixture sintética altera o mundo do jogo.
- **T096-100 — NÃO EXECUTADO:** teste end-to-end BG2:EE/EEex é requisito antes de alegar implementação.

## 12. Riscos e gates para implementação posterior

- Maior risco: **inventar datas** e importar conhecimento futuro; mitigar com pins, precisão explícita e testes de corpus de fontes.
- Risco de **onisciência e divulgação**: ACL por NPC/canal, retrieval temporal físico e registro de recepção.
- Risco de **mudanças mecânicas não corroboradas**: Action Gateway, inventário real, adapter testado por build, receipt host; fail-closed.
- Risco de **explosão de regras**: normalização, índices, budget, composição com caps e scheduler DEC-056.
- Risco de **fato histórico vs decisão do jogador**: overlays separados, revisão do branch, temporal exception DEC-024–026 e irreversíveis DEC-034.
- Risco de **falsa validação**: testes do avaliador Python sintético não contam como nenhum dos 100 T096-* de engine/integração. Cada teste deverá ser executado e registrar ambiente, build, logs e evidências para mudar o status.

## 13. Dependência/continuidade: DEC-097

**Tema:** agregação/precedência, limites e decaimento de efeitos simultâneos de eventos históricos. **A:** último efeito vence; **B:** LLM decide; **C:** políticas determinísticas por domínio com caps, precedência, janela, revisão e receipts. **Ainda em aberto.**

## Integração DEC-097/C — Discovery v9.3

DEC-097/C detalha a composição prevista na DEC-096, com policies tipadas, stacking, caps, fade e receipts; elegibilidade DEC-096 preservada.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Matriz DEC-096 gera elegibilidade/propostas sem spawn: DEC-098 introduz diff por snapshot e confirmação host após composição DEC-097.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Ruleset histórico calcula candidatos apenas, não assume propriedade da área/entidades.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Rulesets históricos usam critérios narrativos curados, não future branches extraídos de scripts.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Semantic quest milestones are curated technical metadata, separate from FR historical canon partitioned by year DR and private campaign overlays. UNKNOWN, AMBIGUOUS or stale milestones cannot trigger chronology, historical effect or materialization; lore packs do not authorize interpreting runtime flags. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Não derivar impactos cronológicos de marcos apenas rebaseados, sem admissão causal DEC-103. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** marcos confirmados de quests originais são **origens candidatas** de regras históricas/regionais, não fatos canônicos escritos em `knowledge/periods/<ANO>-DR/`. A admissão exige prova reconciliada DEC-100/101/102, clock DR e branch adequados; a matriz DEC-096 filtra local, fase e precondições e DEC-097 compõe impactos. Escopo global não dá conhecimento universal. Evento proposto, evento host-confirmed e rumor entregue são distintos; nenhum efeito mecânico sem Action Gateway/receipt. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **janela DR e ramo ao retificar repercussão**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para eventos históricos não criam recebimento global instantâneo, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para matriz cronológica condiciona elegibilidade por local, fase e DR, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
