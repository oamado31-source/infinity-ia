# Documento técnico 98 — Materialização incremental de efeitos históricos em mapas e regiões

**Discovery v9.4 · DEC-098/C APROVADA COMO ARQUITETURA · ADR-0093.** Contratos candidatos; **sem POC de EEex, BG2:EE multiplayer, host+2 clientes ou compatibilidade específica de build**. **104 testes T098-* abaixo são candidatos e NÃO EXECUTADOS**. Não confundir testes unitários de fixtures com integração.

## 1. Problema concreto

A matriz DEC-096 identifica eventos canônicos relevantes e DEC-097 calcula projeções por domínio/variável. A entrada em uma região não autoriza simplesmente reexecutar scripts de criação/alteração. Há NPCs persistentes DEC-066, operações offscreen DEC-068–071, encontros já resolvidos, loot transferido, scripts de quests e mods, jogadores em multiplayer e efeitos de mercado aplicados anteriormente. Um save pode ter sido carregado ou restaurado entre uma proposta e sua confirmação. Precisamos de um diffs que preserve causalidade e só peça ao host o estritamente necessário.

**Invariante:** cálculo do `target` e diffs **não é** mutação mecânica nem confirmação de fato. A autoridade do host DEC-011/012 permanece soberana para instâncias, combate, inventário, quest e posicionamento.

## 2. Camadas e pipeline

```text
CanonEvent (fonte curada/pinada por ano DR; DEC-060–063)
   -> regras condicionais DEC-096 -> propostas de repercussões
   -> composição determinística DEC-097 -> DesiredRegionProjection
   -> cruzar RegionSnapshot (somente last confirmed), HostRegionObservation
      e InstanceOwnershipRegistry + lease offscreen/active + risk & capabilities
   -> MaterializationPlanner (pure function) -> RegionDeltaPlan (PROJECTION_ONLY)
   -> validação DEC-027/041/053/056/071/073/093–095 + autorizações
   -> Action Gateway DEC-012 -> único host mecânico
   -> recibo, observação e reconciliação -> RegionSnapshotRevision + ledgers
   -> propagar consequências confirmadas DEC-074 / knowledge DEC-029
```

### Separação de camadas de estado

| Camada | Entidade | Autoridade / escopo | Proibição |
|---|---|---|---|
| Lore canônico | `CanonEvent` / `KnowledgePackPin` | Curadoria histórica por ano DR | Não receber escrita da campanha |
| Proposta de regras | `DesiredRegionProjection` | Avaliador DEC-096 + compositor DEC-097 | Não afirma mundo real nem spawn |
| Último observado como fato | `HostRegionObservation` | Host e adapter da build, com cobertura declarada | Não usar ausência parcial como prova |
| Persistência | `RegionSnapshot` | Ledger de receipts confirmados por campanha/ramo/epoch | Não pré-commit em proposta |
| Identidade e propriedade | `InstanceOwnershipRegistry` | Host receipts, decisões 066/071/073 e transferências | CRE, nome e texto da LLM não provam owner |
| Diff | `RegionDeltaPlan` | Planner puro, determinístico, versão pinned | Não escreve no motor |
| Efeito realizado | `MaterializationReceipt`/`AppliedEffectLedger` | Apenas confirmação host reconciliada | Não promover `UNCERTAIN` a sucesso |
| Conhecimento social | `NPCBelief`, `Rumor` | Aquisição DEC-029/064/074 | Não inferir de spawn ou logs |

## 3. Contratos candidatos (não são APIs EEex existentes)

