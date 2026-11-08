# ADR-0024 — Propagação de informações por redes sociais, geográficas e temporais

- **ID:** DEC-029
- **Status:** **APROVADA — opção B**
- **Data:** 2026-11-06
- **Fonte:** decisão expressa do idealizador do Infinity AI nesta conversa.
- **Domínio:** notícias, rumores, segredos, facções, reputação, memória diegética e simulação distante.
- **Relacionamentos:** DEC-019 (segredos dos históricos), DEC-028/ADR-0023 (recuperação por destinatário antes do LLM), DEC-008/ADR-0011 (estado/eventos), DEC-009/ADR-0012 (canon), DEC-014/ADR-0008 (código primeiro), DEC-021/ADR-0009 (ACTIVE/NEAR/DISTANT/DORMANT), DEC-022/ADR-0010 (relógio híbrido), DEC-027/ADR-0021 (níveis de risco), DEC-012/ADR-0022 (gateway) e DEC-011/ADR-0007 (autoridade).

## Contexto e alternativas

O Living World deverá reproduzir a disseminação gradual de relatos: testemunhas, viajantes, tavernas, comércio, organizações, mensageiros e facções podem espalhar notícias sobre acontecimentos confirmados e rumores. Um fato registrado globalmente não pode, por si, ser considerado conhecido por todos os NPCs. Históricos secretos e informações equivocadas exigem controle distinto.

- **A — Somente transmissão direta/programada:** não escolhida; previsível, mas gera um mundo pouco reativo fora de cenas explicitamente escritas.
- **B — Redes sociais/geográficas, calendário e regras determinísticas:** **APROVADA**; cada transferência depende de canal, contato, deslocamento/alcance, oportunidade, interesse e política de acesso.
- **C — LLMs independentes decidindo continuamente todas as comunicações:** não escolhida; custo elevado, baixa auditabilidade e maior exposição de segredos.

## Decisão aprovada

1. **Redes e caminhos diegéticos.** Informações se propagam por relações NPC↔NPC, membros de facção, relações entre assentamentos, rotas e canais adequados ao cenário. Não existe difusão global automática nem entrega instantânea apenas por compartilhar uma cidade/região. Grafos, agendas e eventos serão representações lógicas — não implicam simular agentes continuamente.
2. **Tempo do mundo, não relógio de parede direto.** O momento elegível de comunicação respeita o calendário autorizado da campanha (DEC-022); sessões congeladas não avançam notícias. Após ausência, eventual difusão é simulada em lotes/catch-up delimitados, alinhada a DEC-021 e sem ultrapassar marcos irreversíveis protegidos.
3. **Disseminação prioritariamente por código.** Regras/FSM, tabelas, agendas, sementes reproduzíveis e filas duráveis definem emissor, receptor, alcance, elegibilidade, prioridades e probabilidade de retransmissão. LLM local só pode ser acionado sob demanda para **formular diálogos ou versões narrativas** de uma crença já legitimamente atribuída; ele não é fonte de permissões ou verdade.
4. **Controle na saída e na entrada.** Antes de transmitir, verificar se o emissor conhece legitimamente a informação e tem canal/intenção plausíveis de compartilhá-la; antes de atribuir conhecimento ao receptor, verificar campanha, época, destinatário, classificação, escopo e política de segredos da DEC-028/019. Não basta que o emissor possua acesso do narrador para disponibilizar a terceiros.
5. **Segredos protegidos.** Fatos privados de históricos não entram automaticamente em redes de rumores. Uma revelação genuinamente ocorrida no mundo poderá ser considerada fonte, mas exposições para novos destinatários exigem política explícita de consentimento/risco, contexto ficcional e verificações. Na ausência dessa política ou quando a autorização for ambígua, **não propagar** o segredo. A decisão não estabelece que todo segredo descoberto jamais pode vazar na ficção nem autoriza vazamento indiscriminado.
6. **Separar realidade, relato e crença.** O evento histórico/canônico e o estado verdadeiro da campanha não são modificados pelo simples fato de alguém dizer algo. Cada retransmissão produz/atualiza uma **crença atribuída**, com origem, cadeia de custódia, momento em que foi conhecida e grau de confiabilidade; rumor falso, suspeita e exagero continuam distintos de evento confirmado. Um mesmo NPC pode receber versões conflitantes.
7. **Deformação controlada e proveniência.** Reinterpretações, exageros e mal-entendidos podem criar *variantes de rumor* de forma estruturada, sem alterar automaticamente a verdade nem afirmar que toda fala procede da fonte original. Não permitir que texto livre invente autorização de leitura, comando de motor ou prova de um fato.
8. **Escala por região/facção.** `ACTIVE` pode materializar conversa explicitamente observada pelo host; `NEAR` considera vínculos e agendas relevantes; `DISTANT` pode propagar por lotes agregados/checkpoints; `DORMANT` não requer atualização permanente, podendo reconstruir eventos elegíveis sob demanda. Não usar LLM por NPC/tick.
9. **Autoridade e risco.** Atribuições de conhecimento/narrativas são registradas no domínio correto; qualquer efeito mecânico (inventário, spawn, agressão, mudança efetiva de estado do motor) passa pelo gateway e confirmação do host. Rumor que gere missão ou consequência política relevante respeita DEC-027: `LOW` validado, `MEDIUM` gated e `HIGH` bloqueado sem política especial.
10. **Persistência e reconstrução.** Registrar transferência, destinatário, tempo, fonte, cadeia causal, versão das regras, identificadores idempotentes e posição de processamento. Reabrir saves, reprocessar lotes ou reconectar clientes não pode criar conhecimento/recompensa repetida nem atravessar campanhas.
11. **Cronologia e canonicidade.** A notícia sobre um evento oficial só pode surgir após sua ocorrência válida na linha temporal específica e após existir um caminho de informação até o personagem. Divergências confirmadas (DEC-009) podem tornar versões anteriores obsoletas sem apagá-las silenciosamente das memórias existentes.
12. **Sem capacidade técnica presumida.** A decisão aprova o comportamento pretendido e o contrato lógico; não comprova implementação de canais, viagem, banco, EEex, bridge, multiplayer ou integração com mods.

