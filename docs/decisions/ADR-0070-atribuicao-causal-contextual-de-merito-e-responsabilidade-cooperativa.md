# ADR-0070 — Atribuição causal contextual de mérito, reconhecimento e responsabilidade cooperativa

- **Decisão:** DEC-075, **opção C**, aprovada expressamente em 2026-11-06.
- **Estado:** **APROVADA apenas como arquitetura — NÃO IMPLEMENTADA**; Discovery v7.1.
- **Documento técnico:** `docs/75-atribuicao-de-autoria-merito-responsabilidade-e-reconhecimento-cooperativo.md` — 54 testes candidatos `T075-*`, todos **NÃO EXECUTADOS**.
- **Preservação integral:** DEC-060 a DEC-074 e ADR-0055 a ADR-0069, além dos ADRs mais antigos, permanecem byte a byte idênticos ao pacote v7.0.

## Contexto e problema

DEC-074 autoriza repercussões graduais de encontros confirmados, mas não decide **a quem** atribuir participação, autoria, ajuda indireta, responsabilidade, reconhecimento e reputação. Em coop, o combate pode envolver personagens que atacam, curam, protegem, negociam, distraem, oferecem planejamento ou atuam fora do campo visual da testemunha. O host pode confirmar parte do estado sem expor uma causalidade fina e completa. Testemunhos podem ser honestamente incompletos, tendenciosos ou falsos. Um evento coletivo não justifica fama automática igual para todos, e uma ação individual observada não prova que o resto da equipe não ajudou.

## Alternativas

- **A — Crédito coletivo uniforme:** rejeitada como regra universal por ignorar contribuição, ausência, consentimento e responsabilidades distintas; reconhecimento coletivo continua possível quando houver evidência de atuação conjunta.
- **B — Crédito somente a autores identificados diretamente:** rejeitada como regra universal por ignorar apoio, coordenação e autoria não observável; a falta de evidência não prova não participação.
- **C — Atribuição causal contextual, coletiva e individual, distinta da percepção pública:** **APROVADA**.

## Regras vinculantes

