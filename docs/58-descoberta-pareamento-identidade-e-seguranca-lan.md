# DEC-058 — Descoberta, pareamento, identidade e segurança de nós LAN

**Pacote:** Infinity AI Discovery **v5.4**. Complementa **ADR-0053**, DEC-057 e DEC-028. **Documento de Discovery: contratos, fluxos e testes abaixo são propostas para SPECS, não implementações validadas.**

## 1. Objetivo e fronteiras de confiança

A execução `SINGLE_HOST` permanece o padrão inicial. A distribuição opcional `LAN_OPTIONAL` permite usar nó de inferência ou simulação por lotes, que **não é outro host de BG2:EE** e não possui autoridade para alterar saves, flags, NPCs, controles de jogadores ou estado mecânico. A LAN é tratada como **potencialmente hostil**, inclusive se residencial.

```text
         Rede LAN (anúncios não confiáveis)
  worker A   worker B (falso)   worker C (revogado)
      |           |                  |
      +-----------+------------------+
                  | descoberta ≠ autorização
                  v
        [Registro de descoberta isolado]
                  |
           verificação de identidade
           + aprovação do anfitrião
                  |
                  v
     [Registro de confiança por campanha]
       identidade / escopos / época
                  |
      [Canal protegido + autorização]
                  |
                  v
[Broker de jobs] --(contexto ACL mínimo)--> [Worker de proposta]
       |                                         |
       +<--(retorno verificado e não autoritativo)-+
       |
    [Orquestrador + gateway no host] ---> [BG2:EE host confirma mecânica]
```

A imagem é um **desenho proposto** e não indica APIs suportadas pelo jogo. Descoberta e pareamento aplicam-se a workers de IA; a conexão multiplayer nativa do BG2:EE tem fluxo próprio, cujo comportamento de segurança não é alterado por esta ADR.

## 2. Ciclo de vida de um nó

| Estado | Descrição | Operações admitidas |
|---|---|---|
| `DISCOVERED_UNTRUSTED` | Anúncio recebido sem identidade confiável | Exibir metadados mínimos, **sem** jobs, dados privados ou comandos |
| `PENDING_VERIFICATION` | Anfitrião iniciou pareamento; identidade precisa ser verificada | Negociar prova de identidade por fluxo dedicado; sem conteúdo de campanha |
| `PAIRED_RESTRICTED` | Identidade aprovada, escopos ainda restritos | Configuração de capacidades consentidas e verificações de canal |
| `ACTIVE` | Autorização válida + canal protegido + capability checks | Somente jobs allowlisted com contexto minimizado |
| `SUSPENDED` | Desconexão, problema operacional ou suspensão voluntária | Não aceitar despachos novos; revalidação para retorno |
| `QUARANTINED` | Suspeita de invasão, spoofing, alteração de chave ou resposta anômala | Bloqueio de novos jobs/resultados; retenção mínima da evidência e revisão |
| `REVOKED` | Autorização cancelada ou identidade invalidada | Sem jobs/resultados aceitos; nova identidade/pareamento necessário |

Revogação não remove cópias locais de dados já recebidos pelo nó. Um worker comprometido que tenha visto um segredo continua sendo risco residual; por isso o broker não envia todos os dados do mundo.

## 3. Fluxo proposto de pareamento

