# ADR-0088 — Orquestração concorrente determinística com reservas, fencing e justiça cooperativa

- **Decisão:** DEC-093 — **opção C expressamente aprovada** em 2026-11-07.
- **Estado:** APROVADA **como arquitetura de Discovery v8.9**; **NÃO IMPLEMENTADA**.
- **Documento técnico:** `docs/93-operacoes-concorrentes-arbitragem-de-recursos-reservas-prioridades-e-recibos.md`.
- **Evidência:** 92 testes candidatos `T093-01..T093-92`, **TODOS NÃO EXECUTADOS**, sem POC em BG2:EE/EEex, bridge, host + dois clientes.
- **Proteção de histórico:** decisões DEC-060–092 preservadas integralmente; **ADRs ADR-0001..ADR-0087 byte a byte idênticos** à v8.8.
- **Dependências:** DEC-011/012/019/022/027/028/031–034/041/045/046/050/051/053/055/056/057/058/063/066–074/083–086/089–092; DEC-006/007/013/015/017/018 permanecem abertas em suas áreas.

## Contexto

A DEC-091 definiu plano, validação, autorização, reserva, despacho e receipt host em camadas distintas. A DEC-092 estabeleceu monitoramento, pausa lógica e replanejamento por eventos. Resta permitir a **coexistência de várias operações** sem reservar o mesmo NPC, item singular, veículo, quota de ouro, janela limitada ou capacidade incompatível duas vezes; sem fazer a LLM escolher prioridades arbitrárias; e sem um plano de um jogador consumir recursos ou compromissos de outro sem consentimento. A capacidade do middleware de coordenar filas não prova controle físico de personagens na engine. Devemos distinguir capacidade de computação (DEC-056) de recurso narrativo ou mecânico. Um fato confirmado por host não pode ser desfeito por decisão posterior do scheduler.

## Alternativas

- **A — Serialização de todas as operações:** rejeitada; reduz o Living World a uma única missão por vez, mesmo quando os recursos e locais são independentes.
- **B — Arbitragem livre pela IA:** rejeitada; um modelo não pode decidir titularidade, criar recurso, tomar controle de PC ou publicar efeitos mecânicos.
- **C — Orquestração concorrente determinística, sensível a contexto, fairness e autorizações:** **APROVADA**.

## Invariantes e regras vinculantes

