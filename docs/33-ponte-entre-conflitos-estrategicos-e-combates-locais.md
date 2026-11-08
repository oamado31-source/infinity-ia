# Ponte entre conflitos estratégicos e combates locais — DEC-033

**Status:** desenho técnico preliminar para Discovery v3.0; **não é SPEC aprovada nem POC executada**. ADR vinculante: `decisions/ADR-0028-resolucao-hibrida-de-conflitos-e-intervencoes-locais.md`.

## Objetivo

Transformar uma parte de um conflito entre facções em oportunidades jogáveis no BG2:EE, sem instanciar exércitos inteiros, inventar mecânicas de combate ou confundir simulação externa com resultados confirmados pelo host.

```text
Cânone FR + facções + recursos + histórico da campanha
                        |
              Simulador estratégico
        (regras, tempo, tiers, lotes e seeds)
                        |
                 Validador de risco
                /                  \
        DISTANT/DORMANT          ACTIVE/NEAR
              |                     |
        resultado agregado     candidato a encontro
        externo autorizado          |
              |               catálogo de assets +
              |               diretor de encontros
              |                     |
              |                 Action Gateway
              |                     |
              |                BG2:EE host
              |                     |
              |                recibo mecânico
                \                  /
                 ledger de conflitos
                    |
           eventos, relações, reputação
```

## Objetos e estados candidatos

- `conflict_id` identifica a disputa estratégica; `segment_id` identifica a força, caravana ou frente específica; `campaign_id`, `world_time` e `rule_version` limitam a operação ao contexto correto.
- `strategic_event` registra o resultado de cálculo agregado validado. **Não recebe o campo de confirmação do host.**
- `local_encounter_request` é apenas proposta; valida região, cronologia, instalações, risco, participantes, cooldowns e limites de spawn.
- `host_receipt` contém prova verificada do evento mecânico observado/executado; sem isso, estado fica pendente ou incerto.
- `idempotency_key` estável por subinstância+ação+revisão previne repetir pedidos que já possam ter sido executados.

| Estado da subinstância | Significado | Regra de transição |
|---|---|---|
| `AGGREGATED` | Pode evoluir por regras da simulação externa | Só dentro do calendário e política de risco |
| `OFFERED` | Oportunidade local proposta | Participação opcional; sem atribuir resultado aos jogadores |
| `ENGAGED` | Host iniciou instância jogável | **Trava** para impedir auto-resolve da mesma parcela |
| `AWAITING_RECEIPT` | Resultado local ainda não confirmado | Não repetir ação automaticamente |
| `RECONCILED` | Resultado confirmado e registrado uma única vez | Propagar efeito proporcional, se autorizado |
| `BLOCKED_HIGH` | Resultado histórico crítico ou impacto proibido | Requer política de autorização especial |

A guerra geral pode continuar na simulação enquanto **uma subinstância específica** está em `ENGAGED`.

## Exemplos da relação entre escala local e estratégica

| Acontecimento local confirmado | Mudança estratégica potencial | O que não se presume |
|---|---|---|
| Escolta conclui viagem | Risco menor para aquela caravana/rota por período delimitado | Fim permanente do banditismo |
| Patrulha inimiga derrotada | Redução da força efetiva daquela unidade | Derrota de todo exército/facção |
| Comandante capturado | Penalidade contextual de coordenação ou moral | Queda automática de um reino |
| Negociação aceita e registrada | Mudança de relação ou condição de cessar-fogo elegível | Tratado histórico universal sem autorização |
| Jogadores ignoram convite | Oportunidade pode expirar; disputa evolui por regras | Penalidade arbitrária não previamente prevista |
| Rumor de vitória divulgado | Percepção de alguns NPCs conforme cadeia de conhecimento | Vitória histórica confirmada sem fonte |

## Governança de tempo, conhecimento e mecânica

