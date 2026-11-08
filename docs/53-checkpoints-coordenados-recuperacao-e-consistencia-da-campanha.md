# DEC-053 — Checkpoints coordenados, recuperação e consistência entre motor e memória

**Escolha:** opção C, aprovada em 2026-11-06 (ADR-0048).  
**Versão:** Infinity AI Discovery v4.9.  
**Natureza:** contrato arquitetural e critérios candidatos para SPECS/POCs; não existe implementação demonstrada de salvamento, bridge, atomicidade entre processos, recuperação ou multiplayer.

## 1. Problema, invariantes e prioridades

O BG2:EE detém as consequências mecânicas enquanto o Infinity AI registra cronologia narrativa, memórias e simulações externas. Um checkpoint só é **recuperável** se os dois conjuntos representam uma fronteira causal compatível e estão ligados por evidências. Capturar dois arquivos no mesmo segundo **não prova** consistência.

**Invariantes:**

- `INV-01`: nenhum fato mecânico é inferido de resposta LLM ou de snapshot narrativo; confirmação vem de observação confiável do host quando tecnicamente disponível.
- `INV-02`: um checkpoint publicado tem par save + snapshot/log referenciável, íntegro, revisão/epoch coerentes, build e campanha compatíveis.
- `INV-03`: nenhum evento irreversível `HIGH` ou mutação incerta é reexecutado automaticamente para completar lacuna.
- `INV-04`: Original e Living World, campanhas distintas e ramos de recuperação não compartilham estado/segredos.
- `INV-05`: snapshot é projeção reconstruível sob regras versionadas; **log confirmado e comprovável não é apagado silenciosamente**.
- `INV-06`: nenhum cliente remoto nem modelo local escolhe unilateralmente qual das duas bases prevalece.
- `INV-07`: confirmação, recusa, proposta e `UNCERTAIN` são estados distintos; relógio e simulação não avançam mecanicamente por suposição.

## 2. Autoridade e fontes de confirmação

| Domínio | Autoridade | Prova exigida antes de confirmar |
|---|---|---|
| HP, inventário, itens, área, scripts, flags, combate | BG2:EE host | Save/estado observado segundo método comprovado; receipt por tipo de operação quando houver bridge testada |
| Histórico pessoal, relações, fatos narrativos | Serviço narrativo Infinity AI | Event log, proveniência, escopo, revisões e vínculo com causa (se houver efeito físico) |
| Simulação distante de facções/rumores | Regras determinísticas externas | Snapshot/log externo, tempo autorizado, origem de dados; efeitos físicos permanecem propostas |
| Identidade de build/mods | Manifesto DEC-051/052 | Fingerprint, ordem de mods, origens, cobertura, possíveis incompatibilidades |
| Promover recuperação, ações críticas, migração | Política e anfitrião | Autorização válida e trilha de auditoria; não substitui validações mecânicas |

A leitura completa de flags e estados de BG2:EE/EEex **não está comprovada**; onde faltarem observações necessárias, a operação correspondente ficará bloqueada até SPEC/POC.

## 3. Esquema lógico de dados candidato (não implementado)

```text
CheckpointManifest {
  checkpoint_id, campaign_id, game_mode, branch_id, epoch_id,
  build_id, content_catalog_revision, policy_revision,
  world_clock_ref, host_session_ref, host_save_ref, host_save_hash,
  save_completion_evidence_ref, host_observation_ref,
  narrative_snapshot_ref, narrative_snapshot_hash,
  event_log_watermark, event_log_integrity_ref,
  pending_action_ids[], uncertain_action_ids[],
  preparation_revision, verification_report_ref,
  status, created_at, published_at, provenance, access_scope
}
RecoveryAttempt {
  recovery_id, campaign_id, selected_checkpoint_id,
  requested_save_ref, observed_build_id, observed_branch_id,
  comparison_ref, blocking_discrepancies[],
  pending_receipt_reconciliations[], host_authorization_ref,
  recovery_status, audit_ref
}
```

