# ADR-0087 — Monitoramento por eventos, pausa, cancelamento e replanejamento controlado

- **Decisão:** DEC-092, **opção C aprovada expressamente** em **2026-11-07**.
- **Estado:** APROVADA como decisão de arquitetura de Discovery **v8.8**; **NÃO IMPLEMENTADA**.
- **Documento técnico:** `docs/92-monitoramento-operacional-eventos-pausa-aborto-replanejamento-e-reconciliacao.md`.
- **Evidência de testes:** **90 cenários candidatos `T092-01..T092-90`, TODOS NÃO EXECUTADOS**. Não existem POCs comprovadas de pausa de motor, cancelamento de comandos, movimento, script ou sincronização BG2:EE/EEex host + 2 clientes.
- **Precedência:** DEC-060–091 preservadas integralmente. Os 86 ADRs anteriores ADR-0001..ADR-0086 permanecem **byte a byte idênticos** ao Discovery v8.7.

## Contexto e problema

DEC-091/C separou dossiê, proposta, validação, autorização, reserva, despacho pelo Action Gateway e confirmação do host. Um plano em andamento pode perder atualidade após uma mudança de evidência, uma revogação de consentimento, um NPC indisponível, a saída de um jogador ou a ruptura de um recurso reservado. Um modelo que altera livremente alvos, participantes e planos sem nova validação quebra a agência dos jogadores e a autoridade do host. O extremo oposto — continuar o plano apesar de condições invalidadas — pode gerar operações perigosas, recursos duplicados e decisões contrárias ao próprio mundo. É necessário monitoramento **orientado a eventos confirmados**, sem introduzir ticks de LLM, e com replanejamento audível e idempotente.

## Alternativas

- **A — Plano imutável até conclusão:** rejeitada; não lida com perda de recursos, consentimentos, evidências e riscos.
- **B — Replanejamento livre pela LLM:** rejeitada; transfere decisões de PCs/host ao modelo, cria ações sem autorização e pode repetir comandos após falha.
- **C — Monitoramento por eventos, avaliação determinística, pausas/cancelamentos seguros e nova autorização conforme impacto:** **APROVADA**.

## Decisão vinculante

