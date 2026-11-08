# ADR-0083 — Recrutamento voluntário de informantes, negociação, acordos e controle de recursos

- **Decisão:** **DEC-088 — opção C**, expressamente escolhida pelo idealizador em **2026-11-07**.
- **Estado:** **APROVADA SOMENTE COMO ARQUITETURA DE DISCOVERY**; **NÃO IMPLEMENTADA**.
- **Pacote:** Infinity AI — Discovery **v8.4**.
- **Documento técnico:** `docs/88-recrutamento-de-informantes-ofertas-negociacao-termos-sigilo-e-encerramento.md`, com **82 testes candidatos T088-01..T088-82, todos NÃO EXECUTADOS**.
- **Preservação:** todas as decisões **DEC-060–087**, incluindo a integridade física do lore anual DEC-060, permanecem inalteradas; **82 ADRs anteriores (ADR-0001..ADR-0082) byte a byte idênticos à v8.3**.

## Contexto e problema

NPCs podem ter motivações e compromissos múltiplos (DEC-087), suspeitar ou conhecer acontecimentos por canais legítimos (DEC-064/074/077), manter segredos e receber proteção (DEC-076/083–085). Resta distinguir **contato, proposta, negociação, consentimento, acordo firmado, prestação concreta e encerramento** no recrutamento de informantes. Um funcionário de guilda insatisfeito pode não desejar colaborar, não ter informações relevantes, exigir garantias ou mentir sobre sua disponibilidade. Uma oferta financeira não compra automaticamente a lealdade de um NPC, e promessas da IA não criam moedas, itens, proteção, conhecimento ou contratos comprovados pela engine.

## Alternativas

- **A — Recrutamento automático por preço ou requisito:** rejeitada; transforma crenças, motivações e lealdades em compra compulsória, com risco de farming de segredos e recursos infinitos.
- **B — Negociação controlada livremente pela LLM:** rejeitada; permite inventar aceitação, compromissos, dados secretos, pagamentos e consentimento sem fatos ou receipts.
- **C — Negociação contextual e voluntária, termos auditáveis, recursos verificados, confidencialidade e possibilidade de recusa/saída:** **APROVADA**.

## Regras vinculantes

