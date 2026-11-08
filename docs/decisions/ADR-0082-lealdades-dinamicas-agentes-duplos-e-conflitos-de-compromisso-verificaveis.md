# ADR-0082 — Agentes duplos, lealdades dinâmicas e conflitos de compromisso causalmente verificáveis

- **Decisão:** **DEC-087 — opção C**, aprovada expressamente em **2026-11-07**.
- **Estado:** **APROVADA APENAS COMO ARQUITETURA DE DISCOVERY**, **NÃO IMPLEMENTADA**.
- **Versão:** Infinity AI Discovery **v8.3**.
- **Documento técnico:** `docs/87-agentes-duplos-lealdades-confianca-motivacoes-e-conflitos-causais.md`, com **80 testes candidatos T087-01..T087-80, todos NÃO EXECUTADOS**.
- **Preservação integral:** DEC-060 a DEC-086 e todos os **81 ADRs anteriores** (ADR-0001..ADR-0081) mantidos **byte a byte idênticos** ao pacote v8.2. Esta decisão não revoga qualquer regra existente.

## Contexto

NPCs persistentes, companheiros e integrantes de guildas podem desenvolver deveres simultâneos e conflitos de confiança. Um agente de uma guilda poderia colaborar secretamente com outra organização para proteger um familiar; um companheiro pode discordar dos objetivos do grupo sem cometer traição. DEC-047/048 já define autonomia narrativa e recusa de companheiros, DEC-064/065 define crenças e memória, DEC-066 identidade persistente, DEC-083–086 regula fontes, sigilo, proteção e desinformação. Falta definir como **relações de lealdade evoluem** sem serem reescritas pela LLM, sem espionagem onisciente e sem decisões impostas aos PCs.

## Alternativas

- **A — Lealdades fixas, sem agentes duplos emergentes:** rejeitada; permite apenas roteiros predefinidos e limita transformação pessoal e relações faccionais.
- **B — IA altera lealdades e determina traições livremente:** rejeitada; fabricaria motivações, compromissos, fatos e consequências, inclusive de PCs ou NPCs canônicos, sem provas.
- **C — Lealdades e compromissos contextuais, evoluindo por eventos, valores, recursos, evidência e autorização:** **APROVADA**.

## Decisão e invariantes vinculantes