## Exemplo orientador

Após uma batalha confirmada em Athkatla, guardas testemunham o evento. Um mercador que conversa com eles pode receber um relato por regras. Quando seu deslocamento para outra região se tornar elegível, esse relato poderá chegar a um comerciante local ou bardo. Algumas pessoas conhecerão versões incompletas ou exageradas; quem não recebeu a notícia não poderá falar dela legitimamente. Os dias específicos e as probabilidades permanecem **indefinidos** até as SPECS.

## Modelo lógico candidato, ainda não SPEC

- **Evento/fato:** `campaign_id`, `fact_id`, `event_id`, `truth_status`, `occurred_at_dr`, `region_id`, `classification`, `canon_source_id`.
- **Conhecimento do emissor:** `holder_id`, `claim_id`, `learned_at_dr`, `knowledge_source_id`, `confidence`, `redisclosure_policy`.
- **Enlace/canal:** `edge_id`, `sender_id`, `recipient_id`, `channel_type`, `route_id`, `eligible_from_dr`, `trust`, `availability`.
- **Transmissão:** `transmission_id`, `campaign_id`, `sender_id`, `recipient_id`, `claim_version`, `channel`, `source_chain`, `sent_at_dr`, `received_at_dr`, `rule_version`, `seed`, `policy_decision`, `idempotency_key`.
- **Crença do receptor:** `belief_id`, `claim_id`, `recipient_id`, `confidence`, `received_at_dr`, `is_verified`, `source_chain`.
- **Execução de lote:** `campaign_id`, `world_time_window`, `cursor`, `checkpoint_id`, `rule_version`, `replay_token`.

Campos são sugestões de design. Não foi escolhida tecnologia de armazenamento, algoritmo de rumor, taxas, limites de salto ou escala numérica de confiança.

## Critérios de aceitação candidatos

1. Testemunha conhece o acontecimento confirmado, mas NPC distante não o conhece imediatamente.
2. Um mercador com rota e encontro elegíveis poderá levar a notícia após o tempo permitido; sem rota/canal ou contato não transmite.
3. Com relógio `FROZEN`, nenhuma transferência futura é aplicada enquanto a campanha permanece parada.
4. Em `DISTANT`, duas execuções com mesmo estado, seed e regras chegam ao mesmo conjunto lógico de transferências sem LLM por tick.
5. Uma história secreta não pode ser publicada por mera presença no banco nem por tentativa de prompt injection em diálogo.
6. Agente do narrador não pode repassar seu conhecimento privilegiado como se fosse conhecimento de um NPC.
7. Rumor falso ou versão exagerada é persistido como crença/alegação, sem sobrescrever o fato confirmado.
8. Duas fontes distintas podem gerar rumores conflitantes; cada NPC recebe apenas as versões que alcançaram seu contexto.
9. Rumor sobre evento futuro no canon não aparece antes da ocorrência/liberação válida na campanha.
10. Evento confirmado alterado por divergência de campanha preserva cadeia histórica sem apaga-retroativo de crenças preexistentes.
11. Reabrir save e repetir catch-up não duplica transmissores, conhecimento nem recompensas.
12. Sem acesso do host ou com evento mecânico incerto, não afirmar que NPC presenciou ação não comprovada.
13. Dados de outra campanha e do modo Original não podem ser consultados nem disseminados.
14. Um rumor que proponha invasão, morte importante ou alteração política é classificado como consequência `HIGH` e não publicado/executado automaticamente.
15. Logs/resumos/caches não vazam conteúdo indevido por canais secundários.
16. Dois clientes multiplayer devem observar estado lógico coerente de diálogos/rumores autorizados; condição não comprovada até POC.

## Consequências e riscos

**Benefícios:** sociedade com memória causal, reputação emergente fundamentada em rumores, cronologia coerente, custo de inferência reduzido e relatos auditáveis.

**Custos:** exigirá dados sobre relações/rotas, política de confidencialidade, filas/checkpoints, controle de crenças conflitantes, limites de propagação, reprocessamento e simulação por proximidade.

**Riscos:** espalhar segredos por engano; loops de retransmissão; notícia global instantânea; notícias de eventos futuros; rumor tratado como prova; tempo deslocado após reload; conflito entre versões de estado e múltiplos clientes.

## Pendências para SPECS / próximos ADRs

- **DEC-030:** política de reputação: percepção por NPC, facção e região versus escore global e como separar fama, notoriedade, confiança e temor; **não decidida nesta ADR**.
- Definir canais e velocidades plausíveis, limites de retransmissão, expiração/correção, papéis e consentimento de segredos, agregação de milhares de NPCs, curadoria de rotas, orçamento e métricas de desempenho.
- DEC-018 (snapshots/logs/replay), DEC-006 (modelos/custo/privacidade) e DEC-015 (gates de teste); sem atribuir aprovação implícita.