1. **Opt-in da LAN:** anfitrião habilita descoberta local; a topologia SINGLE_HOST funciona sem ela. Fazer binding somente a interfaces previstas, não automaticamente à internet.
2. **Anúncio não confiável:** coletar ID alegado, capacidade declarada, endpoint e evidências permitidas. Nenhum anúncio recebe token ou dados de jogador.
3. **Confirmação de posse da identidade:** validar identidade usando um método robusto **a selecionar** em SPECS; exibição de código comparável nos dois dispositivos ou outra prova fora de banda é candidata, não requisito de implementação já decidido.
4. **Consentimento humano:** apresentar ao anfitrião identidade verificável, capacidades requisitadas, riscos e escopo da campanha; **aprovação expressa**. Ausência/cancelamento = rejeição.
5. **Autorização limitada:** criar registro com permissões por serviço, campanha/mode, limite de contexto, validade e versão da política; nó LLM não recebe permissão de acessar arquivos de save ou banco bruto.
6. **Canal protegido:** apenas estabelecer rota operacional após autenticação de ambos e proteção de integridade/confidencialidade. Revisar downgrade e substituição de chave.
7. **Heartbeat/monitoramento:** validar estado e autorização nos jobs, não somente no pareamento inicial; detector de anomalia envia evento ao World Health Monitor.
8. **Revogar/rotacionar:** bloquear imediatamente novos despachos; invalidar credenciais e resultados antigos no broker e revisar trabalhos em trânsito. Rotação e recuperação de chaves são caminhos distintos de autorização automática.

## 4. Envelope de autorização e contrato ilustrativo

Este exemplo descreve campos lógicos, **não** autenticação pronta nem API aprovada. A proteção real será implementada por mecanismo testado, nunca por confiar em valores recebidos no próprio payload.

```yaml
node_id: node-02
node_identity_fingerprint: verificavel-no-canal-nao-no-json
campaign_id: campaign-A
mode: LIVING_WORLD
session_id: session-17
build_fingerprint: sha256-...
branch_id: branch-03
input_revision: 172
permission_epoch: 5
service_role: llm_inference
allowed_job_type: dialog_suggestion
privacy_scope: npc-dialog-public-context-only
request_id: req-unique
job_idempotency_key: job-unique
input_digest: sha256-of-minimized-payload
result_authority: PROPOSAL_ONLY
policy_revision: 9
```

**Validações obrigatórias propostas:** identidade do canal e do nó pareado, período de autorização, permissão por `service_role`, destino, modo/campanha, revisão/branch/build, ACL antes de criar o payload, schema e digest ao receber, origem de resposta e antirreplay. Um `node_id` autodeclarado não autentica o trabalhador. Assinatura de mensagem e autenticação de canal são mecanismos diferentes e ainda não selecionados.

## 5. Matriz de dados e capacidades

| Categoria de dado/ação | Worker LLM/simulação | Regra |
|---|---|---|
| Texto necessário e **permitido** para uma inferência | Condicional | ACL + minimização antes do envio, escopo por job |
| Segredo de outro PC, player ou NPC | Não por padrão | Só se legitimamente autorizado para a finalidade e destinatário |
| Snapshot completo de campanha | Não por padrão | Exige decisão e gates novos para transferência stateful |
| Save BG2:EE, scripts/flags mutáveis e credenciais do host | Não | Autoridade host e Action Gateway; worker não acessa diretamente |
| Proposta de fala, classificação ou cenário simulado | Sim | Validação posterior; jamais um efeito mecânico confirmado |
| Comando shell, Lua livre, patch em save, alteração de ACL | Não | Gateway tipado e controles específicos; IA não pode conceder privilégios |
| Logs, erro, prompt, cache/telemetria | Restritos | Evitar payload sensível, isolar por campanha, retenção minimizada |
| Dados de campanha Original | Não para serviço Living World | Modo Original separado; filtro de modo antes do despacho |

## 6. Defesas de rede e ciclo de confiança

