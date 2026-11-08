# 75 — Autoria causal, participação cooperativa e reconhecimento percebido

> **Discovery v7.1 — DEC-075/C aprovada como arquitetura, não implementada.** Este documento propõe contratos, fluxos e testes sem afirmar que o BG2:EE/EEex oferece telemetria individual suficiente. POCs e SPECS são obrigatórias.

## 1. Propósito

Definir como um único encontro confirmado gera (i) contribuição factual sustentada por evidência; (ii) responsabilidade individual e compartilhada sob regras de consentimento; (iii) testemunhos parciais; (iv) percepção social; (v) efeitos proporcionais deduplicados. A DEC-074 rege os canais de propagação. A DEC-075 **não** altera os mecanismos de recompensas da engine nem aprova UI de placar ou análise moral automática.

## 2. Fronteiras de confiança e evidência

- **Camada mecânica:** a instância BG2:EE sob host decide o que ocorreu no jogo. Bridge/EEex só podem fornecer as observações que forem realmente demonstradas em POC por versão e build; nenhum hook assumido.
- **Camada factual:** ledger de evento confirmado DEC-071/073 e evidências atribuídas a personagens/instâncias identificados DEC-066, com revisão causal e checkpoint.
- **Camada narrativa:** o diretor coop e regras determinísticas avaliam categorias de contribuição comprovadas; LLM pode redigir explicações, não inventar autoria.
- **Camada epistêmica:** testemunhas observam seletivamente; relatos e rumores DEC-029/074 contêm crenças/proveniência, não confirmação factual independente.
- **Camada de impacto:** reputação DEC-030, facções DEC-031/032, histórias pessoais DEC-039/040, segurança DEC-041/042 e gateway DEC-012 aplicam regras e gates de autorização.
- **Cânone:** `knowledge/periods/<ANO>-DR/` permanece particionado fisicamente DEC-060, com fontes/curadoria DEC-061/062 e Knowledge Pack fixado DEC-063. Todos os registros de contribuição existem somente no overlay privado `campaign_id/branch_id`.

## 3. Fluxo de dados conceitual

```text
Evento de encontro PROPOSED/UNCERTAIN ----> [NÃO ATRIBUIR]
Evento CONFIRMED + host receipt válido
                |
                v
       Ledger factual do incidente (único)
                |
                v
       Coletar provas realmente disponíveis
                |
                v
       [Identity/Owner/Controller/ACL/Consent Gate]
                |
                v
       Attribution Assessment (UNKNOWN aceito)
                |                        \
                |                         \----> Witness Accounts / Rumors
                v                                      |
       FactualContributionLedger                         v
                |                                 Beliefs by NPC/faction
                |                                      |
                \----------> Causal policy & risk <-----/
                                 |
                                 v
                       AuthorizedDomainEffect
                        /               \
               Narrativo LOW      Efeito de engine
                                  só host/gateway/POC
```

## 4. Entidades e contratos candidatos — não são APIs existentes

```yaml
ConfirmedEncounterEvent:
  campaign_id: string
  branch_id: string
  incident_id: string
  encounter_id: string
  event_id: string
  resolution_epoch: integer
  host_receipt_id: string | null
  checkpoint_revision: string
  world_time_dr: string
  engine_build_fingerprint: string
  certainty: CONFIRMED
  evidence_refs: [opaque_ref]

ActorContributionEvidence:
  evidence_id: string
  event_id: string
  actor_character_id: string | null
  actor_identity_status: VERIFIED | AMBIGUOUS | UNKNOWN
  player_owner_id: string | null
  controlling_player_id: string | null
  contribution_type: COMBAT | DEFENSE | HEALING | SUPPORT | PLANNING | NEGOTIATION | OTHER | UNKNOWN
  evidence_kind: HOST_RECEIPT | CURATED_EVENT | AUTHORIZED_WITNESS | UNKNOWN
  source_ref: string
  observed_time_dr: string
  certainty: CONFIRMED | CORROBORATED | REPORTED | UNKNOWN | DISPUTED
  privacy_acl_ref: string

AttributionAssessment:
  event_id: string
  actor_character_id_or_group_id: string
  participation_category: DIRECT | SUPPORT | INDIRECT | COLLECTIVE | UNKNOWN
  responsibility_scope: INDIVIDUAL | GROUP | UNCERTAIN
  confidence_basis_refs: [opaque_ref]
  status: CONFIRMED | PENDING_EVIDENCE | DISPUTED | REJECTED
  rule_revision: string
  assessment_revision: integer
  authorizing_policy_ref: string

WitnessAccount:
  account_id: string
  claimed_source_event_id: string
  witness_identity_id: string
  observed_actor_or_alias_id: string | null
  claimed_actor_id: string | null
  visibility_basis_ref: string | null
  location_time_ref: string
  transmission_channel_ref: string | null
  testimony: string
  epistemic_status: OBSERVED | HEARD | INFERRED | RUMORED | DISPUTED
  privacy_acl_ref: string

RecognitionProposal:
  source_event_id: string
  observer_or_faction_id: string
  perceived_actor_id_or_alias: string | null
  perception_status: RECOGNIZED | UNATTRIBUTED | MISATTRIBUTED | DISPUTED
  source_account_refs: [opaque_ref]
  target_dimension: FAME | TRUST | RESPECT | FEAR | HOSTILITY | FAVOR | NONE
  proposed_effect: opaque
  risk: LOW | MEDIUM | HIGH
  prior_application_key: string | null
```

