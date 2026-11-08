# DEC-059 — AI Model Router: políticas de privacidade, qualidade, recursos e fallback

**Estado:** desenho técnico de Discovery; **DEC-059/C aprovada em 2026-11-06**, ADR-0054. Nada implementado, medido ou testado. Este texto contém modelos conceituais, não contratos de API validados.

## 1. Objetivo e fronteiras

Permitir inferências local-first eficientes no PC host, com workers opcionais pareados na LAN, **sem transferir para modelos qualquer decisão mecânica ou autoridade sobre história confirmada**. Integra:

- DEC-014: regras primeiro; LLM somente em tarefas abertas que o justifiquem, sem um modelo por NPC.
- DEC-028/041: ACL de conhecimento e autonomia de PCs; filtrar contexto antes de compor o prompt.
- DEC-057/058: single-host sem LAN obrigatória e somente nós devidamente identificados, autorizados e com canal seguro.
- DEC-055/056: saúde, admissão, filas por prioridade, deadlines, backpressure e cancelamento.
- DEC-011/012/053: host é autoridade mecânica, gateway tipado para operações mutativas, checkpoints e revisão/ramo.
- DEC-006 **ainda aberta**: modelos concretos, VRAM/RAM/GPU, consentimento para serviços fora da LAN, latência e custos.

## 2. Separação entre tarefas determinísticas e de IA

| Classe de tarefa | Caminho preferencial | Por quê |
|---|---|---|
| Ticks regionais, produção, comércio, diplomacia por regras | Código e lote persistente | Não há necessidade de LLM por tick |
| Reputação, autorização, clock, validação de risco | Regras auditáveis | Resultados verificáveis e reproduzíveis |
| Falas comuns com texto já disponível e compatível | Conteúdo aprovado/cache com escopo | Menor latência e risco |
| Diálogo aberto que exige linguagem natural | Modelo autorizado e avaliado | Texto proposto, nunca fato confirmado automaticamente |
| Proposta de cena, missão pessoal ou síntese narrativa | Modelo capaz, somente quando necessário | Maior complexidade, sujeito a story director/validação |
| Avaliação contextual ambígua de alinhamento | Regras + parecer auxiliar se permitido | A IA não decide alinhamento nem penalidades |
| Processar segredos de personagem | Worker com permissão explícita ao contexto mínimo | Dados privados não migram por conveniência |

## 3. Pipeline lógico de roteamento

```text
[Evento/solicitação auditável]
         |
[Elegibilidade: regras bastam?] --- sim ---> [Caminho determinístico]
         | não
[Tipo de job, contexto, risco, prazo]
         |
[ACL + minimização antes da transmissão]
         |
[Elegibilidade forte: modo/campanha/escopo/autorização/identidade/canal]
         |
[Capacidade: família de tarefa, compatibilidade, qualidade mínima aferida]
         |
[Admissão RPD: recursos, concorrência, latência e prioridade]
         |
[Modelo/nó selecionado -> proposta sem efeito]
         |
[Validação da resposta, proveniência e risco]
         |
[Story director/regras e Action Gateway se houver efeito]
         |
[Somente host confirma consequência mecânica]
```

Filtros de confiança e privacidade **nunca** são relaxados em caso de escassez computacional.

## 4. Contrato candidato de job (não implementado)

```json
{
  "job_id": "uuid",
  "campaign_id": "campaign-id",
  "mode": "LIVING_WORLD",
  "branch_id": "branch-id",
  "build_fingerprint": "hash-identificador",
  "world_revision": "revision-id",
  "permission_epoch": 0,
  "task_type": "NPC_DIALOGUE|STORY_DRAFT|CONTEXT_ANALYSIS",
  "risk_level": "LOW|MEDIUM|HIGH",
  "confidentiality": "PUBLIC|CAMPAIGN|PARTICIPANT_PRIVATE",
  "audience_scope": ["principal-autorizado"],
  "required_capabilities": ["pt-br-dialogue"],
  "deadline_policy": "interactive|background",
  "context_ref": "opaque-ref-minimized-by-ACL",
  "output_schema": "proposal-vN",
  "idempotency_key": "opaque-key"
}
```

O payload real de contexto é filtrado e enviado somente ao executor autorizado, não armazenado em metadados globais. `context_ref` é ilustrativo; não se afirma existência de API correspondente. Identificadores, classes e JSON são convenções **propostas** para futura SPEC.

