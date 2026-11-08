# DEC-055 — World Health Monitor e resposta segura a incidentes

**Infinity AI Discovery v5.1.** Detalhamento candidato do ADR-0050. **Nenhuma sonda, motor de alertas, recovery worker ou integração de monitoramento foi implementada/testada em BG2:EE/EEex multiplayer.**

## 1. Objetivo e princípios

Detectar falhas de componentes sem inferir que o jogo e o estado narrativo estão coerentes somente porque a tela continua funcionando. O monitor deve oferecer um diagnóstico legível, degradar funcionalidades conforme segurança comprovada e preservar a autoridade mecânica do host. Decisões e comandos da IA gerativa permanecem propostas, nunca autorização.

**Invariantes:**

- `HOST_CONFIRMED` e logs de acontecimentos confirmados não são substituídos por healthcheck de serviço.
- `UNCERTAIN` exige reconciliação de receipt e contexto; não existe retry automático de mutação não idempotente.
- Uma sonda ausente equivale a `UNKNOWN`; serviço reiniciado não significa que a campanha esteja saudável.
- Fallback deve ser **por capacidade**, com permissões pré-validadas; não existe chave global «continuar mesmo com erro».
- Nenhum alerta deve vazar segredo, histórico individual, conteúdo de prompts ou credenciais.
- Qualquer recuperação que altere estado mecânico ou restaure campanha ativa respeita autorização e evidência.

## 2. Arquitetura lógica candidata

```text
            Game host BG2:EE / bridge EEex (sondas somente onde viáveis)
                               │
   Narrative DB + event log ───┤
   LLM runtime + workers ──────┤──→ Health Collector (local-first)
   Action Gateway + receipts ──┤                │
   Clock + factions + stories ─┤          Health State Store
   Checkpoints / backups ──────┤                │
   Multiplayer host+clients ───┘         Policy & Risk Evaluator
                                             │
                   ┌─────────────────────────┼──────────────────────┐
                   │                         │                      │
          Alert/UI (ACL)            Safe Auto-actions        Fail-closed Gate
                   │                 (allowlisted)            / Escalation
              Anfitrião            read-only/stateless       host/operator
                                             │
                                      verify evidence
                                             └──→ re-enable only confirmed capacities
```

O desenho acima é **topologia conceitual**, não comprovação de APIs do motor. O jogo BG2:EE pode continuar exibindo quadros mesmo que seus adaptadores estejam invisíveis; isso não permite afirmar observação suficiente para mutação.

## 3. Modelo candidato de observação

| Classe de observação | Sinal possível | O que a observação NÃO comprova |
|---|---|---|
| Processo/jogo | PID/heartbeat, janela/sessão acessível se viável | Save íntegro, execução correta da quest, multiplayer sincronizado |
| Bridge e gateway | heartbeat, disponibilidade, backlog, action_id e receipt | Efeito físico concluído sem confirmação do host |
| Runtime de IA | pronto, fila, latência e timeout | Qualidade narrativa ou autorização para alterar quests |
| Memória narrativa | leitura/escrita, watermark, commit, lag | Correspondência automática com save BG2:EE |
| Simulação regional | backlog, último tick aplicado, catch-up pendente | Atualização física do mundo no mapa |
| Multiplayer | presença/versão, identidade, revisão e reconciliação se medíveis | Acordo sobre todos os estados ocultos sem teste |
| Checkpoints | manifest, integridade, estado de publicação e idade | Que o save carrega e progride sem ensaio de restore |
| Backups | cópia íntegra, última tentativa, destino, teste de restauração | Recuperação garantida em outro build ou hardware |

Campos propostos em `HealthSignal`/`Incident` (a especificar): `incident_id`, `campaign_id`, `mode`, `branch_id`, `build_fingerprint`, `component`, `capability`, `observed_at`, `signal_type`, `confidence`, `health_state`, `severity`, `evidence_refs`, `policy_revision`, `action_id`, `resolution_state`, `authorized_actor`. Logs para não operadores devem excluir segredos e caminhos privados. Rejeitar sinais de campanhas e builds diferentes.

## 4. Estados, níveis e modo degradado

**Estados candidatos:** `HEALTHY`, `DEGRADED`, `UNAVAILABLE`, `UNKNOWN`, `UNCERTAIN`, `RECOVERING`, `QUARANTINED`; não misturar saúde de processo, elegibilidade de escrita e integridade da campanha em uma só flag.