```json
{
  "RegionScope": {"campaign_id":"cmp","branch_id":"main","region_id":"area",
    "host_epoch":1,"checkpoint_epoch":7,"build_fingerprint":"pinned-build",
    "knowledge_pack_hash":"sha256","ruleset_revision":"ruleset-1","region_revision":19},
  "RegionSnapshot": {"scope_ref":"RegionScope","confirmed_world_tick":1302,
    "snapshot_revision":19,"snapshot_hash":"sha256","observed_coverage":"PARTIAL_OR_COMPLETE",
    "instances":[{"persistent_id":"npc-42","engine_instance_id":"opaque-instance-ref",
      "owner_kind":"INFINITY_AI","ownership_receipt_id":"host-receipt-123",
      "origin_kind":"ENCOUNTER_PERSISTENT","last_confirmed_state_hash":"sha256"}],
    "pending_action_ids":[]},
  "HostRegionObservation": {"scope_ref":"RegionScope","host_session_id":"session-1",
    "observation_id":"obs-5","coverage":"UNKNOWN_OR_PARTIAL_OR_CAPABILITY_VERIFIED_COMPLETE",
    "instance_mappings":[],"engine_state_hash":"sha256","observation_receipt_id":"receipt-obs"},
  "DesiredRegionProjection": {"scope_ref":"RegionScope","world_tick":1303,
    "source_composition_trace_ids":["DEC-097-trace"],"entity_targets":[],
    "metric_targets":[],"pending_incident_leases":[]},
  "RegionDeltaPlan": {"scope_ref":"RegionScope","expected_snapshot_revision":19,
    "observation_id":"obs-5","plan_status":"PROJECTION_ONLY_OR_BLOCKED",
    "actions":[{"intent":"NO_OP_OR_PROPOSE_CREATE_OR_PROPOSE_UPDATE_OR_REVIEW_RETIRE_OR_HOLD_RECONCILE",
      "persistent_id":"npc-42","idempotency_key":"stable-hash","risk":"LOW_MEDIUM_HIGH",
      "required_capability":"per-build-verified","required_receipt":true}],
    "blockers":[],"backlog_ticks":0,"plan_hash":"sha256"}
}
```

**Protocolo de estados candidato:** `NOT_OBSERVED` → `OBSERVING` → `RECONCILED` → `DELTA_PROPOSED` → `AUTHORIZED` → `OUTBOX_PREPARED` → `DISPATCHED` → `CONFIRMED`/`REJECTED`/`UNCERTAIN`. `UNCERTAIN` requer rescan/reconciliação antes de qualquer retry. A revisão regional só avança após confirmação, não no momento `DELTA_PROPOSED`.

## 4. Identidade e ownership

- `persistent_id` identifica o NPC/objeto em `campaign_id+branch_id`. `engine_instance_id` é opaco, efêmero e pode ser reciclado ao recarregar; `template_id`/`.CRE` não identifica instância. Um NPC individualizado DEC-066/067 pode existir offscreen sem objeto presente; isso não constitui autorização para cloná-lo.
- `owner_kind` tipado: `INFINITY_AI`, `NATIVE_OR_MOD`, `PLAYER`, `TRANSFERRED`, `UNKNOWN`, `CONTESTED`. Padrão seguro é **PRESERVE** para não-INFINITY_AI e **HOLD** para UNKNOWN.
- Só associar instância a owner `INFINITY_AI` com `ownership_receipt_id` e correspondência de identidade verificada. Retirar objeto temporário não elimina sua identidade narrativa; `ENCOUNTER_PERSISTENT` ou NPC conversacional podem continuar no mundo mesmo sem entidade local ativa.
- Quests, romances, scripts, cutscenes, drops, inventário e itens/atores de outros mods estão fora da autorização de limpeza genérica. Objetos transferidos a PCs ou consumidos devem ter novo owner e recibo de transferência.
- Se um novo plugin criar objeto com mesmo template, a presença não autoriza classificar como nosso. Colisão de engine ref/ownership -> `BLOCKED_CONTESTED`, a detalhar DEC-099.

## 5. Algoritmo candidato de diffs

