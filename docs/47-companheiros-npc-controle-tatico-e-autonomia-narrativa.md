# Companheiros NPCs — controle tático, agência narrativa e integração segura (DEC-047)

**Infinity AI Discovery v4.3 — desenho técnico candidato, não SPEC nem implementação.**  
**Escolha aprovada:** DEC-047 **C** — jogador comanda taticamente o companheiro; o NPC mantém identidade, motivações, memória, opiniões, limites e agência narrativa.  
**ADR:** `decisions/ADR-0042-controle-tatico-com-autonomia-narrativa-dos-companheiros-npc.md`.

## 1. Objetivo e fronteiras

O jogo continua usando as mecânicas nativas de party/exploração/combate; uma camada externa interpreta **relações, personalidade e consequências** de companheiros, especialmente os canônicos do BG2:EE. O mecanismo não deve gerar magias/ações/quest flags mecânicos em silêncio. O controle compartilhado de PCs (DEC-045/046) não se confunde com o controle tático de companheiros NPCs.

| Aspecto | Player Character (PC) | Companion NPC |
|---|---|---|
| Identidade/histórico | Autor e jogador titular (DEC-004/019/020) | Fontes do mundo, personagem canônico curado ou conteúdo validado |
| Controle durante combate | Titular ou humano temporário autorizado (DEC-045/046) | Jogador com controle tático da party dentro do motor |
| Decisões pessoais | Exclusivamente jogador titular, sujeito às regras de delegação | Objetivos/valores próprios interpretados por regras e narrativa |
| Conhecimento | ACL e observações legitimadas do PC | Memória/observações legítimas do NPC, sem onisciência |
| Consequências mecânicas | Host/Action Gateway | Host/Action Gateway, não apenas texto do LLM |
| Quests e relações | PSD/CSD com agência do jogador | Propostas relacionadas ao NPC, sem forçar escolhas do grupo |

## 2. Camadas conceituais (sem impor arquitetura de processos)

1. **Inventário e Curadoria Canônica:** dados de NPC, período de Forgotten Realms, fontes oficiais/mods, restrições de classe, fatos fixados e condições de aparição. O catálogo completo ainda precisa ser elaborado.
2. **NPC Identity Profile:** valores, alinhamento inicial do NPC e eventuais mudanças justificadas, prioridades, lealdades, vínculos, limites, conflitos pessoais, tabus, preferências de diálogo e proveniência de cada afirmação.
3. **NPC Knowledge View:** filtro obrigatório por fatos observados, relatos com fonte, rumores com credibilidade, tempo/região, privacidade, estado de campanha e divergências históricas. Executar antes de qualquer LLM.
4. **NPC Relationship State:** amizade, confiança, temor, hostilidade, respeito, promessas e relações com PCs/grupo/facções, sem confundir com a métrica nativa de reputação do BG2:EE.
5. **NPC Narrative Policy Evaluator:** regras determinísticas verificam elegibilidade, risco, gravidade/recorrência de eventos, compatibilidade com valores e consequências permitidas. Gera uma `reaction_proposal`, nunca um efeito mecânico irrevogável.
6. **Dialogue & Story Assistant:** IA local opcional formula falas e variações aderentes ao caráter e evidências, observando rate limits, orçamento e segurança de dados; fallback para conteúdo validado.
7. **Encounter/Party Bridge:** quando autorizado, traduz uma proposta em operação tipada do gateway; aguarda evidência/recibo do host. Suporte a recusa mecânica, saída voluntária, recrutamento e estados de combate **não foi demonstrado**.
8. **Event Log & Projection:** persiste reações, vínculos, decisões confirmadas, deliberações pendentes e reconciliações com versão e idempotência.

## 3. Exemplo conceitual — companhia de princípios rígidos

- **Evidência:** um NPC testemunha os jogadores atacarem moradores não hostis; o motor confirma efeitos, mas o NPC conhece apenas o que realmente presenciou, não as motivações privadas dos jogadores.
- **Avaliação:** regras observam histórico de atos, contexto, falta de certeza sobre intenções e os valores do NPC. Evento ambíguo não força conclusão moral automática.
- **Narrativa:** o NPC pode pedir explicações, advertir, rejeitar futuras ações ou propor compensação; seus diálogos devem respeitar personalidade e conhecimento.
- **Mecânica:** se uma regra futura validada autorizar uma saída de party, o gateway solicita operação tipada e confirma no host. Sem hook confiável, limitar-se a reação narrativa ou à lógica já existente no jogo.
- **Persistência:** a reação e as evidências têm IDs próprios; save/load não deve provocar o mesmo protesto ou despedida novamente por engano.

