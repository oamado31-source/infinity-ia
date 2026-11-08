# DEC-087 — Agentes duplos, lealdades, confiança e conflitos causais de NPCs

**Discovery v8.3 · ADR-0082 · Opção C APROVADA COMO ARQUITETURA · NÃO IMPLEMENTADA**  
**80 cenários candidatos de teste T087-01 a T087-80 — TODOS NÃO EXECUTADOS.**  
**Escopo:** NPCs, companheiros, guildas, facções, segredos e compromissos; não programação já integrada a BG2:EE.

## 1. Fronteiras de autoridade

- **Fatos:** prova de compromisso/autoria e regras validadas; `UNKNOWN`/`ALLEGED` não são fatos.
- **Motivações:** perfis canônicos/estabelecidos, histórico confirmado, decisões verificadas de NPC; LLM não inventa uma necessidade oculta para justificar traição.
- **Agência:** PC somente por titular/delegação específica; NPC toma opções narrativas sob a política de autonomia DEC-047/048, sem controle arbitrário do motor.
- **Crença:** guildas e NPCs conhecem apenas o que observaram/receberam por canal legítimo DEC-029/064/074.
- **Mecânica:** alterações de party, faction, itens, quest, alinhamento ou hostilidade somente com DEC-011/012, risco DEC-027 e capability testada por build.

## 2. Separação entre identidade, compromisso, percepção e prova

```text
                       ActorIdentity [PRIVADA/VERIFICADA DEC-066]
                                      |
                      +---------------+------------------+
                      |                                  |
             NPCDisposition                     LoyaltyBond(s)
      [valores, limites, fonte]          [dever, confiança, pessoa/facção]
                      |                                  |
                      +-----------+----------------------+
                                  |
                         ConflictAssessment
                 [conflito real? evidências? opções?]
                                  |
                    NPCReaction / DualAllegianceProposal
                                  |
           DeterministicRules + ACL + RiskGate + Consent
                                  |
                      ValidatedTransition/Receipt
                                  |
           EventLog/Projection privada por campanha + branch
                                  |
     ObserverBelief / Rumor / Divulgação por fonte e canal válidos
```

A ficha mecânica de um NPC e a identidade social/persona são entidades distintas. `LoyaltyBond` não confere identidade factual de outra persona. Crenças podem ser falsas e não devem alterar fatos automaticamente.

## 3. Contratos de dados candidatos — não implementados

```text
LoyaltyBond {
  campaign_id, branch_id, bond_id, npc_identity_id,
  beneficiary_type: PERSON|PARTY|FACTION|INSTITUTION|CAUSE,
  beneficiary_ref, bond_kind: TRUST|DUTY|FAMILY|OATH|FEAR|DEBT|OTHER,
  declared_or_private, strength_band?, valid_from_dr?, valid_to_dr?,
  causal_evidence_refs[], source_provenance_refs[], visibility_acl,
  knowledge_pack_pin, revision, checkpoint_epoch
}
Commitment {
  commitment_id, issuer_actor_id, beneficiary_ref, stated_terms,
  authorization_ref?, source_event_id, status: PROPOSED|ACCEPTED|REFUSED|
    FULFILLED|BROKEN|EXPIRED|DISPUTED, obligations[], cost_refs[],
  time_dr, audience_scope, rev
}
LoyaltyConflictAssessment {
  assessment_id, npc_identity_id, bond_refs[], affected_commitment_refs[],
  event_evidence_refs[], worldview_or_values_refs[], alternatives[],
  cannot_conclude_reasons[], risk_class, autonomy_policy_revision,
  outcome: NO_CONFLICT|TENSION|CONFLICTED|INCONCLUSIVE,
  checkpoint_ref, decision_trace_redacted, revision
}
DualAllegianceProposal {
  proposal_id, actor_identity_id, bond_refs[], proposed_scope,
  actor_type: PC|NPC, cause_event_id, possible_actions[],
  motivation_evidence_refs[], owner_consent_ref?, resources[],
  affected_parties[], disclosure_policy_refs[], risk_class,
  requires_host_receipt, state: PROPOSED|VALIDATED|AUTHORIZED|
    DECLINED|STAGED|UNCERTAIN|CONFIRMED|RECONCILED
}
LoyaltyTransition {
  transition_id, npc_identity_id, before_bond_revision, after_bond_revision?,
  proposal_id, cause_event_id, evidence_refs[],
  time_dr, applied_policy_revision, campaign_id, branch_id,
  knowledge_pack_pin, checkpoint_epoch,
  narrative_receipt_ref?, mechanical_host_receipt_ref?,
  idempotency_key, audit_ref, state
}
ObserverBeliefOnLoyalty {
  observer_id, alleged_npc_id, proposition, source_chain[],
  time_learned_dr, confidence_label, contradiction_refs[],
  acl, revision
}
```

