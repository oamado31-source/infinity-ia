# Arquitetura preliminar — persistência híbrida e cronologia de Forgotten Realms

**Discovery v1.2** · **Estado:** desenho técnico provisório, não SPEC aprovada  
**Fundamento aprovado:** DEC-008 / ADR-0011, DEC-011, DEC-014, DEC-019, DEC-021 e DEC-022.  
**Pendente:** DEC-009 (canon), DEC-018 (backup/migração), DEC-007 (diálogos), DEC-013 (compatibilidade).

## Objetivo

A cronologia deve afetar ações e experiências do mundo, não funcionar apenas como enciclopédia de lore. O servidor narrativo preserva o que ocorreu, o que é sabido, o que está apenas proposto e o que já pode ser consultado por regiões/NPCs.

## Modelo de dados candidato (não é esquema definitivo)

```text
CanonicalSource(source_id, titulo, autor, editora, edicao, ano_publicacao,
                localizacao_citacao, uri_referencia, versao_ingestao)
LoreEvent(lore_event_id, fonte_ids[], titulo_curto, resumo_original,
          tempo_DR_inicio, tempo_DR_fim, precisao_temporal,
          local_ids[], atores_ids[], etiquetas[], status_verificacao,
          grau_controversia, revisao, provenance)
Campaign(campaign_id, mode, epoch_DR_start, clock_policy, world_revision, ...)
LoreActivation(campaign_id, lore_event_id, activation_phase,
               trigger_world_time, ruleset_version, dedup_key, status)
EventProposal(proposal_id, cause_ids[], context_revision, actions[], status)
WorldEvent(event_id, campaign_id, origin_type, origin_id, occurrence_time_DR,
           observed_at_utc, participants[], location_id,
           causal_parent_ids[], effect_receipts[], authority, status)
KnowledgeFact(knower_id, fact_id, learned_at_world_time, channel,
              confidence, allowed_visibility)
WorldProjection(entity_or_region_id, world_revision, current_state, ...)
Snapshot(campaign_id, world_revision, event_cursor, save_fingerprint, ...)
```

**Separar status:** `IN_SOURCE` ≠ `DUE` ≠ `PLANNED` ≠ `WORLD_CONFIRMED` ≠ `MECHANICALLY_APPLIED`. Preservar precisão de calendário; se a fonte cita apenas **1371 DR**, jamais fabricar dia e mês.

## Fluxo lógico proposto

```text
Fontes verificáveis -> curadoria / verificação cronológica
      -> catálogo de LoreEvents (somente conteúdo autorizado e resumos próprios)
                  |
Clock da campanha -> comparação temporal/locacional
                  |
      Regras de disparo + DEC-009 canon (a definir)
                  |
         Plano de consequências / rumor
                  |
      Permissões + conhecimento por NPC + estado vigente
                  |
       Controller -> ações narrativas confirmadas
                       -> mudanças mecânicas apenas via host / reconciliação
                  |
              WorldEvent log
                  |
             Projeções + snapshots
                  |
   Diálogos/quest hooks/contexto para LLM local sob demanda
```

## Exemplos de regras de repercussão (não equivalem a fatos oficiais confirmados)

1. **Morte de nobre ou autoridade (lore):** quando evento verificado for efetivamente devido no calendário da campanha, alterações propostas em estabilidade, patrulhas, disputa entre facções e rumores ficam condicionadas a DEC-009, distância geográfica, condições atuais e confirmação do host para efeitos mecânicos.
2. **Notícias chegam gradualmente:** uma pessoa que estava presente pode saber no mesmo dia; o comerciante de outra cidade aprende após jornada/informante, se existir uma rota plausível. A IA não compartilha automaticamente todo o catálogo com cada NPC.
3. **Jogadores intervêm na história:** registrar a intervenção como evento da campanha. Se ela contradiz o lore, marcar `CANON_CONFLICT_PENDING`; não apagar evento ou preservar cânone à força antes da política DEC-009.
4. **Personagem visita dez vezes a mesma taverna:** manter estado e memórias; a presença de evento oficial gera ganchos e fala, mas o diretor usa cooldowns e regras para não repetir toda visita uma grande notícia.
5. **Campanhas com datas diferentes:** uma campanha em 1368 DR não pode usar fatos verificados apenas para 1372 DR como acontecimentos pretéritos.

