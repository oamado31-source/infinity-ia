# DEC-048 — Protocolo de desacordo, lealdade, negociação e ruptura dos companheiros NPCs

**Versão:** Discovery v4.4 · **Estado:** arquitetura candidata, não SPEC nem implementação · **ADR:** `decisions/ADR-0043-protocolo-contextual-de-desacordo-e-ruptura-dos-companheiros-npc.md`.

## 1. Objetivo e fronteiras

Tornar coerentes, persistentes e auditáveis as respostas dos companheiros NPCs aos atos e relações com o grupo, incluindo possíveis críticas, advertências, acordos, recusa narrativa e eventual saída. Manter **controle tático humano** da DEC-047 quando o NPC permanece recrutado; a IA local redige diálogos sob demanda, mas não executa efeitos de party. O motor BG2:EE permanece autoridade mecânica, o histórico canônico permanece como baseline e o modo Original não recebe mudanças.

A DEC-048 **não determina** que exista um hook funcional para impedir um jogador de comandar um companion, forçar abandono, agir em combate ou alterar scripts/flags; todas essas capacidades carecem de POC em BG2:EE e EEex multiplayer.

## 2. Fontes de decisão (ordem de confiança)

1. **Acontecimento confirmado:** `host_event_id`, instante, local, observadores, autoria efetiva, resultado e política da campanha. Morte, furto, ataque e outros efeitos mecânicos exigem evidência do host.
2. **Observação ou relato legitimamente recebido:** perspectiva do NPC, cadeias de transmissão, ruídos e confiança nas fontes. Rumor ≠ fato; rumor pode provocar *pergunta*, mas não é por si só prova de atrocidade.
3. **Identidade e histórico do NPC:** crenças, valores, alinhamento quando pertinente, lealdades, deveres, amizades, tensões, limites inegociáveis, grau de conhecimento, fontes do cânone por período/build.
4. **Vínculo e contexto:** cooperação prévia, promessas cumpridas/quebradas, ameaça, coação, necessidade, alternativas, intenção declarada (sem inventá-la), oportunidades de reparação e disponibilidade de discussão.
5. **Políticas configuráveis:** limites de reações, proteções a eventos críticos, intervalos, fallback e regras de RPG; alinhamento de PC não equivale a reputação, nem aprovação do NPC.

## 3. Modelo de estados proposto (não uma sequência obrigatória)

| Estado conceitual | Significado | Saída permitida sem integração mecânica |
|---|---|---|
| `STABLE` | vínculo sem conflito relevante corrente | nenhum efeito; rotinas existentes |
| `CONCERNED` | preocupação justificada | comentário, pergunta, observação contextual |
| `WARNED` | limite ou objeção declarados | conversa/advertência, proposta de reparação |
| `NEGOTIATING` | condições e promessas em discussão | opções de diálogo/compromissos narrativos verificáveis |
| `REFUSAL_INTENT` | NPC manifesta recusa a colaborar com algo | aviso narrativo; veto mecânico **não** presumido |
| `DEPARTURE_PENDING` | intenção de sair elegível, com condições e riscos verificados | proposta de ação via gateway; sem alterar party antes de receipt |
| `DEPARTED_CONFIRMED` | host confirmou remoção do NPC | atualizar memória/party; simulação do NPC após saída é DEC-049 |
| `RECONCILIATION_PENDING` | fatos novos/reparação em avaliação | reavaliar sem retcon; vínculo pode mudar de rumo |
| `UNCERTAIN` | solicitação mecânica sem confirmação inequívoca | congelar retry, reconciliar com host |

Estados são **projeções narrativas** e não necessariamente um conjunto exclusivo; o vínculo guarda dimensões independentes. Eventos graves confirmados podem ir diretamente à proposta de saída, pulando etapas conversacionais, **nunca** gates de risco, técnico e autoridade. Consequências coerentes podem perdurar mesmo após desculpas.

## 4. Pipeline lógico candidato

```text
Host/ledger -> evento idempotente + campanha/era/local/observadores
            -> visão e ACL do NPC (antes de qualquer LLM)
            -> valida fontes e crenças, diferencia fato e suspeita
            -> perfil canônico, vínculos, contexto e políticas por build
            -> avaliador determinístico de severidade + alternativas
            -> (A) nenhuma reação / (B) pergunta / (C) advertência
               / (D) negociação / (E) recusa narrativa / (F) saída proposta
            -> LLM local opcional redige falas com fatos filtrados
            -> para efeitos mecânicos: gate de risco, compatibilidade,
               contexto seguro, Action Gateway, host receipt
            -> atualiza projeção + ledger ou marca UNCERTAIN
```