`strength_band` é ordem qualitativa candidata, não é porcentagem oficial de amizade, teste de persuasão ou estatística do BG2:EE. Entidades e estados são exemplos para SPECS, sem schema definitivo.

## 4. Estados e condições candidatas

| Situação | Evidência | Próxima ação permitida |
|---|---|---|
| `STABLE` | Compromissos válidos e sem conflitos relevantes | Manter estado; sem tick de LLM. |
| `TENSION` | Evento contrário a valores, com origem | Propor comentário/pergunta. |
| `CONFLICTED` | Obrigações incompatíveis verificadas | Propor alternativas limitadas; pode permanecer sem decisão. |
| `NEGOTIATING` | Oferta/conversa permitida e acessível | Avaliar opções, recursos, consentimentos. |
| `DUAL_COMMITMENT_PROPOSED` | Ação elegível com motivação comprovada | Avaliar ACL, prioridades e risco; nenhuma nova lealdade confirmada. |
| `DUAL_COMMITMENT_VERIFIED` | Ato/compromisso validado conforme política e autoridade | Atualizar vínculo privado, não conhecimento público. |
| `REFUSAL_PENDING` | Limite ou recusa NPC alegada | Diálogo e eventual gateway; não presumir veto mecânico. |
| `RUPTURE_PROPOSED` | Desacordo grave e meios/autoridade | Gate DEC-027/048, risco e confirmação quando mecânico. |
| `RECONCILIATION_PENDING` | Novo fato relevante | Propor revisão sem apagar eventos antigos. |
| `DISPUTED/UNCERTAIN` | Prova inconclusiva ou host receipt ausente | Bloquear promoção irreversível e retry cego. |

Os estados podem ser eixos simultâneos na SPECS. **Tensão ou suspeita não equivalem a traição.**

## 5. Pipeline de avaliação determinística

1. **Receber** evento com `event_id`, fonte, campanha, ramo, época, região, participantes e evidência; `UNKNOWN` se faltarem dados.
2. **Validar** identidade do NPC DEC-066, compatibilidade de regras/build, âncoras canônicas DEC-050 e opções de autonomia DEC-047/048.
3. **Consultar** somente fatos da era via partições anuais DEC-060 e Knowledge Pack pinado DEC-063; compromissos dinâmicos residem no overlay privado do branch.
4. **Filtrar ACL** por agente/observador e finalidade antes do LLM, incluindo pseudônimos, fontes e redes de confiança DEC-076/083/085.
5. **Avaliar** se o acontecimento contraria vínculos existentes; não inventar motivações ou transformar contato com rival em traição.
6. **Produzir candidatos**: manter estado, pedir explicação, negociar, colaborar limitadamente, recusar, proteger fonte, romper/reconciliar sob política.
7. **Verificar recursos e risco** de cada alternativa (tempo, presença, contratos, disponibilidade, danos a terceiros, PC agency, histórico, direitos e cancelação).
8. **Oferecer diálogo** opcional por LLM local, restrita a contexto e opções filtrados; o texto não é uma prova de mudança de lealdade.
9. **Confirmar** fatos exclusivamente por evento narrativo elegível e, quando houver efeito de engine, Action Gateway + host receipt. Caso contrário deixar apenas `PROPOSED`/`UNCERTAIN`.
10. **Projetar** novos vínculos/credibilidade por `transition_id` idempotente, mantendo revisões e histórico; revelar informações a terceiros só por canal causal.

### 5.1 Sem mudança por mera estimativa de IA

Não são gatilhos suficientes isoladamente: uma frase ambígua, afinidade por outra facção, pagamento não executado, boato duplicado, nome parecido, falha de comunicação, ausência do NPC, mudança de humor improvisada por LLM ou interpretação do silêncio de um jogador como consentimento.

### 5.2 Coação, fraude e risco

A presença de chantagem, refém ou ameaça não entrega controle automático de um NPC ao coator. Registrar separadamente ameaça, capacidade do agressor, conhecimento, opções de recusa e proteções DEC-041/042/083/084. Mudança de lado de alto impacto sobre canon, party, quest ou integridade de PC exige o conjunto de gates aplicável, com indeferimento por padrão se informação ou autorização crítica faltar.

