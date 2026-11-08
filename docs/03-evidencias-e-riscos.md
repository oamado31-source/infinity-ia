# Evidências técnicas e riscos — linha de base

**Versão:** 0.1. Pesquisado em 2026-11-05. Estado técnico não substitui teste local.

## Evidências verificadas documentalmente

| Componente | O que a documentação confirma | O que NÃO foi comprovado | Referência |
|---|---|---|---|
| EET | Reúne a saga BG em BG2:EE, áreas descobertas acessíveis, compatibilidade modding | Funcionamento de IA dinâmica e sincronização de novas ações no multiplayer | https://github.com/Gibberlings3/EET |
| IWD1_EET | Repositório de integração e ordem de instalação envolvendo EET, IWD2_EET e NWNForBG | Estabilidade da combinação completa na máquina-alvo | https://github.com/The-Gate-Project/IWD1_EET |
| NWNForBG | Adaptação de história e cenários de NWN, com componentes para BG2EE/EET | Mundo aberto contínuo e multiplayer de todas as áreas | https://github.com/abalabokhin/NWNForBG |
| EEex | Extende recursos da Infinity Engine; compatibilidade e suporte dependem de versão e SO | Que todas as APIs e mods funcionem simultaneamente no multiplayer | https://github.com/Bubb13/EEex |
| EEex Remote Console | Execução de comandos Lua e respostas JSON via IPC local, testes em BG2EE | Multiplayer, todas as versões EEex, segurança contra código arbitrário | https://github.com/Chrizhermann/eeex-remote-console |

## Alerta crítico de compatibilidade

EEex documenta suporte a motores 2.7 com versões >=1.1.0 e a motores 2.6 com versões >=0.9.0-alpha, enquanto o README atual de EEex Remote Console descreve compatibilidade confirmada por teste com EEex 0.11.0-alpha e compatibilidade apenas verificada no código com 1.0.x; **não afirmar compatibilidade automática entre quaisquer versões recentes**. Fazer matriz real antes de instalar.

EEex informa melhor suporte no Windows; Linux por Proton/Wine é parcial e macOS por CrossOver é limitado. Isso é uma restrição arquitetural a confirmar com o usuário.

## Riscos principais

- **R-001 — Instabilidade em mods combinados:** instalar incrementalmente em cópias imutáveis, guardar logs de instalação, criar testes de smoke e rollback.
- **R-002 — Manipulação insegura do processo:** Remote Console aceita Lua arbitrário com privilégios do jogo. Expor apenas ações pré-definidas, validar entradas e restringir acesso a diretórios/comandos.
- **R-003 — Assincronismo multiplayer:** ações que funcionam em single-player podem não sincronizar entre clientes; validar antes de especificar eventos avançados.
- **R-004 — Diálogo em tempo real:** console pode suspender polling em diálogos forçados; planejar experiência alternativa ou restrição.
- **R-005 — Integridade narrativa:** IA pode inventar fatos contraditórios; memória estruturada e regras de canon, sem alteração não validada de estado.
- **R-006 — Compatibilidade de saves:** mudanças em strings/recursos de mods podem quebrar referências; versionamento de pacotes e saves.
- **R-007 — Latência/custo IA:** chamadas por evento, cache e regras determinísticas para combate/rotinas simples; definir orçamento depois.
- **R-008 — Licenciamento/recursos:** uso pessoal não concede automaticamente permissão para redistribuir assets proprietários; apenas mods e instalações legítimas conforme suas licenças.

## Gates de experimentação futuros (não executados)

- POC-01: abrir BG2:EE versão fixada com EEex e efetuar um comando de leitura inofensivo via Remote Console.
- POC-02: comando controlado de spawn offline em área isolada, com backup e registro.
- POC-03: repetir ação em multiplayer com 2 clientes e provar sincronização do estado.
- POC-04: diálogo/entrada de texto e persistência externa que sobreviva a restart.
- POC-05: EET e expansões instaladas incrementalmente, com matriz de regressões.

**Regra:** POC-03 é bloqueante para especificar eventos dinâmicos multiplayer como capacidade pronta.


## Atualização de riscos — DEC-049 (Discovery v4.5)

- **R-POST-001 — Duplicidade de NPC:** estado projetado offscreen conflita com instância física em área, personagem recrutado ou script nativo. Reconciliar `npc_id`, área, party e confirmação host antes de propor aparição.
- **R-POST-002 — Modificações indevidas de roteiros:** alterar localização, quests, banters ou romance de NPC canônico pode quebrar a progressão original. Inventariar recursos/scripts por build e restringir ações a hooks testados; aprofundar DEC-050.
- **R-POST-003 — Simulação além da capacidade:** evitar modelagem individual permanente e LLM por tick; usar níveis de atividade, regras versionadas, checkpoint e limites de catch-up.
- **R-POST-004 — Metaconhecimento e cronologia:** difusão de rumores ou previsão de destino não equivale a observação nem fato do motor; filtrar memória, época e fontes antes de narrar.
- **R-POST-005 — Recrutamento inseguro:** convite verbal não confirma party join; testar slots, diálogos, scripts, flags, 2 clientes, save/load e rollback/fallback sem replay cego.
- **R-POST-006 — Mudanças irreversíveis remotas:** morte, prisão e mudanças históricas de NPC importante exigem regras, níveis de risco e autorização especial; não presumir execução física offscreen.

**Evidência nova:** a opção B é uma decisão do projeto, não evidência de suporte a movimentação fora da party ou reencontro automatizado no BG2:EE/EEex. Nenhum experimento foi executado nesta versão.

## Atualização de riscos — DEC-050 (Discovery v4.6)

- **R-SCRIPT-001 — Estado nativo não observado:** inventário de recursos não comprova flag atual. Para mutação, `UNKNOWN` deve produzir bloqueio/revisão; nunca assumir valor a partir de texto gerado.
- **R-SCRIPT-002 — Quebra de quests ou romances:** deslocar companheiro, mudar diálogos/flags ou etapas pode causar softlock. Reconciliador com reservas/precondições verificadas, regressões de quests e fallback sem mutação.
- **R-SCRIPT-003 — Builds/mods divergentes:** versão e ordem de instalação alteram scripts e dependências. Fingerprint e invalidação automática das garantias anteriores; inventário curado por build.
- **R-SCRIPT-004 — Instância/narrativa duplicada:** vida offscreen e scripts originais podem reivindicar mesmo NPC. Controlar identidade, party-state, área e host revision antes de reencontro.
- **R-SCRIPT-005 — Inconsistência multiplayer/save:** alteração aparente em um cliente não prova estado do host/outros clientes. Exigir receipts, pós-condição e testes de 2 clientes, save/load e reconexão.
- **R-SCRIPT-006 — Divergência histórica acidental:** texto dinâmico pode antecipar/falsificar a cronologia. Verificar época, causalidade e política HIGH/cânone; sem branch mecânica testada, manter apenas hipótese.
- **R-SCRIPT-007 — IA altera consentimento ou segredos:** não utilizar geração para afirmar confissão, romance, autoria de ações ou conhecimento não obtido. ACL anterior ao modelo e checagem de publicação.
- **R-SCRIPT-008 — Replay/timeout:** operação `UNCERTAIN` não pode ser reexecutada automaticamente; reconciliar snapshots/receipts e usar idempotência.

**Natureza da evidência:** a DEC-050 é política arquitetural aprovada, não demonstração de introspecção de flags, alteração segura de romances ou instalação de mods. Testes do documento técnico 50 seguem candidatos.

## DEC-051 — Novos riscos de inventário híbrido por build (Discovery v4.7)

- **R-INV-001 — Cobertura parcial mascarada:** scanner ignora formato, arquivo ou condição, e o sistema conclui falsamente que não há conflito. Exigir métricas de cobertura e estados `UNKNOWN`/`CONFLICTED` com preflight conservador.
- **R-INV-002 — Fingerprint desatualizado:** jogo, override ou ordem dos mods muda depois do inventário. Invalidar evidências afetadas e bloquear ações até recaptura e regressão por build.
- **R-INV-003 — Proveniência ambígua:** recursos alterados/sobrescritos por diferentes mods, aliases, TLK ou scripts sem vínculo inequívoco. Curadoria com evidência, resolução de conflitos e logs; não inventar autor ou versão.
- **R-INV-004 — Confusão recurso vs runtime:** presença de recurso não revela flag de quest, romance ativo ou disponibilidade de NPC. Runtime requer observação separada, host revision e POC read-only.
- **R-INV-005 — Ferramenta altera instalação:** extrator não validado escreve caches, normaliza arquivos ou toca saves. Testar read-only em cópia isolada e observar diffs antes/depois.
- **R-INV-006 — Vazamento/licenciamento:** manifests e depurações contêm texto proprietário, caminhos privados ou saves. Redução de dados, controle de acesso, hashes/refs quando suficientes; sem redistribuição inadvertida.
- **R-INV-007 — Desalinhamento de clientes:** manifestos do host e clientes diferem; não alegar sincronização de recurso/estado até teste em dois clientes.

**Evidência:** DEC-051 registra política aprovada, não comprova execução de WeiDU/Near Infinity, extração de flags ou suporte em EEex/BG2:EE multiplayer. Gates e 20 testes candidatos estão no documento 51.

## DEC-052 — Riscos de migração de builds e continuidade (Discovery v4.8)

- **R-MIG-001 — Atualização destrutiva:** sobrescrever a instalação/save de produção causa perda de baseline. Preparar candidato isolado e manter fingerprint/backup verificável.
- **R-MIG-002 — Save abre, mas não progride:** carga bem-sucedida não assegura quests, romances, scripts ou NPCs funcionais. Gates de regressão além do load.
- **R-MIG-003 — Mod removido/reordenado:** IDs/scripts/recursos podem ficar ausentes ou incompatíveis. Tratar como risco crítico e bloquear sem migração específica comprovada.
- **R-MIG-004 — Backup incoerente:** save do host e narrativa externa divergem. Validar vínculo de checkpoint e ensaiar restauração completa; DEC-053 detalhará coordenação.
- **R-MIG-005 — Duplo processamento:** replay pós-migração reaplica recompensas/eventos. Usar watermarks, idempotência e reconciliação `UNCERTAIN`.
- **R-MIG-006 — Multiplayer dessincronizado:** clientes com builds diferentes ou estado não equivalente. Testes em dois clientes e parada segura até alinhamento.
- **R-MIG-007 — Confiança indevida no inventário:** diff read-only não comprova estado runtime ou compatibilidade mecânica. Desconhecido bloqueia promoção.
- **R-MIG-008 — Ausência de aprovação:** testes aprovados não autorizam atualização automática. Obter permissão explícita do anfitrião para promoção.
- **R-MIG-009 — Licenças e privacidade:** backup/manifests podem revelar segredos, caminhos ou ativos proprietários. Restringir acesso/redistribuição e reduzir dados.
- **R-MIG-010 — Rollback ilusório:** desinstalar mod não devolve necessariamente flags/quest ou banco narrativo. Restaurar conjunto de origem provado, com trilha de auditoria.

**Estado das evidências:** DEC-052 é uma política aprovada, não comprovação de migrador, rollback transacional, snapshots coerentes, compatibilidade de EET/NWNForBG nem de comandos de runtime EEex em multiplayer. Vinte cenários estão propostos no documento técnico 52.

## DEC-053 — Riscos de checkpoint e recuperação de duas fontes (Discovery v4.9)

- **R-CP-001 — Falsa atomicidade:** cópia do save e do banco externo não é uma transação comum demonstrada. Exigir par íntegro publicado e bloqueio de candidato parcial.
- **R-CP-002 — Save e log de épocas diferentes:** timestamps iguais não asseguram coerência; usar build/campanha/modo/branch, hash, revisões e watermark verificados.
- **R-CP-003 — Replay duplo:** ações `UNCERTAIN` com efeito já aplicado podem duplicar recompensas ou mortes. Idempotência, recibos e reconciliação antes de retry.
- **R-CP-004 — Rewind com conhecimento futuro:** restauração de save antigo pode expor segredos e fatos ainda não ocorridos. Isolamento de ramificação e ACL.
- **R-CP-005 — Corrupção/backup incompleto:** hash de uma metade falha. Não promover; restaurar conjunto coerente anterior validado.
- **R-CP-006 — Multiplayer divergente:** client disconnect/save/load não prova equivalência. Gates com host e dois clientes.
- **R-CP-007 — Flags/quests não observáveis:** integridade do arquivo não certifica comportamento do motor. Não declarar recuperação técnica sem POC e progressão testada.
- **R-CP-008 — Segredos em arquivos de backup:** snapshots, manifests e logs podem conter informação privada. Escopos de acesso, retenção governada e minimização.
- **R-CP-009 — Linha de recuperação sem auditoria:** apagamento de registros confirmados destrói causalidade. Preservar eventos originais em ramo arquivado e histórico da intervenção.
- **R-CP-010 — Reentrada durante operação crítica:** novo comando enquanto se captura checkpoint pode invalidar consistência. Gate de quiescência demonstrado ou bloqueio conservador.

**Estado:** DEC-053 aprovada como política; não há prova de API de save do BG2:EE, captura atômica, recuperação operacional ou compatibilidade EEex multiplayer. Vinte e quatro cenários candidatos estão no documento 53. DEC-018/054 detalharão a operação.


## DEC-054 — Riscos de backups e restaurabilidade (Discovery v5.0)

- **R-BKP-001 — Backup parcial promovido:** somente pares `PUBLISHED` da DEC-053, com catálogo de dependências e verificação de cópia, podem ser considerados candidatos válidos.
- **R-BKP-002 — Mesma falha física:** cópias no mesmo disco não fornecem redundância independente; sinalizar proteção local apenas e oferecer segundo destino opt-in.
- **R-BKP-003 — Erro de retenção:** limpeza destrói a última cópia funcional ou backup pinado pré-migração. Validar pins/referências antes de remover; falhar por falta de espaço.
- **R-BKP-004 — Integridade falsa como prova de restore:** checksum é necessário, não suficiente para save/quest progredir. Ensaios isolados por build e multiplayer exigidos antes de declarar recuperabilidade.
- **R-BKP-005 — Exfiltração de segredos:** snapshots e históricos podem conter dados privados; acesso por ACL, minimização de logs, criptografia em remoto e adesão explícita a qualquer destino externo.
- **R-BKP-006 — Chave de criptografia irrecuperável:** validar custódia de chave e método de recuperação autorizado; não prometer reverter perda de senha/chave.
- **R-BKP-007 — Destino desconectado / backup silenciosamente falho:** monitorar age/status das cópias, expor `DEGRADED` e falhas, sem relatório otimista.
- **R-BKP-008 — Mistura de build/modo/ramo:** manifesto inclui `campaign_id`, build, modo, epoch e watermark; proibir merge de metades de origens distintas.
- **R-BKP-009 — Reprocessamento em restore:** ação `UNCERTAIN` não recebe retry cego nem duplica recompensas, morte ou alteração de quest.
- **R-BKP-010 — Restauração que altera dados ativos:** ensaio em ambiente separado; produção só com autorização e preservação da situação anterior quando possível.
- **R-BKP-011 — Ransomware/overwrite:** segunda cópia independente, proteção contra sobrescrita, mínimo privilégio e mídia isolada quando suportado; não há imunidade universal.
- **R-BKP-012 — RPO/RTO não medidos:** não prometer perda/tempo máximo de recuperação sem testes reais e capacidade de captura BG2:EE comprovada.

