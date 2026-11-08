# 72 — Catálogo modular de encontros, templates, componentes e gates por build

**Estado:** Discovery v6.8, DEC-072/C **APROVADA como arquitetura, NÃO IMPLEMENTADA**. ADR normativo: `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md`. **48 testes candidatos T072-01..48 — NENHUM EXECUTADO.**

## 1. Propósito, fronteiras e dependências

DEC-071 disciplina o **handoff de incidente para possível encontro local**. DEC-072 especifica **como inventariar, selecionar e validar as peças do encontro**, em uma determinada instalação do BG2:EE, sem prometer que a engine permita qualquer tipo de criação dinâmica. DEC-073, ainda aberta, tratará limpeza seletiva/persistência pós-encontro.

- Respeitar DEC-010 (conteúdo curado com procedural validado), DEC-051 (inventário por build), DEC-050 (scripts/quests/romances nativos), DEC-003/013/015 (sequência de integração e gates), DEC-011/012 (host/gateway), DEC-070/071 (incidente, riscos e handoff).
- **DEC-060–071 integralmente preservadas:** cânone em `knowledge/periods/<ano>-DR/` fisicamente separado, fontes/proveniência, ingestão controlada, Knowledge Packs pinados, identidade/memória NPC, viagens e ledger exclusivo do incidente.
- Não é proposta de gerar `.CRE`, `.ARE`, `.DLG`, `.BCS` em runtime, modificar saves, carregar mods sem autorização, executar Lua de LLM, criar mapas ausentes, ativar scripts desconhecidos ou garantir sincronização multiplayer.
- Os nomes das estruturas, estados e atributos deste documento são **contratos candidatos**. Não existe API de BG2:EE/EEex implementada ou validada neste Discovery.

## 2. Separação de camadas

```text
Inventário por build (DEC-051)     Conhecimento e contexto (DEC-060..063)
                 |                           |
                 v                           v
          Component Registry          contexto anual/ACL
                 |                           |
                 +-------> Encounter Catalog <---- Director DEC-005-E
                                  |
                                  v
                           Template Binder
                     (itens, atores, área, regras)
                                  |
                         Composition Validator
                (build+capability+mods+quest+risco+rights)
                                  |
                Incidente reservado? DEC-071 ledger/CAS/fencing
                                  |
                         Action Gateway DEC-012
                                  |
                  BG2:EE host mecânico DEC-011
                                  |
             receipts verificados + eventos de campanha
```

**Fronteiras:** o catálogo descreve recursos; o binder propõe uma seleção; o validador recusa incompatibilidades; o coordenador da DEC-071 protege o direito de resolver; o gateway solicita somente ações suportadas; o host comprova efeitos. Um componente presente não é um componente instanciado e uma proposta de template não é um encontro jogável.

## 3. Manifestos e contratos candidatos

### 3.1 `BuildManifest`

- `build_fingerprint`, `game_version` quando observável, `expansion_flags`, `eeex_version` quando aplicável, `mod_load_order`, `mod_versions`, `override_manifest_digest`, `asset_inventory_hash`, `host_session_epoch` e fingerprint por cliente quando disponível.
- `capability_matrix`: ações read-only, validação de área, diálogo, ativação, spawn, criação de objeto, scripts, persistência, sincronização e rollback; **cada capability tem evidência de POC e escopo**.
- Build com componentes não verificáveis ou `digest` divergente não é considerada elegível; ausência de dado importante retorna `UNKNOWN`, não `SUPPORTED`.

### 3.2 `EncounterComponent`

| Campo candidato | Sentido | Gate |
|---|---|---|
| `component_id`, `component_revision` | Identidade estável do item de catálogo | Imutável por revisão |
| `kind` | `AREA`, `ACTOR`, `DIALOGUE`, `SCRIPT`, `TRIGGER`, `PROPS`, `ENCOUNTER_RULE`, `ADAPTER` | Tipagem e allowlist |
| `asset_locator` | Ref verificável em inventário da build | Não inferir por nome |
| `source_mod`, `source_version`, `source_hash` | Origem, proveniência e compatibilidade | DEC-017/051 |
| `rights_policy` | Uso local, importação e distribuição permitidos | Falta de autorização bloqueia |
| `dependencies`, `conflicts` | Assets/quests/scripts e incompatibilidades | Revisão e POC |
| `capability_requirement` | Ação concreta necessária para usar o componente | `HOST_MP_VERIFIED` no caso multiplayer |
| `risk_bounds`, `allowlisted_parameters` | Efeitos máximos e parâmetros seguros | DEC-027/070 |
| `ownership`, `lifecycle_hint` | Origem e possível limpeza pós-encontro | DEC-073 pendente |

