# DEC-011 — Modelo preliminar de autoridade, eventos e consistência

**Versão:** Discovery 0.8 · **Status:** desenho candidato para SPECS, subordinado ao ADR-0007 aprovado. **Não implementado / não testado.**

## Responsabilidades por domínio

| Domínio | Autoridade definida na DEC-011 | Origem da evidência / ressalva |
|---|---|---|
| HP, dano, combate, itens, magias, criaturas e posições | Host do jogo | Leitura e confirmação dependem de EEex/bridge e testes multiplayer |
| Histórico, revisões, segredos, relações e ganchos | Serviço narrativo do Infinity AI | Sujeito a políticas DEC-004, DEC-019 e DEC-020 |
| Missões e eventos dinâmicos | Proposta pela IA; fatos confirmados no registro externo somente após evidência relevante | Missões puramente narrativas versus ações mecânicas exigem contratos diferentes |
| Registros e memória persistente | Infinity AI para o domínio narrativo; jogo/saves para o domínio mecânico | Convergência e procedimentos de backup pendentes |
| Comandos para o jogo | Bridge controlada, somente operações autorizadas | Sem execução de Lua arbitrário de LLM |
| Tela de cada jogador | Projeção do estado, não fonte autoritativa | Testes com dois clientes ainda não realizados |

## Vocabulário de evento (proposta, NÃO contrato final)

- `ActionProposal`: desejo/hipótese de um agente, sem efeito confirmado.
- `ActionIntent`: pedido validado e identificado como pendente.
- `CommandDispatched`: comando encaminhado à bridge, sem sucesso mecânico presumido.
- `EngineObservation`: evidência obtida do host ou do estado do jogo (se tecnicamente disponível).
- `ActionConfirmed`: efeito conferido conforme regra específica do comando.
- `ActionRejected`: operação bloqueada por validação ou rejeitada de forma verificável.
- `ActionUncertain`: retorno ausente ou insuficiente; proibido retry com efeito colateral antes da reconciliação.
- `NarrativeFact`: fato confirmado do mundo, com fonte, escopo e regras de visibilidade.

## Fluxos candidatos para POCs

1. **Leitura somente:** obter estado básico e confirmar que a resposta é da build/sessão correta.
2. **Escrita local controlada:** criar um efeito descartável, ler o resultado e verificar se é reversível.
3. **Timeout artificial:** despachar comando, perder resposta e detectar estado incerto sem duplicar recompensa.
4. **Multiplayer:** conferir efeito no host e nos clientes A/B e repetir o teste após save/reload.
5. **Segredos:** impedir que um diálogo, log de jogador ou evento público apresente histórico privado sem revelação autorizada.
6. **Modos:** conferir que testes do Living World não modificam saves do Original.

## Questões pendentes para as SPECS

- Como identificar o host e obter confirmação confiável por tipo de comando?
- Quais ações são idempotentes, reversíveis ou irreversíveis?
- Quando o evento narrativo pode ser confirmado sem uma alteração mecânica?
- Como reconciliar save de BG2:EE com banco externo após crash/reload?
- Quais logs podem armazenar informações secretas e sob quais permissões?
- Como detectar divergência e impedir duas aplicações do mesmo comando?
- Qual fallback ao detectar falta de suporte multiplayer do EEex para uma ação?

## Rastreabilidade

- Aprovada: `decisions/ADR-0007-autoridade-dividida-e-consistencia-do-estado.md`.
- Gates originais: `07-plano-de-integracao-progressiva.md`.
- Pendências: DEC-008, DEC-012, DEC-014, DEC-015, DEC-018.

## Conciliação de roteiro nativo e propostas — DEC-050 (v4.6)

Para efeitos narrativos que colidam com estado de quests, banters, romances ou companion, o reconciliador determinístico (ADR-0045/doc. 50) não substituirá o host como autoridade. `PROPOSED`, `DEFERRED` e `DIVERGENCE_REVIEW` não representam efeitos mecânicos; `COMMITTED` depende da fonte autoritativa apropriada. Estado de flags desconhecido e `UNCERTAIN` exigem bloqueio da mutação e reconciliação antes de qualquer retry.

## Integração com DEC-051 — inventário de conteúdo validado por build (Discovery v4.7)