**Evidência:** política DEC-054 aprovada e 28 testes candidatos no documento 54; nenhum sistema de backup, captura automática do motor ou teste de restore multiplayer foi executado. DEC-018 permanece aberta para observabilidade e resposta a incidentes (DEC-055 proposta).

## DEC-055 — Riscos de observabilidade e resposta a incidentes (Discovery v5.1)

- **R-OBS-001 — Falso estado saudável:** heartbeat/processo ativo não equivale a save narrativo e mecânico consistente; sonda ausente é `UNKNOWN`.
- **R-OBS-002 — Autorreparação destrutiva:** restart/retry de comando mecânico `UNCERTAIN` duplica efeitos; gateway deve conter mutações e reconciliar receipts.
- **R-OBS-003 — Modo degradado inseguro:** seguir sessão sem DB/bridge pode deixar fatos contraditórios; continuar apenas com capacidade demonstrada no build.
- **R-OBS-004 — Pausa inexistente:** supor controle programático da sessão multiplayer e perder estado; testar antes de anunciar pausa/recovery automático.
- **R-OBS-005 — Falha silenciosa de backup:** recuperar indicador de última cópia verificada e ensaio, não afirmar proteção por tentativa iniciada.
- **R-OBS-006 — Vazamento em logs/alertas:** secrets/ACL DEC-028, prompts, caminhos privados e narrativas não autorizadas; redigir, minimizar e isolar por campanha.
- **R-OBS-007 — Alert fatigue/restart loops:** flapping sem histerese, backoff e limites; medir na SPEC, preservar prioridade de alertas críticos.
- **R-OBS-008 — Monitor deixa de observar:** falha de sonda ou do próprio monitor indica `UNKNOWN`; não falsificar HEALTHY por ausência de alarmes.
- **R-OBS-009 — Desync entre host e clientes:** a recuperação de um serviço não prova consenso de sessão; host+2 clientes em POCs.
- **R-OBS-010 — Upload não autorizado:** telemetria externa somente com consentimento; nenhum dado de backup/LLM enviado por padrão.
- **R-OBS-011 — Impacto de desempenho do monitor:** medições excessivas competem por CPU/RAM/I/O; orçamento e prioridades na futura DEC-056.
- **R-OBS-012 — Falha de identidade:** observação de outro branch/build/modo/campanha aplicada ao atual; vincular fingerprints e escopos.

**Evidência:** aprovação arquitetural DEC-055; 28 testes candidatos documentados em doc. 55. Não há métricas reais, sondas verificadas, fallback implementado ou testes host+2 clientes. DEC-018 permanece aberta.

## DEC-056 — Riscos e evidências pendentes do Resource & Performance Director (Discovery v5.2)

- **R-PERF-001 — Contenção de recursos:** LLM CPU/GPU e workers podem degradar jogo, host e clientes; medir baseline e cargas mistas.
- **R-PERF-002 — Prioridade ilusória:** níveis P0–P4 são internos ao Infinity AI, sem evidência de prioridade real no scheduler do BG2:EE.
- **R-PERF-003 — Métrica não observável:** FPS, GPU/VRAM e latência de confirmação podem faltar; `UNKNOWN` em vez de inferência otimista.
- **R-PERF-004 — Starvation/filas infinitas:** adiar DISTANT indefinidamente pode deixar projeções atrasadas; fairness limitado e alerta, não avanço forçado.
- **R-PERF-005 — Causalidade e cronologia:** lote tardio com input obsoleto pode duplicar evento; versionar intervalo de mundo, revisão, seed e watermark.
- **R-PERF-006 — Cancelamento de ação não descartável:** interrupção após dispatch sem receipt exige `UNCERTAIN`; preservar evidência e gateway.
- **R-PERF-007 — Fallback inventado:** resposta LLM expirada não autoriza reescrever diálogo, salvar flag ou produzir evento de quest.
- **R-PERF-008 — Backpressure em I/O crítico:** limitar disco indiscriminadamente pode falhar checkpoint/backup; isolamento e POCs.
- **R-PERF-009 — Cache sem ACL:** pré-geração e conteúdo por personagem podem vazar segredos ou misturar campanhas/branches.
- **R-PERF-010 — Métricas invasivas:** monitor sob carga consome os próprios recursos que mede; instrumentação amostrada e benchmark.
- **R-PERF-011 — Variabilidade de hardware:** quotas de VRAM/memória, timeslicing de LLM e latências dependem da plataforma/DEC-006 e não podem ser inferidas sem teste.
- **R-PERF-012 — Topologia não definida:** competir com o host no mesmo PC versus nó LAN altera latência, ACL e ponto de falha; resolver DEC-057 sem introduzir novo host autoritativo.

**Evidências ainda inexistentes:** métricas reais BG2:EE Windows host + dois clientes, controle de processos, API de sondas, overhead de LLM, compatibilidade de captura de estado, impacto de backlog e resultados de ensaios de degradação. Nenhuma validação técnica foi realizada nesta decisão.

## DEC-057 — Riscos de topologia e execução em LAN (Discovery v5.3)

- **R-TOPO-001 — Autoridade dividida indevidamente:** nó remoto tenta alterar estado mecânico sem host; somente proposta, gateway e recibo real.
- **R-TOPO-002 — Rede LAN presumida segura:** nó desconhecido ou falso aceita tarefas e recebe segredos; pareamento/autenticação e canais protegidos a decidir na DEC-058.
- **R-TOPO-003 — Divisão de estado narrativo:** banco ou event log com escritores simultâneos em nós distintos causaria inconsistência; owner lógico único, checkpoint DEC-053 e gates extras para DB remota.
- **R-TOPO-004 — Partições / duplicação:** timeout de worker não determina execução de mutação; não reexecutar comandos `UNCERTAIN` sem receipt.
- **R-TOPO-005 — Privacidade do jogador:** histórico/segredo pode vazar para nó LAN ou logs; minimização ACL antes do dispatch e telemetria estritamente limitada.
- **R-TOPO-006 — Performance contraditória:** transferência para LAN economiza GPU local, mas aumenta latência; avaliar cargas reais host+2 clientes antes de prometer ganho.
- **R-TOPO-007 — Dependência de segundo computador:** proteger modo `SINGLE_HOST` e fallback sem internet; hardware de teste ainda não caracterizado.
- **R-TOPO-008 — Distorção da cronologia:** lotes devolvidos atrasados após rewind/migração podem atualizar mundo incorreto; branch, build e revision obrigatórios.
- **R-TOPO-009 — Incompatibilidade Windows/nó:** runtime/OS/protocolo real de LAN ainda não definido; não prometer suporte multiplataforma.
- **R-TOPO-010 — Exposição à internet:** service binding amplo/NAT/port forwarding podem divulgar contexto; não abrir portas públicas por padrão, gateway de entrada sujeito a DEC-058.
- **R-TOPO-011 — Observabilidade de nó enganosa:** heartbeat não prova resultados confirmados nem save/quest íntegro; Health Monitor com status `UNKNOWN` e revisão.
- **R-TOPO-012 — Recovery automático incorreto:** reposicionar DB/gateway ou eleger outro host sem prova rompe segurança; fail-close com revisão de operador.

**Evidências ausentes:** suporte real de bridge/EEex à instrumentação multiplayer, medições LAN/CPU/GPU/latência, identificação de nós, canais autenticados, privacidade em trânsito, migração de memória distribuída e testes de reconexão. Nenhuma POC executada. Ver ADR-0052/documento 57.

## DEC-058 — Evidências e riscos de identidade e segurança LAN (Discovery v5.4)

- **R-LAN-001 — Descoberta não autenticada:** um nó falsificado anuncia serviço; mitigar mantendo descoberta em estado `DISCOVERED_UNTRUSTED` sem jobs/contexto.
- **R-LAN-002 — Pareamento com dispositivo impostor:** verificar identidade por mecanismo robusto e aprovação explícita do anfitrião; código fora de banda e protocolo para SPECS.
- **R-LAN-003 — Interceptação/adulteração de tráfego:** exigir canal autenticado e protegido, rejeitar downgrade para transporte não protegido; nenhuma biblioteca foi selecionada ou testada.
- **R-LAN-004 — Acesso excessivo:** worker de LLM recebe save, secret de PC, log ou token administrativo; escopo mínimo, recuperação/ACL pré-envio, isolamento Original/Living World.
- **R-LAN-005 — Revogação tardia:** resultado pendente aceito após perda de autorização; usar estado de nó, `permission_epoch`, revisão/branch/build e validação na aceitação. Revogar não apaga dados anteriormente recebidos.
- **R-LAN-006 — Replay, spoof e chave substituída:** rejeitar origem não autenticada, job de versão obsoleta, identidade nova sem revalidação; alertar/quarentenar.
- **R-LAN-007 — Nó previamente confiável comprometido:** não confiar em saídas de modelo como comandos; protocolo protegido não garante integridade do próprio worker. Proteger gateway e revisar threat model.
- **R-LAN-008 — Exposição inadvertida à WAN:** binding e firewall devem ser verificados; LAN-only não é prova de inacessibilidade pública; portas públicas desligadas por padrão.
- **R-LAN-009 — Partition/failover indevido:** queda de nó não autoriza eleição de host, repetição de operações `UNCERTAIN`, ou efeitos offscreen; modo degradado da DEC-055.
- **R-LAN-010 — Privacidade operacional:** prompts, logs, caches e diagnósticos contendo segredos ou chaves; redigir e testar minimização/retention por escopo.

**Estado da evidência:** DEC-058/ADR-0053 aprovam o **desenho**, com 26 testes candidatos no documento 58. **Zero prova executada** de segurança do transporte, identidade de nó, assinatura de resultados, desempenho LAN ou integração EEex/BG2:EE multiplayer. DEC-006/013/015/018 seguem abertas.

## DEC-059 — Riscos do roteamento de IA entre modelos e nós (v5.5)

- **R-MODEL-001 — Privacidade e seleção:** a classificação errada do job pode transmitir histórico secreto a nó fora do escopo. Mitigação candidata: ACL restritiva **antes** de materializar prompt, avaliações negativas e mínimo privilégio.
- **R-MODEL-002 — Capacidades não comprovadas:** modelo rápido e pequeno pode não seguir limites de conhecimento ou não lidar com lore complexo. Mitigação candidata: critérios de capacidade por tarefa, testes e falha fechada.
- **R-MODEL-003 — Injeção/prompt adversarial:** saída de worker ou texto recuperado pode pedir comando ou alterar fatos. Mitigação: schema, políticas, gateway tipado e proibição de ação direta pelo modelo.
- **R-MODEL-004 — Resposta tardia/revogação:** resultados de outro ramo, checkpoint, build ou `permission_epoch` podem contaminar estado. Mitigação: binding de job/revisão e invalidação.
- **R-MODEL-005 — Fallback indevido:** falha de GPU/rede poderia provocar upload para internet ou downgrade de segurança. Mitigação: sem fallback cloud implícito, só destinos igualmente elegíveis.
- **R-MODEL-006 — Custo/latência e saturação:** chamadas excessivas ou revisões por IA congestionam jogo/LLM. Mitigação: regras primeiro, RPD e benchmarks.
- **R-MODEL-007 — Logs/cache:** rastros de prompt e contexto confidencial em worker podem persistir. Mitigação: retenção minimizada e isolamento de campanha/worker; revogação não apaga dados já recebidos.
- **R-MODEL-008 — Inconsistência textual:** respostas bem formatadas podem ser factualmente falsas, quebrar cânone ou atribuir agência a PC. Mitigação: validação de conteúdo (DEC-060 proposta) e DEC-015.

**Evidência:** a DEC-059/ADR-0054 e doc. 59 são escolhas arquiteturais com 24 **testes propostos, não executados**; não há POC de modelos, inferência distribuída ou integração multiplayer.


## Riscos DEC-060 — qualidade e fidelidade das saídas de IA

- **Alucinação factual/temporal:** falas podem antecipar eventos, inventar organizações ou contradizer fontes. Mitigar por proveniência, cronologia DR e estado do ramo, com rejeição/deferimento quando faltar evidência.
- **Vazamento de segredos:** verificar ACL antes do prompt e da publicação; não tratar memória global como conhecimento de NPC.
- **Confiança excessiva no avaliador LLM:** julgamentos de segundo modelo são auxiliares e falíveis; invariantes são determinísticas.
- **Falhas e latência:** timeout não libera proposta; medir regressão, falsos positivos/negativos e custo em SPECS/DEC-015.
- **Limite:** nenhum verificador ou taxa de qualidade foi testado; DEC-061 tratará conflitos entre fontes.

## Riscos da emenda DEC-060 — diretórios anuais de lore (v5.6.1)

- **R-TIME-01 — Contaminação entre anos:** busca unificada pode revelar/fazer NPC afirmar como presente fato de ano futuro. Mitigação: recuperação física primária por ano DR confirmado e deny-by-default para busca transversal.
- **R-TIME-02 — Perda de continuidade:** leitura exclusiva da pasta anual pode apagar antecedentes ainda vigentes. Mitigação: histórico anterior acessado explicitamente com metadados de validade e referências, sem copiar fatos sem controle.
- **R-TIME-03 — Onisciência do NPC:** pastas não substituem conhecimento adquirido, comunicação ou ACL. Mitigação: filtro pré-prompt do destinatário, tempo de aprendizagem e difusão.
- **R-TIME-04 — Mistura com ramo divergente:** campanha que alterou facção não pode reescrever fonte histórica nem contaminar outra campanha. Mitigação: overlay separado por campanha/ramo/ano e revisão, com receipts/snapshots.
- **R-TIME-05 — Integridade e performance:** diretórios/índices incompletos, caches obsoletos e buscas históricas custosas. Mitigação: manifesto/versões, invalidar caches por ano/revisão/ACL, benchmarks e falha segura.
- **Evidência:** apenas **estrutura de pastas vazias e documentação** foram produzidas. Nenhuma pesquisa de lore, importação, recuperação, implementação, POC ou teste multiplayer foi realizado.

## Riscos novos — DEC-061: proveniência e conflitos no mesmo período (Discovery v5.7)

