# DEC-086 — Contraespionagem, iscas e desinformação: autoria, controle e revisão causal

**Discovery v8.2 · ADR-0081 · DEC-086/C APROVADA APENAS COMO ARQUITETURA · NÃO IMPLEMENTADA**  
**Evidência:** decisão expressa; **76 testes candidatos T086-01..T086-76, todos NÃO EXECUTADOS.**

## 1. Objetivo e fronteiras

Permitir contraespionagem ficcional com alegações intencionalmente plantadas, iscas e mensagens enganosas **sem** transformar o conteúdo falso em fato. O mecanismo usa regras determinísticas verificáveis para autorização, recursos, cronologia e divulgação; a LLM local apenas sugere formulações e possíveis interpretações sob política. Sem autonomia para modificar mundo, inventar crime, falsificar recibo de host ou reescrever o cânone. A operação pode falhar, ser descoberta ou não surtir efeito.

## 2. Separação de domínios e armazenamento lógico candidato

```text
knowledge/periods/<ANO>-DR/                  # lore canônico físico/curado por ano; DEC-060–063
campaign-overlays/<campaign>/<branch>/       # esquema lógico candidato; caminho físico final em SPECS
  verified-world-events/                     # fatos e receipts, sem adulteração por engano
  protected-identity-persona/                # DEC-076 e DEC-083
  protection-plan/<plan_revision>/           # plano verdadeiro DEC-084/085, ACL estrita
  deception-operations/<operation_id>/
    proposals/                               # intenção, dono, alvo, consentimentos
    authorizations-and-risk/                 # gates, políticas e validade
    decoy-assets-and-false-claims/           # narrativa fabricada, proveniência e tipo falso
    resource-reservations/                   # custo, tempo, alocação, TTL
    dissemination-and-delivery/              # canais, destinatários, receipts
    recipient-beliefs/                       # quem realmente recebeu/acreditou/suspeitou
    discovery-and-contestation/              # refutação, confiança, consequências propostas
    audit-and-checkpoints/                   # revisões, idempotência, falhas
```

A árvore de overlays é **ilustrativa, não implementada**. Textos de mensagem de isca não entram em lore canônico nem no Knowledge Pack. A verdade privada da campanha fica segregada por branch e ACL.

## 3. Esquemas candidatos — não implementados

```text
DeceptionOperation {
  campaign_id, branch_id, operation_id, objective, operation_kind,
  proponent_actor_id, player_owner_id?, authorization_ref?,
  subject_protection_case_ref?, protected_plan_revision_ref?,
  target_audience_scope[], location_scope, world_time_dr, validity_window,
  risk_classification, accumulated_risk, expected_third_party_impact,
  rule_revision, checkpoint_ref, resolution_epoch,
  status: DRAFT|VALIDATED|AUTHORIZED|RESOURCES_RESERVED|STAGED|
          DISSEMINATED|SUSPECTED_COMPROMISED|CONFIRMED_EXPOSED|
          CANCELLED|EXPIRED|UNCERTAIN|RECONCILED
}
PlantedClaim {
  claim_id, operation_id, factual_status: INTENTIONALLY_FALSE|UNVERIFIED|CONTESTED,
  claimed_subject_id?, claim_text, originator_private_ref, source_type,
  claimed_source_public_ref?, provenance_private, audience_acl,
  world_time_dr, effective_from?, effective_to?, revision
}
DecoyAsset {
  decoy_id, operation_id, decoy_type: RUMOR|MESSAGE|ALIAS|VISIBLE_DISTRACTION|OTHER,
  narrative_payload, engine_capability_required?, host_action_ref?,
  resource_reservation_ref?, status: PROPOSED|APPROVED|STAGED|CONFIRMED|UNCERTAIN
}
ResourceReservation {
  reservation_id, operation_id, actor_or_asset_ref, cost_type, quantity,
  availability_evidence, reserved_from_dr, expires_at_dr,
  status: REQUESTED|RESERVED|COMMITTED|RELEASED|UNCERTAIN
}
DisseminationEvent {
  event_id, operation_id, claim_id, sender_id?, receiver_scope, channel,
  opportunity_evidence, source_chain[], send_time_dr, delivered_time_dr?,
  receipt_ref?, idempotency_key, attempt_state, checkpoint_epoch
}
RecipientBelief {
  recipient_actor_or_faction_ref, claim_id, source_chain[], confidence_label,
  learned_at_dr, rejected_or_contested_at_dr?, memory_revision, acl
}
DeceptionReview {
  review_id, operation_id, evaluator_scope, corroboration_refs[],
  contradiction_refs[], exposure_scope, impact_refs[],
  outcome: UNKNOWN|INEFFECTIVE|PARTIAL|BELIEVED|CONTESTED|EXPOSED|UNCERTAIN,
  risk_gate_ref, revision, audit_ref
}
```

