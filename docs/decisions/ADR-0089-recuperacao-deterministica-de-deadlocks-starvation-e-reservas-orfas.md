# ADR-0089 — Recuperação determinística de deadlocks, starvation e reservas órfãs

- **Decisão:** DEC-094, **opção C**, aprovada expressamente pelo idealizador em **2026-11-07**.
- **Estado:** **APROVADA SOMENTE EM ARQUITETURA** (Discovery v9.0). **NÃO IMPLEMENTADA NEM TESTADA**.
- **Documento técnico:** `docs/94-deadlocks-starvation-reservas-orfas-preempcao-segura-e-reconciliacao.md`; **94 testes T094-01..94 propostos, NÃO EXECUTADOS**.
- **Preservação:** **DEC-060 a DEC-093 integralmente válidas**, com **ADRs anteriores ADR-0001..ADR-0088 mantidos byte a byte idênticos** ao pacote v8.9. Nenhuma regra anterior é substituída.
- **Dependências:** DEC-011/012/019/022/027/028/041/045/046/050–056/058/063/066–074/083–093; DEC-006/007/013/015/017/018 ainda abertas.

## Contexto e problema

A DEC-093/C permite concorrência e reservas lógicas com lease, CAS e fencing como design candidato. Entretanto, dois planos podem manter recursos que o outro aguarda; tarefas podem sofrer adiamento repetido (*starvation*); um worker pode desaparecer deixando reserva órfã; e operações `DISPATCHED`/`UNCERTAIN` podem ainda ter alterado o BG2:EE. Expiração do lease interno **não prova** que um NPC foi desocupado, que ouro foi devolvido, que um comando não chegou ao host, nem que uma decisão de jogador pode ser revogada. Resolver indiscriminadamente causaria corrupção narrativa e mecânica.

## Alternativas avaliadas

- **A — Cancelar todas as operações em impasse:** rejeitada; elimina progresso confirmado, fere agência e pode liberar recurso ainda usado no motor.
- **B — IA escolhe quais operações abortar/recursos reatribuir:** rejeitada; LLM não possui autoridade de consentimento, propriedade ou host.
- **C — Recuperação determinística, proporcional, auditável e reconciliada:** **APROVADA**.

## Política arquitetural vinculante

