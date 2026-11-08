# DEC-063 — Knowledge packs por campanha: diff temporal, adoção controlada e recuperação

**Discovery v5.9 · opção C aprovada · ADR-0058 · proposta para SPECS, não implementada/testada.**

## 1. Objetivo e fronteiras de autoridade

A curadoria e a publicação de fatos históricos (DEC-062) não devem alterar implicitamente campanhas que já usam revisões anteriores. Separar três processos: **publicação** de uma revisão anual curada, **oferta de migração** a uma campanha e **consumo** do novo conhecimento por NPCs após promoção autorizada. O host BG2:EE é autoridade mecânica (DEC-011). Infinity AI organiza a narrativa confirmada; modelos, importadores e nós LAN produzem somente propostas.

**Invariantes:**

- DEC-060: arquivos **fisicamente separados por ano DR** em `knowledge/periods/<ano>-DR/...`. Um manifesto de pack armazena somente referências/hashes, **nunca** unifica lore de todos os anos em um corpus único.
- DEC-061: preservar fonte, edição, proveniência, intervalo/precisão DR, conflitos e decisões curatoriais, inclusive após migração.
- DEC-062: fatos novos entram primeiro em staging protegido e só recebem publicação anual após validação/curadoria autorizada; esse fluxo **não** muda campanhas por si só.
- DEC-008/009: canon histórico e overlays de campanha/ramo são domínios diferentes; eventos confirmados não são retocados para coincidir com revisão editorial.
- DEC-028/029: uma verdade curada pode continuar desconhecida de certos NPCs ou circular como rumor; ACL e aquisição de conhecimento são avaliadas antes da inferência.
- DEC-052/053/054: pin de build, checkpoints coerentes, backups e recuperação são gates independentes da troca de referência narrativa.
- DEC-011/012: o pack não emite comandos mecânicos; nenhum efeito de jogo é aplicado sem gateway e evidência do host.

## 2. Modelo conceitual de dados (não schema final)

```text
AnnualPartitionRevision {
  year_DR, revision_id, categories[{category, manifest_hash}],
  claim_ids[], conflict_set_ids[], source_refs[],
  curation_revision, coverage_status, published_at, license_scope
}
KnowledgePackManifest {
  pack_id, pack_revision, manifest_hash, curation_policy_revision,
  annual_refs[{year_DR, partition_revision_id, revision_hash}],
  scope, signed_or_verified_provenance, created_at
}
CampaignKnowledgeBinding {
  campaign_id, branch_id, mode, build_id, epoch_id,
  knowledge_pack_id, knowledge_pack_revision, manifest_hash,
  annual_refs_snapshot, campaign_policy_revision,
  active_from_checkpoint_id, bound_at_world_time_DR,
  approved_by, approval_ref, status
}
KnowledgeUpdateCandidate {
  proposal_id, campaign_id, branch_id,
  source_binding_id, target_pack_id, candidate_annual_refs,
  diff_ref, dependency_graph_ref, assessed_risk,
  impacted_event_ids[], impacted_quest_refs[], impacted_npc_memories[],
  impacted_secrets[], impacted_overlay_ids[], unverified_dependencies[],
  proposed_actions[], blockers[], reviewer_ref, host_approval_ref
}
KnowledgePromotionAttempt {
  attempt_id, source_binding_id, target_binding_id,
  checkpoint_ref, last_known_good_ref, safe_point_evidence_ref,
  index_cache_epoch, affected_jobs[], result,
  uncertain_reconciliations[], audit_ref
}
```

*Hashes* identificam revisões, mas não provam veracidade do lore nem compatibilidade com save. Manifestos podem incluir somente anos já curados, sem implicar cobertura total. Referências não revelam conteúdo protegido sem autorização. O formato de `knowledge/campaigns/` permanece conceitual; não armazenar saves ou segredos reais no Discovery.

## 3. Vinculação sem violar a partição anual