IDs de evento e de claim são diferentes; `ReceiptRef` é opaco e gerado/validado pela integração, nunca pelo texto de LLM. Estado do NPC e avaliação do host continuam separados. `PlantedClaim` pode ser falso deliberado ou não verificado **e tal status não pode ser consultado pelo NPC sem acesso legítimo**.

## 4. Máquina de estados e precondições

```text
DRAFT -> VALIDATED             # esquema/autor/limites de terceiros e risco
VALIDATED -> AUTHORIZED        # consentimento, ACL, política e host conforme nível
AUTHORIZED -> RESOURCES_RESERVED  # disponibilidade real/TTL/sem gasto duplicado
RESOURCES_RESERVED -> STAGED  # artefato/plano de difusão elegíveis
STAGED -> DISSEMINATED         # prova de envio/recepção conforme o canal
[STAGED] -> CANCELLED|EXPIRED # antes do envio, liberar reservas com recibos
DISSEMINATED -> SUSPECTED_COMPROMISED|CONFIRMED_EXPOSED|RECONCILED
[qualquer fase técnica] -> UNCERTAIN  # não repetir cegamente; reconciliar
```

O `RecipientBelief` nasce **somente** após recepção fundamentada, e pode representar rejeição da isca. Mesmo `DISSEMINATED` não significa `BELIEVED`, não gera ataque e não confirma presença ou identidade secreta. Fatos verificados do motor permanecem invariantes.

## 5. Gates e responsabilidade

1. **Agência:** decisão ativa de PC precisa de seu titular; controle delegado não autoriza falsificar testemunho, usar identidade de terceiro ou revelar segredo. Para NPC, exigir autonomia e recursos DEC-047/048/068.
2. **Legitimidade narrativa:** propósito, tipo de isca, público, meios, timing, fonte que poderá receber, expectativa de efeito, terceiro afetado, saída e custos.
3. **Danos indiretos:** falsa acusação de crime, PVP, fuga, exposição de denunciante, ameaça física, mudança de regime, prisão/confisco e eventos irreversíveis exigem escalada por risco; `HIGH` não pode avançar com política/autoridade ambígua.
4. **Conhecimento:** o emissor pode conhecer a falsidade; o receptor só recebe o claim por canal válido. Auditor e safety gate não informam o NPC automaticamente.
5. **Evidência:** assinatura falsa é um dado ficcional representado como tal; não pode virar autenticação host, prova jurídica, item real ou certeza de identidade.
6. **Motor:** qualquer spawn, item, viagem, alteração visual, script ou flag de missão exige capability por build, autorização gateway, host receipt e POC host+2 clientes. Sem isso, usar representação puramente narrativa com verdade de estado claramente limitada.

## 6. Fluxo operacional proposto

```text
(1) intenção atribuída e autorizada
    -> (2) validação determinística de política e risco
    -> (3) confirmação de recursos, canais e cronologia
    -> (4) isolamento entre plano verdadeiro e claims fabricados
    -> (5) publicação por canal permitido, com recibo e idempotência
    -> (6) crença do observador após receber, podendo rejeitar
    -> (7) investigação/refutação posterior com evidências
    -> (8) consequências sociais contextuais; efeito mecânico só por host
```

