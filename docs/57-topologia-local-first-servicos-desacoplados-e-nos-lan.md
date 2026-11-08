# DEC-057 — Topologia modular local-first e execução distribuída opcional

**Infinity AI Discovery v5.3.** Artefato técnico de Discovery para ADR-0052. **Não é SPEC nem prova de conectividade, compatibilidade do motor, robustez de IPC ou desempenho.**

## 1. Decisão e motivação

A opção **C** permite duas topologias de implantação sem mudar a semântica dos serviços, ações, memória, segurança e mundo:

- `SINGLE_HOST`: BG2:EE é hospedado no Windows; serviços Infinity AI podem rodar em processo(s) separado(s) na mesma máquina. É o **primeiro alvo de teste**.
- `LAN_OPTIONAL`: um ou mais workers — inferência local, resumos e simulação por lotes — podem rodar em máquinas LAN de confiança **explicitamente cadastradas**, com possibilidade de revogação e reconciliação. Não requer nuvem, mas acrescenta fronteira de confiança que exige proteção própria.

Serviços lógicos desacoplados não precisam equivaler a containers ou microsserviços desde o início; processo, serviço, runtime e protocolo continuam para SPECS e benchmarks. Não presumir que EEex funciona para as intervenções almejadas em multiplayer.

## 2. Diagramas de implantação candidatos

### 2.1 Máquina única (baseline)

```text
PC anfitrião — Windows (primeiro alvo)
  BG2:EE host ──[observação/ação viável e validada]── Bridge / Action Gateway
       │                                               │
       │                                         receipts / evidências
       │                                               │
       └─────── host authority ──────────────── Orquestrador Infinity AI
                                                   │
                                     ┌─────────────┼────────────┐
                                     │             │            │
                                 Regras/FSM    LLM local   Simulação em lotes
                                     │             │            │
                                     └─────────────┼────────────┘
                                                   │
                                      Memória + event log + checkpoints
                                                   │
                               RPD / World Health Monitor / backup local

BG2:EE clientes (até dois nos primeiros gates) ⇄ multiplayer nativo do jogo
```

Neste desenho, as linhas são **integrações propostas**, não APIs existentes demonstradas. O orquestrador não assume que o game host forneça save/quest flags via interface programática.

### 2.2 LAN opcional — colocação de computação

```text
PC anfitrião Windows                                  Nó LAN autorizado
  BG2:EE host                                              Worker LLM
     │                                                      Simulação/batch
  Bridge/Gateway (autoridade mecânica permanece host)          │
     │                                                        │
  Orquestrador / RPD / Monitor ←── canal autenticado* ─── contratos de job
     │                              e escopado*                │
  Memória + event log + checkpoints (padrão inicial)   retorno PROPOSTA

* Protocolo, pareamento, proteção de transporte e revogação exigem DEC-058/POCs.
* Nenhuma aresta permite escrita direta do nó LAN nas estruturas BG2:EE.
```

A transferência da camada **stateful** para um nó LAN é possibilidade futura condicionada a testes próprios; worker stateless é a primeira candidata à distribuição. A separação física não transfere controle da party, do save ou do relógio a outra máquina.

## 3. Separar função lógica de autoridade e localização

