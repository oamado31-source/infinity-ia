# 73 — Pós-encontro: ownership, persistência seletiva e limpeza segura

**Estado:** desenho técnico candidato para Discovery v6.9; DEC-073/C aprovada em `ADR-0068`. **Nada implementado ou testado** no BG2:EE/EEex/multiplayer. 50 testes `T073-*` abaixo são **propostas**. DEC-060 a DEC-072 e seus ADRs permanecem intactos.

## 1. Objetivos e fronteiras

O encerramento de um encontro local exige conciliar: o ledger do incidente DEC-070/071; o catálogo de templates/componentes DEC-072; receipts mecânicos do host DEC-011/012; memória e identidade NPC DEC-064–068; scripts/quests nativos DEC-050; checkpoints DEC-053/054; e campanhas/Knowledge Packs DEC-060–063. **Não tratar componentes como descartáveis por serem visíveis temporariamente**, nem declarar preservação física por inferência narrativa.

O ciclo de vida pós-encontro é separado do ciclo de vida do *asset* instalado. Ex.: um template pode referir `.CRE` de outro mod, mas a licença, o arquivo e a instância no motor têm responsabilidades diferentes; nunca modificar ou apagar arquivos de mod por “limpar encontro”.

## 2. Glossário e matriz de propriedade

| Categoria candidata | Exemplos conceituais | Default seguro | Condição para cleanup |
|---|---|---|---|
| `NATIVE_OR_MOD` | ator de quest, objeto do mapa, script/área de conteúdo instalado | `PRESERVE` | Não elegível por este mecanismo; exigir procedimento próprio de mod/build e autorização especial, fora do escopo atual |
| `ENCOUNTER_TEMP` | marcador/ator temporário criado por adapter validado e rastreado | `PENDING_RECONCILE` | Ownership comprovado + estado observado + adapter POC + receipt host + risco e checkpoint |
| `ENCOUNTER_PERSISTENT` | personagem individual com continuidade legitimada | `PRESERVE` | Não remover por mero encerramento; decisão específica de lifecycle |
| `TRANSFERRED_TO_PLAYER_OR_WORLD` | item coletado, recurso incorporado ao mundo/quest | `PRESERVE` | Propriedade antiga revogada; limpar só se novo owner autorizar por contrato distinto |
| `UNKNOWN/CONTESTED` | ator indistinguível, nome repetido, asset/instância sem prova | `BLOCK_UNCERTAIN` | Não operar enquanto houver dúvida |

A propriedade é específica **da instância observada**, não do nome do recurso; `owner_kind`, `origin_kind`, `owner_id` e transferência de posse precisam de auditoria. Não supor spawn nem cleanup habilitados.

## 3. Contratos candidatos (não definitivos)

```json
{
  "EncounterClosurePlan": {
    "campaign_id": "...", "branch_id": "...", "incident_id": "...", "encounter_id": "...",
    "resolution_epoch": 1, "checkpoint_epoch": 1,
    "build_fingerprint": "...", "catalog_revision": "...",
    "incident_lease_fence": "...", "idempotency_key": "...",
    "host_observation_ref": "...", "confirmed_result_receipts": ["..."],
    "proposed_effects": [], "component_dispositions": [],
    "policy_decision": "PENDING_VALIDATION"
  },
  "ComponentDisposition": {
    "component_instance_id": "...", "resource_ref": "...",
    "origin_kind": "ENCOUNTER_TEMP", "owner_kind": "ENCOUNTER", "owner_id": "...",
    "ownership_evidence_refs": ["..."], "transfer_receipt_ref": null,
    "engine_observation_ref": "...", "validated_capability_ref": "...",
    "requested_action": "NO_OP", "risk_class": "UNKNOWN"
  },
  "EffectReceiptLink": {
    "effect_id": "...", "mechanical_host_receipt_ref": "...",
    "narrative_event_ref": "...", "campaign_revision": "...",
    "commit_state": "UNCOMMITTED"
  }
}
```