- **R-SRC-01 — Consolidação inventada:** duas fontes contraditórias geram falsa terceira versão pela IA. Mitigação: preservar `Claim` individuais, `ConflictSet` e status `UNRESOLVED`; LLM não homologa resoluções.
- **R-SRC-02 — Supremacia editorial falsa:** fonte mais recente é tomada como automaticamente verdadeira num ano DR antigo. Mitigação: separar data editorial/edição de validade e data in-world; curadoria contextual explícita.
- **R-SRC-03 — Falso conflito:** duas lideranças em subperíodos distintos do mesmo ano são tratadas como simultâneas. Mitigação: `valid_from/valid_to`, precisão e identidade da entidade antes do confronto.
- **R-SRC-04 — Vazamento entre partições:** índice misturado permite ao NPC saber em 1369 fatos posteriores. Mitigação: conservar **diretórios físicos anuais** DEC-060, recuperar antes do prompt e buscar antecedentes somente com autorização.
- **R-SRC-05 — Opinião promovida a verdade:** rumor ou narrador não confiável convertido em fato. Mitigação: `epistemic_status`, atribuição explícita, ACL/rumor DEC-028/029 e verificador DEC-060.
- **R-SRC-06 — Curadoria muda campanha confirmada:** alteração do corpus reescreve história de ramo sem consentimento. Mitigação: fontes canônicas versionadas, overlays separados, checkpoints e autorização/reconciliação antes de promover mudanças de estado.
- **R-SRC-07 — Licença ou segredos violados:** importação de material proprietário/restrito para outro pacote, log ou worker LAN. Mitigação: fontes mínimas, resumos originais, controle de uso e minimização pré-modelo.
- **R-SRC-08 — Falsa cobertura do lore:** pastas vazias e status de curadoria são confundidos com catálogo completo. Mitigação: manifests `EMPTY/PARTIAL/UNKNOWN`, falha segura e testes de gaps.
- **Evidência:** somente política escrita e estrutura física documental do v5.6.1. Nenhuma obra importada, resolução de conflito aplicada ou POC/benchmark de busca executado.

## Riscos e evidências DEC-062 — pipeline híbrido de ingestão (Discovery v5.8)

- **R-ING-01 — Datas alucinadas:** IA classifica cronologia por edição/data editorial em vez de DR. Mitigação: validador temporal e `UNKNOWN → NEEDS_REVIEW`, sem escrita no ano suposto.
- **R-ING-02 — Mistura física de períodos:** índice único ou escrita cruzada mistura 1369/1370. Mitigação: diretórios anuais reais DEC-060, manifestos independentes e restrição pré-consulta.
- **R-ING-03 — Consenso fictício:** extração sintetiza duas fontes concorrentes. Mitigação: preservar Claims e ConflictSets DEC-061 e revisão audível.
- **R-ING-04 — Injeção de prompt ou parser:** obra maliciosa tenta executar comandos, alterar ACL ou publicar fatos. Mitigação: quarentena, dados delimitados, parser restrito, Action Gateway, nenhuma ferramenta mutativa ao LLM.
- **R-ING-05 — Uso/redistribuição indevida:** privado não implica licença; texto proprietário ou assets entram no ZIP/workers. Mitigação: rights gate, vault privado, metadados/resumos próprios e escopo explícito.
- **R-ING-06 — Aprovação automática indevida:** modelo homologa suas próprias extrações; risco HIGH/UNCERTAIN é publicado. Mitigação: revisão humana para fatos novos, política LOW limitada e auditável após testes; fail-closed.
- **R-ING-07 — Publicação parcial/duplicada:** crash ou retry expõe versão parcial/duplicatas. Mitigação: staging, hash/idempotência, validação, manifestos versionados e rollback editorial.
- **R-ING-08 — Retcon de campanha:** nova fonte sobrescreve eventos confirmados ou ramos separados. Mitigação: conhecimento base somente-leitura durante gameplay, overlays isolados; DEC-063 definirá revisão por campanha.
- **R-ING-09 — Acesso de NPC/worker acima do necessário:** índice/staging vaza segredo ou fonte restrita. Mitigação: ACL antes do prompt, fonte privada, autorização LAN e índices temporais segregados.
- **R-ING-10 — Falsa cobertura:** andaimes com pastas vazias parecem enciclopédia pronta. Mitigação: `EMPTY/PARTIAL/REVIEWED` e pendências rastreadas.
- **Evidência atual:** apenas DEC-062/C registrada por ADR e desenho de 30 testes. Sem obras importadas, direitos específicos auditados, parser, banco indexado, execução de revisão ou POC de BG2:EE/EEex/multiplayer.

## Riscos e evidências DEC-063 — Knowledge Packs por campanha (Discovery v5.9)

- **R-KP-01 — Retcon silencioso:** revisão publicada sobrepõe diálogos, mortes, quests ou eventos já confirmados. **Mitigação:** pin, diff semântico, overlay causal e host gating.
- **R-KP-02 — Mistura temporal:** migrador consulta todos os anos ou considera fato de 1370 consumado em 1369. **Mitigação:** manifesto só de referências, acesso nas **pastas anuais físicas** DEC-060 e intervalo de vigência.
- **R-KP-03 — Perda de proveniência:** claims conflitantes são sintetizados em consenso. **Mitigação:** preservar registros e decisões DEC-061, bloqueio `UNRESOLVED`.
- **R-KP-04 — Staging contaminando campanhas:** fonte ainda não aprovada da DEC-062 é tratada como fato. **Mitigação:** somente revisões anuais publicadas são elegíveis.
- **R-KP-05 — Atualização parcial:** falha/crash revela pack B sem checkpoint ou índice coerente. **Mitigação:** preparo isolado, commit lógico auditável, *last-known-good*, reconcile e POCs.
- **R-KP-06 — Rollback destrutivo:** reversão apaga fatos posteriores confirmados pelo host. **Mitigação:** recuperar ramo/checkpoint causalmente compatível, sem replay cego.
- **R-KP-07 — Cache e jobs stale:** modelo LAN usa conteúdo de pacote anterior ou outro ramo. **Mitigação:** revision-bound jobs, ACL, epoch, validação de output e revogação.
- **R-KP-08 — NPC onisciente:** atualização de informação curada altera automaticamente crenças privadas. **Mitigação:** separar canon de memória e propagação; DEC-064 aberta.
- **R-KP-09 — Incompatibilidade com build:** novo fato pressupõe quest/script/mod não observado em BG2:EE. **Mitigação:** check de manifesto da instalação DEC-051/052 e gates DEC-050/053.
- **R-KP-10 — Retenção insuficiente/licenças:** pack antigo é removido enquanto um save o referencia; materiais protegidos vazam em backups/log. **Mitigação:** pins de retenção, backups e metadados mínimos com direitos.
- **Evidência atual:** opção C documentada no ADR-0058 e doc. 63, **32 testes futuros**. Não há versionador/upgrade real, diffs executados, verificação de checkpoint mecânico, integração LAN ou multiplayer BG2:EE/EEex comprovados.

## Riscos e evidências DEC-064 — memória epistêmica individual (Discovery v6.0)

- **R-NPCB-01 — NPC onisciente:** atualização de Knowledge Pack é confundida com descoberta pessoal. Mitigação: aquisição por evento/propagação legítimos, separação de binding e experiência.
- **R-NPCB-02 — Rumor tratado como fato:** crença subjetiva vira cânone. Mitigação: tipos epistêmicos, provenance, validação DEC-060, não promover `REPORT/BELIEF`.
- **R-NPCB-03 — Retcon da memória:** revisão apaga diálogos ou episódios históricos. Mitigação: append de crença versionada, preservação de eventos/causalidade.
- **R-NPCB-04 — Segredo vazado:** lore/perfil privado incluído indevidamente em prompt/worker. Mitigação: ACL antes de recuperar DEC-028, classificação, minimização, revogação.
- **R-NPCB-05 — Mistura de anos DR:** usar 1370 como fato consumado em 1369. Mitigação: **diretórios físicos anuais** DEC-060, vigência e relógio confirmado.
- **R-NPCB-06 — Fonte não curada/conflictada:** dado em staging DEC-062 ou conflito DEC-061 vira prova. Mitigação: only published/current pack, estados `UNRESOLVED` e curadoria.
- **R-NPCB-07 — Transmissão inverossímil:** fama/segredo difundido sem contato, tempo ou canal. Mitigação: roteamento social, relógio e limites DEC-029/021/022.
- **R-NPCB-08 — Atualização duplicada/stale:** retry/job LAN da revisão antiga produz crença nova. Mitigação: idempotência, revisions/epoch/ACL, reconciliação `UNCERTAIN`.
- **R-NPCB-09 — Consequência mecânica indevida:** crença nova altera diretamente reputação, alinhamento, quest ou combate. Mitigação: gates DEC-011/012/030/035–037, recibo do host.
- **R-NPCB-10 — Crescimento de memória/performance:** episódios por NPC tornam inviável execução. Mitigação: budgets DEC-056 e futura DEC-065 de retenção; não LLM por tick.
- **Evidência:** escolha C registrada no ADR-0059 e doc. 64, **30 testes candidatos NÃO EXECUTADOS**. Não há protótipo de memória, POC de BG2:EE/EEex/multiplayer, medição de latência ou importação de lore neste pacote.


## Riscos e evidências DEC-065 — memória de longa duração (Discovery v6.1)

- **R-NPCM-01 — Amnésia por decaimento temporal:** promessa/crise antiga é excluída do contexto e do histórico. Mitigação: âncoras verificáveis e separação entre recuperação e retenção.
- **R-NPCM-02 — Alucinação de síntese:** resumo cria testemunho, fato ou certeza não existente. Mitigação: vínculos a eventos/versões e verificador DEC-060, rejeitar sem fonte.
- **R-NPCM-03 — Exfiltração de segredo em busca/caches:** classificação crítica é exposta a quem não tem ACL. Mitigação: controle antes da indexação/recuperação, minimização/ACL e revogação.
- **R-NPCM-04 — Mistura de ano DR:** resumo consulta informações de épocas futuras como fatos presentes. Mitigação: **partições físicas anuais DEC-060**, vigência, relógio e Knowledge Pack DEC-063.
- **R-NPCM-05 — Memória de NPC incorreto:** homônimos, clones, IDs temporários ou mods causam atribuição errada. Mitigação: identidade lógica, DETECT/DEFER; DEC-066 pendente.
- **R-NPCM-06 — Stale/duplicado:** job ou restore aplica síntese de outro branch/revisão. Mitigação: idempotência, comparação de revisões, invalidação e checkpoint DEC-053/054.
- **R-NPCM-07 — Sobrecarga:** indexação e sínteses concorrem com combate/multiplayer. Mitigação: batch, quotas e backpressure DEC-056; não LLM por tick.
- **R-NPCM-08 — Retenção indevida:** âncora crítica impede exclusão/redação de dado pessoal legitimamente exigida. Mitigação: política de privacidade/retention com tombstone minimizada quando aplicável, sem supor retenção eterna.
- **R-NPCM-09 — Resumo vira autoridade:** memória subjetiva altera quest, reputação, alinhamento ou cânone. Mitigação: separação epistêmica DEC-064, gateway/host, curadoria DEC-061/062.
- **R-NPCM-10 — Âncoras infinitas:** tudo classificado como crítico causa crescimento descontrolado. Mitigação: critérios auditáveis, revisão de proteção, SPECS de capacidade e benchmarking.
- **Evidência:** decisão C do idealizador registrada no ADR-0060, documento 65 e **32 testes candidatos NÃO EXECUTADOS**. Nenhuma prova de EEex/memória NPC, compatibilidade BG2:EE/multiplayer, latência, capacidade de storage ou privacidade operacional foi realizada.

## Riscos e evidências pendentes — DEC-066/C (Discovery v6.2)

- **R-ID-01 — Homônimos e NPCs genéricos:** nome/portrait/área iguais causam associação errada. Mitigar exigindo identidade lógica, evidências e estado `AMBIGUOUS`.
- **R-ID-02 — ID nativo reciclado:** spawn ou load reutiliza handle temporário. Mitigar tratando IDs como indícios versionados, não chave de pessoa.
- **R-ID-03 — Duplicatas e clones scriptados:** instâncias simultâneas herdam incorretamente memória. Mitigar com exclusão mútua, evidências e revisão.
- **R-ID-04 — Mudança de build/mod:** CRE/script/flags mudam e invalidam correspondência. Mitigar fingerprint/reconciliação DEC-051/052.
- **R-ID-05 — Replay/branch leakage:** memória pós-fork ou posterior ao checkpoint migra a outro ramo. Mitigar checkpoints/revisions/lineage e idempotência DEC-053/054.
- **R-ID-06 — Segredos expostos por falso reconhecimento:** `VERIFIED` sem ACL ou candidato incerto usado no prompt. Mitigar ACL antes de busca e revalidação na publicação DEC-028/064/065.
- **R-ID-07 — Falha de worker LAN:** resposta tardia confirma identidade obsoleta. Mitigar epochs/expiry e autoridade do host DEC-057/058/059.
- **R-ID-08 — Correção destrutiva:** merge/split elimina histórico confirmado. Mitigar trilha, revisão por risco, checkpoint e sem retcon automático.
- **R-ID-09 — Ausência de hooks:** motor não oferece identificação estável suficiente. Mitigar POC read-only, retorno limitado/`DEFER`, não prometer suporte.
- **R-ID-10 — Custos de rastrear milhares de NPCs:** busca cresce e afeta FPS. Mitigar scheduler DEC-056, índices/limites em SPECS e seleção futura DEC-067.
- **Evidência disponível:** apenas escolha arquitetural DEC-066/C e desenhos de contratos; **34 testes candidatos NÃO EXECUTADOS**. Estabilidade de identidades nativas, suporte multiplayer, latência, scripts, mods e precisão de correspondência não foram medidos.

## Riscos e evidências pendentes — DEC-067/C (Discovery v6.3)

- **R-IND-01 — Promoção de NPC errado:** NPC genérico homônimo, handle/CRE reciclado. Mitigar com DEC-066 `VERIFIED` e fail-closed.
- **R-IND-02 — Inflação de população:** dupla representação em agregado e indivíduo; exigir reconciliação e chave idempotente.
- **R-IND-03 — Inflação de custo computacional:** promover em massa após diálogos triviais, estourando CPU/GPU/memória; saliência contextual, quotas e RPD DEC-056, benchmarks pendentes.
- **R-IND-04 — Biografia alucinada:** LLM inventa infância/segredos/contatos para completar figurante; negar escrita factual sem evento/fonte comprovada.
- **R-IND-05 — Vazamento de segredo:** memória privada atribuída a spawn parecido, NPC não autorizado ou worker LAN; ACL antes da busca, identidade verificada e isolamento de ramo.
- **R-IND-06 — Quebra de scripts nativos:** promoção confunde entidade narrativa com CRE/quest/romance e tenta alterar motor; proibir mutação implícita, aplicar gateway/receipts.
- **R-IND-07 — Retcon na retomada:** fatos posteriores a restore/fork aparecem no NPC; validar checkpoint, branch/epoch, versão de build e KPack.
- **R-IND-08 — NPC duplicado em multiplayer:** clientes veem instâncias distintas e criam promoções concorrentes; host autoritativo, event idempotente e POC com dois clientes.
- **R-IND-09 — Operações pendentes em overload:** adiar promoção sem apagar evento confirmado; fila durável e retry seguro.
- **R-IND-10 — Desindividualização indevida:** evento crítico é descartado quando NPC sai de cena; retenção protegida DEC-065 e política DEC-068 pendente.
- **Evidência disponível:** escolha C registrada e 36 testes candidatos ainda não executados. Não existem provas de suporte a NPC genérico persistente, hooks, IDs estáveis, desempenho ou compatibilidade multiplayer BG2:EE/EEex.