**Severidades candidatas:** `INFO` (informação), `WARNING` (funcionalidade reduzida), `ERROR` (capacidade essencial indisponível), `CRITICAL` (risco de inconsistência, perda de dados, segredo ou mutação irreversível). A severidade informa operadores; não fornece permissão para atuar.

**Máquina de estados de uma capacidade (candidata):** `HEALTHY → DEGRADED/UNAVAILABLE/UNKNOWN → QUARANTINED` quando houver evidência crítica; `RECOVERING → HEALTHY` somente após verificação de pós-condições. `UNCERTAIN` é estado de operação/efeito e pode coexistir com processo disponível; nunca promover por restart.

| Falha | Modo degradado **candidato, não presumido** | Ação que deve ser bloqueada |
|---|---|---|
| LLM fora do ar | Comportamentos e diálogos nativos já existentes, quando integração independente comprovada | Novos fatos/diálogos gerados dependentes do LLM |
| Banco narrativo fora do ar | Somente jogo nativo, se não gerar efeitos proibidos/desconexão causal | Novas missões e mutações persistentes dependentes do DB |
| Worker de facções indisponível | Suspender eventos e cálculos autônomos afetados, sem inventar ticks perdidos | Avanço histórico ou guerra com efeitos mecânicos |
| Bridge sem heartbeat | Exibir diagnóstico; manter recursos nativos se seguro | Novos comandos mutativos pelo gateway |
| Operação gateway UNCERTAIN | Reconciliação quando host voltar a fornecer evidências | Retentativa de recompensa, kill, item, flag, quest |
| Checkpoint falhou | Preservar último conjunto publicado | Publicação do par parcial ou restore automático |
| Backup falhou | Advertir sobre janela de perda; manter cópia válida | Excluir última cópia, afirmar backup protegido |
| Host/cliente inconsistente | Interromper funcionalidades afetadas; eventualmente sessão se necessário | Publicar evento mecânico sem concordância/receipt |

**Impossibilidade de fallback seguro = bloquear a capacidade**. Pausar o motor/encerrar sessão só se o BG2:EE oferecer mecanismo testado, ou por instrução transparente ao anfitrião; não alegar que o monitor consegue parar um jogo remoto sem provas.

## 5. Matriz de respostas por risco e autoridade

| Classe | Exemplo | Automação candidata | Condição de retomada |
|---|---|---|---|
| LOW | Falha de consulta/sonda transitória | Retry limitado de leitura; reconexão de canal read-only | Heartbeat e leitura testada |
| LOW | Worker sem estado com fila não mutativa | Restart allowlisted com circuit breaker | Fila coerente e sem ações mutativas pendentes |
| MEDIUM | LLM falhou, DB íntegro | Desabilitar geração/avisar; eventual reinício limitado | Testes de interface, sem publicar texto antigo |
| MEDIUM | Backup externo indisponível | Alerta; manter política de retenção e cópias locais intactas | Cópia confirmada e integridade revisada |
| HIGH | Divergência save/narrativa | Quarentena de checkpoint e revisão | Par coerente validado/autorizações |
| HIGH | UNCERTAIN mutativo | Bloqueio de replay e reconciliação com host | Receipt/idempotência/pós-condição comprovados |
| HIGH | Exposição de segredos ou corrupção | Isolar capacidade, registrar incidente minimizado, escalar | Política de privacidade e restauração aprovada |

A definição LOW/MEDIUM/HIGH é de **risco de intervenção**, derivada de DEC-027/034; não confundir com gravidade de alerta nem converter reinicialização de serviço em permissão para alterar histórico.

## 6. Modelo de incidente e ciclo de vida

1. **Detectar:** receber evidência com proveniência/escopo (não apenas texto de LLM).
2. **Classificar:** capacidades afetadas, criticidade, incerteza e superfície de segredo.
3. **Conter:** desabilitar ações específicas e impedir propagação de estado `UNCERTAIN`/corrupção.
4. **Notificar:** mensagem ao anfitrião com consequência prática, sem segredos irrelevantes; alertas deduplicados para evitar spam.
5. **Recuperar:** aplicar apenas ação allowlisted e pré-aprovada, ou solicitar intervenção explícita do operador.
6. **Verificar:** confirmar pós-condições e, quando aplicável, consistência de saves/memória, build e multiplayer.
7. **Registrar:** fechar incidente com evidência, revisar riscos; manter auditoria e evitar retenção desnecessária de dados pessoais.