| Componente | Responsabilidade | Localização inicial sugerida | Pode ir à LAN? | Gate principal |
|---|---|---|---|---|
| BG2:EE host | Estado e resultado mecânico | PC Windows anfitrião | **Não** como worker IA; host do jogo mantém-se autoridade | DEC-011 + prova multiplayer |
| EEex/bridge (se viável) | Observar e enviar ações tipadas ao host | Mesmo PC do host | Não assumir bridge remota | DEC-003/011/012 |
| Action Gateway | Validar identidade, permissão, risco e receipts | Próximo ao host | Gateway de comando autoritativo preferencialmente junto ao host; qualquer mudança exigiria revisão e POC | DEC-012/027/034 |
| Orquestrador / World Director | Encaminhar tarefas sem efeito físico autônomo | PC anfitrião | Possível após contrato seguro; sem transferir autoridade | DEC-014/056 |
| Runtime LLM | Gerar proposta/diálogo com contexto ACL | Processo local | **Sim**, primeira candidata, somente mediante autorização explícita | DEC-006/028/058 |
| Simulação distante | Projeções determinísticas e lotes versionados | Processo local | **Sim**, mediante verificação de revisão/seed/relógio | DEC-021/022/032/056 |
| Memória + event log | Estado narrativo, provenance e revisões | Controlado pela campanha, idealmente no host no início | **Condicional**, nunca sem durabilidade/checkpoints/recovery e ACL | DEC-008/028/053/054 |
| World Health Monitor | Detectar falha por capacidade, alertar, degradar | Monitor do host; sondas por nó onde existirem | Pode receber sinais da LAN; não toma controle mecânico | DEC-055 |
| RPD | Admission control/filas/budgets por serviço | Coordenação junto ao host inicialmente | Pode aplicar orçamento lógico por nó, sem prometer scheduler OS | DEC-056 |
| Backups | Cópia de checkpoint verificado | Local + destino independente opt-in | NAS LAN possível, não equivale a mover autoridade do save | DEC-054 |

## 4. Contratos de job e retorno — candidatos, não implementados

Envelope ilustrativo, que respeita os contratos DEC-011/012/056:

```yaml
request_id: req-unique-id
campaign_id: campaign-A
mode: LIVING_WORLD
session_id: session-01
build_fingerprint: build-hash
branch_id: branch-01
input_revision: 125
authority: proposal_only
service: local_llm | sim_batch | read_only_index
node_binding: explicitly_authorized_node
risk: LOW
knowledge_scope: scoped_acl_token_or_reference
idempotency_key: job-key
world_interval: null
input_digest: hash_of_minimized_inputs
deadline_policy: bounded_or_none
```

Retorno candidato:

```yaml
request_id: req-unique-id
origin_node_id: registered_node
campaign_id: campaign-A
branch_id: branch-01
build_fingerprint: build-hash
input_revision: 125
result_status: PROPOSED | FAILED | STALE | UNKNOWN
result_schema_version: version
result_digest: hash
payload: validated_suggestion_only
```

Conceitos e sintaxe ilustrativos; **não** é um contrato de rede aprovado, implementação de autenticação ou token de sessão existente. Checagens de integridade, autenticação, autorização, capacidade do nó e freshness são independentes. Resultado `PROPOSED` não é efeito do motor, `CONFIRMED` exige receipt mecânico legítimo. Respostas tardias de branch/build antigo são descartadas do caminho ativo sem apagar auditoria.

## 5. Distribuição de trabalho, ciclo de vida e degradação

1. **Admission:** host/orquestrador identifica campanha, modo, privacidade, revisão, custo/urgência, capacidade do nó e prioridade do RPD.
2. **Minimização:** recupera somente informações ACL-compatíveis antes de qualquer inferência ou envio. Históricos privados não são broadcast entre nós ou jogadores.
3. **Despacho:** worker realiza cálculo/proposta de maneira isolada, sem acesso ao gateway mutativo, credenciais de administrador ou saves da campanha por padrão.
4. **Recebimento:** validar identidade, revisão/epoch, digest, schema, proveniência e risco, ignorando resultado se obsoleto ou originado em nó não autorizado.
5. **Commit de mundo:** somente regras/serviços autorizados validam fatos; qualquer alteração mecânica requer o gateway e confirmação BG2:EE host (DEC-011/012).
6. **Falha:** timeout/queda de worker cria `FAILED` ou `UNKNOWN` para cálculo sem efeito; comando já enviado ao host com receipt ausente fica `UNCERTAIN` até reconciliação, sem replay cego.
7. **Retomada:** reatribuir tarefas puramente descartáveis apenas se a idempotência, input_revision e escopo continuarem válidos; não failover automático de estado narrativo primário.
8. **Monitoramento:** registrar apenas metadados mínimos de operação, latências e status; não armazenar ou transmitir prompts segredos em telemetria.

## 6. Identidade da sessão e limites de segurança