O timestamp serve apenas para auditoria; **não é identificador suficiente de sincronização**. O manifest não exige que saves físicos sejam modificados para armazenar IDs — a associação externa pode ser usada, condicionada à comprovação de identidade. Hash sem sequência causal verificada também não prova equivalência.

## 4. Pipeline de checkpoint proposto

```text
REQUEST_CHECKPOINT
  -> PRECHECK (identidade de campanha/build, estado da sessão, permissões)
  -> QUIESCENCE_GATE (sem nova mutação externa; pendências reconciliadas)
  -> SAVE_CAPTURE (método BG2:EE demonstrado; confirmar término)
  -> NARRATIVE_CAPTURE (snapshot revisionado + watermark compatível)
  -> VERIFY_PAIR (integridade, IDs, clocks, revisions, ausência de inconsistência)
  -> PUBLISH_MANIFEST (somente par verificado, publicação lógica controlada)
  -> RETAIN_PREVIOUS_VERIFIED (até política de retenção DEC-018/054)
```

Se o jogo não permitir checkpoint seguro em combate/transição de área, a operação deverá adiar e manter o último par confiável. Se o método exigir save manual, o processo usará o procedimento manual validado, não uma suposta API. Uma interrupção antes da publicação **não torna elegível** qualquer candidato incompleto.

**Quiescência** é um objetivo de arquitetura: as SPECS deverão definir como impedir/observar mutações simultâneas sem congelar o jogo indevidamente. Não pressupor bloqueio de entrada em multiplayer se não houver hook demonstrado.

## 5. Falhas e reconciliação

| Cenário | Diagnóstico esperado | Política de recuperação |
|---|---|---|
| Save novo, banco narrativo antigo | Watermark/pós-condições divergentes | Não adivinhar eventos faltantes; usar par anterior ou revisão autorizada após evidências |
| Narrativa avançada, save antigo | Log inclui efeitos pós-save | Preservar log original; recuperar par anterior ou ramo compatível, sem replay cego |
| Timeout depois de emitir comando | `UNCERTAIN` | Verificar receipt/observação; congelar retries destrutivos |
| Arquivo de save corrompido | Hash ou validação falha | Quarentena do candidato, restaurar par anterior íntegro |
| Snapshot corrompido ou log truncado | Inconsistência de revisão/hash | Não usar candidato; analisar last verified, trilha e cópias |
| Host e cliente divergem | Estados ou build incompatíveis | Bloquear publicação/retomada e reconciliar host + clientes |
| Carregamento manual de save anterior | Save/epoch anterior ao log corrente | Criar/selecionar branch após revisão; não propagar informações do futuro |
| Migração de build A→B incompleta | Build mismatch ou dependência UNKNOWN | Rejeitar promoção; voltar ao par coerente A preservado |
| Save do modo Original usado no Living World | `game_mode` mismatch | Bloquear carregamento cruzado no orquestrador, sem modificar original |

Uma decisão de recuperar o par anterior implica possível perda de eventos após aquele ponto na **linha ativa**. O registro histórico não deve ser apagado: arquivar a divergência com ramo, contexto e consentimento conforme política futura. Não prometer que o BG2:EE suporta bifurcação/rollback nativos; ramificação é controle da camada externa e de cópias de save.

## 6. Máquina de estados lógica candidata

- `NEW` → pedido ainda não examinado.
- `PREPARING` → aguardando segurança/quiescência.
- `CAPTURED` → artefatos presentes, ainda não certificados.
- `VERIFYING` → integridade e coerência em análise.
- `VERIFIED` → par íntegro e coerente com evidências disponíveis.
- `PUBLISHED` → manifesto certificado e elegível, publicação concluída.
- `BLOCKED` → verificação falhou; candidato não recuperável.
- `UNCERTAIN` → sinais insuficientes, requer observação/revisão.
- `QUARANTINED` → artefatos suspeitos preservados para análise, nunca carregados automaticamente.

