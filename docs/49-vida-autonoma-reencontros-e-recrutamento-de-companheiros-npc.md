# DEC-049 — Continuidade autônoma de NPCs após saída, reencontros e recrutamento

**Versão:** Discovery v4.5 · **Estado:** diretriz arquitetural aprovada; modelo candidato para SPECS (não implementado) · **ADR:** `decisions/ADR-0044-vida-autonoma-persistente-de-companheiros-apos-saida.md`.

## 1. Objetivo e limites

Quando um companheiro NPC deixa a party **de modo realmente confirmado**, mantê-lo como agente persistente do Living World, com histórico e objetivos próprios. A party não o “desinstala” do mundo; nem o motor necessariamente consegue movê-lo fisicamente em background. O plano integra DEC-047 (identidade/autonomia narrativa), DEC-048 (ruptura), DEC-021/022 (escala/tempo), DEC-031/032 (facções/economia), DEC-008 (persistência), DEC-028/030 (conhecimento/reputação), DEC-009/034 (cânone/eventos críticos) e DEC-011/012 (autoridade mecânica).

A opção aprovada é **B — autonomia persistente com simulação hierárquica, reencontros e possível recrutamento futuro**. Não são requisitos aprovados os resultados exatos de viagens, sucesso de recrutamento, modificações de mapas ou ativação de hooks ainda não demonstrados.

## 2. Estados conceituais e fronteiras

| Estado | Significado | Efeito mecânico que NÃO se deve presumir |
|---|---|---|
| `IN_PARTY_CONFIRMED` | NPC está na equipe segundo host | autonomia não remove controle tático acordado |
| `DEPARTURE_INTENT` | desacordo e possível intenção de partir | NPC ainda não foi removido |
| `DEPARTURE_PENDING` | operação tipada solicitada, aguardando recibo | não iniciar vida offscreen como saída concluída |
| `POST_PARTY_ACTIVE` | saída confirmada, NPC relevante e próximo | NPC não está automaticamente carregado em outra área |
| `POST_PARTY_NEAR` | agenda mais resumida em região próxima | spawn e presença física ainda requerem host |
| `POST_PARTY_DISTANT` | checkpoint/agenda regional, recursos agregados | não rodar IA por NPC a cada tick |
| `POST_PARTY_DORMANT` | estado persistido até reativação justificada | não avançar tempo se política FROZEN |
| `REUNION_CANDIDATE` | há contexto compatível para possível reencontro | não significa spawn/diálogo disponível |
| `RECRUITMENT_PENDING` | proposta/aceitação narrativa e preflight | não significa personagem já incorporado |
| `IN_PARTY_CONFIRMED` | retorno confirmado pelo host | fechar/excluir agenda concorrente de viagem |

**Invariante:** o modelo de vida externa só começa quando `PARTY_MEMBER_REMOVED` estiver confirmado. Em `UNCERTAIN`, bloquear materialização, reconciliar e não repetir comando cegamente.

## 3. Dados candidatos (não schema final)

```text
CompanionContinuityState
  campaign_id, npc_id, canon_source_id?, native_resource_ref?, ruleset_version
  time_dr, host_revision, last_engine_receipt_id?, identity_revision
  party_membership (CONFIRMED_IN_PARTY | CONFIRMED_OUT | PENDING | UNCERTAIN)
  activity_tier (ACTIVE | NEAR | DISTANT | DORMANT)
  last_confirmed_location?, projected_region?, projected_location_confidence
  current_objectives[], obligations[], active_affiliations[], available_resources
  relationship_refs[], knowledge_acl_refs[], former_party_refs[]
  last_checkpoint_id, pending_reunion_id?, simulation_seed, provenance

CompanionActivityProposal
  proposal_id, npc_id, campaign_id, cause_event_id, time_window
  preconditions[], faction_links[], travel_route_ref?, region_resources
  expected_effects[], risk_class (LOW | MEDIUM | HIGH)
  knowledge_scope, canon_source, approval_status, mechanical_status

CompanionReunionCandidate
  reunion_id, npc_id, campaign_id, compatible_area, valid_time_window
  position_preflight, host_party_state, lore_constraints, availability
  narrative_context, safe_fallback, host_receipt_id?
```

`projected_region` é projeção explicável do simulador, não confirmação de uma entidade presente no motor. O log de eventos preserva fatos mesmo quando o NPC muda de estado. Ao voltar a party, **não duplicar** uma agenda offscreen e uma instância tática ativa.

## 4. Ciclo de continuidade

