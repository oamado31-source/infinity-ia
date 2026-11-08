# ADR-0103 — Cumprimento verificável, fiscalização causal e contestação de acordos voluntários (DEC-108/C)

- **Decisão:** DEC-108, alternativa **C — APROVADA COMO ARQUITETURA** em 2026-11-07.
- **Discovery:** v10.4. Não corresponde a implementação em BG2:EE/EEex, bridge, host ou multiplayer.
- **Preservação:** DEC-060 a DEC-107 vinculantes; **102 ADRs anteriores intocados byte a byte**.
- **Contrato normativo complementar:** `docs/108-cumprimento-de-acordos-obrigacoes-prazos-recibos-e-contestacao-causal.md`.
- **Referências principais:** DEC-011/012/022/027/028/030/041/042/045/046/053/056/060–065/066/068–074/075/077–082/083/089/090/091–095/096/098/099/100–105/106/107.

## Contexto

A DEC-107/C define direito de resposta e mediação voluntária e admite **minutas**, **aceites por parte e por termo** e **acordos efetivamente confirmados**. Uma vez firmado um acordo, sua execução deve ser acompanhada sem pressupor que uma obrigação vence por relógio de parede, que uma promessa equivale à entrega, que o silêncio significa descumprimento deliberado ou que o texto de uma cláusula confere poderes mecânicos ao Infinity AI. O mundo pode ter transferências parciais, pagamentos contestados, atrasos, dificuldades materiais, restauração de saves e alterações legítimas por renegociação. Uma parte pode alegar cumprimento sem haver evidência conclusiva.

## Alternativas avaliadas

**A — Execução automática por prazo/termo: rejeitada.** Riscos de transferência de propriedade sem recibos, recursos inexistentes, confusão entre pacto e autorização de motor, penalidades inventadas e duplicação após reload.

**B — LLM determina cumprimento, inadimplência e sanções: rejeitada.** Um texto convincente não autentica entrega, recibo, consentimento, motivo de atraso, força maior ou autoridade jurisdicional. A LLM não é fiscal, juiz nem executor mecânico.

**C — Monitoramento determinístico, verificável e não coercitivo: APROVADA.** As obrigações versionadas são observadas por evidências e receipts autenticados, com prazos no relógio DR, cumprimento parcial, alegações e contraditório separados, propostas limitadas de esclarecimento/renegociação e host gates para efeitos reais.

## Invariantes normativas

