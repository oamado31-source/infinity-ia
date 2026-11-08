# DEC-031 — Facções autônomas e catálogo canônico expandido (desenho técnico preliminar)

**Discovery v2.8** · **ADR-0026 aprovada, opção B com adendo** · **Documento candidato para SPECS, não funcionalidade implementada**

## Meta e limites

Manter as facções/grupos já presentes em BG/IWD/NWN e ampliar a cobertura do **catálogo** a organizações existentes no cânone de Forgotten Realms, com importação/curadoria progressiva e simulação seletiva segundo relevância, época, geografia, disponibilidade de assets e orçamento. **Catálogo universal não equivale a simulação simultânea universal.**

O mundo de testes usará 1369 DR (DEC-023); uma facção conhecida em um suplemento posterior ou em outra época não será tratada como automaticamente existente/ativa em 1369. Algumas organizações podem influenciar eventos de forma indireta, sem depender de áreas jogáveis ou NPCs importados.

## Pipeline conceitual de catálogo

```text
Fontes oficiais/licenciadas + índices de referência (curadoria; não cópia massiva)
        |
        v
Normalização: identidade estável, aliases, ramificações, períodos, localização
        |
        v
Validação de fontes / cronologia DR / confiança / conflitos de versão
        |
        v
Canonical Faction Catalog [histórico versionado; independente da campanha]
        |
        v
Campaign World Overlay [1369 DR ou outra época configurada, divergências]
        |
        +--> CATALOG_ONLY / WORLD_RELEVANT / SIMULATED / IN_GAME_ACTIVE
                            |
                            v
       Rules/Goals/Resource Projections [batch; no LLM per tick]
                            |
                            v
  Propostas LOW/MEDIUM/HIGH -> Action Gateway -> Host confirmation
                            |
                            v
           Confirmed event log + snapshot / knowledge / reputation
```

### Catálogo x disponibilidade na instalação

| Escopo | Registro | Pode existir sem mod/área? | Limite |
|---|---|---|---|
| Conhecimento canônico | Organização documentada com proveniência e temporalidade | Sim | Não ganha ações/gameplay automaticamente |
| Influência narrativa | Rumor, agente indireto, relação comercial/política, missão contextual | Sim, se validado e pertinente | Não inventar evidências nem ações mecânicas realizadas |
| Simulação resumida | Objetivos, influência, alianças e recursos virtuais | Sim | Orçamento por atividade e políticas de risco |
| Presença física | NPC, edifício, guarda, diálogo, interações e conflitos no mapa | **Depende** de conteúdo compatível instalado | Gate de versões/mods/bridge/host; não criar assets de modo implícito |

## Entidades candidatas

| Entidade | Campos sugeridos | Invariantes |
|---|---|---|
| `canon_faction` | `id`, `names`, `aliases`, `source_refs`, `branch`, `continuity_tag`, `date_evidence` | Origem rastreável; IDs distintos para facções cindidas |
| `faction_presence` | `id`, `region`, `start_dr/end_dr`, `presence_type`, `confidence` | Não assumir onipresença nem datas exatas desconhecidas |
| `faction_status_epoch` | `faction_id`, `range_dr`, `active/forming/disbanded/unknown`, `leadership` | Fundada/extinta/reestruturada segundo a data e fontes |
| `campaign_faction_state` | `campaign_id`, `world_revision`, `goals`, `resources`, `relations`, `influence`, `risk_tier` | Estado da campanha separado do fato canônico |
| `faction_actor_link` | `faction_id`, `npc_id`, `role`, `knowledge_scope`, `valid_from/to` | Um membro não herda automaticamente todos os segredos da facção |
| `faction_event` | `cause_id`, `date_dr`, `faction_id`, `proposed/confirmed`, `source`, `receipt` | Sem efeito mecânico não confirmado, replay idempotente |
| `faction_asset_binding` | `installation_id`, `resource_ids`, `verified_versions`, `area_ref`, `availability` | Nenhum asset presumido se não estiver instalado |

## Simulação por objetivos (candidata)

