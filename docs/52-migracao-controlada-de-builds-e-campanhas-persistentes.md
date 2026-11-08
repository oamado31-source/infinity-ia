# DEC-052 — Migração controlada de builds e campanhas persistentes

**Versão:** Infinity AI Discovery v4.8  
**Escolha:** opção C, aprovada em 2026-11-06 — ADR-0047.  
**Natureza:** arquitetura e critérios candidatos para futuras SPECS/POCs, não ferramenta implementada nem compatibilidade comprovada.

## 1. Objetivo

Permitir avaliar se uma campanha Living World pode evoluir de uma **build A** para uma **build B** mantendo os saves mecânicos de BG2:EE, eventos confirmados, personagens, scripts/quests, romances, relações, tempo DR, inventário de mods e políticas da campanha. **Preservação da campanha tem prioridade sobre adoção da atualização.** A atualização é opt-in, controlada e reversível por restauração de cópia previamente comprovada, não por suposto undo de mods.

**Fora de escopo:** atualizar instalações ativas em tempo real, sobrescrever saves de produção em POC, automatizar conversão de qualquer mod, redistribuir conteúdo de terceiros, garantir compatibilidade EET/IWD/NWNForBG, prometer migração de estados que o motor não expõe, afirmar rollback transacional multi-sistema.

## 2. Camadas de integridade e suas fontes

| Camada | Referência da campanha | Evidência exigida | Quem confirma |
|---|---|---|---|
| Build e mods | `build_id`, fingerprint, ordem, versão e hashes | Manifesto DEC-051, captura read-only e diffs | Scanner/curadoria **não** confirmam runtime |
| Save mecânico | Slot/save, hash, timestamp e revisão observável | Cópia íntegra, carga/re-salvamento e pós-condições | Host BG2:EE, nos limites demonstrados |
| Mundo narrativo | Event log e snapshot vinculados a `campaign_id` | Integridade do log, revisões, IDs e referências | Serviço narrativo validado; nunca substitui host |
| Quests/scripts/romances | Recursos da build + estados runtime observáveis | Dependências curadas, flags comprovadas, testes de progressão | Preflight DEC-050 + host nas ações efetivas |
| NPCs, facções, cronologia | Snapshots, ações confirmadas e regras versionadas | Causalidade, relógio, identidade e histórico preservados | Motor confirma físicos, simulador confirma só projeções |
| Multiplayer | Estado do host e clientes | Dois clientes, save/load, ressincronização, slot/party | Gate experimental, nunca pressuposto |
| Autorizações | Política de campanha, concessões e versão | Revisão de permissões e assinatura/log de decisão do anfitrião | Anfitrião para promoção; gateway para ações |

Uma build com arquivos aparentemente iguais pode ter saves de estado diferente. Um save que abre pode ter quests interrompidas. Um log narrativo íntegro não prova que o motor aplicou as consequências. **Os três casos devem ter testes separados.**

## 3. Máquina de estados candidata

```text
PINNED_BUILD_A (campanha operacional)
       └─ solicitação de avaliação de B ──> CANDIDATE_B_ISOLATED
                                           │
                                           v
                                     DIFF_AND_CURATE
                                       │      └─ UNKNOWN/CONFLICTED crítico → BLOCKED
                                       v
                                  CHECKPOINT_SOURCE
                                       │      └─ backup incompleto → BLOCKED
                                       v
                                     DRY_RUN_B
                                       │      └─ regressão/falha → BLOCKED
                                       v
                                  VALIDATION_GATES
                                       │      └─ falha ou teste ausente → BLOCKED
                                       v
                                  HOST_APPROVAL
                                       │      └─ negado/ausente → KEEP_A
                                       v
                                PROMOTION_CONTROLLED
                                       │      ├─ pós-condição OK → PINNED_BUILD_B
                                       │      └─ falha/UNCERTAIN → FREEZE_AND_RECONCILE
                                       v
                             Audit log + checkpoint IDs
```

