# 109 — DEC-109/C: grafo determinístico de obrigações condicionais em acordos multipartes

**Status:** APROVADO COMO ARQUITETURA, 2026-11-07 · Discovery v10.5 · ADR-0104. **Não implementado no BG2:EE/EEex; POCs e multiplayer pendentes.** Mantém DEC-060–108 e seus 103 ADRs anteriores byte a byte intactos.

## 1. Motivação e fronteiras

A DEC-107/C define mediação voluntária, consentimento e commit de acordo; a DEC-108/C fiscaliza cláusulas individuais, com comprovantes host-confirmed, saldo parcial e contraditório. A DEC-109/C acrescenta **dependências e condições** entre cláusulas pertencentes a várias partes. O resultado do avaliador **não é um comando**: detectar satisfação torna uma obrigação elegível à revisão autorizada, não executa pagamentos, deslocamentos, sanções ou alterações de quests. A abordagem evita que acordos sejam usados como um novo canal de mutação mecânica, autorização ou spoilers. A política é local-first e código primeiro (DEC-014), sem agentes LLM oniscientes.

## 2. Camadas e registros

| Camada | Registro canônico | Não implica |
|---|---|---|
| Acordo committed | `AgreementCommit` DEC-107; participantes, revisões, mandatos | Prestação cumprida, autorização de usar recursos |
| Termo condicional | `ObligationNode` tipado; `term_id/revision` | Relação com mecanismo de engine não testado |
| Dependência | `DependencyEdge`; limiar curado, operador explícito | Execução automática de seu destino |
| Prestação | `HostPerformanceReceipt` autenticado DEC-108 | Verdade de declarações não comprovadas |
| Avaliação | `ConditionAssessment`/`GraphEvaluation` determinísticos | Validade de sanção, consentimento ou cobrança |
| Planejamento | `EligibleActionProposal`, política e quorum de atores | Comando enviado, pagamento concluído |
| Execução | `ActionGatewayRequest` e `HostReceipt` DEC-011/012 | Conhecimento universal de NPCs |
| Estado narrativo | eventos/versionamento/ACL | Apagar memória, reverter fatos por decreto |

## 3. Modelo de dados normativo

`AgreementGraph`: `agreement_id`, `agreement_revision`, `graph_revision`, `campaign_id`, `branch_id`, `lineage_id`, `knowledge_pack_id`, `build_fingerprint`, `modpack_hash`, `host_epoch`, `checkpoint_epoch`, `policy_revision`, `world_tick`, `party_roles`, `commit_receipt`, `terms[]`, `dependencies[]`, `acl`, `provenance`, `content_hash`.

`ObligationNode`: `term_id`, `term_revision`, `agreement_ref`, `obligor_id`, `beneficiary_id`, `resource_type`, `resource_unit`, `required_quantity` (decimal determinístico, não float), `earliest_world_tick`, `due_world_tick` opcional, `conditions`, `reservation_ref`, `acceptance_proofs`, `scope`, `status` e `risk_category`. Não autorizar contas, itens ou NPCs além da titularidade realmente comprovada.

`DependencyEdge`: `upstream_term_id`, `upstream_revision`, `downstream_term_id`, `predicate` (`CONFIRMED_COMPLETE`, `CONFIRMED_AT_LEAST`, `DR_TIME_REACHED`, `EXTERNAL_AUTHORIZATION_CONFIRMED`), `threshold` tipado, `combiner_group_id`, `provenance`, `policy_version`. O exemplo Python implementa apenas os dois primeiros predicados e `earliest_world_tick` separadamente; a lista completa é **contrato candidato para SPECS**, não funcionalidade do exemplo.

`GateGroup`: `ALL`, `ANY`, `AT_LEAST(k)` com `minimum`, membros e semântica aprovada no acordo; composição e alternativas não são inferidas a partir de conversas. Resolução de cláusulas ambíguas ocorre por curadoria ou emenda voluntária, nunca por interpretação LLM que muda obrigação.

`TrustedEvidenceLedger`: `receipt_id`, `action_id`, `term_id/revision`, quantity, unit, from/to, source authority, campaign/branch/lineage, host/checkpoint epoch, build, DR tick, status, signature/channel, content hash e causal parents. A fonte confiável é o host ou serviço autenticado compatível, jamais o corpo da requisição ao avaliador.

