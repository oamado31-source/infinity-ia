# Plano de integração progressiva — DEC-003 / Discovery v0.7

**Estado:** proposta de execução decorrente da decisão aprovada **DEC-003 (opção A)**. Gates e valores de teste definitivos dependem das futuras SPECS, sobretudo DEC-013 e DEC-015. Nenhuma instalação/teste real executado.

## Objetivo

Validar primeiro a capacidade de BG2:EE executar uma integração segura com um serviço externo e **sincronizar alterações entre dois jogadores**, antes de expandir para EET, Icewind Dale e NWNForBG.

## Marcos de validação

| Marco | Ambiente/build | Ação controlada | Evidência | Risco principal |
|---|---|---|---|---|
| P0 | BG2:EE puro, Windows | abrir, viajar, salvar e recarregar | logs, versão, captura/registro de teste | baseline |
| P1 | BG2:EE + EEex | inicializar via loader compatível | manifesto, estabilidade | incompatibilidade de versões |
| P2 | P1 + bridge externa | consultar estado **sem alterar** jogo | payload sanitizado, logs | acesso indevido |
| P3 | P2 offline | ação permitida e reversível (ex.: spawn de teste) | estado anterior/posterior | escrita descontrolada |
| P4 | P3 com dois clientes | consistência de ação e estado após save/reload | resultados dos dois clientes | dessincronização |
| P5 | EET, build reconstruída quando necessário | reaplicar provas de regressão | manifesto, transições, saves | dependências de mods |
| P6 | IWD1/IWD2, builds por combinação | testar áreas/recursos/multiplayer | provas por incremento | colisão de recursos |
| P7 | NWNForBG, build por combinação | testar áreas, NPCs e transições | provas por incremento | conflitos de integração |

## Regra para construir builds

- Cada ambiente começa de **instalações legítimas copiadas para teste**, preservando originais e saves pessoais.
- Reutilizar um snapshot somente quando a documentação de **toda a combinação** permitir. Caso contrário, **reconstruir uma instalação de teste limpa** com a ordem correta dos mods.
- Registrar versão exata, fonte, ordem, componente, saída da instalação, checksum quando aplicável e identificador do baseline anterior.
- Não assumir que EET, IWD1/IWD2 e NWNForBG aceitem instalação cumulativa simples; preservar componentes finais como `EET_End` nas posições documentadas.
- Ao falhar um gate, manter último baseline aprovado e registrar causa/alternativa; não prosseguir com expansão como se o problema estivesse resolvido.

## POCs prioritárias para as primeiras SPECS técnicas

1. **SPEC-POC-001 (candidata):** comando externo **somente leitura** em BG2:EE Windows usando EEex/bridge com versions pin e log.
2. **SPEC-POC-002 (candidata):** comando allowlisted de alteração local em save de teste, com reversão comprovada.
3. **SPEC-POC-003 (candidata):** comparação do estado resultante em dois clientes; log de divergências e decisão de continuar/reprojetar.
4. **SPEC-POC-004 (candidata):** regressão EET e conteúdo incremental conforme manifestos reproduzíveis.

**As SPECS acima são nomes provisórios de testes, não features formalmente aprovadas.**

## Próxima decisão proposta

**DEC-011 — autoridade do estado multiplayer e da IA**: definir quem pode confirmar alterações em combate, inventário, NPCs, missões e fatos narrativos; e como os clientes observam um estado consistente. É fundamental antes do desenho da bridge, banco de dados e agentes.

## Integração com DEC-051 — inventário de conteúdo validado por build (Discovery v4.7)

A DEC-051 aprovou captura de fingerprint/manifesto e recursos **read-only**, enriquecidos por curadoria e cobertura explícita (ADR-0046/doc. 51). A presença estática de arquivos não comprova flags/quests vivas. Propostas dependentes de conteúdo desconhecido ou build divergente devem ser bloqueadas/adiadas pelo reconciliador DEC-050; operações efetivas continuam sob gateway e confirmação do host. Regressões são específicas de instalação/ordem de mods; implementações e suporte multiplayer permanecem não comprovados.

## DEC-052 — Gates de continuidade na evolução do stack (Discovery v4.8)

Ao avançar de BG2:EE limpo para EEex/EET/IWD/NWNForBG, tratar **cada mudança de build** como candidato isolado: capturar manifestos DEC-051, checkpoint recuperável, diff dos recursos e scripts DEC-050, save/load e progressão relevante, consistência entre host e dois clientes e autorização explícita do anfitrião. Falhas bloqueiam promoção e preservam baseline; não presumir que a instalação cumulativa ou a reversão de mods mantém a campanha. DEC-013/015/018 seguem abertas. ADR-0047/documento 52 definem a política, não resultados de POCs.

## Integração posterior — DEC-055 (Discovery v5.1)