## 5. Seleção em duas etapas

**Etapa 1 — elegibilidade restritiva** (falha fechada):

1. Política de campanha, modo e titularidade permite processar essa classe de dado.
2. Worker está `ACTIVE`, não `QUARANTINED/REVOKED`, com identidade verificada e canal protegido, se em LAN.
3. Escopo de autorização inclui `campaign_id`, `task_type`, contexto, resultado e validade atual.
4. Modelo/worker tem evidência de capacidade para a classe de tarefa; ausência de avaliação = capacidade desconhecida, não elegível para tarefas críticas.
5. Contexto foi minimizado e rotulado **antes** da transmissão; não contém segredos de terceiros, chaves nem saves brutos.
6. Job pertence ao ramo, build, revisão e época de permissões atuais.

**Etapa 2 — ordenação dos elegíveis:** aplicar política determinística por adequação linguística, qualidade validada para a tarefa, prioridade, latência observada, disponibilidade de memória/VRAM, fila/recursos RPD, saúde do worker e custo estimado (se algum custo vier a ser permitido pela DEC-006). Valores, pesos, limiares e prioridades específicas permanecem para SPECS/benchmarks; não otimizar custo/velocidade sacrificando qualidade mínima.

## 6. Fallback e indisponibilidade

| Evento | Resposta segura |
|---|---|
| Modelo menor indisponível | Modelo alternativo **já elegível** se houver; sem escalonamento automático de privilégios |
| Worker LAN interrompido | Cancelar/desqualificar resposta tardia; usar host se autorizado/capaz ou adiar |
| Pedido contém segredo pessoal e somente worker não autorizado está livre | Bloquear envio; responder com recurso aprovado ou deixar pendente |
| Deadline expirou | Ignorar resposta tardia; usar texto preexistente compatível ou falha explícita |
| Modelo retorna output inválido | Rejeitar e, se seguro, solicitar nova proposta limitada, sem executar ação |
| Revogação durante job | Atualizar `permission_epoch`, invalidar resultado e não prometer apagar informação já transmitida |
| Mudança de ramo/save/versão | Resultados de revisões antigas não são incorporados silenciosamente |
| Falta de LLM em combate | Sem mutação narrativa inventada; simulação/combate seguem apenas pelo caminho comprovado |
| Operação mutativa `UNCERTAIN` | Nenhum retry automático por outro worker; reconciliar host primeiro |
| Recurso online externo não configurado | Nenhuma tentativa de contato ou vazamento: DEC-006 continua em aberto |

## 7. Qualidade e integridade do resultado

Toda saída é **dado não confiável** e deve receber marcação de modelo, tarefa, revisão, escopo de leitura, validade e proveniência. Uma saída JSON bem formada não comprova verdade narrativa. Exigir, futuramente, validação de:

- estrutura/schema e tamanho permitido;
- fatos e eventos citados no event log versus rumores/opiniões;
- limites de conhecimento do NPC que fala;
- cronologia, região, NPC canônico, missões originais e conteúdo da build;
- autoria de decisões dos PCs e bloqueio a ações mecânicas não autorizadas;
- nível de risco e regras do gateway;
- respostas tardias ou oriundas de trabalho revogado.

Critérios de avaliação semântica e tratamento de ambiguidades serão objeto da **DEC-060** (proposta); testes de aceitação por feature seguem DEC-015, ainda aberta.

## 8. Segurança, observabilidade e custos

- Não expor prompts privados, logs integrais, chaves, saves ou transcripts secretos por conveniência do roteador.
- Registros locais usam `job_id`, tipo, worker/modelo, motivo resumido da escolha, versão, `permission_epoch`, tempos, uso aproximado, resultado `ACCEPTED|REJECTED|PENDING`, indicador de fallback e correlação ao checkpoint, sem corpo privado.
- O Health Monitor pode desabilitar modelos/nós degradados, mas **não** liberar escopos, reduzir validações ou inventar estado.
- O RPD pode limitar concorrência, batches e cache por ramo/ACL, especialmente durante combate; não executar segundo modelo revisor por padrão sem critério de risco/custo.
- Sem afirmar que criptografia, controles de processo, isolamento de dados ou APIs existem: especificar/validar em POC.

## 9. Plano de testes candidatos (24; **não executados**)