`BLOCKED`, `KEEP_A` e `FREEZE_AND_RECONCILE` são resultados de **política proposta**, não estados do BG2:EE. Nenhuma operação precisa ser materializada no motor para registrar uma tentativa rejeitada. Troca de build nunca deve ser inferida apenas do texto de um diálogo ou do LLM.

## 4. Contratos de dados candidatos

```text
BuildManifest {
  build_id, game_edition, engine_version_evidence,
  installed_components[{mod_id, version_evidence, install_order, source}],
  resource_fingerprints, scan_version, unknown_components,
  captured_at, provenance, privacy_scope
}
CampaignBinding {
  campaign_id, mode, active_build_id, campaign_policy_revision,
  host_save_ref, narrative_state_revision, catalog_revision,
  pending_actions, verified_checkpoint_id
}
CheckpointCandidate {
  checkpoint_id, campaign_id, build_id, save_ref, save_hash,
  narrative_snapshot_ref, event_log_watermark,
  policy_revision, runtime_observation_ref, integrity_status
}
MigrationAttempt {
  attempt_id, campaign_id, source_build_id, target_build_id,
  diff_ref, backup_checkpoint_id, migration_plan_revision,
  tests[{gate_id, status, evidence_ref}], blockers[],
  host_approval_ref, result, reconciliation_ref
}
```

Esses contratos são apenas um modelo lógico para SPECS; não são formatos finais, nem instruções executáveis, nem suporte comprovado a leitura de memória/flags do jogo. Nunca armazenar conteúdo de saves e segredos em logs públicos.

## 5. Pipeline de migração e controles

1. **Pin da build A:** campanha ativa referencia conjunto fixo de jogo/mods. Suspender ações durante uma eventual janela de promoção; não supor hot migration.
2. **Capturar estado A:** guardar evidências do build, saves mecânicos consistentes, eventos do Infinity AI, snapshots, pendências `UNCERTAIN`, relógio e permissões. Caso ações pendentes não possam ser conciliadas, **não prosseguir**.
3. **Criar B isolada:** instalar/atualizar componentes somente em pasta/ambiente separado, com ordem e hashes próprios. Não modificar arquivos da instalação principal nem o save original.
4. **Calcular delta:** comparar recursos, dependências, quests, diálogos, NPCs, identificadores e catálogos de A/B; marcar desconhecidos, incompatibilidades e mudanças não mapeadas.
5. **Plano de transformação:** se necessário, preparar mapeamentos explícitos e versionados de dados externos; transições mecânicas de saves somente quando ferramentas testadas permitirem. Proibir reinterpretações retroativas de eventos confirmados sem autorização.
6. **Dry-run com cópias:** verificar carregamento em B, áreas, exploração, diálogos relevantes, progressão de quests/romances, inventário, experiência, status de PCs, NPCs recrutáveis e desfechos locais; repetir save/load.
7. **Validação multiplayer:** observar host e dois clientes em pontos equivalentes, entrada/saída, Character Arbitration quando relevante e ressincronização. Falha aqui bloqueia promoção.
8. **Aprovação explícita:** apresentar diferenças, riscos e resultados; anfitrião decide se promove B. A autorização não substitui os testes obrigatórios.
9. **Promover apenas par coerente:** associar nova build a save e projeção narrativa compatíveis, registrar commit e verificar pós-condições. Se incerto, congelar e reconciliar; nunca declarar sucesso por timeout.
10. **Recuperação:** caso tenha ocorrido efeito danoso, restaurar **o conjunto** de backup validado da build A e dos estados ligados, com auditoria. Evitar restaurar apenas save ou apenas banco narrativo quando isso cria divergência.

**Política de fail-closed:** atualização disponível não implica atualização exigida. Se não houver migração comprovada, a campanha permanece ativa em A. Reverter nunca significa apagar escolhas confirmadas sem registrar a linha de recuperação e a autorização do anfitrião.

## 6. Categorias de compatibilidade para um relatório de migração