Campos, tipos, IDs, armazenamento, locking e schema exatos ficam para SPECS; exemplos são ilustrativos, não APIs existentes.

## 4. Estados sugeridos de encerramento

`ENCOUNTER_ACTIVE` → `CLOSURE_PROPOSED` → `OBSERVED_AND_CLASSIFIED` → `WAITING_GATES` → `CLOSURE_PREPARED` → `CLEANUP_PENDING` → `RECONCILING` → `CLOSED_CONFIRMED`.

Ramificações: `BLOCKED_UNSUPPORTED`, `BLOCKED_UNCERTAIN`, `ABORTED_WITHOUT_EFFECTS` e `MANUAL_REVIEW`. A ordem real, as transições atômicas e o suporte de engine não estão definidos. **`CLOSED_CONFIRMED` exige receipts e ledger compatíveis; nunca apenas um texto de LLM.**

**Invariantes:**

1. Um `(campaign, branch, incident, resolution_epoch)` tem no máximo um fechamento válido.
2. O fechamento mantém a exclusão entre resolvedor offscreen e encontro local DEC-071 até reconciliar.
3. Toda alteração mecânica precisa de receipt do host da época/build/checkpoint corretos.
4. Uma tentativa de limpeza não pode atingir componentes `NATIVE_OR_MOD`, `TRANSFERRED...` ou `UNKNOWN`.
5. A reexecução de um job deve ser idempotente para o ledger; operações mecânicas com resultado incerto não são reemitidas.
6. Eventos narrativos confirmados são persistidos em overlay por campanha/ramo e jamais no cânone anual físico DEC-060.
7. A ausência de limpeza não invalida automaticamente efeitos mecânicos já confirmados; gera pendência/alerta em separado.

## 5. Fluxo proposto de encerramento seguro

1. **Congelar revisão causal:** verificar incident lease/epoch e build/checkpoint atuais, origem do template e região; rejeitar branch/host/client defasado.
2. **Observar estado host:** coletar, via interface testada, apenas o estado que o motor realmente expõe. Se não houver observação segura, marcar `UNKNOWN`; não adivinhar mortos, drops ou inventários.
3. **Classificar recursos e transferências:** combinar manifesto DEC-072, recibos de instanciação/observação, propriedade, inventário transferido e scripts de quest; marcar `CONTESTED` quando identificador for reciclado ou faltar referência.
4. **Separar disposições:** `PRESERVE`, `NO_OP`, `ARCHIVE_NARRATIVE`, `REQUEST_CLEANUP` ou `BLOCK_UNCERTAIN`. Nenhuma remoção em `REQUEST_CLEANUP` sem adapter tipado e POC para essa função, build e modo multiplayer.
5. **Validar risco e consentimento:** conferir LOW/MEDIUM/HIGH pelo efeito agregado, DEC-027/034/041; detalhes de itens de PCs ausentes exigem política de consentimento. Qualquer HIGH default-deny.
6. **Criar checkpoint coordenado:** associar intenção de cleanup a log durável e ponto consistente DEC-053/054. Não afirmar transação atômica motor/banco que não tenha sido demonstrada.
7. **Aplicar operação permitida:** Action Gateway DEC-012 passa pedido tipado ao host apenas se capability permitida. Resultado deve ser observado/confirmado; timeout gera `UNCERTAIN` e proíbe retry cego.
8. **Conciliar efeitos:** cada `EffectReceiptLink` é incorporado uma vez, sem duplo XP/loot/quest/reputação. Memórias NPC não são substituídas por remoção de uma representação física.
9. **Liberar exclusividade:** somente após prova de término ou política explícita de abort sem efeitos. Limpeza pendente não pode ressuscitar o resolvedor distante para repetir o incidente.
10. **Registrar auditoria redigida:** hash/revisão/risco/resultados/pendências, preservando ACL e segredos; falha operacional notifica Health Monitor DEC-055.