A DEC-051 aprovou captura de fingerprint/manifesto e recursos **read-only**, enriquecidos por curadoria e cobertura explícita (ADR-0046/doc. 51). A presença estática de arquivos não comprova flags/quests vivas. Propostas dependentes de conteúdo desconhecido ou build divergente devem ser bloqueadas/adiadas pelo reconciliador DEC-050; operações efetivas continuam sob gateway e confirmação do host. Regressões são específicas de instalação/ordem de mods; implementações e suporte multiplayer permanecem não comprovados.

## Checkpoints coerentes e recuperação — DEC-053 (Discovery v4.9)

ADR-0048 define que `ActionConfirmed` mecânico requer evidência do host e que `NarrativeFact` não é uma alteração de save. Um checkpoint **publicado** liga save mecânico comprovado a snapshot/revisão/watermark narrativo por campanha, modo, ramo e build. Nenhum rollback entre motor e banco é presumido atômico. Candidato parcial/`UNCERTAIN` é não recuperável; eventos posteriores a save antigo seguem ramo isolado, preservando auditoria e segregação de segredos. Para reentrada, comparar IDs, integridade e receipts, sem duplicação por replay. Operação concreta, APIs do motor e testes host+2 clientes seguem sem POC; ver documento 53 e DEC-018 aberta.


## Complemento DEC-054 — autoridade em backups e recuperação (Discovery v5.0)

Backup é cópia de checkpoint certificado pela DEC-053, não recibo do host sobre evento novo. A restauração real precisa de autorização do anfitrião e observação consistente do motor; um ensaio de backup não publica alterações no jogo ativo. `UNCERTAIN` permanece pendente mesmo após recuperar bytes íntegros. Logs de operação devem respeitar a ACL DEC-028 e não expor histórico secreto ou caminhos privados. Ver ADR-0049/doc. 54.

## DEC-055 — Monitoramento e autoridade após falhas (Discovery v5.1)

A saúde do processo não constitui confirmação de efeitos mecânicos. Um timeout do host ou da bridge exige marcar ação `UNCERTAIN`, preservar action_id e recibos/evidências e impedir retry destrutivo. O World Health Monitor pode alertar e executar apenas recovery LOW previamente autorizado; o host confirma estado mecânico, o anfitrião autoriza recuperações HIGH e a camada narrativa registra somente fatos com lastro. Ver ADR-0050/doc. 55.

## DEC-057 — Localização física não altera autoridade (v5.3)

Uma inferência ou lote computado em nó LAN é somente `PROPOSED`, mesmo quando a rede é local. `CONFIRMED` para mutação mecânica exige gateway autorizado e evidência do host BG2:EE. Resposta tardia, sessão errada, revisão de mundo vencida ou nó não autorizado não pode ser incorporada ao ramo corrente. Um timeout de serviço não justifica repetir mutação com receipt ausente (`UNCERTAIN`). A futura DEC-058 cuidará da confiança do transporte; ver ADR-0052/doc. 57.

## DEC-058 — Identidade do worker não altera autoridade do mundo

Um worker LAN pareado é autorizado **somente para computação delegada**, não para confirmar estado mecânico nem criar fatos narrativos sem validação. Retornos devem corresponder à autorização atual e ao ramo/revisão do mundo; mensagens antigas de nós revogados permanecem isoladas. O host de BG2:EE e Action Gateway continuam as únicas instâncias para confirmação mecânica permitida. A própria LAN não é prova de confiança. ADR-0053/documento 58; transporte ainda não implementado.


### Memória NPC e autoridade — DEC-065/C (Discovery v6.1)

A síntese de experiências é uma projeção **derivada** por NPC/campanha/ramo, não recibo do host nem fato canônico; não muda flags, quests ou estado mecânico. Evento `UNCERTAIN` não é consolidado como confirmação, e checkpoints/branches devem conter referências coerentes. Memória crítica protege continuidade narrativa, não concede autorização de ação. Preservar DEC-060–064, inclusive partição física de lore por ano DR.

### Integração DEC-066/C — identidade não é receipt do motor (v6.2)

O bridge pode observar uma instância, mas só evidências confirmadas e revisões coerentes podem vincular `EngineObservation` a `NPCIdentity` do overlay. Em `UNCERTAIN`, ID reciclado ou conflito de candidatos, não confirmar reencontro nem liberar operações dependentes da identidade. Host segue autoridade mecânica, Infinity AI narrativa sobre eventos confirmados; identidades não autorizam escrever save diretamente.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