| Categoria | Condição | Ação |
|---|---|---|
| `UNCHANGED` | Identidades e dependências verificadas | Ainda exige gates básicos de save e multiplayer |
| `CHANGED_MAPPED` | Mudanças cobertas por migração específica testada | Exige dry-run + regressão pertinente |
| `ADDED_NONCONFLICTING` | Novo conteúdo presente sem colisão conhecida | Exige verificação de progresso/condições e gates |
| `REMOVED_OR_REORDERED` | Mod alterado, removido ou reordenado | Elevado risco; bloquear até prova específica |
| `UNKNOWN_OR_CONFLICTED` | Cobertura parcial, scripts desconhecidos, estados não observáveis | Bloqueio conservador de publicação |
| `FAILED_TEST` | Save, quest, state ou multiplayer não passou | Não promover; manter build antiga |

As categorias são propostas para classificação de mudanças, não certificações genéricas. Resultados dependem do par específico de builds e da campanha.

## 7. Critérios de promoção (todos exigidos conforme escopo validado)

- Build B isolada, manifesto completo o bastante para mudanças relevantes e comparação preservada.
- Backup da campanha A íntegro e **restauração ensaiada** em cópia de teste.
- Nenhuma operação mecânica pendente não reconciliada; sem `UNKNOWN` crítico ou incompatibilidade não mapeada.
- Evidências de preservação dos IDs e relações de PCs/NPCs, inventário, quests/romances ativos e regras/cânone.
- Cópia do save carrega, progride e salva novamente na build B em teste.
- Logs narrativos e snapshots relacionados a eventos confirmados não duplicam transações ao reabrir.
- Teste com pelo menos host e dois clientes; resultados por cenário de save/load e reconexão.
- Configurações de Original e Living World não são cruzadas; segredos e permissões preservados.
- Autorização explícita do anfitrião antes da troca da referência ativa, com pós-condições e auditoria.

**No-go automático:** falha de backup; impossibilidade de restaurar cópia; dependência crítica desconhecida; incompatibilidade de save; quest/romance travado; divergência multiplayer; `UNCERTAIN` não conciliado; ausência de aprovação.

## 8. Vinte testes candidatos (não executados)

| ID | Cenário | Resultado esperado |
|---|---|---|
| T-052-01 | Manter build A após disponibilidade de patch | Nenhuma alteração silenciosa na campanha |
| T-052-02 | Atualizar cópia isolada | Hash da instalação/save A permanece igual |
| T-052-03 | Mod instalado em outra ordem | Fingerprint e relatório detectam a diferença |
| T-052-04 | Build B contém recursos novos conhecidos | Inventário curado identifica novas dependências |
| T-052-05 | Scanner incompleto | Classificação `UNKNOWN`, sem aprovação indevida |
| T-052-06 | Remoção de mod que define quest ativa | Migração bloqueada até solução testada |
| T-052-07 | Alteração de identificador de NPC | Mapeamento verificado ou bloqueio |
| T-052-08 | Romance ativo usa condição alterada | Regressão obrigatória; falha bloqueia publicação |
| T-052-09 | Checkpoint não inclui snapshot narrativo | Não promover nem declarar rollback pronto |
| T-052-10 | Backup gravado com erro | Detectar corrupção e manter build A |
| T-052-11 | Cópia restaura e abre em A | Integridade/recuperabilidade comprovadas |
| T-052-12 | Save abre em B mas quest não progride | Falha funcional; bloquear promoção |
| T-052-13 | Save abre e grava em B com NPC duplicado | Falha de identidade; bloquear |
| T-052-14 | Host e cliente exibem estado divergente | Falha de sincronização; não promover |
| T-052-15 | Dois clientes reentram após save/load | Verificar party, itens e estados, sem assumir sucesso |
| T-052-16 | Evento confirmado duplicado no replay | Deduplicar/conciliar; sem alteração dupla |
| T-052-17 | Operação de migração termina em timeout | `UNCERTAIN`, congelar e reconciliar antes de retry |
| T-052-18 | Anfitrião recusa migração aprovada por testes | Build A permanece ativa |
| T-052-19 | Migração autorizada e verificada | Registrar novo vínculo e desativar autorizações obsoletas |
| T-052-20 | Falha após promoção controlada | Recuperar par coerente aprovado, com evidência e auditoria |

