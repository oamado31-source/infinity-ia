# 110 — Custódia condicional verificável de garantias: propriedade, recibos, disputas e liberação

**Status:** DEC-110/C aprovada como arquitetura · Discovery v10.6 · ADR-0105. Os 104 ADRs anteriores permanecem imutáveis. **Nenhuma capacidade real de escrow foi validada em BG2:EE/EEex.**

## 1. Fronteira de confiança e objetivo

Garantias contratuais só podem ser consideradas mecanicamente custodiadas após um *host-confirmed transfer receipt* autenticado; uma reserva lógica é apenas indisponibilidade **planejada**, não segregação real. Este documento define decisões de planejamento e reconciliação; a implementação de transferências depende de uma SPEC com gate por build. O modelo deve distinguir títulos de propriedade, custódia física, direito de uso, condições e pretensões contestadas.

## 2. Contratos e registros por camada

| Registro | Campos mínimos | Garantia negativa |
|---|---|---|
| `EscrowAgreement` | `agreement_id/revision`, `escrow_id/revision`, parties, mandatos, termos committed, scope | Não prova depósito. |
| `AssetOwnershipProof` | asset ID, PC/NPC owner, custody status, build/epoch, proveniência | Não transfere propriedade. |
| `EscrowCapabilityManifest` | build/modpack/EEex/bridge versions, validated hooks, POC IDs, restrictions | Declaração sem POC não basta. |
| `DepositProposal` | asset, amount, custodian, owner consent, action ID, policy revision | Não consome item. |
| `HostDepositReceipt` | authority, action ID, receipt ID, resource ID, amount, owner/custodian, scope, epoch, signature | Sem receipt, não alegar custódia. |
| `CustodyPosition` | custodian, asset, balance confirmed, ledger revision, state | Saldo não pode ser inferido de texto. |
| `ReleaseTerm` | condition DEC-109, beneficiary, permitted amount, term/revision | Elegibilidade não transfere nada. |
| `ReleaseProposal` | receipt refs, condition refs, scope, ACL, authorization refs, fencing token | Nunca gera host command. |
| `HostReleaseReceipt` | transfer confirmed, amount, signer, action ID, epoch, beneficiary | Somente esse receipt prova liberação mecânica. |

## 3. Estados e transições

`PROMISED` (acordo declarado) → `DEPOSIT_PROPOSED` (pedido ainda sem efeito) → `DISPATCHED` ou `UNCERTAIN` (quarentena) → `CUSTODY_CONFIRMED` (somente receipt autenticado) → `RELEASE_ELIGIBLE_FOR_REVIEW` (condição + consentimento + saldo) → `RELEASE_DISPATCHED/UNCERTAIN` → `RELEASE_CONFIRMED` (receipt autenticado).

Estados laterais: `NOT_MECHANICALLY_HELD`, `WAITING_CAPABILITY`, `WAITING_CONSENT`, `CONTESTED_HOLD`, `BLOCKED_STALE`, `RECONCILE_REQUIRED`, `RETURN_ELIGIBLE`, `EXPIRED_REVIEW`. Uma liberação sem receipt permanece `UNCERTAIN` e não libera recursos. Nenhuma transição cria ações de inventário no exemplo Python.

## 4. Ordem normativa dos gates

1. Validar schema, tipos, versões, scope (campanha/branch/linhagem), host/checkpoint epoch e Knowledge Pack.
2. Resolver a revisão committed do acordo no registro autenticado da DEC-107 e os nós/condições DEC-109; validar autoridade de participantes, titular e custodiantes.
3. Verificar `EscrowCapabilityManifest`: **precisa da prova real para a combinação exata** de jogo + EEex + bridge + modpack + multiplayer.
4. Verificar titularidade por instância/campo DEC-099, disponibilidade e resguardos de conteúdo nativo/quest/PC; falha conserva `NOT_MECHANICALLY_HELD`.
5. Conferir consentimento explícito para depósito ou liberação, separadamente da assinatura de contrato; auditoria e risco DEC-027.
6. Confrontar recibos host-confirmed autênticos com IDs de ação e quantidades decimais; duplicatas, faltas e `UNCERTAIN` não são sucesso.
7. Validar que o mesmo recurso não está reservado/consumido em outras operações; resolver DEC-093/094 sem retirada automática.
8. Se as condições DEC-109 forem satisfeitas, gerar **somente `PROPOSE_RELEASE_REVIEW`**; bloquear se existir contestação não resolvida.
9. Enviar operação ao Action Gateway apenas por uma etapa posterior autorizada e testada; confirmar receipt antes da nova revisão de custódia.
10. Reconciliar save/load, rollback e multiplayer; nunca misturar forks, epochs, assinaturas ou reexecutar transferência em dúvida.