## Importação de fontes e proveniência

- Preferir livros de cenário, aventuras e referências publicadas com identificação bibliográfica. A Forgotten Realms Wiki pode ser índice de descoberta com citações a fontes, não prova única para casos controversos.
- Classificar `EXACT_DATE`, `MONTH_ONLY`, `YEAR_ONLY`, `RANGE`, `APPROX`, `DISPUTED`. Uma entrada sem data suficiente não aciona efeitos irreversíveis automaticamente.
- Guardar resumos originais e ligações para referências; não embutir reprodução extensa de material protegido no pacote compartilhado.
- Distinguir cenário original importado, evento da obra original, história oficial, adaptação de mod e evento criado nesta campanha.

## Regras de persistência e integridade candidatas

- Event log append-only (com correções explícitas) para eventos confirmados; projeções recalculáveis e snapshots periódicos.
- Deduplicação `(campaign_id, lore_event_id, activation_phase, ruleset_version)` ou equivalente e transações atômicas apenas **dentro do banco de dados narrativo**; sem supor atomicidade com save BG2:EE.
- Registro de dependências entre fontes, eventos do mundo, conhecimento e consequências. IDs estáveis de região/NPC em compatibilidade com mods/builds (DEC-013).
- O save do host não é substituído pelo banco narrativo. Compare revisões/fingerprint antes de aplicar catch-up (ADR-0010).
- Proteger segredos dos históricos (DEC-019) e evitar que LLM use fatos futuros ou ainda não conhecidos; recuperação de conhecimento sempre filtrada por personagem/NPC e época.
- Processamento de datas e propagação por código; narrativa complementar opcional por LLM local, com fallback sem modelo.

## Gates de validação candidatos

| ID | Cenário | Resultado esperado |
|---|---|---|
| CAND-LORE-001 | Importar evento atribuído a fonte | Possui autoria/fonte, data ou intervalo DR e precisão, local, revisão e status de verificação |
| CAND-LORE-002 | Campanha antes da ocorrência | Evento não aparece como notícia consumada ou conhecimento do NPC |
| CAND-LORE-003 | Relógio cruza data e roda catch-up duas vezes | Uma ativação idempotente e nenhuma duplicação de consequência |
| CAND-LORE-004 | Personagem se encontra próximo da ocorrência | Recebe contexto/rumor permitido e localmente plausível |
| CAND-LORE-005 | Região sem canais de notícia plausíveis | NPC não conhece imediatamente o acontecimento distante |
| CAND-LORE-006 | Evento oficial conflita com morte já confirmada pelo host | Conflito é sinalizado, sem retcon ou alteração mecânica automática |
| CAND-LORE-007 | Fonte imprecisa apenas informa ano | Nenhum dia/mês arbitrário é inventado para efeito irreversível |
| CAND-LORE-008 | Duas campanhas com épocas distintas | Nenhum evento ou memória cruza a fronteira de campanha |
| CAND-LORE-009 | LLM local desligado | Eventos determinísticos e consulta a estado persistem; diálogos caem no fallback |
| CAND-LORE-010 | Recarregar save anterior | Detecta divergência entre save e projeções; oferece reconciliação, não duplica recompensa |
| CAND-LORE-011 | Fonte apresenta data contraditória | Evento entra em revisão; não há imposição automática da versão preferida |
| CAND-LORE-012 | NPC conhece notícia mas outro não | Cada um responde segundo seu `KnowledgeFact`, não todo contexto do diretor |

## Dependências de definição