1. **Distinguir explicitamente as camadas:** `(a) ConfirmedEvent` — fato confirmado; `(b) ContributionEvidence` — ações e participações com suas provas; `(c) AttributionAssessment` — inferência restrita, nível de certeza e categoria de contribuição; `(d) WitnessAccount` — quem percebeu ou afirma algo; `(e) PublicRecognition` — reconhecimento/opinião por comunidade; `(f) AuthorizedDomainEffect` — efeito narrativo ou mecânico autorizado. Não igualar essas entidades.
2. **Não inferir telemetria inexistente.** O host BG2:EE é fonte de evidência mecânica apenas quando há bridge/capability testada. Sem logs por personagem ou causalidade verificável, a participação fina fica `UNKNOWN`, não é adivinhada por LLM. Um vencedor coletivo confirmado não gera automaticamente estatística individual de dano, cura, ação furtiva ou contribuição.
3. **Identidades e controle.** A contribuição aponta para `actor_character_id` estável e `actor_identity_status` verificado (DEC-066); registrar separadamente `player_owner_id` e `controlling_player_id` quando pertinente à delegação DEC-045/046. O controlador temporário não se torna proprietário do personagem nem recebe a autoria ficcional do PC sem evidência.
4. **Mérito não é competição de soma zero.** Reconhecer apoio, cura, proteção, negociação, preparação, tomada de risco, intervenção indireta e liderança quando evidenciados; não exigir que uma contribuição diminua o reconhecimento de outras. Não inventar placares ou pesos de mérito nesta etapa.
5. **Responsabilidade individual e coletiva são relacionais.** Uma decisão confirmada do grupo pode originar responsabilidade de grupo dentro da política consentida; atos individuais não transferem culpa indiscriminadamente a PCs ausentes, não envolvidos ou sem consentimento. Propagação de culpa social incorreta pode existir como **crença/rumor**, nunca como fato mecânico.
6. **Jogadores ausentes e PCs delegados.** Respeitar titularidade, escopo de consentimento, categoria de ação e limites de DEC-041/042/045/046. Não atribuir por padrão a personagem ausente contribuição ou infração que o host não confirmou. Impactos contra PCs exigem gates próprios.
7. **Testemunho não corrige verdade.** Cada `WitnessAccount` vincula testemunha identificada, campo de visão/conhecimento demonstrável quando disponível, fonte, hora, lugar, incerteza e ACL. Um mercador que viu apenas dois integrantes pode atribuir o feito a eles, enquanto o evento e a prova de participação preservam os quatro onde confirmado.
8. **Rumores e falsas atribuições permitidos como crenças.** Relatos podem omitir, exagerar ou atribuir feitos à pessoa errada, sempre com proveniência e sem forjar `ConfirmedEvent`. Correção futura exige novas evidências e evento de retificação, sem apagar a alegação original (DEC-061/064/074).
9. **Não onisciência.** Reconhecimento social depende de canal, distância, tempo, relacionamento, confidencialidade e confiança nos relatos (DEC-028/029/030/074), não de leitura indiscriminada do ledger factual por NPCs.
10. **Segredos, pseudônimos e identidades não expostas.** A atribuição factual privada não autoriza divulgar o verdadeiro ator a terceiros. Identidade pública não verificada fica `UNKNOWN/UNATTRIBUTED`; regras detalhadas para alias, disfarces e revelações são **DEC-076 ainda em aberto**, sem presumir mecânicas de disfarce no motor.
11. **Efeitos separados por domínio.** Fama, confiança, temor, hostilidade, favor, dívida, responsabilidade social, relação pessoal, efeitos de facção e oportunidades de missões exigem políticas específicas. `AttributionAssessment` sozinho **não** altera XP, recompensas, inventário, alinhamento, reputação mecânica, romances ou quests.
12. **Gates de risco e magnitude acumulada.** LOW apenas efeitos narrativos allowlisted e com prova; MEDIUM exige regras e autorização aplicável; HIGH e efeitos contra outros PCs exigem gates especiais, consentimento pertinente, capacidade validada e host receipt quando mecânico (DEC-027/034/041/042).
13. **Atribuição contestada.** Quando provas conflitam, manter avaliações concorrentes com estado `DISPUTED` ou `PENDING_EVIDENCE`, sem declarar autor definitivamente. Um relato tardio pode modificar percepções, mas nunca reescrever silenciosamente o ledger confirmado.
14. **Deduplicação por evento, personagem, tipo e regra.** Repetição de recebimento do mesmo evento, múltiplos relatos ou replays não podem repetir crédito material ou sanção. Uma chave conceitual inclui `(campaign_id, branch_id, source_event_id, actor_character_id_or_group_id, attribution_kind, rule_revision)` e revisão da resolução.
15. **Regra de resolução única.** O `incident_id`, `encounter_id`, `resolution_epoch` e recibos da DEC-071/073/074 amarram a atribuição ao acontecimento já confirmado; não criar crédito por proposta offscreen/local concorrente nem somar resultados duplicados.
16. **Temporalidade, branch e builds.** Toda afirmação e aplicação depende de relógio e branch corretos, Knowledge Pack fixado, checkpoint, fingerprint da build e identidade estável, com bloqueio de `STALE`, `REVOKED`, `UNCERTAIN` e incompatibilidades. Não importar o mérito de eventos futuros após restore.
17. **Privacidade dos PCs.** Provas de participação privada, segredos de histórico e decisão pessoal possuem ACL por ator, destinatário, finalidade e período; logs, prompts e nós LAN recebem somente contexto minimizado. Atribuição factual para auditoria não é visibilidade pública.
18. **Autonomia narrativa com correção.** NPCs podem agradecer apenas a quem viram e depois revisar suas crenças; reputação percebida não sobrescreve as memórias históricas nem recompõe automaticamente a reputação social a partir do cânone revisado.
19. **Efeitos mecânicos sob host.** Nenhum modelo ou cliente remoto confirma XP, reputação do motor, itens, dano ou quest. Action Gateway tipado DEC-012 e recibo válido do host DEC-011 continuam obrigatórios com POC por build e multiplayer.
20. **Cânone anual isolado.** DEC-060 permanece vinculante: lore canônico em diretórios físicos `knowledge/periods/<ANO>-DR/`; fontes com proveniência DEC-061; ingestão DEC-062; Knowledge Packs por campanha DEC-063. Autoria, testemunhos, crédito e percepções ficam **exclusivamente no overlay privado da campanha/ramo**.
21. **Auditoria e contestação legível.** Cadeia: evento → evidência → avaliação de contribuição → testemunho/percepção → regra → efeito/receipt ou bloqueio, com motivo para ausência de crédito e versão. Sem pontuação de contribuição opaca definida por LLM.
22. **Execução proporcional.** Avaliações assíncronas não bloqueiam o combate; prioridade ao gameplay/host/consistência (DEC-056), filas duráveis, backpressure e retomada segura, sem revelar segredos em background.
23. **Implementação progressiva.** Começar por fixtures sintéticas, logs fictícios, teste de ausência/controle delegado, testemunhas divergentes, deduplicação, replay; depois POC com BG2:EE limpo + bridge/EEex, host e dois clientes. Ausência de evidência fina ou capability implica `UNKNOWN`, nunca falsa medição.

## Exemplo hipotético (não ocorrência observada no jogo)

Quatro PCs protegem uma caravana. O host confirma o desfecho; evidências adicionais poderiam corroborar dano do guerreiro, cura da clériga, proteção de carga do ladino e interrupção de reforços pelo mago **se** a integração um dia capturar essas ações. Um comerciante vê apenas os dois primeiros, e por isso sua gratidão inicial pode favorecer ambos. A participação factual dos outros não é eliminada, mas sua reputação pública pode não mudar sem relato legítimo. Nenhum XP/loot adicional é concedido por este registro narrativo.

## Consequências e limites

- **Benefícios:** reconhecimento de papéis cooperativos, consequências distintas por observador e integridade entre mérito factual e fama; confiança/auditoria para controvérsias.
- **Custos:** evidências por ação, identidades estáveis, ACL, deduplicação por regra e evento, avaliação de responsabilidade e canais de relato.
- **Incerteza explícita:** não conhecemos a granularidade de eventos disponíveis no BG2:EE/EEex multiplayer; medir em POCs antes de prometer atribuição individual detalhada.
- **Lacunas:** fórmulas, pesos, UI, contestação pelo jogador e efeitos econômicos/mecânicos vão para SPECS e testes. **54 testes candidatos não executados**.

## Próxima discussão — DEC-076, ainda em aberto

**Identidades públicas, pseudônimos e ações sob anonimato/disfarce.** A) atribuir sempre publicamente à identidade verdadeira; B) separar definitivamente pseudônimos sem possibilidade de correlação; **C recomendada:** identidade factual privada persistente versus identidade percebida pública, com ligação/revelação somente por evidência, ACL, tempo, autorização e capacidades do motor verificadas. Esta escolha **não está aprovada** pela DEC-075.
