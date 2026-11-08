# ADR-0077 — Responsabilização institucional contextual por evidências, competência e limites de risco

- **Decisão:** DEC-082 — **opção C**, aprovada expressamente em **2026-11-07**.
- **Estado:** **APROVADA COMO ARQUITETURA DE DISCOVERY v7.8; NÃO IMPLEMENTADA**.
- **Documento técnico:** `docs/82-investigacao-institucional-abuso-de-poder-responsabilidades-e-gates-de-reforma.md`, com **68 testes candidatos T082-01..T082-68, NÃO EXECUTADOS**.
- **Preservação vinculante:** DEC-060 a DEC-081 e seus ADRs anteriores **preservados integralmente e byte a byte** com relação ao ZIP v7.7; DEC-006/007/013/015/017/018 permanecem com seus estados anteriores.

## Contexto e problema

A DEC-081/C permite reparar uma injustiça comprovada, sem determinar automaticamente quem responde por ela. Em Forgotten Realms, um guarda pode exceder suas competências, um superior pode ter instruído ou tolerado a conduta, e uma guilda pode ter pressionado autoridades, mas nenhuma destas hipóteses equivale a culpa factual ou compromisso institucional comprovado. Cada organização tem estrutura, normas, jurisdição e época próprias, sustentadas por fontes canônicas curadas e pelo estado da campanha. Precisamos de uma investigação institucional com cadeia de comando, atribuição causal, contraditório contextual e limites de consequências, sem impor direito moderno uniforme nem permitir golpes, demissões ou sanções decididos livremente por IA.

## Alternativas e escolha

- **A — Limitar-se à reparação da vítima:** rejeitada como política geral; impede fiscalização e conflitos político-faccionais legítimos mesmo quando há provas contextualizadas.
- **B — Sanção ou reforma institucional automáticas após injustiça:** rejeitada; confunde erro, dolo, omissão e culpa coletiva, desconsidera competência e pode provocar mudanças canônicas irreversíveis.
- **C — Investigação contextual com responsabilidades individualizadas/institucionais, evidências, contestação e gates de risco:** **APROVADA**.

## Regras vinculantes

