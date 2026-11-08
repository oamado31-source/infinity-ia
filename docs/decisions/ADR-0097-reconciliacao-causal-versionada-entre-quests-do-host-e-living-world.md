# ADR-0097 — DEC-102/C: reconciliação causal, versionada e não destrutiva entre quests do host e Living World

- **Data:** 2026-11-07.
- **Decisão:** **DEC-102/C**, aprovada expressamente pelo idealizador.
- **Situação:** **APROVADA COMO ARQUITETURA** — sem implementação ou POCs de BG2:EE/EEex/bridge/multiplayer.
- **Discovery:** v9.8. **ADR-0001..ADR-0096 anteriores preservados integralmente, byte a byte; decisões DEC-060..DEC-101 não foram revogadas.**
- **Especificação normativa:** `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md`.
- **Próximo tema em aberto:** DEC-103 — admissão e propagação causal de marcos de quest reconciliados para outros sistemas do Living World.

## Contexto

A DEC-099 impede que o Infinity AI sobrescreva instâncias/fields de quests, scripts ou mods sem ownership e capabilities comprovadas. A DEC-100 fornece envelopes de observação read-only por build/ACL, sem spoilers; a DEC-101 transforma conjuntos observados em marcos semânticos somente quando existe catálogo curado, prova de cobertura e transição. Ainda assim, o **marco semântico que o host pode sustentar** e a **projeção do último estado persistido no Living World** podem diferir, por exemplo após progresso legítimo em script original, save/load, checkpoint restaurado, patch/modpack alterado, observação incompleta, cache desatualizado, mudança de ramo ou receipt pendente.

Não existe um sistema transacional global comprovado que possa desfazer ou impor alterações a BG2:EE/EEex. Um conflito detectado não concede direitos de escrita no motor nem permite reescrever diálogos, lembranças, fatos confirmados, identidades ou consequências que os personagens já presenciaram. Além disso, alguns estados do jogo revelam segredos internos: reconciliação deve ocorrer no domínio técnico protegido, não em prompts ou rumores.

## Alternativas discutidas

- **A — impor automaticamente ao host o estado persistido no Living World:** **REJEITADA**; viola autoridade mecânica DEC-011, ownership DEC-099, quests e saves; pode destruir progressão, itens, romances e flags.
- **B — deixar a LLM escolher o estado verdadeiro e reparar a história:** **REJEITADA**; pode fabricar progressões, suprimir fatos, vazar spoilers ou reescrever histórico sem prova.
- **C — comparar provas, epochs, snapshots e receipts, e propor apenas revisão auditável de projeções derivadas:** **APROVADA**.

## Decisão normativa

