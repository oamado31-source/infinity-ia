# Documento técnico 99 — Ownership por instância, compatibilidade por build e arbitragem segura

**Status:** DEC-099/C **APROVADA COMO ARQUITETURA**, 2026-11-07, Discovery v9.5. **Não implementado** no BG2:EE, EEex nem multiplayer. **ADR:** `docs/decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md`.

## 1. Objetivo e limites

Impedir que a materialização incremental DEC-098 destrua, substitua, ressuscite, remova ou altere indevidamente estados de BG2:EE, quests, scripts originais, mods, jogadores e recursos cujo proprietário não seja o Infinity AI. Este documento define interfaces/estados candidatos, sem pressupor API real de EEex ou autorização implícita do host. A LLM auxilia somente com descrição e alternativas; não classifica propriedade nem assina recibos.

## 2. Quatro dimensões de autoridade

| Dimensão | Significado | Exemplos e limites |
|---|---|---|
| `authored_origin` | Quem forneceu template/recurso originalmente | CRE nativo ou modded; não transfere ownership de toda instância |
| `runtime_custodian` | Quem hoje mantém o ciclo de vida | Um item inicialmente do mod pode estar em inventário de PC |
| `instance_owner` | Titularidade da instância comprovada por proveniência e host evidence | Não inferir de nome, CRE, diálogo, id de sessão ou memória de LLM |
| `field_authority` | Escopo permitido em campos/ações específicos | Permitir schedule de ator IA não permite editar romance/quest flag |

**Valores conservadores:** `ENGINE_NATIVE`, `QUEST_SCRIPT`, `THIRD_PARTY_MOD`, `PLAYER`, `INFINITY_AI`, `UNKNOWN`; `UNKNOWN` preserva o objeto. O subsistema Infinity AI nunca assume propriedade completa quando a fonte reconhecida fornece apenas licença para um campo. **Não existe ordenação universal** `INFINITY_AI > native > mod`; a autoridade é por **campo**, **ação**, **instância**, **estado de quest** e **build**.

## 3. Contratos candidatos

```text
BuildCompatibilityManifest
  build_fingerprint; engine_version; game_edition; platform; game_language
  eeex_version?; bridge_version?; modpack_hash; mods[] (id, version, load_order, file_hash)
  area_manifest_hashes[]; map_ids[]; adapter_id; adapter_revision
  action_capabilities[] (action_id, owner_scope, field_id, test_case_ref,
                         tested_build_hash, verified_host_mode, validation_status)
  coverage (read_only_obs, instance_enumeration, events, save_load, 2_clients)
  manifest_hash; provenance; approved_at; expiry?; curator

OwnershipRecord
  campaign_id; branch_id; region_id; persistent_id; engine_instance_id
  instance_generation; template_id; authored_origin; runtime_custodian
  instance_owner; owner_claim_evidence[]; owner_receipt_id?; field_authorities[]
  lifecycle_state; last_observed_revision; owner_revision; host_epoch
  checkpoint_epoch; build_fingerprint; modpack_hash; save_revision

FieldAuthorityRule
  policy_revision; instance_selector; owner_kind; action_type; field_id
  allowed_when[] (quest_phase?, encounter_state?, party_state?, consent?)
  priority_only_within_same_field; forbidden_conflicts[]; evidence_refs[]

MutationIntent
  intent_id; operation_id; idempotency_key; campaign_id; branch_id
  region_id; persistent_id; engine_instance_id?; field_id; action_type
  expected_owner_revision; expected_host_epoch; expected_checkpoint_epoch
  expected_build_fingerprint; expected_modpack_hash; expected_area_revision
  expected_host_state; action_risk; approval_refs[]; effect_refs[]

CompatibilityDecision
  status (NO_OP | PRESERVE_READ_ONLY | PROPOSE_OWNED_PATCH |
          PROPOSE_OWNED_CREATE | REVIEW_RETIRE | HOLD_RECONCILE |
          BLOCKED_OWNERSHIP | BLOCKED_CAPABILITY |
          BLOCKED_PROTECTED_FIELD | ESCALATE_CONFLICT)
  decision_hash; reason_codes[]; required_evidence[]; read_scope[]
  source_refs[]; host_calls=0; engine_mutations=0; current_revision

OwnershipCollisionLedger (append-only)
  id; campaign; branch; region; instance; field; contender_ids[]
  detected_by; host_observation_ref?; policy_version; blocker_codes[]
  state (OPEN | RECONCILING | RESOLVED_CONFIRMED | BLOCKED)
  resolution_authority; receipt_refs[]; audit_hash; redaction_scope
```