- `FROZEN` impede simulação offscreen não autorizada; `PARTIAL` e `REALTIME` respeitam catch-up limitado (DEC-022).
- ACTIVE tem autoridade mecânica do host; NEAR prepara oportunidades; DISTANT usa projeções; DORMANT evita loop contínuo (DEC-021).
- Simulação externa pode projetar recursos e movimentações agregadas, mas não declarar mortes ou inventários locais no motor do jogo.
- Eventos canônicos HIGH (morte histórica, destruição de cidade, guerra decisiva) permanecem bloqueados até a **DEC-034**, não aprovada.
- Fatos confirmados, suspeitas e relatos devem ficar separados conforme DEC-028/029/030.
- A DEC-005-R mantém AD&D 2e como núcleo; a DEC-005-T de turnos individuais é opcional e tecnicamente pendente.
- Assets de EET/IWD/NWNForBG só podem ser instanciados se realmente existirem na build testada; catálogo de facções canônicas não implica recursos disponíveis.

## Cálculo estratégico: proposta ainda sem algoritmo aprovado

Considerar, em futuras SPECS, tropas agregadas, recursos, suprimentos, moral, liderança, defesa/terreno, rotas, informação e objetivos. **Não existem pesos, fórmulas, CR equivalentes ou valores de perdas aprovados.** Resultados irreversíveis de alto impacto devem parar no gateway/validador, não ultrapassá-los por acaso.

## Cenários de teste candidatos

| ID | Cenário | Aceitação candidata |
|---|---|---|
| MIL-01 | Facções batalham longe dos jogadores | Simular por agregados sem mapa carregado nem recibo falso |
| MIL-02 | O grupo entra numa região próxima de conflito | Oferta local coerente, não obrigatória |
| MIL-03 | O grupo recusa a missão | Sem travar a campanha nem atribuir participação |
| MIL-04 | Encontro aceito em área compatível | Gateway valida recursos e host confirma spawn |
| MIL-05 | Patrulha derrotada | Afeta somente aquela parcela, com impacto proporcional |
| MIL-06 | Escaramuça jogável em andamento | Não existe resolução estratégica concorrente da mesma força |
| MIL-07 | Salvar e reabrir combate pendente | Sem reaplicar baixas ou recompensas |
| MIL-08 | Queda de cidade canônica proposta | HIGH bloqueado sem autorização especial |
| MIL-09 | Rumor falso de vitória | Só conhecimento e percepção mudam, não o fato |
| MIL-10 | DISTANT passa para ACTIVE | Materialização consistente com registros e recursos instalados |
| MIL-11 | Recurso não instalado na build | Não executar spawn; recusar/fallback compatível |
| MIL-12 | Dois clientes conectados | Host autoritativo; registros convergem |
| MIL-13 | Falha na bridge depois de comando | Reconciliação antes de qualquer retry |
| MIL-14 | Sessão fechada e tempo congelado | Simulação de guerra não avança |
| MIL-15 | Catch-up após ausência longa | Lotes limitados e nenhum HIGH autoconsumado |
| MIL-16 | Campanhas Original/Living World | Nenhuma alteração cruzada de dados e saves |
| MIL-17 | Instalação sem turnos individuais | RTwP continua íntegro e jogável |
| MIL-18 | Reentrada e reprocessamento do mesmo evento | Sem duplicação de exércitos, perdas ou recompensas |

## POCs sugeridas — nenhuma executada

1. **POC-MIL-01:** simulador externo mínimo com duas facções, duas regiões e uma rota; persistir/reproduzir resultados com seeds estáveis.
2. **POC-MIL-02:** estados `OFFERED` e `ENGAGED`, locks e prevenção de resolução dupla em protótipo externo.
3. **POC-MIL-03:** BG2:EE limpo, leitura de eventos mecânicos em sandbox, sem gravar alterações reais.
4. **POC-MIL-04:** gateway + bridge com escrita controlada após permissões e validação de recursos.
5. **POC-MIL-05:** dois clientes multiplayer, desconexão, restauração e reentrada na mesma disputa.

**Dependências:** DEC-003 (baseline e integração incremental), DEC-011 (confirmação host), DEC-012 (allowlist), DEC-027 (níveis de risco), DEC-032 (simulador estratégico). A implementação **não foi comprovada** em BG2:EE, EEex nem nos mods.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: cruzar zona perigosa não confirma combate; efeitos de conflito precisam de política DEC-027/034 e validação host para resultados mecânicos, tema a aprofundar na DEC-070.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070 mantém ataques de caravana como propostas de incidente até o gate apropriado; cruzar conflito estratégico não produz combate/HP/loot de engine. O handoff para encontro jogável será DEC-071 (aberta).

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