1. **Fatos observados, não sugestões de LLM:** monitores recebem `ConfirmedWorldEvent`, `HostExecutionReceipt`, notificações de revogação/expiração, novas avaliações DEC-089, revisões de dossiê DEC-090, presença/recursos e mudanças de checkpoint. Rumores, propostas, previsões e mensagens da IA não são fatos nem gatilhos de execução automática.
2. **Operação com revisão imutável:** `OperationInstance` vincula `plan_id`, `plan_revision`, `campaign_id`, `branch_id`, `checkpoint_ref`, `resolution_epoch`, `knowledge_pack_binding`, participantes/titulares, aprovações, capacidades e recursos reservados. Replanejar cria uma nova revisão, não substitui silenciosamente o plano em curso.
3. **Máquina de estados distinta:** estados lógicos candidatos `RUNNING`, `REVIEW_REQUIRED`, `PAUSE_REQUESTED`, `PAUSED_ORCHESTRATION`, `REPLAN_PROPOSED`, `REAPPROVAL_REQUIRED`, `RESUME_READY`, `ABORT_REQUESTED`, `ABORTED_CONFIRMED`, `COMPLETE`, `FAILED`, `UNCERTAIN`, `STALE`. Nenhum `PAUSED_ORCHESTRATION` afirma pausa da simulação nativa do BG2:EE.
4. **Avaliação de impacto:** cada alteração produz um `OperationImpactAssessment` com causa, referências de evidência, alvos, objetivos, participantes, localização, janela DR, ACL, risco (incluindo risco agregado), custo/recursos, capacidades por build e estado das ações pendentes. Sem mudança material pode-se continuar sob política determinística já autorizada; mudança material exige suspensão de novos despachos, nova revisão e nova autorização.
5. **Reautorização por escopo:** trocar destino, risco, objetivo, participantes, uso de recursos, exposição de segredos, janela crítica, alvo ou escopo de ação requer revalidação de DEC-091/C, decisões do titular para PCs DEC-041/045/046, autoridade faccional e gates de risco DEC-027/034. Autorização de versão antiga não migra automaticamente à nova revisão; HIGH permanece default-deny.
6. **Retirada de consentimento:** quando um PC retira sua participação, o sistema bloqueia novos atos voluntários atribuídos a ele, marca decisões dependentes para revisão e propõe pausa/cancelamento ou continuação dos trechos independentes. Não apaga ações anteriormente confirmadas nem interrompe arbitrariamente os demais PCs.
7. **Autonomia limitada de NPC:** NPCs/facções podem reconsiderar seus compromissos dentro dos valores e obrigações estabelecidos DEC-047/048/068/087/088; planos NPC não forçam ações de PCs, não usam recursos impossíveis e não inferem presença física de CRE sem host.
8. **Pausa é lógica, não mecânica presumida:** `PAUSE_REQUESTED` pode impedir novos comandos do orquestrador; uma pausa real do motor, de script ou de batalha requer capability do adapter e teste de host + dois clientes, sem assumir que existe. Não chamar uma solicitação pendente de pausa confirmada.
9. **Abortar não é desfazer:** cancelar impede novos despachos quando seguro, mas não retrocede movimentos, dano, entregas, itens, diálogos, rumores ou eventos já confirmados. Compensações são propostas e validadas caso a caso, nunca rollback narrativo automático.
10. **Segurança de ações em voo:** comandos `DISPATCHED` ou com resultado `UNCERTAIN` exigem reconciliação por idempotency key, `host_session_id`, checkpoint e receipt antes de descartar reserva, repetir comando, mover NPC ou declarar operação abortada. Uma solicitação de cancelamento não comprova que engine a executou.
11. **Precedência de risco e consentimento:** autorização revogada, capacidade desconhecida, escalada HIGH, checkpoint inconsistente, divergência de ramo, alvo inválido ou ausência de prova autoritativa produz **fail-closed para novos atos**, mesmo se modelo narrativo propor urgência.
12. **Recursos e reservas versionados:** `ResourceReservation` DEC-091 usa leases/fencing; pausa não libera automaticamente recursos comprometidos; aborto confirma quais reservas podem ser liberadas, consumidas ou estão `UNCERTAIN`. Não duplicar NPC, veículo, ouro, item, janela ou serviço entre planos.
13. **Conhecimento e tempo:** plano revisado consulta apenas `DisclosureView` e avaliação legítima para cada ator no ano DR, conforme Knowledge Pack DEC-063 e ACL DEC-028. Fato verdadeiro privado do host não equivale a conhecimento do NPC. Rumor novo pode justificar nova investigação, mas não reautoriza coercão.
14. **Sem onisciência temporal:** a alteração do plano de proteção DEC-084/085, descobertas DEC-085/086 e mudanças de dossiê DEC-089/090 têm tempos de transmissão/recebimento, por canal e público. Nada se propaga instantaneamente entre guildas, PCs e NPCs.
15. **Monitoramento eficiente:** subscriptions por evento relevante, coalescing/dedup e scheduler DEC-056; não fazer polling de LLM por frame, tick, segundo ou passo do host. LLM local pode propor alternativas textuais quando solicitada, após filtro de ACL e orçamentos DEC-057–060.
16. **Prioridade e fairness:** em caso de múltiplos eventos, processar perda de consentimento/segurança antes de otimização. Mudanças cosméticas não reabrem consentimento desnecessariamente; muitas mudanças LOW que elevam risco total a HIGH exigem revisão de escopo e autorização.
17. **Queda e restore:** checkpoint DEC-053 e logs permitem identificar comandos concluídos, pendentes, incertos e divergências. Ramo antigo ou revisão de KPack incompatível fica `STALE`; reanexar/adaptar só após reconciliação explícita, sem importar fatos futuros.
18. **Criação de eventos válida:** `WorldFact` confirmado pode provocar novo plano, mas não se pode fabricar um evento para que o replanejamento pareça necessário; ação do host se materializa em receipt ou permanece UNKNOWN.
19. **Observabilidade e privacidade:** auditoria descreve razão do replanejamento, diferença entre revisões, quem autorizou, recursos/ações e recibos, com dados sensíveis redigidos. Logs/UI/LAN não revelam planos de escolta, localização de testemunhas ou pseudônimos DEC-076/083/085 sem ACL.
20. **Mecânica desconhecida:** sem POC, pausa do orquestrador não garante imobilidade do ator nativo; cancelamento de comandos já aceitos na engine, edição runtime de quests e movimentação multiplayer permanecem **não suportados até demonstração**. Nenhum contrato candidato é uma API entregue.
21. **Escopo não abordado:** priorização cruzada e coordenação de **múltiplas operações simultâneas** com contenção de recursos compartilhados e objetivos conflitantes ficam para DEC-093, sem alterar a reserva básica já definida em DEC-091.

## Exemplo conceitual

O grupo aprova observar o Armazém Norte, mas uma revisão válida do dossiê identifica possível transferência para o Sul; um PC também decide sair da missão. O monitor não troca automaticamente de lugar nem move ninguém. Marca os novos despachos que envolvem o PC como suspensos, preserva as ações já confirmadas, avalia o que mudou, apresenta alternativas aos participantes autorizados e cria `plan_revision + 1`. Somente após consentimento renovado e verificação de recursos/host poderá haver continuação. Se o pedido de pausa chegou quando uma ação já estava `DISPATCHED`, essa ação permanece em reconciliação.

## Consequências e riscos

- **Benefícios:** reatividade sem perda de agência; planos coerentes com novos acontecimentos, recursos reservados e consentimento; transparência e recuperação após falhas.
- **Custos:** ledger de eventos, gestão de revisões, pause/resume lógico, fencing de recursos, rastreio de atos in-flight, timeouts e testes de corrida.
- **Riscos:** falsa pausa de engine, dupla execução após cancelamento, invalidade silenciosa de aprovação, vazamento de segredo, abandono sem reconciliar reservas, troca de branch; mitigados por gates, receipt host, ACL e fail-closed.
- **Estado de evidência:** escolha C aprovada no Discovery. **90 testes são propostas não executadas**; engine e multiplayer permanecem sem prova.

## Próxima decisão aberta — DEC-093

**Coordenação de múltiplas operações simultâneas e objetivos/recursos compartilhados.**

- **A — Execução estritamente sequencial:** não coexistem operações, simplifica concorrência mas reduz o Living World.
- **B — Coordenação livre pela IA:** LLM escolhe prioridades, participantes e recursos sem arbitragem determinística, arriscando duplicação e coerção de PCs.
- **C — Orquestração concorrente com conflitos detectados, reserva/fencing, prioridades contextualizadas, fairness, reautorização quando necessário e recibos autoritativos do host:** **recomendada**, ainda **NÃO DECIDIDA**.
