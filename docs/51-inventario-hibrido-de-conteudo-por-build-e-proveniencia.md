# DEC-051 — Inventário híbrido, automatizado, curado e versionado por build

**Versão:** Infinity AI Discovery v4.7  
**Decisão:** opção C, aprovada em 2026-11-06 — ADR-0046.  
**Estado:** desenho arquitetural/candidatos para SPECS; nenhuma varredura ou integração local foi demonstrada.

## 1. Objetivo e não objetivos

Viabilizar a conciliação segura da DEC-050 com missões, diálogos, scripts, romances e NPCs **realmente presentes na instalação**, incluindo mods e diferenças entre builds, sem confiar que uma lista de lore ou a geração da IA represente a configuração concreta do jogo. Um manifesto não substitui o estado runtime da campanha nem prova que uma mutação será segura.

**Não objetivos:** implementar extratores nesta etapa; instalar/modificar jogos; redistribuir dados proprietários; garantir leitura de flags vivas; considerar todos os mods compatíveis; permitir remendo de save; usar o LLM para autorizar mutações ou inferir verdade a partir de lacunas.

## 2. Pipeline lógico proposto

```text
Instalação/build concreto (preferência: cópia isolada)
    ↓ identificação e fingerprint (somente leitura)
BUILD_MANIFEST [versão, ordem de mods, evidências, hashes, escopo]
    ↓ extração automatizada com limites de cobertura
RESOURCE_INVENTORY [IDs, tipos, fontes e referências cruzadas]
    ↓ normalização/aliases/duplicatas e curadoria humana
CONTENT_CATALOG [quest, diálogo, romance, NPC, script, região, estado da curadoria]
    ↓ avaliação de cobertura, conflitos e versões
COMPATIBILITY_EVIDENCE [verified/observed/inferred/unknown/conflicted]
    ↓ preflight e conferência do estado runtime obtido legitimamente
DEC-050 RECONCILER [allow/adapt/defer/block/divergence_review]
    ↓ só para ação autorizada e tecnicamente comprovada
DEC-012 GATEWAY → BG2:EE HOST → receipt + pós-condição + log
```

A localização de um arquivo e a extração de referências **não provam que o recurso será executado**, que determinado diálogo estará disponível ou que o jogador esteja no estágio correspondente da missão. A observação do runtime só se torna válida após POC de leitura, vinculação à instância/host e controles de versão.

## 3. Entidades candidatas e rastreabilidade

| Entidade | Campos candidatos (não são API implementada) | Finalidade |
|---|---|---|
| `BuildManifest` | `build_id`, `game_edition`, `version_evidence`, `platform`, `install_profile`, `mod_order_evidence`, `resource_hashes`, `captured_at`, `scanner_version`, `completeness` | Reproduzir o objeto analisado e identificar mudanças. |
| `ModComponent` | `component_id`, `name`, `version_evidence`, `position`, `install_log_ref`, `confidence` | Diferenciar nome anunciado, componente efetivo e ordem. |
| `ResourceRecord` | `resref`, `type`, `source_file`, `resolved_provider`, `references`, `effective_hash`, `parser_evidence` | Conhecer conteúdo instalado e possíveis sobrescritas. |
| `ContentEntry` | `content_id`, `kind`, `aliases`, `source_refs`, `locale`, `era`, `region`, `reviewer`, `review_state` | Relacionar arquivos a quests/romances/companheiros sem prometer leitura semântica completa. |
| `DependencyEdge` | `from`, `to`, `type`, `evidence`, `confidence`, `scope` | Identificar condições/scripts/diálogos compartilhados. |
| `RuntimeObservation` | `campaign_id`, `build_id`, `host_revision`, `observed_at`, `source`, `value`, `status` | Separar fato observado de hipótese estática; somente após POC. |
| `CoverageRecord` | `resource_type`, `source_set`, `scanned_fraction_or_scope`, `unknowns`, `limitations`, `tests` | Evitar alegar ausência com varredura incompleta. |
| `ConflictReport` | `proposal_id`, `manifest_id`, `dependencies`, `unknowns`, `risk`, `recommendation`, `reason_codes` | Fundamentar preflight seguro e decisões auditáveis. |

Os nomes e campos são candidatos; os formatos definitivos, dados mínimos e política de retenção aguardam SPECS e POCs.

## 4. Fontes e limites de inventário