### 3.3 `EncounterTemplate`

`template_id`, `template_revision`, `origin` (curado/nativo/preparado offline), `allowlisted_component_ids`, `participants`, `area_candidates`, `region_year_constraints`, `story_preconditions`, `quest_script_guards`, `composition_slots`, `max_effects`, `risk_class`, `consent_policy`, `fallback_policy`, `required_capabilities`, `test_evidence_refs` e `cleanup_contract_candidate`.

Um template pode ser parte de um plano documentado e **continuar desabilitado** até comprovação de integração por build. Um modelo LLM pode propor preenchimento de slots apenas dentro de listas autorizadas; não pode produzir novos recursos de engine que passem a existir por texto.

### 3.4 `EncounterProposal`

`proposal_id`, `incident_id`, `template_id@revision`, `campaign_id`, `branch_id`, `knowledge_manifest_id`, `build_fingerprint`, `checkpoint_epoch`, `party_area_observation_id`, `npc_identity_refs`, `composition_hash`, `permissions`, `risk_aggregate`, `capability_evidence`, `state_revision`, `idempotency_key`, `expires_at_clock_revision` (prazo proposto, sem valor arbitrário) e `validation_result`.

Todo resultado de seleção contém o motivo de elegibilidade ou recusa. `proposal_id` não é `engine_operation_id`. Nenhum resultado do modelo é recibo de host.

## 4. Matriz de estados de capacidade (candidata)

| Estado | Conhecimento que autoriza | Limitação |
|---|---|---|
| `DISCOVERED` | Recurso foi mencionado ou observado no catálogo | Não confirma arquivo instalado |
| `PRESENT` | Asset foi identificado na instalação | Não confirma que pode ser usado |
| `STATIC_VALIDATED` | Hash, dependências, licença e contrato passam por análise | Não confirma alteração runtime |
| `POC_VERIFIED` | Operação específica demonstrada em ambiente isolado, build delimitada | Não significa multiplayer verificado |
| `HOST_MP_VERIFIED` | Host + dois clientes com save/load e efeitos reconciliados na build testada | Não transfere validade a outra build |
| `UNSUPPORTED` | Falha conhecida ou indisponibilidade | Não executar |
| `STALE/UNKNOWN` | Build alterada ou evidência insuficiente | Padrão: bloquear e reavaliar |

**Regra:** promoção de estado exige evidência assinada/referenciada e execução de testes; documentação de catálogo não promove automaticamente capacidade. Não há nenhum `HOST_MP_VERIFIED` hoje.

## 5. Algoritmo de seleção, vinculação e validação (conceitual)

1. Receber `incident_id` ainda pendente da DEC-070/071, campanha e revisão temporal; verificar que não está resolvido e não existe operação incerta.
2. Confirmar party/área/sessão pela observação do host; uma região mencionada no cânone não prova área carregada.
3. Carregar o `BuildManifest` correspondente ao host e os fingerprints necessários dos clientes. Rejeitar incompatibilidade e mods desconhecidos.
4. Recuperar contexto do **ano DR confirmado** via DEC-060; consultar outros anos apenas por vigência histórica permitida e ACL; manter narrativas e memórias no overlay da campanha.
5. Filtrar templates por região, período, source rights, quest state, script guards, actors elegíveis, tipo de incidente e risco permitido.
6. Verificar os componentes e seus adapters: ausência, conflito, dependência faltante ou capability não verificada => candidato recusado.
7. Fazer `bind` dos slots do template usando apenas atores/recursos permitidos e identidade DEC-066 verificada; nome parecido não é identificação.
8. Recalcular risco total e avaliar agência/consentimento do grupo. Omissão/ambiguidade => fail-closed.
9. Verificar orçamento DEC-056 e SLA; insuficiência de capacidade devolve `PENDING`/alternativa narrativa, nunca substitui resultado inexistente.
10. Gerar proposta **imutável** (hash de composição, versões e precondições). Ela é elegível, mas ainda não tem direito de resolver.
11. DEC-071 adquire reserva exclusiva e fencing para o `incident_id`; somente depois, se houver adapter comprovado, solicitar ação tipada via host.
12. Após receipt válido, projetar os efeitos confirmados uma única vez no overlay da campanha. `UNCERTAIN` exige reconciliação, não retry automático.

