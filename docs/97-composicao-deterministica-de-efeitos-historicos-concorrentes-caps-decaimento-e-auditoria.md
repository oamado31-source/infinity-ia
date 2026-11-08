# Documento técnico 97 — Composição de efeitos históricos concorrentes (DEC-097/C)

**Discovery v9.3 | Estado:** arquitetura aprovada; contratos candidatos e ensaios ilustrativos, sem implementação no jogo. **ADR normativo:** ADR-0092. **Prioridade:** preservar todas DEC-060–096 e 91 ADRs anteriores.

## 1. Propósito e fronteiras

A DEC-096 decide quando `CanonEvent`/`ImpactRule` pode produzir `ImpactCandidate` no escopo correto. A DEC-097 somente **compõe os candidatos elegíveis**, por métrica, domínio, duração e provenance. Não reinterpreta canon, não antecipa acontecimentos, não amplia mapeamento geográfico e não escreve estado mecânico. `WorldFact`, `NPCBelief`, `RuleCandidate`, `CompositionProjection`, `HostReceipt` e `AppliedEffectLedger` são entidades diferentes.

## 2. Pipeline

```text
CanonEvent (knowledge/periods/<ANO>-DR, fontes e precisão)
 -> DEC-096 eligibility(time, phase, region, map/tag, branch, known facts)
 -> ImpactCandidate (scope, lineage, origin, parents, period, revision)
 -> DEC-097 group(metric, scope, unit, policy, branch, epoch)
 -> policy validation / conflict resolution / anti-double-count / aging
 -> composed TargetProposal (baseline + deterministic modifiers; cap; trace)
 -> risk / ownership / consent / DEC-093 resource reservations
 -> Action Gateway DEC-012 (typed, allowlisted; HOST is mechanical authority)
 -> CONFIRMED receipt + append-only AppliedEffectLedger
 -> later confirmed indirect effects DEC-074, per-parent and per-delay
```

No dry-run `target` is an **illustrative projection**, never an applied game value. The host may implement a different granularity, not yet established.

## 3. Dados normalizados

| Entidade | Campos mandatórios candidatos | Regra |
|---|---|---|
| `MetricPolicy` | `metric_id`, `domain`, `unit`, `operator`, `baseline`, `min`, `max`, `scale`, `rounding`, `revision`, `policy_hash` | Imutável dentro de uma avaliação; não inferir unidade |
| `ImpactCandidate` | `event_id`, `rule_id`, `effect_id`, `lineage_root_id`, `campaign_id`, `branch_id`, `epoch`, `scope_id`, `metric_id`, `delta`, `start_world_day`, `hold_days`, `fade_days`, `stack_family`, `priority` | Prova de elegibilidade DEC-096, não equivalência com fato aplicado |
| `ContributionEvidence` | `origin`, `parent_effect_ids`, `host_receipt_id`, `status`, `risk`, `provenance_chain`, `available_to_audience` | Pais/citações e permissões; `UNCERTAIN` nunca vira `CONFIRMED` automaticamente |
| `CompositionPolicyVersion` | `policy_set_id`, `revision`, `pack_hash`, `branch_epoch`, `compatibility_groups`, `caps`, `rounding`, `effective_from` | Pin explícito e migração com diff DEC-063 |
| `CompositionTrace` | `included_ids`, `suppressed_ids`, `reasons`, `sum_bp`, `baseline`, `unclamped`, `bounded`, `policy_hash`, `context_hash` | Visão restrita por ACL, auditoria reproduzível |
| `AppliedComposition` | `composition_key`, `target_revision`, `status`, `action_id`, `host_epoch`, `host_receipt_id`, `last_confirmed_target` | Somente após comprovante host; sem aplicação duplicada |

**IDs e epochs:** keys incluem campanha, ramo, epoch de resolução, knowledge-pack hash, policy revision/hash, scope, metric e revision de efeito. `branch_id` jamais é derivado do texto do modelo. Prefixos de arquivo de lore por ano não concedem acesso a segredos de outro período.