## Riscos e evidências pendentes — DEC-068/C (Discovery v6.4)

- **R-OFF-01 — Dormência apaga relação:** NPC perde promessa/memória/identidade ao sair de cena. Mitigação: atividade separada de identidade e episódios DEC-064–067; snapshots e anchors.
- **R-OFF-02 — Teleporte físico narrativo:** simulação distante pressupõe chegada ou spawn mecânico sem host. Mitigação: estado `NOT_OBSERVED/UNKNOWN`, evento proposto e POC; continuidade de viagem será DEC-069.
- **R-OFF-03 — Relógio inflado:** tempo em fila, ausência real ou worker indisponível são convertidos em anos DR. Mitigação: DEC-022 e cursor por intervalo autorizado; catch-up delimitado.
- **R-OFF-04 — Biografia retroinventada:** IA descreve cinco anos de experiências sem eventos. Mitigação: regras/evidências confirmadas, controle da DEC-060 e recusa de inventar testemunho.
- **R-OFF-05 — Efeitos irreversíveis inventados:** morte, romance, casamento, descendência, recrutamento ou quests alterados fora de cena. Mitigação: gates HIGH, host receipts, consentimento e scripts compatíveis.
- **R-OFF-06 — Replay / stale após save ou fork:** job tardio pertence ao futuro/ramo diferente. Mitigação: epoch, build, branch, checkpoint, KPack, idempotência e fail-closed.
- **R-OFF-07 — Identidade errada:** respawn/nomes duplicados herdam memórias após reativação. Mitigação: DEC-066 `VERIFIED`, `AMBIGUOUS` mantém resposta genérica.
- **R-OFF-08 — Inflação de população:** NPC promovido reaparece no agregado e no individual. Mitigação: transições e reconciliação idempotente DEC-067.
- **R-OFF-09 — Vazamento de segredos:** catch-up ou worker LAN acessa história privada sem ACL. Mitigação: filtros antes de modelos/filas/cache DEC-028/057–059.
- **R-OFF-10 — Backlog descontrolado:** anos DISTANT competem com combate/host. Mitigação: RPD DEC-056, quotas e métricas, sem inventar eventos por não processar.
- **R-OFF-11 — Divergência nativa:** script/romance/party mudou sem reconhecimento do sistema. Mitigação: inventário DEC-050/051, host receipt e reconciliação POC; sem mutação implícita.
- **R-OFF-12 — Falsa alegação de capacidade:** desenho é apresentado como NPC fora de cena rodando em engine/multiplayer. Mitigação: declarar DEC-068 como arquitetura não implementada, 36 testes candidatos não executados.
- **Evidência real nesta etapa:** escolha C e documentação técnica produzida. Nenhuma POC executada, nenhum benchmark FPS/CPU/latência, nem recurso de movimento, save ou NPC offscreen verificado em BG2:EE/EEex.

## Riscos e evidências pendentes — DEC-069/C (Discovery v6.5)

- **R-TRAVEL-01 — Teleporte narrativo:** cena remota aparece instantaneamente. Mitigar por grafo temporal e estados, sem materialização implícita.
- **R-TRAVEL-02 — Mundo não roteável:** LLM inventa estrada, porto, conexão ou velocidade. Mitigar por fontes/curadoria, `UNKNOWN/UNROUTABLE` e partição anual DR DEC-060.
- **R-TRAVEL-03 — Onipresença:** NPC em duas áreas ao mesmo tempo. Mitigar por presença mecânica reconciliada, host, epoch, identidade DEC-066 e branch.
- **R-TRAVEL-04 — Confusão lore/engine:** região canônica não possui mapa jogável. Mitigar por `lore_region != engine_area`, build inventariada e fallback narrativo sem spawn.
- **R-TRAVEL-05 — Relógio divergente:** tempo real ou fila vira semanas DR. Mitigar DEC-022, intervalos autorizados e cursores idempotentes.
- **R-TRAVEL-06 — Rota obsoleta:** guerra/bloqueio só aparece depois, mas planejamento velho segue como certeza. Mitigar diff, revisão de grafo, evento confirmado e replanejamento transparente.
- **R-TRAVEL-07 — Resultado stale após save/fork/migração:** viagens de outra revisão aparecem como atuais. Mitigar epoch/checkpoint/branch/build/KPack e fail-closed.
- **R-TRAVEL-08 — Efeito HIGH fora de cena:** morte/ataque/romance/quest confirmados só por plano. Mitigar DEC-027/034/050, revisão, consentimento e Action Gateway.
- **R-TRAVEL-09 — Segredo de rota:** itinerários privados vazam para nó LAN. Mitigar ACL, mínimo contexto e cache segmentado.
- **R-TRAVEL-10 — Dupla contagem/população:** NPC viajante pertence a dois agregados ou clones. Mitigar DEC-067, transições idempotentes e identidade verificada.
- **R-TRAVEL-11 — Incompatibilidade com scripts nativos:** teleporte/spawn conflita com quests ou companions. Mitigar DEC-050/051, read-only POC, ações offline e host+2 clientes.
- **R-TRAVEL-12 — Alegação tecnológica indevida:** design de rota é apresentado como pathfinding e viagens funcionais no multiplayer. Mitigar declarar desenho não implementado e 40 testes candidatos não executados.
- **Evidência real:** escolha expressa DEC-069/C, artefatos documentais e integridade do ZIP; **nenhuma POC executada** para BG2:EE/EEex/EET/multiplayer ou benchmarks de distância/tempo.

## Riscos e evidências pendentes — DEC-070/C (Discovery v6.6)

- **R-TRV-01 — Perigo tratado como acontecimento:** Separar perigos/contexto/boatos de fatos confirmados; `PROPOSED` não é `COMMITTED`.
- **R-TRV-02 — Morte ou saque automático offscreen:** HIGH fail-closed, autorização e receipt host para efeitos mecânicos.
- **R-TRV-03 — Risco fragmentado em LOW:** Classificar impacto cumulativo, não somente cada fala/evento isolado.
- **R-TRV-04 — Evento deslocado no tempo/rota:** Segment_id, clock, epoch, revisão KPack e verificação do grafo temporal.
- **R-TRV-05 — Acúmulo e replay de efeitos:** Idempotency_key, filas limitadas, checkpoints, revalidação e deduplicação por branch.
- **R-TRV-06 — NPC errado recebe consequência:** NPCIdentity VERIFIED DEC-066; ambiguidade impede associação e commit.
- **R-TRV-07 — Host incomunicável ou estado UNCERTAIN:** Não repetir spawn/ataque; reconciliação e fail-closed.
- **R-TRV-08 — Conteúdo original ou mod incompatível:** Matriz de build/recursos, scripts nativos e POCs escalonadas.
- **R-TRV-09 — Rumor gera impacto econômico indevido:** Distinguir rumor e evento factual; não gerar bloqueio ou saque sem evidência.
- **R-TRV-10 — Segredos vazados a worker LAN:** Contexto mínimo e ACL/pareamento DEC-057–059; revogação invalida proposta.
- **R-TRV-11 — Conflito com evento local futuro:** Pendência de DEC-071: trava de exclusão entre resolução offscreen e encounter jogável.
- **R-TRV-12 — Resultados falsamente atribuídos a BG2:EE:** Declarar ausência de POCs/benchmarks; sem recibo não há fato mecânico.

**Evidência disponível:** escolha C expressa em 2026-11-06, 44 testes candidatos, nenhum executado; nenhum resultado de engine/multiplayer validado. DEC-060–069 mantidas.

## DEC-071 — Riscos de transferência de incidentes offscreen para encontros locais (Discovery v6.7)

- **R-HANDOFF-01 — Dupla resolução da mesma emboscada:** reserva durável `incident_id` + revisão/fencing antes de abrir encontro; resolver apenas uma vez.
- **R-HANDOFF-02 — Área/capability inexistente na build:** inventário DEC-051 e POC da interface efetiva; fallback narrativo/pendente.
- **R-HANDOFF-03 — NPC duplicado ou homônimo:** DEC-066 e observação verificada; nunca gerar uma instância porque o nome coincide.
- **R-HANDOFF-04 — Falha pós-operação e retry mecânico:** `UNCERTAIN` + reconciliação de receipt, não retry cego.
- **R-HANDOFF-05 — Quest/romance/script nativo corrompido:** isolar e revisar pelo DEC-050; fail-closed no conflito.
- **R-HANDOFF-06 — Cliente multiplayer confirma resultado sozinho:** autoridade do host DEC-011 e receipts autenticados.
- **R-HANDOFF-07 — Falta de consentimento/risco HIGH:** bloquear e solicitar autorização específica DEC-027/034/041/046.
- **R-HANDOFF-08 — Ramo, checkpoint ou Knowledge Pack defasado:** revalidação e descarte de proposta stale antes de qualquer commit.
- **R-HANDOFF-09 — Segredo vazado por LLM/worker LAN:** ACL pré-inferência, pareamento autorizado e auditoria com redação.
- **R-HANDOFF-10 — Release de lock por timeout com comando em voo:** fencing + estado UNCERTAIN e bloqueio offscreen até prova.
- **R-HANDOFF-11 — Evento canônico confundido com encontro mecânico:** manter DEC-060–063, overlays e gates; nenhuma escrita no cânone.
- **R-HANDOFF-12 — Recursos insuficientes / backlog:** priorização DEC-056; narrativa/pendência sem fingir conclusão.

**Evidência observada:** somente a aprovação humana da DEC-071/C e a inspeção documental do Discovery. **Não existem POCs de spawn, encounter, EEex/multiplayer ou testes T071 executados.**

## DEC-072 — Riscos do catálogo e composição de encontros por build (Discovery v6.8)

- **R-COMP-01 — Asset presente confundido com capability de engine:** matriz por função/build, evidência POC e `UNKNOWN` fail-closed.
- **R-COMP-02 — Incompatibilidade de mod/ordem de carga:** fingerprints, hashes de overrides, dependências e revisão após migração.
- **R-COMP-03 — Área inexistente, script indisponível ou quest em conflito:** gates DEC-050/051 e fallback narrativo.
- **R-COMP-04 — Código LLM, Lua ou criação runtime arbitrária:** allowlist de componentes e gateway tipado; nenhuma execução livre.
- **R-COMP-05 — Spawn duplicado ou NPC homônimo:** DEC-066 identity verified e presença observada pelo host.
- **R-COMP-06 — Direitos autorais/licença de assets:** proveniência e restrições DEC-017; pacote offline não autoriza redistribuição por si só.
- **R-COMP-07 — Handoff duplicado e efeito mecânico incerto:** manter ledger DEC-071, CAS/fencing e host receipt, `UNCERTAIN` sem retry.
- **R-COMP-08 — Cliente multiplayer com build divergente:** gate host+dois clientes por build e versões imutáveis.
- **R-COMP-09 — Classificação de risco incompleta:** risco cumulativo, DEC-027/034/070, HIGH default-deny.
- **R-COMP-10 — Contaminação entre anos/campanhas:** DEC-060 partição física anual, DEC-063 manifest pinado, overlay por ramo e ACL.
- **R-COMP-11 — Hot patch de template em save ativo:** revisions imutáveis, staging offline, checkpoint/rollback comprovado.
- **R-COMP-12 — Degradação enganosa:** sem suporte ficar PENDING/narrativo, jamais inventar NPC, combate ou loot.

**Evidência existente:** exclusivamente a escolha humana da DEC-072/C e a revisão documental. **48 testes candidatos não executados; nenhum adapter, template executável, mod/EEex/multiplayer verificado.**

## DEC-073 — Riscos de persistência e limpeza pós-encontro (Discovery v6.9)

- **R-CLEAN-01 — Remoção de conteúdo nativo/terceiro:** negar cleanup para `NATIVE_OR_MOD` e ownership não comprovado; permissão por instância, não CRE/template.
- **R-CLEAN-02 — Item legítimo apagado após loot:** rastrear transferência comprovada e invalidar propriedade antiga do encounter.
- **R-CLEAN-03 — NPC errado ou duplicado:** identidade DEC-066, prova de instância, bloqueio de homônimo e origem incerta.
- **R-CLEAN-04 — Falso cleanup por narração:** comando/receipt host tipado e capability validada por build; não inferir engine.
- **R-CLEAN-05 — Dupla resolução e recompensas repetidas:** ledger DEC-071, fencing, revisão monotônica e idempotência.
- **R-CLEAN-06 — Destruição após timeout:** `UNCERTAIN` e reconciliação antes de qualquer novo efeito, nunca retry cego.
- **R-CLEAN-07 — Save/load ou restore com mundo divergente:** reobservar host e checkpoint/branch, não aplicar futuro a ramo restaurado.
- **R-CLEAN-08 — Script/quest/romance corrompido:** preservar nativo/mod; DEC-050/051 e provas de compatibilidade por build.
- **R-CLEAN-09 — Jogador ausente perde item/posse:** host, consentimento e gating por risco; sem exclusão implícita.
- **R-CLEAN-10 — Apagar memória junto ao recurso:** separar ciclo físico de registro narrativo persistente e identidade NPC.
- **R-CLEAN-11 — Vazamento de segredos em auditoria/worker LAN:** ACL, contexto mínimo e redação; workers não removem engine.
- **R-CLEAN-12 — Pendências de limpeza crescentes:** quotas e observabilidade DEC-055/056, sem releases prematuros nem falsa conclusão.
- **R-CLEAN-13 — Confundir o corpus anual com o estado do encontro:** DEC-060–063, overlays por campanha e catálogo operacional isolado.
- **R-CLEAN-14 — Efeito global indevido:** DEC-029/030/032/033 exigem propagação causal; não universalizar rumores/reputação em DEC-073.

**Evidência:** escolha C do idealizador; 50 testes candidatos **NÃO EXECUTADOS**. Não há POC de adapters de cleanup, BG2:EE/EEex/multiplayer; riscos seguem abertos até SPECS/testes.


## Riscos e evidências pendentes — DEC-074/C (Discovery v7.0)

- **R-074-01 / Onisciência social:** todos os NPCs/facções tomam conhecimento de encontro distante ao ler estado global. Mitigar com `ObservationReport`, canais, ACL, relógio e prova de recepção.
- **R-074-02 / Duplicação de efeitos:** várias testemunhas, retries e save/load multiplicam confiança, recompensas ou resultados econômicos. Mitigar com ledger causal idempotente e `resolution_epoch`.
- **R-074-03 / Contágio de boato falso:** rumor vira verdade canônica ou causa alteração de quest/motor. Separar `claim`, belief e evento confirmado; bloquear efeitos mecânicos sem receipt do host.
- **R-074-04 / Desproporção:** repercussões locais provocam guerras, colapso econômico ou mudanças HIGH através de múltiplos LOW. Somar impacto, impor gates DEC-027/034/032 e revisão de especialistas.
- **R-074-05 / Causalidade temporal:** notícia percorre anos/regiões sem percurso validado, atravessa FROZEN ou mistura 1369 com 1370 DR. Fixar pack/branch/ano e difusão DEC-022/029.
- **R-074-06 / Vazamento de segredo:** mensagens/LLM/logs revelam informações de PCs ou NPCs indevidas. Filtragem ACL antes da chamada, segregação por campanha, telemetria desativada por padrão.
- **R-074-07 / Conflito host/cliente:** worker ou cliente cria efeito mecânico sem engine. Exigir gateway e receipt host validado, fail-closed.
- **Evidência:** aprovação do idealizador e documentação técnica; **52 testes não executados**. Nenhum benchmark, adapter, validação host+dois clientes ou integração real de propagação demonstrada.

