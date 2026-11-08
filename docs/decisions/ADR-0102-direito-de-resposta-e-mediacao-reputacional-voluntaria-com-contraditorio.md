# ADR-0102 — Direito de resposta e mediação reputacional voluntária, com contraditório verificável (DEC-107/C)

- **Estado:** **APROVADA COMO ARQUITETURA**, alternativa C escolhida expressamente em 2026-11-07.
- **Versão:** Infinity AI Discovery v10.3. **Implementação real BG2:EE/EEex/bridge/multiplayer:** NÃO COMPROVADA.
- **Preservação:** DEC-060 a DEC-106 vigentes; ADR-0001 a ADR-0101 preservados byte a byte.
- **Contrato técnico:** `docs/107-direito-de-resposta-mediacao-voluntaria-contraditorio-privacidade-e-gates.md`.

## Contexto

A DEC-106 admite reconstrução contextual da confiança depois de uma acusação corrigida. Entretanto, controvérsias reputacionais podem permanecer **em disputa**: uma parte aponta quebra de acordo, outra contesta, testemunhas divergem e pode não haver prova conclusiva. É necessário permitir apresentação de versões, direito de resposta e mediação **sem transformar o mediador ou a LLM em juiz onisciente**, sem confissões forçadas ou acordos impostos. O procedimento deve respeitar DEC-030 (reputação), DEC-041/042 (jogadores), DEC-064/065 (crenças), DEC-075/077/078 (autoria, provas e justiça), DEC-081 (reparações), DEC-083–085 (fontes e segurança), DEC-089/090 (evidências/dossiês), DEC-095 (compensações), DEC-104–106 (retificação, difusão e reabilitação).

## Alternativas analisadas

- **A — Retratação pública obrigatória após refutação:** **REJEITADA**. Nem toda disputa é comprovadamente falsa; retratação não equivale a acordo, reparação ou perdão. Viola autonomia e pode revelar fontes protegidas.
- **B — Mediação arbitrada livremente por LLM:** **REJEITADA**. Pode fabricar provas, confissões, consentimentos, autoridade, pagamentos ou fatos do host.
- **C — Direito de resposta e mediação contextual, voluntária e auditável:** **APROVADA**. Fases distintas, participação legítima, evidências com proveniência, sigilo, recusas válidas, aceite por termo e gates mecânicos separados.

## Invariantes vinculantes

