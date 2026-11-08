# Desenho técnico preliminar — Progressão híbrida dos arcos paralelos

**Discovery v1.6** · **Fundamento aprovado:** DEC-025 / ADR-0015 · **Situação:** proposta de contratos e testes; não é SPEC nem código de produção.

## Escopo e dependências

Consolidar as decisões DEC-024/025 sem acoplar a progressão das histórias clássicas aos scripts originais. Integrar calendário autorizado (DEC-022), atividade regional (DEC-021), persistência (DEC-008), canon e divergências (DEC-009), conhecimento e segredos (DEC-019), host/bridge (DEC-011) e orquestrador determinístico-first (DEC-014).

## Fluxo lógico

```text
CampaignClock (tempo de mundo confirmado / catch-up permitido)
  -> Canon/Arc Eligibility (fonte, região, época, versões e pré-condições)
  -> Arc Scheduler (regras e transições idempotentes)
       |-- transição narrativa reversível -> Arc Event Log + Snapshot
       |-- janela opcional -> Opportunity Window Manager -> jogador aceita/ignora
       |-- alteração mecânica -> Controller -> EEex/Host -> recibo -> confirmação
       |-- marco irreversível -> Critical Event Gate -> aprovado / pendente
  -> Arc/Canon Reconciler -> rumos futuros e divergência causal
  -> Rumor/Dialogue Router -> fatos conhecidos pelo NPC + LLM local sob demanda
```

## Tabelas lógicas candidatas

| Entidade | Campos ilustrativos | Invariantes |
|---|---|---|
| `ArcDefinition` | `arc_id`, `source_story`, `canon_line_id`, `time_precision`, `source_refs`, `required_assets`, `ruleset_version` | Falta de data exata não vira data fictícia |
| `ArcInstance` | `campaign_id`, `arc_id`, `stage`, `state`, `world_revision`, `last_advance_at`, `branch_id` | Estado por campanha, independente do modo Original |
| `ArcBeat` | `beat_id`, `from_stage`, `trigger`, `preconditions`, `effects`, `criticality`, `fallback` | Transição só após pré-condições verdadeiras |
| `OpportunityWindow` | `window_id`, `arc_id`, `open_condition`, `close_condition`, `area_ids`, `participation_type`, `expiry_policy` | Ativação não é uma missão obrigatória |
| `ArcTransition` | `event_id`, `arc_id`, `beat_id`, `clock_revision`, `cause`, `confirmation`, `idempotency_key` | Reprocessar não duplica efeitos |
| `RumorPropagation` | `source_event`, `known_by`, `channel`, `available_at`, `audience_acl` | NPC sabe apenas se recebeu informação de modo plausível |

Os nomes são sugestões de esquema; não são modelos físicos aprovados.

## Regras de elegibilidade (pseudoprocedimento)

1. Validar `campaign_id`, modo Living World, versão de mundo e fingerprint de save.
2. Ler **tempo de mundo confirmado**, regras de catch-up e proteção de eventos irreversíveis; não consultar relógio real diretamente para decidir o fato histórico.
3. Verificar pré-condições, região, personagens existentes, dependências de lore, origem de mods e disponibilidade de assets.
4. Se um arco tem data incerta, utilizar gatilho condicional ou manter pendência de curadoria; **não inventar dia/mês**.
5. Abrir, manter ou encerrar oportunidades com justificativa e log. Permitir NPCs informarem oportunidades sem obrigar o grupo a aceitá-las.
6. Para avanço narrativo simples, registrar transição com chave idempotente e atualizar projeção/snapshot.
7. Para efeito mecânico, emitir proposta para controlador e aguardar confirmação do host antes de marcar conclusão.
8. Para evento irreversível, aplicar política de Critical Event Gate; sem política explícita, segurar resultado em pendência.
9. Se jogadores modificaram a causa/desfecho, registrar ramo divergente e reavaliar dependências dos eventos futuros.
10. Produzir rumor/diálogo apenas para NPCs com acesso fundamentado; inferência local pode escrever o texto, **não certificar o fato**.