- Cada nó inicia **sem confiança**; proximidade na LAN não equivale a autorização. Descoberta automática, se houver, **não** pode conceder permissões.
- Anfitrião decide quais nós podem servir quais campanhas e quais capacidades; revogação deve cancelar trabalho futuro e invalidar permissões, preservando recibos/auditoria.
- Binding de endereço/IP não basta: requer prova de identidade do serviço, sessão, escopo e autorização. Mecanismo concreto a escolher na DEC-058.
- Expor endpoint LAN é opt-in; modo máquina única não precisa abrir portas na rede externa. Proibir acesso público por padrão.
- Tráfego de narrativas inclui informações potencialmente secretas; desenho deverá proteger confidencialidade e integridade em trânsito, inclusive na LAN. Detalhes criptográficos e pareamento pendentes.
- Não alterar política de uso de nuvem, servidores externos, SaaS ou LLM remoto apenas por existir opção LAN: DEC-006 continua aberta.
- O nó LAN não deve receber a chave de criptografia dos backups nem acesso root a arquivos de save, salvo política e POC futura específicos.

## 7. Operação e persistência em topologia distribuída

O `campaign_id` está vinculado a um host e manifesto de execução por sessão, sem equivaler ao identificador de jogador conectado. O banco de dados narrativo e o save mecânico continuam atrelados a checkpoints coordenados DEC-053: não criamos dois escritores independentes nem presumimos commits distribuídos atômicos. Se memória estiver em outro nó futuramente, indisponibilidade do banco bloqueia mutações dependentes e exige restabelecer coerência antes de reabrir o gateway.

Troca de nó de processamento não altera tempo do mundo (DEC-022), decisões HIGH (DEC-034), versão de mods (DEC-052), escopo de segredo (DEC-028), agência de jogadores (DEC-041/046) ou regra de PvP (DEC-042). O backup remoto independente autorizado da DEC-054 é **cópia**, não nova autoridade de campanha.

## 8. Riscos específicos a medir

| Risco | Consequência possível | Proteção candidata |
|---|---|---|
| Latência LAN | Conversa interrompida/timeout | Budget do RPD e fallback validado, sem inventar diálogo |
| Nó malicioso/desatualizado | Payload adulterado, dados vazados | Identidade, escopo, autenticação, schema/freshness, permissão restrita |
| Partição de rede | Jobs sem resposta/estado incerto | Fail-closed de capacidade; sem election de host; reconciliação |
| Reprocessamento tardio | Evento/quest duplicado | Input revision, idempotência e watermark |
| Segundo escritor de DB | Corrupção/branch divergente | Um proprietário lógico do event log, checkpoint coordenado |
| Desalinhamento de build | Quest/estado incompatível | Fingerprint e isolamento por campanha |
| Dados privados no nó LAN | Vazamento de segredos de PC | Recuperação seletiva antes do envio, minimização e ACL |
| Competições por GPU | Queda de FPS/tick do host | Processamento LAN opt-in, budgets medidos, limite por nó |
| Falha silenciosa | Resultado antigo tratado como vigente | World Health Monitor, deadlines e estados UNKNOWN |
| Exposição da rede | Acesso indevido ao serviço | Sem portas públicas por default; pareamento/segurança DEC-058 |

## 9. Plano candidato de POCs — 24 ensaios, ainda não executados

