# Propagação social, geográfica e temporal de notícias — desenho técnico preliminar

**Infinity AI — Discovery v2.6** · **DEC-029 / ADR-0024 — aprovada, opção B**  
**Estado:** modelo candidato para SPECS; **não implementado**, sem métricas, banco ou testes de BG2:EE realizados.

## Premissa

Rumores e notícias são eventos sociais modelados por **relações, canais, tempo de campanha e elegibilidade**. Não são atributos globais distribuídos instantaneamente; indivíduos só podem usar a informação atribuída a eles por fatos testemunhados, comunicação ou descoberta validada (DEC-028). A base de memória é compartilhada fisicamente/lógicamente, mas seu conteúdo não é automaticamente conhecido por todos.

## Estruturas lógicas propostas

```text
Campaign canonical event log / confirmed outcomes
                   |
                   v
   Claim / news item / testimony (classified, sourced)
                   |
                   v
  Holder knowledge + disclosure permissions (DEC-028)
                   |
                   v
  Rule-based propagation planner: channel / social graph / travel / time
                   |
                   v
   Pending Transmission Queue (versioned, idempotent)
                   |
                   v
  Receiver authorization + provenance validation
                   |
                   v
    Recipient belief / memory projection (not canonical rewrite)
                   |
                   v
   Dialogue context (filtered) or future narrative candidate
                   |
                   v
 Publication policy (DEC-027) / gateway (DEC-012) / host receipts when needed
```

## Tipos de informação que NÃO devem ser confundidos

| Tipo | Exemplo | Como persistir |
|---|---|---|
| `WORLD_FACT` | A batalha ocorreu, confirmação do host | Evento autoritativo com data/proveniência |
| `OBSERVATION` | Guarda presenciou o combate | Vínculo testemunha→evento validado |
| `REPORT` | Mercador ouviu o guarda | Mensagem proveniente da fonte e horário |
| `RUMOR` | Bardo ouviu relato exagerado | Variante de alegação, confiança e origem |
| `SUSPICION` | Espião suspeita de uma identidade | Crença não confirmada, acesso restringido |
| `SECRET` | História reservada do personagem | Restrição de divulgação conforme DEC-019/028; negar por padrão |

## Planificador por regras (pseudocódigo conceitual, não para execução)

```text
on_confirmed_event(event):
  add_world_fact(event)
  for each authorized_witness(event):
    attribute_knowledge(witness, event, source=OBSERVED)

simulate_information_window(campaign, from_dr, to_dr, seed, budget):
  assert window_allowed_by_clock_policy(campaign, from_dr, to_dr)
  for transmission in eligible_queued_transmissions(campaign, window, budget):
    if already_processed(transmission.idempotency_key): continue
    if not source_holder_knows(transmission.claim): continue
    if not legitimate_channel_and_contact(transmission): continue
    if not sender_may_disclose(transmission.claim, transmission.recipient): continue
    if not recipient_may_receive(transmission.claim, transmission.context): continue
    belief = create_belief_view(transmission.claim, provenance=transmission.chain)
    persist_once(transmission.key, belief)
    maybe_queue_forwarding_via_rules(belief, seed, budget)
  checkpoint_window_without_duplicating()
```

**Atenção:** a função `recipient_may_receive` não pressupõe que o receptor precisa já conhecer a informação; ela verifica se a divulgação é autorizada pelas políticas, se a aquisição é plausível e se a informação pode ser registrada em sua memória. Conhecimento prévio não é requisito para aprender algo novo.

## Regras de transmissão a especificar posteriormente

- **Plausibilidade de contato:** relação social documentada, mesma cena/testemunho, proximidade, rota comercial, mensageiro, organização, carta ou canal reconhecido pela configuração da campanha.
- **Janelas de disponibilidade:** personagem presente, canal funcional, região acessível, notícia ainda pertinente, tempo do mundo compatível.
- **Interesse e propensão:** papel social e interesses da fonte; tendência a compartilhar vs guardar informação; confiabilidade e relação entre interlocutores. Valores numéricos ainda indefinidos.
- **Transporte:** viagens e mensagens não saltam instantaneamente entre cidades sem canal ou magia/evento autorizado que justifique isso.
- **Ciclos e memória:** evitar loop infinito na mesma rota; duplicação sem nova informação não é automaticamente uma nova transmissão relevante.
- **Lições de informações contraditórias:** retenção de crenças rivais; investigação e correção exigem evidência, não substituição automática do fato.
- **Confidencialidade:** usar classificação por fato e regras de redistribuição; proibir transferência de segredos do jogador por simples proximidade; permitir apenas eventos e permissões definidos futuramente.

