# ADR-0105 — Custódia condicional verificável de garantias (*escrow*) sem liberação automática (DEC-110/C)

- **Status:** APROVADA COMO ARQUITETURA em 2026-11-07; Discovery v10.6.
- **Decisão:** DEC-110, opção C.
- **Documento normativo:** `docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md`.
- **Imutabilidade:** DEC-060 a DEC-109 vinculantes; 104 ADRs anteriores preservados byte a byte.
- **Limite:** não existe depósito, transferência, escrow real, hook EEex, serviço host ou multiplayer comprovado; o código de referência é uma simulação pura.
- **Dependências:** DEC-011/012/014/022/027/028/041–046/053/056/081/093–095/099/107–109.

## Problema

O DAG de acordos (DEC-109) torna obrigações *elegíveis*, mas não reserva magicamente moedas, itens ou NPCs. Uma promessa de depósito narrada ou registrada em contrato não é um depósito mecânico confirmado. É preciso distinguir titularidade, autorização, disponibilidade, custódia real, retenção por disputa e liberação; evitar recursos simultaneamente livres e empenhados; preservar recibos, epochs e checkpoints e não assumir que BG2:EE/EEex suporta transferência segura de escrow.

## Alternativas

- **A — Transferência e liberação automáticas: rejeitada.** A aceitação contratual não autoriza confisco; cria riscos de duplicação, retirada de bens de PC e inconsistência de save.
- **B — LLM como custodiante: rejeitada.** Texto não prova propriedade, recibo, compromisso, decisão de disputa ou permissão para alterar inventário.
- **C — Garantia verificável e liberação condicionada, sem execução automática: APROVADA.** Contratos/versionamento, ownership, custódia explícita, logs confiáveis, gates e reconciliação; sem capability validada, no máximo um compromisso narrativo sem alegar custódia mecânica.

## Decisão vinculante

1. `EscrowAgreement` possui `agreement_id/revision`, `escrow_id/revision`, `campaign_id`, `branch_id`, `lineage_id`, `build_fingerprint`, `modpack_hash`, `host_epoch`, `checkpoint_epoch`, `knowledge_pack_id`, `world_tick`, moeda/item/unidade/quantidade decimal, `depositant`, `custodian`, `beneficiaries`, `release_terms`, custodian authority, ownership proofs e ACL. Mudanças de condições geram revisão committed, jamais reescrita do passado.
2. **Seis estágios não equivalentes:** `PROMISED` → `DEPOSIT_PROPOSED` → `HOST_DISPATCHED/UNCERTAIN` → `CUSTODY_CONFIRMED` → `RELEASE_ELIGIBLE` → `RELEASE_CONFIRMED`; `CONTESTED`, `BLOCKED`, `RETURN_ELIGIBLE`, `RECONCILE_REQUIRED` são ramificações, não atalhos. Não promover estado sem recibo válido.
3. **Custódia somente verificável:** no modo mecânico, requer transferência efetiva para custodiante validado/conta permitida, comprovada pelo host e conciliada com inventário, ownership e reserva. Um `ReservationToken` meramente lógico não é prova de que o item saiu da posse original.
4. **Capability gate por build:** exigir contrato explícito e POC de criação/transferência/consulta/recuperação de custódia, com dois clientes e save/load. Se ausente, `BLOCKED_CAPABILITY` e apenas acordo/proposta narrativos, rotulados `NOT_MECHANICALLY_HELD`.
5. **Titularidade e consentimento:** depósitos de PCs exigem aprovação explícita do titular, inclusive para execução delegada; de NPC/facção exigem mandato e recursos comprovados. Contrato assinado, cláusula econômica, rumor, dossiê ou LLM não concedem acesso à carteira.
6. **Condições de liberação:** o grafo DEC-109 e recibos DEC-108 podem tornar uma liberação `ELIGIBLE_FOR_REVIEW`, nunca `TRANSFERRED`. Toda liberação exige autorização própria, custódia ainda confirmada, ausência de disputas não resolvidas, recurso disponível e recibo de host.
7. **Contestação e retenção:** disputa explícita pode conter novos despachos; não autoriza unilateralmente adjudicar bens. Decisão de autoridade curada, arbitragem aceita ou novo acordo pode habilitar uma proposta; a LLM não decide propriedade nem culpa.
8. **Idempotência/concurrency:** `escrow_id`, revisão, `action_id`, `receipt_id`, `host_epoch`, `checkpoint_epoch`, `ledger_revision` e `fencing_token` previnem segunda liberação, overspend e conflitos com DEC-093/094. Com `DISPATCHED/UNCERTAIN`, não repetir, liberar nem reutilizar garantia sem reconciliação.
9. **Save/load e forks:** nunca importar custódia de outra campanha/ramo/linhagem. Após restauração, cotejar recibos e inventário observável; preservar histórico antigo. `UNKNOWN` não autoriza liberação.
10. **Transparência e privacidade:** relatório pode divulgar compromisso/custódia apenas a audiências permitidas; não expor segredos de partes, inventários privados, pseudônimos ou parâmetros de scripts a NPCs ou LLMs.
11. **Sem mecanismos coerção:** descumprimento, vencimento, suspeita ou erro não autorizam multa, punição, retirada, reparação ou transferência automática; usar DEC-081/095/107/108 e host gates.
12. **Referência sintética:** apenas planejamento determinístico e saída `host_action=NONE`; o esquema candidato, fixture e testes não são comprovação de capability EEex.