1. **Confirmar a saída:** capturar evidência do host e associá-la à intenção da DEC-048; rejeitar transições baseadas apenas em fala gerada.
2. **Congelar o snapshot inicial:** identidade, estado mecânico conhecido, data/hora, região, inventário com fonte autoritativa, relações e promessas, sob proteção de privacidade.
3. **Selecionar atividades elegíveis:** cumprir obrigações, procurar trabalho, viajar dentro de rotas possíveis, visitar organização, negociar relações, seguir missão pessoal; não fabricar vitórias/saques/bens.
4. **Aplicar níveis de relevância:** se próximo, avaliar acontecimentos concretos; se distante, agrupar evolução em janelas e checkpoints; se dormente, atualizar apenas na reativação autorizada.
5. **Conservar recursos e cronologia:** não gastar/gerar recursos arbitrariamente; verificar época, deslocamento, facções e relevância dos eventos canônicos.
6. **Classificar risco:** eventos críticos (morte permanente, prisão duradoura, mudança histórica, posse de item único etc.) aguardam política explícita. Não narrar como ocorrido antes de autorização/observação suficiente.
7. **Publicar conhecimento legitimamente:** rumores e relatos com trajetórias sociais/geográficas, `FACT != BELIEF`; PCs ausentes não recebem segredos de graça.
8. **Propor reencontro:** localização, época, interesse do NPC, recursos e suporte de área/roteiro geram candidato, não aparição instantânea.
9. **Executar só quando validado:** ação do Action Gateway sob host, reconciliar com saída/entrada e bloquear duplicidade. Se indisponível, recuar para fallback narrativo sem prometer presença física.
10. **Registrar reaproximação ou recusa:** recrutamento depende do NPC, de suas obrigações, de possíveis reparações e das condições técnicas; confirmar `PARTY_MEMBER_JOINED` antes de atualizar status.

## 5. Fluxo macro/micro

```text
Host PARTY_MEMBER_REMOVED --confirmed--> Snapshot pós-party
                                 |             |
                           regras de objetivos  catálogos lore/tempo
                                 |             |
                             agenda hierárquica (ACTIVE/NEAR/DISTANT/DORMANT)
                                 |
                        logs / snapshots / conhecimento filtrado
                                 |
                       oportunidade plausível de reencontro
                                 |
                           preflight de lore + risco + motor
                                 |
                       ação tipada gateway --> recibo do host
                                 |
                falha/UNKNOWN: fallback    sucesso: reencontro confirmável
                                 |
                       re-recrutamento: proposta, aceite, preflight, host
```

## 6. Companheiros canônicos e coexistência com BG2:EE

- Antes de qualquer modificação, catalogar por NPC: nome e recurso, diálogos e scripts após dismissal, local de espera, incompatibilidades, romances, quest flags, iniciações de conflitos, interações com demais companions e prioridade de mod.
- A identidade canônica não é reescrita pela simulação; eventos originais e sua cronologia prevalecem como baseline até que exista divergência legítima confirmada. O estado de campanha é *overlay*, não substituição silenciosa de scripts.
- Evitar que um NPC em roteiro original de espera seja gerado também em outra região pela simulação. Necessário reconciliação entre `native_location` e `projected_location` antes da materialização.
- Interações nativas (ex.: possibilidade ou proibição de voltar ao grupo) não devem ser sobrescritas sem inventário de script e política de compatibilidade formal.
- Em conteúdo EET/IWD/NWNForBG, a regra continua, mas nenhuma adaptação de NPC particular é presumida testada.
- Compatibilidade detalhada entre eventos originais e gerados será objeto da **DEC-050**, sem confundir sua pendência com rejeição da DEC-049.

## 7. Reencontros, negociações e possíveis re-recrutamentos

**Reencontro proposto:** requer horário/região/local plausíveis, disposição do NPC, existência/compatibilidade do recurso em build, consentimentos pertinentes, pré-condições do Action Gateway, ausência de outra instância e estado mecânico reconciliado.

**Recrutamento proposto:** verificar reações ao histórico da ruptura, promessas, novas afiliações, responsabilidade do NPC com terceiros, vagas na party e scripts originais. O jogador pode pedir, o NPC pode negar; decisão textual não concede capacidades mecânicas.

**Privacidade e percepção:** NPC pode lembrar das ações que presenciou; não recebe conhecimento dos históricos secretos dos jogadores por ter saído. O grupo pode ouvir rumores de suas atividades — cada rumor retém fonte, rota e confiança, sem ser convertido automaticamente em fato.

## 8. Falhas e fallback