## 4. Modelo mínimo de dados candidato (nomes NÃO vinculantes)

```text
NPCIdentity { campaign_id, npc_id, canonical_identity_ref, era_range, location_scope,
              values, goals, loyalties, red_lines, source_provenance, version }
NPCBelief { npc_id, fact_or_rumor_id, source, observed_at, believed_at, confidence,
            access_policy, campaign_id }
NPCRelationship { npc_id, target_type, target_id, dimensions, timestamps, provenance }
NPCReactionProposal { proposal_id, npc_id, trigger_event_ids, evidence_ids, severity,
                      narrative_options, mechanical_action_candidate, policy_version,
                      risk_level, expires_at }
NPCActionReceipt { proposal_id, host_event_id, operation, status, engine_state_hash,
                   assignment_epoch, confirmed_at }
```

`values`, `severity` e `dimensions` não constituem ainda uma tabela numérica fechada; definições e limiares são SPECS posteriores. Não modelar uma escala numérica única como substituta de crenças, vínculos e eventos do mundo.

## 5. Pipeline candidato de avaliação

```text
Host observa evento -> normalização e deduplicação -> valida proveniência e campanha
  -> filtra visão/ACL de cada NPC -> policy evaluator determinístico
  -> (se necessário) IA local redige possíveis falas em contexto filtrado
  -> marca reação narrativa elegível, sem atribuir escolhas aos PCs
  -> se houver efeito mecânico: Action Gateway permite/negar/proteger HIGH
  -> host confirma ou estado UNCERTAIN solicita reconciliação
  -> ledger + snapshots atualizam memória, relações e flags autorizadas
```

**Gates importantes:** NPC que não observou não deve saber; NPC em local distante não deve reagir instantaneamente; propostas mecânicas não devem escapar do gateway; o modo Original permanece intocado.

## 6. Relação com decisões aprovadas

- **DEC-014/021/022:** LLM apenas sob demanda; estados ativos/próximos/distantes determinam granularidade, relógio determina prazos e catch-up.
- **DEC-008/009/023/024/025/034:** proteger época/cânone, desenvolvimento de arcos originais e divergências causais, sem cópia irrestrita de scripts.
- **DEC-011/012/027:** host, gateway, gradação de risco e comprovante para qualquer mudança mecânica.
- **DEC-019/028/029:** ACL, conhecimento legítimo, rumores, memória e proveniência antes do modelo.
- **DEC-030/035/036/037:** reputação, crenças e alinhamento não são sinônimos; eventual mecânica de alinhamento ainda requer validação.
- **DEC-031/032/033:** objetivos de facção e conflitos podem informar escolhas do NPC, mas não substituir seus vínculos ou justificativa pessoal.
- **DEC-039/040/041:** PSD/CSD integram missões NPC ao grupo, respeitando escolhas e segredos de cada PC.
- **DEC-042/043/045/046:** controlar um NPC não equivale a consentimento de PC ou permissão de PvP; separar delegation grants de PC e autonomia de NPC.

## 7. Riscos e mitigação candidata

| ID | Risco | Mitigação/validação futura |
|---|---|---|
| R-NPC-01 | Reação aleatória ou contraditória à personalidade | Curadoria canônica, regras, registros de evidências e testes de regressão |
| R-NPC-02 | NPC onisciente descobre segredos de jogador | Filtrar conhecimento por NPC antes do LLM e testar vazamentos |
| R-NPC-03 | Duas IAs/scripts diferentes controlam o mesmo companheiro | Inventariar scripts nativos/mods; uma proposta por autoridade, recibos |
| R-NPC-04 | Saída automática de party causa estado impossível | Gate de integração, ação tipada, ponto seguro, recibo do host |
| R-NPC-05 | IA altera flags de romance/missão canônica | Bloquear sem SPEC por script/flag e testes por época/mod |
| R-NPC-06 | Desacordo narrativo tratado falsamente como veto mecânico | Distinguir intenção, protesto e bloqueio efetivo comprovado |
| R-NPC-07 | Reações repetem a cada load/reconexão | Event IDs, projeção persistente, deduplicação e idempotência |
| R-NPC-08 | NPC reagir a ato distante ou não testemunhado | Grafo social, relato/rumor com origem, relógio e difusão |
| R-NPC-09 | Companion monopoliza protagonismo | CSD, limites de interrupção e prioridades narrativas |
| R-NPC-10 | Efeito irreversível sem autorização específica | DEC-027/034, consentimento e regras da campanha |
| R-NPC-11 | LLM por companheiro a cada tick gera latência/custo | Evento significativo, budget, batching e fallback determinístico |
| R-NPC-12 | EET/IWD/NWNForBG altera conteúdo e gatilhos nativos | Baseline, modlist reprodutível, testes progressivos e flags isoladas |

