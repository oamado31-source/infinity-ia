# ADR-0068 — Propriedade, persistência seletiva e limpeza segura após encontros

- **Decisão:** DEC-073 — **opção C**, escolhida expressamente pelo idealizador em 2026-11-06.
- **Estado:** **APROVADA na arquitetura de Discovery v6.9; NÃO IMPLEMENTADA**. Não foram comprovados adapters de limpeza, spawn, remoção, transferência de inventário, save/load ou multiplayer BG2:EE/EEex.
- **Documento técnico:** `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md`, com **50 testes candidatos T073-01..50 (NÃO EXECUTADOS)**.
- **Preservação vinculante:** DEC-060–072 e seus ADR-0055–0067 **idênticos** aos do Discovery v6.8. Mantêm-se também DEC-003/005-E/008/009/011/012/017/021/022/027/029/030/032/033/034/050/051/052/053/054/055/056/066/070/071/072.

## Contexto

A DEC-071 disciplina o handoff exclusivo entre incidente fora de cena e encontro local, enquanto a DEC-072 define o catálogo de templates/componentes elegíveis. Mesmo após um encontro, permanecem elementos com origens e ciclos de vida diferentes: NPCs e scripts nativos; atores do catálogo eventualmente habilitados por POCs; recursos temporários do encontro; drops e inventários reais; estados de quest; relações e memórias. Apagar tudo destrói fatos legítimos e conteúdo original; manter tudo favorece duplicação, conflitos e degradação. O estado mecânico pertence ao host; a memória narrativa pertence a eventos confirmados, não a imaginação de um modelo.

## Alternativas

- **A — Remover tudo ao encerrar:** rejeitada; apagar indiscriminadamente pode atingir conteúdo nativo, objetos adquiridos e NPCs legítimos.
- **B — Preservar tudo:** rejeitada; deixa resíduos temporários, clones e flags inválidas em sessões seguintes.
- **C — Persistência seletiva, limpeza por propriedade comprovada e reconciliação com receipts do host:** **APROVADA**.

## Regras vinculantes