## 9. Riscos e integrações pendentes

- **Save BG2:EE pode não ser portátil** entre versões/ordens de mods; suporte de carregamento, não de conclusão de campanhas, é insuficiente.
- **Não há commit atômico comum** entre save do motor, banco narrativo, dados de mods e vários clientes. O protocolo de checkpoint/reconciliação exige DEC-053 e SPECS.
- **Retenção de versões antigas** pode exigir armazenamento, licenças e acesso a instaladores/arquivos. Não pressupor possibilidade de redistribuição de ativos.
- **Compatibilidade externa** (EEex/EET/IWD/NWNForBG) depende de ensaio específico e baseline reproduzível; não rotular modpacks como oficialmente suportados por inferência.
- **Privacidade:** logs/manifests/backups podem conter dados locais do computador e histórias secretas; limitar acesso e material extraído.
- **Decisões conexas em aberto:** DEC-013 (versões/matriz), DEC-015 (gates de testes), DEC-018 (retenção/recuperação), DEC-053 proposta (coordenação de checkpoints).

**Próxima decisão candidata:** DEC-053 — como construir checkpoints coerentes e restaurar campanhas quando o save BG2:EE e os registros narrativos externos evoluem em ritmos diferentes.

## 10. Complemento aprovado — DEC-053 (Discovery v4.9)

A DEC-053 aprovou o protocolo lógico de **checkpoint coordenado**: migração da build A depende de um par publicado e verificado (`save_ref/hash` + `narrative_snapshot`/watermark), associado ao manifest e política da campanha. Em ambiente B isolado, ensaiar e publicar um novo par coerente somente após gates e aprovação do anfitrião; jamais promover candidato incompleto. Caso falhe, usar cópias e pares verificados da build A, sem assumir undo atômico ou converter estado narrativo mais recente em flags antigas. Comandos `UNCERTAIN` devem ser reconciliados antes de ensaio/promoção. A DEC-018/054 ainda definirá cadência e retenção dos backups.


## Complemento aprovado — DEC-054 (Discovery v5.0)

O backup de pré-migração precisa ser feito de **checkpoint publicado DEC-053** com cadeia de dependências, e deve receber proteção de retenção (`pin`) enquanto for necessário restaurar a build A. A adoção da build B não apaga essa reserva por simples sucesso de carregamento. DEC-054 acrescenta segunda cópia opcional e ensaios isolados de restauração; checksums apenas não atestam progressão de quests. Ver ADR-0049/doc. 54.

## Integração posterior — DEC-055 (Discovery v5.1)

Uma mudança de build invalida sondas e políticas de fallback associadas ao fingerprint anterior; falhas durante migração bloqueiam promoção e preservam a build A. World Health Monitor fornece diagnóstico, mas não autoriza atualização automática ou restauração em produção. Ver ADR-0050/doc. 55.

## Integração DEC-063/C — pin distinto para revisão de conhecimento (v5.9)

O pin da **build de jogo/mods** desta DEC-052 e o pin do **knowledge pack** DEC-063 são vínculos distintos, ambos associados à campanha/ramo/checkpoint. Uma atualização apenas de lore não equivale a migração de save ou instalação; se exigir flags, recursos ou scripts, os gates mecânicos desta DEC-052 continuam obrigatórios. A publicação curada DEC-062 não muda automaticamente nem a build nem o pack da campanha. É indispensável diff de impacto, autorização do host, referências anuais válidas DEC-060, proveniência DEC-061 e recuperação coerente DEC-053/054. Não afirmar suporte a hot-swap ou save migration sem POC.


### Migração de memórias NPC — DEC-065/C (Discovery v6.1)

Migração preserva referência das sínteses a eventos de origem, classificações de proteção, ACL e identidade lógica/branch; qualquer incompatibilidade invalida projeções derivadas até revalidação. Não misturar memória de NPC homônimo após mudança de build. Reconciliação de identidade permanece DEC-066. Cânone DEC-060 continua segregado por ano DR.

