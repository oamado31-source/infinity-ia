# ADR-0101 — Reabilitação reputacional proporcional e reconstrução contextual da confiança (DEC-106/C)

- **Estado:** APROVADA COMO ARQUITETURA, em 2026-11-07, por escolha expressa da opção C.
- **Discovery:** v10.2. **Implementação em BG2:EE/EEex/bridge/host + dois clientes:** NÃO COMPROVADA; nenhuma alteração em reputação/quest/inventário foi efetuada.
- **Invariantes vinculantes:** DEC-011/012/019–022/027–030/034/041/042/053–065/066–069/074–083/086–095/096–105. As **DEC-060..105 permanecem aprovadas; ADR-0001..0100 preservados byte a byte**.
- **Contrato detalhado:** `docs/106-reabilitacao-reputacional-proporcional-confianca-danos-alcance-e-reparacoes.md`.

## Contexto e motivação

Uma acusação incorreta, ainda que devidamente retificada (DEC-104), pode ter sido difundida e percebida por públicos distintos (DEC-105), causando prejuízos comerciais, rompimento de contratos, perda de confiança, estigma e eventual sanção (DEC-078/081). A correção não necessariamente alcançou as mesmas pessoas; quem a recebeu pode discordar; efeitos confirmados pelo host não desaparecem. Restaurar um placar global de reputação seria incoerente com a DEC-030 e com a autoridade dividida.

Devemos oferecer meios contextualizados de **propor** reabilitação sem impor opiniões, apagar memórias, declarar dano não comprovado ou fabricar compensações. Reabilitação social, retratação, reparação material, remediação institucional e alteração mecânica são ações com entidades e permissões diferentes.

## Alternativas consideradas

- **A — Restauração instantânea de reputação:** REJEITADA. Impõe aceitação universal, apaga assimetrias de difusão e tenta desfazer danos históricos.
- **B — LLM restaura reputação e escolhe reparações:** REJEITADA. Pode criar recursos, decidir crenças, conceder perdão ou editar efeitos do host sem autoridade.
- **C — Reabilitação contextual, gradual, proporcional e causal:** **APROVADA**. Evidência curada + população realmente exposta e alcançada + danos comprovados + pedido legítimo + opções voluntárias e gates próprios.

## Invariantes normativos