## DEC-075/C — Riscos e evidências pendentes (Discovery v7.1)

- **R-ATTR-01 — Crédito inventado:** evento coletivo ou fala gerada vira contribuição individual sem prova; aceitar `UNKNOWN`.
- **R-ATTR-02 — Culpa indevida de ausentes:** responsabilização automática por pertencer à party; verificar autoria, presença e consentimento.
- **R-ATTR-03 — Dono confundido com controlador:** delegação temporária altera identidade/autoria ficcional; armazenar campos separados.
- **R-ATTR-04 — Onisciência testemunhal:** NPC adquire conhecimento do ledger privado sem ver/receber relato; ACL, percepção e proveniência.
- **R-ATTR-05 — Fama de autor errado:** rumor incorreto sobrescreve autoria factual; separar `WitnessAccount` e `ConfirmedEvent`.
- **R-ATTR-06 — Recompensa duplicada:** quatro contribuições geram quatro resultados; deduplicação por evento, ator, regra e categoria.
- **R-ATTR-07 — Mudança mecânica indevida:** mérito narrativo vira XP, loot, alignment, quest ou reputação de engine; exigir host/gateway/POC.
- **R-ATTR-08 — Exposição de segredo ou pseudônimo:** auditoria privada vaza para NPC, cliente ou worker; ACL antes de LLM e logs mínimos.
- **R-ATTR-09 — Save divergente:** branch/epoch/build antigos aplicam crédito futuro; revisão, fencing e reconciliação.
- **R-ATTR-10 — Viés contra suporte:** privilegiar dano e ignorar cura/defesa/negociação por falta de telemetria; taxonomia inclusiva, sem inventar prova.
- **R-ATTR-11 — Disputa apagada:** retificação sobrescreve relato anterior sem trilha; conservar revisões e proveniência.
- **R-ATTR-12 — Dependência de hook inexistente:** declarar granularidade de combate sem EEex/bridge verificados; bloquear claims até POC.
- **Evidência:** apenas escolha arquitetural do usuário e arquivos documentais. **54 testes candidatos não executados**. Compatibilidade e observabilidade BG2:EE/EEex/multiplayer permanecem desconhecidas.

## Riscos e evidências pendentes — DEC-076/C (Discovery v7.2)

- **R-IDP-01 — Fusão por homônimos:** nomes iguais não são identificadores; exigir identidade lógica DEC-066 e provas.
- **R-IDP-02 — Onisciência de NPC:** ledger factual privado não alimenta automaticamente crença; ACL e canal por observador.
- **R-IDP-03 — Vazamento de segredo de PC:** consentimento, audience scope, fail-closed e logs redigidos antes de LLM/LAN.
- **R-IDP-04 — Disfarce mecânico presumido:** capability/POC por build, host+2 clientes; narrativa não garante ocultação visual.
- **R-IDP-05 — Fusão global de reputações:** reputação da persona por público; efeitos causais distintos e dedup DEC-075.
- **R-IDP-06 — Boato vira identidade comprovada:** evidência e proveniência; SUSPECTED/DISPUTED nunca equivalem a VERIFIED_PRIVATE.
- **R-IDP-07 — Segredo exposto por cache/log/embedding:** minimizar e filtrar também índices, workers LAN e auditorias.
- **R-IDP-08 — Vazamento temporal/restore:** branch/checkpoint/ano DR e revisão de persona; invalidar jobs stale.
- **R-IDP-09 — Revelação multiplicada por retries:** ledger por disclosure, audience, revision, cause e epoch; estado UNCERTAIN bloqueia.
- **R-IDP-10 — Persona enganosa sem limites consentidos:** proteção de PC, riscos HIGH, fair-play DEC-041/042 e autorização por público.
- **R-IDP-11 — Associação por delegado:** owner e controlling player separados; delegação não autoriza exibir segredos.
- **R-IDP-12 — Mistura com cânone por ano:** personas e descobertas exclusivamente no overlay, nunca no diretório knowledge/periods.

**Evidência:** escolha expressa C e desenho documental; **56 testes candidatos NÃO EXECUTADOS**. Não há teste de disfarce, rename, detecção de identidade ou sincronização multiplayer BG2:EE/EEex. Preservam-se DEC-060–075 e cânone físico anual.

## DEC-077/C — Riscos e evidências pendentes (Discovery v7.3)

- **R-INV-01 — Pista única vira certeza:** não elevar alegação sem verificação; manter `SUSPECTED/INCONCLUSIVE`.
- **R-INV-02 — Corroboração circular:** múltiplos relatos de uma mesma origem não são fontes independentes; ledger de ancestralidade.
- **R-INV-03 — Documento autêntico com conteúdo falso:** separar integridade, autoria e veracidade.
- **R-INV-04 — Contraprovas descartadas:** preservar revisão e álibis, reabrir hipótese em `DISPUTED`.
- **R-INV-05 — Segredo de PC revelado:** consentimento e ACL antes de prompts, UI, logs, índices e LAN.
- **R-INV-06 — Vínculo privado tratado como público:** gate distinto de divulgação por audiência.
- **R-INV-07 — Falsa condenação mecânica:** investigação não altera prisão, alinhamento, XP, quests, reputação nativa ou inventário sem POC/gateway/host.
- **R-INV-08 — Fonte de período errado:** validar ano DR, Knowledge Pack, branch e proveniência anual DEC-060/061/063.
- **R-INV-09 — Identificação de homônimos:** DEC-066/076, sem fusão por apelido, rosto ou nome.
- **R-INV-10 — Retroatividade em restore:** invalidar filas `STALE` e conhecimento do futuro; reconciliar checkpoints/epoch.
- **R-INV-11 — Retries divulgam duplicado:** idempotência por evento/decisão/audiência e falha `UNCERTAIN` fechada.
- **R-INV-12 — LLM inventa prova ou testemunha:** uso somente como auxiliar; regras/provenance e revisão contextual obrigatórias.
- **R-INV-13 — Metadado vaza verdade:** resultados de pesquisa, contagens, erros e telemetria também sujeitos a ACL.
- **R-INV-14 — Mecânica de investigação inexistente:** nenhuma detecção/diálogo/hook no BG2:EE/EEex assumido sem POC por build e multiplayer.

**Evidência:** escolha explícita DEC-077/C e documentação; **58 testes candidatos NÃO EXECUTADOS**. Sem prova de detecção de identidade, coleta mecânica de pistas, IA investigativa funcional ou sincronização host+dois clientes. DEC-060–076 e a segregação física por ano DR permanecem vigentes.

## DEC-078 — Evidências pendentes e riscos de justiça ficcional (Discovery v7.4)

- **R-JUST-01 — Sistema jurídico inventado:** alocar leis/poderes não documentados a Forgotten Realms; exigir fonte e vigência regional/DR ou `UNKNOWN`.
- **R-JUST-02 — Denúncia vira culpa:** separar fonte, testemunho, prova, caso e decisão; manter `INCONCLUSIVE` quando não suficiente.
- **R-JUST-03 — Autoridade fictícia vira árbitro da verdade:** veredito e fatos confirmados permanecem separados, inclusive para corrupção e erro.
- **R-JUST-04 — Punição automática de PC:** HIGH default-deny, consentimento e política DEC-041/042; sem prisão/remoção ou ação host sem gateway/receipt.
- **R-JUST-05 — Conflito entre guardas e facções:** jurisdição pode ser disputada; bloquear efeito irreversível e encaminhar para DEC-079.
- **R-JUST-06 — LLM cria condenação/alucinação de prova:** motor de regras e validação determinística, LLM somente para linguagem permitida.
- **R-JUST-07 — Vazamento de identidade/segredo:** ACL DEC-019/028/076/077 antes do LLM, UI, caches, logs ou LAN.
- **R-JUST-08 — Save/branch divergente ou retry duplicado:** epoch/checkpoint/ledger idempotente e `UNCERTAIN` bloqueia retry mecânico.
- **R-JUST-09 — Teleporte de agentes ou propagação instantânea:** NPC presença via host DEC-069 e notícias por DEC-029/074.
- **R-JUST-10 — Cânone contaminado:** política canônica curada por ano DEC-060–063, processos privados só em overlay.
- **R-JUST-11 — Scripts nativos quebrados:** DEC-050/051 e POCs por build antes de efeitos de quest/guarda/inventário.
- **R-JUST-12 — Backlog de casos artificialmente encerrado:** regras/filas DEC-056 sem agente por NPC ou desfecho inventado.

**Evidência:** escolha DEC-078/C e documentação de Discovery; **60 testes T078-* NÃO EXECUTADOS**, nenhuma integração mecânica BG2:EE/EEex/multiplayer confirmada.

## DEC-079 — Riscos e evidências interjurisdicionais pendentes (Discovery v7.5)

- **R-JUR-01 — Jurisdição universal fictícia:** pedido local aceito automaticamente por qualquer guarda. Gate por autoridade destinatária, região, ano DR, tipo e acordo curado.
- **R-JUR-02 — Tratado inventado por LLM:** registro sem fonte/corrente temporal. Compromissos apenas por fontes verificáveis e curadoria, `UNKNOWN` fail-closed.
- **R-JUR-03 — Onisciência de mandados:** solicitações teletransportadas entre cidades. Canais/rotas DEC-029/069, relógio DEC-022 e recibo de entrega.
- **R-JUR-04 — Recebimento confundido com execução:** separar pedido, delivery, recognition e host receipt; sem ação mecânica presumida.
- **R-JUR-05 — Autoridade e documento falsificados:** cadeia de custódia e validação de emissor; alegação ficcional não cria poder.
- **R-JUR-06 — NPC homônimo ou identidade secreta:** identidade DEC-066 e aliases DEC-076/077 verificados; não expor segredos a todos os destinatários.
- **R-JUR-07 — Prisão/guarda automático sem capacidade:** Action Gateway, build/host+2 clientes e POC, HIGH default-deny; não gerar perseguidor.
- **R-JUR-08 — Sanção duplicada por multipath/retry:** idempotência por pedido, autoridade, revisão e efeito, checkpoint e fencing.
- **R-JUR-09 — Pedido vencido/revogado em trânsito:** revalidar antes de coerção, bloquear STALE, preparar DEC-080 de correções propagadas.
- **R-JUR-10 — Facções rivais com precedência presumida:** `DISPUTED` e trilha de negociação, sem LLM árbitro único.
- **R-JUR-11 — Vazamento LAN/log:** ACL por público/finalidade, contexto mínimo e logs redigidos.
- **R-JUR-12 — Impacto HIGH sobre PC ausente:** DEC-041/042 consentimento e restrições, autorização especial, sem host effect até precondições.
- **R-JUR-13 — Contaminação de cânone:** lore por ano DR físico DEC-060 e overlay isolado por campanha/ramo.
- **Evidência:** apenas aprovação arquitetural do usuário, dados anteriores de Discovery e **62 testes candidatos NÃO EXECUTADOS**; nenhuma POC jurídica, perseguição, detenção, host/EEex comprovada.

## Riscos e evidências — DEC-080/C (Discovery v7.6)

- **R-REV-01 — Mandado revogado reativado por atraso:** revisões monotônicas e tombstone terminal, não prevalência por ordem de entrega.
- **R-REV-02 — NPC onisciente:** distinguir conhecimento local de prova autoritativa usada só por safety gate.
- **R-REV-03 — Captura com ordem incerta:** HIGH fail-closed, competência e prova de validade antes de host/gateway.
- **R-REV-04 — Notícia confundida com execução:** evento emitido/recebido/reconhecido/executado são fases diferentes.
- **R-REV-05 — Documento/autoridade falsos:** validar origem/competência; selos falsos podem ser parte de rumor, não poder coercitivo.
- **R-REV-06 — Revision spoof e conflitos entre emissores:** lineage e escopo por caso/autoridade, `COMPETENCE_DISPUTED` até revisão curada.
- **R-REV-07 — Duplicatas e retries:** idempotência por branch/ordem/revisão/emissor/destinatário, UNCERTAIN e receipts verificados.
- **R-REV-08 — Restore e Knowledge Pack incoerentes:** epochs/campanha/ano DR, invalidar mensagens de futuro, não misturar diretórios anuais.
- **R-REV-09 — Vazamento de identidade secreta:** ACL DEC-028/076/077 para casos, mensagens, logs, prompts e workers LAN.
- **R-REV-10 — Falsa reversão de dano passado:** revogação não apaga prisão/quest/loot comprovados; reparação exige DEC-081 e host.
- **R-REV-11 — Priorização sem entrega garantida:** notificações em fila têm prioridade, mas ausência de canal não gera ACK fictício.
- **R-REV-12 — Gate de coerção alega capacidade inexistente:** POC por build e host+2 clientes, DEFAULT UNSUPPORTED.
- **Evidência:** escolha humana DEC-080/C e documentação. **64 testes T080-01..64 NÃO EXECUTADOS**, nenhum efeito BG2:EE/EEex/multiplayer validado.

## DEC-081/C — Riscos e evidências pendentes (Discovery v7.7)

- **R-REP-01 — Revogação confundida com dano:** Exigir prova do ato efetivamente ocorrido e nexo causal.
- **R-REP-02 — Compensação fictícia:** Separar proposta e recibo host; sem valor ou item inventado.
- **R-REP-03 — Restituição duplicada:** Ownership e ledger por dano/remédio/beneficiário/branch/efeito.
- **R-REP-04 — Rollback irreal:** Histórico imutável, nova reparação causal; proibir rewind automático.
- **R-REP-05 — Competência inventada:** Jurisdição/ano DR/fontes curadas DEC-060–063/078/079.
- **R-REP-06 — Segredos expostos por retratação:** ACL/audiência, identidades privadas DEC-076/077 e consentimento.
- **R-REP-07 — Consentimento presumido:** Titular/controlador distintos e PC ausente não aceita por padrão.
- **R-REP-08 — Reputação restaurada instantaneamente:** Propagação DEC-029/074 e crenças persistentes; efeitos por domínio.
- **R-REP-09 — Quest ou inventário corrompidos:** Adapter comprovado, risk gate, host receipt, não editar save.
- **R-REP-10 — Falha/retry destrutivo:** UNCERTAIN, checkpoint, fencing e reconciliação antes de novo comando.
- **R-REP-11 — Fontes anacrônicas:** Normas historicamente vinculadas a ano DR e pack fixado.
- **R-REP-12 — Retaliação automática contra autoridades:** Investigação institucional DEC-082 ainda aberta e HIGH default-deny.
- **R-REP-13 — Pagamento pelo mesmo dano em várias cidades:** Correlacionar remédios interjurisdicionais no ledger privado.
- **R-REP-14 — Promessa de suporte inexistente BG2:EE:** Somente POC read-only/host+2 clientes; capacidades desabilitadas até evidência.

