# ADR-0069 — Propagação causal, gradual e contextual de consequências confirmadas no Living World

- **Decisão:** DEC-074, **opção C**, aprovada expressamente em 2026-11-06.
- **Estado:** **APROVADA como arquitetura no Discovery v7.0; NÃO IMPLEMENTADA**.
- **Documento técnico:** `docs/74-propagacao-causal-de-consequencias-rumores-reputacao-faccoes-e-economia.md` — **52 testes candidatos T074-01..52, NÃO EXECUTADOS**.
- **Preservação obrigatória:** DEC-060–073, ADR-0055–0068, **literalmente inalterados** em relação ao ZIP validado v6.9; demais decisões anteriores igualmente preservadas.

## Contexto

A DEC-073 fixa um conjunto reconciliado de consequências pós-encontro; DEC-071 impede resolver duas vezes o incidente; DEC-029 já define difusão contextual de rumores e DEC-030, reputação local. Falta o contrato de **saída do encontro para os sistemas do Living World**, diferenciando a verdade mecânica, o conhecimento distribuído e impactos de domínio (relações, reputação, organizações, economia, guerras e missões). Sem isso, salvar uma caravana poderia atualizar instantaneamente facções distantes ou gerar múltiplas recompensas por reprocessamento, enquanto notícias falsas não seriam distinguíveis de eventos confirmados.

## Alternativas avaliadas

- **A — Consequências apenas locais:** rejeitada; impediria repercussões causais legítimas ao longo das relações e regiões.
- **B — Propagação global instantânea:** rejeitada; cria NPCs oniscientes, ignora distância, tempo, canais e confiança e eleva o risco de efeitos artificiais.
- **C — Propagação causal, gradual e contextual com evidência, autorização e idempotência:** **APROVADA**.

## Regras vinculantes

1. **Gatilho ancorado em fato confirmado.** Uma repercussão factual nasce de evento `CONFIRMED` no ledger da campanha, com `campaign_id`, `branch_id`, `incident_id`, `encounter_id`, `resolution_epoch`, `event_id`, checkpoint/revisão e fonte/receipt pertinente. `PROPOSED`, `RUMORED`, `PENDING`, `STALE` e `UNCERTAIN` não se tornam verdade factual por narração.
2. **Verdade ≠ notícia ≠ crença ≠ efeito.** Separar `ConfirmedWorldEvent`, `Observation/Report`, `BeliefUpdate` e `DomainEffect`. Um boato falso pode existir como crença atribuída a uma fonte, sem afirmar ocorrência do fato e sem aplicar sua mecânica.
3. **Propagar informação por canais legítimos.** Testemunho, conversa, mensageiro, registro de guilda ou rota mercantil precisam de emissor, receptor, meio, local, tempo, ACL, proveniência e disponibilidade do canal. Eventos sem testemunha não concedem reconhecimento social universal.
4. **Cronologia e geografia efetivas.** DEC-022 rege FROZEN/PARTIAL/REALTIME; notícia não antecede o acontecimento nem percorre distâncias instantaneamente salvo canal explicitamente fundamentado e curado. O atraso/custo depende de SPECS; não inventar tempos oficiais de viagem ou alcance de comunicação.
5. **Conhecimento individual e revisável.** DEC-028/029/064/065 preservam diferenças entre conhecimento e crença: NPCs podem aceitar, desconfiar, deturpar ou negar um relato. Não sobrescrever memórias com a base canônica, nem criar onisciência por leitura do ledger.
6. **Reputação proporcional e localizada.** DEC-030 permite fama/confiança/temor/respeito/hostilidade por entidade, facção e região, **não** atualiza implicitamente o valor mecânico de reputação do BG2:EE. Atribuição de mérito, autoria e testemunho exigem evidências próprias, a detalhar em DEC-075.
7. **Camadas de efeitos separadas.** Difusão de informação, relações pessoais, reputação social, disposição de facções, oportunidades de missão, economia/rotas e política/militar têm validadores, limites de magnitude, causalidade e gatilhos próprios. Receber notícia não prova ganho econômico, compromisso ou mudança de governo.
8. **Autonomia de facções não equivale a onisciência.** DEC-031/032/033: organizações só podem responder com base em notícias acessíveis e recursos/objetivos verificados; resultados estratégicos de alto impacto obedecem aos gates existentes.
9. **Tipos de impacto LOW/MEDIUM/HIGH e efeito acumulado.** LOW somente sob allowlist de regra segura e permissões; MEDIUM requer validação e autorizações aplicáveis; HIGH, irreversível, canônico, mecânico ou afetando PCs requer autorização especial e/ou host conforme DEC-027/034/041. Muitas alterações LOW não podem contornar um limite HIGH.
10. **Uma aplicação por causa, alvo e regra.** Introduzir `CausalImpactLedger` com chave conceitual `(campaign, branch, source_event, target_entity, effect_kind, rule_revision)` e idempotência. Eventos reentregues, múltiplos rumores sobre o mesmo fato ou jobs repetidos não duplicam efeitos materiais.
11. **Não confundir múltiplos relatos com múltiplos fatos.** Relatórios de vários NPCs podem ser registrados separadamente para avaliar credibilidade, mas não criar um segundo incidente nem um segundo loot/XP/quest, mudança de reputação ou impacto econômico.
12. **Consistência de revisões e concorrência.** Toda proposta contém versão de campanha, Knowledge Pack fixado, relógio e branch. Reentregas defasadas, worker LAN revogado ou concorrência host/cliente não aplicam mudanças; `UNCERTAIN` implica suspensão e reconciliação.
13. **Host controla efeitos mecânicos.** LLM e simulação distantes apenas propõem; manipulação de reputação BG2:EE, flags, XP, itens, inventário, quests e estado de engine exigem Action Gateway e recibo do host com capability validada. Propostas narrativas não se transformam em efeitos mecânicos.
14. **Auditoria e possibilidade de contestar/retificar.** Manter cadeia causal: evento confirmado → testemunha/relato → crença → decisão de regra → recibo de efeito ou rejeição. Retificação não apaga o histórico anterior; aplica evento corretivo curado, sem rollback cego nem apagar memórias legítimas.
15. **Privacidade e segredo.** Respeitar ACL por segredo, jogador, NPC, facção, tempo e finalidade. Operadores LAN, logs, prompts e telemetria não recebem automaticamente segredos por conduzir propagação.
16. **Separação física por ano DR.** DEC-060 é vinculante: cânone em `knowledge/periods/<ANO>-DR/`, e nunca em repositório único de lore misturado. DEC-061/062 preservam fontes e staging; DEC-063 mantém Knowledge Packs por campanha. Notícias, eventos e impactos decorrentes do jogo ficam exclusivamente em overlays de campanha/ramo, não alteram arquivos canônicos.
17. **Limites do scheduler e catch-up.** DEC-056 aplica quotas, prioridade, backpressure, armazenamento de pendências e entrega durável, com avanço temporal limitado DEC-022; tarefas distantes podem esperar, não gerar propagação retroativa ilimitada ou salto causal.
18. **Integridade em coop.** DEC-011/041/045/046: autoria/consentimento e segredos por PC importam; só o host consolida estado mecânico. Clientes não podem enviar notícia falsificada como receipt de encontro.
19. **Proteção do ciclo do encontro.** A reserva única DEC-071 e fechamento DEC-073 precedem efeitos de repercussão. Cleanup de instância temporária não apaga cadeia de evidências; incidente `CLOSED` não faz os destinatários saberem automaticamente dele.
20. **Época e fonte de cenário.** O conteúdo empregado é compatível com a versão do Knowledge Pack da campanha e o ano da consulta. Uma notícia de 1374 DR não alcança NPC em 1369 DR salvo mecanismo temporal extraordinário explicitamente validado, nunca por recuperação genérica.
21. **Negar quando faltam dados.** Sem observador/canal/relação ou sem causa confirmada, registrar `PENDING_EVIDENCE`, `NO_PROPAGATION` ou `REJECTED`, em vez de inventar um mensageiro ou resultado socioeconômico.
22. **Lançamento progressivo.** Primeiro observar eventos fictícios e reproduzir propagação determinística em testes; depois integrações narrativas isoladas; só habilitar impacto de motor mediante capability/POC específica e host+dois clientes. Nenhum suporte EEex alegado.