- **Descoberta:** preferir mecanismos limitáveis ao escopo LAN, com lista de endpoints aprovada; nunca abrir automaticamente uma porta para WAN. Nenhum broadcast de contextos privados.
- **Identidade:** credencial criptográfica própria; endpoint IP/hostname são apenas meios de conexão, não identidade. Negar aceitação silenciosa de chave nova, chave vencida ou acesso sem autenticação.
- **Confidencialidade/integridade:** usar transporte autenticado e criptografado com propriedades demonstradas. mTLS é exemplo candidato, sem aprovação de stack/cifra/PKI neste Discovery.
- **Permissões:** menor privilégio por tarefa e expiração/revisão. Um nó comprometido não pode promover a si mesmo a gateway ou administrador da campanha.
- **Proteção contra replay e stale:** validar `permission_epoch`, `branch_id`, revisão, deadline, idempotência, estado de nó e identidade de resposta; cache compartilhado tem de preservar separação e ACL.
- **Revogação:** broker/quadro de permissões revalida identidade e escopo antes de liberar novos jobs **e antes de aceitar resultados**; enfileiramentos/retries de um nó revogado são isolados. Limites para revogação durante trânsito serão testados; não alegar garantia absoluta de bloqueio no sistema operacional remoto.
- **Partições:** não eleger segundo host ou assumir que timeout implica nenhuma execução. Tarefa somente calculada e descartável pode ser refeita com critérios de segurança; side-effect `UNCERTAIN` exige reconciliação.
- **Segredos em repouso:** chaves de nó, credenciais e dados temporários exigem armazenamento local e limpeza seguros, mas solução específica é tema de SPECS.

## 7. Integração com componentes existentes

- **DEC-011/012:** gateway e receipts de host; worker só propõe.
- **DEC-028:** ACL na recuperação e antes da transmissão, nem mesmo um nó confiável deve receber segredos fora do escopo do job.
- **DEC-053/054:** checkpoints e backups continuam sob autoridade da campanha; não migrar stateful para LAN por causa do pareamento.
- **DEC-055:** incidentes de autenticação, identidade ou vazamento = `DEGRADED`, `QUARANTINED` ou `UNKNOWN` com alerta mínimo; nenhuma autorreparação agressiva.
- **DEC-056:** filas/quotas apenas para nós atualmente autorizados, sem privilegiar rapidez em relação a segurança ou privacidade.
- **DEC-057:** topologia de máquina única continua primeira POC e não exige configurar rede.
- **DEC-006:** políticas de modelo e eventual API remota ainda estão abertas; autorização LAN **não** equivale a autorização para cloud.

## 8. Critérios de aceitação e testes candidatos (26)

| ID | Caso | Resultado esperado |
|---|---|---|
| T-058-01 | SINGLE_HOST sem LAN | Serviços locais independem de descoberta/pairing remoto |
| T-058-02 | Descoberta de nó legítimo não pareado | Exibido como não confiável; zero dados de campanha |
| T-058-03 | Anúncio falso com nome parecido | Não recebe identidade privilegiada ou job |
| T-058-04 | Anfitrião cancela pareamento | Estado retorna a não autorizado; nenhum token de job emitido |
| T-058-05 | Pareamento explícito válido | Identidade verificada e permissões mínimas vinculadas |
| T-058-06 | Endpoint muda de IP preservando identidade | Aplicar política de reconexão sem conceder novo privilégio implícito |
| T-058-07 | Chave muda inesperadamente | Bloquear e exigir revalidação; alertar |
| T-058-08 | Dispositivo tenta personificar nó aprovado | Rejeitar canal/resultados por identidade |
| T-058-09 | Interceptação ou adulteração de payload | Proteção do canal deve impedir aceitação |
| T-058-10 | Downgrade para texto claro | Falhar fechado e não transmitir contextos |
| T-058-11 | Reutilização de autenticação/nonce | Rejeitar replay conforme mecanismo adotado |
| T-058-12 | Worker LLM pede acesso a save/DB | Negar; permissão não contempla recursos privilegiados |
| T-058-13 | Worker de uma campanha acessa outra | Bloquear ACL cross-campaign e logs/caches |
| T-058-14 | Modo Original versus Living World | Impedir mistura dos respectivos contextos |
| T-058-15 | Diálogo com segredo oculto de PC | Nunca enviar segredo sem autorização específica antes da recuperação |
| T-058-16 | Logs/erro contêm token ou segredo | Diagnóstico deve ocultar informações proibidas |
| T-058-17 | Revogar nó com fila pendente | Cancelar/desabilitar despachos e rejeitar respostas pós-revogação |
| T-058-18 | Revogar nó durante inferência | Não aceitar resposta tardia; registrar status para auditoria |
| T-058-19 | Resultado de epoch/branch/build anterior | Rejeitar do caminho ativo; sem reexecutar mecânica |
| T-058-20 | Retorno adulterado/com esquema inválido | Isolar, alertar e manter integridade de narrativa |
| T-058-21 | Perda de LAN durante job sem side effect | Desabilitar capacidade ou refazer somente quando seguro |
| T-058-22 | Receipt do host em `UNCERTAIN` | Nunca retry cego após partição |
| T-058-23 | Worker injeta instruções em output | Tratar output como dado; gateway não executa comando livre |
| T-058-24 | Worker malicioso simula privilégio de administrador | Rejeitar, conter e registrar identidade |
| T-058-25 | Host BG2:EE + dois clientes com worker LAN | Sem transferência de autoridade e com sincronização verificada em POC futura |
| T-058-26 | Recuperação de checkpoint após revogação de nó | Restaura apenas ramo e estado legítimos, sem resultado de nó revogado |

