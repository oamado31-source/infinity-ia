# ADR-0100 — Propagação causal de retificações e atualização falível de crenças (DEC-105/C)

- **Estado:** APROVADA COMO ARQUITETURA em 2026-11-07, por decisão expressa do idealizador.
- **Discovery:** v10.1. **Implementação real:** NÃO INICIADA/NÃO COMPROVADA em BG2:EE/EEex/bridge/host + dois clientes.
- **Decisões vinculantes:** DEC-011/012/019/020/021/022/027/028/029/030/041/053/057–065/068/069/074/076/077/083–090/095/096/098/099/100–104. **DEC-060..104 preservadas; ADR-0001..ADR-0099 imutáveis.**
- **Contrato detalhado:** `docs/105-propagacao-causal-de-correcoes-recebimento-crencas-e-revisoes.md`.

## Contexto

Uma retificação de prova, marco de quest ou rumor (DEC-104) não apaga que um NPC recebeu ou acreditou no relato original. A correção pode alcançar apenas parte do mundo por canais sociais e geográficos. Destinatários podem receber uma mensagem e não compreendê-la, compreender e contestá-la ou reconsiderar sua opinião gradualmente. Tratar uma errata como atualização global permitiria onisciência, falsificação de memórias e revelação de segredos protegidos.

## Alternativas

- **A — Correção instantânea universal:** REJEITADA. Suprime distância, canais, diferenciação social, memória e autonomia dos NPCs.
- **B — Reescrita livre de crenças por LLM:** REJEITADA. Pode alterar eventos, evidências, relações, fontes protegidas e decisões dos jogadores sem comprovação.
- **C — Correção como nova comunicação causal, com crenças falíveis e auditoria:** **APROVADA**.

## Invariantes normativos

1. **Fato, alegação, mensagem, entrega, percepção e crença são registros distintos.** `WorldFact`, `Claim`, `CommittedCorrection`, `Transmission`, `DeliveryReceipt`, `PerceptionReceipt`, `RecipientKnowledge`, `RecipientBelief` e `BeliefRevisionProposal` têm ciclos de vida e autoridades próprios. Nenhum desses registros implica automaticamente o seguinte.
2. **A correção nasce de prova legítima, não de comando textual.** O serviço consultará prova curada, versionada e `COMMITTED` conforme DEC-089/100–104. A requisição só aponta a correção pretendida; não cria prova, autoridade, consentimento ou capacidade.
3. **A retificação não destrói o relato anterior.** Manter alegação, versão, proveniência, datas, canais, recepções e avaliações anteriores. `CORRECTS` ou `SUPERSEDES` não equivale a `DELETE` e não faz o NPC “desaprender” uma informação.
4. **Sem transmissão universal.** Cada mensagem depende de emissor habilitado, canal disponível, deslocamento/localização, cronologia DR, alcance, custo/recurso e destinatário efetivamente alcançável. Broadcast, telepatia, envio instantâneo ou conhecimento generalizado só podem existir se houver mecanismo canônico e capability legitimamente comprovados.
5. **Entregar não é perceber; perceber não é concordar.** `SENT`, `IN_TRANSIT`, `LOST`, `UNCERTAIN` não equivalem a recepção. `DELIVERED` precisa de evidência de percepção/compreensão quando a regra depender disso. Ouvir uma errata pode criar registro de ciência sem modificar crença.
6. **Identidade e público tipados.** `recipient_id` persistente distinto da instância no motor; pseudônimos, identidade privada, testemunhas protegidas e grupos têm ACL por finalidade, audiência, classificação, campanha/branch/lineage, tempo e versão. A associação nominal/grupal não é autorização.
7. **Sem vazamento indireto.** Redações públicas, anexos, identificadores, rotas, tamanho de payload, logs, prompt, cache, tabelas e contadores não podem expor fonte protegida, fato secreto ou localização de refúgio. Filtrar antes da criação da mensagem e do contexto LLM.
8. **Crença falível e gradual.** O sistema preserva como estados distintos `NOT_HEARD`, `HEARD_UNASSESSED`, `BELIEVES_OLD`, `DOUBTS_OLD`, `CONTESTING`, `RECONSIDERING`, `BELIEVES_CORRECTION` e `UNCERTAIN`. As transições dependem de evidência, credibilidade da origem, confiança prévia, interesses e relações **curados**. Não há aceitação obrigatória, nem números psicossociais inventados pela LLM.
9. **Contradições permanecem possíveis.** A verdade curada não gera automaticamente crença. Famílias de relatos com a mesma origem não contam como confirmação independente (DEC-077/089); interpretações contestadas permanecem assim até nova evidência.
10. **A revisão de crença exige autoridade separada.** O planejador apenas propõe uma transição. Uma futura política determinística/campanha e o controlador legítimo do NPC validam a revisão; nenhum PC recebe crença, opinião, confissão ou consentimento decidido pela IA. Narrativa LLM só atua sobre contexto já filtrado.
11. **Temporalidade real do mundo.** Usar ano DR, janela/precisão de data, relógio DEC-022 e presença/viagens DEC-068/069. Modo `FROZEN` impede avanço implícito, não apaga mensagens já entregues. O sistema não presume que o tempo real do computador é tempo do mundo.
12. **Cadeia de comunicação e idempotência.** `CorrectionEnvelope` → `Transmission` → `DeliveryProof` → `PerceptionProof` → `BeliefReviewProposal` → eventual `BeliefRevisionReceipt`, com IDs estáveis, causal parents e revisões. Outbox/CAS/fencing evitam reenvio, dupla recepção ou dupla mudança em save/load/restore/reentrada e multiplayer.
13. **Ramo, epoch e Knowledge Pack isolados.** Não transportar errata, memória, rumor ou recibo entre campanhas, saves divergentes, branches e versões de build. Rejeitar prova/receipt de outras epochs sem procedimento explícito de migração e reconciliação (DEC-053/060–063).
14. **Canal incerto permanece incerto.** Mensagem `DISPATCHED/UNCERTAIN` exige reconciliação; não concluir entrega, não reenviar às cegas, não liberar recurso em reserva. Cancelamento só pode bloquear futuros envios ainda não despachados.
15. **Uma correção pode também estar errada.** Versões sucessivas geram novas correções com ligações e fontes preservadas. Evitar loops de corrigir a correção, ciclos de proveniência e revisões infinitas; aplicar limites de fan-out, profundidade, cadência e revisão assinada.
16. **Efeitos sociais não são efeitos mecânicos.** Revisar crença não modifica diretamente reputação nativa, alinhamento, quest, inventário, punição, comércio ou política. Tais consequências possuem gates próprios DEC-027/030/074/078/081/095/099, consentimentos e receipts do host.
17. **Priorização de segurança e performance.** Processamento local-first com filas orçamentadas e entrega progressiva. Em dados insuficientes, incompatibilidade, ACL incerta, identidade contestada ou grafo temporal incompleto: `DENIED`, `UNKNOWN` ou `QUARANTINED`, nunca inferência livre.
18. **Estado técnico atual.** Exemplo Python, fixture e schema são **SINTÉTICOS E SEM EFEITOS COLATERAIS**; não implementam mensageiros, NPCs, redes, bridge, EEex nem multiplayer. Os 144 cenários T105-* são **candidatos de integração não executados**.