1. **Validar contexto:** campanha, branch, epoch, checkpoint, build, pack pin e revisão da região idênticos em snapshot e observação. Snapshot sem versão = bloqueio; não usar cache de outro host.
2. **Validar observabilidade:** apenas uma capability de enumeração **testada naquela build e modo multiplayer**, com cobertura suficiente, pode distinguir ausência de entidade. Scans `UNKNOWN/PARTIAL` não autorizam CREATE/RETIRE nem alterações baseadas em suposta ausência.
3. **Validar disponibilidade da projeção:** DEC-096/097 elegíveis no ano/local/branch, tempo do mundo DEC-022, baseline/metric policy, autorização de recursos, ordem de causalidade e referência do evento. `UNVERIFIED` não vira desired state.
4. **Indexar por identidade persistente:** construir mapas de IDs únicos do snapshot, observação e alvo. Se IDs duplicados, reciclagem, colisão owner ou mapeamento ambíguo, bloquear identidade e pedir correção. Nunca combinar por posição na lista.
5. **Preservar entidades confirmadas já presentes:** `NO_OP` se o estado observado é compatível com snapshot/projeção. Mesmo objetivo sem mudança não cria novo outbox. Atualizar apenas campo allowlisted e somente com compare-and-swap de revisões/recibos.
6. **Identidade ainda sem instância:** apenas propor `PROPOSE_CREATE` quando **não existe** no snapshot e uma observação suficiente evidencia que não há instância correspondente, com capability explícita por build, template allowlisted, recursos, limites e autorização; caso contrário `HOLD_RECONCILE`.
7. **Identidade snapshot presente, observação ausente:** não concluir morte/despawn. Pode ser transferência legítima, script nativo, unload parcial ou falha do scan. Marcar `HOLD_RECONCILE`, nunca recriar às cegas.
8. **Instância existente não desejada:** emitir `REVIEW_RETIRE` somente se comprovadamente owned e elegível. A revisão respeita DEC-073 (encontro, loot, transferências, quests, receipts), riscos e capacidade testada; não é comando de apagar.
9. **Recursos/pending:** se `pending_action_id` ou ação `DISPATCHED/UNCERTAIN` afeta a identidade/recurso, bloquear novos comandos e quarentenar; reconciliar antes de qualquer operação subsequente.
10. **Ordenar diff e identificar versão:** todas as ações candidatas em ordenação canônica por região + ID + intent; chave de idempotência inclui revisão, motivo, autorização e sessão. Fingerprint de plano para detecção de repetição, não prova de commit.

## 6. Materialização por domínio

| Domínio | Projeção DEC-096/097 | Diferença materializável e bloqueios |
|---|---|---|
| Patrulhas | Intensidade/quantidade plausível (não instância) | Propor recursos já permitidos; nenhum NPC infinito; DEC-066/069/071/072 |
| Preços | Target tipado com baseline | Diferença do target host-confirmado, **não** `price *= 1.2` por entrada |
| Rumores | Elegibilidade de conteúdo narrativo | Transmissão causal DEC-029/074, não spawn de conhecimento global |
| Comércio | Oferta/demanda/proposta de caravanas | Recursos e presença reais, sem ouro ou cargas fantasma |
| Encontros | Template/incident lease | Um incidente = uma resolução DEC-070/071; não duplicar encounter |
| Quest/script nativo | Estado observado via adapter testado | Default PRESERVE; nenhum patch genérico de flags/diálogo/romance |
| Efeito expirado | Novo target sem contribuição antiga | Nenhuma reversão física automática de atos confirmados; ações separadas sob DEC-095 |

## 7. Tempo do mundo, zonas de atividade e catch-up

- `ACTIVE`: reconciliar com host e avançar a frequência limitada por eventos; nunca a cada frame. `NEAR`: deltas de baixa resolução e pré-carregamento hipotético **sem assumir suporte na engine**.
- `DISTANT`: simular apenas eventos agregados/indivíduos promovidos com regras DEC-068/069 e quotas. `DORMANT`: snapshots resumidos e janelas selecionadas; não criar/retirar instâncias em engine offscreen sem proof.
- Em `FROZEN` DEC-022, `elapsed_world_ticks=0`, ainda que relógio real avance. `PARTIAL/REALTIME` só seguem o relógio DR validado da campanha; não usar wall time do SO nem converter diretamente o calendário de Harptos.
- `catchup_steps=min(elapsed_ticks, configured_budget)`, retornar `remaining_backlog` para ticks futuros. Não percorrer todos os dias, eventos e NPCs desde 1369 DR numa visita nem inferir episódios irreversíveis pelo silêncio. Event sourcing e mudanças agregadas exigem confirmação própria quando produzem efeitos mecânicos.
- Ano desconhecido da fonte não é habilitado pela passagem de tick; efeitos futuros e `YEAR_ONLY` continuam respeitando precisão DEC-096.