- **Instalação BG2:EE:** avaliar formatos de recursos relevantes (por exemplo, scripts, diálogos, áreas, personagens, tabelas e arquivos de texto de diálogo) por meio de ferramentas que demonstrem suporte aos formatos efetivos do build.
- **Mods:** avaliar logs de instalação, metadados, versões, componentes, arquivos de configuração, hashes e relação de recursos sobrescritos. Logs podem estar ausentes, incompletos ou não refletir alterações manuais; a cobertura deve registrar isso.
- **Ferramentas candidatas para investigação:** WeiDU e Near Infinity, além de parsers específicos quando necessários; a escolha depende de inspeção da versão, licenças, compatibilidade e provas de leitura sem alteração.
- **Catálogo humano:** curadores revisam mapeamentos de recursos, relevância de flags, colisões, aliases, relação com personagens/cronologia e evidências de funcionamento.
- **Estado da campanha:** fica fora do inventário estático. Apenas observação runtime demonstrada e confirmada pelo host pode indicar estágio de quest, personagem presente, romance ativo, variável corrente ou posse real de itens.
- **Lore canônico:** fornece identidade, datas e contexto narrativo, mas não demonstra existência de qualquer recurso no BG2:EE ou instalação modded (DEC-009/031).

## 5. Exemplo de decisões de segurança por cobertura

| Evidência disponível | Interpretação permitida | Consequência de proposta com efeito mecânico |
|---|---|---|
| Recurso identificado, origem conhecida e build correspondente | `OBSERVED` (presença estática) | Ainda precisa de estado runtime, dependências, política e testes. |
| Quest curada e dependências confirmadas por testes no build | `VERIFIED` no escopo documentado | Pode prosseguir para preflight; não é autorização automática. |
| Ferramenta não suporta parte dos arquivos | `UNKNOWN` | Bloquear alterações que dependam dessa parte; não afirmar ausência. |
| Dois mods oferecem recursos conflitantes e resolução não comprovada | `CONFLICTED` | Adiar/bloquear até curadoria e testes. |
| Build ou ordem de mods mudou após aprovação | `STALE` (estado de controle candidato) | Invalidar evidências associadas e exigir novo fingerprint/revisão. |
| LLM sugeriu que determinada flag deve estar ativa | `INFERRED` | Nunca tratar como confirmação ou usar para autorizar escrita. |

Distinguir **não encontrado** de **comprovadamente ausente**, e **identificado** de **compatível**. A ausência só pode ser afirmada para escopo de varredura cuja cobertura e resolução de sobreposições foram comprovadas.

## 6. Impacto na DEC-050, gateway e lore

O reconciliador recebe `manifest_id`, referência ao conjunto de recursos relevante, cobertura, observações runtime confirmadas (quando disponíveis) e política de risco. Se algo essencial estiver desconhecido, retorna `DEFER` ou `BLOCK` em vez de permitir a IA contornar o problema.

A IA pode propor textos ou descrições, mas não pode declarar que uma quest completou, um romance foi ativado ou uma flag mudou. Qualquer mutação precisa de operação tipada allowlisted, políticas/consentimento e confirmação mecânica do host. Mudar conteúdo instalado não é o mesmo que mudar o histórico de Forgotten Realms; ambos são controlados por fontes diferentes e conciliação explícita.

## 7. Progressão de validação

- **G0 — Baseline:** BG2:EE limpo, Windows, cópia isolada, captura estável de manifesto e hashing; nenhuma modificação.
- **G1 — Leitura de recursos:** testar extração de um conjunto mínimo de tipos, registro de erros, cobertura e origem efetiva. Não assumir cobertura 100%.
- **G2 — Curadoria:** uma quest e um companion conhecidos com diálogos, dependências e conflitos explicitamente documentados; revisão de fontes cruzadas.
- **G3 — Comparação de builds:** adicionar uma mudança/mod controlado; detectar componentes, ordem, sobrescritas, recursos alterados, conflitos e invalidação de evidências.
- **G4 — Runtime observável:** prova técnica independente para leitura de estados no host; comparação com dados estáticos sem presumir correspondência.
- **G5 — Conciliação segura:** acionar apenas preflight sem mutação; em etapa posterior, testar gateway com operação tipada, logs, saves isolados, dois clientes e recuperação de `UNCERTAIN`.
- **G6 — Expansão:** EET, IWD1/2 e NWNForBG somente conforme ordem de mods, licenças, disponibilidade dos componentes e POCs próprios.

## 8. Matriz de testes candidatos (20)