1. **Domínios separados:** `NPCIdentity` e `NPCDisposition` (valores e perfil validado), `LoyaltyBond` (vínculo com facção/pessoa/grupo), `Commitment` (promessa ou obrigação com origem), `ConflictAssessment` (conflito de objetivos), `DualAllegianceProposal`, `LoyaltyTransition`, `WitnessObservation`, `ObserverBelief`, `DisclosureEvent`, `OutcomeReceipt`. **Lealdade factual privada ≠ filiação declarada ≠ suspeita externa ≠ evidência de colaboração ≠ traição comprovada.**
2. **Identidade persistente:** estado sempre vinculado a `campaign_id`, `branch_id`, `npc_identity_id`/identidade de ator verificada DEC-066, facções identificadas, revisão, ano DR, Knowledge Pack pinado, ACL e checkpoint. Igualdade de nome, visual, alias ou função não transfere lealdade a outro personagem.
3. **Lealdades não exclusivas:** um NPC pode ter compromissos distintos com indivíduos, famílias, deidades, guildas e party; manter qualidades (confiança, dever, proteção, medo, dívida, hostilidade) **com proveniência**, sem reduzir tudo a um escalar universal ou à reputação nativa da engine. Filiação formal não comprova apoio a toda ordem da organização.
4. **Personalidade e cânone:** valores, histórico, lealdades originais, contradições e limites de NPCs canônicos vêm de fontes curadas relevantes ao período DEC-060–063. **Não sobrescrever fatos canônicos, quests, romances, alinhamento nativo ou limites do personagem** por conveniência dramática. Mudanças irreversíveis que afetem canon exigem DEC-034/050 e autorização específica.
5. **Eventos necessários:** mudança substantiva de vínculo requer evidência de acontecimentos do mundo ou decisão pessoal validada do NPC conforme regras de autonomia DEC-047/048. Promessa inventada por LLM ou silêncio de NPC não cria compromisso. Registros `UNKNOWN`, `ALLEGED`, `DISPUTED` são mantidos sem promoção automática.
6. **Agência de PC inviolável:** somente jogador titular pode escolher seus compromissos, falas, conspirações, revelações, traições ou deserções; delegação DEC-045/046 precisa de permissão específica. Nenhum sistema pode fabricar escolha de PC nem impor conflito moral, aliança secreta ou PvP; aplicar DEC-019/041/042.
7. **NPC autônomo, porém limitado:** NPC poderá avaliar oferecer ajuda, questionar, recusar, guardar segredo, renegociar, colaborar parcialmente, reconsiderar ou planejar ruptura quando motivação, oportunidade e política permitirem. A LLM **não** decide livremente a transição nem executa decisões mecânicas; código e regras verificam precondições, custo, risco e limites.
8. **Sem traição obrigatória:** suspeita, dívida, medo ou oferta de dinheiro não forçam mudança de lealdade. Possível `CONFLICTED` ou `NEGOTIATING` pode persistir; o NPC pode negar proposta, pedir provas, buscar terceira via ou retomar lealdade anterior. Não existe obrigação de concluir um arco com traição.
9. **Coerção e manipulação:** chantagem/ameaça/engano são **eventos e riscos**, não autorizações ilimitadas para controlar outro NPC; diferenciar colaboração voluntária, coação, relato falso e infiltração simulada. Dano grave, intimidação de PC ou coerção que implique captura/morte tem gate MEDIUM/HIGH e proteção DEC-027/042/083/084.
10. **Conhecimento compartimentado:** guilda A pode acreditar que o NPC é fiel; guilda B pode suspeitar; identidade de fonte e contatos ocultos continuam no overlay privado com ACL. Auditor host conhece vínculos quando necessário, mas não os transmite automaticamente a NPCs/LLMs/clientes. DEC-028/064/076/077/083–086 aplicáveis.
11. **Dupla colaboração não equivale a traição:** manter `allegiance_type`, `authorization_scope`, vigência e conflitos específicos. Uma colaboração autorizada entre facções pode ser diplomacia; espionagem só se configurar pelas ações verificadas. Não converter todo contato com rival em culpa.
12. **Recrutamento e contrato separados:** esta DEC permite condições e intenção de dupla lealdade; **não** estabelece sistema completo para contratar/recrutar informantes, compensação ou negociação. Esses detalhes ficam na DEC-088 em aberto.
13. **Causalidade e propagação:** vazamento, descoberta e boato sobre agente duplo obedecem canais, testemunhas, alcance, itinerários e tempo DEC-022/029/069/074/077/085; não existir conhecimento global ou revelação retroativa. Comunicações plantadas DEC-086 continuam alegações, não recibos ou provas reais.
14. **Reputação e responsabilização:** mérito, crédito e atos atribuídos ao NPC seguem DEC-075; suspeitas e consequências faccionais DEC-030/074/078–082 devem ter prova/autoridade. Um agente duplo comprovado não torna toda guilda cúmplice. Nenhuma sanção automática apenas por suspeita.
15. **Economia e recursos:** favors, pagamentos, itens, tempo, disponibilidade de rede e oportunidades não podem ser criados livremente. Considerar DEC-032/056/068/069; se houver consequências mecânicas de inventário/moeda, requer host receipt DEC-011/012/051 e limite antiexploração.
16. **Compatibilidade com party:** controle tático de companion no BG2:EE não confere ao NPC poderes de sabotagem do jogador nem garante veto mecânico, mudança de facção, saída de party ou triggers de diálogo. Caso engine não suporte, reações permanecem narrativas ou uso nativo já demonstrado; sem declarar capability não testada.
17. **Gates de transição:** `STABLE`, `TENSION`, `CONFLICTED`, `NEGOTIATING`, `DUAL_COMMITMENT_PROPOSED`, `DUAL_COMMITMENT_VERIFIED`, `REFUSAL_PENDING`, `RUPTURE_PROPOSED`, `RECONCILIATION_PENDING`, `DISPUTED`, `UNCERTAIN` são **candidatos**, não estados de engine; transições só por regras, provas, riscos e autoridade. Situações simultâneas podem requerer eixos distintos em SPECS.
18. **Manter memória, sem retcon:** alianças anteriores e promessas confirmadas são event logs imutáveis; término de contrato ou mudança de lado produz nova revisão, sem apagar diálogos, descobertas ou consequências anteriores. NPCs externos conservam crenças próprias até novas informações.
19. **Determinismo e LLM opcional:** avaliador de elegibilidade usa regras/configurações primeiro; LLM local DEC-059 pode sugerir fala, negociação ou opções, com contexto autorizado, sem alterar fatos/filiação diretamente. Propostas opacas sem fonte ficam em `PENDING/REJECTED`.
20. **Idempotência e falhas:** `transition_id`, `cause_event_id`, `npc_identity_id`, `bond_revision`, `rules_revision`, `checkpoint_epoch` e `host_receipt_id?` evitam duplicar mudança de lado, bônus, boato ou ruptura após retry/load. `UNCERTAIN` não autoriza retry cego nem mobilização/teleporte do NPC.
21. **Tempo e presença:** NPC DORMANT pode reavaliar apenas acontecimentos comprovados no intervalo e por canais alcançáveis; sem ticks de LLM, sem conhecer eventos futuros, sem comparecer fisicamente sem observação host ou capacidade de movimentação testada DEC-068/069/071.
22. **Limites de implementação:** não prometer lealdade mecânica de NPC, atualização de party, scripts, mudança de faction flags, hostilização, IA controlando companions ou espionagem em runtime em BG2:EE/EEex sem POCs por build e host+dois clientes. Os 80 cenários técnicos são candidatos e **NÃO EXECUTADOS**.
23. **Proteger o corpus canônico:** lore físico em `knowledge/periods/<ANO>-DR/` DEC-060–063 não recebe traições, confiança ou agentes duplos dinâmicos de uma campanha. Vínculos/confiança permanecem no overlay privado por campanha/branch.

