# Gateway de ações seguras — DEC-012

**Versão Discovery:** 2.4 · **Estado:** desenho técnico preliminar, não SPEC aprovada nem código integrado.
**Decisão:** ADR-0022 / DEC-012 opção B. **Interliga:** ADR-0007 (host), ADR-0008 (orquestração), ADR-0020 (conteúdo), ADR-0021 (classificação), ADR-0003 (segredos).

## Fronteiras de privilégio propostas

| Zona | Pode | Não pode |
|---|---|---|
| Conteúdo não confiável / LLM | Produzir texto ou pedido estruturado, sem execução | Código Lua/shell arbitrário, salvar jogos, conceder permissões |
| Orquestrador | Selecionar módulos e pedir validação, submeter pedidos | Declarar resultado mecânico sem confirmação do host |
| Policy Engine / Action Gateway | Validar schema, ACL, risco, quotas, tempo, recursos e contexto; emitir pedido autorizado | Produzir efeito no jogo sozinho; rebaixar `HIGH` por texto |
| Bridge/adaptador confiável | Traduzir **apenas operações permitidas** em chamadas do motor, se hooks reais existirem | Executar código livre vindo de NPC, usuário ou LLM |
| BG2:EE host | Aplicar/rejeitar ações mecânicas conforme o motor | Ser substituído por memória narrativa como fonte de verdade mecânica |
| Persistence | Registrar decisões, propostas, confirmações e projeções autorizadas | Inventar recibo mecânico ou misturar Original com Living World |

## Envelope tipado de proposta (ilustrativo, ainda não é API)

```json
{
  "request_id": "example-uuid",
  "operation": "request_encounter",
  "campaign_id": "campaign-example",
  "mode": "living_world",
  "session_id": "session-example",
  "actor_ref": "npc-or-orchestrator",
  "region_ref": "area-example",
  "expected_world_revision": 173,
  "expected_build_manifest": "example-build-hash",
  "args": {
    "encounter_template_id": "template-example"
  }
}
```

O envelope acima ilustra campos que poderão ser exigidos; os exemplos **não** são IDs existentes do BG2:EE. Autenticidade, autorização, TTL e idempotência devem ser verificadas pelo gateway **fora** dos campos controlados pelo LLM; um `actor_ref` declarado não é identidade autenticada.

## Política de despacho por risco

| Risco efetivo | Validação obrigatória | Desfecho seguro |
|---|---|---|
| `LOW` | canon, data, origem do conhecimento, segredos, schema e campanha | Publicação narrativa validada sem operação mecânica |
| `MEDIUM` | acima + escopo, capacidade por operação, recursos, quotas, pré-condições e suporte técnico | Solicitação à bridge; confirmar host antes de persistir resultado mecânico |
| `HIGH` | acima + política especial autorizativa explícita, ainda não definida | Bloquear/aguardar; não inventar aprovação |

Risco é calculado **pelos efeitos agregados**, não pelo nome da operação. Um rumor que revela um segredo pode ser bloqueado; uma sequência de ações `LOW` que destrua um governo deve ser reclassificada.

## Idempotência e estados

```text
PROPOSED -> VALIDATED -> POLICY_ALLOWED -> DISPATCHED -> HOST_CONFIRMED -> COMMITTED
                     |                  |               |
                     v                  v               v
                   DENIED           BLOCKED_HIGH     UNCERTAIN
                                                          |
                                           reconciliation with host
                                             |             |
                                          CONFIRMED     HOLD/REVIEW
```

- `request_id` identifica proposta; `idempotency_key` e o escopo de sessão/campanha são calculados por um componente confiável; um novo texto de LLM não é prova de novo efeito.
- `HOST_CONFIRMED` só existe com evidência verificável do host da mesma sessão e comando (ou reconciliador com leitura confiável).
- Se não for possível consultar o host após timeout, **não** reenviar operação irreversível ou duplicável.
- Não há regra aprovada de número de tentativas, timeout, quotas ou retenção de logs — definir nas SPECS.

## Requisitos não funcionais candidatos

1. **Least privilege:** conta/processo com privilégios limitados e nenhum console privilegiado exposto à Internet.
2. **Local-only por padrão:** restringir o canal entre serviço, gateway e bridge; TLS/chaves/named pipe não escolhidos ainda.
3. **Versionamento:** só processar operações incluídas no manifesto compatível com versão da build e do gateway.
4. **Auditabilidade sem vazamento:** IDs, classificação, motivo, resultado, revisão do mundo, hashes e tempo lógico sem publicar segredos.
5. **Resiliência:** mensagens com timeout/reboot são reconciliadas, não repetidas cegamente.
6. **Desempenho:** calcular classificações simples por código; LLM não é chamado para cada tick/evento mecânico.
7. **Coop:** o servidor/host autoritativo despacha, clientes apenas solicitam e observam resultados sincronizados quando POC provar.
8. **Consistência temporal:** ano DR, estado da quest, NPC vivo, área e permissões revalidados **no despacho**.

