# ADR-0104 — Grafos determinísticos de obrigações condicionais em acordos multipartes (DEC-109/C)

- **Decisão:** DEC-109, opção **C — APROVADA COMO ARQUITETURA**, 2026-11-07.
- **Discovery:** v10.5.
- **Documento normativo associado:** `docs/109-obrigacoes-condicionais-acordos-multipartes-grafo-de-dependencias-e-gates.md`.
- **Limitação:** não há scheduler contratual, executor de acordos, escrow, hook BG2:EE/EEex ou multiplayer implementado/comprovado. Python, Schema e fixtures são exclusivamente sintéticos.
- **Imutabilidade:** as DEC-060 a DEC-108 são vinculantes; **103 ADRs anteriores devem permanecer byte a byte idênticos** ao pacote v10.4.
- **Referências:** DEC-011/012/019/022/027/028/030/041–046/053/056/060–065/066–074/075–083/089/090/091–095/096–105/106–108.

## Problema

A DEC-107/C permite mediar e aceitar acordos voluntários; a DEC-108/C fiscaliza **cada obrigação** sem confundir vencimento, alegação, prestação host-confirmed e culpa. Em um acordo de três ou mais partes, certas obrigações dependem de **fatos/quantidades/autorizações anteriores** e podem não ser executáveis no momento da assinatura. Uma entrega parcial não satisfaz, por definição, uma cláusula de entrega integral. Uma condição cumprida permite **analisar o próximo passo**, não gastar recursos alheios, comandar NPCs, punir partes nem despachar uma operação automaticamente. É necessário controlar dependências, consentimento de terceiros, concorrência, idempotência, forks e eventuais ciclos.

### Alternativas

- **A — Execução automática em cascata: REJEITADA.** Trata requisitos como autorização e permite transferências/compromissos não confirmados; falhas propagam erros e multiplicam efeitos após save/load.
- **B — Coordenação livre pela LLM: REJEITADA.** Não há prova de entrega, mandato, recurso, prazo ou permissão derivada da plausibilidade narrativa do texto. Não delegar à LLM emenda ou dispensa de obrigações.
- **C — Grafo tipado e determinístico, com gates independentes: APROVADA.** Predicados curados e versionados, snapshots de evidência host-confirmed, avaliação reprodutível, fiscalização não coercitiva, conflito/fairness, revisões e autorizações por etapa.

## Decisão normativa