**Schema de referência:** `examples/chronology/ownership_policy_v1.candidate.schema.json` e fixture `ownership_v1.synthetic.json` são contratos de **teste**, não APIs do motor.

## 4. Proteção por owner, escopo e campo

| Origem/caso | Leitura para planejador | Mudança proposta | Mutação automática |
|---|---|---|---|
| `ENGINE_NATIVE` | Somente se adapter e ACL aprovados | `PRESERVE_READ_ONLY`; revisão de alternativas | **PROIBIDA** |
| `QUEST_SCRIPT` | Somente sinais testados e autorizados | `HOLD_RECONCILE` se a intenção colidir | **PROIBIDA** |
| `THIRD_PARTY_MOD` | Inventário curado não confere acesso a runtime | `BLOCKED_OWNERSHIP`; integração explícita futura | **PROIBIDA** |
| `PLAYER` | Somente permissões/consentimentos pertinentes | Requer titular, política PvP e host gate | **PROIBIDA** |
| `UNKNOWN` | Acesso mínimo e sem inferência de ownership | `HOLD_RECONCILE` | **PROIBIDA** |
| `INFINITY_AI` com prova | Campos allowlisted e observabilidade suficiente | Pode gerar `PROPOSE_OWNED_*` | **NÃO**: requer Action Gateway, autorização e host receipt |

### Campos críticos sempre bloqueados por padrão

`quest_flag`, `global_var`, `area_script`, `npc_script`, `banter`, `romance_state`, `dialogue_state`, `player_inventory`, `third_party_inventory`, `kill_revive`, `character_control`, `cutscene_state`, `quest_reward`, `script_trigger`, `plot_teleport`. Mesmo que uma fixture sintética permita `state_overlay`, essa permissão não significa que haja hook de runtime testado. O inventário de conteúdo DEC-051 não é uma licença de escrita.

## 5. Pipeline de preflight e reconcile

```text
EVENTO DEC-096/097 → DesiredRegionProjection DEC-098
  → MutationIntent identificada com campo/instância/branch
  → Validar fingerprints (build, modpack, area, adapter, save)
  → Validar host epoch/checkpoint/revision
  → Determinar ownership (host receipts + lineage + mod manifests + field claims)
  → Detectar colidências de campos/owners e proteger quest/PC/mod
  → Confirmar capability real por build E pelo tipo de ação
  → Validar observação suficiente, pré-condições, consentimentos, risco e recursos
  → CompatibilityDecision (somente PREVIEW, sem writes)
  → DEC-091/092 aprovação; DEC-093/094 reservas; Action Gateway DEC-012
  → Despacho idempotente ao host quando disponível em produção
  → Recibo host, confirmação de estado e ledger append-only
  → RegionSnapshot DEC-098 atualizado somente por commit confirmado
```

**FALHA FECHADA:** se duas origens reivindicarem o mesmo campo, `ESCALATE_CONFLICT`; se a origem for incerta, `HOLD_RECONCILE`; se um patch for para campo protegido, `BLOCKED_PROTECTED_FIELD`. Nenhuma delas é convertida automaticamente em `PROPOSE_OWNED_PATCH` por prioridade narrativa ou texto LLM.

## 6. Máquina de estados e garantia de não execução

| Estado | Condição de entrada | Próxima etapa permitida |
|---|---|---|
| `PLANNED` | Repercussão candidata, sem authority | Preflight |
| `PRESERVE_READ_ONLY` | Instância nativa/mod/PC, sem mudança | Não aplicar |
| `HOLD_RECONCILE` | Ownership/versão/observação incompleta | Coletar evidências com ACL |
| `BLOCKED_*` | Mutação proibida ou capability ausente | Registrar razão; revisar proposta |
| `ESCALATE_CONFLICT` | Contendas sem precedência curada | Revisão autorizada específica |
| `PROPOSE_OWNED_*` | Apenas escopo IA provado, sem conflict | Validar approvals e Action Gateway |
| `PREPARED` | Plano autorizado/idempotency registrada | Despacho apenas se capability testada |
| `DISPATCHED/UNCERTAIN` | Recibo ausente/ambíguo | Quarentena + reconciliação host |
| `CONFIRMED` | Receipt genuíno e pós-condição | Snapshot/ledger append-only |
| `REJECTED` | Host negou ou precondition falhou | Não mutar ledger factual |

