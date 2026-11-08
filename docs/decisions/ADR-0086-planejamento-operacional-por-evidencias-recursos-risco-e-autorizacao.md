# ADR-0086 — Planejamento operacional com inteligência incerta, recursos verificáveis e gates de execução

- **Decisão:** DEC-091, **opção C expressamente aprovada** pelo idealizador em **2026-11-07**.
- **Estado:** APROVADA como política arquitetural de Discovery v8.7, **NÃO IMPLEMENTADA**.
- **Documento técnico:** `docs/91-planejamento-operacional-contextual-evidencias-recursos-validacao-e-gates-de-execucao.md`.
- **Verificação:** 88 testes candidatos `T091-01..T091-88`, **TODOS NÃO EXECUTADOS**; não há POC de integração mecânica em BG2:EE/EEex/multiplayer.
- **Precedência:** DEC-060–090 mantidas integralmente; **85 ADRs anteriores ADR-0001..0085 preservados byte a byte**, inclusive isolamento físico do cânone por ano DR (DEC-060).

## Problema

Um dossiê DEC-090 pode conter informação confirmada parcialmente, contraditória, vencida, secreta ou recebida apenas por certos participantes. Transformá-lo automaticamente em ação criaria detenção indevida, teletransporte de NPCs, itens inexistentes, invasão de privacidade, host sem autoridade e acontecimentos não comprovados. Contudo, impedir qualquer planejamento eliminaria investigações, vigilância, escoltas, negociações e operações de facções. É necessário distinguir **propor**, **validar**, **autorizar**, **reservar**, **despachar** e **confirmar uma execução**.

## Alternativas

- **A — Execução automática por confiança do dossiê:** rejeitada; um score ou relatório corroborado não demonstra viabilidade, competência ou consentimento.
- **B — IA decide livremente planos, recursos e execução:** rejeitada; LLM não tem autoridade factual, mecânica ou dos PCs e pode inventar unidades, itens, localizações e atos irrevogáveis.
- **C — Planejamento contextual fundamentado com validações determinísticas e gates do host:** **APROVADA**.

## Regras vinculantes