1. Executar BG2:EE Windows limpo sem serviços extras e medir baseline de gameplay.
2. Observar o host em sidecar somente leitura, sem alteração mecânica.
3. Rodar orquestrador local e retornar proposta não mutativa válida.
4. Rodar LLM local com timeouts sem bloquear jogo/host.
5. Executar batches distantes locais com pausa/retomada idempotente.
6. Verificar nenhuma interação com a campanha Original ao iniciar Living World.
7. Registrar dois clientes e comparar estados durante gameplay/saves.
8. Executar worker stateless em um PC LAN autorizado com conteúdo sintético, sem abrir portas internet.
9. Rejeitar nó desconhecido que tente responder a job ou conectar-se.
10. Recusar payload de outra campanha, modo, branch ou build.
11. Recusar payload de revisão antiga após rewind de save.
12. Recusar resposta que não segue schema validado e registrar erro sem executar ação.
13. Desconectar LAN antes do envio de tarefa e verificar fallback apenas validado.
14. Desconectar LAN após despacho e antes do retorno e verificar status do job.
15. Derrubar worker após retorno parcial sem publicar novo estado mecânico.
16. Repetir retorno do mesmo job e garantir ausência de efeitos/recompensas duplicados.
17. Confirmar que um nó LAN não possui acesso ao gateway mutativo/saves sem autorização.
18. Testar ACL seletivo: segredo privado não incluído em tarefa de NPC sem conhecimento.
19. Testar workers sob CPU/GPU/VRAM saturadas e comparar filas/latência/FPS.
20. Forçar falha de sonda ou monitor e expor `UNKNOWN`, não HEALTHY.
21. Executar checkpoint e backup durante indisponibilidade do worker LAN.
22. Ensaiar estado narrativo em rede (somente ambiente descartável) e fail-close de perda do banco.
23. Restaurar baseline isolado após falha, conferindo host e dois clientes.
24. Verificar que troca de nó não altera relógio, event log, risco HIGH ou versão dos mods.

Os testes exigem critérios de aceitação instrumentados e avaliação específica de versão/hardware na fase de SPECS. **Nenhuma compatibilidade real foi demonstrada nesta fase.**

## 10. Pendências e próxima decisão

- **DEC-058 (próxima):** como parear, identificar, autorizar e proteger os canais entre host e nó LAN (sem presumir confiança pela rede física).
- **DEC-006:** modelos, VRAM, CPU e consentimento para serviços LLM externos.
- **DEC-013/015:** matriz real de versões e gates mínimos para EEex/bridge/multiplayer.
- **DEC-018:** operação e privacidade dos logs/alertas na topologia escolhida.
- **SPECS:** escolha de protocolo, formato final de envelope, hardware mínimo, portas, runtime, processo Windows, perfis de tolerância, metas de latência e testes de segurança.

## DEC-058 — Fronteira de confiança e pareamento da distribuição LAN (v5.4)

A DEC-058 aprova descoberta assistida como sinal **não confiável**, confirmação de identidade e aprovação do anfitrião, canal protegido e autorização de mínimo privilégio para trabalhadores LAN. Cada job deve checar a época atual de autorização e identidade do canal, além dos invariantes `campaign_id/mode/build_fingerprint/branch_id/input_revision`. Worker retorna **proposta**, nunca efeito mecânico; ACL e minimização de contexto acontecem **antes** de transmitir. Revogação impede novos despachos/aceitação de retornos obsoletos, mas não desfaz dados já recebidos. Nenhuma implementação de protocolo/pareamento foi validada; consultar ADR-0053 e documento 58. Princípio de `SINGLE_HOST` permanece sem dependência de LAN.

## DEC-059 — Seleção entre host e nó LAN autorizado

AI Model Router é agnóstico à localização: executa single-host normalmente e usa nó LAN **opcional**, já pareado/ativo, somente para cálculo. Contextos filtrados por ACL e work requests revision-bound; worker não grava no motor/saves, não obtém segredos fora do escopo nem substitui autoridade do host. Quedas permitem fallback seguro ou pendência, nunca failover mecânico com `UNCERTAIN`. Documentos ADR-0054/doc. 59; comportamento ainda não testado.

### Integração DEC-066/C — serviço de identidade sob autoridade do host (v6.2)

Workers LAN opcionais podem sugerir correspondências de NPC com dados mínimos e permitidos; confirmação usa evidências e revisão do host/serviço de campanha. Um nó não mantém autoridade para ligar identidades, consultar segredos ou reaplicar resultados após mudança de branch, build ou pareamento.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

