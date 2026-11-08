# ADR-0058 — Knowledge packs versionados por campanha e atualizações seletivas com análise de impacto

- **Decisão:** **DEC-063**, opção **C**, aprovada explicitamente pelo idealizador em **2026-11-06**.
- **Estado:** **APROVADA como política de Discovery; NÃO implementada nem testada**.
- **Versão:** Infinity AI Discovery **v5.9**.
- **Documento técnico:** `docs/63-knowledge-packs-por-campanha-diff-curadoria-e-migracao-segura.md`.
- **Precedência obrigatória:** DEC-060/C e seu adendo (ADR-0055) — **separação física do cânone em diretórios por ano DR**; DEC-061/C (ADR-0056) — proveniência, conflitos e curadoria contextual; DEC-062/C (ADR-0057) — importação legítima, staging e publicação aprovada. Estas três decisões **não são alteradas**.
- **Relacionadas:** DEC-008/009/011/012/019/020/022/028/029/050/051/052/053/054/055/056/058/059/060/061/062; DEC-006/013/015/017/018 ainda abertas em seus escopos.

## Problema

O catálogo histórico pode evoluir depois que uma campanha já iniciou. A adoção automática de uma revisão que muda a história conhecida, as facções, missões, segredos ou a cronologia do mundo pode contradizer o *event log*, os saves BG2:EE e as escolhas dos jogadores. Congelar eternamente a base impede correções válidas. É preciso incorporar revisões **sem reescrever retroativamente fatos já confirmados**.

## Alternativas consideradas

- **A — Atualização automática e imediata:** mantém todos no pacote mais recente, mas expõe campanhas a retcons e divergências silenciosas.
- **B — Congelar definitivamente o pacote inicial:** garante estabilidade, mas inviabiliza correções e enriquecimento curatorial legítimos.
- **C — Pin por campanha e atualização seletiva, avaliada, autorizada e recuperável:** **APROVADA**.

## Decisão vinculante

1. **Vinculação por campanha e ramo.** Ao criar campanha, registrar um *KnowledgeBinding* versionado: `campaign_id`, `branch_id`, `world_epoch`, `build_id`, `knowledge_pack_id`, `manifest_hash`, `per_year_revision_refs`, `curation_policy_revision`, `active_from_checkpoint` e provas de origem. O ano inicial **não** é fixado em 1369 DR (apenas referência inicial dos testes DEC-023). Um save/restauração deve recuperar a vinculação coerente com o ramo e o instante histórico.
2. **Manter pastas físicas anuais.** A publicação curada continua ocorrendo em `knowledge/periods/<ano>-DR/<categoria>/` conforme DEC-060. *Knowledge pack* é um **manifesto de referências imutáveis a revisões de partições anuais**, e não uma base global com conteúdo factual de todos os anos. Pode listar anos relevantes e hashes sem tornar todos os conteúdos consultáveis; o resolvedor permanece restrito à partição do ano confirmado, abrindo antecedentes somente por vigência/proveniência/ACL. Informações de anos futuros não são fatos já ocorridos.
3. **Proveniência conservada.** Cada revisão anual mantém `Source`, `Claim`, `ConflictSet`, `CuratedResolution`, status epistêmico e período de vigência da DEC-061. Uma nova revisão não autoriza mesclar versões contraditórias nem converter `UNRESOLVED` em fato. Identidade e rastreabilidade de todas as fontes devem sobreviver à migração.
4. **Publicação não equivale a adoção.** A promoção de fonte ao catálogo pela DEC-062 produz uma versão disponível para avaliação; **nenhuma campanha existente migra por essa operação**. Campanhas distintas e branches podem continuar em versões diferentes.
5. **Diff semântico e temporal antes de qualquer troca.** Comparar revisões anuais, entidades/identidades, datas/validade, proveniência, nível de confiança, conflitos, permissões, conhecimento já adquirido, missões, vínculos de personagens, estados narrativos confirmados e *overlays* específicos. Distinguir: (a) editorial/baixo risco, (b) novos fatos compatíveis, (c) mudanças narrativas relevantes, (d) conflito/incerteza/alto risco, (e) alteração do conteúdo efetivamente disponível na build. Informação ausente no índice **não** implica ausência de impacto.
6. **Aplicação por seleção explícita.** O anfitrião recebe uma proposta com itens, riscos, dependências, previsões de efeito e possibilidade de rejeitar/adiar. **Padrão inicial: aprovação explícita do anfitrião para adotar um novo pack**, com revisão humana obrigatória em conteúdo substantivo/conflitante ou com fatos já observados. Uma automatização futura de correções estritamente `LOW` pode ser permitida **somente** por política pré-autorizada, limitada, auditável e comprovada por testes. O modelo de IA não aprova a própria alteração. Decisões `HIGH/UNCERTAIN` seguem *fail-closed* e gates especiais já aprovados.
7. **Sem reescrita de história nem conhecimento retroativo.** Eventos mecânicos confirmados pelo host, missões concluídas, decisões dos jogadores, história pessoal, segredos e eventos do *event log* não podem ser silenciosamente alterados para concordar com nova fonte. *Overlays* da campanha mantêm sua causalidade e prevalecem na projeção do ramo quando legitimamente confirmados, sem alterar o cânone original. Conhecimento de NPC continua dependente de aquisição/difusão legítima DEC-028/029; corrigir fonte não torna todos oniscientes.
8. **Pré-condições de coerência.** Não promover revisão no meio de operações mecânicas pendentes ou `UNCERTAIN`, checkpoint incompleto, importação parcial, retentativa de operação destrutiva, migração de build concorrente, mudança de relógio incompatível ou divergência host/clientes. Exigir ponto seguro do ciclo da campanha, referência ao último checkpoint íntegro DEC-053, retenção e recuperação DEC-054. Se o jogo não permitir janela segura sem interrupção, **adiar**; não alegar hot swap validado.
9. **Transação lógica e recuperação.** Preparar candidato sem visibilidade para NPCs/jogadores; verificar hashes, permissões, dependências, cobertura de anos e caches, fixar `old_binding`, obter aprovação válida e promover **logicamente** o manifesto ativo de uma só vez sob um mecanismo a especificar. Falha ou estado `UNCERTAIN` não causa migração parcial: bloquear consultas novas e reconciliar ao último vínculo íntegro. Não há garantia prévia de transação física BG2:EE–Infinity AI; recuperação consistente depende de SPECS/POCs.
10. **Reversão sem apagar causalidade.** Conservar manifesto antigo, revisões anuais referenciadas e checkpoint restaurável enquanto exigido. Rollback **não** consiste em apagar evento confirmado posterior: se a campanha avançou com o novo pack, exigir análise causal e eventual recuperação para ramo/checkpoint compatível, com consentimento adequado. Não substituir `last-known-good` por uma revisão não verificada.
11. **Privacidade, rede e desempenho.** Caches, prompts, índices, backups e workers LAN estão vinculados a `campaign_id/branch_id/pack_revision/year_DR/ACL`. Workers com jobs da revisão anterior retornam `STALE`, não fatos novos. Nó LAN não pode promover pack. Sem envio de arquivos privados ou fonte protegida à rede/nuvem por padrão; respeitar DEC-055–059. Migrações ficam atrás das prioridades do jogo DEC-056.
12. **Métricas e auditoria.** Registrar proposta, diff, impacto, itens aceitos/recusados, revisor, consentimento, hashes do manifesto, checkpoint e resultados de gates; expor ao anfitrião cobertura incompleta (`EMPTY/PARTIAL/REVIEWED`). Log não armazena material protegido extenso ou segredos de PCs em local indevido.