Nunca executar automaticamente `DISPATCHED` após timeout. Um `RETIRE` sempre é revisão e precisa de DEC-071/073 e competência específica. Salvar um snapshot sem recibo é proibido.

## 7. Conflitos e precedência localizada

**Exemplo 1 — original:** a quest original mantém um guarda em determinada sala. Uma projeção de guerra deseja movimentá-lo. O reconciliador não possui autoridade sobre `QUEST_SCRIPT` e retorna `PRESERVE_READ_ONLY`/`BLOCKED_OWNERSHIP`. A projeção poderá propor **outro** ator IA em área compatível, com recursos, mapa e direitos comprovados, mas não alterará o guarda da quest.

**Exemplo 2 — mod de terceiro:** um mod adiciona NPC e altera seu script; o inventário do build confirma o recurso mas não garante enumerabilidade de instância. `THIRD_PARTY_MOD` permanece protegido. Nome coincidente com NPC gerado não autoriza adoção por GUID heurístico.

**Exemplo 3 — item de PC:** um item criado em encontro do Infinity AI foi legitimamente recolhido pelo jogador. A custódia/controle atual passa a ser do PC; limpar o encontro não pode remover o item no inventário (DEC-073/095).

**Exemplo 4 — instância IA com camada nativa:** o Infinity AI tem prova de ter criado a instância, mas um script de quest ou mod tomou controle de determinado campo. O campo fica protegido apesar do owner original ser IA. Sem contrato explícito e comprovado de coexistência, o patch é recusado.

**Exemplo 5 — regra empatada:** duas policies versionadas autorizam efeitos incompatíveis no mesmo campo. Nem o order de chegada nem uma LLM escolhem vencedor; registrar colisão e `ESCALATE_CONFLICT` até resolução por autoridade competente.

**Exemplo 6 — modpack modificado:** muda um hash/ordem ou versão de mod. Não reutilizar permissões nem `engine_instance_id` de outra build; reexecutar inventário DEC-051 e processo de migração DEC-052, com nova matriz de testes.

## 8. Isolamento, builds e limites de POC

- **Builds e ambientes:** usar Windows e baseline de BG2:EE de DEC-002/003, primeiro limpo, depois EEex/bridge, depois dois clientes. Documentar versão do motor, EEex, ordem de mods e checksums. Não prometer hooks desconhecidos. Uma regra `allow` com `tested_build_hash` vazio é inválida para qualquer write.
- **Original vs Living World:** DEC-004 mantém saves isolados. Um overlay da campanha Living World não escreve em recurso instalado nativo nem em outra campanha. No modo Original, o componente nunca altera o jogo.
- **Saves:** guardar `branch_id`, epoch, checkpoint, modpack hash, owner revision, optimistic precondition; rollback/restore sem revalidação -> sem dispatch.
- **Spoliers e privacidade:** quest states e mod manifests podem conter segredos; somente ids mínimos e reason codes autorizados em logs e prompts. Aplicar DEC-028/055/057/076/083–090.
- **Códigos de referência:** `ownership_reference.py` é função pura em fixture sintética e retorna **PREVIEW_ONLY** e **zero chamadas ao host**, mesmo quando `PROPOSE_OWNED_PATCH` aparece.

## 9. Testes de integração candidatos

**120 casos T099-001..120; TODOS NÃO EXECUTADOS.** Os testes unitários sintéticos são uma categoria diferente e **não** demonstram capacidades de jogo. Prioridades iniciais para POC: preservação de quest e mod, owners conflitantes, campos protegidos, build/modpack trocados, save/restore, 2 clientes, e patch de campo IA realmente comprovado.

### Identidade e proveniência

- **T099-001 — NÃO EXECUTADO:** Identidade persistente difere de instance_id.
- **T099-002 — NÃO EXECUTADO:** CRE igual não demonstra mesmo ator.
- **T099-003 — NÃO EXECUTADO:** Nome igual não demonstra mesmo ator.
- **T099-004 — NÃO EXECUTADO:** Instance_id reciclado exige generation e reconcile.
- **T099-005 — NÃO EXECUTADO:** Recibo host falsificado rejeitado.
- **T099-006 — NÃO EXECUTADO:** Recibo sem vínculo de origem não prova owner.
- **T099-007 — NÃO EXECUTADO:** Autoria de template separada da titularidade.
- **T099-008 — NÃO EXECUTADO:** Custódia transferida a PC prevalece.
- **T099-009 — NÃO EXECUTADO:** Duas origens reivindicam mesma instância.
- **T099-010 — NÃO EXECUTADO:** Origem UNKNOWN sempre preservada.
- **T099-011 — NÃO EXECUTADO:** Registro sem branch não é reutilizado.
- **T099-012 — NÃO EXECUTADO:** Registro sem campaign não é reutilizado.

