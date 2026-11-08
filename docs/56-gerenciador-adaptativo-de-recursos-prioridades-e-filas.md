# DEC-056 — Resource & Performance Director: qualidade de serviço, orçamentos e filas adaptativas

**Escolha:** C, aprovada em 2026-11-06; ADR-0051.  
**Pacote:** Infinity AI Discovery v5.2.  
**Estado:** análise arquitetural candidata para SPECS e provas de conceito; nenhum serviço, prioridade de SO, sensor, benchmark, fila, LLM ou bridge foi implementado/testado.

## 1. Objetivo e fronteira de autoridade

O sistema deve ajustar **sua própria demanda** de computação, não alterar a lógica interna do BG2:EE nem prometer controle da thread do motor. Preservar a experiência cooperativa sem produzir cronologia falsa, perda de logs, segredos expostos ou efeitos mecânicos sem receipt. Adaptar o ritmo da simulação pode alterar **quando calculamos** uma projeção, mas não **qual resultado confirmado** a campanha registra. A topologia de execução e modelos/hardware estão pendentes de DEC-057/DEC-006.

### Invariantes

- **INV-RPD-01:** o host do BG2:EE permanece fonte de confirmação mecânica; prioridade de fila não concede autoridade para alterar jogo.
- **INV-RPD-02:** segurança, ACL, recibos, reconciliação `UNCERTAIN` e checkpoints não são trabalho descartável sob carga.
- **INV-RPD-03:** nenhum job de simulação distante cria resultado mecânico offscreen sem confirmação; não inferir spawn/morte/venda por cálculo agregado.
- **INV-RPD-04:** o relógio da DEC-022 e as fronteiras causais da DEC-053 prevalecem sobre filas e atrasos.
- **INV-RPD-05:** o estado reportado das sondas (`UNKNOWN` se não suportadas) deve ser verídico; falha de instrumento não se converte em medição sintética.
- **INV-RPD-06:** trabalhos não urgentes podem ser retomados ou descartados **apenas se nunca produziram efeito durável**; tarefas mutativas pendentes precisam ser reconciliadas.
- **INV-RPD-07:** prioridade operacional não revoga políticas de cânone, consentimento, PvP, privacidade ou decisão humana.

## 2. Diagrama lógico proposto

```text
BG2:EE host + 2 clients ──> capability / optional metrics probes
         |                               |
         | events + receipts             v
         +----------------------> World Health Monitor (DEC-055)
                                           |
                                           v
                      Resource & Performance Director (RPD)
                          | measures, capacity confidence
                          | admission, priority, fairness
                          | backpressure, budgets, queues
                      ____|______________________________________
                     |                 |               |          |
                Interactive        ACTIVE/NEAR     DISTANT/    Optional
                NPC+LLM tasks      deterministic   DORMANT     pregen/
                     |             simulations    batches     indexing
                     |                 |               |          |
                     +-----------------+---------------+----------+
                                       |
                           typed proposals + validation
                                       |
                      ACL / canon / risk / Action Gateway
                                       |
                    host receipt + persistence + checkpoint
```

O RPD **não** é um segundo host, não substitui o Action Gateway e não supervisiona o jogo com privilégios implícitos. O fluxo é lógico: a implementação poderá ser processo, biblioteca ou serviço local, condicionada à validação da topologia.

## 3. Classes candidatas de prioridade (não equivalentes ao scheduler do Windows)