## Exemplo simulado de linha temporal (não é cronologia oficial de BG2)

| Instante em tempo de jogo | Estado de um arco inventado | Grupo | Resultado permitido |
|---|---|---|---|
| Dia 1 | Um mensageiro prepara viagem | Distante | Agenda e evento narrativo por código |
| Dia 3 | Abre oportunidade de escolta | Próximo | Oferta opcional, sem iniciar missão obrigatória |
| Dia 5 | Janela termina | Ausente | Desfecho leve registrado se relógio autorizado |
| Dia 6 | Morte de autoridade estava prevista | Ausente | **Pendente** sem autorização explícita de evento crítico |
| Dia 7 | Grupo retorna | Ativo | Verificações, possíveis rumores e oportunidade de intervenção se ainda consistente |

## Interfaces e falhas

- **Timeout no host/bridge:** `PENDING_MECHANICAL_CONFIRMATION`; nenhum retry automático não idempotente.
- **Data/artefato não confirmado:** `BLOCKED_UNVERIFIED` ou `HISTORICAL_UNRESOLVED`.
- **Conflito de save/revisão:** suspender transição, registrar conflito e reconciliar; não aplicar duas linhas temporais sobre o mesmo estado.
- **LLM indisponível:** texto padrão/templated, nenhum bloqueio da máquina de estados.
- **Carga excessiva:** simulação em lotes com orçamento; priorizar arcos relevantes à região/grupo, não rodar uma inferência por NPC.
- **Jogadores desconectados:** respeitar `FROZEN`/`PARTIAL`/`REALTIME` por campanha; nenhum servidor permanente exigido no MVP.

## Candidate features para priorização futura

1. `FEAT-ARC-SCHEDULER` — transições por regras, datas e condições.
2. `FEAT-ARC-OPPORTUNITIES` — janelas opcionais, descoberta e expiração.
3. `FEAT-ARC-CRITICAL-GATE` — proteção/autorizações de eventos irreversíveis.
4. `FEAT-ARC-CANON-BRANCHES` — divergências causais e reavaliação de consequências.
5. `FEAT-ARC-SAVE-RECONCILIATION` — recuperação de saves e idempotência.
6. `FEAT-ARC-RUMORS` — rumores por conhecimento, região e tempo; LLM local opcional.

**Importante:** IDs de features são propostas de backlog, não requisitos aprovados; contrato técnico final depende das decisões pendentes e do teste real com EEex/bridge e multiplayer.

## Integração DEC-091/C — Discovery v8.7

Plano sugerido para arco paralelo não implica presença do grupo; participantes têm janela opcional e autonomia.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Critérios de qualidade para adapters devem incluir capacidades de monitorar, pausar middleware e identificar ações nativas em voo, sem assumir pausa do motor.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Matriz proposta DEC-096 pode ativar janelas de arcos pela época, região e precondições; marcos irreversíveis continuam protegidos e não são forçados pelo scheduler.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Arcos clássicos paralelos preservam scripts e estados originais; nenhuma reconciliação de história autoriza quest writes.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Informações de eventos e campanhas precisam de provenance temporal e público autorizado, sem metaconhecimento de script.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** marcos confirmados de quests originais são **origens candidatas** de regras históricas/regionais, não fatos canônicos escritos em `knowledge/periods/<ANO>-DR/`. A admissão exige prova reconciliada DEC-100/101/102, clock DR e branch adequados; a matriz DEC-096 filtra local, fase e precondições e DEC-097 compõe impactos. Escopo global não dá conhecimento universal. Evento proposto, evento host-confirmed e rumor entregue são distintos; nenhum efeito mecânico sem Action Gateway/receipt. Ver doc. 103. **POCs reais pendentes.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para arcos clássicos podem gerar notícias somente por canais legítimos, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para repercussões de quests canônicas com prova de autoria, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