**Evidência disponível:** escolha C e documentação; **66 testes candidatos NÃO EXECUTADOS**. Não há POC de restituição, reabilitação ou alteração mecânica BG2:EE/EEex/multiplayer.

## DEC-082/C — Riscos de responsabilização institucional (Discovery v7.8)

- **R-082-01 / Culpa automática:** denúncia, erro ou compensação vira prova de corrupção; separar alegação, evidência e responsabilidade.
- **R-082-02 / Culpa coletiva:** agente isolado provoca sanção institucional sem nexo; avaliar ordem, chefia, omissão e padrão verificados.
- **R-082-03 / Instituições inventadas:** LLM presume tribunal/cargo/competência não fundamentados; fonte canônica e `PENDING_POLICY`.
- **R-082-04 / Contaminação temporal:** órgãos e leis de ano futuro aplicados retroativamente; DEC-060 partições físicas anuais e Knowledge Pack fixado.
- **R-082-05 / Punições prematuras:** LLM determina exoneração/prisão/reforma; risco HIGH, DEC-034, gateway/host, fail-closed.
- **R-082-06 / Confissão forçada:** NPC/LLM atribui ação, intenção ou fala a PC sem autorização; DEC-041/045/046.
- **R-082-07 / Segredos vazados:** identidade de denunciante/PC em prompts/LAN/logs; ACL/minimização e DEC-083 pendente.
- **R-082-08 / Falha de reconciliação:** job duplicado aplica sanção/alteração política duas vezes; ledger causal, fencing, `UNCERTAIN` sem retry.
- **R-082-09 / Rumor como verdade:** crença regional vira prova institucional e reputação mecânica; separar camadas e host receipt.
- **R-082-10 / Falsificação de prova:** depoimentos dependentes são contados como fontes independentes; grafo de proveniência DEC-077.
- **R-082-11 / Erro de titularidade:** superior é culpado apenas por posição; cadeia de delegação/ciência e tempo verificáveis.
- **R-082-12 / Capacidade fictícia:** alterar NPC/quest/facção sem adapter testado; POC por build, host+dois clientes.

**Evidência disponível:** somente aprovação DEC-082/C e elaboração documental. **68 testes NÃO EXECUTADOS**; não há POC BG2:EE/EEex/multiplayer.

## Riscos e evidências DEC-083/C — Fontes protegidas (Discovery v7.9)

- **R-083-01 — Exposição prematura:** depoimento vaza nome da fonte; separação de identidade e conteúdo com gate por campo.
- **R-083-02 — Reidentificação indireta:** metadados de hora/cargo/local revelam identidade apesar de ocultar nome; revisão de minimização e risco.
- **R-083-03 — Sigilo como prova:** testemunho confidencial tratado como verdade; avaliação independente de origem e contradições.
- **R-083-04 — Cópias circulares:** três rumores dependem de uma fonte e aparentam corroboração; grafo de proveniência DEC-077.
- **R-083-05 — Acesso indevido por autoridade:** competência/época desconhecida usada para exibir identidade; default-deny e revisão.
- **R-083-06 — Exposição de PC:** LLM força depoimento/confissão ou revela segredo em sessão coop; DEC-019/041/045/046 e consentimento.
- **R-083-07 — Vazamento em sistemas de apoio:** RAG, logs, cache, embedding, export ou LAN divulgam vínculo; filtragem antes do processamento.
- **R-083-08 — Divulgação duplicada:** retries/reconnect enviam nome duas vezes ou ampliam audiência; ledger idempotente, fencing e `UNCERTAIN`.
- **R-083-09 — Retaliação fictícia:** ameaça abstrata vira ataque real ou NPC invulnerável; prova de evento, risco HIGH e host comprovado.
- **R-083-10 — Contágio de ramo ou época:** restore importa segredo de futuro diferente; checkpoint/branch/ano DR e expiração de jobs.
- **R-083-11 — Ausência de contraditório:** sigilo absoluto impede contestação legítima; extratos redigidos sob competência contextual.
- **R-083-12 — Revogação confundida com esquecimento:** credenciais revogadas apagam memória de quem recebeu legitimamente; bloquear novas divulgações e manter história.
- **R-083-13 — Cânone contaminado:** depoimento de campanha grava em lore anual; somente overlay e isolamento físico DEC-060.
- **R-083-14 — Capacidade de engine inventada:** alegar escort/proteção/invisibilidade sem bridge POC e host+2 clientes; manter pending unsupported.

**Evidência:** apenas escolha arquitetural DEC-083/C; 70 testes candidatos T083-* NÃO EXECUTADOS. Sem implementação BG2:EE/EEex/multiplayer.**

## Integração DEC-084/C — Discovery v8.0: riscos e evidências pendentes

- **R-084-01 — Ameaça inventada:** LLM ou rumor gera fato de perseguição; separar `ThreatReport` de `ProtectionOutcome` e exigir host para efeitos.
- **R-084-02 — Invulnerabilidade ou teleporte:** plano narrativo altera presença/HP sem capabilities; bloquear.
- **R-084-03 — Fonte exposta pelo próprio plano:** rota, hora e refúgio reidentificam; ACL/minimização antes de modelo, logs e LAN.
- **R-084-04 — Antagonista onisciente:** facção hostil deduz plano privado sem canal; exigir evidência de conhecimento DEC-029/074.
- **R-084-05 — Protetores/recursos duplicados:** reservas sem owner/lease; exigir idempotência e fencing por caso/ação.
- **R-084-06 — NPC indisponível:** texto de escolta cria guarda físico; exigir identidade, localização e capacidade host verificadas.
- **R-084-07 — Retaliação HIGH automática:** morte, prisão, confisco e PvP por risco narrativo; default-deny sem autorização e host.
- **R-084-08 — Consentimento de PC ignorado:** fuga/testemunho forçado por LLM, ou delegado age além do escopo; bloquear.
- **R-084-09 — Conflito de interesse:** instituição sob suspeita recebe identidades/planos de fonte; verificar competência/ACL.
- **R-084-10 — Duplo encontro offscreen/local:** garantir handoff único DEC-071 e receipts.
- **R-084-11 — Restauração inconsistente:** job de ramo/época futura gera teleporte ou recurso duplicado; reconciliar.
- **R-084-12 — Capacidade BG2:EE não comprovada:** abrigo, escolta e perseguição são SPECS/POCs, não implementação.

**Evidência:** escolha arquitetural do idealizador e contratos documentais; 72 testes T084-* **NÃO EXECUTADOS**, sem provas host+dois clientes. Proteção contextual não equivale a garantia de segurança.

## Riscos e evidências pendentes — DEC-085/C (Discovery v8.1)

- **R-085-01 — Metaconhecimento adversário:** NPC recebe rota por leitura do ledger privado; mitigar com `AdversaryBelief` separado e ACL antes de LLM.
- **R-085-02 — Vazamento lateral:** nome de arquivo, mapeamento, horário, coordenadas, cardinalidade de comboios, logs ou prompt revelam identidade; tratar inferência indireta como dado sensível.
- **R-085-03 — Suspeita vira plano comprovado:** boatos/confirmações fabricadas por IA; exigir fonte, independência, causalidade, cronologia e estados parciais.
- **R-085-04 — Conhecimento global instantâneo:** todos os membros de guilda sabem o esconderijo; exigir audiência, canais e trânsito de notícias.
- **R-085-05 — Replanejamento mágico:** abrigo/rota/guarda criado do nada ou teleporte; validar disponibilidade, consentimento e receipts host.
- **R-085-06 — Descoberta resulta em ataque HIGH:** aplicação mecânica sem risco/host; separar inteligência de ação coercitiva e default-deny HIGH.
- **R-085-07 — Segredo persiste em cache obsoleto:** revogação não invalida contextos futuros; revisão, fencing, grants e cache partitioning.
- **R-085-08 — Replay de divulgação:** jobs duplicados geram vazamentos ou efeitos repetidos; ledgers idempotentes e `UNCERTAIN` reconciliação.
- **R-085-09 — Branch ou ano vazado:** informação de outra campanha/época entra em NPC atual; proteger `branch`, checkpoint, ano DR e KPack.
- **R-085-10 — Investigação impossível ou invencível:** plano é indetectável por decreto ou espionagem tem sucesso inevitável; permitir descobertas legítimas verificáveis, recusando capacidades inexistentes.
- **R-085-11 — Pistas plantadas sem política:** LLM fabrica provas falsas sem autorização; DEC-086 em aberto, DEC-085 não aprova engano ativo.
- **R-085-12 — Confiança em hooks não testados:** engine não expõe observação/interceptação pretendida; sem POC BG2:EE/EEex não afirmar operação mecânica.
- **Evidência:** escolha arquitetural humana e documentação apenas; **74 testes T085-* NÃO EXECUTADOS**, sem benchmark multiplayer. DEC-060–084 preservadas.

## Riscos e evidências da DEC-086/C — Discovery v8.2

- **R-D086-01 (fato falso):** rumor plantado é confundido com `WorldFact`; impedir promoção sem evidência e host-confirmation.
- **R-D086-02 (culpa fabricada):** documento ou testemunha fictícia incrimina PC; bloquear consequência punitiva e exigir autoria/consentimento/risco.
- **R-D086-03 (metaconhecimento):** NPC consulta rota real ou fonte secreta; ACL/need-to-know antes de LLM/RAG/LAN.
- **R-D086-04 (cadeia de fontes circular):** rumor repetido vira prova; dedup/ancestralidade e confiança contextual.
- **R-D086-05 (recursos inventados):** mensageiros/objetos/horários criados por texto; verificação de disponibilidade e POC por build.
- **R-D086-06 (efeitos HIGH):** isca produz captura, PVP ou morte sem autorização; gate cumulativo, fail-closed e host receipt.
- **R-D086-07 (disseminação duplicada):** retry/reload multiplica rumores, custo ou reputação; idempotência e epoch.
- **R-D086-08 (documento host falsificado):** texto se passa por receipt; apenas componente verificador confirma receipts reais.
- **R-D086-09 (sigilo indireto):** descrições, metadados e horários revelam fonte; filtragem por campo, privacidade de logs e índices.
- **R-D086-10 (futuro e branch):** rumor futuro passa a NPC do passado; revisão de checkpoint, época DR e pin do Knowledge Pack.
- **R-D086-11 (desfecho de LLM):** modelo decide que isca funciona sem prova; somente proposta, observação e regras determinísticas.
- **R-D086-12 (vazamento de cânone):** claims de campanha contaminam lore; armazenamento isolado fisicamente de `knowledge/periods/<ANO>-DR/`.

**Evidência real:** escolha C, arquitetura textual e **76 testes T086-* candidatos NÃO EXECUTADOS**. Não existe integração validada de espionagem/iscas no BG2:EE/EEex/multiplayer. DEC-060–085 preservadas.

## Integração da DEC-087/C — Evidências e riscos (Discovery v8.3)

| Risco | Falha a impedir | Mitigação candidata |
|---|---|---|
| R087-01 | A LLM inventa traição ou intenção de PC | Owner consent/DEC-019/041/045/046, filtrar e validar fatos. |
| R087-02 | Trocar toda lealdade por contato com facção rival | Proveniência, conflito e valores distintos; suspeita ≠ prova. |
| R087-03 | Alterar canon, romance ou companion nativo | Curadoria DEC-060–063, DEC-047/048/050 e gating por build. |
| R087-04 | NPC conhece vínculo secreto sem canal | ACL, crença local, difusão causal e minimização LLM/LAN. |
| R087-05 | Coação torna NPC ou PC um fantoche | Limites de agência, risco e consentimento aplicáveis. |
| R087-06 | Falha de host duplica saída, facção ou despesas | Idempotência, recibos, checkpoint e fail-closed UNCERTAIN. |
| R087-07 | LLM fabrica provas/diálogos com falsas promessas | Evento canônico/host confirmado e fonte auditável. |
| R087-08 | Mudança social vira alteração mecânica não suportada | Capability POC BG2:EE/EEex host+2 clientes e action gateway. |
| R087-09 | Lealdade dinâmica contamina lore de outras eras | Cânone físico anual; compromissos apenas overlay campanha/ramo. |
| R087-10 | Rumor de agente duplo gera sanções injustas | Investigação DEC-077/078/082, contraditório e gates de risco. |

**Evidência real:** aprovação arquitetural da opção C. **80 testes T087-* são candidatos, NÃO EXECUTADOS**; sem POC de troca de lealdade/facção/party em BG2:EE.

## DEC-088/C — Riscos e lacunas de evidência (Discovery v8.4)

- **R-INF-01:** NPC forçado a colaborar por oferta/insatisfação — mitigação por agência e recusa obrigatórias.
- **R-INF-02:** LLM assina contrato inventado — aceite somente após evento, regra, consentimento e registro válidos.
- **R-INF-03:** PC ausente/terceiro assume obrigação — separar owner/delegação DEC-041/045/046.
- **R-INF-04:** conhecimento fabricado da fonte — consultar observações e fontes realmente alcançáveis, `UNKNOWN` permitido.
- **R-INF-05:** promessa transformada em entrega ou em verdade — campos/ledger distintos e DEC-089 posterior.
- **R-INF-06:** ouro/itens gerados sem saldo ou duplicados — reservas tipadas, budgets, gateway e receipt do host.
- **R-INF-07:** farming por múltiplos aliases ou negociação repetida — caps por identidade factual e dedup.
- **R-INF-08:** exposição da fonte a NPC/PC/LLM/LAN indevidos — ACL antes de retrieval, minimização em logs/caches.
- **R-INF-09:** acordos cross-branch ou além do ano DR — binding de campanha/ramo/KPack/checkpoint.
- **R-INF-10:** aceitação de fonte como mudança mecânica de facção — capability build, Action Gateway, confirmação host.
- **R-INF-11:** rompimento apaga histórico ou produz retcon — eventos append-only e correção causal.
- **R-INF-12:** coerção disfarçada de consentimento — estado distinto e gates MEDIUM/HIGH.

**Status:** somente aprovação de design; **82 testes candidatos T088-* NÃO EXECUTADOS**; sem POC multiplayer para diálogos/recursos/recrutamento.

## DEC-089/C — Evidência e riscos de confiabilidade dos informes (Discovery v8.5)