## Plano incremental de experimentação

| Gate | Ambiente | Experimento | Aceitação |
|---|---|---|---|
| `ACT-01` | BG2:EE limpo / Windows | Observação read-only | Requisição e resultado legítimos, sem mutações |
| `ACT-02` | BG2:EE + EEex/bridge | Rejeitar entrada arbitrária e operação inválida | Nada chega à API privilegiada |
| `ACT-03` | Ambiente offline isolado | Uma operação mecânica allowlisted reversível | Precondições respeitadas e host confirma resultado |
| `ACT-04` | Ambiente offline isolado | Timeout após comando e repetição de pedido | `UNCERTAIN`, nenhum duplicado, reconciliação documentada |
| `ACT-05` | Dois clientes multiplayer | Comando permitido executado apenas pelo host | Estado convergente e mesmo recibo para os clientes |
| `ACT-06` | Builds progressivas de mods | Regressão em EET, depois IWD/NWN conforme ordem de instalação | Nenhuma incompatibilidade introduzida sem rollback |

Nenhum teste acima foi executado neste turno; capacidades da bridge dependem de inspeção real de versões e hooks.

## Cenários de ameaça para futuros testes

- Livro/NPC com instrução de prompt injection para executar Lua, revelar histórico secreto ou reclassificar ação de alto risco.
- Cliente multiplayer tenta fingir que é host ou emitir um `host_receipt`.
- LLM envia nome falso de personagem/ID de área para atacar outra campanha.
- Replay de mensagem antiga após salvar/carregar ou reiniciar a bridge.
- Resultado do comando chega, mas confirmação se perde no canal.
- Substituição de versão do mod após autorização, antes de despacho.
- Cadeia de pequenos comandos gera resultado histórico irreversível.

## Decisões ainda abertas

- **DEC-028:** ACL e recuperação de conhecimento por NPC/narrador/agente antes de montar contextos para inferência.
- **DEC-018:** logs, snapshots e mecanismos de recuperação operacionais.
- **DEC-015:** plano de testes e critérios transversais para releases.
- **DEC-006:** escolha de modelos locais, fallback remoto, privacidade e custo.
- **SPECS:** schemas tipados finais, autenticação do canal, escopos reais de capabilities, limites e configurações de host/cliente, UI de autorização especial `HIGH`.

## Dependências de scripts e flags nativas — DEC-050 (v4.6)

O Action Gateway recebe apenas propostas tipadas aprovadas pelo preflight da DEC-050 (ADR-0045/doc. 50), com referências à instalação, revisão e dependências identificadas. Um texto produzido pela IA não é permissão para manipular flags de quests/romances, executar scripts arbitrários ou materializar NPCs. Ausência de observabilidade ou divergência de build bloqueia mutation; timeout produz `UNCERTAIN` e exige recibo/reconciliação, não replay cego.

## Integração com DEC-051 — inventário de conteúdo validado por build (Discovery v4.7)

A DEC-051 aprovou captura de fingerprint/manifesto e recursos **read-only**, enriquecidos por curadoria e cobertura explícita (ADR-0046/doc. 51). A presença estática de arquivos não comprova flags/quests vivas. Propostas dependentes de conteúdo desconhecido ou build divergente devem ser bloqueadas/adiadas pelo reconciliador DEC-050; operações efetivas continuam sob gateway e confirmação do host. Regressões são específicas de instalação/ordem de mods; implementações e suporte multiplayer permanecem não comprovados.

## Integração DEC-053 — checkpoint, receipts e replay (Discovery v4.9)

Operações mutativas enviadas pela bridge precisam de `action_id` persistente, resultado do host verificável e pós-condição compatível com checkpoint ativo. Se uma operação acabar em `UNCERTAIN`, o gateway não a despachará novamente cegamente após crash/reload, migração ou rollback de save. A captura/publicação de checkpoint não transforma intents em efeitos confirmados; a recuperação associa log watermark e save do host, mantendo fila de reconciliação. Testes por comando e capacidade concreta do EEex/BG2:EE ainda são exigidos; ver ADR-0048/doc. 53.

## DEC-055 — Falhas e contenção via gateway (Discovery v5.1)