**Sem inferência LLM a cada tick.** Avaliação pode ser orientada a eventos significativos e snapshots/catch-up delimitado; não disparar conversas automaticamente fora do alcance temporal/geográfico do NPC.

## 5. Contratos candidatos — nomes ilustrativos

```text
NPCDisposition { npc_id, campaign_id, canonical_profile_version, bond_dimensions,
                 moral_limits, current_concerns, commitments, last_evidence_id,
                 updated_at, policy_version }
NPCDissentAssessment { assessment_id, npc_id, source_event_ids, evidence_ids,
                       received_knowledge_refs, situation_context, severity_class,
                       proposed_reactions, reason_codes, confidence, policy_version }
NPCDialogueOffer { offer_id, npc_id, player_options, available_until,
                   dependencies, scope, privacy_policy, campaign_id }
NPCDepartureProposal { proposal_id, npc_id, party_id, required_safe_conditions,
                       engine_build_id, permission_scope, expected_party_state,
                       idempotency_key, risk_class, policy_version }
NPCMechanicalReceipt { proposal_id, host_event_id, status, party_state_hash,
                       confirmed_at, assignment_epoch }
```

Nenhum contrato implica API implementada. `confidence` e `severity_class` não concedem ao LLM autoridade para mudar flags/recursos por texto.

## 6. Regras de negociação e relações

- **Explicação:** contexto novo pode mudar interpretação, mas confissão, motivação e mudança de coração são escolhas do PC; NPC não deve inferi-las sem evidências.
- **Reparação:** restaurar confiança pode exigir atos ou compromissos verificáveis; não bastam palavras geradas automaticamente. Reputação pública não desbloqueia perdão universal.
- **Limites absolutos:** princípios centrais podem tornar inviável qualquer acordo naquele momento. Persuasão/magia só operam dentro de regras existentes, e coerção pode gerar outras consequências.
- **Divergência privada:** não revelar um histórico secreto do PC só para produzir o confronto narrativo; a possibilidade de descobri-lo deve seguir fatos e canais legítimos.
- **Relações múltiplas:** um NPC pode admirar a coragem do guerreiro e rejeitar seus atos contra inocentes, sem ser reduzido a uma escala única de aprovação.
- **Participação cooperativa:** o companheiro reage aos responsáveis e aos que legitimamente apoiaram ou toleraram os atos; não atribuir a um PC ausente consentimento por ações da party.

## 7. Portas de segurança para abandono e recusa

| Gate | Exigência | Fallback conservador |
|---|---|---|
| Canônico | Inventário de scripts/banters/romance/quest flags e limites por build | Reação narrativa sem sobrescrita de conteúdos originais |
| Evento e conhecimento | Evidência host e fatos/rumores com proveniência | Pedido de esclarecimento, nunca condenação com segredo vazado |
| Jogo e party | Verificar combate, cutscene, transição, slot, protagonista, itens, companions exigidos e sincronização | Aguardar ponto seguro; não remover NPC em estado inválido |
| Gateway e autorização | Operação tipada, escopo, risco, idempotência, pré-condições | Negar mutação mecânica se sem permissão |
| Mecânico | Confirmação do host e state hash | Estado `UNCERTAIN`, reconciliação sem replay cego |
| Multiplayer | Reprodutibilidade host + 2 clientes, save/load, reconexão | Desabilitar ação não comprovada |
| Original | Separação de build/saves | Nenhuma alteração de scripts/dados do modo Original |

**Risco importante:** um protesto narrativo não impede que a engine aceite uma ordem tática incompatível. Enquanto não existir interceptação comprovada, a interface não poderá afirmar que o NPC efetivamente recusou uma ação no motor.

## 8. Matriz de riscos candidata