**Exemplo:** o defensor autoriza rumor de horário alternativo. Um mensageiro disponível sai e encontra contato; só esse contato aprende a mensagem. Se a guilda recebe o rumor, pode decidir investigá-lo com recursos próprios; não recebe a rota real pela função de auditoria. O sucesso de proteção não é garantido e nenhuma emboscada surge por texto.

## 7. Matriz de acesso e adversários

| Público ou ator | Conhecimento permitido | Bloqueio essencial |
|---|---|---|
| Titular do plano | Detalhes conforme role e consentimento | Não divulgar identidades alheias sem autorização |
| Controlador temporário do PC | Só a delegação explícita | Sem licença automática de trair/expor o PC |
| Participante da isca | Sua parte necessária do plano | Rota real fora do need-to-know |
| NPC destinatário | Mensagem efetivamente recebida | Sem fato privado/autor oculto do ledger |
| Fação rival | Informação filtrada por contato, tempo e investigação | Sem consulta global de proteção/segredos |
| Host safety gateway | Fatos, policy e receipts sob ACL | Não exportar identidade a cliente/NPC |
| Worker LAN/LLM | Payload mínimo autorizado por purpose | Sem segredo no fallback, memória e logs |
| Observador posterior | Descobertas por eventos causais | Sem retcon de testemunho ou conhecimento futuro |

## 8. Falhas e proteção contra abuse

- **Double-submit:** dedup por operação, claim, audiência, etapa, checkpoint e revisão, sem duplicar custo ou credibilidade.
- **Entrega não confirmada:** `UNCERTAIN`, não declarar recebimento e reconciliar, sem retry cego.
- **Restauração de save:** epoch/branch invalidam sends futuros; histórico anterior válido fica preservado.
- **Plano atualizado:** nova revisão bloqueia envio obsoleto, mas não remove crenças anteriores de NPCs.
- **Fonte falsa que gera acusação:** manter `Allegation` separado de `ConfirmedCrime`; qualquer acusação/procedimento segue DEC-077–082.
- **Prompt injection/vazamento:** dados do claim são não confiáveis e nunca autorizam ferramentas; sanitizar origem e saída, filtrar ACL antes de gerar texto.
- **Recurso inexistente:** abortar sem criar mensageiro, item, NPC ou custo negativo.
- **Ameaça a terceiros:** desvio LOW→HIGH em cadeia aciona gate acumulado; `fail-closed` se autorização não existe.
- **Conhecimento disperso:** receptores não fundem instantaneamente seus relatos; cronologia e difusão governam.
- **Falha de sincronização multiplayer:** host conserva autoridade, cliente não assina receipt; POC exigida.

## 9. Matriz de 76 testes candidatos — TODOS NÃO EXECUTADOS

Cada caso deve ser parametrizado por fixture e resultado esperado em SPECS; esta lista **não representa testes realizados ou integração validada**.