Esses nomes não são estados internos do motor, interfaces implementadas nem protocolo definitivo. `PUBLISHED` não deve ser inferido apenas pela presença de dois arquivos.

## 7. Relação com evento, tempo e identidade

1. **Idempotência:** `action_id`/`command_id` e receipts devem sobreviver ao save/load; o event log não reaplica uma morte, recompensa ou spawn só por receber resposta novamente.
2. **Causalidade:** fatos confirmados dependentes do motor referenciam observação ou checkpoint apropriado; narrativas puramente externas registram seu próprio escopo e tempo.
3. **Relógio:** estados FROZEN/PARTIAL/REALTIME da DEC-022 são respeitados; catch-up somente após par verificado e autorização temporal do host.
4. **Conhecimento:** NPC/PC só acessa fatos da ramificação, época e permissões legítimas (DEC-028); log interno pode conservar história arquivada, mas não virar lembrança de personagens no ramo restaurado.
5. **Multiplayer:** observar host + dois clientes em POCs após save/load e reconexão; mudanças de controle de PCs (DEC-045/046) não alteram titularidade, secrets ou checkpoint ownership.
6. **Conteúdo nativo:** um checkpoint verificado por hashes não certifica por si só quests/romances; regressões exigem DEC-050/051 e testes por build.
7. **Mortalidade e eventos HIGH:** nunca inferir ressurreição, morte definitiva, destruição de cidade ou alteração canônica durante recuperação; exigir confirmação específica.

## 8. Vinte e quatro testes candidatos (não executados)

| ID | Cenário | Resultado esperado |
|---|---|---|
| T-053-01 | Captura segura no mesmo campaign/mode/build | Manifest relaciona artefatos com IDs e revisões válidos |
| T-053-02 | Timestamps iguais, watermark diferente | Não declarar checkpoint coerente só pelos horários |
| T-053-03 | Save concluído, banco não capturado | Candidato incompleto não é `PUBLISHED` |
| T-053-04 | Snapshot capturado, save falha | Não publicar; último par válido preservado |
| T-053-05 | Interrupção antes de promover manifest | Recovery usa somente conjunto publicado anterior |
| T-053-06 | Save alterado após captura | Hash falha; bloquear |
| T-053-07 | Snapshot ou log adulterado/truncado | Integridade bloqueia uso |
| T-053-08 | Build/mod order difere do manifest | Recuperação bloqueada até compatibilidade comprovada |
| T-053-09 | Usar save de outra campanha | Detectar `campaign_id` ou vínculo inválido |
| T-053-10 | Carregar Original com narrativa Living World | Bloquear cruzamento de modos |
| T-053-11 | Replay de recompensa já confirmada | Nenhuma segunda concessão |
| T-053-12 | Comando com timeout e sem receipt | Manter `UNCERTAIN` e não retry destrutivo |
| T-053-13 | Comando com recibo atrasado | Reconciliar apenas uma vez por action_id |
| T-053-14 | Carregar save antigo com log novo | Detectar divergência e exigir escolha de ramo |
| T-053-15 | Restaurar branch antigo | Não revelar rumorações/segredos do futuro alternativo |
| T-053-16 | Restaurar com NPC e quest incompatíveis | Bloquear resolução fictícia ou flag por texto |
| T-053-17 | Alterar relógio/catch-up durante recovery | Não avançar eventos sem par/tempo reconciliados |
| T-053-18 | Falha no checkpoint durante combate | Adiar ou bloquear conforme capacidade demonstrada |
| T-053-19 | Reabrir depois de desconexão do cliente A | Host e cliente A sincronizados por teste |
| T-053-20 | Reabrir depois de desconexão do cliente B | Host e cliente B sincronizados por teste |
| T-053-21 | PC temporariamente atribuído a outro jogador | Titularidade e permissões inalteradas na retomada |
| T-053-22 | Restaurar backup pré-migração | Build A, save e narrativa A restaurados em conjunto |
| T-053-23 | Evento HIGH pendente durante crash | Nenhuma execução irreversível sem política/receipt |
| T-053-24 | Snapshot com histórico privado | Auditoria e relatórios não expõem segredos a não autorizados |