`GraphEvaluation`: `agreement_revision`, `policy_revision`, `graph_digest`, `term_id/revision`, `predicate_evidence_refs`, `satisfied_count`, `status`, `reason`, `proposal_key`, `expected_host_epoch`, `expected_checkpoint_epoch`; não contém nenhuma autorização mecânica implícita.

## 4. Estados, regras e decisão tipada

- `UNKNOWN`: termo não encontrado/observação incompleta; não supor conclusão negativa.
- `WAITING_DEPENDENCIES`: pré-condições confirmadas ainda insuficientes.
- `WAITING_DR_TIME`: dependências satisfeitas, mas a janela DR não abriu.
- `BLOCKED_UNCERTAIN`: ações relevantes in-flight/`DISPATCHED`/`UNCERTAIN`, exigindo reconciliação.
- `BLOCKED_RESOURCE_CONFLICT`, `BLOCKED_RESOURCE_UNAVAILABLE`: reservas/recursos indisponíveis.
- `BLOCKED_AUTHORIZATION`: titular ou mandato não autorizou a etapa específica.
- `BLOCKED_AGREEMENT`, `BLOCKED_STALE`: acordo não committed ou revisões/política incompatíveis.
- `QUARANTINED`: grafo inválido, receipt conflitante, identidade/escopo incorreto ou ciclos.
- `READY_FOR_AUTHORIZED_PLANNING`: condições suficientes para discutir/solicitar a próxima ação, **sem despacho**.
- `COMPLETE_CONFIRMED`: prestação daquela obrigação comprovada por evidências adequadas, **sem conceder reputação, sanção ou efeitos externos**.

### Algoritmo normativo

1. Validar contexto autenticado do host, branch/lineage, build/modpack/epoch, revisão do acordo, aceite de todos e política. A requisição não escolhe seus próprios grants, credenciais ou receipts.
2. Validar termos/revisões/quantidades/unidades, existência e tipagem de todas as arestas. Bloquear duplicatas e loops (DAG na versão 1).
3. Detectar ações in-flight e reservas incertas; enquanto pendentes, bloquear transições causais que poderiam duplicar movimentos, pagamentos ou alocação.
4. Construir ordenação topológica estável, independente da ordem de inserção; processar receipts com chave de ação e prova, rejeitando hashes/ids incompatíveis, unidades erradas, escopos de outro save e contagem dupla.
5. Avaliar predicados curados `CONFIRMED_COMPLETE` e `CONFIRMED_AT_LEAST` com decimais exatos, nunca com resumo LLM. `ALL`/`ANY`/`AT_LEAST(k)` só se previsto contratualmente.
6. Verificar `earliest_world_tick` no calendário DR do host e relógio `FROZEN/PARTIAL/REALTIME`. Tempo de parede não adianta vencimento nem ativa obrigações.
7. Verificar, por etapa, consentimento do titular, legitimidade do representante, escopo ACL, ownership, reservas/fencing DEC-093/094, risco DEC-027 e capacidade testada DEC-099–102.
8. Gerar **somente** avaliação estável e `EligibleActionProposal`, idempotente. Nova execução no host só pode ser solicitada por outro contrato tipado do Action Gateway, com aprovação e recibo específicos.
9. Registrar estado proposto, prova/contradição/lineage e divulgar apenas vistas mínimas autorizadas; não gerar rumor, perda de reputação ou sanção por estar em espera.
10. Mudança de regra contratual exige nova revisão committed, nova avaliação e CAS; não reescrever receipts, eventos ou memoriais anteriores.

## 5. Cenários exemplares sintéticos

| Obrigação | Prestação | Condição | Estado com seis caixas entregues |
|---|---|---|---|
| A, Guilda A → B | Entrega de 10 caixas | Compromisso vigente | `PARTIAL_CONFIRMED` no ledger DEC-108 |
| B, Guilda B → C | 50 moedas | A confirmada por inteiro | `WAITING_DEPENDENCIES` |
| C, Guilda C → A | Escolta | B confirmada por recibo | `WAITING_DEPENDENCIES` |