1. **Controvérsia não é culpa.** `DisputeClaim` (alegação), `ReplyStatement` (versão da parte), `EvidenceRecord` (material e cadeia de fontes), `FactAssessment` (avaliação curada), `MediationOffer`, `SessionRecord`, `SettlementDraft`, `PartyAcceptance` e `SettlementReceipt` são objetos e autoridades distintos. O registro de alegação não concede status de fato.
2. **Contraditório genuíno.** Notificação com escopo e conteúdo permitido, oportunidade razoável de resposta conforme relógio DR, canal acessível, registro de manifestação/recusa/não localização; a ausência de resposta **não é prova de culpa**. Não atribuir declaração a quem não a fez.
3. **Voluntariedade.** Solicitar mediação, oferecer canal de resposta e registrar proposta não vinculam as partes. Participação, retratação, pedido de desculpas, reconhecimento de culpa, indenização, perdão e aceitação de termos exigem aprovação separada de cada titular legítimo. Coerção ou silêncio não valem como consentimento.
4. **Jogadores permanecem soberanos sobre seus PCs.** O host e a LLM não podem falar ou assinar por PC ausente ou delegado. Exigir confirmação inequívoca do controlador legítimo por compromisso, mesmo que outro integrante da party tenha solicitado a mediação (DEC-041/042/045/046).
5. **Representação de facções.** Verificar vínculo, mandato, escopo, validade temporal, revogações e alçada do representante; diplomata sem poder para contratar não assina reparação financeira. DEC-079/080/082 não fornecem autorização universal.
6. **Neutralidade e conflitos de interesse.** Facilitador possui identidade persistente, afiliações e registro de conflitos; se for autor, beneficiário direto, fonte sigilosa envolvida ou possuir vínculo incompatível, o processo exige revisão/substituição ou recusa. A simples declaração do requerente não legitima mediador.
7. **Direito de resposta ≠ publicidade irrestrita.** Audiências, finalidade e payload redigido dependem de ACL/consentimento independente. Réplica pública é uma operação separada, mais sensível, e não transmite automaticamente depoimentos, nomes de testemunhas, segredos, refúgios, endereços ou conteúdo integral de dossiês.
8. **Evidência não é contagem de relatos.** Preservar cadeia de proveniência, independência de fontes, contradições, revisões, documentos contestados e incerteza DEC-077/089/090; o facilitador não pode declarar verdade apenas por parecer mais convincente.
9. **Procedimento auditável por estágios.** `REQUESTED`, `NOTICE_PROPOSED`, `NOTICE_SENT`, `REPLY_WINDOW`, `REPLY_FILED`, `MEDIATION_OFFERED`, `CONSENTS_PENDING`, `SESSION_PROPOSED`, `DRAFTED`, `PARTY_ACCEPTANCES_PENDING`, `SETTLED`, `CLOSED_NO_AGREEMENT`, `QUARANTINED`. Uma transição pode ser proposta sem ser committed. Estados de recepção/percepção são separados.
10. **Recusa e saída.** Uma parte pode recusar mediação ou retirar autorização para etapas futuras. Isso não retroage recebimentos ou compromissos confirmados, mas impede novos atos que necessitem do consentimento. Recusa não produz sanções ou reputação negativa por padrão.
11. **Acordo por termos, não por narrativa.** `SettlementTerm` inclui prestador, destinatário, obrigação, prazo, recursos, autoridade, consentimentos, versionamento, risco e meio de prova. `Draft` não constitui contrato; cada aceite é explícito, independente e vinculado a uma revisão exata. Mudança de termo invalida aceite da versão anterior.
12. **Sem enforcement implícito.** Nenhum acordo cria ouro, itens, flags de quest, reputação mecânica, prisões, mandados, punições, transferências ou reparações automaticamente. Qualquer efeito mecânico passa pelo Action Gateway, capabilities por build, ownership e receipt do host; sanções/reparações seguem DEC-078/081/095.
13. **Sem reconciliação compulsória das crenças.** Receber direito de resposta não exige acreditar, confiar, perdoar ou esquecer. DEC-104–106 preservam memórias individuais, danos já confirmados e correções distribuídas causalmente.
14. **Tempo e território.** Janelas de resposta e sessões seguem tempo do mundo DR/DEC-022, alcance geográfico e canais DEC-029/074/105. Não presumir entrega instantânea, disponibilidade simultânea de NPCs nem progressão em FROZEN.
15. **Branches e epochs.** Todos os casos, recibos, cartas, aceites e termos são vinculados a campanha, branch, lineage, build/modpack fingerprint, host epoch, checkpoint epoch, versão da política e mundo. Uma decisão de fork não autoriza replay de mensagens em outro ramo.
16. **CAS, chaves idempotentes e receipts.** Repetir pedido não implica segunda notificação, compromisso ou pagamento. `DISPATCHED/UNCERTAIN` entra em reconciliação, não em retry cego. Snapshot de processo permite recuperação sem duplicar consentimentos.
17. **Risco e confidencialidade.** Conteúdo `PROTECTED`, risco de represália, menores ou testemunhas exigem filtros/redações e autorização separada; casos HIGH permanecem bloqueados até gates apropriados. Nenhum segredo em prompt, título de evento, log, índice ou audit trail público.
18. **LLM somente para redação autorizada.** Pode ajudar a produzir minuta, formulação polida ou resumo do contraditório sobre view minimizada; não inventa documentos, julga culpa, valida consentimento, seleciona destinatários ou envia publicações.
19. **Não misturar processo institucional e voluntário.** Justiça formal, poder de coerção, revogação de sanções, mediação privada e negociação entre guildas têm normas distintas; este ADR não cria jurisdição e não substitui DEC-078–082.
20. **Fail closed quando incompleto.** Fonte ausente, parte não identificada, dúvida de representação, autorização não validada, conflito de interesses, observação parcial, status incerto, prova contestada ou mudança de build levam a proposta limitada ou `QUARANTINED`, nunca a confissão ou acordo presumido.
21. **Capacidade não comprovada.** Exemplos sintéticos e testes locais não demonstram NPC dialog, UI de mediação, pagamento, quests ou multiplayer na bridge EEex. Nenhum POC no jogo está declarado executado por esta decisão.