1. **Consultar estado permitido:** campanha, data DR, jurisdição, recursos, alvos, conhecimento comprovado, relações e tensões.
2. **Gerar alternativas por regras:** expandir influência, negociar, arrecadar, recrutar, evitar inimigos, buscar apoio, cumprir obrigações; nenhuma ação é ativada sem precondições.
3. **Validar restrições:** capacidade realista, fronteiras geográficas, rotas, custo, histórico canônico, alianças/leis e estado da campanha.
4. **Aplicar orçamento:** ACTIVE pode gerar eventos locais; NEAR recebe projeções resumidas; DISTANT simulação em checkpoints; DORMANT só quando relevante/reativada (DEC-021/022).
5. **Classificar risco DEC-027:** negócios cotidianos não autorizam golpes, morte de liderança, guerra, anexação territorial ou mudança institucional definitiva. Essas ações `HIGH` ficam bloqueadas sem política específica.
6. **Emitir propostas idempotentes:** um mesmo evento não produz custo/ganho duplicado após reconexão ou replay.
7. **Persistir apenas confirmado:** efeitos narrativos autorizados em log/snapshot; efeitos do jogo somente após receipt do host (DEC-011/012).
8. **Publicar conhecimento permitido:** rumores e reputação seguem DEC-028/029/030, preservando a individualidade dos NPCs.

## Catálogo canônico — abordagem de curadoria

- **Prioridade não é exclusividade:** primeiro entradas presentes no BG2:EE/EET e regiões utilizadas no MVP; depois organizações adicionais relevantes em 1369 DR; posteriormente outros períodos/continentes/planos conforme as campanhas requererem. A meta declarada continua sendo incluir **todas as organizações comprovadas no canon**, sem afirmar completude enquanto houver lacunas.
- Documentar fontes primárias/edição/ano, páginas ou referências identificáveis e proveniência do nome; material da comunidade pode apoiar descoberta, mas é indexador, não prova final.
- Tratar lacunas de data e divergências de continuidade de modo explícito (`UNKNOWN`, confiança, intervalos), sem inventar que a facção existia ou estava ativa em 1369 DR.
- Guardar membros, filiais, subgrupos, nomes antigos e cisões como relações ao longo do tempo, sem fusões automáticas.
- Distinguir entidade do cânone de **facção nova criada especificamente para a campanha**, sempre identificada como conteúdo original do Living World.
- Não duplicar trechos extensos dos livros nem distribuir assets proprietários; guardar referências, metadados e conteúdo próprio gerado de forma permitida.

## Testes candidatos

| ID | Cenário | Critério |
|---|---|---|
| FAC-01 | Facção dos jogos está no catálogo | Identidade e conteúdo original preservados |
| FAC-02 | Facção canônica ausente dos jogos | Entrada histórica consultável, sem assets inventados |
| FAC-03 | Facção fundada posteriormente a 1369 DR | Inativa no ano-base; nenhuma atividade precoce |
| FAC-04 | Organização dissolvida antes do ano da campanha | Histórico acessível, sem poder vigente sem reativação |
| FAC-05 | Informação sem data/fonte conclusiva | Estado `UNKNOWN`, revisão pendente, sem data adivinhada |
| FAC-06 | Nome alternativo ou mudança de liderança | Resolução temporal correta, sem duplicidade de identidade |
| FAC-07 | Cisão de uma facção | Não misturar membros, recursos ou relações sem origem válida |
| FAC-08 | Facção remota influencia rumores | Propagação exige canais e tempo válidos |
| FAC-09 | Jogadores hostilizam um membro | Não atribuir hostilidade automaticamente a toda facção sem evento/política |
| FAC-10 | Facção regional não possui recursos de mapa | Apenas influência narrativa; nenhum spawn automático |
| FAC-11 | Facções rivais disputam interesse local | Propostas determinísticas e recursos coerentes |
| FAC-12 | Múltiplas regiões DISTANT/DORMANT | Custo limitado e checkpoints, sem LLM por tick |
| FAC-13 | Facção propõe guerra/morte de líder histórico | `HIGH` bloqueada até política especial |
| FAC-14 | Falha de comunicação/host durante spawn de patrulha | `UNCERTAIN`; sem duplicação por retry cego |
| FAC-15 | Save/reload/multiplayer | Replay idempotente, consistência host/cliente |
| FAC-16 | Campanha com divergência do cânone | Overlay da campanha preservado, fonte oficial intacta |
| FAC-17 | Fonte comunitária em desacordo com fonte oficial | Conflito marcado, não publicação de fato falso |
| FAC-18 | Catálogo cresce para muitas facções | Paginação/indexação/lotes conforme limites de desempenho a medir |