| Classe | Exemplo | Sem recurso suficiente | Nunca permitir |
|---|---|---|---|
| **P0 — proteção de estado** | Contenção de mutação perigosa, receipt de gateway, incidente `UNCERTAIN`, ACL, checkpoints em transição crítica | Bloquear novas mutações e escalar alerta; reservar capacidade para registrar causa/estado quando viável | Descartar evidência, confirmar sem host, executar rollback cego |
| **P1 — interação ativa** | Resposta pedida pelo jogador, eventos de sessão sensíveis ao prazo, consultas read-only do host | Desacelerar opcionalidades; fallback validado ou sinalização de indisponibilidade | Inventar resposta, ocultar latência, sobrepor política P0 |
| **P2 — mundo próximo** | Regras determinísticas ACTIVE/NEAR e missões relevantes | Reduzir taxa, granularidade e quantidade admitida | Modificar resultados já confirmados ou operar contra estado obsoleto |
| **P3 — mundo distante** | Lotes de economia/facções, rumores em DISTANT | Pospor/compactar lotes dentro de intervalos e dependências permitidos | Avançar calendário implicitamente, fazer catch-up sem limite |
| **P4 — preparações** | Indexação/curadoria não urgente, rascunhos de conteúdo, pré-computação | Cancelar se descartável, adiar para baixa atividade | Publicar conteúdo não revisado ou ignorar privacidade |

P0 não é um loop de alto uso CPU: no normal, deve dormir e ser acordado por evento. P1 não dá ao LLM permissão de execução de efeitos mecânicos. Prioridade para renderização/multiplayer é um **objetivo de não interferência**, e não acesso não demonstrado ao código do BG2:EE.

## 4. Medidas candidatas e confiança

| Dimensão | Exemplos de métricas | Limite de interpretação |
|---|---|---|
| CPU | Carga total e dos processos Infinity, tempo de worker, enfileiramento | CPU total não prova causa de perda de FPS |
| RAM | Uso, pressão de memória, paginação | Não inferir segurança de GPU por RAM |
| GPU / VRAM | Disponibilidade do dispositivo e consumo do runtime LLM se acessível | Sonda opcional; sem dados usar `UNKNOWN` |
| Disco / I/O | Latência de gravação, espaço livre, checkpoint/backup atrasado | Não interromper escrita crítica de modo a corromper dados |
| Rede / multiplayer | Latência de confirmação, estado host/clientes, desconexões quando observáveis | Um ping bom não prova estado mecânico sincronizado |
| LLM | Fila de inferência, duração, timeout, tamanho do contexto, pressão de memória | Não estabelecer meta antes de conhecer modelo/hardware |
| Simulação | Idade da fila, intervalo de mundo pendente, duração dos lotes, memória de jobs | Um lote concluído não prova efeito físico no jogo |
| Mundo / evento | Revision watermark, atrasos, falhas idempotentes | Relógio da campanha difere do relógio de parede |

**Padrão:** métricas locais com escopo/capacidade; não coletar prompts, históricos secretos nem texto de personagens sem necessidade/consentimento. Limiares e frequência das sondas serão determinados por benchmark, inclusive a sobrecarga do próprio monitor.

## 5. Admission control e contrato candidato do job

O agendador só pode executar tarefa se ela superar checagens de autorização e compatibilidade. Campos conceituais:

```yaml
job_id: identificador_unico
campaign_id: campanha
mode: LIVING_WORLD  # isolamento de ORIGINAL
build_fingerprint: hash_do_manifesto
branch_id: ramo_causal
world_interval: intervalo_de_tempo_da_campanha_ou_nulo
input_revision: revisao_origem
priority_class: P0|P1|P2|P3|P4
authority: read_only|proposal_only|typed_gateway_request
risk: LOW|MEDIUM|HIGH
knowledge_scope: acl_minima
idempotency_key: chave_estavel_ou_nula
deadline_kind: interactive|bounded|none
estimated_cost: cpu_ram_gpu_io_estimados_ou_UNKNOWN
dependencies: [ids_de_eventos_ou_tarefas]
resume_policy: stateless|checkpointed|non_retryable
status: queued|running|paused|blocked|uncertain|completed|obsolete
```

O exemplo é **contrato exploratório**, não esquema/API final. Um job com `typed_gateway_request` ainda passa por gateway, regras, consentimento, controles de risco e receipt do host. Prioridade não promove permissão.

### Gestão de filas