1. **Domínios de autoridade não intercambiáveis.** `HostQuestSemanticObservation` (estado técnico do host observado) ≠ `CuratedSemanticAssertion` (interpretação DEC-101) ≠ `LivingWorldQuestProjection` (visão derivada, não mecânica) ≠ `NarrativeFactLedger` (acontecimentos confirmados) ≠ `RecipientKnowledge` (conhecimento legitimamente adquirido). Nenhum deles pode substituir silenciosamente os demais.
2. **Entradas estritamente comprovadas.** `QuestReconciliationCase` contém IDs opacos de campanha/branch/sessão/quest, `build_fingerprint`, `modpack_hash`, `script_digest`, `observer_revision`, `mapping_revision`, `host_epoch`, `checkpoint_epoch`, `observation_id`, cobertura, freshness, `semantic_id`, ID de prova DEC-100/101, overlay revision, parent lineage, receipts, autoria técnica e política. **A solicitação não pode fornecer suas próprias concessões** de ACL nem atestar o host. Validações e acessos vêm de registros distintos.
3. **Verificação de identidade/tempo.** Exigir identidade de quest/variante, instância/sessão, build/modpack/mapper e ramo iguais entre evidências ou uma migração certificada específica. Nenhum fallback por nomes de flags, strings de scripts ou “similaridade” de LLM. `host_epoch` e `checkpoint_epoch` determinam a linha temporal válida; snapshots/restores divergentes exigem inspeção e possível fork/rescope, não merge cego.
4. **Semântica anterior à reconciliação.** Apenas resultado DEC-101 `MAPPED_MINIMAL`, com prova suficiente, explícita e fresh, serve de candidato. `UNKNOWN`, `AMBIGUOUS`, `CONTRADICTORY`, `UNAVAILABLE`, ausência sob cobertura parcial e mapping revogado **não** provam progresso/regressão; resultam em `UNKNOWN` ou quarentena, sem mutation.
5. **Política determinística de divergência.** Resultados: `CONSISTENT` (mesmo marco), `PROPOSE_DERIVED_VIEW_REBASE` (transição curada avançou no host na mesma epoch, com prova), `RESTORE_REVIEW_REQUIRED` (epoch/lineage divergem), `UNKNOWN` (prova insuficiente), `QUARANTINED` (conflito não explicado, receipt incerto, identity/ACL incompatíveis), `BLOCKED_MAPPING` e `BLOCKED_ACL`. **O host não é sobrescrito** para “corrigir” o overlay, e o overlay não é sobrescrito automaticamente pela observação.
6. **Correção somente de visões derivadas.** `DerivedViewRebaseProposal` aponta para nova revisão de projeção com `expected_overlay_revision` (CAS), `reason_code`, `host_semantic_proof_ref`, `source_mapping_revision`, epoch e escopo. Aplicar exige processo privilegiado, autorização separada, políticas de anúncio e ledger append-only. Um `rebase` não falsifica fatos nem remove eventos do histórico original; registram-se `SUPERSEDED/CORRECTED` em nova revisão, nunca edição destrutiva.
7. **Host receipts e decisões pendentes.** Operações DEC-012/092–095/098/099 `DISPATCHED`, `DISPATCH_PENDING`, `UNCERTAIN`, `ACK_UNKNOWN` permanecem em quarentena para consulta/reconciliação com o host. Nem retry, nem compensação, nem rollback, nem liberação de recurso decorrem automaticamente da divergência. Observação read-only **não** é receipt de uma ação.
8. **Histórico após restore.** Restaurar um save pode fazer a quest regressar legitimamente **em outra linha temporal**, sem demonstrar que o acontecimento anterior “nunca existiu”. O overlay antigo fica imutável e retido em seu ramo/epoch; qualquer associação a novo save requer política de branch, consentimentos, migração/snapshot certificado e auditoria. Nunca se “esquece” informação já transmitida aos NPCs de um ramo anterior por uma atualização silenciosa de banco.
9. **Prioridade e conflitos de scripts.** Quests originais e mods permanecem sob autoridade de seus scripts/ownership DEC-099. Um conflito não motiva escrita em globals, CRE, inventários, scripts, diálogos nem atributos do PC. Somente capacidades testadas e autorizadas poderiam permitir outra operação futura, fora desta reconciliação observacional.
10. **Idempotência e multiusuário.** Chaves incluem `operation_id`, campanha/branch/sessão, quest, build/modpack/mapping, epochs, revision e prova de host. Locks/CAS/fencing impedem que dois clientes aceitem revisões concorrentes. Duplicata retorna mesma decisão ou pendência consistente, não cria novo fato. Cliente não host não resolve disputa unilateralmente.
11. **Privacidade, knowledge e spoilers.** Flags e evidências brutas são protegidas conforme DEC-028/059/083/100. O relatório público indica somente o código de status e o mínimo liberado por ACL; `semantic_id` oculto quando necessário. Nenhum `rebase` envia conhecimento à party, NPC, facção, dossiê ou LLM sem evento independente de divulgação DEC-029/077/089/090.
12. **Cânone não é overlay.** O sistema jamais escreve `knowledge/periods/<ANO>-DR/`; Knowledge Pack pinado DEC-060–063 e divergências de cânone DEC-009/022/025/026 permanecem intactos. Correção de projeção de quest não gera automaticamente impactos históricos DEC-096–098 nem reabre quests encerradas.
13. **Ausência de implementação.** O `QuestReconciler` Python e Schema JSON de `examples/chronology/` são *somente fixtures e testes unitários sintéticos*. Nenhuma API/hook real BG2:EE/EEex, leitura de save, console Lua, mod ou sincronização multiplayer foi demonstrada. **132 cenários T102-001..T102-132 são candidatos NÃO EXECUTADOS.**

## Fluxo decisório aprovado

1. Admitir solicitação identificada, autorizada e escopada; obter política assinada/atestada em fonte separada.
2. Vincular a observação somente-leitura DEC-100 à afirmação semântica DEC-101, mapa e fingerprint exatos.
3. Correlacionar a revisão derivada do overlay, epoch/checkpoint/branch e recibos reais do host.
4. Suspender em `UNKNOWN`/`QUARANTINED` se houver prova incompleta, interpretação ambígua, receipt pendente, discrepância de build ou transição não curada.
5. Se comprovadamente equivalentes, emitir somente `CONSISTENT`.
6. Se houver avanço curado e verificável, **propor** uma revisão `PROPOSE_DERIVED_VIEW_REBASE`, sujeita a CAS/fencing/aprovação; **sem escrever** no jogo, no ledger de fatos ou no conhecimento dos NPCs.
7. Após revisão autorizada, registrar decisão e proveniência append-only; efeitos derivados de outros módulos requerem procedimento futuro separado (DEC-103).

## Consequências e riscos

- **Benefícios:** reconciliação reproduzível de saves e scripts; proteção de quests e dos fatos históricos; ausência de spoilers em contexto narrativo; classificação clara da incerteza.
- **Custos:** versionar catálogos, snapshots, epochs, artefatos de host, autorização de CAS e testes por build/modpack; operação manual/host em casos incertos.
- **Riscos residuais:** observações atrasadas, falhas de bridge, forks simultâneos, migrações incompatíveis e combinações de mods. Todos exigem abordagem fail-closed até POCs e evidência.

## Dependências e próximos passos

Vinculação normativa: DEC-008/009/011/012/019/022/027/028/041/050/053/054/055/057/058/059/060–063/064/066/074/075/077/089/090/091–101. Implementação requer baseline Windows BG2:EE limpo → EEex → bridge → host+dois clientes, leituras certificadas sem efeitos colaterais, restore/branch e receipts de ações reais. **DEC-103 permanece EM ABERTO** para admitir marcos reconciliados como fontes de eventos/rumores/efeitos sem vazar spoilers e sem duplicidade.
