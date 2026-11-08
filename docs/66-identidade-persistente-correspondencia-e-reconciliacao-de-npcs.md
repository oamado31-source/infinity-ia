# Documento 66 — Identidade persistente, correspondência e reconciliação de NPCs

> **Discovery v6.2 — DEC-066/C aprovada (ADR-0061).** Contratos e testes **CANDIDATOS**, sem implementação, telemetria, benchmarks, provas de API EEex ou validação em BG2:EE multiplayer.

## 1. Objetivo e cenário de ameaça

Reconhecer um mesmo NPC ao longo de saves, carregamentos, áreas, ausências, spawns e revisões da instalação **sem** atribuir lembranças de um personagem a outro. O sistema não poderá tratar como equivalentes: personagem histórico canônico, ator narrativo persistente, objeto/instância runtime, arquivo/asset de conteúdo e nome visível. As observações do motor podem ser incompletas; nenhuma API específica de EEex/BG2:EE é pressuposta.

**Invariantes:**

1. Cânone separado fisicamente por ano (`knowledge/periods/<ano>-DR/`, DEC-060); fonte/proveniência DEC-061, publicação curada DEC-062 e Knowledge Pack por campanha DEC-063.
2. As memórias subjetivas DEC-064/065 são por `campaign_id`, `branch_id` e `npc_identity_id`, em armazenamento da campanha, nunca no cânone anual.
3. Nome, imagem, raça, posição, NPC script/CRE name e engine object id, isoladamente, são **indícios**, não prova de identidade durável.
4. A correspondência `VERIFIED` é necessária, mas **não suficiente**, para entregar memória: ACL, tempo, fonte e direito de conhecimento aplicam-se depois.
5. O host permanece autoridade de eventos mecânicos confirmados; um trabalhador LLM/LAN pode sugerir, não confirmar identidades por conta própria.
6. `UNCERTAIN`, `STALE`, conflito de candidatos e falha de resolução resultam em `DEFER`/interação limitada, não junção por palpite.
7. Nenhuma afirmação de estabilidade de ID, hook, spawn ou script nativo até SPECS, matrizes de build e POCs.

## 2. Entidades distintas

| Elemento | Escopo | Significado e limite |
|---|---|---|
| `CanonicalCharacterRef` | Referência curada, fonte/ano/versão | Personagem na fonte canônica; não armazena memória de campanha e não prova qual instância está no jogo |
| `NPCIdentity` | Campanha + branch/linhagem + revisão | Indivíduo lógico persistente, com evidências e estado de vínculo |
| `EngineObservation` | Sessão + instante + build + estado observado | O que a bridge conseguiu observar de uma instância runtime; pode desaparecer, reaparecer ou ser reciclado |
| `CandidateMatch` | Solicitação/revisão | Associação possível, com evidências positivas/negativas, status e razões; não autoriza recuperação privada |
| `VerifiedBinding` | Campanha + branch + epoch | Vínculo confirmado com prova causal, escopo e revisões, sujeito a revogação/invalidação |
| `IdentityAuditEvent` | Event log da campanha | Criação, confirmação, rejeição, split/merge controlado ou revogação, sem expor segredos nos logs |

### Exemplo de contratos candidatos (não interfaces implementadas)