Adicionar POCs para healthchecks observáveis de gateway, DB, LLM e bridge; falhas de conectividade e receipts `UNCERTAIN`; modos degradados seguros; diagnóstico host + dois clientes; e alarmes de backup/checkpoint. Nenhuma sonda ou capacidade de pausar BG2:EE deve ser declarada suportada sem prova por build. Ver ADR-0050/doc. 55.

## DEC-057 — Gate adicional de distribuição LAN (v5.3)

Após BG2:EE limpo/bridge read-only e validação de host+dois clientes, ensaiar orquestrador/LLM **local** e só então worker stateless **LAN opcional**. Validar rejeição de nó não autorizado, respostas obsoletas, desligamento de LAN no meio do job, ACL, retorno com `proposal_only` e ausência de acesso direto ao motor. Nenhuma mudança em EET/IWD/NWN ou no status de EEex até POCs. A política de pareamento/autenticação é DEC-058 aberta.

## DEC-062 — prova de ingestão histórica sem modificação do motor

Adicionar às futuras SPECS/POCs um gate offline de ingestão com fontes de teste sintéticas/autorizadas: arquivo em staging, datas incertas, duas fontes conflitantes em 1369, evento futuro 1370, ACL e licença, anti-prompt-injection, crash/idempotência e rollback de revisão anual. Esse gate é **independente** de alegar interoperabilidade com BG2:EE/EEex e não altera save nem instalação. DEC-060/061 obrigatórias; a promoção de novas revisões em campanhas requer DEC-063.


### Gate futuro DEC-065 — memória hierárquica verificável (Discovery v6.1)

Após validar bridge e observação real, ensaiar memória de NPC em modo somente leitura, com identidade testada (DEC-066 pendente), eventos com fonte, resumos derivados e recuperação ACL. Depois testar checkpoint/restore por branch e custo sob carga. **Não** inferir suporte de EEex sem POC, nem conectar escrita mecânica antes de gate. Cânone mantém diretórios físicos anuais DEC-060.

### POC adicional DEC-066/C — identidade em saves/áreas/duas instâncias (v6.2)

Acrescentar ao roteiro de provas read-only no BG2:EE Windows: registrar somente campos efetivamente visíveis em vanilla/EEex; testar save/load, troca de área, ID reciclado, dois NPCs homônimos, companion ausente, clone de mod e host+dois clientes. Atestar por build a estabilidade, escopo e ambiguidade das provas. Falha bloqueia identidade pessoal, não é compensada por heurísticas de nome. Nenhuma dessas POCs foi executada.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

POC futura DEC-067: em BG2:EE limpo → EEex/bridge → host+dois clientes, testar observação de NPC genérico, promoção lógica, homônimos, save/load, rollback e contagem agregada. Nenhuma capacidade presumida.

## Integração com DEC-069/C — Discovery v6.5

Integração DEC-069: inventariar áreas e scripts por build, observar posição/IDs sem mutações, testar save/load offline, avaliar integração EEex somente após POC e testar host+dois clientes antes de qualquer viagem com aparição física; sem promessa de spawn ou pathfinding offscreen.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070 exige POCs graduais para distinguir relato de incidente, evento narrativo validado e efeito mecânico realmente confirmado pelo host; não se presume encontro/combate/spawn offscreen. Testar read-only antes de escrita offline e host+2 clientes.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

A sequência de integração deve incluir POCs separadas para (i) proximidade/área em modo somente leitura, (ii) reserva durável do `incident_id` contra resolução offscreen, (iii) oferta narrativa sem efeitos e (iv) eventual encontro mecânico **somente** após adapter por build comprovado, gateway e receipt host. Testar host + dois clientes; nenhum recurso está demonstrado.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

POC incremental DEC-072: inventário read-only → catálogo e validação sintética offline → adapter de interação de baixo impacto se viável → host+dois clientes e save/load → testes de expansão/rollback. Não ativar spawn, script ou pack sem evidência real.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Incluir POCs incrementais específicas de ownership/cleanup após ensaios offline: inventário passivo, observações host, checkpoint, save/load/rollback, host+2 clientes.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

DEC-074 entra após simulações sintéticas de fontes/eventos, ACL, clock, idempotência e testes de risco, antes de qualquer integração mecânica; requer POC BG2:EE/EEex, host+dois clientes e gates de release DEC-015. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

POC de atribuição exige medir quais eventos individuais realmente são observáveis por BG2:EE/EEex e host+2 clientes, sem prometer granularidade.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Antes de qualquer suporte de alias/disfarce na engine, testar inventário read-only, identidade DEC-066, NPCs e campo de nome/visual BG2:EE por build; em seguida teste host+dois clientes. A DEC-076/C aprova apenas a camada narrativa privada, não mudança de CRE ou render.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação por evidências (Discovery v7.3; não implementada)