## Riscos abertos e decisões dependentes

- Cobertura de todo o canon não está pesquisada nem carregada: é um objetivo de curadoria progressiva.
- As fontes oficiais podem divergir por edição; precedência deve respeitar política de canon DEC-009 e revisão editorial.
- Controle territorial numérico, economia e conflitos armados ainda sem nível de detalhe definido.
- Não há suporte atestado a spawn de facções novas, patch de scripts, modificação de governo ou persistência de recursos em BG2:EE multiplayer.
- **Próxima decisão: DEC-032 — profundidade da simulação econômica, política e militar das organizações.**


## Companheiros desligados e facções — DEC-049 (v4.5)

Ex-companheiros podem participar de facções, assumir obrigações e criar relações **conforme evidência/condições e época**; a vinculação não é automática nem reescreve identidade canônica. Seu estado é simulado na mesma escala hierárquica do mundo, sem consumo LLM contínuo. Transferências de recursos, eventos HIGH e efeitos de engine exigem as validações e a confirmação do host pertinentes. Evitar que agendas de NPCs e facções gerem dois eventos para o mesmo fato. Ver ADR-0044/doc. 49.

## Emenda DEC-060 — organizações/guildas por ano (v5.6.1)

O catálogo de facções passa a ter representação curada **por período DR em diretórios separados**, especialmente `knowledge/periods/{year}-DR/organizations/` e `guilds/`. Identidade, lideranças, área de influência e existência devem ser consultadas conforme a data real da campanha; uma facção criada posteriormente não pode operar em 1369 por contaminação de conteúdo. Mudanças causais da campanha não reescrevem o catálogo do cânone e dependem do overlay do ramo e eventos confirmados. O andaime de pastas não afirma cobertura factual de facções do ano. Ver 60a.

## DEC-061/C — facções com fontes concorrentes no mesmo ano

Duas fontes sobre liderança, alianças, nome ou território de uma guilda/facção em **1369 DR** devem permanecer identificáveis no catálogo físico `1369-DR/{organizations,guilds}/`. A simulação não escolhe silenciosamente a versão mais recente nem gera organização mesclada por IA. Validar datas e região, perspectivas e possível retcon; conflito irresolvido impede efeito crítico derivado da afirmação. Divergência causada pela campanha vive em overlay separado, com evento confirmado e autoridade do host para efeitos mecânicos. Ver ADR-0056/doc. 61.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

NPC de facção genérico pode permanecer representação agregada. Promoção DEC-067 exige evidência de identidade e papel/ação, sem inventar pertencimento, autoridade ou conhecer segredos de facção.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: controle de passagens, portos e fronteiras por facção pode limitar rota apenas após evento confirmado e válido para a campanha, não por texto de LLM.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070: perigo político na rota e ação de facções só viram bloqueio/ataque factual após prova e curadoria. Eventos de guerra/organização de HIGH risco continuam protegidos.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Facções DEC-074 respondem a relatos recebidos e validados, não a qualquer fato global. Notícias são distintas de decisão política ou ordem de movimento de exércitos. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Guilda reconhece contribuições somente ao adquirir relatos legítimos; não imputar a membros ausentes responsabilidade sem nexo e fonte.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

