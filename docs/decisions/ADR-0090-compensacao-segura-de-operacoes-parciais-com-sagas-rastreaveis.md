# ADR-0090 — Compensação segura de operações parcialmente concluídas com Sagas rastreáveis

- **Decisão:** **DEC-095 — Opção C**, aprovada expressamente em **2026-11-07**.
- **Status:** **APROVADA COMO ARQUITETURA** no Discovery v9.1; **NÃO IMPLEMENTADA nem TESTADA** no motor do jogo.
- **Preservação:** todas as DEC-060 a DEC-094 válidas. Os **89 ADRs anteriores** permanecem **byte a byte idênticos** à v9.0.
- **Especificação candidata:** `docs/95-compensacoes-de-operacoes-parciais-sagas-idempotencia-e-reconciliacao.md` (96 testes candidatos **NÃO EXECUTADOS**).
- **Dependências:** DEC-011/012/019/022/027/028/041/042/045/046/050–056/063/066–074/078–094; aspectos técnicos da DEC-006/007/013/015/017/018 continuam abertos.

## Problema

Uma operação composta pode realizar e confirmar ações em sequência e falhar parcialmente. Um contrato pode ser assinado e parte do pagamento realizado antes da desistência da escolta; o NPC pode ter se deslocado, pessoas podem ter observado e o host pode ter consumido itens. Não existe transação global presumida com BG2:EE/EEex, nem garantia de rollback seguro de eventos do mundo. DEC-094 resolve disputas de reserva, não a compensação de efeitos já confirmados.

## Alternativas avaliadas

- **A — Rollback global:** rejeitada. Desfaz eventos irreversíveis, altera fatos testemunhados e pressupõe capacidade não comprovada no motor.
- **B — LLM define compensação:** rejeitada. O modelo não detém propriedade dos recursos, autoridade do host ou consentimento dos jogadores.
- **C — Sagas explícitas com ações compensatórias verificáveis, proporcionais e autorizadas:** **APROVADA**.

## Regras arquiteturais vinculantes