1. Selecionar trabalho pronto, validado e causalmente habilitado; adiar tarefas cujas dependências estejam `UNKNOWN`/`UNCERTAIN`.
2. Admitir execução dentro de orçamentos de simultaneidade/memória/latência observados, sem comprometer espaço para P0.
3. Aplicar *backpressure* aos produtores quando filas ou pressão de recursos subirem, evitando um acúmulo infinito.
4. Executar tarefas interativas com deadline **candidato**; quando expirar, sinalizar ausência ou entregar fallback aprovado, sem transformar timeout em resultado narrativo factual.
5. Para P3/P4, permitir checkpoint de lote, coalescência de tarefas compatíveis e cotas mínimas condicionais, evitando starvation indefinida.
6. Em mudança de build, ramo, save carregado, ACL ou versão de regras, invalidar trabalhos obsoletos. Preservar log/receipt de operações já despachadas para reconciliação, nunca removê-los silenciosamente.

## 6. Interação com tempo, simulação e persistência

- `ACTIVE/NEAR`: processar mudanças relevantes em menor lote **quando permitido**, sem assumir dados mecânicos de regiões não observáveis.
- `DISTANT`: continuar agregação deterministicamente reproduzível baseada em relógio da campanha, nunca no simples tempo decorrido do worker.
- `DORMANT`: projetar só ao reativar/catch-up limitado; ausência de processamento não equivale a ausência de eventos canônicos.
- Lote adiado precisa registrar `world_interval`, dependências, seed de regras quando aplicável, versão e posição do log para recuperar o mesmo resultado de lógica determinística; amostras de LLM usadas em fatos propostos precisam ser persistidas para replay/auditoria, sem alegar determinismo do modelo.
- Eventos de alto impacto permanecem aguardando política DEC-034. O RPD não deve usar carga baixa como autorização para resolver uma guerra, morte de figura canônica ou decisão de jogador ausente.
- DEC-053: job externo não publica checkpoint; apenas o protocolo coordenado publica par elegível. A política de latência/I/O nunca remove cópia íntegra nem ignora backup obrigatório.

## 7. Falhas, degradação e caminhos seguros

| Condição | Reação candidata |
|---|---|
| GPU/VRAM pressionada pelo LLM | Limitar concorrência/tamanho do trabalho quando suportado; não garantir liberação imediata de VRAM |
| CPU alta durante combate | Pausar P3/P4; reduzir P2 dentro de regras; não manipular thread do motor sem validação |
| Disco cheio | Bloquear novas escritas que possam corromper estado; acionar DEC-055 e DEC-054; preservar último par íntegro |
| Resposta LLM fora do prazo | Cancelar proposta sem efeito ou marcar timeout; conversa nativa somente se segura e disponível |
| Gateway com action `UNCERTAIN` | Não reexecutar; elevar P0 para reconciliação/alerta, sem alterar mecanismo de autoridade |
| Worker regional reiniciado | Reconstruir jobs pendentes compatíveis com watermark persistido; idempotência obrigatória |
| Mudança de ramo após restore | Invalidar jobs e cache futuros; manter trilha histórica separada |
| Detecção/controle indisponível | Informar `UNKNOWN`; reduzir capacidades não seguras, sem afirmar FPS protegido |
| Saturação prolongada | Informar anfitrião; degradar simulação/IA não essencial; se a integridade não puder ser garantida, parar mutações afetadas |

## 8. Interação com IA, caches e privacidade

A geração é **sob demanda** (DEC-014). Não rodar LLM por NPC/tick; priorizar pedidos reais de jogadores. Cache narrativo precisa ser indexado por campanha/ramo/build/contexto e ACL, e invalidado se fatos ou permissões mudarem. Pré-geração pode ocorrer somente onde não presume segredos futuros, resultados de quests nem informação privada. Um cache errado é dado inválido, não um fallback. Política de API remota e modelos permanece aberta na DEC-006; desempenho insuficiente **não** autoriza upload para provedor externo.