A individualização é transição narrativa idempotente; criar NPC lógico não executa spawn/ação mecânica. Eventual alteração de engine passa por Action Gateway e host; `UNCERTAIN` não é evento confirmado. Relacionado: ADR-0062 e doc. 67.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

NPC fora de cena mantém estado narrativo da campanha; suas decisões são propostas. Alterações mecânicas, mudança de área observável, quests, recrutamento e efeitos irreversíveis exigem host/bridge, receipts e reconciliação. Falta de observação não é autorização. ADR-0063/doc. 68, DEC-068/C.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: itinerário e `ARRIVED_NARRATIVE` pertencem ao estado narrativo condicionado; `ENGINE_OBSERVED` é somente host/receipt com identidade, área, build e checkpoint. Incerto/stale não causa comando mecânico nem presença dupla.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

Incidentes DEC-070 são propostas do Living World até gates de risco. Evento narrativo LOW aprovado não corresponde a mutação no BG2:EE; consequências mecânicas exigem receipt do host. Operação incerta bloqueia repetição automática e requer reconciliação.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Uma transição de incidente DEC-070 para encounter local DEC-071 nunca muda a autoridade: o host confirma presença/ação/efeito de engine, o ledger narrativo registra decisões validadas. `LOCAL_RESERVED` apenas exclui o resolvedor distante; não prova encontro realizado. `UNCERTAIN` exige reconciliar receipts antes de liberar resolvedor ou repetir comando.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Composição DEC-072 produz proposta sem efeito. Ledger DEC-071 continua dono do incident_id; gateway/host autenticam operação e receipts antes de alterar estado mecânico; `UNCERTAIN` bloqueia reexecução.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Receipts host e ledger do incidente são pré-condições de fechamento; cleanup de engine somente por Action Gateway e capacidade testada, `UNCERTAIN` falha fechado.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Efeitos de repercussão DEC-074 só se tornam mecânicos mediante receipt host/Action Gateway; relatos e crenças não validam motor. Event source precisa de branch/checkpoint/revision e idempotência causal. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Separar fato confirmado pelo host, participação inferível de evidências, testemunhos e efeitos; o modelo não confirma dano, cura, XP, autoria mecânica ou culpa por simples narrativa.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Host confirma estados mecânicos; um nome/pseudônimo revelado pelo LLM não confirma identidade nem alteração física. `IdentityLinkAssessment` é privado e exige evidência; `DisclosureEvent` exige ACL/consentimento/risco; UNCERTAIN e STALE bloqueiam efeitos.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação por evidências (Discovery v7.3; não implementada)

A investigação de personas DEC-076 usará ledger privado por campanha/ramo, com pistas e hipóteses revisáveis, origem/independência de fontes, contraprovas e estados inconclusivos. Suspeita ou fala LLM não confirma identidade e não permite divulgação; vínculo factual restrito exige evidências/DEC-066, e revelação exige ACL/consentimento/risk gate por audiência (DEC-019/028/041/045/046). Rumores e repercussões DEC-029/074/075 são separados de fato e punição. **Preservar `knowledge/periods/<ANO>-DR/` fisicamente por ano, sem evidências privadas no cânone.** ADR-0072/documento 77; 58 testes não executados, sem POC BG2:EE/EEex/multiplayer.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

DEC-078 distingue a posição da autoridade ficcional do estado factual do ledger e do estado mecânico. Regras e autorização são determinísticas; qualquer efeito BG2:EE depende do host e Action Gateway, sem veredito LLM.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Pedido interjurisdicional não transfere autoridade mecânica; emissão, entrega, reconhecimento, autorização e receipt de host são fronteiras distintas. Operação UNCERTAIN não pode ser repetida cegamente.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

DEC-080 separa status autoritativo, conhecimento de autoridade destinatária e safety gate mecânico. A prova restrita não torna NPC onisciente; HIGH só passa após vigência, competência, direitos do PC, capability e receipt do host.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