```text
NPCIdentity {
  npc_identity_id, campaign_id, branch_id, created_at_event_id,
  canonical_character_ref?, narrative_entity_type,
  identity_revision, lineage_origin?, status,
  evidence_refs[], protection_labels[], created_at_world_clock,
  permissions_policy_revision
}

EngineObservation {
  observation_id, campaign_id, branch_id, session_id,
  host_checkpoint_ref, build_fingerprint, mode,
  observed_at_world_clock, area_ref?, party_context?,
  actor_hints[], available_engine_hints[],
  observation_epoch, engine_receipt_refs[], coverage_status
}

CandidateMatch {
  observation_id, candidate_npc_identity_id?,
  supporting_evidence_refs[], conflicting_evidence_refs[],
  confidence_class: INSUFFICIENT | SUPPORTED | CONFLICTED,
  requires_host_review, policy_revision,
  state: CANDIDATE | VERIFIED | AMBIGUOUS | STALE | REJECTED
}

VerifiedBinding {
  npc_identity_id, observation_id, campaign_id, branch_id,
  build_fingerprint, checkpoint_revision, observation_epoch,
  policy_revision, verified_by, verified_evidence_refs[],
  expires_on_transition_or_revision, state: ACTIVE | STALE | REVOKED
}

IdentityResolutionRequest {
  campaign_id, branch_id, knowledge_pack_id,
  world_clock_dr, scene_id, observation_ids[],
  host_state_revision, build_fingerprint, purpose, caller_acl
}

IdentityResolutionResult {
  status: VERIFIED | AMBIGUOUS | UNKNOWN | STALE | DENIED | DEFER,
  npc_identity_id?, binding_ref?, reasons[],
  allowed_use: PERSONAL_MEMORY | GENERAL_DIALOGUE_ONLY | NONE,
  evidence_revision, access_policy_revision
}
```

A representação final de IDs e tipos de objeto depende do motor observado, sistema de persistência e segurança efetivamente medidos.

## 3. Criação e resolução de identidade

1. **Observar sem escrever:** obter somente dados disponíveis e legalmente autorizados no host, com contexto de sessão, build, branch e instante; não presumir que nome/script ID é estável.
2. **Distinguir instância/indivíduo:** verificar se há evidência de ator único, clone scriptado, spawn genérico, party member ou NPC canônico; ausência de dados = `UNKNOWN`.
3. **Consultar universo permitido:** candidatos exclusivamente da mesma campanha/branch, respeitando parentesco de forks e revisões; não realizar busca de segredos por nome em campanhas diferentes.
4. **Avaliar evidências:** continuidade confirmada de partida/área, save/checkpoint, eventos de presença, inventário por build DEC-051, flags de quest comprovadas DEC-050, ou vínculo de identidade previamente certificado. Indícios fracos podem ordenar inspeção, não provar.
5. **Aplicar exclusão mútua:** simultaneidade de duas instâncias não autoriza automaticamente que ambas sejam o mesmo indivíduo; permitir relações de transformação/clone somente sob regras e comprovação específicas.
6. **Resolver ou bloquear:** `VERIFIED` somente com evidências suficientes e nenhuma contradição impeditiva. Se duplo candidato, ID reciclado, lacuna de snapshot ou build nova: `AMBIGUOUS`/`STALE`.
7. **Persistir vínculo idempotente:** associar chave de operação, host revision, build, checkpoint, identity revision, branch e proof refs; operações repetidas não duplicam identidades.
8. **Recuperar memória com ACL:** somente após `VERIFIED`, filtrar episódios, âncoras e conhecimento DEC-028/064/065; respeitar pack do ano e a revisão. `VERIFIED` não concede segredos automaticamente.
9. **Revalidar na publicação:** se o NPC despawnar, a sessão mudar, o nó LAN revogar ou o host revisar estado antes da resposta, cancelar/atualizar a solicitação. Resultados tardios não usam binding antigo.

## 4. Estratégia para transições e cenários limítrofes