### Conteúdo nativo e quests

- **T099-013 — NÃO EXECUTADO:** Guarda de quest nativo não recebe patch IA.
- **T099-014 — NÃO EXECUTADO:** Quest flag original não é alterada.
- **T099-015 — NÃO EXECUTADO:** Global var original não é alterada.
- **T099-016 — NÃO EXECUTADO:** Script original de área não é substituído.
- **T099-017 — NÃO EXECUTADO:** Script de companion nativo não é substituído.
- **T099-018 — NÃO EXECUTADO:** Diálogo original não é sobreposto.
- **T099-019 — NÃO EXECUTADO:** Estado de romance não recebe mutation.
- **T099-020 — NÃO EXECUTADO:** Cutscene original preserva gatilhos.
- **T099-021 — NÃO EXECUTADO:** Loot nativo não sofre cleanup IA.
- **T099-022 — NÃO EXECUTADO:** PC que matou guarda não o revive por reentrada.
- **T099-023 — NÃO EXECUTADO:** Quest futura não é disparada por matriz histórica.
- **T099-024 — NÃO EXECUTADO:** Observação de quest ausente não é inferida.

### Mods e compatibilidade

- **T099-025 — NÃO EXECUTADO:** Mod terceiro desconhecido bloqueia mudança.
- **T099-026 — NÃO EXECUTADO:** Mod terceiro identificado continua protegido.
- **T099-027 — NÃO EXECUTADO:** Mudança de versão invalida contrato.
- **T099-028 — NÃO EXECUTADO:** Mudança da ordem de mods invalida contrato.
- **T099-029 — NÃO EXECUTADO:** Mudança hash modpack invalida contrato.
- **T099-030 — NÃO EXECUTADO:** Mudança de engine invalida adapter antigo.
- **T099-031 — NÃO EXECUTADO:** Mudança EEex invalida adapter antigo.
- **T099-032 — NÃO EXECUTADO:** Mapa id divergente bloqueia ação.
- **T099-033 — NÃO EXECUTADO:** Adapter sem POC comprovada não habilita write.
- **T099-034 — NÃO EXECUTADO:** Inventário de mods não confere capability.
- **T099-035 — NÃO EXECUTADO:** Dois mods reivindicam campo -> conflito.
- **T099-036 — NÃO EXECUTADO:** Mod removido não autoriza adoção de instância órfã.

### Campos e autoridade granular

- **T099-037 — NÃO EXECUTADO:** Campo de overlay IA com licença explícita gera proposta.
- **T099-038 — NÃO EXECUTADO:** Campo de instância IA sem licença é bloqueado.
- **T099-039 — NÃO EXECUTADO:** Instância IA não ganha licença quest_flag.
- **T099-040 — NÃO EXECUTADO:** Campo player_inventory protegido.
- **T099-041 — NÃO EXECUTADO:** Campo romance_state protegido.
- **T099-042 — NÃO EXECUTADO:** Campo ai_script protegido.
- **T099-043 — NÃO EXECUTADO:** Campo plot_teleport protegido.
- **T099-044 — NÃO EXECUTADO:** Campo kill_revive protegido.
- **T099-045 — NÃO EXECUTADO:** Campo npc_speech autorado por outro módulo preservado.
- **T099-046 — NÃO EXECUTADO:** Revogação de licença impede próximos writes.
- **T099-047 — NÃO EXECUTADO:** Capacidade leitura não implica capacidade escrita.
- **T099-048 — NÃO EXECUTADO:** Permissão só vale para ação+campo+instância.

### Conflitos e precedência