```text
KnowledgePack P-1.0 (manifesto de referências)
  ├── 1368-DR  -> revisão anual R2, hash H2 (se publicada)
  ├── 1369-DR  -> revisão anual R7, hash H7 (se publicada)
  └── 1370-DR  -> revisão anual R1, hash H1 (se publicada)
                 [REFERÊNCIAS, NÃO ÍNDICE DE LORE GLOBAL]

Campanha A / ramo principal -> KnowledgePack P-1.0
Campanha B / ramo principal -> KnowledgePack P-1.1
Campanha A / ramo derivado  -> vínculo próprio, herdado e revisável

Consulta NPC em 1369 DR:
  relógio confirmado -> partição física 1369-DR na revisão pinada
                    -> antecedentes relevantes e validados (se autorizados)
                    -> overlay desta campanha/ramo
                    -> conhecimento/ACL do NPC
                    -> validação de saída por risco (DEC-060)
```

Ano de publicação editorial da fonte **não** se confunde com ano DR do evento. O ano do mundo não é decidido pela IA. No exemplo acima, os IDs/hashes são ilustrativos e não representam packs realmente publicados.

## 4. Classes de alteração e matriz de risco (valores qualitativos candidatos)

| Classe | Exemplo hipotético | Política inicial de adoção |
|---|---|---|
| `EDITORIAL_LOW` | Correção de grafia sem mudança de identidade/data/significado | Proposta com explicação; host aprova. Automação futura só com allowlist explícita, limites e testes. |
| `ADDITIVE_COMPATIBLE` | Nova referência verificável que não contradiz eventos conhecidos | Avaliação de dependências e host aprova; efeito informativo condicionado a ACL/clock. |
| `NARRATIVE_IMPACT` | Alteração no papel histórico de facção relevante para missão ativa | Revisão humana e anfitrião; migração pode ser adiada ou parcialmente rejeitada. |
| `CONFLICTED` | Revisões discordam, `UNRESOLVED` ou vigência incerta | Bloquear fato assertivo ou manter versão anterior; resolver por curadoria DEC-061. |
| `MECHANICAL/CRITICAL` | Mudança requer flags, itens, scripts ou alterar evento confirmado | **Não** aplicar como migração de lore; acionar gates DEC-012/034/050/052/053 e prova de compatibilidade. |
| `UNVERIFIED` | Fonte/índice/backup/host sem evidência suficiente | *Fail-closed*, adiar e sinalizar limite. |

Uma correção editorial aparentemente leve pode mudar aliases de entidades, índices ou ACL: só é `LOW` após verificação de impacto, não pela aparência do texto. Conteúdo de alto impacto não se torna seguro ao dividir em dezenas de alterações `LOW`.

## 5. Pipeline de avaliação e promoção

```text
PACK_PUBLISHED_IN_CATALOG
    -> DISCOVER_UPDATE (sem mutação de campanha)
    -> PINNED_BINDING_A + CANDIDATE_B
    -> DIFF_VERSIONED (per-year, claims, provenance, conflicts)
    -> ANALYZE_DEPENDENCIES (quests, PCs, NPCs, event log, overlays, build)
    -> CHECK_ACL_RIGHTS_AND_COVERAGE
    -> RISK_GATES (UNKNOWN/HIGH -> BLOCK or HUMAN REVIEW)
    -> HOST_PREVIEW (adotar parcialmente / adiar / rejeitar)
    -> HOST_APPROVAL + REQUIRED_CURATOR_APPROVAL
    -> SAFE_POINT_AND_QUIESCENCE (não presumidos; provar em POC)
    -> VERIFIED_CHECKPOINT + RETAIN_OLD_PACK
    -> PREPARE_INDEX_AND_BINDING_B_IN_ISOLATION
    -> PROMOTE_BINDING_ATOMICALLY_AT_LOGICAL_LEVEL
    -> VERIFY_POSTCONDITIONS (epoch, indexes, host/client, ACL)
    -> ADOPTED_B (audit, cache/jobs revisionados)
```

O princípio de atomicidade **é lógico e alvo de SPEC**; não há garantia de mutação atômica entre BG2:EE, banco e workers. Um checkpoint do jogo só é coerente quando DEC-053 o comprovar. Se ação externa estiver `UNCERTAIN`, parar e reconciliar; nunca refazer ação destrutiva por conta de timeout. Não impor troca no meio de combate, diálogo/sync ou save se a ponte não demonstrar janela segura.

