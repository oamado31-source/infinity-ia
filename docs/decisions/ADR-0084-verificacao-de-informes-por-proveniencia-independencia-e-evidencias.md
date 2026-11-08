# ADR-0084 — Verificação de informes por proveniência, independência e evidências

- **Decisão:** DEC-089, **opção C**, aprovada expressamente pelo idealizador em **2026-11-07**.
- **Estado:** **APROVADA SOMENTE COMO ARQUITETURA DE DISCOVERY — NÃO IMPLEMENTADA**.
- **Discovery:** **v8.5**.
- **Documento técnico:** `docs/89-verificacao-de-informes-proveniencia-independencia-contradicoes-e-confiabilidade.md`, com **84 testes candidatos T089-01..T089-84, todos NÃO EXECUTADOS**.
- **Precedência/preservação:** decisões **DEC-060 a DEC-088 integralmente mantidas**; **83 ADRs anteriores ADR-0001..ADR-0083 byte a byte idênticos** à versão 8.4. As demais decisões anteriores também não são substituídas.

## Problema

DEC-088 permitiu que informantes entreguem relatos e documentos, mas separou `InformationPromise` de `DeliveryEvidence`, sem resolver se o conteúdo recebido é verdadeiro. Em uma campanha, duas pessoas podem reproduzir uma mesma fofoca como se fossem fontes independentes, fornecer lembranças erradas, elaborar uma informação deliberadamente falsa ou descrever fatos parcialmente verdadeiros. NPCs podem ter acesso restrito a lugares, pessoas e épocas. A resposta de uma LLM, por mais convincente que pareça, não é prova de que um evento existiu ou de que uma fonte o presenciou.

## Alternativas avaliadas

- **A — Confiança automática nos relatos de fontes recrutadas:** rejeitada; acordos de DEC-088 não certificam acesso epistêmico, independência ou veracidade.
- **B — Veredito livre da LLM:** rejeitada; conclusões inventadas, circularidade, metaconhecimento e riscos de coerção/quest sem prova.
- **C — Avaliação por proveniência, independência, corroboração, contradições, acesso e risco, com revisão contextual:** **APROVADA**.

## Regras vinculantes