- **T099-049 — NÃO EXECUTADO:** Duas regras equivalentes produzem mesma decisão.
- **T099-050 — NÃO EXECUTADO:** Prioridade narrativa não aumenta ownership.
- **T099-051 — NÃO EXECUTADO:** Prioridade computacional não aumenta ownership.
- **T099-052 — NÃO EXECUTADO:** Empate curado sem desempate explícito bloqueia.
- **T099-053 — NÃO EXECUTADO:** Versões de regras divergentes bloqueiam.
- **T099-054 — NÃO EXECUTADO:** Conflito de quest vs IA preserva quest.
- **T099-055 — NÃO EXECUTADO:** Conflito de mod vs IA preserva mod.
- **T099-056 — NÃO EXECUTADO:** Conflito de player vs IA preserva player.
- **T099-057 — NÃO EXECUTADO:** Proposta de conflito fornece reason code.
- **T099-058 — NÃO EXECUTADO:** Alteração independente segue apesar de outra bloqueada.
- **T099-059 — NÃO EXECUTADO:** Precedência só vale no mesmo campo autorizado.
- **T099-060 — NÃO EXECUTADO:** Resolver conflito não autoriza mutação automática.

### Observação e materialização

- **T099-061 — NÃO EXECUTADO:** Scan parcial não prova ausência.
- **T099-062 — NÃO EXECUTADO:** Scan UNKNOWN não prova ausência.
- **T099-063 — NÃO EXECUTADO:** Host scan completo apenas sintético não comprova runtime.
- **T099-064 — NÃO EXECUTADO:** Snapshot diverge da observação exige reconcile.
- **T099-065 — NÃO EXECUTADO:** Entidade já presente não duplica.
- **T099-066 — NÃO EXECUTADO:** Desired projection não prova ownership.
- **T099-067 — NÃO EXECUTADO:** Despawn marcado apenas REVIEW_RETIRE.
- **T099-068 — NÃO EXECUTADO:** Ator em encounter ativo não é eliminado.
- **T099-069 — NÃO EXECUTADO:** Transferência de loot sobrevive cleanup.
- **T099-070 — NÃO EXECUTADO:** Dois snapshots da mesma região preservam idempotência.
- **T099-071 — NÃO EXECUTADO:** Host observation de cliente não é host authoritative.
- **T099-072 — NÃO EXECUTADO:** Mudança de área invalida observação antiga.

### Autorizações e risco

- **T099-073 — NÃO EXECUTADO:** Consentimento de titular PC não presumido.
- **T099-074 — NÃO EXECUTADO:** PC ausente não transfere direitos.
- **T099-075 — NÃO EXECUTADO:** Risco HIGH bloqueado sem gate.
- **T099-076 — NÃO EXECUTADO:** Assinatura de LLM não é approval.
- **T099-077 — NÃO EXECUTADO:** Autorização com branch errado falha.
- **T099-078 — NÃO EXECUTADO:** Autorização de outro personagem falha.
- **T099-079 — NÃO EXECUTADO:** Owner receipt não equivale a consentimento.
- **T099-080 — NÃO EXECUTADO:** Preflight PROPOSE não executa engine.
- **T099-081 — NÃO EXECUTADO:** Action Gateway sem capability bloqueia.
- **T099-082 — NÃO EXECUTADO:** Revisão de plano invalida preflight anterior.
- **T099-083 — NÃO EXECUTADO:** Fonte proibida não é escalada por urgência.
- **T099-084 — NÃO EXECUTADO:** Recusa de jogador preservada.

### Concorrência, receipts e recuperação

- **T099-085 — NÃO EXECUTADO:** Host epoch divergente bloqueia.
- **T099-086 — NÃO EXECUTADO:** Checkpoint epoch divergente bloqueia.
- **T099-087 — NÃO EXECUTADO:** Action UNCERTAIN fica em quarentena.
- **T099-088 — NÃO EXECUTADO:** Action DISPATCHED não é reenviada após timeout.
- **T099-089 — NÃO EXECUTADO:** Recibo duplicado é idempotente.
- **T099-090 — NÃO EXECUTADO:** Recibo host antigo não confirma nova build.
- **T099-091 — NÃO EXECUTADO:** Save/load mantém propriedades e direitos.
- **T099-092 — NÃO EXECUTADO:** Restore exige reconciliar revisões e ledgers.
- **T099-093 — NÃO EXECUTADO:** Reserva de recurso não prova propriedade.
- **T099-094 — NÃO EXECUTADO:** Deadlock não libera item com despacho incerto.
- **T099-095 — NÃO EXECUTADO:** Saga compensatória não apaga quest passada.
- **T099-096 — NÃO EXECUTADO:** Falha de rede não gera owner sintético.

### Privacidade, canon e multiplayer

