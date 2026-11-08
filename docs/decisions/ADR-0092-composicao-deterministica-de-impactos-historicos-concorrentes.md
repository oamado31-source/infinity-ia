# ADR-0092 — DEC-097/C: composição determinística de impactos históricos concorrentes, limites e duração

- **Data:** 2026-11-07.
- **Decisão expressamente aprovada:** DEC-097 — alternativa **C**.
- **Fase:** Discovery arquitetural **v9.3**, sem alegação de implantação mecânica no BG2:EE/EEex.
- **Fonte principal:** regras DEC-096/C (ADR-0091, documento técnico 96), que determinam **elegibilidade**; a DEC-097/C governa exclusivamente **composição das repercussões elegíveis**.
- **Decisões preservadas:** todas as DEC-060–096 e os ADR-0001..ADR-0091 inalterados byte a byte em relação ao pacote v9.2; decisões previamente abertas continuam abertas.
- **Contrato técnico:** `docs/97-composicao-deterministica-de-efeitos-historicos-concorrentes-caps-decaimento-e-auditoria.md`.
- **Validação:** 102 testes T097-001..T097-102 **CANDIDATOS E NÃO EXECUTADOS**. Demonstração Python isolada com fixtures **sintéticas**, sem conexão a canon real, mapa, game engine, save, bridge ou host.

## Problema

Na mesma região, tempo e estabelecimento, guerra, peste, rotas mercantis e festivais podem modificar as mesmas variáveis. Substituição pelo último registro torna o resultado dependente da ordem. Somar todos os bônus sem limites superestima consequências, duplica origens e permite ciclos entre efeitos indiretos. A arbitragem livre por LLM inventa intensidade, duração e fatos; aplicar uma alteração no jogo sem recibo host pode gerar dupla aplicação após reload e retrigger.

## Alternativas

- **A — Último efeito vence:** rejeitada; dependência de ordem de avaliação, perda de impactos anteriores, instabilidade na retomada.
- **B — LLM calcula intensidade e precedência:** rejeitada; ausência de determinismo, auditabilidade, garantias de domínio e autoridade mecânica.
- **C — Composição por domínio, políticas versionadas, limites, janelas e decaimento determinísticos, gates, idempotência e auditoria causal:** **APROVADA**.

## Regras vinculantes