| ID | Caso candidato | Critério de aceitação proposto |
|---|---|---|
| T-051-01 | Instalação limpa repetida | Fingerprints equivalentes sob critérios explícitos. |
| T-051-02 | Alteração de arquivo relevante | Mudança detectada e evidências dependentes invalidadas. |
| T-051-03 | Mudança irrelevante de timestamp | Não gerar falso positivo se hashes e escopo forem idênticos. |
| T-051-04 | Versão desconhecida do jogo | Manifesto indica lacuna, sem inventar versão. |
| T-051-05 | Mod sem log de instalação | `UNKNOWN` para ordem/proveniência, sem confiar na lista declarada. |
| T-051-06 | Dois mods sobrescrevem recurso | Provedor efetivo identificado somente se comprovado; caso contrário `CONFLICTED`. |
| T-051-07 | Alias/resref ambíguo | Não fundir entidades sem evidência. |
| T-051-08 | Varredura interrompida | Cobertura parcial marcada; ausência não afirmada. |
| T-051-09 | Arquivo corrompido | Falha localizada e relatório reproduzível; nenhuma modificação. |
| T-051-10 | Diálogo com múltiplas condições | Referências extraídas, sem inferir ordem runtime. |
| T-051-11 | Missão ativa somente no save | Nunca deduzir estado a partir do catálogo estático. |
| T-051-12 | Romance alternativo modded | Fonte e condições curadas sem fingir compatibilidade automática. |
| T-051-13 | Dependência de quest desconhecida | Preflight recusa mutação insegura. |
| T-051-14 | Recurso de NPC canônico ausente | Sem spawn automático; `UNKNOWN` até provar ausência. |
| T-051-15 | Mudança de ordem de mods | Fingerprint altera e aprovações dependentes são invalidadas. |
| T-051-16 | Scanner atualizado | Proveniência de extração e diff do catálogo são preservados. |
| T-051-17 | LLM afirma flag sem evidência | Afirmação não vira estado runtime nem autorização. |
| T-051-18 | Dois clientes em builds diferentes | Não declarar sincronização compatível; bloquear transição insegura. |
| T-051-19 | Timeout de ação do gateway | `UNCERTAIN`, sem replay cego; conciliar por receipt/observação. |
| T-051-20 | Replay de manifesto e catálogo | Registros de curadoria/evidência rastreáveis e revisão auditável. |

Nenhum teste foi executado ou aprovado como implementação. Critérios quantitativos, estrutura de dados final e compatibilidade real serão definidos nas SPECS.

## 9. Riscos e pendências

- Sem leitura semântica garantida de todas as extensões/formats, ordem de execução ou scripts gerados em runtime.
- Sem garantia de ferramentas que permitam manipular flags/missões em BG2:EE/EEex multiplayer.
- Não assumir que arquivos ausentes significam ausência do conteúdo, nem que hash igual garante equivalência do estado de campanha.
- Gestão de licenças de jogos/mods, privacidade de saves/logs, isolamento da instalação e consistência de manifests são requisitos de segurança e manutenção.
- Não usar conteúdo do game/mod para distribuição indiscriminada; o Discovery registra a arquitetura, não os ativos proprietários.

**Próxima decisão candidata:** DEC-052 — estratégia de atualização de jogos e mods em campanhas persistentes: manter build imutável, atualizar livremente ou migrar sob validação com snapshot e rollback seguro.

## Complemento DEC-052 — Manifesto como entrada da migração (Discovery v4.8)

O catálogo e o fingerprint da DEC-051 são **entradas read-only** para comparar `source_build_id → target_build_id` em um ambiente isolado. Mudanças de mods, ordem, recursos ou identidade invalidam aprovações dependentes e exigem plano específico, teste de saves/quests e autorização do anfitrião conforme ADR-0047/documento 52. Inventário não migra o save nem prova compatibilidade de romances e multiplayer. `UNKNOWN` crítico permanece bloqueante.

## Integração DEC-063/C — separar catálogo de conteúdo instalado do lore (v5.9)

O inventário da build DEC-051 e o manifesto de *knowledge pack* DEC-063 são componentes distintos. Adoção de fato histórico que pressupõe recurso/quest não constatado na instalação deve ser classificada com risco e bloqueada/escalada, não atribuída a capacidade real do BG2:EE. O diff considera build, scripts, quests e revisões anuais curadas; não pressupõe leitura completa do motor.

### Integração DEC-066/C — evidência de identidade ligada ao inventário por build (v6.2)

Manifesto de build pode registrar candidatos de CRE/script/resource e observabilidade runtime, com status de cobertura e fingerprint. Nenhum inventário estático certifica que uma observação é o mesmo NPC de sessão anterior; mudanças de mods/ordem ou flags desconhecidas tornam vínculo `STALE` até revalidação. Manter proveniência e diferenciar asset de instância/pessoa.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

