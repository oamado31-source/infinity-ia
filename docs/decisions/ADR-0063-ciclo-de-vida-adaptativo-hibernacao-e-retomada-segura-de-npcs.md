# ADR-0063 — Vida persistente com atividade adaptativa, hibernação e retomada segura de NPCs

- **Decisão:** DEC-068 — **opção C**, aprovada expressamente pelo idealizador em 2026-11-06.
- **Estado:** APROVADA como arquitetura de Discovery **v6.4**; NÃO IMPLEMENTADA, SEM POCs BG2:EE/EEex ou testes multiplayer executados.
- **Documento técnico:** `docs/68-vida-persistente-atividade-adaptativa-e-retomada-de-npcs-fora-de-cena.md`.
- **Preservação integral:** DEC-060 a DEC-067 e ADR-0055 a ADR-0062 continuam vinculantes e não foram modificados.

## Contexto

Um NPC que ganha identidade lógica persistente pela DEC-067 poderá passar anos de campanha longe dos jogadores. Executar IA/LLM, pathfinding e rotinas detalhadas de todos os indivíduos o tempo todo não é viável como pressuposto. Descartar personalidade, vínculos, promessas e experiências quando o personagem sai de cena destruiria a continuidade do Living World. A existência de uma representação narrativa não comprova que a Infinity Engine seja capaz de manter uma instância física persistente em todas as áreas ou de sincronizar transições em multiplayer.

## Opções consideradas

- **A — Simulação individual permanente:** rejeitada como padrão por custo imprevisível e pela falsa pressuposição de NPCs carregados/observáveis continuamente no BG2:EE.
- **B — Retorno à população genérica com descarte de memória:** rejeitada; viola DEC-064/065 e compromissos causais com os jogadores.
- **C — Vida persistente, atividade adaptativa e hibernação operacional:** **APROVADA**; conservar identidade e fatos, modular frequência e detalhe das tarefas conforme relevância/área, retomar sob reconciliação segura.

## Decisão vinculante