1. **Só acordo committed é elegível.** `SettlementDraft`, proposta, sessão de mediação, aceite informal ou promessa verbal não produzem automaticamente obrigação executável. Antes de monitorar, verificar `AgreementCommit` autenticado, consentimento independente de todos os titulares, mandatos e revisões exatas (DEC-107).
2. **Granularidade por obrigação.** `AgreementTerm` inclui `term_id`, `term_revision`, tipo (`DELIVER_GOODS`, `PAY`, `PUBLISH_CORRECTION`, `PERFORM_SERVICE`, `OTHER_CURATED`), titular da obrigação, beneficiário, recurso tipado, unidade, quantidade ou condição verificável, prazo DR, pré-condições, prova de aceitação, ACL e riscos. Acordo não cria autoridade sobre a propriedade alheia.
3. **Separar eventos e afirmações.** `ObligationDue`, `PerformanceClaim`, `EvidenceSubmission`, `HostPerformanceReceipt`, `ReceiptValidation`, `FulfillmentAssessment`, `BreachAllegation`, `DisputeRecord`, `AmendmentProposal` e `TermAmendmentCommit` são objetos distintos. Alegação de entrega não é prova; análise não é recibo mecânico.
4. **Cumprimento parcial.** Somar apenas recebimentos/transferências independentes, válidos, não revogados e comprovadamente vinculados ao termo, unidade, beneficiário, branch, checkpoint/epoch e revisão. Um recibo repetido não duplica quantidades. A multiplicidade de boatos não equivale a recebimento.
5. **Sem inadimplência automática.** Prazo transcorrido significa `DUE_FOR_REVIEW` ou `OVERDUE_UNVERIFIED`, **não culpa, fraude, má-fé, punição, confisco, reputação negativa ou condenação**. Ausência de prova de entrega não constitui prova de não entrega. Status em disputa mantém incerteza.
6. **Prazos DR.** Datas e janelas vinculadas ao relógio da campanha (`FROZEN/PARTIAL/REALTIME`, DEC-022). O relógio do sistema, a data de criação do log ou a passagem de tempo real não adiantam deadlines; mês/dia desconhecidos não são fabricados.
7. **Entrega mecânica e claims independentes.** Uma parte pode declarar `DELIVERED`, o beneficiário pode declarar `NOT_RECEIVED`, e ambos permanecem na controvérsia até observação adequada. Para bens, moedas e inventários mecânicos, somente `HostPerformanceReceipt` autenticado pode sustentar entrega confirmada.
8. **Recibos com provenance.** `receipt_id`, action id, hash da operação, quantidade, unidade, proprietário de origem e destino, build/modpack, campaign/branch/lineage, host/checkpoint epochs, `world_tick`, status e assinatura/canal autenticado; verificar identity, ownership, escopo, monotonicidade, idempotência, source capability e conflito de recibos.
9. **Estado assinado versus estado relatado.** Receipt `DISPATCHED`, `UNCERTAIN`, `FAILED`, `CANCELLED`, ausente ou não reconhecido ≠ `CONFIRMED`. Não fazer retry cego, liberar reservas ou presumir restituição; reconciliar DEC-011/012/053/093–095.
10. **ACL e mínimo necessário.** Provas de cumprimento não divulgam automaticamente nomes verdadeiros, fontes protegidas, endereços de refúgios, itinerários, contas privadas ou documentos não autorizados. Notificações, relatórios e prompts dependem de view redigida por audiência.
11. **Contraditório genuíno.** Alegação de cumprimento/descumprimento abre canal contextual para esclarecer, anexar evidências e contestar. Falta de resposta não é admissão. Só autoridades e representantes com mandato curado podem firmar manifestação vinculante; PCs exigem aprovação do proprietário.
12. **Renegociação não coercitiva.** Pedido de extensão, ajuste de quantidade, troca de beneficiário, parcelamento ou substituição de obrigação gera uma **proposta**; não altera prazos ou termos committed até novo aceite explícito **por termo e revisão**. DEC-107 continua válida; revogação de autorização impede passos futuros, não desfaz ações já confirmadas.
13. **Dificuldade e força maior.** Circunstância alegada (`force_majeure`) pode motivar exame ou renegociação, não extingue obrigação automaticamente nem apaga dano; dependerá de fatos, escopo jurídico/faccional, evidências, consentimento e gates aplicáveis.
14. **Separação de status.** Status operacional (`WAITING`, `DUE`, `OVERDUE`, `PARTIAL`, `COMPLETE_CANDIDATE`, `UNCERTAIN`, `CONTESTED`) não equivale a decisão de culpa. O modelo deverá admitir `UNKNOWN` e `QUARANTINED` quando faltar prova.
15. **Sem penalidades implícitas.** Nunca aplicar sanções, reputação, mandados, juros, execuções, arrestos, multas ou confisco por cronômetro, LLM ou relatório. Procedimentos com competência institucional seguem DEC-078–082; reparação DEC-081/095; reputação DEC-030/104–106.
16. **Titularidade e recursos.** Qualquer transferência exige disponibilidade, ownership por campo e instância, capabilities e recibo do host. Uma simulação narrativa não credita recursos nativos nem altera containers ou flags de quests (DEC-099–102).
17. **Conflitos de simultaneidade.** Recursos e participantes compartilhados respeitam reservas/fencing DEC-093/094; o mesmo lote não cumpre duas obrigações por referência duplicada sem contrato de divisão e comprovantes independentes.
18. **Checkpoints e forks.** Acordos, obrigações, recibos, alegações, avisos e emendas permanecem isolados por `campaign_id/branch_id/lineage_id`, `host_epoch/checkpoint_epoch`, build e revision. Restauração de save dispara reconciliação antes de declarar saldo disponível ou reenviar pagamento.
19. **Histórico imutável.** Um aditamento é um evento adicional e uma nova revisão; não altera retroativamente entregas, promessas ou violações alegadas. Compensações são eventos novos quando autorizadas (DEC-095). Conhecimento de NPCs não é apagado (DEC-104/105).
20. **Idempotência.** Chaves por `agreement_id/term_id/revision/action_id/epoch/campaign/branch`; deduplicar receipts confirmados e separar planejamento, despacho e commit. Ajustes de versão invalidam propostas stale, não criam entregas novas.
21. **Regras determinísticas antes da LLM.** Um avaliador tipado prepara apenas recomendações: `WAIT_FOR_DUE`, `PROPOSE_EVIDENCE_REQUEST`, `PROPOSE_PARTIAL_REVIEW`, `PROPOSE_CLARIFICATION`, `PROPOSE_CONTESTED_REVIEW`, `PROPOSE_RENEGOTIATION`, `OBSERVE_FULFILLMENT_CANDIDATE`, `QUARANTINE_UNCERTAIN`. A LLM pode redigir linguagem autorizada, sem declarar pagamento, culpa ou quitação.
22. **Competência limitada.** O coordenador de cumprimento não cria lei, tribunal, representação, vínculo PC, sanção, poderes judiciais ou direitos sobre bem. Mandatos já revogados ou expirados bloqueiam novos atos.
23. **Recebimento de notícias ≠ efeito sobre crença.** Aviso enviado não prova recebido, entrega não prova percepção e percepção não impõe acordo ou reputação. O ledger de difusão DEC-105 registra essas fases.
24. **Fail closed.** Ausência de agreement commit, identificador inválido, quantidades inconsistentes, recibo forjado, capacidades não comprovadas, ACL contraditória, mismatch de branch/epoch, prazo sem precisão ou órgão incompetente causam `DENIED/UNKNOWN/QUARANTINED`. Nada é executado.
25. **Sem POC de motor.** Casos T108-001..160 são especificações candidatas NÃO EXECUTADAS em BG2:EE/EEex/multiplayer. Os arquivos em `examples/chronology` são testes e dados inteiramente sintéticos.

