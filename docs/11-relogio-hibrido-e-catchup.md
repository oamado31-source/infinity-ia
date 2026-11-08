# Desenho preliminar — relógio híbrido, ausência e catch-up (DEC-022)

**Discovery v1.1** · **Estado:** arquitetura conceitual, não SPEC aprovada · **Fundamento:** ADR-0010 / DEC-022.

## Objetivo

Manter calendário coerente do Living World nas sessões e permitir evolução limitada durante ausências **sem** servidor contínuo. Integrar aos quatro níveis `ACTIVE`, `NEAR`, `DISTANT` e `DORMANT` da DEC-021 e à autoridade dividida da DEC-011.

## Políticas autorizadas

| Política | Com o jogo desligado | Na volta dos jogadores | Atenção |
|---|---|---|---|
| `FROZEN` | Nenhum avanço em razão do relógio externo | Carregar último `world_time` confirmado | O mundo retoma do ponto anterior |
| `PARTIAL` | Nenhum processo precisa executar | Converter ausência em avanço limitado, conforme parâmetros escolhidos pelo anfitrião | Limites e fórmula ainda não fixados |
| `REALTIME` | Nenhum processo precisa executar | Calcular avanço tomando o tempo real como referência, limitado e reconciliado | Não permite efeitos mecânicos retroativos sem validação |

O anfitrião define a política por campanha. Alteração de política exige versionamento; a regra aplicável a intervalos já transcorridos, o default e os parâmetros numéricos ainda serão definidos na SPEC. Não confundir `world_time`, timestamps UTC e tick do motor.

## Entidades candidatas

```text
CampaignClock:
  campaign_id
  mode: LivingWorld
  world_time_confirmed
  last_session_closed_at_utc
  time_policy / policy_version / parameters
  world_revision
  catchup_cursor
  host_save_fingerprint

CatchupBatch:
  batch_id / campaign_id / source_revision
  from_world_time / target_world_time
  ruleset_version / seed / budget
  status: PLANNED | PROCESSING | COMMITTED | FAILED | NEEDS_RECONCILIATION
  staged_narrative_changes
  pending_mechanical_actions
  resulting_revision
```

Os campos são hipóteses de contrato, não modelos de banco aprovados. Um mesmo intervalo só deve ser consumido uma vez; não se deve atualizar o checkpoint antes de persistir transacionalmente os fatos narrativos aceitos. Resultados mecânicos exigem o fluxo separado de confirmação do host.

## Algoritmo de alto nível — candidato

1. Detectar encerramento ou retomada de uma sessão cooperativa, identificando campanha, revisão e save do host.
2. Na retomada, comparar fingerprint do save, revisão e timestamps externos: se houver incompatibilidade, suspender catch-up e reconciliar.
3. Determinar política, janela de ausência, limites máximos e tempo alvo autorizado. Clock skew e timestamp futuro não criam avanço negativo.
4. Derivar atualizações de mundo com regras determinísticas e seeds estáveis; não rodar simulação individual por tick. Priorizar regiões narrativamente relevantes.
5. Filtrar alterações por causalidade, conhecimento e proteção contra eventos irreversíveis. Propostas que excedem permissões ficam pendentes.
6. Aplicar somente mudanças narrativas autorizadas e com IDs idempotentes. Ações mecânicas só avançam após o jogo confirmá-las em sessão válida.
7. Registrar revisão, checkpoint, cursor e um resumo inteligível das mudanças ocorridas, distinguindo confirmado de proposto.

## Proteção contra situações específicas

- **Sete dias de ausência:** o processamento segue o limite e a política escolhida. Não inferir que todas as missões expiraram.
- **Save do host restaurado:** detectar divergência antes de ativar atualizações; sugerir recuperação de snapshot correspondente, não repetir prêmios/alterações.
- **Vários jogadores ao reconectar:** um único lote no host/servidor narrativo por campanha/revisão; demais aguardam a mesma conclusão.
- **NPC significativo e segredo:** mudanças irreversíveis dependem de política futura; nenhum NPC aprende segredo por acesso direto da IA ao backstory sem causa registrada.
- **Modelo local indisponível:** apenas regras/tabelas/rotinas são aplicadas; geração criativa pode ser adiada. Jogo permanece funcional.
- **Jogo Original:** não compartilhar campanha ou chave de save com Living World.

## Requisitos de observabilidade (candidatos)