- **R-089-01: rumor circular contado como três fontes** — lineage e `EvidenceFamily` por raiz; dependências não multiplicam corroboração.
- **R-089-02: NPC aprende segredo oniscientemente** — verificações de presença, data DR, documento e comunicação legítima.
- **R-089-03: ausência de prova vira falsa condenação** — distinguir `UNKNOWN`, `INCONCLUSIVE` e contradição efetiva.
- **R-089-04: LLM fabrica documento ou certeza** — validação determinística e identificadores/recibos de evidência; LLM só propõe.
- **R-089-05: reputação de informante vira probabilidade absoluta** — perfis por tema e histórico, revisão e sem equivalência com DEC-030/087.
- **R-089-06: informação parcialmente verdadeira autentica todo o relatório** — avaliação por campo e recorte temporal/espacial.
- **R-089-07: vazamento da fonte por metadados** — ACL DEC-083 em nomes, horários, locais, IDs, índices, RAG, logs e LAN.
- **R-089-08: informação de futuro/branch errado** — vinculação de Knowledge Pack, checkpoint, DR e epoch; descartar STALE.
- **R-089-09: relatório vira mandado ou ataque** — gates DEC-027/077–082 e Action Gateway DEC-011/012, sem ação mecânica por parecer.
- **R-089-10: correção apaga crença histórica** — revisões append-only; fatos confirmados não retroagem.
- **R-089-11: replay gera dupla prova ou confiança** — dedup por report/evidence/family/epoch e reconciliação UNCERTAIN.
- **R-089-12: informes de campanha poluem cânone histórico** — lore físico por ano DR DEC-060 sem segredos/rumores no corpus.

**Evidências existentes:** somente aprovação arquitetural da DEC-089/C; 84 cenários **NÃO EXECUTADOS**. Nenhuma POC de veracidade, entrevista, documento ou sincronização em BG2:EE/EEex multiplayer.

## Integração DEC-090/C — Discovery v8.6

- **R-DOS-01 — Fonte indireta exposta em citação, filename, timestamp ou ID:** minimização e pseudocitações antes de export/LLM, teste de inferência em metadados.
- **R-DOS-02 — Sumário promove rumor a verdade:** validar cada conclusão contra `ClaimAssessment` e evidências DEC-089; preservar qualificadores.
- **R-DOS-03 — Relatos circularmente copiados contam como provas independentes:** preservar `EvidenceFamily` e grafo de linhagem na revisão.
- **R-DOS-04 — View de autoridade é entregue a aliado:** amarrar view hash a recipient_id/purpose/policy/ACL.
- **R-DOS-05 — Compartilhamento implícito com a party ou NPCs:** estado `ShareAuthorization` separado de `TransmissionEvent` e `RecipientReceipt`.
- **R-DOS-06 — Conteúdo omitido na UI vaza via LLM/log/cache/embedding:** sanitização pre-inferência e pre-armazenamento; auditoria redigida.
- **R-DOS-07 — Nova revisão apaga crença ou recibo passado:** snapshots e ledger append-only com atualização causal por destinatário.
- **R-DOS-08 — Revogação de ACL promete apagamento impossível:** bloquear novas divulgações e jobs pendentes, reconhecer memórias legitimamente adquiridas.
- **R-DOS-09 — Recebimento não verificado vira certeza de leitura:** estados PENDING/UNCERTAIN, confirmação por canal e receipt.
- **R-DOS-10 — Branch/clock stale vaza segredo de outra campanha:** checkpoint/epoch/DR/KPack e invalidação de cache.
- **R-DOS-11 — Dossiê vira item/quest na engine sem POC:** gateway/host/capability e testes host+2 clientes.
- **R-DOS-12 — Confirmação de autoridade ficcional passa a ser verdade factual:** múltiplos planos epistêmicos DEC-077/078/089, competência e prova de causa.

**Evidência atual:** aprovação de arquitetura DEC-090/C e arquivos Markdown; **86 testes candidatos não executados**, sem implementação de envio/dossiê mecânico em BG2:EE/EEex/multiplayer. DEC-060–089 preservadas.

## Integração DEC-091/C — Discovery v8.7: riscos e evidências ainda ausentes

- **R-091-01, meta-conhecimento:** dossiês secretos podem revelar identidade, operação ou refúgio; mitigar com `DisclosureView` ACL/consentimento antes de qualquer modelo, LAN, cache e log.
- **R-091-02, execução antecipada:** plano/approval/reserva são confundidos com receipt; bloquear publicação de fatos até confirmação do host.
- **R-091-03, falso positivo:** relatos contraditórios usados para prender/atacar; gates MEDIUM/HIGH, evidência por origem e fail-closed.
- **R-091-04, recurso fictício/duplo:** reserva não comprovada ou duplicada; ledger, conflito e fencing TTL, receipt de consumo mecânico.
- **R-091-05, perda de agência:** líder/LLM assume decisões de PC ausente/delegado; consentimento DEC-041/045/046 obrigatório.
- **R-091-06, presença fictícia:** NPC não está na região ou não há capability CRE; validação de identidade/rota e POCs host+2 clientes.
- **R-091-07, reexecução:** restart, timeout ou restore duplicam despacho; estado UNCERTAIN, epoch/checkpoint e idempotency key.
- **R-091-08, desvio temporal/canônico:** futuro/branch errado, KPack incorreto; isolamento físico por ano DR DEC-060 e referências do overlay.
- **R-091-09, escalada LOW→HIGH:** composição de operações de baixo risco gera sanção/violência; risco agregado e controle de autorização.
- **Evidência real:** aprovação arquitetural C e documentação; **88 testes candidatos NÃO EXECUTADOS**; nenhuma POC BG2:EE/EEex realizada nesta etapa.

## Riscos pendentes DEC-092/C — monitoramento, pausa e replanejamento (Discovery v8.8)

- **R-092-01 — falsa pausa:** pausa de orquestrador confundida com pausa real do BG2:EE; separar níveis e exigir capability testada.
- **R-092-02 — ação duplicada:** cancelamento/retry de dispatch `UNCERTAIN` replica ataque, item ou movimento; host receipt, idempotência e reconciliação.
- **R-092-03 — consentimento obsoleto:** revisão herda aprovação anterior; CAS de revisão, escolha de PC e reautorização por escopo.
- **R-092-04 — replanejamento por rumor:** hipótese/LLM vira WorldFact; só trigger confirmado e avaliação de origem DEC-089.
- **R-092-05 — recursos duplicados:** pausa/aborto libera lease sem prova; fencing, reserva/consumo separados e ledger DEC-091.
- **R-092-06 — rollback fictício:** abortar missão apaga dano ou conhecimento de NPC; fatos prévios persistem, reparações são eventos próprios.
- **R-092-07 — meta-conhecimento:** mudança de dossiê expõe identidade/rota secreta ao NPC; ACL e transmissão DEC-083/085/090.
- **R-092-08 — eventos de outro branch:** restore reexecuta decisão futura; checkpoint, KPack, branch, watermarks e `STALE`.
- **R-092-09 — escalada silenciosa:** dezenas de LOW produzem efeito HIGH; avaliação agregada e default-deny DEC-027/034.
- **R-092-10 — pressupor API engine:** falar em pausa física/cancelamento sem POC BG2:EE/EEex host+dois clientes; status `UNKNOWN` e bloqueio.

**Evidência disponível:** escolha arquitetural C e documentos ADR-0087/técnico 92. **90 testes candidatos NÃO EXECUTADOS**, nenhuma operação real executada.

## Integração da DEC-093/C — riscos e evidências (Discovery v8.9)

- **R-CON-01 — dupla reserva de NPC/item:** CAS/fencing interno e identidade persistente; build host receipt ainda não demonstrados.
- **R-CON-02 — corrida e retry de worker:** epoch/token e idempotência; `UNCERTAIN` impede liberar recurso ou repetir ação.
- **R-CON-03 — leilão de prioridade injusto:** tie-break auditável, espera/fairness e compromissos verificados; urgência não dá autoridade.
- **R-CON-04 — coação de jogador/PC delegado:** owner, consentimento por revisão e autorização DEC-041/045/046.
- **R-CON-05 — confundir CPU com NPC:** scheduler DEC-056 otimiza compute, não confere direito sobre recursos de mundo.
- **R-CON-06 — ilusão de pausa/atomicidade BG2:** leases em middleware não alteram runtime; exigir POC por build host+2 clientes.
- **R-CON-07 — vazamento de segredo ao explicar conflito:** ACL e mensagem redigida, sem identidade de testemunha ou rota.
- **R-CON-08 — deadlock/starvation:** grafo de espera e observabilidade; recuperação detalhada DEC-094 aberta.
- **R-CON-09 — branch/restore e locks obsoletos:** checkpoint, KPack, session e epoch; fence e reconciliação.
- **R-CON-10 — tempo DR versus TTL de serviço:** manter os relógios distintos para não fabricar conclusão de viagem.

**Evidência:** design aprovado somente; **92 testes candidatos NÃO EXECUTADOS**, sem integração scheduler/CAS/EEex/multiplayer comprovada. ADRs anteriores intocados.

## Integração DEC-094/C (Discovery v9.0) — riscos e evidências pendentes

- **R094-01 Deadlock falso:** ciclo pode ter alternativa viável; classificar suspeita versus bloqueio confirmado com provas/OR dependencies.
- **R094-02 Lease expirado incorretamente liberado:** estado do motor não acompanha TTL interno; exigir evidência positiva de não dispatch e fencing.
- **R094-03 Retry de comando UNKNOWN/UNCERTAIN:** quarentena e conciliação, sem dupla mutação de host.
- **R094-04 Starvation e viés de prioridade:** aging/cotas auditáveis, sem transformar urgência em permissão.
- **R094-05 Preempção de PC/recursos de terceiro:** autorização explícita, consentimento e ownership por ator persistente.
- **R094-06 Crash e relógio reiniciado:** nova epoch, checkpoint, host receipt/outbox; nunca inferir ausência de comando por timeout.
- **R094-07 Vazamento por grafo/telemetria:** redigir nomes de testemunhas, planos e dossiês privados.
- **R094-08 Falha de sincronização BG2:EE:** CAS do middleware não prova transação com host ou cancelamento nativo.

**Evidência:** decisão arquitetural C expressa; nenhum scheduler/lock/bridge testado. **94 testes T094-* candidatos NÃO EXECUTADOS**; DEC-060–093 preservadas.

## Integração DEC-095/C — Discovery v9.1 — riscos, ainda sem POC no motor

- **R095-01 Reversão de evento irreversível:** Saga somente adiciona novas ações compensatórias, sem apagar memória/história/combate/tempo.
- **R095-02 Reembolso duplicado:** host receipt, outbox/idempotency e reconciliação de UNCERTAIN antes de retry.
- **R095-03 Autoridade falsa:** contratos exigem consentimento, ownership e gates; LLM não autoriza novas ações.
- **R095-04 Compensação sem recursos:** não criar saldo, NPC ou item; falha segura/parcial.
- **R095-05 Restore/replay:** checar checkpoint/epoch/branch e persistir ledger original.
- **R096-PROP-01 Evento anacrônico:** datas YEAR_ONLY/DISPUTED, mês/feriado desconhecidos devem bloquear efeitos automáticos precisos.
- **R096-PROP-02 Lore de ano futuro:** proteger diretórios físicos DEC-060, KPack pinado DEC-063 e acesso epistêmico NPC.
- **R096-PROP-03 Disseminação instantânea:** globalidade do evento não é conhecimento de todos os NPCs; rumor somente por DEC-029/074.
- **R096-PROP-04 Reaplicação e efeitos em cascata:** caps/dedup e propagação dependente de confirmação do efeito pai.
- **R096-PROP-05 Efeito do jogo presumido:** localizações/build/map IDs e capabilities sem teste -> proposal-only.

**Evidência:** DEC-095/C expressa; 96 testes candidatos **NÃO EXECUTADOS**. Matriz/DEC-096 ainda proposta, exemplos unitários sintéticos e sem teste BG2:EE.

## Integração DEC-096/C — Discovery v9.2 — riscos técnicos pendentes de POC

- **CR-096-01 | Risco crítico:** anacronismo por data ambígua → bloquear ativação mensal sem precisão MONTH/EXACT_DAY/INTERVAL válido.
- **CR-096-02 | Risco crítico:** NPC recebe spoiler futuro ou segredos → partição física por ano DR, KPack pinado e filtragem por conhecimento adquirido/ACL.
- **CR-096-03 | Risco alto:** evento GLOBAL implica impacto em qualquer mapa → exigir escopo de repercussão com locais e IDs por build comprovados.
- **CR-096-04 | Risco alto:** confundir evento fonte com efeito aplicado → `ImpactProposal` separada de `AppliedImpact` e recibo host.
- **CR-096-05 | Risco alto:** evento indireto sem parent/erro de horário → DAG, lineage, delay e recibos confirmados.
- **CR-096-06 | Risco alto:** retry/restore duplica patrulhas/reputação/itens → epoch, dedup transacional, outbox e reconciliação host.
- **CR-096-07 | Risco alto:** dados canônicos preliminares da matriz 14 têm datas/alcances disputados → curadoria humana, fontes primárias, não publicar sem pin.
- **CR-096-08 | Risco alto:** loops/caps e conflito de eventos concorrentes → orçamento, DAG, limites e DEC-097.
- **CR-096-09 | Risco alto:** texto LLM manipula predicado ou risco → DSL fechada e narrativa apenas pós-filtro.
- **CR-096-10 | Risco médio:** custo O(todos eventos por frame) → índices por data/região e avaliação por mudança factual, zonas DORMANT bounded.
- **CR-096-11 | Risco crítico:** efeitos sobre PC/host sem autorização → DEC-011/012/027/041 e capabilities por build.
- **CR-096-12 | Risco médio:** diferença calendário Harptos/feriados → parser com testes específicos e precisão explícita.

**Evidência:** aprovação arquitetural DEC-096/C; 100 testes candidatos de integração **NÃO EXECUTADOS**. JSON Schema e testes Python sintetizados validam forma/filtragem em sandbox, **não** demonstram integração de FR/BG2:EE/EEex.

## Integração DEC-097/C — Discovery v9.3

**Evidência de aprovação:** escolha C em 2026-11-07, ADR-0092. **Riscos R-CMP-097-01..10:** (1) stacking de mesma causa; (2) arredondamento divergente de clientes; (3) caps insuficientes; (4) origem de evento sem temporalidade; (5) fade calculado pelo relógio do sistema em vez do DR; (6) revision/policy hash divergente; (7) efeito simulado tomado como receipt; (8) ações irreversíveis repetidas no reload; (9) atraso de rumor ignorado; (10) carga de recomposição por frame. Mitigação: grupos causais editoriais, Decimal/ponto fixo, unidades/caps por domínio, relógio DEC-022, pin DEC-063, gates host DEC-011/012, idempotência DEC-093–095, ACL DEC-028 e orquestração por eventos. **102 testes candidatos não executados**; referência Python é sintética, sem interface com o jogo.

## Evidências e riscos DEC-098/C — Discovery v9.4

**Aprovação arquitetural:** DEC-098 opção C, ADR-0093. **Não existe evidência de capacidade de observação, spawn, persistência, cleanup ou sincronização no BG2:EE/EEex multiplayer**. O script unitário de referência só consome JSON sintético.