## Contratos mínimos

| Registro | Campos e autoridade | Garantia |
|---|---|---|
| `AgreementCommit` | agreement/version/party acceptances + provenance do registry (DEC-107) | Não inferir de minuta |
| `AgreementTerm` | term/revision/type/obligor/beneficiary/unit/amount/due_tick/classification | Cada termo é isolado e tipado |
| `DueSchedule` | tick DR, clock_mode, precisão, grace policy curada | Wall-clock não define vencimento |
| `PerformanceClaim` | id/party/term/alleged_amount/time/statement/evidence_refs | Alegação contestável, sem efeito host |
| `HostPerformanceReceipt` | authenticated status, action, amount, unit, parties, epochs, tick | Só comprovado após validação externa |
| `FulfillmentLedger` | allocated receipt ids, confirmed_amount, disputed_amount, reconciliation_state | Sem double counting |
| `BreachAllegation` | party/grounds/scope/time/evidence | Não é veredito |
| `TermDispute` | contested claims, counterevidence, notice status, response opportunity | Silêncio não prova culpa |
| `AmendmentProposal` | changed terms, consent requests, version, resources, deadline | Não modifica commit |
| `TermAmendmentCommit` | accepted revision/parties/mandates/receipt | Só então vigora novo termo |
| `ObligationAudit` | events append-only, restricted provenance, safe summary | Sem vazamento de fonte/PC |

## Exemplo de referência, inteiramente fictício

Acordo committed prevê 10 caixas até determinado `world_tick`. O host validado confirma a entrega de seis caixas. O sistema registra **seis unidades confirmadas e quatro ainda não comprovadas**, prepara pedido de esclarecimento e permite contestação e renegociação. Não assume má-fé, não transfere as outras quatro caixas, não penaliza a parte nem devolve dinheiro automaticamente. O fato de faltar quatro unidades de comprovação não significa prova absoluta de não entrega.

## Decisões anteriores e temas pendentes

Permanecem abertas DEC-006/007/013/015/017/018, bem como POCs EEex/bridge/cooperativo. A DEC-108 não altera contratos originais de direitos, ownership, conhecimento privado, confiança ou economia. **Próxima DEC-109 em discussão:** obrigações condicionais e encadeadas em acordos multipartes. Alternativas: A disparo automático em cadeia; B encadeamento arbitrado pela LLM; **C grafo determinístico de dependências, autorizações por obrigação, condições host-confirmed, time DR e prevenção de deadlocks sem execução automática**.

## Consequências e critérios de aceite

- Permite narrativas com contratos, entregas parciais, prazos e contestações, mantendo incerteza e autonomia.
- Exige protótipos separados para observação de inventário/transferências, comunicação com NPCs, tempo DR, save/load e dois clientes.
- A integração mecânica só será considerada funcional após testes reais com build/modpack fixados, host recibos e reconciliação de falha.
