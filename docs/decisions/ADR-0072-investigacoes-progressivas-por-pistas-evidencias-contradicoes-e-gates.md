# ADR-0072 — Investigação progressiva de identidades secretas por evidências, contradições e gates

- **DEC:** DEC-077.
- **Opção aprovada:** **C — Investigações progressivas, com provas, contradições, revisão e autorizações.**
- **Status:** **APROVADA COMO DECISÃO ARQUITETURAL DE DISCOVERY**, ainda **NÃO IMPLEMENTADA**.
- **Data:** 2026-11-06; **Discovery:** v7.3.
- **Dependências:** DEC-019, DEC-028/029/030, DEC-041/042/045/046, DEC-060–076, DEC-011/012/027/034/053/056/057–060.
- **Documento técnico:** `docs/77-investigacoes-de-identidade-pistas-proveniencia-contradicoes-e-revelacao-segura.md` (**58 testes candidatos T077-01..58, NÃO EXECUTADOS**).
- **Preservação:** decisões **DEC-060–076** preservadas; **ADRs anteriores ADR-0001..ADR-0071 não foram editados**, inclusive o adendo DEC-060 de separação física do lore por ano DR.

## Contexto e problema

A DEC-076 permite múltiplas personas sociais por identidade factual privada, e distingue suspeita (`SUSPECTED`), vínculo verificado de modo restrito (`VERIFIED_PRIVATE`) e divulgação autorizada (`DISCLOSED_TO_SCOPE`). Uma investigação pode reunir documentos, depoimentos, observações, rumores, álibis e evidências contraditórias. Uma pista isolada, sem procedência ou contradita, não deve transformar suspeita em fato nem revelar o histórico de um PC a outros jogadores, NPCs ou workers LAN. Uma LLM pode ajudar a propor hipóteses ou perguntas, mas não assumir autoridade epistemológica, jurídica ou mecânica. A investigação pode ser narrativa sem requerer interações ou mecânicas inexistentes do BG2:EE.

## Alternativas

- **A — Primeira pista relevante revela a identidade:** rejeitada; induz falsos positivos, meta-conhecimento e exposição prematura.
- **B — LLM arbitra livremente:** rejeitada; conclusões não verificáveis, alucinação de provas e falha de ACL.
- **C — Investigação progressiva, evidências auditáveis e divulgação autorizada:** **APROVADA**.

## Regras vinculantes