1. **Separação epistêmica estrita:** `DeliveredReport` registra a entrega de um conteúdo, `SourceClaim` a alegação, `EvidenceRecord` o material ou observação que a sustenta, `OriginLineage` sua cadeia de origem, `EvidenceFamily` o conjunto de fontes dependentes, `ClaimAssessment` a avaliação contextual e `WorldFactReference` um fato já confirmado por autoridade/evidência legítima. **Entrega ≠ alegação ≠ corroboração ≠ verdade factual ≠ conhecimento de cada NPC.**
2. **Não transformar fala em mundo:** falas ou documentos fabricados de maneira *diegética* podem existir como alegações com autoria e proveniência, inclusive desinformação DEC-086. Não criam fatos confirmados, recursos, objetos, calendário, scripts, loot ou evidências mecânicas. A existência de um informante não prova o relato.
3. **Escopo obrigatório:** todas as entidades referenciam `campaign_id`, `branch_id`, `knowledge_pack_revision`, `checkpoint_ref`, `resolution_epoch`, período/instante DR e precisão, `observer_scope`, `privacy_acl`, `evidence_revision` e fonte de origem. Atores são identificados por ID lógico DEC-066, não nome de persona DEC-076.
4. **Acesso epistêmico:** antes da avaliação, verificar se a fonte poderia conhecer a informação: posição e itinerário DEC-068/069, testemunho direto ou canal plausível DEC-029/074, acesso documental, limites de memória DEC-064/065, sigilo e tempo. Se o acesso não puder ser demonstrado, manter `UNKNOWN/UNVERIFIED`, nunca completar a lacuna com lore host/LLM.
5. **Proveniência encadeada:** registrar observador original, transmissores, documentos/recibos, datas, região, contexto, versão e reinterpretações. Não inventar cadeia de custódia nem marcar como independentes relatos que descendem de uma única origem; ciclo `A→C→A` não gera nova prova.
6. **Independência explicitamente testada:** agrupamento determinístico por `origin_event_ref`, `underlying_document_id`, cadeias de relato e `shared_informant_ref`; duas fontes que repetem a mesma mensagem representam uma **família** de evidência, salvo prova verificável de observação autônoma. Uma identidade alternativa não multiplica corroboradores.
7. **Corroboração contextual:** evidência independente consistente pode sustentar parcial ou integralmente uma alegação, por recorte de pessoa/local/tempo. Diferentes partes do relato podem receber avaliações distintas. Frequência e confiança subjetiva de declarações não substituem provas.
8. **Contradição e ausência:** contradições devem conter elementos, versões e fontes de ambos os lados, com tempo e perspectiva. Ausência de confirmação não é evidência de falsidade; versões incompatíveis podem permanecer `DISPUTED/INCONCLUSIVE` até revisão.
9. **Estados epistemológicos candidatos:** `RECEIVED`, `UNVERIFIED`, `PARTIALLY_CORROBORATED`, `CORROBORATED_WITH_SCOPE`, `CONTRADICTED`, `INCONCLUSIVE`, `RETRACTED_BY_SOURCE` e `STALE` (por tempo/branch). Não usar estado `TRUE` como simples efeito de acumular depoimentos. Status de entrega, veracidade e crenças são campos diferentes.
10. **Perfil de confiabilidade não é credulidade automática:** histórico verificável de acertos, erros, retratações e limitações da fonte pode influenciar avaliações **por tema, época e contexto**, com revisão e limites; reputação social DEC-030 e lealdade DEC-087 não são probabilidade objetiva de veracidade. Uma fonte confiável pode estar errada; uma fonte antes enganosa pode fornecer evidência válida.
11. **Modelo local auxiliar, não árbitro:** regras determinísticas verificam IDs, escopo, linhagem, ACL, temporalidade, dependência, coerência e admissibilidade; LLM local opcional pode sugerir perguntas, relações e resumos **com citação dos registros acessíveis**, devolvendo propostas para validação. Não assina `ClaimAssessment`, cria origem ou aplica impacto mecânico.
12. **Provas canônicas versus informes da campanha:** lore permanece **fisicamente separado por ano DR** em `knowledge/periods/<ANO>-DR/` DEC-060, com fontes DEC-061, ingestão DEC-062 e Knowledge Packs DEC-063. Alegações/relatórios de campanha e correções ficam somente no overlay privado por campanha/ramo. Fato de lore que existe para o host não se torna automaticamente conhecido pelo informante/NPC.
13. **Revisões append-only:** correções, reinterpretações, retratações e refutações geram novas revisões ligadas às anteriores; não apagam relatos recebidos, crenças históricas ou eventos confirmados. Novas evidências podem mudar a avaliação sem retcon retroativo.
14. **Privacidade por campo e finalidade:** dados brutos de informantes, identidade protegida DEC-083, local de abrigo DEC-084/085, operação de engano DEC-086 e detalhes de acordo DEC-088 são compartimentados. Metadados de endereço, horário, referência documental e perfil podem identificar uma fonte indiretamente. RAG, logs, prompts, embeddings, modelos remotos e nós LAN obedecem a mesma filtragem DEC-028/057–059.
15. **Separar avaliação de disseminação:** `ClaimAssessment` não publica automaticamente relatórios; o leitor, NPC, facção ou jogador só descobre fatos pela experiência ou canais permitidos DEC-029/074. O escopo e a divulgação de **dossiês** permanecem decisão posterior **DEC-090**.
16. **Nunca converter suspeita em punição:** informe não confirmado pode motivar investigação ou cautela narrativa de baixo risco quando a política permitir, mas não confirma crime, agente duplo, mandado, prisão, confisco, alteração de facção, ruptura de NPC, ataque ou quest. DEC-027/034/077–082 exigem evidências, competência, gates e host para ações mecânicas.
17. **Cadeia de autoridade:** `SourceClaim` e `ClaimAssessment` são registros epistêmicos privados; fatos mecânicos exigem host authoritative receipt DEC-011/012; conclusões curatoriais sobre fontes canônicas DEC-061 requerem curadoria, não texto gerado. Divergências irreversíveis DEC-034 permanecem bloqueadas sem política específica.
18. **Conflitos em multiplayer:** jogadores com direitos diferentes podem receber relatórios com campos e fonte ocultos, mas sempre preservar que há incerteza. A versão filtrada não permite inferência indevida pelo tamanho, contagem, IDs sequenciais ou horário. Decisões de PCs exigem intenção do titular DEC-019/041/045/046, nunca inferida de ausência.
19. **Temporalidade e causalidade:** informação recebida no dia X não é conhecida no dia X−1, nem por NPC que não estava disponível. Validade temporal da informação (p.ex., 'reunião amanhã') deve distinguir horário previsto, horário de transmissão e data de observação. Restores DEC-053 não importam evidência ou avaliação de branches/futuros.
20. **Idempotência e reconciliação:** chaves como `report_id`, `claim_id`, `origin_lineage_hash`, `evidence_family_id`, `assessment_revision`, `cause_event_id`, `checkpoint_epoch`, `rule_revision` e `idempotency_key` impedem contagem dupla por reentrega, retransmissão, retrial ou reconnect. Eventos `UNCERTAIN` exigem reconciliação, não retry cego.
21. **Limites computacionais:** grafo de origem acíclico (ou ciclos detectados), limites de profundidade/total de provas por caso, consultas por escopo/tempo, snapshots e custos DEC-056. Sem polling contínuo ou LLM por tick de NPC. Falha de avaliação retorna `INCONCLUSIVE`, não 'verdade provável' inventada.
22. **Capacidades técnicas pendentes:** não há demonstração de captura de testemunhos, detecção de falsidade, diálogo, perícia, evidência do inventário, sincronização ou assinatura mecânica em BG2:EE/EEex. Primeiros testes são offline sintéticos; POC read-only, host e dois clientes antes de qualquer integração.
23. **Critérios revisáveis:** pesos, thresholds, rubricas de confiabilidade, independência de fontes e apresentação da incerteza serão detalhados futuramente em SPECS; nenhuma porcentagem universal de 'verdade' foi aprovada.
24. **Governança:** todo parecer contém explicação verificável do que foi confirmado, contestado, desconhecido e por quais fontes **autorizadas**; não expor segredos protegidos no próprio texto de auditoria distribuída.