| ID | Cenário | Resultado esperado |
|---|---|---|
| T-059-01 | Mundo determinístico em lote | Nenhuma chamada ao LLM por tick ou NPC |
| T-059-02 | Conversa simples com modelo pequeno validado | Roteador prefere recurso elegível dentro do orçamento |
| T-059-03 | História complexa exige capacidade superior | Seleciona modelo com evidência de qualidade adequada ou adia |
| T-059-04 | Worker mais rápido não possui permissão de dados | É eliminado antes do ranking |
| T-059-05 | História secreta de PC | Contexto mínimo e scope somente titular/autorizados |
| T-059-06 | NPC não conhece segredo do grupo | Contexto ocultado e saída que o revela rejeitada |
| T-059-07 | Nó LAN não pareado tenta oferecer serviço | Não recebe trabalho nem contexto |
| T-059-08 | Nó revogado durante inferência | Resultado antigo rejeitado por epoch |
| T-059-09 | Reconexão com chave alterada | Revalidação, não reconexão silenciosa |
| T-059-10 | Fallback para modelo menos capaz | Executa somente se satisfizer requisitos mínimos |
| T-059-11 | Nenhum worker elegível para dado privado | Falha fechada; sem envio a nó não autorizado |
| T-059-12 | Worker LAN cai no meio de uma fala | Sem narrativa nova inventada; fallback aprovado ou pendência |
| T-059-13 | Deadline de interação estourado | Resultado tardio descartado, sem surpresa ao usuário |
| T-059-14 | Fila congestionada durante combate | RPD posterga jobs P3/P4; preserva integridade |
| T-059-15 | Proposta contém comando malicioso | Gateway não executa texto livre |
| T-059-16 | Saída JSON válida mas contrária ao cânone | Validador semântico rejeita/corrige por novo fluxo controlado |
| T-059-17 | Proposta atribui ação a PC ausente | Bloqueio por agência/consentimento |
| T-059-18 | Save anterior restaurado | Job da revisão futura invalidado |
| T-059-19 | Migração Build A para B | Hash/revisão antiga não autoriza resultado posterior |
| T-059-20 | Receipt `UNCERTAIN` durante failover | Nenhum retry de efeito; reconciliação |
| T-059-21 | Métrica e log de worker | Ausência de segredo e credenciais nos logs |
| T-059-22 | Single-host com LAN desabilitada | Fluxo completo sem dependência de descoberta LAN |
| T-059-23 | Host BG2:EE + dois clientes e worker LAN | Ausência de segunda autoridade, consistência do estado |
| T-059-24 | Benchmark latência/VRAM/CPU/qualidade entre rotas | Medições reais usadas antes de definir thresholds |

## 10. Pendências para SPECS e próximas decisões

1. DEC-006: escolha de modelos, runtimes, hardware, contexto, custos, políticas para IA remota (ainda **não autorizada por padrão**).
2. DEC-015: estratégia global de testes e aceitação por recurso.
3. DEC-060 (a discutir): validação de conteúdo gerado, confiabilidade factual, consistência com lore e critérios de revisão.
4. Métricas de qualidade por tipo de tarefa; budgets, concorrência e deadlines por benchmarks no Windows host e LAN.
5. Contratos reais de comunicação, fila, cache temporário, confidencialidade, observabilidade, testes de falhas de dispositivos e redes.
6. Prova de que nenhuma decisão narrativa aceita conduz indiretamente a escrita não autorizada no BG2:EE/EEex.

**Status final:** desenho de roteamento em Discovery, **sem** modelos selecionados, testes realizados, alterações em código ou validação BG2:EE multiplayer.


## Integração DEC-060 — validação das propostas

O roteamento aprovado na DEC-059 não constitui aprovação do conteúdo. Toda saída proposta passa pelo pipeline DEC-060 (schema, ACL, conhecimento, evidências/cronologia, quests/build, risco), e só então pode ser publicada ou encaminhada ao gateway com validação específica. Um worker mais capaz ou revisor LLM não concede autoridade factual/mecânica. Ver ADR-0055 e documento 60.

## Emenda DEC-060 — seleção temporal antes de escolher o modelo (v5.6.1)

Uma tarefa de IA com lore informa ao AI Model Router **o período/ano DR confirmado, categoria, ramo, escopo de conhecimento, ACL e finalidade**. O recuperador aplica **seleção física da partição anual** antes de montar prompt; não se permite usar conteúdo de outros anos por conveniência de performance ou fallback de modelo. Workers LAN só recebem trechos autorizados. O roteador não promove resposta de worker a fato canônico. Ver 60a e ADR-0055 (emendada).