Jobs offscreen DEC-068 podem ser roteados a nó autorizado conforme DEC-057/058/059, mas IA remota não materializa NPC nem confirma estado mecânico. Resultados só são aceitos com branch/epoch/ACL, identidade e revisão compatíveis.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: worker LAN de planejamento entrega propostas de rota vinculadas à revisão e ACL; não publica presença mecânica, não conhece segredos não autorizados e não substitui o host.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Worker de LAN pode propor variante de encontro DEC-071, mas o coordenador da campanha/host é o único a gerenciar reserva e confirmação mecânica; tráfego autenticado/ACL e fencing impedem nós não autorizados de resolver evento.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Workers LAN podem auxiliar avaliação de template DEC-072, mas não distribuir assets com direitos restritos, acionar gateway nem declarar encontro materializado no BG2:EE.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Módulos distribuídos devem receber somente persona/contexto permitido. Mapas privados persona→ator não se propagam a nós sem papel e autorização explícitos.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Worker LAN pode auxiliar difusão de pedidos DEC-079 só com ACL e pareamento; não ganha competência jurídica ou mecânica, e nunca confirma ação no host.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Workers LAN DEC-080 podem transportar mensagens permitidas mas não mudar estado autoritativo nem autorizar captura; fencing/ACL e revogação da conexão prevalecem.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Workers remotos podem auxiliar análise de documentos DEC-081 apenas com ACL mínima, sem direito de devolver itens, julgar culpa ou acessar segredos de PCs.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Worker LAN pode auxiliar avaliação de provas minimizadas, mas não recebe autoridade judicial/mecânica nem segredos de denunciantes sem ACL.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Nós LAN recebem somente extratos autorizados; não distribuir identity map nem depoimento integral por padrão a serviços auxiliares.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Nó LAN não tem acesso universal a dados de proteção, identidade e rota; contexto mínimo com ACL de finalidade, revision e branch.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Nós LAN têm apenas campos mínimos por função; cache e logs não replicam automaticamente ProtectedPlanTruth para todos os serviços.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Distribuição LAN só fornece claim plantado ao serviço autorizado; proteção de rota verdadeira fica com nó/role apropriado, com correlação de campaign/branch.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Nós LAN não recebem mapas privados de compromissos sem role, escopo de campanha e finalidade; minimizar dados enviados a modelos.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Serviço LAN não recebe contratos de terceiros por padrão; só campos conforme job/role/campanha, e revogação de acesso invalida jobs em trânsito.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Serviços locais trocam apenas claims/evidence autorizados por campanha e purpose; a fonte real não precisa viajar ao worker para uma análise de resumo.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Payload da view destinado a um nó LAN não pode conter dados de outra audiência. O host de dados privados não entrega o dossiê bruto por conveniência.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Worker LAN somente recebe versão autorizada do plano; autoridade de execução reside no host/gateway.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Nos serviços LAN, um nó de planejamento não adquire autoridade de mutação sobre o host; mensagens e revisões levam ACL e idempotência.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Scheduler e workers LAN usam uma autoridade de reserva por campaign/branch com fencing; nó lento não retoma mutação após perda de epoch, nem recebe segredos sem ACL.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Workers LAN atrasados com epoch/fence obsoletos não podem arbitrar ou liberar leases; revogação de nó não demonstra fim de ação host em voo.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-096/C — Discovery v9.2

Não transmitir ruleset completo com segredos/cronologia futura em LAN DEC-096/C; aplicar host authority, pins, ACL e idempotência de eventos.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Trilhas e targets DEC-097/C continuam isolados por campanha/branch/epoch, não devem vazar lore futuro entre clientes LAN.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Canais LAN não aceitam observações mecânicas de clientes como confirmação host e não transportam dados privados de região sem ACL.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Serviços LAN read-only/write têm capacidades distintas; nenhum nó cliente autentica owner ou receipt global.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Canal de rede seguro transporta apenas projeção autorizada, nunca dump bruto de quests.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** DEC-101 interpretation is read-only, version-pinned and independent of gateway/host execution. A confirmed semantic milestone does not authorize actions or prove a command receipt; mod upgrades, checkpoint restore, revised mapping, epoch mismatch or contradictory states cause fail-closed reconciliation. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Cache e filas de reconciliação DEC-102 são segregados por campanha/branch/build/epoch, sem vazamento em LAN. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **confidencialidade**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para serviços locais de correção, entrega e crença separados por autoridade, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para serviços locais separados de avaliação, prova e execução, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Sessões LAN não compartilham automaticamente contratos privados. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Mensagens LAN não são automaticamente contratos committed. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