### Atualização seletiva

- Diferenças são avaliadas por unidade de alegação ou conjunto fechado de dependências, nunca apenas por arquivo. O anfitrião pode escolher o que entra **quando os componentes são independentemente compatíveis**.
- Não criar um pack parcialmente publicado sem manifesto explícito e sem rastreabilidade de dependências. Revisões parcialmente adotadas devem gerar novo manifesto e revisão auditada; mudanças acopladas entram juntas ou ficam todas de fora.
- Uma escolha por campanha não altera o catálogo canônico, as outras campanhas ou o staging de novas fontes.
- A adoção deve ser idempotente pelo ID de tentativa e revisões de origem/destino; se a origem mudou durante a análise, refazer o diff e revalidar a aprovação.
- A documentação não aprova leitura/escrita nova na estrutura real do save, alteração de mods ou integração EEex; são POCs futuras.

## 6. História confirmada, rumores e memórias

Uma fonte recém-curada pode afirmar que determinada guilda existia em 1369 DR. Se nesta campanha a guilda foi destruída após um evento confirmado, a projeção do ramo deve mostrar a consequência dessa destruição; não ressuscitar a guilda. O registro histórico e as mudanças do ramo continuam rastreáveis. Se a fonte revela um fato até então desconhecido, o NPC não recebe conhecimento automático. Memórias, crenças, rumores e correções pessoais exigem política própria da **DEC-064**, ainda não decidida.

O log de evento confirmado não deve ser editado para acomodar uma suposta descoberta. Se o pacote novo corrige algo que um NPC já disse no passado, preservar o diálogo e sua proveniência e decidir em fluxo separado como a informação corrigida se dissemina. Isto não transforma desinformação passada em evento verdadeiro.

## 7. Erros, recuperação e retenção

| Falha | Conduta segura |
|---|---|
| Pasta anual ausente, incompleta ou sem direitos | Não promover; continuar pack antigo e informar limitação. |
| O diff foi feito sobre revisão A obsoleta | Invalidar proposta e autorização; avaliar de novo. |
| Chegou job LLM da revisão A após promover B | Rejeitar resposta `STALE`; novo job só com contexto/ACL de B. |
| Divergência entre índice anual e manifesto | Bloquear nova leitura e reconstruir/validar índice antes de prosseguir. |
| Worker LAN desconectado durante preparo | Manter A, cancelar ou pausar candidatos; não inventar sucesso. |
| Crash entre preparo e commit | Reconciliar qual binding está ativo por trilha durável; não expor estado parcial. |
| `UNCERTAIN` mecânico ou checkpoint incompleto | Bloquear migração até reconciliação; nunca reaplicar ações cegamente. |
| Restauração de save antigo com pack novo | Selecionar branch/checkpoint e pack históricos correspondentes, não consumir automaticamente B. |
| Solicitação de rollback após novos eventos confirmados | Não apagar eventos; decidir recuperação causal/ramo compatível e consentimento. |
| Pack antigo removido por retenção indevida | Bloquear recuperação e reportar perda de evidência; não reconstruir fatos por chute. |

Retenção de revisões anuais, chaves/manifestos e backups deve considerar campanhas ainda ativas e checkpoints referenciados; não excluir referências necessárias. Política quantitativa e GC só em SPECS/DEC-018.

## 8. Privacidade, riscos e observabilidade

- `campaign_id/branch_id/epoch_id/pack_revision/year_DR` fazem parte de chaves de cache, resultados, ferramentas, jobs e autorizações; revisão antiga não é reutilizada após mudança.
- Índices semânticos e workers são limitados por ano **na recuperação**, não apenas com filtro posterior; o manifesto global é índice de referências, não base única de texto.
- Receipts mecânicos, saves, histórias de PCs, arquivos integrais de fontes e conteúdo com licença restritiva não são copiados para documentação compartilhável ou nós não autorizados.
- A cadeia de auditoria mantém o mínimo necessário (manifest hash, IDs, mudanças, revisores e aprovações), sem revelar segredos ou excertos longos protegidos.
- Recurso de verificação é prioridade não urgente do Resource & Performance Director; o host/multiplayer tem prioridade.
- Monitor DEC-055 deve relatar incompatibilidade de pack, index mismatch, backlog e falha de recovery sem autoaplicar mudanças críticas.

