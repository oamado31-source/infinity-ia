# DEC-043 — Mortalidade configurável, ressurreição e legado de personagens

**Discovery v3.9 · DEC-043 aprovada (opção C) · ADR-0038 · não é SPEC nem implementação**

## Objetivo

Fazer com que a perda de um personagem possa ter peso dramático sem impor a mesma tolerância a risco a todas as campanhas. A simulação histórica mantém consequências do personagem mesmo quando ele deixa de ser controlável; a mecânica real de morte e retorno pertence ao host de BG2:EE.

### Fronteiras de autoridade

- **Jogador:** controla intenções/atos do próprio PC e decisões pessoais que o motor ou a política reconheça; não assume permissão de outro jogador.
- **Anfitrião:** configura e comunica o perfil versionado de risco da campanha; não inventa consentimento para permadeath PvP de terceiros.
- **Motor/host:** determina e comprova se PC sofreu a morte, retornou, ficou com itens ou alcançou estado de game-over.
- **Regras + Action Gateway:** verificam se operações propostas são permitidas e se dependem de receipts; não executam ações arbitrárias de LLM.
- **Diretores (PSD/CSD/Strategic):** planejam desdobramentos narrativos possíveis, mas não escolhem morte/ressurreição de PC nem criam fatos mecânicos não observados.
- **Memória/cronologia:** registra fato confirmado, separa crença/boato e aplica ACL; preserva legado independentemente de existir personagem ativo.

## Estados conceituais candidatos (NÃO correspondem diretamente a APIs do BG2:EE)

```text
ACTIVE --[host observa derrota]--> INCAPACITATED_OR_UNVERIFIED
          |
          +--[host confirma morte]--> DEAD_CONFIRMED
                                         |
                                         +--[regra confirma possibilidade]--> RETURN_ELIGIBLE
                                         |       |
                                         |       +--[recursos, comando e receipt do host]--> RETURNED_CONFIRMED
                                         |
                                         +--[politica e estado mecanico validos]--> FINAL_DEATH_RECORDED

qualquer transicao ambigua --> UNCERTAIN (reconciliar; NAO repetir comando)
```

`RETURN_ELIGIBLE` não significa que uma magia já foi usada ou que o jogador aceitou um procedimento. `FINAL_DEATH_RECORDED` é conclusão de política respaldada por estado e condições efetivas; não se confunde com simples ausência de atividade. Uma morte confirmada pode permanecer registrada como evento histórico mesmo após um retorno confirmado mais tarde.

A máquina acima é puramente conceitual: se o motor não oferecer estado observável ou impedir a continuação da sessão, o sistema entra em bloqueio/diagnóstico, não cria um segundo personagem artificialmente.

## Modelo de eventos candidato

```text
CampaignMortalityPolicy(
  campaign_id, policy_version, policy_profile, published_at,
  affected_participants[], consent_reference?, engine_build_fingerprint,
  compatible_feature_gates[], status
)
PCDeathEvidence(
  campaign_id, pc_id, controlled_by, encounter_id, world_time, host_event_id,
  engine_build, save_fingerprint, cause_class, observation_status,
  authorized_pvp_scope?, provenance
)
ReturnAttempt(
  campaign_id, pc_id, attempt_id, ruleset_version, resource_refs[],
  policy_version, requested_by, requested_action_id, status, host_receipt?
)
PCLegacy(
  campaign_id, pc_id, event_cursor, confirmed_event_ids[],
  relationships[], obligations[], world_effect_refs[], knowledge_acl,
  summary_revision, projection_status
)
```

São campos exploratórios. Não representam tabelas implementadas nem uma promessa de acesso aos dados por EEex. Identidade e proprietários não devem ser inferidos apenas por nome do personagem ou nickname de cliente.

## Políticas operacionais candidatas