- **CR-MAT-098-01:** observação parcial tomada como prova de ausência -> exigir cobertura validada por ação/build.
- **CR-MAT-098-02:** clone de NPC persistente/mesmo CRE -> identidade por persistent ID + ownership receipt.
- **CR-MAT-098-03:** objeto de quest/mod/PC removido por cleanup -> owner não-INFINITY_AI é PRESERVE.
- **CR-MAT-098-04:** save/load reinicia instância e duplica patrol -> ledger + snapshot + epoch/checkpoint + host scan.
- **CR-MAT-098-05:** timeout do host dispara retry duplicado -> outbox idempotente e quarentena UNCERTAIN.
- **CR-MAT-098-06:** mapa com mods diferentes invalida referências -> fingerprint/capabilities e revisão DEC-099.
- **CR-MAT-098-07:** percentual econômico reaplicado ao entrar -> target absoluto da DEC-097 + diff único.
- **CR-MAT-098-08:** offscreen avança anos instantaneamente -> catch-up bounded/quotas/DEC-022.
- **CR-MAT-098-09:** encounter resolvido reaparece em tela -> lease e handoff únicos DEC-071/073.
- **CR-MAT-098-10:** efeito narrativa vira verdade mecânica -> gate Action Gateway e recibo host.
- **CR-MAT-098-11:** logs revelam fontes/identidades privadas -> ACL/redação DEC-028/083–090.
- **CR-MAT-098-12:** POC de EEex inexistente -> bloquear ações sem capability e reportar sem implementação.

**Provas pendentes:** capability matrix por build e modo multiplayer; observação host por instância; correlação com receipts; save/load; 2 clientes; scripts/mods/quests; escalas DORMANT, ACTIVE; privacidade. **T098-001..104 não executados.**


## Evidência e riscos — DEC-099/C (Discovery v9.5)

- **Risco crítico de regressão:** sobrescrever quest flags, scripts, banters, cutscenes, romances, inventários de PC, NPCs de mods ou entidades nativas ao reconciliar DEC-098. **Mitigação de projeto:** owner de instância e por campo, proveniência e custódia distintas, contratos por build/EEex/modpack hash, bloqueio de writes sem POC.
- **IDs recicláveis e observação parcial:** nome/CRE/engine-instance-id não comprovam ownership e ausência em scan incompleto não comprova desaparecimento. Requer geração da instância, correlação a identidade persistente e recibos host-confirmed; divergência → `HOLD_RECONCILE`.
- **Mods e migração:** atualização/ordem dos mods e revisões EEex/bridge invalidam capabilities não revalidadas. Não usar heurísticas da LLM para resolver conflitos mecânicos.
- **Privacidade e spoilers:** observação de quest/script pode conter segredos; exigir minimização, ACL e DEC-100 específica. Read-only não confere autorização de divulgação nem escrita.
- **Evidência disponível:** ADR-0094, documento técnico 99, JSON Schema, fixture e preflight Python **puramente sintéticos**. T099-001..120 são **CANDIDATOS NÃO EXECUTADOS**; nenhum hook real, save de jogo, modpack ou teste de 2 clientes foi conduzido.


## Evidências, riscos e bloqueios — DEC-100/C (Discovery v9.6)

- **R100-01 — spoilers e conhecimento indevido:** leaks por nomes de flags/scripts, futuros ramos, identidades e romance. Mitigar com allowlist estrita, classificações sensíveis, safe semantic projection e ACL por audiência/finalidade.
- **R100-02 — leitura com side effects:** opcode/EEex hook não catalogado pode disparar scripts; **POC real por build é obrigatória**. Sem teste independente => capability indisponível; classificação read-only em documentação não é prova.
- **R100-03 — falso negativo:** varredura parcial, estado `UNAVAILABLE`, `UNKNOWN` ou `STALE` não significa que quest não ocorreu; manter unknown sem alucinação.
- **R100-04 — compatibilidade inválida:** versão BG2:EE, EEex, bridge, modpack hash/ordem, adapter revision e schema mismatch invalidam manifest/caches e exigem recertificação.
- **R100-05 — dados no prompt/cache/LAN:** separar estado técnico secreto, marcos projetados e conhecimento dos atores; logs opacos e caches por branch/audience/purpose/epoch.
- **R100-06 — mistura de autoridade:** observação técnica não é host receipt e não concede write ownership DEC-099, nem mudanças mecânicas DEC-011/012.
- **R100-07 — scripts maliciosos:** strings do mod são dados não confiáveis; nunca instruções para a IA, e saída nunca bruta.
- **R100-08 — testes de jogo pendentes:** T100-001..124 **NÃO EXECUTADOS**. O gate Python/JSON é sintético e não demonstra a existência de qualquer hook BG2:EE/EEex ou integração multiplayer.

**Risco residual alto:** ausência de POCs em Windows BG2:EE + EEex/bridge com 1 host e 2 clientes. Próxima DEC-101 para mapeamento semântico de fases.

## Evidências, riscos e bloqueios — DEC-101/C (Discovery v9.7)

- **R101-01 — significado errado:** mesma flag/valor pode ter semântica diferente por build, modpack, ordem, quest variant ou script. Gate: catálogo pinado, curado e versionado, sem fallback genérico.
- **R101-02 — progressão falsa:** leitura parcial, estágio desconhecido ou negativo inferido não provam que quest não aconteceu; saída `UNKNOWN`/`STALE`, sem inferência LLM.
- **R101-03 — contradição de fases:** marcos exclusivos simultâneos ou transição regressiva na mesma epoch exigem `AMBIGUOUS`/`BLOCKED_TRANSITION`, sem arbitragem automática.
- **R101-04 — spoiler no mapeamento:** regras, IDs, nomes de flags e dependências podem revelar romancing/future branches; ACL rigorosa, logs opacos, prompts somente com projeção mínima.
- **R101-05 — cache/restore/patch:** alteração de build, mod, save, revisão semântica ou host/checkpoint epoch invalida afirmações.
- **R101-06 — autoridade espúria:** marco semântico não é host receipt, não cria conhecimento NPC nem autoriza mutation de quest, scripts, NPC, romances ou World State.
- **R101-07 — cobertura de curadoria:** catálogo não revisado, assinado ou testado fica indisponível por default; a LLM não preenche a lacuna.
- **R101-08 — ausência de POC real:** T101-001..128 **NÃO EXECUTADOS** em BG2:EE/EEex/bridge ou multiplayer. Exemplos Python/JSON e testes unitários são exclusivamente sintéticos.

**Bloqueio:** validar read-only de DEC-100 por build, transições e proteção de spoiler em Windows BG2:EE/EEex, modpack pinado e host + dois clientes. DEC-102 permanece tema aberto para divergência host/overlay.


## Integração DEC-102/C — Discovery v9.8

**Evidências e riscos.** Risco de divergir host/overlay após save/load, caches, epochs e mudança de modpack. DEC-102/C prevê quarentena, evidência semântica curada e CAS em visões derivadas. Ainda sem prova de leitura real nem de reconciliação com BG2:EE/EEex host+dois clientes.


## DEC-103/C — Riscos e evidências pendentes (Discovery v9.9)

- **Prova pendente:** adaptação read-only de quests em BG2:EE/EEex/host+dois clientes (DEC-100), mapeamento curado por build (DEC-101) e reconciliação committed (DEC-102). Um `CONSISTENT` sem prova não autoriza admissão.
- **Risco crítico:** vazamento de spoilers/identidades por rumos, métricas, prompts, logs, IDs de regras e inferência de audiência; ACL independente para admissão e transmissão, erro minimizado, canário de privacidade obrigatório.
- **Risco crítico:** duplicação de eventos após reentry/save/load/restore; dedup baseado em occurrence certificada e ledger/outbox transacional por branch/lineage.
- **Risco alto:** host receipt ausente, action `UNCERTAIN`, regras modificadas após pin, ownership de quest/mod/PC, propagação instantânea não causal e interpretação de clock DR incorreta; fail-closed e reconciliação.
- **Evidência técnica atual:** testes unitários Python exclusivamente sintéticos; **136 cenários T103 candidatos NÃO EXECUTADOS**. Nenhum efeito de reputação/economia/rumor, bridge, LLM ou NPC BG2:EE real foi observado/testado.
- **Seguinte tema:** DEC-104 em aberto para retificar os efeitos já emitidos preservando cadeia de provas e ações confirmadas.

## Riscos adicionais — DEC-104/C (Discovery v10.0)

R-RET-104-01: cascata apaga efeito host-confirmed; impedir rollback e exigir Saga DEC-095. R-RET-104-02: contenção de comando já despachado causa replay ou liberação incorreta; bloquear até receipt. R-RET-104-03: grafo causal incompleto, cíclico, cross-branch ou com multi-causas; quarentena e prova de suporte. R-RET-104-04: errata expõe fonte protegida ou muda memória NPC sem entrega; ACL e transmissão causal. R-RET-104-05: restore/save/epochs/rev são confundidos; fencing/CAS e linhagem. Nenhuma POC host+2 clientes foi executada; T104-* candidatos.

## Riscos e evidências pendentes — DEC-105/C (Discovery v10.1)

- **R105-01 — broadcast onisciente:** errata global ou inferência de recebimento sem rota/DR; exigir canal legítimo e receipt individual.
- **R105-02 — cognição forçada:** `DELIVERED` não prova `PERCEIVED` e nenhum dos dois prova crença; revisão como proposta separada e falível.
- **R105-03 — leak de fonte protegida:** view, metadado, ID, distância, logs, embeddings e prompt precisam de ACL/redaction anterior à emissão.
- **R105-04 — fonte ecoada e falsos consensos:** identificar famílias de proveniência DEC-089; múltiplos rumores derivados da mesma origem não independem entre si.
- **R105-05 — tempo/branch/epoch:** não misturar versões, cronologias, save restores, Knowledge Packs ou canais de outro ramo.
- **R105-06 — replay e incerteza:** outbox/CAS, idempotência por destinatário e revisão; `DISPATCHED/UNCERTAIN` somente reconciliação.
- **R105-07 — efeito mecânico indevido:** crença/errata não restitui bens, altera reputação do host ou modifica quests; novos efeitos apenas via gates/receipts próprios.
- **Estado real:** 144 cenários T105-001..144 **NÃO EXECUTADOS** em BG2:EE/EEex/host+2 clientes; `correction_diffusion_*` é referência puramente sintética.

## Riscos e evidências pendentes — DEC-106/C (Discovery v10.2)

- **R106-01 — restauração global indevida:** recuperar valor de reputação para todos apaga diversidade de crenças e contextos DEC-030. Exigir `ReputationContext` por comunidade/região/relação e recibo para cada ação.
- **R106-02 — dano presumido:** perda alegada não é dano comprovado; fonte independente, nexo causal e host receipts necessários antes de propor reparação material.
- **R106-03 — coerção de confiança, perdão ou confissão:** NPC/PC preserva autonomia; nenhum pedido implica aceitação. Consentimentos legítimos e gates próprios.
- **R106-04 — reparação ou restituição fabricada:** planejamento não é pagamento; ownership, recursos, Saga DEC-095, Action Gateway e confirmação host.
- **R106-05 — alcance social imaginado:** errata enviada, entregue, percebida e aceita são coisas diferentes; evitar broadcast instantâneo e pontuação social global.
- **R106-06 — vazamento reputacional:** publicações não revelam origem protegida, alias, refúgio, testemunha ou dossiê bruto; ACL/redaction antes de prompt/cache/log.
- **R106-07 — stale save e duplicação:** branch/lineage/epoch, CAS/fencing/outbox/idempotência; `UNCERTAIN` exige reconciliação, nunca retry cego.
- **R106-08 — POC inexistente:** T106-001..148 são **candidatos NÃO EXECUTADOS em BG2:EE/EEex/host+2 clientes**; testes Python são sintéticos, não demonstram reputação nativa, relações ou ações econômicas reais.

**Dependência de implementação:** validar compatibilidade por build, legitimidade de fontes, consentimento de NPC/PC, percepção e efeitos host-confirmed antes de liberar qualquer escrita de reputação ou restituição.

### Integração DEC-107/C — Riscos de mediação sem consentimento

**R-MED-107:** confissão atribuída indevidamente, mandato fictício, facilitador interessado, silêncio equiparado a culpa, vazamento de dossiês, aceite implícito, execução patrimonial ou reputacional sem recibo, duplicação em save/load. Mitigar com registry autenticado de papéis e provas independente da requisição, ACL e redação, consentimento por parte/termo, auditoria versionada, gates HIGH, `UNCERTAIN` fail-closed e Action Gateway. POCs do motor e dois clientes **NÃO EXECUTADOS**. ADR-0102 / doc.107.

### Integração DEC-108/C — Riscos de monitoramento de acordos

**R-FUL-108:** cláusula não committed tratada como exigível; claim escrito como receipt de host; atraso DR transformado em veredito; fake receipt; pagamento duplicado após timeout/save-load; dedup insuficiente por action ID; entrega em outra campanha usada como prova; mandato ou aceite vencido; compensação sem autorização; sigilo de fontes exposto em avisos; força maior presumida; crédito de item/ouro inexistente. Mitigações: `AgreementRegistry` independente, revisão/term accepted, receipts autenticados, ledger imutável, `UNCERTAIN` em quarentena, CAS/fencing, ACL por audiência, prazo DR, contraditório, emendas por novo aceite e Action Gateway. **Pendente:** POC do motor com dois clientes; 160 cenários T108 candidatos NÃO EXECUTADOS. ADR-0103, doc.108.

### Integração DEC-109/C — Riscos de grafos condicionais multipartes

- **R109-01 — cascata indevida:** dependência satisfeita não autoriza pagamento, entrega ou escolta; proposta e host receipt separados.
- **R109-02 — prova fabricada:** claims, boatos, logs e texto da LLM não substituem receipts DEC-108 vinculados a term/revision/branch/epoch.
- **R109-03 — ciclo/deadlock e starvation:** verificar DAG, detectar ciclos, aplicar DEC-093/094 sem cancelar decisões ou retirar propriedade de PCs.
- **R109-04 — parcialidade e limiares inventados:** seis/dez não satisfaz entrega integral; partial thresholds só via cláusula expressa e committed.
- **R109-05 — autorização transitiva:** commit do contrato e autorização do predecessor não concedem autoridade sobre o sucessor; grants e capabilities independentes.
- **R109-06 — double spend e replay:** idempotência, ownership/fencing, save epochs e receipts únicos; `UNCERTAIN` bloqueia retry.
- **R109-07 — confusão entre tempo e culpa:** janelas DR não presumem inadimplência, execução, multa ou reputação negativa.
- **R109-08 — vazamento e coerção:** ACL e mandatários por termo, nomes protegidos e zero imposição de consentimento aos PCs/NPCs.

**Pendência verificável:** T109-001..168 são cenários candidatos **NÃO EXECUTADOS** no host/EEex + dois clientes. Testes de referência apenas sintéticos. A decisão não aprova escrow; **DEC-110 EM ABERTO**.

## Integração DEC-110/C — riscos de custódia e handoff (v10.6)

**Novos riscos:** interpretar promessa como depósito, depósito sem recibo, double-spend, inventário de PC ou quest transferido, perda de ownership, disputa adjudicada pela LLM, confusão de epochs e desync multiplayer. Controles: receipt autenticado, capability manifest por build, owner consent por ação, `UNCERTAIN` fail-closed, rastreabilidade e revisão do escrow ledger. Não há POC comprovada; 176 candidatos T110 não executados. O questionário SPEC P0 cobre justamente as lacunas de integração, testes e observabilidade em aberto.