## 6. Canonicidade e conflitos com BG2:EE/EEex

O jogo pode conter scripts, romances, quests e falas próprias de companions. A DEC-087 **não** as substitui; contratos sociais externos não pressupõem engine suportar alteração de allegiance/faction flag ou saída de party em runtime. Reações narrativas só podem fazer afirmações que a engine ou o log verificado não contradigam. POCs futuras: baseline Windows limpo, EEex e bridge read-only, safety gateway, compatibilidade de mods, host+2 clientes, save/reload, ausência e saída/retorno de NPC — cada uma com resultados observados, não presumidos.

## 7. Segurança, consentimento e proteção de identidades

| Domínio | Proteção obrigatória |
|---|---|
| PC titular | Nunca deduzir vontade, traição ou aceitação; só ação/consentimento explicitamente autorizados. |
| Delegação de PC | Permissão granular com prazo/scope; sem autorização genérica para alianças ocultas. |
| Companion NPC | Agência narrativa contextual; controle tático não equivale a controle de personalidade. |
| Guilda A | Conhece sua relação com NPC, não necessariamente contatos secretos em B. |
| Guilda B | Só conhece contato se houve canal e evidência; pode estar enganada. |
| Narrador/LLM | Contexto mínimo filtrado por finalidade; nunca publica matriz privada de compromissos por descuido. |
| Operação de contraespionagem | `PlantedClaim` é alegação fabricada e não prova de colaboração real. |
| Host | Pode verificar identidade/efeito sem torná-los conhecidos por NPCs. |
| Fações e autoridades | Suspeita de agente duplo não ativa automaticamente sanção, prisão ou hostilidade. |
| Cache/log/LAN | Campos sensíveis com ACL, revisão, invalidação e redação. |

## 8. Cronologia, persistência e recuperação

A vida persistente DEC-068 utiliza atividade adaptativa sem LLM por tick. Mudanças de lealdade são eventos versionados, com `time_dr` e `checkpoint_epoch`; em restore, descartar proposta de outro ramo e evitar aplicação duplicada. Repassar crenças requer difusão contextual, sem reescrever percepções passadas. Retenção de compromisso não modifica cânone anual físico. Diferenças entre actor ID da engine e identidade lógica do NPC impedem fusão por nome/sprite.

## 9. Matriz de testes candidatos — TODOS NÃO EXECUTADOS

Cada teste precisa de fixture, política de risco, resultado esperado, versão e evidência de execução. A matriz **não afirma execução nem POC de motor**.