## 4. Domínios, operadores e aritmética

- `BASELINE_PLUS_BPS`: `unbounded = baseline + baseline × (Σ(delta_bp × weight_bp ÷ 10000)) ÷ 10000`. BPs são **aditivos na mesma base**, não cadeia de multiplicações. Usar Decimal/ponto fixo. O cálculo de cada contribuição só usa peso determinístico e nenhuma hipótese de taxa econômica real.
- `ADD_ABSOLUTE`: `unbounded = baseline + Σ(delta_in_unit × weight_bp ÷ 10000)` na unidade definida; patamar mínimo/máximo da política determina limites válidos.
- Aplicar `clamp(unbounded, min, max)` **depois da soma e apenas uma quantização** na unidade de exibição/engine. Não permitir `NaN`, float binário em JSON, overflow, divisões por zero, unidade dinâmica/sem enum, ausência de cap ou alteração improvisada do baseline.
- Operadores futuros (`MULTIPLY_RATIOS`, `PRIORITY_OVERRIDE`, `MAX`, `MIN`) **não estão aprovados por implicação**: requerem nova política tipada, versão, testes e análise de ordem. Proibir mistura de operadores na mesma métrica.
- Exemplo sintético `food_price` = 100 +20% +15% -10% = **125**. O fato de uma festa coexistir com guerra não garante que seus efeitos realmente tenham independência causal: exige famílias editoriais independentes. Caso contrário, seleção exclusiva ou conflito bloqueado.
- Precedência *não* supera risco, consentimento, existência de recurso nem recibo host. `higher_priority` só escolhe entre alternativas concorrentes **no mesmo grupo explicitamente exclusivo**. Empates diferentes no topo => `CONFLICTED`, omitindo o grupo até revisão.

## 5. Efeitos relacionados, acúmulo e reversão

- `stack_family`: famílias independentes somam; alternativas duplicadas da mesma família são selecionadas por prioridade ou bloqueadas em empate. Origem e fontes compartilhadas precisam rastreabilidade, para não converter um mesmo fato em 2–3 parcelas econômicas acidentalmente.
- `parent_effect_ids`: efeito indireto só é elegível quando cada pai está `CONFIRMED` e visível no mesmo ramo/epoch. Pais `UNCERTAIN`, `DISPATCHED` ou `REJECTED` bloqueiam. Ciclos no grafo são inválidos. Causas de efeito que se anulam continuam registradas na trilha, não eliminadas do lore.
- Duplicata com mesma key e conteúdo idêntico é suprimida; key repetida com conteúdo diferente é erro de integridade que bloqueia a métrica (não usa a linha mais recente).
- Diferença entre *recalcular target* e *desfazer ação*: expirou bônus de preços -> apenas muda projeção; alteração mecânica atual exige um **novo comando com autorização e receipt**. Não devolver automaticamente moeda/patrulha ou apagar história. Saga DEC-095 pode propor compensação separada se aplicável.

## 6. Janelas e decaimento

Para `elapsed = world_day - start_world_day`:

- `elapsed < 0`: não começou;
- `0 ≤ elapsed < hold_days`: peso `10000` bp;
- `hold_days ≤ elapsed < hold_days + fade_days`: peso linear `(hold_days + fade_days - elapsed) / fade_days`, em bp com arredondamento determinístico;
- depois da janela: `0`. `fade_days=0` expira imediatamente ao final de `hold_days`.

É um **perfil candidato** (linear); nenhum fato de FR impõe sua adoção para toda categoria. Curadoria define `hold/fade` por efeito, não ao sabor da LLM. Eventos sem duração conhecida não podem ser automaticamente agendados para desaparecer. `world_day` será validado pela implementação do calendário de Harptos e do relógio DEC-022 — não pelo relógio do SO. A fase histórica e a data original permanecem preservadas.