**Observações:** `opaque_ref` indica referência privada, não URL pública. Os campos de execução/motor só podem ser preenchidos a partir de capabilities demonstradas; qualquer esquema depende de revisão em SPECS. `CONFIRMED` no nível de encontro não implica `CONFIRMED` para a ação individual.

## 5. Modelo causal de crédito e responsabilidade

1. Verificar `CONFIRMED` do encontro pela DEC-071/073, com `resolution_epoch` e receipts sem conflitos.
2. Extrair somente evidências disponíveis e indexá-las por `actor_character_id`, sem associação por nome, aparência ou posição de sprite.
3. Separar papéis: dano direto, suporte, cura, proteção, planejamento/negociação e participação coletiva, **sem pesos pré-definidos**; registrar `UNKNOWN` quando não observável.
4. Preservar `owner` vs. `controller` dos PCs delegados; ação no personagem controlado não concede autoria ficcional ao controlador nem extrapola consentimento.
5. Estimar responsabilidade coletiva apenas por evento/decisão de grupo explicitamente confirmados, sem equiparar presença em party a endosso de atos individuais, especialmente quando alguém esteve ausente.
6. Publicar um assessment versionado e auditável, não um ranking oculto. Disputas ficam pendentes; registrar revisões sem apagar versões passadas.
7. Permitir testemunhas com visão incompleta e relatos falsos *como relatos*, nunca como recibos de host.
8. Propagar percepções DEC-029/074 somente para receptores legitimamente alcançados e autorizados; reputação contextual DEC-030 não é reputação mecânica do BG2.
9. Submeter efeitos a regras de domínio, risco e idempotência; deduplicar por evento+alvo+tipo de atribuição+revisão da regra+branch.
10. Expor em futuras UIs apenas a parte permitida da cadeia causal e a justificativa para casos pendentes; parâmetros de disputas/revisão humana permanecem para SPECS.

## 6. Exemplos de casos-limite

### Caravana protegida por quatro PCs

O host poderá confirmar que a party venceu. Se também houver telemetria validada, contribuidores específicos podem ser listados; se não houver, registrar `COLLECTIVE CONFIRMED`, detalhes individuais `UNKNOWN`. O comerciante presencia só guerreiro e clériga: seu testemunho reconhece esses dois, mas não altera provas sobre ladrão e mago nem finge que o NPC os viu.

### PC ausente sob delegação

O personagem pertence a um jogador ausente; outro o controla nos limites DEC-045/046. Registrar a ação mecânica do **personagem** e, separadamente, o **controlador temporário**, quando observável. A autoria ficcional não muda de proprietário. Proteger consentimento e não imputar conduta contrária às permissões.

### Rumor calunioso

Um NPC afirma que a clériga saqueou a caravana. Essa alegação pode gerar desconfiança localizada como percepção social, condicionada à política de risco e proveniência. **Não** gera `ConfirmedEvent`, não altera autor factual nem inventário; futura prova corretiva atualiza crenças sem apagar o rumor histórico.

### Ação sob anonimato

Um PC realiza ato confirmado sem ser identificado por testemunhas. O ledger privado pode conhecer seu ator se o host suportar a evidência; os espectadores podem lembrar de uma figura desconhecida. A ligação entre identidade civil, alias e disfarce será decidida em DEC-076; **não há suporte de disfarce BG2:EE/EEex comprovado**.

### Evento stale, replays e contas de reputação

Replays, jobs duplicados, retomada de save antigo ou recepção de dois relatos não elevam mérito ou sanções novamente. `UNCERTAIN`, `STALE`, build ou branch divergente bloqueiam a aplicação e acionam reconciliação; reputação mecânica só por gateway/host.