## 8. Multiplayer, falhas, saves e divergências

- **Host-first:** clientes só exibem fatos autorizados recebidos, não são fontes de verdade de spawn/despawn. Testar 2 clientes conectados, host, disconnect, reconnect e alternância de área. Observações privadas não vazam IDs/segredos DEC-028/083–090.
- **Save/load:** snapshot e host checkpoint precisam corresponder. Se engine apresentou instâncias extras ou ausentes após restore, reconciliar antes de propor. Não supor persistência automática de engine instance IDs.
- **Crash entre comando e receipt:** `UNCERTAIN`; não reenfileirar mesmo comando com nova chave. Garantir outbox/idempotency ledger e reobservação.
- **Build ou mods alterados:** invalidar capability e fingerprint até novos testes. A reconciliação de alterações nativas e de terceiros será detalhada na DEC-099.
- **Quests e cutscenes:** preservar autoridade nativa sobre originais; nunca desmaterializar ator com scripts/quest pendentes apenas por expiração de efeito de guerra.
- **Baseline divergente:** comparar `RegionSnapshotRevision` e `HostRegionObservation`, não normalizar diferença silenciosamente; escalar para revisão manual se o estado do motor não for reproduzível.
- **Concorrência:** usar fences por `(host_epoch,checkpoint_epoch,region_revision,operation_revision)` para evitar dois workers planejando comandos conflitantes. DEC-093/094/095 administram reservas, impasses e compensações; nenhuma reserva é equivalente a spawn real.

## 9. Segurança, custos e capacidades ainda não demonstradas

- Potenciais capacidades por build **a investigar em POC separada**: observar objetos/atores e ownership com confiabilidade; criar instâncias sob host authority; manter ids entre save/load; retirar representações sem afetar quest; sincronizar cliente e atualizar variáveis de jogo. Não afirmar que EEex fornece APIs exatas sem verificação por build.
- Dispatcher deve aplicar allowlist por ação e campo, sanitização de origem, limites por tick/região, custeio de CPU/memória DEC-056 e orçamento de NPCs DEC-067. Fallback sem capabilities é **não aplicar**, e não improvisar Lua/LLM.
- Na UI, um `PROJECTION_ONLY` deve parecer "prévia"; um `UNCERTAIN` deve aparecer como pendência de confirmação; `CONFIRMED` só mediante comprovante validado. Auditoria com hash/scope/reasons sem publicar segredos.
- Não executar código de documentos canônicos, de mods ou de LLM. A matriz é **dados allowlisted**, não scripting arbitrário.

## 10. Referências executáveis e limites dos testes

- `examples/chronology/materialization_v1.synthetic.json`: cenário exclusivamente fictício, com um NPC já presente e um novo NPC candidato.
- `examples/chronology/materialization_plan_v1.candidate.schema.json`: esquema candidato de input sintético e output esperado; não interface oficial do EEex.
- `examples/chronology/materializer_reference.py`: **função pura**, sem import de jogo, rede ou alterações de estado. Gera somente `PROJECTION_ONLY`, `NO_OP`, `HOLD_RECONCILE` ou `BLOCKED_*`.
- `examples/chronology/test_materializer_reference.py`: regressões unitárias de guardrails, escopo, dedup, parcialidade, gates, time e reentry. Não comprovam host receipts reais, multiplayer, identidade de engine ou assets.

## 11. Matriz de testes de integração/aceitação — 104 CANDIDATOS NÃO EXECUTADOS

**Nenhum dos T098-001..T098-104 foi executado no BG2:EE/EEex/host+2 clientes.** Os testes de referência Python são unitários **sintéticos e separados**. A matriz abaixo é um plano para SPECS/POCs, não evidência de funcionamento.

### Escopo e pins

