# ADR-0093 — DEC-098/C: materialização incremental de repercussões regionais com snapshots, diferenças e reconciliação do host

- **Data de aprovação:** 2026-11-07.
- **Decisão expressa do idealizador:** **DEC-098 — opção C**.
- **Estado:** APROVADA COMO ARQUITETURA em Discovery **v9.4**; **não implementada nem comprovada no BG2:EE/EEex/multiplayer**.
- **Base:** DEC-060–DEC-097 mantidas integralmente; os **92 ADRs anteriores (ADR-0001 a ADR-0092) permanecem byte a byte idênticos** aos do ZIP v9.3.
- **Documento normativo complementar:** `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`.
- **Próxima discussão aberta:** DEC-099, compatibilidade/ownership de estados nativos, quests e mods com alterações de Living World.

## Contexto e problema

As DEC-096/C e DEC-097/C permitem avaliar a elegibilidade e compor repercussões históricas em regiões, mapas e tipos de estabelecimento. Ainda falta manifestar mudanças no motor quando jogadores visitam, deixam e revisitam áreas sem recriar os mesmos NPCs, duplicar loot, retroagir consequências, aplicar incrementos de preço repetidos ou confundir simulação distante com alterações que o host realmente confirmou. Dados de source lore por ano DR não são objetos físicos, nem o conteúdo narrativo de uma LLM é comprovação de entidade no motor. O BG2:EE e mods podem não oferecer APIs/observações suficientes para qualquer um dos mecanismos candidatos.

## Alternativas avaliadas

- **A — Reexecutar todos os efeitos em cada entrada no mapa:** **rejeitada**. Violaria identidade persistente DEC-066, encontro único DEC-071, limpeza segura DEC-073, deduplicação, save/load, host authority e economia coerente.
- **B — Deixar a LLM criar ou remover instâncias ao reentrar:** **rejeitada**. Falta prova de existência, ownership, recursos, autorizações, versão de build e determinismo; permitiria reescrever scripts originais ou remover itens coletados.
- **C — Snapshot regional + projeção desejada + observação autorizada do host + diff incremental + recibos + catch-up limitado:** **APROVADA**. Sem capacidade verificada, somente planejamento/telemetria segura e bloqueio específico.

## Decisão vinculante