1. **Concorrência real, autoridade limitada:** várias operações podem estar planejadas, reservadas ou ativas simultaneamente. O coordenador opera somente sobre o estado do Infinity AI; não é um segundo host BG2:EE nem controla diretamente a thread do jogo.
2. **Identidades estáveis:** toda operação/reserva aponta para `campaign_id`, `branch_id`, `operation_id`, `plan_revision`, `resource_identity_id`, `resource_kind`, janela temporal (clock DR para mundo), escopo de uso e `checkpoint_ref`. Nome, pseudônimo DEC-076 ou string de item não identificam unicidade.
3. **Classes de recurso:** distinguir NPC/PC singular, item/equipamento identificado, moeda/quantidade fungível com fonte, transporte, serviço, área/capacidade, tempo/janela, permissão/slot e capacidade computacional do middleware. Cada classe exige regra de compatibilidade e prova específica; sem informação suficiente, `UNKNOWN` e não alocar.
4. **Claims/locks de recursos:** reserva é uma **pretensão lógica exclusiva ou compartilhável conforme regra**; não consome item nem move NPC. Para recurso singular em uso incompatível, permitir **um único titular válido** por janela/branch, via armazenamento durável e atualização atômica/fencing na implantação futura.
5. **Reserva ≠ consumo ≠ presença:** consumo/movimento físicos somente após gateway DEC-012 e receipt host DEC-011, capability provada por build e presença DEC-066/069. Reservas são reconciliadas com estado observado, jamais inventadas como alteração de engine.
6. **Fencing/idempotência:** reserva e despacho levam `reservation_id`, versão do recurso, `lease_epoch`, `fencing_token`, `idempotency_key`, revisão do plano, sessão host e epoch de resolução. Token vencido perde autoridade para novas mutações mesmo se worker atrasado retomar.
7. **Tempos separados:** janela de disponibilidade narrativa usa tempo DR DEC-022, enquanto timeout de mutex/lease interno pode usar relógio monotônico do serviço. Expiração interna não prova viagem, término narrativo nem liberação de efeito já confirmado na engine.
8. **Conflitos contextuais:** incompatibilidade pode surgir de interseção de horário, espaço, mesmo NPC, contrato exclusivo, dinheiro insuficiente, quotas de facção, permissão, objetivos mutuamente impossíveis ou ação in-flight. Estar na mesma região ou compartilhar um objetivo não é conflito automaticamente.
9. **Sem movimentação duplicada:** um NPC persistente DEC-066 não pode estar em dois locais fisicamente incompatíveis no mesmo tempo validado; clones de instância CRE, aliases e snapshots não concedem um segundo ator. Capacidade de localização deve ser host-confirmed ou tratada como incerta.
10. **Fairness transparente:** admitir operações com regras explícitas de urgência verificada, compromissos e reservas previamente assumidos, idade de espera, custos e prioridade de segurança. Estabelecer tie-break determinístico e auditável; **não** usar favores da IA, pontuação oculta ou privilégio fixo de um jogador.
11. **Prioridade não é permissão:** aumento de risco ou prazo pode antecipar análise, mas **não** revoga consentimento de PC, ACL, autoridade, limites de inventário ou proteção de evento HIGH. Prioridades P0–P4 do DEC-056 tratam carga computacional, não direito automático de requisitar NPCs/jogadores.
12. **Revisão de compromissos:** conflito pode produzir alternativas: adiar, fracionar etapas independentes, reduzir escopo, negociar compartilhamento permitido, solicitar substituto verificado, propor mudança de reserva ou pedir novas autorizações. Jamais transferir unilateralmente recursos pessoais ou comprometer PC.
13. **Preempção segura limitada:** reatribuição automática só é possível para tarefa **não despachada, ainda revogável e não dependente de consentimento novo**, com contrato explícito. Ação `DISPATCHED/UNCERTAIN` não pode ser cancelada, reexecutada ou liberar seu recurso sem reconciliação; preempção de PC/quest/combate requer gates próprios.
14. **Duas fases candidatas:** validar/admitir reservas no ledger primeiro (preparo); ações reais continuam no gateway/host (execução/recibo). O arranjo não é atomicidade distribuída engine+middleware e não promete transação impossível.
15. **Confirmações e efeitos:** um `HostExecutionReceipt` prova somente a alteração observada no escopo da sessão/build/branch; não autoriza inventar efeitos colaterais nem promover uma proposta à conclusão. Reentregas de mesmo receipt deduplicadas.
16. **Falhas/concorrência:** compare-and-swap por `resource_revision` e `fencing_epoch` futuros; se duas solicitações competirem, apenas uma vence e a outra recebe conflito explícito. `UNKNOWN/UNCERTAIN` bloqueia liberação ou novo despacho que gere duplicação; reconciliação supera retry.
17. **Sem deadlock silencioso:** registrar dependências (`wait-for`), detectar ciclos, exigir timeout/alerta e bloquear compromissos adicionais ao detectar impasse. **Política detalhada** de resolver deadlocks, starvation e preempção emergencial será DEC-094, sem autorizar abortos cegos agora.
18. **Revogação:** retirada de consentimento DEC-041/045/046 impede novos despachos em nome do PC; cancelamento DEC-092 invalida futuras reservas, mas não apaga despesas/efeitos passados confirmados. Recursos retidos por ação incerta permanecem em quarentena até conciliação.
19. **Chronology/branch:** cada operação aponta para Knowledge Pack pinado DEC-063 e estado do mundo/campanha correto. Restore DEC-053, troca de host/build ou branch invalida epochs antigos e exige revisão; eventos futuros/segredos não podem vazar para operações em curso.
20. **Privacidade:** scheduler vê apenas metadata mínima para arbitragem; dados de dossiê DEC-090, informantes DEC-088/089, refúgios DEC-083–085 e identidades secretas DEC-076 devem ser minimizados em logs, fila, LLM, clientes e LAN DEC-058. Um conflito pode ser comunicado sem revelar qual testemunha está sendo protegida.
21. **LLM sob demanda:** planejamento textual ou sugestões de negociação são opcionais, posteriores aos filtros determinísticos; nunca concedem `lease`, prioridade, consentimento, reserva ou mutação de host. Sob pressão, DEC-056 reduz trabalho opcional, nunca invalida ledger de segurança.
22. **Observabilidade e auditoria:** registrar decisão de admissão, recurso, janelas, regras de conflito, autorização, vencedores e bloqueios, starvation/tempo de fila, revisões, recibos e motivos redigidos. Critérios e limiares concretos ficam para SPECS/benchmarks.
23. **Limites de implementação:** não afirmar prova de controle simultâneo de CRE, inventário, equipagem, posição, pausas ou comandos canceláveis em BG2:EE/EEex multiplayer. POC por build/host+dois clientes obrigatória antes de permitir alterações nativas.

## Exemplo conceitual

Uma operação de investigação já reservou a disponibilidade de um NPC para 23h–1h. Uma escolta pede o mesmo NPC para meia-noite, enquanto uma observação remota usa outro recurso. O coordenador verifica identidade real, temporalidade e compromissos: mantém a investigação/observação independentes, **não** duplica o NPC, propõe adiar a escolta ou negociar substituição e solicita autorização das pessoas afetadas. Um rumor de urgência sem corroboração não revoga automaticamente o contrato anterior. Se o NPC já recebeu despacho host, a segunda operação aguarda receipt/reconciliação e não o desloca magicamente.

## Consequências e provas necessárias

- **Benefícios:** Living World paralelo, contabilidade de recursos, agência dos PCs e previsibilidade/replay determinístico.
- **Custos:** índice de disponibilidade, compatibilidade de locks, leases/fencing, arbiter com fairness, auditabilidade e recuperação de tarefas in-flight.
- **Riscos:** disponibilidade de NPC presumida, corrida de recursos, starvation, deadlocks, prioridade impondo consentimento, vazamento de objetivos secretos e falha entre ledger e engine.
- **Testes:** 92 casos T093-01..T093-92 **NÃO EXECUTADOS**. Não há implementação de scheduler, reserva atômica, adapter ou controle mecânico demonstrados.

## Próxima decisão aberta — DEC-094

**Resolução segura de deadlocks, starvation e reservas abandonadas entre operações.**

- **A — Cancelar todas as operações conflitantes** assim que um impasse for detectado.
- **B — Deixar a LLM escolher livremente quem perde reservas, é cancelado ou preemptado.**
- **C — Recuperação determinística, proporcional e auditável:** identificar ciclos de espera, leases expirados e starvation; liberar somente compromissos revogáveis e não despachados, propor negociação/repriorização e exigir reconciliação/consentimento/host para estados irreversíveis. **Recomendada, ainda NÃO decidida.**