A investigação de personas DEC-076 usará ledger privado por campanha/ramo, com pistas e hipóteses revisáveis, origem/independência de fontes, contraprovas e estados inconclusivos. Suspeita ou fala LLM não confirma identidade e não permite divulgação; vínculo factual restrito exige evidências/DEC-066, e revelação exige ACL/consentimento/risk gate por audiência (DEC-019/028/041/045/046). Rumores e repercussões DEC-029/074/075 são separados de fato e punição. **Preservar `knowledge/periods/<ANO>-DR/` fisicamente por ano, sem evidências privadas no cânone.** ADR-0072/documento 77; 58 testes não executados, sem POC BG2:EE/EEex/multiplayer.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

O fluxo DEC-078 deve começar com políticas sintéticas e regras offline de competência/prova/contestação e depois observar o host BG2:EE sem alterar saves. Prisão, hostilidade, mandados, inventário e flags só por POC isolada, adapter por build, checkpoint e host+dois clientes.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

DEC-079 exige G79-0..G79-5 com fixtures sintéticos, estados e ACL, depois inventário read-only do BG2:EE e teste host+dois clientes antes de declarar suporte a guardas perseguidores, mandados ou captura.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Testar revogação em simulador determinístico antes de qualquer POC host; em BG2:EE investigar apenas observabilidade read-only, depois host+2 clientes se adapter seguro existir. Evitar presumir release de prisioneiro/wanted flag.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Exigir POCs de danos/remédios DEC-081 em sequência: dados sintéticos, competência curada, recibos de engine read-only, operações benígnas com backup em sandbox e host+2 clientes. Nada comprovado de soltura, restituição ou edição de quest.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Priorizar testes sintéticos de competência e proveniência antes de efeitos; POC engine read-only, depois host+dois clientes e rollback ensaiado, nenhum suporte presumido.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Antes de POC do motor, testar privacidade, redactions, identidade, origem, consentimento, revisões e leakage no LLM/RAG/LAN; nenhuma proteção física autorizada.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Adicionar POCs de ameaças com source/evidence, consentimento, reserva de protetores, tempo/rotas, reconciliação, observação host read-only e só depois escolta testada host+dois clientes.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Separar protótipo offline de ACL/rumores e POC de motor read-only, depois host+dois clientes; não prometer interceptação, perseguição ou stealth antes de testes.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Templates de isca e documentos falsos são candidatos narrativos; validar capacidade de observação read-only e, só depois, alterações de motor host+2 clientes. Não anunciar captura, interceptação ou disfarce por texto de IA.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Na integração progressiva, observar inicialmente ID e informações read-only do companion; scripts de party/faction flags, saída, hostilidade e sincronização de lealdade exigem capability por build e testes host+2 clientes.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Adicionar POCs futuras do processo de contato→negociação→acordo e payment read-only antes de escrita; testar host+2 clientes por build. Não presumir diálogo dinâmico nem oferta monetária engine.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Incluir POCs sintéticas/offline de depoimentos conflitantes, repetição de rumor e documentação autenticada antes de pensar em coleta do BG2:EE. Integração real exigirá host+2 clientes.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Na bridge inicial, dossiês devem ser artefatos externos, read-only. Qualquer renderização em journal, item ou multiplayer requer capability por build e provas com host+2 clientes; nenhuma existe hoje.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

POC progressiva: primeiro planner read-only determinístico; só após build manifest e host+2 clientes, testar Action Gateway para operação isolada; sem assumir bridge funcional.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

A integração progressiva requer provar separadamente observar ações, bloquear novos despachos, cancelar ações em voo e pausar motor. Sem evidência, somente pausa do middleware.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Planejar testes por build do inventário de NPC, inventário, posição, estado e recibos antes de habilitar alocação mecânica concorrente em host+dois clientes. Reservas lógicas não atestam integração.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Incluir POCs isoladas de scheduler/locks internos e crash-recovery antes de host+dois clientes. Fencing do serviço não prova que EEex/host rejeita uma ação tardia; testar in-flight sem modificar saves reais.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

O caminho BG2:EE limpo → EEex → bridge → 2 clientes deve demonstrar observabilidade de instâncias, receipts e capacidade por build antes de materializar qualquer repercussão regional.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Sequência de integração: BG2:EE limpo como baseline observável; adicionar EEex/bridge e mods progressivamente; comparar quest/scripts antes e depois, 1 host e 2 clientes.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Integração progressiva BG2:EE limpo → EEex/bridge → host+2 clientes inclui observação sem side effects, sempre por build.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração DEC-102/C (Discovery v9.8)

POC da DEC-102 requer host real, dois clientes, save/load, restore, divergência de mod e validação da observação sem escrita. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para integração progressiva e POC host + dois clientes de delivery/perception, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Custódia mecânica passa após bridge read-only, autoridade de dois clientes e inventário confirmado. Não elevar POC de escrow à condição de P0 necessária para o primeiro desenvolvimento.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