## 8. Vinte testes candidatos de aceite futuro

| ID | Cenário e resultado esperado |
|---|---|
| NPC-T01 | Companheiro recrutado permanece movimentável e comandável em combate no baseline existente. |
| NPC-T02 | O mesmo NPC comenta uma ação testemunhada sem alterar habilidades/inventário. |
| NPC-T03 | Uma ação não testemunhada não gera reação sem mensagem/rumor legítimo. |
| NPC-T04 | Segredo privado de PC não entra no prompt ou memória do NPC sem fonte. |
| NPC-T05 | Evento moral ambíguo não gera punição/saída automática. |
| NPC-T06 | Reação a padrão recorrente não contradiz valores e histórico canônico inventariado. |
| NPC-T07 | Aprovação ou protesto não altera automaticamente reputação global BG2:EE. |
| NPC-T08 | Diálogo gerado não afirma uma confissão ou decisão de outro PC. |
| NPC-T09 | Recrutar/dispensar exige suporte mecânico comprovado, operação tipada e host receipt. |
| NPC-T10 | Sem hook de saída seguro, fallback narrativo é explícito e não corrompe party. |
| NPC-T11 | Fala NPC na coop é consistente para host e clientes, conforme UX a ser especificada. |
| NPC-T12 | Save/load reproduz estado relacional sem repetir eventos e propostas. |
| NPC-T13 | Reação de romance/banter nativo não dispara uma segunda vez por módulo externo. |
| NPC-T14 | NPC canônico da época divergente mantém fatos confirmados e anota exceções causais. |
| NPC-T15 | IA local indisponível permite fallback de conteúdo roteirizado/regras. |
| NPC-T16 | Duas pessoas controlando slots diferentes não duplicam comando/proposta de NPC. |
| NPC-T17 | NPC fora da região ativa usa simulação agregada, sem inferência contínua. |
| NPC-T18 | NPC não causa PvP/morte/alteração HIGH sem autorizações correspondentes. |
| NPC-T19 | Uma nova build de mod não reutiliza flags incompatíveis sem diagnóstico. |
| NPC-T20 | Modo Original não recebe eventos, reações ou memórias extras do Living World. |

**Critérios exatos, ferramentas e versões de teste serão definidos em SPECS.**

## 9. Sequência de provas técnicas

- **G0 — Inventário:** BG2:EE vanilla/EEex, NPCs originais, triggers, diálogos, scripts, reputação e banters/romances existentes; identificar riscos de conflito.
- **G1 — Read-only:** observar fatos e calcular reação em logs externos sem alterar o jogo; validar sigilo, cronologia e memória.
- **G2 — Narrativo seguro:** propostas de diálogo sem alterar flags; medir consistência, localidade e ausência de replays.
- **G3 — Mecânica isolada:** somente quando previsto em SPEC, testar ações tipadas de party em host + dois clientes, reinício/save/load e fallback.
- **G4 — Expansão por mods:** EET, IWD e NWNForBG por build, revalidando hooks/roteiros e evitando assumir compatibilidade de conteúdo.

## 10. Próxima decisão arquitetural — DEC-048

Definir o **protocolo de limites e desacordo dos companheiros**: advertência, explicação, negociação, recusa, ruptura e eventual saída da party; estabelecer se é roteirizado, contextual com regras e estados graduais ou entregue livremente a IA. O apoio da IA em diálogos não equivale a sua autoridade mecânica.


## Continuidade após saída — DEC-049 (aprovada na v4.5)