## 9. Gates técnicos e critérios de no-go

**Gates candidatos:** (G1) cópia do save verificada e carregável; (G2) snapshot/event log e watermark íntegros; (G3) associação entre revisões/ações observáveis; (G4) teste de ação com timeout e deduplicação; (G5) recuperação em cópia com host+2 clientes; (G6) teste de ramo antigo e filtragem de conhecimento; (G7) falha de build, modo e corrupção corretamente bloqueadas.

**No-go:** salvar parcialmente sem prova de término, publicação com ação mecânica incerta impeditiva, falta de artefato, corrupção, mismatch de campanha/build/modo, cliente divergente, segredo cruzando ramos, replay de mutação HIGH, restauração não ensaiada.

## 10. Pendências e próxima decisão

- **DEC-018:** política operacional de backups, cadência/retenção, logs, recuperação e observabilidade permanece aberta.
- **DEC-054 sugerida:** decidir modelo operacional de backups versionados, cópias redundantes e ensaios periódicos de restauração para implementar DEC-053.
- **DEC-013/015:** precisarão fixar versões/matriz e gates reproduzíveis antes de aceitação.
- **Integração com save BG2:EE/EEex e sincronização real:** não testada. Não prometer API de save, mutações reversíveis ou atomicidade cruzada.

## Integração posterior — DEC-055 (Discovery v5.1)

World Health Monitor deve expor falhas de captura, watermark divergente, `UNCERTAIN` impeditivo e idade do último par publicado, sem promover candidato incompleto. Retorno à saúde exige verificação do vínculo entre save do host, snapshot, event log e build/ramo; processo reiniciado não certifica checkpoint. Ver ADR-0050/doc. 55.

## DEC-057 — Checkpoint e localização da persistência (v5.3)

A distribuição opcional de workers de cálculo na LAN **não** transfere a autoridade do save nem implica banco narrativo remoto no MVP. Caso uma SPEC futura mova memória/event log para um nó LAN, exigirá testes próprios de único escritor lógico, consistência, falha de rede e restauração do par de checkpoint DEC-053. Nenhum commit atômico entre máquinas foi demonstrado. Ver ADR-0052/doc. 57.

## Integração DEC-063/C — vínculo do knowledge pack no checkpoint (v5.9)

Os contratos candidatos de checkpoint passam a considerar `knowledge_pack_id/revision/manifest_hash`, referências de revisões das **partições anuais**, `campaign_id/branch_id` e epoch na verificação. Um save antigo só será restaurado sob o pack e o ramo historicamente compatíveis; não reinterpretar automaticamente eventos passados à luz da revisão mais recente. Promoção seletiva de pack requer checkpoint seguro e ausência de operações `UNCERTAIN` não reconciliadas; falha aciona `FREEZE_AND_RECONCILE`. Nenhuma atomicidade real entre motor e banco foi comprovada.

## Integração DEC-064/C — aprendizado e crenças sem onisciência (v6.0)

Revisões de memória/crença DEC-064/C precisam de vínculo causal com event log, branch, NPC e Knowledge Pack DEC-063. Um checkpoint verificado deverá, em SPECS/POCs, permitir restaurar estado epistêmico coerente com world time; não aplicar crença posterior ao checkpoint nem repetir aquisição após crash. Nada disso comprova atomicidade entre saves BG2:EE e persistência externa.


### Checkpoint de memória hierárquica — DEC-065/C (Discovery v6.1)

