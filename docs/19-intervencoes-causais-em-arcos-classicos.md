# Modelo preliminar — Níveis de intervenção e divergências dos arcos clássicos

**Discovery v1.7** · **DEC-026 / ADR-0016 aprovada** · **Desenho candidato para futuras SPECS, não implementação comprovada**

## Finalidade

Permitir encontros nostálgicos e participações opcionais em arcos clássicos sem acoplar o estado do Living World às flags da campanha Original. A camada de direção narrativa pode oferecer N1/N2/N3; apenas decisões validadas e eventos efetivamente confirmados mudam a história daquele grupo.

## Visão de contratos

```text
World clock / arc scheduler (DEC-022/025)
      -> candidate opportunity (arc_id, window, participation_level, dependencies)
      -> policy + lore + knowledge filter
      -> player chooses whether to engage
      -> allowed action proposal (rules first, LLM optional)
      -> controller validation (preconditions, permissions, idempotency)
      -> BG2:EE host execution, if mechanical
      -> confirmation / reconciliation
      -> durable event + projected state + campaign-specific canon branch
```

## Níveis e limites

| Nível | Possibilidades | Proibido presumir |
|---|---|---|
| N1: interação | conversa, rumor, barganha, reconhecimento, relacionamento | que uma resposta de IA alterou um arco crítico |
| N2: participação | missão de apoio, escolta, coleta de pistas, luta vinculada a trama | que o jogador assumiu a identidade/flags do protagonista original |
| N3: intervenção | impedir morte, alterar desfecho, salvar uma facção, desviar cronologia | mudança irreversível sem precondições, política de aprovação e confirmação |

## Estrutura candidata de oportunidade (dados exemplificativos, não schema final)

```json
{
  "arc_id": "arc_example_athkatla",
  "opportunity_id": "opp_example_informant",
  "campaign_id": "campaign_001",
  "level": "N2",
  "time_window": {"start_dr": 1369, "end_dr": 1369},
  "dependencies": ["npc_present", "rumor_discovered"],
  "player_opt_in": true,
  "criticality": "ordinary",
  "status": "available"
}
```

São IDs inventados para ilustrar formato. Não descrevem missões efetivas de BG2. Antes de implementação: definir IDs estáveis, referências do motor, precisão de data, janelas, flags e modelos de erro.

## Estado candidato de uma intervenção

1. `DISCOVERABLE` — oportunidade existe, mas pode não ter sido percebida.
2. `AVAILABLE` — tempo e condições permitem engajamento.
3. `ENGAGED` — grupo optou por participar.
4. `ACTION_PENDING` — pedido validado, execução/resultado ainda não confirmados.
5. `CONFIRMED` — efeito confirmado e registrado idempotentemente.
6. `BLOCKED` — sem permissão, condição ou capacidade técnica.
7. `EXPIRED` — janela passou sem interferência; progressão autônoma conforme DEC-025.
8. `RECONCILIATION_REQUIRED` — save, bridge ou host geraram resultado incerto.

Estados e transições são **propostas**, não contrato final aprovado. Um evento crítico N3 jamais deve pular diretamente de `ACTION_PENDING` para `CONFIRMED` a partir de texto do agente.

## Reconciliação da linha temporal

- Manter `official_reference_event_id`, `campaign_branch_id`, `caused_by_event_ids`, `affected_entities`, `source_provenance` e versões.
- Eventos oficiais de Forgotten Realms são candidatos ao mundo conforme data/precisão; divergências confirmadas geram ramo local e reavaliam os eventos dependentes.
- NPCs só recebem conhecimento de eventos quando há mecanismo verificável de testemunho, rumor ou comunicação (DEC-019).
- Região DISTANT/DORMANT não simula intervenção ativa por NPC em tempo real (DEC-021), mas pode atualizar estados agregados permitidos.
- Intervenções que alteram mapas, inventários ou morte de criaturas exigem verificação pelo host (DEC-011); uma divergência narrativa não se transforma em fato mecânico por interpretação.

## Critérios de aceite candidatos

- `T-026-01`: N1 não marca missão clássica como concluída.
- `T-026-02`: N2 permite assistência voluntária sem transformar PC em protagonista original.
- `T-026-03`: ações N2 falhas não produzem recompensa/rumor de vitória.
- `T-026-04`: N3 autorizado reencaminha eventos futuros dependentes de maneira rastreável.
- `T-026-05`: N3 sem autorização bloqueado e auditável.
- `T-026-06`: save restaurado reconcilia sem progressão duplicada.
- `T-026-07`: cliente multiplayer secundário recebe alteração após confirmação do host, se bridge comprovar capacidade.
- `T-026-08`: dados secretos do histórico não aparecem em falas de NPC sem conhecimento justificado.
- `T-026-09`: modo Original não recebe flags nem progresso do Living World.
- `T-026-10`: sem LLM local, oportunidades determinísticas continuam acessíveis e a simulação não trava.

## Dependências e blockers

- DEC-005: regras, balanceamento e recompensa.
- Política de aprovação de ações críticas ainda não escolhida.
- Comprovação EEex/bridge multiplayer e integração com scripts/flags do motor é gate obrigatório.
- Segurança: allowlist, isolamento, não executar Lua gerado livremente por modelos.
- Marcos de histórias clássicas exigem curadoria do lore, além da extração e adaptação dos recursos.

## Integração DEC-084/C — Discovery v8.0

Ameaça a NPC envolvido em arco clássico não autoriza dano/captura/realocação irreversível sem DEC-034 e gates de compatibilidade e cronologia.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Propostas que incluem dados privados ou obrigações de PCs requerem consentimento explícito de titular, sem acordos por silêncio ou membro delegado além da permissão.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-090/C — Discovery v8.6

Exposição de dossiês ou descobertas não impõe retcon irreversível no cânone; intervenções relevantes seguem gates, cronologia e consentimento de PCs.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Intervenção N3 em arco clássico é HIGH, requer autorização e receipt; dossiê não autoriza retcon.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Política de coop não permite que host/scheduler reatribua ação voluntária de PC retirado; gates e delegações DEC-041/045/046 aplicam-se a revisões.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Divergência N3 confirmada pode invalidar regras históricas dependentes DEC-096; source CanonEvent não é apagado, mas ramo ativo registra exceções e condiciona efeitos.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Intervenções causais de PCs preservam host receipts, ownership de quest e autorização por ação.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Históricos públicos/privados não herdam acesso global a quests por terem sido consultados tecnicamente.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** marcos confirmados de quests originais são **origens candidatas** de regras históricas/regionais, não fatos canônicos escritos em `knowledge/periods/<ANO>-DR/`. A admissão exige prova reconciliada DEC-100/101/102, clock DR e branch adequados; a matriz DEC-096 filtra local, fase e precondições e DEC-097 compõe impactos. Escopo global não dá conhecimento universal. Evento proposto, evento host-confirmed e rumor entregue são distintos; nenhum efeito mecânico sem Action Gateway/receipt. Ver doc. 103. **POCs reais pendentes.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para intervenções de jogadores não impõem crenças a NPCs distantes, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para decisões dos jogadores e consequências não retroativas, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Segregação de campanhas e event sourcing de acordos. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Isolamento por campanha e regras de append-only dos acordos committed. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