## 7. Segurança, autoridade e falhas

1. DEC-096 bloqueia evento fora de data/região/branch; DEC-097 nunca pode reabilitá-lo.
2. Projeções não equivalem a host state. A implementação usará receipts autenticados para reconstruir efeitos confirmados e registrar diffs, sem tratar `SYN-RECEIPT` de fixtures como receipt real.
3. Gate de risco DEC-027 e DEC-041/042 para PCs; DEC-093/094 para recursos; DEC-034 para mudança histórica irreversível. `HIGH` default-deny até autorização explícita.
4. Canais de rumor (DEC-029/074) não recebem automaticamente valores de estado privado; DEC-076/083–090 e ACL DEC-028 aplicam-se a prompts, contexto, auditoria, overlays e LAN.
5. `UNCERTAIN` permanece pendente de reconciliação. Cancelar plano, atualizar ruleset ou expirar janela não apaga efeitos confirmados.
6. Rate limits, amostragem por tick de mundo e cache separado por `campaign_id, branch_id, epoch, pack_hash, policy_revision, metric, region, window` evitam reprocessamento por frame. Cache nunca substitui ledger transacional de idempotência.
7. Se operador, baseline, unidade, parent, intervalo, mapa, fonte, pin de ruleset ou capability for desconhecido, interromper aquele domínio (`FAIL_CLOSED`) preservando outros domínios independentes com evidência.

## 8. Exemplo de JSON e algoritmo de referência

- `examples/chronology/composition_policy_v1.candidate.schema.json`: estrutura de teste tipada, com `additionalProperties: false` e sem campos de engine.
- `examples/chronology/composition_v1.synthetic.json`: 3 contribuições fictícias (guerra, transporte e festa), ambas no mesmo escopo de teste e com IDs/receipts sintéticos.
- `examples/chronology/composer_reference.py`: cálculo puro, determinístico, restrito a fixtures `SYNTHETIC_TEST`, **sem IO/engine** (exceto leitura local de fixture em função de teste).
- `examples/chronology/test_composer_reference.py`: testes unitários do compositor sintético. Não validam o motor de jogo ou o pipeline de receipts reais.

## 9. Exemplo de contrato de execução (a implementar)

```text
compose_preview(campaign, branch, epoch, pack_pin, policy_revision, scope, world_day,
                baseline_snapshot, authorized_candidates)
  -> {status: PROJECTION_ONLY | CONFLICTED | BLOCKED,
      metric_targets: {metric: number},
      included: [...], excluded: [{id, reason}],
      policy_hash, snapshot_hash, arithmetic_trace}

authorize_and_dispatch(plan, consent, capabilities, resource_ledger, host_session)
  -> HOST_ACTION_QUEUED | DENIED

observe_and_reconcile(host_receipt, action_id, epoch)
  -> CONFIRMED | REJECTED | UNCERTAIN
```

Sem suporte validado no engine, a segunda e terceira funções não podem ser implementadas mediante suposições sobre Lua/EEex.

## 10. Matriz de testes candidatos — 102 testes NÃO EXECUTADOS

**Todos os T097-001..T097-102 abaixo são testes de integração/aceitação propostos, com status `NÃO EXECUTADO`.** Testes de unitários Python para fixtures sintéticas são um conjunto **separado**; não promovem estes testes a `PASS`.

### Políticas e domínios

- **T097-001 — NÃO EXECUTADO:** policy exige ID/revision/hash.
- **T097-002 — NÃO EXECUTADO:** policy vincula unidade explícita.
- **T097-003 — NÃO EXECUTADO:** operador desconhecido bloqueia.
- **T097-004 — NÃO EXECUTADO:** métrica sem policy falha fechado.
- **T097-005 — NÃO EXECUTADO:** baseline ausente bloqueia.
- **T097-006 — NÃO EXECUTADO:** limite inferior obrigatório.
- **T097-007 — NÃO EXECUTADO:** limite superior obrigatório.
- **T097-008 — NÃO EXECUTADO:** min maior que max é rejeitado.
- **T097-009 — NÃO EXECUTADO:** número decimal não declarado é rejeitado.
- **T097-010 — NÃO EXECUTADO:** política divergente em cliente não aplica.