## Contratos conceituais

| Entidade | Campos candidatos (não API real) | Garantia |
|---|---|---|
| `CommittedCorrection` | `correction_id`, `prior_claim`, `proof_ref`, `proof_revision`, `classified_scope`, `source_family`, `time_dr`, `branch/lineage` | Prova independente da request; nunca redefine fatos host-confirmed |
| `CorrectionEnvelope` | `envelope_id`, `correction_ref`, `audience`, `redaction_view`, `classification`, `policy_revision` | Nenhum spoiler/identidade privada na view entregue |
| `TransmissionEvent` | `channel_id`, `sender`, `recipient`, `sent_at_dr`, `route`, `hop_count`, `ttl`, `resource_ref` | Existe apenas se o canal físico/social é legítimo e autorizado |
| `DeliveryReceipt` | `delivery_id`, `envelope_ref`, `recipient_persistent_id`, `arrived_at_dr`, `state`, `evidence_ref` | `DELIVERED` não implica compreensão/aceitação |
| `PerceptionReceipt` | `delivery_ref`, `actor`, `perceived_at_dr`, `coverage`, `scope` | Conhecimento do conteúdo mínimo recebido, nunca dados não expostos |
| `BeliefRevisionProposal` | `proposal_key`, `prior_belief_ref`, `evidence_family_refs`, `trust_context_ref`, `proposal`, `review_policy`, `CAS` | Proposta, não uma escrita automática na memória |
| `BeliefRevisionReceipt` | `proposal_ref`, `authority`, `revision`, `decision`, `event_time`, `branch` | Só comprova revisão depois da política/autoridade própria |

## Exemplo sintético

Uma notícia equivocada chega a três comerciantes de uma cidade fictícia. Uma correção `COMMITTED` é enviada por mensageiro a apenas dois. O primeiro recebe, percebe, mas mantém dúvidas; o segundo recebe, percebe e é candidato a reconsiderar; o terceiro ainda não recebeu nada. O planejador entrega **propostas** por destinatário, sem alterar memória, repertório de fontes, preços, reputação, host ou status de mensagens. A mesma prova revisada não cria uma transmissão nova a cada chamada.

## Compatibilidade e critérios de aceite

Necessário comprovar posteriormente em Windows BG2:EE/EEex/bridge, host + dois clientes: mecanismo real de evento observado, transporte causal ou conversas, identidade persistente do destinatário, receipt de recepção/percepção, ACL pré-prompt, relógio DR e modos `FROZEN/PARTIAL/REALTIME`, versão de belief store, CAS/outbox, restore/fork, comportamento offscreen e ausência de efeitos duplicados. Sem essas provas, a função permanece em SPEC/POC pendente.

## Próxima discussão — DEC-106 (EM ABERTO)

**Reabilitação de reputações após retificações públicas:** (A) restaurar automaticamente reputação; (B) LLM decidir a reparação e percepções sociais; **(C recomendada)** correção reputacional proporcional e causal, diferenciando verdade, crença, exposição, danos já ocorridos, canais de contestação, recursos, legitimidade/consentimento e efeitos host-confirmados. DEC-081 e DEC-030 são precedentes; não criar reversão mecânica automática.