## 5. Política de resultados

| Status | Significado | Próximo passo permitido |
|---|---|---|
| `NOT_MECHANICALLY_HELD` | Promessa sem depósito confirmado | Mostrar compromisso sem afirmar custódia real. |
| `BLOCKED_CAPABILITY` | Build sem capacidade testada | Somente narrativa/proposta, nenhum gasto. |
| `WAITING_CONSENT` | Falta autorização específica do titular | Solicitar consentimento explicitamente. |
| `WAITING_HOST_RECEIPT` | Depósito proposto/dispachado sem confirmação | Reconciliar, não repetir. |
| `CUSTODY_CONFIRMED` | Depósito autenticado + escopo/quantidade íntegros | Examinar condições de liberação. |
| `CONTESTED_HOLD` | Disputa declarada e não resolvida | Mediar/revisar conforme DEC-107/108. |
| `WAITING_CONDITIONS` | Gatilhos contratuais pendentes | Manter, monitorar; nunca liberar automaticamente. |
| `RELEASE_ELIGIBLE_FOR_REVIEW` | Condições + autorização confirmadas | Gerar plano seguro, sem host command. |
| `RECONCILE_REQUIRED` | Host uncertain, epoch stale, receipt suspeito | Bloquear e auditar. |
| `RELEASE_CONFIRMED` | Liberação comprovada por recibo do host | Atualizar ledger; evitar repetição. |

## 6. Exemplo sintético

As guildas A e B firmam contrato para depositar 50 moedas com custodiante C. `EscrowCommit` + `DepositProposal` não provam depósito. Um ledger artificial de teste contendo um recibo *host-confirmed (fictício)* representa a hipótese `CUSTODY_CONFIRMED`. A entrega de dez caixas validada pela DEC-108/109 torna uma liberação de 50 moedas *elegível*; o avaliador sintético devolve `host_action: NONE`. O valor só seria efetivamente transferido em uma futura SPEC implementada, após comando autorizado e recibo real. **Nenhum exemplo cria, credita ou subtrai ouro no BG2.**

## 7. POCs e critérios de aceitação exigidos

- P0 — Ambiente reproduzível: Windows, BG2:EE puro, EEex (se viável), manifesto/hashes e duas instalações de teste. 
- P1 — Read-only e prova de ownership/quantidade; operação sem efeitos e logs do host.
- P2 — Transferência de item/moeda fictícia em save descartável; confirmar com dois clientes e save/reload.
- P3 — Reserva/custódia exclusiva, disputas, retries, perda de conexão, host swap, restituição autorizada.
- P4 — Testes de regressão com quests e mods; bloqueio por capability ausente; consentimento explícito de PC.
- Nenhum POC consta como executado/aprovado neste documento.

## 8. Matriz T110 — 176 cenários candidatos de integração (TODOS NÃO EXECUTADOS)

