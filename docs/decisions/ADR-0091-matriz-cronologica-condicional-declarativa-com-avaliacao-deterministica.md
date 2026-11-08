# ADR-0091 — DEC-096/C: matriz cronológica condicional declarativa, causal e determinística

- **Data:** 2026-11-07.
- **Decisão expressa do idealizador:** **DEC-096, alternativa C — APROVADA COMO ARQUITETURA**.
- **Versão:** Infinity AI Discovery **v9.2**.
- **Escopo:** Forgotten Realms Living World, cronologia DR / calendário de Harptos, BG2:EE/EEex coop privado local-first; futura integração sujeita a prova.
- **Dependências preservadas:** DEC-004/008/009/011/012/021–034/041/045/051–059/060–074/076/077/083–095.
- **Compatibilidade:** DEC-060–095 continuam válidas; ADR-0001..ADR-0090 **idênticos byte a byte** ao pacote v9.1; decisões pendentes anteriores continuam pendentes.
- **Especificação normativa candidata:** `docs/96-matriz-cronologica-condicional-arquitetura-aprovada-e-contratos-do-motor.md` e proposta original datada `docs/96-proposta-matriz-cronologica-condicional-de-eventos-e-repercussoes.md`.
- **Validação:** testes de referência com dados **sintéticos apenas**. Provas end-to-end de engine, multiplayer e lore real **NÃO EXECUTADAS**. Matriz de 100 testes T096-001..T096-100 **NÃO EXECUTADOS**.

## Problema

A cronologia de Forgotten Realms contém fatos com datas exatas, períodos aproximados e versões em disputa. Mostrar em outra época uma revolta, uma guerra, um governante ainda vivo ou seus efeitos locais quebra a continuidade. Entretanto, não basta filtrar por ano: mês, fase histórica, escala geográfica, tipo de estabelecimento, disponibilidade de recursos, consequência verificada, divergências dos PCs e canais de notícias podem alterar os efeitos. Uma LLM que lê todas as épocas ou um conjunto de `IF/ELSE` espalhados pelo código aumenta anacronismos, spoilers, bugs e falta de auditabilidade.

## Alternativas avaliadas

- **A — `IF/ELSE` codificado por evento**: rejeitada como modelo principal. Difícil escalar, versionar, auditar e testar; condicional espalhada permite impactos globais incorretos. Condicionais internas do avaliador continuam normais, mas **não** são lógica de lore hardcoded.
- **B — LLM interpreta e aplica eventos**: rejeitada. Modelo não é juiz de canon, calendário, presença mecânica, fatos históricos ou efeitos host-confirmed; risco de spoilers e onisciência.
- **C — Catálogo histórico curado + matriz declarativa + avaliador determinístico + ledger causal**: **APROVADA**, código primeiro, LLM apenas para refinamento textual autorizado.

## Decisão vinculante