## 6. Exemplos de templates (ilustrativos, NÃO IMPLEMENTADOS)

- **`ROAD_CARAVAN_CONVERSATION`** — encontro social de baixo impacto: presença de NPC verificada; uso mecânico depende de diálogo/gatilho realmente disponível, caso contrário apenas notícia narrativa autorizada.
- **`ROAD_BLOCKED_DETOUR`** — alteração proposta de itinerário por estrada bloqueada com causa verificada; não criar barreira, sprite ou alteração de pathfinding sem capability.
- **`BANDIT_AMBUSH_ELIGIBLE`** — oportunidade potencial de emboscada; ameaça ou rumor não confirma combate. Exige área, atores, scripts, consentimento, risco HIGH conforme efeito, adapter e receipt host; se faltar qualquer requisito, pendente/narrativa sem HP/XP/loot inventados.
- **`FACTION_CHECKPOINT`** — possível encontro com autoridades da região, sem alterar reputação/quest a menos que efeito seja autorizado e comprovado.

Os exemplos são **nomes de templates hipotéticos** e não correspondem a assets comprovadamente existentes na instalação ou a eventos históricos confirmados.

## 7. Proteções específicas

### 7.1 Contra conflitos nativos e duplicação

- Consultar DEC-050/051 para flags de quests, romances e scripts existentes; nunca sobrescrever gatilhos originais por colisão.
- Se o ator estiver presente como instância nativa, não criar outro; se a identidade DEC-066 for ambígua, suspender a associação e a execução.
- Detectar origem, hash e dependências de áreas/scripts, evitando que duas versões de mods sejam tratadas como compatíveis por nome.
- Isolar logs privados, rascunhos de templates e segredos de personagens: contexto da LLM só após ACL DEC-028/060.

### 7.2 Direitos e produção offline

- Registrar procedência e condições de uso de cada asset e mod; uso privado não elimina automaticamente obrigações autorais e de licença.
- Preparar pacotes em instalação de teste dedicada. Exigir revisão de dependências, scanning de arquivos importados, hashes, comparação de assets, backups, instalação reversível e testes por build.
- Separar aprovação da peça de conteúdo de aprovação de seu uso para alterar uma campanha ativa (DEC-052/053/063). Não implementar hot patch nem update automático silencioso.

### 7.3 Política de falhas e operação

- `MISSING_ASSET`, `MOD_CONFLICT`, `NO_CAPABILITY`, `ACL_DENIED`, `RISK_GATE_PENDING`, `STALE_BUILD`, `UNCERTAIN` não podem degradar para execução livre.
- Se uma migração de build invalidar um template já selecionado, descartar sua elegibilidade e reconciliar a reserva DEC-071, sem reexecutar ações possivelmente aplicadas.
- Um save/restauração deve revalidar branch, templates, composição e ledger. Backups não são garantia de reversibilidade da engine sem ensaio.
- Preferir `PENDING` ou narrativa honesta a travar gameplay, inventar resolução ou executar scripts desconhecidos.

## 8. Escada de POCs e evidências (pendentes)

1. **G72-0 — Inventário somente leitura:** enumerar assets, scripts, dependências, hash/ordem de mods e capabilities desconhecidas sem modificar BG2:EE.
2. **G72-1 — Catálogo offline:** validar esquemas, proveniência e templates com fixtures sintéticos e dados licenciados, incluindo conflitos e fontes ausentes.
3. **G72-2 — Verificador de compatibilidade:** diferenciar `PRESENT` de `POC_VERIFIED`, negar versões divergentes e provar que LLM não pode introduzir componente não autorizado.
4. **G72-3 — Integração offline isolada:** testar um único template de baixo impacto, somente se adapter seguro for demonstrado; capturar receipts, save/load, restauração e ausência de efeito em conteúdo nativo.
5. **G72-4 — Multiplayer host+dois clientes:** mesmos hashes/permissões, concorrência, reconexão, incidente único e registro único; desativar capability em qualquer falha.
6. **G72-5 — Expansão/rollback:** adicionar módulo compatível offline, verificar reversão após ensaio e proteção de campanhas existentes antes da habilitação.