## 9. Matriz de testes candidatos — T063 (não executados)

1. `T063-01`: campanha recém-criada fixa pack específico e suas revisões anuais com manifesto verificável.
2. `T063-02`: publicação de pack B no catálogo não altera vínculo de campanha em A.
3. `T063-03`: campanhas distintas e branches distintos preservam pacotes e caches separados.
4. `T063-04`: pasta física 1369-DR é consulta primária quando relógio confirmado está em 1369 DR.
5. `T063-05`: referência de 1370-DR não é mostrada como evento consumado em 1369 DR.
6. `T063-06`: fato anterior é consultado somente com validade temporal, proveniência e autorização demonstradas.
7. `T063-07`: novo pack preserva claims concorrentes/ConflictSets e resoluções da DEC-061.
8. `T063-08`: origem, edição e direitos de fonte continuam rastreáveis após revisão.
9. `T063-09`: fonte em staging, sem publicação da DEC-062, não aparece em candidato de update.
10. `T063-10`: diff aponta mudança de data/entidade/identidade de guilda mesmo que arquivo tenha nome igual.
11. `T063-11`: diff de uma nova fonte que contradiz diálogo confirmado não reescreve diálogo passado.
12. `T063-12`: overlay com guilda destruída prevalece na campanha sem alterar cânone anual.
13. `T063-13`: correção de conhecimento não atribui automaticamente o novo fato ao NPC.
14. `T063-14`: mudança dependente não permite atualização parcial que gere contradição.
15. `T063-15`: adoção LOW sem política pré-autorizada ainda requer host; HIGH/UNCERTAIN bloqueado.
16. `T063-16`: proposta sem revisor/host válido não migra campanha.
17. `T063-17`: alteração de build/mod ou flags não é tratada como simples update informativo.
18. `T063-18`: `UNCERTAIN` mecânico impede preparação e commit.
19. `T063-19`: ausência de checkpoint verificado impede troca.
20. `T063-20`: ação do host com receipt novo durante diff invalida proposta stale.
21. `T063-21`: crash durante preparo não expõe parte de B ao NPC.
22. `T063-22`: falha após commit entra em reconciliação, não reverte apagando eventos novos.
23. `T063-23`: save antigo escolhe pack antigo e branch compatíveis; isolamento multijogador.
24. `T063-24`: última versão conhecida íntegra permanece recuperável por manifesto e backing anual.
25. `T063-25`: worker LAN revogado não promove versão ou retorna conteúdo aceito.
26. `T063-26`: LLM retorna contexto da revisão A após adoção B → rejeição por versão.
27. `T063-27`: novo índice vazio não é tratado como prova de inexistência de entidade.
28. `T063-28`: revisão de 1369 não modifica arquivos físicos de 1370.
29. `T063-29`: cache, backup, log ou diff não vaza segredo de PC nem conteúdo protegido extenso.
30. `T063-30`: carga de migração não compromete loop prioritário de gameplay/multiplayer.
31. `T063-31`: host rejeita B e campanha continua em A sem efeito colateral.
32. `T063-32`: testes/relatórios não afirmam integração BG2:EE/EEex comprovada sem evidências de POC.

## 10. Próxima decisão e pendências

**DEC-064:** política de correção e evolução de crenças/memórias NPC após atualização da fonte de conhecimento (sem reescrever automaticamente memória passada ou conceder onisciência). As decisões abertas DEC-006/007/013/015/016/017/018 continuam abertas. A SPECS determinará schema, interface de diff/aprovação, atomicidade efetiva, ponto seguro do host, retenção, baselines e métricas. **Nenhuma POC ou teste de runtime executado.**

## Integração DEC-064/C — aprendizado e crenças sem onisciência (v6.0)