- **DEC-009:** canon oficial x desvios produzidos pelos jogadores x conteúdos importados.
- **DEC-018:** retenção, checkpoint, recuperação e restauração.
- **DEC-013:** mapeamento de IDs entre mods e builds.
- **DEC-007:** apresentação de rumores/diálogos dinâmicos no BG2:EE e multiplayer.
- **DEC-006:** limites e modelos de IA local.
- **DEC-005:** impacto sobre CR, reações táticas e regras de combate.

Nenhuma destas funções está implementada ou validada no jogo nesta fase.

## Complemento DEC-052 — Continuidade de estado em migrações (Discovery v4.8)

Build pinada por campanha, backup de save mecânico e de revisão narrativa, verificação de integridade e migração em cópias isoladas são necessários para alterar o stack sem perdas. O motor BG2:EE e o banco externo **não** oferecem atomicidade cruzada conhecida; checkpoints devem ser relacionados por IDs/revisões e restaurados em conjunto quando coerentes. DEC-053 detalhará a coordenação e falhas parciais; DEC-018 permanece aberta para operações de recuperação. Nenhuma garantia técnica de rollback/migração foi demonstrada.

## Política DEC-053 — checkpoint vinculado e ramificações de recuperação (v4.9)

A DEC-008 mantém snapshots/projeções + log de eventos, mas DEC-053 exige que um checkpoint recuperável **vincule** revisão narrativa/event log watermark a uma cópia de save mecânico efetivamente concluída e íntegra. `campaign_id`, modo, `build_id`, branch/epoch e relógio são escopos essenciais; igualdade de hora não confirma causalidade. Save anterior com fatos do futuro gera reconciliação ou ramo arquivado, não retcon invisível. Rumores, reputação e conhecimento de outra linha não podem contaminar o ramo ativo. O processo deve falhar fechado se não houver evidência de quiescência/captura segura ou se operações pendentes do host seguirem `UNCERTAIN`. Documento 53 detalha os critérios candidatos; nenhuma API de save foi validada.


## Complemento DEC-054 — retenção operacional de checkpoints (Discovery v5.0)

O event log e snapshots persistentes devem ter suas dependências incluídas nos backups versionados dos pares de checkpoint; a política de retenção não pode remover segmentos necessários à restauração nem transferir memórias secretas de outro ramo. Cópia independente é opt-in; restore é ensaiado em isolamento e só é promovido após validação. Histórico canônico e dados do jogo não são automaticamente reconstituídos a partir de narrativa.

## Complemento DEC-060 — separação física anual do cânone (v5.6.1)

O antigo modelo conceitual `LoreEvent/CanonicalSource` **não exige** que o corpus seja materializado num banco único. O novo requisito aprovado é armazenar o catálogo canônico em diretórios por ano DR (`knowledge/periods/1369-DR/`, etc.), com metadados de validade e referências de proveniência. Eventos confirmados de campanha continuam em overlay/log **separado por campanha/ramo/ano**, com checkpoints e receipts. Consultas históricas entre anos são explícitas e limitadas; o estado persistente de um NPC e seu `learned_at` não é deduzido da mera presença de documentos no diretório anual. A escolha de formato físico/DB para logs e índices ainda será especificada; a partição anual do corpus de lore não deve ser eliminada por essa implementação. Ver documento 60a.

## DEC-062 — fonte, partição e revisão não são eventos confirmados

O pipeline de ingestão DEC-062 publica **revisões versionadas de lore** em arquivos físicos anuais após verificação de direitos e curadoria DEC-061; não acrescenta automaticamente eventos ao log persistente da campanha. A projeção histórica é montada com ano confirmado, ramo, ACL e revisão autorizada, sob DEC-060/028/009. Fontes e claims permanecem rastreáveis e staging não é consultável pelo runtime. A política de adoção de revisões em campanhas ativas fica para DEC-063. Ver ADR-0057/doc. 62.

## Integração DEC-063/C — referências históricas pinadas por campanha (v5.9)

