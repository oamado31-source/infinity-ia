# ADR-0050 — Monitoramento contínuo e recuperação segura orientada a risco

- **Decisão:** DEC-055 — política de observabilidade, alertas, modos degradados e recuperação de incidentes no Living World.
- **Escolha expressa:** **C — monitoramento contínuo com recuperação segura por níveis de risco**.
- **Estado:** **APROVADA** pelo idealizador em 2026-11-06.
- **Versão:** Infinity AI Discovery **v5.1**.
- **Fase:** SDD Discovery, **não implementada nem comprovada** em BG2:EE/EEex ou multiplayer.
- **Detalhamento:** `docs/55-observabilidade-health-monitor-e-resposta-segura-a-incidentes.md`.
- **Dependências:** DEC-011 (host/autoridade), DEC-012 (Action Gateway/idempotência), DEC-014 (IA local e regras), DEC-018 (operação geral, ainda aberta), DEC-021/022 (simulação/relógio), DEC-027/034 (risco e cânone), DEC-028 (ACL), DEC-045/046 (delegação), DEC-050/051/052 (scripts/builds), DEC-053 (checkpoints), DEC-054 (backup), DEC-015 (gates de testes, ainda aberta).

## Contexto

Uma campanha pode continuar exibindo o jogo enquanto o serviço narrativo, o modelo local, a bridge, um cliente multiplayer ou a rotina de backup estiverem degradados. Sem monitoramento, falhas silenciosas podem causar perda de progresso, divulgação indevida de segredos, divergência entre saves e narrativa ou repetição de efeitos mecânicos. A plataforma necessita manter observabilidade sem confundir uma falha detectada com autorização para consertar o estado do jogo ou alterar a história.

## Decisão aprovada

1. **World Health Monitor local-first:** monitorar a saúde *das interfaces realmente implementadas e observáveis* do host BG2:EE, bridge/EEex, gateway, banco e log narrativos, workers de simulação, LLM local, sessão multiplayer, checkpoints e backups; ausência de uma sonda deve ser marcada `UNKNOWN`, não `HEALTHY`.
2. **Separar componente, capacidade, severidade e ação:** um serviço pode estar em falha enquanto a campanha segue com capacidades restritas. Registrar evidência, timestamp/relógio, escopo (`campaign_id`, modo, build e ramo), causa conhecida ou suspeita e nível de confiança. Severidade de alerta não determina sozinha autorização para mutações.
3. **Estados candidatos:** `HEALTHY`, `DEGRADED`, `UNAVAILABLE`, `UNCERTAIN`, `RECOVERING`, `QUARANTINED`, `UNKNOWN`. São vocabulário de Discovery, não esquema ou API final. Definir histerese, limites e política de transição nas SPECS.
4. **Resposta por risco e por capacidade:** falhas de baixo risco permitem *apenas* ações automáticas previamente aprovadas, reversíveis e idempotentes (p.ex. reconectar um canal **somente leitura**, verificar status, reabrir worker stateless). Não fazer restart cego durante transação mecânica ou publicar resultado narrativo sem evidência.
5. **Degradação segura:** LLM indisponível pode suspender diálogo novo e manter conteúdo nativo já validado; banco narrativo indisponível bloqueia mutações que exijam persistência; bridge/gateway incertos bloqueiam despachos mutativos; checkpoint incompleto não é publicável; backup falho não equivale a save perdido, mas exige alerta. Continuar jogo base **apenas se a continuidade tiver sido comprovada segura** no build e no multiplayer.
6. **Falha crítica / fail-closed:** `UNCERTAIN`, divergência host/clientes, corrupção, quebra de identidade save–narrativa, risco de dupla recompensa, morte irreversível, segredo exposto ou impossibilidade de impor política obrigatória suspendem capacidades afetadas; poderão exigir pausa/interrupção da sessão conforme o que o motor permitir. **Nenhuma correção de estado mecânico por IA ou retries destrutivos.**
7. **Autoridade e recuperação:** anfitrião aprova ações de alto impacto e restauração em produção; host confirma efeitos físicos; gateway exige allowlist, autenticação, escopo, idempotência e receipt. A IA pode ajudar a explicar um incidente, mas não autoriza mudanças de estado.
8. **Retorno ao serviço:** verificar causa e pré-condições, reconciliar ações incertas, comparar checkpoint ativo/branch/build e, quando aplicável, sincronização com host + dois clientes; só então reabilitar a capacidade. Não presumir que serviço reiniciado signifique mundo consistente.
9. **Privacidade:** métricas e logs locais como padrão, acesso por necessidade/ACL, segredos removidos dos alertas genéricos, sem prompts ou históricos confidenciais em logs públicos, sem upload/telemetria externa por padrão. Qualquer exportação futura exige configuração e autorização explícitas, mantendo a DEC-028.
10. **Transparência e auditabilidade:** indicadores de saúde, últimas operações confirmadas, idade de checkpoint/backup íntegro, tentativas de autocorreção, estados `UNKNOWN`/`UNCERTAIN` e incidentes pendentes devem ser apresentados ao anfitrião em linguagem clara; não indicar sucesso antes de verificação.
11. **Monitorar o próprio monitor:** perda de heartbeat das sondas, relógio divergente, monitor indisponível ou armazenamento de logs cheio geram status de observabilidade insuficiente, nunca falsa declaração de normalidade. Alertas de degradação não devem ser usados para contornar política de falha fechada.
12. **Separação de escopo:** isolamento entre campanhas, Original/Living World, players, builds e branches. Um incidente em uma campanha não autoriza acesso ou modificação em outra.