| ID | Expectativa | Execução |
|---|---|---|
| T086-01 | PC só propõe operação de engano quando seu titular consentir e possuir permissão. | NÃO EXECUTADO |
| T086-02 | Controlador delegado não divulga segredo do titular sem permissão específica. | NÃO EXECUTADO |
| T086-03 | NPC pode propor engano somente dentro de autonomia, recursos e objetivos legítimos. | NÃO EXECUTADO |
| T086-04 | Inexistência de autoria confirmada bloqueia operação atribuída a PC. | NÃO EXECUTADO |
| T086-05 | Uma mensagem plantada é classificada como CLAIM_PLANTED, jamais WORLD_FACT. | NÃO EXECUTADO |
| T086-06 | Documento forjado não cria prova de crime, identidade ou autoria verdadeira. | NÃO EXECUTADO |
| T086-07 | Um recibo de host falsificado como texto não se torna receipt válido. | NÃO EXECUTADO |
| T086-08 | Engano não altera cânone nem os diretórios físicos knowledge/periods por ano DR. | NÃO EXECUTADO |
| T086-09 | Overlay de campanha A não importa plano falso da campanha B. | NÃO EXECUTADO |
| T086-10 | Branch restaurado não recebe desinformação de ramo alternativo. | NÃO EXECUTADO |
| T086-11 | Um plano falso não revela rota verdadeira ao destinatário. | NÃO EXECUTADO |
| T086-12 | Metadados de arquivo não revelam localização protegida em mensagens públicas. | NÃO EXECUTADO |
| T086-13 | Rota com nome codificado ainda é bloqueada se permitir reidentificação indireta. | NÃO EXECUTADO |
| T086-14 | Data da isca deve existir no relógio DR da campanha. | NÃO EXECUTADO |
| T086-15 | Claim futuro não pode influenciar NPC em passado de checkpoint. | NÃO EXECUTADO |
| T086-16 | Envio a destinatário sem canal ou alcance é rejeitado. | NÃO EXECUTADO |
| T086-17 | Mensageiro inexistente não é criado pela narração do LLM. | NÃO EXECUTADO |
| T086-18 | Mensageiro ocupado não pode ser simultaneamente reservado duas vezes. | NÃO EXECUTADO |
| T086-19 | Envio por rota bloqueada não é declarado entregue. | NÃO EXECUTADO |
| T086-20 | Propagação entre regiões respeita atraso e canais plausíveis. | NÃO EXECUTADO |
| T086-21 | NPC que não recebeu a mensagem não a conhece por consulta ao ledger. | NÃO EXECUTADO |
| T086-22 | Modelo LLM não recebe plano verdadeiro em prompt de NPC sem ACL. | NÃO EXECUTADO |
| T086-23 | Fallback de modelo não amplia permissão de segredo. | NÃO EXECUTADO |
| T086-24 | Node LAN sem permissão não recebe rota real ou identidade da testemunha. | NÃO EXECUTADO |
| T086-25 | Revogar grant impede processamento de job sensível pendente. | NÃO EXECUTADO |
| T086-26 | Logs de auditoria externa não contêm campos protegidos. | NÃO EXECUTADO |
| T086-27 | Índice RAG de rumor não produz verdade privada para observador. | NÃO EXECUTADO |
| T086-28 | Dez retransmissões do mesmo boato preservam ancestralidade comum. | NÃO EXECUTADO |
| T086-29 | Dois informantes independentes são representados como fontes distintas só se comprovado. | NÃO EXECUTADO |
| T086-30 | NPC que recebe isca pode ignorá-la por falta de credibilidade, sem sucesso forçado. | NÃO EXECUTADO |
| T086-31 | NPC que suspeita da isca não descobre o plano verdadeiro. | NÃO EXECUTADO |
| T086-32 | NPC que encontra prova de engano revisa crença com motivo e cronologia. | NÃO EXECUTADO |
| T086-33 | Correção posterior não apaga que o NPC acreditou anteriormente. | NÃO EXECUTADO |
| T086-34 | Não inventar testemunho falso pronunciado por PC ausente. | NÃO EXECUTADO |
| T086-35 | Não inventar consentimento de PC para incriminar terceiro. | NÃO EXECUTADO |
| T086-36 | Tentativa de incriminar PC com prova falsa aciona risco e bloqueio apropriado. | NÃO EXECUTADO |
| T086-37 | Alegação plantada não altera automaticamente alinhamento, reputação mecânica ou quest. | NÃO EXECUTADO |
| T086-38 | Falso mandado não autoriza prisão ou confisco. | NÃO EXECUTADO |
| T086-39 | Alegação de traição não confirma vínculo de agente duplo. | NÃO EXECUTADO |
| T086-40 | Fato host-confirmed permanece intacto após campanha de desinformação. | NÃO EXECUTADO |
| T086-41 | Fonte protegida não perde sigilo por criação de pseudônimo da isca. | NÃO EXECUTADO |
| T086-42 | Isolamento campo-a-campo protege nome, horário, abrigo e escolta. | NÃO EXECUTADO |
| T086-43 | Negar operação sem recursos retorna explicação redigida, sem revelar segredos. | NÃO EXECUTADO |
| T086-44 | Reserva falha não consome saldo narrativo nem gera item falso. | NÃO EXECUTADO |
| T086-45 | Retry da mesma proposta não multiplica custo nem rumor publicado. | NÃO EXECUTADO |
| T086-46 | Retry após DISSEMINATED não envia segunda mensagem indevida. | NÃO EXECUTADO |
| T086-47 | Crash entre reserva e envio produz UNCERTAIN e reconciliação. | NÃO EXECUTADO |
| T086-48 | Host sem recibo não autoriza afirmar spawn de objeto de isca. | NÃO EXECUTADO |
| T086-49 | Cliente multiplayer não pode gerar efeitos sem host. | NÃO EXECUTADO |
| T086-50 | Não prometer mudança de aparência como capacidade engine sem teste. | NÃO EXECUTADO |
| T086-51 | Template não suportado em build é rejeitado sem mutação. | NÃO EXECUTADO |
| T086-52 | Comprometimento parcial não implica exposição de todos os campos do plano. | NÃO EXECUTADO |
| T086-53 | Expiração de janela impede novo envio, preservando histórico entregue. | NÃO EXECUTADO |
| T086-54 | Cancelamento anterior ao envio libera recursos sem criar rumor. | NÃO EXECUTADO |
| T086-55 | Cancelamento após envio não faz NPC esquecer mensagem recebida. | NÃO EXECUTADO |
| T086-56 | Rota revisada invalida cache de plano antigo sem borrar crenças já adquiridas. | NÃO EXECUTADO |
| T086-57 | Rollback não transporta mensagens futuras para o passado. | NÃO EXECUTADO |
| T086-58 | Descrição em diálogo não torna documento mecânico existente. | NÃO EXECUTADO |
| T086-59 | Investigação adversária exige capacidade, presença, oportunidade e custo. | NÃO EXECUTADO |
| T086-60 | Descoberta do falso por uma guilda não informa automaticamente outra guilda. | NÃO EXECUTADO |
| T086-61 | Divulgação pública exige canal, destinatário e risco explícitos. | NÃO EXECUTADO |
| T086-62 | Acúmulo de operações LOW que causa HIGH é reavaliado pelo gate. | NÃO EXECUTADO |
| T086-63 | Recompensa, XP ou loot não são criados por número de rumores espalhados. | NÃO EXECUTADO |
| T086-64 | Consequência grave em PC não é criada automaticamente por engano NPC. | NÃO EXECUTADO |
| T086-65 | Operação de proteção não permite emboscada automática de adversário. | NÃO EXECUTADO |
| T086-66 | Autoridade fictícia pode interpretar rumor como suspeita, não verdade host. | NÃO EXECUTADO |
| T086-67 | Reputação social só muda por consequência causal contextual verificada. | NÃO EXECUTADO |
| T086-68 | NPC enganado pode manter crença falsa apesar de verdade privada contrária. | NÃO EXECUTADO |
| T086-69 | A origem privada da fabricação fica auditável e protegida da audiência. | NÃO EXECUTADO |
| T086-70 | ID duplicado de disseminação não altera a crença duas vezes. | NÃO EXECUTADO |
| T086-71 | Alteração de Knowledge Pack exige revisão de validade temporal da operação. | NÃO EXECUTADO |
| T086-72 | Tentativa de disseminação por worker revogado é descartada. | NÃO EXECUTADO |
| T086-73 | Falha na confirmação do host deixa efeito mecânico UNCERTAIN e bloqueado. | NÃO EXECUTADO |
| T086-74 | POC read-only necessária antes de detectar diálogo, documento ou isca na engine. | NÃO EXECUTADO |
| T086-75 | POC BG2:EE/EEex host+2 clientes necessária antes de declarar feature multiplayer. | NÃO EXECUTADO |
| T086-76 | Restauração de checkpoint preserva consistência entre autoria, recursos, crenças e segredo. | NÃO EXECUTADO |