## 9. Abertos para SPECS, threat model e provas

1. Protocolo/SDK de transporte, modelo de chaves (geração, guarda, rotação), autenticação mútua, método efetivo de pareamento e UX de confirmação.
2. Discovery service, portas, firewall, isolamento de interfaces, compatibilidade Windows e diferentes sistemas dos workers.
3. Limites de nós, cert expiry, timeout, retry seguro, reconexão, sandbox e proteção de cache temporário.
4. Metas de rede/latência/perda, impacto em FPS e saturação CPU/GPU com dois clientes, a partir de medição.
5. Regras concretas para cancelamento e revogação durante jobs em voo; threat model para dispositivos previamente autorizados e comprometidos.
6. Casos de processamento de dados privados em nós, consentimento, política de retenção e eventual revisão de DEC-006.
7. **Nenhum teste foi executado**: os casos acima são plano, não alegação de suporte BG2:EE/EEex ou robustez criptográfica.

**Próxima decisão proposta: DEC-059 — política de roteamento entre modelos locais/nós por sensibilidade, capacidade, latência e fallback, articulando a DEC-006 ainda aberta.**

## DEC-059 — Roteamento somente entre identidades e capacidades autorizadas

A descoberta/pareamento da DEC-058 antecede qualquer job. O router só considera nós `ACTIVE` e escopo vigente para `campaign_id`, tipo de job, contexto, versão, `permission_epoch` e canal protegido. O ranking por qualidade/recursos ocorre depois desse filtro. Revogação e alteração de ramo invalidam resultados. Se não houver nó autorizado para determinado segredo, processar no host somente se permitido ou deixar pendente. Cloud permanece não autorizada por padrão; DEC-006 aberta. Ver ADR-0054/doc. 59.

### Integração DEC-066/C — distinguir identidade LAN de identidade NPC (v6.2)

