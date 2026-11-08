# ADR-0094 — DEC-099/C: ownership por instância, compatibilidade por build e proteção do conteúdo original

- **Data de aprovação:** 2026-11-07.
- **Escolha expressa:** **DEC-099 — opção C**, aprovada pelo idealizador.
- **Estado:** **APROVADA COMO ARQUITETURA**, Discovery **v9.5**; **nenhuma implementação ou integração BG2:EE/EEex/multiplayer comprovada**.
- **Integridade:** DEC-060–DEC-098 permanecem válidas e os **93 ADRs anteriores (ADR-0001…ADR-0093) permanecem byte a byte idênticos** à versão v9.4.
- **Documento normativo de engenharia:** `docs/99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md`.
- **Próxima discussão:** **DEC-100 — observação somente-leitura e allowlisted de estados de quests/scripts**, com isolamento de spoilers, por build e host.

## Contexto

A DEC-098/C materializa repercussões históricas somente por planos incrementais a partir de projeções, snapshots confirmados pelo host e observações com cobertura conhecida. A mesma área pode conter personagens e objetos criados pelo BG2:EE, scripts e quests originais, um mod de terceiro, conteúdo do Infinity AI e ações legítimas de jogadores. O mesmo `CRE`, nome ou `engine_instance_id` pode referir origens distintas, e scripts podem alterar um estado sem que o planejador tenha observado integralmente a transição. A simples divergência entre o estado desejado pelo Infinity AI e o jogo **não** é autorização para corrigir o jogo. A inexistência de observação plena tampouco prova ausência.

## Alternativas

- **A — Estado Infinity AI sempre prevalece:** **REJEITADA**. Risco de remover cenas, matar/ressuscitar NPCs, modificar inventários, quests, romance, diálogo e conteúdo de mods sem domínio ou consentimento.
- **B — LLM resolve ownership e prioridade:** **REJEITADA**. Linguagem narrativa não é autoridade sobre engine scripts, versão de mods, recursos, titularidade ou ação mecânica; introduz decisões não determinísticas e acesso indevido a spoilers.
- **C — Ownership granular com evidência, contratos por build, precedência explicitamente definida, quarantine e reconciliação host-first:** **APROVADA**. Atribuição de propriedade nunca nasce de inferência por nome/CRE, de um estado desejado ou de certeza textual de LLM.

## Decisão vinculante