1. **Separar estados:** detectar `WAITING` não comprova *deadlock*, e espera longa não prova *starvation*. O monitor distingue `SUSPECTED_CYCLE`, `CONFIRMED_DEADLOCK`, `STARVATION_RISK`, `ORPHAN_SUSPECTED`, `UNKNOWN_HOST_EFFECT` e `RESOLVED` com evidências/versionamento. A decisão de liberação é distinta da detecção.
2. **Grafo de espera versionado:** cada dependência liga operações a recursos e titulares por `campaign_id`, `branch_id`, `operation_id`, `resource_identity_id`, janela DR, revisão, `lease_epoch`, `fencing_token` e `checkpoint_ref`. Uma aresta só vale enquanto a reserva/condição realmente bloqueia; eliminar arestas stale e ignorar espera por recurso alternativo comprovadamente viável. Ciclos `AND/OR` exigem análise conservadora para evitar falsos positivos.
3. **Deadlock confirmado:** ciclo de espera que impede o progresso de todas as operações envolvidas sob recursos/alternativas comprovados. Detectar SCC ou ciclo não autoriza cancelamento nem comprova automaticamente que todas as tarefas estão sem alternativas.
4. **Starvation mensurável:** medir tempo de espera monotônico para serviço e atraso narrativo pela cronologia DR **separadamente**, tentativas de admissão, ultrapassagens e compromissos. Idade de fila pode influenciar o desempate/antiguidade, mas nunca dá direito de movimentar PC, gastar ouro alheio ou superar um gate HIGH. Limiares e cotas ficam para SPECS/benchmarks.
5. **Lease expirado ≠ recurso livre:** lease expirado de reserva puramente lógica `HELD`, com prova positiva de ausência de dispatch ou efeitos, poderá entrar em liberação condicionada a CAS/fencing. `DISPATCH_PENDING` sem prova de não envio, `DISPATCHED`, `UNCERTAIN` e `CONSUMED_VERIFIED` ficam **QUARANTINED/RECONCILIATION_REQUIRED**, não liberados automaticamente.
6. **Fencing por epoch e host:** worker antigo com token vencido não pode obter nova reserva, modificar recurso nem reemitir comando. Fencing do middleware **não substitui** capacidade de rejeição no adaptador do host; antes de POC, não assumir que a engine rejeita ações tardias. Mudança de sessão/build/branch invalida autoridade da época anterior.
7. **Recuperação gradual:** primeiro remover solicitações *não admitidas* e candidatas obsoletas, negociar replanejamento, procurar alternativas verificadas e aguardar confirmação; só depois propor liberação de **reservas lógicas não despachadas e explicitamente revogáveis**, com aprovação quando necessário. Proibir preempção automática de item consumido, PC ou recurso in-flight.
8. **Escolha justa/reproduzível:** regras estáveis: autorização e segurança como pré-requisitos; depois reversibilidade, menor impacto comprovado, reservas anteriores, espera e urgência verificada; desempate estável por IDs/versionamento. LLM não seleciona vítima, rank oculto ou prioridade. Fairness da DEC-093 não autoriza violação de consentimento.
9. **Consentimento e titularidade:** cada proposta de cancelar/reservar novamente considera owner PC DEC-041/045/046, facção, delegação e compromissos prévios. Nenhum PC é forçado a desistir, sair da party, alterar rota, ceder equipamento ou gastar recursos por recuperação de deadlock. Ausência de aprovação implica esperar/falhar de modo seguro.
10. **Separar ações e ledger:** reserva lógica, aprovação, despacho e efeito host-confirmed são marcos diferentes DEC-091/092/093. A liberação pode retirar a pretensão lógica futura; **não** reverte ações já executadas. Host Action Gateway DEC-011/012 continua a única via de mutações com capabilities provadas.
11. **Idempotência e atomicidade local:** resolução usa `recovery_id`, `conflict_graph_revision`, `reservation_id`, `lease_epoch`, `fencing_token`, `idempotency_key`, `resolution_epoch` e CAS em ledger durável (tecnologia a especificar). Não pressupor transação distribuída com BG2:EE. Retries só após reconciliação de estado incerto.
12. **Crash/restart:** relógio monotônico de processo não sobrevive necessariamente a reinícios; após restart, suspender conclusões baseadas só em deadlines locais, verificar identidade do scheduler, epochs, log de despacho, última sessão host, checkpoint e receipts. Ação cuja entrega é ambígua fica `UNCERTAIN`; nenhum release/duplo gasto por timeout.
13. **Cronologia e save:** tempo de serviço e tempo DR DEC-022 não se confundem. Restore DEC-053/054, KPack pinado DEC-063, build ou branch diferente invalidam jobs e reservas stale, sem reexecutar histórico futuro. Conflitos fora da cena obedecem DEC-068–071, sem fabricar deslocamento de NPC.
14. **Impacto causal mínimo:** recuperação não cria automaticamente quests, sanções, combate, perda de relação, punição, fatos canônicos ou eventos de facção. Mudanças narrativas materiais são propostas e submetidas a DEC-027/034/074/091/092. Não apagar recepção anterior de informação nem resultados confirmados.
15. **Segredos e observabilidade:** grafo/diagnóstico pode conter IDs privados de NPCs, PCs, operação, testemunhas DEC-083–085 e dossiês DEC-090; fornecer a cada observador somente conflito e alternativas redigidos, sem revelar rotas, alvos, fontes ou pseudônimos associados. Logs do host e workers LAN também minimizados.
16. **Recurso não bloqueante:** separar CPU/RAM/LLM DEC-056 de recursos de mundo; starving um job de embedding não equivale a impedir deslocamento de NPC. Reduzir carga não pode atrasar indefinidamente reconciliação de segurança nem permitir fallback LLM que reatribua atores.
17. **Falha segura e progresso possível:** quando nenhuma liberação é provadamente segura, bloquear apenas as operações dependentes, manter outras independentes em andamento, alertar host/jogadores com descrição redigida e aguardar decisão ou prova. Não prometer garantia formal de ausência de deadlocks/starvation antes de SPECS e testes.
18. **Evidência antes de implementação:** 94 cenários sintéticos candidatos cobrem ciclos/OR alternatives, fairness, ownership, filas, fencing, restart e host incerto; POCs de bridge, persistência atômica, recuperação e host+2 clientes ainda **não executadas**. O sistema é somente projeto documental.

## Exemplo

Operação A reserva carroça e espera o guarda. Operação B reserva guarda e espera a carroça. O grafo identifica ciclo. Antes de qualquer liberação, verificar se ambos são `HELD` sem despacho, quem os autorizou e se existe um guarda substituto ou adiantamento de tempo. Uma operação pode propor adiar seu estágio futuro ou ceder voluntariamente reserva revogável. Se a carroça ou guarda tiver recebido ordem em voo, a reserva permanece em quarentena até recibo e reconciliação; não há teleporte, cópia ou reset mecânico.

## Consequências e riscos

- **Benefícios:** coordenação sustentável, trilha de auditoria, recuperação segura, proteção contra preempção arbitrária e redução de starvation sem violar autonomia.
- **Custos:** grafo de espera, progresso mensurável, epochs, CAS/fencing, reconciliação, alertas e política de revogabilidade por classe de recurso.
- **Riscos:** deadlock falso, falsa liberação por expiração, duplo efeito, relógio reiniciado, segredo vazado, favorecimento de jogador, trabalhadores antigos e host sem recibo; mitigados por fail-closed, dedup, ACL e POCs obrigatórias.
- **Condição real:** não houve implementação nem experimento em BG2:EE/EEex multiplayer; **94 testes candidatos NÃO EXECUTADOS**.

## Próxima DEC-095 — em aberto

**Compensação segura de operações parcialmente concluídas** (não confundir com resolução de reserva travada):

- **A:** rollback global automático de toda a operação e seus efeitos.
- **B:** LLM decide livremente quais efeitos reverter ou compensar.
- **C (recomendada):** passos tipo *saga* com histórico de efeitos confirmados, compensações explicitamente reversíveis, exigências de consentimento/gates e receipts do host, preservando consequências irreversíveis e marcando estados não compensáveis.