## 6. Save/load, crashes, migrações e rollback

- **Save/load:** checkpoint_epoch antigo invalida plano; reobservar instâncias, effects, inventory e flags antes de continuar. Não remover objetos que possam ter sido coletados antes do save.
- **Crash ou disconnect:** qualquer operação destrutiva em voo é `UNCERTAIN`. Consultar host/ledger antes de decidir; não repetir `DELETE` por timeout.
- **Restore:** branch restaurado não herda efeitos, limpeza ou reservas de futuro distinto; associar todo receipt a timeline/checkpoint.
- **Migração de build:** fingerprints alterados invalidam adapters; não executar cleanup nem “consertar” com scripts LLM. DEC-052 pode requerer plano de migração independente.
- **Multiplayer:** host controla, clientes recebem estado confirmado. Verificar reconexões, divergência de asset e idempotência sem atribuir autoridade a nó LAN.
- **Retenção:** histórico causal e anchors de memória podem requerer guarda; logs operacionais devem ser mínimos e redigidos, sob política específica, sem telemetria automática.

## 7. Proteção de conteúdo nativo, loot e NPCs

Um corpo, baú, portal, criatura ou item **observado** após combate não é automaticamente temporário do Infinity AI. `resource_ref`/nome de actor/CRE não identifica a propriedade da instância. Checar transferências legítimas antes de cleanup; item no inventário de jogador ou objeto utilizado por quest nunca se apaga como resíduo de encounter. Personagens persistentes DEC-064–068 mantêm identidade mesmo com instância física ausente. Alterações em missões/romances/scripts nativos DEC-050 exigem gates específicos e não são inferidas a partir de narrativa.

## 8. Matriz resumida de decisão

| Evidência | Origem/owner | Capability | Decisão |
|---|---|---|---|
| Host confirma componente temporário ainda presente | `ENCOUNTER_TEMP` comprovado | cleanup HOST_MP_VERIFIED para build e ação | Candidato a limpeza após risco/gates/checkpoint |
| Host confirma transferência ao jogador | `TRANSFERRED...` | qualquer | `PRESERVE`; ownership antigo revogado |
| Ator é nativo ou pertence a outro mod | `NATIVE_OR_MOD` | qualquer | `PRESERVE` |
| Origem/instância ambígua | `UNKNOWN/CONTESTED` | qualquer | `BLOCK_UNCERTAIN` |
| Não há POC da operação | `ENCOUNTER_TEMP` comprovado | `PRESENT` apenas | `BLOCKED_UNSUPPORTED`, sem simular cleanup |
| Operação em voo com timeout | qualquer | qualquer | `BLOCKED_UNCERTAIN`, reconciliar antes de agir |
| Evento encerrado e todos os efeitos reconciliados | — | — | fechar ledger uma única vez, sem efeitos implícitos |

## 9. Matriz de testes candidatos — 50 casos, NENHUM EXECUTADO