1. **Quatro dimensões distintas de ownership:** registrar (i) **origem do conteúdo** (`ENGINE_NATIVE`, `QUEST_SCRIPT`, `THIRD_PARTY_MOD`, `INFINITY_AI`, `PLAYER`, `UNKNOWN`), (ii) **custódia/controle atual**, (iii) **autoridade para uma ação tipada específica** e (iv) **titularidade de cada campo/efeito**. O autor do template não é automaticamente dono da instância, do inventário, de um diálogo ou da variável de quest.
2. **Registro por identidade real da instância:** `OwnershipRecord` exige `campaign_id`, `branch_id`, `region_id`, `persistent_id`, `engine_instance_id`, `instance_generation`, `source_manifest_ref`, `owner_kind`, `owner_claim_evidence`, `verified_host_receipt_ref?`, `field_authorities[]`, `lifecycle_state`, `host_epoch`, `checkpoint_epoch`, `build_fingerprint`, `modpack_hash`, `rule_revision`, `last_observed_revision`. Um nome, CRE/template, id reciclado, `spawn proposal` ou memória de NPC nunca bastam para atribuir propriedade.
3. **Propriedade desconhecida ou contestada = preservar:** `UNKNOWN`, reivindicações contraditórias, mod não inventariado ou evidência fraca produzem `HOLD_RECONCILE`/`BLOCKED_OWNERSHIP`, com revisão humana quando preciso. Jamais adotar instância alheia automaticamente, nem apagar por ausência em scan parcial.
4. **Proteção do conteúdo original:** scripts, quest flags/globals, romances/banters, cenas, áreas, inventários de PCs, loot legitimamente transferido, estados de morte/ressurreição e entidades de outros mods são **não editáveis por padrão**. Fonte original, progresso da quest e decisões host-confirmed não são ruído no diff. Não existe uma precedência absoluta pela qual o Infinity AI sobrescreva recursos nativos.
5. **Autoridade por ação e campo, não por categoria genérica:** mesmo uma entidade `INFINITY_AI` admite alteração apenas em campo explicitamente allowlisted, com evidência de controle e capability testada. A titularidade do corpo/ator não autoriza mexer em quest, scripts, inventário ou relacionamentos que passaram a ser controlados por outro subsistema.
6. **Manifesto de compatibilidade por build:** `BuildCompatibilityManifest` é pinado por engine/game versão, EEex/bridge/plugins, SO prioritário Windows, mod list/ordem/hash, mapa/área, adapter revision, scripts observáveis, operações/campos admitidos e **evidências de POC efetiva**. Catalogação estática não equivale a runtime-capability; capacidade desconhecida, não testada, conflitante ou fora de revisão **bloqueia** mutation.
7. **Precedência formal, estreita e curada:** quando duas fontes afetam o **mesmo campo** de uma instância, avaliar `FieldAuthorityRule` versionada (owner, destino, tipo de ação, fase de quest, scope, proveniência, precondição). Regras incompatíveis ou empate não resolvido -> `HOLD_RECONCILE` ou `ESCALATE_CONFLICT`. Uma prioridade narrativa ou computacional DEC-056/093 não transfere ownership.
8. **Separação de preflight e aplicação:** `CompatibilityPreflight` avalia intenção com escopo, risco, consentimentos, contexto do host e revisões. Produz `PRESERVE_READ_ONLY`, `NO_OP`, `PROPOSE_OWNED_PATCH`, `PROPOSE_OWNED_CREATE`, `REVIEW_RETIRE`, `HOLD_RECONCILE`, `BLOCKED_OWNERSHIP`, `BLOCKED_CAPABILITY`, `BLOCKED_PROTECTED_FIELD` ou `ESCALATE_CONFLICT`. Qualquer `PROPOSE_*` é apenas planejamento, não execução.
9. **Host é fonte da mecânica, não das permissões:** constatar que a instância existe no host não prova quem pode editá-la. Action Gateway e host receipts autenticados são exigidos para efeitos; revalidar revisões, ownership, autorização, risk class, checkpointer/epochs e `modpack_hash` imediatamente antes do dispatch. `DISPATCHED`/`UNCERTAIN` não são reenviados automaticamente.
10. **Quests, scripts e multiplayer:** scripts originais/mods seguem sendo executados pelo motor quando possível; o Infinity AI os observa somente por interfaces testadas e políticas de acesso. Um cliente não pode declarar autorização, mudar quest flag, substituir a presença de um companion ou criar receipt. Ausência de leitura de quest estado -> bloquear operação dependente; não inventar etapa pela fala da LLM.
11. **Mudança de build/modpack:** invalidar contratos/referências incompatíveis; pin de hash/ordem e versão de area/adapter. Exigir inventário e migração DEC-051/052, reconciliação e testes por build; jamais supor que o mesmo `instance_id`, script name ou opcode permaneceu equivalente. Se um mod muda ownership de campo, resolver conflito antes de retomar writes.
12. **Eventos e mundo persistente:** snapshots DEC-098 e composições DEC-096/097 não alteram conteúdo nativo automaticamente. Entidades persistentes DEC-066, encontros DEC-071/073 e alterações de PC sobrevivem unload/reload, checkpoint, restore, branch e rebalanceamentos. Representação visual e persistência narrativa são coisas diferentes.
13. **Retirada, limpeza e compensação:** `REVIEW_RETIRE` não significa DELETE; exclusão é proibida sem owner confirmado, estado de encounter, transferências, custos, recibos, capability e autorização. Compensação DEC-095 cria evento novo, não desescreve fatos de quest ou host. Em evidência incompleta, manter o recurso e registrar pendência.
14. **Segurança e sigilo:** inventário de mods/quest estados/observações pode revelar spoilers, identidades ocultas e fontes protegidas. Aplicar ACL por campanha/branch/audiência e retenção mínima; logs, prompts, LAN e relatórios não fornecem acesso a flags privadas DEC-028/055/057–059/076/083–090. Canon em `knowledge/periods/<ANO>-DR/` segue fisicamente segregado e somente-leitura para este motor.
15. **Fail-closed e evidência:** conflito desconhecido, inventário incompleto, campo protegido, adapter sem teste, host desconectado ou ambiguidade de titularidade não admitem fallback LLM nem correção automática. Explicar códigos de bloqueio; permitir replanejamento narrativo **sem** alteração do estado protegido.
16. **Fronteira de comprovação:** POCs reais exigirão Windows/BG2:EE + EEex pinados, modpack conhecido, hooks de observação, 1 host + 2 clientes, testes de quest/banter/romance, save/load/restore, falha após dispatch e controles anti-spoiler. A implementação Python e schemas fornecidos são **sintéticos, puros e somente preflight**. Os testes de integração `T099-001..120` são **CANDIDATOS NÃO EXECUTADOS**.

## Relações e invariantes de governança

- **DEC-003/050/051/052:** integração progressiva, conciliação de scripts e inventário/migração por build.
- **DEC-011/012/027/041/042/045/046:** autoridade do host, Action Gateway, risco, consentimento, PCs e delegação.
- **DEC-053/054/056/058/059:** checkpoints, restauração, orçamentos, segurança de sessões e roteamento.
- **DEC-060–065/076/083–090:** canon fisicamente segregado, conhecimento falível, ACL, proteção de segredos e evidências.
- **DEC-066–074:** identidade persistente, viagem, cenas, encontros e ownership após resolução.
- **DEC-091–095:** autorizações, pausa/replanejamento, reserva/impasse e compensações Saga.
- **DEC-096–098:** elegibilidade histórica, composição tipada, snapshots host-confirmed e diff incremental; não conferem ownership.

## Critérios de aceite para futuras POCs (não cumpridos nesta fase)

- O mesmo mapa e roteiro original têm resultado observacional idêntico sem overlay e com overlay bloqueado; sem regressão de quests/romances, no test save.
- Criação e patch em instância Infinity AI requerem receipt genuíno/authority por campo, capability real e sessão/epoch válidos; duplicidade e nomes iguais não criam ownership.
- Mod de terceiro, native script, inventário de PC e `UNKNOWN` não sofrem patch/despawn em reentrada, restore e update de build; conflitos têm codes e ledger.
- Um mesmo preflight é determinístico por entrada/revision; ordem de regras não transforma conflito em autorização; testes host + 2 clientes aprovados por fingerprint exato.
- Um delta bloqueado não corrompe operação independente; nenhuma informação privada ou spoiler é transmitida sem ACL.

## Consequências e acompanhamento

A solução exige curadoria de instâncias, manifestos, teste de capacidades, política de compatibilidade granular e custo de manutenção por build/modpack. Em troca preserva campanhas e dados originais, permitindo overlays dinâmicos somente dentro de domínio comprovado. A DEC-100 detalhará o que pode ser **observado somente-leitura** de quests e scripts sem converter observação em autoridade de escrita.

**Não há execução em jogo, compatibilidade demonstrada, hooks EEex provados, modpacks validados ou POC multiplayer.**