| Cenário | Risco | Conduta aprovada |
|---|---|---|
| Save e load da mesma campanha | Runtime IDs ou instâncias recriados | Reconciliar revisão/checkpoint e evidências antes de recuperar memória |
| NPC viaja entre áreas | Mudança de handle/actor | Confirmar continuidade por trilha autorizada de transição, não só mesmo nome |
| Dois comerciantes homônimos | Fusão de histórias distintas | Dois `NPCIdentity`, nenhum merge automático |
| Spawn genérico reutiliza referência técnica | Confundir indivíduos | Tratar referência reciclável como observação, não identidade |
| Duas instâncias aparentam o mesmo NPC simultaneamente | Clones/mods/scripting | `AMBIGUOUS`, inspeção das causas e autorização conforme risco |
| NPC sai da party e reaparece depois | Perda de memória ou falso retorno | Recuperar histórico somente após confirmação de identidade e eventos DEC-049/050 |
| NPC morre e pode ressuscitar | Confundir status ou criar novo NPC | Diferenciar identidade durável de estado mecânico de vida; host confirma consequências |
| Novo mod muda CRE/script/ordem | Fingerprint divergente | `STALE`, análise por build DEC-051/052, revalidação antes de associação |
| Replay/rollback de checkpoint | Associação a timeline posterior | Invalidar bindings posteriores ao checkpoint e evitar branch bleed |
| Fork A/B a partir da mesma raiz | Compartilhamento de memória pós-fork | Compartilhar só história ancestral confirmada; novos episódios isolados por ramo |
| Identidade não encontrada com certeza | Conversa fica bloqueada por restrição | Oferecer somente diálogo genérico autorizado sem memória privada ou `DEFER` |
| NPC menciona segredo do PC | Exfiltração por associação | Filtrar antes da busca e antes do prompt; negar mesmo com identidade verificada |

## 5. Provas, conflitos e governança

- **Fontes de evidência possíveis, não confirmadas:** receipt host de presença, área/partida, dados nativos acessíveis da build, vínculos com quests/party, observações coerentes, eventos persistidos e identidade curada. Cada evidência possui tempo, escopo e origem.
- **Conflitos de candidatos:** usar determinismo para detectar duplicidade/contradição, classificar risco e impedir vinculação. LLM pode propor explicação, mas não é árbitro ou fonte de observação mecânica.
- **Resolução supervisionada:** ações que poderiam fundir/splitar NPCs ou recuperar segredo incorreto requerem política de risco, revisão de host e trilha auditável. Nenhum merge silencioso por similaridade textual.
- **Correções:** revogar vínculo equivocado e invalidar projeções futuras; fatos já publicados e operações mecânicas do host não podem ser reescritos sem reconciliação e autorização especiais.
- **Correlação com cânone:** um NPC do jogo pode ter referência editorial curada em `knowledge/periods/<ano>-DR/...` mas não copiar para lá dados do encontro ou memórias particulares. Um novo Knowledge Pack não vincula instâncias automaticamente.

## 6. Consistência, segurança, desempenho e restore

- **Checkpoint:** incluir revisão de identidade, vínculo, linhagem, evidências e época, além de campanha/branch, fingerprint de build, Knowledge Pack e watermark do host. Nenhum mecanismo de transação atômica com o motor está comprovado.
- **Idempotência:** chave conceitual `campaign/branch/observation_epoch/build/checkpoint/operation`; no replay, reaplicar leitura e conferência, não repetir confirmação com efeitos duplicados.
- **Cache:** cache de identidade inclui ACL, branch, policy, build, checkpoint, world time e observation epoch. Invalidação após reload, mudança de área relevante, migração, revogação ou restauração.
- **LAN:** worker pareado e autorizado pode sugerir candidatos com dados minimizados; recebe apenas pistas necessárias, nunca cópia integral de segredos/índices. Retorno stale falha fechado.
- **QoS:** reconhecimento não exige LLM por NPC/tick. Priorizar atores da cena, companions, encontros importantes e relações existentes; processar possíveis candidatos em filas não urgentes. DEC-067 decidirá a seleção de NPCs genéricos.
- **Observabilidade:** auditoria registra transições/status/refs minimizados, não prompts, textos de segredo ou dumps integrais de memória por padrão.
- **Original Mode:** não importar memórias do Living World, identidades ou aliases em saves do modo Original. Isolamento por modo/campanha obrigatório.

## 7. Matriz de degradação segura