Se A obtiver recibo autenticado de mais **4** caixas, B passa a ser `READY_FOR_AUTHORIZED_PLANNING`, permanecendo sujeito a recursos, autorização e host. C só avança após receipt independente do pagamento. Uma cláusula expressa `CONFIRMED_AT_LEAST(6)` poderia gerar outra elegibilidade, **mas não pode ser acrescentada automaticamente**. Tentar usá-la sem aceite novo dá `BLOCKED_STALE` ou `QUARANTINED`.

## 6. Idempotência, salvamento e conflitos

- Dedup por `receipt_id` e `action_id` com evidência idêntica; duplicatas conflitantes entram em quarentena. Não dividir um mesmo receipt entre dois termos sem transferência e critérios contratuais próprios.
- Fencing por agreement/graph/term revisions, save lineage, host/checkpoint epoch, hash de build e modpack. Atualização de um contrato invalida proposals da versão antiga; não desfaz pagamentos confirmados.
- Em restauração de save, reconciliar primeiro. Uma ação enviada antes do rollback pode persistir no host ou em outra branch; `UNCERTAIN` não é confirmação nem licença para retry.
- Detecção de ciclo, self-loop, dependência inexistente e dois nós com mesma identidade é falha de curadoria/contrato, não autorização para o runtime apagar cláusulas.
- Convites de mediação e notificações de prazo não são proofs de execução. Prazo vencido não converte bloqueio em culpa, má-fé ou obrigação coercitiva.
- Se for necessário resolver operação complexa parcialmente confirmada, usar Saga DEC-095 com compensações novas e autorizadas, nunca rollback geral.

## 7. Segurança, privacidade e autonomia

- Nenhuma operação executa em nome de PC ausente sem delegação válida de escopo específico; um pacto não transfere controle de PCs para NPCs ou LLM.
- Identidades/endereços de fontes protegidas e termos sigilosos não vazam para documentos externos, rumores, caches, logs, prompts ou NPCs sem ACL.
- O grafo não entrega objetos nem coleta pagamentos. Escrow/custódia de garantia são tema **DEC-110 em aberto**.
- A LLM pode converter status autorizados em explicações e propostas de comunicação, jamais arbitrar o significado técnico de cláusulas, prova de recebimento, vencimento, culpa, dispensa, direito de posse ou mudança de compromisso.
- A aprovação arquitetural não garante que a build suporte leitura/escrita desses elementos. Sem capabilities testadas na build exata, não promover proposta a comando mecânico.

## 8. Especificação de POC e critérios de aceite

- Fixar Windows, BG2:EE build, EEex, bridge, modpack, servidor e dois clientes; testar contrato A→B→C, seis/dez, dez/dez, pagamento 50 e escolta autorizada, em saves isolados.
- Validar execução separada do gateway: pagamento apenas após host receipt, sem duplicação após reload/timeout, sem alteração de quest ou inventory nativos fora de allowlist.
- Testar restauração para epoch anterior, duas sessões concorrentes, deadlock com recurso compartilhado, operador OR apenas quando curado, atores sem mandato, consentimento revogado e provas contestadas.
- Confirmar que logs e relatórios respeitam as ACL e os NPCs não recebem informações de todas as cláusulas automaticamente.
- Medir performance e determinismo de DAG com 64 nós; ultrapassar orçamento bloqueia e gera proposta de redução, não execução parcial silenciosa.
- Critérios só viram implementação após testes funcionais, adversariais, integridade de save e confirmação real de host + dois clientes.

## 9. Matriz de testes candidatos (NÃO EXECUTADOS)

**T109-001..T109-168 — TODOS NÃO EXECUTADOS no BG2:EE/EEex multiplayer.** Os testes de `conditional_obligations_reference.py` são sintéticos, não capacidades do host.