| ID | Risco | Mitigação ou prova necessária |
|---|---|---|
| R-DISS-01 | NPC acusa PC com base em rumor falso como certeza | Fonte, crença, certeza e possibilidade de correção |
| R-DISS-02 | Personagem canônico reage fora de sua identidade | Auditoria de perfil/script/época e testes de regressão |
| R-DISS-03 | Um ato pequeno gera expulsão desproporcional | Classes de gravidade e histórico contextual auditáveis |
| R-DISS-04 | Atrocidade grave exige avisos artificiais antes de ruptura | Exceção crítica contextual, com prova e gates intactos |
| R-DISS-05 | LLM decide deserção, modifica party ou quest flags diretamente | Regras e gateway tipado + receipt do host |
| R-DISS-06 | Diálogo gerado confunde recusa narrativa com bloqueio efetivo | Estado separado + interface transparente/fallback |
| R-DISS-07 | Saída durante combate/cutscene/salvamento corrompe estado | Gate de contexto seguro, POCs multiplayer e idempotência |
| R-DISS-08 | NPC duplica abandono ou diálogo após save/load | IDs de evento, receipts, epochs e projeções idempotentes |
| R-DISS-09 | Segredo de PC vazado no prompt do NPC | ACL + filtros pré-LLM e testes adversariais |
| R-DISS-10 | NPC ausente reage a evento distante em tempo impossível | Grafo de difusão, relógio, localização e vigência |
| R-DISS-11 | Relação é zerada após pedido de perdão | Memória persistente e recuperação gradual quando justificada |
| R-DISS-12 | Contrato de companheiro de mod conflita com script original | Inventário por modlist, compatibilidade por build e isolamento |
| R-DISS-13 | Aumento de LLM por tick eleva latência | Regras event-driven e fallback de fala roteirizada |
| R-DISS-14 | NPC reage por decisão inventada de PC ausente/delegado | IDs de responsáveis e DEC-041/045/046; agência protegida |

## 9. Vinte testes candidatos de aceitação

| ID | Cenário e resultado esperado |
|---|---|
| DISS-T01 | Desacordo leve produz conversa opcional, sem saída automática de party. |
| DISS-T02 | Ato grave confirmado pode justificar saída imediata sem exigir etapas artificiais, mas ainda com gates técnicos. |
| DISS-T03 | Um boato desacreditado não cria condenação automática nem altera o fato histórico. |
| DISS-T04 | NPC não informado não reage a segredo privado do PC. |
| DISS-T05 | NPC que recebeu relato legitimamente pode perguntar sobre ele, distinguindo rumor de certeza. |
| DISS-T06 | Companheiro canônico preserva sua personalidade/flags no cenário-base de teste. |
| DISS-T07 | Atos repetidos criam tendência contextual sem contador mágico único. |
| DISS-T08 | Evidência nova altera a avaliação sem apagar o evento que originou o conflito. |
| DISS-T09 | Pedido de desculpas sem reparação não restaura automaticamente confiança. |
| DISS-T10 | Uma promessa de mudança é registrada e depois verificável/descumprível. |
| DISS-T11 | Controle tático permanece funcional enquanto não houver efeito mecânico confirmado de saída. |
| DISS-T12 | Proposta de recusa não é representada como veto efetivo sem hook validado. |
| DISS-T13 | Pedido de saída em combate/cutscene é bloqueado ou adiado de modo seguro. |
| DISS-T14 | Host confirma saída uma única vez, mesmo após save/load ou reconexão. |
| DISS-T15 | Falta de receipt leva a `UNCERTAIN`, sem repetir operação cegamente. |
| DISS-T16 | Um PC ausente não tem ações ou confissões atribuídas pelo NPC. |
| DISS-T17 | Dois jogadores e host observam estado narrativo/party coerente após reatribuição de slots. |
| DISS-T18 | Sem IA local, fallback de diálogo/regras não força mutação mecânica. |
| DISS-T19 | Regressão detecta efeitos duplicados ou incompatíveis após mods EET/IWD/NWNForBG. |
| DISS-T20 | Modo Original mantém comportamento, saves e scripts intactos. |

## 10. O que falta para SPECS e POCs

- Catalogar perfis, gatilhos e scripts dos companheiros canônicos e das builds; definir critérios de gravidade, filtros de ações, planos de teste e cadências sem converter NPCs em caricaturas.
- Escolher UX de explicação, avisos, negociação e aviso de ruptura sem spoiler, vazamento de segredos ou falsa promessa de veto mecânico.
- Definir schema real de receipts, hooks EEex e fallback em host/2 clientes, com confirmação de modlist/save-state e isolamento Original/Living World.
- Especificar governança de NPCs que saem da party e possibilidades de reencontro/recrutamento futuro na **DEC-049**.