## Contratos mínimos

| Entidade | Campos mínimos e restrições | Autoridade |
|---|---|---|
| `ReputationalDisputeCase` | IDs persistentes de partes, assuntos, escopos, regiões, chronology DR, case revision, estado | Registro do caso com autoridade independente |
| `EvidenceSubmission` | `evidence_ref`, autor, cadeia de fontes, independência, classificação, admissão/contestação | Registry de evidências curado DEC-077/089 |
| `RightOfReplyNotice` | conteúdo redigido, audiência, canal, janela DR, destinatário, origem da alegação | Principal legítimo + ACL + outbox, sem execução presumida |
| `NoticeDeliveryReceipt` | entrega, percepção, assinatura/canal autenticado, timestamp, branch | Serviço de comunicação DEC-105 |
| `PartyRepresentation` | identidade persistente, mandate scope, valid time, consent status, PC owner | Registry autenticado independente do request |
| `FacilitatorAssessment` | legitimidade, conflito de interesse, motivo redigido, consentimento | Registro de facilitadores e arbitragem de legitimidade |
| `MediationSession` | agenda, local, duração, participantes confirmados, confidencialidade | Proposta voluntária, reserva DEC-093, sem teleport |
| `SettlementDraft` | revisão imutável, termos tipados, obligations, recursos, deadlines, ACL | Rascunho sem eficácia automática |
| `TermAcceptance` | `term_revision`, party, representante autorizado, consentimento por termo | Aceite independente de cada parte interessada |
| `SettlementCommitReceipt` | chave idempotente, autorização, efeitos autorizados, host receipt se mecânico | Apenas após validação/gates específicos |

## Algoritmo normativo de referência

```text
1. Requisitante pode pedir abertura de procedimento, NÃO inventar prova, mandato nem consentimento.
2. Verificar scope + ACL + risco + registro curado de alegação e partes.
3. Confirmar oportunidades de contraditório: canal autorizado, prazo DR, notificação enviada e recebida.
4. Se notificação não recebida: propor comunicação, NUNCA inferir ciência ou silêncio culpável.
5. Se versão não apresentada: propor oportunidade de resposta; jamais inventar resposta.
6. Se mediação proposta: verificar voluntariedade e conflitos de interesse do facilitador.
7. Se algum consentimento falta/foi retirado: não criar sessão nem impor acordo.
8. Se ambas as partes aceitam: pode propor sessão com horários e recursos reais.
9. Se há minuta: coletar aceite independente por parte e revisão exata de cada termo.
10. Sem receipts de commit e host: nenhum efeito social/mecânico é declarado realizado.
```

## Demonstração de aceitação futura (não executada)

- Validar semântica de recebimento, intervalos DR, poderes de representantes e identidade de PCs em BG2:EE/EEex + dois clientes.
- Garantir que propostas de publicação usem ACL/redação sem vazamento em UI, prompts, caches, logs e roteamento LAN.
- Confirmar checkpointer, epoch fencing, CAS, notice/outbox idempotentes e restituição só via gateway.
- Garantir que disputas com dados insuficientes permaneçam abertas/inconclusivas, sem forçar veredito.
- Ver matriz `T107-001..T107-152` no contrato técnico. **Cenários candidatos NÃO EXECUTADOS no BG2:EE/EEex.**

## Próxima DEC-108 — CUMPRIMENTO E MONITORAMENTO DE ACORDOS (EM ABERTO)

Como acompanhar prazos, comprovantes de cumprimento, descumprimento contestado e novos acordos, sem execução compulsória? A — cumprimento automático dos termos; B — LLM decide inadimplemento e sanção; **C recomendada:** monitoramento determinístico por obrigações/receipts/tempo DR, aviso e contraditório, renegociação voluntária, compensações legitimamente autorizadas e gates do host.