- **T098-001 — NÃO EXECUTADO:** Campanha correta é condição obrigatória.
- **T098-002 — NÃO EXECUTADO:** Branch correto é condição obrigatória.
- **T098-003 — NÃO EXECUTADO:** Host_epoch diferente bloqueia mutação.
- **T098-004 — NÃO EXECUTADO:** Checkpoint_epoch diferente exige rescan.
- **T098-005 — NÃO EXECUTADO:** Build_fingerprint divergente bloqueia adapter.
- **T098-006 — NÃO EXECUTADO:** Knowledge Pack divergente bloqueia.
- **T098-007 — NÃO EXECUTADO:** Ruleset_revision divergente bloqueia.
- **T098-008 — NÃO EXECUTADO:** Mapa desconhecido para a build falha fechado.

### Snapshots e ledgers

- **T098-009 — NÃO EXECUTADO:** Snapshot novo exige baseline conhecido.
- **T098-010 — NÃO EXECUTADO:** Snapshot registra somente recibos confirmados.
- **T098-011 — NÃO EXECUTADO:** Duas revisões concorrentes não sobrescrevem.
- **T098-012 — NÃO EXECUTADO:** Snapshot parcial é identificado como parcial.
- **T098-013 — NÃO EXECUTADO:** Restore não reescreve ledger futuro.
- **T098-014 — NÃO EXECUTADO:** Snapshot não altera lore físico por ano.
- **T098-015 — NÃO EXECUTADO:** IDs persistentes sobrevivem a unload.
- **T098-016 — NÃO EXECUTADO:** Snapshot não contém segredo em log amplo.

### Identidade e ownership

- **T098-017 — NÃO EXECUTADO:** ID persistente não é CRE ID.
- **T098-018 — NÃO EXECUTADO:** Dois NPCs com mesmo nome não colidem.
- **T098-019 — NÃO EXECUTADO:** Alias de NPC refere identidade única.
- **T098-020 — NÃO EXECUTADO:** Componente nativo é preservado.
- **T098-021 — NÃO EXECUTADO:** Ator de mod de terceiro é preservado.
- **T098-022 — NÃO EXECUTADO:** Item no inventário de PC não é limpo.
- **T098-023 — NÃO EXECUTADO:** Ownership incerto bloqueia atualização.
- **T098-024 — NÃO EXECUTADO:** Transferência legítima revoga owner antigo.

### Observação e ausência

- **T098-025 — NÃO EXECUTADO:** Scan parcial não confirma ausência.
- **T098-026 — NÃO EXECUTADO:** Scan completo sem POC de build não autoriza spawn.
- **T098-027 — NÃO EXECUTADO:** Ator observado idêntico não é recriado.
- **T098-028 — NÃO EXECUTADO:** Instância host inesperada produz conflito.
- **T098-029 — NÃO EXECUTADO:** Instance_id reciclado exige reconciliação.
- **T098-030 — NÃO EXECUTADO:** Receipts falsificados são rejeitados.
- **T098-031 — NÃO EXECUTADO:** Scan de cliente não é observação host.
- **T098-032 — NÃO EXECUTADO:** Mapa não carregado não presume inexistência.

### Create e limites

- **T098-033 — NÃO EXECUTADO:** Spawn sem adapter aprovado bloqueado.
- **T098-034 — NÃO EXECUTADO:** Template fora do allowlist bloqueia.
- **T098-035 — NÃO EXECUTADO:** Reentrada não repete mesmo create.
- **T098-036 — NÃO EXECUTADO:** Cap de novas entidades respeitado.
- **T098-037 — NÃO EXECUTADO:** Recursos de patrulha disponíveis verificados.
- **T098-038 — NÃO EXECUTADO:** NPC persistente offscreen não é clonado.
- **T098-039 — NÃO EXECUTADO:** Outbox pendente bloqueia segunda emissão.
- **T098-040 — NÃO EXECUTADO:** Proposta de spawn não significa execução.

### Update e composição