**Anti-flapping/circuit breaker:** limites de repetição, janela de observação, cooldown, escalonamento e backpressure devem ser definidos em SPECS por testes; nunca reiniciar em loop até fabricar health GREEN.

## 7. Interface mínima e privacidade

O anfitrião deveria visualizar **estado do mundo**, **capacidades temporariamente indisponíveis**, **último checkpoint restaurável**, **última cópia verificada** e **incidentes pendentes**. A UI deve distinguir dados com prova de dados inferidos e comunicar claramente «a sessão pode continuar apenas com recursos nativos» versus «interrompa operações até resolver divergência». Participantes sem autorização não verão ramos secretos, caminhos de arquivos, relatórios de segurança ou prompts privados.

Por padrão, logs/metrics locais e sem envio externo. Exportações de relatório, notificações remotas ou telemetria devem depender de consentimento explícito do anfitrião e minimização por destinatário; a existência de serviços externos não autoriza transmissão de dados. Redigir referências de segredos nos relatórios do monitor, mantendo auditabilidade mínima.

## 8. Dependências, limites e provas técnicas

- DEC-011/012: host/recibos e gateway; DEC-053: checkpoint; DEC-054: backup; DEC-028: ACL; DEC-052: build; DEC-018: operação integral aberta; DEC-015: gates e regressões em aberto.
- **POC-1:** simular falhas de LLM e DB sem BG2:EE, verificando bloqueio e modo degradado somente por capacidades explicitamente implementadas.
- **POC-2:** integrar leitura/receipts com BG2:EE/EEex local e testar estados `UNKNOWN`/`UNCERTAIN` diante de timeout; comprovar se o motor pode ser pausado sem danificar save.
- **POC-3:** host + dois clientes, failover, reconnect, idempotência, persistência e nenhuma divergência mecânica após reinício.
- **POC-4:** crash entre save e snapshot/backup, recuperação isolada e proteção do último checkpoint válido.
- Não há nesta etapa demonstração real de qualquer POC nem implementação de monitor, sondas, UI ou fallback no BG2:EE.

## 9. Vinte e oito testes candidatos (não executados)

| ID | Cenário | Resultado esperado |
|---|---|---|
| T-055-01 | LLM local fora do ar | Novo diálogo IA suspenso; conteúdo nativo elegível permanece, sem inventar resposta |
| T-055-02 | Timeout de inferência com resposta tardia | Não duplicar evento; resposta extemporânea sem elegibilidade não se publica |
| T-055-03 | Reinício de worker stateless permitido | Executar apenas ação allowlisted e confirmar saúde antes de habilitar |
| T-055-04 | Banco narrativo inacessível | Mutação dependente de memória bloqueada e alertada |
| T-055-05 | Event log gravando mas snapshot falhando | Status degradado; checkpoint incompleto não publicado |
| T-055-06 | Bridge somente leitura desconecta | Monitor mostra falha e só reconecta canal testado sem criar mutação |
| T-055-07 | Gateway mutativo sem receipt | `UNCERTAIN` e nenhum retry cego |
| T-055-08 | Receipt chega depois de timeout | Reconciliar por action_id uma única vez |
| T-055-09 | Monitor reinicia durante ação pendente | Reconstruir alertas/estado de log sem reaplicar ação |
| T-055-10 | Host e cliente A divergem | Bloqueio de operação dependente; alerta e revalidação |
| T-055-11 | Host e cliente B divergem | Igual ao cliente A, sem privilegiar visão do cliente |
| T-055-12 | Fallback não suportado pelo build | Falhar fechado, sem afirmar continuidade segura |
| T-055-13 | Falha do LLM durante jogo base saudável | Jogo base não é encerrado por conveniência se independência foi validada |
| T-055-14 | Sem confirmação da capacidade de pausar motor | Não anunciar pausa; exigir alternativa operacional clara |
| T-055-15 | Backup para destino externo desconectado | Status DEGRADED e cópias íntegras preservadas |
| T-055-16 | Armazenamento cheio | Não apagar último backup ou checkpoint íntegro |
| T-055-17 | Checkpoint com pares de branches diferentes | QUARANTINED; recuperação não automática |
| T-055-18 | Carregamento de save antigo | Status de ramo alterado e memória futura segregada |
| T-055-19 | Alteração de ordem de mods durante campanha | Invalidar sondas/gates associados ao build |
| T-055-20 | Eventos HIGH pendentes em incidente | Sem aprovação por default; não promover ações irreversíveis |
| T-055-21 | Alerta enviado a jogador não autorizado | Não expor fatos privados, prompts nem caminhos de backups |
| T-055-22 | Telemetria externa desativada | Nenhum upload, mesmo em incidente CRITICAL |
| T-055-23 | Sonda indisponível/heartbeat vencido | Exibir UNKNOWN, não HEALTHY |
| T-055-24 | Falhas rápidas repetidas/flapping | Histerese/limite evita auto-restart sem fim; alerta persiste |
| T-055-25 | Falha auto-recuperável não responde à primeira tentativa | Respeitar orçamento de tentativas e escalar, sem loop de mutação |
| T-055-26 | Restore em produção solicitado pelo monitor | Exigir autorização do anfitrião e ensaio/cópia isolada |
| T-055-27 | Incidente em campanha Original | Não misturar com Living World nem ler suas memórias privadas |
| T-055-28 | Retorno a HEALTHY após reiniciar bridge | Exigir recebimento, IDs e sincronização, não só processo ativo |