1. **Reparação ≠ responsabilidade.** `RemedyCase` DEC-081, `InstitutionalInvestigation`, `ActorResponsibilityAssessment`, `CommandResponsibilityAssessment`, `InstitutionalPracticeAssessment` e `InstitutionalMeasureProposal` são conceitos distintos. Revogação, retratação ou indenização não comprovam automaticamente má-fé, corrupção, ordem ilegal, omissão ou participação de chefia.
2. **Denúncia ≠ prova ≠ veredito.** Registrar `Allegation`, `EvidenceRecord`, `VerifiedIncident`, `ResponsibilityFinding` e `AuthorityDecision` em trilhas diferentes; hipóteses permanecem `ALLEGED/PENDING_EVIDENCE/DISPUTED` até validação sob política. A decisão de uma autoridade ficcional pode ser errada/corrupta, mas não altera os fatos confirmados.
3. **Âmbito e tempo.** Cada caso vincula `campaign_id`, `branch_id`, `institution_id`, `jurisdiction_id`, `world_time_dr`, autoridade investigadora, `knowledge_pack_revision`, checkpoint/epoch e evidências. Não exportar denúncia, culpa ou mudança de política para outros ramos e campanhas automaticamente.
4. **Competência e procedimento de época.** Confirmar legitimidade e limites de quem investiga, julga, supervisiona ou aplica medidas conforme região, organização e ano DR: `UNKNOWN` não é autorização. O sistema não presume tribunais, ouvidorias, corregedorias ou direitos processuais modernos onde fontes não os sustentem. Regras genéricas de segurança do Infinity AI continuam valendo independentemente da ficção.
5. **Quatro nexos de responsabilidade.** Distinguir (i) ação individual comprovada; (ii) ordem de superior com origem/alcance comprovados; (iii) omissão relevante sob dever/competência comprovados; (iv) padrão institucional demonstrado por múltiplos eventos independentes e procedimento. Uma conduta individual não incrimina automaticamente toda a instituição.
6. **Cadeia de comando auditável.** Relações cargo→autoridade→delegação→ação têm fontes, vigência, escopo e versões. Organograma, título ou proximidade não provam que o superior deu instrução, participou ou sabia. Delegação DEC-045/046 não confunde titularidade/controle de PCs com comando ficcional.
7. **Provas independentes e contraditórias.** DEC-061/077: fonte, observação, autenticidade, origem de cópia, ligação com evento/ator, possibilidade de fraude, duplicação circular e álibis são preservados. Múltiplos relatos derivados da mesma denúncia não são corroboradores independentes.
8. **Direito narrativo de resposta contextual.** Quando compatível com a estrutura institucional e com a agência dos jogadores, partes podem apresentar evidência, testemunho, contestação ou recurso; não fabricar mecanismo jurídico histórico ausente. A inexistência de recurso na ficção não suspende gates de segurança e consentimento do produto.
9. **Corruptibilidade sem onisciência.** Um superior, sacerdote, magistrado ou oficial pode mentir, recusar investigação, favorecer aliados ou decidir injustamente quando o modelo de mundo e evidências o permitirem; sua decisão é fato institucional/narrativo, **não** prova automática do mérito factual. Não usar LLM como árbitro de verdade, condenação ou depuração institucional.
10. **Pessoas e instituições separadas.** Registros de reputação de agente, hierarquia, cargo, guilda ou governo são distintos. Atribuição de culpa individual não modifica globalmente a reputação da instituição; efeitos dependem de canal, alcance, relevância e regra DEC-029/030/074/075.
11. **Medidas propostas, não automáticas.** Tipos candidatos: `OPEN_REVIEW`, `REQUEST_EVIDENCE`, `FORMAL_NOTICE`, `CONTEXTUAL_HEARING`, `OFFICIAL_CORRECTION`, `DISCIPLINARY_REVIEW`, `REMOVAL_PROPOSAL`, `LEADERSHIP_REVIEW`, `POLICY_CHANGE_PROPOSAL`, `NO_ACTION`. Autoridade para cada medida deve ser comprovada; exonerar, punir, reformar ou prender exige gates específicos.
12. **Mudanças políticas e históricas protegidas.** Alteração de comando, governo, aliança, guerra, jurisdição, morte ou acontecimentos canônicos irreversíveis sujeita-se à DEC-034, limitações DEC-031–033, agência DEC-041/042 e risco HIGH, bloqueado por padrão. Não aplicar medidas fora das capacidades ou além da decisão explicitamente autorizada.
13. **Host como fonte mecânica.** Alterar facção de NPC, área, agressividade, inventário, XP, quest, diálogo, scripts, prisão ou morte depende de gateway DEC-012, capacidade demonstrada na build DEC-051/052 e recibo do host DEC-011. Nenhuma bridge/EEex/multiplayer foi comprovada para estes efeitos. Uma decisão narrativa não é execução da engine.
14. **Separação epistemológica.** `InstitutionalFinding`, `ObserverBelief`, `PublicRumor` e `CausalImpactProposal` não são equivalentes. Rumores sobre corrupção podem circular sem prova factual, mas não produzem punições mecânicas nem reputação global automaticamente.
15. **Privacidade, testemunhas e denunciantes.** Identidades secretas DEC-019/028/076/077, dados de PCs, fontes confidenciais e acusações sensíveis têm ACL por finalidade/destinatário. Divulgação pode causar retaliação ou dano HIGH; exigir autorização. Proteção detalhada de denunciantes e testemunhas será a **DEC-083 em aberto**.
16. **Coop e consentimento.** Um jogador controla escolhas/falas/intenções de seu PC; não atribuir confissão, culpa ou testemunho a PC ausente. DEC-041/042/045/046 definem titularidade, controle delegado e riscos; decisão institucional não suprime a agência do usuário.
17. **Registro por evento e idempotência.** Chaves conceituais `(campaign, branch, investigation, source_event, target_actor_or_institution, measure_kind, rule_revision)` e `resolution_epoch` impedem sanções/impactos repetidos por relatórios duplicados. `UNCERTAIN/STALE/REVOKED` bloqueia efeito, exige reconciliação e impede retry cego.
18. **Revisão, correção e recursos.** Conclusões podem ser reabertas após prova nova; revogações DEC-080 e reparações DEC-081 são processos separados, preservando decisões passadas, cronologia e efeitos confirmados. Revisar medida não equivale a reiniciar o mundo.
19. **Canon físico anual e overlays.** DEC-060 exige `knowledge/periods/<ano>-DR/` em diretórios físicos distintos; fontes/proveniência e curadoria DEC-061/062, Knowledge Pack pinado DEC-063. Investigação, acusações, gestão de autoridades e consequências criadas no jogo ficam no **overlay privado da campanha e ramo**, nunca nos diretórios históricos.
20. **Limites de trabalho.** Motor determinístico primeiro para lookup de competência, integridade, prazos, idempotência e gates; LLM local apenas sob demanda para falas, indícios narrativos e pareceres não vinculantes com ACL filtrada. DEC-056 governa filas, prioridade de gameplay e backpressure.
21. **Observabilidade e recuperação.** Logs redigidos, trilha de autoridade, hashes/revisões, checkpoints DEC-053/054, migração de build DEC-052, monitor DEC-055, não vazamento em LAN DEC-057/058/059 e restauração por ramo. Sem comprovação, conservar pendência em vez de sucesso falso.
22. **Implantação incremental.** Começar com fixtures sintéticas e validador offline de competência, causa e evidência; depois simular workflow de organização; por fim POCs read-only, ação benigna testada isoladamente e host+dois clientes. Não declarar sistemas de punição/reforma mecânica implementados.