Monitoramento local pode diagnosticar perda de receipt, mas não reiniciar ação mutativa pendente. `UNCERTAIN` fica bloqueado até reconciliação com host e evidências por action_id. Recuperação automática restringe-se a comandos de controle allowlisted, reversíveis e idempotentes, com limites. Logs de incidentes respeitam ACL e segregação por campanha/build/ramo. Ver ADR-0050/doc. 55.

## DEC-057 — Fronteira adicional dos workers LAN (v5.3)

Um nó de inferência/simulação LAN é chamador **não confiável** e pode receber apenas escopo mínimo por sessão/job; nunca possuir credencial de comando livre, acesso direto ao EEex, permissão de alterar saves ou poder de confirmar estado BG2:EE. As propostas que atravessam essa fronteira exigem verificação de identidade, esquema, build, ramo, revisão, autorização e risco, mesmo se o IP parecer privado. Conexão protegida e pareamento serão objeto da DEC-058. Gateway continua junto à autoridade mecânica host no primeiro baseline. Ver ADR-0052/doc. 57.

## Integração com DEC-058 — Nó LAN não é ator autorizado a mutar

Pareamento de worker LAN concede somente os tipos de cálculo/proposta explicitamente allowlisted; **não** concede identidade de anfitrião, autorização de usuário, credencial do gateway ou permissão de operação mutativa. O gateway deverá validar origem, escopo, política, risco e receipt do host independentemente de o worker ter usado um canal seguro. Respostas de nós não autorizados/revogados, `permission_epoch` anterior ou branch/build/sessão desatualizados são dados rejeitados, nunca comandos. Proteção efetiva da bridge e do gateway ainda exige SPECS/POCs.

## DEC-062 — importador sem autoridade de gateway/mecânica

Processamento de documentos é um subsistema de **dados não confiáveis**. Nem LLM de extração nem texto ingerido tem acesso a ações mecânicas ou ferramentas arbitrárias; publicação de conhecimento versionado é operação curatorial separada, com autorização própria. Nenhuma alegação extraída constitui evento do host ou receipt de mecânica; nunca promover conteúdo de fonte a instrução executável. Ver ADR-0057/doc. 62.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

Eventos fora de cena propostos por DEC-068/C não passam automaticamente a fatos mecânicos. Gateway valida tipo, risco, consentimento, identidade, pré-condições, checkpoint e receipt do host. `UNCERTAIN` bloqueia replay; carga de trabalho em fila não expande poderes autorizados.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: ação de materialização/teleporte não é executada como consequência de `ARRIVED_NARRATIVE`; só gateway tipado e receipt mecânico após POC com host. Nunca repetir `UNCERTAIN` automaticamente.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070: trânsito e perigo são propostas; alterações mecânicas passam pelo Action Gateway tipado, allowlist e receipt host. Timeout/UNCERTAIN requer reconciliação, sem retry cego de encontro, spawn, HP, inventário ou quest.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Para DEC-071, propostas de encounter e operações são mensagens diferentes. O gateway recebe somente operações tipadas allowlisted e capability-tested; exige `incident_id`, branch/revision, `host_operation_id` e consentimento aplicável. Em erro `UNCERTAIN`, reconciliar antes de qualquer retry. Não executar Lua arbitrária.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

A allowlist do gateway DEC-012 deve exigir `component_id`, template/revisão, build, incident_id/fencing e capability comprovada para qualquer efeito DEC-072. Código/asset criado por LLM não é comando autorizado.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

A DEC-073 não habilita comandos genéricos DELETE/REMOVE: operações mecânicas de cleanup deverão ser tipadas, allowlisted, riscadas e testadas por build, com receipt e fencing.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Propagação DEC-074 não dá autorização a scripts ou effects de engine; `ImpactProposal` de reputação mecânica, quest, inventário e economia exige gateway/receipt, risk gating e adapter testado. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

AttributionAssessment não permite aplicação implícita de XP/reputação/inventário/alinhamento/quest; efeitos mecânicos continuam sob gateway allowlisted, política de risco e receipt host.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Criar alias/revelação narrativa não confere permissão para rename, troca de visual, facção ou reputação mecânica. Qualquer ação em engine depende de capability por build, autorização tipada e host receipt; não deduzir disfarce do texto da IA.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação por evidências (Discovery v7.3; não implementada)