## Modos de simulação e tempo

| Regime | Trabalho esperado | Restrições |
|---|---|---|
| `ACTIVE` | Eventos de conversa e testemunhos na sessão, materializados quando confirmados | Não atribuir testemunho se cena/evento não foi confirmado |
| `NEAR` | Agendas simplificadas e transferências sobre contatos plausíveis | Sem pathfinding detalhado fora da área |
| `DISTANT` | Lotes pequenos/bounded, projeções por grupos/facções quando possível | Sem LLM contínuo; seeds/checkpoints; limites de largura |
| `DORMANT` | Não processar até ficar relevante | Reidratação segura e limitada quando necessário |

Na campanha `FROZEN`, o tempo externo real não autoriza difusão. Em `PARTIAL` e `REALTIME`, respeitar os limites de catch-up, checkpoints e proteção de eventos críticos definidos pela DEC-022. Não definir nesta decisão dias de deslocamento, percentuais ou TTLs.

## Segurança, autorização e interpretação

1. O próprio conteúdo de rumor, diálogo ou livro é dado não confiável, não instrução ao modelo/orquestrador.
2. O filtro DEC-028 executa *antes* de entregar contexto à IA, e o acesso de narrador não passa automaticamente para NPC.
3. Uma revelação de segredo é evento de conhecimento, não licença para emissão pública automática; ainda falta política detalhada de divulgação autorizada.
4. Propagação nunca concede poderes de escrita de motor; ações decorrentes passam pelo DEC-012 e recibo do host.
5. O agendador não pode promover um rumor a `WORLD_FACT` por popularidade; um boato replicado cem vezes continua boato.
6. Eventos do canon respeitam data DR, divergências da campanha, procedência e janela de divulgação plausível.
7. Falha, estado inconsistente ou falta de fonte deve bloquear transmissão protegida e evitar falsa confirmação.
8. Caches, logs, embeddings e resumos têm isolamento por campanha, identidade, escopo de permissão e versão.

## Testes candidatos (16; não executados)

| ID | Caso | Comportamento esperado |
|---|---|---|
| NEWS-01 | Guarda testemunha batalha validada | Recebe conhecimento com fonte e horário |
| NEWS-02 | NPC em cidade distante sem contato | Não recebe fato instantaneamente |
| NEWS-03 | Mercador viaja e conversa após janela autorizada | Transferência agendada por regras |
| NEWS-04 | Relógio congelado fora da sessão | Sem avanço indevido |
| NEWS-05 | Mesmo lote `DISTANT` repetido | Sem duplicações, comportamento determinístico por regras |
| NEWS-06 | Jogador marca histórico secreto | Não entra automaticamente na rede social |
| NEWS-07 | Narrador conhece segredo, guarda não | Sem vazamento por contexto privilegiado |
| NEWS-08 | Relato falso e testemunho verdadeiro | Registros distintos; canon preservado |
| NEWS-09 | Espião possui suspeita fraca | Não fala como se fosse fato comprovado |
| NEWS-10 | Duas fontes contraditórias | O destinatário guarda origem separada |
| NEWS-11 | Evento de Forgotten Realms ainda futuro | Sem divulgação retroativa |
| NEWS-12 | Replay/restauração de save | Nenhum conhecimento/evento duplicado |
| NEWS-13 | Dois mundos/campanhas paralelos | Nenhum vazamento lateral |
| NEWS-14 | Rumor induz ação `HIGH` | Não aprovar transformação mecânica ou canônica automaticamente |
| NEWS-15 | Injeção de prompt em carta/documento | Não altera ACL, canon nem gateway |
| NEWS-16 | Dois clientes compartilham sessão | Mesma cadeia autoritativa de eventos; falha de sync bloqueia gate |

## Métricas candidatas (não definidas)

- Transmissões por janela e por canal; razão de duplicações rejeitadas; latência de consultas NPC; proporção de mensagens bloqueadas por origem ou classificação; taxa de divergências host/cliente.
- Crescimento de log por campanha; memória e CPU; desempenho de catch-up após longa ausência; número de inferências LLM (idealmente zero para transmissão mecânica do rumor).
- Avaliar propagação em grandes populações por agregação/organizações para evitar simular conversa por conversa.

## Dependências e backlog

