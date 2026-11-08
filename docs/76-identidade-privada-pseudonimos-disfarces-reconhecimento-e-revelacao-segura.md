# DEC-076 — Identidade privada, pseudônimos, disfarces e reconhecimento controlado

**Discovery v7.2 · ADR-0071 · opção C APROVADA somente como arquitetura · NÃO IMPLEMENTADA**  
**Escopo:** dados de personas sociais e sigilo, não engine de disfarce. **56 testes candidatos T076-01..56 NÃO EXECUTADOS.**

## 1. Problema e invariantes

- O mesmo ator pode usar nomes e personas sociais distintos sem que todos os NPCs conheçam a correlação.
- Um nome ou uma aparência pode corresponder a mais de um ator: strings não são identidade confiável.
- Identidade factual privada pode existir para auditoria, **sem** publicação narrativa.
- Uma pista pode gerar `SUSPECTED`, mas evidência conflitante permanece `DISPUTED` ou `PENDING_EVIDENCE`.
- Descobertas devem respeitar privacidade, consentimento, ano DR, região, ramo e ordem causal de acontecimentos.
- Nenhum alias comprovado pela IA equivale a rename de CRE, troca visual, detecção de disfarce ou scripts de BG2:EE/EEex comprovados.

## 2. Domínios de dados separados

```text
knowledge/periods/<ANO>-DR/            # apenas lore canônico, fontes e resoluções curadas (DEC-060/061/062)
  chronology/, characters/, guilds/ ... # não inserir segredos dinâmicos de PCs/NPCs

campaign-overlays/<campaign>/<branch>/   # ilustração de domínio lógico, caminho físico a definir em SPECS
  identity-registry/                    # identidades estáveis privadas, DEC-066
  persona-registry/                     # aliases com escopo, época, versões
  evidence-ledger/                      # pistas, provas, origem, validade, contradição
  identity-links/                       # hipótese/avaliação/vínculo e audiência
  observer-beliefs/                     # conhecimento por NPC/facção/localidade
  disclosure-ledger/                    # difusão, autorizações, idempotência
  attribution-effects/                  # reconhecimento social DEC-075, sem efeito engine presumido
```

A árvore `campaign-overlays/...` é **apenas desenho candidato**, não repositório implantado; `knowledge/periods/` já possui esqueletos de anos, porém sem lore importado. A indexação cruzada não dissolve o isolamento físico do conhecimento por ano DR.

## 3. Tipos e contratos candidatos (não implementados)

```text
FactualActorIdentity {
  campaign_id, branch_id, actor_identity_id,
  actor_kind: PC|NPC, stable_identity_proof, owner_id?,
  known_runtime_observations[], version, sensitivity_acl
}
Persona {
  campaign_id, branch_id, persona_id, display_alias,
  locale_or_faction_scope, valid_from_dr?, valid_to_dr?,
  actor_link_private_ref?, origin_event_id?, status,
  public_traits[], sensitivity_acl, revision
}
IdentityLinkEvidence {
  evidence_id, event_id?, author_or_source_ref,
  subject_persona_ids[], candidate_actor_id?, provenance,
  time_dr, location_ref?, permitted_audience,
  evidence_kind: OBSERVED|DOCUMENT|TESTIMONY|RUMOR|OTHER,
  corroborates_or_contradicts, confidence_label, validity_state
}
IdentityLinkAssessment {
  link_id, campaign_id, branch_id, persona_ids[],
  candidate_actor_id?, evidence_refs[], contradictory_evidence_refs[],
  state: UNLINKED|SUSPECTED|VERIFIED_PRIVATE|DISCLOSED_TO_SCOPE|DISPUTED|REVOKED,
  curator_or_rule_revision, checkpoint_ref, acl, revision
}
ObserverBelief {
  observer_identity_id, claim_or_link_ref, confidence_label,
  source_chain[], learned_at_dr, region_ref?, visibility_acl,
  contradiction_refs[], belief_revision
}
DisclosureEvent {
  disclosure_id, cause_event_id?, identity_link_revision,
  audience_scope, channel, authorization_ref, privacy_gate_ref,
  effective_dr, idempotency_key, resolution_epoch,
  state: PROPOSED|AUTHORIZED|PUBLISHED|REJECTED|UNCERTAIN,
  receipt_ref?, checkpoint_ref, audit_ref
}
```