RemedyCase é avaliação narrativa da campanha, e não ordem direta ao motor. Restituição, reparação de quest ou liberação mecânica exigem gateway, autorização e receipt host; incerto não se repete cegamente.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Autoria factual, decisão de autoridade ficcional e efeito de engine são domínios diferentes; LLM não confirma condenação ou cumprimento de sanção, e receipt host é necessário.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

A divulgação é operação tipada com audiência/propósito, competência e idempotência. Host confirma efeitos mecânicos, mas sua autoridade não concede acesso público aos dados selados.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Planos de proteção não são recibos mecânicos; somente host autoriza mudanças reais de posição, combate/HP/inventário/quest, sob riscos e fencing.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Distinguir verdade autoritativa de plano, prova de observação, conhecimento social e ação host; avaliação interna de vazamento não equivale a evento de mundo nem permissão de NPC.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

PlantedClaim e WorldFact têm autoridade diferente; operação de engano não pode forjar host receipt, nem criar fato/alteração mecânica por cliente. UNCERTAIN bloqueia retry cego.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Lealdades são projeções privadas de eventos autorizados; uma narrativa de ruptura não altera host/engine. Mudanças mecânicas exigem gateway, host receipt e reconciliação idempotente.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Confirmação de entrega física de ouro/itens exige host; acordo narrativo não é transação mecânica. Divergência e UNCERTAIN bloqueiam replay, com fencing por epoch e identidade.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Parecer epistêmico não equivale a estado mecânico: host authoritative receipts e Action Gateway permanecem separados. O estado INCONCLUSIVE bloqueia efeitos HIGH sem base válida.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

`DossierRevision`, `DisclosureView`, `ShareAuthorization` e `RecipientReceipt` são estados distintos; criação do pacote não equivale à observação pela engine. Host/gateway autorizam efeitos mecânicos, nunca LLM pura.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Host é autoridade mecânica; plano, consentimento, reserva e despacho não são receipts. UNCERTAIN e STALE bloqueiam repetição de ações ou publicação de resultado.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Host e gateway continuam autoritativos: `ABORT_REQUESTED` ou `PAUSE_REQUESTED` não substituem receipt; divergência de sessão/checkpoint gera UNCERTAIN e bloqueia retry.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Concorrência DEC-093 usa fencing/epoch e idempotência para reservas no middleware. Nenhum priority/fairness ou lock lógico cria autoridade mecânica; host DEC-011 e gateway DEC-012 prevalecem.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Recovery de deadlock exige separação de CAS interno, owner consent, host receipt e capability; `UNCERTAIN` não autoriza release, retry ou status de NPC presumido.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

DEC-095 compensa por novos atos e receipts, nunca apaga fatos confirmados; proposta DEC-096 produz somente ImpactProposal antes de autorização/receipt host, sem mutação a partir de lore.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

A autoridade dividida continua: regras DEC-096/097 preveem target; DEC-098 apenas propõe delta; somente host/Action Gateway confirma spawn, patch ou cleanup.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

A autoridade do host sobre estado mecânico não implica licença de mutação: ownership e autorização de campo/ação são precondições adicionais DEC-099.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Eventos de mundo só podem depender de marcos de quests legitimamente observados, sem acesso universal a scripts ou endings.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração DEC-102/C (Discovery v9.8)

Host tem soberania mecânica; reconciliação DEC-102 não sobrescreve globals/scripts nem fatos; projeções derivadas por CAS. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** marcos confirmados de quests originais são **origens candidatas** de regras históricas/regionais, não fatos canônicos escritos em `knowledge/periods/<ANO>-DR/`. A admissão exige prova reconciliada DEC-100/101/102, clock DR e branch adequados; a matriz DEC-096 filtra local, fase e precondições e DEC-097 compõe impactos. Escopo global não dá conhecimento universal. Evento proposto, evento host-confirmed e rumor entregue são distintos; nenhum efeito mecânico sem Action Gateway/receipt. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **história e mundo**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para autoridades separadas: host, registry, canal, crença e ACL, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para autoridade dividida e recibos host, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Event log de obrigações DR, prestação confirmada e aditamentos sem apagar eventos anteriores. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Event log e snapshots preservam estado factual de cada obrigação e dependência. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Distinguir autoridade de contrato, autorização do titular e recibo do host. O custodian não ganha permissão por mensagem de LLM; epoch/fencing vinculam liberação.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