| Questão | Caminho mais seguro para SPECS | Limite |
|---|---|---|
| Regras de base | Registrar morte e possíveis retornos segundo o BG2:EE efetivo | Não duplicar implementação de regras que o host já aplica |
| Perfis alternativos | Opt-in explícito, versionado e verificado antes de ativar | Não mudar risco irreversível silenciosamente durante campanha |
| Permadeath PvE | Expor risco previsto na política e observar estado confirmado | Não afirmar que todas as mortes podem ser preventivamente bloqueadas |
| Permadeath PvP | Exigir regra e consentimento específicos de DEC-042 | Um duelo permitido não dá permissão para eliminação permanente |
| Jogador ausente | Não forçar escolha de sacrifício ou retorno; não gerar morte offscreen por texto | Não inventar ação mecânica em ausência |
| Recuperação | Usar regras e recursos mecânicos comprovados por build/modlist | IA pode propor quest, mas não efetuar ressurreição |
| Legado narrativo | Continuar consequências e memórias derivadas de fatos | Nenhum segredo vira informação pública automaticamente |
| Inventário/espólio | Respeitar engine + propriedade/consentimento/política de campanha | Transferências para sucessor ficam para DEC-044 |
| Restauro de saves | Fingerprint + event cursor + reconciliação | Sem replay automático de morte ou de retorno |

## Exemplo: guerreiro defendendo uma aldeia

1. Durante batalha carregada, o host registra derrota; a camada externa não antecipa morte sem evidência.
2. Confirmada a morte, o estado narrativo marca o acontecimento com hora e testemunhas conhecidas. Um rumor distante não é automaticamente verdade compartilhada.
3. Se o grupo tentar ressuscitá-lo, verificam-se regras, recursos, localização e efeitos da build instalada; somente a ação concretizada e confirmada pelo host gera `RETURNED_CONFIRMED`.
4. Se o perfil/circunstâncias configurarem morte definitiva, o legado mantém feitos, relações, promessas e impactos que efetivamente ocorreram.
5. Se um aldeão erguer um memorial, isso é primeiro uma **proposta narrativa**. Torná-lo NPC, item ou objeto físico no mapa exige suporte e autorização próprios, não nasce automaticamente do registro de morte.
6. Se outro jogador criar um novo personagem, não herda por padrão memórias privadas, itens ou o histórico moral do guerreiro; a política de substituição é DEC-044.

## Relação com decisões anteriores

- **DEC-004/019/020:** histórico próprio e seus segredos não são transferidos por morte.
- **DEC-005-R/003:** manter o BG2:EE como baseline; testar primeiro build limpa e depois mods.
- **DEC-008/011/012:** event log/snapshot, Action Gateway, receipt do host e reconciliação `UNCERTAIN`.
- **DEC-009/025/027/034:** cronologia e riscos canônicos protegidos, inclusive grandes consequências históricas.
- **DEC-021/022/031–033:** avanço de mundo offscreen não pode forjar o óbito físico de um PC; respeitar calendário e escala.
- **DEC-028/029/030:** notícia, rumor, reputação e legado dependem de conhecimento e proveniência.
- **DEC-035–040:** alinhamento, mudanças de fé, jornadas pessoais e coordenação cooperativa continuam como histórico, sem imposição de continuidade a um novo PC.
- **DEC-041/042:** agência individual, segredos e consentimento específico em PvP.

## Matriz de testes candidatos (20 cenários)

| ID | Cenário | Critério de aceitação candidato |
|---|---|---|
| CAND-MORT-001 | Política de mortalidade por campanha | Perfil versionado e comunicado; não há escalada de risco silenciosa |
| CAND-MORT-002 | Duas campanhas em perfis distintos | Cada uma mantém regras/recursos/legado isolados |
| CAND-MORT-003 | Personagem cai sem morte host-confirmada | Não registrar morte definitiva nem criar boato como fato |
| CAND-MORT-004 | Host confirma morte | Evento correlacionado ao PC correto, save e sessão |
| CAND-MORT-005 | Regras permitem ressurreição e magia é executada | Só confirmar retorno com receipt/estado do motor |
| CAND-MORT-006 | Magia falha, recursos insuficientes ou alvo inválido | Não inventar retorno nem conceder itens/XP |
| CAND-MORT-007 | Engine não suporta determinado perfil de recuperação | Não habilitar política anunciada como garantida |
| CAND-MORT-008 | POC com host e dois clientes | Estado de vivo/morto/retornado coerente em ambos após save/load |
| CAND-MORT-009 | Queda provoca game-over de protagonista | Diagnóstico e gate de compatibilidade, sem prometer continuação |
| CAND-MORT-010 | Duelo consensual sob regra sem permadeath | Não equiparar duelo a aceitação de eliminação irreversível |
| CAND-MORT-011 | Consentimento de PvP fatal não existe | Política segura impede/denuncia tentativa; sem afirmar bloqueio mecânico não testado |
| CAND-MORT-012 | Efeito de área/armadilha causa dano PvP | Política sobre resultados indiretos também é verificada |
| CAND-MORT-013 | Jogador ausente | IA não consente, decide morrer ou conduz PC para perigo em nome dele |
| CAND-MORT-014 | Região remota em catch-up | Simulação não cria morte mecânica de PC ausente/offscreen |
| CAND-MORT-015 | Personagem morre com quest pessoal incompleta | Arco pode ficar suspenso/legado; não completa por decreto da IA |
| CAND-MORT-016 | Morte e retorno com notícias em outras regiões | Rumores, testemunhas e desmentidos respeitam canais, tempo e ACL |
| CAND-MORT-017 | Personagem renasce após repercussão pública | Evento de morte continua histórico, mas narrativas refletem retorno conhecido |
| CAND-MORT-018 | Retry/reconexão no momento de ressurreição | Comando não é reaplicado sem reconciliation; nenhum item/recompensa duplicado |
| CAND-MORT-019 | Carga de save anterior à morte | Detecta divergência de save/event cursor; oferece procedimento controlado |
| CAND-MORT-020 | Modo Original e build com mods distintos | Sem vazamento de perfil/legado; capacidades incompatíveis ficam desabilitadas |

