# ADR-0051 — Gerenciamento adaptativo de recursos, prioridades e filas

- **Decisão de produto:** DEC-056 — qualidade de serviço do Living World e arbitragem de recursos entre game/multiplayer, segurança, IA e simulação.
- **Escolha expressa:** **C — gerenciador adaptativo de recursos com prioridades, filas e orçamento**.
- **Estado:** **APROVADA**, 2026-11-06.
- **Pacote:** Infinity AI Discovery **v5.2**.
- **Fase:** SDD Discovery; não é SPEC final, algoritmo implementado, benchmark ou prova de compatibilidade com BG2:EE/EEex/multiplayer.
- **Detalhamento:** `docs/56-gerenciador-adaptativo-de-recursos-prioridades-e-filas.md`.
- **Dependências:** DEC-002/003 (Windows/ordem dos testes), DEC-006 (hardware/modelos local-first, aberta), DEC-011/012 (host/gateway), DEC-014 (orquestrador), DEC-015 (gates, aberta), DEC-018 (operações, aberta), DEC-021/022/032 (simulação/tempo/escalas), DEC-027/034 (autorização e eventos HIGH), DEC-028 (ACL), DEC-053/054 (checkpoint/backup), DEC-055 (observabilidade), DEC-050/051/052 (conteúdo/build/migrações).

## Contexto

A arquitetura prevê múltiplos workers determinísticos, memória, LLM local sob demanda, análise de conteúdo e monitoramento coexistindo com uma sessão BG2:EE multiplayer. Uma política de execução sem limites pode competir por CPU, RAM, VRAM/GPU, disco e rede, degradando a jogabilidade, causando atrasos na sincronização ou produzindo backlog de eventos. A simulação agregada de regiões distantes não precisa consumir a mesma prioridade que uma interação ativa, mas a pressão de desempenho **não** autoriza descartar recibos mecânicos nem inventar acontecimentos.

## Decisão aprovada — invariantes

1. **Resource & Performance Director (RPD) lógico:** planejar/admitir/escalonar trabalho dos serviços sob controle do Infinity AI, com budgets adaptativos e filas diferenciadas; implementação/processos, algoritmos, limites e plataforma de instrumentação ficam para SPECS/POCs. Não afirmar controle interno do scheduler, da thread de renderização ou do motor BG2:EE.
2. **Proteção da partida e consistência:** priorizar fluidez/percepção de controle do jogo base, continuidade multiplayer, confirmações críticas do host, gateway e segurança da memória. O RPD não pode atrasar deliberadamente decisões de proteção, descartar recibos, liberar ações HIGH, reordenar fatos causais ou marcar `UNCERTAIN` como sucesso para ganhar FPS.
3. **Níveis funcionais de prioridade:** P0 controle de risco/integridade/receipt e interrupções necessárias; P1 interação imediata e sincronização já validada, inclusive diálogo requisitado; P2 trabalho relevante de `ACTIVE`/`NEAR`; P3 simulações `DISTANT`, projeções, preparação opcional; P4 reindexação/curadoria e tarefas não urgentes. Essas categorias são conceituais, não prioridades de processo Windows nem garantias de tempo real.
4. **Admissão e *backpressure*:** tarefas entram em fila com custos estimados, deadlines quando aplicável, escopo de campanha/modo/build/ramo, autorização, dependências, chave idempotente e política de cancelamento. Sob pressão, reduzir concorrência do LLM, pospor lotes e cancelar **somente propostas descartáveis que não possuem efeito confirmado**; nunca descartar evento/receipt durável pendente de reconciliação.
5. **Degradação segura:** tarefa interativa pode oferecer um fallback **já validado** ou indicar indisponibilidade sem fabricar diálogo, informação, quest, condição de NPC ou efeito no motor. Se um requisito de segurança não puder ser mantido, o World Health Monitor da DEC-055 bloqueia a capacidade afetada; qualidade de serviço nunca sobrepõe política de risco.
6. **Simulação temporalmente coerente:** lote diferido registra intervalo de mundo, versão das regras, dependências, seed determinística quando aplicável, revisão de entrada e watermark. Reprocessamento/catch-up respeita DEC-021/022/032 e limite de avanço; não há salto automático de tempo, execução infinita pós-ausência, reaplicação duplicada nem resultado offscreen mecânico sem host.
7. **Medição antes de orçamento:** coletar apenas métricas realmente acessíveis (CPU/RAM, GPU/VRAM quando disponíveis, I/O, latência do LLM, backlog/idade de tarefas, latência e estado de confirmações, estabilidade host+2 clientes). Sonda não implementada recebe `UNKNOWN`; não prometer FPS, milissegundos, taxa de tick, prioridades reais de OS ou consumo até benchmark.
8. **Equidade e privacidade:** evitar inanição permanente de trabalho distante mediante quotas/lotes limitados sem competir com tarefas críticas; não processar fatos privados fora do ACL nem pré-gerar conteúdo baseado em segredos para sessões/campanhas não autorizadas. Métricas locais por padrão.
9. **Compatibilidade e segurança de dados:** todos os jobs e caches incluem identificação da build e ramo; migração, rewind ou recovery invalida tarefas incompatíveis. Separar modo Original do Living World. Backups/checkpoints críticos não podem ser confundidos com trabalho de simulação descartável; I/O pode ser agendado, mas retenção/consistência permanecem protegidas.
10. **Implantação progressiva:** iniciar em BG2:EE limpo e orquestrador desacoplado, com medições sem interferência; testar host e dois clientes, carga LLM, VRAM pressionada, backlog, jogo em combate, desconexão, save/restore, incidentes e mudança de build antes de habilitar gestão automática. A localização física dos workers é tema posterior (DEC-057).