1. **Três planos independentes:** fato conhecido pelo registro restrito de identidade, hipótese investigativa dos participantes, crença do observador e ato de divulgação têm dados e autoridades diferentes. Investigação em `SUSPECTED` ou `STRONGLY_SUSPECTED` não equivale a `VERIFIED_PRIVATE`; vínculo privado verificado não implica publicidade.
2. **Escopos:** toda investigação, pista e parecer vinculados a `campaign_id`, `branch_id`, `investigation_id`, `investigator_id|group_scope`, `subject_persona_id`, `target_actor_candidate_id?`, `knowledge_pack_revision`, `checkpoint_ref`, `resolution_epoch`, intervalo/instante DR e ACL. Sem travessia implícita entre campanhas ou branches.
3. **Ledger de provas imutável por eventos:** registrar origem, tipo, cadeia de obtenção, episódio causador, tempo, lugar, observador, acesso permitido, integridade, validade, confiança qualitativa e status de contestação. Corrigir por nova versão/evento, não sobrescrever ou apagar retrospectivamente.
4. **Tipos de alegação:** `Clue` (pista), `WitnessStatement` (testemunho), `DocumentClaim`, `DirectObservation`, `RumorClaim`, `CounterEvidence` (contraprova), `AlibiClaim` e `InvestigativeHypothesis`; todos podem ser falsos ou incompletos. Origem certificada não implica conteúdo verdadeiro.
5. **Corroboração independente real:** duas cópias do mesmo rumor não constituem duas fontes independentes; rastrear ancestralidade da informação e contaminação entre testemunhas. Uma mesma origem não é multiplicada para elevar artificialmente a confiança.
6. **Contradições e desconfirmadores:** contraprovas, álibis e falsificação documentada podem reabrir `DISPUTED`, reduzir grau de suspeita ou retirar conclusão antes sustentada. O sistema deve preservar o histórico de quem acreditou no quê e quando.
7. **Estados candidatos de investigação:** `OPEN`, `COLLECTING`, `SUSPECTED`, `CORROBORATING`, `CONTRADICTED`, `DISPUTED`, `INCONCLUSIVE`, `PRIVATELY_VERIFIED`, `CLOSED_NO_LINK`, `CLOSED`, `STALE`, `UNCERTAIN`. Os nomes finais e limiares são assuntos de SPECS; não criar percentuais de certeza arbitrários.
8. **Critérios de resolução:** revisar procedência, independência, compatibilidade temporal e geográfica, identidade verificada DEC-066, hipóteses alternativas, evidências contrárias e política de risco. Quando insuficientes, conclusão `INCONCLUSIVE`/`DISPUTED`, nunca certeza inventada. A LLM não promove vínculo factual por si só.
9. **Conhecimento situado:** um investigador ou NPC acessa somente as pistas que recebeu legitimamente. O orquestrador pode utilizar o vínculo factual restrito para controle e verificação sem expô-lo em diálogo, UI, prompt, cache ou consulta indevida.
10. **Privacidade de PCs:** ligação de pseudônimos, backstories e segredos pessoais preserva consentimento e visibilidade DEC-019/041/045/046. Uma descoberta ficcional não é autorização universal de divulgação ao grupo; titularidade do PC e controle temporário são distintos.
11. **Separar descoberta e divulgação:** inferência privada, apresentação a um investigador, acusação a uma facção e anúncio público exigem avaliações de audiência, finalidade, risco e autorizadores diferentes. Revelação sensível/HIGH usa gate explícito; na dúvida, **fail-closed**.
12. **Investigações legítimas não garantem sucesso:** pistas insuficientes podem manter mistério, gerar falsa suspeita explicitamente marcada, ou resultar em inocência suspeitada/exoneração; não produzir missão resolvida artificialmente para satisfazer uma cena.
13. **Sem telemetria mecânica inventada:** observações visuais, disfarces, detecção de mentira, furtividade, perícia, interrogatório, checks de atributos e coleta de pistas no motor exigem capability por build comprovada. Até lá, investigação pode ser apenas narrativa/regras offline; nenhuma ação engine sem gateway DEC-012 e receipt do host DEC-011.
14. **Efeito social, reputacional e legal desacoplado:** conclusão não impõe prisão, execução, multa, crime confirmado, PVP, alinhamento, XP, inventário, alteração de facção ou reputação mecânica. Tais efeitos exigem regras e decisões próprias; rumores/atribuição social seguem DEC-074/075 e risk gates DEC-027/034.
15. **Investigações fabricadas intencionalmente:** personagens podem mentir, forjar ou espalhar boatos como alegações ficcionais. Não gerar falsificações como provas factuais no ledger; preservar autores/causas quando confirmados. Limites de consentimento, privacidade e PVP permanecem.
16. **Idempotência e concorrência:** `case_revision`, `evidence_id`, `source_chain_id`, `decision_id`, `audience_scope` e `resolution_epoch` previnem reaplicação de resolução/descoberta; reconciliação de workers LAN, save/load e incidentes antigos rejeita `STALE/UNCERTAIN`.
17. **Proteção contra vazamento por inferência:** considerar que citações, mensagens de erro, avisos, contagens, prompts, índices, logs e resultados de busca também podem revelar ligação secreta. Filtrar antes do LLM e de qualquer cache/worker, usar minimização e auditoria com acesso controlado.
18. **Partição histórica e causalidade:** `knowledge/periods/<ANO>-DR/` contém apenas cânone curado por ano (DEC-060/061/062). Investigações, pistas, suspeitas, backstories, decisões e descobertas ficam exclusivamente no overlay privado `campaign/branch`, vinculadas ao Knowledge Pack pinado DEC-063; nunca duplicar corpus de todos os anos em uma só base.
19. **Orçamento computacional:** investigação não demanda LLM por NPC/tick. Aplicar regras, consulta seletiva, jobs em lote, quotas e prioridade DEC-056/059. Reavaliar somente diante de nova evidência, contestação, evento autorizado ou atualização explícita.
20. **Processo de implementação:** fixtures sintéticas, testes de falso positivo, contraditório, ACL e não vazamento, save/restore, idempotência e LAN antes de POCs específicas da bridge; SPECS e gates de lançamento continuam pendentes. **58 cenários candidatos T077-* NÃO EXECUTADOS**.

## Exemplo hipotético, não canônico

Uma carta traz a assinatura **Corvo Cinzento**, uma testemunha relata uma figura parecida com uma PC e outra fornece álibi. A carta não comprova autoria; a descrição física não comprova identidade; o álibi não é automaticamente verdadeiro. A investigação conserva as três alegações, relaciona suas fontes, verifica dependência entre relatos e pode registrar `DISPUTED/INCONCLUSIVE`. Uma eventual ligação verdadeira, validada de modo restrito, ainda dependerá de outra autorização para ser revelada ao guarda ou aos demais jogadores.

## Consequências e trade-offs

- **Benefícios:** mistérios causais, suspeitas revisáveis, contraditório, proteção de segredos e prevenção de decisões arbitrárias da IA.
- **Custos:** ledger de evidências, grafo de proveniência, filtros por audiência, controles de consentimento, revisões e replay determinístico.
- **Riscos:** testemunha contaminada, boato circular, falsa denúncia, vazamento via prompt, retcon após restore, falsa certeza, dependência de hooks de engine inexistentes.
- **Evidência existente:** aprovação de design; sem implementação e sem POC BG2:EE/EEex multiplayer. Os **58 testes são candidatos e não executados**.

## Próxima DEC-078 — proposta, ainda aberta

**Tratamento de acusações, decisões de autoridades locais e consequências jurídicas/faccionais:** A) sanções automáticas a partir da suspeita; B) efeitos apenas narrativos, sem procedimentos estruturados; **C (recomendada): procedimentos contextuais por jurisdição/facção, com evidência, direito de contestação, gradação de risco e autorização explícita para efeitos graves/mecânicos**. Não presume sistema legal uniforme em Forgotten Realms, nem prisão ou justiça programáveis no BG2:EE sem POC.