1. **Três verdades distintas:** `DesiredRegionProjection` é uma projeção a partir das DEC-096/097 e demais regras; `RegionSnapshot` é um registro persistido do último estado **confirmado por host receipts**; `HostRegionObservation` representa observação real de uma sessão/área e pode ser parcial. Nenhuma é convertida automaticamente na outra. Informação do modelo, notícia ou crença do NPC jamais substitui observação mecânica.
2. **Diff sempre incremental:** `MaterializationPlanner` compara `(projection, snapshot, host observation)` e produz apenas um `RegionDeltaPlan` tipado (`NO_OP`, `PROPOSE_CREATE`, `PROPOSE_UPDATE`, `REVIEW_RETIRE`, `HOLD_RECONCILE`, `BLOCKED`). Nada é spawnado, apagado, movido, consumido ou recompensado no cálculo; aplica-se somente após gates e comprovante do host.
3. **IDs distintos e estáveis:** `persistent_npc_id` (DEC-066) ≠ `engine_instance_id` ≠ `template/CRE ID` ≠ `effect_instance_id`. Chaves têm `campaign_id`, `branch_id`, `region_id`, `host_epoch`, `checkpoint_epoch`, `build_fingerprint`, `pack_hash`, `ruleset_revision` e `materialization_revision`. Nomes, CRE idênticos e número de mapa não provam identidade ou propriedade; o mapeamento depende de evidência.
4. **Ownership/proteção do original:** entidades nativas, de quests, de outros mods, de jogadores ou de propriedade incerta são **PRESERVE/BLOCKED**. Apenas entidades cuja origem `INFINITY_AI` e ownership por instância foram corroborados podem receber proposta; retire/despawn é ainda mais restrito. Um snapshot não confere autorização sobre patrimônio de terceiros nem permite deletar NPCs por estarem longe do jogador.
5. **Observabilidade verificada:** um `HostRegionObservation` deve informar se a cobertura é suficiente para a ação exata. Ausência num scan parcial **não prova inexistência**. Sem API capaz de enumerar e distinguir instâncias na build/multiplayer, bloquear `CREATE` e operações destrutivas que dependam dessa ausência. Capabilities são testadas por build/ação, não inferidas do código Lua ou de exemplos sintéticos.
6. **Portão de criação:** `PROPOSE_CREATE` somente para entidades novas, declaradas por template allowlisted, custo/recursos disponíveis DEC-056/093, limites por área e owner comprovado; nenhuma criação automática de patrulhas, corpo, tesouro, quests ou atores com identidade duplicada. Após despacho, só commit mediante receipt do host e confirmação/observação coerente. Timeout ou `DISPATCHED/UNCERTAIN` bloqueiam retry cego.
7. **Portão de atualização:** atualização só do efeito tipado e autorizado; não redefinir scripts, diálogos, facção, HP, flags, inventário ou estado de quest nativo por analogia. Caso o host observe divergência de propriedade, estado, versão ou epoch, `HOLD_RECONCILE`; não forçar snapshot sobre motor. Para métricas da DEC-097, aplicar **target absoluto/delta entre target confirmado e desejado**, nunca reaplicar percentuais acumulativamente a cada visita.
8. **Portão de retirada:** `REVIEW_RETIRE` não é DELETE. Desmaterializar uma representação visual temporária não é matar nem excluir uma identidade persistente. Só considerar cleanup conforme DEC-071/073, sem encontro ativo, loot/transferências/quest pendentes, observação suficiente, capability validada e autorização/receipt. Itens transferidos a PCs jamais são limpos com a instância de origem.
9. **Snapshot e ledger append-only:** versionar baseline, `RegionStateRevision`, `AppliedEffectLedger`, `MaterializedInstanceLedger`, host receipts, ownership e pendências; mudanças de snapshot são commits confirmados, não gravações antecipadas durante a proposta. Reentrada/reload/restore/concorrência devem ser idempotentes por chave. Não supor transação atômica entre engine, banco e arquivos.
10. **Offscreen e catch-up:** regiões `ACTIVE/NEAR/DISTANT/DORMANT` (DEC-021/068) avançam apenas segundo DEC-022 `FROZEN/PARTIAL/REALTIME`; catch-up é limitado por ticks, orçamento e janelas, resumido quando possível, sem simular cada habitante/segundo. O resultado é projeção/pendência, não confirmação retroativa de combate, morte, deslocamento ou economia. `FROZEN` não gera avanço de tempo por relógio do SO.
11. **Handoff coerente:** DEC-069/070/071/072/073 preservam localização/presença e resolução única. Ao passar de offscreen para área carregada, transferir **apenas** incidentes/instâncias com lease e receipts válidos; nunca executar resolução offscreen e encontro mecânico para o mesmo incidente. Um NPC que já foi observado/retirado não é clonado ao reentrar.
12. **Originais e mods prevalecem nas suas fronteiras:** operações originais BG2:EE/quest scripts, alterações autorizadas por players e ownership de outros mods não são tratados como "ruído" a limpar. Divergências são registradas para revisão; a política detalhada de colisão e versionamento de mapas será tema da DEC-099.
13. **Multiplayer host-first:** um único host mecânico; nenhum cliente declara estado global, cria objetos ou valida receipt. Durante reconexão, clientes recebem estados confirmados; um cliente atrasado não autoriza re-materialização. Commits condicionados a epoch, checkpoint, versão de área e fencing DEC-011/012/053/058/093–095.
14. **Segredos e canon:** `knowledge/periods/<ANO>-DR/` permanece fisicamente intacto; diffs locais são overlays por campanha/branch. Snapshot privado e telemetria nunca revelam fonte protegida, NPC oculto ou spoiler futuro a clientes, conversas LLM, logs ou redes DEC-028/055/057/076/083–090.
15. **Falha fechada e custo:** lote limitado por região/tick, prioridade determinística e quotas; snapshot incompatível com build, host, versão, map-ID, unidade, ownership ou observabilidade bloqueia apenas o delta dependente. Não usar fallback para LLM nem gerar spawn para "consertar" dados inconclusivos.
16. **Integridade de histórico:** conservar decisões DEC-060–097, ADRs anteriores intactos e decisões antigas abertas nos respectivos estados. As **104 verificações T098-001..104 são casos candidatos NÃO EXECUTADOS**. Código de referência em Python opera exclusivamente em fixtures sintéticas e não interage com o jogo.

## Critérios de aceite futuros

- IDs estáveis em reentrada e pós-reload; ator já presente não duplica; ausência não observável bloqueia criação.
- State revision, branch, epoch, build e pack pins impedem contaminação entre saves e campanhas.
- Nativos, loot, PCs, mods e quests não sofrem remoção/patch sem política específica e host action receipt.
- Duas visitas à mesma região após mesmo tick produzem `NO_OP`/projeções sem novo despacho; no `UNCERTAIN`, quarentena.
- Catch-up de dezenas de dias permanece bounded; incidentes offscreen não reaparecem como novos encontros.
- Integração real **somente após matriz de capabilities por build EEex/BG2:EE Windows e teste host+2 clientes**.

## Consequências e trade-offs

A arquitetura acrescenta um ledger regional, índices de instâncias e reconciliação por área, tornando o sistema mais complexo que scripts `OnAreaEnter`. Em troca preserva continuidade, evita inflação de objetos e separa a simulação narrativa da mecânica. A falta de API observacional pode impedir materialização automática até haver POC; isso é uma restrição de segurança, não licença para inventar estado. As políticas de prioridade entre mudanças de quests e overlays ficam deliberadamente para DEC-099.