1. **Verdade, acusação, retificação, ciência, crença, confiança, reputação, dano e reparação são registros distintos.** Uma `CorrectionProof` não implica `BeliefRevisionReceipt`; este não implica `TrustRestorationReceipt` e tampouco altera `HostReputation`.
2. **Legitimidade independente da requisição.** Retificação e suporte DEC-089/104 são consultados de registry curado `COMMITTED`; comunicação DEC-105 provém de recibos validados e stores autenticados. O solicitante não pode declarar sua própria prova, autorização, consentimento ou confiança.
3. **Reputação não é variável global única.** Representar `ReputationContext` por comunidade, região, facção, relação, público e tipo de confiança (comercial, pessoal, institucional etc.); nenhuma operação altera todos os contextos por fan-out.
4. **Distinguir exposição real e alcance da correção.** A população que ouviu a acusação não coincide necessariamente com aquela que recebeu e percebeu a correção. Um rumor repetido não gera comprovante independente. Não inferir opinião de NPCs que não receberam nenhuma mensagem.
5. **Confiança individual é falível e voluntária.** Revisões de crença DEC-105 são separadas de reparação de confiança. Nem mesmo uma absolvição comprova reconciliação, perdão, renovação de contrato ou aceitação por facção/NPC; o controlador legítimo pode recusar.
6. **Danos precisam de ligação causal e prova.** Cada `HarmClaim` distingue `ALLEGED`, `CORROBORATED`, `HOST_CONFIRMED`, `DISPUTED`, `UNATTRIBUTED`, `NOT_IN_SCOPE`; danos comprovados não devem ser somados se pertencerem à mesma origem/recibo.
7. **Não apagar prejuízos confirmados.** Compras canceladas, multas, decisões jurídicas, itens transferidos, reputação mecânica e outros efeitos anteriores permanecem registrados. Reparação ou novo acordo é um acontecimento separado, DEC-081/095.
8. **Medidas não equivalentes.** `ClarificationNotice`, `RightOfReplyProposal`, `PublicRetractionRequest`, `TrustReviewProposal`, `CommercialRenegotiationProposal`, `RestitutionProposal` e `HostReputationChangeProposal` possuem autorizadores distintos; uma não substitui automaticamente outra.
9. **Privacidade e minimização de dados.** Identidades de vítimas, testemunhas, refúgios, informantes, dossiês e prova protegida não devem aparecer em comunicados, prompts, logs, caches, relações de dano ou metadados acessíveis. Redação específica por público antes do encaminhamento.
10. **Consentimento e agência.** A vítima pode contestar ou rejeitar campanha de publicidade, retratação ou acordo. NPCs mantêm autonomia contextual; PCs só assumem compromissos próprios por decisão de seus jogadores, inclusive quando ausentes/delegados (DEC-041/042/045/046).
11. **Sem compensação automática.** Ouro, itens, reputação engine, sanctions, scripts ou contratos não podem ser alterados pela avaliação. Necessitam recurso real, ownership, autorização, Action Gateway e recibo do host; dano monetário não é automaticamente igual à reparação devida.
12. **Proporcionalidade sem métricas inventadas.** Critérios devem incluir provas, extensão da acusação, extensão da correção, danos efetivos, permanência, obrigações, autoridade e recursos. Não atribuir percentuais universais de restauração, scores psicológicos nem reputação BG2:EE sem SPEC/curadoria por domínio.
13. **Temporalidade e geografia.** Usar tempo do mundo DR e modos DEC-022; rumor e retratação viajam por canais DEC-029/074/105, sem teleport, conhecimento universal ou eventos em anos indevidos. O decaimento de confiança não é automático sem política validada.
14. **Isolamento de ramo e identidade persistente.** Prova, destinatários, ledger, claims, recibos e propostas vinculados a campanha/branch/lineage, fingerprint de build/modpack, host/checkpoint epochs e política. Não importar estado de um fork antigo sem migração explícita.
15. **CAS, outbox, fencing e idempotência.** Proposal key deriva de scope + caso + beneficiário + contexto + revisão de provas/correção + ledger. Repetições não geram dinheiro, reputation points, múltiplas desculpas nem alterações duplicadas. `DISPATCHED/UNCERTAIN` exige reconciliação.
16. **Contestação e contraditório.** Um acusado pode solicitar reabilitação; uma alegada vítima pode contestar danos, titulares e terceiros podem preservar discordâncias legítimas. Toda retificação/medida social permanece rastreável, com versões e possibilidade de revisão.
17. **Separação epistêmica.** NPC que recebeu correção mas ainda duvida não é forçado a confiar. Mesmo NPC que aceita prova pode manter reserva comercial por outro motivo. WorldFact e QuestSemanticMilestone não são alterados por opinião pública.
18. **Segurança de alto risco.** Retratações públicas que revelariam localização de testemunha, confissão em nome de PC, sanções, coerção, confisco, dano a imagem de terceiros, agressões ou mudança de quests recebem gates de risco e podem ser recusadas (fail closed).
19. **LLM somente como editor autorizado.** Poderá propor texto já minimizado/redigido, não calcular a verdade, escolher destinatários, regular crenças, autenticar recibos, fazer reputação mecânica ou comprometer recursos.
20. **Limite de evidência técnica.** Código Python, fixtures e JSON Schema são **SINTÉTICOS, DE REFERÊNCIA E SEM EFEITOS COLATERAIS**; testes locais não comprovam capabilities do BG2:EE/EEex. Matriz T106-* é candidata e não foi executada no motor.

