# ADR-0064 — Deslocamentos hierárquicos de NPCs, restrições geográficas e presença confirmada

- **Decisão:** DEC-069 — **opção C**, aprovada expressamente pelo idealizador em 2026-11-06.
- **Estado:** APROVADA como política arquitetural no **Discovery v6.5**; **NÃO IMPLEMENTADA**, sem testes de movimentação offscreen, EEex/BG2:EE, EET ou multiplayer executados.
- **Documento técnico:** `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.
- **Preservação integral:** DEC-060 a DEC-068; ADR-0055 a ADR-0063 são imutáveis e preservados byte a byte nesta versão.

## Contexto e problema

NPCs individualizados DEC-066/067/068 podem deixar Athkatla, viajar para Baldur's Gate e ser reencontrados no futuro. Uma simples alteração narrativa de localização poderia teleportá-los, torná-los simultaneamente presentes em duas regiões ou inventar acesso a áreas inexistentes na instalação. Simular cada passo individual em mapas não carregados, por sua vez, seria custoso e pressuporia recursos não comprovados no BG2:EE/EEex. Localização narrativa e observação mecânica devem permanecer distinguíveis.

## Opções deliberadas

- **A — Localização flexível por conveniência da narrativa:** não aprovada; cria deslocamentos instantâneos e inconsistências de tempo/geografia.
- **B — Pathfinding físico contínuo em todas as regiões:** não aprovada; custos e pressupostos inviáveis sem POC, inclusive para regiões não existentes no build.
- **C — Viagens hierárquicas com itinerário, duração, restrições e presença verificada:** **APROVADA**.

## Resolução vinculante

1. **Itinerário explícito:** criar planos versionados por campanha/ramo e identidade verificada `NPCIdentity` contendo origem, destino, sequência de segmentos quando disponíveis, meio de deslocamento, janela temporal estimada, fonte do traçado, riscos e políticas aplicáveis. Trechos/rotas sem evidência curada são `UNKNOWN/UNROUTABLE`; não inventar conexão ou tempo certo.
2. **Topologia geográfica curada:** utilizar grafo regional com procedência, ano DR e vigência, vinculado à revisão anual do Knowledge Pack DEC-060–063. Distinguir `lore_region` de `engine_area`; o fato de um local existir no cânone **não** garante que possua área carregável no BG2:EE/EET ou em mods.
3. **Trajetória multidetalhe:** `ACTIVE` usa observações de motor quando disponíveis; `NEAR` admite segmentos/regiões e verificações adicionais; `DISTANT` processa etapas de roteiro por lotes/eventos; `DORMANT` preserva plano, cursores e pendências sem simulação física ativa. Compatível com DEC-021/068 e Resource & Performance Director DEC-056.
4. **Estados distintos:** planejamento, partida proposta, trânsito narrativo validado, interrupção, chegada narrativa validada e presença mecânica observada são fatos diferentes. `ARRIVED_NARRATIVE` não implica `ENGINE_PRESENT`; `ENGINE_PRESENT` só é confirmado por observação do host vinculada a identidade/área/checkpoint/build. Nunca usar presença narrativa como comando de spawn.
5. **Tempo causal controlado:** janelas e duração dependem do relógio `FROZEN/PARTIAL/REALTIME` DEC-022, de deslocamentos plausíveis e eventos efetivamente confirmados. O simples transcurso de tempo real ou a espera em fila não avança o calendário DR. Não preencher intervalos desconhecidos como viagens consumadas nem ultrapassar limites de catch-up.
6. **Restrições e rotas dinâmicas:** disponibilidade de estrada/porto, passagens, fronteiras, guerras, clima, transporte, custo e relações com facções podem limitar um trecho quando forem sustentados por evidências/eventos confirmados. Mudanças podem tornar viagem `BLOCKED`/`PAUSED`, exigindo replanejamento autorizado; não recalcular silenciosamente destinos ou durações como certeza histórica.
7. **Origem verificada e não onipresença:** saída física de área é confirmada apenas quando o motor/host fornece prova suficiente; fora de cena pode existir estado narrativo condicional, explicitamente marcado como não observado. Um mesmo NPC não pode aparecer com duas localizações físicas confirmadas incompatíveis no mesmo intervalo causal.
8. **Checkpoints e idempotência:** plano, etapas, revisões de rota, condições, progresso temporal e recibos formam eventos auditáveis vinculados a `campaign_id`, `branch_id`, `npc_identity_id`, `checkpoint_id`, `world_clock_revision`, `build_fingerprint`, `knowledge_pack_revision`, `route_graph_revision` e `idempotency_key`; replays/retornos não duplicam viagens ou localizações.
9. **Falha segura:** `STALE/UNCERTAIN/AMBIGUOUS`, identidade não comprovada, perda de ACL, mod/build incompatível, rota não curada ou conflito com scripts nativos impedem promoção de proposta a fato confirmado e bloqueiam materialização. Recorrência automática de ação mecânica incerta é proibida.
10. **Sem consequências irreversíveis automáticas:** assaltos, ferimentos, mortes, casamentos, prisão, pilhagem, alterações de quests/romances, guerras ou mudanças econômicas exigem as respectivas políticas de risco, provas, consentimentos e confirmações DEC-011/012/027/034/050; itinerário não equivale a um gerador de eventos HIGH.
11. **Dados e conhecimento:** consulta primária ao `knowledge/periods/<ano>-DR/` conforme DEC-060, com proveniência DEC-061, ingestão DEC-062 e versionamento DEC-063. Mapas/rotas canônicos não recebem memórias privadas; planos individuais ficam no overlay da campanha/ramo, sujeitos a ACL, segregação e proteção de segredos DEC-028/057–059.
12. **Agregado versus individual:** uma viagem de NPC promovido DEC-067 não pode manter duplicata simultânea como indivíduo e integrante da população agregada. Movimentação de ex-companheiros DEC-049 respeita identidade, scripts nativos e recrutamento somente se comprovado.
13. **Sincronização multiplayer e compatibilidade:** host BG2:EE tem autoridade mecânica; workers, roteadores LLM e planejadores fornecem propostas, não criam personagens em clientes. Exigir POCs read-only e depois ações offline controladas antes de qualquer teste de materialização host + dois clientes; se falhar, fornecer apenas narrativa limitada, sem alegar encontro físico funcional.
14. **Escopo posterior:** geodados, nós e arestas, critérios de confiança, velocidades, latências, budgets, política de replanejamento, modalidades e fallback são parâmetros a definir nas SPECS/POCs, sem assumir que tempos/distâncias/funções da engine já foram medidos.

## Consequências

- **Benefícios:** continuidade espacial, tempo plausível, encontros não teletransportados, economia/facções afetando rotas sob evidências, desempenho escalável e rastreabilidade causal.
- **Custos:** grafo temporal com proveniência, itinerários versionados, reconciliação de presença, UI para pendências e testes de save/load, scripts e multiplayer.
- **Regra de honestidade técnica:** apresentar todas as rotas e movimentos como hipóteses até curadoria e POCs; não inventar geografia, distâncias, velocidades ou capacidade nativa de viajar fora do mapa.
- **Critério de segurança:** na incerteza, manter `PLANNED/PAUSED/UNCERTAIN`, não afirmar chegada ou aparição.

## Evidências e validação

- Evidência: escolha expressa **C** do idealizador, em 2026-11-06, preservando DEC-060–068.
- Documento 69 especifica **40 testes candidatos (`T069-01` a `T069-40`) NÃO EXECUTADOS**.
- Dependências: DEC-003/008/009/011/012/013/015/021/022/027/028/029/030/031/032/033/034/049/050/051/052/053/054/055/056/057/058/059/060–068. DEC-006/007/013/015/017/018 permanecem abertas.

## Próxima decisão proposta

**DEC-070 — Política de imprevistos, encontros e riscos durante viagens offscreen:** **A** viagens sem eventos intermediários; **B** simulação irrestrita que resolve acontecimentos automaticamente; **C (recomendada)** eventos de estrada por risco, com conflitos propostos/validados, resolução automática somente para consequências LOW curadas, e consentimento/gates para impactos MEDIUM/HIGH e ações mecânicas.