Registros de mudança de política, versão, período de ausência, tempo antes/depois, lote, orçamento, seed, revisões, decisões aprovadas ou pendentes, rejeições e motivo de recuperação. Ocultar do log público os segredos dos personagens e informações que NPCs não possuem.

## Dependências e bloqueios

- **DEC-008:** persistência de relógio, snapshots, eventos, NPCs e perfis; definição do sistema de registro.
- **DEC-009:** canon, ordem cronológica, irreversibilidade e eventos fora de cena.
- **DEC-018:** recuperação, migrações, backups e replay.
- **DEC-006:** limites do modelo local/latência quando a geração narrativa for necessária.
- **Prova técnica:** verificar acesso ao relógio real do BG2:EE, saves, EEex e host multiplayer antes de fixar APIs e comandos.

## Aceitação

Os 12 cenários de verificação da ADR-0010 são critérios **candidatos**. Nenhum foi executado ainda. A SPEC final deverá estabelecer parâmetros explícitos, dados de teste reprodutíveis, comportamento em falhas e critérios de rollback.

## Integração DEC-056 — orçamento não governa o relógio (Discovery v5.2)

Retardar ou adiantar processamento do Infinity AI jamais muda automaticamente a política FROZEN/PARTIAL/REALTIME selecionada. Cada catch-up usa intervalos delimitados de `world_time`, revisão causal, estado do checkpoint e limites da campanha; backlog grande não autoriza saltos temporais, eventos HIGH ou aplicação em massa. Simulações bloqueadas por falta de recursos são mostradas como pendentes/atrasadas, e não confirmadas. Regras e quotas quantitativas dependem de benchmarks/SPECS.

## Integração DEC-064/C — aprendizado e crenças sem onisciência (v6.0)

Aquisição e revisão da crença DEC-064/C levam timestamp/intervalo DR e vínculo causal. Campanha FROZEN não difunde aprendizado porque passaram dias reais; catch-up PARTIAL/REALTIME é limitado, idempotente, com canais sociais plausíveis e sem usar fatos de ano futuro como consumados. Salvar/restaurar recupera projeção epistêmica compatível com a campanha/ramo/checkpoint.


### Linha temporal das memórias — DEC-065/C (Discovery v6.1)

Sínteses e episódios carregam tempo DR/revisão da campanha e só incorporam evidência causalmente adquirida. Catch-up limitado não inventa conversas, testemunhos ou histórias de NPC em períodos sem observação/registro legítimos. Anos de cânone continuam em **pastas físicas separadas** DEC-060; conhecimento de futuro não pode retroagir para crenças presentes.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

Retomada de NPC offscreen segue apenas `world_time` e política FROZEN/PARTIAL/REALTIME DEC-022, com cursor processado separado de confirmado, quotas, revisão, idempotência e estados `STALE/UNCERTAIN`. Catch-up não autoriza fatos irreversíveis retrospectivos nem converte atraso na fila em tempo DR. Ver ADR-0063/doc. 68.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: planos de viagem avançam somente com janelas FROZEN/PARTIAL/REALTIME autorizadas, watermarks e catch-up delimitado; filas atrasadas não se convertem em chegadas consumadas.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

As janelas de incidentes DEC-070 seguem o relógio DEC-022 e o segmento confirmado DEC-069; backlog não cria tempo, mortes ou ataques retroativos. Eventos de futuro/restauração revalidados por epoch e watermarks.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

O tempo do incidente não avança por reservar handoff local. Rejeitar janelas incompatíveis, branch/checkpoint antigos e eventos já resolvidos; restaurar FROZEN/PARTIAL/REALTIME não reexecuta encontro. `UNCERTAIN` não é prova de que o efeito não ocorreu.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Entregas e efeitos DEC-074 obedecem FROZEN/PARTIAL/REALTIME, cronologia, limite de catch-up e fila versionada. Sem retroatividade por worker atrasado. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Ação, testemunho, relato e atribuição precisam respeitar ordem temporal; catch-up não cria observação retrospectiva de quem estava ausente.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

### Integração DEC-077/C — Investigação por evidências (Discovery v7.3; não implementada)