## Invariantes

- `contract_accepted != custodian_transfer_confirmed`.
- `condition_satisfied != release_authorized != host_release_receipt`.
- `logical_reservation != inventory_segregation`.
- `claim != host_receipt`; `expiry != breach`; `UNKNOWN != SAFE_TO_RETRY`.
- Nenhum recurso aparece como simultaneamente livre e custodiado no mesmo snapshot confirmado.
- Recibos duplicados não ampliam quantidade; fontes inconsistentes ficam em quarentena.
- Uma compensação é novo evento autorizado, nunca apagar fatos anteriores.
- Sem novos direitos para NPCs ou jogadores apenas pela existência de cláusulas.

## Consequências e riscos aceitos

**Vantagens:** acordos comerciais robustos, garantias auditáveis, proteção de propriedade e compatibilidade com o DAG de condições, sem falsas reservas narrativas. **Custos:** complexidade de reconciliação de inventário, ownership por campo, modpack, forks e autoridade no multiplayer; diversos cenários ficarão bloqueados até POC. **Risco residual:** EEex pode não oferecer custódia mecanicamente segura: nesse caso, não implementar escrow real e manter a possibilidade como conteúdo puramente narrativo identificado.

## Validação e critérios para SPEC

- Gate P0: jogo base, build fingerprint, bridge read-only e dois clientes.
- Gate P1: inventário/capacidade de transferir/reaver recurso em save de teste, sandbox e multiplayer; reentrância de save/load e retries.
- Gate P2: impedir uso concomitante e duplicação em conflitos de NPCs e PCs.
- Gate P3: contestação, autorização, restituição e rejeição de retenções coercitivas.
- `examples/chronology/escrow_reference.py` + JSON Schema e testes: **apenas sintéticos**.
- **176 cenários T110 candidatos, não executados em BG2:EE/EEex**, detalhados no documento técnico.

## Encaminhamento do projeto

Com mais de cem ADRs, **não exigir novo ADR para cada tarefa de programação**. O questionário `docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md` recolhe decisões restantes de modo em lote, preservando rastreabilidade; decisões antigas abertas permanecem abertas até ratificação do usuário. O handoff SDD fica detalhado em `docs/112-plano-de-transicao-discovery-specs-e-primeiro-ciclo-executavel.md`. DEC-111 fica **em discussão**, não aprovada implicitamente, sobre baseline/controle de mudanças de SPECs.