- **T099-097 — NÃO EXECUTADO:** Cliente remoto não confirma owner global.
- **T099-098 — NÃO EXECUTADO:** Segundo cliente não sobrescreve owner registry.
- **T099-099 — NÃO EXECUTADO:** Modo Original permanece isolado.
- **T099-100 — NÃO EXECUTADO:** Outro branch não recebe estado de campanha.
- **T099-101 — NÃO EXECUTADO:** Outro campaign não recebe segredos.
- **T099-102 — NÃO EXECUTADO:** LLM recebe somente estado autorizado.
- **T099-103 — NÃO EXECUTADO:** Logs evitam quest spoilers sensíveis.
- **T099-104 — NÃO EXECUTADO:** Fonte de testemunha protegida não vai ao adapter.
- **T099-105 — NÃO EXECUTADO:** Canon year DR não é alterado pelo reconcile.
- **T099-106 — NÃO EXECUTADO:** Textos de mod não são copiados por padrão.
- **T099-107 — NÃO EXECUTADO:** Observação read-only não concede controle de flag.
- **T099-108 — NÃO EXECUTADO:** RPA/código externo não é ativado por JSON de lore.

### POC e regressão

- **T099-109 — NÃO EXECUTADO:** BG2EE limpo usado como baseline reproduzível.
- **T099-110 — NÃO EXECUTADO:** POC EEex por build valida enumerabilidade real.
- **T099-111 — NÃO EXECUTADO:** Quest ativa observada sem mudança colateral.
- **T099-112 — NÃO EXECUTADO:** Romance ativo observado sem alteração.
- **T099-113 — NÃO EXECUTADO:** Modpack pinado 1 host 2 clientes testado.
- **T099-114 — NÃO EXECUTADO:** Rollback de test save preserva quest.
- **T099-115 — NÃO EXECUTADO:** Modpack atualizado exige novo teste completo.
- **T099-116 — NÃO EXECUTADO:** Nenhum teste sintético é alegado como POC.
- **T099-117 — NÃO EXECUTADO:** Casos sem hook retornam BLOCKED e motivo.
- **T099-118 — NÃO EXECUTADO:** Reentrada não revive NPC eliminado legitimamente.
- **T099-119 — NÃO EXECUTADO:** Inspeção estática sem runtime não aprova campo.
- **T099-120 — NÃO EXECUTADO:** Conjunto de regras produz mesma decisão sob permutação.

## 10. Critérios de saída e próxima DEC

Nenhuma implementação BG2:EE/EEex ou POC foi realizada nesta etapa. Uma SPEC futura deve validar APIs realmente existentes, cobertura de observação e autorização de `field_authority` em build pinada, com test saves, original intacto, um host e dois clientes, além de revisão de privacidade. Sem comprovação, nenhuma mutação é permitida. **DEC-100 em aberto:** adapters read-only de observação de quests/scripts e política de exposição mínima de informação para os diretores narrativos.


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Ownership de escrita por instância/campo permanece distinto de permissão de leitura; read não confere write e sem POC a leitura também bloqueia.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** DEC-101 interpretation is read-only, version-pinned and independent of gateway/host execution. A confirmed semantic milestone does not authorize actions or prove a command receipt; mod upgrades, checkpoint restore, revised mapping, epoch mismatch or contradictory states cause fail-closed reconciliation. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

DEC-102 preserva ownership DEC-099: comparação de estado não concede direitos de escrita por campo. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** observar DEC-100, interpretar DEC-101 e reconciliar DEC-102 não são eventos automaticamente propagáveis. Apenas prova semântica atual e reconciliação `CONSISTENT_WITH_PROOF` ou `APPROVED_AND_COMMITTED_REBASE` habilita pedido de admissão lógica por ruleset pinado; rebase `PROPOSE_*` não permite emissão. Proposta, autorização, receipt host e conhecimento de NPC permanecem entidades separadas. Não reabrir quest, editar flags, alterar scripts nem assumir ownership por narrativa. Dedup por occurrence/lineage, sem duplicação após save/load ou observação repetida. Consultar `docs/103-admissao-e-propagacao-causal-de-marcos-de-quests-reconciliados.md`. **Sem POC no motor.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **compensações sem overwrite de quest/mod**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para ownership protege NPCs, PC e mods contra escrita epistêmica indevida, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para ownership por campo impede writes automáticas em mod/PC/quest, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Ownership de bem do jogador prevalece sobre texto de contrato. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Ownership por instância/campo protege bens e scripts de outros mods. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Garantia exige ownership por instância e campo, build e modpack; item nativo de quest e outro mod são bloqueados sem autorização explícita.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