Registrar revisão de episódios, sínteses derivadas, âncoras e dependências, conjuntamente com branch, pack e fronteira host confirmada. Uma síntese pode ser reconstruída de fontes coerentes, mas não incorporada a branch diferente ou a save restaurado fora de sua revisão. UNCERTAIN não vira memória confirmada durante recovery. Sem comprovação de transação atômica entre BG2:EE e serviço.

### Integração DEC-066/C — checkpoint de identidades e vínculos (v6.2)

Candidatos de snapshot/event log precisam vincular revisões de `NPCIdentity`, observações, provas, epochs e bindings ao mesmo checkpoint, branch, build e pack verificados. Restore/rollback invalida relações runtime posteriores e não injeta memória de outro ramo. `UNCERTAIN` não certifica identidade; não pressupor atomicidade BG2:EE–serviço externo.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

Salvar/restaurar deve preservar eventos de promoção DEC-067, identidades e transições agregado/individual na revisão causal; rollback não reativa promoção de branch futuro ou duplica registro.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

Checkpoint DEC-068/C deve cobrir estado NPC offscreen, último intervalo processado/confirmado, âncoras e fila de propostas com branch/epoch. Recovery pode manter pendências, mas nunca publicar evento sem reconciliação de host/ACL/identidade. Não criar efeitos históricos em replay.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: checkpoint deve guardar plano e revisões de rota, cursor temporal, estados de presença, evidências/receipts e pendências; restaurar o par save+narrativa sem duplicar viagens.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070: incluir propostas de incidente, risco, decisão, autorização, segment_id, event_id e receipt no checkpoint consistente. No restore/fork revalidar; não duplicar incidentes ou efeitos de engine.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Ledger de handoff DEC-071, reserva e `resolution_epoch` precisam ser consistentes com checkpoint de host/campanha; crash entre operação e receipt vai a `UNCERTAIN`. Restauro revalida idempotência e jamais resolve incidentes em ambos os trilhos.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Checkpoints DEC-053 precisam fixar versões de templates/composições e ledger DEC-071 por incidente; restore não recria encontro mecânico só porque havia template elegível.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Plano de fechamento pós-encontro DEC-073 requer checkpoint e reconciliação de recibos/overlays; não pressupor transação atômica entre engine e banco.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Commit do impacto DEC-074 depende de revisão, branch, epoch e ledger por causa/alvo; save/load, restore e UNCERTAIN pausam e reconciliam sem aplicação dupla. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Ledger de atribuição precisa carregar branch/epoch/checkpoint e respeitar restore; reputação/culpa futura não aparecem após rollback de save.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Checkpoint deve reconciliar versão do registro de personas, vínculos de identidade e revelações; após restore, jobs de divulgação de ramo/época incompatível são STALE. Não duplicar efeitos sociais.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação por evidências (Discovery v7.3; não implementada)

A investigação de personas DEC-076 usará ledger privado por campanha/ramo, com pistas e hipóteses revisáveis, origem/independência de fontes, contraprovas e estados inconclusivos. Suspeita ou fala LLM não confirma identidade e não permite divulgação; vínculo factual restrito exige evidências/DEC-066, e revelação exige ACL/consentimento/risk gate por audiência (DEC-019/028/041/045/046). Rumores e repercussões DEC-029/074/075 são separados de fato e punição. **Preservar `knowledge/periods/<ANO>-DR/` fisicamente por ano, sem evidências privadas no cânone.** ADR-0072/documento 77; 58 testes não executados, sem POC BG2:EE/EEex/multiplayer.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Caso/decisão/receipt DEC-078 fixa branch/epoch e checkpoint; rollback ou save mais antigo suspende sanção e exige reconciliação, sem reenvio cego.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Requisições/receipts interjurisdicionais DEC-079 entram no checkpoint lógico; restore, replay e falha UNCERTAIN não duplicam entrega, reconhecimento ou sanção host.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Cadeia de mandados DEC-080, revisões, comunicação e host receipts devem ser reconciliados no checkpoint; restore descarta futuras mensagens e bloqueia retry de ação UNKNOWN.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Ledger de reparação DEC-081 deve reconciliar dano/ordem, remédio/recibo, branch/checkpoint e idempotência; restauro não duplica itens/pagamentos.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Caso institucional e efeito de medida precisam de branch/checkpoint/epoch e prova do host para mecânica; restore não aplica condenação do futuro.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