Nomes/atributos e tipos são **candidatos**; não estabelecer um novo protocolo pronto nem assumir um banco de dados específico. IDs permanecem internos, não equivalentes a nomes CRE ou tokens de jogador.

## 4. Máquina de estados e limites de autoridade

```text
UNLINKED --pista admissível--> SUSPECTED
SUSPECTED --provas fortes+revisão--> VERIFIED_PRIVATE
SUSPECTED --provas conflitantes--> DISPUTED
DISPUTED --resolução comprovada--> VERIFIED_PRIVATE ou UNLINKED
VERIFIED_PRIVATE --ACL+autorização+canal válido--> DISCLOSED_TO_SCOPE
[qualquer estado] --prova refutada/branch stale--> DISPUTED/REVOKED
```

A execução de `DISCLOSED_TO_SCOPE` exige destino e finalidade explícitos. Uma prova interna **nunca** provoca divulgação global por estado compartilhado. Revogação bloqueia **novas** divulgações, mas não faz os observadores esquecerem a informação já recebida (DEC-064). Lidar com essa memória como crença e, quando necessário, retificação ou propagação de notícia corretiva.

## 5. Fluxo de criação e recuperação de persona

1. Confirmar identidade do ator e autorização do dono/host, se for PC; se identidade incompleta, criar apenas registro `UNLINKED` de observação/persona, sem link factual definitivo.
2. Registrar nome alegado, escopo, validade, fonte e nível de sigilo, considerando homônimos e personas compartilhadas como ambíguos.
3. Aplicar filtros DEC-028 e políticos de DEC-041/045/046/019 **antes** do roteador DEC-059 e do LLM.
4. Separar contexto privado para auditoria de contexto público para NPCs, clientes e nós LAN.
5. Decidir se a representação é meramente narrativa ou possui capability realmente testada na instalação; se não comprovada, não executar mudança visual/mecânica.
6. Durante interação, recuperar apenas a crença e persona acessíveis ao NPC no tempo e local, sem introduzir nome verdadeiro de metadata da engine como conhecimento automático.

## 6. Fluxo de pistas, suspeitas e revelação

1. Registrar `IdentityLinkEvidence` com fonte, período e cadeia de proveniência; permitir testemunhos falsos como **alegações**, não prova de verdade.
2. Verificar validade temporal, vínculo com ator persistente DEC-066, incompatibilidades e possíveis contradições.
3. `SUSPECTED` pode produzir desconfiança localizada mediante políticas, mas não confirma a ligação nem a expõe irrestritamente.
4. A promoção para `VERIFIED_PRIVATE` exige evidências verificadas por mecanismo determinístico/curadoria, não avaliação solitária por LLM; limiares concretos ficam para SPECS/DEC-077.
5. Qualquer publicação solicita `DisclosureProposal` com público, canal, tempo, escopo, consentimento e risco acumulado. `HIGH` e segredos de jogadores têm bloqueio por padrão sem autorização.
6. Publicar apenas para a audiência permitida, com ledger idempotente. Atualizar `ObserverBelief` do destinatário, não reescrever fatos pretéritos.
7. Efeitos sociais posteriores ficam com DEC-029/030/074/075, por causa e público; efeitos mecânicos só por host/gateway/capabilities válidas.

## 7. Multiplayer, consentimento, observabilidade e segurança