| ID | Cenário esperado |
|---|---|
| T073-01 | Catálogo sem capabilities de cleanup não permite comando destrutivo. |
| T073-02 | Componente de origem nativa não pode ser excluído pelo plano pós-encontro. |
| T073-03 | Recurso de outro mod não herda ownership do Infinity AI. |
| T073-04 | Identificador CRE igual em duas instâncias não prova que ambas são temporárias. |
| T073-05 | NPC homônimo sem identidade verificada nunca perde memória/instância. |
| T073-06 | Ator ENCOUNTER_TEMP sem receipt de criação fica pendente e não é removido. |
| T073-07 | Ator temporário com ownership provado e adapter validado é somente candidato, sujeito a gates. |
| T073-08 | Componente UNKNOWN/CONTESTED impede operação de cleanup. |
| T073-09 | Objeto transferido a inventário de jogador deixa de ser elegível à limpeza. |
| T073-10 | Recurso tornado relevante para quest não é removido como resíduo. |
| T073-11 | Drop já coletado pelo grupo não é apagado ao encerrar encontro. |
| T073-12 | Sobrevivente individual mantém identidade e relação após limpeza de marcador temporário. |
| T073-13 | Fim narrativo sem receipt não atribui morte, loot ou XP. |
| T073-14 | Host receipt legítimo associa resultado ao incidente uma única vez. |
| T073-15 | Receipt de cliente multiplayer é insuficiente para fechar efeito mecânico. |
| T073-16 | Receipt de worker LAN é rejeitado como prova de engine. |
| T073-17 | Receipt de outra branch não autoriza cleanup. |
| T073-18 | Receipt de outro checkpoint é rejeitado. |
| T073-19 | Receipt de build incompatível invalida plano. |
| T073-20 | Template atualizado depois do encontro não altera ownership retroativamente. |
| T073-21 | Dois workers concorrentes não obtêm fechamento simultâneo. |
| T073-22 | Fencing antigo não consegue liberar reserva do incidente. |
| T073-23 | Reentrega do mesmo job não duplica XP, loot nem efeito narrativo. |
| T073-24 | Timeout após operação de cleanup passa a UNCERTAIN sem segunda emissão. |
| T073-25 | Save/load entre observação e plano exige nova observação host. |
| T073-26 | Crash com cleanup em voo mantém ledger e reserva em modo seguro. |
| T073-27 | Reconciliação após reconnect distingue já removido de ainda presente. |
| T073-28 | Restore de backup descarta effects/cleanup pertencentes ao futuro abandonado. |
| T073-29 | Migração de mods invalida adapters de cleanup obsoletos. |
| T073-30 | Área nativa com objeto estático não é tratada como resíduo do encontro. |
| T073-31 | Operação MEDIUM sem autorização exigida permanece bloqueada. |
| T073-32 | Operação HIGH de remoção é negada por padrão. |
| T073-33 | Conjunto de operações LOW com impacto HIGH é reclassificado. |
| T073-34 | Item de PC ausente não sofre remoção sem consentimento e host. |
| T073-35 | Encontro não elegível para cleanup permanece fechado com pendência operacional rastreável. |
| T073-36 | Pendência de limpeza não permite resolução offscreen repetida. |
| T073-37 | Cancelamento sem efeitos permite liberação somente após reconciliar. |
| T073-38 | Cleanup não apaga episódio ou memória crítica do NPC. |
| T073-39 | Cleanup não altera diretórios físicos 1369-DR ou 1370-DR. |
| T073-40 | Conhecimento do NPC não se atualiza automaticamente a partir do arquivo canônico. |
| T073-41 | Overlay de campanha não é escrito na biblioteca de templates. |
| T073-42 | Worker sem ACL não recebe receipts com segredos da party. |
| T073-43 | Logs redigidos não contêm segredos de PC ou conteúdo protegido. |
| T073-44 | Quota/backpressure pode adiar cleanup sem alterar o estado de engine. |
| T073-45 | Sobrecarga não libera fencing prematuramente nem cria tempo fictício. |
| T073-46 | Save de host e overlay narrativo discordantes exigem reconciliação bloqueante. |
| T073-47 | Host+dois clientes devem observar resultado único mesmo após reconexão. |
| T073-48 | Capacidade apenas PRESENT/STATIC_VALIDATED não habilita DELETE em runtime. |
| T073-49 | Falha de backup ou checkpoint bloqueia cleanup arriscado antes de executar. |
| T073-50 | Fim de encounter não desencadeia repercussão global de facção/economia sem gates causais. |

**Todos os 50 testes são candidatos para SPECS/POCs, não resultados.** Definir fixtures, critérios de aprovação, builds, interface efetiva do motor, política de sigilo e testes host+dois clientes antes de habilitar qualquer cleanup.

## 10. Próxima decisão — DEC-074 (aberta)