1. **Separar domínios:** `CandidateSource` (NPC identificável ou fonte ainda incerta), `ContactOpportunity`, `RecruitmentProposal`, `NegotiationTurn`, `NegotiationAssessment`, `ConsentEvidence`, `InformantAgreement`, `CommitmentTerm`, `ResourceReservation`, `DisclosureAuthorization`, `InformationPromise`, `DeliveryEvidence`, `AgreementRevision`, `TerminationEvent` e `ObserverBelief`. **Oferta ≠ aceitação ≠ acordo ≠ informação prometida ≠ informação obtida/confirmada.**
2. **Escopo persistente:** usar `campaign_id`, `branch_id`, `npc_identity_id` verificado DEC-066, `player_owner_id?`, `agreement_id`, facção/beneficiário, ACL, revisão do Knowledge Pack, ano DR, checkpoint e epoch. Homônimos/aliases DEC-076 não bastam para estabelecer identidade do contratado ou duplicar relações.
3. **Voluntariedade NPC:** NPC pode ignorar contato, recusar, negociar, propor condições, solicitar tempo, cooperar parcialmente, suspender ou encerrar. Regras determinísticas consideram valores/histórico DEC-047/048/064/065/087, disponibilidade, compromissos anteriores, contexto regional e conhecimento real. Insatisfação não é vontade presumida de espionagem; preço elevado não garante cooperação.
4. **Agência dos PCs:** não forçar nenhum PC, inclusive ausente/delegado, a virar informante, confessar, aceitar pagamento, fazer promessa ou revelar histórico. DEC-019/041/042/045/046 protegem a titularidade, permissão específica e impacto cruzado entre jogadores. Silêncio ou comando mecânico não equivalem a consentimento narrativo.
5. **Informante não equivale a companion:** acordo de informação não autoriza recrutamento para party, troca de facção, combate, tarefas táticas ou alteração de alinhamento. DEC-047–050/087 mantêm limites de NPC canônico, scripts, quests e autoagência; efeitos no motor exigem capability por build e receipt do host.
6. **Contexto e elegibilidade:** abordagem exige oportunidade verificável, contato/alcance causal DEC-068–071, canais legítimos DEC-029/069/074, riscos DEC-027, consentimento de envolvidos e recursos finitos. NPC DORMANT não negocia em tempo real nem se desloca instantaneamente. Sem prova da capacidade de contato, manter `PENDING/UNAVAILABLE`.
7. **Negociação modelada:** registrar turnos com interlocutores, `source_event_id`, solicitação/oferta, contraproposta, vigência, condições, obrigações, proibições, meios de comunicação e eventuais riscos. Fala gerada por LLM local é **candidata**; ato de aceitação precisa de regra, fonte e confirmação/autorização. Não forjar falas ou assinaturas de PC.
8. **Acordo explícito, mínimo e limitado:** contrato narrativo versionado define escopo do que pode ser solicitado/compartilhado, quem recebe, duração, pagamento/benefícios condicionados, sigilo, revogação, condições de término e referências a proteção, sem prometer sucesso ou informação inexistente. Termo fora de política ou de competência é rejeitado.
9. **Consentimento e compromissos separados:** colaboração sob ameaça/coação DEC-087/084 exige classificação distinta, gates superiores e regras de agência. Não rotular acordo coagido como voluntário, nem usar resgate de familiar, medo ou dívida como consentimento irrevogável. Jogos narrativos podem representar coercão histórica com segurança, não executá-la automaticamente.
10. **Promessa não é entrega:** `InformationPromise` informa intenção ou alegação do NPC; `DeliveryEvidence` registra mensagem ou documento realmente entregue. Nenhum item, mapa, documento, conhecimento canônico ou segredo de facção aparece automaticamente porque um NPC assinou acordo. Credibilidade, correção e contradições serão avaliadas sob DEC-061/064/077 e **DEC-089 em aberto**, sem antecipar veredito de inteligência.
11. **Limite de conhecimento:** o informante pode fornecer somente o que razoavelmente sabe, recebeu ou observou, sujeito a falhas de memória, rumores e ACL DEC-028/064/065/074/085/086. Conhecimento do host, lore privado de outro ano ou segredo de PC não é automaticamente conhecido nem revelável por recrutamento.
12. **Confidencialidade compartimentada:** identidade da fonte, termos do acordo, canais, entregas e beneficiários têm ACL por finalidade/audiência; pseudônimos de DEC-076/083 não expõem identidade factual. Relatórios filtrados são possíveis. Segredos não aparecem em prompts LLM, RAG, embeddings, logs, ferramentas LAN ou UI fora de escopo autorizado.
13. **Contatos adversários e agentes duplos:** recrutado pode manter outras lealdades DEC-087, mas essa possibilidade não confirma traição. Distinguir suspeita, alegação de compromisso, promessa e ação comprovada; detecção de enganos DEC-086/077 depende de evidência e não de inspeção onisciente.
14. **Economia real:** promessas de ouro, itens, favores, abrigo, serviço e tempo exigem disponibilidade e orçamento DEC-032/051/056. Usar reserva tipada com valores e beneficiário, limitação anti-farming, validação de saldo e, quando o motor estiver envolvido, host Action Gateway DEC-011/012. Nunca conceder item, XP, gold ou serviço pela mera palavra do modelo.
15. **Reservar não equivale a pagar:** transações propõem `resource_reservation_id`, `amount`, `currency_or_item_ref`, vínculo com milestone, expiry, idempotency; custos só são efetivados mediante receipt host quando mecânicos. Falha `UNCERTAIN` exige reconciliação sem retry cego. Eventuais promessas descumpridas são fatos narrativos contextualizados, não debitados inventados.
16. **Limites de remuneração:** caps por informante, período, ramo, tipo de entrega e total orçamentário; sem prometer taxas universais. Repetir o recrutamento, trocar pseudônimo ou recriar contato não gera bônus, ouro ou documentos duplicados.
17. **Segurança física distinta do contrato:** pedir abrigo, escolta ou realocação depende da DEC-084 e de recursos, trajetos e risk gates; não se cria proteção efetiva por assinar termos. Refúgios/itinerários DEC-085 permanecem secretos por audiência e campo.
18. **Autonomia de recusa e término:** informante poderá recusar nova tarefa, suspender, negociar extensão ou encerrar colaboração quando os termos e a política permitirem; o contratante poderá desistir. Fim não apaga encontros, entregas ou dívidas confirmados, nem causa esquecimento retroativo de NPCs. Proteção e divulgação de segredos após término obedecem cláusulas válidas e ACL, não desaparecem sem causa.
19. **Mudanças de lealdade não implícitas:** iniciar ou encerrar um contrato não rompe filiação original, nem altera reputação/faction flags/party sem provas/gates DEC-030/074/087. Traição e responsabilidade jurídica exigem DEC-077–082, não inferência pelo aceite.
20. **Cronologia e canon:** fatos editoriais continuam segregados fisicamente em `knowledge/periods/<ANO>-DR/` DEC-060 e versão DEC-061–063. Acordos, pagamentos e fontes da campanha ficam apenas no overlay privado por `campaign/branch`, alinhados ao DR, checkpoint e estado confirmado; sem importar segredos de ramo/futuro após restore.
21. **Idempotência e concorrência:** `proposal_id`, `agreement_id`, `revision`, `commitment_id`, `reservation_id`, `delivery_id`, `cause_event_id`, `checkpoint_epoch`, receipts, fencing e dedup impedem acordos duplicados, pagamentos repetidos e entrega fantasma após falhas/retry/host+2 clientes. No estado `UNCERTAIN`, nenhuma compensação ou mutação é repetida automaticamente.
22. **Níveis de risco e efeitos:** comunicação narrativamente inofensiva pode usar gate LOW; segredos de PC, chantagem, dano grave, espionagem de governo, prisão/captura, mudança institucional ou canon irreversível exigem MEDIUM/HIGH e autorizações DEC-019/027/034/041/042/078–085. LLM não é autoridade para aprovar risco ou gastar recursos.
23. **Desempenho e IA opcional:** elegibilidade, inventário, ACL, revisão, receitas e estados por código determinístico; LLM local DEC-014/059 somente para falas e propostas limitadas, sem agente autônomo permanente por informante ou tick de negociação. Scheduler DEC-056 impõe limites e prioridade do jogo.
24. **Observabilidade segura:** eventos mínimos auditáveis, atribuições/recusas justificadas e métricas de risco, mas logs, debugging, prompts e resumos não divulgam fontes ou acordos ocultos a operadores sem papel específico. Apagar dados sensíveis acessíveis por função sem adulterar auditoria obrigatória.
25. **Pé no chão da engine:** não afirmar diálogos persistentes, scripts de recrutamento, pagamento de gold, trocas de inventário, faction changes, party join/leave ou conversas NPC↔PC em runtime sem POCs de BG2:EE/EEex no build e host+dois clientes. Até lá, somente desenho documental e fixtures sintéticas.
26. **Escopo da próxima DEC:** confiabilidade de informes entregues, independência de relatos, desinformação involuntária e validação de conteúdo pertence à **DEC-089 — em aberto**; a DEC-088 define como oferecer, negociar, acordar, entregar e encerrar.