ACL e disclosure receipts carregam branch/checkpoint/epoch; restauração invalida jobs futuros, sem retry de revelação UNCERTAIN.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Plano de proteção tem checkpoint/epoch, reservation fence e receipts; UNCERTAIN/restore pausa ação mecânica sem reexecutar fuga/escolta.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Snapshot deve reconciliar versões de plano, grants, exposições e provas por campanha/ramo; restore bloqueia conhecimento futuro e efeitos duplicados.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Checkpoint reconcilia operação de engano, claim disseminado, recursos reservados e crenças confirmadas; em restore, não reenviar rumor nem criar conhecimento futuro.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Checkpoint agrupa revisões de vínculos e host receipts; restauração previne reaplicação de ruptura ou rumor e mantém estados UNCERTAIN pendentes.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Checkpoints incluem versões de proposta, acordo, reserva, entrega, encerramento; epoch incompatível invalida proposta tardia, sem pagamento duplo.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Checkpoint vincula revisões de relatórios, families e pareceres ao save/epoch; restore de ponto anterior invalida análise produzida no futuro.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Checkpoint registra watermark de dossiês, revisões de ACL, views pendentes e recipients/receipts; restauração invalida transmissão stale, não força entrega futura.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Plano, aprovação, reserva, dispatch e receipts dependem de checkpoint coordenado; restore exige segregação de epochs e reconciliação.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Checkpoint coordenado preserva revisão do plano, consentimentos, in-flight IDs, receipts, reservas e watermarks; restore exige reconciliação e evita replay duplicado.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Checkpoint inclui snapshots consistentes de reservas, epochs, operações em voo e receipts; restore de branch ou sessão torna leases antigos STALE sem reexecutar comando incerto.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Restore confere grafo/epochs/leases, outbox e receipts em par com save host. Ações incertas ficam em quarentena, sem liberar recurso por deadline antigo.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

DEC-095 Saga deve vincular ledger de receipts e compensações ao checkpoint. DEC-096 dedup por branch/epoch/rule revision e estado confirmado, sem reaplicação de efeitos após load.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

DEC-096/C amarra dedup a epoch, KPack, ruleset, ramo e escopo; restore de save antigo não reaplica efeito confirmado nem vaza período futuro.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Recomposição DEC-097/C exige checkpoint/epoch, receipts e ledger; restauração não reaplica impactos mecânicos.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Snapshots de área exigem host/checkpoint epoch e ledger confirmado; restart/restore demanda reconciliação antes do próximo delta.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Checkpoint contém owner revision, host/checkpoint epoch, manifest e pendências; restore não reexecuta mutações incertas.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Checkpoint/restore alteram epochs e invalidam observações; sem reciclar dados antigos em novo ramo.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Catalogues by exact build/modpack/quest/script fingerprint, curated proof of semantic milestone and valid transition; an observed flag or stage is never an authorized quest write or host receipt. On patch or restore, invalidate semantic cache and avoid generic stage inference. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Após restore, epochs e lineage DEC-102 são verificados; não transportar automaticamente memórias da timeline abandonada. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **checkpoint**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para checkpoints e epochs delimitam receipts e versões epistêmicas, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para checkpoint e epochs de reparações e reputação, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Restauração exige reconciliação de recibos e epochs antes de reexecutar. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Restores isolam receipts por checkpoint e exigem reconciliação antes de novo despacho. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Ao restore, reconciliar escrow ledger, recibos, host/checkpoint epoch e inventário sem repetir depósito/liberação.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