1. **Propriedade explícita e verificável.** Todo componente candidato à ação pós-encontro deve ter origem, `owner_kind`, `owner_id`, `encounter_id`, `incident_id`, `component_instance_id`, revisão, build e cadeia de custódia. `UNKNOWN`/`CONTESTED` nunca é tratado como propriedade do Infinity AI. Nenhuma suposição por nome, posição, sprite, arquivo CRE ou mera presença na área.
2. **Categorias de origem separadas.** Distinguir `NATIVE_OR_MOD`, `ENCOUNTER_TEMP`, `ENCOUNTER_PERSISTENT`, `TRANSFERRED_TO_PLAYER_OR_WORLD`, `UNKNOWN` (rótulos candidatos). Um item que mudou legitimamente para inventário, quest ou posse de NPC deixa de ser elegível à limpeza automática pelo antigo proprietário.
3. **Planejar, não executar por narração.** LLM/diretor pode propor uma política de término, nunca decidir diretamente remoção de creature/objeto, alteração de inventário, estado de quest, XP, loot ou morte.
4. **Registro de resultados e ledger de uma só resolução.** Usar o mesmo `incident_id`/`encounter_id`, `resolution_epoch`, fencing e `idempotency_key` da DEC-070/071. Marcar resultados de combate, recompensas e consequência narrativa uma única vez por branch/checkpoint e por receipt correspondente.
5. **Autoridade do host do BG2:EE.** Remoção, persistência física, inventário, flags, morte, XP e spawn são fatos mecânicos **somente** quando constatados/confirmados por host autorizado DEC-011/012. Receipts de LLM, cliente ou worker LAN não validam engine.
6. **Gates por capability e build.** `PRESENT` não prova que um adapter pode remover recursos. Cada operação de cleanup exige adapter tipado, POC verificável para build/versão de mod e testes de host+dois clientes quando multiplayer; sem isso, **não executar**.
7. **Plano de encerramento tipado.** Preparar `EncounterClosurePlan` com snapshot de precondições, conjunto de efeitos confirmados, componentes com ownership comprovado, operações candidatas, riscos e condição de checkpoint/host. `NO_OP`, `PRESERVE`, `ARCHIVE_NARRATIVE`, `REQUEST_CLEANUP`, `BLOCK_UNCERTAIN` são ações conceituais; mapeamento final só em SPECS.
8. **Conservar conteúdo nativo.** Nunca remover, reescrever ou assumir ownership de scripts, quests, romances, atores ou assets nativos/de outros mods por causa de encontro. A configuração original da build não é “lixo” para o Infinity AI.
9. **Consequências persistentes verificadas.** NPC sobrevivente verificado, relação, memória episódica, itinerário, reputação, objeto obtido, flag de quest e efeitos de combate têm tratamentos distintos; cada alteração precisa de origem e confirmação pertinentes. Não presumir que o episódio concedeu loot ou matou um bandido.
10. **Não apagar evidência e memória ao limpar.** Limpeza mecânica de instância temporária não apaga o evento de campanha, log causal, fonte, memória crítica, identidade individual DEC-064–068 ou histórico de handoff; preservar provas conforme retenção, privacidade e backup.
11. **Checkpoint e ordem segura.** Antes de cleanup elegível, exigir fase de encerramento e checkpoint coordenado conforme DEC-053, respeitando proteção de backups DEC-054; não supor atomicidade entre engine e banco. Planejar compensação/reconciliação sem rollback cego do motor.
12. **Falha `UNCERTAIN`/`STALE`.** Timeout, save/load, crash, disconnect, migração de build, divergência de checksum ou recibo incompleto suspendem remoção e liberação de reserva até reconciliação. Não repetir uma remoção destrutiva sem prova do resultado da operação anterior.
13. **Fencing e duplicatas.** Só o resolvedor com token e epoch atuais pode fechar o encontro, liberar a reserva DEC-071, agendar limpeza e publicar resultados. Eventos concorrentes ou reentregues não criam segundo término.
14. **Múltiplos jogadores.** Host é a autoridade, clientes recebem somente fatos confirmados e atualizações consistentes; nenhum cliente decide remoção. Não remover itens de jogadores ausentes sem regras de consentimento específicas.
15. **Risco pelo efeito real.** Remover recursos é potencialmente destrutivo: classificação LOW/MEDIUM/HIGH depende do alcance, risco acumulado, autoria, reversibilidade e contrato validado; HIGH default-deny e requer autorizações especiais. “Só limpeza” não é isenção de risco.
16. **Recursos fora de cena.** Desativar representação operacional não implica apagar NPC individual persistente, itinerário ou estoque; DEC-068/069 permanecem. Um ator nativo temporariamente não carregado não é necessariamente elegível para remoção.
17. **Proveniência e dados segregados.** DEC-060: cânone em diretórios **fisicamente separados por ano DR**, sem mutação por cleanup. DEC-061–063: fontes, staging, manifests e revisões de Knowledge Packs preservados. Efeitos ficam em overlay da campanha/ramo; catálogo DEC-072 separado da base canônica.
18. **Economia, facções e rumores.** Pós-encontro não propaga automaticamente efeitos globais; impactos de mundo requerem causalidade confirmada e políticas próprias DEC-029/030/032/033, a detalhar em DEC-074. Um recurso removido não prova que ninguém soube do acontecimento.
19. **Privacidade.** Receipts, logs e materiais de auditoria têm ACL/segregação por campanha/PC, redação de segredos e nenhuma telemetria não autorizada; workers LAN não recebem direito de cleanup mecânico.
20. **Fail-closed funcional.** Sem capacidade verificada de limpeza, preservar recurso temporário sob observação/flag de pendência e não o declarar removido; restaurar/retentar somente depois de reconciliar e de habilitar um caminho seguro. Priorizar integridade sobre estética visual.
21. **Limites operacionais.** Scheduler DEC-056 pode postergar limpeza não crítica; backlog durável limitado não altera o tempo do mundo, não libera incidentes prematuramente nem substitui confirmação de engine.
22. **Disponibilização incremental.** Começar inventariando passivamente recursos/receipts, simular encerramentos em dados sintéticos, executar POC isolada somente para um recurso temporário benigno se adapter existir, testar save/load/crash/restore, depois host+dois clientes. Cada capability requer aprovação independente.

## Consequências e trade-offs

- **Vantagens:** preserva itens conquistados e NPCs/quests legítimos, evita vazamento de resíduos e conclusões duplicadas, permite auditoria e migração consistente.
- **Custos:** manifesto de ownership, livro-razão de efeitos, reconciliação e testes por build; cleanup pode permanecer pendente em instalações sem suporte.
- **Limitação assumida:** não há confirmação de que BG2:EE/EEex permite destruir uma instância específica de forma segura em multiplayer. Essa opção **não** autoriza scripts livres, edição direta de save ou limpeza por heurística.

## Evidência e próximos passos

Aprovação humana da DEC-073/C e documentos de Discovery são a única evidência atual. Documento 73 contém **50 testes candidatos não executados**. Em SPECS: definir modelos de ownership, atomicidade possível, estados finais, critérios de transferências de item, receipts, matriz de capacidades de engine, política de retenção e testes de rollback. **DEC-006/007/013/015/017/018 continuam abertas**.

## Próxima discussão — DEC-074 (em aberto)

**Propagação das consequências confirmadas para o Living World:** A) fatos ficam isolados no encontro; B) repercutem imediatamente no mundo inteiro; **C, recomendada)** propagação causal gradual, contextual e por risco para rumores, reputação, relações, facções e economia, com evidência, canais de conhecimento, quotas, antidupla-aplicação e gates de autorização. Não confundir efeito mecânico com conhecimento universal.