- **DEC-030 (próxima):** reputação e notoriedade (escores globais vs percepções regionais/sociais com crenças divergentes) — ainda não aprovada.
- DEC-018: snapshots/logs/replay e correções; DEC-006: modelos e privacidade; DEC-015: testes e condições técnicas de aceite.
- DEC-019/028: divulgação/consentimento e políticas de crenças; DEC-027: autoridade para consequências de alto impacto.
- Integração de jogo, EEex/bridge, dados de rotas e sincronização multiplayer não validados.

## Integração DEC-063/C — atualização de base não difunde notícias por magia (v5.9)

Adoção de novo *knowledge pack* por campanha é mudança na referência de conhecimento curado, não um evento social de difusão. Uma informação recém-publicada não deve ser aprendida instantaneamente por todos os NPCs nem reescrever boatos anteriores. Propagação continua temporal, regional, relacional e ACL-aware. Regras específicas para revisão de crenças/rumores individuais serão discutidas na DEC-064.

## Integração DEC-064/C — aprendizado e crenças sem onisciência (v6.0)

DEC-064/C especifica o efeito **subjetivo** de transmissão recebida sob DEC-029: registrar episódio uma vez, depois avaliar a evidência/contexto e produzir eventualmente nova revisão de crença. Receber não significa crer, e crer não torna o rumor fato. Rumores falsos são permitidos como perspectiva; fontes/contatos/tempo devem ser plausíveis e verificados. A publicação do lore DEC-062 ou troca de Knowledge Pack DEC-063 nunca difunde instantaneamente informações para todos os NPCs.


### Rumor antigo e memória individual — DEC-065/C (Discovery v6.1)

Rumor ouvido pode gerar episódio protegido ou trivial, e uma síntese só registra que NPC **ouviu/acreditou** segundo as evidências, não que a acusação é verdadeira. Reduzir recuperação de boato antigo não envia sua correção a ninguém nem o apaga automaticamente. DEC-064 rege revisão de crença e DEC-028/029 rege aquisição/propagação.

### Integração DEC-066/C — rumor não atravessa identidades ambíguas (v6.2)

Arestas de contato, testemunho e difusão referenciam identidade lógica NPC verificada e revisão de campanha, não somente nome ou objeto transitório. Se a observação runtime não corresponder com segurança, suspender atualização do grafo individual; não entregar notícia/segredo a homônimo ou respawn. Tempo, geografia, autoridade da fonte e ACL continuam vinculantes.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

Rumores só chegam a NPC offscreen segundo canais, contexto geográfico, relógio, propagação e lote autorizado; estar DORMANT não equivale a receber instantaneamente atualizações de Knowledge Pack. DEC-068/C mantém watermark e memória epistêmica sem retroinvenção.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: rumores de estrada requerem plausibilidade geográfica/temporal e canal social, sem fazer viagem/chegada proposta virar testemunho confirmado.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070 separa boatos de viajantes de incidentes confirmados. Propagação social não converte rumor de roubo ou emboscada em resultado mecânico; sujeitos só recebem notícia por canal/tempo/contexto autorizado.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Encontro apenas proposto não vira notícia objetiva. Somente efeito narrativo autorizado ou host-confirmed DEC-071 pode originar notícia/rumor com proveniência, timing e ACL; evitar que clientes múltiplos propaguem o mesmo fato duas vezes.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

DEC-074 conecta fatos confirmados pós-encontro à difusão DEC-029. Testemunhos e canais têm origem, ACL, tempo e geografia; alegações sem confirmação nunca viram prova de ocorrência. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Propagar percepções com testemunhas parciais, fontes e canais; falsos créditos são rumores atribuídos, não mudança de autoria factual. Respeitar ACL e cronologia.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Link de identidade pode circular como testemunho, suspeita ou relato; somente provas verificadas e política de divulgação autorizam consolidar reconhecimento de verdade. Uma guilda informada não informa instantaneamente o resto do mundo.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação e consentimento (Discovery v7.3; não implementada)

A DEC-077/C exige ancestralidade de fontes: relatos copiados de um mesmo rumor não corroboram independentemente um vínculo secreto. Difusão e credibilidade de rumor pertencem ao grafo social; revelação factual de uma identidade requer prova/gate separado e destinatário autorizado. Cânone permanece fisicamente particionado por ano DR; investigação só no overlay privado da campanha/ramo. ADR-0072 e documento técnico 77, 58 testes não executados.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Acusação e veredito DEC-078 podem circular como alegações/decisões de autoridade por canais, preservando fonte e recepção; não devem ser confundidos com fato do delito.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Pedidos oficiais DEC-079 e rumores de mandado são canais distintos; entrega com destinatário e data não garante reconhecimento. Mensagens não chegam ao passado nem a todos os territórios automaticamente.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Envio de revogação DEC-080 é mensagem com canal, rota e receipt distintos de emissão; NPC que ainda não a recebeu não passa a sabê-la. Origem documental pode ser falsificada como alegação, nunca prova automática.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