| Limite | Política |
|---|---|
| Player owner versus controlador temporário | Referências distintas; controle DEC-045/046 não concede licença automática para divulgar segredo do titular. |
| Outro jogador na mesma party | Não recebe segredos do PC automaticamente; visibilidade configurada conforme DEC-019/041. |
| NPC homônimo/persona duplicada | `AMBIGUOUS`; vínculo privado só com evidência de identidade DEC-066. |
| Host/ledger privado | Capacidade de auditoria não implica visibilidade narrativa de NPCs ou de clientes. |
| LLM | Recebe persona de observador e contexto mínimo, sem verdade privada quando desnecessária. |
| Nó LAN | Pareado DEC-058 e role autorizada; revogação invalida jobs pendentes e cache com secrets. |
| Logs, índices e caches | ACL, minimização, segregação por campaign/branch, redação de valores e invalidação por revisão. |
| UI nativa | Sem afirmar ocultação visual/nome ou disfarce se API/adapter não comprovar. |
| Save/load e restauro | Reconciliar checkpoint/branch, revisões de persona/ligação e relógio; nunca importar futuras revelações. |
| Incidente UNKNOWN/UNCERTAIN | Não reexecutar divulgação, não inferir conhecimento por ausência de recibo. |

## 8. Reputação, autoria e consequências

- **Fato confirmado:** um personagem praticou a ação quando há prova no ledger; caso contrário `UNKNOWN` DEC-075.
- **Persona alegada:** personagem se apresenta como "Corvo Cinzento"; isso é uma declaração contextual, não atestado de identidade física.
- **Reputação percebida:** um grupo acredita que "Corvo Cinzento" é benfeitor, sem saber quem ele é.
- **Revelação:** nova evidência comprova vínculo a certos atores e uma divulgação específica é permitida.
- **Efeito:** gratidão/hostilidade podem mudar localmente via regras DEC-030/074, sem migração global de reputação por simples junção de nomes. A reputação mecânica do BG2:EE permanece independente.

## 9. Falhas e reconciliação

| Falha | Comportamento seguro |
|---|---|
| Link sem prova | `UNLINKED/SUSPECTED`; não divulgar verdadeira identidade. |
| Duas personas compartilham nome | Manter registros distintos, evitar fusão. |
| Relato forjado | Registrar alegação e contestação, não validá-la como fato. |
| ACL de jogador nega divulgação | Bloquear e registrar justificativa redigida. |
| Disclosure gerado em outro branch | `STALE`, cancelar. |
| Reentrega após retry | Deduplicação por idempotency key, sem dois efeitos. |
| Worker LAN revogado | Descartar resposta; invalidar contexto sensível futuro. |
| Falha de host ao aplicar efeito mecânico | `UNCERTAIN`, aguardar reconciliação; nenhum retry cego. |
| UI expõe nome real | Não afirmar proteção visual sem POC; ajustar experiência após testes. |
| Restauração de checkpoint | Reconciliar persona, links, observadores, caches e eventos de revelação antes de continuar. |

## 10. Matriz de testes candidatos — TODOS NÃO EXECUTADOS

Cada cenário requer fixture sintética, pass/fail esperado, riscos e revisão; alguns exigirão futuras POCs com engine. Não representam resultados de testes realizados.