## Riscos e mitigação preliminar

| ID | Risco | Mitigação candidata |
|---|---|---|
| R-MORT-01 | Game-over ou morte do protagonista impede continuidade | POC com protagonistas e PCs cooperativos; fallback explícito |
| R-MORT-02 | Campanha promete recuperar morte que motor torna irreversível | Capability gates por build e não prometer garantia não demonstrada |
| R-MORT-03 | Narrativa registra morte falsa ou duplicada | Receipts, identidade estável, estado `UNCERTAIN`, cursor de eventos |
| R-MORT-04 | Ação de revive duplicada após timeout | Idempotência + reconciliação de save antes de repetir |
| R-MORT-05 | Itens, XP ou corpos inconsistentes após retorno | Verificar engine em host+dois clientes e persistência |
| R-MORT-06 | Consentimento PvP genérico usado como autorização de permadeath | Escopo separado + acordo dos participantes afetados |
| R-MORT-07 | Segredos de PC morto tornam-se públicos automaticamente | ACL, evidência de descoberta e canal de notícia |
| R-MORT-08 | Retorno apaga fatos e relações legadas | Histórico append-only, projeção de estado atual recalculada |
| R-MORT-09 | Perfil alterado sem ciência dos jogadores | Manifesto versionado, aviso, transição segura e consentimentos pertinentes |
| R-MORT-10 | NPCs reagem a rumor como fato definitivo | Conhecimento por personagem/facção e proveniência de crença |
| R-MORT-11 | Sistema cria personagem substituto com ativos/segredos indevidos | Decisão separada DEC-044; nenhuma herança automática |
| R-MORT-12 | Diferenças de mods alteram as regras de morte | Matriz de compatibilidade/regras por build; POCs repetidas |

## Pendências reais

- Definir regras precisas da campanha e de cada spell/kit por build.
- Verificar se é possível evitar irreversibilidade em casos particulares e o que acontece com protagonista/game-over.
- Interface de avisos, consentimentos, perfil de risco, revogação e troca segura de policy.
- Separar morte permanente de ausência de personagem ou aposentadoria voluntária.
- **DEC-044** — novo personagem, sucessão, continuidade do grupo, propriedade/espólio e conhecimento legítimo.

**Conclusão:** arquitetura escolhida, nenhuma POC ou funcionalidade mecânica implementada.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

DEC-068 não pressupõe mortalidade automática de NPC offscreen por passar tempo ou estar DORMANT. Morte/ressurreição e efeitos de legado seguem regras e gates confirmados; tempo real fora de sessão não implica evento fatal. Ver doc. 68.

## Integração DEC-091/C — Discovery v8.7

Ações operacionais que possam matar personagem ou levar a dano grave exigem os gates e políticas de mortalidade; nunca presumir efeito.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Replanejar não atribui ações a personagem recém-criado que não participou do plano nem tem autorização de titular.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Morte, ressurreição e legado são estados protegidos; não recriar morto por reentrada ou ausência em scan parcial.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Morte e ressurreição de PC não são inferidas de indicadores de quest sem host receipt.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** DEC-101 interpretation is read-only, version-pinned and independent of gateway/host execution. A confirmed semantic milestone does not authorize actions or prove a command receipt; mod upgrades, checkpoint restore, revised mapping, epoch mismatch or contradictory states cause fail-closed reconciliation. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