| ID | Área | Cenário a verificar | Estado |
|---|---|---|---|
| T087-01 | Identidade, vínculos e compromisso | NPC com duas obrigações simultâneas mantém identidades de compromisso distintas. | **NÃO EXECUTADO** |
| T087-02 | Identidade, vínculos e compromisso | Nome igual entre dois NPCs não transfere vínculo ou dívida. | **NÃO EXECUTADO** |
| T087-03 | Identidade, vínculos e compromisso | Filiação formal não implica lealdade em toda decisão institucional. | **NÃO EXECUTADO** |
| T087-04 | Identidade, vínculos e compromisso | Compromisso confirmado exige origem e autor autorizados. | **NÃO EXECUTADO** |
| T087-05 | Identidade, vínculos e compromisso | Promessa apenas proposta pela LLM não altera registro factual. | **NÃO EXECUTADO** |
| T087-06 | Identidade, vínculos e compromisso | Perfil canônico divergente bloqueia mudança drástica sem curadoria. | **NÃO EXECUTADO** |
| T087-07 | Identidade, vínculos e compromisso | Vínculo histórico é versionado sem apagar estado passado. | **NÃO EXECUTADO** |
| T087-08 | Identidade, vínculos e compromisso | Duas facções sem relação causal não compartilham confiança. | **NÃO EXECUTADO** |
| T087-09 | Identidade, vínculos e compromisso | Contato ocasional com rival não é prova de espionagem. | **NÃO EXECUTADO** |
| T087-10 | Identidade, vínculos e compromisso | Estado UNKNOWN não é tratado como deslealdade comprovada. | **NÃO EXECUTADO** |
| T087-11 | NPC, autonomia e decisão | NPC em conflito pode optar por manter lealdade anterior. | **NÃO EXECUTADO** |
| T087-12 | NPC, autonomia e decisão | NPC pode recusar oferta de dupla colaboração sem punição inventada. | **NÃO EXECUTADO** |
| T087-13 | NPC, autonomia e decisão | NPC pode negociar condições sem comprometer recurso inexistente. | **NÃO EXECUTADO** |
| T087-14 | NPC, autonomia e decisão | Conflito de valores causa proposta de diálogo, não ataque automático. | **NÃO EXECUTADO** |
| T087-15 | NPC, autonomia e decisão | Confiança aumenta somente após evento relevante comprovado. | **NÃO EXECUTADO** |
| T087-16 | NPC, autonomia e decisão | Promessa quebrada é atribuída somente ao ator que a confirmou. | **NÃO EXECUTADO** |
| T087-17 | NPC, autonomia e decisão | NPC canônico respeita restrições de personalidade e quest. | **NÃO EXECUTADO** |
| T087-18 | NPC, autonomia e decisão | Estado CONFLICTED pode persistir sem transição forçada. | **NÃO EXECUTADO** |
| T087-19 | NPC, autonomia e decisão | Reconciliação requer novo evento, sem retcon. | **NÃO EXECUTADO** |
| T087-20 | NPC, autonomia e decisão | NPC recusando ordem não pressupõe veto mecânico da engine. | **NÃO EXECUTADO** |
| T087-21 | Agência e coop de jogadores | LLM não determina traição de PC sem consentimento do titular. | **NÃO EXECUTADO** |
| T087-22 | Agência e coop de jogadores | Jogador delegado sem escopo não autoriza aliança secreta. | **NÃO EXECUTADO** |
| T087-23 | Agência e coop de jogadores | PC ausente não é forçado a confirmar compromisso. | **NÃO EXECUTADO** |
| T087-24 | Agência e coop de jogadores | Outro jogador não lê lealdade privada do PC por estar na party. | **NÃO EXECUTADO** |
| T087-25 | Agência e coop de jogadores | Conflito de NPC não inicia PvP obrigatório. | **NÃO EXECUTADO** |
| T087-26 | Agência e coop de jogadores | Escolha narrativa de PC não é atribuída ao companion controlado. | **NÃO EXECUTADO** |
| T087-27 | Agência e coop de jogadores | NPC não controla itens do PC com base em suposta lealdade. | **NÃO EXECUTADO** |
| T087-28 | Agência e coop de jogadores | Sigilo entre jogadores permanece com ACL DEC-019/041. | **NÃO EXECUTADO** |
| T087-29 | Agência e coop de jogadores | Evento de dano HIGH a PC é bloqueado sem gate aplicável. | **NÃO EXECUTADO** |
| T087-30 | Agência e coop de jogadores | Titular pode contestar declaração falsa atribuída ao PC. | **NÃO EXECUTADO** |
| T087-31 | Evidência e investigações | Suspeita de dupla lealdade não confirma vínculo privado. | **NÃO EXECUTADO** |
| T087-32 | Evidência e investigações | Duas retransmissões de uma denúncia não contam como provas independentes. | **NÃO EXECUTADO** |
| T087-33 | Evidência e investigações | Documento plantado é claim, nunca host receipt. | **NÃO EXECUTADO** |
| T087-34 | Evidência e investigações | Prova contraditória mantém caso DISPUTED. | **NÃO EXECUTADO** |
| T087-35 | Evidência e investigações | Mensagem forjada não cria ato confirmado. | **NÃO EXECUTADO** |
| T087-36 | Evidência e investigações | Falha de observação deixa ação do NPC UNKNOWN. | **NÃO EXECUTADO** |
| T087-37 | Evidência e investigações | Investigador com acesso parcial não vê rede inteira. | **NÃO EXECUTADO** |
| T087-38 | Evidência e investigações | Denúncia anônima preserva fonte DEC-083. | **NÃO EXECUTADO** |
| T087-39 | Evidência e investigações | Confirmação de ação real não comprova intenção oculta automaticamente. | **NÃO EXECUTADO** |
| T087-40 | Evidência e investigações | Conclusão de investigação não autoriza sanção mecânica direta. | **NÃO EXECUTADO** |
| T087-41 | ACL, rumores e confiança | Guilda original não aprende vínculo secreto por consulta ao ledger. | **NÃO EXECUTADO** |
| T087-42 | ACL, rumores e confiança | Rumor só alcança NPC por canal temporal válido. | **NÃO EXECUTADO** |
| T087-43 | ACL, rumores e confiança | Mensagem para um NPC não é divulgada globalmente. | **NÃO EXECUTADO** |
| T087-44 | ACL, rumores e confiança | LLM recebe persona e crenças filtradas em vez de verdade secreta. | **NÃO EXECUTADO** |
| T087-45 | ACL, rumores e confiança | Cache de worker LAN sem ACL não recebe compromissos confidenciais. | **NÃO EXECUTADO** |
| T087-46 | ACL, rumores e confiança | Log para cliente redige nomes e vínculos protegidos. | **NÃO EXECUTADO** |
| T087-47 | ACL, rumores e confiança | NPC pode acreditar falsamente em traição e depois corrigir crença. | **NÃO EXECUTADO** |
| T087-48 | ACL, rumores e confiança | Informante vazado não torna publicamente conhecidos outros contatos. | **NÃO EXECUTADO** |
| T087-49 | ACL, rumores e confiança | Revogação de ACL bloqueia novos acessos, não apaga memória adquirida. | **NÃO EXECUTADO** |
| T087-50 | ACL, rumores e confiança | Conhecimento privado do host não é conhecimento de personagem. | **NÃO EXECUTADO** |
| T087-51 | Facções, recursos e consequências | Pagamento prometido não transfere ouro sem receipt confirmado. | **NÃO EXECUTADO** |
| T087-52 | Facções, recursos e consequências | Participar de duas guildas não gera reputação mecânica instantânea. | **NÃO EXECUTADO** |
| T087-53 | Facções, recursos e consequências | Não produzir espias infinitos por repetição de proposta. | **NÃO EXECUTADO** |
| T087-54 | Facções, recursos e consequências | Mudança de confiança não duplica recompensa ou XP. | **NÃO EXECUTADO** |
| T087-55 | Facções, recursos e consequências | Ruptura com guilda exige motivo e precondições. | **NÃO EXECUTADO** |
| T087-56 | Facções, recursos e consequências | Contato com rival não implica crime para aplicação da DEC-078. | **NÃO EXECUTADO** |
| T087-57 | Facções, recursos e consequências | Oficial corrupto não torna todo governo cúmplice. | **NÃO EXECUTADO** |
| T087-58 | Facções, recursos e consequências | Plano de escolta não vaza com mudança de lealdade sem canal. | **NÃO EXECUTADO** |
| T087-59 | Facções, recursos e consequências | Emboscada associada a traição exige recurso, risco e presença real. | **NÃO EXECUTADO** |
| T087-60 | Facções, recursos e consequências | NPC não é teletransportado para encontro de facção. | **NÃO EXECUTADO** |
| T087-61 | Cronologia e recuperação | Ramo alternativo não importa aliança secreta de outro branch. | **NÃO EXECUTADO** |
| T087-62 | Cronologia e recuperação | Checkpoint anterior não conhece traição futura. | **NÃO EXECUTADO** |
| T087-63 | Cronologia e recuperação | Nova revisão do Knowledge Pack não reescreve compromisso da campanha. | **NÃO EXECUTADO** |
| T087-64 | Cronologia e recuperação | NPC DORMANT não descobre reunião sem comunicação possível. | **NÃO EXECUTADO** |
| T087-65 | Cronologia e recuperação | Catch-up limitado não inventa anos de espionagem. | **NÃO EXECUTADO** |
| T087-66 | Cronologia e recuperação | Evento repetido após reload não muda lealdade duas vezes. | **NÃO EXECUTADO** |
| T087-67 | Cronologia e recuperação | Fenced epoch rejeita proposta stale anterior a restore. | **NÃO EXECUTADO** |
| T087-68 | Cronologia e recuperação | UNCERTAIN não permite retry cego de saída de party. | **NÃO EXECUTADO** |
| T087-69 | Cronologia e recuperação | Cancelamento de oferta não apaga comunicações já recebidas. | **NÃO EXECUTADO** |
| T087-70 | Cronologia e recuperação | Identidade NPC após respawn exige reconciliação DEC-066. | **NÃO EXECUTADO** |
| T087-71 | Build, validação e integração | Falta de hook de faction flag bloqueia alteração mecânica. | **NÃO EXECUTADO** |
| T087-72 | Build, validação e integração | Controle tático de NPC não implica autorização narrativa absoluta. | **NÃO EXECUTADO** |
| T087-73 | Build, validação e integração | Mudança de party exige host receipt e capability demonstrada. | **NÃO EXECUTADO** |
| T087-74 | Build, validação e integração | NPC com script nativo protegido não sofre edição sem DEC-050. | **NÃO EXECUTADO** |
| T087-75 | Build, validação e integração | World lore anual não recebe segredos dinâmicos da campanha. | **NÃO EXECUTADO** |
| T087-76 | Build, validação e integração | LM valida apenas texto de fala e não decide estado mecânico. | **NÃO EXECUTADO** |
| T087-77 | Build, validação e integração | Gates rejeitam alinhamento nativo alterado sem operação autorizada. | **NÃO EXECUTADO** |
| T087-78 | Build, validação e integração | Falha da bridge não declara desertor confirmado. | **NÃO EXECUTADO** |
| T087-79 | Build, validação e integração | Multiplayer host+2 clientes é pré-requisito de alegação de sincronização. | **NÃO EXECUTADO** |
| T087-80 | Build, validação e integração | Plano de teste contempla recusa, não cooperação e negociação sem resultados presumidos. | **NÃO EXECUTADO** |