## Exemplo ilustrativo, não executado

Uma funcionária NPC de uma guilda mercantil em Athkatla recebe proposta de revelar **apenas** o horário de uma reunião, em troca de ajuda legítima. Ela pode recusar, pedir garantias ou aceitar um acordo com prazo e restrição de destinatários. O sistema não dá acesso automático ao horário: a funcionária deve saber o dado de forma plausível, autorizada ou por um fato narrativo confirmado, e a entrega deve ser registrada. Se a informação estiver incorreta, a negociação continua válida como fato ocorrido, mas a veracidade do relato fica pendente da avaliação de evidências. Nenhum objeto, ouro, missão ou reputação da engine muda sem receipt do host.

## Consequências e riscos

- **Benefícios:** informantes com agência, negociação significativa, escopo de segredos, custos reais, acordos reversíveis e continuidade cooperativa.
- **Custos:** controle de permissões e contratos, ledger de recursos, estados concorrentes e reconciliação, filtros de conhecimento e testes de segurança.
- **Riscos:** farming de informações/compensações, promessa não cumprível, exposição de PC, contratos implícitos, dupla contagem, inventário divergente, NPC canônico descaracterizado. Mitigação: validação determinística, limites, ACL e gates.
- **Evidência existente:** somente escolha arquitetural. **82 testes candidatos T088-* NÃO EXECUTADOS.** Sem POCs de recruitment/diálogo/pagamento BG2:EE/EEex multiplayer.

## Próxima decisão — DEC-089 (EM ABERTO)

**Avaliação de veracidade, credibilidade e corroboração dos informes recebidos:**
- **A:** informes de fonte recrutada são aceitos como fatos confiáveis.
- **B:** a LLM determina livremente a veracidade de cada informação.
- **C (recomendada):** evidências, proveniência, independência de fontes, contradições, conhecimento disponível, análise de risco e graus de confiança; informação entregue continua separada de fato confirmado, sem denúncia ou punição mecânica automática.