1. **Separação de fases:** catálogo histórico canônico -> filtragem temporal/espacial/causal **DEC-096** -> `ImpactCandidate` autorizado -> `EffectCompositionPlan` **DEC-097** -> gates de risco e consentimento -> `ActionGateway`/host receipt -> projeção `AppliedEffectLedger`. Composição pode produzir **apenas uma proposta de estado-alvo**; não muta o motor por si.
2. **Domínios tipados:** por `MetricPolicy` editorial fixada por `ruleset_revision`/`knowledge_pack_hash`: métrica e unidade explícitas (ex.: índice de patrulha, pontos percentuais sobre baseline de preços), baseline válido, operador `BASELINE_PLUS_BPS` ou `ADD_ABSOLUTE`, min/max, resolução de arredondamento, duração e dependências permitidas. A descrição de fonte e a LLM não são unidades.
3. **Matemática reproduzível:** usar ponto fixo inteiros/Decimal (nunca floats binários no contrato), baseline e porcentagens em basis points, soma de deltas elegíveis **antes** de um único arredondamento e clamp final. A política `BASELINE_PLUS_BPS` no exemplo é **aditiva sobre o mesmo baseline**, não multiplicação sequencial. Percentuais compostos só poderão existir com operador novo explicitamente definido, versionado e testado; não presumir que são equivalentes.
4. **Independência de ordem:** seleção por chaves e precedência estáveis, ordenação apenas para ledger e hash. Permutar candidatos não altera resultado nem prioridade. Se houver empate de mesma prioridade numa família exclusiva, bloquear a família conflitante até arbitragem autorizada, nunca usar a última linha.
5. **Proveniência e não duplicidade:** cada `ImpactCandidate` aponta para `CanonEvent`/`ImpactRule`, scope/branch, receipt original, pais e `lineage_root`. `dedup_key` e `stack_family` evitam repetir o mesmo efeito ou somar a mesma causa duas vezes. Agrupamentos correlacionados exigem curadoria; não inferir independência pelo número de fontes (DEC-061/077/089).
6. **Compatibilidade:** famílias explicitamente independentes podem acumular; alternativas do mesmo grupo exclusivo são resolvidas por precedência editorial, com contestação/tie -> `CONFLICTED` e ausência de aplicação da família. Métricas incompatíveis, operadores diferentes, unidades desconhecidas ou ausência de regras => bloquear, sem fallback narrativo.
7. **Caps e orçamento:** política tem limites físicos e econômicos do domínio; efeitos individuais também podem ter teto ou rate limit. Aplicar min/max **após agregação**, preservando componentes e motivo do clamp. `cap` numérica do DEC-096 não autoriza usar uma unidade sem o domínio apropriado. Nenhum cálculo cria moeda, itens, NPC ou equipes extras.
8. **Janelas e decaimento:** início/duração/hold/fade em unidades de **tempo do mundo DEC-022**; `EXACT/MONTH/YEAR_ONLY` da fonte permanecem separadas das janelas editoriais de repercussão. Decaimento explícito, monotônico, limitado e reprodutível; relógio da máquina não avança guerra. Expiração remove a **contribuição calculada**, não desfaz um host receipt nem apaga história, memória, morte ou consequência indireta.
9. **Estados mecânicos:** para projetar um estado efetivo em jogo, apenas efeitos `CONFIRMED` com receipt host validado e epoch corretos podem ser considerados. `PROPOSED`, `DISPATCHED`, `UNCERTAIN`, `REJECTED` não são fatos aplicados; não reemitir comando ao detectar timeout. Um preview de novos candidatos permanece marcado `PROJECTION_ONLY`, não é estado do jogo.
10. **Causalidade dos indiretos:** requer efeito-pai confirmado naquele ramo/epoch, janelas de atraso respeitadas e grafo acíclico. Proibir efeitos que se alimentam retroativamente ou escalem infinitamente. Rumores/NPC knowledge são outro sistema DEC-029/074; uma variável `market_price` alterada não torna o evento conhecido automaticamente.
11. **Conflitos de operações:** efeitos disputando NPCs, patrulhas, ouro, locais ou equipamentos precisam da disponibilidade, reservas DEC-093, deadlocks DEC-094 e compensações DEC-095, além de consentimento PC e host. Política de métrica não substitui gateways mecânicos.
12. **Atualização e migração:** regras e baseline pinados por campanha/ramo/epoch e hash de policy. Revisão/migração DEC-063 gera diff e plano reautorizado, não recalcula retroativamente efeitos já confirmados como se fossem novos fatos; histórico completo e ledger append-only mantidos.
13. **Límites de acesso:** cada consulta pertence a campanha/ramo/ano DR, com ACL DEC-028; efeitos privados, identidades, planos de proteção e segredos não vazam para LLM, indicadores públicos ou outro cliente LAN. Nenhum modelo obtém acesso antecipado ao cânone futuro.
14. **Fail-closed e observabilidade:** ausências de policy, versão, período, contexto, parent receipt, capacidade de jogo, mapeamento regional ou prova de autorização bloqueiam aplicação. Resultado carrega razão, contribuições ordenadas, caps, policy hash, provenance e snapshot de contexto para auditoria sem revelar segredos além da ACL.
15. **Escala:** atualizar por transição de relógio/flag, confirmação de efeito ou entrada em região; índices por ano DR/escopo/métrica; catch-up controlado para DORMANT DEC-021 e orçamento DEC-056, sem reaplicar cada evento a cada frame.
16. **Código/LLM:** engine determinístico decide regras e números. LLM local opcional recebe **apenas contexto autorizado** para produzir narração (“os preços subiram”, “guardas aparecem com mais frequência”), sem alterar resultados matemáticos, bounds, fases ou receipts.
17. **Limite demonstrado:** nenhum aumento real de patrulhas, alteração de preços BG2:EE, criação de encontro ou alteração de scripts foi comprovado. Esquema/fixture/unit tests são exclusivamente protótipos de cálculo sem side effects.

## Exemplo exclusivamente sintético

Preço-base **100** moedas; famílias independentes curadas de guerra `+2000 bp`, transporte `+1500 bp` e festividade `-1000 bp`, todas ativas no mesmo instante e no mesmo escopo: delta total `+2500 bp` e projeção **125**, antes de limites/quantização. Se duas linhas pertencerem à mesma família incompatível, não são automaticamente somadas. Expiração altera projeção; efeito confirmado no motor somente muda se existir ação corretiva/novo ato autorizado e confirmado pelo host.

## Consequências

- **Pró:** invariância da ordem, escala com cronologia, auditoria/explicações, diversidade de efeitos, respeito a atualizações e agência cooperativa.
- **Custo:** exige curadoria de métricas, unidades, caps e famílias; sincronização transacional; provas por build; versionamento de estado e política.
- **Riscos residuais:** dupla contagem de causas indiretas, inflação artificial, tempos imprecisos, divergência host/clientes e custo de recalcular escalas grandes.

## Critérios de aceitação

A arquitetura é aceita agora. Uma SPEC de implementação precisará comprovar: schema/versioning, comparações de permuta e valores extremos, ausência de stacking duplicado, transições de expiração/decay, empates, host+2 clientes, checkpoint/reload, estados `UNCERTAIN`, branches separados, cálculo de economia/combate autorizado, controle de performance e não vazamento de cronologia. Nenhum T097-* foi executado com o jogo.

**Próxima decisão proposta DEC-098:** política de **persistência e materialização de repercussões na entrada/saída de regiões**. A: recalcular e aplicar tudo ao entrar; B: LLM decide manifestações locais; **C recomendada: materialização incremental por snapshots/epochs, com diferença de estado, limites e recibos**, sem duplicar spawns, preços ou NPCs ao reentrar. Ainda em aberto.