### Aritmética e invariância

- **T097-011 — NÃO EXECUTADO:** três percentuais aditivos produzem 125 sobre base 100.
- **T097-012 — NÃO EXECUTADO:** ordem ABC equivale a CBA.
- **T097-013 — NÃO EXECUTADO:** duplicação exata não altera total.
- **T097-014 — NÃO EXECUTADO:** resultado usa ponto fixo.
- **T097-015 — NÃO EXECUTADO:** negativos respeitam sinal.
- **T097-016 — NÃO EXECUTADO:** rounding ocorre uma vez.
- **T097-017 — NÃO EXECUTADO:** cap superior aplicado ao agregado.
- **T097-018 — NÃO EXECUTADO:** cap inferior aplicado ao agregado.
- **T097-019 — NÃO EXECUTADO:** efeito zero não cria novo fato.
- **T097-020 — NÃO EXECUTADO:** soma de percentuais não implica capitalização composta.

### Famílias e precedência

- **T097-021 — NÃO EXECUTADO:** origens independentes combinam.
- **T097-022 — NÃO EXECUTADO:** mesma família exclusiva seleciona prioridade maior.
- **T097-023 — NÃO EXECUTADO:** empate de prioridade bloqueia família.
- **T097-024 — NÃO EXECUTADO:** maior prioridade não ignora ACL.
- **T097-025 — NÃO EXECUTADO:** grupos de conflito separados coexistem.
- **T097-026 — NÃO EXECUTADO:** mesma origem não empilha inadvertidamente.
- **T097-027 — NÃO EXECUTADO:** métrica diferente não contamina a outra.
- **T097-028 — NÃO EXECUTADO:** incompatibilidade de unidade é bloqueada.
- **T097-029 — NÃO EXECUTADO:** supressão de origem reverte projeção apenas.
- **T097-030 — NÃO EXECUTADO:** contrato de precedência muda só após revisão.

### Tempo e decaimento

- **T097-031 — NÃO EXECUTADO:** efeito futuro não entra no cálculo.
- **T097-032 — NÃO EXECUTADO:** hold mantém efeito integral.
- **T097-033 — NÃO EXECUTADO:** fade reduz proporcionalmente.
- **T097-034 — NÃO EXECUTADO:** fade termina no mundo, não no SO.
- **T097-035 — NÃO EXECUTADO:** fade de delta negativo converge a zero.
- **T097-036 — NÃO EXECUTADO:** revisão do relógio não duplica aplicação.
- **T097-037 — NÃO EXECUTADO:** FROZEN mantém contribuição.
- **T097-038 — NÃO EXECUTADO:** mudança de ano DR respeita novas regras.
- **T097-039 — NÃO EXECUTADO:** YEAR_ONLY não inventa mês para ativação.
- **T097-040 — NÃO EXECUTADO:** evento legado usa baseline curado.

### Causalidade e dependências

- **T097-041 — NÃO EXECUTADO:** indireto exige pai CONFIRMED.
- **T097-042 — NÃO EXECUTADO:** pai UNCERTAIN bloqueia indireto.
- **T097-043 — NÃO EXECUTADO:** pai em ramo distinto não vale.
- **T097-044 — NÃO EXECUTADO:** ciclo parent-child é rejeitado.
- **T097-045 — NÃO EXECUTADO:** DAG de repercussões não gera loops.
- **T097-046 — NÃO EXECUTADO:** rumor não é fato confirmado.
- **T097-047 — NÃO EXECUTADO:** repetição de relato não duplica origem.
- **T097-048 — NÃO EXECUTADO:** guerra regional não impacta local excluído.
- **T097-049 — NÃO EXECUTADO:** mudança canônica N3 suprime regra incompatível.
- **T097-050 — NÃO EXECUTADO:** efeito HIGH não dispensa gate.