## 7. Segurança, privacidade, fair-play e UX

- Personagens não devem ser penalizados ficcionalmente pela ausência do jogador; consentimento da DEC-041/045/046 governa delegações e ações danosas.
- Evitar computar *scores* individualizantes opacos que incentivem competição ou prejudiquem o cooperativo; reconhecer evidência de suporte e objetivos coletivos.
- Não criar telemetria intrusiva sem opt-in; preservar somente os dados de gameplay necessários à rastreabilidade, sob retenção e minimização.
- Segredos do histórico, identidades protegidas e testemunhos privados devem passar pelo filtro DEC-028 **antes** de qualquer modelo ou nó LAN.
- Limitar divulgação ao conhecimento do observador: auditoria privada do host não se torna consciência de NPCs.
- Custos computacionais previstos no scheduler DEC-056; avaliação pode ser postergada sem alterar resultado confirmado.

## 8. Falhas e reconciliação

| Situação | Resultado seguro |
|---|---|
| Host confirma vitória, não ações individuais | Crédito coletivo fundamentado; contribuição pessoal UNKNOWN. |
| Receipts conflitantes | `PENDING_EVIDENCE`; sem atribuição definitiva. |
| NPC homônimo | Identidade não provada; proibir vinculação automática. |
| Dois relatos de mesmo fato | Registrar relatos separados, deduplicar efeitos por causa. |
| PC ausente | Não imputar participação ou culpa por default. |
| Save/load/restore | Reconciliar branch, epochs, checkpoint, Knowledge Pack e ledger. |
| Worker LAN revogado | Invalidar proposta; não executar efeitos. |
| Reputação mecânica solicitada | Exigir capability/host receipt testados e gate de risco. |
| Personagem mascarado/desconhecido | Não desvendar identidade automaticamente; DEC-076 pendente. |

## 9. Sequência futura de POCs

1. Simular fixtures sem jogo: quatro participantes, um ausente, testemunhas divergentes, rumores falsos e delegação.
2. Provar ledger único e replays com checkpoint e branch, inclusive `UNCERTAIN` e reentrega.
3. Auditar no BG2:EE limpo quais eventos realmente podem ser observados por bridge/EEex **somente leitura**, sem supor hooks de ação.
4. Construir gateway para o mínimo necessário quando for tecnicamente autorizado e testado offline, por build.
5. Exercitar host+dois clientes e diferentes roles, save/load, reconnect e mods; registrar lacunas reais e medir custo.
6. Só então definir granularidade efetiva, UI, políticas de consentimento e impactos mecânicos para SPECS.

## 10. Matriz de testes candidatos — TODOS NÃO EXECUTADOS

Os testes abaixo são **propostas de validação**, não evidências de funcionamento em BG2:EE/EEex/multiplayer.