| ID | Caso esperado | Execução |
|---|---|---|
| T076-01 | Duas personas para um mesmo PC não são divulgadas automaticamente entre comunidades. | NÃO EXECUTADO |
| T076-02 | Duas identidades factuais com o mesmo pseudônimo ficam AMBIGUOUS. | NÃO EXECUTADO |
| T076-03 | Nome e aparência iguais não são evidência suficiente para unir personas. | NÃO EXECUTADO |
| T076-04 | Identidade lógica não verificada DEC-066 bloqueia vínculo definitivo. | NÃO EXECUTADO |
| T076-05 | Criar persona narrativa não modifica nome ou visual no motor. | NÃO EXECUTADO |
| T076-06 | Pseudônimo pode constar no diálogo sem afirmar que engine o ocultou. | NÃO EXECUTADO |
| T076-07 | NPC que não testemunhou ato não conhece o ator por consulta ao ledger. | NÃO EXECUTADO |
| T076-08 | Testemunha que viu só pseudônimo não descobre automaticamente identidade real. | NÃO EXECUTADO |
| T076-09 | Link confirmado no ledger privado não altera crença do NPC. | NÃO EXECUTADO |
| T076-10 | Suspeita SUSPECTED não vira vínculo factual VERIFIED_PRIVATE. | NÃO EXECUTADO |
| T076-11 | Prova host-confirmed com ACL pode sustentar vínculo factual privado. | NÃO EXECUTADO |
| T076-12 | Rumor de identidade não equivale a prova confirmada. | NÃO EXECUTADO |
| T076-13 | Documento falso gera alegação contestável, não prova automática. | NÃO EXECUTADO |
| T076-14 | Documento com origem desconhecida mantém PENDING_EVIDENCE. | NÃO EXECUTADO |
| T076-15 | Provas contraditórias produzem DISPUTED, não revelação definitiva. | NÃO EXECUTADO |
| T076-16 | Data futura da pista não é consultada em ano DR anterior. | NÃO EXECUTADO |
| T076-17 | Fato histórico revisado no Knowledge Pack não transfere alias de campanha. | NÃO EXECUTADO |
| T076-18 | Persona criada em outra campanha não é importada implicitamente. | NÃO EXECUTADO |
| T076-19 | Persona de branch alternativo não altera branch atual. | NÃO EXECUTADO |
| T076-20 | Restore pré-revelação não torna a nova revelação conhecida. | NÃO EXECUTADO |
| T076-21 | Reload não duplica o evento de revelação nem seus efeitos. | NÃO EXECUTADO |
| T076-22 | Difusão de identidade depende de canal social e tempo. | NÃO EXECUTADO |
| T076-23 | Guilda informada não torna todas as demais facções informadas. | NÃO EXECUTADO |
| T076-24 | NPC próximo sem contato não recebe ligação por proximidade. | NÃO EXECUTADO |
| T076-25 | Divulgação a um NPC não autoriza divulgação pública. | NÃO EXECUTADO |
| T076-26 | Revelação a um grupo privado não abre ACL universal. | NÃO EXECUTADO |
| T076-27 | Revogação de autorização impede divulgações futuras. | NÃO EXECUTADO |
| T076-28 | Revogação invalida caches pendentes com verdadeiro nome. | NÃO EXECUTADO |
| T076-29 | Worker LAN não autorizado recebe apenas contexto minimizado. | NÃO EXECUTADO |
| T076-30 | Logs redigidos não exibem mapeamento real persona↔ator. | NÃO EXECUTADO |
| T076-31 | Embeddings/índices não tornam segredos acessíveis a usuários sem ACL. | NÃO EXECUTADO |
| T076-32 | Saída LLM com identidade secreta não permitida é bloqueada antes da publicação. | NÃO EXECUTADO |
| T076-33 | Auditoria do anfitrião não equivale a conhecimento narrativo de NPC. | NÃO EXECUTADO |
| T076-34 | PC ausente não tem consentimento presumido para revelar seu segredo. | NÃO EXECUTADO |
| T076-35 | PC delegado mantém titularidade e política de segredo do dono. | NÃO EXECUTADO |
| T076-36 | Jogador do mesmo grupo não lê automaticamente segredo de outro. | NÃO EXECUTADO |
| T076-37 | Ato de outro personagem não é transferido ao mesmo pseudônimo homônimo. | NÃO EXECUTADO |
| T076-38 | Reputação pública de alias não se funde automaticamente com a identidade civil. | NÃO EXECUTADO |
| T076-39 | Revelação válida gera proposta contextual de efeito, não mutação mecânica direta. | NÃO EXECUTADO |
| T076-40 | Relato falso causa no máximo percepção/rumor autorizado, nunca ligação factual. | NÃO EXECUTADO |
| T076-41 | Correção posterior preserva cadeia de crença e origem anterior. | NÃO EXECUTADO |
| T076-42 | Revisão DISPUTED suspende efeitos HIGH e atribuições definitivas. | NÃO EXECUTADO |
| T076-43 | Revelação involuntária HIGH exige gate e consentimento aplicável. | NÃO EXECUTADO |
| T076-44 | Soma de divulgações LOW que expõe segredo HIGH exige novo gate. | NÃO EXECUTADO |
| T076-45 | Rumor repetido não concede reputação duplicada. | NÃO EXECUTADO |
| T076-46 | Nenhum XP ou inventário é alterado por revelar pseudônimo. | NÃO EXECUTADO |
| T076-47 | Nenhuma reputação mecânica muda sem capability e receipt do host. | NÃO EXECUTADO |
| T076-48 | Cliente multiplayer não autoriza sozinho correlação ou mecânica. | NÃO EXECUTADO |
| T076-49 | Nome exposto na UI da engine não é assumido como conhecido por NPC sem prova. | NÃO EXECUTADO |
| T076-50 | Incompatibilidade de mod/build invalida capacidade presumida de disfarce. | NÃO EXECUTADO |
| T076-51 | Falha UNCERTAIN bloqueia repetição cega de divulgação. | NÃO EXECUTADO |
| T076-52 | Queue stale de outro checkpoint não divulga segredo após restore. | NÃO EXECUTADO |
| T076-53 | Caso de ruptura de confiança tem consequência narrativa só após gates. | NÃO EXECUTADO |
| T076-54 | Consulta a diretório anual 1369 DR não encontra segredos de overlays de 1374 DR. | NÃO EXECUTADO |
| T076-55 | Teste sintético de vazamento de identidade no prompt rejeita resposta. | NÃO EXECUTADO |
| T076-56 | POC host+2 clientes é necessária antes de anunciar disfarce mecânico funcional. | NÃO EXECUTADO |