## 10. Plano de testes e checkpoints (pendente)

1. Especificar fixtures NPC com vínculos ortogonais e histórias de família/guilda, além de NPCs canônicos com âncoras protegidas.
2. Simular acordos voluntários, promessas negadas, boatos, infiltrações falsas, tensões morais e versões conflitantes, verificando `UNKNOWN` e contestação.
3. Validar consentimentos, privacidade interjogadores, delegação, logs/clientes/LAN e precondições de gastos.
4. Testar determinismo, dedup, branch rollback, checkpoint, Knowledge Pack pinned e catch-up de NPCs DORMANT sem LLM por tick.
5. Testar gateway read-only antes de qualquer alteração de faction, party, inventário, quests ou hostilidade; depois host+2 clientes somente se build permitir.
6. Avaliar métricas de segurança, ausência de vazamentos/traidores arbitrários e aderência a fontes canônicas; resultados permanecem PENDENTES.

## 11. DEC-088 (aberta) — Recrutamento e gestão de informantes

A) recrutamento instantâneo por preço/oferta, com lealdade presumida; B) negociação livre da IA sem provas de compromisso/custo; **C (recomendada)** contrato contextual de colaboração voluntária com negociação, limites, recursos, confidencialidade, recusa e saída, proteção de PCs e verificação de consequências. A DEC-087 trata do conflito de vínculos e não antecipa detalhes de recrutamento nem as SPECS.

