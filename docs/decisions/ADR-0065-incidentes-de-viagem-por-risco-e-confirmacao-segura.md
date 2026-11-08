# ADR-0065 — Incidentes de viagem por classe de risco e resolução segura

- **Decisão:** DEC-070 — **opção C**, aprovada expressamente pelo idealizador em 2026-11-06.
- **Estado:** **APROVADA como arquitetura no Discovery v6.6**, ainda **NÃO IMPLEMENTADA**, sem POCs BG2:EE/EEex/multiplayer e sem resultados de testes.
- **Detalhamento:** `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md` (**44 testes candidatos, nenhum executado**).
- **Integridade:** DEC-060 a DEC-069 preservadas integralmente; ADR-0055 a ADR-0064 não são modificados.

## Contexto

A DEC-069/C permite planejar e validar itinerários de NPCs persistentes fora de cena. Uma viagem pode ser afetada por rumores, encontros sociais, clima documentado, bloqueios reais e perigos regionais. Entretanto, uma narrativa gerada por IA não constitui evidência de luta, saque, morte, ferimento, perda de inventário, resultado mecânico ou alteração de quest. Simular todos os perigos de modo autoritativo fora do BG2:EE violaria DEC-011/012/027/034/050; proibir todo acontecimento reduziria a proposta Living World. A política deve conciliar plausibilidade, risco, direitos dos jogadores, orçamento e consistência causal.

## Alternativas

- **A — Sem acontecimentos intermediários:** rejeitada por reduzir a persistência do mundo a uma lista de chegadas.
- **B — IA/regras resolvem tudo automaticamente:** rejeitada por permitir efeitos irreversíveis, mecânicos ou canônicos sem autorização nem confirmação.
- **C — Propor incidentes com risco, evidências, gates e confirmação apropriada:** **APROVADA**.

## Decisão vinculante