## Exemplo canônico de operação (hipotético)

O host confirma que o grupo protegeu uma caravana. Um comerciante identificado e presente sabe do resultado; outro NPC ou guilda distante **não sabe** automaticamente. Um relatório autorizado poderá chegar à guilda mais tarde, caso o canal esteja fundamentado e ativo. A guilda poderá atualizar confiança local segundo regra de reputação, mas nenhum efeito econômico/mecânico, recompensa, alinhamento ou mudança política é presumido sem política distinta e evidência adicional. Se um rumor atribuir o feito a outra pessoa, preservar versões e identidade das fontes e não alterar autoria histórica.

## Consequências e custos

- **Benefício:** repercussões orgânicas de escolhas sem onisciência, com causalidade auditável e contenção de duplicidade.
- **Custo:** grafo social/rotas, fila de notícias, ledger de efeitos, versões, ACL, regras de domínio e testes de reconciliação.
- **Trade-off:** fatos podem demorar a circular, e efeitos não suportados ou sem evidência ficarão pendentes; integridade prevalece sobre a aparência de mundo instantaneamente responsivo.

## Evidência e testes

Apenas aprovação humana desta decisão. Documento 74 inclui **52 testes candidatos T074-01..T074-52 não executados**. Parâmetros de canais, confiança, métricas, fórmulas, persistência e gateways permanecem para SPECS/POCs. **DEC-006/007/013/015/017/018 permanecem em aberto**.

## Próxima discussão — DEC-075 (em aberto)

**Atribuição de crédito e responsabilidade em ações cooperativas.** A) conceder crédito idêntico a todo o grupo; B) atribuir crédito apenas ao ator observado no motor; **C (recomendada)** registrar autoria, participação, testemunhos e informação disponível por NPC/facção, distinguindo mérito real, atribuição pública e rumores, com proteções para personagens ausentes, consentimento e efeitos proporcionais. Complementa a DEC-030 e 074 sem substituí-las.