## 10. Gates e critérios de no-go

**Gates candidatos:** G1 sondas observáveis com confiabilidade; G2 segregação de capacidades e políticas por risco; G3 bloqueio de `UNCERTAIN` e receipt; G4 modo degradado sem mutações indevidas; G5 relatório/alerta privado; G6 recuperação e verificação de pós-condições; G7 regressão BG2:EE host + dois clientes; G8 interações com backup/restore e migração de build.

**No-go:** ausência de visibilidade declarada como HEALTHY, restart destrutivo, retries cegos, encerramento/pausa não suportada pelo motor, upload sem consentimento, exposição de segredos, retropropagação de eventos do futuro após rewind e auto-declaração de sucesso sem provas do host.

## 11. Próxima decisão

**DEC-056 proposta:** orçamentos e prioridades de desempenho em tempo real. Como proteger a fluidez do BG2:EE/multiplayer quando simulação regional, LLM local, eventos e logging competirem por CPU, RAM, GPU e I/O? Definir política macro, deixando milissegundos/limites para benchmarks e SPECS.

## Integração DEC-056 — health signals vs budget signals (Discovery v5.2)

O World Health Monitor DEC-055 informa ao Resource & Performance Director somente sondas reais com confiança/status, backlog, capacidade e incidentes. O RPD pode diminuir o trabalho opcional sob pressão, mas **não** marcar o motor saudável com base em FPS, forçar retry mutativo `UNCERTAIN` ou alterar o status de backup/checkpoint. Saturação prolongada é alerta; falha de sonda é `UNKNOWN`. P0 preserva contenção e evidência, e modos degradados somente usam fallback já testado. A taxa das sondas também terá orçamento próprio para não causar degradação. Ver ADR-0051/doc.56.

## DEC-057 — Saúde e incidentes na topologia LAN opcional (v5.3)

Além das capacidades locais, o monitor poderá observar disponibilidade/latência dos workers LAN **somente se instrumentados**. Perda de heartbeat não prova perda de ação nem sucesso de job; `UNKNOWN` onde não houver evidência. Partição deve degradar a capacidade remota, mantendo gateway e checkpoints protegidos. Alertas não expõem conteúdo do job nem segredos. Nenhum retorno de LAN pode promover `UNCERTAIN` a confirmado. Pareamento seguro/identidade é assunto da DEC-058. Ver ADR-0052/doc. 57.

## DEC-058 — Incidentes de identidade e transporte LAN (v5.4)

World Health Monitor inclui sondas/alertas privativos para descoberta suspeita, tentativa de spoof, pareamento negado, chave substituída, identidade expirada, falha de integridade, resultado de nó revogado e exposição potencial de dados. Alertas não devem repetir chaves, tokens ou conteúdos privados. Quarentena bloqueia envio/aceitação de jobs de nó suspeito; operações com efeito mecânico e receipt `UNCERTAIN` permanecem para reconciliação, não autorreparação automática. Nenhum probe de rede foi implementado.

## DEC-059 — Health Monitor supervisiona rotas de modelos

Health Monitor registra falhas por worker/modelo sem conteúdo de prompt, desabilita destinos instáveis e sinaliza timeouts/erros de schema. Não cria permissão de fallback nem tenta resolver `UNCERTAIN`; reabilitação depende de saúde, identidade e autorização ainda válidas. O router aplica revisão de ramo/epoch, RPD regula backpressure. Nenhum monitor ou modelo foi executado.