## 11. Sequência de investigação futura

1. Fixtures offline de personagens homônimos, múltiplas personas, espionagem, testemunho falso, provas conflitantes e revelação localizada.
2. Matriz ACL de PCs e NPCs, delegações DEC-041/045/046 e host versus clientes; testes de vazamento em prompt, cache e worker LAN.
3. Testes de idempotência, estados `DISPUTED/UNCERTAIN`, checkpoint, restore e Knowledge Pack versionado.
4. Inventário de observabilidade da engine BG2:EE limpa e bridge/EEex inicialmente read-only; registrar onde dados de identidade/aparência realmente podem ser lidos.
5. POCs específicas e isoladas para disfarce visual/nome, quando cabíveis, com gating por build, mods, host e dois clientes; negar funcionalidade não comprovada.
6. Somente após evidência, elaborar SPECS de UI, capacidades, mecanismo de validação de provas, timing de rumores e limites de privacidade.

## 12. Dependências e decisões futuras

- **DEC-060–063**: corpus canônico anual físico, fontes, ingestão e Knowledge Pack versionado; sem vazamento ao overlay.
- **DEC-064–068**: crenças, memória hierárquica, identidade persistente, promoção e hibernação de NPCs.
- **DEC-069–075**: viagem, incidentes, encontros, reputações, relatos, autoria e responsabilidades reais versus percepção.
- **DEC-019/028/041/045/046**: visibilidade, ACL, consentimento e delegação de PCs.
- **DEC-011/012/027/034/053/056/057–060**: host, gateway, risco, checkpoints, custos, LAN e validação de texto.
- **DEC-006/007/013/015/016/017/018** ainda abertas; em particular não prometer UI/renomeação ou disfarce mecânico.
- **DEC-077 aberta:** como estruturar investigação, corroborar/contestar pistas e autorizar conclusões sobre identidade sem revelar segredos indevidamente. Alternativas A) pista única resolve; B) LLM arbitra; **C) ledger de evidências, corroborar/contradizer, suspeita progressiva, revisão humana/riscos e autorização contextual**.

### Integração DEC-077/C — Investigação por evidências (Discovery v7.3; não implementada)