1. **Operação como Saga versionada:** `SagaPlan` contém sequência ou DAG de `SagaStep`, `operation_id`, `campaign_id`, `branch_id`, `host_session_epoch`, `plan_revision`, `knowledge_pack_pin`, `checkpoint_ref`, autorizadores e owner. Etapas concluídas permanecem imutáveis no ledger de fatos confirmados.
2. **Etapa não equivale a efeito:** distinguir `PROPOSED`, `VALIDATED`, `AUTHORIZED`, `DISPATCH_PENDING`, `DISPATCHED`, `HOST_CONFIRMED`, `FAILED_VERIFIED`, `UNCERTAIN`; apenas recibo de execução confiável ou prova conforme capacidade validada confirma efeito mecânico. Não presumir que enviar comando foi sucesso.
3. **Compensabilidade declarada:** cada etapa define `COMPENSABLE`, `CONDITIONALLY_COMPENSABLE`, `NON_COMPENSABLE` ou `UNKNOWN`; classificação exige capacidade real e evidência, nunca heurística LLM. Eventos observados, mortes, revelações de segredos, deslocamentos já realizados e reputações publicamente alteradas não são apagados silenciosamente.
4. **Compensar é novo evento:** reembolso, desobrigação, contrato substitutivo ou devolução autorizada são novos atos auditáveis, não mutação retroativa de ledger anterior. Não há garantia de reversão perfeita, mesmo quando restituição numérica é possível.
5. **Política por etapa e titular:** `CompensationPolicy` explicita pré-condições, recurso/titular, consentimento, jurisdição, recurso disponível, risco DEC-027 e capability do adaptador. O host valida qualquer mudança mecânica. Contratos sociais entre NPCs também requerem competência e compromisso genuínos.
6. **No compensation by default:** etapas sem política validada ficam `PENDING_REVIEW` ou `NON_COMPENSABLE`, sem efeito automático. LLM local pode redigir explicação ou proposta, não gerar automaticamente um novo direito de reembolso.
7. **Sequência determinística:** compensações candidatas seguem a dependência inversa de passos quando tal ordem for segura. Etapas paralelas requerem DAG e conflitos de recursos DEC-093/094; não assumir que toda ordem inversa seja válida. Detectar ciclos e impedir loops de compensação.
8. **Falhas e estados:** Saga pode terminar `COMPLETED`, `PARTIALLY_COMPLETED`, `COMPENSATION_PROPOSED`, `COMPENSATING`, `PARTIALLY_COMPENSATED`, `COMPENSATED_WITH_RESIDUAL_EFFECTS`, `ESCALATED`, `UNCERTAIN`; não afirmar `FULLY_ROLLED_BACK` como garantia genérica.
9. **Outbox, dedup e idempotência:** `saga_id`, `step_id`, `compensation_id`, `idempotency_key`, `resolution_epoch`, `host_receipt_id` + `checkpoint_ref` sustentam tentativa única e reconciliação. Timeout e crash **não** provam falha mecânica e não autorizam reenvio cego.
10. **Recursos reservados:** o scheduler DEC-093/094 mantém quarentena de reserva `UNCERTAIN`, `IN_FLIGHT` e `CONSUMED_VERIFIED` até recibos e regras explícitas. Compensar ouro requer prova de saldo, titularidade e nova movimentação host-confirmed; não gerar ouro fictício.
11. **Ações humanas e multiplayer:** PC não se move, aceita contrato, pede desculpas ou abandona missão por imposição da saga; decisões de terceiros exigem consentimento individual/delegação scoped. Não usar prioridade de fila, retentativa ou narrador como consentimento.
12. **Irreversibilidade e efeitos sociais:** morte, combate, viagem concluída, identidade revelada, testemunhas informadas, evento histórico e memória NPC persistem; uma reparação pode mitigá-los sem negar causalidade. DEC-081 (reparações por danos) é conceitualmente distinta do protocolo operacional.
13. **Segurança do tempo e cânone:** eventos canônicos físicamente particionados por ano DR DEC-060, KPack pinado DEC-063, branch e relógio DEC-022. Compensações só alteram overlay autorizado e nunca reescrevem a história curada. Restore DEC-053/054 invalida épocas antigas; divergência controlada DEC-024–026 e DEC-034.
14. **Privacidade:** logs de compensação e dossiês não divulgam identidades de fontes, refúgios, rotas e motivos secretos DEC-083–090. Auditoria operacional usa redaction por audiência/ACL.
15. **Queda do motor/rede:** com confirmação do host ausente, manter `UNCERTAIN`; preservar reservas, não decretar compensação bem-sucedida, não repetir chamada e acionar reconciliação. Capabilities EEex para cancelamento, reversão ou ajuste de engine não comprovadas.
16. **Limites de LLM:** sem capacidade de selecionar compensação imperativa, fabricar recibo, inventar dinheiro, decidir irrevogabilidade, sobrescrever fatos ou executar script arbitrário. Saídas textuais devem passar por validadores de esquema e de permissão.
17. **Teste antes da implementação:** 96 testes candidatos T095-01..T095-96, não executados. A decisão é documento arquitetural; no momento não existem POCs reais com BG2:EE/EEex ou host+2 clientes.

## Exemplo de escolta

O host confirma `PAGAMENTO_10_PO` e `VIAGEM_INICIADA`; o guarda não conclui serviço por evento confirmado. Uma política candidata pode propor **novo reembolso**, sujeito a contrato, recursos e autorização, com novo receipt. O tempo de viagem já gasto e NPCs que viram a escolta não desaparecem. Falha do reembolso deixa a saga parcialmente compensada; estado incerto impede segundo pagamento.

## Consequências

- **Pró:** coerência causal, operações compostas robustas, reparação limitada e auditável, sem retcon automático.
- **Contra/custo:** ledger de etapas, políticas por domínio, idempotência/outbox, reconciliador, revisão de compensabilidades e UX para aprovações.
- **Dependência de SPECS:** classificação de ações, contratos de adaptador, política de titulares, métricas, transições e gates de multiplayer.

## Anotação de arquitetura correlata (não é aprovação de nova DEC)

O idealizador propôs uma **matriz cronológica condicional** que cruza evento oficial, precisão da data DR, geografia, tipos de locais, regras de ativação e efeitos diretos/indiretos. Foi refinada em `docs/96-proposta-matriz-cronologica-condicional-de-eventos-e-repercussoes.md` com dados sintéticos e protótipo unitário independente do jogo. **Essa proposta não constitui aprovação de DEC-096**, a ser deliberada em seguida. Não muda DEC-060–063 nem DEC-023–026.

## Próxima decisão — DEC-096 (em aberto)

**Motor determinístico de ativação temporal/geográfica de eventos e consequências.** A: tabela `IF/ELSE` fixa de eventos; B: LLM interpreta e decide livremente; **C recomendada: catálogo de fatos canônicos versionado + matriz declarativa de regras condicionais + avaliador determinístico por DR/geografia/escopo/estado de campanha, com LLM só para enriquecimento contextual controlado.**