## Consequências positivas

- Evita acoplamento entre quantidade de NPCs/facções e inferências por frame/tick.
- Possibilita expansão gradual de simulação narrativa mantendo prioridades e proteção do estado.
- Favorece determinismo, auditabilidade, capacidade de pausar/resumir batches e medição real de gargalos.
- Permite aproveitar hardware adicional sem torná-lo obrigatório para campanhas pequenas.

## Limitações e riscos

- O Infinity AI não controla necessariamente o processo/CPU/rendering interno do BG2:EE. Um monitor/sidecar local pode competir pelo mesmo hardware; prioridades conceituais não impedem travamentos do jogo.
- Instrumentação, controle de processos Windows, limitação de VRAM, detecção de carga e cancelamento de inferência variam por runtime e hardware; nenhuma API foi validada.
- Uma fila pode esconder falhas ou acumular atraso; backlog, *head-of-line blocking* e tarefas obsoletas exigem testes.
- Promessas de resposta em tempo fixo, economia detalhada completa, milhares de LLMs NPC em paralelo, offscreen ticking irrestrito e salvamento atômico com BG2:EE ficam **explicitamente fora do escopo aprovado**.

## Alternativas consideradas

- **A — Limites fixos por componente:** fácil de configurar, mas pouca adaptação às oscilações de jogo/carga.
- **B — Processamento contínuo com ajustes gerais:** aproveita recursos ociosos, porém pode dar prioridade errada e não protege filas/autoridade.
- **C — Gerenciamento adaptativo por prioridades e filas (aprovada):** controla demanda dos serviços próprios segundo criticidade, relevância e capacidade observada, sem substituir segurança e host.

## Critérios candidatos para validação

1. Com batalha pesada host+2 clientes, reduzir trabalho distante e geração especulativa antes de degradar interação prioritária; medir efeitos reais.
2. Com LLM local congestionado, limitar concorrência; produzir fallback verdadeiro ou indisponibilidade, sem eventos falsos.
3. Sob CPU/GPU/I/O saturados, continuar registrando receipts/estado de risco sem marcar confirmações não recebidas como sucesso.
4. Com jobs pendentes e avanço de relógio FROZEN/PARTIAL/REALTIME, não acelerar indevidamente a cronologia nem duplicar eventos no catch-up.
5. Após rewind/migração, invalidar jobs e caches de ramo/build anterior, preservando auditoria.
6. Sem sonda de GPU/host, marcar `UNKNOWN` e não anunciar orçamento comprovado.
7. Ao pausar uma tarefa, permitir retomada somente a partir de checkpoint e revisão compatível.
8. Sob fila antiga, aplicar fairness limitada sem comprometer a proteção P0/P1.

**Situação dos testes:** nenhum foi executado. As métricas e orçamentos serão fixados somente em SPECS, após os gates técnicos. **Próxima decisão sugerida:** DEC-057 — topologia de execução dos serviços de IA/simulação no multiplayer (host, processo local separado ou nó opcional na LAN).