Nenhuma POC foi executada. Uma etapa não aprova automaticamente a seguinte.

## 9. Matriz de 48 testes candidatos — NÃO EXECUTADOS

| ID | Cenário / expectativa |
|---|---|
| T072-01 | Catálogo vazio não cria encontro local nem gera asset. |
| T072-02 | Recurso DISCOVERED mas não PRESENT não pode compor template executável. |
| T072-03 | Asset PRESENT sem POC de adapter não recebe capability de spawn. |
| T072-04 | Análise estática aprovada não autoriza efeito mecânico em runtime. |
| T072-05 | POC offline aprovada não implica HOST_MP_VERIFIED. |
| T072-06 | Build alterada de forma não inventariada invalida template anteriormente elegível. |
| T072-07 | Hash ou versão de mod divergente entre host/clientes bloqueia uso mecânico. |
| T072-08 | Alteração de load order/override invalida fingerprint da composição. |
| T072-09 | Área citada no lore mas ausente na build não pode receber encontro local. |
| T072-10 | Área presente mas não carregável não prova possibilidade de spawn. |
| T072-11 | Component kind desconhecido é rejeitado em validação de contrato. |
| T072-12 | Template de revisão desconhecida ou mutada após seleção é rejeitado. |
| T072-13 | Dependência ausente bloqueia componente e registra motivo. |
| T072-14 | Conflito de dois mods/recursos bloqueia composição insegura. |
| T072-15 | Recursos com licença desconhecida não são importados/reempacotados. |
| T072-16 | Componente restrito não é redistribuído para cliente sem direito de distribuição. |
| T072-17 | Arquivo importado suspeito permanece em área offline isolada. |
| T072-18 | LLM que pede componente fora da allowlist não pode ativá-lo. |
| T072-19 | LLM que gera script livre não pode executá-lo nem alterar engine. |
| T072-20 | Gateway rejeita comando mecânico fora da allowlist tipada. |
| T072-21 | Template declarado LOW mas com efeito cumulativo HIGH é reclassificado/bloqueado. |
| T072-22 | Ausência de autorização exigida em encontro MEDIUM impede execução. |
| T072-23 | Encontro HIGH sem confirmação pertinente fica bloqueado. |
| T072-24 | Instância nativa já presente não é duplicada por template. |
| T072-25 | NPC homônimo sem identidade VERIFIED não herda memória nem ganha spawn. |
| T072-26 | Flag de quest nativa conflitante bloqueia template mesmo com asset presente. |
| T072-27 | Romance/script nativo protegido impede composição conflituosa. |
| T072-28 | Proposta sem incident_id válido não ingressa na trilha DEC-071. |
| T072-29 | Duas propostas do mesmo incidente não obtêm duas reservas locais. |
| T072-30 | Reserva local suspende resolvedor offscreen até conciliação. |
| T072-31 | Fencing antigo após falha de rede não autoriza ativação de template. |
| T072-32 | Timeout de host após solicitação fica UNCERTAIN sem retry cego. |
| T072-33 | Receipt de cliente ou worker LAN não confirma efeito mecânico. |
| T072-34 | Receipt de outro branch/checkpoint/build não confirma encontro. |
| T072-35 | Receipt válido do host confirma uma única aplicação de efeitos. |
| T072-36 | Mudança de Knowledge Pack não reescreve template pendente silenciosamente. |
| T072-37 | Consulta a 1369 DR não injeta eventos futuros de 1370 DR como consumados. |
| T072-38 | Memória NPC de outro ramo não é exposta na composição nem em log. |
| T072-39 | Conteúdo privado é filtrado antes de enviar solicitação ao modelo LAN. |
| T072-40 | Falta de capacidade computacional gera PENDING, não execução falsa. |
| T072-41 | Carregamento/reload revalida template, identidade, revision e ledger. |
| T072-42 | Restore de backup não reinsere encounter concluído no ramo restaurado indevidamente. |
| T072-43 | Mod atualizado invalida template que depende de versão antiga. |
| T072-44 | Adição offline de pack requer testes de rollback e aprovação antes de habilitar. |
| T072-45 | Script/asset host não suportado mantém alternativa narrativa ou pendência. |
| T072-46 | Sem área/mecânica suportada, diálogo narrativo não modifica HP/XP/inventário. |
| T072-47 | Host + dois clientes devem confirmar uma única ocorrência e ausência de duplicidade. |
| T072-48 | Auditoria registra origens/decisões/receipts sem gravar segredos no log. |