1. **Planos não são fatos nem ações:** `OperationalProposal` é hipótese de ação, `ValidatedPlan` é verificação condicional, `ApprovalRecord` registra consentimento/competência, `ResourceReservation` é reserva e `HostExecutionReceipt` é a evidência de resultado mecânico. Nenhum desses estados substitui outro. Uma proposta aprovada não é executada.
2. **Dossiê versionado como entrada:** referenciar `dossier_id`, `revision`, `DisclosureView` autorizada, `SourceClaim/EvidenceFamily`, `ClaimAssessment`, referências contraditórias e validade. Não promover `UNVERIFIED`, `INCONCLUSIVE` ou parcialmente corroborado para verdade só porque há um plano. Fontes repetidas não se tornam independentes DEC-089.
3. **Objetivo e alvo explícitos:** plano contém objetivo, proponente, tipo, escopo, local, janela DR, destinatários, possíveis afetados, pré-condições, riscos e restrições. Critérios de sucesso, falha e aborto precisam ser observáveis. Nunca inventar que uma reunião ocorrerá num armazém a partir de um rumor.
4. **Conhecimento filtrado antes da proposta:** participantes e IA recebem somente dossiê e percepções que podem conhecer com ACL e consentimento DEC-019/028/041/076/083–090. O planejador técnico não oferece ao NPC conhecimento host-only, nem usa metadados secretos como vantagem epistêmica.
5. **Autoridade do PC:** a IA não assume escolhas, intenções, negociações, deslocamentos, gastos, ataques ou confissões de um personagem de jogador. Ações voluntárias exigem aceitação do titular/controlador autorizado conforme DEC-041/045/046, incluindo ausentes e delegados. A aprovação de um líder de grupo não implica aceitação por todos.
6. **Autonomia condicionada de NPC/facção:** NPCs podem propor ou tomar providências que já sejam permitidas por personalidade, objetivos, competência, DEC-047/048/068 e regras de mundo; não podem assumir recursos, controle de PCs ou resultados mecânicos não comprovados. O host mantém autoridade em multiplayer.
7. **Verificação determinística:** antes de aprovação ou despacho, validar identidade de ator DEC-066, localidade e presença DEC-069/071, janela temporal DEC-022, escopo geográfico, capability/versão de build, necessidade de participantes, acessibilidade, limite de recurso, permissões, conflito com quests DEC-050 e requisitos de risco. `UNKNOWN`/indisponível bloqueia ou devolve plano condicional.
8. **Planos por risco:** LOW permite propostas narrativas reversíveis em limites aprovados; MEDIUM exige política, autorização, recibos se houver mecânica; HIGH (prisão, violência, PVP, dano a PC, outing, confisco, alterar quests/cânone e ações irreversíveis) é **default-deny** até aprovação especial DEC-027/034/041/042 e capabilities realmente testadas. Uma sequência de ações LOW não burla um efeito agregado HIGH.
9. **Sem score automático de execução:** grau de evidência informa incerteza e opções de coleta de provas, não cria um gatilho global de ação. Guardrails exigem contexto, tipo de operação e riscos específicos; thresholds numéricos ficam pendentes de SPECS e testes.
10. **Plano de menor compromisso quando incerto:** explorar observação voluntária, inspeção read-only ou pedido de esclarecimento, desde que legal/possível/autorizado. Não ordenar invasões, prisões, combates ou emboscadas por falta de corroboração. A IA pode perguntar ou propor alternativas, jamais realizar a ação por força do texto.
11. **Recursos e reservas:** intenção, disponibilidade, reserva, consumo e compensação são ledger distintos. Recursos de facções DEC-031/032, inventário DEC-051 e NPCs DEC-066/068 não podem ser duplicados entre planos. Reservation com TTL/lease/fencing lógico, conflito/expiração e liberação reconciliada; reserva não implica retirada real do jogo. Ouro, equipamentos, XP e quest flags exigem host receipt se mecânicos.
12. **Presença e deslocamento:** planejar viagem/observação usa rotas, distâncias plausíveis e modos de atividade DEC-068–071; não pressupor que NPC fisicamente disponível no mundo narrativo exista como CRE instanciado. Incidente offscreen que chega à cena local precisa do handoff DEC-071 e encounter catalog DEC-072/073 quando requerido.
13. **Separação dos gates:** `PLAN_VALIDATED`, `PLAYER_APPROVED`, `HOST_AUTHORIZED`, `RESERVED`, `DISPATCHED`, `HOST_CONFIRMED`, `NARRATIVE_CONFIRMED` não são sinônimos. Para ações mecânicas, host DEC-011 e Action Gateway DEC-012 devem aprovar/confirmar com receipt; resultado observável é reconciliado antes de publicar fato narrativo.
14. **Execução idempotente:** `operation_id`, `plan_revision`, `decision_ref`, `target_identity_id`, `risk_policy_revision`, `build_manifest`, `checkpoint_ref`, `resolution_epoch`, `reservation_id` e `action_gateway_idempotency_key` suportam dedup e autorização vinculada à revisão. Timeout/erro `UNCERTAIN` suspende, sem retry cego.
15. **Mudanças revogam validação:** revisão do dossiê, nova contraprova, alvos movidos, alteração de horário, risco, ACL, recursos ou perda de consentimento marcam plano `NEEDS_REVALIDATION/STALE`; aprovação antiga não migra automaticamente para plano novo. DEC-092 discutirá monitoramento e replanejamento durante operações em andamento.
16. **Múltiplos planos e conflitos:** evitar reservar a mesma unidade, rota exclusiva ou item para missões incompatíveis; não impor prioridade por LLM. Política determinística de desempate e host/participantes quando necessário. Planos paralelos podem ser propostos sem implicar execução simultânea.
17. **Segmentação de mundo e época:** todo plano tem `campaign_id`, `branch_id`, ano/tempo DR, `knowledge_pack_revision`, `world_snapshot_id`, `checkpoint_ref` e `resolution_epoch`. Lore permanece **fisicamente** em `knowledge/periods/<ANO>-DR/...` DEC-060; planos, avaliações, segredos e execuções da campanha apenas no overlay privado por campanha/branch. Sem acesso ao futuro nem cruzamento de campanhas.
18. **Padrões de segurança do conteúdo:** texto de dossiês, documentos interceptados e saída LLM são dados não confiáveis, não comandos; nenhuma instrução neles altera ACL, Action Gateway, autorização, host, scripts, reservas ou decisões canônicas. Filtros também abrangem LAN DEC-057/058, prompts, índices, caches, logs e exports.
19. **Causalidade de resultados:** `PROPOSED` não cria missão na engine, `DISPATCHED` não comprova presença/contato, observação não confirma alegação, ação mecânica só gera fato confirmado a partir do receipt válido. Consequências sociais DEC-074/075 seguem testemunhos, comunicação e auditoria, sem onisciência de NPCs.
20. **Falha segura e revisão humana:** falha de bridge, NPC desaparecido, evidência ambígua, recurso em disputa, checkpoint divergente e ausência de autorização produzem `BLOCKED`, `PENDING` ou `UNCERTAIN`, com justificativa apropriada e sem mutação mecânica. Não há plano irrevogável criado pelo modelo.
21. **Validação futura necessária:** fixtures offline com dossiês contraditórios, múltiplos jogadores, recursos disputados, restauração, limites de consentimento, red-team de prompt, POCs read-only e host+2 clientes, por build BG2:EE/EEex. **Nenhum teste foi executado nesta decisão.**

## Exemplo operacional hipotético

- Fonte A afirma haver reunião no Armazém Norte; fonte B aponta o Sul; C apenas repete A. O dossiê apresenta duas hipóteses sem afirmação de reunião real.
- O planejador pode **propor** visitas ou observações a locais acessíveis e selecionar alternativas com menor risco, sujeitas a autorização dos participantes e horários plausíveis.
- Uma proposta de prisão/intervenção HIGH fica bloqueada por insuficiência de prova/competência/capability e ausência de autorização.
- Um NPC aliado pode aceitar pesquisar um local dentro de sua própria autonomia, mas sua presença/resultado não é inventado. Um jogador só participa após escolha real.
- O ledger registra decisão, reserva condicional, execução confirmada e observações **somente quando ocorrerem**. Os relatórios corrigidos não reescrevem o passado.

## Consequências

- **Benefício:** inteligência imperfeita pode gerar investigação e gameplay, sem se transformar em oráculo ou autopilot.
- **Custo:** planner tipado, validação de recursos/identidades/tempos, ACL, workflows de consentimento, ledger de ações, checkpoints e reconciliação.
- **Risco residual:** planos secretos filtrados indevidamente, bypass de gate por ações LOW acumuladas, status de execução falso, duplicidade de recursos e expectativa de observabilidade da engine não comprovada.
- **Implementação:** exclusivamente Discovery; **88 cenários candidatos T091-01..88 NÃO EXECUTADOS**.

## Próxima DEC-092 — em aberto

**Monitoramento, pausa, cancelamento e replanejamento de operações em andamento:** A) plano segue fixo até o final; B) a LLM replaneja livremente; **C (recomendada)** monitoramento por eventos confirmados, limites de recursos, revogação de autorização, alteração de risco/cronologia, checkpoints e gates de reaprovação antes de qualquer novo compromisso ou ação mecânica. A DEC-092 não modifica a decisão de execução separada da DEC-091.