## 9. Plano progressivo de provas técnicas (candidatos)

- **G0:** baseline BG2:EE limpo Windows, motor sem Infinity e host + dois clientes. Medir FPS/latência e estabilidade com limites reais.
- **G1:** instrumentar serviços Infinity sem mutação e medir overhead do monitor/sondas.
- **G2:** adicionar LLM local sob demanda e filas sem integração mecânica; medir saturação CPU/RAM/GPU/VRAM e timeouts.
- **G3:** adicionar lotes determinísticos ACTIVE/NEAR/DISTANT e testar fairness, adiamentos, recuperação após interrupção.
- **G4:** injetar falhas/rewind/timeout de host e confirmar que P0/gateway/receipts/ACL nunca são rebaixados ou perdidos.
- **G5:** cargas em batalha, viagens, diálogos, saving, restore e rejoin host + dois clientes, comparando com baseline.
- **G6:** testar pressão de armazenamento e retenção/backups; verificar que o escalonador não destrói último checkpoint válido.
- **G7:** comparar build/ramo alterados, perda de sensor e ciclo de vida de jobs suspensos; nenhum replay cruzado.
- **G8:** medir limites sustentáveis por classe de hardware, comparar topologias após DEC-057/DEC-006, sem tornar hardware não validado um requisito normativo.

## 10. Matriz de 28 testes candidatos (não executados)

| ID | Cenário | Resultado esperado |
|---|---|---|
| T-056-01 | BG2:EE base host + dois clientes | Baseline medido antes de iniciar serviços extras |
| T-056-02 | Batalha pesada e worker P3 | P3 cede orçamento; registrar diferença de desempenho |
| T-056-03 | LLM saturado + diálogo solicitado | P1 tratado antes de pregen; fallback verdadeiro/timeout visível |
| T-056-04 | VRAM insuficiente | Limitar/recusar job LLM sem travar gateway |
| T-056-05 | CPU 100% por worker local | Backpressure e alerta sem afirmar controle do motor |
| T-056-06 | RAM sob paginação | Reduzir concorrência e degradar não essenciais |
| T-056-07 | Disco lento durante save | Não publicar checkpoint parcial; reportar latência |
| T-056-08 | Disco cheio durante backup | Preservar último par válido e reportar falha |
| T-056-09 | Gateway em `UNCERTAIN` | Proibir repetição cega mesmo sob fila pressionada |
| T-056-10 | Receipt atrasado pelo host | Preservar pendência até evidência/reconciliação |
| T-056-11 | Worker de DISTANT interrompido | Retomar de intervalo/watermark sem duplicação |
| T-056-12 | Modo FROZEN e fila longa | Nenhum avanço artificial do calendário |
| T-056-13 | Modo PARTIAL após ausência longa | Catch-up dentro de cotas e sem evento irreversível automático |
| T-056-14 | DORMANT reativado | Expansão de projeção compatível, sem spawn suposto |
| T-056-15 | Alteração de build entre jobs | Bloquear trabalho/caches com fingerprint anterior |
| T-056-16 | Restore de save antigo | Invalidar eventos futuros no ramo restaurado |
| T-056-17 | Cancelamento de inferência sem publicação | Nenhum fato criado ou removido indevidamente |
| T-056-18 | Cancelamento de job já despachado | Manter receipt/reconciliação; não tratar como descartável |
| T-056-19 | Fila P4 enorme | Conter produtores e manter limite de armazenamento |
| T-056-20 | P3 continuamente adiado | Fairness bounded ou estado explícito de atraso |
| T-056-21 | Sonda de GPU indisponível | Status `UNKNOWN`, sem métricas inventadas |
| T-056-22 | Monitor falha sob carga | Degradação conservadora e aviso de observabilidade parcial |
| T-056-23 | Jogador A recebe telemetria | Sem vazamento de dados secretos do jogador B |
| T-056-24 | Pré-geração com contexto privado | ACL obrigatória, cache não compartilhado irregularmente |
| T-056-25 | LLM remoto não autorizado | Nunca realizar fallback externo por desempenho |
| T-056-26 | Eventos HIGH aguardando aprovação | Permanecem bloqueados independentemente de CPU livre |
| T-056-27 | Modo Original ativo | Nenhum worker do Living World interfere em seus saves/memórias |
| T-056-28 | Retorno da baixa carga | Aumentar trabalho opcional sem corridas, replay ou starvation |