## Contratos e autoridade

| Entidade | Conteúdo mínimo proposto | Autoridade |
|---|---|---|
| `CommittedRectification` | `correction_id`, `revision`, `claim_ref`, `proof_grade`, `provenance`, `branch`, `classification` | Registry curado DEC-104, nunca request |
| `ExposureLedger` | `recipient_persistent_id`, `original_claim_ref`, `delivery_id`, `perception_status`, `time_dr`, `scope` | Prova de difusão DEC-029/105 |
| `CorrectionReceipt` | `recipient_persistent_id`, `correction_revision`, `delivered`, `perceived`, `time_dr`, `view_hash` | Serviço de comunicação DEC-105 |
| `ReputationContext` | `subject`, `community`, `region`, `relationship`, `dimension`, `revision`, `owner` | Estado contextual de reputação DEC-030 |
| `HarmClaim` | `harm_id`, `kind`, `status`, `source_family`, `cause_refs`, `host_receipt_ref`, `estimated_loss_if_verified` | Dano alegado ≠ dano provado; evidência independente |
| `RehabilitationCase` | `case_id`, `beneficiary`, `sponsor`, `purpose`, `scope`, `consent_ref`, `policy_revision`, `expected_revision` | Caso e solicitação autorizados; não prova retificação |
| `RemedyProposal` | `proposal_key`, `remedy_kind`, `target_context`, `evidence_refs`, `risk`, `required_approvers`, `limitations` | Apenas planejador; não é receipt de commit |
| `RemedyReceipt` | `proposal_key`, `authorized_issuer`, `host_receipt`, `result`, `world_time`, `revision` | Somente após canal/comando autorizado e confirmação |

## Algoritmo normativo (pré-SPEC)

```text
IF correction/provenance != COMMITTED+CURATED: QUARANTINE
IF branch/build/epochs/lineage/registry invalid: QUARANTINE
IF request principal/purpose/subject/consent/ACL invalid: DENY
IF context contains unknown owner, secret leak or unsupported action: DENY/QUARANTINE
IF harm is only alleged/disputed: do not offer material restitution as established fact
IF exposure is absent: no automatic belief/trust update
IF correction not actually received/perceived by target: propose lawful limited disclosure ONLY
IF belief revision absent: DO NOT assume confidence restored
ELSE prepare scoped, risk-reviewed opportunities for clarification / response / trust review
IF separate, proven damage + resources + owner + consent: MAY PROPOSE restitution, never commit
NEVER rewrite host reputation, PC decision, quest flag, NPC memory or historic damage
```

## Compatibilidade e aceite

1. Verificar em Windows BG2:EE/EEex, bridge, host e dois clientes as capabilities reais de leitura de reputação, mudança de relacionamento, quests, transação, exibição de comunicados e persistência. Nenhuma foi comprovada por esta ADR.
2. Avaliar a confidencialidade nos canais de rumor, fontes protegidas, identidades/pseudônimos, ACL pré-prompt e logs.
3. Testar save/load, forks, clocks, recibos, `UNCERTAIN`, duplicidade, replay, continuidade e NPCs não presentes.
4. Garantir que o motor possa permanecer sem qualquer escrita se só forem elegíveis propostas de diálogo.
5. Todos os cenários T106 são **candidatos não executados no jogo**, inclusive os que mencionam pagamentos, quests, comércio e política.

## Próxima decisão — DEC-107 (EM ABERTO)

**Direito de resposta e mediação de disputas reputacionais**, sem consolidar indevidamente opinião pública: A — um pronunciamento global obrigatório; B — LLM escreve/decide a mediação; **C recomendada:** contestação voluntária, provas e fontes versionadas, canal/audiência legítimos, direito de recusa, ACL e procedimento auditável, nenhuma confissão forçada ou alteração automática de crença/reputação.