| ID | Caso esperado |
|---|---|
| T075-01 | Evento confirmado gera registro de participação sem conceder XP ou loot. |
| T075-02 | Evento PROPOSED não gera crédito factual. |
| T075-03 | Evento UNCERTAIN não gera crédito factual. |
| T075-04 | Conclusão de caravana por host com apenas resultado coletivo marca detalhes individuais UNKNOWN. |
| T075-05 | Ataque por PC registrado com receipt válido permite proposta de contribuição individual. |
| T075-06 | Cura sem evidência específica não é inferida pelo LLM. |
| T075-07 | Proteção da carga com prova específica pode compor contribuição não combativa. |
| T075-08 | Interrupção de reforços comprovada é considerada contribuição tática. |
| T075-09 | Negociação documentada é contribuição válida sem dano causado. |
| T075-10 | Planejamento atribuído sem evidência não vira mérito factual. |
| T075-11 | Contribuições não exigem soma zero nem exclusão de suporte. |
| T075-12 | PC ausente e não controlado não recebe participação por presença no grupo. |
| T075-13 | PC temporariamente controlado retém autoria ficcional; dono e controlador são identificados distintamente. |
| T075-14 | Ação além do escopo delegado é bloqueada por política de consentimento. |
| T075-15 | Ação individual hostil não impõe culpa factual automática a PC não envolvido. |
| T075-16 | Responsabilidade coletiva requer nexo e regra aprovada. |
| T075-17 | NPC testemunha apenas dois PCs não conhece os outros dois automaticamente. |
| T075-18 | Testemunha sem identidade verificada não fornece autoria definitiva. |
| T075-19 | Testemunho tardio pode atualizar crença sem alterar o evento confirmado. |
| T075-20 | Rumor falso atribui fama percebida sem mudar autor factual. |
| T075-21 | Dois testemunhos contraditórios mantêm proveniência separada. |
| T075-22 | Conflito de testemunhos marca DISPUTED e suspende autoria definitiva. |
| T075-23 | Tentativa de vincular alias a identidade real sem prova é negada. |
| T075-24 | Contexto secreto de PC não sai para NPC não autorizado. |
| T075-25 | Worker LAN com permissão insuficiente não recebe evidência privada. |
| T075-26 | Log de atribuição é redigido conforme ACL. |
| T075-27 | Reputação de facção distante não muda antes de notícia legítima. |
| T075-28 | Fama regional diferencia reconhecimento coletivo e individual. |
| T075-29 | Notícia recebida não implica automaticamente mudança mecânica de reputação. |
| T075-30 | Proposta de XP a partir de reputação narrativa é bloqueada sem gateway/host. |
| T075-31 | Alteração de inventário sem receipt é rejeitada. |
| T075-32 | Alteração de alignment por crédito não é automática. |
| T075-33 | Recompensa de grupo não é duplicada por quatro registros de participação. |
| T075-34 | Reentrega do mesmo evento não reaplica o efeito. |
| T075-35 | Dois relatos do mesmo fato não produzem duas recompensas. |
| T075-36 | Evento offscreen e local com mesmo incident_id não originam duas atribuições. |
| T075-37 | Evento de outra branch não altera a autoria da branch atual. |
| T075-38 | Restore anterior não herda créditos futuros. |
| T075-39 | Knowledge Pack revisado não reescreve autoria histórica. |
| T075-40 | Corpus anual permanece imutável perante participação de campanha. |
| T075-41 | Evento de 1374 não produz memória em 1369 sem mecanismo autorizado. |
| T075-42 | NPC homônimo não recebe autoria de NPC diferente. |
| T075-43 | Desligamento de nó LAN invalida avaliação pendente desse executor. |
| T075-44 | Receipt de host de outra build é rejeitado. |
| T075-45 | Cliente multiplayer não confirma autoria mecânica sozinho. |
| T075-46 | Revoked/STALE não promove participação ao ledger. |
| T075-47 | Divergência entre receipts marca PENDING_EVIDENCE. |
| T075-48 | Correção de atribuição cria histórico revisado sem apagar testemunho anterior. |
| T075-49 | Soma de efeitos LOW que equivaleria a HIGH exige novo gate. |
| T075-50 | Ação prejudicial a outro PC respeita DEC-041/042. |
| T075-51 | Fila de avaliação não bloqueia gameplay durante combate. |
| T075-52 | Backpressure preserva pendências sem imputar culpa ao expirar. |
| T075-53 | Ausência de telemetria por ação preserva resultado UNKNOWN sem preencher por IA. |
| T075-54 | POC host+dois clientes é gate antes de declarar suporte de atribuição mecânica. |

## 11. Riscos pendentes de SPECS

- Precisão do observador, granularidade de logs do motor, identificação/associação de PCs e controle delegado.
- Proteção de segredos pessoais, aliases, disputas e retificações com consentimento.
- Custos de avaliação, filas, deduplicação e recuperação após falha.
- Fórmulas de reconhecimento e reputação, impacto agregado e campos de UI sem feedback enganoso.
- Teste de compatibilidade por build/mods e POC multiplayer real. **Nenhuma capability foi demonstrada.**

## 12. Próxima decisão — DEC-076 em aberto

**Tratamento de identidades públicas, pseudônimos, anonimato e disfarces:** A) reputação sempre vinculada à identidade verdadeira; B) pseudônimo independente e definitivo; **C (recomendada)** dupla visão factual privada versus percepção pública, com revelação condicionada a evidência, ACL, cronologia e capacidade comprovada. Não pressupor mecânicas de disfarce na engine.

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

DEC-076/C agora separa autoria factual privada do nome usado na cena e do reconhecimento público; um alias não estabelece autoria pelo próprio texto. Reputações, suspeitas e revelações seguem evidências, ACL e consentimento.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação por evidências (Discovery v7.3; não implementada)