DEC-081 origina correções e pedidos de desculpa como notícias com fonte/público/canal/tempo; antiga acusação pode persistir nas crenças até comunicação efetiva.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Denúncias circulam como alegações com fonte e canal; nunca se tornam provas institucionais por repetição ou chegada a múltiplas guildas.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Informação sobre denúncias pode circular com fonte anônima e proveniência; identidade verdadeira não se propaga apenas porque fato ou boato é recebido.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Rumor de ameaça e notícia de realocação têm proveniência, canal e público; perseguidor só conhece destino se houver comunicação/descoberta legítima.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Rumores de escolta/abrigo possuem canais, tempo, fonte e grau de certeza; receptor não recebe detalhes fora do relatório, e testemunhos circulares não são provas independentes.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Rumor plantado é uma alegação de origem privada com cadeia de retransmissão e canais; repetição não cria fontes independentes nem certeza de autoria ou rota.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Notícias de deserção, infiltração ou traição seguem prova, emissor, canal e tempo; redes não replicam compromisso oculto por consulta global à base privada.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Contato e colaboração podem circular como notícias ou suspeitas conforme canal e tempo; o contrato privado não é conhecido automaticamente por facções externas.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Rumor retransmitido preserva origem A→B→C; quantidade de recontagens não valida verdade. Cada NPC sabe apenas o que o canal permitiu no tempo DR.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Compartilhar dossiê cria TransmissionEvent pelo canal autorizado; só destinatários que receberam view podem aprender seu conteúdo, com propagação secundária explícita e tempo DR.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Compartilhar plano/resultado requer canal e destinatário, tempo e proveniência; NPC/facção não aprende por existir proposta em ledger.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Rumores recebidos em tempos diferentes são avaliações de informação, não gatilhos WorldFact; replanejamento não atualiza simultaneamente crença de todas facções.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Aviso de operação pendente em scheduler não é notícia conhecida por NPC. A propagação exige evento, fonte e canal legítimo; não vazar planejamento ao compartilhar recurso.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Efeito indireto e rumor DEC-096 propostos exigem AppliedImpact/ConfirmedCampaignEvent e causalidade de canais/tempo; GLOBAL não concede onisciência de NPC.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Regras DEC-096 podem observar world-state autorizado, não ACL privada; existência de CanonEvent não transfere informação a NPC. Logs e LLM passam por audiência/ramo.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Trilhas de composição DEC-097/C podem conter origens privadas; filtrar ACL antes de logs, prompts e relatórios.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Observações e snapshots privados não são automaticamente visíveis a jogadores, modelos, clientes ou facções; ACL por branch e público.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Rumores e relatos não servem de prova de proprietário de instância; origem de informação difere de ownership mecânico.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

ACL por finalidade, audiência e tempo deve filtrar o próprio acesso aos probes e depois as projeções no contexto da LLM.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** A quest milestone observed on the host is NOT NPC knowledge, player consent, authorship, rumor or dialogue entitlement. A curated, minimal safe milestone must pass ACL/spoiler checks and be delivered causally before appearing in dialogue or memory; no LLM inference from raw flags. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Não transformar atualização de projeção DEC-102 em rumor: divulgação causal depende de evento próprio a decidir na DEC-103. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** a conclusão técnica de uma quest não concede automaticamente conhecimento ou crença a NPCs/facções. `QuestMilestoneAdmission` pode gerar proposta de notícia/reputação somente por regras, proveniência, tempo, geografia, visibilidade e ACL; notícia requer fonte/canal/delivery, e seus destinatários podem conhecer apenas versões parciais. Não expor identidades secretas, fontes protegidas ou raw flags por prompts/logs/dossiês. Ações mecânicas derivadas dependem de recibos host, sem atribuição presumida de PC. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **ACL e contexto**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para difusão causal de rumores e correções com receipts individuais, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para difusão causal da acusação e da correção são processos separados, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

ACL por parte, prova de cumprimento, anexos e prompts redigidos. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Divulgação de cláusulas e receipts exige ACL por titular e finalidade. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