**Todos os 48 casos são testes candidatos a elaborar em SPECS e executar em POCs futuras, não resultados reais.** Critérios de aceitação, fixtures, algoritmos e ambientes ainda serão definidos; nunca assumir suporte de BG2:EE/EEex/multiplayer a partir desta lista.

## 10. Próxima discussão — DEC-073 (em aberto)

Após uma interação local, é necessário decidir **como encerrar e reconciliar componentes temporários e efeitos persistentes**. Alternativas: A) apagar tudo ao encerrar; B) preservar indiscriminadamente todos os recursos; **C, recomendada)** ciclo de vida por ownership e recibos do host, preservação seletiva de consequências realmente confirmadas e limpeza somente de recursos temporários comprovadamente pertencentes ao encontro, com reconciliação após crash/save/load. Não apagar NPC nativo, drop, quest ou memória por suposição. A DEC-073 complementará DEC-071/072 sem presumir capacidades de cleanup da engine.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

DEC-073 exige ownership e lifecycle por instância, evidência de transferência e capability de cleanup verificada independentemente de capability de spawn.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Template DEC-072 não concede fato ocorrido ou repercussão DEC-074; impactos dependem de resultados confirmados e regras independentes de domínio. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Template pré-cadastrado não garante log de participação individual. Capability por build precisa provar observabilidade antes de atribuição granular.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Catálogo poderá descrever recursos com nomes distintos e templates de disfarce apenas se build/adapter/testes os comprovarem; presença em assets não garante capacidade runtime.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Templates de interrogatório, guarda ou julgamento DEC-078 só podem utilizar componentes validados por build; não gerar script ou punição arbitrária runtime.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Template de guardas/tribunal DEC-079 só é elegível se assets e adapters validarem por build; documentos não autorizam injeção automática de scripts.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Templates e adapters não autorizam dar loot/XP como reparação, sem validação de ownership e receipt host por build.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-084/C — Discovery v8.0

A existência de template de emboscada/guarda não prova capability de spawn, follow ou remoção. Medidas mecânicas exigem POCs específicas.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Template de encontro hostil não se torna elegível apenas porque guilda descobriu uma pista de rota; precisa precondições/riscos e build validada.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Templates de isca/rumor são narrativos até prova de capability. Não criar scripts ou documentos de motor falsos por saída LLM.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

EncounterCatalog não instancia informante/interação para sanar promessa sem template seguro, owner e capability comprovados por build.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Template de encontro não consome relatório UNVERIFIED como gatilho factual sem regra de risco, elegibilidade e build; LLM não cria scripts de prova.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-091/C — Discovery v8.7

Planos que exigirem encounters usam componentes de catálogo testados por build; LLM não compila scripts diretamente.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Catálogo de encontros e capabilities por build precisam ser revalidados quando muda local/objetivo; LLM não sintetiza novos scripts runtime.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Catálogo de encontros não materializa recurso em dois eventos; collision e quota por build/asset e ação host devem ser checados antes do despacho.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Template de encontro não é substituto livre de recurso bloqueado; usar apenas componentes/capabilities provadas pela build e pelo host.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Matriz DEC-096 só usa template de evento/encontro allowlisted e testado por build; nenhum efeito direto/in-direto executa script livre.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Templates de patrulha/ameaça DEC-096/C precisam allowlist e prova por build, nenhum spawn/script definido em texto livre.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

DEC-097/C não autoriza spawn por valor numérico isolado; requer encontro curado, disponibilidade e template validado.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Catálogo de templates não dá permissão automática de spawn; adapter e template têm de ser allowlisted e validados na build.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Templates de encontros carregados pelo motor/mod preservam origem e owner, não sendo de propriedade automática da IA.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Catálogo de encontros não pode incluir tokens de scripts protegidos ou precondições não observáveis por build.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Regional simulation and materialization cannot treat ambiguous quest flags as facts. Protect quest-owned actors/objects and persistent NPC identities; semantic milestones need curated proof and do not grant spawn, despawn, cleanup, loot or irreversible effects without existing host gates. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **templates de encontros**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para encontros de mediação exigem elegibilidade e autoria, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-109/C — Obrigações condicionais multipartes

Templates de encontro não criam dívida, pagamento ou escolta contratual automaticamente. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