## Consequências e riscos

**Benefícios:** descoberta precoce de falhas silenciosas, continuidade funcional limitada quando segura, menor chance de duplicidade de ações e diagnósticos mais claros. **Custos:** instrumentação, testes de falsas alarmes, alert fatigue, overhead de monitoramento, possíveis pausas e necessidade de guardar logs de forma privada.

## Limites e pendências

- **Não aprova** autorreparação irrestrita, migração automática de build, replay de operações desconhecidas, auto-rollback do mundo, escrita direta em save/flags, telemetria externa, modificação de políticas PvP/delegação ou garantia de disponibilidade 24/7.
- **Não substitui** checkpoints DEC-053, backups DEC-054, autoridade DEC-011/012, nem a especificação operacional completa DEC-018 (continua **aberta**).
- Saúde/performance de BG2:EE, leitura de flags por EEex, capacidade de pausar, reconnect de clientes, métricas e limites concretos **ainda exigem ensaio técnico** no Windows/host + dois clientes.
- **Próximo tema:** DEC-056 — orçamento adaptativo de desempenho e prioridades entre simulação, IA, bridge e fluidez do jogo.

## Critérios candidatos de aceitação

1. Simular LLM offline: nenhuma resposta fabricada, nenhuma alteração indevida no mundo, fallback somente para recurso comprovado e alerta adequado.
2. Simular timeout de gateway: operação passa a `UNCERTAIN`, não é repetida automaticamente e reabilitação requer receipt/reconciliação.
3. Simular perda do banco: bloquear mutações persistentes dependentes dele e apresentar estado degradado, preservando saves existentes.
4. Simular diferença entre save e narrativa: não publicar checkpoint até prova de coerência; nenhum merge silencioso de branches.
5. Simular backup falho e cheia de disco: preservar último backup íntegro e alertar sem anunciar sucesso.
6. Simular divergência host/clientes: impedir operações afetadas e só retomar após testes de sincronização.
7. Verificar que logs e alertas de um jogador não revelam históricos privados de outro; nenhum upload sem opt-in.
8. Exigir que capacidades sem sonda ou sem validação de fallback permaneçam `UNKNOWN`/não aprovadas.

**Status dos testes:** candidatos; **nenhum executado nesta decisão**.