A investigação de personas DEC-076 usará ledger privado por campanha/ramo, com pistas e hipóteses revisáveis, origem/independência de fontes, contraprovas e estados inconclusivos. Suspeita ou fala LLM não confirma identidade e não permite divulgação; vínculo factual restrito exige evidências/DEC-066, e revelação exige ACL/consentimento/risk gate por audiência (DEC-019/028/041/045/046). Rumores e repercussões DEC-029/074/075 são separados de fato e punição. **Preservar `knowledge/periods/<ANO>-DR/` fisicamente por ano, sem evidências privadas no cânone.** ADR-0072/documento 77; 58 testes não executados, sem POC BG2:EE/EEex/multiplayer.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Caso jurídico DEC-078 requer autoria factual de cada PC/NPC, sem repartir culpa por estar no grupo e sem converter reputação percebida em prova de participação.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Mandado DEC-079 não transfere responsabilidade a todo grupo por um PC suspeito; atribuição causal individual e testemunhos permanecem distintos.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Revogar uma acusação DEC-080 não muda retroativamente atos do PC; autorias e testemunhos permanecem auditáveis e efeitos sociais posteriores devem ter causa/regra.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Determinar dano e reparação DEC-081 exige autorias e responsabilidades comprovadas DEC-075, não culpa automática de todo o grupo.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Atribuição de ação de agente, ordem de superior e responsabilidade institucional requer fontes diferentes; não projetar culpa coletivamente.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Credibilidade e sigilo da fonte não mudam a autoria factual do PC nem dão direito automático a recompensa/culpa; fontes de prova separadas.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Contribuições reais a escolta/proteção exigem evidência, não pontuação inventada; participar de plano não significa responsabilidade por ameaça de terceiros.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Uma pista atribuída a informante não prova autor de vazamento nem responsabilidade do PC; falta de telemetria de ação permanece UNKNOWN.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Autoria de uma operação de engano é distinta do autor fictício no documento. Não transferir culpa/merit factual de PC por falsa assinatura.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Atribuição de colaboração e quebra de promessa exige autoria comprovada; pseudônimo, filiação e suspeita não bastam para imputar mérito ou traição.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Crédito e responsabilidade do informante por informação entregue requer prova; não atribuir mérito por promessa, rumor ou nome compartilhado.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Informes de informantes sobre autoria não certificam mérito/responsabilidade de PC; exigir evento/observação corroborada e regras de consentimento.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Sumário distribuído pode citar méritos atribuídos, mas precisa distinguir autoria factual DEC-075, reconhecimento de observador e alegações DEC-089.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Mérito de planejamento versus participação efetiva em operação deve ser verificado por ator, sem crédito automático a ausentes.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Crédito/culpa por etapa confirmada de operação é mantido após aborto; PC ausente ou retirado não recebe autoria inventada.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Fairness do scheduler não concede mérito automaticamente. Reconhecimento depende das ações verificadas e dos seus autores, não da reserva ou ordem de fila.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Tempo de espera ou cancelamento lógico não atribui mérito/culpa a PCs ausentes; depender de prova real dos acontecimentos.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-096/C — Discovery v9.2

Regras históricas DEC-096/C não atribuem automaticamente causalidade/culpa por ocorrência distante a PCs. Autoria exige receipts DEC-075.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Impacto histórico composto DEC-097/C não atribui culpa/ação a jogador ausente; requer receipts de autoria.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Autoria de feito cooperativo difere de autoria de recurso/ownership do motor; não confundir creditação e licença.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Atribuição de mérito deve distinguir prova de autoria e observação de uma flag de quest.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** A quest milestone observed on the host is NOT NPC knowledge, player consent, authorship, rumor or dialogue entitlement. A curated, minimal safe milestone must pass ACL/spoiler checks and be delivered causally before appearing in dialogue or memory; no LLM inference from raw flags. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Marco DEC-102 não presume autoria dos PCs; recibos e evidências de contribuição continuam independentes. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** a conclusão técnica de uma quest não concede automaticamente conhecimento ou crença a NPCs/facções. `QuestMilestoneAdmission` pode gerar proposta de notícia/reputação somente por regras, proveniência, tempo, geografia, visibilidade e ACL; notícia requer fonte/canal/delivery, e seus destinatários podem conhecer apenas versões parciais. Não expor identidades secretas, fontes protegidas ou raw flags por prompts/logs/dossiês. Ações mecânicas derivadas dependem de recibos host, sem atribuição presumida de PC. Ver doc. 103. **POCs reais pendentes.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para atribuição de autoria depende de prova, não de rumor ou errata, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para atribuição de responsabilidade deve ter prova, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Autoria de pagamento e recebimento não pode ser atribuída por LLM. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Atribuição de entrega ou pagamento exige receipts e autoria comprovadas. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