## 11. Itens não decididos

- Topologia de execução/processos no host, em sidecar local e/ou nó LAN opcional (**DEC-057**).
- Modelos, tokens/s, hardware mínimo, GPU/CPU, limite de memória, política de API remota e quantificação de orçamento (**DEC-006**, aberta).
- FPS, latência de interação, deadlines, cooldowns, throughput de jobs, limites de concorrência e thresholds de alarmes (**SPECS + benchmarks**, DEC-015).
- Algoritmos concretos de fairness, backpressure, cache, checkpoint de job e medidores específicos; **nenhuma implementação foi iniciada**.

## DEC-057 — Orçamento por nó e execução desacoplada (v5.3)

A DEC-057 aprova `SINGLE_HOST` como baseline e `LAN_OPTIONAL` para mover computação não autoritativa a nós aprovados, preservando filas, prioridades P0–P4, input_revision e ACL. O RPD pode considerar custo local, latência LAN e capacidade observada por nó; não há promessa de scheduler de GPU/VRAM ou prioridade Windows. Trabalho `UNCERTAIN`, receipts, ações HIGH e checkpoints não se tornam descartáveis pela mudança de nó. Benchmarks separados de single-host e LAN serão exigidos em SPECS. Ver ADR-0052/doc. 57.

## DEC-058 — Admissão de jobs somente em nós autorizados (v5.4)

O RPD/dispatcher só pode incluir nós `ACTIVE` com identidade e escopo atuais. A política de prioridade nunca supera a ACL, revogação, validade do canal, consentimento ou proteção de segredos. Se nó rápido for `QUARANTINED/REVOKED`, deixar tarefa pendente ou usar fallback *validado*, nunca enviar para dispositivo não pareado. Jobs do ramo/build antigo e epochs inválidos não retornam à fila ativa. Nenhum orçamento ou benchmark foi realizado.

## DEC-059 — Admissão de rotas por capacidade e sensibilidade

O RPD só recebe candidatos **pré-filtrados** por privacidade, escopo, identidade LAN, revisão e capacidade adequada. Se não houver worker elegível, não liberar o mais rápido por conveniência: deixar pendente/usar resposta previamente validada. O RPD controla fila, concorrência, deadlines e recursos e nunca muda `permission_epoch` ou autoriza API remota. Os pesos e budgets serão benchmarkados. Ver ADR-0054 e doc. 59 (24 testes candidatos).

## DEC-062 — tarefas de ingestão nunca preemptem gameplay

Ingestão, OCR/parsing autorizado, embeddings de índice anual e extração com LLM são tarefas **não urgentes** sujeitas a quotas/backpressure e pausas seguras do DEC-056. Se o host estiver sob carga, adiar e retomar com IDs/hashes/revisões idempotentes; nunca escrever arquivo parcialmente publicável nem bloquear operação crítica BG2:EE. Limites numéricos requerem benchmarks e SPECS, não foram medidos.

## Integração DEC-063/C — atualização de lore é trabalho adiável (v5.9)

Diff de *knowledge pack*, preparação de índices anuais e análise de dependências são tarefas de fundo com quotas e backpressure; nunca devem disputar de modo não controlado recursos com host/multiplayer ou salvar sem checkpoint. Adoção só ocorre em ponto seguro validado; backlog não altera automaticamente a versão ativa. Não promover com base em resultado tardio de worker/revisão anterior.