A investigação de personas DEC-076 usará ledger privado por campanha/ramo, com pistas e hipóteses revisáveis, origem/independência de fontes, contraprovas e estados inconclusivos. Suspeita ou fala LLM não confirma identidade e não permite divulgação; vínculo factual restrito exige evidências/DEC-066, e revelação exige ACL/consentimento/risk gate por audiência (DEC-019/028/041/045/046). Rumores e repercussões DEC-029/074/075 são separados de fato e punição. **Preservar `knowledge/periods/<ANO>-DR/` fisicamente por ano, sem evidências privadas no cânone.** ADR-0072/documento 77; 58 testes não executados, sem POC BG2:EE/EEex/multiplayer.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Prazos e fases processuais DEC-078 dependem de norma curada por região/ano e clock FROZEN/PARTIAL/REALTIME; catch-up não cria audiência retroativa nem decisão por atraso artificial.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Envio, trânsito, recebimento e validade de pedido DEC-079 obedecem FROZEN/PARTIAL/REALTIME; catch-up atrasado não inventa comunicação instantânea ou ignora revogações.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Avisos de revogação DEC-080 obedecem relógio FROZEN/PARTIAL/REALTIME, janelas e chegada causal; catch-up não gera ACK retroativo nem executa coerção do passado.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Mandado anulado hoje não cancela o tempo vivido até hoje. Notícias de retratação/restituição seguem FROZEN/PARTIAL/REALTIME, tempo DR e canais; jobs atrasados não geram retroação fictícia.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Revelações e ameaças respeitam clock DR, FROZEN/PARTIAL/REALTIME; uma fonte não pode ser conhecida em tempo anterior ao depoimento.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Escolta/abrigo/realocação seguem FROZEN/PARTIAL/REALTIME, datas DR, atrasos e gates temporais; não inventar viagem instantânea.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Descoberta e informação precisam ocorrer após observação e transmissão; FROZEN, PARTIAL e REALTIME limitam itinerário e notícias, sem retroatividade onisciente.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Lealdade e conflito são marcados por eventos e tempo DR; catch-up não inventa anos de traição nem conhecimento futuro de uma guilda.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Memórias/boatos acumulam histórico temporal de recebimento e validade; informe sobre amanhã deve registrar data DR de referência, evitando deslizamento da previsão no catch-up.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

TransmissionEvent de dossiê obedece DR/clock e catch-up local; não atualizar conhecimento do destinatário antes do receipt, nem retrodatar correções após rewind.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Janelas de operação obedecem clock FROZEN/PARTIAL/REALTIME e regras de catch-up; operação programada não implica execução no futuro sem confirmação.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

O sistema de eventos deve publicar confirmações causais e watermarks; rumores, snapshots especulativos ou mensagens da LLM não disparam execução. Falhas não apagam receipts anteriores.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Matriz proposta DEC-096 usa relógio DR autorizado DEC-022, mês/feriados Harptos e precisão; YEAR_ONLY não ativa por default no primeiro mês e FROZEN não avança por relógio de sistema.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-097/C — Discovery v9.3

Fade e expiração de efeitos DEC-097/C são medidos pelo tempo de mundo DEC-022, não tempo real do SO.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

DEC-098 usa exclusivamente relógio DR DEC-022 e revisão de campanhas, nunca relógio do SO para completar guerras ou eventos offscreen.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Campanhas e saves: identidade da instância deve incluir branch, epoch e build/modpack; migrações requerem reconciliação e bloqueio de writes obsoletos.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Host é autoridade mecânica; um envelope de observação não é recibo de comando nem confirmação de sua execução.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração DEC-102/C (Discovery v9.8)

Epoch e checkpoint de host condicionam a reconciliação DEC-102; relógio DR não substitui prova do save. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** marcos confirmados de quests originais são **origens candidatas** de regras históricas/regionais, não fatos canônicos escritos em `knowledge/periods/<ANO>-DR/`. A admissão exige prova reconciliada DEC-100/101/102, clock DR e branch adequados; a matriz DEC-096 filtra local, fase e precondições e DEC-097 compõe impactos. Escopo global não dá conhecimento universal. Evento proposto, evento host-confirmed e rumor entregue são distintos; nenhum efeito mecânico sem Action Gateway/receipt. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **host authority**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para relógio FROZEN/PARTIAL/REALTIME e latência DR por canal, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para relógio DR FROZEN/PARTIAL/REALTIME, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

O host segue autoridade mecânica sobre transferência de bens e moedas. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Autoridade mecânica permanece com host; grafo não cria transferência. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