## 10. Ordem de validação técnica futura

1. Fixtures sem BG2:EE: claim falso versus `WorldFact`, IDs, autoria, recursos e cronologia.
2. ACL e segurança: segredos, metadados, LLM, RAG, LAN, histórico de NPCs e PCs delegados.
3. Cenários de rumores copiados, falsos testemunhos, acusações indevidas e fontes contestadas; verificar separação de alegação e fato.
4. Testes determinísticos de autorização, custo, entrega, dedup, `UNCERTAIN`, checkpoint, restauração e branch.
5. POC inicialmente read-only de recursos observáveis na build Windows BG2:EE limpa; depois EEex/bridge compatível.
6. Somente após prova de integração: POC para spawn ou item de isca, mudanças de percepção se houver API, e sincronismo com host + dois clientes.
7. Definir limites finais de templates, credibilidade, revisão de operações e UX em SPECS. **Sem afirmar capacidades inexistentes.**

## 11. Dependências e próxima DEC

- **DEC-060–063:** ano DR físico, curadoria e Knowledge Pack pinado; overlays de campanha jamais reescrevem canon.
- **DEC-064–075:** crenças e memória, identidade NPC, recursos, viagem, incidentes, autoria e consequências.
- **DEC-076–085:** personas, investigação, justiça contextual, revisão de mandados, proteção, ameaça, sigilo e descoberta parcial.
- **DEC-011/012/019/022/027/028/034/041/042/045/046/053/056/057–059:** autorização, risco, agência, gateways, checkpoints e segurança local-first.
- **DEC-006/007/013/015/017/018:** temas anteriores ainda abertos, sem inferir sua resolução.
- **DEC-087 aberta:** agentes duplos, fontes comprometidas e lealdades conflitantes — A proibir dupla filiação, B LLM inverte lealdades livremente, **C lealdades e suspeitas contextuais com evidências, consentimento, confiança revisável e gates**.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Operação de dissimulação DEC-086 é distinta de lealdade real: claim fabricado não comprova compromisso, traição ou mudança de facção.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Fonte recrutada pode veicular mensagem enganosa apenas como operação autorizada e registro `PlantedClaim`, nunca como recibo/fato real.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