## DEC-060 — incidentes de validação

Timeout ou indisponibilidade do verificador não é aprovação tácita. O monitor registra falhas sem segredos, coloca tarefas dependentes em modo seguro e evita publicar ou reexecutar operações `UNCERTAIN`.

## DEC-062 — observabilidade de ingestão e status de publicação

Monitorar jobs em staging, filas, direitos `UNKNOWN`, `NEEDS_REVIEW`, publicações incompletas, hashes e falhas de índice anual sem registrar texto integral protegido. Uma falha de publicação mantém last-known-good e bloqueia novos fatos até verificação; não declarar base/cobertura íntegra só porque diretórios existem. Reprocessamento automático apenas se idempotente e permitido, sem suprimir curadoria humana. Nenhuma implementação ou POC executada.

## Integração DEC-063/C — health checks do vínculo canônico (v5.9)

O monitor deve identificar hashes divergentes entre manifesto ativo e partições anuais, ausência de revisão retida, diffs/approvals obsoletos, caches stale e falha de checkpoint, sem autoaplicar packs. `UNKNOWN/UNCERTAIN` bloqueia migração crítica e aponta para reconciliação do last-known-good. Logs mínimos sem vazamento de segredos ou fontes protegidas; thresholds e correções automáticas dependem de SPECS/testes.


### Diagnóstico de consolidação de memória — DEC-065/C (Discovery v6.1)

Monitorar falhas/stale, filas, pressão de cache, reconstrução e uso de âncoras em métricas agregadas; não exportar episódios, segredos, prompts integrais ou nomes de PCs sem consentimento e autorização. Na ausência de fonte válida, sinalizar degradação/defer, não publicar lembrança inventada.

### Integração DEC-066/C — incidentes de identidade ambígua (v6.2)

Monitorar taxas/estados de `AMBIGUOUS`, `STALE`, prova ausente e tentativas de vínculo duplicado sem registrar segredos ou identificadores pessoais desnecessários. Um detector não pode "corrigir" auto-merge crítico nem repetir efeitos mecânicos `UNCERTAIN`. Contenção: suspender personalização, invalidar cache afetado e solicitar reconciliação autorizada.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

Monitorar fila de promoções, conflitos de identidade, duplicações e quotas DEC-067 com métricas minimizadas; saturação pode adiar promoção, nunca inventar `VERIFIED` ou descartar fato confirmado.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

Health Monitor DEC-055 distingue NPC hibernado intencionalmente de worker em falha, backlog e estado `UNCERTAIN`. Em DEC-068, métricas locais devem diferenciar `PROPOSED` de `CONFIRMED` sem revelar segredos; recuperação automática de baixo risco não decide morte/quest.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: monitorar planos bloqueados, rota sem fonte, conflito de área e backlog com metadados mínimos; não revelar itinerários secretos nem autocorrigir ação mecânica UNCERTAIN.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