| ID | Família | Cenário a comprovar no ambiente real | Critério mínimo | Estado |
|---|---|---|---|---|
| T110-001 | Contrato e consentimento | minuta não committed | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-002 | Contrato e consentimento | assinatura parcial | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-003 | Contrato e consentimento | representante sem mandato | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-004 | Contrato e consentimento | revisão vencida | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-005 | Contrato e consentimento | mudança unilateral de condição | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-006 | Contrato e consentimento | terceiro ausente | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-007 | Contrato e consentimento | escrow de outro acordo | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-008 | Contrato e consentimento | recurso sem descrição tipada | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-009 | Campanha e identidade | campanha divergente | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-010 | Campanha e identidade | ramo divergente | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-011 | Campanha e identidade | linhagem divergente | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-012 | Campanha e identidade | host epoch divergente | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-013 | Campanha e identidade | checkpoint epoch divergente | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-014 | Campanha e identidade | modpack alterado | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-015 | Campanha e identidade | build não validada | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-016 | Campanha e identidade | Knowledge Pack incorreto | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-017 | Ownership | titularidade comprovada | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-018 | Ownership | titularidade desconhecida | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-019 | Ownership | item de PC sem consentimento | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-020 | Ownership | NPC sem autorização | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-021 | Ownership | item de quest protegido | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-022 | Ownership | inventário de outro mod | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-023 | Ownership | custodiante sem competência | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-024 | Ownership | custódia duplicada | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-025 | Capabilities | build sem hook seguro | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-026 | Capabilities | consulta read-only insuficiente | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-027 | Capabilities | capacidade declarada sem POC | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-028 | Capabilities | capacidade validada só single-player | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-029 | Capabilities | capability expirada | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-030 | Capabilities | observação parcial | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-031 | Capabilities | transferência com erro | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-032 | Capabilities | fallback narrativo rotulado | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-033 | Proposta de depósito | proposta sem reserva | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-034 | Proposta de depósito | reserva lógica sem segregação | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-035 | Proposta de depósito | saldo desconhecido | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-036 | Proposta de depósito | quantidade decimal inválida | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-037 | Proposta de depósito | unidade incompatível | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-038 | Proposta de depósito | recurso futuro prometido | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-039 | Proposta de depósito | recurso já reservado | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-040 | Proposta de depósito | autorização retirada | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-041 | Recebimento de depósito | recibo confirmado | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-042 | Recebimento de depósito | recibo sem autenticação | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-043 | Recebimento de depósito | recibo emitido pelo cliente | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-044 | Recebimento de depósito | recibo com ação desconhecida | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-045 | Recebimento de depósito | recibo com recurso divergente | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-046 | Recebimento de depósito | recibo de data futura | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-047 | Recebimento de depósito | recibo nulo | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-048 | Recebimento de depósito | recibo host de outro ramo | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-049 | Quantidade | depósito integral | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-050 | Quantidade | depósito parcial | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-051 | Quantidade | quantidade zero | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-052 | Quantidade | quantidade negativa | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-053 | Quantidade | over-deposit | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-054 | Quantidade | duplicação da quantidade | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-055 | Quantidade | divergência de moeda | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-056 | Quantidade | inteiros de itens indivisíveis | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-057 | Idempotência | mesmo receipt_id | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-058 | Idempotência | mesmo action_id | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-059 | Idempotência | retorno tardio | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-060 | Idempotência | retry após timeout | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-061 | Idempotência | ações em vôo | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-062 | Idempotência | digest repetido | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-063 | Idempotência | fencing token expirado | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-064 | Idempotência | dois clientes simultâneos | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-065 | Liberação | condição não cumprida | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-066 | Liberação | condição cumprida mas sem autorização | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-067 | Liberação | autorização válida sem recebimento | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-068 | Liberação | beneficiário diferente | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-069 | Liberação | mudança de revision | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-070 | Liberação | saldo parcialmente liberado | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-071 | Liberação | liberação confirmada | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-072 | Liberação | nova liberação após quitação | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-073 | Retenção e disputa | disputa iniciada | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-074 | Retenção e disputa | disputa contestada | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-075 | Retenção e disputa | decisão jurisdicional inválida | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-076 | Retenção e disputa | mediador parcial | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-077 | Retenção e disputa | acordo de arbitragem ausente | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-078 | Retenção e disputa | liberação contestada | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-079 | Retenção e disputa | custodiante em conflito | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-080 | Retenção e disputa | retorno voluntário aceito | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-081 | Prazos DR | modo FROZEN | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-082 | Prazos DR | modo PARTIAL | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-083 | Prazos DR | modo REALTIME | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-084 | Prazos DR | data desconhecida | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-085 | Prazos DR | prazo alcançado | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-086 | Prazos DR | prazo ainda não alcançado | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-087 | Prazos DR | fuso fictício confuso | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-088 | Prazos DR | mudança de calendário | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-089 | ACL | destinatário sem permissão | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-090 | ACL | disclosure mínima | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-091 | ACL | vazamento de inventário | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-092 | ACL | fonte protegida | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-093 | ACL | pseudônimo vinculado | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-094 | ACL | log sensível | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-095 | ACL | prompt malicioso | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-096 | ACL | retificação de ACL | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-097 | Incompatibilidade | mod cria item próprio | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-098 | Incompatibilidade | script original reserva recurso | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-099 | Incompatibilidade | quest trava inventário | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-100 | Incompatibilidade | personagem morto em outra sessão | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-101 | Incompatibilidade | mudança de ownership | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-102 | Incompatibilidade | troca de host | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-103 | Incompatibilidade | reescrita de save | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-104 | Incompatibilidade | bridge só escreve localmente | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-105 | Retorno e compensação | depósito devolvido | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-106 | Retorno e compensação | restituição sem saldo | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-107 | Retorno e compensação | compensação proposta | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-108 | Retorno e compensação | compensação não autorizada | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-109 | Retorno e compensação | pagamento sem recibo | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-110 | Retorno e compensação | reembolso duplicado | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-111 | Retorno e compensação | retorno a titular diferente | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-112 | Retorno e compensação | efeito já irreversível | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-113 | Estado UNCERTAIN | pedido despachado | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-114 | Estado UNCERTAIN | receipt tardio | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-115 | Estado UNCERTAIN | reconciliação incompleta | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-116 | Estado UNCERTAIN | host desconectado | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-117 | Estado UNCERTAIN | host reiniciado | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-118 | Estado UNCERTAIN | ação cancelada no planejamento | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-119 | Estado UNCERTAIN | mesmo token após restore | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-120 | Estado UNCERTAIN | quarentena de recurso | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-121 | Disponibilidade | custodiante não localizado | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-122 | Disponibilidade | custodiante morto | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-123 | Disponibilidade | custodiante em viagem | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-124 | Disponibilidade | custodiante ocupado | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-125 | Disponibilidade | recurso inacessível | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-126 | Disponibilidade | suspensão de comércio | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-127 | Disponibilidade | NPC hibernando | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-128 | Disponibilidade | falta de janela ativa | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-129 | Concorrência | duas operações pedem mesmo ouro | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-130 | Concorrência | deadlock de reservas | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-131 | Concorrência | starvation de liberação | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-132 | Concorrência | prioridade sem consentimento | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-133 | Concorrência | reserva órfã | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-134 | Concorrência | preempção não autorizada | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-135 | Concorrência | fairness insuficiente | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-136 | Concorrência | operação independente liberada | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-137 | Auditoria | proveniência incompleta | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-138 | Auditoria | documento alterado | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-139 | Auditoria | log truncado | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-140 | Auditoria | recibo omitido | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-141 | Auditoria | prova originada na LLM | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-142 | Auditoria | duplicação de assinatura | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-143 | Auditoria | manifesto incompatível | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-144 | Auditoria | replay divergente | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-145 | UI e agência | confirmação do PC | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-146 | UI e agência | PC ausente | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-147 | UI e agência | controle delegado vencido | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-148 | UI e agência | UX sem aviso de custo | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-149 | UI e agência | aceite de termo versus liberação | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-150 | UI e agência | tela mobile inacessível | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-151 | UI e agência | transparência de status | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-152 | UI e agência | recusa explícita | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-153 | Quests originais | contrato narrativo de quest | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-154 | Quests originais | recurso canônico | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-155 | Quests originais | save da campanha Original | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-156 | Quests originais | spoiler em termo | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-157 | Quests originais | flag sem allowlist | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-158 | Quests originais | reputação sem autorização | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-159 | Quests originais | recompensa preexistente | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-160 | Quests originais | objeto legítimo de jogador | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-161 | Fallback e falhas | serviço LLM off | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-162 | Fallback e falhas | JSON inválido | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-163 | Fallback e falhas | modelo indisponível | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-164 | Fallback e falhas | schema incompatível | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-165 | Fallback e falhas | latência alta | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-166 | Fallback e falhas | falha de checksum | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-167 | Fallback e falhas | perda de energia | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-168 | Fallback e falhas | modo somente leitura | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-169 | Teste em dois clientes | cliente A observa recibo | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-170 | Teste em dois clientes | cliente B observa recibo | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-171 | Teste em dois clientes | save/reload sincronizado | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-172 | Teste em dois clientes | latência variável | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-173 | Teste em dois clientes | desconexão entre clients | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-174 | Teste em dois clientes | reingresso do PC | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-175 | Teste em dois clientes | fencing host/client | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |
| T110-176 | Teste em dois clientes | ausência de prova multiplayer | Sem transferência automática; outcome determinístico + evidência de escopo, ACL, idempotência e ausência de mutações não autorizadas. | **NÃO EXECUTADO** |

## 9. Relação com o início das SPECS

A especificação de custódia real é **posterior** à SPEC da bridge read-only e às provas multiplayer. Não bloquear o desenvolvimento do núcleo por ausência de escrow real. O questionário consolidado está em `docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md`, com P0 prioritário e decisões de V1 separadas; o handoff em `docs/112-plano-de-transicao-discovery-specs-e-primeiro-ciclo-executavel.md` define rastreabilidade DEC → SPEC → plano → tasks → evidências. Status de perguntas não respondidas: **ABERTAS**, mesmo quando existe opção recomendada.