**Nada nesta decisão implementa AI de NPC, flags, comandos de recusa ou saída física da equipe.**


## Encadeamento pós-ruptura — DEC-049 (aprovada na v4.5)

`DEPARTURE_INTENT` ou negociação fracassada não iniciam a simulação externa; somente `PARTY_MEMBER_REMOVED` confirmado pelo host. O NPC passa a ter identidade, relação e objetivos persistentes em atividade escalonada, podendo reencontrar o grupo e ser convidado novamente, sob condições de cronologia, lore, scripts e compatibilidade. Sem recibo, manter `UNCERTAIN` e não criar presença duplicada. Ver ADR-0044/doc. 49.

## Dependência de conteúdo nativo na ruptura — DEC-050 (v4.6)

Um julgamento narrativo de incompatibilidade moral (DEC-048) não autoriza remover NPC, alterar flags de romance ou cortar cenas originais. A DEC-050 exige verificar dependências observáveis da instalação antes de aplicar uma ruptura: colisão com quest/banter/romance pode levar a adaptação, adiamento ou bloqueio da proposta. Somente saída confirmada pelo host permite acionar a vida offscreen (DEC-049). Sem hook seguro, preservar estado e oferecer fallback textual sem falso acontecimento mecânico.

## Integração DEC-064/C — aprendizado e crenças sem onisciência (v6.0)

NPC pode ter desacordo, confiança ou ruptura com base em crença subjetiva falsa, desde que historicamente adquirida e versionada DEC-064/C. Prova posterior pode gerar reconsideração gradual, reparação ou persistência de desconfiança; não desfazer automaticamente ruptura, romances, flags de quest nem reputação/alianhamento mecânicos. Outputs LLM não fabricam testemunho.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

Promoção DEC-067 permite que um NPC secundário desenvolva relação recorrente, quando confirmada; ruptura/recusa não pode derivar de memória de homônimo ou evento inventado.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

Rupturas/relacionamentos de NPC em regime DISTANT/DORMANT DEC-068 continuam subordinados a evidência social, consentimento e risco; ausência não equivale a decisão pessoal irreversível confirmada. Reativação não inventa ofensas ou reconciliação.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

NPC pode recusar participação em engano que contrarie interesses; o sistema não fabrica mudança de lealdade por uma isca. Lealdades duplas ficam para DEC-087.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

DEC-087 complementa aviso, negociação, recusa e ruptura DEC-048: mudança de vínculo exige evidências de compromissos e gates, não dedução livre de LLM.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Desacordo moral, recusa ou ruptura NPC não equivalem automaticamente ao recrutamento/encerramento de informante; avaliar termo, agência e fatos.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Conflito de lealdade motivado por informe só pode avançar segundo regras e evidências; recusa/ruptura de companion não nasce de fofoca sem procedência.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Confiança e vínculos sociais influenciam interpretação de relatório recebido, mas não eliminam filtros ACL ou incertezas de evidências.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Recusa NPC é estado legítimo do plano, não falha a ser reexecutada automaticamente; evitar coerção ou mudança de lealdade por LLM.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Divergência ou ruptura de NPC requer regras da relação; replanejamento não obriga NPC a obedecer outra missão nem dispara hostilidade mecânica.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

NPC pode recusar uma operação concorrente, e o scheduler registra a indisponibilidade sem atribuir traição ou romper vínculo automaticamente.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Recusar tarefa/alterar lealdade não é resultado automático de deadlock; recuperação apenas propõe alternativa, respeitando valores e autonomias de NPC.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Lealdades e conflitos não autorizam assumir scripts originais ou retirar companion sem gates.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Rupturas de companions não são preditas a partir de future-branch flags expostas à LLM.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** A quest milestone observed on the host is NOT NPC knowledge, player consent, authorship, rumor or dialogue entitlement. A curated, minimal safe milestone must pass ACL/spoiler checks and be delivered causally before appearing in dialogue or memory; no LLM inference from raw flags. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **autonomia de companions**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para desacordos de companions podem continuar após correção comprovada, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para conflitos de companion podem persistir após correção, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