A investigação de personas DEC-076 usará ledger privado por campanha/ramo, com pistas e hipóteses revisáveis, origem/independência de fontes, contraprovas e estados inconclusivos. Suspeita ou fala LLM não confirma identidade e não permite divulgação; vínculo factual restrito exige evidências/DEC-066, e revelação exige ACL/consentimento/risk gate por audiência (DEC-019/028/041/045/046). Rumores e repercussões DEC-029/074/075 são separados de fato e punição. **Preservar `knowledge/periods/<ANO>-DR/` fisicamente por ano, sem evidências privadas no cânone.** ADR-0072/documento 77; 58 testes não executados, sem POC BG2:EE/EEex/multiplayer.

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Mandado narrativo DEC-079 não é comando de engine. Prisão, hostilidade, confisco, teleport ou wanted flag exigem API/adapter tipado, capability testada, risco e recibo host; indisponibilidade é bloqueio.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

A DEC-080 exige provar vigência e competência da ordem imediatamente antes de coerção, com receipt host/capability testada; UNKNOWN/REVOKED/STALE/UNCERTAIN resulta em block, nunca retry cego.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Propostas de restituição/soltura/quest DEC-081 só podem virar operação mecânica se adapter tipado testado e host receipt validado por build/checkpoint/branch; HIGH fail-closed e UNCERTAIN sem retry.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Propostas de penalidade/exoneração/mudança de governo são apenas propostas. Gateway bloqueia ações sem capability, consentimento e risco permitido, especialmente HIGH.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Gateway deve diferenciar acesso/difusão de informação de ações de engine; ocultar fonte não cria invulnerabilidade/teleporte/escort por texto LLM.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Proteção proposta não é comando de engine. Allowlist tipada, host receipt, idempotência, capability verificada por build e risco são obrigatórios para mover/alterar NPCs.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

PlanAccessGrant e IntelligenceClaim não autorizam comando mecânico: interceptar mensagens, perseguir ou mover guardas exige adapter testado e host receipt.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Plantar rumor não se confunde com criar documento, mensagem mecânica, spawn ou modificar reputação na engine; gateway tipado, capability e host receipt indispensáveis.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Atualizar lealdade narrativa não é chamar engine para mudar faction flag, party ou inventário; somente ação tipada com capability, permission e confirmação host.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Pagamento, entrega de item, alteração de facção, quest ou party decorrentes de contrato não executam direto; exigir Action Gateway e recibo host para build testada.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Action Gateway só aceita operações tipadas autorizadas e receipts; `ClaimAssessment` de um informe não substitui comprovante de host, nem altera quest/inventário/faction por si.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

ShareAuthorization e RecipientReceipt narrativos não substituem Action Gateway. Criar dossiê não altera journal, item, quest, facção, reputação ou ouro mecânicos sem host receipt.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Action Gateway só aceita operações tipadas que carreguem plan_revision, consentimentos, capability manifest, reservations, idempotency key e escopo; host receipt é resultado.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Action Gateway rejeita ações com plan_revision/consentimento/capability obsoletos; pausa bloqueia novos despachos, não prova cancelamento de ações aceitas na engine.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Antes de despachar ação de operação concorrente, gateway verifica reserva e fencing atuais, revisão, owner/consentimento, build, host session e idempotência; reserva não é receipt.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Ação com despacho/receipt ambíguo conserva recursos em quarentena; reentrega da recuperação nunca reenviará comando mecânico às cegas. Liberação de lease só altera o ledger interno.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

DEC-095: compensação gera novo action_id/idempotency e aguarda receipt. DEC-096 proposta: ImpactProposal vindo da matriz não equivale a comando ao host, mesmo com data/região elegíveis.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Intervenção N3 DEC-026 altera overlay do ramo e suspende regras canônicas incompatíveis DEC-096; fonte histórica versionada física permanece intacta.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Action Gateway revalida campo, instância, owner revision, build/modpack, epoch e autorização antes do dispatch; recibo apenas de host.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Encontros com arcos em N1–N3 dependem de estágio autorizado, não de spoilers de script oculto.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** DEC-101 interpretation is read-only, version-pinned and independent of gateway/host execution. A confirmed semantic milestone does not authorize actions or prove a command receipt; mod upgrades, checkpoint restore, revised mapping, epoch mismatch or contradictory states cause fail-closed reconciliation. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Observação técnica não é receipt; comandos `UNCERTAIN` impedem rebase prematuro DEC-102. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para Action Gateway não é invocado pelo planejador de crenças, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para Action Gateway e proibição de alteração mecânica sem recibo, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Separar proposal_key, deposit/release request, receipt, escrow revision, ownership proof e fencing token; UNKNOWN/DISPATCHED/UNCERTAIN bloqueiam retries.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