Adotar Knowledge Pack novo por campanha DEC-063/C **não corrige automaticamente memórias nem crenças dos NPCs**. Segundo DEC-064/C, a mudança pode oferecer novas fontes a serem descobertas, mas só aprendizado legítimo causa episódio e revisão de crença; o último permanece no overlay de campanha/ramo/NPC. Histórico de falas, fontes, eventos e recepções não sofre retcon. Manter diretórios físicos por ano DEC-060 e conflitos/curadoria DEC-061/062.


### Invalidar sínteses após alteração de Knowledge Pack — DEC-065/C (Discovery v6.1)

Uma revisão de conhecimento pode invalidar materializações dependentes, mas não reescrever eventos de aquisição/diálogos ou atualizar crenças automaticamente. Ao migrar pack, reconstruir somente resumos vinculados às fontes ainda autorizadas, preservando origens por NPC/campanha/branch. Cânone continua fisicamente segregado por ano DR.

### Integração DEC-066/C — pack não reatribui identidade de NPC (v6.2)

Adoção de nova revisão de Knowledge Pack não faz correspondência automática de personagem canônico a `EngineObservation` nem altera `NPCIdentity`. O diff pode exigir invalidar referências/observações dependentes; memória privada e histórico de encontros permanecem no overlay do ramo, nunca nas pastas anuais. Caso status seja `STALE`, adiar falas/ações dependentes até reconciliar.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

Novo Knowledge Pack DEC-063 não individualiza NPCs por si só. Promoção DEC-067 continua circunscrita à campanha/ramo com identidade comprovada e eventos confirmados.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

Quando NPC sai/retorna de hibernação DEC-068, vincular todo catch-up ao Knowledge Pack fixado por campanha, à versão temporal e ao branch. Mudanças de versão sem migração DEC-063 autorizada invalidam resultados obsoletos; sem onisciência de NPC.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: planos viajam com `graph_revision` e Knowledge Pack pinado; nova revisão histórica exige diff/impacto e autorização antes de rerotear uma campanha.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070 fixa revisão do Knowledge Pack em incidentes; update da campanha exige revalidação de fatos de rota e não altera efeitos já confirmados sem migração controlada.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Handoffs DEC-071 carregam a revisão vinculada do Knowledge Pack DEC-063; mudança de revisão durante reserva exige revalidar o contexto antes de usar uma fonte nova. Não aplicar revisão do cânone automaticamente ao incidente.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Manifest de Knowledge Pack DEC-063 referencia versões anuais, enquanto DEC-072 vincula template/revisão/build; atualizar um não autoriza ativação automática do outro em campanha em curso.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Closure de encontro usa Knowledge Pack fixado à campanha/ramo como contexto, sem modificar diretórios anuais físicos ou ingerir lore automaticamente.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Propagação DEC-074 fixa revisão do Knowledge Pack e ramificação: atualizar pack não faz NPCs conhecerem automaticamente novos fatos. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Nova revisão editorial não recalcula retroativamente autoria de encontro, contribuição, reconhecimento ou punição; overlay da campanha preserva cadeia causal.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Nova revisão do Knowledge Pack não altera vínculos secretos, reputações de personas ou conhecimento dos NPCs automaticamente; atualização seletiva não reescreve overlay pessoal.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação por evidências (Discovery v7.3; não implementada)

A investigação de personas DEC-076 usará ledger privado por campanha/ramo, com pistas e hipóteses revisáveis, origem/independência de fontes, contraprovas e estados inconclusivos. Suspeita ou fala LLM não confirma identidade e não permite divulgação; vínculo factual restrito exige evidências/DEC-066, e revelação exige ACL/consentimento/risk gate por audiência (DEC-019/028/041/045/046). Rumores e repercussões DEC-029/074/075 são separados de fato e punição. **Preservar `knowledge/periods/<ANO>-DR/` fisicamente por ano, sem evidências privadas no cânone.** ADR-0072/documento 77; 58 testes não executados, sem POC BG2:EE/EEex/multiplayer.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Policy de autoridade DEC-078 é vinculada à revisão do Knowledge Pack/ano DR; correção de lore não condena/absolve PCs retroativamente sem avaliação de impacto.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Uma requisição interjurisdicional DEC-079 referencia a revisão do Knowledge Pack da campanha; atualização editorial não confirma novo tratado nem altera pedidos já emitidos automaticamente.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Atualização KPack DEC-063 não reescreve as revisões de mandados DEC-080; validar política e época do ramo antes de emitir/retificar/reconhecer.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Mudança do Knowledge Pack não recalcula automaticamente reparação, autoridade ou indenização de evento passado; revalidação/migração requer política explícita.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