| Situação | Resposta segura |
|---|---|
| Saída de party pendente/incerta | não iniciar agenda offscreen confirmada; reconciliar |
| NPC aparece em save em local diferente da projeção | host prevalece para posição; suspender materialização e investigar |
| Dois eventos tentam mover/recrutar o mesmo NPC | lock/revisão, rejeitar segundo, não duplicar |
| Evento crítico sem autorização | aguardar; não registrar como acontecido |
| Caminho físico desconhecido/área ausente | propor história contextual, sem declarar viagem física realizada |
| NPC canônico conflita com quest ou romance | gate de compatibilidade; não sobrescrever scripts |
| Jogadores reencontram NPC mas não desejam recrutá-lo | registrar encontro e resposta; não forçar party join |
| Falha de receipt ou desconexão no recrutamento | `UNCERTAIN` e conciliação com host, sem retentativa cega |
| Replay após save/load | processamento idempotente por evento/intervalo/versão |
| Modo Original | não observar ou modificar estado do Living World |

## 9. Testes candidatos de aceitação (não executados)

| ID | Cenário | Critério futuro |
|---|---|---|
| POST-T01 | NPC expressa intenção de deixar a party | não migra antes da remoção confirmada |
| POST-T02 | Remoção em host confirmada | um único snapshot pós-party |
| POST-T03 | Recibo de saída `UNCERTAIN` | sem deslocamento nem spawn adicional |
| POST-T04 | NPC perto e relevante | atividade detalhada por eventos, sem IA por tick |
| POST-T05 | NPC distante | evolução em lote/agenda agregada com custo limitado |
| POST-T06 | NPC dormente | checkpoint preservado, sem ações não autorizadas |
| POST-T07 | Relógio `FROZEN` | ausência de avanço fictício |
| POST-T08 | Relógio `PARTIAL/REALTIME` | catch-up dentro do orçamento, determinístico |
| POST-T09 | Destino exige viagem impossível | proposta bloqueada por cronologia/rota |
| POST-T10 | NPC tem afiliação nova | entidade e época consistentes com cânone e histórico |
| POST-T11 | Rumor falso sobre localização | crença não vira posição confirmada |
| POST-T12 | Evento offscreen propõe morte do NPC | bloqueado pela política HIGH sem autorização |
| POST-T13 | Jogadores entram na região do NPC | candidato de encontro sem spawn duplicado |
| POST-T14 | NPC em quest nativa/romance incompatível | sistema não altera flags/roteiros sem gate |
| POST-T15 | Convite para regressar à party | NPC pode aceitar ou recusar contextualmente |
| POST-T16 | Proposta textual de retorno sem receipt | não passa a `IN_PARTY_CONFIRMED` |
| POST-T17 | Recrutamento confirmado pelo host | agenda offscreen cessa sem duplicidade |
| POST-T18 | Recarregar save/reconectar | identidade, afiliações, local e logs coerentes |
| POST-T19 | Multiplayer com dois clientes | evitar divergência e múltiplas instâncias do mesmo NPC |
| POST-T20 | Modo Original | comportamentos, recursos e saves originais intactos |

## 10. Riscos, SPECS e POCs pendentes

- **Risco de duplicidade espacial:** NPC nativo presente em mapa/quest e projeção do simulador; resolver host-vs-projeção antes de materializar.
- **Risco de causalidade:** mundo atribuir ganho, perda, ferimento, morte ou afiliação a NPC sem fato legítimo nem autorização.
- **Risco de lore:** companheiro histórico ter disponibilidade ou comportamento incompatível com época/romance ou roteiro original.
- **Risco de multiplayer:** host e clientes divergem sobre party/posição/sprites/scripts; testar baseline BG2:EE antes de mods.
- **Risco de performance:** milhares de NPCs com simulação individual; conter por níveis, caches, prioridades e lotes.
- **Pendência DEC-050:** resolver precedência e conflitos entre os roteiros originais do motor/mods e a narrativa autônoma do Infinity AI.
- **Gates futuros:** inventário do cenário e versões, testes read-only, integração offline segura, coop 2 clientes, save/load, reconciliação em `UNCERTAIN`, preservação de Original.

**O desenho é conceitual. Nenhum NPC foi movimentado, recrutado ou gerado no motor nesta etapa.**

## Atualização posterior — DEC-050 aprovada (Discovery v4.6)

A conciliação com conteúdos originais deixou de ser política em aberto: a DEC-050 (opção C, ADR-0045, documento técnico 50) exige **inventário/observação por build, prevenção de colisões com scripts, quests, banters e romances, e preflight determinístico**. Para NPC em vida externa, nunca avançar presença física, disponibilidade de recrutamento ou missão original apenas por projeção narrativa. Quando houver conflito, adaptar, adiar ou bloquear; divergência causal requer autorização e suporte técnico. O alcance real das flags/hook permanece não testado.

## Integração DEC-064/C — aprendizado e crenças sem onisciência (v6.0)