## Exemplo sintético: reunião em armazém

Fonte A informa que a reunião ocorrerá no **Armazém Norte**. Fonte B descreve uma reunião no **Armazém Sul**. Fonte C repete literalmente o relato da fonte A e admite tê-lo ouvido dela. C integra a mesma família de origem de A e **não** conta como segunda corroboração independente. A divergência entre A e B continua explícita; a avaliação pode permanecer `INCONCLUSIVE`. Nenhuma reunião futura é automaticamente criada no mundo pela LLM; cabe investigar evidências reais em canais permitidos.

## Consequências

- **Benefícios:** inteligência falível, rastreável e contestável; ausência de onisciência; proteção de fontes; fair-play; coerência com investigação/espionagem.
- **Custos:** modelagem de linhagem, dependência de fontes, versões, proveniência, ACL granular e explicações de incerteza.
- **Riscos mitigados:** falsa corroboração, metaconhecimento, invenção de fatos e punições arbitrárias, vazamento da identidade de fontes, falsas certezas por reputação de informantes, resultados duplicados após reload.
- **Evidência de implementação:** **nenhuma**. **84 testes T089-01..84 candidatos, NÃO EXECUTADOS.** Sem POC BG2:EE/EEex/host+2 clientes.

## Próxima decisão aberta: DEC-090 — dossiês e compartilhamento seletivo de inteligência

- **A:** divulgar relatórios brutos e todas as fontes automaticamente aos aliados.
- **B:** deixar a LLM montar e compartilhar dossiês como desejar.
- **C (recomendada):** dossiês versionados com alegações, evidências autorizadas, proveniência, níveis de incerteza, redação/ACL por destinatário, revisão e difusão causal, sem promover análise a fato nem divulgar segredos automaticamente.