**Repercussão causal das consequências confirmadas de encontros:** A) manter impactos exclusivamente locais; B) atualizar imediatamente todas as facções, reputações e mercados; **C, recomendada)** propagar seletivamente consequências com causalidade documentada, trajetos de informação, contexto regional, atraso, risco/autorizações e idempotência. Reputação, rumor, economia e política seguem regras distintas (DEC-029/030/032/033); um NPC distante não ganha conhecimento instantâneo.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

DEC-074 começa com efeitos pós-encontro reconciliados; cleanup DEC-073 não apaga testemunhos nem concede automaticamente reputação, economia, autoria ou fama global. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Fechamento e cleanup não apagam evidência de contribuição, autoria ou testemunho; itens do host não recebem novos donos por atribuição narrativa.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Limpeza de instância temporária não apaga persona e histórico narrativo legítimos; não transferir alias para novo personagem por reaproveitamento de nome.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Efeito de decisão judicial/faccional DEC-078 deve ser confirmado e persistido seletivamente; cleanup de encounter não apaga evidência ou restaura item por texto.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Restituição pós-injustiça DEC-081 verifica ownership e transferências confirmadas DEC-073 para não duplicar item nem apagar item de terceiro.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-084/C — Discovery v8.0

Fim de encontro de escolta mantém memórias/risco/identidade e efeitos confirmados; cleanup apenas recursos temporários comprovados.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Fechamento/limpeza de encontro não apaga pistas ou memórias legítimas, nem expõe rota privada ou destrói fonte protegida.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Objetos de isca só são limpos quando realmente instanciados pelo host e reconhecido ownership; claims persistentes não desaparecem com limpeza de instância.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Fim de encontro não apaga compromissos narrativos persistentes, mas nenhum NPC temporário recebe vínculo por reaproveitamento de nome.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Limpeza pós-encontro não apaga contrato/contato narrativo legítimo; ressurgir NPC temporário não duplica fonte ou dinheiro.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Depois do encontro, fatos comprovados por host são distintos de rumores sobre suas causas; limpeza preserva evidência auditável e não duplica mérito.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-091/C — Discovery v8.7

Resultado/custo pós-encontro depende de evidência e ownership, sem apagar objetos nativos ou duplicar loot ao reconciliar.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Aborto não apaga cenas e assets próprios já confirmados; cleanup precisa de ownership e host receipt, recursos UNCERTAIN são isolados.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Limpeza de instância e liberação de recurso após encontro só ocorrem com ownership e receipt confirmado, nunca por expiração genérica de lease.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Cleanup não é compensação automática de deadlock. Preservar efeitos host-confirmed e ownership, sem apagar cena ou loot por liberação de lease.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-096/C — Discovery v9.2

DEC-096/C não limpa/recria NPC após efeito; segue lifecycle, ownership e dedup pós-encontro DEC-073.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Expirar modificador DEC-097/C não apaga NPC/objeto já confirmado no encontro; ownership/persistência prevalecem.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

REVIEW_RETIRE do DEC-098 não é DELETE: observar ownership, loot, transferências, quests, consentimento e recibo host conforme DEC-073.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Cleanup usa REVIEW_RETIRE, nunca DELETE automático; itens transferidos e encontros resolvidos impedem remoção.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Cleanup pós-encontro não usa leitura de quest flag como autorização de DELETE.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Regional simulation and materialization cannot treat ambiguous quest flags as facts. Protect quest-owned actors/objects and persistent NPC identities; semantic milestones need curated proof and do not grant spawn, despawn, cleanup, loot or irreversible effects without existing host gates. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **limpeza de encontros**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para limpeza pós-encontro não apaga memórias ou receipts de correção, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para limpeza pós-encontro não apaga dano nem restituição confirmada, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Não limpar bem da quest enquanto obrigação/recibo estiver incerto. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Limpeza pós-encontro preserva recursos retidos por obrigação pendente. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