## DEC-062 — classificação por IA é proposta isolada

O AI Model Router pode selecionar modelos autorizados para extração/classificação de fontes **apenas após rights gate e minimização de dados**. Nenhum worker pode publicar lore, escrever em partições anuais diretamente ou consultar fontes privadas sem escopo. A seleção por throughput não contorna DEC-060/061, direitos, staging e revisão humana/política LOW expressa. Fallback que perde proveniência, licença ou precisão de ano deve `DEFER/BLOCK`; sem nuvem por padrão.

## Integração DEC-063/C — roteamento vinculado ao pack (v5.9)

Requisições LLM devem vincular `campaign_id`, `branch_id`, `pack_revision`, `year_DR` e ACL. Alteração de manifesto invalida jobs de contexto anterior; modelos não aprovam migração nem reinterpretam histórico confirmado. Nó LAN apenas propõe avaliação compatível com autorização; caches/prompt seguem DEC-060/061/062 sem base global que misture anos.

## Integração DEC-064/C — aprendizado e crenças sem onisciência (v6.0)

Solicitações sobre crença NPC DEC-064/C devem ser roteadas após validação `campaign_id/branch_id/year_DR/KnowledgePack/ACL/NPC` e recebimento legítimo de evidência. Nó LAN pode formular fala/proposta contextual; não pode escrever memória, revelar segredo ou validar sua própria evidência. Resposta tardia de revisão antiga é STALE e não atualiza crença.


### Síntese e recuperação epistêmica — DEC-065/C (Discovery v6.1)

Modelos podem auxiliar a resumir episódios autorizados, mas o resumo precisa vincular fontes e revisão/ACL e passar validação DEC-060. Roteador não recebe memória privada por ser o executor mais rápido; respeitar nós autorizados e privacidade. Falha de modelo deixa a tarefa pendente ou utiliza projeção verificável, nunca inventa lembranças.

### Integração DEC-066/C — modelo não certifica identidade de NPC (v6.2)

AI Model Router pode chamar inferência para avaliar candidatos limitados, mas só um verificador baseado em evidências/host pode estabelecer `VERIFIED`. Modelos de linguagem não têm autoridade para deduzir que dois atores homônimos são uma pessoa. `AMBIGUOUS`/`STALE` => nenhum contexto privado; nenhum fallback cloud automático.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

Classificação por LLM pode sugerir saliência para DEC-067, mas router/modelo não confirmam identidade ou autorizam promoção. ACL e DEC-066/060 continuam gates.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

Roteador DEC-059 não executa LLM para NPC DORMANT por tick. Quando necessário ao catch-up DEC-068, reduzir contexto ao autorizado e classificar saída como proposta; a falta de modelo não deve forjar avanço causal.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: AI Model Router pode auxiliar redação, mas grafos de origem/destino e durações vêm de regras/evidências; execução remota não certifica realidade do motor.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070: modelos podem auxiliar a redigir propostas/rumores de viagem, não decidir resultados, classificação final, permissões ou fatos mecânicos. Resultado stale/sem fonte fica pendente.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

AI Model Router pode sugerir diálogos de encounter DEC-071 com contexto autorizado; não escolhe se engine suporta materialização, não certifica receipt e não pode resolver combate via texto. Sem modelo elegível, pendência/fallback seguro.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Model Router DEC-059 pode escolher um modelo para preencher slots de DEC-072 com listas curadas, mas o resultado continua hipótese; sem templates validados, nenhum fallback cria código/ator de engine.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Roteamento não deve enviar o vínculo factual privado quando tarefa necessita apenas do pseudônimo; fallback para modelo alternativo requer igual autorização e minimização.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação por evidências (Discovery v7.3; não implementada)