A autonomia narrativa aprovada na DEC-047 **não termina quando o NPC deixa a equipe**. Após saída mecânica confirmada, a DEC-049 estabelece vida externa persistente, simulação hierárquica, vínculos/facções, objetivos e possibilidade de reencontro. A antiga expressão “aguardar a DEC-049” nestas notas é histórica. Não confundir intenção de sair com remoção efetiva; veja ADR-0044 e documento 49.

## Integração de companions canônicos com eventos dinâmicos — DEC-050 (v4.6)

O controle tático e autonomia narrativa da DEC-047 não dão à IA propriedade sobre scripts/flags do NPC. Novos diálogos e trajetórias devem passar pela política de conciliação da DEC-050/ADR-0045, protegendo quests, romances, banters e compromissos originais. Mudanças de estado mecânico exigem gateway/host, e modificações de build exigem revalidação; propostas incompatíveis poderão ser adaptadas, adiadas ou bloqueadas.


### Memória persistente de companheiros — DEC-065/C (Discovery v6.1)

Companheiros preservam episódios e vínculos essenciais mesmo fora da party; recolher apenas lembranças pertinentes ao reencontro, sem acesso irrestrito ao histórico dos PCs. Consolidação contextual não confere ao NPC percepção de acontecimentos que não presenciou. Identidade física no BG2:EE continua pendente DEC-066 e testes.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

Companheiros únicos curados são prioritários na DEC-067, mas persistência narrativa não muda controle tático, agendas nativas ou scripts de romances; host e inventário da build governam.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

Ao sair de cena, companion mantém identidade, memória e compromissos. DEC-068 ajusta atividade; não permite alterar party-state, comportamento tático ou recrutamento sem receipt host e scripts compatíveis. ADR-0063/doc. 68.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

NPCs companheiros podem receber reconhecimento por ações comprovadas, sem atribuir ao jogador uma ação autônoma do NPC nem inventar telemetria.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração DEC-084/C — Discovery v8.0

Companheiro NPC pode aceitar ou recusar escolta/abrigo com agência compatível; a IA não o teleporta nem garante proteção física.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Companheiros NPC podem suspeitar e propor engano dentro de seus princípios, recursos e autonomia, mas não se tornam mentirosos ou traidores arbitrários por LLM.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Companheiro NPC mantém personalidade, valores e agência narrativa. Lealdades podem estar em tensão, mas controle tático de party não autoriza alterações mecânicas improvisadas.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Companheiro NPC pode recusar oferta de espionagem conforme valores e limites, sem ser forçado mecanicamente a desertar ou ingressar numa guilda.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Companheiro NPC pode interpretar informe à luz de sua personalidade, mas a crença do NPC não corrige o `WorldFact` privado nem altera controle mecânico.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Companheiro só interpreta conteúdo realmente recebido por canais autorizados; memória e autonomia não autorizam leitura direta do dossiê confidencial do host.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Companheiro NPC pode discordar ou recusar participação em proposta, conforme sua autonomia e personalidade; texto não força ação tática.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Companheiro NPC pode recusar objetivo revisado por autonomia, personalidade e recursos; pausa/aborto não apagam vínculos nem transformam recusa em traição.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Mesmo companion persistente não pode realizar ações físicas incompatíveis em duas operações simultâneas. Autonomia e limitações da engine permanecem vigentes.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

NPC singular e persistente não pode ser alocado em duas tarefas incompatíveis; liberação lógica não prova disponibilidade física nem altera autonomia do companheiro.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

A tática de companions no motor não concede poder ao diretor narrativo para alterar script/quest/romance.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Companions têm autonomia narrativa, mas não devem receber spoilers de seus próprios scripts por sondagem indiscriminada.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** A quest milestone observed on the host is NOT NPC knowledge, player consent, authorship, rumor or dialogue entitlement. A curated, minimal safe milestone must pass ACL/spoiler checks and be delivered causally before appearing in dialogue or memory; no LLM inference from raw flags. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

A DEC-102/C trata divergências entre milestone validado do host e projeção derivada do Living World: exigir mapeamento DEC-101, observação DEC-100, epoch/branch e receipts, e preservar o host, facts ledger e conhecimento dos NPCs. Somente proposta de revisão CAS/autorizada; detalhes em ADR-0097/doc. 102. **Sem POC mecânica.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para autonomia narrativa de companions dentro de valores e relações curados, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para valores e personalidade de companion não são substituídos por score, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