1. **Incidentes são propostas até validação:** `TravelIncident` referencia `campaign_id`, `branch_id`, `NPCIdentity` verificada, `itinerary_id`, `segment_id`, `world_time`, `checkpoint_epoch`, revisão do Knowledge Pack e fontes. Não inferir incidente só porque uma rota é perigosa; perigo contextual não equivale a ataque confirmado.
2. **Origem rastreável e conhecimento segregado:** candidatos podem nascer de regras regionais/DEC-005-E, eventos de facções, fatos confirmados, encontros sociais ou sugestão de LLM. O LLM não é árbitro, não tem autoridade de alterar estado; rumor permanece rumor, não bloqueio comprovado ou evento objetivo.
3. **Classificação pelo IMPACTO agregado, não pelo tom:** reutilizar `LOW/MEDIUM/HIGH` de DEC-027, com classificação anterior à execução. Encadeamentos de mudanças LOW que produzam efeito MEDIUM/HIGH herdam risco mais alto; proibir reclassificação por prompt, fragmentação ou fuga entre camadas.
4. **LOW autorizável por allowlist:** uma interação social sem efeito mecânico/irreversível pode ser aplicada como **fato narrativo restrito**, somente se validada, prevista em regra explícita, idempotente, dentro da quota e com evidência/contexto suficientes. Nenhum LOW concede itens, XP, ferimentos, modificações de saves ou resultados de combate.
5. **MEDIUM com avaliação contextual e autorização correspondente:** obstruções, atrasos, relações, custos e mudanças relevantes exigem confirmação factual e a política de autorização do seu efeito. Não publicar consequências persistentes até satisfazer o gate específico; na dúvida, pausar ou oferecer alternativas não autoritativas.
6. **HIGH fail-closed:** morte/permadeath, aprisionamento, saque irreversível, grandes perdas, alteração de quest/romance/reputação mecânica, eventos canônicos e resultados de combate são propostas bloqueadas até autorização especial, evidência mecânica quando necessária e confirmação host. Ausência de resposta ≠ consentimento.
7. **Nenhum combate mecânico offscreen presumido:** perigo, emboscada ou confronto proposto não é combate efetivamente processado no BG2:EE; sem mecanismo validado não há `HP`, equipamento, XP, loot, vitória/derrota ou desaparecimento físico. DEC-005-E não autoriza resolver esses efeitos fora da engine.
8. **Distinção narrativa/mecânica:** validação do event log da campanha pode confirmar evento narrativo LOW autorizado, mas qualquer alteração efetiva do motor só é `ENGINE_CONFIRMED` quando o host/bridge fornece receipt compatível. `UNCERTAIN` exige reconciliação, nunca retry cego.
9. **Viagem coerente:** cada incidente se ancora a segmento, janela temporal válida e local com proveniência; um bloqueio confirmado pode pausar/replanejar a rota pela DEC-069, mas não teleportar o NPC, forçar chegada ou gerar velocidade fictícia. Acontecimento ainda pendente não avança o relógio.
10. **Eventos em aberto não duplicam consequências:** `event_id`, `idempotency_key`, revisões e checkpoint; replay/restauração/fork/novos workers não aplicam o mesmo impacto duas vezes. Jobs atrasados revalidam ramo, tempo, identidade, rota, build, ACL, autorização e estado de quests.
11. **Privacidade e autoridade:** contextos pessoais/segreto via ACL DEC-028/057–059; nós LAN só propõem conforme escopo concedido. Host segue autoritativo mecanicamente, Infinity AI apenas narra e registra decisões válidas. Eventos HIGH históricos/privados respeitam consentimentos DEC-034/041/046.
12. **Preservação histórica:** conhecimento canônico permanece fisicamente dividido em `knowledge/periods/<ano>-DR/` (DEC-060), com proveniência e conflitos DEC-061, ingestão DEC-062 e Knowledge Pack versionado DEC-063. Incidentes, memórias NPC, segredos e efeitos ficam **no overlay da campanha/ramo**, não na base canônica.
13. **Escalabilidade segura:** atividade ACTIVE/NEAR/DISTANT/DORMANT DEC-021/068, clock DEC-022 e RPD DEC-056 controlam frequência e trabalho pendente. Não chamar LLM a cada tick, não acumular backlog infinito nem inventar história ao recompor longo período.
14. **Integração futura com presença de jogadores:** detectar encontro próximo não torna automaticamente um incidente jogável; política de transição de proposta offscreen para evento local e prevenção de dupla resolução permanece **DEC-071, aberta**.
15. **Lacunas para SPECS/POCs:** thresholds, classificação final de incidentes específicos, probabilidades curadas, consentimento e UI, evidências de interface do host, critérios de aceitação, orçamentos e fallback são posteriores. Não atribuir capacidades não testadas ao EEex.

## Consequências

- **Benefícios:** viagens mais vivas sem alterar fatos mecanicamente por ficção; rastreabilidade, replay seguro, integração futura com eventos regionais e preservação do espaço-tempo.
- **Custos:** registros versionados, matriz de risco/allowlist, orquestração de decisões, integração com conhecimento/itinerários, reconciliação de receipts, UI de pendências e observabilidade.
- **Trade-off:** acontecimentos HIGH poderão ficar pendentes em vez de serem consumados fora de cena. Preferimos lacuna explícita à fabricação de fatos irreversíveis.

## Evidência e verificação

- **Evidência de aprovação:** escolha C do idealizador em 2026-11-06, com preservação expressa das DEC-060–069.
- **Validação técnica:** documento 70 enumera **44 testes candidatos T070-01 a T070-44**; **nenhum foi executado**, nem há confirmação de spawn/encontro/combate, escrita de saves ou coerência multiplayer BG2:EE/EEex.
- **Dependências:** DEC-003/005-E/008/009/011/012/013/015/021/022/027/028/029/031/032/033/034/041/050/052/053/054/055/056/057/058/059/060–069.
- **Temas abertos históricos:** DEC-006/007/013/015/017/018 não são implicitamente encerradas.

## Próxima discussão proposta — DEC-071

**Transição de incidentes de viagem para encontros locais quando os jogadores se aproximam:** A) narrar sempre, sem eventos jogáveis; B) materializar automaticamente todos; C, recomendada) oferecer/incorporar seletivamente encontros compatíveis e autorizados, travando a resolução offscreen durante a transferência e exigindo confirmação do host e idempotência. **Ainda não aprovada.**