O catálogo de scripts/CREs da DEC-051 fornece evidências potenciais para DEC-066/067, mas CRE e nomes não são identificadores de pessoa; mods podem duplicar ou reciclar instâncias.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

Para reativação de NPC DEC-068, mudanças no inventário, CRE ou scripts da instalação invalidam garantias anteriores; marcar `STALE` e revalidar evidências e flags antes de ações. Inventário não comprova instância física em área descarregada.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: mapeamento `lore_region`↔`engine_area` depende de inventário de build/mod e evidências dinâmicas; arquivo estático não prova suporte runtime.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

A elegibilidade DEC-071 exige matriz de áreas, entidades, diálogos, scripts e adapters realmente testados por build/manifest, distinguindo `PRESENT`, `SUPPORTED`, `UNTESTED`, `UNSUPPORTED`. Asset inventariado não comprova suporte para spawn ou evento local; composição detalhada permanece DEC-072 aberta.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

DEC-072/C aprova catálogo por build com manifests de assets, dependências, rights, templates e adapters; distinguir `PRESENT/STATIC_VALIDATED` de `POC_VERIFIED/HOST_MP_VERIFIED`. Mudança de mod/hash invalida template e nenhuma geração runtime fica autorizada.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Manifesto da DEC-072 deve preservar também origem/ownership de instância e capabilities de cleanup com provas específicas; inventário de asset não equivale a permissão de remoção.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Catálogo DEC-078 pode mapear recursos nativos de guardas e diálogos, mas presença de assets não prova capacidade de arrest, wanted ou confiscate; precisa POC por build/multiplayer.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Nenhum recurso observado em build prova suporte a wanted flags, spawn de guardas, captura ou confisco DEC-079. Adapters precisam prova de POC, testes host+2 clientes, versão e rollback.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Inventariar se a build suporta observar/alterar wanted flags ou guard scripts; não inferir capability de revogação por arquivo PRESENT. Registrar UNSUPPORTED/UNKNOWN sem POC.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Registrar capabilities e limitações de remédios (itens, ouro, soltura, quest/reputação) por build, adapter e modo multiplayer; asset presente não prova capacidade.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-084/C — Discovery v8.0

Inventário por build deve especificar se existe suporte verificável a follow, movimentação e mudança de presença em multiplayer; presença de asset não comprova operação.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Catálogo de build deve distinguir mecânicas de stealth/interceptação efetivamente disponíveis dos recursos apenas narrativos; não presumir engine hooks.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Catálogo de capabilities por build deve diferenciar estado social externo, flags nativas de facção e ações de party/diálogo; não assumir que um nome prova compatibilidade.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Reserva de compensação usa referências reais de inventory/asset e metadados de build; ouro ou itens não se materializam por promessa LLM.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Se um documento alegado não existe como item verificável, não criar resource/asset por texto da fonte; manifesto da build e host receipt prevalecem.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Não presumir item/documento físico representando dossiê sem inventário de capacidades e POC do build. Texto narrativo armazenado em overlay é distinto de recurso CRE/ITM/JRN nativo.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Item, ouro ou equipamento planejado não é gasto; validação de inventário por build e receipt host são necessários.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Reservar/consumir/liberar itens e ouro são fatos distintos; recursos in-flight/UNCERTAIN não voltam ao pool por solicitação de cancelamento.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Lock lógico de item ou slot não prova equipagem ou ownership no inventário da engine. Requer manifest/capability validada e receipt do host; não duplicar item de quest.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Sem API de inventário comprovada por build, lease de item vencido não restaura nem move item. Host receipt condiciona consumo e qualquer compensação futura.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

DEC-096 proposta requer mapeamento de location_tags para area IDs efetivos e capabilities por build; tipo de local não garante que mapa/objeto exista.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Propostas de impacto DEC-096/C não equivalem a capability EEex comprovada; IDs geográficos/spawn/mutadores exigem validação por build.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Inventário por build deve anotar modpack hash, load order, engine asset, owner de instância e direitos de campo separados.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Inventário de builds/mods é estático e não prova que query runtime é read-only; manifestos exigem POC por probe.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Catalogues by exact build/modpack/quest/script fingerprint, curated proof of semantic milestone and valid transition; an observed flag or stage is never an authorized quest write or host receipt. On patch or restore, invalidate semantic cache and avoid generic stage inference. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **inventário técnico**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para catálogo de conteúdo por build e fontes sem vazamento de spoilers, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para conhecimento por build e autores de conteúdo, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