A competência institucional é avaliada contra Knowledge Pack fixado por campanha/ramo; atualização editorial não reabre automaticamente casos passados.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Migração editorial de KPack não publica segredos de testemunhas e não reclassifica depoimentos privados como conhecimento geral.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Atualização de KPack não recalcula retroativamente agressão/proteção e não publiciza testemunhas; contexto do ano/branch permanece pinado.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Atualização de pack não altera conhecimento adversário, grants, plano privado nem comprovante de descoberta passada sem migração autorizada.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Mudança de Knowledge Pack não legitima automaticamente isca, documento falso ou confissão. Estado de engano é versionado em overlay e não transferido por branch.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Atualização seletiva de Knowledge Pack não reatribui compromissos secretos ou crenças aos NPCs ativos automaticamente.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Atualizar Knowledge Pack não cria, encerra ou corrige automaticamente contratos ou entregas da campanha; fixação por ramo e checkpoint permanece.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Knowledge Pack pinado não torna personagem onisciente; migração de revisão curada não reavalia automaticamente testemunhos do branch sem gate.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

DossierRevision referencia KPack pinado e checkpoint; upgrade de fontes não reescreve avaliações/publicações anteriores, que exigem nova revisão e análise de impacto.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Troca de Knowledge Pack pode invalidar fundamentos de plano; revisar antes de seguir, sem alterar retroativamente ações confirmadas.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Knowledge Pack pinado precisa corresponder ao checkpoint, branch e instante DR; revisão de plano não atualiza pack automaticamente.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Mudança de KPack/revisão causa revalidação de operações e locks, sem importar exclusividades de outro ramo ou recriar lore canônico.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Resolução de deadlock conserva Knowledge Pack pinado da campanha e invalida job stale em migração de branch/checkpoint, sem consultar lore futuro.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

A matriz proposta DEC-096 vincula decisões a KPack pinado e versão de ruleset; atualizar pack não executa efeitos retrospectivos sem diff/gates de migração.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

RuleSet DEC-096/C deve fixar hash/revision do KPack e fonte; mudança exige diff/migração explícita e não dispara efeitos retroativos.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Atualização de política DEC-097/C requer diff, revisão e migração explícita; não recalcular retroativamente acts confirmados.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Pins KPack/ruleset/build integram a chave do snapshot/diff; trocar pack exige validação e diffs versionados, não re-materialização cega.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Knowledge Pack fixado por campanha não concede permissão sobre modpack, quest flag ou runtime object.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Knowledge Packs pinados não absorvem flags do motor como canon nem recebem branches futuros em prompts.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Semantic quest milestones are curated technical metadata, separate from FR historical canon partitioned by year DR and private campaign overlays. UNKNOWN, AMBIGUOUS or stale milestones cannot trigger chronology, historical effect or materialization; lore packs do not authorize interpreting runtime flags. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Mapping de quest e views DEC-102 são pinados ao ramo/build; migração entre packs não é automática. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** marcos confirmados de quests originais são **origens candidatas** de regras históricas/regionais, não fatos canônicos escritos em `knowledge/periods/<ANO>-DR/`. A admissão exige prova reconciliada DEC-100/101/102, clock DR e branch adequados; a matriz DEC-096 filtra local, fase e precondições e DEC-097 compõe impactos. Escopo global não dá conhecimento universal. Evento proposto, evento host-confirmed e rumor entregue são distintos; nenhum efeito mecânico sem Action Gateway/receipt. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **Knowledge Pack pinado**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para Knowledge Packs pinados e nenhuma migração implícita de crenças, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para Knowledge Packs pinados e isolamento entre campanhas, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Fork de campanha isola contratos e recibos de obrigações. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Forks de campanha isolam registros e revisões contratuais. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