### Host e idempotência

- **T097-051 — NÃO EXECUTADO:** preview não despacha.
- **T097-052 — NÃO EXECUTADO:** PROPOSED não conta como receipt.
- **T097-053 — NÃO EXECUTADO:** DISPATCHED não conta como sucesso.
- **T097-054 — NÃO EXECUTADO:** UNCERTAIN não gera retries cegos.
- **T097-055 — NÃO EXECUTADO:** CONFIRMED sem receipt válido é rejeitado.
- **T097-056 — NÃO EXECUTADO:** receipt de outro epoch é rejeitado.
- **T097-057 — NÃO EXECUTADO:** mesma chave não gera duas aplicações.
- **T097-058 — NÃO EXECUTADO:** replay do save não reemite item aplicado.
- **T097-059 — NÃO EXECUTADO:** resync host+2 clientes preserva alvo.
- **T097-060 — NÃO EXECUTADO:** compensação posterior é novo evento.

### Recursos e economia

- **T097-061 — NÃO EXECUTADO:** cap de preços não cria moeda.
- **T097-062 — NÃO EXECUTADO:** modificador de mercado respeita min.
- **T097-063 — NÃO EXECUTADO:** patrulha requer NPC e disponibilidade.
- **T097-064 — NÃO EXECUTADO:** falta de recursos bloqueia materialização.
- **T097-065 — NÃO EXECUTADO:** reserva pendente não é consumo.
- **T097-066 — NÃO EXECUTADO:** patrulha não reaparece após reentrada.
- **T097-067 — NÃO EXECUTADO:** efeitos de guerra não forçam mortes.
- **T097-068 — NÃO EXECUTADO:** efeito econômico de guerra não vira boato global.
- **T097-069 — NÃO EXECUTADO:** ajuste de facção não muda titularidade de itens.
- **T097-070 — NÃO EXECUTADO:** operação concorrente não duplica agente.

### Segurança e conhecimento

- **T097-071 — NÃO EXECUTADO:** cache isolado por campanha.
- **T097-072 — NÃO EXECUTADO:** cache isolado por branch.
- **T097-073 — NÃO EXECUTADO:** cache isolado por ruleset revision.
- **T097-074 — NÃO EXECUTADO:** knowledge pack pin verificado.
- **T097-075 — NÃO EXECUTADO:** evento futuro não aparece na LLM.
- **T097-076 — NÃO EXECUTADO:** identidade protegida não vaza em log.
- **T097-077 — NÃO EXECUTADO:** ACL filtra explicação do agregado.
- **T097-078 — NÃO EXECUTADO:** segredo de outro grupo não vaza.
- **T097-079 — NÃO EXECUTADO:** LLM offline mantém cálculo.
- **T097-080 — NÃO EXECUTADO:** LLM não troca prioridade matemática.

### Performance e retomada

- **T097-081 — NÃO EXECUTADO:** índice por ano reduz busca.
- **T097-082 — NÃO EXECUTADO:** índice por métrica reduz agregação.
- **T097-083 — NÃO EXECUTADO:** recálculo por evento e não por frame.
- **T097-084 — NÃO EXECUTADO:** DORMANT usa catch-up limitado.
- **T097-085 — NÃO EXECUTADO:** cache invalida após receipt.
- **T097-086 — NÃO EXECUTADO:** rollback restaura snapshot consistente.
- **T097-087 — NÃO EXECUTADO:** erro de policy não bloqueia outras métricas independentes.
- **T097-088 — NÃO EXECUTADO:** auditoria preserva componentes suprimidos.
- **T097-089 — NÃO EXECUTADO:** ledger usa ordenação estável.
- **T097-090 — NÃO EXECUTADO:** orçamento evita explosão combinatória.