A linha canônica permanece particionada em diretórios físicos **por ano DR** DEC-060. *Knowledge Pack* é um manifesto de revisões anuais e fontes DEC-061 curadas/publicadas via DEC-062, vinculado a campanha/ramo/epoch/checkpoint. A projeção de mundo combina o pack pinado e overlays de eventos confirmados, sem reescrever o log; consultas antigas/futuras obedecem vigência, ACL e causalidade. Adoção de novo pack exige diff, gates, host e checkpoint; hot migration não demonstrada.

## Integração DEC-064/C — aprendizado e crenças sem onisciência (v6.0)

Persistência separa `CanonClaim` em pastas físicas **por ano DR** (DEC-060) de episódio/memória de NPC no overlay de campanha/ramo (DEC-064). O cânone é versionado e curado DEC-061/062, vinculado por pack DEC-063; a memória preserva testemunho e mudança de crença sem alterar evento confirmado. Projeções de crença precisam acompanhar checkpoint, branch e época; não afirmar escrita em saves BG2:EE validada.


### Projeções de memória persistente — DEC-065/C (Discovery v6.1)

Eventos de experiência confirmados são referenciados por sínteses e âncoras com provenance/revision/branch. Caches e resumos são reconstruíveis; uma projeção compactada não substitui evento do ledger nem autoriza retcon. A memória de NPC reside no overlay da campanha, separado dos diretórios físicos anuais de lore DEC-060. Expurgo de dados protegidos e retenção requer política explícita, não é inferido de event sourcing.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: `RoutePlan`, `TravelLeg`, `PresenceRecord` e `TravelEvent` são projeções e eventos candidatos ligados a branch/checkpoint/versão de grafo; fatos confirmados não são substituídos por replanejamento.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

Incidentes de viagem DEC-070 ficam exclusivamente no overlay de campanha/ramo, com IDs, fontes, etapas, status, autorização e recibos, sem reescrever cânone anual. Reprocessamento/restore exige idempotência.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Persistir ledger do handoff com `incident_id`, `resolution_epoch`, checkpoint e receipt host reconciliável. Não registrar duas resoluções ao mesmo evento; após restore/fork, reavaliar idempotência e branch. Eventos novos permanecem no overlay, mantendo conhecimento canônico por ano DR.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — templates de encontro por build (Discovery v6.8)

A proposta de encontro registra `incident_id`, `template_id@revision`, `composition_hash`, `build_fingerprint` e revisões da campanha. A persistência de uma proposta não comprova execução de ação mecânica; somente eventos/receipts confirmados pelo host alteram o estado. DEC-060 preserva diretórios de cânone separados fisicamente por ano DR e os overlays continuam específicos da campanha. Sem POCs executadas.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Pós-encontro gera eventos confirmados na campanha/ramo e links para receipts; limpeza física não escreve no cânone anual.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Ledger causal DEC-074 diferencia fato confirmado, comunicação, crença e impacto. Manter tudo em overlay por campanha/ramo; cânone físico anual DEC-060 não se altera. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Persona, vínculo factual privado, suspeita, destinatário e evento de revelação pertencem ao overlay de campanha/ramo, com proveniência/tempo. Restores e divergências não podem importar conhecimento de identidades de futuros estados.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Casos, acusações, decisões e receipts DEC-078 ficam no overlay privado por campanha/ramo, não na base de lore anual; save e checkpoint precisam reconciliar antes de aplicar sanção.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Pedidos, autorizações, respostas e recibos DEC-079 são eventos de overlay da campanha/ramo, não documentos do corpus canônico. Checkpoint, revisão e KPack fixado garantem causalidade.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Ledger de ordem DEC-080 registra versões, tombstones, entregas, ACKs, crenças e gate de execução por branch/epoch; overlay separado do cânone anual fisicamente dividido.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Danos, revisões e reparações DEC-081 permanecem no overlay por campanha/ramo com cadeia causal; não alteram diretórios físicos de conhecimento por ano DR nem fingem rollback de estados históricos.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Persistir investigação e cadeias causais no overlay de campanha/ramo com eventos e revisões, preservando diretórios físicos por ano DR e snapshots coerentes.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Source identity, testimony, evidence, ACL e disclosure são overlays privados com checkpoint e branch; cânone físico por ano DR permanece isolado.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Casos de ameaça/proteção e suas provas vivem no overlay privado de campanha/ramo, nunca nos diretórios anuais de lore. Checkpoints guardam plano e recibos.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Manter planos e provas em overlay de campanha/ramo com checkpoint/ano DR; revisões e ACL não entram no corpus canônico anual DEC-060.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Rumores plantados vivem no overlay privado por campanha/branch, com período DR e revisão; restauração não leva rumor futuro ao passado. O lore anual físico permanece inalterado.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Compromissos do NPC dependem de branch, checkpoint, identidade e Knowledge Pack; retroceder save não publica futuros vínculos secretos.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Contratos privados de informantes, pagamentos, entregas e compromissos pertencem ao overlay por campanha/ramo, com cronologia DR e revisões, não ao corpus anual.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