Credenciais de nó LAN autenticam **computadores**, não NPCs. Uma proposta de match produzida em nó pareado ainda deve passar por evidências mecânicas, campanha/branch/build, política de risco e ACL; falha/revogação invalida respostas tardias. Nenhuma confiança em hostnames/IPs para inferir NPC narrativo.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: dados de viagem privados trafegam somente com identidade de nó e autorização vigente; revogação invalida resultados pendentes do worker.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070: nó LAN pareado pode sugerir incidente apenas com ACL válida; não executa combate nem recebe segredos além do mínimo. Revogação invalida trabalho ainda não confirmado.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Pareamento LAN não concede permissão para spawn ou decisão de handoff DEC-071. Revogação de nó invalida propostas pendentes e tokens antigos, com reconciliação caso haja operação mecânica em estado desconhecido.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Mesmo nó LAN pareado DEC-058 não tem permissão para instalar recursos, executar scripts ou conferir receipts DEC-072; propostas submetidas ao host e ao catálogo local.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Nó LAN pareado não possui acesso automático às identidades privadas; credenciais são necessárias e insuficientes sem ACL por campanha/finalidade. Revogação invalida jobs com segredo.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Documento oficial fictício não substitui autenticação de sistema: nós LAN DEC-058 devem estar pareados e autorizados para contexto do pedido; revogação invalida jobs.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Pareamento LAN não concede competência jurídica nem acesso a mandados secretos DEC-080; origem e audience autorizados por caso, revogação invalida jobs futuros.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Pareamento LAN não concede automaticamente acesso a danos pessoais, pedidos de compensação, identidades ou comandos mecânicos; revogação invalida jobs.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Pareamento de nó não autoriza acesso amplo a denúncias, credenciais de autoridade ou execução de sanção. Revogação invalida propostas pendentes.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Nó pareado não ganha acesso universal a fontes; roles e ACL por campanha/purpose, revogação invalida jobs e cache pendentes.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Pareamento LAN não concede leitura de refúgio/itinerário; revogação impede receber ou executar plano obsoleto.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Pareamento não dá direito de consultar identidade/refúgio; papel, necessidade, revogação e idempotência são conferidos em toda consulta.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Nó pareado não recebe verdade de contraespionagem por default. Revogação invalida jobs e caches que contenham informação reservada.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Pareamento LAN não concede por padrão acesso a lealdades secretas, listas de fontes ou promessas de jogadores.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Pares LAN autenticados não obtêm identidades de informantes por mera conexão; aplicar ACL granular e cancelar jobs após revogação.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Nó LAN pareado não herda ACL da biblioteca de evidências; revogação invalida trabalho atrasado e cache de fonte protegida.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Pareamento técnico de worker não concede permissão a fontes protegidas ou dossiês; aplicar role, finalidade e ACL antes de processamento/caches do nó.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Papel LAN autorizado não implica visibilidade irrestrita de dossiês, planos ou identidades; revogação invalida jobs pendentes.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Revogação de pareamento ou conexão LAN bloqueia novos despachos sensíveis; filas antigas são invalidadas com fencing/epoch.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Pareamento do worker não lhe concede autonomia de alocar NPCs/PCs; token e ACL por operação/branch, cancelamento de jobs stale e minimização do payload.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Pareamento LAN não concede acesso a diagnósticos secretos de reservas; roles/ACL e fencing condicionam operações sensíveis e jobs antigos perdem autoridade.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-096/C — Discovery v9.2

Pedidos de aplicação de regra DEC-096/C seguem envelope de sessão autenticada/epoch e receipt válido, nunca mero relato narrativo.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

A confirmação de aplicação mecânica da composição DEC-097/C exige mensagem autenticada + epoch e receipt host válido.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Reconexão multiplayer exige snapshot e receipts do host; cliente defasado não pode re-materializar nem sobrescrever epoch.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

A sessão pareada não confere autoridade sobre instâncias do host; ACL do bridge deve ser explícita.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Host e clientes devem manter segregação de audiências e não confiar em atestado de probe gerado por cliente.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** DEC-101 interpretation is read-only, version-pinned and independent of gateway/host execution. A confirmed semantic milestone does not authorize actions or prove a command receipt; mod upgrades, checkpoint restore, revised mapping, epoch mismatch or contradictory states cause fail-closed reconciliation. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

A DEC-102/C trata divergências entre milestone validado do host e projeção derivada do Living World: exigir mapeamento DEC-101, observação DEC-100, epoch/branch e receipts, e preservar o host, facts ledger e conhecimento dos NPCs. Somente proposta de revisão CAS/autorizada; detalhes em ADR-0097/doc. 102. **Sem POC mecânica.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **segurança em LAN**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para LAN autentica emissores e não divulga conteúdo por observabilidade, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para LAN e recibos de comunicação autenticados, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