A DEC-071 complementa a ponte DEC-033: handoff de incidente regional para encontro local é seletivo, condicionado à capacidade da área/build, reserva exclusiva, risco/consentimento e receipt do host. Não há resolução automática de guerra nem duplicação entre estratégia e combate.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — componentes de encontro local em guerras (Discovery v6.8)

A ponte DEC-033 pode sugerir encontro a partir de um conflito estratégico e um template DEC-072 validado por build, mas não gera script, spawn, perdas militares ou resolução de guerra apenas por narrativa. A elegibilidade, reserva de incidente DEC-071, risco DEC-027/070 e receipts de host são obrigatórios. Sem POCs de engine/multiplayer executadas.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Um encontro encerrado não implica vitória de exército nem impacto econômico automático; só consequências causais verificadas podem alimentar simulação estratégica.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Depois da resolução mecânica DEC-071/073, DEC-074 produz repercussões event-driven, sem resolver novamente o combate. Rumores sobre batalha são alegações, não nova derrota. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Autoridade pode ordenar ação na narrativa DEC-078, mas isso não prova guarda em combate nem resultado estratégico; DEC-011/012 e POC host são mandatórios.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Mandados DEC-079 não geram confrontos locais automaticamente: guardas/atores têm itinerário, capacidade de spawn e host receipt se realmente houver interação mecânica.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Hostilidade de guarda decorrente de mandado DEC-080 não é combate já realizado; perseguição e encounter exigem identidade, área, host e gateway, não simples suspeita.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Dano de combate/jurisdição pode originar pedido de reparação, mas não reescreve batalha confirmada nem muda resultado estratégico sem causalidade/risk gate separado.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Responsabilização de oficial não muda automaticamente forças militares, aliança ou resultado de combate; efeitos estratégicos requerem gate causal específico.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Conflito estratégico por espionagem não se converte sozinho em combate, ambush ou hostilidade mecânica; precondições de presença, risco e engine continuam necessárias.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Mudar forças/combates por relatório requer confirmação factual e autorização; intel de possível emboscada não constitui encontro mecânico automático.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Dossiê não dispara combate, movimentação militar ou emboscada; a futura DEC-091 terá planos sob risco/tempo/recursos e host gates, sem converter narrativa em mecânica.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Operação estratégica de facção não cria automaticamente batalha ou ator físico; handoff ao local necessita validação e host.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Mudança de operação com impacto em guerra/aliança eleva risco e requer política/gate; evento não comprovado não altera situação política.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-094/C (Discovery v9.0)

Recuperação de ciclo de espera entre forças não executa combate, remove unidades ou desfaz encontro host-confirmed; states UNCERTAIN aguardam reconciliação.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Repercussão de guerra por DEC-096 é estado/candidata, não spawn ou combate universal; impacto local depende de build/posições e host/bridge testado.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Sucessões e guerras DEC-096/C requerem versão temporal/regional curada; governante não é ressuscitado e decisões políticas irreversíveis não são inventadas por LLM.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Intensidade militar agregada DEC-097/C não cria tropas ou encontros; depende de risco, templates e host.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Conflitos estratégicos e combates locais não reutilizam ownership do overlay para editar conteúdo nativo por engano.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Conflitos militares só utilizam condições de quest semanticamente liberadas e causas confirmadas.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** a conclusão técnica de uma quest não concede automaticamente conhecimento ou crença a NPCs/facções. `QuestMilestoneAdmission` pode gerar proposta de notícia/reputação somente por regras, proveniência, tempo, geografia, visibilidade e ACL; notícia requer fonte/canal/delivery, e seus destinatários podem conhecer apenas versões parciais. Não expor identidades secretas, fontes protegidas ou raw flags por prompts/logs/dossiês. Ações mecânicas derivadas dependem de recibos host, sem atribuição presumida de PC. Ver doc. 103. **POCs reais pendentes.**

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-109/C — Obrigações condicionais multipartes

Conflitos externos não obrigam participantes a mobilizar guarda sem autorização. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