| Entrada/condição | Saída | Restrição |
|---|---|---|
| Provas positivas suficientes, revisões compatíveis | `VERIFIED` | Ainda aplicar ACL e validar conhecimento temporal |
| Nome coincide, sem prova causal | `UNKNOWN`/`CANDIDATE` | Sem memórias pessoais; diálogo genérico possível |
| Dois candidatos plausíveis | `AMBIGUOUS` | Proibido escolher por palpite ou similaridade LLM |
| Host retorna receipt `UNCERTAIN` | `DEFER` | Não criar vínculo nem fato de reencontro confirmado |
| Build/fork/checkpoint mudou | `STALE` | Invalidar cache, revalidar por provas compatíveis |
| Worker LAN desconectado | `DEFER` ou rota local segura | Não reutilizar binding não verificado |
| Tentativa cross-campaign | `DENIED` | Nenhuma memória ou identidade privada retorna |
| ACL não permite memória | `DENIED` (conteúdo privado) | Identidade confirmada não contorna permissões |
| Identidade verificada, pack temporal indisponível | `DEFER` conteúdo factual | Não pesquisar diretórios futuros ou índice global |
| NPC é duplicata/respawn genérico | `AMBIGUOUS` até prova | Sem fundir identidades automaticamente |

## 8. POCs e critérios de evidência

1. Documentar quais campos realmente podem ser observados em BG2:EE vanilla e EEex na build fixada, respeitando o modo Original e sem escrita invasiva.
2. Testar host+dois clientes com salvar, carregar, sair/voltar de área, party join/leave e instâncias simultâneas; conferir se cada campo é estável e qual escopo possui. Não afirmar sucesso sem resultados reproduzíveis.
3. Para cada alteração de mod/versão, comparar identidade, scripts, recursos e flags de quest; catalogar as limitações reais.
4. Medir latência e memória dos índices de identidade sob cenários ACTIVE/NEAR/DISTANT/DORMANT e falha de worker LAN.
5. Estabelecer política humana e telas para revisão de `AMBIGUOUS`, sem permitir ações mecânicas não autorizadas. Exigir teste de restore com checkpoints verificáveis.
6. Definir thresholds só após dados: margem de evidências, controle de falso positivo (mais crítico que falso negativo), retenção, limites de custo e regras de cancelamento.

## 9. Testes candidatos — NÃO EXECUTADOS

1. **T066-01:** Novo NPC lógico recebe identidade opaca escopada por campanha e ramo.
2. **T066-02:** Duas observações com mesmo nome não são fundidas automaticamente.
3. **T066-03:** Mesmo portrait/assets não constitui prova suficiente.
4. **T066-04:** Engine object ID reciclado não transfere memória a spawn novo.
5. **T066-05:** Persistência entre save/load só ocorre com prova compatível.
6. **T066-06:** Reaparecimento em outra área exige continuidade causal documentada.
7. **T066-07:** Ambiguidade bloqueia memórias privadas e relações exclusivas.
8. **T066-08:** Ausência de identidade permite fala genérica sem alucinar reencontro.
9. **T066-09:** NPCs homônimos mantêm episódios e crenças independentes.
10. **T066-10:** Dois spawns simultâneos geram conflito/isolamento adequado.
11. **T066-11:** Morte e ressurreição não criam identidade nova sem necessidade.
12. **T066-12:** Clone/mod scriptado é distinguido de indivíduo original.
13. **T066-13:** Despedida de companion mantém identidade lógica persistente.
14. **T066-14:** Recrutamento posterior restaura memória só se vínculo `VERIFIED`.
15. **T066-15:** Inventário de build ausente produz `UNKNOWN`, não certeza.
16. **T066-16:** Migração de build invalida binding com fingerprint antigo.
17. **T066-17:** Rollback de save invalida observações posteriores ao checkpoint.
18. **T066-18:** Fork A não recebe novos episódios particulares do ramo B.
19. **T066-19:** História ancestral pré-fork pode ser referenciada sob ACL vigente.
20. **T066-20:** Conhecimento de 1370 DR não é atribuído a NPC em 1369 DR.
21. **T066-21:** Cânone permanece em pastas físicas anuais DEC-060, sem escrita de identidade privada.
22. **T066-22:** Fonte canônica curada não equivale a identidade runtime automaticamente.
23. **T066-23:** Knowledge Pack novo não reatribui identidades ou memórias.
24. **T066-24:** Proposta de LLM de vincular NPC é recusada sem evidência positiva.
25. **T066-25:** Worker LAN revogado não confirma binding pendente.
26. **T066-26:** Retry idempotente não duplica NPCIdentity ou associação.
27. **T066-27:** Receipt host `UNCERTAIN` não confirma identidade.
28. **T066-28:** Mudança de ACL após match impede busca/exposição de segredo.
29. **T066-29:** Revogar binding invalida cache e sínteses dependentes.
30. **T066-30:** Merge/split de identidades exige autorização por risco e auditoria.
31. **T066-31:** Restaurar checkpoint preserva revisões de identidade e projeção.
32. **T066-32:** Original Mode não acessa identidade privada de Living World.
33. **T066-33:** Fila saturada preserva operações críticas, adia reconciliação não urgente.
34. **T066-34:** Relatório de POCs destaca APIs e comportamentos não comprovados, sem rotular testes como executados.