Companheiro ausente só adquire notícia durante seu percurso se houver contato/tempo/canal conforme DEC-029 e DEC-064/C. Ao reencontrar jogadores, seu conhecimento não se sincroniza automaticamente com o catálogo nem com o estado mental do grupo. Memórias e crenças preservam origem e branch; mudanças de comportamento são validadas, sem presumir observabilidade mecânica nativa.


### Continuidade de memória durante ausência — DEC-065/C (Discovery v6.1)

Para reencontros, recuperar âncoras e episódios relevantes das interações anteriores. Ausência geográfica não autoriza conhecimento de fatos não transmitidos; evolução distante deve registrar eventos legítimos e fontes. Quando entidade de engine mudar de ID/spawn, não associar memória sem correspondência validada (DEC-066 pendente). Sem afirmação de hooks disponíveis.

### Integração DEC-066/C — reencontros com identidade verificada (v6.2)

Em reencontro com companion fora da party, a continuidade é proposta pela trajetória verificada e reconciliada com nova observação runtime. Mesmo nome/CRE em área distinta ou spawn após load não prova ser o mesmo NPC. Somente `VERIFIED` permite recuperar episódios, promessas e relacionamentos DEC-064/065; `AMBIGUOUS` ou build incompatível deixa o reencontro personalizado pendente. Não afirmar suporte de hook de deslocamento/reaparecimento sem POC.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

A DEC-067 permite individualização seletiva de figurantes com eventos confirmados; vida fora de cena segue níveis DEC-021 e limites DEC-056. O reencontro exige identidade DEC-066, não nome/sprite iguais. Detalhamento de hibernação aguarda DEC-068.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

DEC-068 detalha gestão de atividade do NPC separado do grupo: identidade e relações persistem, rotina fora de cena pode ser em lotes ou dormência, encontro físico depende do host/observação e de provas por build. O itinerário entre áreas permanece assunto DEC-069. Não prometer NPC autônomo fisicamente sempre presente.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: deslocamentos e reencontros de ex-companheiros usam itinerário regional e identidade DEC-066; chegada narrativa não autoriza aparição física nem recrutamento sem host/scripts.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070: ex-companheiro em viagem mantém identidade, memórias e itinerário, mas não pode ser morto, capturado ou ter equipamento alterado por resolução fictícia de ataque fora de cena.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Uma aparição local de companheiro/NPC relacionada a evento de viagem DEC-071 deve usar identidade DEC-066 verificada, presença host e reserva única. Sem POC para inserir personagem na área, diálogo narrativo permitido ou evento pendente; não criar clone nem reatribuir memória.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Companheiro poderá ser conhecido por persona diferente e ser reencontrado; restauração da identidade lógica DEC-066 não torna seus pseudônimos automaticamente conhecidos por todos.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Identidade de informante NPC deve sobreviver à hibernação e não se tornar pública quando o personagem é reencontrado; memória e risco permanecem separados.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

NPC protegido continua vivendo entre sessões; encontros futuros respeitam plano, disponibilidade, percurso e memória, não servindo como spawn instantâneo.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Companheiro que deixa party mantém identidade e vínculos persistentes; reencontro não presume que guildas conheçam sua vida secreta ou que engine tenha operado saída.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Recrutamento de companion em party e contratação como informante são contratos distintos; a segunda não altera controle tático ou vagas da party.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

NPC recrutável ou reencontrado pode lembrar boato recebido, sem acesso a relatórios futuros nem multiplicação de fontes por múltiplas personas.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-091/C — Discovery v8.7

NPC persistente precisa localização, acesso e disponibilidade confirmados para aceitar participação em plano; não reaproveitar CRE aleatória.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

NPC persistente pode estar fora de cena; mudança de plano consulta posição e disponibilidade, não convoca uma CRE instantânea.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Reencontros/viagens usam identidade, posição e janela DR, de modo que uma instância reutilizada ou nome coincidente não gere presença em duas missões.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Se NPC aparece como recurso em duas operações, resolver identidade persistente e presença; pseudônimo não replica ator e lease expirado não o teleporta.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Recrutamentos e desencontros de companions exigem observação/receipts reais; o NPC não pode ser duplicado.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Agenda de companion fora da party não usa spoilers internos do motor como conhecimento factual do NPC.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** A quest milestone observed on the host is NOT NPC knowledge, player consent, authorship, rumor or dialogue entitlement. A curated, minimal safe milestone must pass ACL/spoiler checks and be delivered causally before appearing in dialogue or memory; no LLM inference from raw flags. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para reencontros podem trazer notícias tardias conforme rota e tempo DR, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para reencontro e notícias tardias podem mudar relação com atraso, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