`PlantedClaim` de operação de engano mantém o rótulo de alegação estratégica, sem alterar WorldFact e sem corroboração artificial por repasses.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

PlantedClaim pode ser apresentado como relato conforme visão do observador, nunca confirmado só por constar em um relatório; o agente só pode saber da isca se recebeu essa informação.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Isca/informação plantada pode ser objeto de plano autorizado, mas nunca é WorldFact; gateway não executa coerção fundada na mentira.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Desinformação deliberada permanece PlantedClaim mesmo que motive revisão; verdade factual e compromisso de ação são independentes.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Duas operações de dissimulação concorrentes precisam de recursos reais e autoria; boatos podem gerar prioridades de pesquisa, não direitos automáticos sobre NPCs.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Isca não é recurso real extra para resolver deadlock; falso claim preserva rotulagem de engano e nunca é usado para satisfazer reserva física.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-096/C — Discovery v9.2

Pista falsa DEC-086 não reescreve CanonEvent DEC-096/C ou regra; apenas crença recebida do observador, com proveniência.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Desinformação DEC-086 não altera métrica DEC-097/C como fato; apenas eventos host-confirmed e fontes apropriadas.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Iscas e desinformação não se transformam automaticamente em NPCs/objetos reais ao materializar uma área.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Desinformação deliberada é um PlantedClaim, não evidência de origem ou licença de edição do jogo.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Operações de desinformação não alteram flag técnico nem injetam conteúdo falso em projeção semântica.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Quest state, mapping rule names and even flag metadata may expose future branches, romance or hidden identities; they remain private technical evidence. Dossiers, sources and NPCs receive only authorized safe milestones through independently confirmed disclosure; no belief is promoted to fact from ambiguous observations. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para desinformação intencional permanece distinguível de retificação curada, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para desinformação plantada distinta de correção curada, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-109/C — Obrigações condicionais multipartes

Informação plantada não vira recibo ou assinatura confiável. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