**Nenhum desses testes foi executado.** SPECS deverá definir critérios mensuráveis, fixtures de engine, seleção de builds, revisão de questões de segurança e evidências reproduzíveis.

## 10. Próxima discussão — DEC-067

**Como decidir quais NPCs merecem identidade individual durável, memória completa e simulação ao longo do mundo?**

- **A:** individualizar automaticamente todo NPC observado, inclusive spawns genéricos.
- **B:** persistir apenas NPCs únicos e previamente curados.
- **C (recomendação preliminar):** individualização híbrida e progressiva — NPCs únicos/companions priorizados, NPCs genéricos inicialmente agregados/efêmeros e promoção quando experiências relevantes e provas de identidade justificarem, com orçamento e segurança. A promoção não permite vínculo especulativo: permanece sujeita à DEC-066.

Não confundir política de individualização com a existência de objetos de runtime ou acesso automático a memórias.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

DEC-067/C individualiza gradualmente NPCs efêmeros/agrupados apenas após evento relevante e prova positiva de identidade DEC-066; status `CANDIDATE/AMBIGUOUS/STALE` não autoriza associação de memória privada.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

NPC persistente ausente continua com identidade lógica, mas não pressupõe uma instância do motor. DEC-068 exige `VERIFIED` com evidência compatível antes de carregar memórias após reencontro; spawn/homônimo/CRE reciclado ficam AMBIGUOUS ou STALE.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: plano de viagem exige identidade lógica verificada; `EngineObservation` e presença física permanecem distintas de posição narrativa inferida.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070 vincula incidentes ao NPCIdentity VERIFIED e itinerário; homônimos/instâncias AMBIGUOUS não recebem memórias, perdas, ataques ou consequências por suposição.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Handoff DEC-071 requer identidade DEC-066 `VERIFIED` para atores vinculados a memórias; observação de área/instância é evidência adicional, não prova por nome/CRE. `AMBIGUOUS` impede spawn ou vínculo.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Ator de template DEC-072 deve corresponder a NPC persistente com identidade DEC-066 `VERIFIED`; recurso CRE/asset igual ou nome idêntico não autoriza associação nem spawn de duplicata.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Owner da instância não equivale a NPCIdentity; identidades ambíguas impedem cleanup que possa atingir NPC diferente.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Testemunhas e destinatários DEC-074 exigem identidade lógica confirmada para conceder memórias e efeitos individualizados; homônimos e instâncias ambíguas bloqueiam atribuição. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Testemunha/autor NPC exige identidade verificada quando a ação depende disso; homônimos não compartilham crédito, culpa ou histórico por semelhança.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

A identidade lógica provada DEC-066 é distinta do nome/persona percebido DEC-076; correspondência mecânica interna não implica divulgação ao NPC ou ao jogador.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação por evidências (Discovery v7.3; não implementada)