## Integração DEC-064/C — aprendizado e crenças sem onisciência (v6.0)

Aprendizado DEC-064/C segue prioridades: evento social ativo pode precisar de resposta responsiva, mas revisões de crença não urgentes e difusão distante entram em filas delimitadas. Não LLM por NPC/tick; atrasos não inventam fatos nem alteram relógio. DEC-065 decidirá política de memória hierárquica/retention após avaliação de custos e integridade.


### Agendamento de consolidação e recuperação — DEC-065/C (Discovery v6.1)

A recuperação de memória necessária a interação urgente compete por orçamento limitado; consolidação e indexação são adiáveis com filas limitadas e idempotentes. Sem LLM por NPC/tick, sem expiração de eventos por sobrecarga. Proteção de âncoras não implica carregar tudo em memória RAM nem expor segredos.

### Integração DEC-066/C — orçamento de reconciliação (v6.2)

Checagem de identidade de NPC ativo é requisito de segurança antes de personalizar, mas scans de NPCs distantes podem ser adiados. Não recorrer a correspondência arriscada quando houver fila ou pressão de CPU/VRAM. Propostas de agendamento e promoção de NPCs genéricos dependem de DEC-067 e benchmarks.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

DEC-067 permite promoção seletiva conforme orçamento, mas não impõe LLM por NPC/tick; prioridades do host e tarefas confirmadas prevalecem. Quotas de individualização somente após benchmarks.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

DEC-068/C emprega quotas, filas duráveis e fairness limitados: ACTIVE e confirmações têm precedência sobre DISTANT, enquanto DORMANT consome apenas manutenção mínima. Saturação não apaga âncoras ou produz evento não confirmado; thresholds exigem benchmark.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: processamento DISTANT de roteiros é trabalho adiável com quotas e idempotência; host/jogabilidade prevalecem e atraso em fila não confirma viagem.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070: priorizar incidentes em cena e autorizações pendentes, adiar LOW DISTANT com cursor durável, limitar backlog e revalidar revisão temporal; não inventar desfechos para “alcançar o relógio”.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Reservas e handoffs DEC-071 sensíveis ao tempo entram na fila de prioridade adequada, mas não podem monopolizar processamento; overload degrada para pendente/narrativa, não inventa resultado para liberar backlog. Sem reprocessamento de evento já commitado.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

RPD DEC-056 controla custos de seleção e validação de templates DEC-072; atrasos podem levar a PENDING ou diálogo narrativo permitido, nunca a execução de assets não comprovados.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Limpeza não crítica pode ser postergada em filas duráveis com quotas; backlog não justifica descartar ownership, liberar incidente ou simular sucesso.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Jobs de difusão DEC-074 são background adiáveis e duráveis: filas e backpressure com prioridades menores que engine/host, sem fome infinita ou overflow silencioso. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Atribuição de mérito é tarefa adiável que não compete com gameplay e confirmação do host; filas duráveis e limites de backlog preservam revisão/ACL.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Verificação de provas de identidade e divulgação pode ser assíncrona e limitada por fila; gameplay prioritário não autoriza fallback que vaze identidade ou ignore ACL.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação por evidências (Discovery v7.3; não implementada)

A investigação de personas DEC-076 usará ledger privado por campanha/ramo, com pistas e hipóteses revisáveis, origem/independência de fontes, contraprovas e estados inconclusivos. Suspeita ou fala LLM não confirma identidade e não permite divulgação; vínculo factual restrito exige evidências/DEC-066, e revelação exige ACL/consentimento/risk gate por audiência (DEC-019/028/041/045/046). Rumores e repercussões DEC-029/074/075 são separados de fato e punição. **Preservar `knowledge/periods/<ANO>-DR/` fisicamente por ano, sem evidências privadas no cânone.** ADR-0072/documento 77; 58 testes não executados, sem POC BG2:EE/EEex/multiplayer.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Fluxos judiciais de facção DEC-078 usam filas event-driven e código, mantendo prioridade de gameplay/host; sem agente dedicado a cada guarda ou token por comando determinístico.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Regras e filas de pedidos DEC-079 preservam prioridade do gameplay, backpressure e cursor durável. Não permitir LLM por guarda/tick nem inventar conclusão para liberar fila.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