1. **Persistência não é execução contínua:** `NPCIdentity` da DEC-066/067, eventos confirmados, vínculos, promessas, estado epistêmico e âncoras protegidas DEC-064/065 sobrevivem a afastamento, modo DORMANT e indisponibilidade computacional. Hibernar significa suspender trabalho ativo, **não apagar fatos**; políticas de privacidade e retenção legítima permanecem aplicáveis.
2. **Níveis de atividade reutilizados, sem um novo relógio:** `ACTIVE`, `NEAR`, `DISTANT` e `DORMANT` vêm da DEC-021. São prioridades de processamento, não prova de que NPC existe fisicamente em área não observada; a classificação é por relevância, localização observada/hipotética, orçamento DEC-056 e estado da campanha.
3. **ACTIVE/NEAR:** efeitos situados em cena dependem de observação válida e de ações confirmadas pelo host; diálogo e decisões podem ser mais detalhados, sem LLM/tick. `NEAR` admite regras e batches limitados.
4. **DISTANT:** avançar somente propostas/eventos narrativos permitidos por regras, em lotes delimitados com `world_time`, versão causal e prioridades. Não inventar encontros presenciais, diálogos detalhados ou estados mecânicos que exigiriam observação.
5. **DORMANT:** manter projeção persistente e watermarks mínimos; não executar ticks por NPC até haver evento elegível, necessidade da campanha ou retomada. Dormência não é morte, deserção, esquecimento, descarte de memória nem transferência de controle.
6. **Política temporal única DEC-022:** respeitar `FROZEN/PARTIAL/REALTIME` e catch-up delimitado; tempo real, espera na fila ou indisponibilidade do host **não** avançam automaticamente o relógio DR. Retomada usa apenas intervalos autorizados e observáveis pela política da campanha; intervalos não processados permanecem pendentes ou resumidos por regras legítimas, nunca como fatos já consumados.
7. **Retomada reconciliada:** antes de reativar, validar `campaign_id`, `branch_id`, `npc_identity`, build/fingerprint, Knowledge Pack fixado, revisão de relógio, checkpoint/epoch, autoridade do host, ACL e evidências de localização quando aplicável. Divergência de quaisquer vínculos críticos => `STALE/UNCERTAIN` e pausa fail-closed.
8. **Eventos com duas etapas:** saída de regras/IA é `PROPOSED`; o registro `CONFIRMED` só existe após política, ação/receipt do host quando mecânica, ou aceite narrativo determinístico autorizado. Propostas nunca implicam morte, gravidez, casamento, nascimento, romance, recrutamento, mudança de quests/facções, desaparecimento ou eventos históricos HIGH como fato irrevogável. Reaplicar pedido incerto automaticamente é proibido.
9. **História causal sem biografias improvisadas:** o processamento fora de cena pode manter consequências documentadas, relações e planos já autorizados. Não gerar retrospectivamente encontros, ofícios, famílias ou trajetórias pessoais não comprovadas apenas para preencher intervalo de anos. Eventos propostos podem ficar pendentes de curadoria/consentimento.
10. **Identidade e população:** estado individual persiste separado do agregado e deve manter reconciliação idempotente DEC-067; nenhum spawn/reaparição do motor é implicitamente garantido. Reconhecer o mesmo NPC exige correspondência verificada DEC-066, inclusive após retorno e save/load; não associar memória por nome/visual.
11. **Cânone e conhecimento por período:** lore continua fisicamente particionado em `knowledge/periods/<ano>-DR/` conforme DEC-060; DEC-061 proveniência, DEC-062 ingestão curada e DEC-063 Knowledge Packs fixados continuam obrigatórios. Memórias NPC vivem em overlays privados por campanha/ramo; um novo fato canônico não ensina NPC dormente automaticamente.
12. **Resiliência, custo e privacidade:** DEC-053/054 checkpoints/backups, DEC-055 health monitor, DEC-056 quotas/fairness, DEC-057–059 nós LAN/model router; trabalhos pendentes são duráveis e idempotentes, resultados stale/fora da ACL não publicam. Segredos não são enviados a workers não autorizados; sem telemetria remota implícita.
13. **Presença física futura é gate técnico:** encontro/ausência em regiões, recrutamento, diálogos e movimentação fora da party dependem de inventário de scripts e POCs read-only → ações offline seguras → host+clientes multiplayer. Não afirmar suporte BG2:EE/EEex nem manipular save/script sem prova.
14. **SPECS pendentes:** thresholds de atividade, políticas detalhadas de retenção, limites de lote, latência tolerada, scheduler, persistência concreta, ativação, UI e critérios de validação têm de ser medidos/testados; não congelar valores arbitrários em Discovery.

## Consequências

- **Benefícios:** personagens mantêm identidade e relações por anos, com custo ajustado à distância/relevância; retomada auditável; respeito ao jogador e ao cânone.
- **Trade-offs:** índices, filas duráveis, marcações de progresso temporal, checagem de divergências, summaries e estados provisórios; risco de backlog e de encontro contraditório com scripts nativos.
- **Falha segura:** falha no motor, identidade, permissão, clock ou checkpoint impede materialização/efeito e mantém registro como pendente/`UNCERTAIN`. Não transformar espera em ação confirmada.
- **Não implica:** simulação física detalhada de toda a cidade, NPC surgindo automaticamente em nova área, save/edit de engine, namoro/casamento/família autogerados, IA acordada continuamente nem efeitos mecânicos offscreen.

## Evidência e verificação futura

- Fonte: escolha expressa **C** pelo idealizador, em 2026-11-06.
- Documento 68 especifica um modelo conceitual, invariantes, contratos candidatos e **36 testes candidatos não executados (`T068-01`–`T068-36`)**.
- DEPENDÊNCIAS: DEC-008/009/011/012/014/021/022/027/028/029/032/034/043/047/049/050/051/052/053/054/055/056/057/058/059 e DEC-060–067. DEC-006/007/013/015/017/018 ainda abertas.

## Próxima decisão proposta

**DEC-069 — Continuidade espacial de NPCs persistentes entre regiões:** **A** localização narrativa flexível sem deslocamento modelado; **B** deslocamento físico minucioso e contínuo em todas as áreas; **C (recomendada)** itinerários e deslocamentos em múltiplas escalas, com tempos, restrições e confirmação do motor antes de aparições, evitando teleporte narrativo e alegações de pathfinding/scripting sem POC.