- **T098-041 — NÃO EXECUTADO:** Target de preço absoluto não reaplica percentual.
- **T098-042 — NÃO EXECUTADO:** Unidade desconhecida impede update.
- **T098-043 — NÃO EXECUTADO:** Update limitado a campo allowlisted.
- **T098-044 — NÃO EXECUTADO:** Item de quest não recebe update arbitrário.
- **T098-045 — NÃO EXECUTADO:** Host divergiu do snapshot exige revisão.
- **T098-046 — NÃO EXECUTADO:** Nova policy revision exige diff.
- **T098-047 — NÃO EXECUTADO:** Efeito expirado não desfaz recibo antigo.
- **T098-048 — NÃO EXECUTADO:** Empate não resolvido DEC-097 bloqueia.

### Retirada e pós-encontro

- **T098-049 — NÃO EXECUTADO:** Retire é revisão e não DELETE.
- **T098-050 — NÃO EXECUTADO:** NPC permanente não é descartável.
- **T098-051 — NÃO EXECUTADO:** Loot recolhido não é removido.
- **T098-052 — NÃO EXECUTADO:** Encontro ativo impede limpeza.
- **T098-053 — NÃO EXECUTADO:** Incidente resolvido não reativa no reload.
- **T098-054 — NÃO EXECUTADO:** Ação de limpeza requer receipt host.
- **T098-055 — NÃO EXECUTADO:** Ator de quest segue preservado.
- **T098-056 — NÃO EXECUTADO:** Remover representação não apaga NPC em memória.

### Offscreen e tempo

- **T098-057 — NÃO EXECUTADO:** FROZEN não avança por tempo do SO.
- **T098-058 — NÃO EXECUTADO:** PARTIAL limita catch-up por orçamento.
- **T098-059 — NÃO EXECUTADO:** REALTIME respeita tempo DR validado.
- **T098-060 — NÃO EXECUTADO:** Muito backlog produz continuação posterior.
- **T098-061 — NÃO EXECUTADO:** DORMANT não simula cada NPC por frame.
- **T098-062 — NÃO EXECUTADO:** Evento futuro não materializa cedo.
- **T098-063 — NÃO EXECUTADO:** Efeito YEAR_ONLY não inventa mês.
- **T098-064 — NÃO EXECUTADO:** Rumor só propaga com canal causal.

### Handoff e causalidade

- **T098-065 — NÃO EXECUTADO:** Evento offscreen não resolve também em tela.
- **T098-066 — NÃO EXECUTADO:** Lease DEC-071 controla handoff.
- **T098-067 — NÃO EXECUTADO:** Incidente pendente mantém exclusividade.
- **T098-068 — NÃO EXECUTADO:** Pais de efeitos indiretos exigem receipt.
- **T098-069 — NÃO EXECUTADO:** Entidade distante não teleporta sem travel.
- **T098-070 — NÃO EXECUTADO:** Retorno ao mapa conserva consequências.
- **T098-071 — NÃO EXECUTADO:** Mudança de cronologia N3 respeita branch.
- **T098-072 — NÃO EXECUTADO:** Reação regional não chega a mapa excluído.

### Host e estados

- **T098-073 — NÃO EXECUTADO:** PROPOSED não vira CONFIRMED.
- **T098-074 — NÃO EXECUTADO:** DISPATCHED não dispara retry cego.
- **T098-075 — NÃO EXECUTADO:** UNCERTAIN fica em quarentena.
- **T098-076 — NÃO EXECUTADO:** Receipt de epoch antigo é rejeitado.
- **T098-077 — NÃO EXECUTADO:** Receipt duplicado é idempotente.
- **T098-078 — NÃO EXECUTADO:** Timeout de criação não gera novo spawn.
- **T098-079 — NÃO EXECUTADO:** Host rejeitou comando sem snapshot falso.
- **T098-080 — NÃO EXECUTADO:** Cliente reconectado não altera host state.

### Operações e recursos

- **T098-081 — NÃO EXECUTADO:** Reserva DEC-093 não equivale a instância.
- **T098-082 — NÃO EXECUTADO:** Deadlock DEC-094 não libera ação pendente.
- **T098-083 — NÃO EXECUTADO:** Compensação Saga DEC-095 é evento novo.
- **T098-084 — NÃO EXECUTADO:** PC sem consentimento impede efeito seu.
- **T098-085 — NÃO EXECUTADO:** Mudança HIGH exige gate.
- **T098-086 — NÃO EXECUTADO:** Quota regional impede explosão de spawn.
- **T098-087 — NÃO EXECUTADO:** Dois planos concorrentes não usam mesmo recurso.
- **T098-088 — NÃO EXECUTADO:** Prioridade não concede ownership.