## Estados conceituais (não API implementada)

`PINNED_A → UPDATE_AVAILABLE → DIFF_PREPARED → IMPACT_REVIEW → (DEFERRED | REJECTED | BLOCKED | APPROVED) → SAFE_POINT → CHECKPOINT_VERIFIED → PREPARED_B → COMMIT_BINDING_B → VERIFIED_B`.

Falha/`UNCERTAIN` em qualquer fase de adoção mantém/recupera A **somente se houver evidência de que ainda é o estado causal correto**; caso contrário `FREEZE_AND_RECONCILE`. Não realizar *replay* destrutivo para fingir rollback.

## Consequências e limites

- **Benefícios:** catálogo evolutivo e campanhas estáveis; aderência a lore, fontes e temporalidade; migração reproduzível, seletiva, auditável e baseada em consentimento.
- **Custos:** múltiplas revisões retidas, armazenamento/versionamento anual, diffs semânticos dependentes de boa evidência, interface de revisão, caches por vínculo e checkpoints coordenados.
- **Pendente:** estruturas definitivas, políticas LOW, granularidade do diff, formato do manifesto, plano de retention, algoritmos de impacto, janela segura BG2:EE/EEex e critérios de teste/multiplayer. Nada foi testado na engine.

## Critérios candidatos de aceite

1. Campanhas A e B usam packs diferentes sem contaminação entre ramos.
2. Atualização do catálogo não troca automaticamente o vínculo de uma campanha.
3. Revisão de 1370 DR não vaza para NPC de 1369 DR.
4. Fato de 1368 com continuidade demonstrada pode ser recuperado por consulta explicitamente autorizada.
5. Dois claims contraditórios persistem como versões distintas com curadoria rastreável.
6. Atualização que contradiz quest concluída é bloqueada/depende de revisão; nunca reescreve save.
7. Nenhum LLM ou nó LAN promove revisão unilateralmente.
8. Se checkpoint/host receipt ou arquivo anual necessário estiver ausente, promoção é bloqueada.
9. Cache e job de revisão A não se incorporam a B como saída válida.
10. Reversão pós-evento confirmado exige análise causal e não apaga log.
11. Restauração para save anterior reconstitui pack e branch corretos.
12. Falha de rede/crash não expõe pacote parcialmente adotado.

## Decisão seguinte

**DEC-064 — Evolução das crenças e memórias individuais dos NPCs após correções de conhecimento.** Decidir se atualizar fontes deve reescrever automaticamente crenças existentes, congelá-las ou preservar memória com correção/difusão contextual. **DEC-006/013/015/017/018 permanecem abertas**, e DEC-007/016 também não foram resolvidas. Nenhum suporte à migração de knowledge pack foi demonstrado.