1. **Ponto de entrada:** apenas `AgreementCommit` autêntico da DEC-107, com todas as partes participantes identificadas, mandatos válidos e consentimento comprovado na versão exata. Minutas, negociações, rumores e consentimentos parciais não ativam grafos.
2. **Grafo versionado:** `AgreementGraph {agreement_id, agreement_revision, graph_revision, campaign_id, branch_id, lineage_id, build_fingerprint, modpack_hash, host_epoch, checkpoint_epoch, policy_revision, term_nodes, dependency_edges}`. Mudar arestas/limiares muda uma revisão committed, não reescreve a anterior.
3. **Nó de obrigação:** `ObligationNode` carrega `term_id`, revisão, responsável, beneficiário, prestação tipada/unidade/quantidade, data DR quando aplicável, ACL, natureza do recurso, provas do aceite e regra de comprovação. Há uma única identidade lógica de cada obrigação no grafo; uma instância NPC/objeto do host não equivale a um nó distinto.
4. **Aresta condicional:** `DependencyEdge {upstream_term, upstream_revision, downstream_term, predicate_kind, threshold, provenance}`. Predicados permitidos no contrato v1: `CONFIRMED_COMPLETE`, `CONFIRMED_AT_LEAST(amount)` **somente se estipulado no acordo**, além de condições DR e de aprovação externa tipadas. Não inferir limites a partir de porcentagens improvisadas pela LLM.
5. **Composição explícita:** o contrato pode usar grupos `ALL`, `ANY` ou `AT_LEAST(k)` aprovados, com semântica tipada e resultado auditável. `ANY` não significa que uma parte pode substituir prestação diferente, salvo cláusula efetivamente aceita; nenhuma condição é inventada no runtime.
6. **Grafo acíclico como padrão v1:** todas as dependências devem referenciar nós existentes da mesma revisão e campanha; rejeitar nós/arestas duplicados, self-edges, referências stale, ciclos e dependências impossíveis. Fluxos cíclicos genuínos deverão virar etapas temporalmente distintas ou subacordos curados com política própria, não ficar presos em retry.
7. **DAG e evidências diferentes:** a topologia prova apenas ordem de precedência; **não** prova que a condição se cumpriu. Avaliar cada predecessor usando receipts autenticados e agregados conforme DEC-108, com idempotência por `action_id/receipt_id`, item, unidade, beneficiário, quantidade e escopo de save.
8. **Três estados separados:** `CONDITION_SATISFIED` (prova da condição), `READY_FOR_AUTHORIZED_PLANNING` (proposta de etapa), `HOST_CONFIRMED_EFFECT` (efeito mecânico após Action Gateway e receipt). Nenhuma implicação automática de um estado para o seguinte.
9. **Entrega parcial não autoriza entrega integral:** seis de dez caixas confirmadas não ativam `CONFIRMED_COMPLETE(10)`. Podem ativar `CONFIRMED_AT_LEAST(6)` **se e somente se** o acordo permitir esse limiar. Alegações, silêncio, boatos e recibos pendentes nunca contam como prestação confirmada.
10. **Proveniência por etapa:** `EvidenceRef` de condição aponta para o receipt de DEC-108, revisão de termo, autor, cronologia DR, escrow ou custódia **se existir capacidade comprovada**, mais histórico de validação. Uma declaração do próprio solicitante não cria um novo comprovante confiável.
11. **Autorizações independentes:** `AgreementCommit` e satisfação de condições não garantem `ActionAuthorization`. Cada etapa pode demandar aceite renovado, ownership, reservas, orçamento, risk gate e consentimento de cada PC afetado, DEC-041–046. Uma parte não assume direitos sobre recursos de outra.
12. **Tempo do mundo:** `earliest_world_tick`, `deadline_world_tick` e janelas de ativação respeitam DEC-022 (`FROZEN/PARTIAL/REALTIME`). O relógio real e timestamps de log não ativam etapa. Prazo vencido não comprova culpa, nem libera recursos automaticamente.
13. **Recursos e concorrência:** consultar apenas registros autenticados de alocação; aplicar reservas, fencing e fairness DEC-093/094. Dois nós não podem consumir o mesmo lote por reutilização do mesmo receipt; transferir um bem em cascata requer novo ato autorizado e recibo próprio.
14. **Dependência bloqueada não cancela acordo:** `WAITING_DEPENDENCIES`, `WAITING_DR_TIME`, `BLOCKED_RESOURCE_CONFLICT`, `BLOCKED_AUTHORIZATION`, `BLOCKED_UNCERTAIN`, `QUARANTINED` são estados de avaliação, não sanções ou descumprimento comprovado.
15. **Falta de prova é incerteza:** observação parcial, atraso ou ausência de recibo não é prova de não entrega, fraude, quebra contratual, culpa ou má-fé. Manter espaço para contraditório, esclarecimento, investigação e renegociação voluntária conforme DEC-107/108.
16. **Impasses e starvation:** ciclos detectados não geram remoção de cláusula, preempção arbitrária ou execução de terceiros. Aplicar DEC-094 para resolução proporcional, mediada e autorizada, registrando alternativas. Uma longa espera não cria direito de posse sobre recursos de PCs.
17. **Fencing de operações incertas:** qualquer predecessor/despacho relevante com estado `PENDING`, `DISPATCHED` ou `UNCERTAIN` impede ativação/reativação consequente até reconciliação; não reenviar, liberar reservas nem declarar quitação por timeout.
18. **Falha parcial e compensação:** com efeito confirmado, preservar fato; eventual compensação DEC-095 é um novo ato, com consentimento, disponibilidade e receipt próprios. Não há rollback global de quests, reputação, entrega ou memória.
19. **Revisões e renegociação:** emenda de quantidade, prazo, ordem, beneficiário, cláusula `ANY`/`ALL` ou dependência gera nova revisão committed por partes competentes. Reavaliar propostas stale via CAS/epoch; fatos anteriores permanecem no ledger histórico.
20. **Status de verificação versus decisão social:** `READY`, `DUE`, `PARTIAL`, `BLOCKED`, `CONTESTED` não autorizam reputação negativa, prisão, mandado, confisco, execução compulsória ou sanção. DEC-078–082/104–108 preservadas.
21. **Sigilo:** `AgreementGraph` pode conter obrigações privadas, nomes de fontes, rotas e valores. Os destinatários obtêm apenas vistas autorizadas; logs, caches, prompts e mensagens não vazam ledger bruto. LLM apenas redige material permitido.
22. **Isolamento:** campaign/branch/lineage, host/checkpoint epoch, versão de build/modpack, data DR e revisões de acordo são todos vinculados. Recuperar save anterior não reexecuta etapas nem mistura receipts entre ramos.
23. **SPECS/POCs antes do motor:** exigir testes de capabilities específicas (consulta, transferência, reserva, estado de quest, execução, multiplayer com dois clientes). Falha ou capacidade desconhecida = nenhuma mutação; regra lógica pode continuar como proposta.
24. **Sem autonomia para execução:** código determinístico avalia o grafo e produz somente planos auditáveis. Nenhum esquema, fixture, contrato ou texto de NPC concede poderes de host. LLM nunca decide liberar recursos, cobrar ou punir.