A investigação de personas DEC-076 usará ledger privado por campanha/ramo, com pistas e hipóteses revisáveis, origem/independência de fontes, contraprovas e estados inconclusivos. Suspeita ou fala LLM não confirma identidade e não permite divulgação; vínculo factual restrito exige evidências/DEC-066, e revelação exige ACL/consentimento/risk gate por audiência (DEC-019/028/041/045/046). Rumores e repercussões DEC-029/074/075 são separados de fato e punição. **Preservar `knowledge/periods/<ANO>-DR/` fisicamente por ano, sem evidências privadas no cânone.** ADR-0072/documento 77; 58 testes não executados, sem POC BG2:EE/EEex/multiplayer.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Roteador DEC-078 limita LLM local a diálogos e explicações com contexto mínimo; falta de modelo não transfere decisões jurídicas para LLM externo nem invalida regras.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

DEC-079 usa LLM local on-demand para formulações narrativas de cooperação/recusa; roteador filtra segredos antes da inferência e proíbe decisão sobre autenticidade/competência.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

LLM DEC-080 pode redigir mensagem/diálogo contextual, mas não decide validade de ordem, status legal nem competência; contexto ACL mínimo e fallback sem expor segredos.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Modelo local pode redigir petições e respostas contextuais DEC-081; regras/host decidem competência, compensações e efeitos. Filtrar PII/segredos antes da inferência.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Roteador envia apenas contexto autorizado de processos institucionais, não segredo de PC/denunciante a modelo ou nó sem permissão.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Roteador aplica minimização de fontes antes do modelo local/fallback; fallback com escopo diferente não pode tornar público segredo.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Antes de escolher LLM/fallback, aplicar política de segredos de fonte e localização; gerar somente propostas narrativas, nunca comandos de proteção/coerção.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Prompt deve receber segredo minimizado por NPC/propósito; fallback não altera autorização. Bloquear respostas que vazem info fora do contexto aprovado.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Roteador de LLM mantém necessidade de conhecimento, separa claim público de verdade secreta e aplica mesma política em fallback local/remoto; nenhum modelo gera host receipt.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Roteador local-first oferece à IA apenas informação autorizada sobre NPC/observador, e produz diálogo, nunca transição mecânica ou factual de lealdade livre.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Prompts de negociação enviam informações mínimas; fallback de modelo local/remoto não aumenta permissões nem permite aprovar acordo ou gastar recursos.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Roteador de modelos recebe dados minimizados e não pode elevar tipo de dado por fallback; regras de verificação primárias continuam determinísticas.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

LLM local ou fallback remoto, se permitido, recebe somente view pré-filtrada; nunca confiar ao modelo a decisão sobre qual segredo pode sair, nem permitir cache não controlado.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Fallback LLM só pode reformatar alternativas autorizadas; planejamento determinístico permanece funcional sem modelo e não concede permissões.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Roteador LLM fornece somente contexto filtrado para propostas de replanejamento sob demanda; fallback nunca ganha acesso extra a identidades/rotas.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

A LLM pode sugerir alternativas textuais somente sob demanda e com contexto filtrado; decisão de lease/prioridade, retry e entrega de segredo nunca são delegadas a inferência.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

LLM recebe apenas propostas já filtradas e metadados minimizados; fallback não decide preempção, abre locks, envia mutação ou anuncia recuperação concluída.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

LLM não ativa regras DEC-096 nem escolhe data/impacto; usa apenas fatos autorizados pelo filtro determinístico; DEC-095 não concede poder de refund a prompts.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Matriz DEC-096/C calcula elegibilidade sem LLM; roteamento textual recebe somente recorte temporo-espacial autorizado e não controla efeitos.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

A LLM recebe apenas composição DEC-097/C derivada de fonte e scope filtrados; não recebe diretório de ano futuro.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Cache/roteamento de modelos deve usar somente projeções já filtradas por ACL; nunca vazar instâncias/identidades de mapas privados ao LLM.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Contextos fornecidos à LLM omitem quest flags e spoilers fora do escopo; texto não confere ownership.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

LLM routing usa apenas SafeQuestProjection filtrada e evita prompt injection em strings de mods.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Catalogues by exact build/modpack/quest/script fingerprint, curated proof of semantic milestone and valid transition; an observed flag or stage is never an authorized quest write or host receipt. On patch or restore, invalidate semantic cache and avoid generic stage inference. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

A LLM não recebe flags crus nem escolhe reconciliação DEC-102; somente marcos mínimos autorizados. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **roteamento LLM**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para roteamento LLM depende de view filtrada; fallback nunca libera segredo, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para roteamento LLM somente de redação pública autorizada, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Não enviar provas PROTECTED para prompts ou provedores remotos. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Proteção de prompts evita vazamento de termos confidenciais. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