| ID | Área | Cenário candidato | Estado |
|---|---|---|---|
| T109-001 | Commit, escopo e mandatos | minuta sem commit não habilita etapas | **NÃO EXECUTADO** |
| T109-002 | Commit, escopo e mandatos | assinatura de apenas duas das três partes não fecha acordo | **NÃO EXECUTADO** |
| T109-003 | Commit, escopo e mandatos | grant assinado em outra branch é recusado | **NÃO EXECUTADO** |
| T109-004 | Commit, escopo e mandatos | mandato revogado impede aprovações futuras | **NÃO EXECUTADO** |
| T109-005 | Commit, escopo e mandatos | PC ausente não assume cláusula por silêncio | **NÃO EXECUTADO** |
| T109-006 | Commit, escopo e mandatos | versão de termo stale bloqueia avaliação | **NÃO EXECUTADO** |
| T109-007 | Commit, escopo e mandatos | commit de outro acordo não é reutilizável | **NÃO EXECUTADO** |
| T109-008 | Commit, escopo e mandatos | aceite de mediação não equivale ao commit do acordo | **NÃO EXECUTADO** |
| T109-009 | Nós e identificação | termo de pagamento com unidade de mercadoria é recusado | **NÃO EXECUTADO** |
| T109-010 | Nós e identificação | obrigor desconhecido impede ação | **NÃO EXECUTADO** |
| T109-011 | Nós e identificação | beneficiário desconhecido impede ação | **NÃO EXECUTADO** |
| T109-012 | Nós e identificação | termos de mesmo ID geram quarentena | **NÃO EXECUTADO** |
| T109-013 | Nós e identificação | mesma entidade com dois aliases não duplica obrigação | **NÃO EXECUTADO** |
| T109-014 | Nós e identificação | quantidade zero é inválida para prestação positiva | **NÃO EXECUTADO** |
| T109-015 | Nós e identificação | unidade sem curadoria não é convertida pela LLM | **NÃO EXECUTADO** |
| T109-016 | Nós e identificação | nó do outro ramo é excluído do grafo | **NÃO EXECUTADO** |
| T109-017 | Arestas, DAG e topologia | aresta sem predecessor comprovado é recusada | **NÃO EXECUTADO** |
| T109-018 | Arestas, DAG e topologia | self-loop é bloqueado | **NÃO EXECUTADO** |
| T109-019 | Arestas, DAG e topologia | ciclo A→B→C→A é bloqueado | **NÃO EXECUTADO** |
| T109-020 | Arestas, DAG e topologia | arestas duplicadas não causam múltiplo desconto | **NÃO EXECUTADO** |
| T109-021 | Arestas, DAG e topologia | dependência com revisão antiga é recusada | **NÃO EXECUTADO** |
| T109-022 | Arestas, DAG e topologia | nó inexistente não gera execução implícita | **NÃO EXECUTADO** |
| T109-023 | Arestas, DAG e topologia | ordem de entrada dos nós não muda a resposta | **NÃO EXECUTADO** |
| T109-024 | Arestas, DAG e topologia | profundidade excessiva excede orçamento seguro | **NÃO EXECUTADO** |
| T109-025 | ALL, ANY e quórum | ALL com uma condição falsa permanece aguardando | **NÃO EXECUTADO** |
| T109-026 | ALL, ANY e quórum | ANY contratado com um predecessor comprovado habilita revisão | **NÃO EXECUTADO** |
| T109-027 | ALL, ANY e quórum | ANY ausente no acordo não pode ser presumido | **NÃO EXECUTADO** |
| T109-028 | ALL, ANY e quórum | AT_LEAST(k) aplica k curado | **NÃO EXECUTADO** |
| T109-029 | ALL, ANY e quórum | k maior que o número de fontes causa quarentena | **NÃO EXECUTADO** |
| T109-030 | ALL, ANY e quórum | quórum de atores não substitui assinatura de terceiros | **NÃO EXECUTADO** |
| T109-031 | ALL, ANY e quórum | condição alternativa não transfere recurso de outro titular | **NÃO EXECUTADO** |
| T109-032 | ALL, ANY e quórum | mudança ALL→ANY exige novo commit | **NÃO EXECUTADO** |
| T109-033 | Prova de cumprimento | seis de dez não satisfaz entrega integral | **NÃO EXECUTADO** |
| T109-034 | Prova de cumprimento | dez de dez com dois receipts válidos satisfaz condição | **NÃO EXECUTADO** |
| T109-035 | Prova de cumprimento | claim de dez caixas sem host receipt não satisfaz | **NÃO EXECUTADO** |
| T109-036 | Prova de cumprimento | recibo de pagamento não comprova mercadoria | **NÃO EXECUTADO** |
| T109-037 | Prova de cumprimento | receipt com beneficiário divergente é rejeitado | **NÃO EXECUTADO** |
| T109-038 | Prova de cumprimento | receipt sem autenticação é rejeitado | **NÃO EXECUTADO** |
| T109-039 | Prova de cumprimento | receipt com quantidade negativa é rejeitado | **NÃO EXECUTADO** |
| T109-040 | Prova de cumprimento | vários rumores não substituem comprovante único | **NÃO EXECUTADO** |
| T109-041 | Cumprimento parcial | cláusula integral não aceita limiar de seis | **NÃO EXECUTADO** |
| T109-042 | Cumprimento parcial | CONFIRMED_AT_LEAST(6) curado pode habilitar revisão | **NÃO EXECUTADO** |
| T109-043 | Cumprimento parcial | limiar maior que a obrigação é inválido | **NÃO EXECUTADO** |
| T109-044 | Cumprimento parcial | entrega parcial não encerra acordo | **NÃO EXECUTADO** |
| T109-045 | Cumprimento parcial | quitação parcial não libera garantia não prevista | **NÃO EXECUTADO** |
| T109-046 | Cumprimento parcial | percepção de entrega difere de posse efetiva | **NÃO EXECUTADO** |
| T109-047 | Cumprimento parcial | fração de unidade obedece precisão tipada | **NÃO EXECUTADO** |
| T109-048 | Cumprimento parcial | duas prestações do mesmo receipt não podem ser contadas | **NÃO EXECUTADO** |
| T109-049 | Duplicaçao e idempotência | mesmo receipt idêntico é contado apenas uma vez | **NÃO EXECUTADO** |
| T109-050 | Duplicaçao e idempotência | mesmo receipt id com conteúdo divergente é quarentenado | **NÃO EXECUTADO** |
| T109-051 | Duplicaçao e idempotência | action_id usado por dois receipts distintos é recusado | **NÃO EXECUTADO** |
| T109-052 | Duplicaçao e idempotência | mesmo action_id após save/load não gera segundo envio | **NÃO EXECUTADO** |
| T109-053 | Duplicaçao e idempotência | dois termos não gastam mesmo lote sem autorização | **NÃO EXECUTADO** |
| T109-054 | Duplicaçao e idempotência | retry por timeout não executa pagamento | **NÃO EXECUTADO** |
| T109-055 | Duplicaçao e idempotência | chave de proposta estável preserva dedup | **NÃO EXECUTADO** |
| T109-056 | Duplicaçao e idempotência | revisão antiga não permite repetir quitação | **NÃO EXECUTADO** |
| T109-057 | Prazos e relógio DR | prazo de parede não inicia obrigação DR | **NÃO EXECUTADO** |
| T109-058 | Prazos e relógio DR | modo FROZEN não progride obrigação por tempo real | **NÃO EXECUTADO** |
| T109-059 | Prazos e relógio DR | PARTIAL depende de world_tick autorizado | **NÃO EXECUTADO** |
| T109-060 | Prazos e relógio DR | REALTIME usa relógio DR do host, não sistema civil | **NÃO EXECUTADO** |
| T109-061 | Prazos e relógio DR | início de prazo futuro mantém estado de espera | **NÃO EXECUTADO** |
| T109-062 | Prazos e relógio DR | mês incerto não vira primeiro dia inventado | **NÃO EXECUTADO** |
| T109-063 | Prazos e relógio DR | tempo de viagem restringe início de escolta | **NÃO EXECUTADO** |
| T109-064 | Prazos e relógio DR | prazo vencido não implica culpa automática | **NÃO EXECUTADO** |
| T109-065 | Consentimento e titulares | condição satisfeita não concede grant de gasto | **NÃO EXECUTADO** |
| T109-066 | Consentimento e titulares | grants devem vir de registro independente do pedido | **NÃO EXECUTADO** |
| T109-067 | Consentimento e titulares | mandato expirado impede aditamento | **NÃO EXECUTADO** |
| T109-068 | Consentimento e titulares | PC sem aprovação não realiza transação | **NÃO EXECUTADO** |
| T109-069 | Consentimento e titulares | autorização de escolta não autoriza pagamento | **NÃO EXECUTADO** |
| T109-070 | Consentimento e titulares | assinatura de uma facção não vincula outra | **NÃO EXECUTADO** |
| T109-071 | Consentimento e titulares | recusa legítima preserva o acordo em controvérsia | **NÃO EXECUTADO** |
| T109-072 | Consentimento e titulares | LLM não pode inventar assinatura por narrativa | **NÃO EXECUTADO** |
| T109-073 | Recursos e concorrência | saldo de ouro inexistente bloqueia planejamento | **NÃO EXECUTADO** |
| T109-074 | Recursos e concorrência | guarda reservado em outra operação causa conflito | **NÃO EXECUTADO** |
| T109-075 | Recursos e concorrência | fencing impede dupla reserva do mesmo lote | **NÃO EXECUTADO** |
| T109-076 | Recursos e concorrência | fairness não concede posse de recursos alheios | **NÃO EXECUTADO** |
| T109-077 | Recursos e concorrência | uma operação independente continua normalmente | **NÃO EXECUTADO** |
| T109-078 | Recursos e concorrência | reserva de guarda não equivale a guarda contratado | **NÃO EXECUTADO** |
| T109-079 | Recursos e concorrência | prioridade HIGH exige autorização adicional | **NÃO EXECUTADO** |
| T109-080 | Recursos e concorrência | cancelamento não libera recurso in-flight | **NÃO EXECUTADO** |
| T109-081 | Reconciliação e operações incertas | receipt DISPATCHED não comprova execução | **NÃO EXECUTADO** |
| T109-082 | Reconciliação e operações incertas | receipt UNCERTAIN bloqueia transição dependente | **NÃO EXECUTADO** |
| T109-083 | Reconciliação e operações incertas | host epoch divergente exige quarentena | **NÃO EXECUTADO** |
| T109-084 | Reconciliação e operações incertas | checkpoint divergente não valida pagamento | **NÃO EXECUTADO** |
| T109-085 | Reconciliação e operações incertas | comando pendente bloqueia retry cego | **NÃO EXECUTADO** |
| T109-086 | Reconciliação e operações incertas | reconciliação exige dados do host e canal autenticado | **NÃO EXECUTADO** |
| T109-087 | Reconciliação e operações incertas | recibo FAILED não habilita sucessor | **NÃO EXECUTADO** |
| T109-088 | Reconciliação e operações incertas | ação anterior confirmada não pode ser apagada | **NÃO EXECUTADO** |
| T109-089 | Build, mods e ownership | build divergente invalida mapeamento | **NÃO EXECUTADO** |
| T109-090 | Build, mods e ownership | modpack diferente não compartilha capacidade | **NÃO EXECUTADO** |
| T109-091 | Build, mods e ownership | ownership de item do jogador prevalece | **NÃO EXECUTADO** |
| T109-092 | Build, mods e ownership | quest original não é alterada por contrato | **NÃO EXECUTADO** |
| T109-093 | Build, mods e ownership | NPC de outro mod não é designado escolta automaticamente | **NÃO EXECUTADO** |
| T109-094 | Build, mods e ownership | capability ausente bloqueia mutação | **NÃO EXECUTADO** |
| T109-095 | Build, mods e ownership | mudança de load order exige recertificação | **NÃO EXECUTADO** |
| T109-096 | Build, mods e ownership | identificador de engine não substitui entidade persistente | **NÃO EXECUTADO** |
| T109-097 | Pessoas e facções | facção deixa de existir e etapa fica pendente | **NÃO EXECUTADO** |
| T109-098 | Pessoas e facções | representante perde mandato e não assina emenda | **NÃO EXECUTADO** |
| T109-099 | Pessoas e facções | NPC muda de lealdade sem assumir nova dívida | **NÃO EXECUTADO** |
| T109-100 | Pessoas e facções | proposta de agente duplo não prova pagamento | **NÃO EXECUTADO** |
| T109-101 | Pessoas e facções | pessoa sob proteção não perde sigilo por contrato | **NÃO EXECUTADO** |
| T109-102 | Pessoas e facções | terceiro não signatário não é obrigado a participar | **NÃO EXECUTADO** |
| T109-103 | Pessoas e facções | beneficiário pode contestar entrega parcial | **NÃO EXECUTADO** |
| T109-104 | Pessoas e facções | recusa de participar não prova má-fé | **NÃO EXECUTADO** |
| T109-105 | Revisões e aditamentos | mudança de quantidade exige nova revisão | **NÃO EXECUTADO** |
| T109-106 | Revisões e aditamentos | mudança de beneficiário exige consentimento | **NÃO EXECUTADO** |
| T109-107 | Revisões e aditamentos | mudança de deadline exige nova revisão | **NÃO EXECUTADO** |
| T109-108 | Revisões e aditamentos | adição de dependency edge invalida proposta stale | **NÃO EXECUTADO** |
| T109-109 | Revisões e aditamentos | emenda não apaga pagamentos anteriores | **NÃO EXECUTADO** |
| T109-110 | Revisões e aditamentos | revisão do grafo é independente de observation id | **NÃO EXECUTADO** |
| T109-111 | Revisões e aditamentos | composição de grants é explícita por termo | **NÃO EXECUTADO** |
| T109-112 | Revisões e aditamentos | revogação de autorização bloqueia atos futuros | **NÃO EXECUTADO** |
| T109-113 | Falha e compensação | fracasso de escolta não apaga pagamento confirmado | **NÃO EXECUTADO** |
| T109-114 | Falha e compensação | compensação exige novo receipt | **NÃO EXECUTADO** |
| T109-115 | Falha e compensação | rollback global de acordo não é permitido | **NÃO EXECUTADO** |
| T109-116 | Falha e compensação | Sagas parciais preservam ações irreversíveis | **NÃO EXECUTADO** |
| T109-117 | Falha e compensação | restituição pendente não significa quitada | **NÃO EXECUTADO** |
| T109-118 | Falha e compensação | erro ao devolver bem não cria segundo objeto | **NÃO EXECUTADO** |
| T109-119 | Falha e compensação | host deve autorizar reembolso de ouro | **NÃO EXECUTADO** |
| T109-120 | Falha e compensação | cancelamento posterior não transforma passado em hipótese | **NÃO EXECUTADO** |
| T109-121 | Boatos, evidências e reputação | inadimplência alegada não gera rumor universal | **NÃO EXECUTADO** |
| T109-122 | Boatos, evidências e reputação | prazo vencido não reduz reputação automaticamente | **NÃO EXECUTADO** |
| T109-123 | Boatos, evidências e reputação | rumor repetido não equivale a três provas | **NÃO EXECUTADO** |
| T109-124 | Boatos, evidências e reputação | informação protegida não entra em prompts externos | **NÃO EXECUTADO** |
| T109-125 | Boatos, evidências e reputação | fonte privada não aparece em notificação pública | **NÃO EXECUTADO** |
| T109-126 | Boatos, evidências e reputação | retificação não apaga memória prévia do NPC | **NÃO EXECUTADO** |
| T109-127 | Boatos, evidências e reputação | dossiê tem view específica para destinatário | **NÃO EXECUTADO** |
| T109-128 | Boatos, evidências e reputação | ação jurídica depende de competência e prova | **NÃO EXECUTADO** |
| T109-129 | Save, forks e temporalidade | fork isola recibos de contratos | **NÃO EXECUTADO** |
| T109-130 | Save, forks e temporalidade | restore revê epoch antes de ativar sucessor | **NÃO EXECUTADO** |
| T109-131 | Save, forks e temporalidade | Knowledge Pack por ano não cria obrigação | **NÃO EXECUTADO** |
| T109-132 | Save, forks e temporalidade | estado de campaign errada não pode ser importado | **NÃO EXECUTADO** |
| T109-133 | Save, forks e temporalidade | mudança de branch exige nova autorização | **NÃO EXECUTADO** |
| T109-134 | Save, forks e temporalidade | checkpoints preservam idempotência | **NÃO EXECUTADO** |
| T109-135 | Save, forks e temporalidade | fatos confirmados sobrevivem a replanejamento | **NÃO EXECUTADO** |
| T109-136 | Save, forks e temporalidade | LLM não avança cronologia ou prazo | **NÃO EXECUTADO** |
| T109-137 | Disponibilidade de geografia | NPC não teleporta para local de escolta | **NÃO EXECUTADO** |
| T109-138 | Disponibilidade de geografia | rota bloqueada impede despachar traslado | **NÃO EXECUTADO** |
| T109-139 | Disponibilidade de geografia | distância DR condiciona chegada do mensageiro | **NÃO EXECUTADO** |
| T109-140 | Disponibilidade de geografia | local não materializado exige handoff validado | **NÃO EXECUTADO** |
| T109-141 | Disponibilidade de geografia | incidente offscreen não prova culpa por atraso | **NÃO EXECUTADO** |
| T109-142 | Disponibilidade de geografia | reentrada em mapa não duplica escoltas | **NÃO EXECUTADO** |
| T109-143 | Disponibilidade de geografia | observação parcial não prova ausência de caravana | **NÃO EXECUTADO** |
| T109-144 | Disponibilidade de geografia | ciclo de encontro já resolvido não reaparece | **NÃO EXECUTADO** |
| T109-145 | Segurança de entrada | string maliciosa não cria cláusula executável | **NÃO EXECUTADO** |
| T109-146 | Segurança de entrada | request não assina seus próprios grants | **NÃO EXECUTADO** |
| T109-147 | Segurança de entrada | receipt forjado sem provenance causa quarentena | **NÃO EXECUTADO** |
| T109-148 | Segurança de entrada | nó ausente falha fechado, sem exceção | **NÃO EXECUTADO** |
| T109-149 | Segurança de entrada | filtro ACL ocorre antes da LLM | **NÃO EXECUTADO** |
| T109-150 | Segurança de entrada | resposta não contém dados privados extras | **NÃO EXECUTADO** |
| T109-151 | Segurança de entrada | hash de política errado bloqueia proposta | **NÃO EXECUTADO** |
| T109-152 | Segurança de entrada | recursão excessiva não derruba host | **NÃO EXECUTADO** |
| T109-153 | Operação e observabilidade | log de avaliação inclui reason e revisão | **NÃO EXECUTADO** |
| T109-154 | Operação e observabilidade | decision key ignora ordem de iteração | **NÃO EXECUTADO** |
| T109-155 | Operação e observabilidade | monitoramento não implica execução automática | **NÃO EXECUTADO** |
| T109-156 | Operação e observabilidade | scheduler não consome reservas por leitura | **NÃO EXECUTADO** |
| T109-157 | Operação e observabilidade | falha de rede não realiza nova transferência | **NÃO EXECUTADO** |
| T109-158 | Operação e observabilidade | reserva liberada requer recibo próprio | **NÃO EXECUTADO** |
| T109-159 | Operação e observabilidade | comando HIGH sem gate é negado | **NÃO EXECUTADO** |
| T109-160 | Operação e observabilidade | telemetria não revela identidades protegidas | **NÃO EXECUTADO** |
| T109-161 | POCs BG2:EE e regressão | instalação limpa BG2:EE não assume scripts externos | **NÃO EXECUTADO** |
| T109-162 | POCs BG2:EE e regressão | EEex bridge só libera capacidades comprovadas | **NÃO EXECUTADO** |
| T109-163 | POCs BG2:EE e regressão | duas sessões cliente concordam com receipts | **NÃO EXECUTADO** |
| T109-164 | POCs BG2:EE e regressão | interrupção entre duas operações não duplica pagamento | **NÃO EXECUTADO** |
| T109-165 | POCs BG2:EE e regressão | save/reload não reaplica confirmação | **NÃO EXECUTADO** |
| T109-166 | POCs BG2:EE e regressão | mod da quest mantém ownership de seus recursos | **NÃO EXECUTADO** |
| T109-167 | POCs BG2:EE e regressão | teste de performance de DAG não interfere com combate | **NÃO EXECUTADO** |
| T109-168 | POCs BG2:EE e regressão | desinstalação do Infinity AI não corrompe saves originais | **NÃO EXECUTADO** |

## 10. Próxima decisão arquitetural

**DEC-110 EM ABERTO — garantias e custódia condicional de recursos (escrow) em acordos multipartes.** Nenhuma implementação de depósito, custódia de ouro/itens ou liberação automática é autorizada pela DEC-109.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

A DEC-109 pode habilitar avaliação de liberação de garantia quando o predicado é satisfeito; não envia Action Gateway nem prova que houve depósito. DEC-110 exige custody receipt separado.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