## Exemplo normativo fictício — Athkatla

- A aceita entregar **10 caixas** a B. B aceita pagar **50 moedas** a C **após entrega integral comprovada**. C aceita disponibilizar uma escolta **após pagamento comprovado** e disponibilidade legítima. Cada obrigação é uma entidade distinta do grafo.
- Host confirma entrega de **6 caixas**: o nó A fica parcialmente comprovado; o nó B mantém `WAITING_DEPENDENCIES`; o nó C também aguarda. Um claim de entrega das quatro restantes não altera o estado.
- Se houver receipt autenticado das **quatro** restantes, B se torna `READY_FOR_AUTHORIZED_PLANNING` **apenas**. Ainda exige autorização, recurso real e Action Gateway.
- O pagamento confirmado por recibo independente poderá habilitar a revisão da escolta, jamais causar teleporte/emprego automático de guardas.
- Com política expressa permitindo `CONFIRMED_AT_LEAST(6)`, B poderia tornar-se elegível após seis unidades, mas **somente na revisão do acordo que contém a cláusula**.

## Artefatos, testes e pendências

- Doc. normativo 109 e `examples/chronology/conditional_obligations_{reference.py,v1.synthetic.json,v1.candidate.schema.json}` e `test_conditional_obligations_reference.py`. Exemplos e testes **SYNTHETIC_TEST**, não conectados a engine, não autenticam recibos reais.
- **168 cenários T109-001..T109-168:** candidatos para POC/integração, **NÃO EXECUTADOS** em BG2:EE/EEex, bridge e host multiplayer.
- **DEC-110 EM ABERTO:** garantias condicionais e custódia de recursos (*escrow*) em acordos multipartes. Não implementar custody/escrow por implicação desta DEC-109.

## Critérios de aceite futuro

Mesmo grafo/receipts/política/branch produzem decisão e `proposal_key` idênticos independentemente da ordem de iteração; ciclos são bloqueados; pedidos não injetam grant, receipt nem mandato; seis de dez não satisfaz entrega integral; nenhuma transição lógica despacha ações; efeitos irreversíveis passam por Action Gateway e receipts; após save/load/timeout não há duplicação; dados privados não chegam a destinatários não autorizados; duas sessões cliente confirmam consistência sobre build congelada. Até lá, estado **aprovado apenas como arquitetura**.