### Aceitação end-to-end

- **T097-091 — NÃO EXECUTADO:** build fingerprints conferidos.
- **T097-092 — NÃO EXECUTADO:** host+2 clientes fazem cálculo idêntico.
- **T097-093 — NÃO EXECUTADO:** eeex bridge limita comandos a allowlist.
- **T097-094 — NÃO EXECUTADO:** mapeamento real de áreas foi testado.
- **T097-095 — NÃO EXECUTADO:** não há alteração de inventário sem receipt.
- **T097-096 — NÃO EXECUTADO:** não há alteração de script sem recibo.
- **T097-097 — NÃO EXECUTADO:** política por mod/version preservada.
- **T097-098 — NÃO EXECUTADO:** testes comparativos com cronologia curada.
- **T097-099 — NÃO EXECUTADO:** migração versionada sem efeitos retroativos.
- **T097-100 — NÃO EXECUTADO:** falha de LAN preserva estado incerto.

### Convergência final

- **T097-101 — NÃO EXECUTADO:** reentrada após carregamento não duplica efeitos.
- **T097-102 — NÃO EXECUTADO:** uma fonte DISPUTED permanece isolada.

## 11. Provas requeridas para implementação

Validar (i) fontes reais e janela DR/Harptos; (ii) família causal e política de stacking por domínio, editorialmente; (iii) compatibilidade de efeito com BG2:EE/EEex em fingerprint de build; (iv) host+2 clientes, Action Gateway, save/reload, epoch, UNCERTAIN; (v) benchmarks de carga e cache; (vi) ACL de narrativas e LAN; (vii) comparações independentes de sequenciamento, quantização e decaimento. Nada aqui autoriza mover NPCs, atualizar preço real ou criar eventos sem esses gates.

## 12. Proposta para DEC-098 — aberta

**Tema:** snapshots e materialização de repercussões derivadas da cronologia ao entrar ou sair de uma região, após dormir/hibernar regiões e restaurar saves. **A:** reaplicar todas as regras ao entrar; **B:** LLM decide o que existe ao carregar; **C (recomendada):** snapshots versionados de estado local + materialização incremental por delta com epoch, ownership, cap, receipts, no duplicate spawn/price, rollback seguro e catch-up limitado. DEC-098 **não está aprovada** nesta atualização.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Target DEC-097 é projeção: DEC-098 compara com último target confirmado por host e não repete percentuais/ações após reentrada.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Impactos agregados não autorizam writes diretos sobre estado de scripts/quests/mods.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Compositor de efeitos não transforma leituras técnicas em impactos confirmados sem host receipt.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Semantic quest milestones are curated technical metadata, separate from FR historical canon partitioned by year DR and private campaign overlays. UNKNOWN, AMBIGUOUS or stale milestones cannot trigger chronology, historical effect or materialization; lore packs do not authorize interpreting runtime flags. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

DEC-102 não altera parâmetros compostos em silêncio, nem recalcula fatos já confirmados sem evento legítimo. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** marcos confirmados de quests originais são **origens candidatas** de regras históricas/regionais, não fatos canônicos escritos em `knowledge/periods/<ANO>-DR/`. A admissão exige prova reconciliada DEC-100/101/102, clock DR e branch adequados; a matriz DEC-096 filtra local, fase e precondições e DEC-097 compõe impactos. Escopo global não dá conhecimento universal. Evento proposto, evento host-confirmed e rumor entregue são distintos; nenhum efeito mecânico sem Action Gateway/receipt. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **contribuições contestadas e efeitos multicausais**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para composição de impactos e crenças de NPCs não são o mesmo domínio, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para efeitos múltiplos e seus limites não restauram reputação automaticamente, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Composição de efeitos econômicos não entrega automaticamente recursos pactuados. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Compositor de efeitos econômicos não define cláusulas nem disponibilidade real. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