A investigação de personas DEC-076 usará ledger privado por campanha/ramo, com pistas e hipóteses revisáveis, origem/independência de fontes, contraprovas e estados inconclusivos. Suspeita ou fala LLM não confirma identidade e não permite divulgação; vínculo factual restrito exige evidências/DEC-066, e revelação exige ACL/consentimento/risk gate por audiência (DEC-019/028/041/045/046). Rumores e repercussões DEC-029/074/075 são separados de fato e punição. **Preservar `knowledge/periods/<ANO>-DR/` fisicamente por ano, sem evidências privadas no cânone.** ADR-0072/documento 77; 58 testes não executados, sem POC BG2:EE/EEex/multiplayer.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

NPCs de guardas, acusados e testemunhas DEC-078 devem ter identidade lógica verificada, sem confundir sprite ou nome de NPC/homônimo com acusado.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Guarda/mensageiro/alvo DEC-079 exigem NPCIdentity verificada onde necessária; homônimos e CRE não dão identidade causal para perseguir ou receber caso.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Atualização de mandado DEC-080 liga alvo por identidade verificada, não por homônimo/CRE. Sem prova, proibida captura por alias.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Dano/beneficiário/remédio DEC-081 exigem identidade lógica verificada; homônimo ou instância ambígua não pode receber itens ou culpa.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Responsabilizar agente requer identidade lógica verificada, não homônimos, farda, cargo ou instância CRE; superior separado por evidência.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Fonte NPC requer identidade lógica confirmada; homônimos ou CRE iguais não podem ser fundidos nem publicamente identificados.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Pessoa protegida e protetores usam identidades lógicas verificadas, evitando trocar testemunha por homônimo ou instância reciclada.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Informante, protetor e fonte têm identidade lógica verificada. Alias/mesmo nome não liga automaticamente testemunha protegida a rota.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Nome ou assinatura usada em documento falso não comprova identidade lógica de NPC/PC; reconciliação de actor IDs separada de claims.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

ID persistente verificado é precondição para atribuir vínculos; duplicata de nome/sprite não herda lealdades nem traições.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Contratos vinculam identidade NPC persistente comprovada, não nome textual, alias ou instância temporária de engine; respawn requer reconciliação.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Atribuição a fonte exige identidade lógica DEC-066; homônimos e aliases DEC-076 não viram fontes independentes por diferença de nome.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Receptor de dossiê precisa ser identificado por ator lógico e scope, não homônimo. ID de fonte protegida não se torna campo público da view.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Identidade persistente verificada, não nome/CRE por semelhança, fundamenta alvos e participantes de plano.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Identidade lógica do NPC deve ser revalidada após mudança de instância/host; mesmo nome de CRE não comprova que ator está disponível.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Identidade lógica estável é a chave de exclusividade de reservas DEC-093; runtime CRE ou nome de personagem não comprova identidade diferente nem disponibilidade física.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Deduplicar recurso NPC por identidade lógica persistente DEC-066, não alias, nome CRE ou instância. Sem receipt físico, status permanece desconhecido.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-096/C — Discovery v9.2

Regra histórica DEC-096/C não recria NPC morto por cronologia ou alias duplicado; toda presença mecânica usa identity/adapter testado.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Efeitos de patrulha DEC-097/C não multiplicam NPCs com aliases de mesmo persistent ID; manter ownership.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

persistent_npc_id deve sobreviver a troca de engine instance. Nome, CRE/template e alias não são IDs de instância nem prova de ownership.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Persistent NPC ID não é engine instance ID; geração e proveniência distinguem múltiplas instâncias e reciclagem.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Identidade persistente do NPC não autoriza acesso a scripts/romance/quest state por nome ou CRE.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Regional simulation and materialization cannot treat ambiguous quest flags as facts. Protect quest-owned actors/objects and persistent NPC identities; semantic milestones need curated proof and do not grant spawn, despawn, cleanup, loot or irreversible effects without existing host gates. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

A reconciliação DEC-102 não ressurge nem duplica instâncias por diferença de quest. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **identidade persistente**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para identidade persistente do destinatário independente de instance do motor, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para identidade persistente distinta da instância de motor, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Id persistente de obrigor e beneficiário distinto da instância host. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Identidade persistente de obligor é separada da instância física no host. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