## Exemplo hipotético (não ocorrido na engine)

Uma autoridade de Athkatla decide prender injustamente um aventureiro e um processo DEC-081 documenta dano confirmado. Surge alegação de que um oficial aceitou suborno de uma guilda. A investigação institucional reúne registros, ordens, depoimentos e fluxo de benefícios, distinguindo culpa do oficial, ordens comprovadas de chefia e participação real da guilda. Mesmo que o oficial confesse em narrativa autorizada, isso não prova corrupção do governo inteiro. Possíveis resultados: ausência de prova, apuração adicional, medida disciplinar válida ou disputa entre facções. Nenhuma exoneração, alteração de quest, prisão, confisco ou golpe é executado por texto.

## Trade-offs e evidências

- **Benefícios:** consequências políticas orgânicas, casos contestáveis, distinção entre agente/instituição, rastreabilidade e integridade temporal.
- **Custos:** modelar estrutura administrativa por facção/ano, cadeia de comando, competências, evidências, versões e impacto cumulativo.
- **Limitação:** sem fontes específicas suficientes, `PENDING_POLICY`/`PENDING_EVIDENCE` e ausência de sanções; nunca inventar direito local.
- **Testes:** **68 cenários T082-01..T082-68 CANDIDATOS NÃO EXECUTADOS**; nenhum modelo causal ou efeito BG2:EE/EEex/multiplayer testado.

## Próxima discussão — DEC-083 (EM ABERTO)

**Proteção contextual de denunciantes, testemunhas e fontes confidenciais:** A) identidade e testemunhos públicos por padrão; B) sigilo absoluto e imutável, inclusive contra destinatários legitimamente autorizados; **C recomendada)** proteção graduada com minimização, identidade/ACL por finalidade, avaliação de risco, provas rastreáveis sem exposição desnecessária e divulgação legítima controlada, sem imunidade ou invulnerabilidade mecânica fictícia. A DEC-082 **não aprova** antecipadamente essa escolha.