A organização só conduz procedimento DEC-078 se sua competência/regras na região/época forem curadas ou explicitamente parte do overlay de campanha; poder de facto e legitimidade não são equivalentes.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Facções podem cooperar, recusar ou negociar pedidos DEC-079 conforme relações políticas e fontes em época DR correta. Filiação, rivalidade ou poder militar não implica competência judicial global.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Facções DEC-080 podem reconhecer, contestar ou ignorar pedidos conforme competência/recebimento; mudança de governo revalida autoridade, e revogação não cria onisciência.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Facção que reconhece erro pode propor desculpas/restituições DEC-081 somente por competência e recursos comprovados; não obrigar facções distantes a aceitar uma decisão automaticamente.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Organizações podem investigar e contestar membros segundo poderes de época comprovados, sem alterar liderança ou governo por decisão LLM não autorizada.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Guilda investigada não recebe acesso automático ao nome do funcionário denunciante; conhecimento e eventual resposta precisam de fonte/canal/ACL e risco.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Guilda suspeita de retaliação não é automaticamente culpada nem conhece plano da testemunha; ações exigem capacidade e informação real da facção.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Uma guilda adversária precisa de objetivos, recursos, agentes presentes e notícia validada antes de propor investigação; não tem acesso ao plano privado por ser facção simulada.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Uma facção pode financiar investigação ou receber desinformação com meios plausíveis; a IA não inventa recursos, mensageiros, fontes ou crenças oniscientes.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Facções podem ter integrantes com vínculos sobrepostos; colaboração com rival precisa de evidência contextual antes de ser classificada como traição, sem punição global automática.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Recrutar fonte de guilda rival não transforma automaticamente facção inteira em inimiga e não altera hierarquia política sem evidência e gates.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Facções podem investigar informes recebidos por canais; não acessam o parecer privado do host nem consultam todas as fontes globais. Consequências seguem política de riscos.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Cada facção só obtém views mediante canal, competência e ACL. Não sincronizar dossiês entre todas as facções nem usar avaliação privada de host como conhecimento institucional.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Facções podem propor investigações conforme objetivos/competência e disponibilidade, sem operação universal ou agentes teleportados.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Histórico de reputação por persona/observador não é reiniciado quando o plano é cancelado; eventos confirmados mantêm sua causalidade.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-094/C (Discovery v9.0)

Facções podem aguardar recursos e sofrer conflitos; deadlock de operação não justifica redefinição automática de lealdade, economia, competência ou ações políticas.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Dec-096 proposta: facções e patrulhas reagem a fase/abrangência/region tags, mas sem inventar tropas ou ordens; exigir resources e capabilities.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-097/C — Discovery v9.3

Mudanças de reputação DEC-097/C não são agregadas como preços sem política específica e conhecimento legítimo do observador.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Agentes de facção não podem transferir ownership de NPCs/scripts de outros mods por inferência narrativa.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Reputação e percepção são distintas de quest flags técnicos, cuja leitura não é rumor nem conhecimento percebido.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração DEC-102/C (Discovery v9.8)

A DEC-102/C trata divergências entre milestone validado do host e projeção derivada do Living World: exigir mapeamento DEC-101, observação DEC-100, epoch/branch e receipts, e preservar o host, facts ledger e conhecimento dos NPCs. Somente proposta de revisão CAS/autorizada; detalhes em ADR-0097/doc. 102. **Sem POC mecânica.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** a conclusão técnica de uma quest não concede automaticamente conhecimento ou crença a NPCs/facções. `QuestMilestoneAdmission` pode gerar proposta de notícia/reputação somente por regras, proveniência, tempo, geografia, visibilidade e ACL; notícia requer fonte/canal/delivery, e seus destinatários podem conhecer apenas versões parciais. Não expor identidades secretas, fontes protegidas ou raw flags por prompts/logs/dossiês. Ações mecânicas derivadas dependem de recibos host, sem atribuição presumida de PC. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **reputação contextual**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para facções podem continuar com percepções distintas apesar de errata comum, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para facções e comunidades com confiança não universal, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Reputação não sofre alteração automática por prazo vencido. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Condição não satisfeita não causa redução automática de reputação. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