`SourceClaim` e `ClaimAssessment` pertencem a overlay por ramo/checkpoint, sem converter um rumor em fato persistente; restores não importam informação futura.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Versionar dossiês e views por campaign/branch/epoch e KPack; corroboração futura não reescreve revisão antiga nem informação recebida por NPC em outro ano DR.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Plano e suas revisões são overlay por campanha/branch e ano DR, com checkpoint/epoch; restauração não migra approvals de outra linha temporal.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Replanejamento referencia campanha, ramo, janela DR e Knowledge Pack pinado; restore antigo não recebe triggers do futuro nem versão nova de forma silenciosa.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Reservas por recurso usam janela DR, branch, checkpoint e epoch; TTL de sistema não equivale a dias DR nem libera viagem/ação pendente sem receipt.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Persistir epoch/leases/grafo com branch/clock DR/checkpoint, revalidando monotonic clocks após restart; conciliar recibos antes de reutilizar NPC ou item.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

DEC-095: log Saga/compensações é overlay campanha/branch/epoch, jamais retcon de lore físico por ano DR. DEC-096 proposta: catálogo curado físico anual + regras declarativas separadas + AppliedImpact/KnowledgeAcquisition somente em overlay; nenhum evento futuro exibido por alias de diretório.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-097/C — Discovery v9.3

Exigir que a composição DEC-097/C seja projeção por snapshot/epoch e preserve receipts históricos; não reescrever cronologia persistida.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Camadas de persistência devem distinguir último snapshot host-confirmed, projeção e observação host; replay/checkpoint não reenvia comandos incertos.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Eventos cronológicos produzem estados propostos; não substituem quests/globals nem scripts nativos na área.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Action Gateway mantém writes independentes da allowlist de probes de leitura; read capability não confere write.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração DEC-102/C (Discovery v9.8)

Correção DEC-102 pertence ao overlay de ramo; cânone por ano DR e fatos históricos confirmados não são reescritos. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** marcos confirmados de quests originais são **origens candidatas** de regras históricas/regionais, não fatos canônicos escritos em `knowledge/periods/<ANO>-DR/`. A admissão exige prova reconciliada DEC-100/101/102, clock DR e branch adequados; a matriz DEC-096 filtra local, fase e precondições e DEC-097 compõe impactos. Escopo global não dá conhecimento universal. Evento proposto, evento host-confirmed e rumor entregue são distintos; nenhum efeito mecânico sem Action Gateway/receipt. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **Action Gateway**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para separação entre cânone e notícias contextualizadas por época, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para cânone, overlay e conhecimento social separados, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Action Gateway, idempotência e recibos antes de alterar inventários. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Action Gateway valida cada etapa tipada, sem comando emitido pela condição satisfeita. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Persistir revisões escrow por campanha/ramo/DR; não misturar snapshots, Knowledge Packs nem saldos entre forks.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