## 12. Dependências explícitas

DEC-019/027/028/029/030/032/034/041/042/045/046/047/048/049/050/051/053/056/057–060/060–086. DEC-060–063 preservam o cânone físico por ano DR, proveniência e Knowledge Pack; DEC-064–068 memória/identidade/persistência; DEC-069–075 geografia/causalidade/autoria; DEC-076–086 segredos, investigações, instituições, fontes e engano. DEC-006/007/013/015/017/018 continuam abertas em seus escopos.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

DEC-088 complementa DEC-087: lealdades privadas e conflitos não são automaticamente contrato de espionagem. Oferta e aceite voluntário exigem termos, recursos e consentimento.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Lealdades rivais podem influenciar hipótese de viés, mas não comprovam falsidade ou traição; perfis de fontes são contextuais e contestáveis.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Dossiês podem relatar suspeitas de agente duplo, mas não revelam vínculos privados/compromissos por padrão; lealdade real ≠ relato ≠ crença da audiência.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Lealdade de agente duplo não pode ser mudada para cumprir objetivos de planner; autonomia e compromissos reais prevalecem.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

NPC com lealdades divididas pode negar plano revisado; conflito pessoal não é traição automática nem autorização de hostilidade.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

NPC agente duplo não é duplicado como duas identidades alocáveis; conflito de lealdade pode provocar recusa contextual, não teleportar o ator.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Arbitrar recurso de NPC com múltiplas lealdades não altera compromissos/relações sem decisão do próprio NPC e evidência.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Lealdade dinâmica não permite editar scripts nativos de companions/quests sem capability verificada.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Lealdades de NPC não são inferidas por futuros gatilhos de scripts observados sem divulgação.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Quest state, mapping rule names and even flag metadata may expose future branches, romance or hidden identities; they remain private technical evidence. Dossiers, sources and NPCs receive only authorized safe milestones through independently confirmed disclosure; no belief is promoted to fact from ambiguous observations. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **suspeita refutada e memória do NPC**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para lealdades NPC podem influenciar contestação sem criar nova verdade, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para lealdade NPC e confiança não são resetadas automaticamente, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Agentes duplos não provam pagamentos por alegação de confiança. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Lealdades divididas não mudam titularidade de obrigação. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