### Integração DEC-066/C — invalidação de identidade entre builds (v6.2)

Ao migrar build/mods, não migrar cegamente `VerifiedBinding` para a instalação B. Revalidar cada vínculo afetado com fingerprint, observações, evidência e checkpoint. Identidade narrativa lógica e episódios permanecem, mas memórias privadas não podem ser atribuídas a nova instância runtime sem reconciliação. `STALE`/`AMBIGUOUS` impedem uso personalizado; nenhuma capacidade de migração real foi demonstrada.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

Migração DEC-052 invalida correspondência de NPCs genéricos até prova DEC-066. Promoções DEC-067 e referências a população agregada dependem da revisão de build; não remapear memórias por nome.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

Migrar save/build com NPC offscreen DEC-068 requer versionar estado, pendências, watermarks e provas de identidade; não transportar jobs stale entre forks ou sobrescrever quest/party. Dependências de engine não testadas devem ser bloqueadas.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: ao mudar build/mod, invalidar planos/refs de presença dependentes de áreas e rotas; revalidar checkpoint/branch/KPack; nenhuma materialização migrada automaticamente.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Uma migração altera capabilities de encontros DEC-071: invalidar handoffs pendentes e exigir revalidação de área, scripts, identidade, branch e receipts antes de qualquer operação. Nunca transportar resultado incerto de build anterior.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Migração DEC-052 deve revalidar todos os templates/componentes DEC-072 usados por incidentes pendentes, sob novo fingerprint e revisão; não hot-swap sem checkpoint/rollback testados.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Migração invalida planos de cleanup e adapters associados a fingerprints anteriores; revalidar antes de operar em campanha persistente.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Mudança de mods/versão invalida capacidades mecânicas de autoridade e casos pendentes DEC-078 precisam de revalidação de build, fonte de política e checkpoint.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Mandados pendentes DEC-079 carregam fingerprint/build/época/branch; mudança de mods ou área exige revalidação antes de ação mecânica, não transporte cego entre builds.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Migração invalida planos de reparação com adapter de build anterior; revalidar ownership, effects/receipts e checkpoint antes de executar.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-084/C — Discovery v8.0

Mudança de build invalida adapters e planos em voo; reconciliar identidade, abrigo, rota e recursos antes de aplicar medidas.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Mudança de build exige reconciliação dos vínculos persistentes com identidade e recursos nativos; migrations não convertem compromisso social em alteração de script.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Migração de build deve reconciliar contratos e receipts sem reatribuir itens, NPCs ou faction flags por novo nome/resref.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Migração de build conserva versões da evidência, fonte e parecer; capability ausente em build destino não vira detector de mentira ou item de prova implementado.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Migrar views/dossiês por manifestos, campaign/branch e KPack, mantendo snapshots e recibos anteriores; não prometer compatibilidade de journal/documentos sem POC.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Nova build altera capabilities; aprovações/reservas antigas não podem ser reaplicadas sem revisão da instalação e seus manifests.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Mudanças de build durante operação invalidam capabilities e despacho posterior; reconciliar sessões antes de retomar, sem migrar estado inseguro.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Ao migrar build, invalidar epochs/tokens de scheduler e reconciliar claims/receipts com o novo manifest antes de admitir operações.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Troca de build/adapter invalida sessões e epochs do scheduler; reabrir operações bloqueadas exige reconciliar recursos e validar capabilities, não migrar tokens velhos.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Alterar mods/EEex/bridge invalida permissões de runtime e exige migração, testsave, reconciliar old engine IDs e fingerprints.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Migração de build invalida manifestos, caches e mapeamentos semânticos de quests não revalidados.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Catalogues by exact build/modpack/quest/script fingerprint, curated proof of semantic milestone and valid transition; an observed flag or stage is never an authorized quest write or host receipt. On patch or restore, invalidate semantic cache and avoid generic stage inference. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **log transacional**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para migração invalida receipt/ACL incompatíveis sem apagar histórico, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para mudança de modpack invalida capabilities não certificadas, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