A investigação de personas DEC-076 usará ledger privado por campanha/ramo, com pistas e hipóteses revisáveis, origem/independência de fontes, contraprovas e estados inconclusivos. Suspeita ou fala LLM não confirma identidade e não permite divulgação; vínculo factual restrito exige evidências/DEC-066, e revelação exige ACL/consentimento/risk gate por audiência (DEC-019/028/041/045/046). Rumores e repercussões DEC-029/074/075 são separados de fato e punição. **Preservar `knowledge/periods/<ANO>-DR/` fisicamente por ano, sem evidências privadas no cânone.** ADR-0072/documento 77; 58 testes não executados, sem POC BG2:EE/EEex/multiplayer.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Processo DEC-078 não revela automaticamente nome real de acusado sob pseudônimo; ligação factual restrita e divulgação são gates separados.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Alvo de mandado DEC-079 pode ser persona não reconhecida; identidade factual privada não é divulgada automaticamente ao destinatário sem evidência/ACL.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Retificar mandado DEC-080 de persona/alias não revela identidade factual privada automaticamente; transmissão de alvo exige ACL e evidências DEC-076.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Reabilitar pseudônimo DEC-081 não autoriza revelar identidade factual de PC ou fundir reputações sem evidence/ACL/consentimento.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Investigação de autoridade não autoriza desmascarar pseudônimo ou publicar identidade secreta de testemunha/PC sem ACL/consentimento.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Identidade factual protegida da fonte mantém persona/alias independente e disclosure por competência; revelação pública não decorre de investigação selada.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Fonte protegida pode ter alias e esconderijo; não assumir que perseguidor sabe o alias real ou que o disfarce mecânico está validado.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Saber localização de abrigo não comprova identidade verdadeira da pessoa; personas/aliases e autoria privada permanecem distintos.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Alias usado em isca não revela identidade factual verdadeira sem prova. NPC pode ser enganado sem a IA modificar verdadeiro registro de identidade.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Identidade social, pseudônimo e compromisso secreto são eixos separados; associação entre personas e agente duplo precisa de prova e divulgação autorizada.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Pseudônimos e aliases não substituem ID factual NPC ao contratar; identidade da fonte permanece separada da persona conhecida pelo contratante.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Alias do informante não prova identidade factual, nem constitui outra fonte independente. Investigações de identidade permanecem sob ACL e evidências.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Citações e aliases de dossiê não podem ligar duas personas públicas à identidade factual privada sem permissão/evidência e canal legítimo.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Proposta de investigar uma persona preserva identidade factual privada e não fornece o nome verdadeiro a todos os participantes.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Personas e pseudônimos permanecem privados/por audiência; replanejamento não revela identidade verdadeira a aliados ou perseguidores.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Aliases de uma mesma identidade factual não podem obter agendas paralelas do mesmo ator; dados secretos sobre quem é dono da reserva são redigidos para públicos externos.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Alias não é identificador de recurso: duas personas do mesmo NPC compartilham identidade persistente para detectar deadlocks, sem revelar ligação ao jogador.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-096/C — Discovery v9.2

Evento histórico DEC-096/C não quebra pseudônimo ou revela identidade privada pela escala GLOBAL; observadores usam provas de reconhecimento.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Famílias de efeitos DEC-097/C não expõem identidade privada em explicações a NPCs sem permissão.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

IDs reais e pseudônimos protegidos não vazam via snapshot, comparação host, logs, prompts LLM ou eventos de entrada de mapa.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Persona, pseudônimo e disfarce não criam novas identidades mecânicas nem propriedade de instância.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Identidade secreta não deve vazar por nomes de scripts ou flags com significado autoexplicativo.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Quest state, mapping rule names and even flag metadata may expose future branches, romance or hidden identities; they remain private technical evidence. Dossiers, sources and NPCs receive only authorized safe milestones through independently confirmed disclosure; no belief is promoted to fact from ambiguous observations. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Quest flags DEC-102 não podem revelar identidades privadas apenas por uso técnico. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** a conclusão técnica de uma quest não concede automaticamente conhecimento ou crença a NPCs/facções. `QuestMilestoneAdmission` pode gerar proposta de notícia/reputação somente por regras, proveniência, tempo, geografia, visibilidade e ACL; notícia requer fonte/canal/delivery, e seus destinatários podem conhecer apenas versões parciais. Não expor identidades secretas, fontes protegidas ou raw flags por prompts/logs/dossiês. Ações mecânicas derivadas dependem de recibos host, sem atribuição presumida de PC. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **identidade e sigilo**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para pseudônimos e identidades privadas não vazam em erratas públicas, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para aliases e identidades privadas com ACL, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Identidade real protegida não aparece em notificações públicas. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Pseudônimos e fontes são protegidos em views de contrato. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