### Segurança, multiplayer e privacidade

- **T098-089 — NÃO EXECUTADO:** Prompt LLM não contém NPC oculto.
- **T098-090 — NÃO EXECUTADO:** Log redigido preserva privacidade.
- **T098-091 — NÃO EXECUTADO:** Cache separa campanhas.
- **T098-092 — NÃO EXECUTADO:** Cache separa branches.
- **T098-093 — NÃO EXECUTADO:** Cliente defasado não confirma ação.
- **T098-094 — NÃO EXECUTADO:** 2 clientes recebem snapshot autorizado.
- **T098-095 — NÃO EXECUTADO:** Reconexão com checkpoint antigo suspende.
- **T098-096 — NÃO EXECUTADO:** Host observation expõe somente campos permitidos.

### Recuperação e regressão

- **T098-097 — NÃO EXECUTADO:** Crash entre dispatch e receipt preserva UNCERTAIN.
- **T098-098 — NÃO EXECUTADO:** Save/load não materializa evento duas vezes.
- **T098-099 — NÃO EXECUTADO:** Carga após upgrade de build exige rescan.
- **T098-100 — NÃO EXECUTADO:** Delta vazio produz NO_OP.
- **T098-101 — NÃO EXECUTADO:** Permutação de candidatos não altera diff.
- **T098-102 — NÃO EXECUTADO:** Hash do snapshot protege revisão.
- **T098-103 — NÃO EXECUTADO:** Nenhum teste sintético prova bridge real.
- **T098-104 — NÃO EXECUTADO:** Capability faltante produz BLOCKED sem LLM fallback.

## 12. Critérios de saída e próxima decisão

Não avançar para afirmações de integração sem identificar a build Windows prioritária, demonstrar snapshots de observação por host, confirmação de spawn/patch compatível, persistência após save/load, isolamento de dois clientes e cenário de mods/quest coexistindo. Se falharem, a arquitetura continua válida como especificação, com materialização bloqueada no adapter. **DEC-099 aberta:** ownership/precedência e proteção de alterações de scripts originais/quests/mods ao reconciliar overlays do Infinity AI.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Planejador incremental usa snapshot e cobertura host, mas deve validar titularidade por instância e campo; delta nunca é autorização.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Snapshots regionais só incluem observações com cobertura/escopo conhecidos; não deduzem ausência de scan parcial.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Semantic quest milestones are curated technical metadata, separate from FR historical canon partitioned by year DR and private campaign overlays. UNKNOWN, AMBIGUOUS or stale milestones cannot trigger chronology, historical effect or materialization; lore packs do not authorize interpreting runtime flags. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Materialização DEC-098 não pode usar conflito de quest DEC-102 como autorização para spawn/despawn. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** observar DEC-100, interpretar DEC-101 e reconciliar DEC-102 não são eventos automaticamente propagáveis. Apenas prova semântica atual e reconciliação `CONSISTENT_WITH_PROOF` ou `APPROVED_AND_COMMITTED_REBASE` habilita pedido de admissão lógica por ruleset pinado; rebase `PROPOSE_*` não permite emissão. Proposta, autorização, receipt host e conhecimento de NPC permanecem entidades separadas. Não reabrir quest, editar flags, alterar scripts nem assumir ownership por narrativa. Dedup por occurrence/lineage, sem duplicação após save/load ou observação repetida. Consultar `docs/103-admissao-e-propagacao-causal-de-marcos-de-quests-reconciliados.md`. **Sem POC no motor.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **snapshots e estado host-confirmed**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para materialização regional não duplica mensagens/receipts de NPCs, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para região materializada mantém fatos e NPCs anteriores, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Reentrada em mapa não reaplica transferência já confirmada. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Reentrada em região não reexecuta cumprimento de obrigações. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