## Exemplo hipotético

Uma agente NPC de uma guilda mercantil deseja ajudar uma rival porque esta acolheu seu irmão. O sistema confirma o vínculo familiar conforme fatos estabelecidos, as fontes disponíveis, recursos de comunicação e valores da NPC. A personagem pode negociar ajuda limitada, recusar ou reconsiderar; **não** passa a ser traidora automaticamente. A guilda original não conhece essa tensão sem observação ou informação transmitida. Uma mensagem falsa plantada por outro NPC (DEC-086) não é prova de que houve dupla colaboração. Uma decisão crítica de mudança de facção ou efeito no motor permanece pendente de gates e capacidade testada.

## Benefícios, custos, riscos e limites

- **Benefícios:** NPCs e facções com lealdades plausíveis, conflitos pessoais, amizades, promessas e espionagem sem traidores arbitrários.
- **Custos:** perfil/compromissos versionados, provas, difusão de conhecimento, matriz de riscos/ACL, migração de saves, observabilidade e testes de variantes canônicas.
- **Riscos:** falsos motivos inferidos, personagens canônicos descaracterizados, traições impostas a PCs, contatos tomados por crimes, falhas de confidencialidade e bugs de party/faction flags; mitigar por contratos, consentimento e gateway.
- **Estado de evidência:** somente desenho aprovado. **80 testes candidatos T087-01..80 não executados; nenhuma capacidade BG2:EE/EEex/multiplayer validada nesta decisão.**

## Próxima DEC-088 — em aberto

**Recrutamento e gestão de informantes e colaboradores voluntários:** A) recrutamento instantâneo por oferta/preço; B) IA negocia livremente sem contratos e custos validados; **C (recomendada)** negociação contextual verificável, consentimento, motivação, recursos, prazo, confidencialidade e saída/recusa, sem obrigar PCs ou fabricar lealdade. Avaliar na próxima entrevista.