1. **Três camadas separadas:** (i) `CanonEvent` curado, fisicamente particionado em `knowledge/periods/<ANO>-DR/`, sujeito a proveniência DEC-061/062 e Knowledge Pack pinado DEC-063; (ii) `ImpactRule`/`HistoricalRuleSet` versionados, com DSL tipada e declarativa; (iii) `CampaignHistoricalState` e `AppliedImpact` privados por campanha/ramo e epoch. Nenhum evento da fonte altera automaticamente o mundo.
2. **Planilha como interface de curadoria:** campos editáveis de evento, mês, abrangência, locais afetados, impactos diretos/indiretos, dependências, duração, riscos e origem; exportação/normalização em entidades validadas. Não executar `eval`/Python/JS/SQL ou texto livre recebido pela LLM.
3. **Tempo sem falsificação:** `EXACT_DAY`, `MONTH`, `YEAR_ONLY`, `INTERVAL`, `DISPUTED`, `UNKNOWN`; calendários DR e Harptos (12 meses/feriados intercalares) com representação própria. `YEAR_ONLY` **não vira primeiro mês**; disputa não é resolvida por LLM. Precisão de fonte e janela de materialização são campos diferentes. Um legado de ano anterior requer baseline curado, não repetição do acontecimento.
4. **Fase e abrangência independentes:** pré-evento, ocorrência, pós-evento e repercussão legada são fases com janelas autorizadas. `GLOBAL` descreve abrangência histórica, **não** autoriza efeitos em todos os mapas ou notícia instantânea. Scopes têm IDs canônicos de região/local, tags de lugar e mapeamento para assets reais validado por build; desconhecido = fail-closed para efeitos mecânicos.
5. **DSL controlada:** `all/any/not`, comparadores tipados e campos allowlisted com limite de profundidade, custo e tamanho; negar campos, operadores, branches ou valores desconhecidos. Condições consultam fatos confirmados, não texto narrativo nem segredos de outro ramo.
6. **Cadeia de efeitos:** fato histórico elegível -> candidato de impacto direto -> gate de risco/consentimento/capability -> `HostReceipt` para efeito mecânico -> `AppliedImpact` confirmado -> eventual impacto indireto que dependa explicitamente desse pai. A LLM não produz confirmações, spawns, ouro, multas, mortes, combates, mudanças políticas ou alterações de NPCs.
7. **Causalidade multiplayer:** mundo `FROZEN/PARTIAL/REALTIME` DEC-022, autoridade host DEC-011/012, interação PC DEC-041/042, ações de NPC offscreen DEC-068–073, decisões de arco DEC-024–026 e DEC-034. Impacto histórico pode justificar hipótese ou proposta, não forçar destino irreversível de personagens.
8. **Estado e idempotência:** chave estável por `campaign_id + branch_id + resolution_epoch + knowledge_pack_hash + ruleset_revision + event_id + rule_id + phase + scope_id + effect_id`; outbox/ledger e ações `PENDING/PROPOSED/AUTHORIZED/DISPATCHED/UNCERTAIN/CONFIRMED/REJECTED/SUPPRESSED`. Runtime deve usar CAS/unique constraint transacional quando implementado, não um `set` Python em memória.
9. **Níveis de certeza:** fontes conflitantes são `DISPUTED`, datas desconhecidas e período incompleto bloqueiam inferência de ativação exata; pode haver baseline de estado pós-evento se **separadamente** curado e autorizado. Lore do futuro não é consultável por NPC fora da política de informação/presságio legitimamente aprovada.
10. **Exceções e divergência:** quando jogador altera causalmente um arco, impactos canônicos incompatíveis tornam-se `SUPPRESSED/DIVERGED` no overlay desse ramo; nunca reescrever fonte canônica ou silenciosamente apagar efeitos confirmados. Mudança de pack ou ruleset exige diff, revisão e migração DEC-063.
11. **Conhecimento não é ocorrência:** `KnowledgeAcquisition` separado de `CanonEvent`, de `ImpactRule` e de `AppliedImpact`. NPC recebe rumores e notícias por canais temporais/geográficos DEC-029/074 com ACL, proveniência, recepção e atraso; evento `GLOBAL` não produz NPC onisciente.
12. **Efeitos concorrentes:** políticas de composição por domínio com escopo, precedência documentada, `caps`, decaimento, incompatibilidade, resolução e deduplicação; sem loops autorreforçados ou stacking ilimitado. DEC-097 discutirá detalhamento destas políticas, sem deixar a LLM arbitrar.
13. **Desempenho e sono:** compilar índices por ano/janela/fase, região, tags e dependências; reavaliar por transição do relógio do mundo, entrada em região, confirmação de fato ou revisão de estado. Sem fazer varredura a cada frame. Zonas DORMANT recebem catch-up limitado e auditável, sem materializar NPCs instantaneamente.
14. **Falhas seguras:** se KPack, precisão, mapeamento espacial, parent receipt, host session, dados de condições ou build capability estiver ausente/ambiguamente definido, não aplicar. Falhas e `UNCERTAIN` exigem reconciliação, sem reaplicação após reload/rollback.
15. **Isolamento e segredos:** consultas/caches físicos limitados ao ano/ramo/pin; as regras não podem vazar refúgios/identidades e dossiês protegidos DEC-076/083–090. Logs por audiência e capacidade, observabilidade sem quebrar ACL.
16. **LLM restrita:** usa somente pacote contextual pós-filtragem para produzir rumor/diálogo/descrição opcional; não pode selecionar verdade histórica, inventar data, fazer downgrade de risco, alterar `rule`, `scope`, `receipt`, `event_id` ou aplicar efeitos. Desligada, o código continua funcional.
17. **Curadoria e testes:** auditoria das 12 linhas preliminares da matriz `docs/14-matriz-eventos-excecoes-repercussoes.md` antes de importação. As datas/lore daquele levantamento **não** são automaticamente publicadas como fatos executáveis. `examples/chronology/` permanece exclusivamente sintético e não integrado ao motor.
18. **Aprovação não equivale a POC:** todas as SPECS e acoplamentos (conversão de calendário, IDs de mapas, templates, consumo de recursos, persistência de alto desempenho, API EEex) devem ser testados em build fixada e multiplayer host+2 clientes. DEC-006/007/013/015/017/018 mantêm-se abertas.

## Exemplo de comportamento

Um evento histórico com ano DR mas mês **não informado** é elegível como fonte para um `HistoricalBaseline` de estado legado **se** houver regra de estado aprovada; não dispara uma batalha em um mês escolhido arbitrariamente. Uma fase com mês e geografia confirmados pode propor, numa estrada mapeada, uma alteração limitada de patrulhas. Apenas efeito direto confirmado com recibo permite propor efeito indireto de mudança de risco. Rumor só chega à taverna após canal de transmissão legítimo. Uma divergência autorizada da campanha pode bloquear fases canônicas seguintes nesse ramo, mantendo o catálogo original intacto.

## Consequências e custos

- **Benefícios:** consistência temporal/espacial, baixo custo de runtime, testabilidade, explicabilidade das regras, migrações versionadas e identidade causal dos efeitos.
- **Custos:** curadoria de fontes/calen­dário, catálogo normalizado, versão de ruleset, IDs geográficos por build, design de DSL e políticas de risco, adaptadores host e ledger idempotente.
- **Não coberto:** validar cronologias FR específicas, provar comportamento de EEex/BG2:EE, publicar regras de impacto reais, decidir agregação detalhada dos modificadores concorrentes.

## Próxima DEC-097 — regras de composição de impactos simultâneos

**Questão:** quando guerra, epidemia, festividade e crise comercial afetam o mesmo mercado, como combinar duração, prioridades, incompatibilidades e efeitos cumulativos?

- **A:** último efeito aplicado prevalece.
- **B:** LLM decide valores e prioridades.
- **C recomendada:** políticas determinísticas e versionadas de agregação por domínio, caps, precedência, não-comutatividade explícita, expiração/decaimento e reconciliação; decisões de alto risco continuam com o host.

**Status:** DEC-096/C **APROVADA**, DEC-097 **EM ABERTO**.