Health Monitor DEC-055 e incidentes de viagem DEC-070 têm escopos diferentes: métricas de filas, gates e UNCERTAIN sem logs de segredo; monitor não autoriza automaticamente efeito narrativo/meânico nem retry cego.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Monitorar handoffs DEC-071 em `LOCAL_RESERVED`, `ENGINE_PENDING` e `UNCERTAIN`, locks órfãos, revisão de ledger e falhas de sync. Alertas e diagnósticos não autorizam automação de spawn, efeito HIGH nem liberação de reserva mecanicamente ambígua.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Monitor DEC-055 observa templates DEC-072 `STALE`, assets ausentes e capacidades revogadas; contenção LOW pode desativar seleção futura, mas não forçar spawn, limpeza de engine ou rollback falso.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Pendência ou resultado UNCERTAIN de cleanup recebe alerta local e contenção; monitor não retenta operações destrutivas sem evidência.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Monitor DEC-074: filas bloqueadas, deliveries atrasadas, eventos UNCERTAIN, propagação sem ACL, duplicatas e impacto acima de limite, com alertas locais redigidos e sem auto-correção HIGH. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Monitorar backlog e erros do ledger de atribuição com telemetria local sem expor segredos, aliases ou dados de PCs; UNCERTAIN requer reconciliação.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Logs e diagnósticos de personas preservam IDs redigidos quando necessário; falha de serviço ou fila UNCERTAIN não pode levar a divulgação duplicada nem revelar nomes privados aos observadores.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Monitor DEC-078 identifica casos disputados, autorização incompleta, operação UNCERTAIN, ACL violada e tentativas de punição duplicada; não executa remediação destrutiva.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Monitorar filas de pedidos DEC-079 sem exibir identidades secretas; alertas de entrega incerta, competência contestada e receipts obsoletos não disparam prisões nem retries.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Monitorar mandados DEC-080 revogados com notificações pendentes, delivery atrasado, ações BLOCKED_STALE e UNCERTAIN, sem vazamento de segredo ou autoexecução de coerção.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Monitorar reparações UNCERTAIN, pedidos repetidos, item duplicado, ausência de autorização e queues, sem efetuar automaticamente compensação ou expor vítimas em logs.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Monitorar pendências de revisão/medidas, inconsistência de competência, efeitos HIGH bloqueados, duplicatas e privacidade de testemunhas em logs.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Monitorar vazamentos/redactions/negações e UNCERTAIN sem colocar nomes protegidos em logs/alertas; não enviar telemetria remota involuntária.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Monitorar risco, filas e desvio de recursos sem incluir identidade ou localização secreta nos logs; UNCERTAIN demanda revisão, não retry de ação destrutiva.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Health Monitor sinaliza acesso negado, grant obsoleto e exposição provável com IDs redigidos; logs/alertas não contêm rota ou refúgio para observadores indevidos.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Auditar autorização, recurso, envio e refutação por IDs redigidos; não colocar roteiro real, identidade da fonte ou rota protegida em métricas acessíveis.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Diagnóstico de mudanças de lealdade não revela guildas secretas em logs de usuário; falhas de reconciliação geram alerta sem promover ruptura.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Auditoria exibe IDs e decisões de regra sob acesso permitido; detalhes de identidade, acordo, informante e benefício devem ser redigidos para logs gerais.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Monitoramento registra resultados redigidos de lineage, dedup e failures, sem expor nomes de testemunhas ou locais de refúgio em logs.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Auditoria técnica de dossiê deve registrar IDs, revisões, decisão/causa e outcomes sem vazar nome de fonte nos logs; erros UNCERTAIN não viram sucesso de transmissão.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Observabilidade deve registrar transições tipadas e redigidas, principalmente UNCERTAIN/STale, sem vazar objetivos ou alvos secretos.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Health/observability distingue RUNNING, PAUSE_REQUESTED, PAUSED_ORCHESTRATION, UNCERTAIN e ABORTED_CONFIRMED; logs redigidos e recibos autoritativos.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Medir wait age, conflitos por recurso, CAS perdido, starvation, deadlock e in-flight UNCERTAIN sem expor nomes, locais ou roteiros protegidos.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Monitorar ciclos confirmados versus suspeitos, starvation, lease órfão, quarentena, progresso independente e CAS/fencing; não vazar dados de planos em logs.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Métricas DEC-095: Saga UNCERTAIN, compensações pendentes/duplicadas; DEC-096 proposta: eventos elegíveis vs bloqueados, razões temporal/geográficas e dedup, sem vazamento de dados canônicos futuros ou secretos.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Avaliador DEC-096/C deve explicar por que uma regra foi elegível/negada, com log redigido por ACL, sem expor sigilos e sem confundir proposta com receipt.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Auditar DEC-097/C com ID, family, cap, fade, motivo de exclusão e hash de policy, mas redigir logs conforme ACL.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Monitoramento DEC-098 deve expor contadores de plano, conflitos e `UNCERTAIN` redigidos, sem publicar segredos ou tratar telemetry como estado engine.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Logs de conflitos de ownership expõem reason codes sem spoilers de quests, IDs privados ou segredos de fontes.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Observabilidade técnica não publica valores brutos de scripts/globals; logar reason codes opacos e revisões.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Catalogues by exact build/modpack/quest/script fingerprint, curated proof of semantic milestone and valid transition; an observed flag or stage is never an authorized quest write or host receipt. On patch or restore, invalidate semantic cache and avoid generic stage inference. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Logs de reconciliação DEC-102 contêm reason codes e referências opacas; sem payloads com spoilers. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **telemetria sigilosa**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para health monitor não registra fontes ou payload sensível em métricas, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para observabilidade e métricas não podem expor acusados ou fontes protegidas, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Logs mostram resumo seguro, sem dados privados de contratos. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Logs de dependências são redigidos por ACL antes de expor status. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Monitorar receipt duplicado, custódia não comprovada, liberação concorrente, stale epoch e disputa; logs com redaction.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