DEC-080 prioriza mensagens de revogação proporcionais ao risco, mantendo causalidade, ACL e quotas; fila atrasada não inventa entrega e gatilho HIGH sem status atual fica bloqueado.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Reparações podem aguardar revisão e prioridade de dano iminente; quotas/backpressure não permitem inventar pagamento, recibo ou audiência consumada.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Investigação é fila secundária; reduzir recursos pode adiar revisão, nunca pular prova/gates ou provocar punição automática por timeout.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Jobs de disclosure não podem ser acelerados ignorando ACL; quotas e fila durável preservam versão, prazo e cancelamento/revogação.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Reserva de guardas, abrigos e jobs de proteção tem quotas e prioridade, sem gerar NPCs/recursos do nada; backpressure não afrouxa gates HIGH.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Trânsito de notícias e investigações offscreen podem esperar sem abandonar política ACL; fila revogada ou stale é cancelada/reconciliada.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Isolamento de quotas para operações de engano; jobs de difusão atrasados devem verificar janela DR, revisão e credenciais antes de rodar. Fallback não ignora ACL.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Avaliações de conflito seguem eventos e budget; nenhuma LLM por tick ou criação sem custo de mensageiros, espiões e favores.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Negociações podem rodar por demanda sem LLM tick; caps/quotas por informante e budget impedem spam e farming.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Análise de relatório é fila priorizada por relevância, com orçamento para grafo de evidências e teto de uso do LLM; overload retorna INCONCLUSIVE.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Compilar/diff/versionar dossiê por evento, sem LLM tick. ACL revogada cancela fila de views e transmissões pendentes; uso de CPU por destinatário recebe limites.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Planejamento e avaliação rodam por evento/batch sob orçamento; faltando recursos computacionais, não descartar ACL, risk gate ou confirmação host.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Scheduler orientado a eventos faz coalescing/dedup de mudanças e prioriza revogação/risco; jamais chamar LLM por tick, frame ou segundo para monitorar.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Prioridade computacional P0–P4 e orçamento CPU/RAM/LLM são diferentes de prioridade narrativa/operacional. DEC-093 aloca NPCs/itens/tempo por consentimento, fairness e locks lógicos, nunca por score de CPU.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Tempo de espera por NPC/item não é fila CPU/LLM. Redução de computação pode atrasar trabalho opcional, nunca pular rechecagem de segurança, consentimento ou reconciliador.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Proposta DEC-096 exige indexação por ano/region/type e cálculo só em transições, não loop LLM por tick; DEC-095 processa falhas/compensações em filas seguras.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Indexar DEC-096/C por ano DR/região/fase/efeito e acionar por mudança de estado, evitando varredura completa em cada frame; DORMANT com catch-up limitado.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

DEC-097/C usa índices e invalidação focal por evento/tempo/região, mantendo orçamento DEC-056; nenhuma varredura per-frame.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Quotas por região/tick e orçamento de catch-up limitam CPU/LLM e número de entidades; prioridade computacional não é autorização para spawn.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Prioridade computacional não é propriedade nem autorização de recursos narrativos/mecânicos.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Budget/rate limit de sondagens impede varredura massiva; prioridade computacional não concede ACL.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **orçamento de recursos**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para fan-out limitado e filas orçamentadas para mensagens offscreen, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para orçamento e filas de processamento de reputação social, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Orçamento de tarefas não é autorização para cobrança. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Prioridades computacionais não impõem prioridades de quitação ou recursos. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Escrow não deve consumir simulação contínua; monitorar apenas mudanças de evento DR e receipts, com avaliação limitada.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
